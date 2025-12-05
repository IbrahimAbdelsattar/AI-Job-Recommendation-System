from fetchers.adzuna import AdzunaFetcher
import os
from dotenv import load_dotenv

load_dotenv()

def test_adzuna_eg():
    print("Testing Adzuna for Egypt (eg)...")
    try:
        fetcher = AdzunaFetcher()
        jobs = fetcher.search_jobs("Software Engineer", location="eg", results_per_page=5)
        
        if jobs:
            print(f"✅ Success! Found {len(jobs)} jobs in Egypt.")
            for job in jobs:
                print(f"- {job['title']} at {job['company']}")
        else:
            print("❌ No jobs found for Egypt (eg). It might not be supported or just empty.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_adzuna_eg()
