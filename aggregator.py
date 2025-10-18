import os
from dotenv import load_dotenv
from scrapers import (
    AdzunaScraper, RemoteOKScraper, WeWorkRemotelyScraper,
    RemotiveScraper, AuthenticJobsScraper, GitHubJobsScraper,
    IndeedScraper, AngelListScraper, CrunchboardScraper
)
from models import DatabaseManager
from location_filter import is_us_location, filter_us_jobs
from typing import List, Dict
import time


class JobAggregator:
    """Main aggregator class that coordinates all scrapers"""

    def __init__(self, database_url=None, us_only=True):
        load_dotenv()

        self.database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///jobs.db')
        self.db = DatabaseManager(self.database_url)
        self.us_only = us_only  # Filter for US jobs only

        # Initialize scrapers
        self.scrapers = {
            'remoteok': RemoteOKScraper(),
            'remotive': RemotiveScraper(),
            'weworkremotely': WeWorkRemotelyScraper(),
            'authenticjobs': AuthenticJobsScraper(),
            'indeed': IndeedScraper(),
            'crunchboard': CrunchboardScraper(),
        }

        # Add API-based scrapers if credentials are available
        adzuna_id = os.getenv('ADZUNA_APP_ID')
        adzuna_key = os.getenv('ADZUNA_APP_KEY')
        if adzuna_id and adzuna_key:
            self.scrapers['adzuna'] = AdzunaScraper(adzuna_id, adzuna_key)

        github_token = os.getenv('GITHUB_TOKEN')
        if github_token:
            self.scrapers['github'] = GitHubJobsScraper(github_token)
        else:
            self.scrapers['github'] = GitHubJobsScraper()

    def scrape_all(self, keywords=None, location=None, sources=None, max_pages=5):
        """
        Scrape all or selected sources

        Args:
            keywords: Search keywords (e.g., "python developer")
            location: Job location (e.g., "remote", "New York")
            sources: List of sources to scrape (None = all)
            max_pages: Maximum pages per source

        Returns:
            Dict with statistics
        """
        if sources:
            active_scrapers = {k: v for k, v in self.scrapers.items() if k in sources}
        else:
            active_scrapers = self.scrapers

        stats = {
            'total_scraped': 0,
            'total_new': 0,
            'total_duplicates': 0,
            'by_source': {}
        }

        print(f"\n{'='*60}")
        print(f"Starting job aggregation from {len(active_scrapers)} sources")
        print(f"Keywords: {keywords or 'All'}")
        print(f"Location: {location or 'All'}")
        print(f"{'='*60}\n")

        for source_name, scraper in active_scrapers.items():
            print(f"Scraping {source_name}...", end=' ')
            start_time = time.time()

            try:
                jobs = scraper.scrape(keywords=keywords, location=location, max_pages=max_pages)

                # Filter for US jobs if enabled
                filtered_count = 0
                if self.us_only:
                    before_filter = len(jobs)
                    jobs = filter_us_jobs(jobs)
                    filtered_count = before_filter - len(jobs)

                scraped_count = len(jobs)
                new_count = 0
                duplicate_count = 0

                for job in jobs:
                    is_new, _ = self.db.add_job(job)
                    if is_new:
                        new_count += 1
                    else:
                        duplicate_count += 1

                elapsed = time.time() - start_time
                if filtered_count > 0:
                    print(f"[OK] ({scraped_count} US jobs, {new_count} new, {duplicate_count} duplicates, {filtered_count} non-US filtered) - {elapsed:.1f}s")
                else:
                    print(f"[OK] ({scraped_count} found, {new_count} new, {duplicate_count} duplicates) - {elapsed:.1f}s")

                stats['total_scraped'] += scraped_count
                stats['total_new'] += new_count
                stats['total_duplicates'] += duplicate_count
                stats['by_source'][source_name] = {
                    'scraped': scraped_count,
                    'new': new_count,
                    'duplicates': duplicate_count
                }

                time.sleep(1)  # Be respectful between sources

            except Exception as e:
                print(f"[FAIL] Error: {e}")
                stats['by_source'][source_name] = {
                    'scraped': 0,
                    'new': 0,
                    'duplicates': 0,
                    'error': str(e)
                }

        print(f"\n{'='*60}")
        print(f"Aggregation Complete!")
        print(f"Total jobs found: {stats['total_scraped']}")
        print(f"New jobs added: {stats['total_new']}")
        print(f"Duplicates filtered: {stats['total_duplicates']}")
        print(f"{'='*60}\n")

        return stats

    def search_jobs(self, keyword=None, source=None, remote=None, limit=100):
        """Search stored jobs"""
        filters = {}
        if source:
            filters['source'] = source
        if remote is not None:
            filters['remote'] = remote
        if keyword:
            filters['keyword'] = keyword

        return self.db.get_jobs(filters=filters, limit=limit)

    def export_jobs(self, filename, format='csv', filters=None):
        """Export jobs to CSV or JSON"""
        import pandas as pd

        jobs = self.db.get_jobs(filters=filters, limit=10000)

        if not jobs:
            print("No jobs to export")
            return

        data = []
        for job in jobs:
            data.append({
                'Title': job.title,
                'Company': job.company,
                'Location': job.location,
                'Description': job.description[:200] + '...' if len(job.description) > 200 else job.description,
                'URL': job.url,
                'Source': job.source,
                'Posted Date': job.posted_date,
                'Job Type': job.job_type,
                'Salary': job.salary,
                'Tags': job.tags,
                'Remote': job.remote,
                'Created At': job.created_at
            })

        df = pd.DataFrame(data)

        if format == 'csv':
            df.to_csv(filename, index=False)
        elif format == 'json':
            df.to_json(filename, orient='records', indent=2)

        print(f"Exported {len(data)} jobs to {filename}")

    def get_statistics(self):
        """Get database statistics"""
        from sqlalchemy import func
        from models import Job

        total = self.db.session.query(Job).count()

        by_source = {}
        for source, count in self.db.session.query(Job.source, func.count(Job.id)).group_by(Job.source).all():
            by_source[source] = count

        remote_count = self.db.session.query(Job).filter_by(remote=True).count()

        return {
            'total_jobs': total,
            'remote_jobs': remote_count,
            'by_source': by_source
        }

    def close(self):
        """Close database connection"""
        self.db.close()
