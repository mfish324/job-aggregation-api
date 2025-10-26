# Gen-Z Automated Job Scraper - Complete Guide

Your job aggregator now automatically searches for Gen-Z targeted jobs at maximum API-allowed rates!

## What It Does

Automatically searches for **entry-level and mid-level** jobs in categories that appeal to Gen-Z:

### Job Categories Covered

1. **Tech/Programming** (Entry & Mid-level)
   - Junior Developer, Software Engineer, Full Stack Developer
   - Python, JavaScript, React, Node.js developers
   - Frontend, Backend, DevOps positions

2. **Finance** (Entry & Mid-level)
   - Financial Analyst, Junior Accountant
   - Investment Analyst, Budget Analyst
   - Finance Associates

3. **Data Science & Analytics** (Entry & Mid-level)
   - Data Analyst, Data Scientist
   - Business Analyst, Analytics Engineer
   - Machine Learning Engineer

4. **Marketing** (Entry & Mid-level)
   - Marketing Coordinator, Social Media Manager
   - Content Marketing, Digital Marketing
   - SEO, Growth Marketing

5. **Design** (Entry-level)
   - UI/UX Designer, Product Designer
   - Graphic Designer, Web Designer

6. **Sales** (Entry-level)
   - Sales Representative, Account Executive
   - Business Development Representative (BDR/SDR)

## How It Works

### Rate Limiting (Respects API Limits)

Each source has configured rate limits to maximize searches without getting blocked:

| Source | Requests/Hour | Delay Between Requests |
|--------|---------------|------------------------|
| RemoteOK | 60 | 60 seconds |
| Remotive | 60 | 60 seconds |
| GitHub | 10 | 6 minutes |
| Indeed (RapidAPI) | 10 | 6 minutes |
| Authentic Jobs | 30 | 2 minutes |
| We Work Remotely | 30 | 2 minutes |

### Search Profiles

**10 targeted profiles** with multiple keywords each:

- `entry_tech`: 10 keywords (junior developer, entry level developer, etc.)
- `mid_tech`: 9 keywords (software engineer, python developer, etc.)
- `entry_finance`: 8 keywords (junior financial analyst, etc.)
- `mid_finance`: 6 keywords (financial analyst, accountant, etc.)
- `entry_data`: 6 keywords (junior data analyst, data analyst, etc.)
- `mid_data`: 5 keywords (data scientist, data engineer, etc.)
- `entry_marketing`: 7 keywords (marketing coordinator, etc.)
- `mid_marketing`: 7 keywords (marketing manager, growth marketing, etc.)
- `entry_design`: 6 keywords (junior designer, ui designer, etc.)
- `entry_sales`: 6 keywords (sales rep, account executive, etc.)

**Total**: 70+ targeted keyword searches!

---

## Usage Options

### Option 1: Automatic Scheduled Scraping (Recommended)

Run the scheduler as a background service that automatically searches on a schedule:

```bash
python scheduled_scraper.py
```

**Default Schedule:**
- **Every 6 hours**: Priority profiles (entry tech, mid tech, entry finance, entry data)
- **Every 12 hours**: All profiles with 2 keywords each
- **Daily at 3 AM**: Full comprehensive search with 5 keywords per profile

The scheduler will:
- ✅ Run continuously in the background
- ✅ Respect all rate limits
- ✅ Log all activity to `scraper.log`
- ✅ Automatically add new jobs to database

**To run as a background service (Linux/Mac):**
```bash
nohup python scheduled_scraper.py > scraper_output.log 2>&1 &
```

**To run as a background service (Windows):**
```bash
# Option 1: Start minimized
start /min python scheduled_scraper.py

# Option 2: Use Windows Task Scheduler (see below)
```

### Option 2: API Endpoints (Manual Triggers)

Control searches via the REST API (useful for integration with your other platforms):

#### Get Available Profiles
```bash
curl http://localhost:8001/genz/profiles
```

