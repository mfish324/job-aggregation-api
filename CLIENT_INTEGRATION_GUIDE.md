# Client Integration Guide

How to integrate the Job Server API into your other job search platforms.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Job Server API                           │
│              http://localhost:8000                           │
│  ┌────────────────────────────────────────────────────┐     │
│  │  FastAPI REST API                                  │     │
│  │  - /jobs (list jobs)                               │     │
│  │  - /jobs/{id} (job details)                        │     │
│  │  - /scrape (trigger scraping)                      │     │
│  │  - /stats (statistics)                             │     │
│  └────────────────────────────────────────────────────┘     │
│                           ↓                                  │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Job Board Database (lightweight)                  │     │
│  │  - Essential fields only                           │     │
│  │  - Fast queries                                    │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↑
                            │ HTTP/REST API calls
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌───────▼────────┐  ┌──────▼─────────┐
│  Platform #1   │  │  Platform #2   │  │  Web Frontend  │
│  (Python)      │  │  (Node.js)     │  │  (React/Vue)   │
└────────────────┘  └────────────────┘  └────────────────┘
```

## Quick Start

### 1. Start the Job Server

```bash
cd Job_APIs
python job_server.py
```

Server runs at: **http://localhost:8000**

API Docs: **http://localhost:8000/docs** (interactive!)

### 2. Test the API

```bash
# Get jobs
curl http://localhost:8000/jobs?page=1&per_page=10

# Get job details
curl http://localhost:8000/jobs/1

# Get stats
curl http://localhost:8000/stats
```

---

## Integration Options

### Option 1: Direct HTTP Requests (Any Language)

**Pros:**
- Works with any programming language
- Simple HTTP requests
- No dependencies

**Cons:**
- Manual request handling
- Need to parse JSON responses

### Option 2: Python SDK

**Pros:**
- Type hints and autocomplete
- Error handling built-in
- Pythonic interface

**Cons:**
- Python only

### Option 3: JavaScript/Node.js SDK

**Pros:**
- Easy web integration
- Promise-based
- Works in browser and Node.js

**Cons:**
- JavaScript/TypeScript only

---

## Python Integration

### Example 1: Simple Job Search

```python
import requests

# Job Server URL
API_URL = "http://localhost:8000"

def search_jobs(keyword, page=1, per_page=20):
    """Search for jobs"""
    response = requests.get(
        f"{API_URL}/jobs",
        params={
            'keyword': keyword,
            'page': page,
            'per_page': per_page
        }
    )
    return response.json()

# Use it
results = search_jobs("python developer")
print(f"Found {results['total']} jobs")

for job in results['jobs']:
    print(f"- {job['title']} at {job['company']}")
```

### Example 2: Get Job Details

```python
def get_job_details(job_id):
    """Get full job details including description"""
    response = requests.get(f"{API_URL}/jobs/{job_id}")
    if response.status_code == 404:
        return None
    return response.json()

# Use it
job = get_job_details(1)
if job:
    print(f"Title: {job['title']}")
    print(f"Company: {job['company']}")
    print(f"Description: {job['description'][:200]}...")
    print(f"Apply: {job['source_url']}")
```

### Example 3: Full Python Client Class

```python
# job_api_client.py
import requests
from typing import Optional, List, Dict

