"""
Company Scraper Factory
Dynamically creates scrapers for companies based on their platform and configuration
"""

import json
from typing import Dict, List, Optional
from platform_scrapers import (
    GreenhouseScraper,
    LeverScraper,
    AshbyHQScraper,
    TaleoScraper,
    iCIMSScraper,
    create_scraper_for_platform
)
from company_scrapers import (
    GoogleCareersScraper,
    AmazonCareersScraper,
    AppleCareersScraper,
    MicrosoftCareersScraper,
    MetaCareersScraper,
    TeslaCareersScraper
)
from workday_scraper import WorkdayScraper


class CompanyScraperFactory:
    """Factory for creating company-specific scrapers"""

    # Manual overrides for companies with existing custom scrapers
    CUSTOM_SCRAPERS = {
        'Google/Alphabet': GoogleCareersScraper,
        'Google': GoogleCareersScraper,
        'Amazon': AmazonCareersScraper,
        'Apple': AppleCareersScraper,
        'Microsoft': MicrosoftCareersScraper,
        'Meta': MetaCareersScraper,
        'Tesla': TeslaCareersScraper,
    }

    def __init__(self, config_file: str = 'gen_z_companies_full_config.json'):
        """
        Initialize factory with company configuration

        Args:
            config_file: Path to JSON config file with company data
        """
        self.config_file = config_file
        self.companies = []
        self.load_config()

    def load_config(self):
        """Load company configuration from JSON file"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.companies = config.get('companies', [])
            print(f"Loaded {len(self.companies)} companies from config")
        except FileNotFoundError:
            print(f"Config file not found: {self.config_file}")
            print("Run analyze_all_companies.py first to generate the config")
        except Exception as e:
            print(f"Error loading config: {e}")

    def create_scraper(self, company_name: str):
        """
        Create a scraper for a specific company

        Args:
            company_name: Name of the company

        Returns:
            Scraper instance or None if company not found/supported
        """
        # Check if we have a custom scraper
        if company_name in self.CUSTOM_SCRAPERS:
            return self.CUSTOM_SCRAPERS[company_name]()

        # Find company in config
        company = next((c for c in self.companies if c['name'] == company_name), None)
        if not company:
            print(f"Company '{company_name}' not found in config")
            return None

        platform = company.get('platform')

        if platform in ['greenhouse', 'lever', 'ashbyhq', 'workday', 'taleo', 'icims']:
            # Use platform-specific scraper
            return create_scraper_for_platform(company, platform)
        else:
            print(f"⚠ {company_name}: Platform '{platform}' not yet supported")
            return None

    def create_all_scrapers(self) -> Dict[str, object]:
        """
        Create scrapers for all companies in config

        Returns:
            Dictionary mapping company names to scraper instances
        """
        scrapers = {}

        for company in self.companies:
            name = company['name']
            scraper = self.create_scraper(name)
            if scraper:
                scrapers[name] = scraper

        print(f"\nCreated {len(scrapers)} scrapers out of {len(self.companies)} companies")
        return scrapers

    def get_companies_by_platform(self, platform: str) -> List[Dict]:
        """Get all companies using a specific platform"""
        return [c for c in self.companies if c.get('platform') == platform]

    def get_supported_companies(self) -> List[str]:
        """Get list of companies that we can scrape"""
        supported = []

        for company in self.companies:
            name = company['name']
            platform = company.get('platform')

            # Check if custom scraper exists or platform is supported
            if name in self.CUSTOM_SCRAPERS:
                supported.append(name)
            elif platform in ['greenhouse', 'lever', 'ashbyhq', 'workday', 'taleo', 'icims']:
                supported.append(name)

        return supported

    def get_summary(self) -> Dict:
        """Get summary of companies and their scraping status"""
        summary = {
            'total_companies': len(self.companies),
            'scrapable': 0,
            'custom_scrapers': 0,
            'platform_scrapers': 0,
            'not_supported': 0,
            'by_platform': {}
        }

        for company in self.companies:
            name = company['name']
            platform = company.get('platform', 'unknown')

            # Update platform count
            summary['by_platform'][platform] = summary['by_platform'].get(platform, 0) + 1

            # Check if scrapable
            if name in self.CUSTOM_SCRAPERS:
                summary['scrapable'] += 1
                summary['custom_scrapers'] += 1
            elif platform in ['greenhouse', 'lever', 'ashbyhq', 'workday', 'taleo', 'icims']:
                summary['scrapable'] += 1
                summary['platform_scrapers'] += 1
            else:
                summary['not_supported'] += 1

        return summary


def main():
    """Test the factory"""
    print("Company Scraper Factory")
    print("="*80)

    factory = CompanyScraperFactory()

    if not factory.companies:
        print("\n❌ No companies loaded. Run analyze_all_companies.py first.")
        return

    # Show summary
    summary = factory.get_summary()
    print(f"\nSUMMARY:")
    print(f"  Total companies: {summary['total_companies']}")
    print(f"  Scrapable: {summary['scrapable']}")
    print(f"    - Custom scrapers: {summary['custom_scrapers']}")
    print(f"    - Platform scrapers: {summary['platform_scrapers']}")
    print(f"  Not yet supported: {summary['not_supported']}")

    print(f"\nPlatform breakdown:")
    for platform, count in sorted(summary['by_platform'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {platform:20} {count:3d} companies")

    # Show supported companies
    supported = factory.get_supported_companies()
    print(f"\n{len(supported)} companies ready to scrape:")
    for name in sorted(supported)[:20]:  # Show first 20
        print(f"  - {name}")
    if len(supported) > 20:
        print(f"  ... and {len(supported) - 20} more")

    print("\n" + "="*80)


if __name__ == "__main__":
    main()
