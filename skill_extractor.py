"""
Skill Extractor - Parse technical skills from job descriptions
"""

import re
import json

# Common technical skills to extract
TECHNICAL_SKILLS = {
    # Programming Languages
    'python', 'javascript', 'java', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin',
    'go', 'rust', 'typescript', 'scala', 'r', 'perl', 'matlab', 'sql',

    # Web Frameworks
    'react', 'angular', 'vue', 'django', 'flask', 'fastapi', 'express', 'node.js',
    'nodejs', 'spring', 'rails', 'laravel', 'asp.net', 'nextjs', 'nuxt',

    # Mobile
    'ios', 'android', 'react native', 'flutter', 'xamarin',

    # Cloud Platforms
    'aws', 'azure', 'gcp', 'google cloud', 'heroku', 'digitalocean', 'cloudflare',

    # DevOps & Tools
    'docker', 'kubernetes', 'k8s', 'jenkins', 'gitlab', 'github actions', 'circleci',
    'terraform', 'ansible', 'chef', 'puppet', 'vagrant',

    # Databases
    'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'cassandra',
    'dynamodb', 'oracle', 'sql server', 'sqlite', 'mariadb', 'neo4j',

    # Data Science & ML
    'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'keras',
    'scikit-learn', 'pandas', 'numpy', 'jupyter', 'spark', 'hadoop',

    # Other Technologies
    'git', 'linux', 'unix', 'bash', 'api', 'rest', 'graphql', 'microservices',
    'agile', 'scrum', 'ci/cd', 'test-driven development', 'tdd'
}

def extract_skills(text):
    """
    Extract technical skills from job description text

    Args:
        text: Job description or title text

    Returns:
        List of unique skills found (lowercase)
    """
    if not text:
        return []

    text_lower = text.lower()
    found_skills = set()

    # Check for each skill
    for skill in TECHNICAL_SKILLS:
        # Use word boundaries for exact matches
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            # Normalize skill name for consistency
            normalized = skill.replace(' ', '_').replace('.', '')
            found_skills.add(normalized)

    return sorted(list(found_skills))

def skills_to_json(skills):
    """
    Convert skills list to JSON string

    Args:
        skills: List of skill strings

    Returns:
        JSON string of skills array
    """
    if not skills:
        return json.dumps([])
    return json.dumps(skills)

def extract_and_format_skills(text):
    """
    Extract skills from text and return as JSON string

    Args:
        text: Job description or title text

    Returns:
        JSON string of skills array
    """
    skills = extract_skills(text)
    return skills_to_json(skills)

# Test function
if __name__ == "__main__":
    test_descriptions = [
        "We're looking for a Python developer with experience in Django, PostgreSQL, and AWS.",
        "Senior Software Engineer - React, Node.js, TypeScript, Docker, Kubernetes",
        "Data Scientist needed: Python, TensorFlow, Pandas, Machine Learning, AWS"
    ]

    print("Testing Skill Extractor\n" + "="*60)
    for desc in test_descriptions:
        skills = extract_skills(desc)
        print(f"\nDescription: {desc[:80]}...")
        print(f"Skills found: {skills}")
        print(f"JSON: {skills_to_json(skills)}")
