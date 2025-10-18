# Setup Indeed via RapidAPI

## Quick Start (5 minutes)

### Step 1: Sign Up for RapidAPI

1. Go to https://rapidapi.com/
2. Click "Sign Up" (free account)
3. Verify your email

### Step 2: Subscribe to an Indeed API

Choose one of these Indeed APIs (all have free tiers):

#### Option A: Indeed Jobs API (Recommended)
- **Link**: https://rapidapi.com/vuesdata/api/indeed-jobs-api
- **Free Tier**: 25-100 requests/month
- **Host**: `indeed-jobs-api.p.rapidapi.com`

#### Option B: Indeed Jobs Scraper API
- **Link**: https://rapidapi.com/bebity-bebity-default/api/indeed-jobs-scraper-api
- **Free Tier**: 25 requests/month
- **Host**: `indeed-jobs-scraper-api.p.rapidapi.com`

#### Option C: Browse More
- Search "Indeed" on https://rapidapi.com/search/indeed
- Look for APIs with free tiers

**Steps to Subscribe:**
1. Click on your chosen API
2. Click "Subscribe to Test"
3. Choose "Basic" (Free) plan
4. Click "Subscribe"

### Step 3: Get Your API Key

1. After subscribing, you'll see your API key
2. Or go to: https://rapidapi.com/developer/security
3. Copy your "X-RapidAPI-Key"

### Step 4: Add to Your .env File

```bash
# Open .env file (or create it)
nano .env

# Add these lines:
RAPIDAPI_KEY=your_key_here
RAPIDAPI_INDEED_HOST=indeed-jobs-api.p.rapidapi.com
```

Replace `your_key_here` with your actual API key.

### Step 5: Test It

```bash
python indeed_rapidapi_scraper.py
```

If setup correctly, you'll see:
```
Found X jobs
1. Python Developer at TechCorp
   Location: Remote
   URL: https://...
```

---

## Integration with Aggregator

### Option 1: Quick Integration (Use Standalone)

```python
from indeed_rapidapi_scraper import IndeedRapidAPIScraper
import os
from dotenv import load_dotenv

load_dotenv()

# Create scraper
api_key = os.getenv('RAPIDAPI_KEY')
api_host = os.getenv('RAPIDAPI_INDEED_HOST')
scraper = IndeedRapidAPIScraper(api_key, api_host)

# Scrape jobs
jobs = scraper.scrape(keywords="python", location="Remote", max_pages=2)
print(f"Found {len(jobs)} jobs")
```

### Option 2: Add to Main Aggregator

**Add to [aggregator.py](aggregator.py):**

```python
# At top of file
from indeed_rapidapi_scraper import IndeedRapidAPIScraper

# In __init__ method, replace the current indeed scraper:
rapidapi_key = os.getenv('RAPIDAPI_KEY')
rapidapi_host = os.getenv('RAPIDAPI_INDEED_HOST', 'indeed-jobs-api.p.rapidapi.com')

if rapidapi_key:
    self.scrapers['indeed'] = IndeedRapidAPIScraper(rapidapi_key, rapidapi_host)
else:
    print("Indeed RapidAPI: No API key. Add RAPIDAPI_KEY to .env")
```

Then run:
```bash
python main.py --sources indeed --keywords "python developer" --max-pages 2
```

---

## Pricing & Limits

### Free Tier (Basic Plan)

Most Indeed APIs offer:
- **25-100 requests per month**
- **No credit card required**
- **1000 requests per hour** limit
- ~15 jobs per request

**That's 375-1,500 jobs/month FREE!**

### Paid Plans

If you need more:

| Plan | Cost | Requests/Month | Use Case |
|------|------|----------------|----------|
| **Basic** | $0 | 25-100 | Testing, hobby projects |
| **Pro** | ~$10-25 | 1,000-5,000 | Small businesses |
| **Ultra** | ~$50-100 | 10,000+ | Medium businesses |
| **Mega** | ~$150+ | 50,000+ | Large scale |

*Exact pricing varies by provider*

