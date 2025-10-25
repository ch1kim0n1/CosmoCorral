# EyeCore MVP Test Demo Script
# This script demonstrates the data collection from EyeCore

Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   🔍 EyeCore MVP - Test Run & Data Visualization" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Sample data based on EyeCore's collection format
$sampleData = @{
    session_id = [guid]::NewGuid().ToString()
    timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
    system_metrics = @{
        timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
        cpu_usage = [math]::Round((Get-Random -Minimum 20 -Maximum 85), 2)
        memory_usage = [math]::Round((Get-Random -Minimum 40 -Maximum 90), 2)
        disk_usage = [math]::Round((Get-Random -Minimum 50 -Maximum 80), 2)
    }
    process_data = @{
        timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
        active_process = "0x" + [guid]::NewGuid().ToString().Substring(0, 8)
        active_window_title = @("Visual Studio Code", "Google Chrome", "Microsoft Teams", "PowerShell", "Discord", "Spotify")[Get-Random -Minimum 0 -Maximum 6]
        process_count = Get-Random -Minimum 120 -Maximum 180
    }
    input_metrics = @{
        timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
        mouse_clicks = Get-Random -Minimum 0 -Maximum 10
        keyboard_events = Get-Random -Minimum 0 -Maximum 20
        idle_duration_seconds = Get-Random -Minimum 0 -Maximum 60
    }
    network_metrics = @{
        timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
        bytes_sent = Get-Random -Minimum 10000 -Maximum 1000000
        bytes_received = Get-Random -Minimum 50000 -Maximum 5000000
        active_connections = Get-Random -Minimum 5 -Maximum 50
    }
    focus_metrics = @{
        timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
        focus_level = [math]::Round((Get-Random -Minimum 0.3 -Maximum 1.0), 2)
        context_switches = Get-Random -Minimum 2 -Maximum 20
        productive_app_time = Get-Random -Minimum 60 -Maximum 600
    }
}

Write-Host "📊 COLLECTING DATA..." -ForegroundColor Yellow
Start-Sleep -Seconds 1

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "   ✓ Data Collection Complete!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""

# Display Session Info
Write-Host "📋 SESSION INFORMATION" -ForegroundColor Cyan
Write-Host "  Session ID:   $($sampleData.session_id)" -ForegroundColor White
Write-Host "  Timestamp:    $($sampleData.timestamp)" -ForegroundColor White
Write-Host ""

# Display System Metrics
Write-Host "🖥️  SYSTEM METRICS" -ForegroundColor Cyan
Write-Host "  CPU Usage:    $($sampleData.system_metrics.cpu_usage)%" -ForegroundColor $(if ($sampleData.system_metrics.cpu_usage -gt 70) { "Red" } else { "Green" })
Write-Host "  Memory Usage: $($sampleData.system_metrics.memory_usage)%" -ForegroundColor $(if ($sampleData.system_metrics.memory_usage -gt 80) { "Red" } else { "Green" })
Write-Host "  Disk Usage:   $($sampleData.system_metrics.disk_usage)%" -ForegroundColor $(if ($sampleData.system_metrics.disk_usage -gt 75) { "Yellow" } else { "Green" })
Write-Host ""

# Display Process Data
Write-Host "📱 PROCESS INFORMATION" -ForegroundColor Cyan
Write-Host "  Active Window:    $($sampleData.process_data.active_window_title)" -ForegroundColor White
Write-Host "  Active Process:   $($sampleData.process_data.active_process)" -ForegroundColor Gray
Write-Host "  Process Count:    $($sampleData.process_data.process_count)" -ForegroundColor White
Write-Host ""

# Display Input Metrics
Write-Host "⌨️  INPUT ACTIVITY" -ForegroundColor Cyan
Write-Host "  Mouse Clicks:        $($sampleData.input_metrics.mouse_clicks)" -ForegroundColor White
Write-Host "  Keyboard Events:     $($sampleData.input_metrics.keyboard_events)" -ForegroundColor White
Write-Host "  Idle Time (seconds): $($sampleData.input_metrics.idle_duration_seconds)" -ForegroundColor $(if ($sampleData.input_metrics.idle_duration_seconds -gt 30) { "Yellow" } else { "Green" })
Write-Host ""

# Display Network Metrics
Write-Host "🌐 NETWORK METRICS" -ForegroundColor Cyan
Write-Host "  Bytes Sent:          $($sampleData.network_metrics.bytes_sent) bytes" -ForegroundColor White
Write-Host "  Bytes Received:      $($sampleData.network_metrics.bytes_received) bytes" -ForegroundColor White
Write-Host "  Active Connections:  $($sampleData.network_metrics.active_connections)" -ForegroundColor White
Write-Host ""

# Display Focus Metrics
Write-Host "🎯 FOCUS ANALYSIS" -ForegroundColor Cyan
$focusLevel = $sampleData.focus_metrics.focus_level
$focusBar = "█" * [math]::Floor($focusLevel * 20)
$focusColor = if ($focusLevel -gt 0.7) { "Green" } elseif ($focusLevel -gt 0.4) { "Yellow" } else { "Red" }

Write-Host "  Focus Level:         $focusLevel / 1.0" -ForegroundColor White
Write-Host "  Visual:              [$focusBar]" -ForegroundColor $focusColor
Write-Host "  Context Switches:    $($sampleData.focus_metrics.context_switches)" -ForegroundColor White
Write-Host "  Productive Time:     $($sampleData.focus_metrics.productive_app_time) seconds" -ForegroundColor White
Write-Host ""

# Display JSON format
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "   📄 RAW JSON OUTPUT" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
$sampleData | ConvertTo-Json -Depth 5
Write-Host ""

# Simulate multiple collections
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "   📊 SIMULATING 5-SECOND COLLECTION CYCLE" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

for ($i = 1; $i -le 3; $i++) {
    Write-Host "Collection #$i at $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Yellow
    Write-Host "  - CPU: $([math]::Round((Get-Random -Minimum 20 -Maximum 85), 2))%" -ForegroundColor Gray
    Write-Host "  - Memory: $([math]::Round((Get-Random -Minimum 40 -Maximum 90), 2))%" -ForegroundColor Gray
    Write-Host "  - Focus: $([math]::Round((Get-Random -Minimum 0.3 -Maximum 1.0), 2))" -ForegroundColor Gray
    Write-Host ""
    if ($i -lt 3) {
        Start-Sleep -Seconds 2
    }
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "   ✓ Test Run Complete!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""
Write-Host "💡 This data represents what EyeCore collects every 5 seconds" -ForegroundColor Cyan
Write-Host "   from student computers in your school environment." -ForegroundColor Cyan
Write-Host ""
