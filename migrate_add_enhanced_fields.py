"""
Database Migration: Add Enhanced Fields
Adds company_website and tags columns to job_listings table
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def run_migration():
    """Add company_website and tags columns to job_listings table"""
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("Error: DATABASE_URL not found in environment")
        return False

    print(f"Connecting to database...")
    engine = create_engine(database_url)

    try:
        with engine.connect() as conn:
            print("Adding company_website column...")
            conn.execute(text(
                'ALTER TABLE job_listings ADD COLUMN IF NOT EXISTS company_website VARCHAR(500)'
            ))

            print("Adding tags column...")
            conn.execute(text(
                'ALTER TABLE job_listings ADD COLUMN IF NOT EXISTS tags TEXT'
            ))

            conn.commit()
            print("\nMigration completed successfully!")
            print("  - Added company_website VARCHAR(500)")
            print("  - Added tags TEXT")

            # Verify columns were added
            result = conn.execute(text("""
                SELECT column_name, data_type, character_maximum_length
                FROM information_schema.columns
                WHERE table_name = 'job_listings'
                AND column_name IN ('company_website', 'tags')
                ORDER BY column_name
            """))

            print("\nVerification:")
            for row in result:
                print(f"  - {row.column_name}: {row.data_type}", end="")
                if row.character_maximum_length:
                    print(f"({row.character_maximum_length})")
                else:
                    print()

            return True

    except Exception as e:
        print(f"Error running migration: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        engine.dispose()

if __name__ == "__main__":
    print("="*60)
    print("DATABASE MIGRATION: Add Enhanced Fields")
    print("="*60)
    print()

    success = run_migration()

    if success:
        print("\n" + "="*60)
        print("Migration completed successfully!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("Migration failed!")
        print("="*60)
