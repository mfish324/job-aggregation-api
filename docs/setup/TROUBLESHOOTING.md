# Troubleshooting Guide

Common issues and their solutions.

## Installation Issues

### Issue: "Preparing metadata (pyproject.toml) did not run successfully"

**Solution:**
```bash
# Try installing packages individually
pip install requests python-dotenv sqlalchemy beautifulsoup4 tabulate python-dateutil

# Install pandas separately (often the problem)
pip install pandas

# If lxml fails, try:
pip install --only-binary :all: lxml
```

**Alternative - Minimal installation:**
```bash
pip install requests beautifulsoup4 python-dotenv sqlalchemy tabulate python-dateutil
```
Skip pandas (only for export) and lxml (only for some RSS) if problematic.

---

### Issue: "ModuleNotFoundError: No module named 'X'"

**Solution:**
```bash
pip install -r requirements.txt

# Or install the specific missing module
pip install module_name
```

---

## Database Issues

### Issue: "The process cannot access the file because it is being used by another process"

**Cause:** Database file locked (Windows issue)

**Solution:**
```python
# The test_setup.py has been fixed to handle this
# If you see this in your own code, ensure you:
1. Close database connections properly
2. Use unique database names for tests
3. Add small delays before file deletion
```

---

### Issue: "OperationalError: database is locked"

**Solution:**
```bash
# Close all connections to the database
# Or delete and recreate:
rm jobs.db
python main.py
```

---

## Scraping Issues

### Issue: "'str' object cannot be interpreted as an integer"

**Cause:** Date parsing error in scrapers

**Solution:** Already fixed in RemoteOK scraper. If you see this elsewhere:
```python
# Always parse dates safely
try:
    if isinstance(date_value, (int, float)):
        date = datetime.fromtimestamp(date_value)
    else:
        date = self.normalize_date(date_value)
except:
    date = datetime.utcnow()
```

---

### Issue: "No jobs found" or "0 jobs scraped"

**Possible causes:**
1. Network connection issue
2. Source website is down
3. Source changed their structure
4. Keywords too specific

**Solutions:**
```bash
# Test one source at a time
python main.py --sources remoteok --max-pages 1

# Try without keywords first
python main.py --sources remoteok

# Check source directly in browser
# RemoteOK API: https://remoteok.com/api
```

---

### Issue: "Error: 429 Too Many Requests"

**Cause:** Rate limiting

**Solution:**
```bash
# Reduce max pages
python main.py --max-pages 2

# Wait between runs (already built-in)
# Or increase delays in scrapers.py
```

---

### Issue: "SSL Certificate verification failed"

**Solution:**
```python
# In scrapers.py, add to session:
self.session.verify = False  # Not recommended for production

# Better solution: update certificates
pip install --upgrade certifi
```

---

## Windows-Specific Issues

### Issue: Unicode characters not displaying (✓, ✗, etc.)

**Status:** Fixed in test_setup.py

**If you see this elsewhere:**
```python
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

Or use ASCII alternatives:
```python
# Instead of ✓ use [OK]
# Instead of ✗ use [FAIL]
```

---

### Issue: "chcp 65001" needed error

**Solution:**
```cmd
# Run in command prompt before Python
chcp 65001

# Or add to script
import subprocess
subprocess.run(['chcp', '65001'], shell=True)
```

---

## Test Failures

### Issue: "All tests failed with encoding errors"

**Status:** Fixed - test_setup.py now handles Windows encoding

**Manual fix if needed:**
```bash
# Set console to UTF-8
chcp 65001

# Then run
python test_setup.py
```

---

### Issue: "Test database cleanup fails"

**Cause:** Database still in use

**Solution:** Already fixed with:
- Unique database names per test
- Proper connection closing
- Sleep delays before cleanup
- Try-except on cleanup

---

## API Key Issues

### Issue: "Invalid API credentials"

**Solution:**
```bash
# Check .env file
cat .env

# Adzuna: Get free key from https://developer.adzuna.com/
ADZUNA_APP_ID=your_id
ADZUNA_APP_KEY=your_key

# GitHub: Create token at https://github.com/settings/tokens
GITHUB_TOKEN=your_token
```

---

### Issue: "API rate limit exceeded"

**Solution:**
```bash
# Most sources work without API keys
python main.py --sources remoteok remotive