---

## API Comparison

### Indeed Jobs API (vuesdata)
```
Endpoint: https://indeed-jobs-api.p.rapidapi.com/
Parameters:
  - keyword: Job search keywords
  - location: Job location
  - offset: Pagination offset
Response: ~15 jobs per request
```

**Example Request:**
```bash
curl --request GET \
  --url 'https://indeed-jobs-api.p.rapidapi.com/?keyword=python&location=Remote&offset=0' \
  --header 'X-RapidAPI-Host: indeed-jobs-api.p.rapidapi.com' \
  --header 'X-RapidAPI-Key: YOUR_KEY'
```

**Response Format:**
```json
[
  {
    "title": "Python Developer",
    "company": "TechCorp",
    "location": "Remote",
    "description": "...",
    "url": "https://indeed.com/...",
    "salary": "$100k-$150k"
  }
]
```

---

## Troubleshooting

### Error: "Invalid API Key"
```
✗ Check your API key in .env
✗ Make sure you've subscribed to the API
✓ Copy key from https://rapidapi.com/developer/security
```

### Error: "403 Forbidden"
```
✗ API key is wrong
✗ You haven't subscribed to the API
✓ Go to API page and click "Subscribe to Test"
```

### Error: "429 Rate Limit Exceeded"
```
✗ You've exceeded free tier limits
✓ Wait until next month
✓ Or upgrade to paid plan
```

### Error: "No results found"
```
✗ API might be temporarily down
✗ Your keywords might be too specific
✓ Try broader keywords like "developer"
✓ Try different location like "United States"
```

### No Error but 0 Jobs
```
✗ API response format might have changed
✓ Check API documentation on RapidAPI
✓ Update field mappings in scraper
```

---

## Testing Your Setup

### Test 1: Check API Key

```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(f'API Key: {os.getenv(\"RAPIDAPI_KEY\")[:10]}...' if os.getenv('RAPIDAPI_KEY') else 'No API Key')"
```

### Test 2: Run Scraper

```bash
python indeed_rapidapi_scraper.py
```

### Test 3: Full Integration

```bash
python main.py --sources indeed --keywords "python" --location "Remote" --max-pages 1
```

---

## Daily Usage

### Recommended Strategy

With free tier (25-100 requests/month):

```bash
# Daily scrape (2 requests per day = ~60/month)
python main.py --sources indeed --keywords "developer" --max-pages 2

# Weekly deep scrape (10 requests once per week = ~40/month)
python main.py --sources indeed --keywords "engineer" --max-pages 10
```

This gives you ~450-900 Indeed jobs per month on the free tier!

---

## Alternative: Combine with Other Sources

You already have 1,710 jobs from free sources. Indeed adds more:

```bash
# Combine all sources
python main.py --sources remoteok remotive indeed authenticjobs --max-pages 3
```

**Result:**
- RemoteOK: ~300 jobs
- Remotive: 1,600+ jobs
- Indeed (RapidAPI): 30-45 jobs (with free tier)
- Authentic Jobs: ~10 jobs

**Total: ~2,000 jobs!**

---

## Next Steps

1. ✅ Sign up for RapidAPI
2. ✅ Subscribe to Indeed API (free plan)
3. ✅ Add API key to .env
4. ✅ Test: `python indeed_rapidapi_scraper.py`
5. ✅ Integrate with main aggregator
6. ✅ Run full scrape

---

## Support

**RapidAPI Issues:**
- Help: https://rapidapi.com/support
- Docs: https://docs.rapidapi.com/

**API Provider Issues:**
- Check API's discussion tab on RapidAPI
- Contact API provider through RapidAPI

**This Integration:**
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review [indeed_rapidapi_scraper.py](indeed_rapidapi_scraper.py)

---

## Summary

✅ **Free tier available** (25-100 requests/month)
✅ **No credit card required**
✅ **~375-1,500 Indeed jobs/month free**
✅ **Easy 5-minute setup**
✅ **Legal and compliant**

Get started now: https://rapidapi.com/ 🚀
