# EyeCore MVP - School Deployment Guide

## 🏫 Deployment for Educational Institutions

This guide shows how to deploy EyeCore MVP across school computers.

---

## Before You Deploy

### Legal & Compliance

⚠️ **CRITICAL**: Before deploying in your school:

1. **Parental Consent**: Obtain written consent from parents/guardians
2. **Policy Approval**: Get approval from school board/administration
3. **Privacy Policy**: Update your school's privacy policy to include EyeCore monitoring
4. **FERPA Compliance**: Ensure compliance with Family Educational Rights and Privacy Act
5. **Transparency**: Inform students and parents clearly about what is being monitored

### Network Requirements

- Windows 10+ machines with internet access
- Admin access to install software
- Port 3000 (or configured port) available
- ~100 MB disk space per machine

---

## Option 1: Single Computer Setup

### Step 1: Prepare Binary

```powershell
# On developer machine
cd eyecore_mvp
cargo build --release

# Copy the binary
Copy-Item "target\release\eyecore_mvp.exe" -Destination "C:\School\EyeCore\"
```

### Step 2: Create Startup Script

Create `C:\School\EyeCore\start-eyecore.bat`:

```batch
@echo off
REM EyeCore Startup Script
REM Run as Administrator

set RUST_LOG=info

echo Starting EyeCore MVP...
cd C:\School\EyeCore
eyecore_mvp.exe

pause
```

### Step 3: Test Locally

```powershell
# Run as Administrator
C:\School\EyeCore\start-eyecore.bat
```

Check: `http://127.0.0.1:3000/health`

---

## Option 2: Multi-Computer Deployment (Group Policy)

### Step 1: Create Shared Network Folder

On server:
```powershell
# Create share
mkdir \\SERVER\EyeCore
icacls "\\SERVER\EyeCore" /grant "DOMAIN\Computers:RX"
```

Copy binary: `eyecore_mvp.exe` → `\\SERVER\EyeCore\`

### Step 2: Group Policy Setup

On Domain Controller:

1. Open **Group Policy Manager**
2. Create new policy: "Deploy EyeCore"
3. Link to: **Computers > School Labs OU**
4. Configure:
   - **User Configuration** > **Policies** > **Windows Settings** > **Scripts**
   - Add **Startup** script: `\\SERVER\EyeCore\deploy.ps1`

### Step 3: Create Deployment Script

`\\SERVER\EyeCore\deploy.ps1`:

```powershell
# EyeCore Deployment Script

# Create directory
if (-not (Test-Path "C:\Program Files\EyeCore")) {
    New-Item -ItemType Directory -Path "C:\Program Files\EyeCore" -Force
}

# Copy binary
Copy-Item "\\SERVER\EyeCore\eyecore_mvp.exe" -Destination "C:\Program Files\EyeCore\" -Force

# Create scheduled task (runs at startup)
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -RunLevel "Highest"
$task = New-ScheduledTaskAction -Execute "C:\Program Files\EyeCore\eyecore_mvp.exe"
$taskSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask `
    -TaskName "EyeCore Monitoring" `
    -Trigger $trigger `
    -Principal $principal `
    -Action $task `
    -Settings $taskSettings `
    -Force
```

### Step 4: Verify Deployment

On any school computer:

```powershell
# Check if running
Get-ScheduledTask -TaskName "EyeCore Monitoring"

# Check if process running
Get-Process eyecore_mvp

# Test API
curl http://127.0.0.1:3000/health
```

---

## Option 3: Centralized Data Collection

For collecting data from multiple computers to a dashboard:

### Setup Central Server

```powershell
# On admin computer
# Install & run EyeCore with data aggregation

# Python/Node script to collect data from all machines:
$computers = @("LAB-01", "LAB-02", "LAB-03", "LAB-04")

foreach ($computer in $computers) {
    $data = Invoke-RestMethod -Uri "http://$computer:3000/data/latest"
    
    # Log data
    $data | ConvertTo-Json | Add-Content "C:\Logs\eyecore-$computer.json"
}
```

---

## Configuration for Schools

### Example: Monitoring with Student Focus Tracking

Edit `src/main.rs` before deployment:

```rust
// Collect every 10 seconds instead of 5
tokio::time::sleep(tokio::time::Duration::from_secs(10)).await;

