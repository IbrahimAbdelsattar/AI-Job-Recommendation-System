"""
Scraper Logger
Provides structured logging for job scraping operations.
"""
import logging
from datetime import datetime
from pathlib import Path

class ScraperLogger:
    """Structured logger for scraper operations"""
    
    def __init__(self, log_dir='logs'):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger('JobScraper')
        self.logger.setLevel(logging.INFO)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            # File handler
            log_file = self.log_dir / f'scraper_{datetime.now().strftime("%Y%m%d")}.log'
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
        
        self.stats = {
            'platforms_attempted': [],
            'platforms_succeeded': [],
            'platforms_failed': [],
            'total_jobs_scraped': 0,
            'valid_jobs': 0,
            'invalid_jobs': 0
        }
    
    def log_platform_attempt(self, platform: str):
        """Log platform scraping attempt"""
        self.stats['platforms_attempted'].append(platform)
        self.logger.info(f"Attempting to scrape {platform}")
    
    def log_platform_success(self, platform: str, job_count: int):
        """Log successful platform scrape"""
        self.stats['platforms_succeeded'].append(platform)
        self.stats['total_jobs_scraped'] += job_count
        self.logger.info(f"✓ {platform}: Found {job_count} jobs")
    
    def log_platform_failure(self, platform: str, error: str):
        """Log failed platform scrape"""
        self.stats['platforms_failed'].append(platform)
        self.logger.warning(f"✗ {platform}: {error}")
    
    def log_validation_result(self, valid_count: int, invalid_count: int):
        """Log validation results"""
        self.stats['valid_jobs'] = valid_count
        self.stats['invalid_jobs'] = invalid_count
        self.logger.info(f"Validation: {valid_count} valid, {invalid_count} invalid")
    
    def log_search_summary(self, query: str, total_results: int):
        """Log search summary"""
        self.logger.info(f"Search '{query}' completed: {total_results} jobs returned")
    
    def get_stats(self):
        """Get scraping statistics"""
        return self.stats.copy()
    
    def print_summary(self):
        """Print summary of scraping session"""
        print("\n" + "="*70)
        print("SCRAPING SESSION SUMMARY")
        print("="*70)
        print(f"Platforms Attempted: {len(self.stats['platforms_attempted'])}")
        print(f"Platforms Succeeded: {len(self.stats['platforms_succeeded'])}")
        print(f"Platforms Failed: {len(self.stats['platforms_failed'])}")
        print(f"Total Jobs Scraped: {self.stats['total_jobs_scraped']}")
        print(f"Valid Jobs: {self.stats['valid_jobs']}")
        print(f"Invalid Jobs: {self.stats['invalid_jobs']}")
        print("="*70 + "\n")
