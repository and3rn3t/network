# Create Windows Task Scheduler task for UniFi Metrics Collection
# Run this as Administrator

Write-Host ""
Write-Host "Creating Windows Task Scheduler task..."
Write-Host ""

# Get paths
$scriptPath = Get-Location
$pythonPath = (Get-Command python).Source
$collectorScript = Join-Path $scriptPath "collect_real_metrics.py"

Write-Host "Configuration:"
Write-Host "  Python: $pythonPath"
Write-Host "  Script: $collectorScript"
Write-Host "  Interval: Every 5 minutes"
Write-Host ""

try {
    # Create action to run Python script
    $action = New-ScheduledTaskAction -Execute $pythonPath -Argument "`"$collectorScript`" --auto" -WorkingDirectory $scriptPath

    # Create trigger for every 5 minutes
    $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5)

    # Create settings
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

    # Register the task
    $taskName = "UniFi Metrics Collection"

    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Collects metrics from UniFi Network devices every 5 minutes" -Force | Out-Null

    Write-Host "Task created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Details:"
    Write-Host "  Name: $taskName"
    Write-Host "  Interval: Every 5 minutes"
    Write-Host "  Status: Running"
    Write-Host ""
    Write-Host "Management:"
    Write-Host "  View: Open Task Scheduler and look for '$taskName'"
    Write-Host "  Stop: Disable the task in Task Scheduler"
    Write-Host "  Delete: Right-click and delete in Task Scheduler"
    Write-Host ""
    Write-Host "Or use PowerShell commands:"
    Write-Host "  Get-ScheduledTask -TaskName '$taskName'"
    Write-Host "  Disable-ScheduledTask -TaskName '$taskName'"
    Write-Host "  Unregister-ScheduledTask -TaskName '$taskName'"
    Write-Host ""
}
catch {
    Write-Host "Error creating task:" -ForegroundColor Red
    Write-Host "  $($_.Exception.Message)"
    Write-Host ""
    Write-Host "Note: You may need to run this script as Administrator" -ForegroundColor Yellow
    Write-Host ""
}
