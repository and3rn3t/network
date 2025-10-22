# Deploy UniFi Network to Cloudflare Pages
# Run this script to build and deploy the frontend

Write-Host "`n=== UniFi Network - Cloudflare Deployment ===" -ForegroundColor Cyan
Write-Host "Domain: net.andernet.dev`n" -ForegroundColor Gray

# Step 1: Check if we're in the right directory
if (-not (Test-Path "frontend\package.json")) {
    Write-Host "❌ Error: Must run from project root (c:\git\network)" -ForegroundColor Red
    exit 1
}

# Step 2: Check if wrangler is installed
Write-Host "[1/5] Checking Wrangler installation..." -ForegroundColor Yellow
$wranglerInstalled = Get-Command wrangler -ErrorAction SilentlyContinue
if (-not $wranglerInstalled) {
    Write-Host "⚠️  Wrangler not found. Installing globally..." -ForegroundColor Yellow
    npm install -g wrangler
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install Wrangler" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Wrangler installed" -ForegroundColor Green
}
else {
    Write-Host "✅ Wrangler is installed" -ForegroundColor Green
}

# Step 3: Install dependencies
Write-Host "`n[2/5] Installing frontend dependencies..." -ForegroundColor Yellow
cd frontend
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Dependencies installed" -ForegroundColor Green

# Step 4: Build frontend
Write-Host "`n[3/5] Building frontend for production..." -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed" -ForegroundColor Red
    Write-Host "Check errors above and fix before deploying" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Build completed successfully" -ForegroundColor Green

# Step 5: Check build output
if (-not (Test-Path "dist\index.html")) {
    Write-Host "❌ Build output not found (dist\index.html)" -ForegroundColor Red
    exit 1
}
$distSize = (Get-ChildItem dist -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "   Build size: $([math]::Round($distSize, 2)) MB" -ForegroundColor Gray

# Step 6: Deploy to Cloudflare
Write-Host "`n[4/5] Deploying to Cloudflare Pages..." -ForegroundColor Yellow
Write-Host "   Project: unifi-network" -ForegroundColor Gray
Write-Host "   Domain: net.andernet.dev" -ForegroundColor Gray
Write-Host ""

# Check if user is logged in to Cloudflare
wrangler whoami 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Not logged in to Cloudflare. Running login..." -ForegroundColor Yellow
    wrangler login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Login failed" -ForegroundColor Red
        exit 1
    }
}

# Deploy
npx wrangler pages deploy dist --project-name=unifi-network --branch=main
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Deployment failed" -ForegroundColor Red
    exit 1
}

Write-Host "`n✅ Deployment successful!" -ForegroundColor Green

# Step 7: Summary
Write-Host "`n[5/5] Deployment Summary" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "Frontend URL:  " -NoNewline; Write-Host "https://net.andernet.dev" -ForegroundColor Cyan
Write-Host "Pages Dashboard: " -NoNewline; Write-Host "https://dash.cloudflare.com/pages" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

Write-Host "`n⚠️  Important Next Steps:" -ForegroundColor Yellow
Write-Host "1. Set up custom domain in Cloudflare Pages dashboard:" -ForegroundColor White
Write-Host "   → Go to project → Custom domains → Add net.andernet.dev" -ForegroundColor Gray
Write-Host "2. Deploy backend API (see docs/CLOUDFLARE_DEPLOYMENT.md):" -ForegroundColor White
Write-Host "   → Recommended: Railway.app or Render.com" -ForegroundColor Gray
Write-Host "   → Update .env.production with actual API URL" -ForegroundColor Gray
Write-Host "3. Configure CORS on backend to allow net.andernet.dev" -ForegroundColor White
Write-Host "4. Test the deployed application:" -ForegroundColor White
Write-Host "   → Visit https://net.andernet.dev" -ForegroundColor Gray
Write-Host "   → Check browser console for errors" -ForegroundColor Gray
Write-Host "   → Verify API calls work" -ForegroundColor Gray

Write-Host "`n🚀 Frontend deployed! Now deploy the backend API." -ForegroundColor Green
Write-Host ""

cd ..
