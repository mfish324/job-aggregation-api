#!/usr/bin/env python3
"""
View Job Details Script
Shows complete job information including URLs and descriptions
"""

import argparse
from aggregator import JobAggregator


def view_jobs(keyword=None, source=None, remote_only=False, limit=10, show_full=False):
    """View job details"""
    aggregator = JobAggregator()

    jobs = aggregator.search_jobs(
        keyword=keyword,
        source=source,
        remote=remote_only if remote_only else None,
        limit=limit
    )

    if not jobs:
        print("No jobs found matching your criteria")
        aggregator.close()
        return

    print(f"\n{'='*80}")
    print(f"Found {len(jobs)} jobs")
    print(f"{'='*80}\n")

    for i, job in enumerate(jobs, 1):
        print(f"{i}. {job.title}")
        print(f"   Company: {job.company}")
        print(f"   Location: {job.location}")
        print(f"   Source: {job.source}")
        print(f"   Remote: {'Yes' if job.remote else 'No'}")
        print(f"   Posted: {job.posted_date.strftime('%Y-%m-%d') if job.posted_date else 'Unknown'}")

        if job.salary:
            print(f"   Salary: {job.salary}")

        if job.job_type:
            print(f"   Type: {job.job_type}")

        print(f"   URL: {job.url}")

        if show_full and job.description:
            desc = job.description[:300] + '...' if len(job.description) > 300 else job.description
            print(f"   Description: {desc}")

        print()

    aggregator.close()


def main():
    parser = argparse.ArgumentParser(
        description='View detailed job listings',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # View 10 Python jobs
  python view_jobs.py --keyword "python"

  # View remote JavaScript jobs with full details
  python view_jobs.py --keyword "javascript" --remote-only --full

  # View jobs from specific source
  python view_jobs.py --source remoteok --limit 5

  # View all remote jobs
  python view_jobs.py --remote-only --limit 20
        """
    )

    parser.add_argument(
        '--keyword', '-k',
        type=str,
        help='Search keyword'
    )

    parser.add_argument(
        '--source', '-s',
        type=str,
        help='Filter by source'
    )

    parser.add_argument(
        '--remote-only', '-r',
        action='store_true',
        help='Show only remote jobs'
    )

    parser.add_argument(
        '--limit', '-l',
        type=int,
        default=10,
        help='Number of jobs to show (default: 10)'
    )

    parser.add_argument(
        '--full', '-f',
        action='store_true',
        help='Show full details including description'
    )

    args = parser.parse_args()

    view_jobs(
        keyword=args.keyword,
        source=args.source,
        remote_only=args.remote_only,
        limit=args.limit,
        show_full=args.full
    )


if __name__ == '__main__':
    main()
