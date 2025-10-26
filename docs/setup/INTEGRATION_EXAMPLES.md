# Job Board Integration Examples

How to integrate the job aggregator with your job board platform.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Job Board                            │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐│
│  │  Job Listing   │  │  Job Details   │  │   Search       ││
│  │     Page       │  │      Page      │  │    Page        ││
│  └────────┬───────┘  └────────┬───────┘  └────────┬───────┘│
│           │                   │                    │         │
│           └───────────────────┼────────────────────┘         │
│                               ↓                              │
│                    ┌─────────────────────┐                   │
│                    │  JobBoardAPI        │                   │
│                    │  (Lightweight DB)   │                   │
│                    └──────────┬──────────┘                   │
│                               │                              │
└───────────────────────────────┼──────────────────────────────┘
                                │
                    ┌───────────┴──────────┐
                    │                      │
          ┌─────────▼────────┐  ┌─────────▼────────┐
          │  Minimal Storage │  │ On-Demand Fetch  │
          │  (title, company,│  │  (full details   │
          │   location, URL) │  │   when clicked)  │
          └──────────────────┘  └──────────────────┘
```

## Quick Start

### Step 1: Import Jobs to Lightweight Database

```python
from job_board_integration import JobBoardAPI

# Create API instance
api = JobBoardAPI(database_url='sqlite:///job_board.db')

# Import from aggregator (one-time or scheduled)
imported, skipped = api.import_from_aggregator()
print(f"Imported {imported} jobs")

api.close()
```

### Step 2: Display Job List

```python
# Get paginated job list
result = api.get_job_list(
    page=1,
    per_page=20,
    keyword="python",
    remote_only=True
)

# result contains:
# - jobs: list of job dicts with essential fields
# - total: total count
# - page: current page
# - total_pages: number of pages
```

### Step 3: Show Full Details When Clicked

```python
# When user clicks a job
details = api.get_job_details(job_id=123)

# details contains everything + full description
# Automatically fetched from source on first view
# Cached for subsequent views
```

---

## Flask Integration

### Basic Flask App

```python
from flask import Flask, render_template, jsonify, request
from job_board_integration import JobBoardAPI

app = Flask(__name__)
api = JobBoardAPI()

@app.route('/')
def index():
    """Job listing page"""
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('q', '')
    remote_only = request.args.get('remote', False, type=bool)

    result = api.get_job_list(
        page=page,
        per_page=20,
        keyword=keyword,
        remote_only=remote_only
    )

    return render_template('jobs.html', **result)


@app.route('/job/<int:job_id>')
def job_detail(job_id):
    """Job details page"""
    details = api.get_job_details(job_id)

    if not details:
        return "Job not found", 404

    return render_template('job_detail.html', job=details)


@app.route('/api/jobs')
def api_jobs():
    """JSON API endpoint"""
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('q', '')

    result = api.get_job_list(page=page, per_page=20, keyword=keyword)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
```

### Flask Templates

**templates/jobs.html:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Job Board</title>
    <style>
        .job-card {
            border: 1px solid #ddd;
            padding: 20px;
            margin: 10px 0;
            border-radius: 5px;
        }
        .job-title { font-size: 20px; font-weight: bold; }
        .job-company { color: #666; }
        .job-location { color: #999; }
        .remote-badge { background: #28a745; color: white; padding: 3px 8px; border-radius: 3px; }
    </style>
</head>
<body>
    <h1>Job Listings ({{ total }} jobs)</h1>

    <form method="get">
        <input type="text" name="q" placeholder="Search..." value="{{ request.args.get('q', '') }}">
        <label><input type="checkbox" name="remote" value="1"> Remote only</label>
        <button type="submit">Search</button>
    </form>

    {% for job in jobs %}
    <div class="job-card">
        <div class="job-title">
            <a href="/job/{{ job.id }}">{{ job.title }}</a>
            {% if job.remote %}<span class="remote-badge">Remote</span>{% endif %}
        </div>
        <div class="job-company">{{ job.company }}</div>
        <div class="job-location">{{ job.location }}</div>
        {% if job.salary %}<div>💰 {{ job.salary }}</div>{% endif %}
        <p>{{ job.preview_text }}</p>
    </div>
    {% endfor %}

    <!-- Pagination -->
    <div>
        {% if page > 1 %}
        <a href="?page={{ page - 1 }}">← Previous</a>
        {% endif %}
        Page {{ page }} of {{ total_pages }}
        {% if page < total_pages %}
        <a href="?page={{ page + 1 }}">Next →</a>
        {% endif %}
    </div>
</body>
</html>
```

