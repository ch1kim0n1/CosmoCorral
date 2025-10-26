# Space Cowboy: Complete Setup & Deployment Guide

## Quick Start (5 minutes)

### Prerequisites
- Python 3.9+
- Node.js 16+
- Rust 1.70+
- Gemini API Key (free at https://aistudio.google.com/app/apikeys)

### 1. Configure Environment

```bash
cd rowdyhack-25
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 2. Install Server Dependencies

```bash
cd server
pip install -r requirements.txt
# If requirements.txt doesn't exist:
pip install websockets peewee google-generativeai
```

### 3. Initialize Database

```bash
cd server
python db_init.py
# This creates app.db with Device and Report tables
```

### 4. Start Server

```bash
cd server
export GEMINI_API_KEY="your-key-here"  # or set in .env
python main.py
# Should output: WebSocket server on ws://localhost:8765
```

### 5. Start Student Client (in new terminal)

```bash
cd client/eyecore_mvp
cargo run --release
# Should output: 🔍 EyeCore MVP Starting...
#                🚀 EyeCore API running on http://127.0.0.1:3000
```

### 6. Start Professor Dashboard (in another new terminal)

```bash
cd dashboard
npm install  # First time only
npm run dev
# Should output: ▲ Next.js 16.0.0
#                - Local: http://localhost:3000
```

### 7. Test the Flow

In a new terminal:

```bash
# Create a device (student's computer)
curl -X POST http://localhost:8765 \
  -H "Content-Type: application/json" \
  -d '{
    "method": "CreateDevice",
    "data": {
      "name": "Student-Laptop-01",
      "description": "John Doe - Exam Room 101"
    }
  }'

# Response: {"status": "success", "data": {"id": "...", "access_code": "ABC123XYZ"}}
```

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         SPACE COWBOY                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  STUDENT SIDE                SERVER SIDE              PROF SIDE  │
│  ──────────────              ────────────              ─────────  │
│                                                                   │
│  EyeCore MVP                 Pipeline                Dashboard    │
│  (Rust)                      (Python)                 (Next.js)   │
│                                                                   │
│  ├─ System metrics           ├─ Ingest                ├─ Real-time
│  ├─ Process data             ├─ Normalize             │  alerts
│  ├─ Input dynamics           ├─ Aggregate (30s/60s)   ├─ Flagged
│  ├─ Network activity    ──→  ├─ Anomaly detection    │  reports
│  ├─ Focus metrics            ├─ Rules engine         ├─ Student
│  └─ Voice data               ├─ Gemini analysis   ←──┤  sessions
│                              └─ Database storage     └─ Actions
│
│  Local REST API              WebSocket (ws://)
│  (http://127.0.0.1:3000)     (ws://localhost:8765)
│
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Example

### Scenario: Student Takes Exam

#### 1. **Initialization**
```
Student boots laptop → EyeCore starts → Connects to server
Server: Creates device with access code
Student enters code → Authenticated with JWT token
```

#### 2. **Activity Collection** (Every 5 seconds)
```
Student is taking exam
↓
EyeCore collects:
  - CPU: 42%, Memory: 58%, Disk I/O: 2.3MB/s
  - Active window: "Google Docs" | App switches: 1
  - Keystrokes: 65 keys/sec, rhythm variance: 0.1 (normal)
  - Network: 150KB sent, 850KB received
  - Focus score: 0.85 (very focused)
  - Voice: sentiment +0.3, energy 0.7
↓
Packages as ActivityPackage JSON
↓
Sends via WebSocket to server
```

#### 3. **Server-Side Processing** (ms latency)
```
Server receives ActivityPackage
↓
├─ STAGE 1: Normalize & Validate ✓
├─ STAGE 2: Store raw package in DB ✓
├─ STAGE 3: Add to 30s/60s/5m windows ✓
├─ STAGE 4: Detect anomalies
│   - CPU 42% < 90% ✓ OK
│   - Focus 0.85 > 0.3 ✓ OK
│   - Network normal ✓ OK
│   - Keystroke rhythm 0.1 < 0.75 ✓ OK
│   → No anomalies detected
├─ STAGE 5: Check rules
│   - No triggered rules
├─ STAGE 6: Gemini analysis?
│   → Not needed (no anomalies)
├─ STAGE 7: Store & route
│   → Log to database as "clean_activity"
│   → No alert to professor
└─ ✓ Efficiency win! Saved Gemini API cost
```

#### 4. **Suspicious Activity Example**
```
Student suddenly:
  - Switches to Chrome Developer Tools
  - Opens Discord in new tab
  - Focus score drops to 0.15
  - Network spike: 15MB/s
↓
Server detects:
  - Focus < 0.3 ✓ ANOMALY
  - Network spike ✓ ANOMALY
  - App switches > 15 ✓ ANOMALY
↓
RULES TRIGGERED:
  1. "distraction_burst": low focus + high app switches
  2. "resource_spike": network anomaly
↓
ESCALATE TO GEMINI (cost: ~2 cents)
  Input: {
    "active_app": "Discord",
    "focus_score": 0.15,
    "network_sent": 15MB,
    "anomalies": [...],
    "triggered_rules": [...]
  }
