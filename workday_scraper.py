"""
Workday Job Scraper
Scrapes jobs from companies using Workday (myworkdayjobs.com)
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import time
from typing import List, Dict
import hashlib


class WorkdayScraper:
    """
    Generic scraper for Workday job boards
    Works with any company's myworkdayjobs.com site
    """

    # Major companies using Workday
    COMPANIES = {
        'walmart': {
            'name': 'Walmart',
            'url': 'https://walmart.wd5.myworkdayjobs.com/WalmartExternal',
            'api_url': 'https://walmart.wd5.myworkdayjobs.com/wday/cxs/walmart/WalmartExternal/jobs'
        },
        'nike': {
            'name': 'Nike',
            'url': 'https://nike.wd1.myworkdayjobs.com/nke',
            'api_url': 'https://nike.wd1.myworkdayjobs.com/wday/cxs/nike/nke/jobs'
        },
        'citi': {
            'name': 'Citibank',
            'url': 'https://citi.wd5.myworkdayjobs.com/2',
            'api_url': 'https://citi.wd5.myworkdayjobs.com/wday/cxs/citi/2/jobs'
        }
    }

    def __init__(self, timeout=30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

    def scrape_company(self, company_id: str, keywords: str = None, location: str = None, max_results: int = 100) -> List[Dict]:
        """
        Scrape jobs from a specific company's Workday site

        Args:
            company_id: Company identifier (walmart, nike, citi)
            keywords: Search keywords
            location: Job location
            max_results: Maximum number of jobs to retrieve

        Returns:
            List of job dictionaries
        """
        if company_id not in self.COMPANIES:
            print(f"Company '{company_id}' not supported. Available: {list(self.COMPANIES.keys())}")
            return []

        company = self.COMPANIES[company_id]
        jobs = []

        try:
            # Workday uses a JSON API for job listings
            payload = {
                "appliedFacets": {},
                "limit": min(max_results, 20),
                "offset": 0,
                "searchText": keywords or ""
            }

            # Add location filter if provided
            if location:
                payload["appliedFacets"]["locations"] = [location]

            response = self.session.post(
                company['api_url'],
                json=payload,
                timeout=self.timeout
            )

            if response.status_code != 200:
                print(f"Error: {company['name']} returned status {response.status_code}")
                return []

            data = response.json()
            job_postings = data.get('jobPostings', [])

            for job_data in job_postings:
                try:
                    title = job_data.get('title', 'N/A')
                    job_id = job_data.get('bulletFields', [{}])[0] if job_data.get('bulletFields') else 'N/A'
                    posted_date = job_data.get('postedOn', '')

                    # Extract location
                    locations = job_data.get('locationsText', 'USA')

                    # Build job URL
                    job_url = company['url'] + '/' + job_data.get('externalPath', '')

                    jobs.append({
                        'title': title,
                        'company': company['name'],
                        'location': locations,
                        'description': title,  # Workday API doesn't return full description in list
                        'url': job_url,
                        'source': f'{company_id}_workday',
                        'posted_date': self.normalize_date(posted_date),
                        'job_type': 'Full-time',
                        'salary': None,
                        'tags': json.dumps(['workday', company_id]),
                        'remote': 'remote' in locations.lower() if locations else False
                    })

                except Exception as e:
                    print(f"Error parsing {company['name']} job: {e}")
                    continue

            print(f"{company['name']}: Found {len(jobs)} jobs")

        except Exception as e:
            print(f"Error scraping {company['name']}: {e}")

        return jobs

    def scrape_all_companies(self, keywords: str = None, max_results_per_company: int = 50) -> List[Dict]:
        """
        Scrape jobs from all supported Workday companies

        Args:
            keywords: Search keywords
            max_results_per_company: Max jobs per company

        Returns:
            Combined list of jobs from all companies
        """
        all_jobs = []

        for company_id in self.COMPANIES.keys():
            print(f"\nScraping {self.COMPANIES[company_id]['name']}...")
            jobs = self.scrape_company(company_id, keywords=keywords, max_results=max_results_per_company)
            all_jobs.extend(jobs)
            time.sleep(2)  # Rate limiting between companies

        return all_jobs

    def normalize_date(self, date_str):
        """Normalize date string to datetime"""
        if not date_str:
            return datetime.utcnow()
        try:
            # Workday uses ISO format dates
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return datetime.utcnow()


class WalmartScraper:
    """Walmart Workday scraper with standard interface"""
    def __init__(self):
        self.workday = WorkdayScraper()

    def scrape(self, keywords=None, location=None, max_pages=5):
        return self.workday.scrape_company('walmart', keywords=keywords, location=location, max_results=max_pages*20)


class NikeScraper:
    """Nike Workday scraper with standard interface"""
    def __init__(self):
        self.workday = WorkdayScraper()

    def scrape(self, keywords=None, location=None, max_pages=5):
        return self.workday.scrape_company('nike', keywords=keywords, location=location, max_results=max_pages*20)


class CitiScraper:
    """Citibank Workday scraper with standard interface"""
    def __init__(self):
        self.workday = WorkdayScraper()

    def scrape(self, keywords=None, location=None, max_pages=5):
        return self.workday.scrape_company('citi', keywords=keywords, location=location, max_results=max_pages*20)


def main():
    """Test the Workday scraper"""
    scraper = WorkdayScraper()

    # Test scraping Walmart
    print("Testing Walmart scraper...")
    jobs = scraper.scrape_company('walmart', keywords='software engineer', max_results=10)

    if jobs:
        print(f"\nFound {len(jobs)} Walmart jobs")
        print("\nSample job:")
        job = jobs[0]
        print(f"  Title: {job['title']}")
        print(f"  Company: {job['company']}")
        print(f"  Location: {job['location']}")
        print(f"  URL: {job['url']}")
        print(f"  Posted: {job['posted_date']}")

    # Test scraping all companies
    print("\n" + "="*60)
    print("Testing all companies...")
    all_jobs = scraper.scrape_all_companies(keywords='analyst', max_results_per_company=5)
    print(f"\nTotal jobs from all companies: {len(all_jobs)}")


if __name__ == "__main__":
    main()
