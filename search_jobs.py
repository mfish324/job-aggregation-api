"""
Simple Job Search Utility
Search and view jobs directly from the database
"""

import os
import sys
from dotenv import load_dotenv
from job_board_integration import JobBoardDatabase, JobBoardAPI
from datetime import datetime
import json

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

load_dotenv()


def search_jobs(keyword=None, source=None, limit=20):
    """
    Search jobs in the database

    Args:
        keyword: Search in title, company, description
        source: Filter by source (e.g., 'adzuna', 'google_careers')
        limit: Number of results to show
    """
    database_url = os.getenv('DATABASE_URL', 'sqlite:///job_board.db')
    db = JobBoardDatabase(database_url)

    filters = {}
    if keyword:
        filters['keyword'] = keyword
    if source:
        filters['source'] = source

    try:
        jobs = db.get_jobs(filters=filters, limit=limit)

        if not jobs:
            print("\nNo jobs found matching your criteria.")
            return

        print(f"\n{'='*80}")
        print(f"FOUND {len(jobs)} JOBS")
        print(f"{'='*80}\n")

        for i, job in enumerate(jobs, 1):
            print(f"{i}. {job.title}")
            print(f"   Company: {job.company}")
            print(f"   Location: {job.location or 'Not specified'}")
            print(f"   Source: {job.source}")
            print(f"   Salary: {job.salary or 'Not specified'}")
            print(f"   Posted: {job.posted_date}")
            print(f"   Remote: {'Yes' if job.remote else 'No'}")
            print(f"   URL: {job.source_url}")
            print()

        # Show statistics
        total = db.get_total_count()
        print(f"{'='*80}")
        print(f"Total jobs in database: {total}")
        print(f"{'='*80}\n")

    except Exception as e:
        print(f"Error searching jobs: {e}")
        import traceback
        traceback.print_exc()


def show_stats():
    """Show database statistics"""
    database_url = os.getenv('DATABASE_URL', 'sqlite:///job_board.db')
    api = JobBoardAPI(database_url)

    try:
        stats = api.get_statistics()

        print(f"\n{'='*80}")
        print(f"DATABASE STATISTICS")
        print(f"{'='*80}\n")

        print(f"Total jobs: {stats['total_jobs']}")
        print(f"Remote jobs: {stats['remote_jobs']}")
        print(f"Jobs with salary: {stats.get('with_salary', 'N/A')}")

        print(f"\nJobs by source:")
        for source, count in sorted(stats['by_source'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {source}: {count}")

        print(f"\n{'='*80}\n")

    except Exception as e:
        print(f"Error getting statistics: {e}")
        import traceback
        traceback.print_exc()


def show_sources():
    """Show all unique sources in database"""
    database_url = os.getenv('DATABASE_URL', 'sqlite:///job_board.db')
    db = JobBoardDatabase(database_url)

    try:
        from sqlalchemy import func
        from job_board_integration import JobListing

        sources = db.session.query(
            JobListing.source,
            func.count(JobListing.id).label('count')
        ).group_by(JobListing.source).order_by(func.count(JobListing.id).desc()).all()

        print(f"\n{'='*80}")
        print(f"SOURCES IN DATABASE")
        print(f"{'='*80}\n")

        for source, count in sources:
            print(f"{source}: {count} jobs")

        print(f"\n{'='*80}\n")

    except Exception as e:
        print(f"Error getting sources: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Interactive menu"""
    print("\n" + "="*80)
    print("JOB DATABASE SEARCH UTILITY")
    print("="*80)

    while True:
        print("\nOptions:")
        print("1. Search jobs by keyword")
        print("2. Search jobs by source")
        print("3. View recent jobs")
        print("4. Show database statistics")
        print("5. Show all sources")
        print("6. Exit")

        choice = input("\nEnter choice (1-6): ").strip()

        if choice == '1':
            keyword = input("Enter keyword (title/company/description): ").strip()
            limit = input("Number of results (default 20): ").strip() or "20"
            search_jobs(keyword=keyword, limit=int(limit))

        elif choice == '2':
            source = input("Enter source (e.g., 'adzuna', 'google_careers'): ").strip()
            limit = input("Number of results (default 20): ").strip() or "20"
            search_jobs(source=source, limit=int(limit))

        elif choice == '3':
            limit = input("Number of results (default 20): ").strip() or "20"
            search_jobs(limit=int(limit))

        elif choice == '4':
            show_stats()

        elif choice == '5':
            show_sources()

        elif choice == '6':
            print("\nGoodbye!")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    # Check if command line arguments provided
    if len(sys.argv) > 1:
        if sys.argv[1] == "stats":
            show_stats()
        elif sys.argv[1] == "sources":
            show_sources()
        elif sys.argv[1] == "search":
            keyword = sys.argv[2] if len(sys.argv) > 2 else None
            search_jobs(keyword=keyword)
        else:
            print("Usage:")
            print("  python search_jobs.py              # Interactive mode")
            print("  python search_jobs.py stats        # Show statistics")
            print("  python search_jobs.py sources      # Show all sources")
            print("  python search_jobs.py search <keyword>  # Quick search")
    else:
        # Interactive mode
        main()
