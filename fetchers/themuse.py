"""
The Muse API Integration
Fetcher for job listings from The Muse.
"""
import requests
from typing import List, Dict, Optional

class TheMuseFetcher:
    """Fetches job listings from The Muse API"""
    
    BASE_URL = "https://www.themuse.com/api/public/jobs"
    
    def search_jobs(
        self,
        category: str = "",
        location: str = "",
        page: int = 0
    ) -> List[Dict]:
        """
        Search for jobs on The Muse.
        
        Args:
            category: Job category (e.g. Software Engineering)
            location: Job location
            page: Page number
            
        Returns:
            List of job dictionaries
        """
        try:
            params = {
                'page': page,
                'descending': 'true'
            }
            
            if category:
                params['category'] = category
            if location:
                params['location'] = location
                
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            jobs = []
            for result in data.get('results', []):
                job = self._transform_job(result)
                jobs.append(job)
            
            return jobs
            
        except Exception as e:
            print(f"Error fetching The Muse jobs: {e}")
            return []
    
    def _transform_job(self, raw_job: Dict) -> Dict:
        """Transform The Muse job format to standardized format"""
        
        locations = [loc.get('name') for loc in raw_job.get('locations', [])]
        location_str = ", ".join(locations) if locations else "Unknown"
        
        return {
            'id': str(raw_job.get('id', '')),
            'title': raw_job.get('name', 'Unknown Position'),
            'company': raw_job.get('company', {}).get('name', 'Unknown Company'),
            'location': location_str,
            'description': raw_job.get('contents', 'No description available'),
            'url': raw_job.get('refs', {}).get('landing_page', ''),
            'salary': 'Not specified',
            'posted_date': raw_job.get('publication_date', ''),
            'platform': 'The Muse',
            'skills': [cat.get('name') for cat in raw_job.get('categories', [])]
        }
