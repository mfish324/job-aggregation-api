#!/usr/bin/env python3
"""
Direct scraping script - adds jobs NOW without needing server
"""
from dotenv import load_dotenv
load_dotenv()

import logging
from scheduled_scraper import GenZJobSearcher
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

print("="*80)
print("DIRECT JOB SCRAPING - Adding Fresh Jobs NOW")
print("="*80)

# Get database URL
db_url = os.getenv('DATABASE_URL', 'sqlite:///job_board.db')
print(f"\nDatabase: {db_url.split('@')[1] if '@' in db_url else 'Local SQLite'}")

# Initialize searcher
searcher = GenZJobSearcher(database_url=db_url, us_only=True)

# Run priority profiles
profiles = ['entry_tech', 'entry_finance', 'entry_data']

for profile in profiles:
    print(f"\n{'='*80}")
    print(f"Scraping: {profile}")
    print("="*80)

    try:
        stats = searcher.run_search_profile(profile, max_keywords=5)
        print(f"\nResults for {profile}:")
        print(f"  Keywords searched: {stats['keywords_searched']}")
        print(f"  Total jobs found: {stats['total_jobs_found']}")
        print(f"  New jobs added: {stats['new_jobs_added']}")
        print(f"  Sources used: {', '.join(stats['sources_used'])}")
        print(f"  Duration: {stats['duration_minutes']:.1f} minutes")
    except Exception as e:
        print(f"\nERROR scraping {profile}: {e}")
        logger.error(f"Error scraping {profile}", exc_info=True)

print("\n" + "="*80)
print("SCRAPING COMPLETE!")
print("="*80)

# Get final stats
from models import DatabaseManager
db = DatabaseManager(db_url)
print(f"\nFinal job count: Check your database")
print("Done!")
