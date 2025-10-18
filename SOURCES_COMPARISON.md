# Job Sources Comparison

A comprehensive comparison of all integrated job sources to help you choose which ones to use.

## Overview Table

| Source | Type | API Key | Remote Jobs | Tech Focus | Job Count | Update Freq | Quality |
|--------|------|---------|-------------|------------|-----------|-------------|---------|
| RemoteOK | API | No | ✓ | High | 1000s | Daily | ⭐⭐⭐⭐⭐ |
| Remotive | API | No | ✓ | High | 100s | Daily | ⭐⭐⭐⭐⭐ |
| We Work Remotely | Scrape | No | ✓ | High | 100s | Daily | ⭐⭐⭐⭐ |
| Adzuna | API | Yes | Mixed | Medium | 10000s | Real-time | ⭐⭐⭐⭐ |
| Indeed RSS | RSS | No | Mixed | Low | 1000s | Hourly | ⭐⭐⭐ |
| GitHub | API | No* | ✓ | Very High | 100s | Variable | ⭐⭐⭐ |
| Authentic Jobs | RSS | No | Mixed | High | 100s | Daily | ⭐⭐⭐⭐ |
| Crunchboard | Scrape | No | Mixed | Medium | 100s | Daily | ⭐⭐⭐ |

*GitHub API works without key but has lower rate limits

## Detailed Comparison

### 1. RemoteOK
**Type**: Public JSON API
**URL**: https://remoteok.com/

**Pros:**
- ✓ No API key required
- ✓ Simple JSON API
- ✓ 100% remote jobs
- ✓ Tech-focused
- ✓ Includes salary data
- ✓ Good categorization
- ✓ Fast and reliable

**Cons:**
- ✗ Remote only (not good for location-specific)
- ✗ Rate limiting on high volume

**Best For:**
- Remote tech positions
- Startups
- International opportunities

**Example Jobs:**
- Senior Python Developer - Remote
- React Frontend Engineer - Worldwide
- DevOps Engineer - US/EU Remote

---

### 2. Remotive
**Type**: Public REST API
**URL**: https://remotive.com/

**Pros:**
- ✓ No API key required
- ✓ Clean JSON API
- ✓ Curated listings
- ✓ High quality jobs
- ✓ Multiple categories
- ✓ Company descriptions

**Cons:**
- ✗ Smaller quantity
- ✗ Remote-focused only

**Best For:**
- Remote positions
- Quality over quantity
- Vetted companies

**Example Jobs:**
- Backend Developer - Remote
- Product Manager - Anywhere
- UX Designer - Global

---

### 3. We Work Remotely
**Type**: Web Scraping
**URL**: https://weworkremotely.com/

**Pros:**
- ✓ Popular platform
- ✓ High-quality listings
- ✓ Good categorization
- ✓ Established companies
- ✓ Detailed job posts

**Cons:**
- ✗ Scraping required (slower)
- ✗ Structure changes can break scraper
- ✗ Remote only

**Best For:**
- Remote tech jobs
- Established companies
- Multiple categories (design, marketing, etc.)

**Example Jobs:**
- Full Stack Engineer - Remote
- Customer Success Manager - Worldwide
- Content Writer - Anywhere

---

### 4. Adzuna
**Type**: Official REST API
**URL**: https://developer.adzuna.com/

**Pros:**
- ✓ Millions of jobs
- ✓ Multiple countries
- ✓ Salary data
- ✓ Official API
- ✓ Location-based search
- ✓ Free tier available

**Cons:**
- ✗ API key required
- ✗ Rate limits on free tier
- ✗ Quality varies
- ✗ Many duplicates

**Best For:**
- Comprehensive coverage
- Specific locations
- Salary research
- International markets

**Example Jobs:**
- Software Engineer - San Francisco
- Data Analyst - London
- Project Manager - Sydney

---

