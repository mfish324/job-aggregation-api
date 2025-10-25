"""
USAJOBS API Scraper - Official Federal Government Jobs

Official API Documentation: https://developer.usajobs.gov/

This scraper uses the official USAJOBS API to fetch federal government jobs.
USAJOBS is perfect for Gen-Z because it includes:
- 20,000+ entry-level positions annually
- Recent graduate programs (Pathways)
- Internships and fellowships
- Job security and excellent benefits
- All federal agencies (DOD, NASA, FBI, CIA, etc.)

API Requirements:
- Free API key from https://developer.usajobs.gov/APIRequest/Index
- Required headers: Host, User-Agent, Authorization-Key
- Rate limit: 10 requests per minute (generous)

Grade Levels for Entry-Level (Gen-Z):
- GS-5: Entry level (Bachelor's degree or 1 year experience)
- GS-7: Mid-level entry (Master's degree or 1 year specialized experience)
- GS-9: Advanced entry (Master's + 1 year or PhD)
- GS-11: Early career progression

Author: LevelUp Careers
Date: October 25, 2025
"""

import requests
import time
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class USAJobsScraper:
    """
    Official USAJOBS API scraper for federal government positions
    """

    BASE_URL = "https://data.usajobs.gov/api/search"

    # Entry-level grade levels for Gen-Z
    ENTRY_LEVEL_GRADES = ["GS-5", "GS-7", "GS-9", "GS-11"]

    # Gen-Z relevant job series (federal job classification codes)
    RELEVANT_SERIES = {
        # Information Technology
        "2210": "Information Technology Management",
        "0854": "Computer Engineering",
        "1550": "Computer Science",

        # Business & Finance
        "0501": "Financial Administration",
        "0510": "Accounting",
        "0560": "Budget Analysis",
        "0343": "Management Analysis",

        # Data & Analytics
        "1529": "Mathematical Statistics",
        "1515": "Operations Research",

        # Communications & Marketing
        "1035": "Public Affairs",
        "1082": "Writing and Editing",
        "1084": "Visual Information",

        # Engineering
        "0800": "Engineering",
        "0850": "Electrical Engineering",
        "0830": "Mechanical Engineering",
        "0896": "Industrial Engineering",

        # General Professional
        "0301": "Miscellaneous Administration",
        "0340": "Program Management",
    }

    def __init__(self, api_key: Optional[str] = None, user_agent: Optional[str] = None):
        """
        Initialize USAJOBS scraper

        Args:
            api_key: USAJOBS API key (or set USAJOBS_API_KEY env var)
            user_agent: User agent for API requests (or set USAJOBS_USER_AGENT env var)
        """
        self.api_key = api_key or os.getenv('USAJOBS_API_KEY')
        self.user_agent = user_agent or os.getenv('USAJOBS_USER_AGENT', 'LevelUpCareers/1.0 (contact@levelupcareers.com)')

        if not self.api_key:
            raise ValueError(
                "USAJOBS API key required. Get one at: https://developer.usajobs.gov/APIRequest/Index\n"
                "Set USAJOBS_API_KEY environment variable or pass api_key parameter."
            )

        self.headers = {
            "Host": "data.usajobs.gov",
            "User-Agent": self.user_agent,
            "Authorization-Key": self.api_key
        }

        # Rate limiting: 10 requests per minute
        self.requests_per_minute = 10
        self.request_delay = 60 / self.requests_per_minute  # 6 seconds between requests
        self.last_request_time = 0

        logger.info(f"USAJOBS scraper initialized with User-Agent: {self.user_agent}")

    def _rate_limit(self):
        """Enforce rate limiting (10 requests per minute)"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_delay:
            sleep_time = self.request_delay - elapsed
            logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def _make_request(self, params: Dict) -> Dict:
        """
        Make API request to USAJOBS

        Args:
            params: Query parameters for API

        Returns:
            JSON response from API
        """
        self._rate_limit()

        try:
            logger.debug(f"Request URL: {self.BASE_URL}")
            logger.debug(f"Request params: {params}")

            response = requests.get(
                self.BASE_URL,
                headers=self.headers,
                params=params,
                timeout=30
            )

            logger.debug(f"Response status: {response.status_code}")

            response.raise_for_status()
            json_response = response.json()

            # Log response summary
            search_result = json_response.get('SearchResult', {})
            result_count = search_result.get('SearchResultCount', 0)
            logger.debug(f"API returned {result_count} results")

            return json_response

        except requests.exceptions.RequestException as e:
            logger.error(f"USAJOBS API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text[:500]}")
            raise

    def _parse_job(self, job_data: Dict) -> Dict:
        """
        Parse USAJOBS API job response into standard format

        Args:
            job_data: Raw job data from API

        Returns:
            Standardized job dictionary
        """
        matched_job = job_data.get('MatchedObjectDescriptor', {})

        # Extract basic info
        position_id = matched_job.get('PositionID', '')
        title = matched_job.get('PositionTitle', 'Untitled Position')
        org_name = matched_job.get('OrganizationName', 'Federal Government')
        department = matched_job.get('DepartmentName', '')

        # Location information
        location_list = matched_job.get('PositionLocationDisplay', 'United States')
        locations = matched_job.get('PositionLocation', [])

        # Parse location (use first location if multiple)
        if isinstance(locations, list) and len(locations) > 0:
            loc = locations[0]
            city = loc.get('CityName', '')
            state = loc.get('StateName', '')
            location_str = f"{city}, {state}" if city and state else location_list
        else:
            location_str = location_list

        # Salary information
        salary_min = matched_job.get('PositionRemuneration', [{}])[0].get('MinimumRange', '')
        salary_max = matched_job.get('PositionRemuneration', [{}])[0].get('MaximumRange', '')

        if salary_min and salary_max:
            try:
                salary = f"${int(float(salary_min)):,} - ${int(float(salary_max)):,}"
            except (ValueError, TypeError):
                salary = None
        else:
            salary = None

        # Job details
        grade_range = matched_job.get('JobGrade', [{}])[0].get('Code', '')
        job_category = matched_job.get('JobCategory', [{}])[0].get('Name', '') if matched_job.get('JobCategory') else ''

        # URLs
        apply_url = matched_job.get('PositionURI', '')
        details_url = matched_job.get('ApplyURI', [apply_url])[0] if matched_job.get('ApplyURI') else apply_url

        # Dates
        posted_date_str = matched_job.get('PublicationStartDate', '')
        end_date_str = matched_job.get('ApplicationCloseDate', '')

        try:
            posted_date = datetime.fromisoformat(posted_date_str.replace('Z', '+00:00'))
            posted_str = posted_date.strftime('%Y-%m-%d')
        except (ValueError, AttributeError):
            posted_str = None

        # Job type (most federal jobs are full-time)
        work_schedule = matched_job.get('PositionSchedule', [{}])[0].get('Name', 'Full-Time') if matched_job.get('PositionSchedule') else 'Full-Time'

        # Remote work info
        telework = matched_job.get('TeleworkEligible', False)

        # Job description (qualification summary)
        description = matched_job.get('QualificationSummary', '')
        if not description:
            description = matched_job.get('UserArea', {}).get('Details', {}).get('JobSummary', '')

        # Preview text (first 200 chars of description)
        preview = description[:200] + '...' if len(description) > 200 else description

        # Build company name with department
        if department and department != org_name:
            company = f"{org_name} - {department}"
        else:
            company = org_name

        return {
            'job_id': f"usajobs_{position_id}",
            'title': title,
            'company': company,
            'location': location_str,
            'salary': salary,
            'source': 'usajobs',
            'source_url': details_url or apply_url,
            'posted_date': posted_str,
            'remote': telework,
            'job_type': work_schedule,
            'description': description,
            'preview_text': preview,
            'tags': [grade_range, job_category] if grade_range or job_category else []
        }

    def search_by_keyword(
        self,
        keyword: str,
        location: Optional[str] = None,
        grade_levels: Optional[List[str]] = None,
        max_results: int = 100,
        posted_within_days: int = 30,
        min_salary: Optional[int] = None,
        max_salary: Optional[int] = None
    ) -> List[Dict]:
        """
        Search USAJOBS by keyword

        Args:
            keyword: Search keyword (e.g., "software engineer", "data analyst")
            location: Location filter (city, state, or "Remote")
            grade_levels: List of grade levels (default: None for all levels)
            max_results: Maximum number of results to return
            posted_within_days: Only jobs posted within this many days
            min_salary: Minimum salary filter (e.g., 40000)
            max_salary: Maximum salary filter (e.g., 100000 for entry-level)

        Returns:
            List of job dictionaries
        """
        # Don't filter by grade by default - it's unreliable
        # Instead we'll filter by salary range if specified
        if min_salary is None:
            min_salary = 35000  # Minimum for entry-level
        if max_salary is None:
            max_salary = 95000  # Cap for entry/mid-level Gen-Z positions (includes GS-7 to GS-11)

        # Calculate date range
        from_date = (datetime.now() - timedelta(days=posted_within_days)).strftime('%Y-%m-%d')

        params = {
            "Keyword": keyword,
            "ResultsPerPage": min(max_results * 2, 500),  # Get more to filter by salary
            "DatePosted": "30",  # Last 30 days
        }

        if location:
            params["LocationName"] = location

        logger.info(f"Searching USAJOBS: '{keyword}' (salary: ${min_salary:,}-${max_salary:,})")

        try:
            response = self._make_request(params)

            search_result = response.get('SearchResult', {})
            total_jobs = search_result.get('SearchResultCount', 0)

            logger.info(f"Found {total_jobs} USAJOBS results for '{keyword}'")

            # Parse jobs and filter by salary
            jobs = []
            filtered_out = 0
            for item in search_result.get('SearchResultItems', []):
                try:
                    job = self._parse_job(item)

                    # Filter by salary range (for entry-level targeting)
                    if job.get('salary'):
                        # Extract salary numbers from string like "$59,966 - $94,317"
                        salary_str = job['salary'].replace('$', '').replace(',', '')
                        if '-' in salary_str:
                            try:
                                min_sal_str, max_sal_str = salary_str.split('-')
                                job_min_salary = int(min_sal_str.strip())
                                job_max_salary = int(max_sal_str.strip())

                                # Keep if minimum salary is within our range
                                if job_min_salary >= min_salary and job_min_salary <= max_salary:
                                    jobs.append(job)
                                else:
                                    filtered_out += 1
                            except (ValueError, AttributeError):
                                # If we can't parse salary, include the job anyway
                                jobs.append(job)
                        else:
                            jobs.append(job)
                    else:
                        # No salary info, include the job
                        jobs.append(job)

                    if len(jobs) >= max_results:
                        break

                except Exception as e:
                    logger.error(f"Error parsing job: {e}")
                    continue

            logger.info(f"After salary filtering: {len(jobs)} jobs (filtered out {filtered_out} senior positions)")
            return jobs[:max_results]

        except Exception as e:
            logger.error(f"Error searching USAJOBS for '{keyword}': {e}")
            return []

    def search_entry_level_tech(self, max_results: int = 100) -> List[Dict]:
        """Search for entry-level tech positions"""
        keywords = [
            "software developer",
            "software engineer",
            "computer scientist",
            "IT specialist",
            "data analyst",
            "cybersecurity"
        ]

        all_jobs = []
        for keyword in keywords:
            jobs = self.search_by_keyword(keyword, max_results=max_results // len(keywords))
            all_jobs.extend(jobs)
            if len(all_jobs) >= max_results:
                break

        return all_jobs[:max_results]

    def search_entry_level_finance(self, max_results: int = 100) -> List[Dict]:
        """Search for entry-level finance/business positions"""
        keywords = [
            "financial analyst",
            "accountant",
            "budget analyst",
            "management analyst",
            "program analyst"
        ]

        all_jobs = []
        for keyword in keywords:
            jobs = self.search_by_keyword(keyword, max_results=max_results // len(keywords))
            all_jobs.extend(jobs)
            if len(all_jobs) >= max_results:
                break

        return all_jobs[:max_results]

    def search_recent_graduate_programs(self, max_results: int = 100) -> List[Dict]:
        """
        Search for Pathways Recent Graduate programs
        These are 1-year developmental programs for recent grads
        """
        return self.search_by_keyword(
            "recent graduate",
            max_results=max_results,
            posted_within_days=90  # These programs are posted less frequently
        )

    def search_internships(self, max_results: int = 100) -> List[Dict]:
        """Search for federal internships (Pathways Internship Program)"""
        return self.search_by_keyword(
            "intern",
            max_results=max_results,
            posted_within_days=90
        )

    def scrape(
        self,
        keyword: Optional[str] = None,
        location: Optional[str] = None,
        max_results: int = 100
    ) -> List[Dict]:
        """
        Main scraping method compatible with JobAggregator interface

        Args:
            keyword: Search keyword
            location: Location filter
            max_results: Maximum results to return

        Returns:
            List of standardized job dictionaries
        """
        if keyword:
            return self.search_by_keyword(
                keyword=keyword,
                location=location,
                max_results=max_results
            )
        else:
            # Default: search entry-level positions
            tech_jobs = self.search_entry_level_tech(max_results // 2)
            finance_jobs = self.search_entry_level_finance(max_results // 2)
            return tech_jobs + finance_jobs


# Test function
if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv

    logging.basicConfig(level=logging.INFO)

    # Load environment variables from .env file
    load_dotenv()

    # Check for API key
    api_key = os.getenv('USAJOBS_API_KEY')
    if not api_key:
        print("\n" + "="*80)
        print("USAJOBS API KEY REQUIRED")
        print("="*80)
        print("\nTo use this scraper, you need a free API key from USAJOBS.")
        print("\nSteps:")
        print("1. Visit: https://developer.usajobs.gov/APIRequest/Index")
        print("2. Fill out the form with your email and organization details")
        print("3. You'll receive the API key via email (usually instant)")
        print("4. Set environment variable: USAJOBS_API_KEY=your_key_here")
        print("5. Optionally set: USAJOBS_USER_AGENT=YourApp/1.0 (your_email@example.com)")
        print("\nExample .env file:")
        print("  USAJOBS_API_KEY=aBcD1234...")
        print("  USAJOBS_USER_AGENT=LevelUpCareers/1.0 (contact@levelupcareers.com)")
        print("="*80 + "\n")
        sys.exit(1)

    # Test scraper
    print("\nTesting USAJOBS Scraper...")
    print("="*80)

    scraper = USAJobsScraper()

    # Test 1: Entry-level software developer
    print("\n[TEST 1] Searching for entry-level software developer jobs...")
    jobs = scraper.search_by_keyword("software developer", max_results=5)
    print(f"Found {len(jobs)} jobs")

    if jobs:
        print("\nSample job:")
        job = jobs[0]
        print(f"  Title: {job['title']}")
        print(f"  Company: {job['company']}")
        print(f"  Location: {job['location']}")
        print(f"  Salary: {job['salary']}")
        print(f"  Posted: {job['posted_date']}")
        print(f"  URL: {job['source_url']}")
        print(f"  Remote: {job['remote']}")

    # Test 2: Recent graduate programs
    print("\n[TEST 2] Searching for Recent Graduate programs...")
    grad_jobs = scraper.search_recent_graduate_programs(max_results=3)
    print(f"Found {len(grad_jobs)} recent graduate positions")

    for i, job in enumerate(grad_jobs[:3], 1):
        print(f"\n  {i}. {job['title']} at {job['company']}")
        print(f"     Location: {job['location']}")
        print(f"     Salary: {job['salary']}")

    print("\n" + "="*80)
    total_jobs = len(jobs) + len(grad_jobs)
    if total_jobs > 0:
        print(f"[SUCCESS] USAJOBS scraper working! Total jobs found: {total_jobs}")
    else:
        print(f"[WARNING] USAJOBS API connected but returned 0 jobs.")
        print("This could be normal if:")
        print("  - No jobs match the search criteria")
        print("  - USAJOBS has fewer postings today")
        print("  - Try different keywords like 'IT Specialist' or 'Information Technology'")
    print("="*80 + "\n")
