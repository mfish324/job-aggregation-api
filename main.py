#!/usr/bin/env python3
"""
Job Aggregation Platform - Main Entry Point

Scrapes job listings from multiple sources and stores them in a database.
"""

import argparse
import sys
from aggregator import JobAggregator
from tabulate import tabulate


def main():
    parser = argparse.ArgumentParser(
        description='Aggregate job listings from multiple sources',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape all sources
  python main.py

  # Search for Python jobs
  python main.py --keywords "python developer"

  # Scrape specific sources only
  python main.py --sources remoteok github indeed

  # Filter by location
  python main.py --location "remote"

  # Export results to CSV
  python main.py --export jobs.csv

  # Show statistics
  python main.py --stats

  # Search existing jobs
  python main.py --search "javascript" --source github
        """
    )

    parser.add_argument(
        '--keywords', '-k',
        type=str,
        help='Search keywords (e.g., "python developer", "react")'
    )

    parser.add_argument(
        '--location', '-l',
        type=str,
        help='Job location (e.g., "remote", "New York", "San Francisco")'
    )

    parser.add_argument(
        '--sources', '-s',
        nargs='+',
        choices=['adzuna', 'remoteok', 'weworkremotely', 'remotive',
                 'authenticjobs', 'github', 'indeed', 'crunchboard'],
        help='Specific sources to scrape (default: all available)'
    )

    parser.add_argument(
        '--max-pages', '-m',
        type=int,
        default=5,
        help='Maximum pages to scrape per source (default: 5)'
    )

    parser.add_argument(
        '--export', '-e',
        type=str,
        help='Export results to file (CSV or JSON based on extension)'
    )

    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show database statistics'
    )

    parser.add_argument(
        '--search',
        type=str,
        help='Search existing jobs in database'
    )

    parser.add_argument(
        '--source',
        type=str,
        help='Filter by source when searching'
    )

    parser.add_argument(
        '--remote-only',
        action='store_true',
        help='Filter remote jobs only'
    )

    args = parser.parse_args()

    # Initialize aggregator
    aggregator = JobAggregator()

    try:
        # Show statistics
        if args.stats:
            stats = aggregator.get_statistics()
            print("\n" + "="*60)
            print("DATABASE STATISTICS")
            print("="*60)
            print(f"Total Jobs: {stats['total_jobs']}")
            print(f"Remote Jobs: {stats['remote_jobs']}")
            print("\nJobs by Source:")
            for source, count in sorted(stats['by_source'].items(), key=lambda x: x[1], reverse=True):
                print(f"  {source:20s}: {count}")
            print("="*60 + "\n")
            return

        # Search existing jobs
        if args.search:
            print(f"\nSearching for: {args.search}")
            jobs = aggregator.search_jobs(
                keyword=args.search,
                source=args.source,
                remote=args.remote_only if args.remote_only else None,
                limit=50
            )

            if jobs:
                print(f"\nFound {len(jobs)} jobs:\n")
                table_data = []
                for job in jobs[:20]:  # Show first 20
                    table_data.append([
                        job.title[:40] + '...' if len(job.title) > 40 else job.title,
                        job.company[:20] + '...' if len(job.company) > 20 else job.company,
                        job.location[:20] + '...' if len(job.location) > 20 else job.location,
                        job.source,
                        'Yes' if job.remote else 'No'
                    ])

                print(tabulate(
                    table_data,
                    headers=['Title', 'Company', 'Location', 'Source', 'Remote'],
                    tablefmt='grid'
                ))

                if len(jobs) > 20:
                    print(f"\n... and {len(jobs) - 20} more results")
            else:
                print("No jobs found matching your criteria")
            return

        # Export jobs
        if args.export:
            format_type = 'json' if args.export.endswith('.json') else 'csv'
            filters = {}
            if args.search:
                filters['keyword'] = args.search
            if args.source:
                filters['source'] = args.source
            if args.remote_only:
                filters['remote'] = True

            aggregator.export_jobs(args.export, format=format_type, filters=filters)
            return

        # Scrape jobs
        stats = aggregator.scrape_all(
            keywords=args.keywords,
            location=args.location,
            sources=args.sources,
            max_pages=args.max_pages
        )

        # Show summary table
        if stats['by_source']:
            print("Detailed Results:\n")
            table_data = []
            for source, data in sorted(stats['by_source'].items()):
                if 'error' in data:
                    table_data.append([source, 'ERROR', data['error'][:30], '-', '-'])
                else:
                    table_data.append([
                        source,
                        data['scraped'],
                        data['new'],
                        data['duplicates'],
                        f"{(data['duplicates'] / data['scraped'] * 100) if data['scraped'] > 0 else 0:.1f}%"
                    ])

            print(tabulate(
                table_data,
                headers=['Source', 'Scraped', 'New', 'Duplicates', 'Dup Rate'],
                tablefmt='grid'
            ))

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
    finally:
        aggregator.close()


if __name__ == '__main__':
    main()
