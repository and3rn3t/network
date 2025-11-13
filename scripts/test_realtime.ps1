# Test Real-Time Monitoring System
# This script helps restart the backend and run comprehensive tests

Write-Host "`n🚀 UniFi Network Dashboard - Real-Time System Testing" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Step 1: Check if backend is running
Write-Host "`n📍 Step 1: Checking backend status..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2
    Write-Host "✅ Backend is running" -ForegroundColor Green
    Write-Host "   Version: $($response.Content | ConvertFrom-Json | Select-Object -ExpandProperty version)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Backend is not running" -ForegroundColor Red
    Write-Host "   Please start the backend first:" -ForegroundColor Yellow
    Write-Host "   python backend/src/main.py" -ForegroundColor Gray
    exit 1
}

# Step 2: Ask user to restart backend
Write-Host "`n📍 Step 2: Backend restart required" -ForegroundColor Yellow
Write-Host "   The backend must be restarted to apply WebSocket broadcast fixes." -ForegroundColor Gray
Write-Host ""
$restart = Read-Host "Have you restarted the backend? (y/n)"

if ($restart -ne 'y' -and $restart -ne 'Y') {
    Write-Host "`n⚠️  Please restart the backend:" -ForegroundColor Yellow
    Write-Host "   1. Go to the backend terminal" -ForegroundColor Gray
    Write-Host "   2. Press Ctrl+C to stop" -ForegroundColor Gray
    Write-Host "   3. Run: python backend/src/main.py" -ForegroundColor Gray
    Write-Host "   4. Run this script again" -ForegroundColor Gray
    exit 0
}

# Step 3: Run comprehensive tests
Write-Host "`n📍 Step 3: Running comprehensive tests..." -ForegroundColor Yellow
Write-Host ""
python scripts/test_realtime_system.py

# Step 4: Test analytics endpoint
Write-Host "`n📍 Step 4: Testing analytics endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/analytics/network-insights" -TimeoutSec 10
    Write-Host "✅ Analytics endpoint working" -ForegroundColor Green
    Write-Host "   Devices: $($response.network_summary.total_devices) total, $($response.network_summary.online_devices) online" -ForegroundColor Gray
    Write-Host "   Insights: $($response.insights.Count) insights generated" -ForegroundColor Gray
} catch {
    Write-Host "❌ Analytics endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 5: Next steps
Write-Host "`n📍 Step 5: Manual Testing" -ForegroundColor Yellow
Write-Host "   1. Open browser to http://localhost:5173" -ForegroundColor Gray
Write-Host "   2. Navigate to Dashboard page" -ForegroundColor Gray
Write-Host "   3. Watch for live chart updates (every 30 seconds)" -ForegroundColor Gray
Write-Host "   4. Open DevTools Console to see WebSocket messages" -ForegroundColor Gray
Write-Host "   5. Click Settings to verify no infinite loop" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 See docs/REALTIME_TESTING_SUMMARY.md for detailed instructions" -ForegroundColor Cyan
Write-Host ""
