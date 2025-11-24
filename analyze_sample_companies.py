"""
Analyze a sample of Gen-Z hiring companies (first 10) to understand platform distribution
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

print("Analyzing Sample of Gen-Z Hiring Companies")
print("="*80)

generator = CompanyScraperGenerator()

# Load companies
all_companies = generator.load_companies_from_csv(csv_path)
print(f"\nLoaded {len(all_companies)} companies from CSV")

# Analyze first 10 as a sample
sample_companies = all_companies[:10]
print(f"\nAnalyzing first {len(sample_companies)} companies as a sample...")
print("="*80)

analysis = generator.analyze_companies(sample_companies)

# Show detailed results
print("\n" + "="*80)
print("DETAILED RESULTS:")
print("="*80)
for company in analysis['companies']:
    print(f"\n{company['name']}:")
    print(f"  Website: {company['website']}")
    print(f"  Careers URL: {company['careers_url']}")
    print(f"  Platform: {company['platform']}")

# Generate config
generator.generate_scraper_config(analysis, output_file='gen_z_sample_config.json')

print("\n" + "="*80)
print("Next: Review the platforms detected and decide if you want to:")
print("  1. Analyze all 100 companies (will take 10-15 minutes)")
print("  2. Manually review/update the careers URLs in the CSV")
print("  3. Proceed with creating scrapers for the detected platforms")
print("="*80)
