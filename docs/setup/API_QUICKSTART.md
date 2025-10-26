# Job Server API - Quick Start Guide

The Job Server API is now running and ready to integrate with your other job search platforms!

## Server Information

- **Base URL**: `http://localhost:8001`
- **API Documentation**: `http://localhost:8001/docs` (Interactive Swagger UI)
- **Health Check**: `http://localhost:8001/health`

## Starting the Server

### Method 1: Direct Python
```bash
python job_server.py
```

### Method 2: Docker Compose (Recommended for Production)
```bash
docker-compose up -d
```

The server will start on port **8001** (to avoid conflicts with your Django server on port 8000).

---

## Quick Integration Examples

### 1. Get Job Listings (Paginated)

**Request:**
```bash
curl "http://localhost:8001/jobs?page=1&per_page=20"
```

**Response:**
```json
{
  "jobs": [...],
  "total": 1710,
  "page": 1,
  "per_page": 20,
  "total_pages": 86
}
```

### 2. Search Jobs by Keyword

**Request:**
```bash
curl "http://localhost:8001/jobs?keyword=python&per_page=10"
```

### 3. Filter Remote Jobs Only

**Request:**
```bash
curl "http://localhost:8001/jobs?remote_only=true"
```

### 4. Get Full Job Details

**Request:**
```bash
curl "http://localhost:8001/jobs/1"
```

**Response includes:**
- Full description (fetched on-demand from source)
- All job metadata
- View count

### 5. Get Statistics

**Request:**
```bash
curl "http://localhost:8001/stats"
```

**Response:**
```json
{
  "total_jobs": 1710,
  "remote_jobs": 1700,
  "with_salary": 794,
  "by_source": {
    "remotive": 1602,
    "remoteok": 97,
    "authenticjobs": 10,
    "github": 1
  }
}
```

### 6. Get Available Sources

**Request:**
```bash
curl "http://localhost:8001/sources"
```

---

## Integration with Your Platforms

### For Your Django Job Board

Add this to your Django views:

```python
import requests

def get_jobs_from_aggregator(keyword=None, page=1, per_page=20):
    """Fetch jobs from the job aggregator API"""
    url = "http://localhost:8001/jobs"
    params = {
        "page": page,
        "per_page": per_page
    }
    if keyword:
        params["keyword"] = keyword

    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def get_job_details(job_id):
    """Fetch full job details including description"""
    url = f"http://localhost:8001/jobs/{job_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
```

### For Your Other Job Search Platform

If it's a JavaScript/Node.js application:

```javascript
// Fetch jobs
async function getJobs(keyword = null, page = 1, perPage = 20) {
  const params = new URLSearchParams({ page, per_page: perPage });
  if (keyword) params.append('keyword', keyword);

  const response = await fetch(`http://localhost:8001/jobs?${params}`);
  return await response.json();
}

// Get job details
async function getJobDetails(jobId) {
  const response = await fetch(`http://localhost:8001/jobs/${jobId}`);
  return await response.json();
}
```

---

## Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/jobs` | GET | List jobs (paginated, with filters) |
| `/jobs/{id}` | GET | Get full job details |
| `/stats` | GET | Database statistics |
| `/sources` | GET | Available job sources |
| `/scrape` | POST | Trigger new scraping |
| `/import` | POST | Import from aggregator DB |
| `/docs` | GET | Interactive API documentation |

---

## Query Parameters for `/jobs`

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `page` | int | Page number (default: 1) | `page=2` |
| `per_page` | int | Items per page (default: 20, max: 100) | `per_page=50` |
| `keyword` | string | Search in title, company, description | `keyword=python` |
| `remote_only` | boolean | Filter remote jobs only | `remote_only=true` |
| `location` | string | Filter by location | `location=New York` |

---

## Current Database Status

- **Total Jobs**: 1,710
- **Remote Jobs**: 1,700 (99.4%)
- **Jobs with Salary Info**: 794 (46.4%)
- **Sources**:
  - Remotive: 1,602 jobs
  - RemoteOK: 97 jobs
  - Authentic Jobs: 10 jobs
  - GitHub: 1 job
  - Indeed: Ready (currently rate-limited, resets monthly)

---

## Testing the API

### Option 1: Browser
Visit `http://localhost:8001/docs` for an interactive Swagger UI where you can test all endpoints.

### Option 2: cURL
```bash
# Health check
curl http://localhost:8001/health

# Get first page of jobs
curl "http://localhost:8001/jobs?page=1&per_page=5"

# Search for Python jobs
curl "http://localhost:8001/jobs?keyword=python"

# Get statistics
curl http://localhost:8001/stats
```

### Option 3: Python Requests
```python
import requests

# Get jobs
response = requests.get("http://localhost:8001/jobs", params={"page": 1, "per_page": 5})
jobs = response.json()
print(f"Found {jobs['total']} jobs")

# Get job details
response = requests.get("http://localhost:8001/jobs/1")
job = response.json()
print(f"Job: {job['title']} at {job['company']}")
```

---

## Production Deployment

### Environment Variables

Create a `.env` file:
```bash
# API Configuration
API_PORT=8001

# Database
DATABASE_URL=sqlite:///job_board.db

# Optional: RapidAPI for Indeed
RAPIDAPI_KEY=your_key_here
RAPIDAPI_INDEED_HOST=indeed-jobs-api.p.rapidapi.com
```

### Docker Deployment

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## Next Steps

1. **Test the API**: Visit `http://localhost:8001/docs`
2. **Integrate with your platforms**: Use the examples above
3. **Set up periodic scraping**: Add a cron job to POST to `/scrape`
4. **Monitor**: Check `/stats` endpoint for database health
5. **Scale**: Use Docker for consistent deployment

## Need Help?

- Full integration guide: See [CLIENT_INTEGRATION_GUIDE.md](CLIENT_INTEGRATION_GUIDE.md)
- Docker deployment: See [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md)
- API documentation: Visit `http://localhost:8001/docs` when server is running

---

**Your job aggregator is ready to serve jobs to all your platforms!**
