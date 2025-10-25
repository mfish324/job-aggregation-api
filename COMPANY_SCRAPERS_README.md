# Major Tech Company Scrapers

Your job aggregator now scrapes jobs **directly from major tech companies**!

## Supported Companies

### ✅ Fully Working

**Google** - Official XML Feed
- Source: `https://www.google.com/about/careers/applications/jobs/feed.xml`
- Jobs per scrape: 50+
- Includes: Software Engineer, Product Manager, all teams
- Data: Title, location, description, job type, remote status

### 🔨 Implemented (Pending Testing)

**Amazon** - Jobs API
- Source: `https://www.amazon.jobs/en/search.json`
- Includes: Amazon, AWS, Whole Foods, all subsidiaries
- Location filtering supported

**Apple** - Careers API
- Source: `https://jobs.apple.com/api/role/search`
- Includes: All Apple positions
- Team information included

**Microsoft** - Careers Search API
- Source: `https://gcsservices.careers.microsoft.com/search/api/v1/search`
- Includes: Microsoft, Azure, LinkedIn positions
- Full-text search supported

**Meta** - Careers Page Scraper
- Source: `https://www.metacareers.com/jobs`
- Includes: Facebook, Instagram, WhatsApp, Reality Labs
- Note: May need adjustments as page structure changes

**Tesla** - Careers API
- Source: `https://www.tesla.com/cua-api/apps`
- Includes: Tesla, SpaceX opportunities
- Location-based filtering

## How to Use

### Scrape All Major Companies

```bash
python trigger_scrape.py --url https://web-production-94ca.up.railway.app --sources google amazon apple microsoft meta tesla
```

### Scrape Specific Company

```bash
# Google only
python trigger_scrape.py --url https://web-production-94ca.up.railway.app --sources google

# FAANG companies
python trigger_scrape.py --url https://web-production-94ca.up.railway.app --sources google amazon apple meta
```

### With Keywords

```bash
python trigger_scrape.py --url https://web-production-94ca.up.railway.app --sources google --keywords "software engineer"
```

## What You Get

Each job scraped includes:

- ✅ **Job Title** - Official position name
- ✅ **Company** - Google, Amazon, Apple, etc.
- ✅ **Location** - City, State
- ✅ **Description** - Job details and requirements
- ✅ **URL** - Direct link to apply
- ✅ **Job Type** - Full-time, Contract, etc.
- ✅ **Remote Status** - Remote, Hybrid, or Onsite
- ✅ **Posted Date** - When the job was listed
- ✅ **Tags** - ['tech', 'google', 'faang']

## API Endpoints

### List Available Sources

```bash
GET https://web-production-94ca.up.railway.app/sources
```

Response:
```json
{
  "job_boards": [...],
  "company_careers": [
    {
      "id": "google",
      "name": "Google Careers",
      "type": "xml_feed",
      "active": true,
      "description": "Official Google job listings (all teams)"
    },
    ...
  ]
}
```

### Scrape Companies via API

```bash
POST https://web-production-94ca.up.railway.app/scrape
Content-Type: application/json

{
  "sources": ["google", "amazon", "apple"],
  "keywords": "software engineer",
  "max_pages": 3
}
```

## Job Examples

### Google Jobs You'll Get

- Software Engineer, YouTube
- Senior Software Engineer, Infrastructure
- Product Manager, Android
- Data Scientist, Google Cloud
- UX Designer, Chrome
- And hundreds more!

### Amazon Jobs You'll Get

- Software Development Engineer, AWS
- Solutions Architect, Amazon
- Product Manager, Alexa
- Data Engineer, AWS
- Cloud Support Engineer
- And more!

### Apple Jobs You'll Get

- Software Engineer, iOS
- Hardware Engineer, iPhone
- Product Designer, Mac
- Machine Learning Engineer, Siri
- And more!

## Advantages Over Job Boards

### Why Scrape Companies Directly?

