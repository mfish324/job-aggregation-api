"""
JobSpy Scraper - Aggregates jobs from LinkedIn, Indeed, Glassdoor, ZipRecruiter, Google Jobs
Uses the python-jobspy library to scrape multiple job boards simultaneously
"""

from jobspy import scrape_jobs
from datetime import datetime
from typing import List, Dict
import pandas as pd


class JobSpyScraper:
    """
    Scraper that uses JobSpy library to aggregate jobs from multiple platforms:
    - Indeed
    - LinkedIn
    - ZipRecruiter
    - Glassdoor
    - Google Jobs
    """

    # JobSpy site names (all US-focused platforms)
    # Note: Use exact names from JobSpy library
    SUPPORTED_SITES = ['indeed', 'linkedin', 'glassdoor', 'google']  # 'zip_recruiter' has issues

    def __init__(self):
        self.name = "JobSpy Multi-Platform Scraper"
        self.sites = self.SUPPORTED_SITES

    def scrape(self, keywords=None, location=None, max_pages=5, max_results=None, hours_old=72, sites=None) -> List[Dict]:
        """
        Scrape jobs using JobSpy library

        Args:
            keywords: Search term (e.g., "software engineer")
            location: Job location (e.g., "San Francisco, CA", "Remote", "United States")
            max_pages: For compatibility with other scrapers (converted to max_results)
            max_results: Number of results per site (overrides max_pages if provided)
            hours_old: Only get jobs posted in last N hours (default: 72 = 3 days)
            sites: List of sites to scrape (default: all)

        Returns:
            List of job dictionaries
        """
        # Convert max_pages to max_results for compatibility
        if max_results is None:
            max_results = max_pages * 10  # Approximate: ~10 jobs per page
        if not keywords:
            keywords = "software engineer"

        if not location:
            location = "United States"

        # Use specified sites or all supported sites
        sites_to_scrape = sites if sites else self.SUPPORTED_SITES

        print(f"\n[JobSpy] Scraping {len(sites_to_scrape)} platforms: {', '.join(sites_to_scrape)}")
        print(f"[JobSpy] Search: '{keywords}' in '{location}'")
        print(f"[JobSpy] Requesting {max_results} results per platform, posted within {hours_old} hours")

        try:
            # Call JobSpy's scrape_jobs function
            jobs_df = scrape_jobs(
                site_name=sites_to_scrape,
                search_term=keywords,
                location=location,
                results_wanted=max_results,
                hours_old=hours_old,
                country_indeed='USA',
                # linkedin_fetch_description=False,  # Faster without full descriptions
            )

            if jobs_df is None or len(jobs_df) == 0:
                print(f"[JobSpy] No jobs found")
                return []

            print(f"[JobSpy] Found {len(jobs_df)} jobs total")

            # Convert DataFrame to list of dicts in our format
            jobs = []
            for _, row in jobs_df.iterrows():
                job = self._normalize_job(row)
                if job:
                    jobs.append(job)

            print(f"[JobSpy] Normalized {len(jobs)} jobs")
            return jobs

        except Exception as e:
            print(f"[JobSpy] Error scraping: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _normalize_job(self, row: pd.Series) -> Dict:
        """Convert JobSpy result to our standard format"""
        try:
            # JobSpy returns: site, job_url, job_url_direct, title, company, location,
            # job_type, date_posted, interval, min_amount, max_amount, currency,
            # is_remote, num_urgent_words, benefits, emails, description

            # Determine source name
            source_map = {
                'indeed': 'indeed',
                'linkedin': 'linkedin',
                'zip_recruiter': 'ziprecruiter',
                'glassdoor': 'glassdoor',
                'google': 'google'
            }
            source = source_map.get(str(row.get('site', '')).lower(), str(row.get('site', 'jobspy')))

            # Parse date
            posted_date = None
            if 'date_posted' in row and pd.notna(row['date_posted']):
                try:
                    posted_date = pd.to_datetime(row['date_posted'])
                except:
                    posted_date = datetime.utcnow()
            else:
                posted_date = datetime.utcnow()

            # Build salary string
            salary = None
            if pd.notna(row.get('min_amount')) or pd.notna(row.get('max_amount')):
                min_amt = row.get('min_amount', '')
                max_amt = row.get('max_amount', '')
                currency = row.get('currency', 'USD')
                interval = row.get('interval', '')

                if pd.notna(min_amt) and pd.notna(max_amt):
                    salary = f"${min_amt}-${max_amt} {currency}/{interval}"
                elif pd.notna(min_amt):
                    salary = f"${min_amt}+ {currency}/{interval}"
                elif pd.notna(max_amt):
                    salary = f"Up to ${max_amt} {currency}/{interval}"

            # Get job URL (prefer direct link)
            job_url = row.get('job_url_direct') or row.get('job_url', '')
            if pd.isna(job_url):
                job_url = ''

            # Get description
            description = row.get('description', '')
            if pd.isna(description):
                description = ''

            # Create standardized job dict
            job = {
                'title': str(row.get('title', 'N/A')),
                'company': str(row.get('company', 'N/A')),
                'location': str(row.get('location', 'Remote')),
                'description': str(description),
                'url': str(job_url),
                'source': f'jobspy_{source}',
                'posted_date': posted_date,
                'job_type': str(row.get('job_type', '')),
                'salary': salary,
                'tags': '',  # Could parse from description/benefits
                'remote': bool(row.get('is_remote', False))
            }

            return job

        except Exception as e:
            print(f"[JobSpy] Error normalizing job: {e}")
            return None


# Example usage
if __name__ == '__main__':
    scraper = JobSpyScraper()

    # Test scraping
    jobs = scraper.scrape(
        keywords="python developer",
        location="San Francisco, CA",
        max_results=5,
        hours_old=72,
        sites=['indeed']  # Test with Indeed
    )

    print(f"\n{'='*80}")
    print(f"SCRAPED {len(jobs)} JOBS")
    print(f"{'='*80}\n")

    for i, job in enumerate(jobs[:3], 1):
        print(f"{i}. {job['title']} at {job['company']}")
        print(f"   Location: {job['location']}")
        print(f"   Source: {job['source']}")
        print(f"   Remote: {job['remote']}")
        print(f"   URL: {job['url'][:80]}...")
        print()
