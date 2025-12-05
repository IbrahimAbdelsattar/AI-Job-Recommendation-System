"""
Job Data Validator
Validates scraped job data to prevent hallucinations and ensure data quality.
"""
import re
from typing import Dict, List, Optional
from urllib.parse import urlparse

class JobValidator:
    """Validates job data for accuracy and completeness"""
    
    # Suspicious patterns that indicate fake/mock data
    SUSPICIOUS_PATTERNS = [
        r'lorem ipsum',
        r'example\.com',
        r'test company',
        r'sample job',
        r'placeholder',
        r'mock data',
        r'n/a',
        r'not specified',
        r'#$',  # Just a hash symbol as URL
    ]
    
    # Required fields for a valid job
    REQUIRED_FIELDS = ['title', 'company', 'location', 'description', 'platform', 'url']
    
    def __init__(self):
        self.validation_stats = {
            'total': 0,
            'valid': 0,
            'invalid': 0,
            'warnings': 0
        }
    
    def validate_job(self, job: Dict) -> tuple[bool, List[str]]:
        """
        Validate a single job posting.
        
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in job or not job[field]:
                issues.append(f"Missing required field: {field}")
        
        if issues:
            return False, issues
        
        # Validate title
        if len(job['title']) < 3:
            issues.append("Title too short")
        elif len(job['title']) > 200:
            issues.append("Title suspiciously long")
        
        # Validate company
        if len(job['company']) < 2:
            issues.append("Company name too short")
        elif job['company'].lower() in ['n/a', 'unknown', 'none', 'test']:
            issues.append("Invalid company name")
        
        # Validate URL
        url_valid, url_issue = self._validate_url(job['url'])
        if not url_valid:
            issues.append(url_issue)
        
        # Check for suspicious patterns
        job_text = f"{job['title']} {job['company']} {job['description']}".lower()
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, job_text):
                issues.append(f"Suspicious pattern detected: {pattern}")
        
        # Validate description
        if len(job['description']) < 20:
            issues.append("Description too short")
        
        # Check if it's mock data
        if job.get('platform') == 'Mock Data':
            issues.append("Flagged as mock data")
        
        is_valid = len(issues) == 0
        self.validation_stats['total'] += 1
        if is_valid:
            self.validation_stats['valid'] += 1
        else:
            self.validation_stats['invalid'] += 1
        
        return is_valid, issues
    
    def _validate_url(self, url: str) -> tuple[bool, Optional[str]]:
        """Validate job URL"""
        if not url or url == '#':
            return False, "Invalid or placeholder URL"
        
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False, "Malformed URL"
            
            # Check for suspicious domains
            suspicious_domains = ['example.com', 'test.com', 'localhost']
            if any(domain in parsed.netloc for domain in suspicious_domains):
                return False, "Suspicious domain"
            
            return True, None
        except Exception:
            return False, "URL parsing failed"
    
    def validate_batch(self, jobs: List[Dict]) -> List[Dict]:
        """
        Validate a batch of jobs and return only valid ones.
        
        Args:
            jobs: List of job dictionaries
            
        Returns:
            List of valid jobs only
        """
        valid_jobs = []
        
        for job in jobs:
            is_valid, issues = self.validate_job(job)
            if is_valid:
                valid_jobs.append(job)
            else:
                print(f"⚠ Rejected job: {job.get('title', 'Unknown')} - {', '.join(issues[:2])}")
        
        return valid_jobs
    
    def get_stats(self) -> Dict:
        """Get validation statistics"""
        return self.validation_stats.copy()
    
    def reset_stats(self):
        """Reset validation statistics"""
        self.validation_stats = {
            'total': 0,
            'valid': 0,
            'invalid': 0,
            'warnings': 0
        }