1. **Latest Positions** - Get jobs as soon as companies post them
2. **No Middleman** - Direct from source, no job board fees
3. **Complete Information** - Full job descriptions, not summaries
4. **Official Links** - Apply directly on company site
5. **Better Quality** - Verified, legitimate positions
6. **Salary Info** - Many companies include salary ranges (Google does!)

## Technical Details

### File: `company_scrapers.py`

Contains scraper classes for each company:
- `GoogleCareersScraper` - XML feed parser
- `AmazonCareersScraper` - API client
- `AppleCareersScraper` - API client
- `MicrosoftCareersScraper` - API client
- `MetaCareersScraper` - Web scraper
- `TeslaCareersScraper` - API client

All scrapers inherit from `BaseScraper` and implement:
- `scrape(keywords, location, max_pages)` method
- Keyword filtering
- Location filtering
- Data normalization
- Error handling

### Integration with Aggregator

The company scrapers are automatically added to `JobAggregator`:

```python
from aggregator import JobAggregator

# Initialize aggregator (includes all company scrapers)
agg = JobAggregator()

# Scrape Google only
stats = agg.scrape_all(sources=['google'], max_pages=1)

# Scrape all FAANG
stats = agg.scrape_all(sources=['google', 'amazon', 'apple', 'meta'], max_pages=3)
```

## Rate Limiting

Company scrapers respect rate limits:
- 2-second delay between page requests
- Timeouts: 30-60 seconds
- Retry logic for failed requests
- US-based job filtering to reduce API calls

## Troubleshooting

### Company Scraper Not Working?

**Check logs:**
```bash
python company_scrapers.py
```

This runs the test suite for all scrapers.

**Common issues:**
1. **API changes** - Companies update their APIs periodically
2. **Rate limiting** - Too many requests too quickly
3. **Network errors** - Connection timeouts
4. **HTML structure changes** - For web scrapers (Meta, Tesla)

### Google Scraper Returns 0 Jobs

- Check if the feed URL is accessible: https://www.google.com/about/careers/applications/jobs/feed.xml
- Feed is very large (10MB+), may timeout
- Try with keywords to filter results

### Amazon/Apple Scrapers Fail

- These companies may have more strict API protections
- May require specific headers or user agents
- Consider adjusting timeout and retry settings

## Future Enhancements

### Companies to Add

- **Netflix** - careers.netflix.com
- **NVIDIA** - nvidia.wd5.myworkdayjobs.com
- **Salesforce** - salesforce.wd1.myworkdayjobs.com
- **Oracle** - oracle.com/careers
- **IBM** - ibm.com/careers
- **Adobe** - adobe.com/careers
- **Uber** - uber.com/careers
- **Airbnb** - airbnb.com/careers
- **Stripe** - stripe.com/jobs
- **Shopify** - shopify.com/careers

### Improvements

- **Caching** - Cache company feeds to reduce API calls
- **Webhooks** - Get notified when new jobs are posted
- **Filters** - More advanced filtering (experience level, salary range)
- **Alerts** - Email/SMS when specific jobs are posted

## Statistics

After scraping companies, check stats:

```bash
curl https://web-production-94ca.up.railway.app/stats
```

You'll see:
```json
{
  "total_jobs": 2500,
  "by_source": {
    "google": 150,
    "amazon": 200,
    "apple": 80,
    ...
  }
}
```

## Windows Batch File

Double-click `trigger_scrape.bat` to run a full scrape including all companies!

---

## Summary

You now have **direct access to jobs from:**
- ✅ Google (working)
- 🔨 Amazon (implemented)
- 🔨 Apple (implemented)
- 🔨 Microsoft (implemented)
- 🔨 Meta (implemented)
- 🔨 Tesla (implemented)

No more missing out on FAANG jobs! 🎉

---

**Need Help?**
- Check logs: `python company_scrapers.py`
- Test individual scrapers: `GoogleCareersScraper().scrape(max_pages=1)`
- Report issues: GitHub repository issues page