# For Adzuna, free tier is 300 calls/month
# Reduce scraping frequency or upgrade
```

---

## Performance Issues

### Issue: "Scraping is very slow"

**Solutions:**
```bash
# Reduce max pages
python main.py --max-pages 2

# Use specific sources only
python main.py --sources remoteok github

# Skip slow scrapers (We Work Remotely, Crunchboard)
python main.py --sources remoteok remotive indeed
```

---

### Issue: "Database getting too large"

**Solution:**
```sql
-- Delete old jobs (older than 30 days)
DELETE FROM jobs WHERE created_at < datetime('now', '-30 days');

-- Vacuum to reclaim space
VACUUM;
```

Or in Python:
```python
from models import DatabaseManager
from datetime import datetime, timedelta

db = DatabaseManager()
cutoff = datetime.utcnow() - timedelta(days=30)
db.session.query(Job).filter(Job.created_at < cutoff).delete()
db.session.commit()
```

---

## Network Issues

### Issue: "Connection timeout"

**Solution:**
```bash
# Increase timeout in scrapers
# Edit scrapers.py line 15:
timeout=60  # instead of 30

# Or skip problematic sources
python main.py --sources remoteok remotive
```

---

### Issue: "Connection refused" or "Name resolution failed"

**Possible causes:**
1. No internet connection
2. Firewall blocking
3. Source website down
4. VPN/proxy issues

**Solutions:**
```bash
# Test internet connection
ping google.com

# Test specific source
curl https://remoteok.com/api

# Check firewall settings
# Try different network
```

---

## Import/Export Issues

### Issue: "pandas not found when exporting"

**Solution:**
```bash
# Install pandas
pip install pandas

# Or export without pandas (implement custom CSV writer)
```

---

### Issue: "Export file locked"

**Cause:** File open in Excel/other program

**Solution:**
```bash
# Close the file
# Or use different filename
python main.py --export jobs_new.csv
```

---

## Development Issues

### Issue: "Changes to scrapers.py not taking effect"

**Solution:**
```bash
# Python may be caching
rm -rf __pycache__
python main.py

# Or restart Python interpreter
```

---

### Issue: "Source website changed structure"

**Solution:**
1. Inspect the new structure (browser dev tools)
2. Update scraper class in scrapers.py
3. Test with single source:
   ```bash
   python main.py --sources newsource --max-pages 1
   ```

---

## Getting Help

If you still have issues:

1. **Check logs:** Look for error messages
2. **Test individually:** Test each component separately
3. **Check source:** Verify source website is accessible
4. **Update dependencies:** `pip install -U -r requirements.txt`
5. **Review docs:** Check README.md and other guides
6. **Create minimal test case:** Isolate the problem

### Debug Mode

Add to your script:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or use verbose printing:
```python
# In scrapers.py, add print statements
print(f"Response status: {response.status_code}")
print(f"Data received: {len(data)} items")
```

---

## Common Error Messages

| Error | Likely Cause | Solution |
|-------|-------------|----------|
| `ImportError` | Missing package | `pip install package` |
| `OperationalError` | Database locked | Close connections, restart |
| `Timeout` | Network slow | Increase timeout, check internet |
| `429` | Rate limited | Wait, reduce frequency |
| `KeyError` | Source changed | Update scraper code |
| `UnicodeError` | Encoding issue | Use UTF-8 encoding |
| `FileNotFoundError` | Wrong path | Check working directory |
| `AttributeError` | API response changed | Update parsing logic |

---

## Prevention Tips

1. **Always test after changes:** `python test_setup.py`
2. **Start small:** Test with 1-2 sources and max-pages=1
3. **Use version control:** Git to track changes
4. **Monitor sources:** Websites change, update scrapers
5. **Handle errors gracefully:** Try-except blocks
6. **Log everything:** Keep logs for debugging
7. **Rate limit:** Be respectful of source servers
8. **Update regularly:** `pip install -U -r requirements.txt`
9. **Backup database:** Regular database backups
10. **Read error messages:** They usually tell you what's wrong

---

## Still Stuck?

Create an issue with:
1. Full error message
2. Python version (`python --version`)
3. OS version
4. Steps to reproduce
5. What you've already tried
