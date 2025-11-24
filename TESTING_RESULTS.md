# Platform Scraper Testing Results

## Test Date: 2025-11-24

### Summary

We tested platform scrapers for Greenhouse, Lever, AshbyHQ, Taleo, and iCIMS with sample companies from the Gen-Z hiring list.

**Results**: Only 1 out of 5 platforms fully working

### Test Results

#### ✅ GREENHOUSE - **WORKING**
- **Test Company**: Allbirds
- **URL**: `https://boards.greenhouse.io/allbirds`
- **Result**: SUCCESS - Found 2 jobs
- **Sample Job**: "Senior Designer - Content & Growth" in Portland, Oregon
- **Status**: Fully functional, ready to use

#### ❌ LEVER - **NOT TESTED**
- **Test Company**: Seventh Generation
- **Expected URL**: `https://jobs.lever.co/seventhgeneration`
- **Result**: ERROR 404 - Company not using Lever
- **Status**: Platform detection was incorrect
- **Action Needed**: Find actual companies using Lever, or skip this platform

#### ❌ ASHBYHQ - **REQUIRES JAVASCRIPT**
- **Test Company**: Shopify
- **URL**: `https://jobs.ashbyhq.com/Shopify`
- **Result**: Page loads but no jobs visible (JavaScript-rendered React app)
- **Issue**: AshbyHQ uses client-side rendering, HTML scraping won't work
- **Status**: Requires either:
  - Selenium/Playwright for browser automation
  - Reverse-engineering their GraphQL API
  - Skip this platform
- **Recommendation**: Skip AshbyHQ for now (only 1 company)

#### ❌ TALEO - **NO JOBS FOUND**
- **Test Company**: American Express
- **URL**: `https://americanexpress.com/careers`
- **Result**: Scraper runs but finds 0 jobs
- **Issue**: Taleo implementations vary widely per company, likely requires company-specific configuration
- **Status**: Generic scraper not working
- **Recommendation**: Skip or implement company-specific scrapers

#### ❌ iCIMS - **REQUIRES JAVASCRIPT**
- **Test Company**: Booking.com
- **URL**: `https://jobs.booking.com`
- **Result**: Page loads but job listings are JavaScript-rendered
- **Issue**: Similar to Ashby - requires browser automation
- **Status**: HTML scraping won't work reliably
- **Recommendation**: Skip iCIMS for now (only 2 companies)

### Platform Detection Issues

The automatic platform detection system had **high false positive rate**:

- **Epic Games**: Detected as Greenhouse, but NOT using Greenhouse (403 error)
- **Seventh Generation**: Detected as Lever, but NOT using Lever (404 error)
- **Shopify**: Detected as AshbyHQ - CORRECT, but requires JavaScript
- **American Express**: Detected as Taleo - CORRECT, but generic scraper doesn't work
- **Booking.com**: Detected as iCIMS - CORRECT, but requires JavaScript

**Root Cause**: The detection system looked for keywords in page content, but didn't verify the platform was actually accessible/scrapable.

### Revised Coverage Estimate

#### Scrapable Companies

**Existing Custom Scrapers** (6 companies):
- ✅ Google/Alphabet
- ✅ Amazon
- ✅ Microsoft
- ✅ Apple
- ✅ Meta
- ✅ Tesla

**Workday** (15 companies) - ⚠️ Need manual configuration:
- Deloitte, PwC, KPMG, Accenture, Booz Allen Hamilton
- Bank of America, Synchrony
- Nike, Target, Whole Foods, Ben & Jerry's
- Pfizer, Moderna, Vertex Pharmaceuticals
- Plus Meta

**Greenhouse** (1-3 companies verified):
- ✅ Allbirds (VERIFIED)
- ❓ Need to manually verify other companies marked as Greenhouse

**Total Realistically Scrapable**: ~22-24 companies (22-24% coverage)

### Recommendations

#### Option 1: Use What Works (Recommended)
**Focus on platforms that work well:**
1. ✅ Keep 6 existing custom scrapers (FAANG + Tesla)
2. ✅ Add 15 Workday companies (just need config)
3. ✅ Manually verify and add Greenhouse companies
4. ❌ Skip Lever, AshbyHQ, Taleo, iCIMS (too unreliable/complex)

**Expected Result**: 21-24 companies scrapable (21-24% coverage)

#### Option 2: Add Selenium Support
**Invest time in browser automation:**
- Add Selenium or Playwright
- Scrape JavaScript-rendered sites (Ashby, iCIMS)
- Much slower, more resource-intensive
- More brittle (breaks when sites change)

**Expected Result**: +3-4 more companies, but significantly more complexity

#### Option 3: Company-Specific Research
**Manually research top 20-30 companies:**
- Find actual careers pages and platforms
- Build custom scrapers for high-value companies
- Time-intensive but most reliable

### Next Steps (Recommended Path)

**Immediate** (Today):
1. ✅ Update [GEN_Z_COMPANIES_SUMMARY.md](GEN_Z_COMPANIES_SUMMARY.md) with realistic numbers
2. ⏸ Add 15 Workday companies to [workday_scraper.py](workday_scraper.py:1)
3. ⏸ Manually verify 2-3 Greenhouse companies from the list
4. ⏸ Remove non-working platform scrapers (Lever, Ashby, Taleo, iCIMS) OR mark as "future/experimental"

**Short-term** (This Week):
- Integrate working scrapers into aggregator
- Test with 1-2 Workday companies
- Deploy to Railway
- Monitor job counts

**Long-term** (Future):
- Consider Selenium for JavaScript-heavy sites
- Research top 10-20 custom platforms manually
- Add company-specific scrapers as needed

### Files to Update

1. [GEN_Z_COMPANIES_SUMMARY.md](GEN_Z_COMPANIES_SUMMARY.md) - Update coverage numbers (31% → 22%)
2. [company_scraper_factory.py](company_scraper_factory.py:1) - Remove unsupported platforms from supported list
3. [platform_scrapers.py](platform_scrapers.py:1) - Mark Ashby/Taleo/iCIMS as experimental or remove
4. [workday_scraper.py](workday_scraper.py:1) - Add 15 new companies to COMPANIES dict

### Lessons Learned

1. **Platform detection is hard** - Can't rely on keyword matching alone
2. **JavaScript rendering is common** - Many modern career sites use React/Vue
3. **Generic scrapers don't always work** - Taleo/iCIMS implementations vary too much per company
4. **Focus on what works** - Better to have 20 reliable scrapers than 50 flaky ones
5. **Manual verification is essential** - Always test with real companies before claiming support

### Conclusion

While we built a comprehensive platform detection system and multiple platform scrapers, real-world testing revealed that:

- Only **Greenhouse scraper is fully functional**
- **Workday scrapers** work but need configuration
- **AshbyHQ, Taleo, iCIMS** require browser automation or are too inconsistent
- **Platform detection** had false positives

**Realistic coverage**: 22-24 companies (22-24%) instead of 31 (31%)

This is still a solid foundation! We can:
- Scrape jobs from 20+ top companies
- Add more companies over time with manual research
- Expand to JavaScript rendering if needed later

**Recommendation**: Proceed with Greenhouse + Workday companies (21-24 total), deploy, and iterate based on results.
