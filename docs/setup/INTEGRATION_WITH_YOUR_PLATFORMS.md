# Integrating Gen-Z Job Scraper with Your Platforms

Quick guide to integrate this job aggregator with your existing job search platforms.

## Your Setup

You have **TWO job search platforms** that need access to these aggregated jobs:

1. **Django Platform** (running on port 8000)
2. **Another Platform** (language unknown)

Both can now access the **Job Aggregator API** on port 8001.

---

## Integration Architecture

```
┌─────────────────────────┐
│   Django Job Platform   │
│      (Port 8000)        │
└───────────┬─────────────┘
            │
            │ HTTP Requests
            ▼
┌─────────────────────────┐     ┌──────────────────────┐
│   Job Aggregator API    │────▶│  Gen-Z Auto Scraper  │
│      (Port 8001)        │     │  (Background Task)   │
└───────────┬─────────────┘     └──────────────────────┘
            │                              │
            │                              │
┌───────────▼─────────────┐               │
│  Another Platform       │               │
│  (Your 2nd Platform)    │               │
└─────────────────────────┘               │
                                          │
                              ┌───────────▼──────────┐
                              │   Job Board DB       │
                              │   1,710+ Jobs        │
                              └──────────────────────┘
```

---

## For Your Django Platform

### Add to Django Settings

```python
# settings.py
JOB_AGGREGATOR_API = "http://localhost:8001"
```

### Create Django Service Class

```python
# services/job_aggregator.py
import requests
from django.conf import settings

class JobAggregatorService:
    """Service to interact with the job aggregation API"""

    def __init__(self):
        self.base_url = settings.JOB_AGGREGATOR_API

    def get_jobs(self, keyword=None, remote_only=False, page=1, per_page=20):
        """
        Fetch jobs from aggregator

        Args:
            keyword: Search keyword (e.g., 'python developer')
            remote_only: Filter for remote jobs only
            page: Page number
            per_page: Jobs per page

        Returns:
            dict with jobs list and pagination info
        """
        params = {
            'page': page,
            'per_page': per_page
        }
        if keyword:
            params['keyword'] = keyword
        if remote_only:
            params['remote_only'] = True

        response = requests.get(f"{self.base_url}/jobs", params=params)
        response.raise_for_status()
        return response.json()

    def get_job_details(self, job_id):
        """Get full details for a specific job"""
        response = requests.get(f"{self.base_url}/jobs/{job_id}")
        response.raise_for_status()
        return response.json()

    def trigger_genz_search(self, profile='priority'):
        """
        Trigger Gen-Z targeted job search

        Args:
            profile: 'priority', 'all', or specific profile name
        """
        if profile == 'priority':
            endpoint = '/genz/search-priority'
        elif profile == 'all':
            endpoint = '/genz/search-all'
        else:
            endpoint = f'/genz/search/{profile}'

        response = requests.post(f"{self.base_url}{endpoint}")
        response.raise_for_status()
        return response.json()

    def get_stats(self):
        """Get aggregator statistics"""
        response = requests.get(f"{self.base_url}/stats")
        response.raise_for_status()
        return response.json()
```

### Use in Django Views

```python
# views.py
from django.shortcuts import render
from django.http import JsonResponse
from .services.job_aggregator import JobAggregatorService

aggregator = JobAggregatorService()

def job_listing(request):
    """Display job listings from aggregator"""
    keyword = request.GET.get('keyword', '')
    page = int(request.GET.get('page', 1))

    # Fetch from aggregator
    result = aggregator.get_jobs(
        keyword=keyword,
        remote_only=True,
        page=page,
        per_page=20
    )

    context = {
        'jobs': result['jobs'],
        'total': result['total'],
        'page': result['page'],
        'total_pages': result['total_pages']
    }
    return render(request, 'jobs/listing.html', context)

def job_detail(request, job_id):
    """Display full job details"""
    job = aggregator.get_job_details(job_id)
    return render(request, 'jobs/detail.html', {'job': job})

def refresh_jobs(request):
    """Trigger Gen-Z job search (admin only)"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    result = aggregator.trigger_genz_search('priority')
    return JsonResponse(result)

def job_stats(request):
    """Show job statistics"""
    stats = aggregator.get_stats()
    return render(request, 'jobs/stats.html', {'stats': stats})
```

### Django Template Example

