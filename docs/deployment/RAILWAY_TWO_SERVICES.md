# Deploying Two Services to Railway from One Repo

## Your Question: How Does Railway Know What to Run?

**Great question!** Here's how it works:

### The Answer: Railway Service Settings Override Git Files

When you override settings in Railway dashboard, Railway stores them **in its own database**, NOT in your Git repo.

**Your Git Repo:**
- `railway.json` → `"startCommand": "python job_server.py"` ✅
- `Procfile` → `web: python job_server.py` and `worker: python scheduled_scraper.py` ✅
- These files **never change** when you configure Railway

**Railway's Database:**
- Service 1 (API): Uses default → `python job_server.py`
- Service 2 (Scraper): Uses override → `python scheduled_scraper.py`
- **Railway remembers** these settings forever

---

## Two Ways to Deploy Both Services

### Method 1: Using Procfile Process Types (RECOMMENDED)

Your `Procfile` defines two process types:
```
web: python job_server.py
worker: python scheduled_scraper.py
```

**Deploy with Railway:**

1. **First Service (API) - Automatic:**
   - Railway auto-deploys from GitHub
   - Uses `web` process from Procfile
   - Runs: `python job_server.py` ✅

2. **Second Service (Scraper) - Manual Setup:**
   - In Railway, click **"+ New"** → **"Empty Service"**
   - In service settings:
     - **Source**: Same GitHub repo
     - **Root Directory**: Leave empty
     - **Start Command**: `python scheduled_scraper.py`
   - Add same environment variables
   - Deploy!

### Method 2: Manual Override (Alternative)

**Deploy Both:**
1. Create first service from GitHub (API)
2. Create second service from same GitHub repo
3. Override start command in Railway dashboard

**How Railway Remembers:**
- Railway stores override in its service configuration
- Every redeploy uses the stored settings
- Your Git repo stays clean ✅

---

## Step-by-Step: Deploy Both Services (EASY METHOD)

### Service 1: API Server

**Already deployed!** Railway automatically:
- ✅ Detects `railway.json`
- ✅ Runs `python job_server.py`
- ✅ Serves API on assigned PORT

### Service 2: Auto-Scraper

1. **In Railway dashboard**, click **"+ New"**

2. **Select "GitHub Repo"**
   - Choose: `job-aggregation-api`
   - Railway creates new service

3. **Configure the Service:**
   - Click on the new service card
   - Go to **"Settings"** tab
   - Scroll to **"Deploy"** section
   - **Root Directory**: Leave empty
   - **Start Command**: Enter `python scheduled_scraper.py`
   - **Build Command**: Leave as default
   - Click **"Save"**

4. **Add Environment Variables:**
   - Go to **"Variables"** tab
   - Add the same variables as API service:
     ```
     DATABASE_URL=postgresql://neondb_owner:...
     RAPIDAPI_KEY=55a6230b03mshd0f690b6b6ec590p12fc6bjsnbea6f9f1be9b
     RAPIDAPI_INDEED_HOST=indeed-jobs-api.p.rapidapi.com
     ```

5. **Deploy:**
   - Service will auto-deploy
   - Check **"Logs"** tab to see it start scraping!

---

## How Railway Tracks This

### In Railway's Database:

```
Project: job-aggregation-api
├── Service 1: "api-service"
│   ├── Git Repo: mfish324/job-aggregation-api
│   ├── Start Command: (default from railway.json)
│   └── Runs: python job_server.py
│
└── Service 2: "scraper-service"
    ├── Git Repo: mfish324/job-aggregation-api (same repo!)
    ├── Start Command: python scheduled_scraper.py (OVERRIDE)
    └── Runs: python scheduled_scraper.py
```

### In Your Git Repo (Unchanged):

```
GitHub: mfish324/job-aggregation-api
├── railway.json ──→ "startCommand": "python job_server.py"
├── Procfile ──────→ web: python job_server.py
│                    worker: python scheduled_scraper.py
└── (No changes when you configure Railway!)
```

---

## Future Deployments

**When you push to GitHub:**

```bash
git add .
git commit -m "Update job filters"
git push origin main
```

**Railway automatically:**
1. ✅ Detects push
2. ✅ Redeploys **both services**
3. ✅ Service 1: Uses `python job_server.py` (from railway.json)
4. ✅ Service 2: Uses `python scheduled_scraper.py` (from Railway override)
5. ✅ Both services restart with latest code

**Your overrides are permanent** until you change them in Railway!

---

## Why This Works

### Railway's Service Model:

Each service has:
- **Code Source**: Your GitHub repo
- **Service Settings**: Stored in Railway's database
- **Override Priority**: Railway settings > Procfile > railway.json

### Settings Hierarchy:

```
1. Manual Override in Railway Dashboard (HIGHEST)
   ↓
2. Procfile process type
   ↓
3. railway.json startCommand
   ↓
4. Railway auto-detection (LOWEST)
```

So when you override in Railway dashboard, it **always** uses that, even after redeployments!

---

## Example: After You Configure

### First Deploy:
```bash
git push origin main
```

**Railway Action:**
- Service 1: Runs `python job_server.py` ✅
- Service 2: Runs `python scheduled_scraper.py` ✅

### Second Deploy (1 week later):
```bash
git add new_feature.py
git commit -m "Add new feature"
git push origin main
```

**Railway Action:**
- Service 1: Runs `python job_server.py` ✅ (still remembers!)
- Service 2: Runs `python scheduled_scraper.py` ✅ (still remembers!)

**No manual configuration needed!** Railway remembers forever.

---

## Monitoring Both Services

### In Railway Dashboard:

**Service 1 (API):**
- Logs show: `INFO: Application startup complete.`
- Metrics show: HTTP requests coming in
- Health check: `https://your-api.up.railway.app/health`

**Service 2 (Scraper):**
- Logs show: `Searching remoteok for 'junior developer'`
- Metrics show: Steady CPU usage
- No public URL (background worker)

---

## Summary

**Your Concern:** "If I override Railway settings, how does it remember?"

**Answer:**
✅ Railway stores overrides in **its own database**
✅ Your Git repo **never changes**
✅ Future deployments **remember the override**
✅ Each service has **independent configuration**

**The Process:**
1. Deploy Service 1 → Uses `railway.json` or `Procfile`
2. Deploy Service 2 → Override start command in Railway
3. Railway remembers both configurations
4. Every future `git push` uses remembered settings
5. ✨ No manual work needed!

**Your Git repo stays clean, Railway tracks the differences!** 🎉

---

## Quick Reference

### Service 1 (API):
- **What**: Job aggregation REST API
- **Start**: `python job_server.py`
- **Config**: Automatic (from `railway.json`)
- **URL**: `https://your-app.up.railway.app`

### Service 2 (Scraper):
- **What**: Auto-scraper finding jobs 24/7
- **Start**: `python scheduled_scraper.py`
- **Config**: Manual override in Railway
- **URL**: None (background worker)

### Both Services:
- **Repo**: Same (`job-aggregation-api`)
- **Database**: Same (Neon PostgreSQL)
- **Variables**: Same (DATABASE_URL, etc.)
- **Deploy**: Automatic on `git push`

You're all set! Deploy the second service and both will run 24/7! 🚀