**Response:**
```json
{
  "profiles": ["entry_tech", "mid_tech", "entry_finance", ...],
  "total_profiles": 10,
  "profile_details": {...}
}
```

#### Run Priority Searches
```bash
curl -X POST http://localhost:8001/genz/search-priority
```

Searches: entry_tech, mid_tech, entry_finance, entry_data (5 keywords each)

#### Run Specific Profile
```bash
curl -X POST "http://localhost:8001/genz/search/entry_tech?max_keywords=5"
```

#### Run All Profiles
```bash
curl -X POST "http://localhost:8001/genz/search-all?max_keywords_per_profile=3"
```

**Note**: All searches run in the background and respect rate limits.

### Option 3: Python Integration

From your other job search platforms:

```python
import requests

# Trigger priority Gen-Z searches
response = requests.post("http://localhost:8001/genz/search-priority")
print(response.json())
# {"status": "started", "profiles": ["entry_tech", "mid_tech", ...]}

# Get available profiles
profiles = requests.get("http://localhost:8001/genz/profiles").json()
print(f"Total profiles: {profiles['total_profiles']}")

# Run specific search
response = requests.post(
    "http://localhost:8001/genz/search/entry_finance",
    params={"max_keywords": 3}
)
```

### Option 4: One-Time Manual Search

Run a single search session:

```python
from scheduled_scraper import GenZJobSearcher

searcher = GenZJobSearcher()

# Run priority profiles
stats = searcher.run_priority_profiles()
print(f"Found {stats['total_new_jobs']} new jobs")

# Or run specific profile
stats = searcher.run_search_profile('entry_tech', max_keywords=5)
print(f"Entry tech: {stats['new_jobs_added']} new jobs")
```

---

## Setting Up Windows Task Scheduler (Recommended for Windows)

To run the scraper automatically on Windows startup:

1. **Open Task Scheduler**
   - Press `Win + R`, type `taskschd.msc`, press Enter

2. **Create Basic Task**
   - Click "Create Basic Task"
   - Name: `Gen-Z Job Scraper`
   - Description: `Automatic job aggregation for Gen-Z targeted positions`

3. **Trigger**
   - Select "When the computer starts"

4. **Action**
   - Select "Start a program"
   - Program: `C:\Users\matto\projects\Job_APIs\jobs-venv\Scripts\python.exe`
   - Arguments: `scheduled_scraper.py`
   - Start in: `C:\Users\matto\projects\Job_APIs`

5. **Settings**
   - ✅ Check "Run whether user is logged on or not"
   - ✅ Check "Run with highest privileges"

---

## Monitoring

### Check Logs

```bash
# View live logs
tail -f scraper.log

# On Windows (PowerShell)
Get-Content scraper.log -Wait -Tail 50
```

### Check Statistics

```bash
curl http://localhost:8001/stats
```

**Response:**
```json
{
  "total_jobs": 2500,
  "remote_jobs": 2450,
  "with_salary": 1200,
  "by_source": {
    "remotive": 1800,
    "remoteok": 350,
    "authenticjobs": 50,
    "github": 2,
    "indeed": 298
  }
}
```

### View Database

```bash
python verify_database.py
```

---

## Expected Results

### With Default Schedule (6hr/12hr/24hr)

**Daily Job Volume** (estimated):
- Priority searches (4 profiles × 4 runs/day): ~80-200 new jobs/day
- All profiles (10 profiles × 2 runs/day): ~100-300 new jobs/day
- Full search (1× per day): ~200-500 new jobs/day

**Total**: ~400-1000 new jobs per day (varies by demand)

### Search Duration

Due to rate limiting:
- **Priority profiles** (4 profiles, 5 keywords each): ~2-3 hours
- **All profiles** (10 profiles, 3 keywords each): ~4-6 hours
- **Full search** (10 profiles, 5 keywords each): ~6-8 hours

---

## Customization

### Modify Search Profiles

Edit [scheduled_scraper.py](scheduled_scraper.py):

