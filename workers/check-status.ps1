# Cloudflare Workers - Status Check and Manual Setup Guide
# This script verifies what's already done and shows what's left to do

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     Cloudflare Workers - Setup Status Check               ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$allGood = $true

# Check 1: Node.js
Write-Host "[1/7] Node.js..." -ForegroundColor Yellow -NoNewline
try {
    $nodeVersion = node --version 2>&1
    Write-Host " ✅ $nodeVersion" -ForegroundColor Green
}
catch {
    Write-Host " ❌ Not installed" -ForegroundColor Red
    $allGood = $false
}

# Check 2: Wrangler
Write-Host "[2/7] Wrangler CLI..." -ForegroundColor Yellow -NoNewline
try {
    $wranglerVersion = wrangler --version 2>&1 | Select-Object -First 1
    Write-Host " ✅ $wranglerVersion" -ForegroundColor Green
}
catch {
    Write-Host " ❌ Not installed" -ForegroundColor Red
    Write-Host "      Install: npm install -g wrangler" -ForegroundColor Gray
    $allGood = $false
}

# Check 3: Wrangler Auth
Write-Host "[3/7] Wrangler Authentication..." -ForegroundColor Yellow -NoNewline
$whoami = wrangler whoami 2>&1
if ($LASTEXITCODE -eq 0) {
    $email = ($whoami | Select-String "email" | Out-String).Trim()
    Write-Host " ✅ Logged in" -ForegroundColor Green
    if ($email) {
        Write-Host "      $email" -ForegroundColor Gray
    }
}
else {
    Write-Host " ❌ Not logged in" -ForegroundColor Red
    Write-Host "      Run: wrangler login" -ForegroundColor Gray
    $allGood = $false
}

# Check 4: D1 Database
Write-Host "[4/7] D1 Database..." -ForegroundColor Yellow -NoNewline
$dbList = wrangler d1 list 2>&1 | Out-String
if ($dbList -match "network-db") {
    # Extract database ID from wrangler.toml
    $config = Get-Content "wrangler.toml" -Raw
    if ($config -match 'database_id = "([^"]+)"' -and $matches[1] -ne "") {
        Write-Host " ✅ Exists (ID: $($matches[1]))" -ForegroundColor Green
    }
    else {
        Write-Host " ⚠️  Exists but not in wrangler.toml" -ForegroundColor Yellow
        Write-Host "      Get ID: wrangler d1 list" -ForegroundColor Gray
        Write-Host "      Update wrangler.toml database_id" -ForegroundColor Gray
        $allGood = $false
    }
}
else {
    Write-Host " ❌ Not created" -ForegroundColor Red
    Write-Host "      Run: wrangler d1 create network-db" -ForegroundColor Gray
    Write-Host "      Then copy database_id to wrangler.toml" -ForegroundColor Gray
    $allGood = $false
}

# Check 5: Database Schema
Write-Host "[5/7] Database Schema..." -ForegroundColor Yellow -NoNewline
if ($dbList -match "network-db") {
    $tables = wrangler d1 execute network-db --command="SELECT name FROM sqlite_master WHERE type='table'" 2>&1 | Out-String
    if ($tables -match "users" -and $tables -match "alert_rules") {
        Write-Host " ✅ Initialized" -ForegroundColor Green
    }
    else {
        Write-Host " ❌ Not initialized" -ForegroundColor Red
        Write-Host "      Run: wrangler d1 execute network-db --file=schema.sql" -ForegroundColor Gray
        $allGood = $false
    }
}
else {
    Write-Host " ⏭️  Skipped (no database)" -ForegroundColor Gray
}

# Check 6: KV Namespace
Write-Host "[6/7] KV Namespace..." -ForegroundColor Yellow -NoNewline
$kvList = wrangler kv namespace list 2>&1 | Out-String
if ($kvList -match "CACHE") {
    # Extract KV ID from wrangler.toml
    $config = Get-Content "wrangler.toml" -Raw
    if ($config -match '\[\[kv_namespaces\]\].*?binding = "CACHE".*?id = "([^"]+)"' -and $matches[1] -ne "") {
        Write-Host " ✅ Exists (ID: $($matches[1]))" -ForegroundColor Green
    }
    else {
        Write-Host " ⚠️  Exists but not in wrangler.toml" -ForegroundColor Yellow
        Write-Host "      Get ID: wrangler kv namespace list | grep CACHE" -ForegroundColor Gray
        Write-Host "      Update wrangler.toml kv id" -ForegroundColor Gray
        $allGood = $false
    }
}
else {
    Write-Host " ❌ Not created" -ForegroundColor Red
    Write-Host "      Run: wrangler kv namespace create CACHE" -ForegroundColor Gray
    Write-Host "      Then copy id to wrangler.toml" -ForegroundColor Gray
    $allGood = $false
}

# Check 7: JWT Secret
Write-Host "[7/7] JWT Secret..." -ForegroundColor Yellow -NoNewline
$secrets = wrangler secret list 2>&1 | Out-String
if ($secrets -match "JWT_SECRET") {
    Write-Host " ✅ Set" -ForegroundColor Green
}
else {
    Write-Host " ❌ Not set" -ForegroundColor Red
    Write-Host "      Run: wrangler secret put JWT_SECRET" -ForegroundColor Gray
    Write-Host "      (Enter a secure random string)" -ForegroundColor Gray
    $allGood = $false
}

# Summary
Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
if ($allGood) {
    Write-Host "║                  All Checks Passed! ✅                      ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

    Write-Host "🚀 Ready to Deploy!" -ForegroundColor Green
    Write-Host "   Run: wrangler deploy`n" -ForegroundColor White
}
else {
    Write-Host "║            Some Issues Found ⚠️                            ║" -ForegroundColor Yellow
    Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

    Write-Host "📋 Manual Setup Commands:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Create D1 Database:" -ForegroundColor White
    Write-Host "   wrangler d1 create network-db" -ForegroundColor Gray
    Write-Host "   # Copy the database_id and paste into wrangler.toml" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "2. Initialize Database:" -ForegroundColor White
    Write-Host "   wrangler d1 execute network-db --file=schema.sql" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Set JWT Secret:" -ForegroundColor White
    Write-Host "   wrangler secret put JWT_SECRET" -ForegroundColor Gray
    Write-Host "   # Enter: $(openssl rand -base64 32)" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "4. Deploy:" -ForegroundColor White
    Write-Host "   wrangler deploy" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "📖 Full Guide: docs\CLOUDFLARE_QUICK_START.md`n" -ForegroundColor Gray
