"""
Migrate 'jobs' table to 'job_listings' table on Railway database

This script:
1. Creates the new job_listings table
2. Copies all data from jobs to job_listings
3. Keeps the old jobs table (doesn't delete it)
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not set!")
    print("Set it to your Railway PostgreSQL URL")
    sys.exit(1)

print(f"Connecting to database...")
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        # Check if jobs table exists
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        print(f"Found tables: {tables}")

        if 'jobs' not in tables:
            print("ERROR: 'jobs' table does not exist!")
            sys.exit(1)

        # Check if job_listings already exists
        if 'job_listings' in tables:
            print("✓ job_listings table already exists")

            # Check row counts
            result = conn.execute(text("SELECT COUNT(*) FROM jobs"))
            jobs_count = result.scalar()

            result = conn.execute(text("SELECT COUNT(*) FROM job_listings"))
            job_listings_count = result.scalar()

            print(f"  - jobs table: {jobs_count} rows")
            print(f"  - job_listings table: {job_listings_count} rows")

            if job_listings_count > 0:
                print("✓ Migration appears complete!")
                sys.exit(0)

        print("\nCreating job_listings table...")

        # Create job_listings table with same structure as jobs
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS job_listings (
                id SERIAL PRIMARY KEY,
                job_id VARCHAR(255) UNIQUE NOT NULL,
                title VARCHAR(500) NOT NULL,
                company VARCHAR(255) NOT NULL,
                location VARCHAR(255),
                salary VARCHAR(255),
                source VARCHAR(100) NOT NULL,
                source_url VARCHAR(1000) NOT NULL,
                posted_date TIMESTAMP,
                remote BOOLEAN DEFAULT FALSE,
                job_type VARCHAR(100),
                preview_text VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP,
                view_count INTEGER DEFAULT 0,
                cached_description TEXT,
                cache_date TIMESTAMP
            )
        """))

        # Create indexes
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_job_listings_job_id ON job_listings(job_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_job_listings_title ON job_listings(title)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_job_listings_company ON job_listings(company)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_job_listings_location ON job_listings(location)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_job_listings_source ON job_listings(source)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_job_listings_posted_date ON job_listings(posted_date)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_job_listings_remote ON job_listings(remote)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_job_listings_created_at ON job_listings(created_at)"))

        conn.commit()
        print("✓ job_listings table created")

        print("\nCopying data from jobs to job_listings...")

        # Copy data (maps old columns to new columns, extracting preview from description)
        conn.execute(text("""
            INSERT INTO job_listings (
                job_id, title, company, location, salary, source, source_url,
                posted_date, remote, job_type, preview_text, created_at
            )
            SELECT
                job_id, title, company, location, salary, source, url as source_url,
                posted_date, remote, job_type,
                LEFT(description, 500) as preview_text,
                created_at
            FROM jobs
            ON CONFLICT (job_id) DO NOTHING
        """))

        conn.commit()

        # Get counts
        result = conn.execute(text("SELECT COUNT(*) FROM jobs"))
        jobs_count = result.scalar()

        result = conn.execute(text("SELECT COUNT(*) FROM job_listings"))
        job_listings_count = result.scalar()

        print(f"\n✓ Migration complete!")
        print(f"  - Copied {job_listings_count} rows from jobs to job_listings")
        print(f"  - Original jobs table still has {jobs_count} rows")
        print(f"\nRailway API should now work!")

except Exception as e:
    print(f"\nERROR during migration: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
