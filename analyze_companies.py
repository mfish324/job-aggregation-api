"""
Analyze the 100 Gen-Z hiring companies
"""

from company_scraper_generator import CompanyScraperGenerator

# Path to the CSV file
csv_path = r"C:\Users\matto\Documents\Gamed_Jobs\gen_z_hiring_companies.csv"

print("Analyzing Gen-Z Hiring Companies")
print("="*80)

generator = CompanyScraperGenerator()

# Load companies
companies = generator.load_companies_from_csv(csv_path)
print(f"\n✓ Loaded {len(companies)} companies from CSV")

# Analyze platforms (this will take a while - checking each company's careers page)
print("\nThis will take several minutes as we detect each company's platform...")
analysis = generator.analyze_companies(companies)

# Generate config
generator.generate_scraper_config(analysis, output_file='gen_z_companies_config.json')

print("\nDone!")
