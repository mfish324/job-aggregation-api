# Project Structure

```
Job_APIs/
│
├── main.py                 # Main CLI entry point
├── aggregator.py           # Core aggregation logic
├── scrapers.py             # All job source scrapers
├── models.py               # Database models and manager
├── example_usage.py        # Usage examples for integration
│
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
│
├── README.md              # Project overview
├── QUICKSTART.md          # Quick start guide
├── ADDING_SOURCES.md      # Guide for adding new sources
└── PROJECT_STRUCTURE.md   # This file
```

## File Descriptions

### Core Files

#### [main.py](main.py)
- CLI interface for the job aggregator
- Handles command-line arguments
- Coordinates scraping, searching, and exporting
- Usage: `python main.py [options]`

#### [aggregator.py](aggregator.py)
- `JobAggregator` class - main orchestrator
- Manages all scrapers
- Coordinates database operations
- Provides high-level API for scraping and searching

#### [scrapers.py](scrapers.py)
- `BaseScraper` - abstract base class
- Individual scraper classes for each job source:
  - `AdzunaScraper` - Adzuna API
  - `RemoteOKScraper` - RemoteOK API
  - `WeWorkRemotelyScraper` - We Work Remotely scraper
  - `RemotiveScraper` - Remotive API
  - `AuthenticJobsScraper` - Authentic Jobs RSS
  - `GitHubJobsScraper` - GitHub search
  - `IndeedRSSScraper` - Indeed RSS feeds
  - `AngelListScraper` - AngelList (placeholder)
  - `CrunchboardScraper` - TechCrunch jobs

#### [models.py](models.py)
- SQLAlchemy database models
- `Job` model with all job fields
- `DatabaseManager` class for database operations
- Handles deduplication via job ID hashing

### Documentation

#### [README.md](README.md)
- Project overview
- Feature list
- Installation instructions
- Basic usage examples

#### [QUICKSTART.md](QUICKSTART.md)
- 5-minute setup guide
- Common use cases
- Command examples
- Troubleshooting tips

#### [ADDING_SOURCES.md](ADDING_SOURCES.md)
- Tutorial for adding new job sources
- Code templates
- Real-world examples
- Best practices
- Legal considerations

#### [example_usage.py](example_usage.py)
- 8 practical examples
- Shows how to integrate into your app
- Demonstrates all major features
- API integration example

### Configuration

#### [requirements.txt](requirements.txt)
Python dependencies:
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `sqlalchemy` - Database ORM
- `pandas` - Data export
- `python-dotenv` - Environment variables
- `tabulate` - Pretty tables
- And more...

#### [.env.example](.env.example)
Environment variables template:
- API keys (optional)
- Database URL
- Scraping configuration

#### [.gitignore](.gitignore)
Excludes from version control:
- Python cache files
- Virtual environments
- Database files
- Environment variables
- Log files

## Architecture

### Data Flow

```
User Command
    ↓
main.py (CLI)
    ↓
JobAggregator
    ↓
Multiple Scrapers (parallel)
    ↓
Normalize Data
    ↓
DatabaseManager (deduplicate)
    ↓
SQLite Database (jobs.db)
    ↓
Search/Export/Display
```

### Class Hierarchy

```
BaseScraper (abstract)
    ├── AdzunaScraper
    ├── RemoteOKScraper
    ├── WeWorkRemotelyScraper
    ├── RemotiveScraper
    ├── AuthenticJobsScraper
    ├── GitHubJobsScraper
    ├── IndeedRSSScraper
    ├── AngelListScraper
    └── CrunchboardScraper

DatabaseManager
    └── manages → Job (model)

JobAggregator
    ├── uses → All Scrapers
    └── uses → DatabaseManager
```

## Database Schema

