# Railway Scraper Not Running - Fix Guide

**Problem**: Job count always shows same number (1,710 or 2,023), no new jobs being added

**Root Cause**: Automated scraper worker is not running on Railway

**Status**: Railway is only running the FastAPI web server (`job_server.py`), not the scheduled scraper

---

## Current Situation

✅ **Web API**: Running (http://your-app.railway.app)
❌ **Automated Scraper**: NOT running
❌ **USAJOBS**: NOT scraping (API key may not be set)

**Evidence**:
- Last job added: October 24, 2025 (>24 hours ago)
- Jobs in last 24h: 0
- Missing sources: USAJOBS, Apple, Microsoft, Meta, Tesla
- Only 2,023 jobs (should be 10,000+)

---

## Solution Options

### Option A: Add Railway Cron Job (Recommended)

Railway doesn't have built-in cron, but you can use GitHub Actions to trigger scraping.

**1. Create GitHub Action Workflow**

Create `.github/workflows/scrape-jobs.yml`:

```yaml
name: Scrape Jobs
on:
  schedule:
    # Run every 6 hours
    - cron: '0 */6 * * *'
  workflow_dispatch:  # Allow manual trigger

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Railway Scrape
        run: |
          curl -X POST "${{ secrets.RAILWAY_APP_URL }}/genz/search-priority" \
            -H "Content-Type: application/json"

      - name: Wait and check stats
        run: |
          sleep 60
          curl "${{ secrets.RAILWAY_APP_URL }}/stats"
```

**2. Add Secret to GitHub**

1. Go to GitHub repo → Settings → Secrets and variables → Actions
2. Add secret: `RAILWAY_APP_URL` = `https://your-app.railway.app`

**3. Test**

- Go to Actions tab
- Click "Scrape Jobs" workflow
- Click "Run workflow" to test

**Benefits**:
- ✅ Free (GitHub Actions)
- ✅ Reliable scheduling
- ✅ Easy to monitor
- ✅ No Railway changes needed

---

### Option B: Railway Worker Service

Add a separate worker service that runs the scheduled scraper continuously.

**1. Create Worker Script**

Create `worker.py`:

```python
#!/usr/bin/env python3
"""
Background worker for Railway - runs scheduled scraping
"""
import time
import schedule
import logging
from scheduled_scraper import GenZJobSearcher
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_priority_scrape():
    """Run priority Gen-Z profiles"""
    try:
        logger.info("Starting priority scrape...")
        searcher = GenZJobSearcher(
            database_url=os.getenv('DATABASE_URL'),
            us_only=True
        )

        # Run priority profiles
        profiles = ['entry_tech', 'entry_finance', 'entry_data']
        for profile in profiles:
            logger.info(f"Scraping {profile}...")
            searcher.run_search_profile(profile, max_keywords=3)

        logger.info("Priority scrape completed!")
    except Exception as e:
        logger.error(f"Scrape error: {e}")

# Schedule scraping every 6 hours
schedule.every(6).hours.do(run_priority_scrape)

# Run immediately on startup
run_priority_scrape()

# Keep running
logger.info("Worker started. Scraping every 6 hours...")
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
```

**2. Add schedule dependency**

Update `requirements.txt`:
```
schedule==1.2.0
```

**3. Create Railway Worker Service**

In Railway dashboard:
1. Click "+ New" → "Empty Service"
2. Connect to same GitHub repo
3. Set Start Command: `python worker.py`
4. Add same environment variables (DATABASE_URL, USAJOBS_API_KEY, etc.)
5. Deploy

**Benefits**:
- ✅ Runs continuously on Railway
- ✅ More control over scheduling
- ✅ Can see worker logs separately

**Drawbacks**:
- ❌ Uses Railway resources (may increase cost)
- ❌ Need to maintain worker separately

---

### Option C: Manual Trigger via Cron Service

Use a free cron service to trigger Railway API every 6 hours.

**Services**:
- **cron-job.org** (free, 60 requests/day)
- **EasyCron** (free tier available)
- **UptimeRobot** (free, monitors + triggers)

**Setup**:
1. Go to cron-job.org
2. Create account
3. Add new cron job:
   - URL: `https://your-app.railway.app/genz/search-priority`
   - Method: POST
   - Schedule: Every 6 hours
   - Content-Type: application/json

**Benefits**:
- ✅ Free
- ✅ Simple setup
- ✅ No code changes

**Drawbacks**:
- ❌ External dependency
- ❌ Less control
- ❌ May hit rate limits

---

## Quick Fix: Manual Trigger (Right Now)

While you set up automation, manually trigger scraping:

```bash
# Replace with your Railway URL
RAILWAY_URL="https://your-app.railway.app"

# Trigger priority scrape
curl -X POST "$RAILWAY_URL/genz/search-priority"

# Wait a few minutes, then check stats
sleep 180
curl "$RAILWAY_URL/stats"
```

This will:
- Scrape entry_tech, entry_finance, entry_data profiles
- Add 500-1,000 new jobs
- Include USAJOBS (if API key is set)

---

## Fix USAJOBS Not Scraping

Even with automated scraping, USAJOBS won't work without the API key.

**Check if USAJOBS is active**:
```bash
curl "https://your-app.railway.app/sources" | grep usajobs
```

Should show:
```json
{
  "id": "usajobs",
  "active": true,  ← Should be true!
  ...
}
```

If `active: false`:

1. **Add API Key to Railway**:
   - Railway Dashboard → Your Service → Variables
   - Add: `USAJOBS_API_KEY` = your_key
   - Add: `USAJOBS_USER_AGENT` = LevelUpCareers/1.0 (email)

2. **Restart Service**:
   - Railway → Deployments → "Restart"

3. **Verify**:
   ```bash
   curl "https://your-app.railway.app/sources" | grep usajobs
   # Should show active: true
   ```

4. **Trigger Manual Scrape**:
   ```bash
   curl -X POST "https://your-app.railway.app/genz/search-priority"
   ```

---

## Recommended Setup

**For Production** (recommended):

1. **Now**: Add USAJOBS API key to Railway (5 min)
2. **Now**: Manual trigger scrape to populate jobs (5 min)
3. **Today**: Set up GitHub Actions workflow (15 min)
4. **Optional**: Add UptimeRobot as backup (5 min)

**Steps**:

### 1. Add USAJOBS API Key
```
Railway Dashboard → Variables → Add:
- USAJOBS_API_KEY=your_key
- USAJOBS_USER_AGENT=LevelUpCareers/1.0 (email)
→ Save (auto-restarts)
```

### 2. Manual Trigger
```bash
curl -X POST "https://your-app.railway.app/genz/search-priority"
```

### 3. Create GitHub Action
Create `.github/workflows/scrape-jobs.yml` (see Option A above)

### 4. Add GitHub Secret
Add `RAILWAY_APP_URL` secret to GitHub

### 5. Test
GitHub → Actions → Scrape Jobs → Run workflow

---

## Expected Results After Fix

**Immediate** (after manual trigger):
- Jobs increase from 2,023 → 3,000+
- Latest job timestamp updates
- USAJOBS jobs appear (if API key set)

**After 6 hours** (automated):
- Another 500-1,000 jobs added
- Stats show jobs from last 24 hours

**After 1 week**:
- 10,000-15,000 total jobs
- All sources active (USAJOBS, FAANG, remote boards)
- Fresh jobs every 6 hours

---

## Monitoring

### Check Railway Logs
Railway Dashboard → Service → Logs

**Look for**:
```
INFO: Searching USAJOBS: 'software engineer'
INFO: Found 50 USAJOBS results
INFO: After salary filtering: 15 jobs
```

### Check Job Stats
```bash
curl "https://your-app.railway.app/stats"
```

**Expected**:
```json
{
  "total_jobs": 10000,
  "by_source": {
    "usajobs": 3000,
    "remotive": 2000,
    "remoteok": 1500,
    "google_careers": 500,
    ...
  },
  "recent_jobs_24h": 500
}
```

### Check Sources Status
```bash
curl "https://your-app.railway.app/sources"
```

**All should show** `"active": true`

---

## Troubleshooting

### "Still showing 2,023 jobs after trigger"

1. Check Railway logs for errors
2. Verify API responded: `curl -X POST https://your-app.railway.app/genz/search-priority`
3. Wait 5-10 minutes for scraping to complete
4. Check stats again

### "USAJOBS still inactive"

1. Verify API key is set in Railway variables
2. Restart Railway service manually
3. Check logs for: `✅ USAJOBS scraper enabled`

### "GitHub Action not running"

1. Check Actions tab for errors
2. Verify `RAILWAY_APP_URL` secret is set
3. Test with "Run workflow" button
4. Check cron syntax is correct

---

## Summary

**Problem**: Scraper not running automatically
**Solution**: Use GitHub Actions (free, reliable)
**Time**: 15 minutes setup
**Result**: 10,000+ fresh jobs, updated every 6 hours

**Quick Actions**:
1. ✅ Add USAJOBS API key to Railway
2. ✅ Trigger manual scrape now
3. ✅ Set up GitHub Actions for automation
4. ✅ Monitor results in 6 hours

---

**Created**: October 25, 2025
**Last Updated**: October 25, 2025
