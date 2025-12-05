# Adzuna API Integration Setup Guide

## What is Adzuna?

Adzuna is a professional job search platform with an official API that provides access to millions of real job listings from around the world. Unlike web scraping, using their API is:

- **Legal and reliable**
- **Fast and accurate**
- **Free for reasonable usage**

## Getting Your API Credentials

### Step 1: Sign Up

1. Go to: **https://developer.adzuna.com/**
2. Click "Sign Up" or "Get API Key"
3. Fill in your details:
   - Name
   - Email
   - Company/Project name (you can use "Neuronix AI JobFlow")
   - Brief description of your use case

### Step 2: Get Your Credentials

After signing up, you'll receive:

- **APP_ID**: Your application identifier
- **APP_KEY**: Your secret API key

### Step 3: Add to Your Project

1. Open the `.env` file in your project root
2. Replace the placeholder values:
   ```
   ADZUNA_APP_ID=your_actual_app_id_here
   ADZUNA_APP_KEY=your_actual_app_key_here
   ```

## Testing Your Integration

Run the test script to verify everything works:

```bash
python test_adzuna.py
```

If successful, you'll see:

- ✓ Credentials verified
- ✓ API connection successful
- Example job listings

## Supported Countries

Adzuna supports job searches in many countries. Common country codes:

- `us` - United States
- `gb` - United Kingdom
- `ca` - Canada
- `au` - Australia
- `de` - Germany
- `fr` - France
- `in` - India

## API Limits

**Free Tier:**

- 1000 requests per hour
- Sufficient for most applications
- No credit card required

## What Changed in Your Code

I've updated your job search system to use Adzuna instead of web scraping:

1. **New Module**: `fetchers/adzuna.py` - Handles all API communication
2. **Updated Routes**: `routes/jobs.py` - Now uses `fetch_jobs()` from Adzuna
3. **Better Data**: Real job listings with:
   - Accurate company names
   - Valid URLs
   - Salary information
   - Job descriptions
   - Location data

## Next Steps

1. **Get your API credentials** from https://developer.adzuna.com/
2. **Update your `.env` file** with the credentials
3. **Run the test**: `python test_adzuna.py`
4. **Restart your server**: The system will automatically use Adzuna
5. **Test the search**: Try searching for jobs through your web interface

## Troubleshooting

**"No jobs returned"**

- Check your API credentials are correct
- Verify you have internet connection
- Make sure you're not exceeding rate limits

**"Module not found"**

- Run: `pip install requests` (if not already installed)
- Restart your Python server

**"Invalid credentials"**

- Double-check your APP_ID and APP_KEY in .env
- Make sure there are no extra spaces
- Verify your account is active on Adzuna

## Benefits Over Web Scraping

✅ **Reliable**: No more broken scrapers when websites change
✅ **Legal**: Official API with terms of service
✅ **Fast**: Direct database access, not HTML parsing
✅ **Accurate**: Structured data, not guessed from HTML
✅ **Maintained**: Adzuna keeps the API updated
✅ **Global**: Access jobs from multiple countries

---

**Need Help?**

- Adzuna Documentation: https://developer.adzuna.com/docs
- Contact Adzuna Support if you have API issues
