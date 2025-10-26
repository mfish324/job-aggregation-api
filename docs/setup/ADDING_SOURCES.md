# Adding New Job Sources

This guide shows you how to add new job sources to the aggregator.

## Quick Guide

1. Create a new scraper class in [scrapers.py](scrapers.py)
2. Inherit from `BaseScraper`
3. Implement the `scrape()` method
4. Register in [aggregator.py](aggregator.py)

## Template

```python
class NewSourceScraper(BaseScraper):
    """Description of the source"""

    def __init__(self, api_key=None, timeout=30):
        super().__init__(timeout)
        self.api_key = api_key

    def scrape(self, keywords=None, location=None, max_pages=5):
        jobs = []

        try:
            # Your scraping logic here
            # Example: API call
            url = "https://api.newsource.com/jobs"
            params = {
                'query': keywords or '',
                'location': location or '',
                'page': 1
            }

            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            # Parse and normalize the data
            for item in data.get('jobs', []):
                jobs.append({
                    'title': item.get('title', 'N/A'),
                    'company': item.get('company', 'N/A'),
                    'location': item.get('location', 'N/A'),
                    'description': item.get('description', ''),
                    'url': item.get('url', ''),
                    'source': 'newsource',  # Unique identifier
                    'posted_date': self.normalize_date(item.get('date')),
                    'job_type': item.get('type', 'N/A'),
                    'salary': item.get('salary'),
                    'tags': json.dumps(item.get('skills', [])),
                    'remote': 'remote' in str(item.get('location', '')).lower()
                })

            time.sleep(1)  # Rate limiting

        except Exception as e:
            print(f"Error scraping NewSource: {e}")

        return jobs
```

## Real-World Examples

### Example 1: REST API (JSON Response)

```python
class StackOverflowJobsScraper(BaseScraper):
    """Stack Overflow Jobs API"""

    def scrape(self, keywords=None, location=None, max_pages=5):
        jobs = []
        base_url = "https://stackoverflow.com/jobs/feed"

        try:
            params = {'q': keywords, 'l': location}
            response = self.session.get(base_url, params=params)
            soup = BeautifulSoup(response.text, 'xml')

            for item in soup.find_all('item'):
                jobs.append({
                    'title': item.find('title').text,
                    'company': item.find('company').text if item.find('company') else 'N/A',
                    'location': item.find('location').text if item.find('location') else 'N/A',
                    'description': item.find('description').text,
                    'url': item.find('link').text,
                    'source': 'stackoverflow',
                    'posted_date': self.normalize_date(item.find('pubDate').text),
                    'job_type': 'N/A',
                    'salary': None,
                    'tags': json.dumps([]),
                    'remote': False
                })
        except Exception as e:
            print(f"Error: {e}")

        return jobs
```

### Example 2: Web Scraping (HTML)

```python
class LinkedInScraper(BaseScraper):
    """LinkedIn Jobs - Note: requires careful respect of ToS"""

    def scrape(self, keywords=None, location=None, max_pages=5):
        jobs = []

        for page in range(max_pages):
            try:
                url = "https://www.linkedin.com/jobs/search"
                params = {
                    'keywords': keywords,
                    'location': location,
                    'start': page * 25
                }

                response = self.session.get(url, params=params)
                soup = BeautifulSoup(response.text, 'html.parser')

                for job_card in soup.find_all('div', class_='job-card'):
                    title_elem = job_card.find('h3', class_='job-title')
                    company_elem = job_card.find('h4', class_='company-name')
                    link_elem = job_card.find('a')

                    if title_elem and company_elem:
                        jobs.append({
                            'title': title_elem.text.strip(),
                            'company': company_elem.text.strip(),
                            'location': location or 'N/A',
                            'description': '',
                            'url': link_elem['href'] if link_elem else '',
                            'source': 'linkedin',
                            'posted_date': datetime.utcnow(),
                            'job_type': 'N/A',
                            'salary': None,
                            'tags': json.dumps([]),
                            'remote': 'remote' in location.lower() if location else False
                        })

                time.sleep(2)  # Important: respect rate limits
            except Exception as e:
                print(f"Error: {e}")
                break

        return jobs
```

### Example 3: RSS Feed

