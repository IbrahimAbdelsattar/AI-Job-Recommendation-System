# API Keys Setup Guide

To unlock the full potential of the enhanced job scraper, you need to obtain API keys for the following platforms.

## 1. Adzuna (Already Configured)

You already have Adzuna credentials in your `.env` file.

- **App ID**: `0829bb2e`
- **App Key**: `ce6ab3602e5eda8bf2dd269f390627f4`

## 2. The Muse (Optional)

The Muse API is public but rate-limited. If you want higher limits, you can request a key.
Currently, the scraper uses the public endpoint.

## 3. Jobicy (No Key Required)

Jobicy API is free and does not require an API key.

## 4. Wuzzuf (No Key Required)

Wuzzuf scraper is built-in and does not require an API key.

## Summary

Your `.env` file should look like this:

```env
SECRET_KEY=neuronix_secret_key_2025
EMAIL_USER=neuronixaisolutions@gmail.com
EMAIL_PASS=your_app_password_here

# Adzuna API Credentials
ADZUNA_APP_ID=0829bb2e
ADZUNA_APP_KEY=ce6ab3602e5eda8bf2dd269f390627f4
```