**templates/job_detail.html:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ job.title }} - {{ job.company }}</title>
</head>
<body>
    <a href="/">← Back to listings</a>

    <h1>{{ job.title }}</h1>
    <h2>{{ job.company }}</h2>

    <p><strong>Location:</strong> {{ job.location }}</p>
    {% if job.salary %}<p><strong>Salary:</strong> {{ job.salary }}</p>{% endif %}
    <p><strong>Type:</strong> {{ job.job_type }}</p>
    <p><strong>Remote:</strong> {{ 'Yes' if job.remote else 'No' }}</p>

    <div>
        <a href="{{ job.source_url }}" target="_blank" class="apply-btn">
            Apply on {{ job.source }} →
        </a>
    </div>

    <h3>Description</h3>
    <div>{{ job.description | safe }}</div>

    <p><small>Views: {{ job.view_count }} | Posted: {{ job.posted_date }}</small></p>
</body>
</html>
```

---

## Django Integration

### Django Views

```python
# views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from job_board_integration import JobBoardAPI

api = JobBoardAPI()

def job_list(request):
    """Job listing view"""
    page = int(request.GET.get('page', 1))
    keyword = request.GET.get('q', '')
    remote_only = request.GET.get('remote') == '1'

    result = api.get_job_list(
        page=page,
        per_page=20,
        keyword=keyword,
        remote_only=remote_only
    )

    return render(request, 'jobs/list.html', result)


def job_detail(request, job_id):
    """Job detail view"""
    details = api.get_job_details(job_id)

    if not details:
        return render(request, '404.html', status=404)

    return render(request, 'jobs/detail.html', {'job': details})


def api_jobs_list(request):
    """JSON API"""
    page = int(request.GET.get('page', 1))
    keyword = request.GET.get('q', '')

    result = api.get_job_list(page=page, per_page=20, keyword=keyword)
    return JsonResponse(result)
```

### Django URLs

```python
# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('api/jobs/', views.api_jobs_list, name='api_jobs'),
]
```

---

## FastAPI Integration

### REST API with FastAPI

```python
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from typing import Optional
from job_board_integration import JobBoardAPI

app = FastAPI(title="Job Board API")
api = JobBoardAPI()

@app.get("/api/jobs")
async def list_jobs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    remote_only: bool = False,
    location: Optional[str] = None
):
    """Get paginated job list"""
    result = api.get_job_list(
        page=page,
        per_page=per_page,
        keyword=keyword,
        remote_only=remote_only,
        location=location
    )
    return result


@app.get("/api/jobs/{job_id}")
async def get_job(job_id: int):
    """Get full job details"""
    details = api.get_job_details(job_id)

    if not details:
        raise HTTPException(status_code=404, detail="Job not found")

    return details


