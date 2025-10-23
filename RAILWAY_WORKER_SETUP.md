# Railway Worker Setup Guide

Deploy the automatic job scraper as a background worker on Railway.

## Overview

This guide shows you how to deploy TWO services on Railway:
1. **Web Service** - Your API server (already running)
2. **Worker Service** - Background scraper that runs 24/7

Both services will share the same PostgreSQL database.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Railway Project                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────────┐      ┌──────────────────┐   │
│  │  Web Service     │      │  Worker Service  │   │
│  │  (job_server.py) │      │ (scheduled_      │   │
│  │                  │      │  scraper.py)     │   │
│  │  Port: 8001      │      │                  │   │
│  │  Public URL ✓    │      │  No public URL   │   │
│  └────────┬─────────┘      └────────┬─────────┘   │
│           │                         │             │
│           └─────────┬───────────────┘             │
│                     ▼                             │
│           ┌──────────────────┐                    │
│           │  PostgreSQL DB   │                    │
│           │  (Neon/Railway)  │                    │
│           └──────────────────┘                    │
└─────────────────────────────────────────────────────┘
```

---

## Step-by-Step Setup

### Step 1: Go to Your Railway Project

1. Open https://railway.app
2. Login with your GitHub account
3. Click on your existing project (the one with your API)

---

### Step 2: Add a New Service

1. In your Railway project dashboard, click **"+ New"**
2. Select **"GitHub Repo"**
3. Choose your repository: `mfish324/job-aggregation-api`
4. Railway will start deploying a second service

---

### Step 3: Configure the Worker Service

#### A. Change the Service Name

1. Click on the **new service** (not your existing web service)
2. Go to **Settings** tab
3. Under "Service Name", rename it to: `job-scraper-worker`

#### B. Set the Start Command

1. Still in **Settings** tab
2. Scroll to **"Deploy"** section
3. Find **"Start Command"**
4. Enter: `python scheduled_scraper.py`
5. Click **"Save"** or it auto-saves

#### C. Remove Public Networking (Optional but Recommended)

The worker doesn't need a public URL since it just runs in the background.

1. In **Settings** tab
2. Scroll to **"Networking"** section
3. Click **"Remove Public Domain"** (if there is one)

This saves resources and makes the service more secure.

---

### Step 4: Set Environment Variables

Both services need the same `DATABASE_URL` to share the database.

#### Get Your DATABASE_URL

1. Click on your **Web Service** (the original one)
2. Go to **"Variables"** tab
3. Copy the value of `DATABASE_URL`

It should look like:
```
postgresql://neondb_owner:password@ep-xxx-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require
```

#### Set Variables on Worker Service

1. Click on your **Worker Service** (job-scraper-worker)
2. Go to **"Variables"** tab
3. Click **"+ New Variable"**
4. Add:
   - **Key:** `DATABASE_URL`
   - **Value:** (paste the database URL from above)
5. Click **"Add"**

**Optional API Keys** (for better results):

Add these if you have them:
- `ADZUNA_APP_ID` - Adzuna API ID
- `ADZUNA_APP_KEY` - Adzuna API Key
- `GITHUB_TOKEN` - GitHub Personal Access Token
- `RAPIDAPI_KEY` - RapidAPI Key for Indeed

---

### Step 5: Verify Both Services Are Running

After a few minutes, check both services:

#### Web Service (API)
1. Click on **Web Service**
2. Go to **"Deployments"** tab
3. Should show: ✅ Success
4. Go to **"Logs"** tab
5. Should see: `Uvicorn running on http://0.0.0.0:8001`

#### Worker Service (Scraper)
1. Click on **Worker Service** (job-scraper-worker)
2. Go to **"Deployments"** tab
3. Should show: ✅ Success
4. Go to **"Logs"** tab
5. Should see:
   ```
   Starting Gen-Z Job Scraper Scheduler
   Database: job_board.db
   Running initial priority search...
   Searching remoteok for 'junior developer'
   ```

---

## What the Worker Does

The worker runs **automatically 24/7** with this schedule:

### Quick Searches (Every 6 Hours)
- Entry-level Tech
- Mid-level Tech
- Entry-level Data Science

Searches 3 keywords per profile.

### Full Searches (Daily at 3 AM)
- All 10 profiles
- 5 keywords per profile
- Entry/Mid level: Tech, Finance, Data, Marketing, Design, Sales

### Rate Limiting
- Respects API rate limits
- 5-second delay between searches
- Won't overwhelm job boards

---

## Monitoring the Worker

### Check Logs

1. Go to Railway dashboard
2. Click on **Worker Service**
3. Click **"Logs"** tab

**What to look for:**
```
✅ Good logs:
INFO - Searching remoteok for 'junior developer'
INFO - remoteok: Found 45 jobs, 12 new
INFO - Searching remotive for 'entry level developer'
INFO - remotive: Found 23 jobs, 8 new

❌ Error logs:
ERROR - Failed to scrape remoteok: Connection timeout
```

### Check Database Growth

1. Visit your API: `https://your-app.up.railway.app/stats`
2. Watch `total_jobs` increase over time
3. Check `recent_jobs_24h` to see daily additions

---

