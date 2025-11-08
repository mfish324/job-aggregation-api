#!/usr/bin/env python3
"""
Database Initialization Script for Job_APIs

This script initializes the PostgreSQL database schema on Railway.
It creates all required tables for the job board system.

Usage:
    python init_db.py
"""

import os
import sys
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Import models
from job_board_integration import Base, JobListing
from models import Job


def get_database_url():
    """Get database URL from environment"""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("[ERROR] DATABASE_URL environment variable not set")
        sys.exit(1)

    # Fix for newer SQLAlchemy versions (postgresql:// not postgres://)
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)

    return db_url


def check_existing_tables(engine):
    """Check what tables already exist"""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    return existing_tables


def create_tables(engine):
    """Create all tables defined in models"""
    print("\n[+] Creating database tables...")

    try:
        # Create all tables from Base metadata
        Base.metadata.create_all(engine)
        print("[SUCCESS] Successfully created tables from job_board_integration models")
        return True
    except Exception as e:
        print(f"[ERROR] Error creating tables: {e}")
        return False


def verify_tables(engine):
    """Verify tables were created correctly"""
    print("\n[+] Verifying database schema...")

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    print(f"\n[INFO] Found {len(tables)} table(s):")
    for table in tables:
        columns = inspector.get_columns(table)
        print(f"  [OK] {table} ({len(columns)} columns)")
        for col in columns:
            print(f"      - {col['name']} ({col['type']})")

    return tables


def get_table_counts(engine):
    """Get row counts for all tables"""
    print("\n[+] Checking table contents...")

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Check job_listings table
        count = session.execute(text("SELECT COUNT(*) FROM job_listings")).scalar()
        print(f"  job_listings: {count:,} rows")

        return count
    except Exception as e:
        print(f"  [WARNING] Could not count rows: {e}")
        return 0
    finally:
        session.close()


def main():
    """Main initialization function"""
    print("="*80)
    print("JOB_APIs DATABASE INITIALIZATION")
    print("="*80)

    # Get database URL
    db_url = get_database_url()
    db_name = db_url.split('/')[-1].split('?')[0]
    print(f"\n[DATABASE] {db_name}")
    print(f"[HOST] {db_url.split('@')[1].split('/')[0]}")

    # Create engine with connection pooling
    engine_kwargs = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
        'pool_size': 5,
        'max_overflow': 10,
        'connect_args': {
            'connect_timeout': 10
        }
    }

    try:
        print("\n[+] Connecting to database...")
        engine = create_engine(db_url, **engine_kwargs)

        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"[SUCCESS] Connected successfully!")
            print(f"   PostgreSQL version: {version.split(',')[0]}")

    except Exception as e:
        print(f"[ERROR] Failed to connect to database: {e}")
        sys.exit(1)

    # Check existing tables
    print("\n[+] Checking existing tables...")
    existing_tables = check_existing_tables(engine)

    if existing_tables:
        print(f"[WARNING] Found {len(existing_tables)} existing table(s):")
        for table in existing_tables:
            print(f"    - {table}")

        # Ask if user wants to proceed
        if 'job_listings' in existing_tables:
            print("\n[WARNING] 'job_listings' table already exists!")
            print("   Table creation will be skipped (no data will be lost)")
    else:
        print("   No existing tables found - will create fresh schema")

    # Create tables
    success = create_tables(engine)

    if not success:
        print("\n[ERROR] Database initialization FAILED")
        sys.exit(1)

    # Verify tables
    tables = verify_tables(engine)

    # Check required tables
    required_tables = ['job_listings']
    missing_tables = [t for t in required_tables if t not in tables]

    if missing_tables:
        print(f"\n[ERROR] Missing required tables: {', '.join(missing_tables)}")
        sys.exit(1)

    # Get table counts
    total_jobs = get_table_counts(engine)

    # Success summary
    print("\n" + "="*80)
    print("[SUCCESS] DATABASE INITIALIZATION COMPLETE")
    print("="*80)
    print(f"\n[SUMMARY]")
    print(f"   - Tables created: {len(tables)}")
    print(f"   - Total jobs: {total_jobs:,}")
    print(f"\n[NEXT STEPS]")
    print("   1. Test the API: curl https://web-production-94ca.up.railway.app/health")
    print("   2. Trigger scraping: curl -X POST https://web-production-94ca.up.railway.app/genz/search-priority")
    print("   3. Check stats: curl https://web-production-94ca.up.railway.app/stats")
    print("\n" + "="*80)


if __name__ == '__main__':
    main()
