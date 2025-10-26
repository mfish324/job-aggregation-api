# US-Only Job Filtering

Your job aggregator now automatically filters for **US-based jobs only**!

## What It Does

The aggregator now:
- ✅ **Filters out international jobs** (UK, Canada, Europe, Asia, etc.)
- ✅ **Keeps US-based jobs** (all 50 states + DC, Puerto Rico)
- ✅ **Allows remote jobs** (assumes US remote unless specified otherwise)
- ✅ **Smart detection** using states, cities, and keywords

## How It Works

### Location Detection

The filter checks for:

**US Indicators (KEEP):**
- US states: California, TX, New York, etc.
- US cities: San Francisco, NYC, Austin, etc.
- Keywords: USA, US, United States, Remote (US)
- State abbreviations: CA, NY, TX, etc.

**Non-US Indicators (FILTER OUT):**
- Countries: UK, Canada, Germany, France, India, etc.
- Cities: London, Toronto, Berlin, Sydney, etc.
- Keywords: Europe, Worldwide, Global, International

### Examples

| Location | Result | Reason |
|----------|--------|--------|
| New York, NY | ✅ Keep | US state |
| Remote, USA | ✅ Keep | US indicator |
| San Francisco | ✅ Keep | US city |
| Remote | ✅ Keep | Assumes US |
| London, UK | ❌ Filter | UK location |
| Toronto, Canada | ❌ Filter | Canada |
| Worldwide | ❌ Filter | International |
| Berlin | ❌ Filter | German city |

## Current Status

**Default Setting**: US-only filtering is **ENABLED** by default

All new jobs scraped will automatically be US-only.

## Configuration

### Keep US-Only (Default)
No changes needed! This is the default.

### Disable Filtering (Allow All Locations)

If you want jobs from all countries:

**In aggregator.py:**
```python
aggregator = JobAggregator(us_only=False)
```

**In scheduled_scraper.py:**
```python
searcher = GenZJobSearcher(us_only=False)
```

**In main.py:** (for CLI)
Add command line argument to disable filtering.

## Testing

Test the filter:
```bash
python location_filter.py
```

You'll see:
```
[OK] New York, NY                   -> True
[OK] London, UK                     -> False
[OK] Remote                         -> True
[OK] Toronto, Canada                -> False
```

## Statistics

Check how many jobs are being filtered:

```bash
# Run a test scrape
python -c "
from aggregator import JobAggregator
agg = JobAggregator(us_only=True)
stats = agg.scrape_all(sources=['remoteok'], max_pages=1)
print(stats)
"
```

You'll see output like:
```
Scraping remoteok... [OK] (45 US jobs, 12 new, 33 duplicates, 15 non-US filtered)
```

## Current Database

Your existing 1,710 jobs in the database may include some international jobs. Future scrapes will be US-only.

### Clean Existing Database (Optional)

To remove non-US jobs from your current database:

```python
from location_filter import is_us_location
from job_board_integration import JobBoardDatabase

db = JobBoardDatabase()
jobs = db.session.query(JobListing).all()

removed = 0
for job in jobs:
    if not is_us_location(job.location):
        db.session.delete(job)
        removed += 1

db.session.commit()
print(f"Removed {removed} non-US jobs")
```

## API Integration

The API endpoints automatically use US filtering:

```bash
# All jobs returned will be US-based
curl "http://localhost:8001/jobs?per_page=10"
```

## Future Scraping

All future scrapes will be US-only:

```bash
# Priority Gen-Z search (US only)
curl -X POST http://localhost:8001/genz/search-priority

# Scheduled scraper (US only)
python scheduled_scraper.py
```

## Summary

✅ **US-only filtering enabled** by default
✅ **Smart location detection** (50+ indicators)
✅ **Filters out 20+ countries**
✅ **Remote jobs allowed** (assumes US)
✅ **Automatic** - no configuration needed
✅ **Can be disabled** if you want international jobs

Your job aggregator now focuses on **US-based opportunities for Gen-Z**! 🇺🇸