## Cost Estimate

Railway Free Tier:
- **$5 free credit/month**
- **500 hours free/month**

With 2 services:
- Web service: ~740 hours/month (always on)
- Worker service: ~740 hours/month (always on)
- **Total: ~1480 hours/month**

This **exceeds free tier**, so you'll need:

**Option A: Hobby Plan**
- $5/month per service = $10/month total
- Unlimited hours

**Option B: Reduce Worker Hours**
- Stop worker when not needed
- Only run during peak hours
- Use manual `trigger_scrape.py` instead

---

## Troubleshooting

### Worker Not Starting

**Check Logs for Errors:**
1. Railway → Worker Service → Logs
2. Look for Python errors

**Common Issues:**
- Missing `DATABASE_URL` environment variable
- Wrong start command (should be `python scheduled_scraper.py`)
- Python dependencies not installed (Railway should auto-install from requirements.txt)

**Fix:**
1. Verify environment variables are set
2. Check start command in Settings
3. Redeploy: Settings → Click "Redeploy"

---

### Worker Keeps Crashing

**Check if database connection is failing:**
1. Verify `DATABASE_URL` is correct
2. Make sure it's the **pooled connection string** (has `-pooler` in hostname)
3. Check that SSL is enabled (`?sslmode=require` at end)

**Fix:**
1. Update `DATABASE_URL` if needed
2. Make sure the recent database connection fixes are deployed

---

### No New Jobs Being Added

**Check if scraper is actually running:**
1. Railway → Worker Service → Logs
2. Should see search activity every 6 hours

**If no logs:**
- Worker might be sleeping/idle
- Check "Metrics" tab for CPU/RAM activity

**If seeing logs but no new jobs:**
- Scrapers might be hitting rate limits
- Job boards might be returning same jobs (duplicates)
- Check `/stats` endpoint: `recent_jobs_24h` field

---

### Both Services Using Same Database?

**Verify they're connected to the same database:**

1. Check Web Service variables: `DATABASE_URL`
2. Check Worker Service variables: `DATABASE_URL`
3. Both should have **identical** values

**Test:**
1. Trigger scrape manually: `python trigger_scrape.py --url https://your-web-url`
2. Check worker logs - should see import activity
3. Both services should see the same job count

---

## Managing Your Services

### Restart Worker

1. Railway → Worker Service
2. Click "⋮" (three dots)
3. Select "Restart"

### View Environment Variables

1. Railway → Service → Variables tab
2. Shows all variables for that service

### Stop Worker (Save Hours)

1. Railway → Worker Service
2. Settings → Scroll down
3. Click "Pause Service"

**Note:** Worker will stop running. Jobs won't auto-update.

### Resume Worker

1. Railway → Worker Service (shows as paused)
2. Click "Resume Service"

---

## Alternative: Scheduled Manual Scraping

If you don't want to run a 24/7 worker:

### Option 1: Local Cron Job
Run on your computer:
```bash
# Linux/Mac: Add to crontab
0 3 * * * cd /path/to/Job_APIs && python trigger_scrape.py --url https://your-railway-url

# Windows: Use Task Scheduler
```

### Option 2: External Cron Service
Use a service like:
- **cron-job.org** (free)
- **EasyCron** (free tier)
- **Render Cron Jobs** (free)

Configure to call:
```
POST https://your-railway-url/scrape
```

---

## Verification Checklist

After setup, verify everything works:

- [ ] Web service shows ✅ Success in deployments
- [ ] Worker service shows ✅ Success in deployments
- [ ] Worker logs show "Starting Gen-Z Job Scraper Scheduler"
- [ ] Worker logs show search activity
- [ ] Both services have same `DATABASE_URL`
- [ ] `/stats` endpoint shows increasing `recent_jobs_24h`
- [ ] No connection errors in logs

---

## Quick Reference

### Service URLs
- **Web Service:** `https://web-production-94ca.up.railway.app`
- **Worker Service:** No public URL (background only)

### Start Commands
- **Web Service:** `python job_server.py`
- **Worker Service:** `python scheduled_scraper.py`

### Required Environment Variables
- `DATABASE_URL` - PostgreSQL connection string (both services)

### Optional Environment Variables
- `ADZUNA_APP_ID` - Adzuna API
- `ADZUNA_APP_KEY` - Adzuna API
- `GITHUB_TOKEN` - GitHub API
- `RAPIDAPI_KEY` - RapidAPI

---

## Summary

After completing this setup:

✅ **Two Railway services running:**
   - Web API serving requests
   - Worker scraping jobs 24/7

✅ **Automatic job updates:**
   - Quick searches every 6 hours
   - Full searches daily at 3 AM
   - 10 Gen-Z targeted profiles

✅ **Shared database:**
   - Both services use same PostgreSQL DB
   - Jobs sync automatically
   - No manual intervention needed

Your job board will stay fresh automatically! 🎉

---

## Next Steps

1. **Deploy the worker** following steps above
2. **Monitor logs** for first 24 hours
3. **Check `/stats`** daily to see growth
4. **Adjust schedule** if needed (edit `scheduled_scraper.py`)

Need help? Check the Railway logs first - they'll tell you what's wrong!