### 5. Indeed RSS
**Type**: RSS Feeds
**URL**: https://www.indeed.com/

**Pros:**
- ✓ Huge job volume
- ✓ No API key
- ✓ All industries
- ✓ Location-specific
- ✓ Frequently updated

**Cons:**
- ✗ RSS limited to ~50 results
- ✗ Lower quality filtering
- ✗ Many duplicates
- ✗ Inconsistent formatting

**Best For:**
- Broad searches
- Local jobs
- High volume needs
- Multiple industries

**Example Jobs:**
- Software Developer - New York, NY
- Web Developer - Austin, TX
- Java Developer - Chicago, IL

---

### 6. GitHub
**Type**: GitHub API
**URL**: https://github.com/

**Pros:**
- ✓ Tech-focused
- ✓ Open source projects
- ✓ Startup jobs
- ✓ Free to use
- ✓ Remote-friendly

**Cons:**
- ✗ Not traditional job board
- ✗ Requires creative searching
- ✗ Limited structure
- ✗ Rate limits without token

**Best For:**
- Open source positions
- Tech startups
- Developer roles
- Remote opportunities

**Example Jobs:**
- OSS Maintainer - Remote
- Blockchain Developer - Global
- DevRel Engineer - Anywhere

---

### 7. Authentic Jobs
**Type**: RSS Feed
**URL**: https://authenticjobs.com/

**Pros:**
- ✓ Curated tech jobs
- ✓ Quality over quantity
- ✓ Design/dev focus
- ✓ Clean data
- ✓ No API key

**Cons:**
- ✗ Smaller volume
- ✗ RSS limitations
- ✗ Niche audience

**Best For:**
- Design positions
- Web development
- Creative tech roles
- Quality listings

**Example Jobs:**
- UI Designer - Remote/SF
- Frontend Developer - New York
- Product Designer - Los Angeles

---

### 8. Crunchboard
**Type**: Web Scraping
**URL**: https://www.crunchboard.com/

**Pros:**
- ✓ Startup focus
- ✓ TechCrunch network
- ✓ Tech companies
- ✓ Growth companies

**Cons:**
- ✗ Scraping required
- ✗ Smaller volume
- ✗ Inconsistent updates
- ✗ Structure changes

**Best For:**
- Startup jobs
- Early-stage companies
- Tech industry
- Growth opportunities

**Example Jobs:**
- Engineer #5 - Seed Stage Startup
- Growth Marketer - Series A
- Product Lead - YC Company

---

## Recommendations by Use Case

### For Maximum Coverage
Use all sources:
```bash
python main.py
```

### For Remote Tech Jobs Only
```bash
python main.py --sources remoteok remotive weworkremotely
```

### For Local/Location-Specific
```bash
python main.py --sources adzuna indeed --location "San Francisco"
```

### For Quality Over Quantity
```bash
python main.py --sources remotive authenticjobs
```

### For Startups
```bash
python main.py --sources remoteok github crunchboard
```

### For Quick Testing
```bash
python main.py --sources remoteok --max-pages 1
```

## Performance Comparison

| Source | Avg Speed | Jobs/Request | Reliability | Rate Limits |
|--------|-----------|--------------|-------------|-------------|
| RemoteOK | Fast | 50-100 | ⭐⭐⭐⭐⭐ | Generous |
| Remotive | Fast | 20-50 | ⭐⭐⭐⭐⭐ | Generous |
| We Work Remotely | Slow | 10-30 | ⭐⭐⭐⭐ | None |
| Adzuna | Fast | 50+ | ⭐⭐⭐⭐⭐ | 300/month (free) |
| Indeed | Medium | 10-50 | ⭐⭐⭐⭐ | Moderate |
| GitHub | Fast | 30+ | ⭐⭐⭐⭐ | 60/hour (no key) |
| Authentic Jobs | Fast | 20-40 | ⭐⭐⭐⭐ | Generous |
| Crunchboard | Slow | 10-50 | ⭐⭐⭐ | None |