```sql
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY,
    job_id VARCHAR(255) UNIQUE,      -- MD5 hash for deduplication
    title VARCHAR(500) NOT NULL,
    company VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    description TEXT,
    url VARCHAR(1000) NOT NULL,
    source VARCHAR(100) NOT NULL,
    posted_date DATETIME,
    job_type VARCHAR(100),
    salary VARCHAR(255),
    tags TEXT,                        -- JSON array
    remote BOOLEAN,
    created_at DATETIME
);

-- Indexes
CREATE INDEX idx_job_id ON jobs(job_id);
CREATE INDEX idx_title ON jobs(title);
CREATE INDEX idx_company ON jobs(company);
CREATE INDEX idx_location ON jobs(location);
CREATE INDEX idx_source ON jobs(source);
CREATE INDEX idx_posted_date ON jobs(posted_date);
CREATE INDEX idx_remote ON jobs(remote);
```

## Key Design Decisions

### 1. Deduplication Strategy
- Jobs are deduplicated using MD5 hash of: `title|company|location`
- Prevents duplicate entries across different sources
- Same job from multiple sources only stored once

### 2. Normalized Data Structure
- All scrapers return consistent format
- Easy to add new sources
- Simplifies database operations

### 3. Rate Limiting
- Built-in delays between requests
- Respects source servers
- Prevents getting blocked

### 4. Error Handling
- Graceful failure - one source failing doesn't stop others
- Detailed error messages
- Continue scraping on partial failures

### 5. Extensibility
- Easy to add new sources (inherit from BaseScraper)
- Pluggable scraper architecture
- Configuration via environment variables

## Workflow Examples

### Daily Job Scraping
```bash
# Morning: Scrape all sources
python main.py --keywords "python developer" --location "remote"

# Check results
python main.py --stats

# Export for review
python main.py --export daily_jobs.csv
```

### Integration with Web App
```python
from aggregator import JobAggregator

# In your Flask/Django view
def get_jobs(request):
    aggregator = JobAggregator()
    jobs = aggregator.search_jobs(
        keyword=request.GET.get('keyword'),
        remote=True,
        limit=50
    )
    # Convert to JSON and return
    return jsonify([job.to_dict() for job in jobs])
```

### Automated Monitoring
```bash
# Cron job: every 6 hours
0 */6 * * * cd /path/to/Job_APIs && python main.py --keywords "your keywords"
```

## Performance Notes

- **Scraping Speed**: ~2-5 jobs/second per source
- **Database**: SQLite suitable for 100k+ jobs
- **Memory**: ~50-100MB during scraping
- **Disk**: ~1KB per job entry

## Scalability

### Current Setup (SQLite)
- Good for: Single user, ~100K jobs
- Local development and testing
- Desktop applications

### Scaling Up (PostgreSQL/MySQL)
```python
# Change in .env
DATABASE_URL=postgresql://user:pass@localhost/jobs
```

### Adding Search
```python
# Add full-text search
from sqlalchemy import Index
Index('idx_fulltext', Job.description, postgresql_using='gin')
```

## Contributing

To add a new feature:

1. **New Scraper**: Add to `scrapers.py`, register in `aggregator.py`
2. **New Field**: Update `Job` model, create migration
3. **New Export**: Add format in `aggregator.export_jobs()`
4. **New CLI Option**: Add to `main.py` argparse

## Maintenance

### Regular Tasks
- Update dependencies: `pip install -U -r requirements.txt`
- Check scraper health: `python main.py --sources <source>`
- Database cleanup: Remove old jobs periodically
- Monitor API rate limits

### Health Checks
```bash
# Test each source
for source in remoteok github indeed; do
    python main.py --sources $source --max-pages 1
done
```

## Next Steps

1. **Add more sources** - See [ADDING_SOURCES.md](ADDING_SOURCES.md)
2. **Build a web UI** - Flask/Django integration
3. **Add email alerts** - Notify on new matching jobs
4. **ML recommendations** - Match jobs to user profiles
5. **Mobile app** - React Native/Flutter interface
6. **API server** - RESTful API for job search