```python
SEARCH_PROFILES = {
    'entry_tech': {
        'keywords': [
            'junior developer',
            'your custom keyword here',
            # Add more keywords
        ],
        'categories': ['software-dev', 'tech'],
        'experience': 'entry'
    },
    # Add your own profile
    'custom_profile': {
        'keywords': ['keyword1', 'keyword2'],
        'categories': ['category'],
        'experience': 'entry'
    }
}
```

### Modify Schedule

Edit the `setup_schedule()` function in [scheduled_scraper.py](scheduled_scraper.py):

```python
# Every 4 hours instead of 6
schedule.every(4).hours.do(searcher.run_priority_profiles)

# Every 8 hours instead of 12
schedule.every(8).hours.do(
    lambda: searcher.run_all_profiles(max_keywords_per_profile=2)
)

# Daily at different time
schedule.every().day.at("06:00").do(
    lambda: searcher.run_all_profiles(max_keywords_per_profile=5)
)
```

### Adjust Rate Limits

**Only if you know the API allows higher rates:**

Edit `RATE_LIMITS` in [scheduled_scraper.py](scheduled_scraper.py):

```python
RATE_LIMITS = {
    'remoteok': {
        'requests_per_hour': 120,  # Increase from 60
        'delay_seconds': 30  # Decrease from 60
    }
}
```

⚠️ **Warning**: Setting rates too high may get your IP blocked!

---

## Troubleshooting

### "Rate limit exceeded" errors

**Cause**: API limits hit
**Solution**: Wait for rate limit reset (hourly/monthly depending on API)

### No new jobs found

**Cause**: Search terms too specific or already scraped
**Solution**:
- Add more keywords to profiles
- Check if jobs already in database (duplicates are skipped)

### Scheduler not running

**Cause**: Python process stopped
**Solution**:
- Check logs: `scraper.log`
- Restart: `python scheduled_scraper.py`
- Use Task Scheduler (Windows) or systemd (Linux) for auto-restart

### Indeed API errors

**Cause**: Monthly limit exceeded (100 requests/month on free tier)
**Solution**:
- Wait for monthly reset
- Upgrade to paid tier
- Disable Indeed searches temporarily

---

## Integration with Your Job Platforms

### From Django Job Board

```python
# In your Django views.py
import requests

def refresh_genz_jobs():
    """Trigger Gen-Z job refresh from aggregator"""
    response = requests.post("http://localhost:8001/genz/search-priority")
    return response.json()

def get_latest_jobs():
    """Get latest Gen-Z jobs from aggregator"""
    response = requests.get(
        "http://localhost:8001/jobs",
        params={"remote_only": True, "per_page": 50}
    )
    return response.json()
```

### From JavaScript Platform

```javascript
// Trigger Gen-Z search
fetch('http://localhost:8001/genz/search-priority', {
  method: 'POST'
})
.then(res => res.json())
.then(data => console.log('Search started:', data.status));

// Get latest jobs
fetch('http://localhost:8001/jobs?remote_only=true&per_page=20')
.then(res => res.json())
.then(data => {
  console.log(`Found ${data.total} jobs`);
  data.jobs.forEach(job => {
    console.log(`${job.title} at ${job.company}`);
  });
});
```

---

## Summary

✅ **10 Gen-Z targeted search profiles**
✅ **70+ keyword searches**
✅ **Automatic scheduling** (6hr/12hr/24hr)
✅ **Rate limiting** to prevent blocks
✅ **400-1000 new jobs per day** (estimated)
✅ **API endpoints** for manual control
✅ **Background processing** (non-blocking)
✅ **Comprehensive logging**
✅ **Multi-platform integration ready**

## Quick Start

```bash
# Start the automatic scheduler
python scheduled_scraper.py

# Or trigger via API
curl -X POST http://localhost:8001/genz/search-priority

# Check results
curl http://localhost:8001/stats
```

Your Gen-Z job aggregator is ready to run 24/7 at maximum API-allowed rates! 🚀
