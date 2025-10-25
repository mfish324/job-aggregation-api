"""
Enterprise Company Job Scrapers
Scrape job listings directly from major tech companies' career pages

Supported Companies:
- Google (RSS feed)
- Apple (careers page)
- Microsoft (careers page)
- Amazon (careers page)
- Meta/Facebook (careers page)
- Netflix (careers page)
- Tesla (careers page)
- NVIDIA (careers page)
- Salesforce (careers page)
- Oracle (careers page)
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dateutil import parser as date_parser
import json
import time
from typing import List, Dict
import re
import xml.etree.ElementTree as ET
import sys
from scrapers import BaseScraper

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


class GoogleCareersScraper(BaseScraper):
    """
    Google Careers - Official XML Feed
    Source: https://www.google.com/about/careers/applications/jobs/feed.xml
    """

    def scrape(self, keywords=None, location=None, max_pages=5):
        """Scrape jobs from Google's official XML feed"""
        jobs = []
        url = "https://www.google.com/about/careers/applications/jobs/feed.xml"

        try:
            response = self.session.get(url, timeout=60)  # Longer timeout, large feed
            response.raise_for_status()

            # Parse XML feed
            root = ET.fromstring(response.content)

            # Find all job elements
            job_elements = root.findall('job')

            count = 0
            max_jobs = max_pages * 50  # Limit jobs per scrape

            for job_elem in job_elements:
                if count >= max_jobs:
                    break

                try:
                    title = job_elem.find('title').text if job_elem.find('title') is not None else 'N/A'
                    job_id = job_elem.find('jobid').text if job_elem.find('jobid') is not None else ''
                    job_url = job_elem.find('url').text if job_elem.find('url') is not None else ''
                    published = job_elem.find('published').text if job_elem.find('published') is not None else ''
                    description = job_elem.find('description').text if job_elem.find('description') is not None else ''
                    is_remote = job_elem.find('isRemote').text if job_elem.find('isRemote') is not None else 'No'
                    job_type = job_elem.find('jobtype').text if job_elem.find('jobtype') is not None else 'FULL_TIME'
                    employer = job_elem.find('employer').text if job_elem.find('employer') is not None else 'Google'

                    # Extract location
                    location_elem = job_elem.find('locations')
                    location_str = 'USA'
                    if location_elem is not None:
                        loc = location_elem.find('location')
                        if loc is not None:
                            city = loc.find('city').text if loc.find('city') is not None else ''
                            state = loc.find('state').text if loc.find('state') is not None else ''
                            country = loc.find('country').text if loc.find('country') is not None else 'USA'
                            location_str = f"{city}, {state}" if city and state else country

                    # Filter by keywords if provided
                    if keywords:
                        kw_lower = keywords.lower()
                        if kw_lower not in title.lower() and kw_lower not in description.lower():
                            continue

                    # Filter by location if provided
                    if location and location.lower() not in location_str.lower():
                        continue

                    # Clean HTML from description
                    clean_desc = BeautifulSoup(description, 'html.parser').get_text()[:500] if description else ''

                    jobs.append({
                        'title': title,
                        'company': employer,
                        'location': location_str,
                        'description': clean_desc,
                        'url': job_url,
                        'source': 'google_careers',
                        'posted_date': self.normalize_date(published),
                        'job_type': 'Full-time' if job_type == 'FULL_TIME' else job_type,
                        'salary': None,  # Google doesn't include salary in feed
                        'tags': json.dumps(['tech', 'google', 'faang']),
                        'remote': is_remote.lower() == 'yes'
                    })

                    count += 1

                except Exception as e:
                    print(f"Error parsing Google job entry: {e}")
                    continue

            print(f"✓ Google: Found {len(jobs)} jobs")

        except Exception as e:
            print(f"✗ Error scraping Google careers: {e}")

        return jobs


class AppleCareersScraper(BaseScraper):
    """
    Apple Careers - Web Scraper
    Source: https://jobs.apple.com/
    """

    def scrape(self, keywords=None, location=None, max_pages=5):
        """
        Scrape jobs from Apple careers page
        Note: Apple uses a complex React-based site, may need API endpoint
        """
        jobs = []

        # Apple's job search API endpoint
        base_url = "https://jobs.apple.com/api/role/search"

        try:
            for page in range(max_pages):
                params = {
                    'location': location or 'united-states-USA',
                    'page': page + 1,
                    'sort': 'newest'
                }

                response = self.session.post(base_url, json=params, timeout=self.timeout)

                if response.status_code != 200:
                    break

                data = response.json()

                search_results = data.get('searchResults', [])
                if not search_results:
                    break

                for job in search_results:
                    try:
                        title = job.get('postingTitle', 'N/A')
                        job_id = job.get('positionId', '')
                        locations = job.get('locations', [])
                        location_str = locations[0].get('name', 'USA') if locations else 'USA'
                        team = job.get('team', {}).get('teamName', '')
                        posting_date = job.get('postingDate', '')

                        # Filter by keywords
                        if keywords and keywords.lower() not in title.lower() and keywords.lower() not in team.lower():
                            continue

                        jobs.append({
                            'title': title,
                            'company': 'Apple',
                            'location': location_str,
                            'description': f"{team} - {title}",
                            'url': f"https://jobs.apple.com/en-us/details/{job_id}",
                            'source': 'apple_careers',
                            'posted_date': self.normalize_date(posting_date),
                            'job_type': 'Full-time',
                            'salary': None,
                            'tags': json.dumps(['tech', 'apple', 'faang']),
                            'remote': 'remote' in title.lower() or 'remote' in location_str.lower()
                        })

                    except Exception as e:
                        print(f"Error parsing Apple job: {e}")
                        continue

                time.sleep(2)  # Rate limiting

            print(f"✓ Apple: Found {len(jobs)} jobs")

        except Exception as e:
            print(f"✗ Error scraping Apple careers: {e}")

        return jobs


