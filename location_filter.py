"""
Location filtering utilities for US-based jobs
"""

import re

# US states (full names and abbreviations)
US_STATES = {
    # Full names
    'alabama', 'alaska', 'arizona', 'arkansas', 'california', 'colorado',
    'connecticut', 'delaware', 'florida', 'georgia', 'hawaii', 'idaho',
    'illinois', 'indiana', 'iowa', 'kansas', 'kentucky', 'louisiana',
    'maine', 'maryland', 'massachusetts', 'michigan', 'minnesota',
    'mississippi', 'missouri', 'montana', 'nebraska', 'nevada',
    'new hampshire', 'new jersey', 'new mexico', 'new york',
    'north carolina', 'north dakota', 'ohio', 'oklahoma', 'oregon',
    'pennsylvania', 'rhode island', 'south carolina', 'south dakota',
    'tennessee', 'texas', 'utah', 'vermont', 'virginia', 'washington',
    'west virginia', 'wisconsin', 'wyoming',
    # Abbreviations
    'al', 'ak', 'az', 'ar', 'ca', 'co', 'ct', 'de', 'fl', 'ga', 'hi', 'id',
    'il', 'in', 'ia', 'ks', 'ky', 'la', 'me', 'md', 'ma', 'mi', 'mn', 'ms',
    'mo', 'mt', 'ne', 'nv', 'nh', 'nj', 'nm', 'ny', 'nc', 'nd', 'oh', 'ok',
    'or', 'pa', 'ri', 'sc', 'sd', 'tn', 'tx', 'ut', 'vt', 'va', 'wa', 'wv',
    'wi', 'wy',
    # Common variations
    'washington dc', 'dc', 'district of columbia', 'puerto rico', 'pr'
}

# US cities (major cities for better matching)
US_MAJOR_CITIES = {
    'new york', 'los angeles', 'chicago', 'houston', 'phoenix', 'philadelphia',
    'san antonio', 'san diego', 'dallas', 'san jose', 'austin', 'jacksonville',
    'fort worth', 'columbus', 'charlotte', 'san francisco', 'indianapolis',
    'seattle', 'denver', 'washington', 'boston', 'el paso', 'nashville',
    'detroit', 'oklahoma city', 'portland', 'las vegas', 'memphis',
    'louisville', 'baltimore', 'milwaukee', 'albuquerque', 'tucson', 'fresno',
    'mesa', 'sacramento', 'atlanta', 'kansas city', 'colorado springs', 'omaha',
    'raleigh', 'miami', 'long beach', 'virginia beach', 'oakland', 'minneapolis',
    'tulsa', 'tampa', 'arlington', 'new orleans', 'nyc', 'la', 'sf', 'dc'
}

# Keywords that indicate US location
US_INDICATORS = {
    'usa', 'us', 'united states', 'america', 'american', 'nationwide'
}

# Keywords that indicate remote but US-allowed
REMOTE_US_KEYWORDS = {
    'us remote', 'usa remote', 'remote us', 'remote usa', 'remote (us)',
    'remote - us', 'remote united states', 'us only', 'usa only'
}

# Non-US country indicators (to exclude)
NON_US_COUNTRIES = {
    'uk', 'united kingdom', 'england', 'london', 'scotland', 'wales',
    'canada', 'canadian', 'toronto', 'vancouver', 'montreal', 'ottawa',
    'australia', 'australian', 'sydney', 'melbourne', 'brisbane',
    'germany', 'german', 'berlin', 'munich', 'frankfurt',
    'france', 'french', 'paris', 'lyon',
    'spain', 'spanish', 'madrid', 'barcelona',
    'italy', 'italian', 'rome', 'milan',
    'netherlands', 'dutch', 'amsterdam',
    'india', 'indian', 'bangalore', 'mumbai', 'delhi', 'hyderabad',
    'china', 'chinese', 'beijing', 'shanghai',
    'japan', 'japanese', 'tokyo', 'osaka',
    'singapore', 'hong kong', 'brazil', 'mexico', 'argentina',
    'ireland', 'dublin', 'sweden', 'stockholm', 'norway', 'oslo',
    'denmark', 'copenhagen', 'finland', 'helsinki', 'poland', 'warsaw',
    'portugal', 'lisbon', 'israel', 'tel aviv', 'south africa',
    'new zealand', 'auckland', 'europe', 'european', 'asia', 'emea',
    'worldwide', 'global', 'international', 'anywhere'
}


