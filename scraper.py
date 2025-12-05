import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import quote_plus, urljoin
import re

class JobScraper:
    """
    Multi-platform job scraper that searches open-source and public job platforms.
    Supports: RemoteOK, GitHub Jobs (archived but still accessible), Remotive, etc.
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.timeout = 10
        
    def scrape_remoteok(self, keywords, limit=10):
        """Scrape RemoteOK - a popular remote job board with public API"""
        jobs = []
        try:
            # RemoteOK has a public API
            url = f"https://remoteok.com/api"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                # First item is metadata, skip it
                job_listings = data[1:] if len(data) > 1 else []
                
                keywords_lower = [k.lower() for k in keywords]
                
                for job in job_listings[:50]:  # Check first 50 jobs
                    if len(jobs) >= limit:
                        break
                        
                    # Check if job matches keywords
                    job_text = f"{job.get('position', '')} {job.get('description', '')} {' '.join(job.get('tags', []))}".lower()
                    
                    if any(keyword in job_text for keyword in keywords_lower):
                        jobs.append({
                            'title': job.get('position', 'N/A'),
                            'company': job.get('company', 'N/A'),
                            'location': job.get('location', 'Remote'),
                            'description': job.get('description', '')[:500],
                            'skills': job.get('tags', []),
                            'platform': 'RemoteOK',
                            'url': job.get('url', '#'),
                            'posted_date': job.get('date', 'N/A'),
                            'salary': f"${job.get('salary_min', 'N/A')}-${job.get('salary_max', 'N/A')}" if job.get('salary_min') else 'Not specified'
                        })
                        
            print(f"RemoteOK: Found {len(jobs)} jobs")
        except Exception as e:
            print(f"Error scraping RemoteOK: {str(e)}")
            
        return jobs
    
    def scrape_remotive(self, keywords, limit=10):
        """Scrape Remotive.io - Remote jobs platform with public API"""
        jobs = []
        try:
            url = "https://remotive.com/api/remote-jobs"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                job_listings = data.get('jobs', [])
                
                keywords_lower = [k.lower() for k in keywords]
                
                for job in job_listings:
                    if len(jobs) >= limit:
                        break
                        
                    # Check if job matches keywords
                    job_text = f"{job.get('title', '')} {job.get('description', '')} {job.get('category', '')}".lower()
                    
                    if any(keyword in job_text for keyword in keywords_lower):
                        jobs.append({
                            'title': job.get('title', 'N/A'),
                            'company': job.get('company_name', 'N/A'),
                            'location': 'Remote',
                            'description': job.get('description', '')[:500],
                            'skills': [job.get('category', 'General')],
                            'platform': 'Remotive',
                            'url': job.get('url', '#'),
                            'posted_date': job.get('publication_date', 'N/A'),
                            'salary': job.get('salary', 'Not specified')
                        })
                        
            print(f"Remotive: Found {len(jobs)} jobs")
        except Exception as e:
            print(f"Error scraping Remotive: {str(e)}")
            
        return jobs
    
    def scrape_arbeitnow(self, keywords, limit=10):
        """Scrape Arbeitnow - Free job board API"""
        jobs = []
        try:
            url = "https://www.arbeitnow.com/api/job-board-api"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                job_listings = data.get('data', [])
                
                keywords_lower = [k.lower() for k in keywords]
                
                for job in job_listings:
                    if len(jobs) >= limit:
                        break
                        
                    # Check if job matches keywords
                    job_text = f"{job.get('title', '')} {job.get('description', '')} {' '.join(job.get('tags', []))}".lower()
                    
                    if any(keyword in job_text for keyword in keywords_lower):
                        jobs.append({
                            'title': job.get('title', 'N/A'),
                            'company': job.get('company_name', 'N/A'),
                            'location': job.get('location', 'Remote'),
                            'description': job.get('description', '')[:500],
                            'skills': job.get('tags', []),
                            'platform': 'Arbeitnow',
                            'url': job.get('url', '#'),
                            'posted_date': job.get('created_at', 'N/A'),
                            'salary': 'Not specified'
                        })
                        
            print(f"Arbeitnow: Found {len(jobs)} jobs")
        except Exception as e:
            print(f"Error scraping Arbeitnow: {str(e)}")
            
        return jobs
    
    def scrape_findwork(self, keywords, limit=10):
        """Scrape Findwork.dev - Developer jobs"""
        jobs = []
        try:
            # Findwork has a simple structure we can scrape
            search_query = '+'.join(keywords)
            url = f"https://findwork.dev/jobs?search={quote_plus(search_query)}"
            
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('li', class_='job', limit=limit)
                
                for card in job_cards:
                    try:
                        title_elem = card.find('h2')
                        company_elem = card.find('a', class_='company')
                        location_elem = card.find('span', class_='location')
                        link_elem = card.find('a', href=True)
                        
                        jobs.append({
                            'title': title_elem.get_text(strip=True) if title_elem else 'N/A',
                            'company': company_elem.get_text(strip=True) if company_elem else 'N/A',
                            'location': location_elem.get_text(strip=True) if location_elem else 'Remote',
                            'description': 'View job details on Findwork.dev',
                            'skills': keywords,
                            'platform': 'Findwork',
                            'url': urljoin('https://findwork.dev', link_elem['href']) if link_elem else '#',
                            'posted_date': 'Recently',
                            'salary': 'Not specified'
                        })
                    except Exception as e:
                        continue
                        
            print(f"Findwork: Found {len(jobs)} jobs")
        except Exception as e:
            print(f"Error scraping Findwork: {str(e)}")
            
        return jobs
    
    def get_mock_jobs(self, keywords, limit=10):
        """Fallback mock jobs if scraping fails"""
        mock_jobs = [
            {
                'title': 'Senior Python Developer',
                'company': 'TechCorp AI',
                'location': 'Remote',
                'description': 'We are looking for a Python expert with experience in Flask, Django, and AI/ML frameworks.',
                'skills': ['Python', 'Flask', 'Django', 'AI', 'Machine Learning'],
                'platform': 'Mock Data',
                'url': '#',
                'posted_date': '2 days ago',
                'salary': '$80,000 - $120,000'
            },
            {
                'title': 'Full Stack Developer',
                'company': 'WebFlow Systems',
                'location': 'Remote',
                'description': 'Join our team to build modern web applications using React, Node.js, and MongoDB.',
                'skills': ['React', 'Node.js', 'MongoDB', 'JavaScript', 'TypeScript'],
                'platform': 'Mock Data',
                'url': '#',
                'posted_date': '1 week ago',
                'salary': '$70,000 - $100,000'
            },
            {
                'title': 'Data Scientist',
                'company': 'DataFlow Analytics',
                'location': 'Cairo, Egypt',
                'description': 'Analyze large datasets and build predictive models using Python and machine learning.',
                'skills': ['Python', 'Pandas', 'Scikit-learn', 'SQL', 'Data Analysis'],
                'platform': 'Mock Data',
                'url': '#',
                'posted_date': '3 days ago',
                'salary': '$60,000 - $90,000'
            },
            {
                'title': 'Frontend Engineer',
                'company': 'Creative Web Studio',
                'location': 'Remote',
                'description': 'Build beautiful, responsive user interfaces with React and modern CSS.',
                'skills': ['React', 'CSS', 'JavaScript', 'HTML', 'Tailwind'],
                'platform': 'Mock Data',
                'url': '#',
                'posted_date': '5 days ago',
                'salary': '$65,000 - $95,000'
            },
            {
                'title': 'DevOps Engineer',
                'company': 'CloudTech Solutions',
                'location': 'Remote',
                'description': 'Manage cloud infrastructure, CI/CD pipelines, and containerized applications.',
                'skills': ['Docker', 'Kubernetes', 'AWS', 'CI/CD', 'Linux'],
                'platform': 'Mock Data',
                'url': '#',
                'posted_date': '1 day ago',
                'salary': '$75,000 - $110,000'
            },
            {
                'title': 'Machine Learning Engineer',
                'company': 'AI Innovations',
                'location': 'Remote',
                'description': 'Develop and deploy machine learning models for production systems.',
                'skills': ['Python', 'TensorFlow', 'PyTorch', 'ML', 'Deep Learning'],
                'platform': 'Mock Data',
                'url': '#',
                'posted_date': '4 days ago',
                'salary': '$90,000 - $130,000'
            },
            {
                'title': 'Backend Developer',
                'company': 'ServerSide Inc',
                'location': 'Remote',
                'description': 'Build scalable APIs and microservices using Node.js and Python.',
                'skills': ['Node.js', 'Python', 'PostgreSQL', 'REST API', 'GraphQL'],
                'platform': 'Mock Data',
                'url': '#',
                'posted_date': '6 days ago',
                'salary': '$70,000 - $105,000'
            },
            {
                'title': 'Mobile Developer',
                'company': 'AppCraft Studios',
                'location': 'Remote',
                'description': 'Create cross-platform mobile applications using React Native or Flutter.',
                'skills': ['React Native', 'Flutter', 'Mobile Development', 'iOS', 'Android'],
                'platform': 'Mock Data',
                'url': '#',
                'posted_date': '1 week ago',
                'salary': '$65,000 - $100,000'
            }
        ]
        
        # Filter based on keywords
        keywords_lower = [k.lower() for k in keywords]
        filtered = []
        
        for job in mock_jobs:
            job_text = f"{job['title']} {job['description']} {' '.join(job['skills'])}".lower()
            if any(keyword in job_text for keyword in keywords_lower):
                filtered.append(job)
                
        return filtered[:limit] if filtered else mock_jobs[:limit]


def scrape_jobs(query, location='', max_jobs=20):
    """
    Main function to scrape jobs from multiple platforms.
    
    Args:
        query: Search query or job title
        location: Location filter (optional)
        max_jobs: Maximum number of jobs to return
        
    Returns:
        List of job dictionaries
    """
    print(f"\n{'='*60}")
    print(f"Starting job search for: '{query}' in '{location or 'Any location'}'")
    print(f"{'='*60}\n")
    
    # Extract keywords from query
    keywords = [word.strip() for word in query.split() if len(word.strip()) > 2]
    if not keywords:
        keywords = ['developer']  # Default keyword
    
    scraper = JobScraper()
    all_jobs = []
    
    # Scrape from multiple platforms
    jobs_per_platform = max(5, max_jobs // 4)  # Distribute across platforms
    
    # Try real platforms first
    try:
        print("Searching RemoteOK...")
        all_jobs.extend(scraper.scrape_remoteok(keywords, limit=jobs_per_platform))
        time.sleep(1)  # Be respectful to servers
    except Exception as e:
        print(f"RemoteOK failed: {e}")
    
    try:
        print("Searching Remotive...")
        all_jobs.extend(scraper.scrape_remotive(keywords, limit=jobs_per_platform))
        time.sleep(1)
    except Exception as e:
        print(f"Remotive failed: {e}")
    
    try:
        print("Searching Arbeitnow...")
        all_jobs.extend(scraper.scrape_arbeitnow(keywords, limit=jobs_per_platform))
        time.sleep(1)
    except Exception as e:
        print(f"Arbeitnow failed: {e}")
    
    # If we don't have enough jobs, add mock data
    if len(all_jobs) < 5:
        print("\nAdding supplementary mock data...")
        mock_jobs = scraper.get_mock_jobs(keywords, limit=max_jobs - len(all_jobs))
        all_jobs.extend(mock_jobs)
    
    # Remove duplicates based on title and company
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        key = (job['title'].lower(), job['company'].lower())
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    
    # Limit to max_jobs
    result = unique_jobs[:max_jobs]
    
    print(f"\n{'='*60}")
    print(f"Search complete! Found {len(result)} unique jobs")
    print(f"{'='*60}\n")
    
    return result


if __name__ == "__main__":
    # Test the scraper
    test_jobs = scrape_jobs("Python Developer", "Remote", max_jobs=10)
    
    print("\nSample Results:")
    for i, job in enumerate(test_jobs[:3], 1):
        print(f"\n{i}. {job['title']} at {job['company']}")
        print(f"   Platform: {job['platform']}")
        print(f"   Location: {job['location']}")
        print(f"   Skills: {', '.join(job['skills'][:5])}")
