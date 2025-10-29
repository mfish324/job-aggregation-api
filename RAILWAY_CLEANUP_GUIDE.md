# Railway Cleanup Guide - Fix 3 Services Problem

**Problem**: You have 3 Railway services running when you should only have 1

**Impact**:
- 💰 Wasting Railway credits ($$$)
- 🔄 Confusing which service is "production"
- 🐛 May be causing conflicts or stale data
- ⚡ Services may be competing for same database

---

## Step 1: Identify Your Services

1. Go to Railway Dashboard: https://railway.app/dashboard
2. Find your project (likely named `job-aggregation-api` or similar)
3. You'll see 3 services listed

**List them here**:
```
Service 1: _________________
Service 2: _________________
Service 3: _________________
```

---

## Step 2: Identify the CORRECT Service

Look for these indicators:

### ✅ The Correct Service Has:
- **Latest deployment** (most recent timestamp)
- **Domain/URL assigned** (this is your production URL)
- **Environment variables** set (USAJOBS_API_KEY, DATABASE_URL)
- **Healthy status** (green checkmark)
- **Recent activity** in logs

### ❌ Wrong Services Usually Have:
- Old deployment dates
- No domain assigned
- Failed builds (red X)
- No recent activity
- Duplicate names (e.g., `job-api-copy`, `job-api-2`)

---

## Step 3: Delete Redundant Services

**IMPORTANT**: Before deleting, note down:
1. ✍️ Production service URL
2. ✍️ Database connection (if separate)
3. ✍️ Environment variables

### To Delete a Service:

1. Click on the service you want to DELETE
2. Go to **Settings** tab
3. Scroll down to **"Danger Zone"**
4. Click **"Delete Service from All Environments"**
5. Type the service name to confirm
6. Click **Delete**

**Delete Services 2 and 3** (keep only 1!)

---

## Step 4: Verify Your Production Service

After deleting redundant services, verify the remaining service:

### Check 1: Service is Running
- Railway Dashboard → Your service
- Should show green "Deployed" status
- Check logs for recent activity

### Check 2: URL is Accessible
```bash
# Replace with your actual URL
curl https://your-service.railway.app/health

# Should return:
{"status":"healthy","database":"connected","total_jobs":2023}
```

### Check 3: Environment Variables Set
Click Variables tab, verify these exist:
- ✅ `DATABASE_URL` (auto-provided by Railway)
- ✅ `USAJOBS_API_KEY` (you need to add this!)
- ✅ `USAJOBS_USER_AGENT` (you need to add this!)

### Check 4: Database Connected
```bash
curl https://your-service.railway.app/stats
# Should show job counts
```

---

## Step 5: Add Missing Environment Variables

If USAJOBS variables are missing:

1. Click **Variables** tab
2. Click **New Variable**
3. Add:
   ```
   USAJOBS_API_KEY = Rp/efdVMAKC65bMrfVlaFfLHONvT2yK9DeTyYDP+uQQ=
   ```
4. Click **New Variable** again
5. Add:
   ```
   USAJOBS_USER_AGENT = LevelUpCareers/1.0 (mokeefe324@gmail.com)
   ```
6. Service automatically restarts

---

## Step 6: Trigger Scraping to Add Jobs

Now that you have 1 clean service with USAJOBS enabled:

```bash
# Replace with YOUR actual Railway URL
RAILWAY_URL="https://your-service.railway.app"

# Trigger immediate scraping
curl -X POST "$RAILWAY_URL/genz/search-priority"

# Wait 3 minutes for scraping
sleep 180

# Check results
curl "$RAILWAY_URL/stats"
```

You should see:
- Job count increasing (2023 → 3000+)
- USAJOBS jobs appearing
- Fresh timestamp

---

## Step 7: Set Up Automated Scraping

Add GitHub Actions automation:

