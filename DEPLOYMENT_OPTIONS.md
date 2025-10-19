# Remote Server Deployment Guide

Deploy your Gen-Z job aggregator to run 24/7 on a remote server!

## Best Remote Server Options (Ranked)

### 1. Railway.app ⭐ (EASIEST - Recommended for Beginners)

**Why Railway:**
- ✅ **Easiest deployment** - Connect GitHub and deploy in 5 minutes
- ✅ **$5 free credit/month** (enough for small projects)
- ✅ **Auto-deploys** from GitHub commits
- ✅ **Built-in PostgreSQL** database
- ✅ **Environment variables** management
- ✅ **Free domain** included
- ✅ **No server management** needed

**Cost:**
- Free: $5 credit/month (~500 MB RAM, 1 GB storage)
- Paid: ~$5-10/month for hobby project

**Best For:** Quick deployment, minimal configuration, hobby projects

**Setup Time:** 5-10 minutes

---

### 2. Render.com ⭐ (Great Free Tier)

**Why Render:**
- ✅ **Generous free tier** (750 hours/month free)
- ✅ **Free PostgreSQL** database (90 days, then $7/mo)
- ✅ **Auto-deploys** from GitHub
- ✅ **Custom domains** supported
- ✅ **Background workers** (for auto-scraper)
- ✅ **Simple UI**

**Cost:**
- Free: Web service + database (limited)
- Paid: $7/mo for database, $7/mo for web service

**Best For:** Free tier projects, automatic deployments

**Setup Time:** 10-15 minutes

---

### 3. DigitalOcean ⭐ (Best Value for Long-term)

**Why DigitalOcean:**
- ✅ **Full control** over server
- ✅ **Predictable pricing** ($4-6/month)
- ✅ **Best performance** for price
- ✅ **Simple droplets** (VPS)
- ✅ **1-click apps** (Docker, PostgreSQL)
- ✅ **Great documentation**

**Cost:**
- Basic Droplet: $4/month (512 MB RAM, 10 GB SSD)
- Better Droplet: $6/month (1 GB RAM, 25 GB SSD)
- Managed Database: $15/month (optional, use Neon instead)

**Best For:** Long-term projects, full control, best value

**Setup Time:** 20-30 minutes

---

### 4. AWS Lightsail (Alternative to DigitalOcean)

**Why Lightsail:**
- ✅ **AWS ecosystem** but simpler
- ✅ **Predictable pricing** ($3.50-5/month)
- ✅ **Good performance**
- ✅ **Static IP included**

**Cost:**
- $3.50/month (512 MB RAM)
- $5/month (1 GB RAM)

**Best For:** AWS users, simple VPS needs

**Setup Time:** 20-30 minutes

---

### 5. Fly.io (Modern Alternative)

**Why Fly.io:**
- ✅ **Generous free tier**
- ✅ **Auto-scaling**
- ✅ **Edge deployment** (fast globally)
- ✅ **Docker-based**

**Cost:**
- Free: 3 VMs with 256 MB RAM each
- Paid: ~$2-10/month

**Best For:** Docker users, global deployment

**Setup Time:** 15-20 minutes

---

## Quick Comparison

| Service | Free Tier | Monthly Cost | Ease of Use | Best For |
|---------|-----------|--------------|-------------|----------|
| **Railway** | $5 credit | $5-10 | ⭐⭐⭐⭐⭐ | Beginners |
| **Render** | 750 hrs | $7-14 | ⭐⭐⭐⭐⭐ | Free tier |
| **DigitalOcean** | None | $4-6 | ⭐⭐⭐⭐ | Long-term |
| **Lightsail** | 3 months | $3.50-5 | ⭐⭐⭐⭐ | AWS users |
| **Fly.io** | 3 VMs | $2-10 | ⭐⭐⭐ | Docker fans |

---

## Recommended Setup for You

### Option A: Easiest (Railway + Neon) - $5/month

**Services:**
- **Railway**: Host API server + auto-scraper
- **Neon**: PostgreSQL database (already set up!)
- **Total Cost**: $5/month (Railway credit) + $0 (Neon free tier)

