"""
Migrate job_board.db (JobListing table) to PostgreSQL

This migrates the lightweight job board database to remote PostgreSQL.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from job_board_integration import JobListing, JobBoardDatabase
from datetime import datetime

load_dotenv()


def migrate_job_board_to_postgres():
    """Migrate job_board.db to PostgreSQL"""

    print("="*80)
    print("JOB BOARD TO POSTGRESQL MIGRATION")
    print("="*80)

    # Get PostgreSQL URL
    postgres_url = os.getenv('DATABASE_URL')
    if not postgres_url:
        print("\n[FAIL] DATABASE_URL not set in .env file")
        return False

    if 'sqlite' in postgres_url.lower():
        print("\n[FAIL] DATABASE_URL is still pointing to SQLite")
        print("Please set it to your PostgreSQL connection string")
        return False

    print(f"\nSource: sqlite:///job_board.db")
    print(f"Destination: {postgres_url[:60]}...")

    # Test connections
    print("\n" + "-"*80)
    print("Step 1: Testing Connections")
    print("-"*80)

    try:
        sqlite_db = JobBoardDatabase('sqlite:///job_board.db')
        postgres_db = JobBoardDatabase(postgres_url)

        sqlite_count = sqlite_db.get_total_count()
        postgres_count_before = postgres_db.get_total_count()

        print(f"[OK] SQLite connection: {sqlite_count} jobs")
        print(f"[OK] PostgreSQL connection: {postgres_count_before} jobs")

    except Exception as e:
        print(f"[FAIL] Connection error: {e}")
        return False

    if sqlite_count == 0:
        print("\n[WARN] No jobs in SQLite database")
        return True

    # Migrate
    print("\n" + "-"*80)
    print(f"Step 2: Migrating {sqlite_count} Jobs")
    print("-"*80)

    migrated = 0
    skipped = 0
    errors = 0

    try:
        # Get all jobs from SQLite
        sqlite_jobs = sqlite_db.session.query(JobListing).all()

        for i, job in enumerate(sqlite_jobs, 1):
            try:
                # Check if exists
                existing = postgres_db.session.query(JobListing).filter_by(
                    job_id=job.job_id
                ).first()

                if existing:
                    skipped += 1
                else:
                    # Add to PostgreSQL
                    new_job = JobListing(
                        job_id=job.job_id,
                        title=job.title,
                        company=job.company,
                        location=job.location,
                        salary=job.salary,
                        source=job.source,
                        source_url=job.source_url,
                        posted_date=job.posted_date,
                        remote=job.remote,
                        job_type=job.job_type,
                        preview_text=job.preview_text,
                        cached_description=job.cached_description,
                        view_count=job.view_count,
                        created_at=job.created_at
                    )

                    postgres_db.session.add(new_job)
                    migrated += 1

                # Commit in batches
                if i % 100 == 0:
                    postgres_db.session.commit()
                    print(f"  Progress: {i}/{sqlite_count} ({migrated} new, {skipped} skipped)")

            except Exception as e:
                print(f"  [WARN] Error migrating job: {e}")
                errors += 1
                postgres_db.session.rollback()

        # Final commit
        postgres_db.session.commit()
        postgres_count_after = postgres_db.get_total_count()

        print("\n" + "="*80)
        print("MIGRATION COMPLETE")
        print("="*80)
        print(f"\nResults:")
        print(f"  Total processed:      {sqlite_count}")
        print(f"  New jobs migrated:    {migrated}")
        print(f"  Skipped (duplicates): {skipped}")
        print(f"  Errors:               {errors}")
        print(f"\nPostgreSQL Database:")
        print(f"  Jobs before:  {postgres_count_before}")
        print(f"  Jobs after:   {postgres_count_after}")
        print(f"  Jobs added:   {postgres_count_after - postgres_count_before}")

        print("\n[OK] Migration successful!")
        print("\nNext steps:")
        print("1. Restart job_server.py - it will now use Neon PostgreSQL")
        print("2. All platforms can access the same database!")
        print("3. Test: curl http://localhost:8001/stats")

        return True

    except Exception as e:
        print(f"\n[FAIL] Migration error: {e}")
        postgres_db.session.rollback()
        return False

    finally:
        sqlite_db.close()
        postgres_db.close()


if __name__ == "__main__":
    print("\n")
    migrate_job_board_to_postgres()
    print("\n")
