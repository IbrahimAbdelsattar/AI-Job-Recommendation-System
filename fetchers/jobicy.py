"""
Jobicy API Integration
Fetcher for remote jobs from Jobicy.
"""
import requests
from typing import List, Dict, Optional

class JobicyFetcher:
    """Fetches remote job listings from Jobicy API"""
    
    BASE_URL = "https://jobicy.com/api/v2/remote-jobs"
    
    def search_jobs(
        self,
        query: str = "",
        count: int = 20,
        geo: str = ""
    ) -> List[Dict]:
        """
        Search for jobs on Jobicy.
        
        Args:
            query: Job category or tag (Jobicy is category based mostly)
            count: Number of results (max 50)
            geo: Region (usa, uk, etc.)
            
        Returns:
            List of job dictionaries
        """
        try:
            # Jobicy API is simple, mostly RSS-like structure in JSON
            # We can filter by count, geo, industry, tag
            params = {
                'count': min(count, 50)
            }
            
            if geo:
                params['geo'] = geo
            if query:
                params['tag'] = query # Using tag for query as it's most similar
                
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('success'):
                return []
                
            jobs = []
            for result in data.get('jobs', []):
                # Filter by query if not using tag param (or double check)
                if query.lower() in result.get('jobTitle', '').lower() or \
                   query.lower() in result.get('jobDescription', '').lower():
                    job = self._transform_job(result)
                    jobs.append(job)
            
            return jobs
            
        except Exception as e:
            print(f"Error fetching Jobicy jobs: {e}")
            return []
    
    def _transform_job(self, raw_job: Dict) -> Dict:
        """Transform Jobicy job format to standardized format"""
        
        return {
            'id': str(raw_job.get('id', '')),
            'title': raw_job.get('jobTitle', 'Unknown Position'),
            'company': raw_job.get('companyName', 'Unknown Company'),
            'location': f"Remote ({raw_job.get('jobGeo', 'Anywhere')})",
            'description': raw_job.get('jobDescription', 'No description available'),
            'url': raw_job.get('url', ''),
            'salary': raw_job.get('annualSalaryMin', 'Not specified') + (' - ' + raw_job.get('annualSalaryMax') if raw_job.get('annualSalaryMax') else ''),
            'posted_date': raw_job.get('pubDate', ''),
            'platform': 'Jobicy',
            'skills': raw_job.get('jobIndustry', []) # Using industry as skills proxy
        }
