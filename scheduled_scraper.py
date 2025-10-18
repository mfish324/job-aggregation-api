"""
Scheduled Job Scraper for Gen-Z Targeted Searches
Automatically searches for entry-level and mid-level jobs in finance, tech, etc.
Respects rate limits for each API source.
"""

import time
import schedule
import logging
from datetime import datetime, timedelta
from typing import List, Dict
from aggregator import JobAggregator
from indeed_rapidapi_scraper import IndeedRapidAPIScraper
import os
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class GenZJobSearcher:
    """
    Automated job searcher targeting Gen-Z demographics
    Entry-level and mid-level positions in tech, finance, marketing, etc.
    """

    # Gen-Z targeted search profiles
    SEARCH_PROFILES = {
        'entry_tech': {
            'keywords': [
                'junior developer', 'entry level developer', 'junior software engineer',
                'junior python developer', 'junior javascript developer',
                'associate software engineer', 'graduate developer',
                'junior frontend', 'junior backend', 'junior full stack'
            ],
            'categories': ['software-dev', 'tech'],
            'experience': 'entry'
        },
        'mid_tech': {
            'keywords': [
                'software engineer', 'python developer', 'javascript developer',
                'full stack developer', 'frontend engineer', 'backend engineer',
                'react developer', 'node developer', 'java developer'
            ],
            'categories': ['software-dev', 'tech'],
            'experience': 'mid'
        },
        'entry_finance': {
            'keywords': [
                'junior financial analyst', 'entry level analyst',
                'financial analyst associate', 'junior accountant',
                'accounting associate', 'finance associate',
                'junior investment analyst', 'credit analyst'
            ],
            'categories': ['finance', 'accounting'],
            'experience': 'entry'
        },
        'mid_finance': {
            'keywords': [
                'financial analyst', 'senior financial analyst',
                'accountant', 'finance manager', 'budget analyst',
                'investment analyst', 'portfolio analyst'
            ],
            'categories': ['finance', 'accounting'],
            'experience': 'mid'
        },
        'entry_data': {
            'keywords': [
                'junior data analyst', 'data analyst', 'junior data scientist',
                'business analyst', 'junior analyst', 'data associate'
            ],
            'categories': ['data-science', 'analytics'],
            'experience': 'entry'
        },
        'mid_data': {
            'keywords': [
                'data scientist', 'senior data analyst', 'data engineer',
                'machine learning engineer', 'analytics engineer'
            ],
            'categories': ['data-science', 'analytics'],
            'experience': 'mid'
        },
        'entry_marketing': {
            'keywords': [
                'junior marketing', 'marketing coordinator', 'social media coordinator',
                'content marketing associate', 'digital marketing associate',
                'marketing assistant', 'seo specialist'
            ],
            'categories': ['marketing', 'content'],
            'experience': 'entry'
        },
        'mid_marketing': {
            'keywords': [
                'marketing manager', 'social media manager', 'content manager',
                'digital marketing manager', 'growth marketing',
                'product marketing', 'seo manager'
            ],
            'categories': ['marketing', 'content'],
            'experience': 'mid'
        },
        'entry_design': {
            'keywords': [
                'junior designer', 'ui designer', 'ux designer',
                'graphic designer', 'product designer', 'web designer'
            ],
            'categories': ['design'],
            'experience': 'entry'
        },
        'entry_sales': {
            'keywords': [
                'sales representative', 'account executive', 'sales development',
                'business development representative', 'sdr', 'inside sales'
            ],
            'categories': ['sales', 'business'],
            'experience': 'entry'
        }
    }

    # Rate limits for each source (requests per hour)
    RATE_LIMITS = {
        'remoteok': {
            'requests_per_hour': 60,  # Conservative estimate
            'delay_seconds': 60  # 1 request per minute
        },
        'remotive': {
            'requests_per_hour': 60,
            'delay_seconds': 60
        },
        'github': {
            'requests_per_hour': 10,  # GitHub is more restrictive without auth
            'delay_seconds': 360  # 1 request per 6 minutes
        },
        'indeed_rapidapi': {
            'requests_per_month': 100,  # Free tier limit
            'requests_per_hour': 10,
            'delay_seconds': 360
        },
        'authenticjobs': {
            'requests_per_hour': 30,
            'delay_seconds': 120
        },
        'weworkremotely': {
            'requests_per_hour': 30,
            'delay_seconds': 120
        }
    }

    def __init__(self, database_url='sqlite:///job_board.db', us_only=True):
        self.aggregator = JobAggregator(database_url=database_url, us_only=us_only)
        self.indeed_scraper = None
        self.us_only = us_only

        # Initialize Indeed scraper if API key available
        rapidapi_key = os.getenv('RAPIDAPI_KEY')
        if rapidapi_key:
            self.indeed_scraper = IndeedRapidAPIScraper(
                api_key=rapidapi_key,
                api_host=os.getenv('RAPIDAPI_INDEED_HOST', 'indeed-jobs-api.p.rapidapi.com')
            )

        self.search_stats = {
            'total_searches': 0,
            'total_jobs_found': 0,
            'new_jobs_added': 0,
            'last_run': None
        }

        print(f"Gen-Z Job Searcher initialized (US only: {us_only})")

    def search_with_rate_limit(self, source: str, keyword: str, category: str = None):
        """
        Perform search with rate limiting

        Args:
            source: Source name (remoteok, remotive, etc.)
            keyword: Search keyword
            category: Optional category filter

        Returns:
            Tuple of (new_count, total_count)
        """
        rate_limit = self.RATE_LIMITS.get(source, {})
        delay = rate_limit.get('delay_seconds', 60)

        logger.info(f"Searching {source} for '{keyword}' (rate limit: {delay}s)")

        try:
            if source == 'indeed_rapidapi' and self.indeed_scraper:
                results = self.indeed_scraper.scrape(
                    keyword=keyword,
                    location='United States',  # Specify US for Indeed
                    max_results=50
                )

                # Filter for US jobs if enabled
                if self.us_only:
                    from location_filter import filter_us_jobs
                    before_filter = len(results)
                    results = filter_us_jobs(results)
                    filtered = before_filter - len(results)
                    if filtered > 0:
                        logger.info(f"Filtered {filtered} non-US jobs from Indeed")

                # Add to database
                new_count = 0
                for job in results:
                    is_new, _ = self.aggregator.db.add_job(job)
                    if is_new:
                        new_count += 1

                logger.info(f"Indeed: Found {len(results)} jobs, {new_count} new")
                time.sleep(delay)
                return new_count, len(results)

            else:
                # Use standard aggregator
                stats = self.aggregator.scrape_all(
                    sources=[source],
                    max_pages=5,
                    keywords=keyword
                )

                source_stats = stats.get(source, {})
                new_count = source_stats.get('new', 0)
                total_count = source_stats.get('scraped', 0)

                logger.info(f"{source}: Found {total_count} jobs, {new_count} new")
                time.sleep(delay)
                return new_count, total_count

        except Exception as e:
            logger.error(f"Error searching {source} for '{keyword}': {e}")
            time.sleep(delay)  # Still respect rate limit on errors
            return 0, 0

    def run_search_profile(self, profile_name: str, max_keywords: int = None):
        """
        Run all searches for a specific profile

        Args:
            profile_name: Name of search profile (entry_tech, mid_finance, etc.)
            max_keywords: Maximum number of keywords to search (None = all)

        Returns:
            Dictionary with search statistics
        """
        if profile_name not in self.SEARCH_PROFILES:
            logger.error(f"Unknown profile: {profile_name}")
            return None

        profile = self.SEARCH_PROFILES[profile_name]
        keywords = profile['keywords'][:max_keywords] if max_keywords else profile['keywords']

        logger.info(f"Running profile '{profile_name}' with {len(keywords)} keywords")

        stats = {
            'profile': profile_name,
            'keywords_searched': 0,
            'total_jobs_found': 0,
            'new_jobs_added': 0,
            'sources_used': [],
            'start_time': datetime.now()
        }

        # Search each keyword across all sources
        for keyword in keywords:
            stats['keywords_searched'] += 1

            # RemoteOK - Good for tech jobs
            new, total = self.search_with_rate_limit('remoteok', keyword)
            stats['new_jobs_added'] += new
            stats['total_jobs_found'] += total
            if 'remoteok' not in stats['sources_used']:
                stats['sources_used'].append('remoteok')

            # Remotive - Good for all remote positions
            new, total = self.search_with_rate_limit('remotive', keyword)
            stats['new_jobs_added'] += new
            stats['total_jobs_found'] += total
            if 'remotive' not in stats['sources_used']:
                stats['sources_used'].append('remotive')

            # Indeed (if available) - Best for finance, entry-level
            if self.indeed_scraper and profile_name in ['entry_finance', 'mid_finance', 'entry_marketing']:
                new, total = self.search_with_rate_limit('indeed_rapidapi', keyword)
                stats['new_jobs_added'] += new
                stats['total_jobs_found'] += total
                if 'indeed_rapidapi' not in stats['sources_used']:
                    stats['sources_used'].append('indeed_rapidapi')

        stats['end_time'] = datetime.now()
        stats['duration_minutes'] = (stats['end_time'] - stats['start_time']).seconds / 60

        logger.info(f"Profile '{profile_name}' complete: {stats['new_jobs_added']} new jobs "
                   f"from {stats['total_jobs_found']} total in {stats['duration_minutes']:.1f} min")

        return stats

    def run_all_profiles(self, max_keywords_per_profile: int = 3):
        """
        Run all Gen-Z search profiles

        Args:
            max_keywords_per_profile: Limit keywords per profile to respect rate limits

        Returns:
            Combined statistics
        """
        logger.info("Starting full Gen-Z job search across all profiles")

        all_stats = {
            'total_profiles': 0,
            'total_new_jobs': 0,
            'total_jobs_found': 0,
            'profile_results': [],
            'start_time': datetime.now()
        }

        for profile_name in self.SEARCH_PROFILES.keys():
            profile_stats = self.run_search_profile(profile_name, max_keywords=max_keywords_per_profile)

            if profile_stats:
                all_stats['total_profiles'] += 1
                all_stats['total_new_jobs'] += profile_stats['new_jobs_added']
                all_stats['total_jobs_found'] += profile_stats['total_jobs_found']
                all_stats['profile_results'].append(profile_stats)

        all_stats['end_time'] = datetime.now()
        all_stats['duration_hours'] = (all_stats['end_time'] - all_stats['start_time']).seconds / 3600

        self.search_stats['total_searches'] += all_stats['total_profiles']
        self.search_stats['total_jobs_found'] += all_stats['total_jobs_found']
        self.search_stats['new_jobs_added'] += all_stats['total_new_jobs']
        self.search_stats['last_run'] = datetime.now()

        logger.info(f"All profiles complete: {all_stats['total_new_jobs']} new jobs "
                   f"from {all_stats['total_jobs_found']} total across {all_stats['total_profiles']} profiles")

        return all_stats

    def run_priority_profiles(self):
        """
        Run high-priority profiles (entry-level tech and finance)
        Use more keywords since these are most important for Gen-Z
        """
        logger.info("Running priority Gen-Z profiles (entry tech/finance)")

        priority_profiles = ['entry_tech', 'mid_tech', 'entry_finance', 'entry_data']
        stats = {
            'total_new_jobs': 0,
            'total_jobs_found': 0,
            'profiles': []
        }

        for profile_name in priority_profiles:
            profile_stats = self.run_search_profile(profile_name, max_keywords=5)
            if profile_stats:
                stats['total_new_jobs'] += profile_stats['new_jobs_added']
                stats['total_jobs_found'] += profile_stats['total_jobs_found']
                stats['profiles'].append(profile_stats)

        logger.info(f"Priority profiles complete: {stats['total_new_jobs']} new jobs")
        return stats


