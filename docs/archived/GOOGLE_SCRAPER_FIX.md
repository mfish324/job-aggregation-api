# Google Scraper Error Fix

## Error
```
'NoneType' object has no attribute 'lower'
```

## Root Cause

In `company_scrapers.py`, line 94:
```python
if location and location.lower() not in location_str.lower():
```

The `location_str` variable can be `None` in some cases, causing the `.lower()` call to fail.

## Fix

Replace lines 76-85 in `company_scrapers.py`:

### Old Code (lines 76-85):
```python
# Extract location
location_elem = job_elem.find('locations')
location_str = 'USA'
if location_elem is not None:
    loc = location_elem.find('location')
    if loc is not None:
        city = loc.find('city').text if loc.find('city') is not None else ''
        state = loc.find('state').text if loc.find('state') is not None else ''
        country = loc.find('country').text if loc.find('country') is not None else 'USA'
        location_str = f"{city}, {state}" if city and state else country
```

### New Code (with None handling):
```python
# Extract location
location_elem = job_elem.find('locations')
location_str = 'USA'  # Default
if location_elem is not None:
    loc = location_elem.find('location')
    if loc is not None:
        city = loc.find('city').text if loc.find('city') is not None else ''
        state = loc.find('state').text if loc.find('state') is not None else ''
        country = loc.find('country').text if loc.find('country') is not None else 'USA'
        if city and state:
            location_str = f"{city}, {state}"
        elif country:
            location_str = country
        else:
            location_str = 'USA'  # Fallback

# Ensure location_str is never None
if location_str is None:
    location_str = 'USA'
```

## Alternative Quick Fix

Or simply add None-safety to line 94:

### Old (line 94):
```python
if location and location.lower() not in location_str.lower():
```

### New (with None check):
```python
if location and location_str and location.lower() not in location_str.lower():
```

## Apply Fix

### Option 1: Edit file directly

```bash
cd C:\Users\matto\projects\Job_APIs
nano company_scrapers.py
```

Find line 94 and change to:
```python
if location and location_str and location.lower() not in location_str.lower():
```

### Option 2: Use sed (Git Bash)

```bash
cd /c/Users/matto/projects/Job_APIs
sed -i 's/if location and location.lower() not in location_str.lower():/if location and location_str and location.lower() not in location_str.lower():/' company_scrapers.py
```

### Option 3: Python script

```python
# fix_google_scraper.py
with open('company_scrapers.py', 'r') as f:
    content = f.read()

# Fix the issue
content = content.replace(
    'if location and location.lower() not in location_str.lower():',
    'if location and location_str and location.lower() not in location_str.lower():'
)

with open('company_scrapers.py', 'w') as f:
    f.write(content)

print("Fixed Google scraper!")
```

## Test After Fix

```bash
cd C:\Users\matto\projects\Job_APIs
python trigger_scrape.py
```

Should see:
```
google: {'scraped': X, 'new': Y, 'duplicates': Z}
```

Instead of the error.

## Additional Defensive Coding

Also add None-safety to line 90:

### Old (line 90):
```python
if kw_lower not in title.lower() and kw_lower not in description.lower():
```

### New:
```python
if title and description and (kw_lower not in title.lower() and kw_lower not in description.lower()):
```

This ensures `title` and `description` are not None before calling `.lower()`.

## Summary

The error occurs because:
1. XML parsing can return `None` for some fields
2. The code assumes fields have string values
3. Calling `.lower()` on `None` raises AttributeError

**Quick fix**: Add `location_str` check on line 94
**Better fix**: Add None checks throughout
**Best fix**: Use helper functions for safe text comparison

Choose Quick fix for now, Better/Best fix for production.
