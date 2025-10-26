# How to View Job Listings

There are multiple ways to view the job listings you've scraped:

## Method 1: Quick Search (Table View)

Show jobs in a compact table format:

```bash
# Search for Python jobs
python main.py --search "python"

# Search for JavaScript jobs from GitHub
python main.py --search "javascript" --source github

# Search for remote-only jobs
python main.py --search "developer" --remote-only

# Limit results
python main.py --search "react" | head -50
```

**Example Output:**
```
Found 50 jobs:

+-------------------------+---------------+----------+--------+--------+
| Title                   | Company       | Location | Source | Remote |
+=========================+===============+==========+========+========+
| Senior Python Developer | TechCorp      | Remote   | remote | Yes    |
| Data Scientist          | DataInc       | NYC      | indeed | No     |
+-------------------------+---------------+----------+--------+--------+
```

---

## Method 2: Detailed View (With URLs)

Show complete job details including clickable URLs:

```bash
# View Python jobs with details
python view_jobs.py --keyword "python" --limit 10

# View remote JavaScript jobs
python view_jobs.py --keyword "javascript" --remote-only

# View jobs from specific source
python view_jobs.py --source remoteok --limit 5

# View with full descriptions
python view_jobs.py --keyword "developer" --full --limit 3
```

**Example Output:**
```
1. Senior Python Developer
   Company: TechCorp
   Location: Remote
   Source: remoteok
   Remote: Yes
   Posted: 2025-10-14
   Salary: $120K - $180K
   Type: Full-time
   URL: https://remoteok.com/remote-jobs/12345
   Description: We are looking for a senior Python developer...
```

---

## Method 3: Export to CSV/Excel

Export jobs to CSV file that you can open in Excel or Google Sheets:

```bash
# Export all jobs
python main.py --export all_jobs.csv

# Export Python jobs only
python main.py --search "python" --export python_jobs.csv

# Export remote jobs only
python main.py --remote-only --export remote_jobs.csv

# Export from specific source
python main.py --source github --export github_jobs.csv

# Export to JSON instead
python main.py --export jobs.json
```

Then open `python_jobs.csv` in Excel, Google Sheets, or any spreadsheet program!

**CSV includes:**
- Title
- Company
- Location
- Description (truncated)
- URL (clickable link)
- Source
- Posted Date
- Job Type
- Salary
- Remote (Yes/No)

---

## Method 4: Direct Database Query (Python)

For custom analysis, query the database directly:

```python
from aggregator import JobAggregator

aggregator = JobAggregator()

# Get Python jobs
jobs = aggregator.search_jobs(keyword="python", limit=10)

# Access job details
for job in jobs:
    print(f"Title: {job.title}")
    print(f"Company: {job.company}")
    print(f"URL: {job.url}")
    print(f"Description: {job.description}")
    print(f"Salary: {job.salary}")
    print("-" * 80)

aggregator.close()
```

---

## Method 5: Database Statistics

See overall statistics:

```bash
python main.py --stats
```

**Example Output:**
```
============================================================
DATABASE STATISTICS
============================================================
Total Jobs: 1708
Remote Jobs: 1520

Jobs by Source:
  remoteok            : 850
  remotive            : 450
  indeed              : 208
  github              : 120
  authenticjobs       : 80
============================================================
```

---

## Quick Reference

| What You Want | Command |
|---------------|---------|
| Search jobs | `python main.py --search "keyword"` |
| View with URLs | `python view_jobs.py --keyword "keyword"` |
| Export to Excel | `python main.py --export jobs.csv` |
| Remote jobs only | Add `--remote-only` to any command |
| Specific source | Add `--source remoteok` to any command |
| Show descriptions | `python view_jobs.py --keyword "keyword" --full` |
| Statistics | `python main.py --stats` |

---

## Filtering Tips

### By Keyword
```bash
# Single keyword
python view_jobs.py --keyword "python"

# Will match: Python, python developer, Senior Python Engineer
```

