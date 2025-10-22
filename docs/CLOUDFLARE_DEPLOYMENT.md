# Cloudflare Deployment Guide

## Architecture Overview

Your UniFi Network app has two parts:

1. **Frontend (React/Vite)** → Deploy to Cloudflare Pages
2. **Backend (FastAPI)** → Deploy to Cloudflare Workers or separate server

## Option 1: Frontend Only on Cloudflare Pages (Recommended)

### Prerequisites

1. Cloudflare account
2. GitHub repository pushed
3. Custom domain `net.andernet.dev` added to Cloudflare

### Step 1: Build Configuration

The frontend is already configured with Vite. Test local build:

```powershell
cd c:\git\network\frontend
npm run build
```

This creates `dist/` folder with static files.

### Step 2: Deploy to Cloudflare Pages

#### Via Dashboard (Easiest)

1. Go to <https://dash.cloudflare.com>
2. Click **Pages** in sidebar
3. Click **Create a project**
4. Click **Connect to Git**
5. Select repository: `and3rn3t/network`
6. Configure build:
   - **Project name:** `unifi-network`
   - **Production branch:** `main`
   - **Build command:** `npm run build`
   - **Build output directory:** `dist`
   - **Root directory:** `frontend`
7. Click **Save and Deploy**

#### Via Wrangler CLI (Alternative)

```powershell
# Install Wrangler
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Deploy
cd c:\git\network\frontend
npm run build
wrangler pages deploy dist --project-name=unifi-network
```

### Step 3: Add Custom Domain

1. In Cloudflare Pages dashboard
2. Go to your project → **Custom domains**
3. Click **Set up a custom domain**
4. Enter: `net.andernet.dev`
5. Click **Continue**
6. Cloudflare automatically creates DNS records
7. Wait 5-10 minutes for DNS propagation

### Step 4: Configure API Backend URL

The frontend needs to know where the backend API is. You have options:

#### Option A: Backend on Separate Server

Update API calls to point to your backend server:

1. Create environment variable file:

```powershell
# Create .env.production in frontend/
cd c:\git\network\frontend
```

Create `frontend/.env.production`:

```env
VITE_API_BASE_URL=https://api.andernet.dev
VITE_WS_BASE_URL=wss://api.andernet.dev
```

2. Update API calls to use environment variable (if not already done)

3. Redeploy frontend

#### Option B: Backend on Cloudflare Workers (Advanced)

See Option 2 below.

---

## Option 2: Full Stack on Cloudflare (Advanced)

Deploy both frontend and backend to Cloudflare infrastructure.

### Backend: FastAPI on Cloudflare Workers

**Challenge:** Cloudflare Workers don't natively support Python/FastAPI.

**Solutions:**

#### 2A: Use Cloudflare Workers with JavaScript/TypeScript

**Pros:** Native support, fast
**Cons:** Requires rewriting backend

Would need to:

1. Rewrite FastAPI routes in TypeScript
2. Use Cloudflare D1 (SQLite) for database
3. Use Cloudflare KV for caching

#### 2B: Use Cloudflare Workers + Python (Beta)

Cloudflare has Python support in beta:

```powershell
# Install dependencies
npm install -g wrangler

# Create worker
wrangler init backend-worker
```

**Note:** Limited Python support, may not support all FastAPI features.

#### 2C: Hybrid Approach (Recommended)

- **Frontend:** Cloudflare Pages (fast, global CDN)
- **Backend:** Traditional hosting (VPS, DigitalOcean, AWS, etc.)

This gives you:

- Fast frontend delivery via CDN
- Full Python/FastAPI support on backend
- Easy database management

---

## Quick Deploy Steps (Frontend Only)

### 1. Push to GitHub

```powershell
cd c:\git\network
git add .
git commit -m "Prepare for Cloudflare deployment"
git push origin main
```

### 2. Create wrangler.toml

```powershell
cd c:\git\network\frontend
```

Create `frontend/wrangler.toml`:

```toml
name = "unifi-network"
compatibility_date = "2025-10-21"

[site]
bucket = "./dist"
```

### 3. Deploy

```powershell
# Build
npm run build

# Deploy to Cloudflare Pages
npx wrangler pages deploy dist --project-name=unifi-network
```

### 4. Set Environment Variables in Cloudflare

1. Go to Pages project → **Settings** → **Environment variables**
2. Add:
   - `VITE_API_BASE_URL` = `https://your-backend-url.com`
   - `VITE_WS_BASE_URL` = `wss://your-backend-url.com`
3. Redeploy

---

## Backend Deployment Options

