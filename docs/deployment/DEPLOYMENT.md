# Deployment Guide

How to deploy the Job Aggregator to production environments.

## Table of Contents
- [Local Development](#local-development)
- [Production Setup](#production-setup)
- [Cloud Deployment](#cloud-deployment)
- [Scheduled Scraping](#scheduled-scraping)
- [Performance Optimization](#performance-optimization)
- [Monitoring](#monitoring)

## Local Development

### Setup
```bash
# Clone/download project
cd Job_APIs

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Test setup
python test_setup.py

# First scrape
python main.py --sources remoteok --max-pages 1
```

## Production Setup

### 1. Use PostgreSQL Instead of SQLite

**Why?**
- Better concurrent access
- Larger datasets (millions of jobs)
- Better performance
- Production-ready

**Setup:**
```bash
# Install PostgreSQL
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# Create database
createdb jobs_db

# Update .env
DATABASE_URL=postgresql://user:password@localhost/jobs_db
```

**Update requirements.txt:**
```bash
echo "psycopg2-binary==2.9.9" >> requirements.txt
pip install psycopg2-binary
```

### 2. Use Environment Variables

Never commit sensitive data. Use environment variables:

```bash
# .env (never commit this!)
DATABASE_URL=postgresql://user:password@host:5432/jobs_db
ADZUNA_APP_ID=your_real_id
ADZUNA_APP_KEY=your_real_key
GITHUB_TOKEN=your_real_token
```

### 3. Add Logging

Create `logging_config.py`:
```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logger = logging.getLogger('job_aggregator')
    logger.setLevel(logging.INFO)

    # File handler
    handler = RotatingFileHandler(
        'job_aggregator.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
```

Use in your code:
```python
from logging_config import setup_logging
logger = setup_logging()

logger.info("Starting scrape")
logger.error(f"Error: {e}")
```

### 4. Error Notifications

Add email/Slack notifications for errors:

```python
# error_notifier.py
import smtplib
from email.mime.text import MIMEText

def send_error_email(error_message):
    msg = MIMEText(error_message)
    msg['Subject'] = 'Job Aggregator Error'
    msg['From'] = 'alerts@yourcompany.com'
    msg['To'] = 'admin@yourcompany.com'

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('your_email', 'your_password')
        server.send_message(msg)
```

## Cloud Deployment

### Option 1: AWS

#### EC2 Setup
```bash
# Launch EC2 instance (Ubuntu)
ssh ubuntu@your-instance-ip

# Install dependencies
sudo apt-get update
sudo apt-get install python3-pip postgresql

# Clone project
git clone your-repo
cd Job_APIs

# Setup
pip3 install -r requirements.txt
cp .env.example .env
nano .env  # Configure

# Test
python3 main.py --sources remoteok --max-pages 1
```

#### RDS (Database)
```bash
# Create RDS PostgreSQL instance
# Update .env with RDS endpoint
DATABASE_URL=postgresql://user:pass@rds-endpoint.amazonaws.com:5432/jobs
```

### Option 2: Google Cloud Platform

```bash
# Create Compute Engine instance
gcloud compute instances create job-aggregator \
    --machine-type=n1-standard-1 \
    --zone=us-central1-a

# SSH
gcloud compute ssh job-aggregator

# Install Python and dependencies
sudo apt-get install python3-pip
pip3 install -r requirements.txt

# Setup Cloud SQL (PostgreSQL)
# Update .env with Cloud SQL connection
```

### Option 3: Heroku

```bash
# Install Heroku CLI
# Login
heroku login

# Create app
heroku create your-job-aggregator

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Set config
heroku config:set ADZUNA_APP_ID=your_id
heroku config:set ADZUNA_APP_KEY=your_key

# Deploy
git push heroku main

# Run scraper
heroku run python main.py
```

### Option 4: DigitalOcean

```bash
# Create Droplet (Ubuntu)
# SSH to droplet

# Install
git clone your-repo
cd Job_APIs
pip3 install -r requirements.txt

# Setup PostgreSQL
sudo apt-get install postgresql
createdb jobs_db

# Configure .env
nano .env
```

## Scheduled Scraping

### Option 1: Cron (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add job (every 6 hours)
0 */6 * * * cd /path/to/Job_APIs && /path/to/python main.py --sources remoteok remotive >> /var/log/job_scraper.log 2>&1

# Every day at 2 AM
0 2 * * * cd /path/to/Job_APIs && /path/to/python main.py >> /var/log/job_scraper.log 2>&1

# Every Monday at 9 AM
0 9 * * 1 cd /path/to/Job_APIs && /path/to/python main.py
```

### Option 2: Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., Daily at 6 AM)
4. Set action:
   - Program: `C:\Python39\python.exe`
   - Arguments: `main.py`
   - Start in: `C:\Users\matto\projects\Job_APIs`

### Option 3: Python Schedule

```python
# scheduler.py
import schedule
import time
from aggregator import JobAggregator

def scrape_job():
    print("Starting scheduled scrape...")
    aggregator = JobAggregator()
    aggregator.scrape_all(max_pages=5)
    aggregator.close()
    print("Scrape complete!")

# Schedule jobs
schedule.every(6).hours.do(scrape_job)
schedule.every().day.at("02:00").do(scrape_job)

print("Scheduler started...")
while True:
    schedule.run_pending()
    time.sleep(60)
```

Run as background service:
```bash
nohup python scheduler.py &
```

### Option 4: Celery (Advanced)

```python
# celery_tasks.py
from celery import Celery
from aggregator import JobAggregator

app = Celery('job_scraper', broker='redis://localhost:6379/0')

@app.task
def scrape_jobs():
    aggregator = JobAggregator()
    stats = aggregator.scrape_all(max_pages=5)
    aggregator.close()
    return stats

# Schedule
app.conf.beat_schedule = {
    'scrape-every-6-hours': {
        'task': 'celery_tasks.scrape_jobs',
        'schedule': 21600.0,  # 6 hours in seconds
    },
}
```

## Performance Optimization

### 1. Parallel Scraping

```python
# parallel_aggregator.py
from concurrent.futures import ThreadPoolExecutor
from aggregator import JobAggregator

class ParallelAggregator(JobAggregator):
    def scrape_all_parallel(self, keywords=None, location=None, max_workers=5):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []

            for source_name, scraper in self.scrapers.items():
                future = executor.submit(
                    scraper.scrape,
                    keywords=keywords,
                    location=location
                )
                futures.append((source_name, future))

            for source_name, future in futures:
                try:
                    jobs = future.result(timeout=120)
                    for job in jobs:
                        self.db.add_job(job)
                except Exception as e:
                    print(f"Error in {source_name}: {e}")
```

### 2. Caching

```python
# Add to scrapers.py
from functools import lru_cache
import hashlib
import json
import os

class CachedScraper(BaseScraper):
    CACHE_DIR = '.cache'
    CACHE_HOURS = 6

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        os.makedirs(self.CACHE_DIR, exist_ok=True)

    def get_cache_path(self, keywords, location):
        key = f"{self.__class__.__name__}_{keywords}_{location}"
        hash_key = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.CACHE_DIR, f"{hash_key}.json")

    def get_cached(self, keywords, location):
        cache_path = self.get_cache_path(keywords, location)
        if os.path.exists(cache_path):
            age_hours = (time.time() - os.path.getmtime(cache_path)) / 3600
            if age_hours < self.CACHE_HOURS:
                with open(cache_path, 'r') as f:
                    return json.load(f)
        return None

    def save_cache(self, keywords, location, data):
        cache_path = self.get_cache_path(keywords, location)
        with open(cache_path, 'w') as f:
            json.dump(data, f)
```

### 3. Database Indexing

```python
# Add to models.py after table creation
from sqlalchemy import Index

# Add indexes for common queries
Index('idx_job_search', Job.title, Job.description, postgresql_using='gin')
Index('idx_posted_remote', Job.posted_date, Job.remote)
Index('idx_company_location', Job.company, Job.location)
```

### 4. Connection Pooling

```python
# Update models.py
from sqlalchemy.pool import QueuePool

engine = create_engine(
    database_url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

## Monitoring

### 1. Health Check Endpoint

```python
# health_check.py
from flask import Flask, jsonify
from aggregator import JobAggregator

app = Flask(__name__)

@app.route('/health')
def health():
    try:
        aggregator = JobAggregator()
        stats = aggregator.get_statistics()
        aggregator.close()

        return jsonify({
            'status': 'healthy',
            'total_jobs': stats['total_jobs'],
            'sources': len(stats['by_source'])
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(port=8080)
```

### 2. Metrics Collection

```python
# metrics.py
import time
from datetime import datetime

class MetricsCollector:
    def __init__(self):
        self.metrics = {
            'scrapes': 0,
            'jobs_added': 0,
            'errors': 0,
            'last_scrape': None
        }

    def record_scrape(self, stats):
        self.metrics['scrapes'] += 1
        self.metrics['jobs_added'] += stats['total_new']
        self.metrics['last_scrape'] = datetime.utcnow()

    def record_error(self, error):
        self.metrics['errors'] += 1
```

### 3. Alerting

```python
# alerts.py
def check_and_alert():
    aggregator = JobAggregator()
    stats = aggregator.get_statistics()

    # Alert if no jobs added in last 24 hours
    recent_jobs = aggregator.search_jobs(limit=1)
    if recent_jobs:
        hours_since = (datetime.utcnow() - recent_jobs[0].created_at).hours
        if hours_since > 24:
            send_alert("No new jobs in 24 hours!")

    # Alert if total jobs drops significantly
    if stats['total_jobs'] < EXPECTED_MIN:
        send_alert(f"Job count low: {stats['total_jobs']}")
```

## Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  scraper:
    build: .
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/jobs
      - ADZUNA_APP_ID=${ADZUNA_APP_ID}
      - ADZUNA_APP_KEY=${ADZUNA_APP_KEY}
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=jobs
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Run with Docker
```bash
docker-compose up -d
docker-compose exec scraper python main.py
```

## Security Checklist

- [ ] Never commit .env file
- [ ] Use environment variables for secrets
- [ ] Enable SSL for database connections
- [ ] Use HTTPS for API endpoints
- [ ] Rate limit your own API if exposing
- [ ] Regularly update dependencies
- [ ] Use strong database passwords
- [ ] Restrict database access by IP
- [ ] Monitor for suspicious activity
- [ ] Regular security audits

## Cost Estimation

### Small Scale (< 10K jobs/day)
- Server: $5-10/month (DigitalOcean Droplet)
- Database: Included or $7/month
- Total: ~$12-17/month

### Medium Scale (10K-100K jobs/day)
- Server: $40-80/month
- Database: $15-50/month
- CDN/Cache: $10/month
- Total: ~$65-140/month

### Large Scale (100K+ jobs/day)
- Server: $160+/month
- Database: $100+/month
- Cache: $50+/month
- Total: ~$310+/month

## Maintenance Checklist

### Daily
- [ ] Check error logs
- [ ] Verify scraper health
- [ ] Monitor job counts

### Weekly
- [ ] Review new duplicates
- [ ] Check database size
- [ ] Update any broken scrapers

### Monthly
- [ ] Update dependencies
- [ ] Database cleanup/vacuum
- [ ] Review API usage/costs
- [ ] Performance analysis

### Quarterly
- [ ] Security audit
- [ ] Add new sources
- [ ] Review and optimize queries
- [ ] Backup testing

## Troubleshooting

Common issues and solutions in production:

1. **Database connection errors**: Check connection pool size
2. **Scraper timeouts**: Increase timeout values
3. **Memory issues**: Reduce max_pages, add pagination
4. **Rate limiting**: Add delays, respect limits
5. **Stale data**: Increase scraping frequency

## Next Steps

1. Set up monitoring dashboard (Grafana)
2. Implement caching layer (Redis)
3. Add search API (FastAPI)
4. Build admin panel
5. Add machine learning for job matching
