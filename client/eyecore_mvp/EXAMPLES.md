# EyeCore MVP - Usage Examples

## PowerShell Examples

### Basic Health Check

```powershell
$response = Invoke-RestMethod -Uri "http://127.0.0.1:3000/health"
$response
```

**Output:**
```json
{
  "status": "healthy"
}
```

---

### Get Latest Data

```powershell
$data = Invoke-RestMethod -Uri "http://127.0.0.1:3000/data/latest"
$data | ConvertTo-Json
```

**Display Just Focus Level:**
```powershell
$data.focus_metrics.focus_level
```

---

### Monitor CPU Usage

```powershell
while ($true) {
    $stats = Invoke-RestMethod -Uri "http://127.0.0.1:3000/data/stats"
    Write-Host "CPU: $($stats.avg_cpu_usage)% | Memory: $($stats.avg_memory_usage)%"
    Start-Sleep -Seconds 5
}
```

---

### Export Data to CSV

```powershell
$history = Invoke-RestMethod -Uri "http://127.0.0.1:3000/data/history?limit=1000"

$csv = $history | ForEach-Object {
    [PSCustomObject]@{
        Timestamp = $_.timestamp
        CPU = $_.system_metrics.cpu_usage
        Memory = $_.system_metrics.memory_usage
        FocusLevel = $_.focus_metrics.focus_level
        ActiveApp = $_.process_data.active_window_title
    }
}

$csv | Export-Csv -Path "eyecore_data.csv" -NoTypeInformation
Write-Host "Exported to eyecore_data.csv"
```

---

### Monitor Multiple Computers

```powershell
$computers = @("LAB-01", "LAB-02", "LAB-03", "LAB-04", "LAB-05")

foreach ($computer in $computers) {
    try {
        $data = Invoke-RestMethod -Uri "http://$computer:3000/data/latest" -ErrorAction Stop
        Write-Host "$computer: Focus=$($data.focus_metrics.focus_level) | App=$($data.process_data.active_window_title)"
    } catch {
        Write-Host "$computer: OFFLINE" -ForegroundColor Red
    }
}
```

---

### Create Alert for High CPU

```powershell
$threshold = 80

while ($true) {
    $stats = Invoke-RestMethod -Uri "http://127.0.0.1:3000/data/stats"
    
    if ($stats.avg_cpu_usage -gt $threshold) {
        Write-Host "⚠️  HIGH CPU USAGE: $($stats.avg_cpu_usage)%" -ForegroundColor Yellow
        
        # Optional: Send email alert
        # Send-MailMessage -To "admin@school.edu" -Subject "EyeCore Alert" -Body "High CPU usage detected"
    }
    
    Start-Sleep -Seconds 10
}
```

---

## Python Examples

### Real-time Dashboard

```python
import requests
import json
from time import sleep
from datetime import datetime

API_URL = "http://127.0.0.1:3000"

def get_latest():
    response = requests.get(f"{API_URL}/data/latest")
    return response.json()

def display_dashboard():
    while True:
        data = get_latest()
        
        print("\033[2J")  # Clear screen
        print(f"EyeCore Dashboard - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        system = data['system_metrics']
        focus = data['focus_metrics']
        process = data['process_data']
        
        print(f"CPU Usage:        {system['cpu_usage']:.1f}%")
        print(f"Memory Usage:     {system['memory_usage']:.1f}%")
        print(f"Disk Usage:       {system['disk_usage']:.1f}%")
        print(f"Focus Level:      {focus['focus_level']:.2f}/1.0")
        print(f"Active App:       {process['active_window_title']}")
        print(f"Running Processes: {process['process_count']}")
        
        sleep(5)

if __name__ == "__main__":
    display_dashboard()
```

### Export to Database

```python
import requests
import sqlite3
from datetime import datetime

# Create database
conn = sqlite3.connect('eyecore.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS metrics (
        id INTEGER PRIMARY KEY,
        timestamp TEXT,
        cpu REAL,
        memory REAL,
        focus REAL,
        active_app TEXT
    )
''')
conn.commit()

# Collect data
def collect_data():
    response = requests.get("http://127.0.0.1:3000/data/latest")
    data = response.json()
    
    cursor.execute('''
        INSERT INTO metrics (timestamp, cpu, memory, focus, active_app)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        data['timestamp'],
        data['system_metrics']['cpu_usage'],
        data['system_metrics']['memory_usage'],
        data['focus_metrics']['focus_level'],
        data['process_data']['active_window_title']
    ))
    
    conn.commit()

# Run collection
while True:
    collect_data()
    time.sleep(5)
```