```python
class DiceJobsScraper(BaseScraper):
    """Dice.com RSS feed"""

    def scrape(self, keywords=None, location=None, max_pages=5):
        jobs = []

        try:
            url = f"https://www.dice.com/rss/index.xml?q={keywords or ''}&l={location or ''}"
            response = self.session.get(url)
            soup = BeautifulSoup(response.text, 'xml')

            for item in soup.find_all('item'):
                title = item.find('title').text if item.find('title') else 'N/A'
                description = item.find('description').text if item.find('description') else ''

                jobs.append({
                    'title': title,
                    'company': 'N/A',  # Parse from description if available
                    'location': location or 'N/A',
                    'description': description,
                    'url': item.find('link').text if item.find('link') else '',
                    'source': 'dice',
                    'posted_date': self.normalize_date(item.find('pubDate').text),
                    'job_type': 'N/A',
                    'salary': None,
                    'tags': json.dumps([]),
                    'remote': 'remote' in description.lower()
                })
        except Exception as e:
            print(f"Error: {e}")

        return jobs
```

## Registering Your Scraper

Add to [aggregator.py](aggregator.py) in the `__init__` method:

```python
class JobAggregator:
    def __init__(self, database_url=None):
        # ... existing code ...

        # Add your new scraper
        self.scrapers['newsource'] = NewSourceScraper()

        # Or with API key
        newsource_key = os.getenv('NEWSOURCE_API_KEY')
        if newsource_key:
            self.scrapers['newsource'] = NewSourceScraper(newsource_key)
```

## Best Practices

### 1. Respect Rate Limits
```python
time.sleep(1)  # Wait between requests
```

### 2. Handle Errors Gracefully
```python
try:
    # scraping code
except requests.exceptions.Timeout:
    print("Request timed out")
except requests.exceptions.RequestException as e:
    print(f"Request error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### 3. Normalize Data
```python
# Always use normalize_date for dates
posted_date = self.normalize_date(date_string)

# Check for remote keywords
remote = any(word in location.lower() for word in ['remote', 'anywhere', 'work from home'])

# Handle missing data
company = data.get('company') or 'N/A'
```

### 4. Test Your Scraper
```python
# Create a test file
if __name__ == '__main__':
    scraper = NewSourceScraper()
    jobs = scraper.scrape(keywords="python", max_pages=1)
    print(f"Found {len(jobs)} jobs")
    if jobs:
        print(f"Sample: {jobs[0]}")
```

## Popular Sources to Add

Here are some sources you might want to add:

### With Public APIs
- **Glassdoor** - glassdoor.com/developer
- **ZipRecruiter** - ziprecruiter.com/partners
- **CareerBuilder** - careerbuilder.com/share/api
- **Monster** - monster.com (check for API access)

### With RSS Feeds
- **Dice** - dice.com (tech jobs)
- **SimplyHired** - simplyhired.com
- **CareerJet** - careerjet.com

### Niche Boards
- **AngelList/Wellfound** - wellfound.com (startups)
- **Hacker News Who's Hiring** - news.ycombinator.com
- **GitHub Jobs Archive** - github.com/search
- **Dribbble** - dribbble.com/jobs (design)
- **Behance** - behance.net/joblist (creative)
- **ProductHunt Jobs** - producthunt.com/jobs
- **Y Combinator** - workatastartup.com

### Geographic Specific
- **EU Jobs** - eurodesk.eu
- **Canada Jobs** - jobbank.gc.ca
- **UK Jobs** - gov.uk/find-job
- **Australia Jobs** - seek.com.au

## Legal Considerations

Always ensure you:

1. Check the website's `robots.txt`
2. Review Terms of Service
3. Respect rate limits
4. Don't overload servers
5. Cache responses when possible
6. Use official APIs when available
7. Identify your bot with a proper User-Agent

## Testing

Test your scraper:

```bash
# Test in isolation
python -c "from scrapers import NewSourceScraper; s = NewSourceScraper(); print(len(s.scrape()))"

# Test through aggregator
python main.py --sources newsource --max-pages 1
```

## Need Help?

- Check existing scrapers in [scrapers.py](scrapers.py) for examples
- Review the [BaseScraper](scrapers.py) class
- Test with small page counts first
- Use `print()` statements for debugging
