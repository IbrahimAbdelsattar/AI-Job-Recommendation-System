"""
Text Processing Utilities
Clean and process job descriptions and other text data.
"""
import re
from bs4 import BeautifulSoup
from html import unescape

def clean_html(text: str) -> str:
    """
    Remove HTML tags and clean up text.
    
    Args:
        text: Raw text that may contain HTML
        
    Returns:
        Clean text without HTML tags
    """
    if not text:
        return ""
    
    # Decode HTML entities
    text = unescape(text)
    
    # Parse HTML and extract text
    soup = BeautifulSoup(text, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Get text
    text = soup.get_text()
    
    # Break into lines and remove leading/trailing space
    lines = (line.strip() for line in text.splitlines())
    
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    
    # Drop blank lines
    text = ' '.join(chunk for chunk in chunks if chunk)
    
    return text

def clean_description(description: str, max_length: int = 1000) -> str:
    """
    Clean and format job description.
    
    Args:
        description: Raw job description
        max_length: Maximum length to return
        
    Returns:
        Cleaned description
    """
    if not description:
        return "No description available"
    
    # Clean HTML
    clean_text = clean_html(description)
    
    # Remove excessive whitespace
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    # Remove common unwanted patterns
    unwanted_patterns = [
        r'Apply now.*$',
        r'Click here.*$',
        r'Visit our website.*$',
        r'\[.*?\]',  # Remove [brackets]
    ]
    
    for pattern in unwanted_patterns:
        clean_text = re.sub(pattern, '', clean_text, flags=re.IGNORECASE)
    
    # Trim to max length at sentence boundary if possible
    if len(clean_text) > max_length:
        # Try to cut at sentence end
        truncated = clean_text[:max_length]
        last_period = truncated.rfind('.')
        last_exclamation = truncated.rfind('!')
        last_question = truncated.rfind('?')
        
        last_sentence_end = max(last_period, last_exclamation, last_question)
        
        if last_sentence_end > max_length * 0.7:  # If we found a sentence end in last 30%
            clean_text = truncated[:last_sentence_end + 1]
        else:
            clean_text = truncated + '...'
    
    return clean_text.strip()

def extract_skills_from_text(text: str, max_skills: int = 15) -> list:
    """
    Extract technical skills from job description.
    
    Args:
        text: Job description or requirements text
        max_skills: Maximum number of skills to return
        
    Returns:
        List of detected skills
    """
    # Comprehensive list of tech skills
    skill_keywords = [
        # Programming Languages
        'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Ruby', 'PHP', 
        'Go', 'Rust', 'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB', 'Perl',
        
        # Frontend
        'React', 'Angular', 'Vue', 'Vue.js', 'Svelte', 'Next.js', 'Nuxt.js',
        'HTML', 'CSS', 'SASS', 'SCSS', 'Tailwind', 'Bootstrap', 'jQuery',
        
        # Backend
        'Node.js', 'Express', 'Django', 'Flask', 'FastAPI', 'Spring', 'Spring Boot',
        'ASP.NET', '.NET', 'Rails', 'Laravel', 'Symfony',
        
        # Databases
        'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch',
        'Cassandra', 'DynamoDB', 'Oracle', 'SQLite', 'MariaDB',
        
        # Cloud & DevOps
        'AWS', 'Azure', 'GCP', 'Google Cloud', 'Docker', 'Kubernetes', 'K8s',
        'Jenkins', 'GitLab', 'CircleCI', 'Travis CI', 'Terraform', 'Ansible',
        
        # Data & AI
        'Machine Learning', 'ML', 'Deep Learning', 'AI', 'TensorFlow', 'PyTorch',
        'Keras', 'Scikit-learn', 'Pandas', 'NumPy', 'Data Science', 'Big Data',
        'Spark', 'Hadoop', 'Airflow',
        
        # Mobile
        'React Native', 'Flutter', 'iOS', 'Android', 'Swift', 'Kotlin',
        
        # Other
        'Git', 'GitHub', 'REST API', 'GraphQL', 'Microservices', 'Agile', 'Scrum',
        'DevOps', 'CI/CD', 'Linux', 'Unix', 'Bash', 'PowerShell',
        'Jira', 'Confluence', 'Figma', 'Adobe XD'
    ]
    
    text_lower = text.lower()
    found_skills = []
    
    for skill in skill_keywords:
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_skills = []
    for skill in found_skills:
        skill_lower = skill.lower()
        if skill_lower not in seen:
            seen.add(skill_lower)
            unique_skills.append(skill)
    
    return unique_skills[:max_skills]

def clean_company_name(company: str) -> str:
    """Clean up company name."""
    if not company:
        return "Unknown Company"
    
    # Remove common suffixes for cleaner display
    company = re.sub(r'\s+(Inc\.|LLC|Ltd\.|Corp\.|Corporation|Limited)$', '', company, flags=re.IGNORECASE)
    
    return company.strip()

def clean_location(location: str) -> str:
    """Clean up location string."""
    if not location:
        return "Remote"
    
    # Remove excessive whitespace
    location = re.sub(r'\s+', ' ', location).strip()
    
    return location
