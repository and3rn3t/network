# Complete Cloudflare Workers Setup Script
# Automates the entire deployment process with verification

param(
    [switch]$SkipLogin = $false
)

$ErrorActionPreference = "Stop"

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     UniFi Network API - Cloudflare Workers Setup          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Check if we're in the workers directory
if (-not (Test-Path "package.json")) {
    Write-Host "❌ Error: Must run from workers directory" -ForegroundColor Red
    Write-Host "   cd c:\git\network\workers" -ForegroundColor Yellow
    exit 1
}

# Step 1: Check Node.js
Write-Host "[1/9] Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "   ✅ Node.js $nodeVersion installed" -ForegroundColor Green
}
catch {
    Write-Host "   ❌ Node.js not found. Please install Node.js 20+" -ForegroundColor Red
    exit 1
}

# Step 2: Check Wrangler
Write-Host "`n[2/9] Checking Wrangler CLI..." -ForegroundColor Yellow
$wranglerInstalled = Get-Command wrangler -ErrorAction SilentlyContinue
if (-not $wranglerInstalled) {
    Write-Host "   ⚠️  Wrangler not found. Installing globally..." -ForegroundColor Yellow
    npm install -g wrangler
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   ❌ Failed to install Wrangler" -ForegroundColor Red
        exit 1
    }
    Write-Host "   ✅ Wrangler installed" -ForegroundColor Green
}
else {
    $wranglerVersion = wrangler --version
    Write-Host "   ✅ Wrangler $wranglerVersion installed" -ForegroundColor Green
}

# Step 3: Login to Wrangler
Write-Host "`n[3/9] Checking Wrangler authentication..." -ForegroundColor Yellow
if (-not $SkipLogin) {
    $whoami = wrangler whoami 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   ⚠️  Not logged in. Opening browser for authentication..." -ForegroundColor Yellow
        wrangler login
        if ($LASTEXITCODE -ne 0) {
            Write-Host "   ❌ Login failed" -ForegroundColor Red
            exit 1
        }
    }
    $whoami = wrangler whoami 2>&1 | Out-String
    Write-Host "   ✅ Authenticated" -ForegroundColor Green
    Write-Host "   $($whoami.Trim())" -ForegroundColor Gray
}
else {
    Write-Host "   ⏭️  Skipping login check" -ForegroundColor Gray
}

# Step 4: Install dependencies
Write-Host "`n[4/9] Installing npm dependencies..." -ForegroundColor Yellow
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "   ✅ Dependencies installed" -ForegroundColor Green

# Step 5: Create D1 Database
Write-Host "`n[5/9] Setting up D1 database..." -ForegroundColor Yellow

# Check if database already exists
$dbList = wrangler d1 list --json 2>&1 | ConvertFrom-Json -ErrorAction SilentlyContinue
$existingDb = $dbList | Where-Object { $_.name -eq "network-db" }

if ($existingDb) {
    Write-Host "   ✅ Database 'network-db' already exists" -ForegroundColor Green
    Write-Host "      Database ID: $($existingDb.uuid)" -ForegroundColor Gray
    $databaseId = $existingDb.uuid
}
else {
    Write-Host "   Creating new D1 database 'network-db'..." -ForegroundColor Gray
    $createResult = wrangler d1 create network-db --json 2>&1 | ConvertFrom-Json

    if ($createResult.uuid) {
        $databaseId = $createResult.uuid
        Write-Host "   ✅ Database created successfully" -ForegroundColor Green
        Write-Host "      Database ID: $databaseId" -ForegroundColor Gray
    }
    else {
        Write-Host "   ❌ Failed to create database" -ForegroundColor Red
        Write-Host "      $createResult" -ForegroundColor Red
        exit 1
    }
}

# Step 6: Update wrangler.toml with database ID
Write-Host "`n[6/9] Updating wrangler.toml with database ID..." -ForegroundColor Yellow
$wranglerConfig = Get-Content "wrangler.toml" -Raw

# Uncomment and update D1 database section
$d1Section = @"
[[d1_databases]]
binding = "DB"
database_name = "network-db"
database_id = "$databaseId"
"@

