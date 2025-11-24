# Job Aggregation API

**Official job scraping API for LevelUp Careers** - A Gen-Z focused job board featuring 15,000+ positions from tech companies, remote job boards, and federal government.

[![Railway Deployed](https://img.shields.io/badge/Railway-Deployed-success)](https://railway.app)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)](https://fastapi.tiangolo.com)

---

## 🚀 Quick Start

### For Railway (Production)

The Job_APIs is already deployed on Railway. To add new features:

```bash
# Make your changes, commit and push
git add .
git commit -m "Your changes"
git push

# Railway auto-deploys from main branch
```

**Environment Variables Needed in Railway**:
- `DATABASE_URL` - PostgreSQL connection string (auto-provided by Railway)
- `USAJOBS_API_KEY` - Free API key from [developer.usajobs.gov](https://developer.usajobs.gov/APIRequest/Index)
- `USAJOBS_USER_AGENT` - Your contact info: `LevelUpCareers/1.0 (email@example.com)`

### For Local Development

```bash
# Clone and setup
git clone https://github.com/mfish324/job-aggregation-api.git
cd job-aggregation-api

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Add your API keys to .env

# Start server
python job_server.py
```

Server runs at: `http://localhost:8001`

---

## 📊 Job Sources

### Job Boards (No API Key Required)
- **RemoteOK** - Remote tech jobs
- **Remotive** - Remote positions across all fields
- **We Work Remotely** - Premium remote jobs
- **Authentic Jobs** - Design and creative positions

### Company Career Pages
- **Google** - All Google teams (Cloud, Android, Search, etc.)
- **Amazon** - Amazon and AWS positions
- **Apple** - Hardware, software, retail
- **Microsoft** - Azure, Office, Windows, Gaming
- **Meta** - Facebook, Instagram, WhatsApp
- **Tesla** - Automotive, energy, manufacturing
obs
### Government Jobs (Requires Free API Key)
- **USAJOBS** - 20,000+ federal government positions
  - Department of Defense, NASA, FBI, CIA, etc.
  - Entry-level to mid-level (GS-5 to GS-11 equivalent)
  - Salary filtered: $35K-$95K (entry-level focused)

### Optional Premium APIs
- **Indeed** (via RapidAPI) - General job search
- **GitHub Jobs** (with token) - Developer positions

**Total**: ~15,000-20,000 active jobs across all sources

---

## 🎯 Gen-Z Features

### Automated Gen-Z Job Searches

The system automatically searches for Gen-Z relevant positions every 6 hours:

**Search Profiles**:
- `entry_tech` - Junior developer, entry-level software engineer, IT specialist
- `entry_finance` - Financial analyst, accountant, budget analyst
- `entry_data` - Data analyst, business analyst
- `entry_marketing` - Marketing coordinator, social media manager
- `entry_design` - UX designer, graphic designer
- `mid_tech` - Software engineer, DevOps, cybersecurity
- And more...

**71 targeted keywords** across 10 profiles, focusing on entry-level and early-career positions.

### US-Only Filtering

All jobs are automatically filtered to ensure they're US-based:
- 50 US states recognized
- Major US cities validated
- International locations rejected
- Remote jobs (US-based companies) included

---

## 🔌 API Endpoints

### Job Search
```bash
GET /jobs?keyword=software&location=remote&limit=50
```

### Trigger Scraping
```bash
POST /scrape
{
  "keywords": "python developer",
  "sources": ["remoteok", "usajobs"],
  "max_pages": 5
}
```

### Gen-Z Automated Searches
```bash
# Priority profiles (faster)
POST /genz/search-priority

# All profiles (comprehensive)
POST /genz/search-all

# Specific profile
POST /genz/search/entry_tech
```

### Statistics
```bash
GET /stats
# Returns job counts by source, recent activity, etc.
```

### Available Sources
```bash
GET /sources
# Lists all job sources and their active status
```

**Full API Documentation**: See [docs/setup/API_QUICKSTART.md](docs/setup/API_QUICKSTART.md)

---

## 📁 Project Structure

```
job-aggregation-api/
├── job_server.py              # FastAPI server (main entry point)
├── aggregator.py              # Job scraper coordinator
├── scheduled_scraper.py       # Gen-Z automated searches
├── scrapers.py                # Job board scrapers
├── company_scrapers.py        # FAANG career page scrapers
├── usajobs_scraper.py         # Federal government jobs
├── location_filter.py         # US-only filtering
├── models.py                  # Database models
├── trigger_scrape.py          # Manual scraping trigger
├── requirements.txt           # Python dependencies
├── railway.json               # Railway configuration
├── Procfile                   # Railway startup command
└── docs/                      # Documentation
    ├── setup/                 # Setup guides
    ├── deployment/            # Deployment guides
    └── archived/              # Old documentation
```

---

## 📚 Documentation

### Essential Guides
- **[USAJOBS Integration](docs/setup/USAJOBS_INTEGRATION.md)** - Federal government jobs setup
- **[USAJOBS Quick Start](docs/setup/USAJOBS_QUICK_START.md)** - 10-minute USAJOBS setup
- **[Railway USAJOBS Setup](docs/setup/RAILWAY_USAJOBS_SETUP.md)** - Add USAJOBS to Railway

### Setup & Configuration
- **[API Quick Start](docs/setup/API_QUICKSTART.md)** - API usage guide
- **[Gen-Z Auto Scraper](docs/setup/GENZ_AUTO_SCRAPER_GUIDE.md)** - Automated searches
- **[US Filtering Guide](docs/setup/US_FILTERING_GUIDE.md)** - Location filtering
- **[Adding Sources](docs/setup/ADDING_SOURCES.md)** - How to add new job sources
- **[Company Scrapers](docs/setup/COMPANY_SCRAPERS_README.md)** - FAANG integration

### Deployment
- **[Railway Deploy](docs/deployment/RAILWAY_DEPLOY.md)** - Railway deployment guide
- **[Railway Monitoring](docs/deployment/RAILWAY_MONITORING.md)** - Monitor production
- **[Railway Worker Setup](docs/deployment/RAILWAY_WORKER_SETUP.md)** - Background workers
- **[Docker Deploy](docs/deployment/DOCKER_DEPLOY.md)** - Docker containerization

---

## 🔧 Configuration

### Required Environment Variables

```bash
# Database (auto-provided by Railway)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# USAJOBS (required for federal jobs)
USAJOBS_API_KEY=your_key_from_developer_usajobs_gov
USAJOBS_USER_AGENT=LevelUpCareers/1.0 (your_email@example.com)
```

### Optional API Keys

```bash
# Indeed (via RapidAPI)
RAPIDAPI_KEY=your_rapidapi_key
RAPIDAPI_INDEED_HOST=indeed-jobs-api.p.rapidapi.com

# GitHub Jobs
GITHUB_TOKEN=your_github_personal_access_token

# Adzuna
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_APP_KEY=your_adzuna_app_key
```

**Get Free API Keys**:
- USAJOBS: https://developer.usajobs.gov/APIRequest/Index (instant)
- RapidAPI: https://rapidapi.com/ (free tier: 100 requests/month)
- GitHub: https://github.com/settings/tokens (unlimited for public repos)
- Adzuna: https://developer.adzuna.com/ (free tier: 100 requests/month)

---

## 🚀 Deployment

### Railway (Current Production)

```bash
# Already deployed! Just push to GitHub:
git push

# Railway auto-deploys from main branch
```

**Railway Dashboard**: https://railway.app/dashboard

### Docker (Alternative)

```bash
# Build
docker build -t job-api .

# Run
docker run -p 8001:8001 --env-file .env job-api
```

### Traditional Server

```bash
# Install dependencies
pip install -r requirements.txt

# Run with Gunicorn (production)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker job_server:app --bind 0.0.0.0:8001
```

---

## 🤝 Integration with LevelUp Careers

The Job_APIs integrates seamlessly with the Next.js job board:

1. **Job_APIs** (this repo) scrapes and aggregates jobs
2. **LevelUp Careers** frontend fetches jobs via API
3. Users see unified job listings from all sources

**Integration Guide**: [docs/setup/CLIENT_INTEGRATION_GUIDE.md](docs/setup/CLIENT_INTEGRATION_GUIDE.md)

---

## 📈 Performance

- **Job Count**: 15,000-20,000 active jobs
- **Update Frequency**: Every 6 hours (automated)
- **API Response Time**: <500ms average
- **Rate Limiting**: Respectful to all sources
- **Caching**: 24-hour job cache to reduce API calls

---

## 🛠️ Troubleshooting

### Common Issues

**"USAJOBS not active"**
- Add `USAJOBS_API_KEY` to Railway environment variables
- Restart Railway service

**"No jobs found"**
- Trigger manual scrape: `curl -X POST https://your-app.railway.app/genz/search-priority`
- Check Railway logs for errors
- Verify API keys are set

**"Rate limit exceeded"**
- Wait 1 minute (most APIs: 60 requests/hour)
- USAJOBS: 10 requests/minute
- Automated scraper respects all rate limits

**Full Troubleshooting Guide**: [docs/setup/TROUBLESHOOTING.md](docs/setup/TROUBLESHOOTING.md)

---

## 📊 Monitoring

### Check System Health

```bash
# Get statistics
curl https://your-app.railway.app/stats

# View sources status
curl https://your-app.railway.app/sources

# Check recent jobs
curl https://your-app.railway.app/jobs?limit=10
```

### Railway Logs

View real-time logs in Railway dashboard to monitor:
- Scraping activity
- API errors
- Job additions
- Rate limiting

**Monitoring Guide**: [docs/deployment/RAILWAY_MONITORING.md](docs/deployment/RAILWAY_MONITORING.md)

---

## 🤝 Contributing

This is a private project for LevelUp Careers. For internal development:

1. Create a feature branch
2. Make your changes
3. Test locally
4. Push to GitHub
5. Railway auto-deploys

---

## 📝 License

Private - LevelUp Careers Internal Project

---

## 🔗 Links

- **Railway Dashboard**: https://railway.app/dashboard
- **USAJOBS API Docs**: https://developer.usajobs.gov/
- **Repository**: https://github.com/mfish324/job-aggregation-api

---

**Last Updated**: October 25, 2025
**Status**: Production-ready on Railway
**Maintainer**: LevelUp Careers Development Team
