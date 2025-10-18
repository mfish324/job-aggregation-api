"""
Test RapidAPI Indeed API Connection
This will help you figure out which Indeed API you need to subscribe to
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('RAPIDAPI_KEY')

if not api_key:
    print("ERROR: RAPIDAPI_KEY not found in .env file")
    exit(1)

print("="*80)
print("RAPIDAPI INDEED API TESTER")
print("="*80)
print(f"\nAPI Key: {api_key[:10]}... (length: {len(api_key)})")
print()

# List of popular Indeed APIs on RapidAPI
indeed_apis = [
    {
        'name': 'Indeed Jobs API (vuesdata)',
        'host': 'indeed-jobs-api.p.rapidapi.com',
        'url': 'https://indeed-jobs-api.p.rapidapi.com/',
        'params': {'keyword': 'python', 'location': 'Remote', 'offset': 0},
        'subscribe': 'https://rapidapi.com/vuesdata/api/indeed-jobs-api'
    },
    {
        'name': 'Indeed jobs scraper API',
        'host': 'indeed-jobs-scraper-api.p.rapidapi.com',
        'url': 'https://indeed-jobs-scraper-api.p.rapidapi.com/jobs',
        'params': {'query': 'python', 'location': 'Remote'},
        'subscribe': 'https://rapidapi.com/bebity-bebity-default/api/indeed-jobs-scraper-api'
    },
    {
        'name': 'Indeed11 API',
        'host': 'indeed11.p.rapidapi.com',
        'url': 'https://indeed11.p.rapidapi.com/search',
        'params': {'query': 'python', 'location': 'Remote'},
        'subscribe': 'https://rapidapi.com/jaypat87/api/indeed11'
    },
    {
        'name': 'Indeed12 API',
        'host': 'indeed12.p.rapidapi.com',
        'url': 'https://indeed12.p.rapidapi.com/',
        'params': {'query': 'python developer', 'location': 'Remote'},
        'subscribe': 'https://rapidapi.com/search/indeed12'
    }
]

print("Testing each Indeed API on RapidAPI...\n")

working_apis = []
subscription_needed = []

for i, api in enumerate(indeed_apis, 1):
    print(f"{i}. Testing: {api['name']}")
    print(f"   Host: {api['host']}")

    headers = {
        'X-RapidAPI-Key': api_key,
        'X-RapidAPI-Host': api['host']
    }

    try:
        response = requests.get(api['url'], headers=headers, params=api['params'], timeout=10)

        if response.status_code == 200:
            data = response.json()
            jobs_found = 0

            # Try to count jobs from response
            if isinstance(data, list):
                jobs_found = len(data)
            elif isinstance(data, dict):
                jobs_found = len(data.get('results', data.get('jobs', data.get('data', []))))

            print(f"   Status: [OK] WORKS! Found {jobs_found} jobs")
            print(f"   Response preview: {str(data)[:100]}...")
            working_apis.append(api)

        elif response.status_code == 403:
            print(f"   Status: [FAIL] Not subscribed (403 Forbidden)")
            print(f"   -> Subscribe at: {api['subscribe']}")
            subscription_needed.append(api)

        elif response.status_code == 429:
            print(f"   Status: [WARN] Rate limit exceeded (429)")
            print(f"   -> You might be subscribed but hit the limit")

        else:
            print(f"   Status: [FAIL] Error {response.status_code}")
            print(f"   Response: {response.text[:100]}")

    except Exception as e:
        print(f"   Status: [FAIL] Connection error: {e}")

    print()

# Summary
print("="*80)
print("SUMMARY")
print("="*80)

if working_apis:
    print(f"\n[OK] WORKING APIs ({len(working_apis)}):")
    for api in working_apis:
        print(f"\n  • {api['name']}")
        print(f"    Host: {api['host']}")
        print(f"    Add to .env: RAPIDAPI_INDEED_HOST={api['host']}")
else:
    print("\n[FAIL] No working APIs found.")

if subscription_needed:
    print(f"\n[WARN] APIs that need subscription ({len(subscription_needed)}):")
    for api in subscription_needed:
        print(f"\n  • {api['name']}")
        print(f"    Subscribe: {api['subscribe']}")
        print(f"    1. Click 'Subscribe to Test'")
        print(f"    2. Choose 'Basic' (FREE) plan")
        print(f"    3. Re-run this test")

if not working_apis and not subscription_needed:
    print("\n[WARN] Could not test any APIs. Possible issues:")
    print("  - API key might be invalid")
    print("  - Network connectivity issues")
    print("  - RapidAPI service might be down")

print("\n" + "="*80)
print("NEXT STEPS")
print("="*80)

if working_apis:
    api = working_apis[0]
    print(f"\n1. Your API is already working with: {api['name']}")
    print(f"\n2. Update your .env file:")
    print(f"   RAPIDAPI_INDEED_HOST={api['host']}")
    print(f"\n3. Run the scraper:")
    print(f"   python indeed_rapidapi_scraper.py")
else:
    print("\n1. Go to RapidAPI and subscribe to an Indeed API:")
    print("   https://rapidapi.com/search/indeed")
    print("\n2. Choose one with a FREE tier (look for 'Basic' plan)")
    print("\n3. Click 'Subscribe to Test' → Select 'Basic' (FREE)")
    print("\n4. Re-run this test: python test_rapidapi_indeed.py")

print("\n" + "="*80)
print("\nYour RapidAPI Dashboard: https://rapidapi.com/developer/apps")
print("="*80 + "\n")
