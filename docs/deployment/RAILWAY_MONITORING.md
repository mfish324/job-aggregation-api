# How to Find and Monitor Your Project on Railway

## Finding Your Project

### Step 1: Login to Railway

1. Go to **https://railway.app**
2. Click **"Login"** (top right)
3. Sign in with GitHub (same account you used to deploy)

### Step 2: View Your Dashboard

After logging in, you'll see your **Railway Dashboard** with all your projects.

**What You'll See:**
- List of all your projects
- Each project shows:
  - Project name (e.g., "job-aggregation-api")
  - Last deployment time
  - Status (green = running, red = error, yellow = deploying)

### Step 3: Open Your Project

Click on your project card to see details.

---

## How to Know It's Running

### Visual Indicators

**✅ Project is Running:**
- **Green status indicator** on project card
- **"Active"** or **"Running"** badge
- **Recent deployment** timestamp
- **Metrics showing activity** (CPU/RAM usage)

**❌ Project Has Issues:**
- **Red status indicator**
- **"Failed"** or **"Error"** badge
- **Check logs** for error messages

---

## Project Dashboard Overview

When you click on your project, you'll see:

### 1. **Services Tab** (Left sidebar)

Shows all your services:
- `job-aggregation-api` (your main API)
- `job-scraper` (if you deployed the auto-scraper)

Each service card shows:
- **Status**: Running/Failed/Deploying
- **Last deployment**: Time since last deploy
- **Quick actions**: View logs, settings, etc.

### 2. **Deployments Tab**

Shows deployment history:
- Latest deployment status
- Build logs
- Deploy time
- Git commit that triggered deploy

**Green checkmark (✅)** = Successful deployment
**Red X (❌)** = Failed deployment

### 3. **Metrics Tab**

Shows real-time metrics:
- **CPU usage** (%)
- **RAM usage** (MB)
- **Network traffic**
- **Request count** (for API)

If you see activity here, your service is running!

### 4. **Logs Tab** ⭐ Most Important

Real-time logs from your application:
- API server startup messages
- Incoming requests
- Errors (if any)
- Auto-scraper activity

**What to look for:**
```
INFO:     Uvicorn running on http://0.0.0.0:8001
INFO:     Application startup complete.
JOB AGGREGATION API SERVER
Total jobs in database: 1710
```

If you see these, your API is running!

---

## Step-by-Step: Check If Your Project Is Running

### Method 1: Quick Visual Check (30 seconds)

1. **Login to Railway**: https://railway.app
2. **Look at project card**:
   - ✅ Green indicator = Running
   - ❌ Red indicator = Error
3. **Check deployment badge**: Should say "Active"

### Method 2: Check Logs (1 minute)

1. Click on your **project**
2. Click on **service card** (e.g., job-aggregation-api)
3. Go to **"Logs"** tab
4. Look for:
   ```
   INFO:     Application startup complete.
   Total jobs in database: 1710
   ```
5. If you see recent logs = it's running!

### Method 3: Check Metrics (1 minute)

1. Click on your **project**
2. Go to **"Metrics"** tab
3. Look for:
   - CPU usage > 0%
   - RAM usage (should be ~100-300 MB)
   - Network activity (if people are using it)

### Method 4: Test the API (1 minute)

1. Get your Railway URL:
   - Click on service → **"Settings"** → **"Networking"**
   - Copy the public URL (e.g., `https://your-app.up.railway.app`)

2. Test it:
   ```bash
   # Health check
   curl https://your-app.up.railway.app/health

   # Or open in browser:
   # https://your-app.up.railway.app/health
   ```

3. Should return:
   ```json
   {
     "status": "healthy",
     "database": "connected",
     "total_jobs": 1710
   }
   ```

If you get this response = **IT'S RUNNING!** ✅

---

## Finding Your Railway URL

### Where to Find Your Public URL:

1. **Dashboard**: Click on project
2. **Service card**: Click on your API service
3. **Settings tab**: Scroll to "Networking" section
4. **Public Domain**: You'll see your URL

**URL Format:**
```
https://job-aggregation-api-production-XXXX.up.railway.app
```

**Copy this URL** - this is how you access your API!

---

## Common Project Locations

### If You Just Deployed:

1. **Check email**: Railway sends deployment confirmation
2. **Check GitHub**: Look for Railway bot comments on your repo
3. **Dashboard**: https://railway.app/dashboard

### If You Can't Find Your Project:

1. **Check you're logged in** with the right GitHub account
2. **Look in "All Projects"** on Railway dashboard
3. **Search bar**: Top of Railway dashboard - search for your repo name

---

## Monitoring Your Services

### API Server Monitoring

**What to watch:**
- **Logs**: Should show incoming API requests
- **Metrics**: CPU/RAM usage
- **Deployments**: Check for errors

**Healthy API Logs:**
```
INFO:     127.0.0.1:50000 - "GET /jobs HTTP/1.1" 200 OK
INFO:     127.0.0.1:50001 - "GET /stats HTTP/1.1" 200 OK
INFO:     127.0.0.1:50002 - "GET /health HTTP/1.1" 200 OK
```