**What You Get:**
- ✅ API accessible worldwide
- ✅ Auto-scraper running 24/7
- ✅ Auto-deploys from GitHub
- ✅ No server management

---

### Option B: Best Value (DigitalOcean + Neon) - $6/month

**Services:**
- **DigitalOcean Droplet**: $6/month (1 GB RAM)
- **Neon**: PostgreSQL database (free)
- **Total Cost**: $6/month

**What You Get:**
- ✅ Full control over server
- ✅ Better performance
- ✅ Can host job board website too
- ✅ SSH access

---

### Option C: All-in-One Free (Render) - $0-7/month

**Services:**
- **Render**: Free web service + background worker
- **Neon**: Free PostgreSQL
- **Total Cost**: $0 (with limitations) or $7/month

**What You Get:**
- ✅ Completely free to start
- ✅ Auto-deploys from GitHub
- ✅ Upgrade later if needed

---

## Step-by-Step: Railway Deployment (EASIEST)

### Prerequisites
- ✅ GitHub account (you have this)
- ✅ Railway account (free - create at railway.app)
- ✅ Your code already on GitHub ✅

### Step 1: Sign Up for Railway (2 minutes)

1. Go to **https://railway.app**
2. Click **"Start a New Project"**
3. Sign in with GitHub
4. Verify email

### Step 2: Create New Project (3 minutes)

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose: `mfish324/job-aggregation-api`
4. Railway will auto-detect it's a Python project

### Step 3: Configure Environment Variables (2 minutes)

In Railway dashboard:
1. Go to **Variables** tab
2. Add these:

```bash
DATABASE_URL=postgresql://neondb_owner:npg_LoG2yMitzm4Y@ep-flat-hat-aehgdj0h-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require
RAPIDAPI_KEY=55a6230b03mshd0f690b6b6ec590p12fc6bjsnbea6f9f1be9b
RAPIDAPI_INDEED_HOST=indeed-jobs-api.p.rapidapi.com
PORT=8001
```

### Step 4: Add Deployment Files

Railway needs a few files to know how to run your app:

**Create `Procfile`:**
```
web: uvicorn job_server:app --host 0.0.0.0 --port $PORT
worker: python scheduled_scraper.py
```

**Create `railway.json`:**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn job_server:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**Create `nixpacks.toml`:**
```toml
[phases.setup]
nixPkgs = ["python310"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "uvicorn job_server:app --host 0.0.0.0 --port $PORT"
```

### Step 5: Deploy! (1 minute)

1. Commit and push these files to GitHub:
```bash
git add Procfile railway.json nixpacks.toml
git commit -m "Add Railway deployment configuration"
git push origin main
```

2. Railway will **auto-deploy**!
3. Wait 2-3 minutes for build

### Step 6: Get Your URL

1. Railway gives you a URL like: `https://your-app.up.railway.app`
2. Test it: `https://your-app.up.railway.app/health`
3. API docs: `https://your-app.up.railway.app/docs`

### Step 7: Deploy Auto-Scraper (Separate Service)

To run the auto-scraper 24/7:

1. In Railway, click **"New"** → **"GitHub Repo"**
2. Select same repo
3. In settings:
   - **Start Command**: `python scheduled_scraper.py`
   - **Service Name**: `job-scraper`
4. Add same environment variables
5. Deploy!

Now you have:
- ✅ API Server: `https://your-app.up.railway.app`
- ✅ Auto-Scraper: Running 24/7 in background
- ✅ Database: Neon PostgreSQL (already set up)

---

## Step-by-Step: DigitalOcean Deployment (BEST VALUE)

### Step 1: Create Droplet (5 minutes)

1. Sign up at **https://www.digitalocean.com**
2. Click **"Create"** → **"Droplets"**
3. Choose:
   - **Image**: Ubuntu 22.04 LTS
   - **Plan**: Basic ($6/month - 1 GB RAM)
   - **Region**: Closest to you (e.g., New York)
   - **Authentication**: SSH key or password
4. Click **"Create Droplet"**
5. Note the IP address (e.g., 192.168.1.100)

### Step 2: Connect via SSH (2 minutes)

```bash
# Windows (PowerShell)
ssh root@YOUR_DROPLET_IP

# Enter password when prompted
```

