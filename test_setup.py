#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test script to verify setup is working correctly
Run this after installation to check everything is configured properly
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass


def test_imports():
    """Test that all required packages are installed"""
    print("Testing imports...", end=" ")
    try:
        import requests
        import bs4
        import sqlalchemy
        import pandas
        from dotenv import load_dotenv
        import dateutil
        print("[OK]")
        return True
    except ImportError as e:
        print(f"[FAIL]\nMissing package: {e}")
        print("Run: pip install -r requirements.txt")
        return False


def test_models():
    """Test database models"""
    print("Testing database models...", end=" ")
    try:
        from models import Job, DatabaseManager
        import tempfile
        import os
        import time

        # Use temporary database with unique name
        temp_db = os.path.join(tempfile.gettempdir(), f'test_jobs_{int(time.time())}.db')

        try:
            db = DatabaseManager(f'sqlite:///{temp_db}')

            # Test adding a job
            test_job = {
                'title': 'Test Developer',
                'company': 'Test Company',
                'location': 'Remote',
                'description': 'This is a test job',
                'url': 'https://example.com/job',
                'source': 'test',
                'posted_date': None,
                'job_type': 'Full-time',
                'salary': None,
                'tags': '[]',
                'remote': True
            }

            is_new, job = db.add_job(test_job)
            assert is_new, "Failed to add job"

            # Test deduplication
            is_new, duplicate = db.add_job(test_job)
            assert not is_new, "Deduplication failed"

            db.close()
        finally:
            # Clean up - ensure connection is closed first
            time.sleep(0.1)
            if os.path.exists(temp_db):
                try:
                    os.remove(temp_db)
                except:
                    pass  # Ignore cleanup errors

        print("[OK]")
        return True
    except Exception as e:
        print(f"[FAIL]\nError: {e}")
        return False


def test_scrapers():
    """Test that scrapers can be instantiated"""
    print("Testing scrapers...", end=" ")
    try:
        from scrapers import (
            RemoteOKScraper, RemotiveScraper, WeWorkRemotelyScraper,
            AuthenticJobsScraper, IndeedRSSScraper, GitHubJobsScraper
        )

        # Instantiate each scraper
        scrapers = [
            RemoteOKScraper(),
            RemotiveScraper(),
            WeWorkRemotelyScraper(),
            AuthenticJobsScraper(),
            IndeedRSSScraper(),
            GitHubJobsScraper()
        ]

        assert len(scrapers) > 0, "No scrapers available"
        print("[OK]")
        return True
    except Exception as e:
        print(f"[FAIL]\nError: {e}")
        return False


def test_aggregator():
    """Test the main aggregator class"""
    print("Testing aggregator...", end=" ")
    try:
        from aggregator import JobAggregator
        import tempfile
        import os
        import time

        # Use temporary database with unique name
        temp_db = os.path.join(tempfile.gettempdir(), f'test_aggregator_{int(time.time())}.db')

        try:
            aggregator = JobAggregator(database_url=f'sqlite:///{temp_db}')

            # Check scrapers are loaded
            assert len(aggregator.scrapers) > 0, "No scrapers loaded"

            # Test statistics
            stats = aggregator.get_statistics()
            assert 'total_jobs' in stats, "Statistics not working"

            aggregator.close()
        finally:
            # Clean up - ensure connection is closed first
            time.sleep(0.1)
            if os.path.exists(temp_db):
                try:
                    os.remove(temp_db)
                except:
                    pass  # Ignore cleanup errors

        print("[OK]")
        return True
    except Exception as e:
        print(f"[FAIL]\nError: {e}")
        return False


def test_scrape_single_source():
    """Test scraping from one source"""
    print("Testing live scrape (RemoteOK)...", end=" ")
    try:
        from scrapers import RemoteOKScraper

        scraper = RemoteOKScraper(timeout=10)
        jobs = scraper.scrape(keywords="python", max_pages=1)

        # RemoteOK should return some jobs
        if len(jobs) > 0:
            print(f"[OK] (found {len(jobs)} jobs)")

            # Verify job structure
            job = jobs[0]
            required_fields = ['title', 'company', 'location', 'url', 'source']
            for field in required_fields:
                assert field in job, f"Missing field: {field}"

            return True
        else:
            print("[WARN] (no jobs found, but scraper works)")
            return True

    except Exception as e:
        print(f"[FAIL]\nError: {e}")
        print("Note: This might be a network issue")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("JOB AGGREGATOR - SETUP TEST")
    print("="*60 + "\n")

    tests = [
        ("Imports", test_imports),
        ("Database Models", test_models),
        ("Scrapers", test_scrapers),
        ("Aggregator", test_aggregator),
        ("Live Scrape", test_scrape_single_source)
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"Unexpected error in {name}: {e}")
            results.append(False)

    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"[SUCCESS] ALL TESTS PASSED ({passed}/{total})")
        print("="*60)
        print("\nYour setup is ready! Try:")
        print("  python main.py --sources remoteok --max-pages 1")
        print("="*60 + "\n")
        return True
    else:
        print(f"[FAIL] SOME TESTS FAILED ({passed}/{total} passed)")
        print("="*60 + "\n")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
