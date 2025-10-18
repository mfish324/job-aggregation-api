"""
Example usage of the Job Aggregator in your own applications
"""

from aggregator import JobAggregator
from datetime import datetime, timedelta


def example_1_basic_scraping():
    """Basic scraping example"""
    print("\n=== Example 1: Basic Scraping ===")

    aggregator = JobAggregator()

    # Scrape all sources
    stats = aggregator.scrape_all(
        keywords="python developer",
        location="remote",
        max_pages=2
    )

    print(f"Total new jobs: {stats['total_new']}")
    aggregator.close()


def example_2_search_jobs():
    """Search existing jobs in database"""
    print("\n=== Example 2: Searching Jobs ===")

    aggregator = JobAggregator()

    # Search for Python jobs
    jobs = aggregator.search_jobs(keyword="python", remote=True, limit=10)

    print(f"\nFound {len(jobs)} Python remote jobs:")
    for job in jobs[:5]:
        print(f"  - {job.title} at {job.company} ({job.source})")

    aggregator.close()


def example_3_specific_sources():
    """Scrape only specific sources"""
    print("\n=== Example 3: Specific Sources ===")

    aggregator = JobAggregator()

    # Only scrape RemoteOK and GitHub
    stats = aggregator.scrape_all(
        keywords="javascript",
        sources=['remoteok', 'github'],
        max_pages=3
    )

    print(f"Results from RemoteOK: {stats['by_source'].get('remoteok', {})}")
    print(f"Results from GitHub: {stats['by_source'].get('github', {})}")

    aggregator.close()


def example_4_export_data():
    """Export jobs to CSV"""
    print("\n=== Example 4: Exporting Data ===")

    aggregator = JobAggregator()

    # Export all remote Python jobs
    aggregator.export_jobs(
        filename='python_remote_jobs.csv',
        format='csv',
        filters={'keyword': 'python', 'remote': True}
    )

    aggregator.close()


def example_5_statistics():
    """Get database statistics"""
    print("\n=== Example 5: Statistics ===")

    aggregator = JobAggregator()

    stats = aggregator.get_statistics()
    print(f"\nTotal jobs in database: {stats['total_jobs']}")
    print(f"Remote jobs: {stats['remote_jobs']}")
    print("\nBreakdown by source:")
    for source, count in sorted(stats['by_source'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {source:15s}: {count:4d} jobs")

    aggregator.close()


def example_6_custom_workflow():
    """Custom workflow: Scrape, filter, and notify"""
    print("\n=== Example 6: Custom Workflow ===")

    aggregator = JobAggregator()

    # 1. Scrape for senior positions
    print("Step 1: Scraping for senior positions...")
    aggregator.scrape_all(
        keywords="senior engineer",
        location="remote",
        max_pages=2
    )

    # 2. Find high-value jobs (with salary information)
    print("\nStep 2: Finding jobs with salary info...")
    jobs = aggregator.search_jobs(keyword="senior", remote=True, limit=100)

    jobs_with_salary = [j for j in jobs if j.salary]
    print(f"Found {len(jobs_with_salary)} jobs with salary information")

    # 3. Show top results
    print("\nStep 3: Top results:")
    for job in jobs_with_salary[:5]:
        print(f"  - {job.title} at {job.company}")
        print(f"    Salary: {job.salary}")
        print(f"    URL: {job.url}\n")

    aggregator.close()


def example_7_incremental_updates():
    """Scrape only new jobs since last run"""
    print("\n=== Example 7: Incremental Updates ===")

    aggregator = JobAggregator()

    # Get initial count
    initial_stats = aggregator.get_statistics()
    print(f"Jobs before scraping: {initial_stats['total_jobs']}")

    # Scrape new jobs
    stats = aggregator.scrape_all(keywords="developer", max_pages=2)
    print(f"\nNew jobs added: {stats['total_new']}")
    print(f"Duplicates filtered: {stats['total_duplicates']}")

    # Get updated count
    final_stats = aggregator.get_statistics()
    print(f"Jobs after scraping: {final_stats['total_jobs']}")

    aggregator.close()


def example_8_integration_with_api():
    """Example: Building a REST API endpoint"""
    print("\n=== Example 8: API Integration ===")

    def get_jobs_api(keyword=None, source=None, remote=None, limit=20):
        """Simulated API endpoint"""
        aggregator = JobAggregator()
        jobs = aggregator.search_jobs(
            keyword=keyword,
            source=source,
            remote=remote,
            limit=limit
        )

        # Convert to JSON-serializable format
        results = []
        for job in jobs:
            results.append({
                'id': job.id,
                'title': job.title,
                'company': job.company,
                'location': job.location,
                'description': job.description[:200] + '...',
                'url': job.url,
                'source': job.source,
                'posted_date': job.posted_date.isoformat() if job.posted_date else None,
                'remote': job.remote
            })

        aggregator.close()
        return results

    # Simulate API call
    api_results = get_jobs_api(keyword="react", remote=True, limit=5)
    print(f"API returned {len(api_results)} results")
    print(f"First result: {api_results[0]['title'] if api_results else 'None'}")


def main():
    """Run all examples"""
    print("="*60)
    print("JOB AGGREGATOR - USAGE EXAMPLES")
    print("="*60)

    try:
        # Run examples
        example_1_basic_scraping()
        example_2_search_jobs()
        example_3_specific_sources()
        example_4_export_data()
        example_5_statistics()
        example_6_custom_workflow()
        example_7_incremental_updates()
        example_8_integration_with_api()

        print("\n" + "="*60)
        print("All examples completed successfully!")
        print("="*60)

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    # Run individual examples
    # example_1_basic_scraping()
    # example_2_search_jobs()
    # example_5_statistics()

    # Or run all examples
    main()
