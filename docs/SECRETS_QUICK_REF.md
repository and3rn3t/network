# 🔐 GitHub Secrets Quick Reference

## Add These 4 Secrets to GitHub

**Location:** https://github.com/and3rn3t/network/settings/secrets/actions

| Secret Name             | Where to Get It                                                                                         | Example Value              |
| ----------------------- | ------------------------------------------------------------------------------------------------------- | -------------------------- |
| `CLOUDFLARE_API_TOKEN`  | [Create Token](https://dash.cloudflare.com/profile/api-tokens) → Use "Edit Cloudflare Workers" template | `abc123...xyz789`          |
| `CLOUDFLARE_ACCOUNT_ID` | [Cloudflare Dashboard](https://dash.cloudflare.com) → Workers & Pages → Right sidebar                   | `1234567890abcdef`         |
| `VITE_API_BASE_URL`     | Your backend API URL (update after backend deploy)                                                      | `https://api.andernet.dev` |
| `VITE_WS_BASE_URL`      | Your WebSocket URL (update after backend deploy)                                                        | `wss://api.andernet.dev`   |

---

## Quick Steps

### 1. Get Cloudflare Info

```
Cloudflare API Token:    dash.cloudflare.com/profile/api-tokens
Cloudflare Account ID:   dash.cloudflare.com (Workers & Pages section)
```

### 2. Add to GitHub

1. Go to: **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add each secret (name must match exactly!)
4. Click **Add secret**

### 3. Push to Deploy

```powershell
git push origin main
```

Watch progress at: https://github.com/and3rn3t/network/actions

### 4. Add Custom Domain

After first deploy:

1. Go to [Cloudflare Pages](https://dash.cloudflare.com/pages)
2. Select **unifi-network** project
3. **Custom domains** → **Set up a custom domain**
4. Enter: `net.andernet.dev`
5. Click **Activate domain**

---

## That's It!

Every push to `main` branch will now automatically:
✅ Build the frontend
✅ Deploy to Cloudflare Pages
✅ Update https://net.andernet.dev

See full details in: `docs/GITHUB_SECRETS_SETUP.md`