### Analyze Focus Patterns

```python
import requests
import numpy as np
from datetime import datetime, timedelta

API_URL = "http://127.0.0.1:3000"

def analyze_focus():
    # Get last 100 data points
    response = requests.get(f"{API_URL}/data/history?limit=100")
    history = response.json()
    
    focus_levels = [d['focus_metrics']['focus_level'] for d in history]
    
    print(f"Average Focus: {np.mean(focus_levels):.2f}")
    print(f"Max Focus: {np.max(focus_levels):.2f}")
    print(f"Min Focus: {np.min(focus_levels):.2f}")
    print(f"Std Dev: {np.std(focus_levels):.2f}")
    
    # Detect low focus periods
    low_focus = [f for f in focus_levels if f < 0.3]
    print(f"Low Focus Periods: {len(low_focus)}")

analyze_focus()
```

---

## JavaScript/Node.js Examples

### Express Dashboard Server

```javascript
const express = require('express');
const fetch = require('node-fetch');
const app = express();

const EYE_CORE_URL = 'http://127.0.0.1:3000';

// API endpoint
app.get('/api/stats', async (req, res) => {
    try {
        const response = await fetch(`${EYE_CORE_URL}/data/stats`);
        const stats = await response.json();
        res.json(stats);
    } catch (error) {
        res.status(500).json({ error: 'Failed to fetch data' });
    }
});

// Dashboard endpoint
app.get('/dashboard', async (req, res) => {
    try {
        const latest = await fetch(`${EYE_CORE_URL}/data/latest`).then(r => r.json());
        const stats = await fetch(`${EYE_CORE_URL}/data/stats`).then(r => r.json());
        
        const html = `
            <!DOCTYPE html>
            <html>
            <head>
                <title>EyeCore Dashboard</title>
                <style>
                    body { font-family: Arial; margin: 20px; }
                    .metric { 
                        display: inline-block; 
                        margin: 10px;
                        padding: 10px;
                        background: #f0f0f0;
                        border-radius: 5px;
                    }
                </style>
            </head>
            <body>
                <h1>EyeCore Dashboard</h1>
                <div class="metric">
                    <strong>CPU:</strong> ${latest.system_metrics.cpu_usage.toFixed(1)}%
                </div>
                <div class="metric">
                    <strong>Memory:</strong> ${latest.system_metrics.memory_usage.toFixed(1)}%
                </div>
                <div class="metric">
                    <strong>Focus:</strong> ${latest.focus_metrics.focus_level.toFixed(2)}/1.0
                </div>
                <div class="metric">
                    <strong>App:</strong> ${latest.process_data.active_window_title}
                </div>
                <h2>Session Stats</h2>
                <p>Duration: ${(stats.session_duration / 60).toFixed(1)} minutes</p>
                <p>Data Points: ${stats.data_points_collected}</p>
                <p>Avg Focus: ${stats.avg_focus_level.toFixed(2)}</p>
            </body>
            </html>
        `;
        res.send(html);
    } catch (error) {
        res.status(500).send('Error loading dashboard');
    }
});

app.listen(8080, () => console.log('Dashboard on :8080'));
```

### Real-time Chart with Chart.js

```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <style>
        canvas { max-width: 800px; }
    </style>
</head>
<body>
    <canvas id="focusChart"></canvas>
    
    <script>
        const ctx = document.getElementById('focusChart').getContext('2d');
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Focus Level',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: { min: 0, max: 1.0 }
                }
            }
        });

        async function updateChart() {
            const response = await fetch('/api/stats');
            const data = await response.json();
            
            // Add new data point
            chart.data.labels.push(new Date().toLocaleTimeString());
            chart.data.datasets[0].data.push(data.avg_focus_level);
            
            // Keep last 60 points
            if (chart.data.labels.length > 60) {
                chart.data.labels.shift();
                chart.data.datasets[0].data.shift();
            }
            
            chart.update();
        }

        // Update every 5 seconds
        setInterval(updateChart, 5000);
        updateChart(); // Initial call
    </script>
</body>
</html>
```

---

## Batch Script Examples

### Windows Scheduled Task Setup

