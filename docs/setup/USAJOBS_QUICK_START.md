# USAJOBS Quick Start Guide

**Time to Complete**: 10 minutes
**Difficulty**: Easy
**Result**: +20,000 federal government jobs in your database

---

## Step 1: Get Your Free API Key (5 minutes)

1. Visit: **https://developer.usajobs.gov/APIRequest/Index**

2. Fill out the short form:
   - **Email**: your_email@example.com
   - **Organization**: LevelUp Careers
   - **Purpose**: Job aggregation platform for Gen-Z job seekers
   - ✅ Check "I agree to terms of service"

3. Click **Submit**

4. Check your email - API key arrives instantly

---

## Step 2: Add API Key to Environment (2 minutes)

Open `C:/Users/matto/projects/Job_APIs/.env` and add:

```bash
# USAJOBS Official API
USAJOBS_API_KEY=paste_your_key_here
USAJOBS_USER_AGENT=LevelUpCareers/1.0 (your_email@example.com)
```

**Important**: Replace `your_email@example.com` with your actual contact email.

Save the file.

---

## Step 3: Test the Scraper (2 minutes)

```bash
cd C:/Users/matto/projects/Job_APIs
python usajobs_scraper.py
```

**You should see**:
```
Testing USAJOBS Scraper...
================================================================================

[TEST 1] Searching for entry-level software developer jobs...
Found 5 jobs

Sample job:
  Title: SOFTWARE DEVELOPER
  Company: Department of Defense
  Location: Washington, DC
  Salary: $59,966 - $94,317
  ...

✅ USAJOBS scraper working! Total jobs found: 8
```

If you see ✅, you're good to go!

---

## Step 4: Start Job Server (1 minute)

```bash
python job_server.py
```

Server starts on http://localhost:8001

---

## Step 5: Trigger Initial Scrape (Optional)

Let the system scrape federal jobs automatically:

```bash
# Option A: Priority search (faster - 30 minutes)
curl -X POST "http://localhost:8001/genz/search-priority"

# Option B: Full search (comprehensive - 2-3 hours)
curl -X POST "http://localhost:8001/genz/search-all"
```

Or just let the automated scheduler do it (runs every 6 hours).

---

## Verify It's Working

```bash
# Check if USAJOBS is active
curl "http://localhost:8001/sources" | grep usajobs

# Check job statistics
curl "http://localhost:8001/stats"
```

**You should see**:
- `"usajobs"` listed as active source
- Job count growing in stats

---

## Troubleshooting

### "API key required" error?
- Make sure you added `USAJOBS_API_KEY=...` to `.env`
- Restart the server: `python job_server.py`

### "429 Too Many Requests" error?
- This means rate limit hit (10 requests/minute)
- Wait 1 minute and try again
- Our scraper respects limits automatically

### No jobs showing?
- Run manual test: `python usajobs_scraper.py`
- Check API key is correct
- Verify internet connection

---

## What Happens Next?

1. **Automated Searches** run every 6 hours for:
   - Entry-level tech jobs
   - Entry-level finance jobs
   - Entry-level data jobs
   - Mid-level positions

2. **Jobs appear** in LevelUp Careers automatically:
   - Search for "software engineer" → includes federal jobs
   - Search for "data analyst" → includes federal jobs
   - AI summaries work for federal agencies

3. **Database grows** to 10,000-15,000 jobs within 24-48 hours

---

## Need Help?

See full documentation: [USAJOBS_INTEGRATION.md](./USAJOBS_INTEGRATION.md)

---

**That's it!** You now have access to 20,000+ federal government jobs. 🎉