↓
GEMINI ANALYSIS:
  {
    "suspected_activity": "unauthorized_resource_access",
    "confidence": 0.87,
    "why_suspected": "Sudden network spike with Discord open suggests external communication attempt",
    "evidence": [
      "Network bytes 15MB (vs baseline 1MB)",
      "Focus score 0.15 (baseline 0.8)",
      "Discord is communication app, not exam-related",
      "Pattern matches 'seeking external help'"
    ],
    "recommendation": "Review recording. Request explanation from student.",
    "alternative_explanations": ["Internet connectivity issue", "System update"]
  }
↓
CREATE FlaggedReport:
  {
    "id": "flag-5928...",
    "student_id": "john.doe@edu.com",
    "suspected_activity": "unauthorized_resource_access",
    "confidence": 0.87,
    "timestamp": "2025-10-26T15:32:45Z",
    "anomalies": [...],
    "triggered_rules": [...],
    "gemini_analysis": {...}
  }
↓
BROADCAST TO PROFESSORS (via WebSocket)
  message = {
    "type": "FlaggedReportAlert",
    "data": {FlaggedReport}
  }
↓
PROFESSOR DASHBOARD:
  🚨 ALERT: John Doe - Unauthorized Resource Access (87% confidence)
  [Review] [Mark False Positive] [Terminate Session]
```

---

## Message Protocol

### Client → Server

#### 1. Authentication
```json
{
  "method": "Authenticate",
  "data": {
    "access_code": "ABC123XYZ"
  }
}

→ Response:
{
  "status": "success",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs..."
  }
}
```

#### 2. Send Activity Package
```json
{
  "method": "Package",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "student_id": "john.doe@edu.com",
    "data": {
      "session_id": "sess-12345",
      "timestamp": "2025-10-26T15:32:40Z",
      "device_id": "dev-abc123",
      "student_id": "john.doe@edu.com",
      "package_id": "pkg-xyz789",
      "aggregation_window": "raw",
      "system_metrics": {
        "cpu_usage": 42.0,
        "memory_usage": 58.0,
        "disk_io_rate": 2.3
      },
      "process_data": {
        "active_process": "chrome.exe",
        "active_pid": 5932,
        "window_title": "Google Docs - Final Exam",
        "app_switches": 0,
        "running_process_count": 24
      },
      "input_dynamics": {
        "keystroke_rate": 65.0,
        "keystroke_rhythm_variance": 0.1,
        "keystroke_errors": 0.5,
        "mouse_velocity": 150.0,
        "mouse_acceleration": 45.0,
        "mouse_idle_duration": 2.0,
        "clicks_per_minute": 12.0
      },
      "network_activity": {
        "bytes_sent": 150000,
        "bytes_received": 850000,
        "connections_active": 3,
        "data_transfer_rate": 1.0,
        "unusual_protocols": [],
        "dns_queries": 0
      },
      "focus_metrics": {
        "focus_score": 0.85,
        "attention_drops": 0,
        "context_switches": 1,
        "time_since_interaction": 2.0,
        "productive_app_time": 300.0
      },
      "client_version": "0.1.0"
    }
  }
}

→ Response:
{
  "status": "success",
  "data": {
    "message": "Package processed (clean)"
  }
}

OR (if flagged):
{
  "status": "success",
  "data": {
    "message": "Package processed and flagged",
    "flag_id": "flag-5928..."
  }
}
```

### Server → Professor Dashboard

#### 1. Register Professor
```json
{
  "type": "RegisterProfessor",
  "data": {
    "professor_id": "prof.smith@edu.com"
  }
}

→ Response:
{
  "type": "RegistrationConfirmed",
  "professor_id": "prof.smith@edu.com"
}
```

#### 2. Flagged Report Alert (from server to professor)
```json
{
  "type": "FlaggedReportAlert",
  "data": {
    "id": "flag-5928...",
    "student_id": "john.doe@edu.com",
    "suspected_activity": "unauthorized_resource_access",
    "confidence": 0.87,
    "timestamp": "2025-10-26T15:32:45Z",
    "gemini_analysis": {
      "why_suspected": "...",
      "evidence": [...],
      "recommendation": "..."
    }
  }
}
```

#### 3. Professor Takes Action
```json
{
  "type": "AcknowledgeReport",
  "data": {
    "report_id": "flag-5928...",
    "action": "flag_false_positive",
    "notes": "Student was legitimately using Discord for class chat"
  }
}

