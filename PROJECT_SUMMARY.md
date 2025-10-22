# Job Aggregation Platform - Project Summary

## Overview
A fully automated job aggregation platform that scrapes, filters, and serves Gen-Z targeted job listings (entry & mid-level positions) from multiple APIs. The platform runs 24/7 on Railway with a remote PostgreSQL database accessible from anywhere.

## Live Deployment
- **API URL**: https://your-railway-app.up.railway.app
- **GitHub**: https://github.com/mfish324/job-aggregation-api
- **Database**: Neon PostgreSQL (3GB free tier)
- **Current Jobs**: 1,710+ US-based positions

## Key Features

### 1. Multi-Source Job Scraping
- **Sources**: RemoteOK, Remotive, GitHub Jobs, Indeed (via RapidAPI), Authentic Jobs
- **Rate-Limited**: Respects API limits (60s-360s delays)
- **Deduplication**: MD5 hashing prevents duplicate listings

### 2. Gen-Z Targeted Auto-Scraper
- **10 Search Profiles**: Entry/mid-level tech, finance, data, marketing, design, sales
- **70+ Keywords**: "junior developer", "entry level analyst", "associate engineer", etc.
- **Smart Scheduling**:
  - Priority profiles every 6 hours
  - All profiles every 12 hours
  - Full search daily at 3 AM
- **Expected Output**: 400-1000 new jobs per day

### 3. US-Only Location Filtering
- **Filters 26%** of international jobs (UK, Canada, Europe, Asia, etc.)
- **Keeps**: All 50 US states, major cities, remote positions
- **Smart Detection**: Handles abbreviations, typos, edge cases

### 4. REST API (FastAPI)
**Endpoints**:
- `GET /health` - System status & job count
- `GET /jobs` - Search with keyword, location, remote filters
- `GET /jobs/{id}` - Full job details (on-demand fetching)
- `GET /stats` - Database statistics
- `POST /scrape` - Manual scraping trigger
- `GET /docs` - Interactive API documentation

**Features**:
- Pagination (page, per_page)
- CORS enabled for web apps
- OpenAPI/Swagger docs
- Lightweight storage with on-demand detail fetching

### 5. Cloud Infrastructure
- **Hosting**: Railway.app (free tier, auto-deploys from GitHub)
- **Database**: Neon PostgreSQL (remote, multi-user access)
- **Services**:
  - Web service (API server)
  - Worker service (auto-scraper) - *ready to deploy*

## Technology Stack
- **Backend**: Python 3.9+, FastAPI, SQLAlchemy
- **Database**: PostgreSQL (Neon), SQLite (local dev)
- **Scraping**: requests, BeautifulSoup4, RapidAPI
- **Scheduling**: schedule library
- **Deployment**: Railway (Procfile, nixpacks), Docker-ready
- **API Docs**: OpenAPI 3.0, Swagger UI

## Project Structure
```
Job_APIs/
├── job_server.py              # FastAPI REST API server
├── scheduled_scraper.py       # Gen-Z auto-scraper (10 profiles, 70+ keywords)
├── aggregator.py              # Multi-source job scraper
├── job_board_integration.py   # Database ORM & detail fetcher
├── location_filter.py         # US-only filtering logic
├── scrapers/                  # Individual API scrapers
│   ├── remoteok_scraper.py
│   ├── remotive_scraper.py
│   ├── github_scraper.py
│   ├── indeed_rapidapi_scraper.py
│   └── authenticjobs_scraper.py
├── Procfile                   # Railway process definitions
├── railway.json               # Railway deployment config
├── nixpacks.toml              # Build configuration
├── requirements.txt           # Python dependencies
└── .env                       # Environment variables (DATABASE_URL)
```

## Database Schema
**Table**: `job_listings`
- Essential fields: title, company, location, salary
- Metadata: source, source_url, posted_date, remote, job_type
- Preview: 500-char description excerpt
- Tracking: created_at, view_count, last_accessed
- Caching: cached_description (fetched on-demand)

## Usage

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable
DATABASE_URL=postgresql://your-neon-url

# Run API server
python job_server.py
# Visit: http://localhost:8001/docs

# Run auto-scraper
python scheduled_scraper.py
```

### Production (Railway)
1. Push to GitHub: `git push`
2. Railway auto-deploys in 1-2 minutes
3. Set `DATABASE_URL` environment variable in Railway dashboard
4. Add second service for auto-scraper: `python scheduled_scraper.py`

### API Examples
```bash
# Health check
curl https://your-app.up.railway.app/health

# Search Python jobs
curl https://your-app.up.railway.app/jobs?keyword=python&per_page=10

# Remote-only jobs
curl https://your-app.up.railway.app/jobs?remote_only=true

# Get job details
curl https://your-app.up.railway.app/jobs/123
```

## Key Accomplishments
✅ Multi-source job aggregation with deduplication
✅ Gen-Z targeted auto-scraper (70+ keyword searches)
✅ US-only location filtering (26% noise reduction)
✅ Remote PostgreSQL database (1,710+ jobs)
✅ RESTful API with FastAPI
✅ Railway deployment (24/7 uptime)
✅ GitHub integration (auto-deploy on push)
✅ Rate limiting & API compliance
✅ On-demand detail fetching (lightweight storage)

## Next Steps (Optional)
1. **Deploy Auto-Scraper**: Add second Railway service for `scheduled_scraper.py`
2. **Web Frontend**: Build job board UI consuming the REST API
3. **Email Alerts**: Notify users of new matching jobs
4. **Advanced Filters**: Experience level, salary range, skills matching
5. **Analytics Dashboard**: Track job market trends, popular companies
6. **API Authentication**: Add API keys for production use
7. **Webhooks**: Real-time job notifications to other platforms

## Costs
- **Railway**: Free tier (500 hours/month)
- **Neon PostgreSQL**: Free tier (3GB storage, 0.5GB RAM)
- **GitHub**: Free for public repos
- **Total**: $0/month

## Contact & Resources
- **GitHub Repo**: https://github.com/mfish324/job-aggregation-api
- **Railway Dashboard**: https://railway.app/dashboard
- **Neon Console**: https://console.neon.tech
- **API Docs**: https://your-app.up.railway.app/docs

---

**Built**: October 2025
**Status**: Production-ready, deployed, and operational
**License**: Open source
