# Quick Backend Restart and Test Script

Write-Host "`n🔧 UniFi Network Dashboard - Backend Restart Helper`n" -ForegroundColor Cyan

Write-Host "⚠️  CRITICAL FIXES APPLIED:" -ForegroundColor Yellow
Write-Host "   ✅ Fixed database row access (index → dictionary keys)" -ForegroundColor Green
Write-Host "   ✅ Fixed analytics endpoint queries" -ForegroundColor Green  
Write-Host "   ✅ Fixed WebSocket broadcast queries" -ForegroundColor Green
Write-Host "   ✅ Added alert table error handling" -ForegroundColor Green
Write-Host ""

Write-Host "📋 BACKEND MUST BE RESTARTED for fixes to take effect`n" -ForegroundColor Yellow

# Check if backend is running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✅ Backend is currently running" -ForegroundColor Green
    Write-Host ""
    Write-Host "Please follow these steps:" -ForegroundColor Cyan
    Write-Host "  1. Go to the backend terminal window" -ForegroundColor White
    Write-Host "  2. Press Ctrl+C to stop the server" -ForegroundColor White
    Write-Host "  3. Run: python backend/src/main.py" -ForegroundColor White
    Write-Host "  4. Come back here and press Enter when ready" -ForegroundColor White
    Write-Host ""
    
    $null = Read-Host "Press Enter after restarting backend"
    
} catch {
    Write-Host "❌ Backend is not running" -ForegroundColor Red
    Write-Host "   Please start it first: python backend/src/main.py" -ForegroundColor Yellow
    exit 1
}

# Test analytics endpoint
Write-Host "`n🧪 Testing Analytics Endpoint..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/analytics/network-insights" -TimeoutSec 10
    Write-Host "✅ Analytics endpoint is now working!" -ForegroundColor Green
    Write-Host "   Network Summary:" -ForegroundColor Gray
    Write-Host "     - Total Devices: $($response.network_summary.total_devices)" -ForegroundColor Gray
    Write-Host "     - Online: $($response.network_summary.online_devices)" -ForegroundColor Gray
    Write-Host "     - Insights: $($response.insights.Count)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Analytics endpoint still failing" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Make sure backend was restarted!" -ForegroundColor Yellow
}

# Run comprehensive tests
Write-Host "`n🧪 Running Comprehensive Real-Time Tests...`n" -ForegroundColor Cyan
python scripts/test_realtime_system.py

Write-Host "`n📚 For detailed information, see:" -ForegroundColor Cyan
Write-Host "   - docs/DATABASE_ACCESS_FIX.md" -ForegroundColor Gray
Write-Host "   - docs/REALTIME_TESTING_SUMMARY.md" -ForegroundColor Gray
Write-Host ""
