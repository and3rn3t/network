# Test Cloudflare Workers API Endpoints

$baseUrl = "https://network-api.andernet.workers.dev"

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        Cloudflare Workers API - Endpoint Tests            ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Test 1: Health Check
Write-Host "[1/4] Testing Health Endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get
    Write-Host "   ✅ Health check passed" -ForegroundColor Green
    Write-Host "      Status: $($response.status)" -ForegroundColor Gray
    Write-Host "      Version: $($response.version)" -ForegroundColor Gray
} catch {
    Write-Host "   ❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Ready Check
Write-Host "`n[2/4] Testing Ready Endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/health/ready" -Method Get
    Write-Host "   ✅ Ready check passed" -ForegroundColor Green
    Write-Host "      Database: $($response.database)" -ForegroundColor Gray
} catch {
    Write-Host "   ❌ Ready check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Login
Write-Host "`n[3/4] Testing Login Endpoint..." -ForegroundColor Yellow
try {
    $loginData = @{
        username = "admin"
        password = "admin123"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$baseUrl/api/auth/login" -Method Post `
        -ContentType "application/json" `
        -Body $loginData
    
    Write-Host "   ✅ Login successful" -ForegroundColor Green
    Write-Host "      Token: $($response.access_token.Substring(0, 20))..." -ForegroundColor Gray
    Write-Host "      User: $($response.user.username)" -ForegroundColor Gray
    Write-Host "      Email: $($response.user.email)" -ForegroundColor Gray
    
    # Save token for next test
    $global:token = $response.access_token
} catch {
    Write-Host "   ❌ Login failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Get Current User (with auth)
if ($global:token) {
    Write-Host "`n[4/4] Testing Authenticated Endpoint..." -ForegroundColor Yellow
    try {
        $headers = @{
            Authorization = "Bearer $global:token"
        }
        
        $response = Invoke-RestMethod -Uri "$baseUrl/api/auth/me" -Method Get -Headers $headers
        
        Write-Host "   ✅ Authentication working" -ForegroundColor Green
        Write-Host "      Username: $($response.username)" -ForegroundColor Gray
        Write-Host "      Is Superuser: $($response.is_superuser)" -ForegroundColor Gray
    } catch {
        Write-Host "   ❌ Auth test failed: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "`n[4/4] Authenticated Endpoint..." -ForegroundColor Yellow
    Write-Host "   ⏭️  Skipped (no token)" -ForegroundColor Gray
}

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                    Tests Complete!                         ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "📝 API Endpoints:" -ForegroundColor Cyan
Write-Host "   Base URL: $baseUrl" -ForegroundColor White
Write-Host "   Health: $baseUrl/health" -ForegroundColor Gray
Write-Host "   Docs: See workers/README.md for full API reference`n" -ForegroundColor Gray
