# Gen-Z Job Scraper - Quick Start

## What You Have Now

✅ **Automatic Gen-Z job searches** for entry & mid-level positions
✅ **10 targeted profiles**: Tech, Finance, Data, Marketing, Design, Sales
✅ **70+ keyword searches** optimized for Gen-Z
✅ **Rate limiting** to maximize searches without getting blocked
✅ **REST API endpoints** for integration with your platforms

---

## 3 Ways to Use It

### 1. Automatic 24/7 Scraping (Recommended)

Start the scheduler to run searches automatically:

```bash
python scheduled_scraper.py
```

**Schedule:**
- Every 6 hours: Priority searches (entry tech, mid tech, entry finance, entry data)
- Every 12 hours: All profiles (limited keywords)
- Daily at 3 AM: Full comprehensive search

**Expected**: 400-1000 new Gen-Z jobs per day

**Logs**: Check `scraper.log` for activity

---

### 2. API Triggers (On-Demand)

Trigger searches from your other platforms via API:

```bash
# See available profiles
curl http://localhost:8001/genz/profiles

# Run priority searches (entry tech, finance, data)
curl -X POST http://localhost:8001/genz/search-priority

# Run specific profile (entry-level tech)
curl -X POST "http://localhost:8001/genz/search/entry_tech?max_keywords=5"

# Run all profiles
curl -X POST "http://localhost:8001/genz/search-all?max_keywords_per_profile=3"
```

All searches run in background and respect rate limits.

---

### 3. Python Integration

From your Django or other Python platforms:

```python
import requests

# Trigger Gen-Z searches
response = requests.post("http://localhost:8001/genz/search-priority")
print(response.json())
# {"status": "started", "profiles": ["entry_tech", ...]}

# Get latest jobs
jobs = requests.get("http://localhost:8001/jobs?per_page=50").json()
print(f"Found {jobs['total']} jobs")
for job in jobs['jobs']:
    print(f"{job['title']} at {job['company']} - {job['location']}")
```

---

## Gen-Z Job Categories

### 10 Targeted Profiles

1. **entry_tech** - Junior developers, entry-level engineers (10 keywords)
2. **mid_tech** - Software engineers, full stack developers (9 keywords)
3. **entry_finance** - Junior analysts, accounting associates (8 keywords)
4. **mid_finance** - Financial analysts, accountants (6 keywords)
5. **entry_data** - Data analysts, business analysts (6 keywords)
6. **mid_data** - Data scientists, ML engineers (5 keywords)
7. **entry_marketing** - Marketing coordinators, social media (7 keywords)
8. **mid_marketing** - Marketing managers, growth marketing (7 keywords)
9. **entry_design** - UI/UX designers, graphic designers (6 keywords)
10. **entry_sales** - Sales reps, account executives (6 keywords)

**Total: 70+ targeted keyword searches**

---

## API Endpoints

All available at `http://localhost:8001`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/genz/profiles` | GET | List all search profiles |
| `/genz/search-priority` | POST | Run priority searches |
| `/genz/search/{profile}` | POST | Run specific profile |
| `/genz/search-all` | POST | Run all profiles |
| `/jobs` | GET | Get job listings |
| `/jobs/{id}` | GET | Get job details |
| `/stats` | GET | Database statistics |

**Interactive docs**: http://localhost:8001/docs

---

## Quick Commands

```bash
# Start automatic scraper
python scheduled_scraper.py

# Check stats
curl http://localhost:8001/stats

# View logs
tail -f scraper.log

# Test priority search
curl -X POST http://localhost:8001/genz/search-priority

# Get latest jobs
curl "http://localhost:8001/jobs?per_page=10" | python -m json.tool
```

---

## Expected Results

- **Priority search**: ~50-100 new jobs (2-3 hours due to rate limits)
- **All profiles search**: ~100-300 new jobs (4-6 hours)
- **Daily total**: ~400-1000 new Gen-Z jobs

---

## Rate Limits (Maximum API-Allowed)

| Source | Delay | Requests/Hour |
|--------|-------|---------------|
| RemoteOK | 60s | 60 |
| Remotive | 60s | 60 |
| GitHub | 6min | 10 |
| Indeed | 6min | 10 |

These are **conservative limits** to prevent blocking. Searches automatically respect these delays.

---

## Next Steps

1. **Start the scheduler**: `python scheduled_scraper.py`
2. **Check the API docs**: http://localhost:8001/docs
3. **Monitor logs**: `tail -f scraper.log`
4. **Integrate with your platforms**: See [GENZ_AUTO_SCRAPER_GUIDE.md](GENZ_AUTO_SCRAPER_GUIDE.md)

For detailed documentation, see **[GENZ_AUTO_SCRAPER_GUIDE.md](GENZ_AUTO_SCRAPER_GUIDE.md)**
