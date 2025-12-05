"""
Test script for Adzuna API integration.
Run this to verify your API credentials are working.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_adzuna_credentials():
    """Test if Adzuna credentials are set up correctly."""
    app_id = os.getenv('ADZUNA_APP_ID')
    app_key = os.getenv('ADZUNA_APP_KEY')
    
    print("=" * 60)
    print("ADZUNA API CREDENTIAL TEST")
    print("=" * 60)
    
    if not app_id or app_id == 'your_app_id_here':
        print("❌ ADZUNA_APP_ID is not set in .env file")
        return False
    else:
        print(f"✓ ADZUNA_APP_ID found: {app_id[:8]}...")
    
    if not app_key or app_key == 'your_app_key_here':
        print("❌ ADZUNA_APP_KEY is not set in .env file")
        return False
    else:
        print(f"✓ ADZUNA_APP_KEY found: {app_key[:8]}...")
    
    return True

def test_adzuna_api():
    """Test actual API call to Adzuna."""
    try:
        from fetchers.adzuna import fetch_jobs
        
        print("\n" + "=" * 60)
        print("TESTING ADZUNA API CONNECTION")
        print("=" * 60)
        print("Searching for 'Python Developer' jobs in US...\n")
        
        jobs = fetch_jobs("Python Developer", location="us", max_results=5)
        
        if not jobs:
            print("❌ No jobs returned. Check your API credentials.")
            return False
        
        print(f"✓ Successfully fetched {len(jobs)} jobs!\n")
        
        # Display first job as example
        if jobs:
            job = jobs[0]
            print("Example Job:")
            print(f"  Title: {job['title']}")
            print(f"  Company: {job['company']}")
            print(f"  Location: {job['location']}")
            print(f"  Salary: {job['salary']}")
            print(f"  Platform: {job['platform']}")
            print(f"  Skills: {', '.join(job['skills'][:5])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

if __name__ == "__main__":
    print("\n🔍 Starting Adzuna API Tests...\n")
    
    # Test 1: Check credentials
    if not test_adzuna_credentials():
        print("\n" + "=" * 60)
        print("SETUP REQUIRED")
        print("=" * 60)
        print("\nPlease follow these steps:")
        print("1. Go to: https://developer.adzuna.com/")
        print("2. Sign up for a free account")
        print("3. Get your APP_ID and APP_KEY")
        print("4. Add them to your .env file:")
        print("   ADZUNA_APP_ID=your_actual_app_id")
        print("   ADZUNA_APP_KEY=your_actual_app_key")
        print("\n" + "=" * 60)
        exit(1)
    
    # Test 2: Test API connection
    if test_adzuna_api():
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nYour Adzuna integration is ready to use!")
        print("You can now restart your server and test the job search.")
    else:
        print("\n" + "=" * 60)
        print("❌ API TEST FAILED")
        print("=" * 60)
        print("\nPlease verify:")
        print("- Your credentials are correct")
        print("- You have internet connection")
        print("- Your API key is active")
