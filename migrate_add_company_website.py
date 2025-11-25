"""
Migration script to add company_website column to jobs table
Run this once to update your existing jobs.db
"""

import sqlite3
import os

def migrate_add_company_website():
    """Add company_website column to jobs table"""
    db_path = 'jobs.db'

    if not os.path.exists(db_path):
        print(f"Database {db_path} not found. Skipping migration.")
        print("The column will be created automatically when the first job is scraped.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(jobs)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'company_website' in columns:
            print("[OK] company_website column already exists in jobs table")
        else:
            # Add the column
            cursor.execute("""
                ALTER TABLE jobs
                ADD COLUMN company_website VARCHAR(1000)
            """)
            conn.commit()
            print("[OK] Successfully added company_website column to jobs table")

    except sqlite3.Error as e:
        print(f"[ERROR] Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

    print("\nMigration complete!")
    print("You can now run the scraper to populate company websites for new jobs.")

if __name__ == '__main__':
    print("=" * 60)
    print("Database Migration: Add company_website column")
    print("=" * 60)
    print()
    migrate_add_company_website()
