# Quick Cloudflare Deployment

## 🚀 Deploy Now (5 minutes)

### Method 1: Automated Script

```powershell
cd c:\git\network
.\scripts\deploy_cloudflare.ps1
```

This will:

1. ✅ Check Wrangler installation
2. ✅ Install dependencies
3. ✅ Build frontend
4. ✅ Deploy to Cloudflare Pages
5. ✅ Show you next steps

---

### Method 2: Manual Steps

```powershell
# 1. Install Wrangler
npm install -g wrangler

# 2. Login to Cloudflare
wrangler login

# 3. Build frontend
cd c:\git\network\frontend
npm install
npm run build

# 4. Deploy
npx wrangler pages deploy dist --project-name=unifi-network
```

---

## 📋 After Deployment Checklist

### 1. Add Custom Domain

1. Go to <https://dash.cloudflare.com/pages>
2. Click your project: **unifi-network**
3. Go to **Custom domains**
4. Click **Set up a custom domain**
5. Enter: `net.andernet.dev`
6. Click **Activate domain**
7. Wait 5-10 minutes for DNS propagation

### 2. Set Environment Variables

Your frontend needs to know where the backend API is:

1. In Cloudflare Pages dashboard
2. Go to **Settings** → **Environment variables**
3. Click **Add variable** for Production:

| Variable Name       | Value            | Example                    |
| ------------------- | ---------------- | -------------------------- |
| `VITE_API_BASE_URL` | Your backend URL | `https://api.andernet.dev` |
| `VITE_WS_BASE_URL`  | WebSocket URL    | `wss://api.andernet.dev`   |

4. Click **Save**
5. Redeploy (click **View builds** → **Retry deployment**)

### 3. Deploy Backend API

**Option A: Railway.app (Recommended - Free tier)**

1. Go to <https://railway.app>
2. Click **Start a New Project**
3. Click **Deploy from GitHub repo**
4. Select `and3rn3t/network`
5. Select root directory: `backend/`
6. Railway auto-detects FastAPI
7. Add environment variables:
   - `DATABASE_URL=sqlite:///./network.db`
   - `CORS_ORIGINS=https://net.andernet.dev`
8. Deploy!
9. Copy the generated URL (e.g., `unifi-backend.railway.app`)
10. Add custom domain: `api.andernet.dev`

**Option B: Render.com (Free tier)**

1. Go to <https://render.com>
2. Click **New** → **Web Service**
3. Connect GitHub: `and3rn3t/network`
4. Set root directory: `backend`
5. Environment: Python 3
6. Build command: `pip install -r requirements.txt`
7. Start command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
8. Add environment variables (same as above)
9. Deploy!

**Option C: DigitalOcean App Platform ($5/month)**

1. Go to <https://cloud.digitalocean.com/apps>
2. Create App → GitHub
3. Select `backend/` folder
4. Auto-detects Python
5. Configure environment variables
6. Deploy

### 4. Configure DNS

In your Cloudflare DNS dashboard, you should see:

```
Type    Name    Content                           Proxy
──────────────────────────────────────────────────────────
CNAME   net     unifi-network.pages.dev          ✓ Proxied
CNAME   api     your-backend-url.railway.app     ✓ Proxied
```

Cloudflare automatically creates the `net` record when you add custom domain.

You need to add the `api` record manually:

1. Go to Cloudflare DNS
2. Click **Add record**
3. Type: CNAME
4. Name: `api`
5. Target: `your-backend.railway.app` (or your backend URL)
6. Proxy: ✓ On (orange cloud)
7. Save

---

## ✅ Testing Deployment

### 1. Test Frontend

```powershell
# Open in browser
start https://net.andernet.dev

# Or use curl
curl https://net.andernet.dev
```

**Expected:** See the login page

### 2. Test Backend API

```powershell
curl https://api.andernet.dev/api/alerts
```

**Expected:** JSON response with alerts

### 3. Test Full App

1. Navigate to <https://net.andernet.dev>
2. Login
3. Check Dashboard loads
4. Navigate to **Alert System** menu
5. Test all 3 pages load:
   - Active Alerts
   - Alert Rules
   - Notification Channels
6. Open browser DevTools (F12)
7. Check Network tab - all API calls should return 200
8. Check Console - no errors

---

## 🔄 Update Deployment

### Auto-deploy on Git Push

Once GitHub Actions is set up:

```powershell
cd c:\git\network
git add .
git commit -m "Update frontend"
git push origin main
```

GitHub Actions automatically builds and deploys!

### Manual Redeploy

```powershell
cd c:\git\network\frontend
npm run build
npx wrangler pages deploy dist --project-name=unifi-network
```

---

## 🎯 GitHub Actions Setup (Auto-deploy)

### 1. Get Cloudflare Credentials

**API Token:**

1. Go to <https://dash.cloudflare.com/profile/api-tokens>
2. Click **Create Token**
3. Use template: **Edit Cloudflare Workers**
4. Or create custom with:
   - Account: Cloudflare Pages - Edit
   - Zone: DNS - Edit
5. Click **Continue to summary** → **Create Token**
6. **Copy the token** (shown only once!)

**Account ID:**

1. Go to <https://dash.cloudflare.com>
2. Click **Workers & Pages**
3. Find **Account ID** on right side
4. Copy it

### 2. Add Secrets to GitHub

1. Go to your GitHub repo: <https://github.com/and3rn3t/network>
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these secrets:

| Secret Name             | Value                       |
| ----------------------- | --------------------------- |
| `CLOUDFLARE_API_TOKEN`  | Your API token from step 1  |
| `CLOUDFLARE_ACCOUNT_ID` | Your Account ID from step 1 |
| `VITE_API_BASE_URL`     | `https://api.andernet.dev`  |
| `VITE_WS_BASE_URL`      | `wss://api.andernet.dev`    |

### 3. Enable Actions

GitHub Actions workflow is already created: `.github/workflows/deploy-cloudflare.yml`

Next push to `main` branch will auto-deploy!

---

## 💰 Cost Summary

| Service                | Cost                                             |
| ---------------------- | ------------------------------------------------ |
| Cloudflare Pages       | **FREE** (500 builds/month, unlimited bandwidth) |
| Custom Domain          | **FREE** (if you own andernet.dev)               |
| Backend - Railway      | **FREE** tier (500 hours/month)                  |
| Backend - Render       | **FREE** tier (750 hours/month)                  |
| Backend - DigitalOcean | **$5/month**                                     |
| **Total**              | **$0-5/month**                                   |

---

## 🆘 Troubleshooting

### Build Fails

```powershell
# Clean install
cd c:\git\network\frontend
Remove-Item node_modules -Recurse -Force
Remove-Item package-lock.json -Force
npm install
npm run build
```

### "Not logged in to Cloudflare"

```powershell
wrangler login
# Opens browser for authentication
```

### CORS Errors

Update backend CORS settings:

```python
# backend/src/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://net.andernet.dev"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API Calls Fail

1. Check environment variables in Cloudflare Pages
2. Verify backend is running
3. Check browser console for exact error
4. Test API directly: `curl https://api.andernet.dev/api/alerts`

---

## 📚 Resources

- **Cloudflare Pages Docs:** <https://developers.cloudflare.com/pages/>
- **Wrangler CLI Docs:** <https://developers.cloudflare.com/workers/wrangler/>
- **Railway Docs:** <https://docs.railway.app/>
- **Your Deployment Guide:** `docs/CLOUDFLARE_DEPLOYMENT.md`

---

**Ready to deploy?** Run:

```powershell
cd c:\git\network
.\scripts\deploy_cloudflare.ps1
```

🚀 Good luck!
