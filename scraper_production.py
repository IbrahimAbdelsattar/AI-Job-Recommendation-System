"""
Production-Grade Job Scraper
Enhanced scraper with validation, logging, and better error handling.
"""
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import quote_plus, urljoin
import re
from validators.job_validator import JobValidator
from utils.scraper_logger import ScraperLogger
from utils.text_processor import (
    clean_description, 
    extract_skills_from_text, 
    clean_company_name, 
    clean_location
)
from fetchers.adzuna import AdzunaFetcher

from fetchers.jobicy import JobicyFetcher
from fetchers.wuzzuf import WuzzufFetcher

class ProductionJobScraper:
    """
    Production-grade multi-platform job scraper with validation and logging.
    """
    
    def __init__(self, enable_validation=True, enable_logging=True):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/html',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        self.timeout = 15
        self.validator = JobValidator() if enable_validation else None
        self.logger = ScraperLogger() if enable_logging else None
        
    def scrape_remoteok(self, keywords, limit=10):
        """Scrape RemoteOK with validation and improved text processing"""
        platform = "RemoteOK"
        jobs = []
        
        if self.logger:
            self.logger.log_platform_attempt(platform)
        
        try:
            url = "https://remoteok.com/api"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            job_listings = data[1:] if len(data) > 1 else []
            
            keywords_lower = [k.lower() for k in keywords]
            
            for job in job_listings[:50]:
                if len(jobs) >= limit:
                    break
                    
                job_text = f"{job.get('position', '')} {job.get('description', '')} {' '.join(job.get('tags', []))}".lower()
                
                if any(keyword in job_text for keyword in keywords_lower):
                    # Get raw description
                    raw_description = job.get('description', '')
                    
                    # Clean and process description
                    clean_desc = clean_description(raw_description, max_length=1000)
                    
                    # Extract skills from description and tags
                    tags = job.get('tags', [])
                    desc_skills = extract_skills_from_text(raw_description)
                    all_skills = list(set(tags + desc_skills))[:15]  # Combine and limit
                    
                    job_data = {
                        'title': job.get('position', 'N/A'),
                        'company': clean_company_name(job.get('company', 'N/A')),
                        'location': clean_location(job.get('location', 'Remote')),
                        'description': clean_desc,
                        'skills': all_skills,
                        'platform': platform,
                        'url': job.get('url', ''),
                        'posted_date': job.get('date', 'N/A'),
                        'salary': f"${job.get('salary_min', 'N/A')}-${job.get('salary_max', 'N/A')}" if job.get('salary_min') else 'Not specified',
                        'job_type': 'Remote'
                    }
                    
                    # Validate if enabled
                    if self.validator:
                        is_valid, issues = self.validator.validate_job(job_data)
                        if is_valid:
                            jobs.append(job_data)
                    else:
                        jobs.append(job_data)
            
            if self.logger:
                self.logger.log_platform_success(platform, len(jobs))
                
        except Exception as e:
            if self.logger:
                self.logger.log_platform_failure(platform, str(e))
            print(f"✗ {platform} error: {str(e)}")
            
        return jobs
    
    def scrape_remotive(self, keywords, limit=10):
        """Scrape Remotive with validation and improved text processing"""
        platform = "Remotive"
        jobs = []
        
        if self.logger:
            self.logger.log_platform_attempt(platform)
        
        try:
            url = "https://remotive.com/api/remote-jobs"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            job_listings = data.get('jobs', [])
            
            keywords_lower = [k.lower() for k in keywords]
            
            for job in job_listings:
                if len(jobs) >= limit:
                    break
                    
                job_text = f"{job.get('title', '')} {job.get('description', '')} {job.get('category', '')}".lower()
                
                if any(keyword in job_text for keyword in keywords_lower):
                    # Get raw description
                    raw_description = job.get('description', '')
                    
                    # Clean description
                    clean_desc = clean_description(raw_description, max_length=1000)
                    
                    # Extract skills
                    desc_skills = extract_skills_from_text(raw_description)
                    category = job.get('category', 'General')
                    job_type = job.get('job_type', 'Full-time')
                    all_skills = list(set([category, job_type] + desc_skills))[:15]
                    
                    job_data = {
                        'title': job.get('title', 'N/A'),
                        'company': clean_company_name(job.get('company_name', 'N/A')),
                        'location': 'Remote',
                        'description': clean_desc,
                        'skills': all_skills,
                        'platform': platform,
                        'url': job.get('url', ''),
                        'posted_date': job.get('publication_date', 'N/A'),
                        'salary': job.get('salary', 'Not specified'),
                        'job_type': job_type
                    }
                    
                    if self.validator:
                        is_valid, issues = self.validator.validate_job(job_data)
                        if is_valid:
                            jobs.append(job_data)
                    else:
                        jobs.append(job_data)
            
            if self.logger:
                self.logger.log_platform_success(platform, len(jobs))
                
        except Exception as e:
            if self.logger:
                self.logger.log_platform_failure(platform, str(e))
            print(f"✗ {platform} error: {str(e)}")
            
        return jobs
    
    def scrape_arbeitnow(self, keywords, limit=10):
        """Scrape Arbeitnow with validation and improved text processing"""
        platform = "Arbeitnow"
        jobs = []
        
        if self.logger:
            self.logger.log_platform_attempt(platform)
        
        try:
            url = "https://www.arbeitnow.com/api/job-board-api"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            job_listings = data.get('data', [])
            
            keywords_lower = [k.lower() for k in keywords]
            
            for job in job_listings:
                if len(jobs) >= limit:
                    break
                    
                job_text = f"{job.get('title', '')} {job.get('description', '')} {' '.join(job.get('tags', []))}".lower()
                
                if any(keyword in job_text for keyword in keywords_lower):
                    # Get raw description
                    raw_description = job.get('description', '')
                    
                    # Clean description
                    clean_desc = clean_description(raw_description, max_length=1000)
                    
                    # Extract and combine skills
                    tags = job.get('tags', [])
                    desc_skills = extract_skills_from_text(raw_description)
                    all_skills = list(set(tags + desc_skills))[:15]
                    
                    job_data = {
                        'title': job.get('title', 'N/A'),
                        'company': clean_company_name(job.get('company_name', 'N/A')),
                        'location': clean_location(job.get('location', 'Remote')),
                        'description': clean_desc,
                        'skills': all_skills,
                        'platform': platform,
                        'url': job.get('url', ''),
                        'posted_date': job.get('created_at', 'N/A'),
                        'salary': 'Not specified',
                        'job_type': job.get('job_types', ['Full-time'])[0] if job.get('job_types') else 'Full-time'
                    }
                    
                    if self.validator:
                        is_valid, issues = self.validator.validate_job(job_data)
                        if is_valid:
                            jobs.append(job_data)
                    else:
                        jobs.append(job_data)
            
            if self.logger:
                self.logger.log_platform_success(platform, len(jobs))
                
        except Exception as e:
            if self.logger:
                self.logger.log_platform_failure(platform, str(e))
            print(f"✗ {platform} error: {str(e)}")
            
        return jobs

    def scrape_adzuna(self, query, location, limit=10):
        """Fetch jobs from Adzuna API"""
        platform = "Adzuna"
        jobs = []
        if self.logger:
            self.logger.log_platform_attempt(platform)
            
        try:
            fetcher = AdzunaFetcher()
            # Map location to country code if possible, or default to 'us' or 'gb'
            # For now, we'll default to 'us' unless location implies otherwise
            country = 'us'
            if 'uk' in location.lower() or 'london' in location.lower():
                country = 'gb'
            elif 'canada' in location.lower():
                country = 'ca'
            elif 'egypt' in location.lower() or 'cairo' in location.lower():
                # Adzuna might not support EG fully via API but we can try if we found it supported
                # Based on test, it returned 0 jobs, so maybe not.
                # But let's leave logic here just in case.
                country = 'za' # South Africa is closest supported African country usually, but let's stick to 'us' default or specific if known
                
            raw_jobs = fetcher.search_jobs(query, location=country, results_per_page=limit)
            
            for job in raw_jobs:
                # Adzuna jobs are already standardized by the fetcher, but we ensure fields match
                job_data = {
                    'title': job.get('title', 'N/A'),
                    'company': clean_company_name(job.get('company', 'N/A')),
                    'location': clean_location(job.get('location', 'Remote')),
                    'description': clean_description(job.get('description', ''), max_length=1000),
                    'skills': job.get('skills', []),
                    'platform': platform,
                    'url': job.get('url', ''),
                    'posted_date': job.get('created', 'N/A'),
                    'salary': job.get('salary', 'Not specified'),
                    'job_type': job.get('contract_type', 'Full-time')
                }
                
                if self.validator:
                    is_valid, issues = self.validator.validate_job(job_data)
                    if is_valid:
                        jobs.append(job_data)
                else:
                    jobs.append(job_data)
                    
            if self.logger:
                self.logger.log_platform_success(platform, len(jobs))
                
        except Exception as e:
            if self.logger:
                self.logger.log_platform_failure(platform, str(e))
            print(f"✗ {platform} error: {str(e)}")
            
        return jobs


    def scrape_jobicy(self, query, limit=10):
        """Fetch jobs from Jobicy API"""
        platform = "Jobicy"
        jobs = []
        if self.logger:
            self.logger.log_platform_attempt(platform)
            
        try:
            fetcher = JobicyFetcher()
            raw_jobs = fetcher.search_jobs(query=query, count=limit)
            
            for job in raw_jobs:
                job_data = {
                    'title': job.get('title', 'N/A'),
                    'company': clean_company_name(job.get('company', 'N/A')),
                    'location': clean_location(job.get('location', 'Remote')),
                    'description': clean_description(job.get('description', ''), max_length=1000),
                    'skills': job.get('skills', []) + extract_skills_from_text(job.get('description', '')),
                    'platform': platform,
                    'url': job.get('url', ''),
                    'posted_date': job.get('posted_date', 'N/A'),
                    'salary': job.get('salary', 'Not specified'),
                    'job_type': 'Remote'
                }
                
                # Deduplicate skills
                job_data['skills'] = list(set(job_data['skills']))[:15]
                
                if self.validator:
                    is_valid, issues = self.validator.validate_job(job_data)
                    if is_valid:
                        jobs.append(job_data)
                else:
                    jobs.append(job_data)
                    
            if self.logger:
                self.logger.log_platform_success(platform, len(jobs))
                
        except Exception as e:
            if self.logger:
                self.logger.log_platform_failure(platform, str(e))
            print(f"✗ {platform} error: {str(e)}")
            
        return jobs

    def scrape_wuzzuf(self, query, limit=10):
        """Scrape jobs from Wuzzuf (Egypt)"""
        platform = "Wuzzuf"
        jobs = []
        if self.logger:
            self.logger.log_platform_attempt(platform)
            
        try:
            fetcher = WuzzufFetcher()
            raw_jobs = fetcher.search_jobs(query, limit=limit)
            
            for job in raw_jobs:
                job_data = {
                    'title': job.get('title', 'N/A'),
                    'company': clean_company_name(job.get('company', 'N/A')),
                    'location': clean_location(job.get('location', 'Egypt')),
                    'description': clean_description(job.get('description', ''), max_length=1000),
                    'skills': job.get('skills', []),
                    'platform': platform,
                    'url': job.get('url', ''),
                    'posted_date': job.get('posted_date', 'N/A'),
                    'salary': job.get('salary', 'Confidential'),
                    'job_type': 'Full-time'
                }
                
                if self.validator:
                    is_valid, issues = self.validator.validate_job(job_data)
                    if is_valid:
                        jobs.append(job_data)
                else:
                    jobs.append(job_data)
                    
            if self.logger:
                self.logger.log_platform_success(platform, len(jobs))
                
        except Exception as e:
            if self.logger:
                self.logger.log_platform_failure(platform, str(e))
            print(f"✗ {platform} error: {str(e)}")
            
        return jobs


