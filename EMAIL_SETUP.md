# Email Integration Setup Guide

## Overview

The AI Job Matcher now includes professional email integration for password reset and welcome emails.

## Features

### 1. Password Reset Emails

- **HTML-formatted emails** with branded design
- **Secure reset links** with 1-hour expiration
- **Security warnings** included in email
- **Fallback to console** if SMTP not configured

### 2. Welcome Emails

- Sent automatically when new users sign up
- Professional branding
- Quick start guide included

## Email Templates

Both email types include:

- ✅ Responsive HTML design
- ✅ Gradient headers with brand colors
- ✅ Clear call-to-action buttons
- ✅ Security notices
- ✅ Plain text fallback

## Setup Instructions

### Option 1: Development Mode (No SMTP)

By default, emails are simulated and printed to the console. This is perfect for development and testing.

**No setup required!** Just run the server and check the console for email content.

### Option 2: Production Mode (With SMTP)

#### For Gmail:

1. **Enable 2-Factor Authentication** on your Google account
2. **Generate an App Password**:

   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the generated 16-character password

3. **Create `.env` file** in project root:

```bash
cp .env.example .env
```

4. **Edit `.env` file**:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=Neuronix AI JobFlow
```

#### For Other Email Providers:

**Outlook/Hotmail:**

```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

**Yahoo:**

```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
```

**Custom SMTP:**

```env
SMTP_SERVER=your-smtp-server.com
SMTP_PORT=587
SMTP_USERNAME=your-username
SMTP_PASSWORD=your-password
```

## Testing

### Test Password Reset Email:

1. Go to `http://localhost:5000/src/forgot-password.html`
2. Enter your email address
3. Click "Send Reset Token"
4. **Without SMTP**: Check server console for email content and reset link
5. **With SMTP**: Check your email inbox

### Test Welcome Email:

1. Go to `http://localhost:5000/src/signup.html`
2. Create a new account
3. **Without SMTP**: Check server console
4. **With SMTP**: Check your email inbox

## Email Content

### Password Reset Email Includes:

- Personalized greeting
- Reset button with direct link
- Plain text link (for copy/paste)
- 1-hour expiration warning
- Security tips
- Contact information

### Welcome Email Includes:

- Personalized greeting
- Feature overview (Structured Search, Chat Mode, CV Upload)
- "Start Job Search" button
- Contact information

## Security Features

1. **Token Expiration**: Reset tokens expire after 1 hour
2. **One-time Use**: Tokens are marked as used after password reset
3. **No Email Disclosure**: System doesn't reveal if email exists
4. **Secure Links**: Reset links include unique tokens

## Troubleshooting

### Emails Not Sending (SMTP Mode):

- ✅ Check `.env` file exists and has correct credentials
- ✅ Verify SMTP server and port are correct
- ✅ For Gmail, ensure App Password is used (not regular password)
- ✅ Check firewall isn't blocking port 587
- ✅ Look for error messages in server console

### Emails Going to Spam:

- Add sender email to contacts
- Check SPF/DKIM records (production)
- Use a verified domain email address

### Console Shows "EMAIL SIMULATION":

- This is normal in development mode
- SMTP credentials not configured in `.env`
- Copy reset link from console output

## Files Created

- `email_utils.py` - Email sending functionality
- `.env.example` - Configuration template
- `.env` - Your actual configuration (create this, not tracked in git)

## API Changes

### Updated Endpoints:

**POST /api/auth/forgot-password**

- Now sends email instead of returning token
- Returns success message regardless of email existence (security)

**POST /api/auth/signup**

- Now sends welcome email after account creation
- Email sent asynchronously (doesn't block response)

## Next Steps

1. **Production Deployment**: Use a dedicated email service (SendGrid, AWS SES, Mailgun)
2. **Email Templates**: Customize HTML templates in `email_utils.py`
3. **Email Tracking**: Add open/click tracking
4. **Unsubscribe**: Add unsubscribe links for marketing emails
