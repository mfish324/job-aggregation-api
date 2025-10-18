import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dateutil import parser as date_parser
import json
import time
from abc import ABC, abstractmethod
from typing import List, Dict
import re


class BaseScraper(ABC):
    """Base class for all job scrapers"""

    def __init__(self, timeout=30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    @abstractmethod
    def scrape(self, keywords=None, location=None, max_pages=5) -> List[Dict]:
        """Scrape jobs from the source"""
        pass

    def normalize_date(self, date_str):
        """Normalize various date formats to datetime"""
        if not date_str:
            return datetime.utcnow()

        try:
            # Handle relative dates like "2 days ago"
            if 'ago' in str(date_str).lower():
                numbers = re.findall(r'\d+', str(date_str))
                if numbers:
                    days = int(numbers[0])
                    return datetime.utcnow() - timedelta(days=days)

            # Try parsing standard formats
            return date_parser.parse(date_str)
        except:
            return datetime.utcnow()


class AdzunaScraper(BaseScraper):
    """Adzuna API - requires free API key"""

    def __init__(self, app_id, app_key, timeout=30):
        super().__init__(timeout)
        self.app_id = app_id
        self.app_key = app_key
        self.base_url = "https://api.adzuna.com/v1/api/jobs"

    def scrape(self, keywords=None, location=None, max_pages=5):
        jobs = []
        country = "us"  # Can be parameterized

        for page in range(1, max_pages + 1):
            try:
                url = f"{self.base_url}/{country}/search/{page}"
                params = {
                    'app_id': self.app_id,
                    'app_key': self.app_key,
                    'results_per_page': 50,
                    'what': keywords or '',
                    'where': location or ''
                }

                response = self.session.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()

                for job in data.get('results', []):
                    jobs.append({
                        'title': job.get('title', 'N/A'),
                        'company': job.get('company', {}).get('display_name', 'N/A'),
                        'location': job.get('location', {}).get('display_name', 'N/A'),
                        'description': job.get('description', ''),
                        'url': job.get('redirect_url', ''),
                        'source': 'adzuna',
                        'posted_date': self.normalize_date(job.get('created')),
                        'job_type': job.get('contract_time', 'N/A'),
                        'salary': f"${job.get('salary_min', 0)}-${job.get('salary_max', 0)}" if job.get('salary_min') else None,
                        'tags': json.dumps(job.get('category', {}).get('tag', '')),
                        'remote': 'remote' in job.get('location', {}).get('display_name', '').lower()
                    })

                time.sleep(1)  # Rate limiting
            except Exception as e:
                print(f"Error scraping Adzuna page {page}: {e}")
                break

        return jobs


class RemoteOKScraper(BaseScraper):
    """RemoteOK - public API, no key needed"""

    def scrape(self, keywords=None, location=None, max_pages=5):
        jobs = []
        try:
            url = "https://remoteok.com/api"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            # First item is metadata, skip it
            for job in data[1:]:
                if keywords and keywords.lower() not in json.dumps(job).lower():
                    continue

                # Parse date safely
                job_date = job.get('date')
                try:
                    if isinstance(job_date, (int, float)):
                        posted_date = datetime.fromtimestamp(job_date)
                    elif isinstance(job_date, str):
                        posted_date = self.normalize_date(job_date)
                    else:
                        posted_date = datetime.utcnow()
                except:
                    posted_date = datetime.utcnow()

                jobs.append({
                    'title': job.get('position', 'N/A'),
                    'company': job.get('company', 'N/A'),
                    'location': job.get('location', 'Remote'),
                    'description': job.get('description', ''),
                    'url': f"https://remoteok.com/remote-jobs/{job.get('id', '')}",
                    'source': 'remoteok',
                    'posted_date': posted_date,
                    'job_type': 'Full-time',
                    'salary': None,
                    'tags': json.dumps(job.get('tags', [])),
                    'remote': True
                })
        except Exception as e:
            print(f"Error scraping RemoteOK: {e}")

        return jobs


class WeWorkRemotelyScraper(BaseScraper):
    """We Work Remotely - scrapes public listings"""

    def scrape(self, keywords=None, location=None, max_pages=5):
        jobs = []
        categories = ['programming', 'design', 'marketing', 'product', 'customer-support']

        for category in categories:
            try:
                url = f"https://weworkremotely.com/categories/remote-{category}-jobs"
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                # Use lxml parser to avoid XML warning
                soup = BeautifulSoup(response.text, 'lxml')

                for job_elem in soup.find_all('li', class_='feature'):
                    try:
                        title_elem = job_elem.find('span', class_='title')
                        company_elem = job_elem.find('span', class_='company')
                        link_elem = job_elem.find('a')

                        if not title_elem or not company_elem:
                            continue

                        title = title_elem.text.strip()
                        company = company_elem.text.strip()

                        if keywords and keywords.lower() not in title.lower():
                            continue

                        jobs.append({
                            'title': title,
                            'company': company,
                            'location': 'Remote',
                            'description': '',
                            'url': f"https://weworkremotely.com{link_elem['href']}" if link_elem else '',
                            'source': 'weworkremotely',
                            'posted_date': datetime.utcnow(),
                            'job_type': 'Full-time',
                            'salary': None,
                            'tags': json.dumps([category]),
                            'remote': True
                        })
                    except Exception as e:
                        continue

                time.sleep(2)  # Be respectful
            except Exception as e:
                print(f"Error scraping WeWorkRemotely {category}: {e}")

        return jobs


class RemotiveScraper(BaseScraper):
    """Remotive - public API"""

    def scrape(self, keywords=None, location=None, max_pages=5):
        jobs = []
        try:
            url = "https://remotive.com/api/remote-jobs"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            for job in data.get('jobs', []):
                if keywords and keywords.lower() not in json.dumps(job).lower():
                    continue

                jobs.append({
                    'title': job.get('title', 'N/A'),
                    'company': job.get('company_name', 'N/A'),
                    'location': 'Remote',
                    'description': job.get('description', ''),
                    'url': job.get('url', ''),
                    'source': 'remotive',
                    'posted_date': self.normalize_date(job.get('publication_date')),
                    'job_type': job.get('job_type', 'N/A'),
                    'salary': job.get('salary', None),
                    'tags': json.dumps([job.get('category', '')]),
                    'remote': True
                })
        except Exception as e:
            print(f"Error scraping Remotive: {e}")

        return jobs


class AuthenticJobsScraper(BaseScraper):
    """Authentic Jobs - RSS feed"""

    def scrape(self, keywords=None, location=None, max_pages=5):
        jobs = []
        try:
            url = "https://authenticjobs.com/rss"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'xml')

            for item in soup.find_all('item'):
                try:
                    title = item.find('title').text if item.find('title') else 'N/A'
                    description = item.find('description').text if item.find('description') else ''
                    link = item.find('link').text if item.find('link') else ''
                    pub_date = item.find('pubDate').text if item.find('pubDate') else None

                    if keywords and keywords.lower() not in title.lower():
                        continue

                    # Parse company from title (usually format: "Job Title at Company")
                    company = 'N/A'
                    if ' at ' in title:
                        parts = title.split(' at ')
                        title = parts[0].strip()
                        company = parts[1].strip()

                    jobs.append({
                        'title': title,
                        'company': company,
                        'location': 'N/A',
                        'description': description,
                        'url': link,
                        'source': 'authenticjobs',
                        'posted_date': self.normalize_date(pub_date),
                        'job_type': 'N/A',
                        'salary': None,
                        'tags': json.dumps([]),
                        'remote': False
                    })
                except Exception as e:
                    continue
        except Exception as e:
            print(f"Error scraping Authentic Jobs: {e}")

        return jobs


