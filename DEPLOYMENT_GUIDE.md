# 🚀 Deployment Guide - Neuronix AI JobFlow

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Option 1: Render (Recommended - Free Tier)](#option-1-render-recommended)
3. [Option 2: Railway](#option-2-railway)
4. [Option 3: PythonAnywhere](#option-3-pythonanywhere)
5. [Option 4: Heroku](#option-4-heroku)
6. [Post-Deployment Steps](#post-deployment-steps)

---

## Pre-Deployment Checklist

### ✅ Step 1: Prepare Your Code

1. **Update `.gitignore`** - Add these lines:

```
.env
*.db
__pycache__/
temp_uploads/
logs/
*.log
```

2. **Create `requirements.txt`** (already exists, verify it has):

```
flask==3.0.0
flask-cors==4.0.0
requests==2.31.0
beautifulsoup4==4.12.2
pandas==2.1.1
scikit-learn==1.3.1
PyPDF2==3.0.1
python-docx==1.0.1
python-dotenv==1.0.0
reportlab==4.0.7
gunicorn==21.2.0
```

3. **Create `Procfile`** (for Heroku/Railway):

```
web: gunicorn server:app
```

4. **Update `server.py`** for production:

```python
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)
```

5. **Generate Strong Secret Key**:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Save this for environment variables.

---

## Option 1: Render (Recommended)

**Why Render?**

- ✅ Free tier available
- ✅ Easy deployment from GitHub
- ✅ Automatic HTTPS
- ✅ Good for Python apps

### Step-by-Step:

#### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/Job-Recommendation-System.git
git push -u origin main
```

#### 2. Create Render Account

- Go to [render.com](https://render.com)
- Sign up with GitHub

#### 3. Create New Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `neuronix-jobflow`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn server:app`
   - **Instance Type**: `Free`

#### 4. Add Environment Variables

In Render dashboard, add:

```
SECRET_KEY=<your-generated-secret-key>
ADZUNA_APP_ID=0829bb2e
ADZUNA_APP_KEY=ce6ab3602e5eda8bf2dd269f390627f4
EMAIL_USER=admin@neuronix.ai
EMAIL_PASS=<your-email-password>
FLASK_ENV=production
```

#### 5. Deploy

- Click **"Create Web Service"**
- Wait 5-10 minutes for deployment
- Your app will be live at: `https://neuronix-jobflow.onrender.com`

---

## Option 2: Railway

**Why Railway?**

- ✅ $5 free credit monthly
- ✅ Very fast deployments
- ✅ Great developer experience

### Step-by-Step:

#### 1. Push to GitHub (same as Render)

#### 2. Create Railway Account

- Go to [railway.app](https://railway.app)
- Sign up with GitHub

#### 3. Deploy

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository
4. Railway auto-detects Python and deploys

#### 4. Add Environment Variables

In Railway dashboard → Variables:

```
SECRET_KEY=<your-generated-secret-key>
ADZUNA_APP_ID=0829bb2e
ADZUNA_APP_KEY=ce6ab3602e5eda8bf2dd269f390627f4
FLASK_ENV=production
```

#### 5. Generate Domain

- Go to **Settings** → **Networking**
- Click **"Generate Domain"**
- Your app: `https://your-app.up.railway.app`

---

## Option 3: PythonAnywhere

**Why PythonAnywhere?**

- ✅ Free tier (with pythonanywhere.com subdomain)
- ✅ Persistent storage
- ✅ Good for Python/Flask

### Step-by-Step:

#### 1. Create Account

- Go to [pythonanywhere.com](https://www.pythonanywhere.com)
- Sign up for free account

#### 2. Upload Code

**Option A: Git Clone**

```bash
# In PythonAnywhere Bash console:
git clone https://github.com/YOUR_USERNAME/Job-Recommendation-System.git
cd Job-Recommendation-System
```

**Option B: Upload Files**

- Use "Files" tab to upload your project folder

#### 3. Create Virtual Environment

```bash
mkvirtualenv --python=/usr/bin/python3.10 jobflow
pip install -r requirements.txt
```

#### 4. Configure Web App

1. Go to **Web** tab
2. Click **"Add a new web app"**
3. Choose **"Manual configuration"** → **Python 3.10**
4. Set:
   - **Source code**: `/home/YOUR_USERNAME/Job-Recommendation-System`
   - **Working directory**: `/home/YOUR_USERNAME/Job-Recommendation-System`
   - **Virtualenv**: `/home/YOUR_USERNAME/.virtualenvs/jobflow`

#### 5. Edit WSGI Configuration

Click on WSGI file link and replace with:

```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/YOUR_USERNAME/Job-Recommendation-System'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['SECRET_KEY'] = 'your-secret-key-here'
os.environ['FLASK_ENV'] = 'production'

# Import Flask app
from server import app as application
```

#### 6. Reload Web App

- Click **"Reload"** button
- Visit: `https://YOUR_USERNAME.pythonanywhere.com`

---

## Option 4: Heroku

**Why Heroku?**

- ✅ Industry standard
- ✅ Many add-ons available
- ⚠️ No free tier anymore (starts at $5/month)

### Step-by-Step:

#### 1. Install Heroku CLI

```bash
# Windows (using Chocolatey)
choco install heroku-cli

# Or download from: https://devcenter.heroku.com/articles/heroku-cli
```

#### 2. Login and Create App

```bash
heroku login
heroku create neuronix-jobflow
```

#### 3. Add Buildpack

```bash
heroku buildpacks:set heroku/python
```

#### 4. Set Environment Variables

```bash
heroku config:set SECRET_KEY=your-secret-key-here
heroku config:set ADZUNA_APP_ID=0829bb2e
heroku config:set ADZUNA_APP_KEY=ce6ab3602e5eda8bf2dd269f390627f4
heroku config:set FLASK_ENV=production
```

#### 5. Deploy

```bash
git push heroku main
```

#### 6. Open App

```bash
heroku open
```

Your app: `https://neuronix-jobflow.herokuapp.com`

---

## Post-Deployment Steps

### 1. Test Your Deployment

Visit these URLs on your deployed site:

- `/` - Home page should load
- `/src/signup.html` - Signup should work
- `/src/login.html` - Login should work
- `/src/services.html` - Services page
- `/src/structured.html` - Job search form

### 2. Update CORS Settings (if needed)

If you get CORS errors, update `server.py`:

```python
CORS(app,
     supports_credentials=True,
     origins=["https://your-deployed-domain.com"])
```

### 3. Monitor Logs

**Render:**

```
Dashboard → Logs tab
```

**Railway:**

```
Dashboard → Deployments → View Logs
```

**PythonAnywhere:**

```
Web tab → Log files
```

**Heroku:**

```bash
heroku logs --tail
```

### 4. Set Up Custom Domain (Optional)

**Render:**

- Settings → Custom Domain → Add your domain
- Update DNS with provided CNAME

**Railway:**

- Settings → Networking → Custom Domain

**Heroku:**

```bash
heroku domains:add www.yourdomain.com
```

---

## Troubleshooting

### Issue: "Application Error" or 500 Error

**Solution:**

1. Check logs for errors
2. Verify all environment variables are set
3. Ensure `gunicorn` is in `requirements.txt`
4. Check Python version compatibility

### Issue: Static Files Not Loading

**Solution:**
Add to `server.py`:

```python
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching in dev
```

### Issue: Database Not Persisting

**Solution:**

- SQLite doesn't persist on free hosting
- Consider upgrading to PostgreSQL:
  - Render: Add PostgreSQL database
  - Railway: Add PostgreSQL service
  - Heroku: `heroku addons:create heroku-postgresql`

### Issue: Job Scraping Timeout

**Solution:**

- Increase timeout in hosting settings
- Or optimize scraper to be faster
- Consider background jobs (Celery + Redis)

---

## Recommended: Render Free Tier

For your project, I recommend **Render** because:

1. ✅ Completely free tier
2. ✅ Easy GitHub integration
3. ✅ Automatic HTTPS
4. ✅ Good performance
5. ✅ Persistent disk (for SQLite)

**Quick Start with Render:**

```bash
# 1. Push to GitHub
git init
git add .
git commit -m "Deploy to Render"
git push origin main

# 2. Go to render.com
# 3. New Web Service → Connect GitHub
# 4. Add environment variables
# 5. Deploy!
```

---

## Need Help?

- **Render Docs**: https://render.com/docs
- **Railway Docs**: https://docs.railway.app
- **PythonAnywhere**: https://help.pythonanywhere.com
- **Heroku Docs**: https://devcenter.heroku.com

---

**Last Updated**: December 2025
**Status**: ✅ Ready for deployment
