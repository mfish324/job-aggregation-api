# Railway USAJOBS Setup Guide

**Time**: 10 minutes
**Status**: Code deployed, API key needed

---

## Current Status

✅ **USAJOBS integration code pushed to GitHub**
✅ **Railway will auto-deploy from main branch**
⏳ **Waiting for USAJOBS API key in Railway environment**

---

## Step 1: Get USAJOBS API Key (5 minutes)

If you haven't already:

1. Visit: **https://developer.usajobs.gov/APIRequest/Index**
2. Fill out the form:
   - Email: your_email@example.com
   - Organization: LevelUp Careers
   - Purpose: Job aggregation for Gen-Z career platform
   - ✅ Agree to terms
3. Submit and check email (key arrives instantly)

---

## Step 2: Add API Key to Railway (3 minutes)

### Option A: Railway Web Dashboard (Recommended)

1. **Go to Railway Dashboard**: https://railway.app/dashboard

2. **Select your Job_APIs project**

3. **Click on your service** (the one running job_server.py)

4. **Go to "Variables" tab**

5. **Click "New Variable"**

6. **Add these two variables**:

   ```
   Variable 1:
   Key: USAJOBS_API_KEY
   Value: paste_your_api_key_here

   Variable 2:
   Key: USAJOBS_USER_AGENT
   Value: LevelUpCareers/1.0 (your_email@example.com)
   ```

7. **Click "Save"** - Railway will automatically restart your service

### Option B: Railway CLI

```bash
# Install Railway CLI (if not already)
npm install -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Add environment variables
railway variables set USAJOBS_API_KEY=your_key_here
railway variables set USAJOBS_USER_AGENT="LevelUpCareers/1.0 (your_email@example.com)"

# Service restarts automatically
```

---

## Step 3: Verify Deployment (2 minutes)

### Check Railway Logs

1. Go to Railway dashboard
2. Click on your service
3. Go to "Deployments" tab
4. Click on the latest deployment
5. Check logs for:
   ```
   ✅ USAJOBS scraper enabled (20,000+ federal jobs)
   ```

### Test the API

Once deployed, test with your Railway URL:

```bash
# Check if USAJOBS is listed as active source
curl "https://your-railway-app.railway.app/sources"

# Should see:
{
  "job_boards": [
    ...
    {
      "id": "usajobs",
      "name": "USAJOBS (Federal Government)",
      "type": "api",
      "requires_key": true,
      "active": true,  ← Should be true!
      "description": "Official federal government jobs..."
    }
  ]
}
```

---

## Step 4: Trigger Initial Scrape

Once API key is added and service restarted:

```bash
# Replace with your Railway URL
RAILWAY_URL="https://your-railway-app.railway.app"

# Trigger priority Gen-Z searches (includes USAJOBS)
curl -X POST "$RAILWAY_URL/genz/search-priority"

# Or full comprehensive search
curl -X POST "$RAILWAY_URL/genz/search-all"
```

This will:
- Search USAJOBS for entry_tech keywords
- Search USAJOBS for entry_finance keywords
- Search USAJOBS for entry_data keywords
- Add federal jobs to database
- Jobs appear in LevelUp Careers automatically

---

## Step 5: Monitor Results

### Check Statistics

```bash
curl "https://your-railway-app.railway.app/stats"
```

**Expected response** (after scraping):
```json
{
  "total_jobs": 5000,
  "by_source": {
    "usajobs": 500,      ← Federal jobs!
    "remoteok": 1200,
    "google_careers": 234,
    ...
  },
  "recent_jobs_24h": 120
}
```

### Railway Logs

Watch for successful USAJOBS searches:
```
INFO:usajobs_scraper: Searching USAJOBS: 'IT Specialist' (salary: $35,000-$95,000)
INFO:usajobs_scraper: Found 10 USAJOBS results for 'IT Specialist'
INFO:usajobs_scraper: After salary filtering: 5 jobs (filtered out 1 senior positions)
```

---

## Troubleshooting

### Issue: "active": false in /sources

**Cause**: API key not set in Railway environment

**Solution**:
1. Double-check Railway Variables tab
2. Make sure `USAJOBS_API_KEY` is set
3. Restart service manually if needed

### Issue: No federal jobs in database

**Possible causes**:
1. API key not set → Check Railway variables
2. Scraping not triggered → Trigger with `/genz/search-priority`
3. API key invalid → Check key from USAJOBS email
4. Rate limiting → Wait 1 minute and try again

**Debug**:
```bash
# Check Railway logs for errors
# Look for lines with "usajobs" or "USAJOBS"

# Test API key directly
curl -X POST "https://your-railway-app.railway.app/scrape" \
  -H "Content-Type: application/json" \
  -d '{"keywords": "IT specialist", "sources": ["usajobs"], "max_pages": 1}'
```

### Issue: Railway deployment failed

**Check**:
1. Railway build logs for Python errors
2. Make sure `requirements.txt` includes `python-dotenv` and `requests`
3. Check Railway dashboard for service status

---

## What Happens Next (Automatic)

Once the API key is added, the scheduled scraper will:

**Every 6 hours**:
1. Search USAJOBS for:
   - entry_tech: "software developer", "IT specialist", "data analyst"
   - entry_finance: "financial analyst", "accountant", "budget analyst"
   - entry_data: "data analyst", "business analyst"
   - mid_tech: "software engineer", "cybersecurity"
   - mid_finance: "senior analyst", "management analyst"

2. Filter for entry-level salaries ($35K-$95K)

3. Add new jobs to database

4. Jobs automatically sync to LevelUp Careers

**Expected growth**:
- Week 1: 500-1,000 federal jobs
- Month 1: 3,000-5,000 federal jobs
- Month 3: 8,000-10,000 federal jobs

---

## Summary Checklist

- [ ] USAJOBS API key obtained from developer.usajobs.gov
- [ ] API key added to Railway Variables (`USAJOBS_API_KEY`)
- [ ] User agent added to Railway Variables (`USAJOBS_USER_AGENT`)
- [ ] Railway service restarted (automatic)
- [ ] Checked `/sources` endpoint - usajobs shows `"active": true`
- [ ] Triggered initial scrape with `/genz/search-priority`
- [ ] Verified federal jobs in `/stats` endpoint
- [ ] Confirmed jobs appearing in LevelUp Careers frontend

---

## Support

**Documentation**:
- Full guide: [USAJOBS_INTEGRATION.md](./USAJOBS_INTEGRATION.md)
- Quick start: [USAJOBS_QUICK_START.md](./USAJOBS_QUICK_START.md)

**Railway**:
- Dashboard: https://railway.app/dashboard
- Docs: https://docs.railway.app/

**USAJOBS API**:
- Documentation: https://developer.usajobs.gov/
- API request: https://developer.usajobs.gov/APIRequest/Index

---

**Status**: Ready for Railway configuration
**Next Action**: Add USAJOBS_API_KEY to Railway environment variables