```html
<!-- templates/jobs/listing.html -->
<div class="job-listings">
    <h2>Gen-Z Jobs ({{ total }} total)</h2>

    <!-- Search Form -->
    <form method="get">
        <input type="text" name="keyword" placeholder="Search jobs..."
               value="{{ request.GET.keyword }}">
        <button type="submit">Search</button>
    </form>

    <!-- Job List -->
    {% for job in jobs %}
    <div class="job-card">
        <h3>{{ job.title }}</h3>
        <p class="company">{{ job.company }}</p>
        <p class="location">{{ job.location }}</p>
        {% if job.salary %}
        <p class="salary">{{ job.salary }}</p>
        {% endif %}
        <p class="meta">
            Posted: {{ job.posted_date }}
            {% if job.remote %}<span class="badge">Remote</span>{% endif %}
        </p>
        <a href="{% url 'job_detail' job.id %}" class="btn">View Details</a>
    </div>
    {% endfor %}

    <!-- Pagination -->
    <div class="pagination">
        {% if page > 1 %}
        <a href="?page={{ page|add:"-1" }}&keyword={{ request.GET.keyword }}">Previous</a>
        {% endif %}
        Page {{ page }} of {{ total_pages }}
        {% if page < total_pages %}
        <a href="?page={{ page|add:"1" }}&keyword={{ request.GET.keyword }}">Next</a>
        {% endif %}
    </div>
</div>
```

### Django Management Command (Optional)

Create a management command to trigger scraping:

```python
# management/commands/scrape_genz_jobs.py
from django.core.management.base import BaseCommand
from myapp.services.job_aggregator import JobAggregatorService

class Command(BaseCommand):
    help = 'Trigger Gen-Z job scraping'

    def add_arguments(self, parser):
        parser.add_argument(
            '--profile',
            type=str,
            default='priority',
            help='Search profile to run (priority, all, or profile name)'
        )

    def handle(self, *args, **options):
        aggregator = JobAggregatorService()
        profile = options['profile']

        self.stdout.write(f'Triggering Gen-Z search: {profile}')
        result = aggregator.trigger_genz_search(profile)

        self.stdout.write(self.style.SUCCESS(
            f"Search started: {result['status']}"
        ))
```

Usage:
```bash
python manage.py scrape_genz_jobs --profile=priority
```

---

## For Your Other Platform (JavaScript/Node.js)

### Node.js Service Class

```javascript
// services/jobAggregator.js
const axios = require('axios');

class JobAggregatorService {
  constructor(baseUrl = 'http://localhost:8001') {
    this.baseUrl = baseUrl;
    this.client = axios.create({
      baseURL: this.baseUrl,
      timeout: 10000
    });
  }

  async getJobs({ keyword, remoteOnly, page = 1, perPage = 20 }) {
    const response = await this.client.get('/jobs', {
      params: {
        keyword,
        remote_only: remoteOnly,
        page,
        per_page: perPage
      }
    });
    return response.data;
  }

  async getJobDetails(jobId) {
    const response = await this.client.get(`/jobs/${jobId}`);
    return response.data;
  }

  async triggerGenZSearch(profile = 'priority') {
    let endpoint;
    if (profile === 'priority') {
      endpoint = '/genz/search-priority';
    } else if (profile === 'all') {
      endpoint = '/genz/search-all';
    } else {
      endpoint = `/genz/search/${profile}`;
    }

    const response = await this.client.post(endpoint);
    return response.data;
  }

  async getStats() {
    const response = await this.client.get('/stats');
    return response.data;
  }
}

module.exports = JobAggregatorService;
```

### Express.js Routes

```javascript
// routes/jobs.js
const express = require('express');
const router = express.Router();
const JobAggregatorService = require('../services/jobAggregator');

const aggregator = new JobAggregatorService();

// Job listing page
router.get('/jobs', async (req, res) => {
  try {
    const { keyword, page = 1 } = req.query;

    const result = await aggregator.getJobs({
      keyword,
      remoteOnly: true,
      page: parseInt(page),
      perPage: 20
    });

    res.render('jobs/listing', {
      jobs: result.jobs,
      total: result.total,
      page: result.page,
      totalPages: result.total_pages
    });
  } catch (error) {
    res.status(500).send('Error fetching jobs');
  }
});

// Job details page
router.get('/jobs/:id', async (req, res) => {
  try {
    const job = await aggregator.getJobDetails(req.params.id);
    res.render('jobs/detail', { job });
  } catch (error) {
    res.status(500).send('Error fetching job details');
  }
});

// Trigger Gen-Z search (API endpoint)
router.post('/api/jobs/refresh', async (req, res) => {
  try {
    const profile = req.body.profile || 'priority';
    const result = await aggregator.triggerGenZSearch(profile);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: 'Failed to trigger search' });
  }
});

module.exports = router;
```

