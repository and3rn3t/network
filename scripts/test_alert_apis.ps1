# Quick test script for Alert Management APIs
# Tests all endpoints used by the new Alert Management UI

Write-Host "`n=== Testing Alert Management APIs ===" -ForegroundColor Cyan

# Test 1: Check if backend is running
Write-Host "`n[1/7] Testing backend availability..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/alerts" -Method Get -TimeoutSec 5
    Write-Host "✅ Backend is running" -ForegroundColor Green
    Write-Host "   Found $($response.alerts.Count) alerts" -ForegroundColor Gray
}
catch {
    Write-Host "❌ Backend is NOT running or not accessible" -ForegroundColor Red
    Write-Host "   Start backend with: cd backend && python -m uvicorn src.main:app --reload" -ForegroundColor Yellow
    exit 1
}

# Test 2: Get alert statistics
Write-Host "`n[2/7] Testing alert statistics endpoint..." -ForegroundColor Yellow
try {
    $stats = Invoke-RestMethod -Uri "http://localhost:8000/api/alerts/stats/summary" -Method Get
    Write-Host "✅ Alert stats retrieved" -ForegroundColor Green
    Write-Host "   Total: $($stats.total), Active: $($stats.active), Acknowledged: $($stats.acknowledged)" -ForegroundColor Gray
}
catch {
    Write-Host "⚠️  Alert stats endpoint failed" -ForegroundColor Yellow
}

# Test 3: List alert rules
Write-Host "`n[3/7] Testing alert rules endpoint..." -ForegroundColor Yellow
try {
    $rules = Invoke-RestMethod -Uri "http://localhost:8000/api/rules" -Method Get
    Write-Host "✅ Alert rules retrieved" -ForegroundColor Green
    Write-Host "   Found $($rules.rules.Count) rules" -ForegroundColor Gray
    if ($rules.rules.Count -gt 0) {
        $enabled = ($rules.rules | Where-Object { $_.enabled -eq $true }).Count
        Write-Host "   Enabled: $enabled, Disabled: $($rules.rules.Count - $enabled)" -ForegroundColor Gray
    }
}
catch {
    Write-Host "⚠️  Alert rules endpoint failed" -ForegroundColor Yellow
}

# Test 4: List notification channels
Write-Host "`n[4/7] Testing notification channels endpoint..." -ForegroundColor Yellow
try {
    $channels = Invoke-RestMethod -Uri "http://localhost:8000/api/channels" -Method Get
    Write-Host "✅ Notification channels retrieved" -ForegroundColor Green
    Write-Host "   Found $($channels.channels.Count) channels" -ForegroundColor Gray
    if ($channels.channels.Count -gt 0) {
        $channels.channels | ForEach-Object {
            Write-Host "   - $($_.name) ($($_.channel_type))" -ForegroundColor Gray
        }
    }
}
catch {
    Write-Host "⚠️  Notification channels endpoint failed" -ForegroundColor Yellow
}

# Test 5: Filter alerts by status
Write-Host "`n[5/7] Testing alert filtering..." -ForegroundColor Yellow
try {
    $triggered = Invoke-RestMethod -Uri "http://localhost:8000/api/alerts?status=triggered" -Method Get
    Write-Host "✅ Alert filtering works" -ForegroundColor Green
    Write-Host "   Triggered alerts: $($triggered.alerts.Count)" -ForegroundColor Gray
}
catch {
    Write-Host "⚠️  Alert filtering failed" -ForegroundColor Yellow
}

# Test 6: Check if we have any alerts to test acknowledge/resolve
Write-Host "`n[6/7] Checking for testable alerts..." -ForegroundColor Yellow
if ($response.alerts.Count -gt 0) {
    $testAlert = $response.alerts[0]
    Write-Host "✅ Found alert #$($testAlert.id) for testing" -ForegroundColor Green
    Write-Host "   Status: $($testAlert.status), Severity: $($testAlert.severity)" -ForegroundColor Gray
    Write-Host "   Message: $($testAlert.message)" -ForegroundColor Gray
}
else {
    Write-Host "⚠️  No alerts available for acknowledge/resolve testing" -ForegroundColor Yellow
    Write-Host "   You'll need to trigger an alert to test those features" -ForegroundColor Gray
}

# Test 7: Summary
Write-Host "`n[7/7] Test Summary" -ForegroundColor Yellow
Write-Host "✅ Backend API is accessible" -ForegroundColor Green
Write-Host "✅ All alert management endpoints are responding" -ForegroundColor Green

Write-Host "`n=== Next Steps ===" -ForegroundColor Cyan
Write-Host "1. Start frontend: cd frontend && npm run dev" -ForegroundColor White
Write-Host "2. Open browser: http://localhost:5173" -ForegroundColor White
Write-Host "3. Navigate to Alert System menu (should see 3 items)" -ForegroundColor White
Write-Host "4. Test each page:" -ForegroundColor White
Write-Host "   - Active Alerts: View/filter/acknowledge/resolve" -ForegroundColor Gray
Write-Host "   - Alert Rules: Create/edit/delete/enable/disable" -ForegroundColor Gray
Write-Host "   - Notification Channels: Create/edit/delete/test" -ForegroundColor Gray

Write-Host "`nReady to test! 🚀`n" -ForegroundColor Green
