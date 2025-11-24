"""
Analyze all 100 Gen-Z hiring companies to detect their careers platforms
This will take 10-15 minutes as we check each company's website
"""

import sys
from company_scraper_generator import CompanyScraperGenerator

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Path to the CSV file
csv_path = r"C:\Users\matto\Documents\Gamed_Jobs\gen_z_hiring_companies.csv"

print("Analyzing ALL Gen-Z Hiring Companies")
print("="*80)
print("This will take 10-15 minutes as we check each company's careers page...")
print("="*80)

generator = CompanyScraperGenerator()

# Load companies
all_companies = generator.load_companies_from_csv(csv_path)
print(f"\nLoaded {len(all_companies)} companies from CSV")
print("\nStarting analysis...\n")

# Analyze all companies
analysis = generator.analyze_companies(all_companies)

# Generate config
generator.generate_scraper_config(analysis, output_file='gen_z_companies_full_config.json')

# Show summary by category
print("\n" + "="*80)
print("COMPANIES BY PLATFORM:")
print("="*80)

# Group companies by platform
from collections import defaultdict
platform_companies = defaultdict(list)
for company in analysis['companies']:
    platform_companies[company['platform']].append(company['name'])

for platform in sorted(platform_companies.keys()):
    companies = platform_companies[platform]
    print(f"\n{platform.upper()} ({len(companies)} companies):")
    for company in sorted(companies):
        print(f"  - {company}")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
print(f"\nResults saved to: gen_z_companies_full_config.json")
print("\nNext steps:")
print("  1. Review the configuration file")
print("  2. Create scrapers for detected platforms")
print("  3. Integrate scrapers into aggregator")
