# Quick Start Guide

## Setup (5 minutes)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure (Optional)

```bash
cp .env.example .env
```

Edit `.env` to add API keys (optional - works without them):
- **Adzuna**: Free API key from https://developer.adzuna.com/ (gives access to millions of jobs)
- **GitHub**: Personal access token for higher rate limits

### 3. Run Your First Scrape

```bash
# Scrape all available sources
python main.py
```

That's it! Jobs are now in `jobs.db`

## Common Use Cases

### Search for Specific Jobs

```bash
# Find Python developer jobs
python main.py --keywords "python developer"

# Find remote jobs
python main.py --location "remote"

# Find React jobs from specific sources
python main.py --keywords "react" --sources remoteok github
```

### View Results

```bash
# Show statistics
python main.py --stats

# Search stored jobs
python main.py --search "javascript"

# Search remote-only jobs
python main.py --search "backend" --remote-only
```

### Export Data

```bash
# Export to CSV
python main.py --export jobs.csv

# Export to JSON
python main.py --export jobs.json

# Export filtered results
python main.py --search "python" --remote-only --export remote_python_jobs.csv
```

## Available Sources

### No API Key Required (Ready to Use)
1. **RemoteOK** - Remote jobs from around the world
2. **Remotive** - Curated remote positions
3. **We Work Remotely** - Popular remote job board
4. **Authentic Jobs** - Design, development, creative jobs
5. **Indeed RSS** - Jobs from Indeed via RSS
6. **GitHub** - Tech jobs and hiring repos
7. **Crunchboard** - Startup jobs from TechCrunch

### API Key Required (Optional)
8. **Adzuna** - Millions of jobs worldwide (free API)

## Tips

1. **Start Small**: Test with one source first
   ```bash
   python main.py --sources remoteok
   ```

2. **Be Specific**: Use keywords to reduce noise
   ```bash
   python main.py --keywords "senior python engineer"
   ```

3. **Schedule Regular Scrapes**: Use cron/Task Scheduler
   ```bash
   # Example cron: scrape every 6 hours
   0 */6 * * * cd /path/to/Job_APIs && python main.py
   ```

4. **Monitor Database Growth**:
   ```bash
   python main.py --stats
   ```

## Troubleshooting

### "No module named 'X'"
```bash
pip install -r requirements.txt
```

### Slow scraping
- Reduce `--max-pages` (default is 5)
- Select specific sources with `--sources`

### Rate limiting errors
- Wait a few minutes between runs
- Check if API keys are configured correctly

### Empty results
- Check internet connection
- Try different keywords
- Some sources may temporarily be down

## Next Steps

1. **Integrate with your app**: Import `JobAggregator` class
   ```python
   from aggregator import JobAggregator

   aggregator = JobAggregator()
   stats = aggregator.scrape_all(keywords="developer")
   jobs = aggregator.search_jobs(keyword="python", limit=10)
   ```

2. **Customize scrapers**: Edit `scrapers.py` to add more sources

3. **Build a web interface**: Use Flask/Django to display jobs

4. **Add email alerts**: Notify when new jobs match criteria

5. **Enhance matching**: Add ML-based job recommendations
