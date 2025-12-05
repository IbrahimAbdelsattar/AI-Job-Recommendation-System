"""
Wuzzuf Job Scraper
Scrapes jobs from Wuzzuf.net (Egypt's leading job site).
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import time
from urllib.parse import quote_plus

class WuzzufFetcher:
    """Scrapes job listings from Wuzzuf"""
    
    BASE_URL = "https://wuzzuf.net/search/jobs/"
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://wuzzuf.net/'
        }
    
    def search_jobs(self, query: str, limit: int = 20) -> List[Dict]:
        """
        Search for jobs on Wuzzuf.
        
        Args:
            query: Job title or keywords
            limit: Number of results (approximate)
            
        Returns:
            List of job dictionaries
        """
        jobs = []
        page = 0
        
        while len(jobs) < limit:
            try:
                # Wuzzuf uses start parameter for pagination (0, 1, 2...)
                url = f"{self.BASE_URL}?q={quote_plus(query)}&start={page}"
                
                response = requests.get(url, headers=self.headers, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find all h2 tags as they usually contain job titles
                h2_tags = soup.find_all('h2')
                
                if not h2_tags:
                    print(f"No h2 tags found on Wuzzuf page {page}")
                    break
                    
                found_on_page = 0
                for h2 in h2_tags:
                    if len(jobs) >= limit:
                        break
                        
                    try:
                        # Check if it's a job title (has a link)
                        link = h2.find('a')
                        if not link:
                            continue
                            
                        # Get container (usually the parent div of the h2, or the grandparent)
                        # We'll try to extract data relative to the h2
                        container = h2.find_parent('div')
                        if not container:
                            continue
                            
                        job = self._extract_job_data(h2, container)
                        if job:
                            jobs.append(job)
                            found_on_page += 1
                    except Exception as e:
                        # print(f"Error extracting Wuzzuf job: {e}")
                        continue
                
                if found_on_page == 0:
                    break
                    
                page += 1
                time.sleep(1) # Be polite
                
            except Exception as e:
                print(f"Error scraping Wuzzuf: {e}")
                break
                
        return jobs
    
    def _extract_job_data(self, title_tag, container) -> Dict:
        """Extract data from a single job card"""
        
        # Title & URL
        link_tag = title_tag.find('a')
        if not link_tag:
            return None
            
        title = link_tag.get_text(strip=True)
        url = link_tag['href']
        if not url.startswith('http'):
            url = f"https://wuzzuf.net{url}"
            
        # Company
        # Look for the first link after the title that is NOT the title
        # Usually in the same container
        company = "Unknown Company"
        company_tag = container.find('a', {'class': lambda x: x and 'css-17s97q8' in x}) # Try specific class first
        
        if not company_tag:
            # Fallback: find all links in container
            links = container.find_all('a')
            for l in links:
                if l != link_tag and 'jobs/p' not in l.get('href', ''): # Avoid job links
                    company = l.get_text(strip=True).replace(' -', '')
                    break
        else:
            company = company_tag.get_text(strip=True).replace(' -', '')
            
        # Location
        location = "Egypt"
        location_tag = container.find('span', {'class': lambda x: x and 'css-5wys0k' in x})
        if location_tag:
            location = location_tag.get_text(strip=True)
        else:
            # Fallback: look for text that looks like a location (e.g. "Cairo, Egypt")
            spans = container.find_all('span')
            for span in spans:
                text = span.get_text(strip=True)
                if ',' in text and any(c in text for c in ['Cairo', 'Giza', 'Egypt', 'Alexandria']):
                    location = text
                    break
        
        # Date
        posted_date = "Recent"
        # Try to find "posted" text
        divs = container.find_all('div')
        for div in divs:
            text = div.get_text(strip=True)
            if 'ago' in text and len(text) < 20:
                posted_date = text
                break
            
        # Skills
        skills = []
        # Wuzzuf usually puts skills in tags at the bottom
        # Look for a container with many links or small divs
        # This is hard to guess generically, but let's try finding the last div with links
        
        # Description
        description = f"Job at {company} in {location}."
        
        return {
            'id': f"wuzzuf-{abs(hash(url))}",
            'title': title,
            'company': company,
            'location': location,
            'description': description,
            'url': url,
            'salary': 'Confidential',
            'posted_date': posted_date,
            'platform': 'Wuzzuf',
            'skills': skills
        }
