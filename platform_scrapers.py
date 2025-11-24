"""
Platform-Specific Scraper Templates
Generic scrapers for common ATS platforms (Greenhouse, Lever, Workday, etc.)
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
from typing import List, Dict, Optional
from scrapers import BaseScraper
from skill_extractor import extract_skills, skills_to_json


class GreenhouseScraper(BaseScraper):
    """
    Generic Greenhouse scraper
    Works with any company using Greenhouse (boards.greenhouse.io or jobs.greenhouse.io)
    """

    def __init__(self, company_name: str, board_token: str, company_website: str = None):
        """
        Args:
            company_name: Company name
            board_token: Greenhouse board token (from URL)
            company_website: Company website URL
        """
        super().__init__()
        self.company_name = company_name
        self.board_token = board_token
        self.company_website = company_website
        self.api_url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"

    def scrape(self, keywords=None, location=None, max_pages=5):
        """Scrape jobs from Greenhouse board"""
        jobs = []

        try:
            # Greenhouse API returns all jobs at once
            response = self.session.get(self.api_url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            for job in data.get('jobs', []):
                try:
                    title = job.get('title', 'N/A')
                    job_id = job.get('id', '')
                    location_obj = job.get('location', {})
                    location_str = location_obj.get('name', 'Not specified') if isinstance(location_obj, dict) else str(location_obj)

                    # Filter by keywords
                    if keywords and keywords.lower() not in title.lower():
                        continue

                    # Filter by location
                    if location and location.lower() not in location_str.lower():
                        continue

                    # Extract content and metadata
                    content = job.get('content', '')
                    updated_at = job.get('updated_at', '')

                    # Extract skills
                    combined_text = f"{title} {content}"
                    skills = extract_skills(combined_text)
                    skills.append(self.company_name.lower().replace(' ', '_'))

                    jobs.append({
                        'title': title,
                        'company': self.company_name,
                        'location': location_str,
                        'description': content[:500] if content else '',
                        'url': f"https://boards.greenhouse.io/{self.board_token}/jobs/{job_id}",
                        'source': f'{self.company_name.lower().replace(" ", "_")}_greenhouse',
                        'posted_date': self.normalize_date(updated_at),
                        'job_type': 'Full-time',
                        'salary': None,
                        'company_website': self.company_website,
                        'tags': skills_to_json(skills),
                        'remote': 'remote' in title.lower() or 'remote' in location_str.lower()
                    })

                except Exception as e:
                    print(f"Error parsing Greenhouse job: {e}")
                    continue

            print(f"✓ {self.company_name} (Greenhouse): Found {len(jobs)} jobs")

        except Exception as e:
            print(f"✗ Error scraping {self.company_name} Greenhouse: {e}")

        return jobs


class LeverScraper(BaseScraper):
    """
    Generic Lever scraper
    Works with any company using Lever (jobs.lever.co)
    """

    def __init__(self, company_name: str, lever_site: str, company_website: str = None):
        """
        Args:
            company_name: Company name
            lever_site: Lever site identifier (from URL: jobs.lever.co/{lever_site})
            company_website: Company website URL
        """
        super().__init__()
        self.company_name = company_name
        self.lever_site = lever_site
        self.company_website = company_website
        self.api_url = f"https://api.lever.co/v0/postings/{lever_site}"

    def scrape(self, keywords=None, location=None, max_pages=5):
        """Scrape jobs from Lever board"""
        jobs = []

        try:
            params = {'mode': 'json'}
            response = self.session.get(self.api_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            for job in data:
                try:
                    title = job.get('text', 'N/A')
                    job_id = job.get('id', '')
                    categories = job.get('categories', {})
                    location_str = categories.get('location', 'Not specified')

                    # Filter by keywords
                    if keywords and keywords.lower() not in title.lower():
                        continue

                    # Filter by location
                    if location and location.lower() not in location_str.lower():
                        continue

                    description = job.get('description', '')
                    created_at = job.get('createdAt', '')
                    job_url = job.get('hostedUrl', f"https://jobs.lever.co/{self.lever_site}/{job_id}")

                    # Extract skills
                    combined_text = f"{title} {description}"
                    skills = extract_skills(combined_text)
                    skills.append(self.company_name.lower().replace(' ', '_'))

                    jobs.append({
                        'title': title,
                        'company': self.company_name,
                        'location': location_str,
                        'description': description[:500] if description else '',
                        'url': job_url,
                        'source': f'{self.company_name.lower().replace(" ", "_")}_lever',
                        'posted_date': self.normalize_date(created_at),
                        'job_type': categories.get('commitment', 'Full-time'),
                        'salary': None,
                        'company_website': self.company_website,
                        'tags': skills_to_json(skills),
                        'remote': 'remote' in title.lower() or 'remote' in location_str.lower()
                    })

                except Exception as e:
                    print(f"Error parsing Lever job: {e}")
                    continue

            print(f"✓ {self.company_name} (Lever): Found {len(jobs)} jobs")

        except Exception as e:
            print(f"✗ Error scraping {self.company_name} Lever: {e}")

        return jobs


class AshbyHQScraper(BaseScraper):
    """
    Generic AshbyHQ scraper
    Works with companies using Ashby (jobs.ashbyhq.com)
    """

    def __init__(self, company_name: str, ashby_site: str, company_website: str = None):
        """
        Args:
            company_name: Company name
            ashby_site: Ashby site identifier
            company_website: Company website URL
        """
        super().__init__()
        self.company_name = company_name
        self.ashby_site = ashby_site
        self.company_website = company_website
        self.api_url = f"https://jobs.ashbyhq.com/{ashby_site}"

    def scrape(self, keywords=None, location=None, max_pages=5):
        """Scrape jobs from Ashby board"""
        jobs = []

        try:
            response = self.session.get(self.api_url, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Ashby uses a specific class structure
            job_cards = soup.find_all('a', class_='ashby-job-posting-brief')

            for card in job_cards:
                try:
                    title_elem = card.find('h3')
                    title = title_elem.text.strip() if title_elem else 'N/A'

                    # Filter by keywords
                    if keywords and keywords.lower() not in title.lower():
                        continue

                    location_elem = card.find('div', class_='location')
                    location_str = location_elem.text.strip() if location_elem else 'Not specified'

                    # Filter by location
                    if location and location.lower() not in location_str.lower():
                        continue

                    job_url = card.get('href', '')
                    if job_url and not job_url.startswith('http'):
                        job_url = f"https://jobs.ashbyhq.com{job_url}"

                    # Extract skills
                    skills = extract_skills(title)
                    skills.append(self.company_name.lower().replace(' ', '_'))

                    jobs.append({
                        'title': title,
                        'company': self.company_name,
                        'location': location_str,
                        'description': '',
                        'url': job_url,
                        'source': f'{self.company_name.lower().replace(" ", "_")}_ashby',
                        'posted_date': datetime.utcnow(),
                        'job_type': 'Full-time',
                        'salary': None,
                        'company_website': self.company_website,
                        'tags': skills_to_json(skills),
                        'remote': 'remote' in title.lower() or 'remote' in location_str.lower()
                    })

                except Exception as e:
                    continue

            print(f"✓ {self.company_name} (Ashby): Found {len(jobs)} jobs")

        except Exception as e:
            print(f"✗ Error scraping {self.company_name} Ashby: {e}")

        return jobs


class TaleoScraper(BaseScraper):
    """
    Generic Taleo scraper
    Works with companies using Oracle Taleo
    """

    def __init__(self, company_name: str, taleo_site_url: str, company_website: str = None):
        """
        Args:
            company_name: Company name
            taleo_site_url: Full Taleo site URL
            company_website: Company website URL
        """
        super().__init__()
        self.company_name = company_name
        self.taleo_site_url = taleo_site_url
        self.company_website = company_website

    def scrape(self, keywords=None, location=None, max_pages=5):
        """Scrape jobs from Taleo site"""
        jobs = []

        try:
            # Taleo uses various URL patterns, try to find the job search API
            # Common pattern: /careersection/jobsearch.ftl or /api/jobs

            # Try to scrape HTML job listings
            response = self.session.get(self.taleo_site_url, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Taleo uses various class names, try common ones
            job_links = soup.find_all('a', href=True)

            for link in job_links:
                try:
                    # Look for job posting links
                    href = link.get('href', '')
                    if 'jobdetail' in href.lower() or 'requisition' in href.lower():
                        title = link.text.strip()

                        if not title or len(title) < 3:
                            continue

                        # Filter by keywords
                        if keywords and keywords.lower() not in title.lower():
                            continue

                        # Build full URL
                        if href.startswith('http'):
                            job_url = href
                        elif href.startswith('/'):
                            base = self.taleo_site_url.split('/careersection')[0]
                            job_url = f"{base}{href}"
                        else:
                            job_url = f"{self.taleo_site_url}/{href}"

                        # Extract skills
                        skills = extract_skills(title)
                        skills.append(self.company_name.lower().replace(' ', '_'))
                        skills.append('taleo')

                        jobs.append({
                            'title': title,
                            'company': self.company_name,
                            'location': 'Not specified',
                            'description': '',
                            'url': job_url,
                            'source': f'{self.company_name.lower().replace(" ", "_")}_taleo',
                            'posted_date': datetime.utcnow(),
                            'job_type': 'Full-time',
                            'salary': None,
                            'company_website': self.company_website,
                            'tags': skills_to_json(skills),
                            'remote': 'remote' in title.lower()
                        })

                        if len(jobs) >= 50:  # Limit to avoid too many results
                            break

                except Exception as e:
                    continue

            print(f"✓ {self.company_name} (Taleo): Found {len(jobs)} jobs")

        except Exception as e:
            print(f"✗ Error scraping {self.company_name} Taleo: {e}")

        return jobs


class iCIMSScraper(BaseScraper):
    """
    Generic iCIMS scraper
    Works with companies using iCIMS Talent Cloud
    """

    def __init__(self, company_name: str, icims_site_url: str, company_website: str = None):
        """
        Args:
            company_name: Company name
            icims_site_url: Full iCIMS site URL
            company_website: Company website URL
        """
        super().__init__()
        self.company_name = company_name
        self.icims_site_url = icims_site_url
        self.company_website = company_website

    def scrape(self, keywords=None, location=None, max_pages=5):
        """Scrape jobs from iCIMS site"""
        jobs = []

        try:
            # iCIMS typically has an API or structured search page
            response = self.session.get(self.icims_site_url, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # iCIMS uses various class names for job listings
            # Common patterns: class="iCIMS_JobsTable", "iCIMS_JobContent"
            job_rows = soup.find_all('tr', class_=lambda x: x and 'job' in x.lower())

            if not job_rows:
                # Try alternative selectors
                job_rows = soup.find_all('div', class_=lambda x: x and ('job' in str(x).lower() or 'position' in str(x).lower()))

            for row in job_rows:
                try:
                    # Find title link
                    title_link = row.find('a', href=True)
                    if not title_link:
                        continue

                    title = title_link.text.strip()

                    if not title or len(title) < 3:
                        continue

                    # Filter by keywords
                    if keywords and keywords.lower() not in title.lower():
                        continue

                    # Get job URL
                    href = title_link.get('href', '')
                    if href.startswith('http'):
                        job_url = href
                    elif href.startswith('/'):
                        base = self.icims_site_url.split('/jobs')[0]
                        job_url = f"{base}{href}"
                    else:
                        job_url = f"{self.icims_site_url}/{href}"

                    # Try to find location
                    location_str = 'Not specified'
                    location_elem = row.find(class_=lambda x: x and 'location' in str(x).lower())
                    if location_elem:
                        location_str = location_elem.text.strip()

                    # Extract skills
                    skills = extract_skills(title)
                    skills.append(self.company_name.lower().replace(' ', '_'))
                    skills.append('icims')

                    jobs.append({
                        'title': title,
                        'company': self.company_name,
                        'location': location_str,
                        'description': '',
                        'url': job_url,
                        'source': f'{self.company_name.lower().replace(" ", "_")}_icims',
                        'posted_date': datetime.utcnow(),
                        'job_type': 'Full-time',
                        'salary': None,
                        'company_website': self.company_website,
                        'tags': skills_to_json(skills),
                        'remote': 'remote' in title.lower() or 'remote' in location_str.lower()
                    })

                    if len(jobs) >= 50:  # Limit results
                        break

                except Exception as e:
                    continue

            print(f"✓ {self.company_name} (iCIMS): Found {len(jobs)} jobs")

        except Exception as e:
            print(f"✗ Error scraping {self.company_name} iCIMS: {e}")

        return jobs


def create_scraper_for_platform(company: Dict, platform: str):
    """
    Factory function to create appropriate scraper for a company

    Args:
        company: Dict with name, website, careers_url
        platform: Platform type (greenhouse, lever, workday, ashby, etc.)

    Returns:
        Scraper instance or None
    """
    name = company['name']
    careers_url = company['careers_url']
    website = company['website']

    if platform == 'greenhouse':
        # Extract board token from URL
        # Format: boards.greenhouse.io/{token} or boards.greenhouse.io/{company}/{token}
        import re
        import requests

        # First try to extract from careers_url directly
        match = re.search(r'greenhouse\.io/([^/]+)(?:/([^/]+))?', careers_url)
        if match:
            board_token = match.group(2) if match.group(2) else match.group(1)
            return GreenhouseScraper(name, board_token, website)

        # If not found, visit the careers page to find redirect or embedded URL
        try:
            response = requests.get(careers_url, timeout=10, allow_redirects=True)
            final_url = response.url

            # Check if redirected to greenhouse
            if 'greenhouse.io' in final_url:
                match = re.search(r'greenhouse\.io/([^/]+)(?:/([^/]+))?', final_url)
                if match:
                    board_token = match.group(2) if match.group(2) else match.group(1)
                    return GreenhouseScraper(name, board_token, website)

            # Check page content for greenhouse embed
            content = response.text
            match = re.search(r'greenhouse\.io/([^/"\']+)', content)
            if match:
                board_token = match.group(1)
                return GreenhouseScraper(name, board_token, website)

        except Exception as e:
            print(f"⚠ {name}: Could not extract Greenhouse token: {e}")

    elif platform == 'lever':
        # Extract lever site from URL
        # Format: jobs.lever.co/{site}
        import re
        import requests

        # First try to extract from careers_url directly
        match = re.search(r'lever\.co/([^/]+)', careers_url)
        if match:
            lever_site = match.group(1)
            return LeverScraper(name, lever_site, website)

        # If not found, visit the careers page to find redirect or embedded URL
        try:
            response = requests.get(careers_url, timeout=10, allow_redirects=True)
            final_url = response.url

            # Check if redirected to lever
            if 'lever.co' in final_url:
                match = re.search(r'lever\.co/([^/]+)', final_url)
                if match:
                    lever_site = match.group(1)
                    return LeverScraper(name, lever_site, website)

            # Check page content for lever embed
            content = response.text
            match = re.search(r'jobs\.lever\.co/([^/"\']+)', content)
            if match:
                lever_site = match.group(1)
                return LeverScraper(name, lever_site, website)

        except Exception as e:
            print(f"⚠ {name}: Could not extract Lever site: {e}")

    elif platform == 'ashbyhq':
        # Extract ashby site from URL
        # Format: jobs.ashbyhq.com/{site}
        import re
        import requests

        # First try to extract from careers_url directly
        match = re.search(r'ashbyhq\.com/([^/]+)', careers_url)
        if match:
            ashby_site = match.group(1)
            return AshbyHQScraper(name, ashby_site, website)

        # If not found, visit the careers page to find redirect or embedded URL
        try:
            response = requests.get(careers_url, timeout=10, allow_redirects=True)
            final_url = response.url

            # Check if redirected to ashby
            if 'ashbyhq.com' in final_url:
                match = re.search(r'ashbyhq\.com/([^/]+)', final_url)
                if match:
                    ashby_site = match.group(1)
                    return AshbyHQScraper(name, ashby_site, website)

            # Check page content for ashby embed
            content = response.text
            match = re.search(r'jobs\.ashbyhq\.com/([^/"\']+)', content)
            if match:
                ashby_site = match.group(1)
                return AshbyHQScraper(name, ashby_site, website)

        except Exception as e:
            print(f"⚠ {name}: Could not extract Ashby site: {e}")

    elif platform == 'workday':
        # Already have workday scraper, need to add company to config
        print(f"⚠ {name}: Workday scraper needs manual configuration")
        return None

    elif platform == 'taleo':
        # Taleo uses various URL patterns - follow redirects to find actual job search page
        import requests
        try:
            response = requests.get(careers_url, timeout=10, allow_redirects=True)
            final_url = response.url
            # Use the redirected URL if it's a taleo site
            if 'taleo.net' in final_url or 'careersection' in final_url:
                return TaleoScraper(name, final_url, website)
        except:
            pass
        return TaleoScraper(name, careers_url, website)

    elif platform == 'icims':
        # iCIMS uses various URL patterns - follow redirects to find actual job search page
        import requests
        try:
            response = requests.get(careers_url, timeout=10, allow_redirects=True)
            final_url = response.url
            # Use the redirected URL if it's an iCIMS site
            if 'icims.com' in final_url:
                return iCIMSScraper(name, final_url, website)
        except:
            pass
        return iCIMSScraper(name, careers_url, website)

    else:
        print(f"⚠ {name}: Platform '{platform}' not yet supported")
        return None


# Test function
if __name__ == "__main__":
    print("Testing Platform Scrapers\n")
    print("="*80)

    # Test Greenhouse (example: Webflow)
    print("\n1. Testing Greenhouse scraper...")
    greenhouse = GreenhouseScraper(
        company_name="Webflow",
        board_token="webflow",
        company_website="https://webflow.com"
    )
    jobs = greenhouse.scrape(max_pages=1)
    if jobs:
        print(f"   Sample: {jobs[0]['title']} - {jobs[0]['location']}")

    print("\n" + "="*80)
