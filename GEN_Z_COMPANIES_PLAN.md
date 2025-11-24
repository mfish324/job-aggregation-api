# Gen-Z Hiring Companies Scraper Strategy

## Overview
We're building custom scrapers for 100 top Gen-Z hiring companies to aggregate their job postings into LevelUp Careers.

## Current Progress

### ✓ Completed
1. **Platform Detection System** - Created `company_scraper_generator.py` to detect which ATS platform each company uses
2. **Platform-Specific Scrapers** - Created `platform_scrapers.py` with generic scrapers for:
   - Greenhouse
   - Lever
   - AshbyHQ
   - Workday (already existed)
3. **Scraper Factory** - Created `company_scraper_factory.py` to dynamically create scrapers based on company platform
4. **Full Analysis Running** - Currently analyzing all 100 companies to detect their platforms (10-15 minutes)

### 🔄 In Progress
- Analyzing all 100 companies from `gen_z_hiring_companies.csv`
- Generating configuration file with platform mappings

### ⏸ Pending
1. Review analysis results
2. Create scrapers for additional platforms if needed
3. Integrate company scrapers into aggregator
4. Test sample companies
5. Deploy to Railway

## Architecture

### 1. Platform Detection
```
CSV File → CompanyScraperGenerator → Detect Platform → Config JSON
```

The system:
- Reads company list from CSV
- Constructs careers URLs (company.com/careers)
- Fetches each careers page
- Detects platform by:
  - URL patterns (myworkdayjobs.com, greenhouse.io, lever.co, etc.)
  - Page content analysis
  - Meta tags and scripts

### 2. Scraper Creation
```
Config JSON → CompanyScraperFactory → Create Scrapers → Aggregator
```

For each company:
- Check if custom scraper exists (Google, Amazon, etc.)
- Otherwise, create platform-specific scraper
- Use standardized interface: `scraper.scrape(keywords, location, max_pages)`

### 3. Platform Scrapers

**Greenhouse** (`GreenhouseScraper`)
- API: `https://boards-api.greenhouse.io/v1/boards/{token}/jobs`
- Returns JSON with all jobs
- Extract: title, location, description, date

**Lever** (`LeverScraper`)
- API: `https://api.lever.co/v0/postings/{site}`
- Returns JSON with all jobs
- Extract: title, location, categories, description

**AshbyHQ** (`AshbyHQScraper`)
- Scrapes HTML from `https://jobs.ashbyhq.com/{site}`
- Parses job cards
- Extract: title, location, URL

**Workday** (`WorkdayScraper`)
- Already exists for Walmart, Nike, Citi
- POST to: `https://{company}.wd5.myworkdayjobs.com/wday/cxs/{company}/{site}/jobs`
- Returns paginated JSON

**Custom** (Company-specific scrapers)
- Google: XML feed scraper (already exists)
- Amazon: JSON API scraper (already exists)
- Microsoft: API scraper (already exists)
- Apple: API scraper (already exists)
- Meta: API scraper (already exists)
- Tesla: API scraper (already exists)

## Expected Platform Distribution

Based on sample analysis:
- **Custom platforms**: ~60-70% (large companies with proprietary systems)
- **Greenhouse**: ~10-15% (startups and mid-size companies)
- **Lever**: ~5-10% (tech companies)
- **Workday**: ~5-10% (enterprise companies)
- **Other platforms**: ~5-10% (iCIMS, Taleo, SmartRecruiters, etc.)

## Integration Plan

### Step 1: Generate Config (IN PROGRESS)
```bash
python analyze_all_companies.py
# Output: gen_z_companies_full_config.json
```

### Step 2: Test Factory
```bash
python company_scraper_factory.py
# Shows summary of supported companies
```

### Step 3: Integrate into Aggregator
Update `aggregator.py`:
```python
from company_scraper_factory import CompanyScraperFactory

class JobAggregator:
    def __init__(self):
        # ... existing scrapers ...

        # Add Gen-Z company scrapers
        self.company_factory = CompanyScraperFactory()
        company_scrapers = self.company_factory.create_all_scrapers()
        self.scrapers.update(company_scrapers)
```

### Step 4: Test Sample Companies
```bash
python test_company_scrapers.py
# Test 5-10 companies from each platform
```

### Step 5: Deploy
- Push to GitHub
- Railway auto-deploys
- Monitor scraping logs

## Challenges & Solutions

### Challenge 1: Most Companies Use Custom Platforms
**Solution**:
- Focus on companies with standard ATS platforms first
- For custom platforms, manually research their APIs
- Some may not be scrapable (require Selenium or have anti-scraping)

### Challenge 2: Careers URL Discovery
**Solution**:
- Try common patterns: `/careers`, `/jobs`, `jobs.{domain}`, `careers.{domain}`
- For companies that fail, manually update the CSV with correct URLs
- Store known URLs in config for future runs

### Challenge 3: Rate Limiting
**Solution**:
- Add delays between requests (2-5 seconds)
- Respect robots.txt
- Use session pooling
- Implement exponential backoff

### Challenge 4: Dynamic Content (React/Vue apps)
**Solution**:
- Look for hidden JSON APIs
- Check Network tab in DevTools
- If necessary, use Selenium for JavaScript-heavy sites
- For now, skip sites that require JS rendering

## Files Created

1. **company_scraper_generator.py** - Platform detection and analysis
2. **platform_scrapers.py** - Generic scrapers for Greenhouse, Lever, AshbyHQ
3. **company_scraper_factory.py** - Factory to create scrapers dynamically
4. **analyze_all_companies.py** - Script to analyze all 100 companies
5. **gen_z_companies_full_config.json** - Configuration file (generated)

## Next Steps After Analysis Completes

1. **Review Results**
   ```bash
   cat gen_z_companies_full_config.json
   ```

2. **Check Coverage**
   ```bash
   python company_scraper_factory.py
   ```

3. **Manual URL Updates** (if needed)
   - For companies where /careers doesn't work
   - Research actual careers URLs
   - Update CSV or config

4. **Add Missing Platforms**
   - If analysis shows companies using iCIMS, Taleo, etc.
   - Create scrapers for those platforms

5. **Integration Testing**
   - Test 2-3 companies from each platform
   - Verify jobs are scraped correctly
   - Check enhanced fields (company_website, tags)

6. **Full Deployment**
   - Integrate into aggregator
   - Add to scheduled_scraper
   - Deploy to Railway
   - Monitor first scraping run

## Estimated Coverage

After implementation:
- **Scrapable with existing/platform scrapers**: 30-40 companies
- **Requires custom development**: 20-30 companies
- **Not scrapable (requires Selenium/complex)**: 20-30 companies
- **API access required**: 10-20 companies

**Target**: Get 40-50 companies scraped in first phase, expand over time.

## Timeline

- **Phase 1 (Today)**: Platform detection, scraper factory ✓
- **Phase 2 (Next)**: Integration and testing
- **Phase 3 (Future)**: Add more custom scrapers, handle edge cases