def is_us_location(location_str: str) -> bool:
    """
    Determine if a location string indicates a US-based job

    Args:
        location_str: Location string from job posting

    Returns:
        True if location is US-based, False otherwise
    """
    if not location_str:
        # Empty location - could be remote, allow it
        return True

    location_lower = location_str.lower().strip()

    # Empty or very short - allow
    if len(location_lower) < 2:
        return True

    # Check for explicit non-US countries first (highest priority)
    for country in NON_US_COUNTRIES:
        if country in location_lower:
            return False

    # Check for US indicators
    for indicator in US_INDICATORS:
        if indicator in location_lower:
            return True

    # Check for remote US keywords
    for keyword in REMOTE_US_KEYWORDS:
        if keyword in location_lower:
            return True

    # Check for US states
    words = re.findall(r'\b[a-z]+\b', location_lower)
    for word in words:
        if word in US_STATES:
            return True

    # Check for US cities
    for city in US_MAJOR_CITIES:
        if city in location_lower:
            return True

    # Check for state abbreviations with comma pattern (e.g., "City, CA")
    state_pattern = r',\s*([a-z]{2})\b'
    state_match = re.search(state_pattern, location_lower)
    if state_match and state_match.group(1) in US_STATES:
        return True

    # If it says "remote" without country specification, allow it
    # (assumes US companies posting on US job boards)
    if location_lower in ['remote', 'remote work', 'work from home', 'wfh']:
        return True

    # If we can't determine, be conservative and exclude
    return False


def filter_us_jobs(jobs: list) -> list:
    """
    Filter a list of jobs to only US-based positions

    Args:
        jobs: List of job dictionaries with 'location' field

    Returns:
        List of US-based jobs
    """
    us_jobs = []

    for job in jobs:
        location = job.get('location', '')
        if is_us_location(location):
            us_jobs.append(job)

    return us_jobs


def get_location_stats(jobs: list) -> dict:
    """
    Get statistics about job locations

    Args:
        jobs: List of job dictionaries

    Returns:
        Dictionary with location statistics
    """
    total = len(jobs)
    us_jobs = filter_us_jobs(jobs)
    us_count = len(us_jobs)

    # Get non-US jobs for analysis
    non_us_jobs = [j for j in jobs if j not in us_jobs]

    # Sample non-US locations
    non_us_locations = [j.get('location', 'N/A') for j in non_us_jobs[:10]]

    return {
        'total_jobs': total,
        'us_jobs': us_count,
        'non_us_jobs': total - us_count,
        'us_percentage': (us_count / total * 100) if total > 0 else 0,
        'sample_non_us_locations': non_us_locations
    }


# Test function
if __name__ == "__main__":
    # Test cases
    test_locations = [
        ("New York, NY", True),
        ("San Francisco, CA", True),
        ("Remote, USA", True),
        ("United States", True),
        ("TX", True),
        ("California", True),
        ("Remote (US)", True),
        ("London, UK", False),
        ("Toronto, Canada", False),
        ("Berlin, Germany", False),
        ("Remote, Worldwide", False),
        ("Bangalore, India", False),
        ("Remote", True),  # Ambiguous but allow
        ("", True),  # Empty - allow
        ("Austin", True),  # US city
        ("Sydney", False),  # Australian city
        ("Europe", False),
        ("Remote - United States", True),
    ]

    print("Location Filter Tests:")
    print("-" * 60)

    for location, expected in test_locations:
        result = is_us_location(location)
        status = "[OK]" if result == expected else "[FAIL]"
        print(f"{status} {location:30s} -> {result} (expected {expected})")