→ Response:
{
  "type": "ActionAcknowledged",
  "report_id": "flag-5928..."
}
```

---

## Database Schema

### Tables

**devices**
- id (UUID primary key)
- name (string)
- description (text)
- access_code (string - hashed with bcrypt)
- last_online (timestamp)
- last_session_time (integer - seconds)
- created_at (timestamp)

**reports**
- id (UUID primary key)
- device_id (UUID foreign key → devices)
- timestamp (timestamp)
- reason (string - "raw_activity", "flagged_activity")
- message (string)
- data (JSON - full activity package or flagged report)
- created_at (timestamp)

**audit_log**
- id (UUID primary key)
- event_type (string)
- report_id (UUID)
- actor_id (string - professor ID)
- action (string)
- details (JSON)
- timestamp (timestamp)

---

## Configuration & Tuning

### Anomaly Thresholds (server/pipeline.py)

```python
ANOMALY_THRESHOLDS = {
    "cpu_usage_high": 90.0,              # Trigger anomaly if > 90%
    "memory_usage_high": 85.0,           # Trigger anomaly if > 85%
    "keystroke_rhythm_variance_high": 0.75,  # Erratic typing threshold
    "focus_score_low": 0.3,              # Distraction threshold
    "app_switches_per_minute_high": 15,  # Too many app switches
    "network_bytes_30s_high": 10 * 1024 * 1024,  # 10MB in 30 seconds
}
```

### Rules (server/pipeline.py)

Each rule has:
- **enabled**: Turn on/off
- **severity**: "warning" | "alert" | "critical"
- **escalate_to_gemini**: Should this trigger Gemini analysis?

Modify rules without restarting server:
```python
# In server/pipeline.py, update RULES dict
RULES["my_custom_rule"] = {
    "enabled": True,
    "severity": "alert",
    "description": "My custom detection",
    "escalate_to_gemini": True,
}
```

### Gemini API Pricing

- Input: ~$0.075/1M tokens
- Output: ~$0.30/1M tokens
- Average flagged package: 2,000 tokens = $0.0002
- 30 students × 300 packages/day × 1% flagged = 90 calls/day
- Daily cost: ~$0.02 (very affordable!)

---

## Testing

### 1. Unit Tests
```bash
cd server
python -m pytest tests/ -v
```

### 2. Integration Test (Manual)

**Terminal 1 - Server:**
```bash
cd server
export GEMINI_API_KEY="..."
python main.py
```

**Terminal 2 - Test Client:**
```bash
python tests/test_integration.py
```

**Expected Output:**
```
Creating device...
Device: id=abc-123, access_code=XYZ789
Authenticating...
Token: eyJhbGci...
Sending clean package...
Response: {"status": "success", "data": {"message": "Package processed (clean)"}}
Sending flagged package (high CPU + low focus)...
Response: {"status": "success", "data": {"message": "Package processed and flagged", "flag_id": "flag-..."}}
✓ Integration test passed!
```

### 3. Load Test
```bash
python tests/load_test.py --students 30 --duration 300 --packages-per-sec 6
# Simulates 30 students for 5 minutes, ~1 package per student per 5 seconds
```

---

## Deployment

### Docker (Single Container)

```dockerfile
FROM python:3.9

WORKDIR /app

COPY server/requirements.txt .
RUN pip install -r requirements.txt

COPY server/ .

ENV GEMINI_API_KEY=${GEMINI_API_KEY}
ENV DATABASE_URL=sqlite:///app.db

CMD ["python", "main.py"]
```

```bash
docker build -t space-cowboy-server .
docker run -e GEMINI_API_KEY="your-key" -p 8765:8765 space-cowboy-server
```

### Production Checklist

- [ ] Use WSS (WebSocket Secure) - add SSL certificates
- [ ] Hash all access codes with bcrypt
- [ ] Implement JWT token expiration (5-10 minutes)
- [ ] Add rate limiting on WebSocket messages
- [ ] Set up proper logging & monitoring
- [ ] Use PostgreSQL instead of SQLite
- [ ] Implement data retention policy (30-90 days)
- [ ] Add audit logging for all professor actions
- [ ] Get legal review for data collection
- [ ] Test with actual student data (anonymized)

---

## Troubleshooting

### "GEMINI_API_KEY not set"
```bash
# Check if .env exists
cat .env | grep GEMINI_API_KEY

# Or set directly
export GEMINI_API_KEY="your-api-key"
```

### "WebSocket connection refused"
```bash
# Make sure server is running
curl http://localhost:8765
# Should fail (not HTTP endpoint), but shows server is listening
```

### "Port 8765 already in use"
```bash
# Find process using port
lsof -i :8765
# Or change port in main.py
```

### "Database locked"
```bash
# SQLite single-threaded issue; restart server
# For production, use PostgreSQL
```

---

## Next Steps

1. **Implement Professor Dashboard UI**
   - Display live flagged reports
   - Show student sessions with anomaly scores
   - Add actions: review, terminate, mark false positive

2. **Add More Data Sources**
   - Screen recording (optional, with consent)
   - Advanced NLP for written responses
   - Facial recognition (optional)

3. **Machine Learning**
   - Build per-student baseline (normal behavior)
   - Anomaly detection with Isolation Forest
   - Cheat pattern classification

4. **Integration**
   - LMS integration (Canvas, Blackboard, etc.)
   - Email alerts to professors
   - Student notification system

---

## Support

For issues or questions:
1. Check ARCHITECTURE.md for system overview
2. Read shared_types.ts for data structure docs
3. Review QUICKSTART.md for basic setup
4. Check logs: `tail -f server/logs/*`