### React Component Example

```jsx
// components/JobListings.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const JobListings = () => {
  const [jobs, setJobs] = useState([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [keyword, setKeyword] = useState('');

  useEffect(() => {
    fetchJobs();
  }, [page, keyword]);

  const fetchJobs = async () => {
    try {
      const response = await axios.get('http://localhost:8001/jobs', {
        params: {
          keyword,
          remote_only: true,
          page,
          per_page: 20
        }
      });

      setJobs(response.data.jobs);
      setTotal(response.data.total);
    } catch (error) {
      console.error('Error fetching jobs:', error);
    }
  };

  const triggerSearch = async () => {
    try {
      await axios.post('http://localhost:8001/genz/search-priority');
      alert('Gen-Z job search started in background!');
    } catch (error) {
      console.error('Error triggering search:', error);
    }
  };

  return (
    <div className="job-listings">
      <h2>Gen-Z Jobs ({total} total)</h2>

      <div className="controls">
        <input
          type="text"
          placeholder="Search jobs..."
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
        />
        <button onClick={triggerSearch}>Refresh Jobs</button>
      </div>

      {jobs.map(job => (
        <div key={job.id} className="job-card">
          <h3>{job.title}</h3>
          <p>{job.company} - {job.location}</p>
          {job.salary && <p className="salary">{job.salary}</p>}
          {job.remote && <span className="badge">Remote</span>}
          <a href={`/jobs/${job.id}`}>View Details</a>
        </div>
      ))}

      <div className="pagination">
        {page > 1 && (
          <button onClick={() => setPage(page - 1)}>Previous</button>
        )}
        <span>Page {page}</span>
        <button onClick={() => setPage(page + 1)}>Next</button>
      </div>
    </div>
  );
};

export default JobListings;
```

---

## Scheduled Refresh (Recommended)

### Django Celery Task

```python
# tasks.py
from celery import shared_task
from .services.job_aggregator import JobAggregatorService

@shared_task
def refresh_genz_jobs():
    """Celery task to refresh Gen-Z jobs periodically"""
    aggregator = JobAggregatorService()
    result = aggregator.trigger_genz_search('priority')
    return result

# settings.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'refresh-genz-jobs': {
        'task': 'myapp.tasks.refresh_genz_jobs',
        'schedule': crontab(hour='*/6'),  # Every 6 hours
    },
}
```

### Node.js Cron Job

```javascript
// scheduledTasks.js
const cron = require('node-cron');
const JobAggregatorService = require('./services/jobAggregator');

const aggregator = new JobAggregatorService();

// Run Gen-Z search every 6 hours
cron.schedule('0 */6 * * *', async () => {
  console.log('Triggering Gen-Z job search...');
  try {
    const result = await aggregator.triggerGenZSearch('priority');
    console.log('Search started:', result);
  } catch (error) {
    console.error('Error triggering search:', error);
  }
});

console.log('Scheduled tasks initialized');
```

---

## Testing the Integration

### Test from Django Shell

```python
python manage.py shell

>>> from myapp.services.job_aggregator import JobAggregatorService
>>> aggregator = JobAggregatorService()
>>>
>>> # Get jobs
>>> jobs = aggregator.get_jobs(keyword='python', per_page=5)
>>> print(f"Found {jobs['total']} jobs")
>>>
>>> # Trigger search
>>> result = aggregator.trigger_genz_search('priority')
>>> print(result)
>>>
>>> # Get stats
>>> stats = aggregator.get_stats()
>>> print(stats)
```

### Test from Command Line

```bash
# Get jobs
curl "http://localhost:8001/jobs?keyword=python&per_page=5"

# Trigger Gen-Z search
curl -X POST http://localhost:8001/genz/search-priority

# Get stats
curl http://localhost:8001/stats
```

---

## Summary

Your platforms can now:

✅ **Fetch jobs** from the aggregator API
✅ **Search jobs** by keyword, location, remote status
✅ **Trigger Gen-Z searches** on-demand
✅ **Get job details** with full descriptions
✅ **View statistics** about aggregated jobs
✅ **Schedule automatic refreshes** via cron/celery

The aggregator runs independently and serves both platforms via REST API on port 8001!