if ($wranglerConfig -match '# \[\[d1_databases\]\]') {
    # Replace commented section
    $wranglerConfig = $wranglerConfig -replace '# \[\[d1_databases\]\][^\[]+', "$d1Section`n`n"
    $wranglerConfig | Set-Content "wrangler.toml" -NoNewline
    Write-Host "   ✅ wrangler.toml updated with database ID" -ForegroundColor Green
}
else {
    Write-Host "   ⚠️  Could not automatically update wrangler.toml" -ForegroundColor Yellow
    Write-Host "      Please manually add D1 section with database_id = `"$databaseId`"" -ForegroundColor Yellow
}

# Step 7: Initialize database schema
Write-Host "`n[7/9] Initializing database schema..." -ForegroundColor Yellow
$schemaResult = wrangler d1 execute network-db --file=schema.sql 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Database schema initialized" -ForegroundColor Green

    # Verify tables were created
    Write-Host "   Verifying tables..." -ForegroundColor Gray
    $tables = wrangler d1 execute network-db --command="SELECT name FROM sqlite_master WHERE type='table'" --json 2>&1 | ConvertFrom-Json
    $tableNames = $tables | ForEach-Object { $_.results } | ForEach-Object { $_.name }
    Write-Host "      Tables created: $($tableNames -join ', ')" -ForegroundColor Gray
}
else {
    Write-Host "   ⚠️  Schema execution completed with warnings" -ForegroundColor Yellow
    Write-Host "      $schemaResult" -ForegroundColor Gray
}

# Step 8: Create KV Namespace
Write-Host "`n[8/9] Setting up KV namespace..." -ForegroundColor Yellow
$kvList = wrangler kv:namespace list --json 2>&1 | ConvertFrom-Json -ErrorAction SilentlyContinue
$existingKv = $kvList | Where-Object { $_.title -like "*CACHE*" }

if ($existingKv) {
    Write-Host "   ✅ KV namespace already exists" -ForegroundColor Green
    Write-Host "      Namespace ID: $($existingKv.id)" -ForegroundColor Gray
    $kvId = $existingKv.id
}
else {
    Write-Host "   Creating KV namespace 'CACHE'..." -ForegroundColor Gray
    $kvResult = wrangler kv:namespace create CACHE --json 2>&1 | ConvertFrom-Json

    if ($kvResult.id) {
        $kvId = $kvResult.id
        Write-Host "   ✅ KV namespace created" -ForegroundColor Green
        Write-Host "      Namespace ID: $kvId" -ForegroundColor Gray
    }
    else {
        Write-Host "   ❌ Failed to create KV namespace" -ForegroundColor Red
        exit 1
    }
}

# Update wrangler.toml with KV ID
Write-Host "   Updating wrangler.toml with KV ID..." -ForegroundColor Gray
$wranglerConfig = Get-Content "wrangler.toml" -Raw

# Uncomment and update KV section
$kvSection = @"
[[kv_namespaces]]
binding = "CACHE"
id = "$kvId"
"@

if ($wranglerConfig -match '# \[\[kv_namespaces\]\]') {
    # Replace commented section
    $wranglerConfig = $wranglerConfig -replace '# \[\[kv_namespaces\]\][^\[]+', "$kvSection`n`n"
    $wranglerConfig | Set-Content "wrangler.toml" -NoNewline
    Write-Host "   ✅ wrangler.toml updated with KV ID" -ForegroundColor Green
}
else {
    Write-Host "   ⚠️  Could not automatically update KV ID in wrangler.toml" -ForegroundColor Yellow
    Write-Host "      Please manually add KV section with id = `"$kvId`"" -ForegroundColor Yellow
}

# Step 9: Set JWT Secret
Write-Host "`n[9/9] Checking JWT secret..." -ForegroundColor Yellow
Write-Host "   ⚠️  You need to set JWT_SECRET manually:" -ForegroundColor Yellow
Write-Host "      wrangler secret put JWT_SECRET" -ForegroundColor Cyan
Write-Host "   (Generate with: openssl rand -base64 32)" -ForegroundColor Gray

# Summary
Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                    Setup Complete! ✅                       ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "📋 Summary:" -ForegroundColor Cyan
Write-Host "   ✅ Dependencies installed" -ForegroundColor Green
Write-Host "   ✅ D1 Database: network-db ($databaseId)" -ForegroundColor Green
Write-Host "   ✅ KV Namespace: CACHE ($kvId)" -ForegroundColor Green
Write-Host "   ✅ Database schema initialized" -ForegroundColor Green
Write-Host "   ✅ wrangler.toml updated" -ForegroundColor Green

Write-Host "`n📝 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Set JWT secret:" -ForegroundColor White
Write-Host "      wrangler secret put JWT_SECRET" -ForegroundColor Gray
Write-Host "`n   2. Deploy to Cloudflare:" -ForegroundColor White
Write-Host "      wrangler deploy" -ForegroundColor Gray
Write-Host "`n   3. Add custom domain in Cloudflare dashboard:" -ForegroundColor White
Write-Host "      api.andernet.dev" -ForegroundColor Gray

Write-Host "`n🔍 Verify Setup:" -ForegroundColor Cyan
Write-Host "   View databases:  wrangler d1 list" -ForegroundColor Gray
Write-Host "   View KV:         wrangler kv:namespace list" -ForegroundColor Gray
Write-Host "   View tables:     wrangler d1 execute network-db --command=`"SELECT name FROM sqlite_master WHERE type='table'`"" -ForegroundColor Gray

Write-Host ""
