# GitHub Secrets Setup for Cloudflare Auto-Deploy

## Required Secrets

Add these 4 secrets to your GitHub repository to enable automatic deployment on every push to `main`:

### 1. CLOUDFLARE_API_TOKEN

**Where to get it:**

1. Go to: <https://dash.cloudflare.com/profile/api-tokens>
2. Click **Create Token**
3. Use template: **Edit Cloudflare Workers** (or create custom token)
4. Permissions needed:
   - Account → Cloudflare Pages → Edit
   - Zone → DNS → Edit (optional, for custom domains)
5. Click **Continue to summary** → **Create Token**
6. **Copy the token** (shown only once!)

**Value format:** `YOUR_CLOUDFLARE_API_TOKEN_HERE`

---

### 2. CLOUDFLARE_ACCOUNT_ID

**Where to get it:**

1. Go to: <https://dash.cloudflare.com>
2. Click **Workers & Pages** in the sidebar
3. On the right side, you'll see **Account ID**
4. Copy the Account ID

**Value format:** `abc123def456ghi789` (example)

---

### 3. VITE_API_BASE_URL

**Value:** `https://api.andernet.dev`

(Update this to your actual backend URL once deployed)

---

### 4. VITE_WS_BASE_URL

**Value:** `wss://api.andernet.dev`

(Update this to your actual WebSocket URL once deployed)

---

## How to Add Secrets to GitHub

1. Go to your repository: <https://github.com/and3rn3t/network>

2. Click **Settings** tab (top navigation)

3. In the left sidebar, expand **Secrets and variables** → Click **Actions**

4. Click the **New repository secret** button

5. For each secret above:

   - **Name:** Enter the exact name (e.g., `CLOUDFLARE_API_TOKEN`)
   - **Secret:** Paste the value
   - Click **Add secret**

6. Repeat for all 4 secrets

---

## Verify Secrets Added

You should see 4 secrets listed:

```
CLOUDFLARE_API_TOKEN      Updated X minutes ago
CLOUDFLARE_ACCOUNT_ID     Updated X minutes ago
VITE_API_BASE_URL         Updated X minutes ago
VITE_WS_BASE_URL          Updated X minutes ago
```

**Note:** You can't view secret values after adding them (security feature). You can only update or delete them.

---

## Test Auto-Deploy

Once secrets are added:

```powershell
# Make a small change
cd c:\git\network
echo "# Test deploy" >> README.md

# Commit and push
git add .
git commit -m "Test Cloudflare auto-deploy"
git push origin main
```

**What happens:**

1. GitHub detects push to `main` branch
2. GitHub Actions workflow starts (`.github/workflows/deploy-cloudflare.yml`)
3. Workflow builds frontend
4. Workflow deploys to Cloudflare Pages
5. Site is live at Cloudflare-generated URL

**View progress:**

- Go to: <https://github.com/and3rn3t/network/actions>
- Click on the latest workflow run
- Watch the build and deploy steps in real-time

---

## After First Deploy

### 1. Find Your Cloudflare Pages URL

After first deployment, Cloudflare gives you a URL like:

- `unifi-network.pages.dev`
- `unifi-network-abc.pages.dev`

### 2. Add Custom Domain

1. Go to: <https://dash.cloudflare.com/pages>
2. Click your project: **unifi-network**
3. Click **Custom domains** tab
4. Click **Set up a custom domain**
5. Enter: `net.andernet.dev`
6. Click **Activate domain**
7. Cloudflare automatically creates DNS records
8. Wait 5-10 minutes for DNS propagation

### 3. Test Your Site

Visit: <https://net.andernet.dev>

You should see the login page!

---

## Update Environment Variables Later

If you need to change API URLs after deployment:

1. Go to: <https://dash.cloudflare.com/pages>
2. Click your project: **unifi-network**
3. Click **Settings** tab
4. Scroll to **Environment variables**
5. Edit the variables:
   - `VITE_API_BASE_URL`
   - `VITE_WS_BASE_URL`
6. Click **Save**
7. Go to **Deployments** tab
8. Click **...** on latest deployment → **Retry deployment**

---

## Troubleshooting

### "Workflow failed"

Check the error in GitHub Actions:

1. Go to: <https://github.com/and3rn3t/network/actions>
2. Click the failed run
3. Expand the failed step to see error
4. Common issues:
   - Wrong secret names (must match exactly)
   - Invalid API token (create new one)
   - Build errors (fix code and push again)

### "Can't find CLOUDFLARE_API_TOKEN"

Make sure:

- Secret name is EXACTLY `CLOUDFLARE_API_TOKEN` (case-sensitive)
- You added it under **Secrets and variables** → **Actions** (not Dependabot)

### "Invalid API token"

1. Delete the old token in Cloudflare
2. Create a new token with correct permissions
3. Update the secret in GitHub

---

## Summary Checklist

- [ ] Get Cloudflare API Token from <https://dash.cloudflare.com/profile/api-tokens>
- [ ] Get Cloudflare Account ID from <https://dash.cloudflare.com>
- [ ] Add 4 secrets to GitHub repo: <https://github.com/and3rn3t/network/settings/secrets/actions>
- [ ] Push to main branch to trigger deploy
- [ ] Check GitHub Actions for build progress: <https://github.com/and3rn3t/network/actions>
- [ ] Add custom domain `net.andernet.dev` in Cloudflare Pages
- [ ] Test site at <https://net.andernet.dev>
- [ ] Deploy backend API (see DEPLOY_QUICK_START.md)
- [ ] Update environment variables with real API URL

---

**Ready?** Add those secrets and push your code! 🚀

The workflow file is already configured: `.github/workflows/deploy-cloudflare.yml`