def scrape_jobs(query, location='', max_jobs=20):
    """
    Production scraper with validation and logging.
    
    Args:
        query: Search query or job title
        location: Location filter (optional)
        max_jobs: Maximum number of jobs to return
        
    Returns:
        List of validated job dictionaries
    """
    print(f"\n{'='*70}")
    print(f"🔍 Production Job Search")
    print(f"{'='*70}")
    print(f"Query: '{query}'")
    print(f"Location: '{location or 'Any location'}'")
    print(f"Target: {max_jobs} jobs")
    print(f"{'='*70}\n")
    
    # Extract keywords
    keywords = [word.strip() for word in query.split() if len(word.strip()) > 2]
    if not keywords:
        keywords = ['developer']
    
    scraper = ProductionJobScraper(enable_validation=True, enable_logging=True)
    all_jobs = []
    
    # Calculate jobs per platform
    # We have 7 platforms now
    jobs_per_platform = max(5, max_jobs // 4) 
    
    # Scrape platforms
    platforms = [
        ('RemoteOK', lambda: scraper.scrape_remoteok(keywords, limit=jobs_per_platform)),
        ('Remotive', lambda: scraper.scrape_remotive(keywords, limit=jobs_per_platform)),
        ('Arbeitnow', lambda: scraper.scrape_arbeitnow(keywords, limit=jobs_per_platform)),
        ('Adzuna', lambda: scraper.scrape_adzuna(query, location, limit=jobs_per_platform)),

        ('Jobicy', lambda: scraper.scrape_jobicy(query, limit=jobs_per_platform)),
    ]
    
    # Add Wuzzuf if location is Egypt or unspecified (global search)
    if not location or 'egypt' in location.lower() or 'cairo' in location.lower():
        platforms.append(('Wuzzuf', lambda: scraper.scrape_wuzzuf(query, limit=jobs_per_platform)))
    
    for platform_name, scrape_func in platforms:
        try:
            jobs = scrape_func()
            all_jobs.extend(jobs)
            time.sleep(0.5)
        except Exception as e:
            print(f"✗ {platform_name} failed: {e}")
    
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
    
    # Add IDs
    for i, job in enumerate(result, 1):
        job['id'] = i
    
    # Log summary
    if scraper.logger:
        scraper.logger.log_search_summary(query, len(result))
        scraper.logger.print_summary()
    
    print(f"\n{'='*70}")
    print(f"✅ Search Complete: {len(result)} validated jobs")
    print(f"{'='*70}\n")
    
    return result


if __name__ == "__main__":
    # Test
    test_jobs = scrape_jobs("Python Developer", "Egypt", max_jobs=10)
    
    print("\n📋 Sample Results:\n")
    for i, job in enumerate(test_jobs[:3], 1):
        print(f"{i}. {job['title']} at {job['company']}")
        print(f"   Platform: {job['platform']} | URL: {job['url'][:50]}...")
        print(f"   Skills: {', '.join(job['skills'][:5])}\n")