### Auto-Scraper Monitoring

**What to watch:**
- **Logs**: Should show scraping activity
- **Metrics**: Should run continuously (not idle)

**Healthy Scraper Logs:**
```
INFO - Searching remoteok for 'junior developer'
INFO - remoteok: Found 45 jobs, 12 new
INFO - Searching remotive for 'entry level developer'
INFO - remotive: Found 23 jobs, 8 new
```

---

## Railway Dashboard Quick Reference

### Left Sidebar:
- **Projects**: All your projects
- **Settings**: Account settings
- **Usage**: Credit usage, billing

### Project View:
- **Deployments**: Deployment history
- **Logs**: Real-time application logs
- **Metrics**: CPU, RAM, network stats
- **Settings**: Service configuration
- **Variables**: Environment variables

### Service Card:
- **Status indicator**: Green/red dot
- **Service name**: job-aggregation-api
- **Last deployment**: Time since last deploy
- **Actions**: Click to view details

---

## Troubleshooting: "I Can't Find My Project"

### Problem 1: Not Deployed Yet

**Solution:**
1. Make sure you clicked "Deploy" in Railway
2. Wait 2-3 minutes for first deployment
3. Check "Deployments" tab for progress

### Problem 2: Wrong GitHub Account

**Solution:**
1. Log out of Railway
2. Log in with the GitHub account that has your repo (mfish324)
3. Check dashboard again

### Problem 3: Deployment Failed

**Solution:**
1. Click on project (even if it failed)
2. Go to "Logs" tab
3. Look for error messages
4. Common issues:
   - Missing environment variables
   - Python package errors
   - Database connection issues

---

## How to Access Your API

Once you confirm it's running:

### 1. Get Your URL
- Railway dashboard → Service → Settings → Networking
- Copy the public domain

### 2. Test Endpoints

**Health Check:**
```bash
curl https://your-app.up.railway.app/health
```

**Get Jobs:**
```bash
curl https://your-app.up.railway.app/jobs?per_page=5
```

**API Documentation:**
Open in browser:
```
https://your-app.up.railway.app/docs
```

### 3. Use from Your Django Platform

```python
import requests

RAILWAY_API = "https://your-app.up.railway.app"

def get_jobs():
    response = requests.get(f"{RAILWAY_API}/jobs")
    return response.json()
```

---

## Checking Service Health

### Quick Health Check Checklist:

✅ **Green status** on Railway dashboard
✅ **Recent logs** in Logs tab
✅ **CPU/RAM usage** in Metrics tab
✅ **Successful response** from `/health` endpoint
✅ **No errors** in deployment logs

If all 5 are ✅ = Your project is healthy!

---

## Setting Up Notifications

Get notified when something goes wrong:

1. Go to project **Settings**
2. Scroll to **"Notifications"**
3. Enable:
   - **Email notifications** (deployment failures)
   - **Webhook** (for Slack/Discord, optional)

---

## What You Should See Right Now

### If You Just Deployed:

**Deployment Tab:**
```
✅ Building... (2 minutes)
✅ Deploying... (1 minute)
✅ Live! - Deployed successfully
```

**Logs Tab:**
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001
```

**Metrics Tab:**
- CPU: 5-20%
- RAM: 100-300 MB
- Status: Active

### If Everything Is Working:

You should be able to:
1. ✅ See green status indicator
2. ✅ Access `/health` endpoint
3. ✅ View logs showing activity
4. ✅ See metrics showing resource usage
5. ✅ Get jobs from `/jobs` endpoint

---

## Quick Visual Guide

### Railway Dashboard:
```
┌─────────────────────────────────────────┐
│  Railway Dashboard                      │
├─────────────────────────────────────────┤
│                                         │
│  Projects:                              │
│  ┌───────────────────────────────────┐ │
│  │ job-aggregation-api          🟢  │ │ ← Green = Running
│  │ Last deployed: 2 minutes ago      │ │
│  │ Status: Active                    │ │
│  └───────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

### Service View:
```
┌─────────────────────────────────────────┐
│  job-aggregation-api                    │
├─────────────────────────────────────────┤
│  Tabs: [Deployments] [Logs] [Metrics]  │
│                                         │
│  Logs:                                  │
│  INFO: Application startup complete     │
│  INFO: GET /health 200 OK               │
│  INFO: GET /jobs 200 OK                 │
│                                         │
└─────────────────────────────────────────┘
```

---

## Summary

**To find your project:**
1. Go to https://railway.app
2. Login with GitHub
3. See your project in dashboard

**To know it's running:**
1. ✅ Green status indicator
2. ✅ Recent logs showing activity
3. ✅ `/health` endpoint returns 200 OK
4. ✅ Metrics showing CPU/RAM usage

**Your Railway URL:**
- Found in: Service → Settings → Networking
- Format: `https://your-app.up.railway.app`
- Use this to access your API from anywhere!

**Next steps:**
1. Test your Railway URL
2. Integrate with your Django platform
3. Monitor logs to see jobs being added
4. Share API with your other projects

Need help? Check the logs first - they usually tell you what's wrong! 📊
