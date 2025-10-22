# Deploy UniFi Network API to Cloudflare Workers
# Run from workers directory

Write-Host "`n=== UniFi Network API - Cloudflare Workers Deployment ===" -ForegroundColor Cyan
Write-Host "Domain: api.andernet.dev`n" -ForegroundColor Gray

# Check if we're in the workers directory
if (-not (Test-Path "package.json")) {
    Write-Host "❌ Error: Must run from workers directory (c:\git\network\workers)" -ForegroundColor Red
    exit 1
}

# Step 1: Install dependencies
Write-Host "[1/5] Installing dependencies..." -ForegroundColor Yellow
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Dependencies installed" -ForegroundColor Green

# Step 2: Type check
Write-Host "`n[2/5] Running type check..." -ForegroundColor Yellow
npm run type-check
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Type check failed - continuing anyway" -ForegroundColor Yellow
} else {
    Write-Host "✅ Type check passed" -ForegroundColor Green
}

# Step 3: Check Wrangler login
Write-Host "`n[3/5] Checking Wrangler authentication..." -ForegroundColor Yellow
wrangler whoami 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Not logged in to Wrangler" -ForegroundColor Yellow
    Write-Host "   Please run: wrangler login" -ForegroundColor Gray
    exit 1
}
Write-Host "✅ Wrangler authenticated" -ForegroundColor Green

# Step 4: Create D1 database (if needed)
Write-Host "`n[4/5] Setting up Cloudflare resources..." -ForegroundColor Yellow
Write-Host "   Checking D1 database..." -ForegroundColor Gray
wrangler d1 list | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ℹ️  D1 databases exist - check wrangler.toml for correct IDs" -ForegroundColor Blue
} else {
    Write-Host "   Creating D1 database..." -ForegroundColor Gray
    Write-Host "   Run: wrangler d1 create network-db" -ForegroundColor Yellow
    Write-Host "   Then update wrangler.toml with the database_id" -ForegroundColor Yellow
}

Write-Host "   Checking KV namespace..." -ForegroundColor Gray
wrangler kv:namespace list | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ℹ️  KV namespaces exist - check wrangler.toml for correct IDs" -ForegroundColor Blue
} else {
    Write-Host "   Creating KV namespace..." -ForegroundColor Gray
    Write-Host "   Run: wrangler kv:namespace create CACHE" -ForegroundColor Yellow
    Write-Host "   Then update wrangler.toml with the id" -ForegroundColor Yellow
}

# Step 5: Deploy
Write-Host "`n[5/5] Deploying to Cloudflare Workers..." -ForegroundColor Yellow
Write-Host "   Project: network-api" -ForegroundColor Gray
Write-Host "   Domain: api.andernet.dev (configure in dashboard)" -ForegroundColor Gray

wrangler deploy
if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ Deployment failed" -ForegroundColor Red
    Write-Host "   Check errors above and fix before retrying" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n✅ Deployment complete!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Add custom domain 'api.andernet.dev' in Cloudflare dashboard" -ForegroundColor White
Write-Host "2. Initialize database: wrangler d1 execute network-db --file=schema.sql" -ForegroundColor White
Write-Host "3. Set JWT_SECRET: wrangler secret put JWT_SECRET" -ForegroundColor White
Write-Host "4. Test API: https://api.andernet.dev/health" -ForegroundColor White
Write-Host "`n📚 See README.md for full documentation" -ForegroundColor Gray
