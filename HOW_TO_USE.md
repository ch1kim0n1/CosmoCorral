# Space Cowboy: How to Use the Software

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial Setup (One Time)](#initial-setup-one-time)
3. [Running the System](#running-the-system)
4. [Using the System](#using-the-system)
5. [Testing Examples](#testing-examples)
6. [Monitoring & Debugging](#monitoring--debugging)
7. [Common Scenarios](#common-scenarios)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- **Python 3.9+** - Download from [python.org](https://www.python.org)
- **Node.js 16+** - Download from [nodejs.org](https://nodejs.org)
- **Rust 1.70+** - Download from [rustup.rs](https://rustup.rs)
- **Git** - For version control (optional)

### Accounts
- **Gemini API Key** (free) - Get from [https://aistudio.google.com/app/apikeys](https://aistudio.google.com/app/apikeys)
  - Click "Create API Key"
  - Copy the key (you'll need it in the next step)

### System Requirements
- **OS**: Windows 10+, macOS, or Linux
- **Disk Space**: 2+ GB
- **RAM**: 4+ GB
- **Network**: Internet connection

---

## Initial Setup (One Time)

### Step 1: Get Your Gemini API Key

1. Go to https://aistudio.google.com/app/apikeys
2. Click **"Create API Key"** button
3. Copy the key (it looks like: `AIzaSyD...`)
4. Keep this safe - you'll use it every time you run the system

### Step 2: Clone/Download the Project

```powershell
# Navigate to project directory
cd C:\Users\chiki\OneDrive\Desktop\GitHib\ Repo\rowdyhack-25
```

### Step 3: Create Environment File

```powershell
# Copy the example environment file
Copy-Item .env.example .env

# Edit it with your API key
notepad .env
```

**In the notepad window, find this line:**
```
GEMINI_API_KEY=your-gemini-api-key-here
```

**Replace it with:**
```
GEMINI_API_KEY=AIzaSyD... (paste your actual key)
```

**Save the file** (Ctrl+S, then close)

### Step 4: Install Dependencies

Run these commands **once**:

```powershell
# Install Python dependencies
cd server
pip install websockets peewee google-generativeai

# Initialize database
python db_init.py
# Output: "Database initialized successfully."

cd ..\dashboard
npm install
# Output: "added X packages in Y seconds"
```

✅ **Setup complete!** Now you're ready to use it.

---

## Running the System

The system has **4 components** that run simultaneously. Open **4 separate PowerShell/Terminal windows** and start each one:

### Terminal 1: Start the Server (Core Processing)

```powershell
cd C:\Users\chiki\OneDrive\Desktop\GitHib\ Repo\rowdyhack-25\server
$env:GEMINI_API_KEY="AIzaSyD..." # Or it reads from .env
python main.py
```

**Expected output:**
```
WebSocket server on ws://localhost:8765
```

**This window must stay open** while you're using the system.

---

### Terminal 2: Start the Student Client

```powershell
cd C:\Users\chiki\OneDrive\Desktop\GitHib\ Repo\rowdyhack-25\client\eyecore_mvp
cargo run --release
```

**Expected output:**
```
🔍 EyeCore MVP Starting...
✓ Data collection #1 complete
🚀 EyeCore API running on http://127.0.0.1:3000
```

**This window must stay open** - it collects monitoring data.

---

### Terminal 3: Start the Dashboard (Optional)

```powershell
cd C:\Users\chiki\OneDrive\Desktop\GitHib\ Repo\rowdyhack-25\dashboard
npm run dev
```

**Expected output:**
```
▲ Next.js 16.0.0
  - Local: http://localhost:3000
```

Then open **http://localhost:3000** in your browser to see the dashboard.

---

### Terminal 4: Send Test Data

```powershell
cd C:\Users\chiki\OneDrive\Desktop\GitHib\ Repo\rowdyhack-25
python test_system.py
```

(We'll create this script in the next section)

---

## Using the System

### Workflow: Monitor a Student

#### Step 1: Create a Device (Register Student's Computer)

```powershell
# Send request to server
$headers = @{"Content-Type" = "application/json"}
$body = @{
    method = "CreateDevice"
    data = @{
        name = "Student-01-Laptop"
        description = "John Doe - Room 101"
    }
} | ConvertTo-Json

# Connect to server and get response
# (Use Python script below)
```

**Better way - use Python script:**

Create file `C:\Users\chiki\OneDrive\Desktop\GitHib\ Repo\rowdyhack-25\create_device.py`:

```python
import asyncio
import json
import websockets

async def create_device():
    async with websockets.connect('ws://localhost:8765') as ws:
        # Request device creation
        await ws.send(json.dumps({
            "method": "CreateDevice",
            "data": {
                "name": "Student-01-Laptop",
                "description": "John Doe - Exam Room 101"
            }
        }))
        
        # Receive response
        response = json.loads(await ws.recv())
        print("✅ Device Created!")
        print(f"   Device ID: {response['data']['id']}")
        print(f"   Access Code: {response['data']['access_code']}")
        print("\n📝 Share this access code with the student")
        return response['data']

asyncio.run(create_device())
```

Run it:
```powershell
python create_device.py
```

**Output:**
```
✅ Device Created!
   Device ID: 12345678-abcd-ef01-2345-6789abcdef01
   Access Code: ABC123XYZ789
```

#### Step 2: Student Authenticates

Give the student the **access code** (e.g., `ABC123XYZ789`).

The student enters it in their exam software, which sends:

```python
{
    "method": "Authenticate",
    "data": {
        "access_code": "ABC123XYZ789"
    }
}
```

**Server response:**
```python
{
    "status": "success",
    "data": {
        "token": "eyJhbGciOiJIUzI1NiIs..." # Authentication token
    }
}
```

#### Step 3: Student's Device Sends Activity Data

Every 5 seconds, the student's client sends an **ActivityPackage** containing:
- CPU/Memory usage
- Active application
- Keystroke patterns
- Network activity
- Focus score
- Voice data (if enabled)

**Server automatically:**
1. ✅ Checks for anomalies (cheap rules)
2. ✅ If clean → logs only (cost: $0)
3. ✅ If suspicious → calls Gemini API (cost: $0.0002)
4. ✅ Creates flagged report if needed
5. ✅ Broadcasts alert to professors

#### Step 4: Professor Reviews Alerts

Professors see real-time alerts in their dashboard:

```
🚨 CRITICAL ALERT
Student: John Doe
Activity: Unauthorized Resource Access (91% confidence)
Time: 2:34 PM
Why: Network spike 18x baseline while Discord open

[Review] [Request Verification] [Terminate] [False Positive]
```

---

## Testing Examples

### Example 1: Send Clean Activity (No Alert)

Create `C:\Users\chiki\OneDrive\Desktop\GitHib\ Repo\rowdyhack-25\test_clean.py`:

```python
import asyncio
import json
import websockets
from datetime import datetime

async def test_clean():
    async with websockets.connect('ws://localhost:8765') as ws:
        # Step 1: Create device
        await ws.send(json.dumps({
            "method": "CreateDevice",
            "data": {
                "name": "Test-Clean",
                "description": "Testing clean activity"
            }
        }))
        device = json.loads(await ws.recv())
        device_id = device['data']['id']
        access_code = device['data']['access_code']
        
        # Step 2: Authenticate
        await ws.send(json.dumps({
            "method": "Authenticate",
            "data": {"access_code": access_code}
        }))
        auth = json.loads(await ws.recv())
        token = auth['data']['token']
        
        # Step 3: Send clean package (all metrics normal)
        clean_package = {
            "session_id": "sess-test-001",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "device_id": device_id,
            "student_id": "john.doe@edu.com",
            "package_id": "pkg-clean-001",
            "aggregation_window": "raw",
            "system_metrics": {
                "cpu_usage": 45.0,      # Normal (< 90%)
                "memory_usage": 60.0,   # Normal (< 85%)
                "disk_io_rate": 2.0,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            },
            "process_data": {
                "active_process": "chrome.exe",
                "active_pid": 1234,
                "window_title": "Google Docs - Exam",
                "app_switches": 1,      # Normal (< 15/min)
                "running_process_count": 20,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            },
            "input_dynamics": {
                "keystroke_rate": 65.0,
                "keystroke_rhythm_variance": 0.1,  # Normal (< 0.75)
                "keystroke_errors": 0.5,
                "mouse_velocity": 150.0,
                "mouse_acceleration": 40.0,
                "mouse_idle_duration": 2.0,
                "clicks_per_minute": 10.0,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            },
            "network_activity": {
                "bytes_sent": 150000,
                "bytes_received": 850000,
                "connections_active": 3,
                "data_transfer_rate": 1.0,
                "unusual_protocols": [],
                "dns_queries": 2,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            },
            "focus_metrics": {
                "focus_score": 0.85,    # Normal (> 0.3)
                "attention_drops": 0,
                "context_switches": 1,
                "time_since_interaction": 1.5,
                "productive_app_time": 300,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            },
            "client_version": "0.1.0"
        }
        
        # Send it
        await ws.send(json.dumps({
            "method": "Package",
            "data": {
                "token": token,
                "student_id": "john.doe@edu.com",
                "data": clean_package
            }
        }))
        
        result = json.loads(await ws.recv())
        print("✅ CLEAN ACTIVITY TEST")
        print(f"Status: {result['status']}")
        print(f"Message: {result['data']['message']}")
        print("\n💰 Cost: $0 (Gemini not called)")

asyncio.run(test_clean())
```

Run it:
```powershell
python test_clean.py
```

**Expected output:**
```
✅ CLEAN ACTIVITY TEST
Status: success
Message: Package processed (clean)

💰 Cost: $0 (Gemini not called)
```

---

### Example 2: Send Suspicious Activity (Triggers Alert)

Create `C:\Users\chiki\OneDrive\Desktop\GitHib\ Repo\rowdyhack-25\test_suspicious.py`:

```python
import asyncio
import json
import websockets
from datetime import datetime

async def test_suspicious():
    async with websockets.connect('ws://localhost:8765') as ws:
        # Step 1: Create device
        await ws.send(json.dumps({
            "method": "CreateDevice",
            "data": {
                "name": "Test-Suspicious",
                "description": "Testing suspicious activity"
            }
        }))
        device = json.loads(await ws.recv())
        device_id = device['data']['id']
        access_code = device['data']['access_code']
        
        # Step 2: Authenticate
        await ws.send(json.dumps({
            "method": "Authenticate",
            "data": {"access_code": access_code}
        }))
        auth = json.loads(await ws.recv())
        token = auth['data']['token']
        
        # Step 3: Send SUSPICIOUS package (multiple anomalies)
        sus_package = {
            "session_id": "sess-test-sus-001",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "device_id": device_id,
            "student_id": "john.doe@edu.com",
            "package_id": "pkg-sus-001",
            "aggregation_window": "raw",
            "system_metrics": {
                "cpu_usage": 94.0,      # ⚠️ HIGH (> 90%)
                "memory_usage": 82.0,
                "disk_io_rate": 5.8,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            },
            "process_data": {
                "active_process": "discord.exe",  # ⚠️ UNUSUAL
                "active_pid": 8234,
                "window_title": "Discord - General",
                "app_switches": 5,      # ⚠️ ELEVATED (> 15/min)
                "running_process_count": 28,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            },
            "input_dynamics": {
                "keystroke_rate": 12.0,
                "keystroke_rhythm_variance": 0.81,  # ⚠️ ERRATIC (> 0.75)
                "keystroke_errors": 8.0,
                "mouse_velocity": 380.0,
                "mouse_acceleration": 128.0,
                "mouse_idle_duration": 28.0,
                "clicks_per_minute": 42.0,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            },
            "network_activity": {
                "bytes_sent": 8234567,    # ⚠️ SPIKE (18MB total)
                "bytes_received": 9876543,
                "connections_active": 7,
                "data_transfer_rate": 18.1,
                "unusual_protocols": ["TLS_1.3"],
                "dns_queries": 12,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            },
            "focus_metrics": {
                "focus_score": 0.08,    # ⚠️ VERY LOW (< 0.3)
                "attention_drops": 3,
                "context_switches": 5,
                "time_since_interaction": 0.1,
                "productive_app_time": 0,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            },
            "client_version": "0.1.0"
        }
        
        # Send it
        await ws.send(json.dumps({
            "method": "Package",
            "data": {
                "token": token,
                "student_id": "john.doe@edu.com",
                "data": sus_package
            }
        }))
        
        result = json.loads(await ws.recv())
        print("🚨 SUSPICIOUS ACTIVITY TEST")
        print(f"Status: {result['status']}")
        print(f"Message: {result['data']['message']}")
        if 'flag_id' in result['data']:
            print(f"Flag ID: {result['data']['flag_id']}")
        print("\n💰 Cost: ~$0.0002 (Gemini called)")
        print("\n✅ Check server logs for Gemini analysis!")

asyncio.run(test_suspicious())
```

Run it:
```powershell
python test_suspicious.py
```

**Expected output:**
```
🚨 SUSPICIOUS ACTIVITY TEST
Status: success
Message: Package processed and flagged
Flag ID: flag-a1b2c3d4-e5f6-47g8-h9i0...

💰 Cost: ~$0.0002 (Gemini called)

✅ Check server logs for Gemini analysis!
```

---

## Monitoring & Debugging

### View All Devices

```powershell
cd server
sqlite3 app.db "SELECT id, name, description, access_code FROM devices;"
```

**Output:**
```
12345678-abcd-ef01-2345-6789abcdef01|Test-Clean|Testing clean activity|ABC123XYZ789
```

### View All Packages (Raw Activity)

```powershell
sqlite3 app.db "SELECT COUNT(*) FROM reports WHERE reason='raw_activity';"
# Shows: 150
```

### View Flagged Reports Only

```powershell
sqlite3 app.db "SELECT id, student_id, timestamp, reason FROM reports WHERE reason='flagged_activity' ORDER BY timestamp DESC LIMIT 5;"
```

**Output:**
```
flag-abc123...|john.doe@edu.com|2025-10-26 15:34:10|flagged_activity
flag-def456...|jane.smith@edu.com|2025-10-26 15:32:45|flagged_activity
```

### View Full Flagged Report Details

```powershell
sqlite3 app.db ".mode json" "SELECT data FROM reports WHERE reason='flagged_activity' LIMIT 1;"
```

This shows the complete JSON with Gemini analysis, evidence, etc.

### Check Server Logs

In the server terminal (Terminal 1), you'll see real-time logs:

```
INFO:__main__:Processing package from john.doe@edu.com on device...
DEBUG:__main__:Stored raw package: report-123-abc
WARNING:__main__:FLAGGED: Student john.doe@edu.com - unauthorized_resource_access
INFO:__main__:Gemini analysis: unauthorized_resource_access (confidence: 0.91)
```

---

## Common Scenarios

### Scenario 1: Monitor a Class of 30 Students During Exam

**Setup (One-time):**
```powershell
# Terminal 1: Start server
cd server
python main.py

# Terminal 2: Start client
cd ..\client\eyecore_mvp
cargo run --release

# Terminal 3: Create 30 devices
python create_all_students.py  # (Create this script)
```

**create_all_students.py:**
```python
import asyncio
import json
import websockets

async def create_students():
    students = [
        ("John Doe", "Room 101"),
        ("Jane Smith", "Room 101"),
        ("Bob Johnson", "Room 102"),
        # ... add all 30 students
    ]
    
    async with websockets.connect('ws://localhost:8765') as ws:
        for name, room in students:
            await ws.send(json.dumps({
                "method": "CreateDevice",
                "data": {
                    "name": f"Laptop-{name.split()[0].upper()}",
                    "description": f"{name} - {room}"
                }
            }))
            response = json.loads(await ws.recv())
            print(f"✅ {name}: {response['data']['access_code']}")

asyncio.run(create_students())
```

**During exam:**
- Students authenticate with their access codes
- Server continuously monitors all 30 students
- Any suspicious activity triggers real-time alerts
- Professor sees alerts in dashboard

---

### Scenario 2: Test False Positive Handling

Sometimes legitimate activity looks suspicious. Test the system:

```powershell
# Send suspicious package
python test_suspicious.py

# Check dashboard - professor sees alert

# Professor marks as false positive:
# (This would be in dashboard UI)
# Message: "Student was downloading large file for project"

# System learns from this feedback
```

---

### Scenario 3: Check Daily Statistics

```powershell
cd server

# Total packages today
sqlite3 app.db "SELECT COUNT(*) FROM reports WHERE DATE(timestamp) = DATE('now');"

# Breakdown by type
sqlite3 app.db "SELECT reason, COUNT(*) FROM reports WHERE DATE(timestamp) = DATE('now') GROUP BY reason;"

# Students flagged
sqlite3 app.db "SELECT DISTINCT student_id, COUNT(*) as flags FROM reports WHERE reason='flagged_activity' GROUP BY student_id ORDER BY flags DESC;"

# Cost estimate (if 1% flagged)
# Total packages × 0.01 × $0.0002 = total cost
```

---

## Troubleshooting

### Problem: "GEMINI_API_KEY not set"

**Solution:**
```powershell
# Option 1: Set environment variable
$env:GEMINI_API_KEY="AIzaSyD..."
python main.py

# Option 2: Edit .env file
notepad .env
# Add: GEMINI_API_KEY=AIzaSyD...
```

### Problem: "Port 8765 already in use"

**Solution:**
```powershell
# Find process using port
Get-NetTCPConnection -LocalPort 8765 -ErrorAction SilentlyContinue | Stop-Process -Force

# Or change port in server/main.py line 95
# From: async with websockets.serve(handler, "localhost", 8765)
# To:   async with websockets.serve(handler, "localhost", 8766)
```

### Problem: "Database locked"

**Solution:**
```powershell
cd server
# Delete and reinitialize
rm app.db
python db_init.py

# Or use PostgreSQL for production
# (See SETUP.md for details)
```

### Problem: "ConnectionRefusedError: [WinError 10061]"

This means the server isn't running.

**Solution:**
```powershell
# Make sure Terminal 1 is running:
cd C:\Users\chiki\OneDrive\Desktop\GitHib\ Repo\rowdyhack-25\server
python main.py

# Should output: WebSocket server on ws://localhost:8765
```

### Problem: "ModuleNotFoundError: No module named 'websockets'"

**Solution:**
```powershell
pip install websockets peewee google-generativeai
python main.py
```

### Problem: Gemini returns no analysis

**Solution:**
```powershell
# Check API key is valid:
# 1. Go to https://aistudio.google.com/app/apikeys
# 2. Verify key hasn't expired
# 3. Update .env file

# Check internet connection:
ping google.com

# Check logs for error message
# (Look in server terminal - Terminal 1)
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Start server | `cd server && python main.py` |
| Start client | `cd client/eyecore_mvp && cargo run --release` |
| Start dashboard | `cd dashboard && npm run dev` |
| Test clean activity | `python test_clean.py` |
| Test suspicious activity | `python test_suspicious.py` |
| View all devices | `sqlite3 server/app.db "SELECT * FROM devices;"` |
| View flagged reports | `sqlite3 server/app.db "SELECT * FROM reports WHERE reason='flagged_activity';"` |
| Count total packages | `sqlite3 server/app.db "SELECT COUNT(*) FROM reports;"` |
| Reset database | `rm server/app.db && python server/db_init.py` |

---

## What Happens Behind the Scenes

When you send an activity package:

```
1. Client collects data every 5 seconds
2. Sends via WebSocket to server
3. Server ingests & validates
4. Checks against thresholds (< 1ms)
5. If normal → logs only (cost: $0)
6. If suspicious:
   - Triggers rules
   - Calls Gemini API (1-2 seconds)
   - Gemini analyzes context
   - Creates flagged report with evidence
   - Broadcasts to professors (< 100ms)
7. Professor sees real-time alert
8. All data stored in database
```

**Total latency: < 5 seconds from suspicious activity to professor alert**

---

## Getting Help

1. **Check ARCHITECTURE.md** - System design overview
2. **Check DATA_FLOW_EXAMPLES.md** - Real JSON data examples
3. **Check SETUP.md** - Deployment details
4. **Check server logs** - Real-time errors and info

---

**Ready to monitor? Start with "Running the System" section above!** 🚀
