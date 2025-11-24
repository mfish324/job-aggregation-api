"""
Simple Job Viewer - View jobs from the database
"""

import os
import sys
from dotenv import load_dotenv
from job_board_integration import JobBoardDatabase, JobBoardAPI

load_dotenv()

def view_jobs(limit=20, source=None):
    """View jobs from database"""
    database_url = os.getenv('DATABASE_URL', 'sqlite:///job_board.db')
    db = JobBoardDatabase(database_url)

    filters = {}
    if source:
        filters['source'] = source

    jobs = db.get_jobs(filters=filters, limit=limit)

    print(f"\n{'='*100}")
    print(f"SHOWING {len(jobs)} JOBS FROM DATABASE")
    print(f"{'='*100}\n")

    for i, job in enumerate(jobs, 1):
        print(f"{i}. {job.title}")
        print(f"   Company: {job.company}")
        print(f"   Location: {job.location or 'Not specified'}")
        print(f"   Source: {job.source}")
        print(f"   Salary: {job.salary or 'Not specified'}")
        print(f"   Remote: {'Yes' if job.remote else 'No'}")
        print(f"   Posted: {job.posted_date}")
        print()

def show_stats():
    """Show database stats"""
    database_url = os.getenv('DATABASE_URL', 'sqlite:///job_board.db')
    api = JobBoardAPI(database_url)

    stats = api.get_statistics()

    print(f"\n{'='*100}")
    print(f"DATABASE STATISTICS")
    print(f"{'='*100}\n")

    print(f"Total jobs: {stats['total_jobs']}")
    print(f"Remote jobs: {stats['remote_jobs']}")
    print(f"Jobs with salary: {stats.get('with_salary', 0)}")

    print(f"\nJobs by source:")
    for source, count in sorted(stats['by_source'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {source:25} {count:4} jobs")

    print(f"\n{'='*100}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "stats":
            show_stats()
        elif sys.argv[1] == "source":
            source = sys.argv[2] if len(sys.argv) > 2 else None
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20
            view_jobs(source=source, limit=limit)
        else:
            limit = int(sys.argv[1])
            view_jobs(limit=limit)
    else:
        show_stats()
        print("\nUsage:")
        print("  python view_jobs.py              # Show stats")
        print("  python view_jobs.py stats        # Show stats")
        print("  python view_jobs.py 10           # View 10 jobs")
        print("  python view_jobs.py source adzuna 10  # View 10 Adzuna jobs")
