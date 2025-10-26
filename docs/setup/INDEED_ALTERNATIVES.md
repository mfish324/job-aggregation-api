# Indeed Scraping - Alternatives

## Issue

Indeed actively blocks automated scraping with 403 Forbidden errors. They have sophisticated bot detection.

## Why Indeed is Difficult

1. **Bot Detection**: Advanced JavaScript challenges
2. **Rate Limiting**: Aggressive IP blocking
3. **Terms of Service**: Prohibits scraping
4. **Legal Risk**: Indeed has sued scrapers in the past

## Alternatives to Indeed

### Option 1: Use Indeed Publisher Program (Recommended) ✅

**Indeed Partner API** - Official, legal, and reliable

```python
# Sign up at: https://www.indeed.com/publisher
# Get API key

class IndeedPublisherAPI(BaseScraper):
    def __init__(self, publisher_id):
        super().__init__()
        self.publisher_id = publisher_id
        self.base_url = "http://api.indeed.com/ads/apisearch"

    def scrape(self, keywords=None, location=None, max_pages=5):
        jobs = []
        for page in range(max_pages):
            params = {
                'publisher': self.publisher_id,
                'q': keywords or '',
                'l': location or '',
                'sort': 'date',
                'radius': '25',
                'st': 'jobsite',
                'jt': 'fulltime',
                'start': page * 25,
                'limit': 25,
                'fromage': '7',  # Last 7 days
                'format': 'json',
                'v': '2'
            }

            response = self.session.get(self.base_url, params=params)
            data = response.json()

            for job in data.get('results', []):
                jobs.append({
                    'title': job.get('jobtitle'),
                    'company': job.get('company'),
                    'location': job.get('formattedLocation'),
                    'description': job.get('snippet'),
                    'url': job.get('url'),
                    'source': 'indeed',
                    'posted_date': self.normalize_date(job.get('date')),
                    'job_type': job.get('jobtype', 'N/A'),
                    'salary': None,
                    'tags': json.dumps([]),
                    'remote': 'remote' in job.get('formattedLocation', '').lower()
                })

        return jobs
```

**How to Get Access:**
1. Visit: https://www.indeed.com/publisher
2. Sign up for free publisher account
3. Get your publisher ID
4. Add to `.env`: `INDEED_PUBLISHER_ID=your_id`

**Pros:**
- ✅ Official API - legal and compliant
- ✅ No rate limiting issues
- ✅ Reliable data
- ✅ Free for low volume

**Cons:**
- ❌ Requires signup and approval
- ❌ Must include Indeed attribution
- ❌ Limited to 25 results per query

---

### Option 2: SimplyHired (Indeed Alternative)

SimplyHired aggregates from multiple sources including Indeed data:

```python
class SimplyHiredScraper(BaseScraper):
    def scrape(self, keywords=None, location=None, max_pages=5):
        # Similar structure, easier to scrape
        # RSS feeds available
        pass
```

---

### Option 3: Use Existing Working Sources

You already have **4 working sources** with 1,710 jobs:

| Source | Jobs | Works? |
|--------|------|--------|
| **Remotive** | 1,602 | ✅ |
| **RemoteOK** | 97 | ✅ |
| **Authentic Jobs** | 10 | ✅ |
| **GitHub** | 1 | ✅ |

**Recommendation**: Focus on these reliable sources rather than fighting Indeed's blocks.

---

### Option 4: Add More Working Sources

Instead of Indeed, add these working alternatives:

#### 1. **LinkedIn Jobs RSS**
```python
# LinkedIn has public RSS feeds
url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keywords}"
```

#### 2. **ZipRecruiter**
```python
# ZipRecruiter has better scraping tolerance
url = "https://www.ziprecruiter.com/jobs-search"
```

#### 3. **Glassdoor Jobs**
```python
# Glassdoor has public job listings
url = "https://www.glassdoor.com/Job/jobs.htm"
```

#### 4. **AngelList/Wellfound**
```python
# Startup jobs
url = "https://angel.co/jobs"
```

#### 5. **Dice.com** (Tech Jobs)
```python
# Tech-focused job board
url = "https://www.dice.com/jobs"
```

#### 6. **Monster.com**
```python
# Large general job board
url = "https://www.monster.com/jobs/search/"
```

---

## Recommended Solution

### Immediate: Remove Indeed, Add Working Sources

```python
# In aggregator.py
self.scrapers = {
    'remoteok': RemoteOKScraper(),
    'remotive': RemotiveScraper(),
    'weworkremotely': WeWorkRemotelyScraper(),
    'authenticjobs': AuthenticJobsScraper(),
    'github': GitHubJobsScraper(),
    # Remove: 'indeed': IndeedScraper(),  # Blocked
    'linkedin': LinkedInScraper(),  # Add new working source
    'ziprecruiter': ZipRecruiterScraper(),  # Add new working source
}
```

### Long-term: Sign Up for Indeed Publisher API

1. Apply at https://www.indeed.com/publisher
2. Wait for approval (usually 1-2 days)
3. Add official API integration
4. Get legal access to Indeed data

---

## Current Status

**Working Sources (1,710 jobs):**
- ✅ Remotive: 1,602 jobs
- ✅ RemoteOK: 97 jobs
- ✅ Authentic Jobs: 10 jobs
- ✅ GitHub: 1 job

**Blocked/Not Working:**
- ❌ Indeed: 403 Forbidden (blocks bots)
- ❌ Crunchboard: 403 Forbidden
- ⚠️ We Work Remotely: 0 jobs (may need fixing)

---

## What to Do Now

### Option A: Keep Current Sources ✅ **Recommended**

You already have **1,710 jobs** from working sources. This is plenty for a job board!

```bash
# Current working scrape
python main.py --sources remoteok remotive authenticjobs github --max-pages 5
```

### Option B: Add More Working Sources

I can add these alternatives that don't block bots:
- LinkedIn Jobs
- ZipRecruiter
- Glassdoor
- Dice.com (tech jobs)
- Monster.com

### Option C: Apply for Indeed Publisher API

Sign up for official access (free, but requires approval):
https://www.indeed.com/publisher

---

## My Recommendation

**Don't waste time fighting Indeed's bot detection.** You have:

✅ 1,710 working jobs
✅ 4 reliable sources
✅ 99.4% remote jobs
✅ 46.4% with salary info

**Instead:**
1. Use what's working (RemoteOK, Remotive, etc.)
2. Add 2-3 more working sources (LinkedIn, ZipRecruiter)
3. Apply for Indeed Publisher API for official access

Would you like me to add LinkedIn, ZipRecruiter, or other working sources instead?
