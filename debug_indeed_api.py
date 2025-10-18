import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

api_key = os.getenv('RAPIDAPI_KEY')
api_host = 'indeed-jobs-api.p.rapidapi.com'

headers = {
    'X-RapidAPI-Key': api_key,
    'X-RapidAPI-Host': api_host
}

# Test with the exact endpoint
url = f"https://{api_host}/indeed-us/"

print("="*80)
print("INDEED API DEBUG")
print("="*80)

# Try different parameter formats
test_cases = [
    {'keyword': 'python', 'location': 'california', 'offset': '0'},
    {'keyword': 'python developer', 'location': 'New York', 'offset': '0'},
    {'keyword': 'software engineer', 'location': 'Remote', 'offset': '0'},
    {'keyword': 'developer', 'location': 'USA', 'offset': '0'},
]

for i, params in enumerate(test_cases, 1):
    print(f"\n--- Test {i} ---")
    print(f"Parameters: {params}")

    response = requests.get(url, headers=headers, params=params, timeout=10)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()

        # Check for error
        if isinstance(data, dict) and 'Error' in data:
            print(f"[FAIL] API Error: {data['Error']}")
            continue

        # Try to find jobs
        if isinstance(data, list):
            print(f"[OK] Found {len(data)} jobs!")
            if len(data) > 0:
                print(f"First job title: {data[0].get('title', 'N/A')}")
                break
        elif isinstance(data, dict):
            jobs = data.get('results') or data.get('jobs') or data.get('data') or []
            if len(jobs) > 0:
                print(f"[OK] Found {len(jobs)} jobs!")
                print(f"First job title: {jobs[0].get('title', 'N/A')}")
                break
            else:
                print("[FAIL] No jobs found in response")
    else:
        print(f"[FAIL] HTTP Error: {response.status_code}")
