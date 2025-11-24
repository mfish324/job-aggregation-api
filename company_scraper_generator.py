"""
Company Scraper Generator
Automatically creates scrapers for companies based on their careers page platform
"""

import csv
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import re
import json


class CareersPlatformDetector:
    """Detect which ATS/platform a company uses for their careers page"""

    PLATFORMS = {
        'workday': [
            'myworkdayjobs.com',
            'wd1.myworkdayjobs.com',
            'wd5.myworkdayjobs.com'
        ],
        'greenhouse': [
            'greenhouse.io',
            'boards.greenhouse.io',
            'grnh.se'
        ],
        'lever': [
            'lever.co',
            'jobs.lever.co'
        ],
        'ashbyhq': [
            'ashbyhq.com',
            'jobs.ashbyhq.com'
        ],
        'jobvite': [
            'jobvite.com',
            'jobs.jobvite.com'
        ],
        'icims': [
            'icims.com',
            'careers.icims.com'
        ],
        'taleo': [
            'taleo.net',
            'careersection'
        ],
        'smartrecruiters': [
            'smartrecruiters.com',
            'jobs.smartrecruiters.com'
        ],
        'breezy': [
            'breezy.hr'
        ],
        'bamboohr': [
            'bamboohr.com'
        ]
    }

    def detect_platform(self, careers_url: str) -> Optional[str]:
        """
        Detect which ATS platform a careers URL uses

        Args:
            careers_url: Company's careers page URL

        Returns:
            Platform name or None if unknown
        """
        careers_url_lower = careers_url.lower()

        # Check URL patterns
        for platform, patterns in self.PLATFORMS.items():
            for pattern in patterns:
                if pattern in careers_url_lower:
                    return platform

        # Try to fetch the page and check meta tags / content
        try:
            response = requests.get(careers_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                content = response.text.lower()

                # Check for platform indicators in page content
                for platform, patterns in self.PLATFORMS.items():
                    for pattern in patterns:
                        if pattern in content:
                            return platform

                # Check for specific meta tags or scripts
                if 'greenhouse' in content or 'grnh.se' in content:
                    return 'greenhouse'
                elif 'lever.co' in content:
                    return 'lever'
                elif 'workday' in content:
                    return 'workday'

        except Exception as e:
            print(f"Error detecting platform for {careers_url}: {e}")

        return 'custom'  # Unknown platform, needs custom scraper


class CompanyScraperGenerator:
    """Generate scrapers for companies based on their platform"""

    def __init__(self):
        self.detector = CareersPlatformDetector()

    def load_companies_from_csv(self, csv_path: str) -> List[Dict]:
        """
        Load company list from CSV

        Expected CSV columns: Company Name, Company Website

        Args:
            csv_path: Path to CSV file

        Returns:
            List of company dictionaries
        """
        companies = []

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get('Company Name', row.get('company_name', row.get('name', '')))
                website = row.get('Company Website', row.get('website', row.get('company_website', '')))

                # Clean website URL
                if website and not website.startswith('http'):
                    website = f'https://{website}'

                # Try to construct careers URL from website
                # Common patterns: /careers, /jobs, jobs.company.com, careers.company.com
                careers_url = row.get('careers_url', row.get('careers_page', ''))
                if not careers_url and website:
                    # Try common patterns
                    base = website.rstrip('/')
                    careers_url = f"{base}/careers"  # Most common pattern

                companies.append({
                    'name': name,
                    'website': website,
                    'careers_url': careers_url
                })

        return companies

    def analyze_companies(self, companies: List[Dict]) -> Dict:
        """
        Analyze companies and detect their platforms

        Args:
            companies: List of company dicts

        Returns:
            Analysis summary with platform breakdown
        """
        results = {
            'total': len(companies),
            'by_platform': {},
            'companies': []
        }

        print(f"\nAnalyzing {len(companies)} companies...")
        print("="*80)

        for i, company in enumerate(companies, 1):
            name = company['name']
            careers_url = company['careers_url']

            print(f"{i:3d}. {name:40} ", end='')

            if not careers_url:
                platform = 'no_url'
                print("❌ No careers URL")
            else:
                platform = self.detector.detect_platform(careers_url)
                print(f"✓ {platform}")

            company['platform'] = platform
            results['companies'].append(company)

            # Update platform counts
            results['by_platform'][platform] = results['by_platform'].get(platform, 0) + 1

        print("\n" + "="*80)
        print("PLATFORM BREAKDOWN:")
        print("="*80)
        for platform, count in sorted(results['by_platform'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {platform:20} {count:3d} companies")

        return results

    def generate_scraper_config(self, analysis: Dict, output_file: str = 'company_scrapers_config.json'):
        """
        Generate configuration file for company scrapers

        Args:
            analysis: Analysis results from analyze_companies()
            output_file: Path to output JSON file
        """
        config = {
            'companies': analysis['companies'],
            'summary': {
                'total': analysis['total'],
                'by_platform': analysis['by_platform']
            }
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)

        print(f"\n✓ Configuration saved to {output_file}")
        print(f"\nNext steps:")
        print(f"  1. Review the configuration file")
        print(f"  2. We'll create platform-specific scrapers for:")
        for platform, count in sorted(analysis['by_platform'].items(), key=lambda x: x[1], reverse=True):
            print(f"     - {platform}: {count} companies")
        print(f"  3. Integrate scrapers into the aggregator")


def main():
    """Example usage"""
    print("Company Scraper Generator")
    print("="*80)
    print("\nThis tool will:")
    print("  1. Read your CSV file with company information")
    print("  2. Detect which careers platform each company uses")
    print("  3. Generate a configuration file")
    print("  4. Create scrapers based on platform types")
    print("\nExpected CSV format:")
    print("  company_name, website, careers_url")
    print("  Example: Apple, https://www.apple.com, https://jobs.apple.com")
    print("="*80)

    # Prompt for CSV file
    csv_path = input("\nEnter path to your CSV file: ").strip()

    if not csv_path:
        print("\n❌ No file path provided")
        return

    try:
        generator = CompanyScraperGenerator()

        # Load companies
        companies = generator.load_companies_from_csv(csv_path)
        print(f"\n✓ Loaded {len(companies)} companies from CSV")

        # Analyze platforms
        analysis = generator.analyze_companies(companies)

        # Generate config
        generator.generate_scraper_config(analysis)

    except FileNotFoundError:
        print(f"\n❌ File not found: {csv_path}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