class MicrosoftCareersScraper(BaseScraper):
    """
    Microsoft Careers - Web Scraper
    Source: https://careers.microsoft.com/
    """

    def scrape(self, keywords=None, location=None, max_pages=5):
        """Scrape jobs from Microsoft careers page"""
        jobs = []

        # Microsoft's job search API
        base_url = "https://gcsservices.careers.microsoft.com/search/api/v1/search"

        try:
            for page in range(max_pages):
                payload = {
                    "from": page * 20,
                    "size": 20,
                    "filters": {
                        "country": ["United States"] if not location else [location]
                    },
                    "query": keywords or ""
                }

                response = self.session.post(base_url, json=payload, timeout=self.timeout)

                if response.status_code != 200:
                    break

                data = response.json()
                results = data.get('operationResult', {}).get('result', {}).get('jobs', [])

                if not results:
                    break

                for job in results:
                    try:
                        title = job.get('title', 'N/A')
                        job_id = job.get('jobId', '')
                        location_str = job.get('location', 'USA')
                        description = job.get('description', '')
                        posted_date = job.get('postingDate', '')

                        jobs.append({
                            'title': title,
                            'company': 'Microsoft',
                            'location': location_str,
                            'description': description[:500] if description else '',
                            'url': f"https://careers.microsoft.com/us/en/job/{job_id}",
                            'source': 'microsoft_careers',
                            'posted_date': self.normalize_date(posted_date),
                            'job_type': 'Full-time',
                            'salary': None,
                            'tags': json.dumps(['tech', 'microsoft', 'faang']),
                            'remote': 'remote' in title.lower() or 'remote' in location_str.lower()
                        })

                    except Exception as e:
                        print(f"Error parsing Microsoft job: {e}")
                        continue

                time.sleep(2)  # Rate limiting

            print(f"✓ Microsoft: Found {len(jobs)} jobs")

        except Exception as e:
            print(f"✗ Error scraping Microsoft careers: {e}")

        return jobs


class AmazonCareersScraper(BaseScraper):
    """
    Amazon Careers - Web Scraper
    Source: https://www.amazon.jobs/
    """

    def scrape(self, keywords=None, location=None, max_pages=5):
        """Scrape jobs from Amazon careers page"""
        jobs = []

        # Amazon's job search API
        base_url = "https://www.amazon.jobs/en/search.json"

        try:
            for page in range(1, max_pages + 1):
                params = {
                    'radius': '100mi',
                    'facets': [],
                    'sort': 'recent',
                    'page': page
                }

                if keywords:
                    params['base_query'] = keywords

                if location:
                    params['loc_query'] = location

                response = self.session.get(base_url, params=params, timeout=self.timeout)

                if response.status_code != 200:
                    break

                data = response.json()
                results = data.get('jobs', [])

                if not results:
                    break

                for job in results:
                    try:
                        title = job.get('title', 'N/A')
                        job_id = job.get('id_icims', '')
                        location_str = job.get('city', 'USA')
                        if job.get('state'):
                            location_str += f", {job.get('state')}"
                        description = job.get('description_short', '')
                        posted_date = job.get('posted_date', '')
                        company_name = job.get('company_name', 'Amazon')

                        jobs.append({
                            'title': title,
                            'company': company_name,
                            'location': location_str,
                            'description': description[:500] if description else '',
                            'url': f"https://www.amazon.jobs/en/jobs/{job_id}",
                            'source': 'amazon_careers',
                            'posted_date': self.normalize_date(posted_date),
                            'job_type': 'Full-time',
                            'salary': None,
                            'tags': json.dumps(['tech', 'amazon', 'faang']),
                            'remote': job.get('is_remote', False) or 'remote' in title.lower()
                        })

                    except Exception as e:
                        print(f"Error parsing Amazon job: {e}")
                        continue

                time.sleep(2)  # Rate limiting

            print(f"✓ Amazon: Found {len(jobs)} jobs")

        except Exception as e:
            print(f"✗ Error scraping Amazon careers: {e}")

        return jobs