def setup_schedule(searcher: GenZJobSearcher):
    """
    Set up scheduled jobs for maximum coverage within rate limits

    Schedule:
    - Every 6 hours: Priority profiles (entry tech, finance)
    - Every 12 hours: All profiles with limited keywords
    - Every 24 hours: Full comprehensive search
    """

    # Priority search every 6 hours
    schedule.every(6).hours.do(searcher.run_priority_profiles)
    logger.info("Scheduled: Priority profiles every 6 hours")

    # All profiles with limited keywords every 12 hours
    schedule.every(12).hours.do(
        lambda: searcher.run_all_profiles(max_keywords_per_profile=2)
    )
    logger.info("Scheduled: All profiles (2 keywords each) every 12 hours")

    # Full comprehensive search daily at 3 AM
    schedule.every().day.at("03:00").do(
        lambda: searcher.run_all_profiles(max_keywords_per_profile=5)
    )
    logger.info("Scheduled: Full search (5 keywords per profile) daily at 3 AM")

    # Run immediately on startup
    logger.info("Running initial priority search...")
    searcher.run_priority_profiles()


def run_scheduler():
    """
    Main scheduler loop
    """
    logger.info("Starting Gen-Z Job Scraper Scheduler")
    logger.info(f"Database: job_board.db")
    logger.info(f"Profiles: {len(GenZJobSearcher.SEARCH_PROFILES)}")

    searcher = GenZJobSearcher()
    setup_schedule(searcher)

    logger.info("Scheduler running. Press Ctrl+C to stop.")

    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    try:
        run_scheduler()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler error: {e}", exc_info=True)
