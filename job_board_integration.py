"""
Job Board Integration
Lightweight database with essential fields only + on-demand detail fetching
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import hashlib
import requests
from bs4 import BeautifulSoup
import json

Base = declarative_base()


class JobListing(Base):
    """Lightweight job listing - essential fields only"""
    __tablename__ = 'job_listings'

    id = Column(Integer, primary_key=True)
    job_id = Column(String(255), unique=True, index=True)  # Hash for deduplication

    # Essential fields for display
    title = Column(String(500), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    location = Column(String(255), index=True)
    salary = Column(String(255))

    # Metadata
    source = Column(String(100), nullable=False, index=True)
    source_url = Column(String(1000), nullable=False)  # Original job URL
    posted_date = Column(DateTime, index=True)
    remote = Column(Boolean, default=False, index=True)
    job_type = Column(String(100))  # full-time, contract, etc.

    # Quick preview (short excerpt)
    preview_text = Column(String(500))  # First 500 chars of description

    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_accessed = Column(DateTime)  # Track when user viewed
    view_count = Column(Integer, default=0)  # How many times viewed

    # Optional: Cache full details after first fetch
    cached_description = Column(String)  # NULL until first access
    cache_date = Column(DateTime)  # When was it cached

    @staticmethod
    def generate_job_id(title, company, location):
        """Generate unique job ID"""
        key = f"{title.lower().strip()}|{company.lower().strip()}|{location.lower().strip()}"
        return hashlib.md5(key.encode()).hexdigest()

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'job_id': self.job_id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'salary': self.salary,
            'source': self.source,
            'source_url': self.source_url,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'remote': self.remote,
            'job_type': self.job_type,
            'preview_text': self.preview_text,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class JobBoardDatabase:
    """Lightweight database manager for job board"""

    def __init__(self, database_url='sqlite:///job_board.db'):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_job(self, job_data):
        """
        Add job with minimal data

        Args:
            job_data: dict with keys: title, company, location, salary,
                     source, url, posted_date, remote, job_type, preview_text

        Returns:
            tuple: (is_new, job_listing)
        """
        job_id = JobListing.generate_job_id(
            job_data['title'],
            job_data['company'],
            job_data.get('location', 'N/A')
        )

        existing = self.session.query(JobListing).filter_by(job_id=job_id).first()
        if existing:
            return False, existing

        job = JobListing(
            job_id=job_id,
            title=job_data['title'],
            company=job_data['company'],
            location=job_data.get('location', 'N/A'),
            salary=job_data.get('salary'),
            source=job_data['source'],
            source_url=job_data['url'],
            posted_date=job_data.get('posted_date'),
            remote=job_data.get('remote', False),
            job_type=job_data.get('job_type'),
            preview_text=job_data.get('preview_text', '')[:500]
        )

        self.session.add(job)
        self.session.commit()
        return True, job

    def get_jobs(self, filters=None, limit=50, offset=0):
        """Get jobs for listing page"""
        query = self.session.query(JobListing)

        if filters:
            if 'keyword' in filters:
                keyword = f"%{filters['keyword']}%"
                query = query.filter(
                    (JobListing.title.like(keyword)) |
                    (JobListing.company.like(keyword)) |
                    (JobListing.location.like(keyword))
                )
            if 'source' in filters:
                query = query.filter_by(source=filters['source'])
            if 'remote' in filters:
                query = query.filter_by(remote=filters['remote'])
            if 'location' in filters:
                location = f"%{filters['location']}%"
                query = query.filter(JobListing.location.like(location))

        return query.order_by(JobListing.posted_date.desc()).offset(offset).limit(limit).all()

    def get_job_by_id(self, job_id):
        """Get single job by ID"""
        return self.session.query(JobListing).filter_by(id=job_id).first()

    def track_view(self, job_id):
        """Track when user views a job"""
        job = self.get_job_by_id(job_id)
        if job:
            job.last_accessed = datetime.utcnow()
            job.view_count += 1
            self.session.commit()

    def cache_description(self, job_id, description):
        """Cache full description after fetching"""
        job = self.get_job_by_id(job_id)
        if job:
            job.cached_description = description
            job.cache_date = datetime.utcnow()
            self.session.commit()

    def get_total_count(self, filters=None):
        """Get total job count for pagination"""
        query = self.session.query(JobListing)

        if filters:
            if 'keyword' in filters:
                keyword = f"%{filters['keyword']}%"
                query = query.filter(
                    (JobListing.title.like(keyword)) |
                    (JobListing.company.like(keyword))
                )
            if 'remote' in filters:
                query = query.filter_by(remote=filters['remote'])

        return query.count()

    def close(self):
        self.session.close()


class DetailFetcher:
    """Fetch full job details on-demand when user clicks"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch_details(self, source_url, source_name):
        """
        Fetch full job details from original URL

        Args:
            source_url: Original job posting URL
            source_name: Source identifier (remoteok, github, etc.)

        Returns:
            dict with full details or None if failed
        """
        try:
            response = self.session.get(source_url, timeout=10)
            response.raise_for_status()

            # Parse based on source
            if 'remoteok.com' in source_url:
                return self._parse_remoteok(response.text)
            elif 'remotive.com' in source_url:
                return self._parse_remotive(response.text)
            elif 'weworkremotely.com' in source_url:
                return self._parse_weworkremotely(response.text)
            else:
                # Generic parsing
                return self._parse_generic(response.text)

        except Exception as e:
            print(f"Error fetching details: {e}")
            return None

    def _parse_remoteok(self, html):
        """Parse RemoteOK job page"""
        soup = BeautifulSoup(html, 'lxml')

        # Try to find job description
        description_elem = soup.find('div', class_='description')
        if not description_elem:
            description_elem = soup.find('div', {'itemprop': 'description'})

        description = description_elem.get_text(strip=True) if description_elem else ''

        return {
            'description': description,
            'source_html': str(description_elem) if description_elem else ''
        }

    def _parse_remotive(self, html):
        """Parse Remotive job page"""
        soup = BeautifulSoup(html, 'lxml')

        description_elem = soup.find('div', class_='job-description')
        description = description_elem.get_text(strip=True) if description_elem else ''

        return {
            'description': description,
            'source_html': str(description_elem) if description_elem else ''
        }

    def _parse_weworkremotely(self, html):
        """Parse We Work Remotely job page"""
        soup = BeautifulSoup(html, 'lxml')

        description_elem = soup.find('div', class_='listing-container')
        description = description_elem.get_text(strip=True) if description_elem else ''

        return {
            'description': description,
            'source_html': str(description_elem) if description_elem else ''
        }

    def _parse_generic(self, html):
        """Generic HTML parsing fallback"""
        soup = BeautifulSoup(html, 'lxml')

        # Try common selectors
        selectors = [
            'div.job-description',
            'div.description',
            'div.content',
            'article',
            'main'
        ]

        description = ''
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                description = elem.get_text(strip=True)
                break

        return {
            'description': description,
            'source_html': html
        }