// Increase history to 1 week
max_history: 50400,  // 7 days * 24 hours * 60 min * 60 sec / 10 sec
```

### Example: Reduced Resource Usage

Edit `src/data_collector.rs`:

```rust
// Reduce history buffer for slower computers
max_history: 500,  // ~42 minutes instead of 83
```

---

## Teacher Dashboard (Optional)

Create a simple web dashboard to view student activity:

### Node.js Dashboard Example

```javascript
// dashboard.js
const express = require('express');
const fetch = require('node-fetch');
const app = express();

// List of lab computers
const COMPUTERS = [
    'lab-01', 'lab-02', 'lab-03', 'lab-04',
    'lab-05', 'lab-06', 'lab-07', 'lab-08'
];

app.get('/dashboard', async (req, res) => {
    let data = [];
    
    for (const computer of COMPUTERS) {
        try {
            const response = await fetch(`http://${computer}:3000/data/latest`);
            const metrics = await response.json();
            data.push({
                computer,
                focus: metrics.focus_metrics.focus_level,
                cpu: metrics.system_metrics.cpu_usage,
                memory: metrics.system_metrics.memory_usage,
                active_app: metrics.process_data.active_window_title
            });
        } catch (error) {
            console.log(`Could not reach ${computer}`);
        }
    }
    
    res.json(data);
});

app.listen(8080, () => console.log('Dashboard running on :8080'));
```

---

## Monitoring & Alerts

### Check Health of All Machines

```powershell
$computers = @("LAB-01", "LAB-02", "LAB-03")

foreach ($computer in $computers) {
    try {
        $health = Invoke-RestMethod -Uri "http://$computer:3000/health" -ErrorAction Stop
        Write-Host "$computer: ONLINE" -ForegroundColor Green
    } catch {
        Write-Host "$computer: OFFLINE" -ForegroundColor Red
    }
}
```

### Alert on High CPU Usage

```powershell
$computer = "LAB-01"
$stats = Invoke-RestMethod -Uri "http://$computer:3000/data/stats"

if ($stats.avg_cpu_usage -gt 80) {
    Write-Host "⚠️ $computer high CPU!" -ForegroundColor Yellow
    # Send email alert, etc.
}
```

---

## Troubleshooting Deployment

### Machines Not Connecting

**Symptom:** `http://LAB-01:3000/health` fails

**Solutions:**
1. Verify machine is on network
2. Check firewall allows port 3000
3. Restart EyeCore service
4. Verify binary copied correctly

### High Latency

**Symptom:** Slow API responses

**Solutions:**
1. Reduce collection frequency (see Configuration section)
2. Reduce history buffer size
3. Check network bandwidth
4. Monitor CPU/disk on machines

### Data Not Persisting

**Symptom:** Data resets after restart

**Note:** MVP version stores data in memory only. To persist:

```rust
// Add to data_collector.rs
fn save_to_disk(&self) {
    // Serialize data_history to JSON file
    // Restore on startup
}
```

---

## Security During Deployment

### Network Security

- **Firewall**: Restrict port 3000 to school network only
- **VPN**: Only allow teacher machines to query data
- **Encryption**: Add TLS (see DOCUMENTATION.md)

### Data Security

- **Backups**: Regularly backup collected data
- **Access Control**: Limit who can query the API
- **Audit Logging**: Track who accessed what data
- **Retention**: Set policy for how long to keep data

### Compliance

- **FERPA**: Don't share student data externally
- **COPPA**: Extra protections for students under 13
- **State Laws**: Check your state's privacy laws

---

## Uninstall

If you need to remove EyeCore:

```powershell
# Remove scheduled task
Unregister-ScheduledTask -TaskName "EyeCore Monitoring" -Confirm:$false

# Delete files
Remove-Item "C:\Program Files\EyeCore" -Recurse

# Verify removed
Get-Process eyecore_mvp -ErrorAction SilentlyContinue
```

---

## Support

For technical issues:
1. Check **DOCUMENTATION.md** troubleshooting section
2. Review **QUICKSTART.md** for common setup issues
3. Check Windows Event Viewer for errors
4. Review EyeCore logs: `$env:RUST_LOG="debug"`

---

## Next Steps

After deployment:

1. **Monitor**: Check `/data/stats` endpoint regularly
2. **Collect**: Build analysis pipeline for collected data
3. **Act**: Use insights to improve student experience
4. **Report**: Share anonymized findings with stakeholders

---

**Important:** This system collects significant data. Use responsibly and ethically.

Last Updated: October 25, 2025
