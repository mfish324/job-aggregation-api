"""
Discover Workday URLs for companies detected as using Workday
"""

import sys
import requests
import re
import json

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Load companies from config
with open('gen_z_companies_full_config.json', 'r') as f:
    config = json.load(f)

workday_companies = [c for c in config['companies'] if c.get('platform') == 'workday']

print(f'Discovering Workday URLs for {len(workday_companies)} companies...\n')
print('='*80)

workday_configs = {}

for company in workday_companies:
    name = company['name']
    careers_url = company['careers_url']

    print(f'\n{name}:')
    print(f'  Checking: {careers_url}')

    try:
        response = requests.get(careers_url, timeout=10, allow_redirects=True)
        final_url = response.url

        # Check if it redirects to workday
        if 'myworkdayjobs.com' in final_url:
            print(f'  ✓ Found Workday: {final_url}')

            # Extract workday details
            # Format: https://{company}.{wd#}.myworkdayjobs.com/{site_id}
            match = re.search(r'https://([^.]+)\.(wd\d+)\.myworkdayjobs\.com/([^/?\s]+)', final_url)
            if match:
                company_id, wd_num, site_id = match.groups()

                workday_url = f'https://{company_id}.{wd_num}.myworkdayjobs.com/{site_id}'
                api_url = f'https://{company_id}.{wd_num}.myworkdayjobs.com/wday/cxs/{company_id}/{site_id}/jobs'

                workday_configs[name.lower().replace(' ', '_').replace('&', 'and')] = {
                    'name': name,
                    'url': workday_url,
                    'api_url': api_url
                }

                print(f'  Company ID: {company_id}')
                print(f'  Site ID: {site_id}')
                print(f'  API URL: {api_url}')
        else:
            print(f'  ✗ Not redirected to Workday')
            print(f'  Final URL: {final_url[:100]}...')

    except Exception as e:
        print(f'  ✗ ERROR: {e}')

print('\n' + '='*80)
print(f'\nSuccessfully discovered {len(workday_configs)} Workday configurations')

if workday_configs:
    print('\nAdd these to workday_scraper.py COMPANIES dict:\n')
    for key, config in workday_configs.items():
        print(f"        '{key}': {{")
        print(f"            'name': '{config['name']}',")
        print(f"            'url': '{config['url']}',")
        print(f"            'api_url': '{config['api_url']}'")
        print(f"        }},")