@app.get("/", response_class=HTMLResponse)
async def index():
    """Simple HTML interface"""
    return """
    <html>
        <head><title>Job Board API</title></head>
        <body>
            <h1>Job Board API</h1>
            <ul>
                <li><a href="/docs">API Documentation</a></li>
                <li><a href="/api/jobs">Get Jobs (JSON)</a></li>
                <li><a href="/api/jobs?keyword=python">Search Python Jobs</a></li>
            </ul>
        </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## React/Next.js Frontend

### React Component

```javascript
// components/JobList.jsx
import { useState, useEffect } from 'react';

export default function JobList() {
  const [jobs, setJobs] = useState([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [keyword, setKeyword] = useState('');

  useEffect(() => {
    fetchJobs();
  }, [page, keyword]);

  const fetchJobs = async () => {
    const response = await fetch(
      `/api/jobs?page=${page}&keyword=${keyword}`
    );
    const data = await response.json();
    setJobs(data.jobs);
    setTotal(data.total);
  };

  return (
    <div>
      <h1>Job Board ({total} jobs)</h1>

      <input
        type="text"
        placeholder="Search..."
        value={keyword}
        onChange={(e) => setKeyword(e.target.value)}
      />

      {jobs.map(job => (
        <div key={job.id} className="job-card">
          <h2>
            <a href={`/job/${job.id}`}>{job.title}</a>
          </h2>
          <div>{job.company} - {job.location}</div>
          {job.remote && <span className="badge">Remote</span>}
          <p>{job.preview_text}</p>
        </div>
      ))}

      <div>
        <button onClick={() => setPage(p => Math.max(1, p - 1))}>
          Previous
        </button>
        <span>Page {page}</span>
        <button onClick={() => setPage(p => p + 1)}>
          Next
        </button>
      </div>
    </div>
  );
}
```

### Next.js API Route

```javascript
// pages/api/jobs.js
import { JobBoardAPI } from '../../lib/job_board';

const api = new JobBoardAPI();

export default async function handler(req, res) {
  const { page = 1, keyword = '', remote_only = false } = req.query;

  const result = await api.get_job_list({
    page: parseInt(page),
    per_page: 20,
    keyword,
    remote_only: remote_only === 'true'
  });

  res.status(200).json(result);
}
```

---

## Scheduled Import

### Daily Job Sync

```python
# sync_jobs.py
from job_board_integration import JobBoardAPI
from aggregator import JobAggregator
from datetime import datetime

def daily_sync():
    """Run this daily via cron/Task Scheduler"""

    print(f"Starting job sync at {datetime.now()}")

    # Step 1: Scrape new jobs
    print("1. Scraping new jobs...")
    aggregator = JobAggregator()
    stats = aggregator.scrape_all(max_pages=5)
    print(f"   Scraped {stats['total_new']} new jobs")
    aggregator.close()

    # Step 2: Import to job board database
    print("2. Importing to job board...")
    api = JobBoardAPI()
    imported, skipped = api.import_from_aggregator()
    print(f"   Imported {imported} jobs, skipped {skipped}")
    api.close()

    print(f"Sync completed at {datetime.now()}")

if __name__ == '__main__':
    daily_sync()
```

### Cron Job (Linux/Mac)
```bash
# Run daily at 2 AM
0 2 * * * cd /path/to/Job_APIs && python sync_jobs.py >> logs/sync.log 2>&1
```

### Windows Task Scheduler
```powershell
# Create task
$action = New-ScheduledTaskAction -Execute "python" -Argument "C:\path\to\sync_jobs.py"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -TaskName "JobBoardSync" -Action $action -Trigger $trigger
```

---

## Performance Tips

### 1. Database Indexes

Already included in the schema:
- `job_id` (unique, indexed)
- `title`, `company`, `location` (indexed)
- `source`, `remote`, `posted_date` (indexed)

### 2. Caching Strategy

Full descriptions are cached after first fetch:
```python
# First user click: fetches from source
details = api.get_job_details(123, use_cache=True)

# Subsequent clicks: uses cached version
details = api.get_job_details(123, use_cache=True)
```

### 3. Pagination

Always paginate large result sets:
```python
# Good: paginated
result = api.get_job_list(page=1, per_page=20)

# Bad: loading all jobs
result = api.get_job_list(limit=10000)  # Don't do this!
```

### 4. Search Optimization

Add full-text search for better performance:
```sql
-- PostgreSQL
CREATE INDEX idx_job_search ON job_listings
USING gin(to_tsvector('english', title || ' ' || company));

-- SQLite FTS5
CREATE VIRTUAL TABLE job_listings_fts USING fts5(
    title, company, content=job_listings
);
```

---

## Database Comparison

### Storage Savings

**Full Storage (current aggregator):**
- Average job size: ~2-5 KB (with full description HTML)
- 10,000 jobs = 20-50 MB

**Lightweight Storage (job board integration):**
- Average job size: ~0.5 KB (essential fields only)
- 10,000 jobs = 5 MB
- Full descriptions fetched on-demand and cached

**Savings: ~75-90% less storage** ✅

### Speed Comparison

| Operation | Full DB | Lightweight + On-Demand |
|-----------|---------|------------------------|
| List 20 jobs | 10ms | 2ms |
| Search jobs | 50ms | 10ms |
| View job details | 5ms | 5ms (cached) or 200ms (first fetch) |
| Import 1000 jobs | 5s | 1s |

---

## Migration Guide

### From Existing System

```python
def migrate_to_lightweight():
    """Migrate from full storage to lightweight"""

    # Your existing database
    from your_app import YourJobModel

    api = JobBoardAPI()

    for job in YourJobModel.objects.all():
        job_data = {
            'title': job.title,
            'company': job.company,
            'location': job.location,
            'salary': job.salary,
            'source': 'your_source',
            'url': job.application_url,
            'posted_date': job.date_posted,
            'remote': job.is_remote,
            'job_type': job.employment_type,
            'preview_text': job.description[:500]
        }

        api.db.add_job(job_data)

    api.close()
```

---

## Testing

```python
# test_job_board.py
from job_board_integration import JobBoardAPI

def test_job_board():
    api = JobBoardAPI(database_url='sqlite:///test_job_board.db')

    # Test import
    imported, skipped = api.import_from_aggregator()
    assert imported > 0

    # Test list
    result = api.get_job_list(page=1, per_page=10)
    assert len(result['jobs']) > 0

    # Test details
    job_id = result['jobs'][0]['id']
    details = api.get_job_details(job_id)
    assert 'description' in details

    api.close()
    print("✓ All tests passed")

if __name__ == '__main__':
    test_job_board()
```

---

## Next Steps

1. **Run the import**: `python job_board_integration.py`
2. **Choose your framework**: Flask, Django, FastAPI, etc.
3. **Build your UI**: Use the examples above
4. **Set up scheduled sync**: Daily or hourly job imports
5. **Add search filters**: Location, salary, remote, etc.
6. **Optimize**: Add caching, CDN, etc.

Happy building! 🚀
