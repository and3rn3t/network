# UniFi Metrics Collection - Windows Setup Script
# This script helps you set up continuous metrics collection on Windows

Write-Host ""
Write-Host "========================================"
Write-Host "UniFi Metrics Collection Setup"
Write-Host "========================================"
Write-Host ""

Write-Host "This script will help you set up automated metrics collection."
Write-Host ""

Write-Host "Collection Options:"
Write-Host ""

Write-Host "1. Manual Collection (recommended for testing)"
Write-Host "   Run whenever you want to collect metrics"
Write-Host "   Command: python collect_real_metrics.py"
Write-Host ""

Write-Host "2. Background Service (run continuously)"
Write-Host "   Collects metrics every 5 minutes in a terminal"
Write-Host "   Command: python start_metrics_collection.py"
Write-Host ""

Write-Host "3. Windows Task Scheduler (recommended for production)"
Write-Host "   Runs automatically in background, starts with Windows"
Write-Host "   This option sets up a scheduled task"
Write-Host ""

$choice = Read-Host "Enter your choice (1-3)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Starting Manual Collection..."
        Write-Host "This will collect current metrics + 24 hours of historical data."
        Write-Host ""

        $confirm = Read-Host "Continue? (y/n)"
        if ($confirm -eq "y" -or $confirm -eq "Y") {
            # Create input file with choice 3
            "3" | Out-File -FilePath "temp_choice.txt" -Encoding ASCII

            Write-Host ""
            Write-Host "Running collector..."
            Get-Content temp_choice.txt | python collect_real_metrics.py

            Remove-Item temp_choice.txt -ErrorAction SilentlyContinue

            Write-Host ""
            Write-Host "Collection complete!"
            Write-Host "View your metrics at: http://localhost:3000"
            Write-Host ""
        }
    }

    "2" {
        Write-Host ""
        Write-Host "Starting Background Service..."
        Write-Host "This will run continuously and collect metrics every 5 minutes."
        Write-Host "Press Ctrl+C to stop."
        Write-Host ""

        Start-Sleep -Seconds 2
        python start_metrics_collection.py
    }

    "3" {
        Write-Host ""
        Write-Host "Setting up Windows Task Scheduler..."

        # Get current directory
        $scriptPath = Get-Location
        $pythonPath = (Get-Command python).Source
        $collectorScript = Join-Path $scriptPath "collect_real_metrics.py"

        Write-Host ""
        Write-Host "Configuration:"
        Write-Host "   Python: $pythonPath"
        Write-Host "   Script: $collectorScript"
        Write-Host "   Interval: Every 5 minutes"
        Write-Host "   Start time: Now"
        Write-Host ""

        $confirm = Read-Host "Create scheduled task? (y/n)"

        if ($confirm -eq "y" -or $confirm -eq "Y") {
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

                Write-Host ""
                Write-Host "Scheduled task created successfully!"
                Write-Host ""
                Write-Host "Task Details:"
                Write-Host "   Name: $taskName"
                Write-Host "   Interval: Every 5 minutes"
                Write-Host "   Status: Running"
                Write-Host ""
                Write-Host "Task Management:"
                Write-Host "   View task: Task Scheduler -> $taskName"
                Write-Host "   Stop task: Disable in Task Scheduler"
                Write-Host "   Delete task: Right-click -> Delete in Task Scheduler"
                Write-Host ""
                Write-Host "The task is now running and will continue after reboot."
                Write-Host "Check metrics in your dashboard: http://localhost:3000"
                Write-Host ""

            }
            catch {
                Write-Host ""
                Write-Host "Error creating scheduled task:"
                Write-Host "   $($_.Exception.Message)"
                Write-Host ""
                Write-Host "Please run this script as Administrator to create scheduled tasks."
                Write-Host ""
            }
        }
        else {
            Write-Host ""
            Write-Host "Setup cancelled."
            Write-Host ""
        }
    }

    default {
        Write-Host ""
        Write-Host "Invalid choice. Please run the script again."
        Write-Host ""
    }
}

Write-Host "========================================`n" -ForegroundColor Cyan
