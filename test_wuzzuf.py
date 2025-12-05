from fetchers.wuzzuf import WuzzufFetcher

def test_wuzzuf():
    print("Testing Wuzzuf Scraper...")
    try:
        fetcher = WuzzufFetcher()
        jobs = fetcher.search_jobs("Software Engineer", limit=5)
        
        if jobs:
            print(f"✅ Success! Found {len(jobs)} jobs on Wuzzuf.")
            for job in jobs:
                print(f"- {job['title']} at {job['company']}")
                print(f"  Location: {job['location']}")
                print(f"  URL: {job['url']}")
                print("-" * 30)
        else:
            print("❌ No jobs found on Wuzzuf. Check selectors.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_wuzzuf()