class GitHubJobsScraper(BaseScraper):
    """GitHub Jobs alternative - using GitHub search for job postings"""

    def __init__(self, github_token=None, timeout=30):
        super().__init__(timeout)
        self.github_token = github_token
        if github_token:
            self.session.headers.update({'Authorization': f'token {github_token}'})

    def scrape(self, keywords=None, location=None, max_pages=5):
        jobs = []
        # Search for repositories tagged with 'jobs' or 'hiring'
        # This is a workaround since GitHub Jobs API was deprecated
        try:
            search_query = f"hiring {keywords or ''} in:readme in:description"
            url = "https://api.github.com/search/repositories"
            params = {
                'q': search_query,
                'sort': 'updated',
                'per_page': 30
            }

            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            for repo in data.get('items', [])[:50]:
                # Check if repo is actually a job posting
                if any(word in repo.get('description', '').lower() for word in ['hiring', 'job', 'career', 'position']):
                    jobs.append({
                        'title': repo.get('name', 'N/A').replace('-', ' ').title(),
                        'company': repo.get('owner', {}).get('login', 'N/A'),
                        'location': 'Remote',
                        'description': repo.get('description', ''),
                        'url': repo.get('html_url', ''),
                        'source': 'github',
                        'posted_date': self.normalize_date(repo.get('created_at')),
                        'job_type': 'N/A',
                        'salary': None,
                        'tags': json.dumps(repo.get('topics', [])),
                        'remote': True
                    })
        except Exception as e:
            print(f"Error scraping GitHub: {e}")

        return jobs


