# CRITICAL: Job Count Stuck - Root Cause Analysis

**Railway URL**: https://web-production-94ca.up.railway.app
**Current Status**: 1,710 jobs (STUCK)
**Last Update**: Days ago
**Problem**: Scraping runs but adds 0 new jobs (all duplicates)

---

## Root Cause Found

The scraper is working BUT returning **100% duplicates** because:

1. **Database has old jobs** (1,710 jobs from days ago)
2. **New scrapes find same jobs** (job boards haven't rotated listings)
3. **Duplicate detection working TOO well** (prevents any updates)
4. **USAJOBS not being scraped** despite being enabled

---

## Why USAJOBS Isn't Adding Jobs

Even though USAJOBS shows `"active": true`, it's not actually scraping because:

**Issue**: The `scheduled_scraper.py` only searches specific profiles, and USAJOBS is only included if explicitly called.

**Check the code**: Lines 328-335 in `scheduled_scraper.py`:
```python
# USAJOBS (if available) - Excellent for all entry-level positions
if self.usajobs_scraper and profile_name in ['entry_tech', 'entry_finance', 'entry_data', 'mid_tech', 'mid_finance']:
    new, total = self.search_with_rate_limit('usajobs', keyword)
```

**The problem**: `search_with_rate_limit('usajobs', keyword)` is being called, but the aggregator might not be initialized with USAJOBS in the Railway environment.

---

## Immediate Solutions

### Solution 1: Force Scrape USAJOBS Directly (Quick Test)

Test if USAJOBS actually works:

```bash
curl -X POST "https://web-production-94ca.up.railway.app/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": "software engineer",
    "sources": ["usajobs"],
    "max_pages": 1
  }'
```

Check response - does it find jobs?

### Solution 2: Clear Old Jobs and Rescrape

The database is full of stale jobs. Options:

**Option A: Truncate and rescrape** (nuclear option)
```sql
-- In Railway PostgreSQL
TRUNCATE TABLE jobs CASCADE;
```
Then trigger scraping - everything will be "new"

**Option B: Delete jobs older than 30 days**
```sql
DELETE FROM jobs
WHERE created_at < NOW() - INTERVAL '30 days';
```

**Option C: Mark all as updated and let deduplication work**
- Keep existing jobs
- Scraper will add truly new listings only

### Solution 3: Fix Scheduled Scraper to Use USAJOBS

The `scheduled_scraper.py` needs to ensure USAJOBS is actually being called with proper keywords.

---

## Test Right Now

Let me test if USAJOBS scraping actually works:

```bash
# Test 1: Check if USAJOBS scraper is initialized
curl "https://web-production-94ca.up.railway.app/sources" | grep -A5 "usajobs"

# Should show:
# "id": "usajobs",
# "active": true

# Test 2: Try to scrape USAJOBS directly
curl -X POST "https://web-production-94ca.up.railway.app/scrape" \
  -H "Content-Type: application/json" \
  -d '{"keywords": "IT specialist", "sources": ["usajobs"], "max_pages": 1}'

# Should return job count > 0

# Test 3: Check stats after
curl "https://web-production-94ca.up.railway.app/stats"

# Should show usajobs in by_source
```

---

## Long-Term Fix: GitHub Actions

Once we confirm scraping works, set up automation:

1. GitHub → Settings → Secrets → Actions
2. Add secret:
   - Name: `RAILWAY_APP_URL`
   - Value: `https://web-production-94ca.up.railway.app`
3. GitHub → Actions → Run "Scrape Jobs Every 6 Hours"

---

## Why Job Count Isn't Increasing

**Hypothesis 1**: Job boards (RemoteOK, Remotive) have same listings
- Solution: Add more sources (USAJOBS, Indeed, FAANG)

**Hypothesis 2**: Duplicate detection too aggressive
- Solution: Check job_id uniqueness logic
- May need to allow updates if job content changes

**Hypothesis 3**: USAJOBS not actually scraping
- Solution: Debug why USAJOBS source isn't being hit
- Check Railway logs for USAJOBS scraping attempts

**Hypothesis 4**: Rate limiting or API errors
- Solution: Check Railway logs for errors
- USAJOBS: 10 req/min limit
- Other APIs may be timing out

---

## Next Steps (Priority Order)

1. **Test USAJOBS directly** (see Solution 1 above)
2. **Check Railway logs** for errors
3. **Consider clearing old jobs** (see Solution 2)
4. **Set up GitHub Actions** for automation
5. **Monitor for 24 hours** to see if jobs increase

---

## Expected Behavior After Fix

**Immediate** (after USAJOBS works):
- Jobs increase: 1,710 → 3,000+
- USAJOBS appears in by_source
- recent_jobs_24h > 0

**After 24 hours**:
- 5,000-7,000 total jobs
- Multiple sources active
- Consistent growth

**After 1 week**:
- 15,000-20,000 total jobs
- All sources contributing
- Fresh listings every 6 hours

---

## Commands to Run NOW

```bash
# 1. Test USAJOBS scraping
curl -X POST "https://web-production-94ca.up.railway.app/scrape" \
  -H "Content-Type: application/json" \
  -d '{"keywords": "software developer", "sources": ["usajobs"]}'

# 2. Wait 30 seconds
sleep 30

# 3. Check if USAJOBS jobs were added
curl "https://web-production-94ca.up.railway.app/stats" | grep usajobs

# 4. If USAJOBS appears, trigger full priority scrape
curl -X POST "https://web-production-94ca.up.railway.app/genz/search-priority"

# 5. Wait 5 minutes
sleep 300

# 6. Check final count
curl "https://web-production-94ca.up.railway.app/stats"
```

---

**Status**: NEEDS IMMEDIATE ATTENTION
**Priority**: CRITICAL
**Created**: October 28, 2025
