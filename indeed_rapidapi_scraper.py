"""
Indeed RapidAPI Scraper

Requires RapidAPI subscription to one of the Indeed APIs.
Add this to your scrapers.py or use as standalone module.
"""

import requests
import json
import time
import re
from datetime import datetime
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from urllib.parse import urlparse


class IndeedRapidAPIScraper:
    """
    Indeed via RapidAPI - Uses RapidAPI's Indeed job scraping services

    Setup:
    1. Sign up at https://rapidapi.com/
    2. Subscribe to one of these Indeed APIs:
       - "Indeed Jobs API" (https://rapidapi.com/vuesdata/api/indeed-jobs-api)
       - "Indeed jobs scraper API" (https://rapidapi.com/bebity-bebity-default/api/indeed-jobs-scraper-api)
    3. Get your RapidAPI key from your account
    4. Add to .env: RAPIDAPI_KEY=your_key_here
    5. Add to .env: RAPIDAPI_INDEED_HOST=indeed-jobs-api.p.rapidapi.com (or your chosen API host)

    Free tiers available:
    - Most Indeed APIs offer 25-100 free requests per month
    - No credit card required for basic plan
    """

    def __init__(self, api_key, api_host='indeed-jobs-api.p.rapidapi.com', timeout=30):
        """
        Initialize Indeed RapidAPI scraper

        Args:
            api_key: Your RapidAPI key
            api_host: The API host (depends on which Indeed API you subscribe to)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.api_host = api_host
        self.timeout = timeout

        self.session = requests.Session()
        self.session.headers.update({
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': self.api_host,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def scrape(self, keywords=None, location=None, max_pages=5):
        """
        Scrape jobs from Indeed via RapidAPI

        Args:
            keywords: Search keywords (e.g., "python developer")
            location: Job location (e.g., "Remote", "New York")
            max_pages: Maximum number of pages to scrape

        Returns:
            List of job dictionaries
        """
        jobs = []

        if not self.api_key:
            print("Indeed RapidAPI: No API key provided")
            return jobs

        # Default search parameters
        if not keywords:
            keywords = "software developer"
        if not location:
            location = "Remote"

        try:
            # API endpoint - varies by provider
            # For indeed-jobs-api.p.rapidapi.com, use /indeed-us/
            if 'indeed-jobs-api.p.rapidapi.com' in self.api_host:
                url = f"https://{self.api_host}/indeed-us/"
            else:
                url = f"https://{self.api_host}/"

            for page in range(max_pages):
                # Parameters format (offset increases by 10 for pagination)
                params = {
                    'keyword': keywords,
                    'location': location,
                    'offset': page * 10  # Offset increases by 10, not 15
                }

                try:
                    response = self.session.get(url, params=params, timeout=self.timeout)
                    response.raise_for_status()
                    data = response.json()

                    # Parse response - structure varies by API provider
                    # Common formats: {'results': [...]} or {'jobs': [...]} or direct array
                    results = self._extract_results(data)

                    if not results:
                        print(f"Indeed RapidAPI: No results on page {page + 1}")
                        break

                    # Parse each job
                    for job in results:
                        parsed_job = self._parse_job(job, location)
                        if parsed_job:
                            jobs.append(parsed_job)

                    print(f"Indeed RapidAPI: Found {len(results)} jobs on page {page + 1}")

                    # Rate limiting - be respectful
                    time.sleep(1)

                except requests.exceptions.HTTPError as e:
                    if '403' in str(e):
                        print("Indeed RapidAPI Error: Invalid API key or subscription expired")
                        print("  → Check your RapidAPI key and subscription status")
                        break
                    elif '429' in str(e):
                        print("Indeed RapidAPI Error: Rate limit exceeded")
                        print("  → Upgrade your RapidAPI plan or wait")
                        break
                    else:
                        print(f"Indeed RapidAPI Error: {e}")
                        continue

        except Exception as e:
            print(f"Indeed RapidAPI Error: {e}")

        return jobs

    def _extract_results(self, data):
        """Extract results from API response (varies by provider)"""
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            # Try common field names
            return (
                data.get('results') or
                data.get('jobs') or
                data.get('data') or
                data.get('items') or
                []
            )
        return []

    def _extract_company_website(self, job: Dict, company_name: str, job_url: str) -> Optional[str]:
        """
        Extract and normalize company website from job data.

        Priority order:
        1. employer_website or company_website field from API
        2. Extract domain from job_url (if it's a company careers page)
        3. Infer from well-known company names

        Args:
            job: Job dictionary from API
            company_name: Company name
            job_url: Job posting URL

        Returns:
            Normalized company website URL or None
        """
        # Try explicit company_website field first
        explicit_website = (
            job.get('employer_website') or
            job.get('company_website') or
            job.get('company_url') or
            job.get('employer_url')
        )

        if explicit_website:
            return self._normalize_url(explicit_website)

        # Extract domain from job_url if it's not Indeed/job board
        if job_url and not any(domain in job_url.lower() for domain in ['indeed.com', 'linkedin.com', 'glassdoor.com', 'monster.com', 'ziprecruiter.com']):
            try:
                parsed = urlparse(job_url)
                if parsed.netloc:
                    # Check if it looks like a careers page
                    if any(keyword in job_url.lower() for keyword in ['careers', 'jobs', 'apply', 'career', 'work', 'join']):
                        # Extract root domain
                        root_domain = f"https://{parsed.netloc.replace('www.', '')}"
                        # Remove careers subdomain if present
                        root_domain = re.sub(r'https://careers\.', 'https://', root_domain)
                        root_domain = re.sub(r'https://jobs\.', 'https://', root_domain)
                        return root_domain
            except:
                pass

        # Infer from well-known company names
        if company_name:
            company_lower = company_name.lower().strip()

            # Map of well-known companies to their websites
            known_companies = {
                'google': 'https://www.google.com',
                'microsoft': 'https://www.microsoft.com',
                'amazon': 'https://www.amazon.com',
                'apple': 'https://www.apple.com',
                'meta': 'https://www.meta.com',
                'facebook': 'https://www.facebook.com',
                'netflix': 'https://www.netflix.com',
                'tesla': 'https://www.tesla.com',
                'walmart': 'https://www.walmart.com',
                'target': 'https://www.target.com',
                'nike': 'https://www.nike.com',
                'starbucks': 'https://www.starbucks.com',
                'mcdonalds': 'https://www.mcdonalds.com',
                'coca-cola': 'https://www.coca-cola.com',
                'pepsico': 'https://www.pepsico.com',
                'ibm': 'https://www.ibm.com',
                'oracle': 'https://www.oracle.com',
                'salesforce': 'https://www.salesforce.com',
                'adobe': 'https://www.adobe.com',
                'intel': 'https://www.intel.com',
                'cisco': 'https://www.cisco.com',
                'jpmorgan': 'https://www.jpmorgan.com',
                'goldman sachs': 'https://www.goldmansachs.com',
                'morgan stanley': 'https://www.morganstanley.com',
                'bank of america': 'https://www.bankofamerica.com',
                'wells fargo': 'https://www.wellsfargo.com',
                'citigroup': 'https://www.citigroup.com',
            }

            # Check for exact match or substring match
            for known_name, website in known_companies.items():
                if known_name in company_lower or company_lower in known_name:
                    return website

        return None

    def _normalize_url(self, url: str) -> str:
        """Normalize URL to consistent format"""
        if not url:
            return None

        url = url.strip()

        # Add https:// if missing
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"

        # Remove trailing slash
        url = url.rstrip('/')

        # Remove query parameters and fragments
        try:
            parsed = urlparse(url)
            url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip('/')
        except:
            pass

        return url

    def _parse_job(self, job, default_location):
        """Parse individual job from API response"""
        try:
            # Normalize field names (different APIs use different field names)
            title = (
                job.get('title') or
                job.get('job_title') or
                job.get('position') or
                'N/A'
            )

            company = (
                job.get('company') or
                job.get('company_name') or
                job.get('employer') or
                'N/A'
            )

            location = (
                job.get('location') or
                job.get('job_location') or
                job.get('city') or
                default_location
            )

            description = (
                job.get('description') or
                job.get('snippet') or
                job.get('summary') or
                job.get('job_description') or
                ''
            )

            url = (
                job.get('url') or
                job.get('job_url') or
                job.get('link') or
                job.get('apply_url') or
                ''
            )

            salary = (
                job.get('salary') or
                job.get('salary_range') or
                job.get('compensation') or
                None
            )

            posted = (
                job.get('posted_date') or
                job.get('date_posted') or
                job.get('posted') or
                job.get('date') or
                None
            )

            job_type = (
                job.get('job_type') or
                job.get('type') or
                job.get('employment_type') or
                'N/A'
            )

            if not title or not company:
                return None

            # Extract company website
            company_website = self._extract_company_website(job, company, url)

            return {
                'title': str(title),
                'company': str(company),
                'location': str(location),
                'description': str(description),
                'url': str(url),
                'source': 'indeed',
                'posted_date': self._normalize_date(posted),
                'job_type': str(job_type),
                'salary': str(salary) if salary else None,
                'tags': json.dumps(job.get('tags', [])),
                'remote': 'remote' in str(location).lower(),
                'company_website': company_website
            }

        except Exception as e:
            print(f"Error parsing job: {e}")
            return None

    def _normalize_date(self, date_value):
        """Normalize date to datetime object"""
        if not date_value:
            return datetime.utcnow()

        try:
            if isinstance(date_value, datetime):
                return date_value
            # Try parsing ISO format
            from dateutil import parser
            return parser.parse(str(date_value))
        except:
            return datetime.utcnow()


# Example usage
if __name__ == '__main__':
    import os
    from dotenv import load_dotenv

    load_dotenv()

    # Get API key from environment
    api_key = os.getenv('RAPIDAPI_KEY')
    api_host = os.getenv('RAPIDAPI_INDEED_HOST', 'indeed-jobs-api.p.rapidapi.com')

    if not api_key:
        print("Error: RAPIDAPI_KEY not found in .env file")
        print("\nTo use Indeed RapidAPI:")
        print("1. Sign up at https://rapidapi.com/")
        print("2. Subscribe to an Indeed API")
        print("3. Add to .env:")
        print("   RAPIDAPI_KEY=your_key_here")
        print("   RAPIDAPI_INDEED_HOST=indeed-jobs-api.p.rapidapi.com")
    else:
        scraper = IndeedRapidAPIScraper(api_key, api_host)
        jobs = scraper.scrape(keywords="python developer", location="Remote", max_pages=1)

        print(f"\nFound {len(jobs)} jobs")
        for i, job in enumerate(jobs[:3], 1):
            print(f"\n{i}. {job['title']} at {job['company']}")
            print(f"   Location: {job['location']}")
            print(f"   URL: {job['url']}")
