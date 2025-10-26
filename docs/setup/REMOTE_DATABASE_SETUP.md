# Remote Database Setup - Free Options

Make your job database accessible to multiple users and platforms with a free remote PostgreSQL database!

## Best Free Options (Recommended Order)

### 1. Neon.tech (BEST - Recommended) ⭐

**Pros:**
- ✅ **3 GB free storage** (plenty for job data)
- ✅ **Generous free tier** with no credit card required
- ✅ **PostgreSQL** (industry standard)
- ✅ **Serverless** - auto-scales
- ✅ **Fast setup** - 2 minutes
- ✅ **Great performance**
- ✅ **Branching support** for dev/prod

**Free Tier:**
- 3 GB storage
- Unlimited projects
- 100 hours compute/month (enough for 24/7 if small queries)
- PostgreSQL compatible

**Sign up**: https://neon.tech

---

### 2. Supabase (Great Alternative) ⭐

**Pros:**
- ✅ **500 MB free database**
- ✅ **PostgreSQL**
- ✅ **No credit card** required
- ✅ **Built-in API** (REST + GraphQL)
- ✅ **Real-time subscriptions**
- ✅ **Authentication included**

**Free Tier:**
- 500 MB database
- 2 GB bandwidth/month
- 50,000 monthly active users
- Unlimited API requests

**Sign up**: https://supabase.com

---

### 3. ElephantSQL (Simple & Reliable)

**Pros:**
- ✅ **20 MB free** (good for starter)
- ✅ **PostgreSQL**
- ✅ **Very simple setup**
- ✅ **Reliable**

**Free Tier:**
- 20 MB storage (can hold ~10,000 jobs)
- 5 concurrent connections

**Sign up**: https://www.elephantsql.com

---

### 4. Railway (Developer Friendly)

**Pros:**
- ✅ **500 MB free**
- ✅ **PostgreSQL**
- ✅ **$5 free credit/month**
- ✅ **Easy deployment**

**Free Tier:**
- $5 free credit/month
- ~500 MB storage

**Sign up**: https://railway.app

---

## Quick Setup Guide (Neon.tech - Recommended)

### Step 1: Create Free Account

1. Go to **https://neon.tech**
2. Click "Sign Up" (use GitHub or email)
3. No credit card required!

### Step 2: Create Database

1. Click **"Create Project"**
2. Name: `job-aggregator`
3. Region: Choose closest to you (e.g., US East)
4. PostgreSQL version: 16 (latest)
5. Click **"Create Project"**

### Step 3: Get Connection String

After creation, you'll see a connection string like:

```
postgresql://username:password@ep-cool-name-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

**Copy this!** You'll need it.

---

## Configure Your Job Aggregator

### Option 1: Environment Variable (Recommended)

Edit your `.env` file:

```bash
# .env
DATABASE_URL=postgresql://username:password@ep-cool-name-123456.us-east-2.aws.neon.tech/neondb?sslmode=require

# Keep your other settings
RAPIDAPI_KEY=your_key_here
RAPIDAPI_INDEED_HOST=indeed-jobs-api.p.rapidapi.com
```

### Option 2: Direct Configuration

Edit the database connection in your Python files:

```python
# Instead of:
database_url = 'sqlite:///job_board.db'

# Use:
database_url = os.getenv('DATABASE_URL', 'sqlite:///job_board.db')
```

---

## Install PostgreSQL Driver

```bash
pip install psycopg2-binary
```

Or add to `requirements.txt`:

```txt
psycopg2-binary>=2.9.9
```

---

## Migrate Your Existing Data

### Automatic Migration Script

I'll create a script to migrate your existing SQLite data to PostgreSQL:

```python
# migrate_to_postgres.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from models import Base, Job, DatabaseManager

load_dotenv()