class IndeedScraper(BaseScraper):
    """Indeed - scrapes public job search results"""

    def scrape(self, keywords=None, location=None, max_pages=5):
        jobs = []

        # Default search parameters
        if not keywords:
            keywords = "software developer"
        if not location:
            location = "Remote"

        try:
            for page in range(max_pages):
                # Indeed uses start parameter (0, 10, 20, etc.)
                start = page * 10

                url = "https://www.indeed.com/jobs"
                params = {
                    'q': keywords,
                    'l': location,
                    'start': start,
                    'sort': 'date'  # Sort by date to get recent jobs
                }

                response = self.session.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'lxml')

                # Find job cards - Indeed uses various class names
                job_cards = soup.find_all('div', class_='job_seen_beacon')

                if not job_cards:
                    # Try alternative selectors
                    job_cards = soup.find_all('a', class_='jcs-JobTitle')

                for card in job_cards:
                    try:
                        # Extract job title
                        title_elem = card.find('h2', class_='jobTitle') or card.find('a', class_='jcs-JobTitle')
                        if not title_elem:
                            continue

                        # Get the actual title text (skip the span with 'new' badge)
                        title_span = title_elem.find('span', title=True)
                        if title_span:
                            title = title_span.get('title', title_elem.get_text(strip=True))
                        else:
                            title = title_elem.get_text(strip=True)

                        # Extract company name
                        company_elem = card.find('span', class_='companyName')
                        company = company_elem.get_text(strip=True) if company_elem else 'N/A'

                        # Extract location
                        location_elem = card.find('div', class_='companyLocation')
                        job_location = location_elem.get_text(strip=True) if location_elem else location

                        # Extract job link
                        link_elem = title_elem if title_elem.name == 'a' else title_elem.find('a')
                        job_id = link_elem.get('data-jk', '') if link_elem else ''
                        job_url = f"https://www.indeed.com/viewjob?jk={job_id}" if job_id else ''

                        # Extract snippet/description
                        snippet_elem = card.find('div', class_='job-snippet')
                        description = snippet_elem.get_text(strip=True) if snippet_elem else ''

                        # Extract salary if available
                        salary_elem = card.find('div', class_='salary-snippet')
                        salary = salary_elem.get_text(strip=True) if salary_elem else None

                        if title and company and job_url:
                            jobs.append({
                                'title': title,
                                'company': company,
                                'location': job_location,
                                'description': description,
                                'url': job_url,
                                'source': 'indeed',
                                'posted_date': datetime.utcnow(),  # Indeed doesn't always show exact dates
                                'job_type': 'N/A',
                                'salary': salary,
                                'tags': json.dumps([]),
                                'remote': 'remote' in job_location.lower()
                            })

                    except Exception as e:
                        continue

                # Be respectful with rate limiting
                time.sleep(2)

                # Stop if we didn't find any jobs
                if not job_cards:
                    break

        except Exception as e:
            print(f"Error scraping Indeed: {e}")

        return jobs


class AngelListScraper(BaseScraper):
    """AngelList/Wellfound - scrapes public startup jobs"""

    def scrape(self, keywords=None, location=None, max_pages=5):
        jobs = []
        # Note: AngelList requires more sophisticated scraping
        # This is a simplified version
        print("AngelList scraping requires authentication - skipping for now")
        return jobs


class CrunchboardScraper(BaseScraper):
    """TechCrunch Crunchboard jobs"""

    def scrape(self, keywords=None, location=None, max_pages=5):
        jobs = []
        try:
            url = "https://www.crunchboard.com/jobs"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')

            # Parse job listings (structure may vary)
            job_cards = soup.find_all('div', class_='job-card')

            for card in job_cards[:100]:
                try:
                    title_elem = card.find('h2') or card.find('h3')
                    company_elem = card.find(class_='company')
                    location_elem = card.find(class_='location')
                    link_elem = card.find('a')

                    if not title_elem:
                        continue

                    title = title_elem.text.strip()

                    if keywords and keywords.lower() not in title.lower():
                        continue

                    jobs.append({
                        'title': title,
                        'company': company_elem.text.strip() if company_elem else 'N/A',
                        'location': location_elem.text.strip() if location_elem else 'N/A',
                        'description': '',
                        'url': link_elem['href'] if link_elem and 'href' in link_elem.attrs else '',
                        'source': 'crunchboard',
                        'posted_date': datetime.utcnow(),
                        'job_type': 'N/A',
                        'salary': None,
                        'tags': json.dumps([]),
                        'remote': False
                    })
                except Exception as e:
                    continue
        except Exception as e:
            print(f"Error scraping Crunchboard: {e}")

        return jobs
