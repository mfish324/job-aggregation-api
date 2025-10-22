"""
Trigger scraping and update the job board database

This script will:
1. Trigger the /scrape endpoint to fetch new jobs
2. Import them to the job board database via /import endpoint
3. Show updated statistics

Usage:
    python trigger_scrape.py
    python trigger_scrape.py --url https://your-railway-app.up.railway.app
"""

import requests
import sys
import time
import os
from dotenv import load_dotenv

load_dotenv()

def trigger_scrape(base_url, sources=None, keywords=None):
    """Trigger job scraping"""
    scrape_url = f"{base_url}/scrape"

    payload = {
        "max_pages": 3
    }

    if sources:
        payload["sources"] = sources
    if keywords:
        payload["keywords"] = keywords

    print(f"🔍 Triggering scrape at {scrape_url}...")
    print(f"   Payload: {payload}")

    try:
        response = requests.post(scrape_url, json=payload, timeout=300)  # 5 min timeout
        response.raise_for_status()

        data = response.json()
        print("\n✅ Scraping completed!")
        print(f"   Total scraped: {data['total_scraped']}")
        print(f"   New jobs: {data['total_new']}")
        print(f"   Duplicates: {data['total_duplicates']}")
        print("\n   By source:")
        for source, count in data['by_source'].items():
            print(f"   - {source}: {count} jobs")

        return True

    except requests.exceptions.Timeout:
        print("⚠️  Request timed out. Jobs may still be scraping in background.")
        return True
    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        return False

def import_jobs(base_url):
    """Import jobs from aggregator to job board database"""
    import_url = f"{base_url}/import"

    print(f"\n📥 Importing jobs to job board database...")

    try:
        response = requests.post(import_url, timeout=120)
        response.raise_for_status()

        data = response.json()
        print("✅ Import completed!")
        print(f"   Imported: {data['imported']} new jobs")
        print(f"   Skipped: {data['skipped']} duplicates")
        print(f"   Total in database: {data['total']}")

        return True

    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def get_stats(base_url):
    """Get current database statistics"""
    stats_url = f"{base_url}/stats"

    print(f"\n📊 Fetching statistics...")

    try:
        response = requests.get(stats_url, timeout=30)
        response.raise_for_status()

        data = response.json()
        print("✅ Current statistics:")
        print(f"   Total jobs: {data.get('total_jobs', 0)}")
        print(f"   Remote jobs: {data.get('remote_jobs', 0)}")
        print(f"   Jobs with salary: {data.get('with_salary', 0)} ({data.get('salary_percentage', 0)}%)")
        print(f"   Recent jobs (24h): {data.get('recent_jobs_24h', 0)}")

        if 'by_source' in data:
            print("\n   Jobs by source:")
            for source, count in data['by_source'].items():
                print(f"   - {source}: {count}")

        return True

    except Exception as e:
        print(f"❌ Failed to get stats: {e}")
        return False

def run_genz_search(base_url, profile=None):
    """Run Gen-Z targeted searches"""
    print(f"\n🎯 Running Gen-Z targeted searches...")

    # Get available profiles
    profiles_url = f"{base_url}/genz/profiles"
    try:
        response = requests.get(profiles_url, timeout=30)
        response.raise_for_status()
        data = response.json()
        profiles = data['profiles']

        print(f"   Available profiles: {', '.join(profiles)}")

        # Run search for specific profile or all
        if profile:
            profiles_to_run = [profile] if profile in profiles else []
            if not profiles_to_run:
                print(f"❌ Profile '{profile}' not found")
                return False
        else:
            # Run a few key profiles
            profiles_to_run = ['entry_tech', 'mid_tech', 'entry_data']

        for prof in profiles_to_run:
            print(f"\n   Running {prof} search...")
            search_url = f"{base_url}/genz/search/{prof}"
            try:
                response = requests.post(search_url, params={"max_keywords": 3}, timeout=180)
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ {prof}: {result.get('message', 'Started')}")
                else:
                    print(f"   ⚠️  {prof}: Status {response.status_code}")
            except Exception as e:
                print(f"   ⚠️  {prof}: {e}")

            time.sleep(2)  # Rate limiting

        return True

    except Exception as e:
        print(f"❌ Gen-Z search failed: {e}")
        return False

def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Trigger job scraping and update database')
    parser.add_argument('--url', default='http://localhost:8001',
                       help='Base URL of the API (default: http://localhost:8001)')
    parser.add_argument('--sources', nargs='+',
                       help='Specific sources to scrape (e.g., remoteok github)')
    parser.add_argument('--keywords', help='Keywords to search for')
    parser.add_argument('--genz-profile', help='Run specific Gen-Z profile search')
    parser.add_argument('--genz-only', action='store_true',
                       help='Only run Gen-Z searches, skip general scraping')
    parser.add_argument('--skip-import', action='store_true',
                       help='Skip importing to job board database')

    args = parser.parse_args()

    base_url = args.url.rstrip('/')

    print("=" * 60)
    print("JOB AGGREGATION API - TRIGGER SCRAPE")
    print("=" * 60)
    print(f"API URL: {base_url}")
    print()

    # Check if API is reachable
    try:
        health_url = f"{base_url}/health"
        response = requests.get(health_url, timeout=10)
        if response.status_code == 200:
            print("✅ API is reachable and healthy")
        else:
            print(f"⚠️  API returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot reach API at {base_url}")
        print(f"   Error: {e}")
        print("\n   Make sure:")
        print("   1. The server is running (python job_server.py)")
        print("   2. The URL is correct")
        print("   3. For Railway: Use your Railway public URL")
        return 1

    # Run Gen-Z searches
    if args.genz_only or args.genz_profile:
        run_genz_search(base_url, args.genz_profile)
        if not args.skip_import:
            time.sleep(5)
            import_jobs(base_url)
        get_stats(base_url)
        return 0

    # Run general scraping
    success = trigger_scrape(base_url, args.sources, args.keywords)

    if success and not args.skip_import:
        time.sleep(3)  # Give scraping a moment to finish
        import_jobs(base_url)

    # Show final stats
    get_stats(base_url)

    print("\n" + "=" * 60)
    print("✅ Complete!")
    print("=" * 60)

    return 0

if __name__ == "__main__":
    sys.exit(main())
