#!/usr/bin/env pwsh
# PowerShell wrapper for the alert CLI tool

$env:PYTHONPATH = "C:\git\network\src"
python -m alerts.cli @args
