"""
Migrate SQLite database to PostgreSQL (Neon, Supabase, etc.)

This script copies all job data from your local SQLite database
to a remote PostgreSQL database.

Usage:
    1. Set DATABASE_URL in .env file to your PostgreSQL connection string
    2. pip install psycopg2-binary
    3. python migrate_to_postgres.py
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Base, Job
from datetime import datetime

load_dotenv()


def test_connection(engine, db_type):
    """Test database connection"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        print(f"[OK] {db_type} connection successful")
        return True
    except Exception as e:
        print(f"[FAIL] {db_type} connection failed: {e}")
        return False


def get_table_stats(session):
    """Get job count from database"""
    try:
        count = session.query(Job).count()
        return count
    except Exception as e:
        print(f"Error getting stats: {e}")
        return 0


def migrate_sqlite_to_postgres(sqlite_path='sqlite:///job_board.db', batch_size=100):
    """
    Migrate data from SQLite to PostgreSQL

    Args:
        sqlite_path: Path to SQLite database
        batch_size: Number of records to commit at once
    """

    print("="*80)
    print("SQLITE TO POSTGRESQL MIGRATION")
    print("="*80)

    # Get PostgreSQL URL from environment
    postgres_url = os.getenv('DATABASE_URL')
    if not postgres_url:
        print("\n[FAIL] DATABASE_URL not set in .env file")
        print("\nPlease add your PostgreSQL connection string to .env:")
        print("DATABASE_URL=postgresql://user:pass@host/db?sslmode=require")
        return False

    print(f"\nSource (SQLite): {sqlite_path}")
    print(f"Destination (PostgreSQL): {postgres_url[:50]}...")

    # Create engines
    print("\n" + "-"*80)
    print("Step 1: Testing Connections")
    print("-"*80)

    try:
        sqlite_engine = create_engine(sqlite_path)
        postgres_engine = create_engine(postgres_url)
    except Exception as e:
        print(f"[FAIL] Could not create database engines: {e}")
        return False

    # Test connections
    if not test_connection(sqlite_engine, "SQLite"):
        return False
    if not test_connection(postgres_engine, "PostgreSQL"):
        print("\nTroubleshooting tips:")
        print("1. Check DATABASE_URL is correct")
        print("2. Ensure psycopg2-binary is installed: pip install psycopg2-binary")
        print("3. Verify SSL mode: add ?sslmode=require to connection string")
        return False

    # Create tables in PostgreSQL
    print("\n" + "-"*80)
    print("Step 2: Creating Tables in PostgreSQL")
    print("-"*80)

    try:
        Base.metadata.create_all(postgres_engine)
        print("[OK] Tables created successfully")
    except Exception as e:
        print(f"[FAIL] Could not create tables: {e}")
        return False

    # Setup sessions
    SQLiteSession = sessionmaker(bind=sqlite_engine)
    PostgresSession = sessionmaker(bind=postgres_engine)

    sqlite_session = SQLiteSession()
    postgres_session = PostgresSession()

    try:
        # Get job counts
        print("\n" + "-"*80)
        print("Step 3: Analyzing Data")
        print("-"*80)

        sqlite_count = get_table_stats(sqlite_session)
        postgres_count_before = get_table_stats(postgres_session)

        print(f"Jobs in SQLite: {sqlite_count}")
        print(f"Jobs in PostgreSQL (before): {postgres_count_before}")

        if sqlite_count == 0:
            print("\n[WARN] No jobs found in SQLite database")
            print("Run the scraper first to populate data:")
            print("  python main.py --scrape-all")
            return True

        # Migrate data
        print("\n" + "-"*80)
        print("Step 4: Migrating Jobs")
        print("-"*80)

        jobs = sqlite_session.query(Job).all()
        print(f"Found {len(jobs)} jobs to migrate")

        migrated = 0
        skipped = 0
        errors = 0

        print("\nMigrating jobs...")
        for i, job in enumerate(jobs, 1):
            try:
                # Check if job already exists (by job_id)
                existing = postgres_session.query(Job).filter_by(job_id=job.job_id).first()

                if existing:
                    skipped += 1
                else:
                    # Create new job object (detached from SQLite session)
                    new_job = Job(
                        job_id=job.job_id,
                        title=job.title,
                        company=job.company,
                        location=job.location,
                        salary=job.salary,
                        description=job.description,
                        url=job.url,
                        source=job.source,
                        posted_date=job.posted_date,
                        remote=job.remote,
                        job_type=job.job_type,
                        tags=job.tags,
                        created_at=job.created_at or datetime.utcnow()
                    )

                    postgres_session.add(new_job)
                    migrated += 1

                # Commit in batches
                if i % batch_size == 0:
                    postgres_session.commit()
                    print(f"  Progress: {i}/{len(jobs)} ({migrated} new, {skipped} skipped)")

            except Exception as e:
                print(f"  [WARN] Error migrating job {job.job_id}: {e}")
                errors += 1
                postgres_session.rollback()

        # Final commit
        postgres_session.commit()

        # Final stats
        postgres_count_after = get_table_stats(postgres_session)

        print("\n" + "="*80)
        print("MIGRATION COMPLETE")
        print("="*80)
        print(f"\nResults:")
        print(f"  Total jobs processed: {len(jobs)}")
        print(f"  New jobs migrated:    {migrated}")
        print(f"  Skipped (duplicates): {skipped}")
        print(f"  Errors:               {errors}")
        print(f"\nPostgreSQL Database:")
        print(f"  Jobs before:  {postgres_count_before}")
        print(f"  Jobs after:   {postgres_count_after}")
        print(f"  Jobs added:   {postgres_count_after - postgres_count_before}")

        print("\n[OK] Migration successful!")
        print("\nNext steps:")
        print("1. Update your .env file with DATABASE_URL")
        print("2. Restart job_server.py - it will now use PostgreSQL")
        print("3. All platforms can now access the same database!")

        return True

    except Exception as e:
        print(f"\n[FAIL] Migration error: {e}")
        postgres_session.rollback()
        return False

    finally:
        sqlite_session.close()
        postgres_session.close()


def verify_migration():
    """Verify migration was successful by comparing counts"""
    print("\n" + "="*80)
    print("VERIFICATION")
    print("="*80)

    postgres_url = os.getenv('DATABASE_URL')
    if not postgres_url:
        print("[SKIP] DATABASE_URL not set")
        return

    try:
        postgres_engine = create_engine(postgres_url)
        PostgresSession = sessionmaker(bind=postgres_engine)
        postgres_session = PostgresSession()

        total_jobs = postgres_session.query(Job).count()
        remote_jobs = postgres_session.query(Job).filter_by(remote=True).count()
        with_salary = postgres_session.query(Job).filter(
            Job.salary.isnot(None),
            Job.salary != ''
        ).count()

        print(f"\nPostgreSQL Database Stats:")
        print(f"  Total jobs:        {total_jobs}")
        print(f"  Remote jobs:       {remote_jobs} ({remote_jobs/total_jobs*100:.1f}%)")
        print(f"  Jobs with salary:  {with_salary} ({with_salary/total_jobs*100:.1f}%)")

        # Jobs by source
        from sqlalchemy import func
        by_source = postgres_session.query(
            Job.source,
            func.count(Job.id)
        ).group_by(Job.source).all()

        print(f"\nJobs by source:")
        for source, count in by_source:
            print(f"  {source:20s}: {count}")

        postgres_session.close()

    except Exception as e:
        print(f"[FAIL] Verification failed: {e}")


if __name__ == "__main__":
    print("\n")
    success = migrate_sqlite_to_postgres()

    if success:
        verify_migration()

    print("\n")