### By Source
```bash
# From RemoteOK
python view_jobs.py --source remoteok

# From GitHub
python view_jobs.py --source github
```

### By Location/Remote
```bash
# Only remote jobs
python view_jobs.py --remote-only

# Combine with keyword
python view_jobs.py --keyword "react" --remote-only
```

### Combine Filters
```bash
# Remote Python jobs from RemoteOK
python view_jobs.py --keyword "python" --source remoteok --remote-only

# First 5 JavaScript jobs
python view_jobs.py --keyword "javascript" --limit 5
```

---

## Opening Job URLs

### Windows
```bash
# View job and copy URL
python view_jobs.py --keyword "python" --limit 1

# Then open in browser
start https://remoteok.com/remote-jobs/12345
```

### Mac/Linux
```bash
# View job and copy URL
python view_jobs.py --keyword "python" --limit 1

# Then open in browser
open https://remoteok.com/remote-jobs/12345  # Mac
xdg-open https://remoteok.com/remote-jobs/12345  # Linux
```

### Automatic Browser Opening (Advanced)

Create a script to open jobs automatically:

```python
# open_jobs.py
from aggregator import JobAggregator
import webbrowser

aggregator = JobAggregator()
jobs = aggregator.search_jobs(keyword="python", limit=5)

for job in jobs:
    print(f"Opening: {job.title} at {job.company}")
    webbrowser.open(job.url)
    input("Press Enter for next job...")

aggregator.close()
```

---

## Pro Tips

1. **Use CSV for bulk review**: Export to CSV and sort/filter in Excel
   ```bash
   python main.py --export jobs.csv
   ```

2. **Check URLs in view_jobs**: URLs are clickable in most terminals
   ```bash
   python view_jobs.py --keyword "your keyword" --limit 10
   ```

3. **Combine with grep**: Filter output further
   ```bash
   python view_jobs.py --keyword "developer" | grep "Remote: Yes"
   ```

4. **Save to file**: Redirect output to a file
   ```bash
   python view_jobs.py --keyword "python" > python_jobs.txt
   ```

5. **Pipe to less**: For easier reading
   ```bash
   python view_jobs.py --keyword "developer" | less
   ```

---

## Examples

### Find High-Paying Remote Python Jobs
```bash
# First scrape fresh data
python main.py --keywords "python" --location "remote"

# View with salary info
python view_jobs.py --keyword "python" --remote-only --full

# Or export and filter in Excel
python main.py --export python_remote.csv
```

### Compare Jobs from Different Sources
```bash
# Export each source separately
python main.py --source remoteok --export remoteok_jobs.csv
python main.py --source github --export github_jobs.csv
python main.py --source indeed --export indeed_jobs.csv
```

### Daily Job Review Workflow
```bash
# 1. Scrape new jobs
python main.py --max-pages 3

# 2. Check stats
python main.py --stats

# 3. View today's jobs
python view_jobs.py --limit 20

# 4. Export for detailed review
python main.py --export today_$(date +%Y%m%d).csv
```

---

## Troubleshooting

**Q: Why do some jobs not have URLs?**
A: Some sources may have broken links or the URL wasn't parsed correctly. Check the source website directly.

**Q: Can I filter by salary?**
A: Not directly via CLI. Export to CSV and filter in Excel, or write a custom Python script.

**Q: How do I see only jobs from today?**
A: Jobs are ordered by creation time. The most recent are shown first. For exact filtering, query the database directly in Python.

**Q: Can I apply directly through your tool?**
A: No, click the URL to visit the job posting page and apply there.

---

## Next Steps

After finding jobs you like:

1. **Click the URL** to visit the job posting
2. **Save interesting jobs** to a separate CSV
3. **Set up alerts** (see DEPLOYMENT.md for scheduling)
4. **Build a web interface** to browse jobs more easily

Happy job hunting! 🎯