1. Go to GitHub repo: https://github.com/mfish324/job-aggregation-api/settings/secrets/actions
2. Click **"New repository secret"**
3. Add:
   - Name: `RAILWAY_APP_URL`
   - Value: `https://your-actual-service.railway.app` (from Step 4)
4. Go to **Actions** tab → **"Scrape Jobs Every 6 Hours"** → **"Run workflow"**

This will scrape jobs automatically every 6 hours!

---

## Expected Results After Cleanup

### Immediate (after Step 6):
- ✅ Only 1 Railway service running
- ✅ USAJOBS enabled and active
- ✅ 3,000-5,000 jobs in database
- ✅ Fresh jobs (last updated: today)

### After 24 Hours:
- ✅ 4 automatic scrapes completed
- ✅ 7,000-10,000 total jobs
- ✅ All sources active (USAJOBS, FAANG, remote boards)
- ✅ Consistent updates every 6 hours

### After 1 Week:
- ✅ 15,000-20,000 total jobs
- ✅ Fresh jobs from 15+ sources
- ✅ GitHub Actions running smoothly
- ✅ No Railway resource waste

---

## Common Service Names to Look For

Your 3 services might be named:
- `job-aggregation-api` ← Keep this (production)
- `job-aggregation-api-worker` ← Delete (unnecessary)
- `job-aggregation-api-test` ← Delete (test environment)

OR:

- `job-api-production` ← Keep this
- `job-api-staging` ← Delete (unless you need staging)
- `job-api-dev` ← Delete (development)

**Rule**: Keep ONLY the production service!

---

## If You're Unsure Which to Keep

### Option 1: Check Deployment Date
Keep the service with the **most recent successful deployment**

### Option 2: Check Domain
Keep the service that has your **production domain/URL**

### Option 3: Check Database
Keep the service with **DATABASE_URL** environment variable set

### Option 4: Safe Approach
1. Note all 3 service URLs
2. Test each: `curl https://service1.railway.app/health`
3. Keep the one that responds and has the most jobs
4. Delete the others

---

## Troubleshooting

### "I deleted the wrong service!"
- Don't panic! Railway keeps backups
- Redeploy from GitHub:
  1. Create new service in Railway
  2. Connect to GitHub repo
  3. Deploy from `main` branch
  4. Add environment variables back
  5. Wait for deployment

### "All 3 services look identical"
- Check the **Deployments** tab on each
- Look at **Recent logs**
- The active one will have continuous activity
- Others will be idle/silent

### "I'm scared to delete anything"
- Take screenshots of all 3 services first
- Write down all environment variables
- Note which database each uses
- Then proceed with deletion

---

## Cost Savings

After cleanup, you'll save:

**Before** (3 services):
- 3 × $5/month = $15/month (minimum)
- 3 × resource usage
- 3 × potential errors

**After** (1 service):
- 1 × $5/month = $5/month
- 1 × resource usage
- Clear production environment

**Savings**: $10/month + cleaner setup!

---

## Final Checklist

After cleanup:
- [ ] Only 1 Railway service running
- [ ] Service URL noted: ___________________
- [ ] USAJOBS_API_KEY added to variables
- [ ] USAJOBS_USER_AGENT added to variables
- [ ] Scraping triggered manually (jobs increased)
- [ ] GitHub Actions secret added (RAILWAY_APP_URL)
- [ ] Test GitHub Actions workflow (ran successfully)
- [ ] Jobs updating automatically every 6 hours

---

## Quick Summary

1. **Go to Railway** → Find your project
2. **Identify 3 services** → Note their names
3. **Keep 1 (production)** → Delete the other 2
4. **Add USAJOBS keys** → In Variables tab
5. **Trigger scraping** → `curl -X POST .../genz/search-priority`
6. **Set up automation** → Add GitHub secret for automated scraping

**Time**: 15 minutes
**Savings**: $10/month
**Result**: Clean, working job scraping system

---

**Created**: October 28, 2025
**Status**: Ready to use
**Priority**: HIGH - Do this first!
