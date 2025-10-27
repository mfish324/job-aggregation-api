#!/usr/bin/env python3
"""
Check Railway database job count and freshness
"""
import os
from dotenv import load_dotenv
import psycopg2
from datetime import datetime

load_dotenv()

# Get Railway DATABASE_URL
db_url = os.getenv('DATABASE_URL')

if not db_url:
    print("ERROR: DATABASE_URL not found in .env")
    print("This should be your Railway PostgreSQL connection string")
    exit(1)

try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()

    # Get total job count
    cursor.execute('SELECT COUNT(*) FROM jobs')
    total = cursor.fetchone()[0]
    print(f'Total jobs in Railway database: {total}')

    # Get jobs by source
    cursor.execute('SELECT source, COUNT(*) as count FROM jobs GROUP BY source ORDER BY count DESC')
    print('\nJobs by source:')
    for row in cursor.fetchall():
        print(f'  {row[0]}: {row[1]}')

    # Get latest job
    cursor.execute('SELECT MAX(created_at) FROM jobs')
    latest = cursor.fetchone()[0]
    if latest:
        print(f'\nLatest job added: {latest}')

        # Calculate age
        now = datetime.now(latest.tzinfo)
        age = now - latest
        print(f'Age: {age.days} days, {age.seconds // 3600} hours ago')

        if age.days > 1:
            print('\n⚠️  WARNING: Jobs are stale! Last update was more than 24 hours ago.')
            print('The automated scraper may not be running.')
    else:
        print('\n⚠️  WARNING: No jobs in database!')

    # Check for recent jobs (last 24 hours)
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE created_at > NOW() - INTERVAL '24 hours'")
    recent = cursor.fetchone()[0]
    print(f'\nJobs added in last 24 hours: {recent}')

    if recent == 0:
        print('⚠️  No jobs added recently. Scraper is not running!')

    conn.close()

except Exception as e:
    print(f'\nERROR connecting to Railway database: {e}')
    print('\nMake sure DATABASE_URL in .env is set to Railway PostgreSQL URL')
    print('Format: postgresql://user:password@host:port/database')