class JobBoardAPI:
    """
    Simple API for your job board
    Combines lightweight database with on-demand fetching
    """

    def __init__(self, database_url='sqlite:///job_board.db'):
        self.db = JobBoardDatabase(database_url)
        self.fetcher = DetailFetcher()

    def import_from_aggregator(self, aggregator_db_path='sqlite:///jobs.db'):
        """Import jobs from the main aggregator database"""
        from aggregator import JobAggregator

        aggregator = JobAggregator(database_url=aggregator_db_path)
        jobs = aggregator.db.get_jobs(limit=10000)

        imported = 0
        skipped = 0

        for job in jobs:
            # Extract preview text (first 500 chars of description)
            preview = ''
            if job.description:
                soup = BeautifulSoup(job.description, 'html.parser')
                preview = soup.get_text()[:500]

            job_data = {
                'title': job.title,
                'company': job.company,
                'location': job.location,
                'salary': job.salary,
                'source': job.source,
                'url': job.url,
                'posted_date': job.posted_date,
                'remote': job.remote,
                'job_type': job.job_type,
                'preview_text': preview
            }

            is_new, _ = self.db.add_job(job_data)
            if is_new:
                imported += 1
            else:
                skipped += 1

        aggregator.close()
        return imported, skipped

    def get_job_list(self, page=1, per_page=20, keyword=None, remote_only=False, location=None):
        """
        Get paginated job list for your job board listing page

        Returns:
            dict with jobs, total, page info
        """
        filters = {}
        if keyword:
            filters['keyword'] = keyword
        if remote_only:
            filters['remote'] = True
        if location:
            filters['location'] = location

        offset = (page - 1) * per_page
        jobs = self.db.get_jobs(filters=filters, limit=per_page, offset=offset)
        total = self.db.get_total_count(filters=filters)

        return {
            'jobs': [job.to_dict() for job in jobs],
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }

    def get_job_details(self, job_id, use_cache=True):
        """
        Get full job details when user clicks

        Args:
            job_id: Database job ID
            use_cache: Whether to use cached description if available

        Returns:
            dict with full job details
        """
        job = self.db.get_job_by_id(job_id)
        if not job:
            return None

        # Track view
        self.db.track_view(job_id)

        # Start with basic info
        details = job.to_dict()

        # Check cache first
        if use_cache and job.cached_description:
            details['description'] = job.cached_description
            details['from_cache'] = True
        else:
            # Fetch from source
            fetched = self.fetcher.fetch_details(job.source_url, job.source)
            if fetched:
                details['description'] = fetched['description']
                details['from_cache'] = False

                # Cache for next time
                self.db.cache_description(job_id, fetched['description'])
            else:
                # Fallback to preview if fetch fails
                details['description'] = job.preview_text + '... (Full details unavailable)'
                details['from_cache'] = False

        details['view_count'] = job.view_count
        return details

    def get_statistics(self):
        """Get database statistics"""
        from sqlalchemy import func

        stats = {
            'total_jobs': self.db.get_total_count(),
            'remote_jobs': self.db.session.query(JobListing).filter_by(remote=True).count(),
            'with_salary': self.db.session.query(JobListing).filter(
                JobListing.salary.isnot(None),
                JobListing.salary != ''
            ).count()
        }

        # Jobs by source
        by_source = self.db.session.query(
            JobListing.source,
            func.count(JobListing.id)
        ).group_by(JobListing.source).all()

        stats['by_source'] = {source: count for source, count in by_source}

        return stats

    def close(self):
        self.db.close()