def migrate_sqlite_to_postgres():
    """Migrate data from SQLite to PostgreSQL"""

    # Source (SQLite)
    sqlite_url = 'sqlite:///job_board.db'
    sqlite_engine = create_engine(sqlite_url)

    # Destination (PostgreSQL)
    postgres_url = os.getenv('DATABASE_URL')
    if not postgres_url:
        print("ERROR: DATABASE_URL not set in .env file")
        return

    postgres_engine = create_engine(postgres_url)

    # Create tables in PostgreSQL
    print("Creating tables in PostgreSQL...")
    Base.metadata.create_all(postgres_engine)

    # Migrate data
    print("Migrating jobs...")

    from sqlalchemy.orm import sessionmaker

    SQLiteSession = sessionmaker(bind=sqlite_engine)
    PostgresSession = sessionmaker(bind=postgres_engine)

    sqlite_session = SQLiteSession()
    postgres_session = PostgresSession()

    try:
        # Get all jobs from SQLite
        jobs = sqlite_session.query(Job).all()
        print(f"Found {len(jobs)} jobs in SQLite")

        # Copy to PostgreSQL
        migrated = 0
        for job in jobs:
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
                created_at=job.created_at
            )

            # Check if already exists
            existing = postgres_session.query(Job).filter_by(job_id=job.job_id).first()
            if not existing:
                postgres_session.add(new_job)
                migrated += 1

                if migrated % 100 == 0:
                    print(f"Migrated {migrated} jobs...")

        postgres_session.commit()
        print(f"\nMigration complete!")
        print(f"Total migrated: {migrated}")
        print(f"Total in PostgreSQL: {postgres_session.query(Job).count()}")

    except Exception as e:
        print(f"Error during migration: {e}")
        postgres_session.rollback()
    finally:
        sqlite_session.close()
        postgres_session.close()

if __name__ == "__main__":
    migrate_sqlite_to_postgres()
```

Run the migration:

```bash
# Install PostgreSQL driver
pip install psycopg2-binary

# Run migration
python migrate_to_postgres.py
```

---

## Update Your Applications

### Job Server

No changes needed! It uses `DATABASE_URL` from environment:

```python
# job_server.py already uses environment variable
database_url = os.getenv('DATABASE_URL', 'sqlite:///job_board.db')
job_api = JobBoardAPI(database_url=database_url)
```

### Scheduled Scraper

```python
# scheduled_scraper.py
def __init__(self, database_url=None):
    if database_url is None:
        database_url = os.getenv('DATABASE_URL', 'sqlite:///job_board.db')
    self.aggregator = JobAggregator(database_url=database_url)
```

---

## Access from Multiple Platforms

Now your Django and other platforms can all use the same database!

### Django Platform

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'neondb',
        'USER': 'username',
        'PASSWORD': 'password',
        'HOST': 'ep-cool-name-123456.us-east-2.aws.neon.tech',
        'PORT': '5432',
    }
}

# Or use dj-database-url
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL')
    )
}
```

### Other Platforms

Any platform can connect using the PostgreSQL connection string!

**Node.js:**
```javascript
const { Pool } = require('pg');
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false }
});
```

**PHP:**
```php
$db_url = getenv('DATABASE_URL');
$conn = pg_connect($db_url);
```

---

## Connection Pooling (Important!)

For production, use connection pooling to handle multiple users:

```python
# Update models.py or aggregator.py
from sqlalchemy.pool import QueuePool

engine = create_engine(
    database_url,
    poolclass=QueuePool,
    pool_size=10,  # Max 10 connections
    max_overflow=20,  # Allow up to 20 extra connections if busy
    pool_pre_ping=True  # Check connection health before using
)
```

---

## Security Best Practices

### 1. Use Environment Variables

**Never hardcode credentials!**

```bash
# .env (DO NOT commit to git)
DATABASE_URL=postgresql://user:pass@host/db
```

### 2. Update .gitignore

Already done, but verify:

```
.env
*.db
```

### 3. Read-Only Access for Other Users (Optional)

