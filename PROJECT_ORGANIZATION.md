# Project Organization

## Core Files (Root Directory)

### API & Server
- `job_server.py` - FastAPI REST API server (main entry point)
- `aggregator.py` - Coordinates all job scrapers
- `scheduled_scraper.py` - Automated Gen-Z job searches (runs every 6 hours)

### Scrapers
- `scrapers.py` - Job board scrapers (RemoteOK, Remotive, Indeed, etc.)
- `company_scrapers.py` - FAANG company career page scrapers (Google, Apple, Amazon, etc.)
- `usajobs_scraper.py` - Federal government job scraper
- `indeed_rapidapi_scraper.py` - Indeed scraper via RapidAPI

### Database & Models
- `models.py` - SQLAlchemy ORM models for main aggregator database
- `job_board_integration.py` - Lightweight job board database with on-demand fetching
- `location_filter.py` - US-only location filtering

### Utilities
- `trigger_scrape.py` - Command-line tool to trigger manual scraping
- `trigger_scrape.bat` - Windows batch file for easy Railway scraping
- `main.py` - Original CLI interface

### Configuration
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (not in git)
- `.env.example` - Environment variable template
- `.gitignore` - Git exclusion rules

### Deployment
- `Dockerfile` - Docker container configuration
- `docker-compose.yml` - Multi-container Docker setup
- `Procfile` - Railway process definitions
- `railway.json` - Railway deployment configuration
- `nixpacks.toml` - Nixpacks build configuration

## Documentation (`docs/`)

### Setup Guides (`docs/setup/`)
Essential setup and configuration guides:
- `API_QUICKSTART.md` - API usage guide
- `COMPANY_SCRAPERS_README.md` - Major tech company integration
- `GENZ_AUTO_SCRAPER_GUIDE.md` - Automated Gen-Z searches
- `US_FILTERING_GUIDE.md` - Location filtering setup
- `USAJOBS_INTEGRATION.md` - Federal jobs integration
- `USAJOBS_QUICK_START.md` - 10-minute USAJOBS setup
- `CLIENT_INTEGRATION_GUIDE.md` - Frontend integration guide

### Deployment Guides (`docs/deployment/`)
Production deployment documentation:
- `RAILWAY_DEPLOY.md` - Railway deployment guide
- `RAILWAY_MONITORING.md` - Monitor production instance
- `RAILWAY_WORKER_SETUP.md` - Background worker setup
- `RAILWAY_USAJOBS_SETUP.md` - Add USAJOBS to Railway
- `DOCKER_DEPLOY.md` - Docker containerization
- `DEPLOYMENT.md` - General deployment options

### Archived (`docs/archived/`)
Old or deprecated documentation

## Databases (Local Only - Not in Git)

- `jobs.db` - SQLite aggregator database (full job data)
- `job_board.db` - SQLite job board database (lightweight)

**Production**: Uses PostgreSQL on Railway/Neon

## Generated Files (Excluded from Git)

### Python
- `__pycache__/` - Python bytecode cache
- `*.pyc`, `*.pyo` - Compiled Python files

### Virtual Environments
- `Jobs-venv/` - Python virtual environment
- `.venv/`, `venv/` - Alternative venv names

### IDE
- `.vscode/` - VS Code settings
- `.idea/` - PyCharm settings
- `.claude/` - Claude Code configuration

### Exports
- `*.csv` - Job export CSV files
- `jobs_export_*.json` - Job export JSON files
- `*.html` - Generated HTML documentation

### Logs
- `*.log` - Application logs
- `scraper.log` - Scraper activity log

## File Count Summary

```
Root Python files: 11
Documentation files: 30+
Total lines of code: ~5,000+
Database tables: 2 (jobs, job_listings)
API endpoints: 15+
Job sources: 15+
```

## Quick Reference

### Start Local Server
```bash
python job_server.py
```

### Trigger Manual Scrape
```bash
python trigger_scrape.py --url https://your-railway-url
```

### Run Automated Scraper
```bash
python scheduled_scraper.py
```

### View API Docs
```
http://localhost:8001/docs
```

## Repository Structure

```
job-aggregation-api/
├── *.py                       # Core Python modules
├── requirements.txt           # Dependencies
├── .env                       # Environment (not in git)
├── .gitignore                 # Git exclusions
├── Procfile                   # Railway config
├── railway.json               # Railway settings
├── Dockerfile                 # Docker config
├── README.md                  # Main documentation
├── docs/                      # Documentation
│   ├── setup/                 # Setup guides
│   ├── deployment/            # Deployment guides
│   └── archived/              # Old docs
├── __pycache__/               # Python cache (ignored)
├── Jobs-venv/                 # Virtual env (ignored)
├── jobs.db                    # Local database (ignored)
└── job_board.db               # Local database (ignored)
```

## Best Practices

### Adding New Files
1. Python modules → root directory
2. Documentation → `docs/setup/` or `docs/deployment/`
3. Tests → `tests/` (if created)
4. Scripts → `scripts/` (if created)

### Excluded from Git
- Local databases (*.db)
- Environment files (.env)
- Python cache (__pycache__)
- Virtual environments (venv/)
- IDE settings (.vscode/, .idea/)
- Generated exports (*.csv, *.json)
- Logs (*.log)

### Included in Git
- All Python source files
- Documentation (*.md)
- Configuration (requirements.txt, Dockerfile, etc.)
- Deployment config (Procfile, railway.json)
- Utility scripts (trigger_scrape.py, .bat)

## Deployment Workflow

```
1. Make changes locally
2. Test with: python job_server.py
3. Commit: git add . && git commit -m "message"
4. Push: git push origin main
5. Railway auto-deploys
6. Monitor: Railway dashboard logs
```

---

**Maintained by**: LevelUp Careers Development Team
**Last Updated**: October 26, 2025