## Data Quality Comparison

### Salary Information
1. **Adzuna** - Most comprehensive
2. **RemoteOK** - Good coverage
3. **Indeed** - Varies widely
4. Others - Limited

### Job Descriptions
1. **We Work Remotely** - Most detailed
2. **Remotive** - Very good
3. **Authentic Jobs** - Good
4. Others - Varies

### Company Information
1. **Adzuna** - Comprehensive
2. **RemoteOK** - Good
3. **Remotive** - Good
4. Others - Basic

### Remote Flag Accuracy
1. **RemoteOK** - 100% (remote only)
2. **Remotive** - 100% (remote only)
3. **We Work Remotely** - 100% (remote only)
4. Others - Varies

## Cost Analysis

| Source | Setup Cost | API Cost | Maintenance |
|--------|------------|----------|-------------|
| RemoteOK | Free | Free | Easy |
| Remotive | Free | Free | Easy |
| We Work Remotely | Free | Free | Medium |
| Adzuna | Free | Free tier available | Easy |
| Indeed | Free | Free | Easy |
| GitHub | Free | Free | Easy |
| Authentic Jobs | Free | Free | Easy |
| Crunchboard | Free | Free | Medium |

**Adzuna Pricing:**
- Free tier: 300 calls/month
- Standard: $450/month (unlimited)
- Enterprise: Custom pricing

## Legal & Ethical Considerations

| Source | Terms Friendly | robots.txt | Rate Limits | Commercial Use |
|--------|----------------|------------|-------------|----------------|
| RemoteOK | ✓ | Allowed | Yes | Check ToS |
| Remotive | ✓ | Allowed | Yes | Check ToS |
| We Work Remotely | ⚠ | Check | N/A | Check ToS |
| Adzuna | ✓ | N/A (API) | Yes | ✓ |
| Indeed | ⚠ | Limited | Yes | Check ToS |
| GitHub | ✓ | N/A (API) | Yes | ✓ |
| Authentic Jobs | ⚠ | Check | Yes | Check ToS |
| Crunchboard | ⚠ | Check | N/A | Check ToS |

**⚠ Warning**: Always review Terms of Service before commercial use

## Recommended Combinations

### Combination 1: Best Coverage
```python
sources = ['remoteok', 'remotive', 'adzuna', 'indeed']
# Pros: Maximum job count
# Cons: More duplicates
```

### Combination 2: Quality Remote Jobs
```python
sources = ['remoteok', 'remotive', 'weworkremotely']
# Pros: High quality, all remote
# Cons: Remote-only
```

### Combination 3: Tech Startups
```python
sources = ['remoteok', 'github', 'crunchboard']
# Pros: Startup focus
# Cons: Smaller volume
```

### Combination 4: Balanced Approach
```python
sources = ['remoteok', 'remotive', 'authenticjobs', 'indeed']
# Pros: Good balance of quality/quantity
# Cons: Mixed remote/local
```

## Update Frequency

How often to scrape each source:

| Source | Recommended Frequency | Reasoning |
|--------|----------------------|-----------|
| RemoteOK | Every 6-12 hours | Daily updates |
| Remotive | Every 12-24 hours | Daily updates |
| We Work Remotely | Every 12-24 hours | Less frequent |
| Adzuna | Every 3-6 hours | Real-time updates |
| Indeed | Every 6-12 hours | Frequent updates |
| GitHub | Every 24 hours | Less frequent |
| Authentic Jobs | Every 24 hours | Weekly updates |
| Crunchboard | Every 24-48 hours | Less frequent |

## Conclusion

**For most users**, we recommend starting with:
```bash
python main.py --sources remoteok remotive indeed
```

This provides:
- Good volume (1000s of jobs)
- Quality listings
- Mix of remote and local
- No API keys required
- Fast performance

Then add more sources based on your specific needs!