```batch
@echo off
REM eyecore-collector.bat
REM Run this script to collect EyeCore data

setlocal enabledelayedexpansion

set OUTPUT_FILE=C:\EyeCore\data\output.txt
set API_URL=http://127.0.0.1:3000

if not exist C:\EyeCore\data mkdir C:\EyeCore\data

REM Get current timestamp
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)

REM Fetch data using PowerShell
powershell -Command ^
  "$data = Invoke-RestMethod -Uri '%API_URL%/data/latest'; " ^
  "$data | ConvertTo-Json | Add-Content '%OUTPUT_FILE%.%mydate%_%mytime%.json'"

echo Data collected: %mydate% %mytime%
```

---

## Monitoring Alerts

### Alert When Focus Drops

```powershell
# alert.ps1
$EMAIL_TO = "teacher@school.edu"
$EMAIL_FROM = "eyecore@school.edu"
$THRESHOLD = 0.3

while ($true) {
    $data = Invoke-RestMethod -Uri "http://127.0.0.1:3000/data/latest"
    $focus = $data.focus_metrics.focus_level
    
    if ($focus -lt $THRESHOLD) {
        $subject = "EyeCore Alert: Low Focus Detected"
        $body = "Focus level dropped to $focus`n`nActive App: $($data.process_data.active_window_title)"
        
        Send-MailMessage `
            -To $EMAIL_TO `
            -From $EMAIL_FROM `
            -Subject $subject `
            -Body $body `
            -SmtpServer "smtp.school.edu"
    }
    
    Start-Sleep -Seconds 30
}
```

---

## Cron Job (Linux/macOS)

```bash
#!/bin/bash
# collect_eyecore.sh
# Run via: crontab -e
# Add: */5 * * * * /path/to/collect_eyecore.sh

API_URL="http://127.0.0.1:3000"
LOG_DIR="/var/log/eyecore"
mkdir -p $LOG_DIR

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
curl -s "$API_URL/data/latest" | jq . > "$LOG_DIR/data_$TIMESTAMP.json"
```

---

## Utility Scripts

### Bulk Export Historical Data

```powershell
# Export all available history
$limit = 1000
$data = Invoke-RestMethod -Uri "http://127.0.0.1:3000/data/history?limit=$limit"

$data | ConvertTo-Json -Depth 10 | Out-File -FilePath "eyecore_export_$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss').json"

Write-Host "Exported $($data.Count) records"
```

### Calculate Daily Statistics

```powershell
# Aggregate data for a report
$history = Invoke-RestMethod -Uri "http://127.0.0.1:3000/data/history?limit=1000"

$report = [PSCustomObject]@{
    TotalRecords = $history.Count
    AvgCPU = ($history | Measure-Object -Property {$_.system_metrics.cpu_usage} -Average).Average
    AvgMemory = ($history | Measure-Object -Property {$_.system_metrics.memory_usage} -Average).Average
    AvgFocus = ($history | Measure-Object -Property {$_.focus_metrics.focus_level} -Average).Average
    MaxCPU = ($history | Measure-Object -Property {$_.system_metrics.cpu_usage} -Maximum).Maximum
}

$report | Format-Table
$report | ConvertTo-Json | Out-File "daily_report.json"
```

---

## Testing & Validation

### Health Check Script

```powershell
# health-check.ps1
$api_url = "http://127.0.0.1:3000"

Write-Host "Testing EyeCore API..."
Write-Host "=" * 50

try {
    # Test health endpoint
    $health = Invoke-RestMethod -Uri "$api_url/health"
    Write-Host "✓ Health Check: OK" -ForegroundColor Green
} catch {
    Write-Host "✗ Health Check: FAILED" -ForegroundColor Red
}

try {
    # Test data endpoint
    $data = Invoke-RestMethod -Uri "$api_url/data/latest"
    Write-Host "✓ Data Endpoint: OK" -ForegroundColor Green
    Write-Host "  - Session ID: $($data.session_id)"
    Write-Host "  - CPU: $($data.system_metrics.cpu_usage)%"
} catch {
    Write-Host "✗ Data Endpoint: FAILED" -ForegroundColor Red
}

try {
    # Test stats endpoint
    $stats = Invoke-RestMethod -Uri "$api_url/data/stats"
    Write-Host "✓ Stats Endpoint: OK" -ForegroundColor Green
    Write-Host "  - Data Points: $($stats.data_points_collected)"
} catch {
    Write-Host "✗ Stats Endpoint: FAILED" -ForegroundColor Red
}

Write-Host "=" * 50
```

---

## Next Steps

- Adapt these examples to your specific use case
- Combine multiple scripts for comprehensive monitoring
- Build a custom dashboard matching your needs
- Share insights with your team

For more examples, see the full documentation in **DOCUMENTATION.md**
