# Quick Remote Database Setup (5 Minutes)

Make your job database accessible to multiple users in 5 minutes!

## Option 1: Neon.tech (Recommended - 3 GB Free)

### Step 1: Create Account (1 minute)

1. Go to **https://neon.tech**
2. Click "Sign Up" → Use GitHub
3. No credit card required!

### Step 2: Create Database (1 minute)

1. Click **"Create Project"**
2. Project name: `job-aggregator`
3. Region: **US East** (or closest to you)
4. Click **"Create Project"**

### Step 3: Copy Connection String (30 seconds)

You'll see something like:

```
postgresql://alex:AbC123xyz@ep-cool-breeze-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

**Click the copy button** 📋

### Step 4: Add to Your Project (1 minute)

Open your `.env` file and add:

```bash
DATABASE_URL=postgresql://alex:AbC123xyz@ep-cool-breeze-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

Replace with YOUR connection string from Neon!

### Step 5: Install PostgreSQL Driver (1 minute)

```bash
pip install psycopg2-binary
```

### Step 6: Migrate Your Data (1 minute)

```bash
python migrate_to_postgres.py
```

You'll see:
```
MIGRATION COMPLETE
Results:
  Total jobs processed: 1710
  New jobs migrated:    1710
  Skipped (duplicates): 0
```

### Step 7: Done! 🎉

```bash
# Start your API server (now using remote database)
python job_server.py

# Test it
curl http://localhost:8001/stats
```

**Your database is now remote and accessible by all your platforms!**

---

## What You Get (Free Tier)

✅ **3 GB storage** (enough for 100,000+ jobs)
✅ **Unlimited projects**
✅ **100 hours compute/month** (plenty for 24/7 small queries)
✅ **Automatic backups**
✅ **SSL encrypted**
✅ **99.9% uptime**
✅ **No credit card required**

---

## Alternative: Supabase (500 MB Free)

If you prefer Supabase:

1. Go to **https://supabase.com**
2. Sign up (GitHub or email)
3. Click **"New Project"**
4. Name: `job-aggregator`
5. Database password: (create a strong password)
6. Region: Choose closest
7. Click **"Create new project"** (takes 2 minutes to provision)

**Get connection string:**
- Go to **Settings** → **Database**
- Copy **Connection string** under "Connection string"
- Select **"URI"** tab
- Replace `[YOUR-PASSWORD]` with your password

Add to `.env`:
```bash
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
```

Then run steps 5-7 above.

---

## Access from Other Platforms

### Your Django Platform

```python
# settings.py
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'neondb'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': '5432',
    }
}

# Or simpler with dj-database-url:
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL')
    )
}
```

### Your Other Platform (Node.js)

```javascript
const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false }
});

// Query jobs
const result = await pool.query('SELECT * FROM job LIMIT 10');
console.log(result.rows);
```

### Any Platform

Just use the connection string! Works with:
- Python ✅
- Node.js ✅
- PHP ✅
- Ruby ✅
- Java ✅
- Any language with PostgreSQL support ✅

---

## Verify It Works

### Test 1: Check Connection

```bash
python -c "from sqlalchemy import create_engine; import os; from dotenv import load_dotenv; load_dotenv(); engine = create_engine(os.getenv('DATABASE_URL')); conn = engine.connect(); print('Connected to remote database!')"
```

### Test 2: Query Data

```bash
curl http://localhost:8001/stats
```

Should return:
```json
{
  "total_jobs": 1710,
  "remote_jobs": 1700,
  "by_source": {...}
}
```

### Test 3: From Another Machine

On your other computer/platform:
```bash
curl "http://YOUR_SERVER_IP:8001/jobs?per_page=5"
```

---

## Share with Team Members

### Read-Only Access

Give team members read-only access:

1. Go to Neon dashboard
2. Click your project
3. Click **"Connection String"**
4. Share this with your team

They can view jobs but not modify them.

### Full Access

Share the full `DATABASE_URL` from your `.env` file (securely!)

---

## Costs

| Users | Queries/Day | Storage | Cost |
|-------|-------------|---------|------|
| 1-10 | <10,000 | <3 GB | **FREE** |
| 10-100 | <100,000 | <10 GB | $19/mo |
| 100+ | Unlimited | <100 GB | $69/mo |

**Start free, upgrade only if needed!**

---

## Troubleshooting

### "Could not connect to server"

Check:
1. Is `DATABASE_URL` in `.env` file?
2. Did you add `?sslmode=require` to the URL?
3. Is `psycopg2-binary` installed?

### "No module named psycopg2"

```bash
pip install psycopg2-binary
```

### Migration shows 0 jobs

Your SQLite database is empty. Scrape first:
```bash
python main.py --scrape-all
```

Then re-run migration:
```bash
python migrate_to_postgres.py
```

---

## Security Checklist

✅ DATABASE_URL in `.env` file (not hardcoded)
✅ `.env` in `.gitignore` (don't commit passwords!)
✅ SSL enabled (`?sslmode=require` in URL)
✅ Strong password used
✅ Read-only users for team members
✅ Regular backups (automatic with Neon)

---

## Next Steps

1. ✅ Database is remote
2. ✅ Multiple platforms can access it
3. **Now**: Deploy your API server to cloud (optional)
4. **Then**: Set up automatic daily scraping

See **[REMOTE_DATABASE_SETUP.md](REMOTE_DATABASE_SETUP.md)** for advanced configuration and deployment.

---

## Summary

🎯 **5 minutes** to set up
💾 **3 GB free** storage (Neon) or 500 MB (Supabase)
🌐 **Multi-user** access ready
🔒 **Secure** SSL encrypted
💰 **Free forever** (for typical usage)
📱 **Accessible** from any platform

Your job database is now in the cloud! 🚀