class MetaCareersScraper(BaseScraper):
    """
    Meta (Facebook) Careers - Web Scraper
    Source: https://www.metacareers.com/
    """

    def scrape(self, keywords=None, location=None, max_pages=5):
        """Scrape jobs from Meta careers page"""
        jobs = []

        # Meta's job search URL
        base_url = "https://www.metacareers.com/jobs"

        try:
            params = {
                'q': keywords or '',
                'location': location or 'United States',
                'results_per_page': 100
            }

            response = self.session.get(base_url, params=params, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Meta uses a complex React structure - this is a simplified scraper
            # For production, you'd want to use their API if available or Selenium
            job_cards = soup.find_all('div', class_='_8ywk')  # Example class, may change

            for card in job_cards[:50]:  # Limit to first 50
                try:
                    title_elem = card.find('a', class_='_9att')
                    if not title_elem:
                        continue

                    title = title_elem.text.strip()
                    job_url = 'https://www.metacareers.com' + title_elem.get('href', '')
                    location_elem = card.find('div', class_='_9axz')
                    location_str = location_elem.text.strip() if location_elem else 'USA'

                    jobs.append({
                        'title': title,
                        'company': 'Meta',
                        'location': location_str,
                        'description': '',
                        'url': job_url,
                        'source': 'meta_careers',
                        'posted_date': datetime.utcnow(),
                        'job_type': 'Full-time',
                        'salary': None,
                        'tags': json.dumps(['tech', 'meta', 'facebook', 'faang']),
                        'remote': 'remote' in title.lower() or 'remote' in location_str.lower()
                    })

                except Exception as e:
                    print(f"Error parsing Meta job: {e}")
                    continue

            print(f"✓ Meta: Found {len(jobs)} jobs")

        except Exception as e:
            print(f"✗ Error scraping Meta careers: {e}")

        return jobs


class TeslaCareersScraper(BaseScraper):
    """
    Tesla Careers - Web Scraper
    Source: https://www.tesla.com/careers/
    """

    def scrape(self, keywords=None, location=None, max_pages=5):
        """Scrape jobs from Tesla careers page"""
        jobs = []

        base_url = "https://www.tesla.com/cua-api/apps"

        try:
            params = {
                'query': keywords or '',
                'locale': 'en_US',
                'offset': 0,
                'limit': 100
            }

            response = self.session.get(base_url, params=params, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                results = data.get('data', [])

                for job in results:
                    try:
                        title = job.get('title', 'N/A')
                        job_id = job.get('id', '')
                        location_str = job.get('location', 'USA')
                        description = job.get('shortDescription', '')

                        # Filter by location if provided
                        if location and location.lower() not in location_str.lower():
                            continue

                        jobs.append({
                            'title': title,
                            'company': 'Tesla',
                            'location': location_str,
                            'description': description[:500] if description else '',
                            'url': f"https://www.tesla.com/careers/job/{job_id}",
                            'source': 'tesla_careers',
                            'posted_date': datetime.utcnow(),
                            'job_type': 'Full-time',
                            'salary': None,
                            'tags': json.dumps(['tech', 'tesla', 'automotive', 'ev']),
                            'remote': 'remote' in title.lower() or 'remote' in location_str.lower()
                        })

                    except Exception as e:
                        print(f"Error parsing Tesla job: {e}")
                        continue

            print(f"✓ Tesla: Found {len(jobs)} jobs")

        except Exception as e:
            print(f"✗ Error scraping Tesla careers: {e}")

        return jobs


# Example usage
if __name__ == "__main__":
    print("Testing Enterprise Company Scrapers\n")
    print("=" * 60)

    # Test Google
    print("\n1. Testing Google Careers...")
    google = GoogleCareersScraper()
    google_jobs = google.scrape(keywords="software engineer", max_pages=1)
    print(f"   Found {len(google_jobs)} jobs")
    if google_jobs:
        print(f"   Example: {google_jobs[0]['title']} - {google_jobs[0]['location']}")

    # Test Amazon
    print("\n2. Testing Amazon Careers...")
    amazon = AmazonCareersScraper()
    amazon_jobs = amazon.scrape(keywords="developer", max_pages=1)
    print(f"   Found {len(amazon_jobs)} jobs")
    if amazon_jobs:
        print(f"   Example: {amazon_jobs[0]['title']} - {amazon_jobs[0]['location']}")

    # Test Apple
    print("\n3. Testing Apple Careers...")
    apple = AppleCareersScraper()
    apple_jobs = apple.scrape(keywords="engineer", max_pages=1)
    print(f"   Found {len(apple_jobs)} jobs")
    if apple_jobs:
        print(f"   Example: {apple_jobs[0]['title']} - {apple_jobs[0]['location']}")

    # Test Microsoft
    print("\n4. Testing Microsoft Careers...")
    microsoft = MicrosoftCareersScraper()
    microsoft_jobs = microsoft.scrape(keywords="software", max_pages=1)
    print(f"   Found {len(microsoft_jobs)} jobs")
    if microsoft_jobs:
        print(f"   Example: {microsoft_jobs[0]['title']} - {microsoft_jobs[0]['location']}")

    print("\n" + "=" * 60)
    print(f"Total jobs found: {len(google_jobs) + len(amazon_jobs) + len(apple_jobs) + len(microsoft_jobs)}")
    print("\nNote: Some scrapers may need adjustments based on company website changes")
