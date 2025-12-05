"""
Adzuna Job API Integration
Official API for fetching real job listings from Adzuna.
"""
import requests
import os
from typing import List, Dict, Optional

class AdzunaFetcher:
    """Fetches job listings from Adzuna API"""
    
    BASE_URL = "https://api.adzuna.com/v1/api/jobs"
    
    def __init__(self, app_id: Optional[str] = None, app_key: Optional[str] = None):
        """
        Initialize Adzuna fetcher with credentials.
        
        Args:
            app_id: Adzuna App ID (defaults to env var ADZUNA_APP_ID)
            app_key: Adzuna App Key (defaults to env var ADZUNA_APP_KEY)
        """
        self.app_id = app_id or os.getenv('ADZUNA_APP_ID')
        self.app_key = app_key or os.getenv('ADZUNA_APP_KEY')
        
        if not self.app_id or not self.app_key:
            raise ValueError(
                "Adzuna credentials not found. Please set ADZUNA_APP_ID and ADZUNA_APP_KEY "
                "in your .env file or pass them to the constructor."
            )
    
    def search_jobs(
        self,
        query: str,
        location: str = "us",
        results_per_page: int = 20,
        page: int = 1,
        sort_by: str = "relevance"
    ) -> List[Dict]:
        """
        Search for jobs on Adzuna.
        
        Args:
            query: Job title or keywords to search for
            location: Country code (us, uk, ca, au, etc.)
            results_per_page: Number of results to return (max 50)
            page: Page number for pagination
            sort_by: Sort order - 'relevance', 'date', or 'salary'
            
        Returns:
            List of job dictionaries with standardized fields
        """
        try:
            # Build API URL
            url = f"{self.BASE_URL}/{location}/search/{page}"
            
            # Prepare parameters
            params = {
                'app_id': self.app_id,
                'app_key': self.app_key,
                'results_per_page': min(results_per_page, 50),
                'what': query,
                'sort_by': sort_by
            }
            
            # Make request
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Transform to standardized format
            jobs = []
            for result in data.get('results', []):
                job = self._transform_job(result)
                jobs.append(job)
            
            return jobs
            
        except requests.exceptions.RequestException as e:
            print(f"Adzuna API Error: {e}")
            return []
        except Exception as e:
            print(f"Error processing Adzuna results: {e}")
            return []
    
    def _transform_job(self, raw_job: Dict) -> Dict:
        """
        Transform Adzuna job format to our standardized format.
        
        Args:
            raw_job: Raw job data from Adzuna API
            
        Returns:
            Standardized job dictionary
        """
        # Extract salary information
        salary_min = raw_job.get('salary_min')
        salary_max = raw_job.get('salary_max')
        
        if salary_min and salary_max:
            salary = f"${salary_min:,.0f} - ${salary_max:,.0f}"
        elif salary_min:
            salary = f"${salary_min:,.0f}+"
        elif salary_max:
            salary = f"Up to ${salary_max:,.0f}"
        else:
            salary = "Not specified"
        
        # Extract location
        location_parts = []
        if raw_job.get('location', {}).get('display_name'):
            location_parts.append(raw_job['location']['display_name'])
        elif raw_job.get('location', {}).get('area'):
            location_parts.extend(raw_job['location']['area'])
        
        location = ', '.join(location_parts) if location_parts else "Remote"
        
        # Build standardized job object
        return {
            'id': raw_job.get('id', ''),
            'title': raw_job.get('title', 'Unknown Position'),
            'company': raw_job.get('company', {}).get('display_name', 'Unknown Company'),
            'location': location,
            'description': raw_job.get('description', 'No description available'),
            'url': raw_job.get('redirect_url', ''),
            'salary': salary,
            'contract_type': raw_job.get('contract_type', 'Full-time'),
            'contract_time': raw_job.get('contract_time', 'permanent'),
            'created': raw_job.get('created', ''),
            'category': raw_job.get('category', {}).get('label', 'Other'),
            'platform': 'Adzuna',
            'skills': self._extract_skills(raw_job.get('description', ''))
        }
    
    def _extract_skills(self, description: str) -> List[str]:
        """
        Extract common tech skills from job description.
        This is a simple keyword-based extraction.
        
        Args:
            description: Job description text
            
        Returns:
            List of detected skills
        """
        # Common tech skills to look for
        common_skills = [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Ruby', 'PHP', 'Go', 'Rust',
            'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'Spring', 'Express',
            'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'Git',
            'Machine Learning', 'AI', 'Data Science', 'Deep Learning', 'TensorFlow', 'PyTorch',
            'REST API', 'GraphQL', 'Microservices', 'Agile', 'Scrum', 'DevOps'
        ]
        
        description_lower = description.lower()
        found_skills = []
        
        for skill in common_skills:
            if skill.lower() in description_lower:
                found_skills.append(skill)
        
        return found_skills[:10]  # Limit to top 10 skills


def fetch_jobs(query: str, location: str = "us", max_results: int = 20) -> List[Dict]:
    """
    Convenience function to fetch jobs from Adzuna.
    
    Args:
        query: Job search query
        location: Country code (default: us)
        max_results: Maximum number of results to return
        
    Returns:
        List of job dictionaries
    """
    try:
        fetcher = AdzunaFetcher()
        jobs = fetcher.search_jobs(query, location, results_per_page=max_results)
        return jobs
    except Exception as e:
        print(f"Error fetching jobs: {e}")
        return []
