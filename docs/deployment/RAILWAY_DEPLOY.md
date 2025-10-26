# Railway.app Deployment - Quick Guide

Deploy your Gen-Z job aggregator to Railway in **10 minutes**!

## Why Railway?

- ✅ **$5 free credit/month** (no credit card needed initially)
- ✅ **Auto-deploys** from GitHub
- ✅ **Super easy** - just connect and deploy
- ✅ **Free domain** included
- ✅ **Environment variables** management
- ✅ **Perfect for your project**

## Step 1: Sign Up (2 minutes)

1. Go to **https://railway.app**
2. Click **"Login"** or **"Start a New Project"**
3. **Sign in with GitHub** (easiest way)
4. Authorize Railway to access your repos

## Step 2: Create New Project (1 minute)

1. Click **"New Project"**
2. Click **"Deploy from GitHub repo"**
3. Select **"Configure GitHub App"** (if first time)
4. Select repository: **`job-aggregation-api`**
5. Railway will start deploying!

## Step 3: Add Environment Variables (3 minutes)

In your Railway project dashboard:

1. Click on the **service card**
2. Go to **"Variables"** tab
3. Click **"+ New Variable"**
4. Add these:

```bash
DATABASE_URL
postgresql://neondb_owner:npg_LoG2yMitzm4Y@ep-flat-hat-aehgdj0h-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require

RAPIDAPI_KEY
55a6230b03mshd0f690b6b6ec590p12fc6bjsnbea6f9f1be9b

RAPIDAPI_INDEED_HOST
indeed-jobs-api.p.rapidapi.com

PORT
8001
```

Click **"Save"** - Railway will redeploy automatically!

## Step 4: Get Your URL (1 minute)

1. Go to **"Settings"** tab
2. Scroll to **"Networking"** section
3. Click **"Generate Domain"**
4. You'll get a URL like: `https://job-aggregation-api-production.up.railway.app`

**Test it:**
```bash
# Health check
curl https://YOUR-APP.up.railway.app/health

# Get jobs
curl https://YOUR-APP.up.railway.app/jobs?per_page=5
```

## Step 5: Deploy Auto-Scraper (3 minutes)

To run the scraper 24/7, create a second service:

1. In Railway dashboard, click **"+ New"**
2. Select **"GitHub Repo"**
3. Select same repo: **`job-aggregation-api`**
4. Click the new service card
5. Go to **"Settings"** → **"Service"**
6. Change **"Start Command"** to:
   ```
   python scheduled_scraper.py
   ```
7. Go to **"Variables"** and add same environment variables
8. Click **"Deploy"**

Now you have:
- ✅ **API Service**: Serving jobs via REST API
- ✅ **Scraper Service**: Finding new jobs 24/7

## Step 6: Verify Everything Works

```bash
# Test API
curl https://YOUR-APP.up.railway.app/health
curl https://YOUR-APP.up.railway.app/stats

# View API docs
# Open in browser:
https://YOUR-APP.up.railway.app/docs
```

## Step 7: Monitor Your Services

In Railway dashboard:

1. **Deployments tab**: See deployment history
2. **Metrics tab**: View CPU/RAM usage
3. **Logs tab**: View real-time logs

To view scraper logs:
- Click on **scraper service**
- Go to **"Logs"** tab
- See it finding jobs in real-time!

## Cost Breakdown

**Free Tier:**
- $5 credit/month
- ~500 MB RAM
- ~1 GB storage
- Enough for 2 services (API + scraper)

**Expected Usage:**
- API: ~$2-3/month
- Scraper: ~$2-3/month
- **Total: ~$4-5/month**

You'll use almost all your free credit, which is perfect!

## Auto-Deploys from GitHub

Every time you push to GitHub:
```bash
git add .
git commit -m "Update job filters"
git push origin main
```

Railway will **automatically redeploy**! No manual work needed.

## Custom Domain (Optional)

Want your own domain?

1. Buy domain from Namecheap/GoDaddy (~$12/year)
2. In Railway **"Settings"** → **"Networking"**
3. Click **"Custom Domain"**
4. Enter your domain: `api.yourjobsite.com`
5. Follow DNS instructions
6. Done!

## Monitoring & Logs

**View Logs:**
```bash
# In Railway dashboard
1. Click on service
2. Go to "Logs" tab
3. See real-time output
```

**Check Status:**
- Railway dashboard shows service status (green = running)
- Email alerts if service crashes
- Automatic restarts on failure

## Troubleshooting

### "Service not starting"
- Check **Logs** tab for errors
- Verify environment variables are set
- Make sure `requirements.txt` is up to date

### "Database connection failed"
- Verify `DATABASE_URL` is correct
- Check Neon database is active
- Test connection from Railway shell

### "Out of credits"
Railway will pause services when credits run out:
- Add payment method
- Or wait until next month for $5 credit

## What's Deployed

After deployment, you have:

✅ **API Server** (Service 1)
- URL: `https://your-app.up.railway.app`
- Endpoints: `/jobs`, `/stats`, `/genz/search-priority`, etc.
- Database: Neon PostgreSQL (remote)

✅ **Auto-Scraper** (Service 2)
- Running 24/7 in background
- Searches every 6/12/24 hours
- Adds jobs to Neon database
- US-only filtering enabled

✅ **Database** (External - Neon)
- 3 GB free storage
- Shared between both services
- Accessible from anywhere

## Accessing from Your Job Board

Now your Django/other platforms can call:

```python
import requests

# Get jobs from Railway API
jobs = requests.get(
    "https://your-app.up.railway.app/jobs",
    params={"keyword": "python", "per_page": 20}
).json()

for job in jobs['jobs']:
    print(f"{job['title']} at {job['company']}")
```

## Updates

To update your deployment:

1. Make changes locally
2. Test locally: `python job_server.py`
3. Commit: `git commit -m "Update"`
4. Push: `git push origin main`
5. Railway auto-deploys!

## Summary

**Deployment Time:** 10 minutes
**Cost:** $5/month (free credit)
**Maintenance:** Zero - auto-deploys from GitHub
**Uptime:** 99.9%

**Your URLs:**
- API: `https://your-app.up.railway.app`
- Docs: `https://your-app.up.railway.app/docs`
- Jobs: `https://your-app.up.railway.app/jobs`

**Services Running:**
- ✅ API Server (24/7)
- ✅ Auto-Scraper (24/7)
- ✅ Neon Database (remote, 3 GB free)

Your Gen-Z job aggregator is now **live on the internet**! 🎉🚀

## Next Steps

1. Test your API at the Railway URL
2. Integrate with your Django job board
3. Monitor logs to see jobs being added
4. Share API with your other platforms

**Need help?**
- Railway docs: https://docs.railway.app
- Neon docs: https://neon.tech/docs
- Your project: [DEPLOYMENT_OPTIONS.md](DEPLOYMENT_OPTIONS.md)
