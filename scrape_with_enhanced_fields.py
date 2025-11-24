"""
Quick Scrape to Test Enhanced Fields
Scrape a few jobs and verify they're saved with enhanced fields
"""

import os
from dotenv import load_dotenv
from job_board_integration import JobBoardDatabase
from scrapers import RemoteOKScraper
import json

load_dotenv()

def scrape_and_save():
    """Scrape some jobs and save them to database"""
    print("="*80)
    print("SCRAPING JOBS WITH ENHANCED FIELDS")
    print("="*80)

    # Initialize database
    database_url = os.getenv('DATABASE_URL')
    db = JobBoardDatabase(database_url)

    # Scrape some RemoteOK jobs (fastest API)
    print("\nScraping RemoteOK jobs...")
    scraper = RemoteOKScraper()
    jobs = scraper.scrape(max_pages=1)

    print(f"Found {len(jobs)} jobs")

    # Display first 3 jobs to show enhanced fields BEFORE saving
    print("\nFirst 3 jobs with enhanced fields (before saving):")
    for i, job in enumerate(jobs[:3], 1):
        print(f"\n{i}. {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Company Website: {job.get('company_website', 'MISSING')}")
        print(f"   Tags: {job.get('tags', 'MISSING')[:100]}...")  # First 100 chars

    # Save first 5 jobs
    saved_count = 0
    for job in jobs[:5]:
        try:
            is_new, _ = db.add_job(job)
            if is_new:
                saved_count += 1
                print(f"  Saved NEW: {job['title']} at {job['company']}")
            else:
                print(f"  Already exists: {job['title']}")
        except Exception as e:
            print(f"  Error saving job: {e}")

    print(f"\nSaved {saved_count} jobs")

    # Query and display saved jobs with enhanced fields
    print("\n" + "="*80)
    print("VERIFYING ENHANCED FIELDS IN DATABASE")
    print("="*80)

    from job_board_integration import JobListing
    recent_jobs = db.session.query(JobListing).filter(
        JobListing.source == 'remoteok'
    ).order_by(JobListing.created_at.desc()).limit(3).all()

    for i, job in enumerate(recent_jobs, 1):
        print(f"\n{i}. {job.title}")
        print(f"   Company: {job.company}")
        print(f"   Company Website: {job.company_website or 'None'}")
        print(f"   Tags: {job.tags or 'None'}")

        if job.tags:
            try:
                tags_list = json.loads(job.tags)
                print(f"   Skills Found: {', '.join(tags_list[:10])}")
            except:
                pass

    print("\n" + "="*80)
    print("COMPLETE")
    print("="*80)

if __name__ == "__main__":
    scrape_and_save()
