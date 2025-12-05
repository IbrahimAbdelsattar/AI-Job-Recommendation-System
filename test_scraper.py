"""
Test script to demonstrate the job scraping system
"""

from scraper import scrape_jobs
from matcher import match_jobs
import json

print("="*80)
print(" " * 20 + "NEURONIX AI JOBFLOW - JOB SCRAPER TEST")
print("="*80)
print()

# Test Case 1: Python Developer
print("TEST CASE 1: Searching for 'Python Developer' jobs")
print("-" * 80)

user_profile = {
    'job_title': 'Python Developer',
    'skills': ['Python', 'Flask', 'Django', 'PostgreSQL', 'REST API'],
    'experience': '3 years'
}

print(f"User Profile:")
print(f"  - Job Title: {user_profile['job_title']}")
print(f"  - Skills: {', '.join(user_profile['skills'])}")
print(f"  - Experience: {user_profile['experience']}")
print()

# Scrape jobs
jobs = scrape_jobs('Python Developer', 'Remote', max_jobs=10)

# Match and score jobs
matched_jobs = match_jobs(user_profile, jobs)

print(f"\nTop 5 Matched Jobs:")
print("=" * 80)

for i, job in enumerate(matched_jobs[:5], 1):
    print(f"\n{i}. {job['title']} at {job['company']}")
    print(f"   Match Score: {job['match_score']}%")
    print(f"   Location: {job['location']}")
    print(f"   Platform: {job['platform']}")
    print(f"   Skills: {', '.join(job['skills'][:5])}")
    print(f"   Salary: {job.get('salary', 'Not specified')}")
    print(f"   Posted: {job.get('posted_date', 'N/A')}")
    print(f"   URL: {job['url'][:50]}..." if len(job['url']) > 50 else f"   URL: {job['url']}")

print("\n" + "="*80)
print()

# Test Case 2: Data Science
print("TEST CASE 2: Searching for 'Data Science' jobs")
print("-" * 80)

user_profile_2 = {
    'keywords': 'Data Science Machine Learning Python Pandas'
}

print(f"User Keywords: {user_profile_2['keywords']}")
print()

# Scrape jobs
jobs_2 = scrape_jobs('Data Science Machine Learning', '', max_jobs=10)

# Match and score jobs
matched_jobs_2 = match_jobs(user_profile_2, jobs_2)

print(f"\nTop 3 Matched Jobs:")
print("=" * 80)

for i, job in enumerate(matched_jobs_2[:3], 1):
    print(f"\n{i}. {job['title']} at {job['company']}")
    print(f"   Match Score: {job['match_score']}%")
    print(f"   Platform: {job['platform']}")
    print(f"   Location: {job['location']}")

print("\n" + "="*80)
print()

# Statistics
print("SCRAPING STATISTICS:")
print("-" * 80)
print(f"Total jobs scraped (Test 1): {len(jobs)}")
print(f"Total jobs scraped (Test 2): {len(jobs_2)}")
print(f"Average match score (Test 1): {sum(j['match_score'] for j in matched_jobs) / len(matched_jobs):.1f}%")
print(f"Average match score (Test 2): {sum(j['match_score'] for j in matched_jobs_2) / len(matched_jobs_2):.1f}%")

# Platform distribution
platforms_1 = {}
for job in jobs:
    platform = job['platform']
    platforms_1[platform] = platforms_1.get(platform, 0) + 1

print(f"\nPlatform Distribution (Test 1):")
for platform, count in platforms_1.items():
    print(f"  - {platform}: {count} jobs")

print("\n" + "="*80)
print(" " * 25 + "TEST COMPLETE!")
print("="*80)
