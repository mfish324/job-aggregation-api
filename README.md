# Job Aggregation Platform

A comprehensive job scraping and aggregation system that pulls job listings from multiple public sources.

## Features

- Aggregates jobs from 10+ sources including:
  - Adzuna API
  - GitHub Jobs
  - RemoteOK
  - We Work Remotely
  - Remotive
  - Authentic Jobs
  - Stack Overflow Jobs
  - AngelList
  - CrunchBoard (TechCrunch)
  - Indeed RSS feeds

- Automatic deduplication based on job title, company, and location
- Normalized data structure across all sources
- SQLite database storage with full-text search capability
- Rate limiting and retry logic
- Export to CSV/JSON

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Most sources work without API keys. Optional keys:
- Adzuna: Register at https://developer.adzuna.com/
- GitHub: Create personal access token for higher rate limits

## Usage

```bash
# Scrape all sources
python main.py

# Scrape specific sources
python main.py --sources adzuna github remoteok

# Search for specific keywords
python main.py --keywords "python developer"

# Specify location
python main.py --location "remote"

# Export results
python main.py --export jobs_export.csv
```

## Data Schema

Each job listing includes:
- Title
- Company
- Location
- Description
- URL
- Source
- Posted date
- Job type (full-time, contract, etc.)
- Salary (when available)
- Tags/skills

## Legal & Ethics

This tool only scrapes publicly available job listings from sources that allow automated access. Always respect:
- robots.txt files
- Terms of Service
- Rate limits
- API usage policies

## License

MIT