# Example usage functions
def example_import_jobs():
    """Import jobs from aggregator to job board database"""
    api = JobBoardAPI()

    print("Importing jobs from aggregator database...")
    imported, skipped = api.import_from_aggregator()

    print(f"Imported: {imported} jobs")
    print(f"Skipped (duplicates): {skipped} jobs")

    api.close()


def example_list_jobs():
    """Get job listing for display"""
    api = JobBoardAPI()

    # Get first page of Python jobs
    result = api.get_job_list(page=1, per_page=10, keyword="python")

    print(f"Total jobs: {result['total']}")
    print(f"Page {result['page']} of {result['total_pages']}\n")

    for job in result['jobs']:
        print(f"{job['title']} - {job['company']}")
        print(f"  Location: {job['location']}")
        # Remove non-ASCII characters for Windows console
        preview = job['preview_text'][:100] if job['preview_text'] else ''
        preview = preview.encode('ascii', 'ignore').decode('ascii')
        print(f"  Preview: {preview}...")
        print()

    api.close()


def example_get_details():
    """Get full job details when user clicks"""
    api = JobBoardAPI()

    # Get job ID 1's details
    details = api.get_job_details(1)

    if details:
        print(f"Title: {details['title']}")
        print(f"Company: {details['company']}")
        print(f"URL: {details['source_url']}")
        print(f"Views: {details['view_count']}")
        print(f"\nFull Description:")
        print(details['description'][:500] + "...")

    api.close()


if __name__ == '__main__':
    # Run examples
    print("Example 1: Import jobs")
    example_import_jobs()

    print("\n" + "="*80 + "\n")

    print("Example 2: List jobs")
    example_list_jobs()

    print("\n" + "="*80 + "\n")

    print("Example 3: Get job details")
    example_get_details()
