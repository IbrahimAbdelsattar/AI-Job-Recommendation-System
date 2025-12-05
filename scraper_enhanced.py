import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import quote_plus, urljoin
import re
import os
from dotenv import load_dotenv

load_dotenv()

class EnhancedJobScraper:
    """
    Enhanced multi-platform job scraper with more sources and better error handling.
    Supports: RemoteOK, Remotive, Arbeitnow, Findwork, Adzuna, GitHub Jobs Archive, 
    WeWorkRemotely, and more.
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/html',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        self.timeout = 15
        self.adzuna_app_id = os.getenv('ADZUNA_APP_ID', '')
        self.adzuna_app_key = os.getenv('ADZUNA_APP_KEY', '')
        
    def scrape_remoteok(self, keywords, limit=10):
        """Scrape RemoteOK - Popular remote job board with public API"""
        jobs = []
        try:
            url = "https://remoteok.com/api"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                job_listings = data[1:] if len(data) > 1 else []
                
                keywords_lower = [k.lower() for k in keywords]
                
                for job in job_listings[:50]:
                    if len(jobs) >= limit:
                        break
                        
                    job_text = f"{job.get('position', '')} {job.get('description', '')} {' '.join(job.get('tags', []))}".lower()
                    
                    if any(keyword in job_text for keyword in keywords_lower):
                        jobs.append({
                            'title': job.get('position', 'N/A'),
                            'company': job.get('company', 'N/A'),
                            'location': job.get('location', 'Remote'),
                            'description': job.get('description', '')[:500],
                            'skills': job.get('tags', [])[:10],
                            'platform': 'RemoteOK',
                            'url': job.get('url', '#'),
                            'posted_date': job.get('date', 'N/A'),
                            'salary': f"${job.get('salary_min', 'N/A')}-${job.get('salary_max', 'N/A')}" if job.get('salary_min') else 'Not specified',
                            'job_type': 'Remote'
                        })
                        
            print(f"✓ RemoteOK: Found {len(jobs)} jobs")
        except Exception as e:
            print(f"✗ RemoteOK error: {str(e)}")
            
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
                        
                    job_text = f"{job.get('title', '')} {job.get('description', '')} {job.get('category', '')} {job.get('job_type', '')}".lower()
                    
                    if any(keyword in job_text for keyword in keywords_lower):
                        jobs.append({
                            'title': job.get('title', 'N/A'),
                            'company': job.get('company_name', 'N/A'),
                            'location': 'Remote',
                            'description': job.get('description', '')[:500],
                            'skills': [job.get('category', 'General'), job.get('job_type', 'Full-time')],
                            'platform': 'Remotive',
                            'url': job.get('url', '#'),
                            'posted_date': job.get('publication_date', 'N/A'),
                            'salary': job.get('salary', 'Not specified'),
                            'job_type': job.get('job_type', 'Full-time')
                        })
                        
            print(f"✓ Remotive: Found {len(jobs)} jobs")
        except Exception as e:
            print(f"✗ Remotive error: {str(e)}")
            
        return jobs
    
    def scrape_arbeitnow(self, keywords, limit=10):
        """Scrape Arbeitnow - Free job board API for Europe"""
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
                        
                    job_text = f"{job.get('title', '')} {job.get('description', '')} {' '.join(job.get('tags', []))}".lower()
                    
                    if any(keyword in job_text for keyword in keywords_lower):
                        jobs.append({
                            'title': job.get('title', 'N/A'),
                            'company': job.get('company_name', 'N/A'),
                            'location': job.get('location', 'Remote'),
                            'description': job.get('description', '')[:500],
                            'skills': job.get('tags', [])[:10],
                            'platform': 'Arbeitnow',
                            'url': job.get('url', '#'),
                            'posted_date': job.get('created_at', 'N/A'),
                            'salary': 'Not specified',
                            'job_type': job.get('job_types', ['Full-time'])[0] if job.get('job_types') else 'Full-time'
                        })
                        
            print(f"✓ Arbeitnow: Found {len(jobs)} jobs")
        except Exception as e:
            print(f"✗ Arbeitnow error: {str(e)}")
            
        return jobs
    
    def scrape_adzuna(self, keywords, limit=10, location='us'):
        """Scrape Adzuna - Job search API (requires API key)"""
        jobs = []
        
        if not self.adzuna_app_id or not self.adzuna_app_key:
            print("⚠ Adzuna: API credentials not configured (optional)")
            return jobs
            
        try:
            search_query = ' '.join(keywords)
            url = f"https://api.adzuna.com/v1/api/jobs/{location}/search/1"
            params = {
                'app_id': self.adzuna_app_id,
                'app_key': self.adzuna_app_key,
                'results_per_page': limit,
                'what': search_query,
                'content-type': 'application/json'
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                job_listings = data.get('results', [])
                
                for job in job_listings:
                    jobs.append({
                        'title': job.get('title', 'N/A'),
                        'company': job.get('company', {}).get('display_name', 'N/A'),
                        'location': job.get('location', {}).get('display_name', 'N/A'),
                        'description': job.get('description', '')[:500],
                        'skills': keywords,
                        'platform': 'Adzuna',
                        'url': job.get('redirect_url', '#'),
                        'posted_date': job.get('created', 'N/A'),
                        'salary': f"${job.get('salary_min', 'N/A')}-${job.get('salary_max', 'N/A')}" if job.get('salary_min') else 'Not specified',
                        'job_type': job.get('contract_time', 'Full-time')
                    })
                        
            print(f"✓ Adzuna: Found {len(jobs)} jobs")
        except Exception as e:
            print(f"✗ Adzuna error: {str(e)}")
            
        return jobs
    
    def scrape_weworkremotely(self, keywords, limit=10):
        """Scrape WeWorkRemotely - Popular remote job board"""
        jobs = []
        try:
            url = "https://weworkremotely.com/remote-jobs/search"
            params = {'term': ' '.join(keywords)}
            
            response = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_listings = soup.find_all('li', class_='feature', limit=limit * 2)
                
                for listing in job_listings:
                    if len(jobs) >= limit:
                        break
                        
                    try:
                        title_elem = listing.find('span', class_='title')
                        company_elem = listing.find('span', class_='company')
                        region_elem = listing.find('span', class_='region')
                        link_elem = listing.find('a', href=True)
                        
                        if title_elem and company_elem:
                            jobs.append({
                                'title': title_elem.get_text(strip=True),
                                'company': company_elem.get_text(strip=True),
                                'location': region_elem.get_text(strip=True) if region_elem else 'Remote',
                                'description': 'View full details on WeWorkRemotely',
                                'skills': keywords,
                                'platform': 'WeWorkRemotely',
                                'url': urljoin('https://weworkremotely.com', link_elem['href']) if link_elem else '#',
                                'posted_date': 'Recently',
                                'salary': 'Not specified',
                                'job_type': 'Remote'
                            })
                    except Exception:
                        continue
                        
            print(f"✓ WeWorkRemotely: Found {len(jobs)} jobs")
        except Exception as e:
            print(f"✗ WeWorkRemotely error: {str(e)}")
            
        return jobs
    
    def scrape_findwork(self, keywords, limit=10):
        """Scrape Findwork.dev - Developer jobs"""
        jobs = []
        try:
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
                            'salary': 'Not specified',
                            'job_type': 'Full-time'
                        })
                    except Exception:
                        continue
                        
            print(f"✓ Findwork: Found {len(jobs)} jobs")
        except Exception as e:
            print(f"✗ Findwork error: {str(e)}")
            
        return jobs
    
    def scrape_himalayas(self, keywords, limit=10):
        """Scrape Himalayas.app - Remote jobs platform"""
        jobs = []
        try:
            search_query = '-'.join(keywords)
            url = f"https://himalayas.app/jobs/{search_query}"
            
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('div', class_='job-card', limit=limit)
                
                for card in job_cards:
                    try:
                        title_elem = card.find('h3')
                        company_elem = card.find('span', class_='company-name')
                        link_elem = card.find('a', href=True)
                        
                        if title_elem:
                            jobs.append({
                                'title': title_elem.get_text(strip=True),
                                'company': company_elem.get_text(strip=True) if company_elem else 'N/A',
                                'location': 'Remote',
                                'description': 'View full details on Himalayas',
                                'skills': keywords,
                                'platform': 'Himalayas',
                                'url': urljoin('https://himalayas.app', link_elem['href']) if link_elem else '#',
                                'posted_date': 'Recently',
                                'salary': 'Not specified',
                                'job_type': 'Remote'
                            })
                    except Exception:
                        continue
                        
            print(f"✓ Himalayas: Found {len(jobs)} jobs")
        except Exception as e:
            print(f"✗ Himalayas error: {str(e)}")
            
        return jobs
    
    def get_mock_jobs(self, keywords, limit=10):
        """Enhanced fallback mock jobs"""
        mock_jobs = [
            {
                'title': 'Senior Python Developer',
                'company': 'TechCorp AI',
                'location': 'Remote',
                'description': 'We are looking for a Python expert with experience in Flask, Django, and AI/ML frameworks. Build scalable backend systems.',
                'skills': ['Python', 'Flask', 'Django', 'AI', 'Machine Learning', 'REST API'],
                'platform': 'Mock Data',
                'url': '#',
                'posted_date': '2 days ago',
                'salary': '$80,000 - $120,000',
                'job_type': 'Full-time'
            },
            {
                'title': 'Full Stack Developer',
                'company': 'WebFlow Systems',
                'location': 'Remote',
                'description': 'Join our team to build modern web applications using React, Node.js, and MongoDB. Work on cutting-edge projects.',
                'skills': ['React', 'Node.js', 'MongoDB', 'JavaScript', 'TypeScript', 'GraphQL'],
                'platform': 'Mock Data',
                'url': '#',
                'posted_date': '1 week ago',
                'salary': '$70,000 - $100,000',
                'job_type': 'Full-time'
            },
            {
                'title': 'Data Scientist',
                'company': 'DataFlow Analytics',
                'location': 'Cairo, Egypt',
                'description': 'Analyze large datasets and build predictive models using Python and machine learning. Experience with deep learning preferred.',
                'skills': ['Python', 'Pandas', 'Scikit-learn', 'SQL', 'Data Analysis', 'TensorFlow'],
                'platform': 'Mock Data',
                'url': '#',
                'posted_date': '3 days ago',
                'salary': '$60,000 - $90,000',
                'job_type': 'Full-time'
            },
            {
                'title': 'Frontend Engineer',
                'company': 'Creative Web Studio',
                'location': 'Remote',
                'description': 'Build beautiful, responsive user interfaces with React and modern CSS. Focus on user experience and performance.',
                'skills': ['React', 'CSS', 'JavaScript', 'HTML', 'Tailwind', 'Next.js'],
                'platform': 'Mock Data',
                'url': '#',
                'posted_date': '5 days ago',
                'salary': '$65,000 - $95,000',
                'job_type': 'Full-time'
            },
            {
                'title': 'DevOps Engineer',
                'company': 'CloudTech Solutions',
                'location': 'Remote',
                'description': 'Manage cloud infrastructure, CI/CD pipelines, and containerized applications. AWS and Kubernetes experience required.',
                'skills': ['Docker', 'Kubernetes', 'AWS', 'CI/CD', 'Linux', 'Terraform'],
                'platform': 'Mock Data',
                'url': '#',
                'posted_date': '1 day ago',
                'salary': '$75,000 - $110,000',
                'job_type': 'Full-time'
            },
            {
                'title': 'Machine Learning Engineer',
                'company': 'AI Innovations',
                'location': 'Remote',
                'description': 'Develop and deploy machine learning models for production systems. Work with large-scale data and modern ML frameworks.',
                'skills': ['Python', 'TensorFlow', 'PyTorch', 'ML', 'Deep Learning', 'MLOps'],
                'platform': 'Mock Data',
                'url': '#',
                'posted_date': '4 days ago',
                'salary': '$90,000 - $130,000',
                'job_type': 'Full-time'
            },
            {
                'title': 'Backend Developer',
                'company': 'ServerSide Inc',
                'location': 'Remote',
                'description': 'Build scalable APIs and microservices using Node.js and Python. Experience with distributed systems is a plus.',
                'skills': ['Node.js', 'Python', 'PostgreSQL', 'REST API', 'GraphQL', 'Redis'],
                'platform': 'Mock Data',
                'url': '#',
                'posted_date': '6 days ago',
                'salary': '$70,000 - $105,000',
                'job_type': 'Full-time'
            },
            {
                'title': 'Mobile Developer',
                'company': 'AppCraft Studios',
                'location': 'Remote',
                'description': 'Create cross-platform mobile applications using React Native or Flutter. Build apps used by millions.',
                'skills': ['React Native', 'Flutter', 'Mobile Development', 'iOS', 'Android', 'Firebase'],
                'platform': 'Mock Data',
                'url': '#',
                'posted_date': '1 week ago',
                'salary': '$65,000 - $100,000',
                'job_type': 'Full-time'
            },
            {
                'title': 'UI/UX Designer',
                'company': 'Design Masters',
                'location': 'Remote',
                'description': 'Design beautiful and intuitive user interfaces. Work closely with developers to bring designs to life.',
                'skills': ['Figma', 'Adobe XD', 'UI Design', 'UX Research', 'Prototyping', 'User Testing'],
                'platform': 'Mock Data',
                'url': '#',
                'posted_date': '2 days ago',
                'salary': '$60,000 - $90,000',
                'job_type': 'Full-time'
            },
            {
                'title': 'Product Manager',
                'company': 'ProductFlow Inc',
                'location': 'Remote',
                'description': 'Lead product development from ideation to launch. Work with cross-functional teams to deliver value.',
                'skills': ['Product Management', 'Agile', 'Scrum', 'Analytics', 'Roadmapping', 'Stakeholder Management'],
                'platform': 'Mock Data',
                'url': '#',
                'posted_date': '3 days ago',
                'salary': '$85,000 - $120,000',
                'job_type': 'Full-time'
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
    Enhanced main function to scrape jobs from multiple platforms.
    
    Args:
        query: Search query or job title
        location: Location filter (optional)
        max_jobs: Maximum number of jobs to return
        
    Returns:
        List of job dictionaries with enhanced metadata
    """
    print(f"\n{'='*70}")
    print(f"🔍 Starting Enhanced Job Search")
    print(f"{'='*70}")
    print(f"Query: '{query}'")
    print(f"Location: '{location or 'Any location'}'")
    print(f"Target: {max_jobs} jobs")
    print(f"{'='*70}\n")
    
    # Extract keywords from query
    keywords = [word.strip() for word in query.split() if len(word.strip()) > 2]
    if not keywords:
        keywords = ['developer']
    
    scraper = EnhancedJobScraper()
    all_jobs = []
    
    # Calculate jobs per platform
    jobs_per_platform = max(3, max_jobs // 6)
    
    # Scrape from all platforms with error handling
    platforms = [
        ('RemoteOK', lambda: scraper.scrape_remoteok(keywords, limit=jobs_per_platform)),
        ('Remotive', lambda: scraper.scrape_remotive(keywords, limit=jobs_per_platform)),
        ('Arbeitnow', lambda: scraper.scrape_arbeitnow(keywords, limit=jobs_per_platform)),
        ('WeWorkRemotely', lambda: scraper.scrape_weworkremotely(keywords, limit=jobs_per_platform)),
        ('Findwork', lambda: scraper.scrape_findwork(keywords, limit=jobs_per_platform)),
        ('Himalayas', lambda: scraper.scrape_himalayas(keywords, limit=jobs_per_platform)),
        ('Adzuna', lambda: scraper.scrape_adzuna(keywords, limit=jobs_per_platform)),
    ]
    
    for platform_name, scrape_func in platforms:
        try:
            jobs = scrape_func()
            all_jobs.extend(jobs)
            time.sleep(0.5)  # Be respectful to servers
        except Exception as e:
            print(f"✗ {platform_name} failed: {e}")
    
    # Add mock data if needed
    if len(all_jobs) < 5:
        print(f"\n⚠ Adding supplementary mock data (found only {len(all_jobs)} real jobs)...")
        mock_jobs = scraper.get_mock_jobs(keywords, limit=max_jobs - len(all_jobs))
        all_jobs.extend(mock_jobs)
    
    # Remove duplicates
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        key = (job['title'].lower().strip(), job['company'].lower().strip())
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    
    # Limit to max_jobs
    result = unique_jobs[:max_jobs]
    
    # Add unique IDs
    for i, job in enumerate(result, 1):
        job['id'] = i
    
    print(f"\n{'='*70}")
    print(f"✅ Search Complete!")
    print(f"{'='*70}")
    print(f"Total Jobs Found: {len(result)}")
    print(f"Platforms Used: {len([p for p, _ in platforms])}")
    print(f"{'='*70}\n")
    
    return result


if __name__ == "__main__":
    # Test the enhanced scraper
    test_jobs = scrape_jobs("Python Developer", "Remote", max_jobs=15)
    
    print("\n📋 Sample Results:\n")
    for i, job in enumerate(test_jobs[:5], 1):
        print(f"{i}. {job['title']} at {job['company']}")
        print(f"   Platform: {job['platform']} | Location: {job['location']}")
        print(f"   Skills: {', '.join(job['skills'][:5])}")
        print(f"   Salary: {job['salary']}\n")