In PostgreSQL, create a read-only user:

```sql
-- Connect to your Neon database via their web SQL editor
CREATE USER readonly_user WITH PASSWORD 'your_password';
GRANT CONNECT ON DATABASE neondb TO readonly_user;
GRANT USAGE ON SCHEMA public TO readonly_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO readonly_user;
```

Share this connection string with read-only users:
```
postgresql://readonly_user:password@host/db
```

---

## Testing the Remote Database

### Test Connection

```bash
# Test with psql (if installed)
psql "postgresql://username:password@host/db"

# Or use Python
python -c "from sqlalchemy import create_engine; import os; engine = create_engine(os.getenv('DATABASE_URL')); print('Connected!' if engine.connect() else 'Failed')"
```

### Run the API Server

```bash
# Set DATABASE_URL in .env
DATABASE_URL=postgresql://...

# Start server
python job_server.py

# Test
curl http://localhost:8001/stats
```

---

## Cost Comparison

| Service | Free Storage | Monthly Cost (Paid) | Best For |
|---------|--------------|---------------------|----------|
| **Neon** | 3 GB | $19/mo for more | Production, scaling |
| **Supabase** | 500 MB | $25/mo | Full stack with auth |
| **ElephantSQL** | 20 MB | $5/mo for 1 GB | Small projects |
| **Railway** | $5 credit | Pay as you go | Dev projects |

**Recommendation**: Start with **Neon.tech** - 3 GB free is enough for 100,000+ jobs!

---

## Monitoring & Management

### Neon Dashboard

- View database size
- Monitor queries
- Create backups
- View connection stats

### Query Your Database

```python
from sqlalchemy import create_engine, text
import os

engine = create_engine(os.getenv('DATABASE_URL'))

# Get database stats
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT
            count(*) as total_jobs,
            count(*) FILTER (WHERE remote = true) as remote_jobs,
            pg_size_pretty(pg_total_relation_size('job')) as table_size
        FROM job
    """))
    stats = result.fetchone()
    print(f"Total jobs: {stats[0]}")
    print(f"Remote jobs: {stats[1]}")
    print(f"Database size: {stats[2]}")
```

---

## Backup Strategy

### Automatic Backups (Neon)

Neon provides automatic backups:
- Point-in-time recovery
- 7-day retention on free tier
- 30-day retention on paid tier

### Manual Backup

```bash
# Export to SQL file
pg_dump "postgresql://user:pass@host/db" > backup.sql

# Restore
psql "postgresql://user:pass@host/db" < backup.sql
```

---

## Troubleshooting

### "SSL connection required"

Add `?sslmode=require` to connection string:
```
postgresql://user:pass@host/db?sslmode=require
```

### "Too many connections"

Use connection pooling (see above) or upgrade tier.

### Slow queries

Add indexes:
```sql
CREATE INDEX idx_job_company ON job(company);
CREATE INDEX idx_job_location ON job(location);
CREATE INDEX idx_job_posted_date ON job(posted_date);
```

### Migration failed

Check error logs and retry with smaller batches.

---

## Summary

✅ **Best Option**: Neon.tech (3 GB free)
✅ **Setup Time**: 5-10 minutes
✅ **Migration**: Automatic script provided
✅ **Multi-User**: ✓ Supports multiple platforms
✅ **Free Forever**: ✓ No credit card needed
✅ **Production Ready**: ✓ With connection pooling

## Quick Start Commands

```bash
# 1. Sign up at https://neon.tech
# 2. Create project and copy connection string
# 3. Add to .env file
echo "DATABASE_URL=postgresql://..." >> .env

# 4. Install PostgreSQL driver
pip install psycopg2-binary

# 5. Migrate data
python migrate_to_postgres.py

# 6. Start server (now using remote DB)
python job_server.py

# Done! Your job database is now accessible remotely!
```

All your platforms can now access the same job database! 🚀