### Step 3: Install Dependencies (5 minutes)

```bash
# Update system
apt update && apt upgrade -y

# Install Python and tools
apt install -y python3-pip python3-venv git nginx

# Install Docker (optional, for easier management)
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

### Step 4: Clone Your Project (2 minutes)

```bash
# Clone your repo
cd /opt
git clone https://github.com/mfish324/job-aggregation-api.git
cd job-aggregation-api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Configure Environment (3 minutes)

```bash
# Create .env file
nano .env
```

Add:
```bash
DATABASE_URL=postgresql://neondb_owner:npg_LoG2yMitzm4Y@ep-flat-hat-aehgdj0h-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require
RAPIDAPI_KEY=55a6230b03mshd0f690b6b6ec590p12fc6bjsnbea6f9f1be9b
RAPIDAPI_INDEED_HOST=indeed-jobs-api.p.rapidapi.com
```

Save: `Ctrl+X`, `Y`, `Enter`

### Step 6: Create Systemd Services (10 minutes)

**API Server Service:**
```bash
nano /etc/systemd/system/job-api.service
```

```ini
[Unit]
Description=Job Aggregation API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/job-aggregation-api
Environment="PATH=/opt/job-aggregation-api/venv/bin"
ExecStart=/opt/job-aggregation-api/venv/bin/python job_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Auto-Scraper Service:**
```bash
nano /etc/systemd/system/job-scraper.service
```

```ini
[Unit]
Description=Job Auto-Scraper
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/job-aggregation-api
Environment="PATH=/opt/job-aggregation-api/venv/bin"
ExecStart=/opt/job-aggregation-api/venv/bin/python scheduled_scraper.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Step 7: Start Services (2 minutes)

```bash
# Reload systemd
systemctl daemon-reload

# Enable and start services
systemctl enable job-api job-scraper
systemctl start job-api job-scraper

# Check status
systemctl status job-api
systemctl status job-scraper
```

### Step 8: Configure Nginx (5 minutes)

```bash
nano /etc/nginx/sites-available/job-api
```

```nginx
server {
    listen 80;
    server_name YOUR_DROPLET_IP;

    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Enable site
ln -s /etc/nginx/sites-available/job-api /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### Step 9: Test!

```bash
# From your local computer
curl http://YOUR_DROPLET_IP/health
curl http://YOUR_DROPLET_IP/stats
```

Your API is now live at: `http://YOUR_DROPLET_IP`

---

## Hosting Your Job Board Website

Once your API is deployed, host your job board website:

### On Same DigitalOcean Server:

```bash
# Upload your website files to /var/www/html
# Configure nginx to serve static files
# Point API calls to http://localhost:8001
```

### On Netlify/Vercel (FREE):

1. Host static job board on Netlify
2. Call your API: `http://YOUR_DROPLET_IP/jobs`
3. Free hosting, free SSL, free CDN

---

## Cost Summary

### Recommended Setup: Railway + Neon

| Service | Cost | What It Does |
|---------|------|--------------|
| Railway (API) | $5/mo | Hosts API server 24/7 |
| Railway (Scraper) | Included | Auto-scraper running 24/7 |
| Neon Database | $0 | PostgreSQL (3 GB free) |
| **Total** | **$5/month** | Complete job aggregation platform |

### Alternative: DigitalOcean + Neon

| Service | Cost | What It Does |
|---------|------|--------------|
| DigitalOcean Droplet | $6/mo | API + Scraper + Website |
| Neon Database | $0 | PostgreSQL (3 GB free) |
| Domain (optional) | $12/yr | Custom domain |
| **Total** | **$6/month** | Full control, better performance |

---

## Next Steps

**I recommend starting with Railway** because:
1. ✅ Easiest to set up (5-10 minutes)
2. ✅ Auto-deploys from GitHub
3. ✅ $5/month (affordable)
4. ✅ Can migrate to DigitalOcean later if needed

**Would you like me to:**
1. Create the Railway deployment files (Procfile, etc.)?
2. Walk you through Railway setup step-by-step?
3. Or set up DigitalOcean if you prefer full control?

Let me know which option you prefer! 🚀