class JobAPIClient:
    """Client for Job Server API"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()

    def search_jobs(
        self,
        keyword: Optional[str] = None,
        location: Optional[str] = None,
        source: Optional[str] = None,
        remote_only: bool = False,
        page: int = 1,
        per_page: int = 20
    ) -> Dict:
        """Search for jobs"""
        params = {
            'page': page,
            'per_page': per_page,
            'remote_only': remote_only
        }
        if keyword:
            params['keyword'] = keyword
        if location:
            params['location'] = location
        if source:
            params['source'] = source

        response = self.session.get(f"{self.base_url}/jobs", params=params)
        response.raise_for_status()
        return response.json()

    def get_job(self, job_id: int, use_cache: bool = True) -> Dict:
        """Get job details"""
        response = self.session.get(
            f"{self.base_url}/jobs/{job_id}",
            params={'use_cache': use_cache}
        )
        if response.status_code == 404:
            raise ValueError(f"Job {job_id} not found")
        response.raise_for_status()
        return response.json()

    def scrape_jobs(
        self,
        keywords: Optional[str] = None,
        location: Optional[str] = None,
        sources: Optional[List[str]] = None,
        max_pages: int = 3
    ) -> Dict:
        """Trigger job scraping"""
        payload = {
            'keywords': keywords,
            'location': location,
            'sources': sources,
            'max_pages': max_pages
        }
        response = self.session.post(f"{self.base_url}/scrape", json=payload)
        response.raise_for_status()
        return response.json()

    def get_stats(self) -> Dict:
        """Get database statistics"""
        response = self.session.get(f"{self.base_url}/stats")
        response.raise_for_status()
        return response.json()

    def get_sources(self) -> Dict:
        """Get available job sources"""
        response = self.session.get(f"{self.base_url}/sources")
        response.raise_for_status()
        return response.json()

# Usage
client = JobAPIClient()

# Search
results = client.search_jobs(keyword="python", remote_only=True)
print(f"Found {results['total']} Python jobs")

# Get details
job = client.get_job(1)
print(job['title'])

# Scrape
stats = client.scrape_jobs(keywords="developer", max_pages=2)
print(f"Scraped {stats['total_new']} new jobs")

# Stats
stats = client.get_stats()
print(f"Total jobs: {stats['total_jobs']}")
```

---

## JavaScript/Node.js Integration

### Example 1: Node.js Client

```javascript
// jobApiClient.js
const axios = require('axios');

class JobAPIClient {
    constructor(baseURL = 'http://localhost:8000') {
        this.client = axios.create({ baseURL });
    }

    async searchJobs({ keyword, location, source, remotely, page = 1, perPage = 20 }) {
        const response = await this.client.get('/jobs', {
            params: {
                keyword,
                location,
                source,
                remote_only: remoteOnly,
                page,
                per_page: perPage
            }
        });
        return response.data;
    }

    async getJob(jobId, useCache = true) {
        const response = await this.client.get(`/jobs/${jobId}`, {
            params: { use_cache: useCache }
        });
        return response.data;
    }

    async scrapeJobs({ keywords, location, sources, maxPages = 3 }) {
        const response = await this.client.post('/scrape', {
            keywords,
            location,
            sources,
            max_pages: maxPages
        });
        return response.data;
    }

    async getStats() {
        const response = await this.client.get('/stats');
        return response.data;
    }
}

// Usage
const client = new JobAPIClient();

// Search jobs
const results = await client.searchJobs({ keyword: 'python', remoteOnly: true });
console.log(`Found ${results.total} jobs`);

// Get job details
const job = await client.getJob(1);
console.log(job.title);

// Scrape
const stats = await client.scrapeJobs({ keywords: 'developer', maxPages: 2 });
console.log(`Scraped ${stats.total_new} new jobs`);
```

### Example 2: Browser/React Integration

```javascript
// hooks/useJobs.js
import { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

export function useJobs(keyword, page = 1) {
    const [jobs, setJobs] = useState([]);
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchJobs() {
            setLoading(true);
            try {
                const response = await axios.get(`${API_URL}/jobs`, {
                    params: { keyword, page, per_page: 20 }
                });
                setJobs(response.data.jobs);
                setTotal(response.data.total);
            } catch (error) {
                console.error('Error fetching jobs:', error);
            } finally {
                setLoading(false);
            }
        }
        fetchJobs();
    }, [keyword, page]);

    return { jobs, total, loading };
}

// Component usage
function JobList() {
    const { jobs, total, loading } = useJobs('python developer', 1);

    if (loading) return <div>Loading...</div>;

    return (
        <div>
            <h2>Found {total} jobs</h2>
            {jobs.map(job => (
                <div key={job.id}>
                    <h3>{job.title}</h3>
                    <p>{job.company} - {job.location}</p>
                    <a href={job.source_url}>Apply</a>
                </div>
            ))}
        </div>
    );
}
```

---

## cURL Examples

### Get Jobs
```bash
# All jobs
curl "http://localhost:8000/jobs?page=1&per_page=20"

# Search Python jobs
curl "http://localhost:8000/jobs?keyword=python&page=1"

# Remote only
curl "http://localhost:8000/jobs?remote_only=true"

# Filter by source
curl "http://localhost:8000/jobs?source=remoteok"
```

### Get Job Details
```bash
curl "http://localhost:8000/jobs/1"
```

### Trigger Scraping
```bash
curl -X POST "http://localhost:8000/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": "python developer",
    "location": "Remote",
    "sources": ["remoteok", "remotive"],
    "max_pages": 3
  }'
```

### Get Statistics
```bash
curl "http://localhost:8000/stats"
```

---

## PHP Integration

```php
<?php
class JobAPIClient {
    private $baseURL;

    public function __construct($baseURL = 'http://localhost:8000') {
        $this->baseURL = $baseURL;
    }

    public function searchJobs($keyword, $page = 1, $perPage = 20) {
        $params = http_build_query([
            'keyword' => $keyword,
            'page' => $page,
            'per_page' => $perPage
        ]);

        $response = file_get_contents("{$this->baseURL}/jobs?{$params}");
        return json_decode($response, true);
    }

    public function getJob($jobId) {
        $response = file_get_contents("{$this->baseURL}/jobs/{$jobId}");
        return json_decode($response, true);
    }
}

// Usage
$client = new JobAPIClient();
$results = $client->searchJobs('python developer');
echo "Found {$results['total']} jobs\n";
?>
```

---

## Ruby Integration

```ruby
require 'net/http'
require 'json'

class JobAPIClient
  def initialize(base_url = 'http://localhost:8000')
    @base_url = base_url
  end

  def search_jobs(keyword:, page: 1, per_page: 20)
    uri = URI("#{@base_url}/jobs")
    uri.query = URI.encode_www_form({
      keyword: keyword,
      page: page,
      per_page: per_page
    })

    response = Net::HTTP.get_response(uri)
    JSON.parse(response.body)
  end

  def get_job(job_id)
    uri = URI("#{@base_url}/jobs/#{job_id}")
    response = Net::HTTP.get_response(uri)
    JSON.parse(response.body)
  end
end

# Usage
client = JobAPIClient.new
results = client.search_jobs(keyword: 'python developer')
puts "Found #{results['total']} jobs"
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process response |
| 404 | Not Found | Job doesn't exist |
| 429 | Rate Limit | Wait and retry |
| 500 | Server Error | Check logs, retry |
| 503 | Service Unavailable | Server down, retry later |

### Example Error Handling (Python)

```python
import requests
from requests.exceptions import RequestException

def safe_api_call(url, **kwargs):
    """Make API call with error handling"""
    try:
        response = requests.get(url, **kwargs)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return None  # Not found
        elif e.response.status_code == 429:
            print("Rate limit exceeded, waiting...")
            time.sleep(60)
            return safe_api_call(url, **kwargs)  # Retry
        else:
            raise

    except RequestException as e:
        print(f"Network error: {e}")
        return None

# Usage
result = safe_api_call("http://localhost:8000/jobs/999")
if result:
    print("Found job")
else:
    print("Job not found or error")
```

---

## Best Practices

### 1. Use Connection Pooling

```python
# Python
session = requests.Session()
session.get(f"{API_URL}/jobs")  # Reuse connection

# JavaScript
const client = axios.create({ baseURL: API_URL })
```

### 2. Cache Results

```python
from functools import lru_cache
import time

@lru_cache(maxsize=100)
def get_job_cached(job_id, cache_time=time.time() // 300):
    # Cache for 5 minutes (300 seconds)
    return requests.get(f"{API_URL}/jobs/{job_id}").json()
```

### 3. Handle Pagination

```python
def get_all_jobs(keyword):
    """Get all jobs across all pages"""
    all_jobs = []
    page = 1

    while True:
        result = client.search_jobs(keyword=keyword, page=page)
        all_jobs.extend(result['jobs'])

        if page >= result['total_pages']:
            break

        page += 1

    return all_jobs
```

### 4. Rate Limiting

```python
import time
from functools import wraps

def rate_limit(calls_per_second=2):
    """Rate limit decorator"""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

@rate_limit(calls_per_second=2)
def search_jobs(keyword):
    return client.search_jobs(keyword=keyword)
```

---

## Deployment

### Production Checklist

- [ ] Set `reload=False` in job_server.py
- [ ] Configure CORS allowed origins
- [ ] Use production ASGI server (Gunicorn + Uvicorn)
- [ ] Set up reverse proxy (Nginx)
- [ ] Enable HTTPS
- [ ] Add authentication/API keys
- [ ] Set up monitoring
- [ ] Configure logging
- [ ] Database backups

### Run in Production

```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn job_server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## Next Steps

1. **Start server**: `python job_server.py`
2. **Test API**: Visit http://localhost:8000/docs
3. **Choose integration**: Pick Python/JavaScript/etc.
4. **Copy example code**: Use examples above
5. **Customize**: Adapt to your needs

**Need help?** Check the interactive API docs at http://localhost:8000/docs
