# Complete Cloudflare Deployment Guide

## Overview

This guide walks you through deploying the entire UniFi Network application to Cloudflare:

- **Frontend**: React app on Cloudflare Pages at `net.andernet.dev`
- **Backend API**: Hono API on Cloudflare Workers at `api.andernet.dev`
- **Database**: Cloudflare D1 (SQLite)
- **Cache**: Cloudflare KV
- **WebSocket**: Durable Objects

## Prerequisites

- Cloudflare account
- GitHub repository
- Wrangler CLI installed: `npm install -g wrangler`
- Node.js 20+

## Part 1: Frontend Deployment (Already Complete ✅)

The frontend is already deployed via GitHub Actions to Cloudflare Pages.

- **URL**: `https://network.pages.dev` (or `net.andernet.dev` when custom domain added)
- **Auto-deploys**: On push to `main` branch

## Part 2: Backend API Deployment

### Step 1: Install Workers Dependencies

```powershell
cd c:\git\network\workers
npm install
```

### Step 2: Login to Wrangler

```powershell
wrangler login
```

This opens a browser for authentication.

### Step 3: Create D1 Database

```powershell
wrangler d1 create network-db
```

**Output example**:

```
✅ Successfully created DB 'network-db'!
database_id = "abc123-def456-ghi789"
```

Copy the `database_id` and update `workers/wrangler.toml`:

```toml
[[d1_databases]]
binding = "DB"
database_name = "network-db"
database_id = "abc123-def456-ghi789"  # <-- PASTE HERE
```

### Step 4: Initialize Database Schema

```powershell
wrangler d1 execute network-db --file=schema.sql
```

This creates all tables and inserts the default admin user.

### Step 5: Create KV Namespace

```powershell
wrangler kv:namespace create CACHE
```

**Output example**:

```
✅ Successfully created KV namespace
id = "xyz987xyz987"
```

Update `workers/wrangler.toml`:

```toml
[[kv_namespaces]]
binding = "CACHE"
id = "xyz987xyz987"  # <-- PASTE HERE
```

### Step 6: Set JWT Secret

```powershell
wrangler secret put JWT_SECRET
```

Enter a secure random string (e.g., generate with: `openssl rand -base64 32`)

### Step 7: Deploy API

```powershell
wrangler deploy
```

**Output**:

```
✅ Deployed network-api
   https://network-api.YOUR_SUBDOMAIN.workers.dev
```

### Step 8: Add Custom Domain

1. Go to: https://dash.cloudflare.com/ → Workers & Pages
2. Click on `network-api`
3. Go to "Settings" → "Domains & Routes"
4. Click "Add Custom Domain"
5. Enter: `api.andernet.dev`
6. Click "Add Custom Domain"

Cloudflare will automatically:

- Create DNS records
- Issue SSL certificate
- Route traffic to your worker

Wait 2-5 minutes for DNS propagation.

### Step 9: Test API

```powershell
# Test health endpoint
curl https://api.andernet.dev/health

# Test login (default credentials)
curl -X POST https://api.andernet.dev/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{\"username\":\"admin\",\"password\":\"admin123\"}'
```

## Part 3: Connect Frontend to Backend

### Update Frontend Environment Variables

1. Go to: Cloudflare Pages → `network` project
2. Go to "Settings" → "Environment variables"
3. Add/Update:
   - `VITE_API_BASE_URL` = `https://api.andernet.dev`
   - `VITE_WS_BASE_URL` = `wss://api.andernet.dev`
4. Click "Save"

### Redeploy Frontend

```powershell
cd c:\git\network
git commit --allow-empty -m "Trigger redeploy with new API URL"
git push origin main
```

Wait 2-3 minutes for GitHub Actions to complete.

## Part 4: Add Custom Domain to Frontend

1. Go to: Cloudflare Pages → `network` project
2. Go to "Custom domains"
3. Click "Set up a custom domain"
4. Enter: `net.andernet.dev`
5. Click "Activate domain"

DNS records are created automatically. Wait 5-10 minutes.

## Part 5: GitHub Actions Auto-Deployment

Both frontend and backend auto-deploy on push to `main`:

### Frontend Workflow

- File: `.github/workflows/deploy-cloudflare.yml`
- Triggers: Changes to `frontend/**`
- Deploys to: Cloudflare Pages

### Backend Workflow

- File: `.github/workflows/deploy-workers.yml`
- Triggers: Changes to `workers/**`
- Deploys to: Cloudflare Workers

## Part 6: Change Default Password

**⚠️ IMPORTANT: Do this immediately!**

### Option A: Via API

```powershell
# 1. Login to get token
$login = Invoke-RestMethod -Method POST -Uri "https://api.andernet.dev/api/auth/login" `
  -ContentType "application/json" `
  -Body '{"username":"admin","password":"admin123"}'

$token = $login.access_token

# 2. Change password (create new endpoint for this)
# TODO: Add password change endpoint to API
```

### Option B: Via Database

```powershell
# Generate bcrypt hash for new password
# Use online tool: https://bcrypt-generator.com/

# Update database
wrangler d1 execute network-db --command "UPDATE users SET hashed_password = 'NEW_HASH' WHERE username = 'admin'"
```

## Verification Checklist

- [ ] Frontend accessible at `https://net.andernet.dev`
- [ ] Backend API responding at `https://api.andernet.dev/health`
- [ ] Login works from frontend
- [ ] Alert Management pages load
- [ ] WebSocket connects
- [ ] Default password changed
- [ ] GitHub Actions workflows passing

## Monitoring & Logs

### View API Logs

```powershell
wrangler tail network-api
```

### View Frontend Logs

Go to: Cloudflare Pages → network → Deployments → View logs

### Check API Analytics

Go to: Workers & Pages → network-api → Analytics

## Troubleshooting

### Frontend shows "API connection failed"

1. Check API is deployed: `curl https://api.andernet.dev/health`
2. Check CORS settings in `workers/wrangler.toml`
3. Verify environment variables in Cloudflare Pages

### Database errors

1. Verify D1 database exists: `wrangler d1 list`
2. Check schema applied: `wrangler d1 execute network-db --command "SELECT name FROM sqlite_master WHERE type='table'"`
3. Verify database_id in wrangler.toml matches

### Worker deployment fails

1. Check Wrangler authentication: `wrangler whoami`
2. Verify CLOUDFLARE_API_TOKEN has correct permissions
3. Check wrangler.toml syntax

### Custom domain not working

1. Wait 10-15 minutes for DNS propagation
2. Check DNS records in Cloudflare DNS dashboard
3. Verify domain is added in Workers/Pages settings

## Cost Estimate

All on Cloudflare Free tier:

- **Pages**: 500 builds/month, unlimited requests
- **Workers**: 100,000 requests/day
- **D1**: 5 GB storage, 5 million rows read/day
- **KV**: 100,000 reads/day, 1,000 writes/day
- **Durable Objects**: 1 million requests/month

**Total**: $0/month for moderate usage

## Next Steps

1. Set up monitoring/alerts
2. Add more API endpoints
3. Implement WebSocket real-time updates
4. Add rate limiting
5. Set up automated backups for D1 database

## Support

- Cloudflare Docs: https://developers.cloudflare.com/
- Hono Framework: https://hono.dev/
- Wrangler CLI: https://developers.cloudflare.com/workers/wrangler/