Since Cloudflare Workers doesn't support Python well, deploy backend separately:

### Option 1: DigitalOcean App Platform

```bash
# Push to GitHub
# Go to DigitalOcean dashboard
# Create New App → GitHub repository
# Select backend/ folder
# Detect Python/FastAPI
# Deploy automatically
```

Cost: ~$5-12/month

### Option 2: Railway.app

```bash
# Go to railway.app
# New Project → Deploy from GitHub
# Select backend/
# Auto-detects FastAPI
# Deploys with free tier
```

Cost: Free tier available

### Option 3: Render.com

```bash
# Go to render.com
# New Web Service
# Connect GitHub
# Select backend/
# Python detected
# Deploy
```

Cost: Free tier available

### Option 4: Self-hosted VPS

Deploy to any VPS (DigitalOcean, Linode, Vultr):

```bash
# SSH to server
git clone https://github.com/and3rn3t/network.git
cd network/backend
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

Use nginx/caddy for reverse proxy and SSL.

---

## Recommended Architecture

```
┌─────────────────────────────────────────┐
│  net.andernet.dev (Cloudflare Pages)   │
│  Frontend: React + Vite                 │
│  CDN: Global edge network               │
└──────────────────┬──────────────────────┘
                   │ HTTPS
                   │
┌──────────────────▼──────────────────────┐
│  api.andernet.dev (Backend Server)      │
│  Backend: FastAPI + Python              │
│  Database: SQLite                       │
│  Hosting: DigitalOcean/Railway/Render   │
└─────────────────────────────────────────┘
```

**Benefits:**

- ✅ Fast frontend (Cloudflare CDN)
- ✅ Full Python/FastAPI support
- ✅ Easy database management
- ✅ Separate scaling for frontend/backend
- ✅ Custom domains for both

---

## Environment Variables Setup

### Frontend (.env.production)

```env
VITE_API_BASE_URL=https://api.andernet.dev
VITE_WS_BASE_URL=wss://api.andernet.dev
```

### Backend (.env)

```env
DATABASE_URL=sqlite:///./network.db
CORS_ORIGINS=https://net.andernet.dev
```

---

## DNS Configuration

In Cloudflare DNS:

```
Type    Name    Content                     Proxy
────────────────────────────────────────────────────
CNAME   net     unifi-network.pages.dev    ✓ Proxied
A/AAAA  api     <backend-server-ip>        ✓ Proxied
```

---

## Complete Deployment Checklist

### Frontend

- [ ] Build locally: `npm run build`
- [ ] Push to GitHub
- [ ] Create Cloudflare Pages project
- [ ] Connect GitHub repository
- [ ] Set root directory: `frontend`
- [ ] Set build command: `npm run build`
- [ ] Set output directory: `dist`
- [ ] Add custom domain: `net.andernet.dev`
- [ ] Add environment variables (API URL)
- [ ] Test deployment

### Backend

- [ ] Choose hosting platform (Railway/Render/DigitalOcean)
- [ ] Deploy backend
- [ ] Get backend URL (e.g., `api.andernet.dev`)
- [ ] Configure CORS for frontend domain
- [ ] Set up database
- [ ] Test API endpoints
- [ ] Add SSL certificate (auto with Cloudflare)

### DNS

- [ ] Add `net` CNAME to Pages
- [ ] Add `api` A/AAAA to backend server
- [ ] Enable Cloudflare proxy (orange cloud)
- [ ] Wait for DNS propagation (5-10 min)

### Testing

- [ ] Visit <https://net.andernet.dev>
- [ ] Check login works
- [ ] Check API calls work
- [ ] Check WebSocket connections
- [ ] Test all Alert Management pages
- [ ] Test data collection

---

## Estimated Costs

| Service          | Cost                            |
| ---------------- | ------------------------------- |
| Cloudflare Pages | Free (100,000 requests/day)     |
| Custom Domain    | $0 (if already have)            |
| Backend Hosting  | $5-12/month (Railway/Render/DO) |
| **Total**        | **~$5-12/month**                |

---

## Next Steps

1. **Deploy Frontend Now:**

   ```powershell
   cd c:\git\network\frontend
   npm run build
   npx wrangler pages deploy dist --project-name=unifi-network
   ```

2. **Choose Backend Hosting** (recommend Railway.app for easy deploy)

3. **Configure DNS** in Cloudflare dashboard

4. **Test** end-to-end

Would you like me to:

1. Create the deployment scripts?
2. Help set up backend hosting?
3. Configure environment variables?
4. Set up CI/CD with GitHub Actions?
