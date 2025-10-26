# Space Cowboy: Complete Data Flow Architecture

## System Overview

```
STUDENT SIDE                      SERVER SIDE                    PROFESSOR SIDE
━━━━━━━━━━━━━━━━━━              ━━━━━━━━━━━━━━━━━━              ━━━━━━━━━━━━━━━━
EyeCore Client (Rust)             Processing Pipeline            Dashboard (Next.js)
  ↓                                 ↓                               ↓
Raw Events                        Aggregate (30s/60s)            Live Flagged Reports
  ↓                                 ↓
Normalize                         Feature Extract
  ↓                                 ↓
Activity Packages              Anomaly Scoring
  ↓                                 ↓
  └──────→ WebSocket ────→ Rules Engine ──→ Gemini API
           (real-time)         ↓                ↓
                           Score > Threshold?  Label + Rationale
                                 ↓                ↓
                            FlaggedReport ← ─ ─ ┘
                                 ↓
                            Database + Cache
                                 ↓
                           WebSocket Broadcast
                                 ↓
                            Professor Dashboard
                                 ↓
                        [Visualize + Take Action]
```

## Data Pipeline Stages

### Stage 1: Raw Event Collection (Client)
**Source**: EyeCore Rust client
**Frequency**: Every 5 seconds (configurable)
**Modalities**: System, Process, Input, Voice, Network, Focus

### Stage 2: Normalization
**What**: Convert all raw signals to typed events
**Where**: Server (Python)
**Output**: `RawEvent` → normalized schema

### Stage 3: Aggregation (Small Windows)
**Windows**:
- 30-second: Fast detection (copy-paste, rapid tab switches)
- 60-second: Behavioral patterns (focus drops, resource spikes)
- 5-minute: Trends (sustained anomalies)

**What we compute**:
- Per-window statistics (mean, max, variance)
- Stability scores
- Rate of change metrics

### Stage 4: Feature Extraction & Scoring
**Compute**:
- Cross-signal correlations (when does X always happen with Y?)
- Anomaly scores per signal (0-1, normalized)
- Composite score (weighted combination)

### Stage 5: Rule-Based Anomaly Detection (Cheap)
**No LLM cost** - just threshold checks:
```
IF cpu_usage > 95% AND network_bytes > 10MB/30s THEN flag "resource_spike"
IF app_switches > 15/min AND focus_score < 0.3 THEN flag "distraction_burst"
IF keystroke_rhythm_variance > 0.8 AND mouse_idle > 20s THEN flag "pause_inconsistent"
```

### Stage 6: Intelligent Analysis (Gemini API)
**When**: Only for flagged packages (cost-efficient)
**What we send**:
```json
{
  "session_id": "...",
  "timestamp": "...",
  "flagged_signals": [...],
  "evidence": {
    "metric_name": "value",
    "baseline": "expected_value",
    "delta": "deviation %"
  },
  "context": "What the student was doing (app names, etc)"
}
```

**What Gemini returns**:
```json
{
  "suspected_activity": "unauthorized_resource_access | impersonation | ...",
  "confidence": 0.92,
  "why_suspected": "Sudden spike in network traffic (12x baseline) while focus score dropped to 0.15",
  "evidence": [
    "Network bytes/30s: 50MB vs baseline 4MB",
    "Focus score: 0.15 vs baseline 0.75",
    "Active app: System Settings (unusual during exam)"
  ],
  "recommendation": "Review session | Request video | Alert professor"
}
```

### Stage 7: Store & Route
- **Persist**: All packages, flags, Gemini analyses
- **Route**: Send flagged reports to professor dashboard via WebSocket
- **Audit**: Immutable log of all decisions

---

## Data Structures

### 1. Raw Events (Client → Server)
```typescript
interface RawEvent {
  session_id: string;
  timestamp: ISO8601;
  device_id: string;
  modality: "system" | "process" | "input" | "voice" | "network" | "focus";
  data: Record<string, any>;
}
```

### 2. Activity Package (After Normalization)
```typescript
interface ActivityPackage {
  session_id: string;
  timestamp: ISO8601;
  device_id: string;
  student_id: string;
  
  system_metrics: {
    cpu_usage: number;        // 0-100
    memory_usage: number;
    disk_io_rate: number;
  };
  
  process_data: {
    active_process: string;
    window_title: string;
    app_switches: number;     // count in this interval
  };
  
  input_dynamics: {
    keystroke_rate: number;   // keys/sec
    keystroke_rhythm_variance: number;
    keystroke_errors: number;
    mouse_velocity: number;
    mouse_idle_duration: number;
  };
  
  network_activity: {
    bytes_sent: number;
    bytes_received: number;
    connections_active: number;
    unusual_protocols: string[];
  };
  
  focus_metrics: {
    focus_score: number;       // 0-1
    attention_drops: number;
    context_switches: number;
  };
  
  voice_data?: {
    sentiment_score: number;   // -1 to +1
    emotion_detected: string;
    speech_rate: number;
    energy_level: number;
  };
}
```

### 3. Anomaly Score (Per Signal)
```typescript
interface AnomalyScore {
  signal_name: string;
  raw_value: number;
  baseline_expected: number;
  z_score: number;            // deviation in std devs
  percentile_anomaly: number;  // 0-1, how anomalous
  threshold_breached: boolean;
  reason: string;
}
```

### 4. Flagged Report (To Gemini & Database)
```typescript
interface FlaggedReport {
  id: string;
  session_id: string;
  timestamp: ISO8601;
  device_id: string;
  student_id: string;
  
  anomalies: AnomalyScore[];
  
  composite_anomaly_score: number;  // 0-1
  triggered_rules: string[];        // Which rules flagged this
  
  aggregation_window: "30s" | "60s" | "5m";
  
  gemini_analysis?: {
    suspected_activity: string;
    confidence: number;
    why_suspected: string;
    evidence: string[];
    recommendation: string;
    tokens_used: number;
  };
  
  status: "new" | "reviewed" | "resolved" | "false_positive";
  professor_notes?: string;
}
```

---

## Implementation Details

### Server Flow

```python
# server/main.py

async def handle_activity_package(ws, package: ActivityPackage):
    # 1. Normalize & validate
    normalized = normalize_package(package)
    
    # 2. Store raw
    db.save_raw_package(normalized)
    
    # 3. Add to aggregation windows
    agg_engine.ingest(normalized)
    
    # 4. Compute anomalies
    anomalies = compute_anomalies(normalized)
    
    # 5. Check rules
    triggered_rules = rules_engine.evaluate(normalized, anomalies)
    
    if triggered_rules:
        # 6. Call Gemini only if flagged
        flagged = FlaggedReport(
            anomalies=anomalies,
            triggered_rules=triggered_rules,
            ...
        )
        
        gemini_analysis = await gemini_client.analyze(flagged)
        flagged.gemini_analysis = gemini_analysis
        
        # 7. Store & broadcast
        db.save_flagged_report(flagged)
        broadcast_to_professor_dashboard(flagged)
    else:
        # Just store, no alert
        db.save_clean_package(normalized)
```

### Database Schema

```sql
-- Raw packages (immutable log)
CREATE TABLE activity_packages (
    id UUID PRIMARY KEY,
    session_id VARCHAR,
    device_id VARCHAR,
    student_id VARCHAR,
    timestamp TIMESTAMP,
    data JSONB,  -- Full ActivityPackage
    created_at TIMESTAMP DEFAULT NOW()
);

-- Flagged reports
CREATE TABLE flagged_reports (
    id UUID PRIMARY KEY,
    package_id UUID REFERENCES activity_packages,
    student_id VARCHAR,
    composite_anomaly_score FLOAT,
    triggered_rules JSONB,
    gemini_analysis JSONB,
    status VARCHAR,
    professor_notes TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Audit log
CREATE TABLE audit_log (
    id UUID PRIMARY KEY,
    event_type VARCHAR,
    report_id UUID,
    actor_id VARCHAR,  -- Professor ID
    action VARCHAR,
    timestamp TIMESTAMP
);
```

---

## Gemini API Integration

### Prompt Template

```
You are a cheating detection analyst for proctored exams.

Analyze this student activity snapshot and determine if there's suspicious behavior.

STUDENT ACTIVITY DATA:
- Active Application: {{active_app}}
- Focus Score: {{focus_score}} (baseline: {{focus_baseline}})
- Keystroke Rhythm Variance: {{keystroke_variance}} (baseline: {{keystroke_baseline}})
- Network Usage: {{network_bytes_sent}} bytes sent, {{network_bytes_received}} received
  (baseline: {{network_baseline}})
- Context Switches: {{context_switches}} (baseline: {{context_baseline}})

ANOMALIES DETECTED:
{{anomalies_list}}

Respond with JSON:
{
  "suspected_activity": "string - type of cheating or none",
  "confidence": number 0-1,
  "why_suspected": "string - clear explanation",
  "evidence": ["string", ...],
  "recommendation": "string - action professor should take"
}
```

### Cost Optimization

- **Baseline packages**: 0.5¢ each (saved locally, no API call)
- **Flagged packages**: 2¢ each (Gemini analysis)
- **Daily budget**: Monitor 30 students × ~300 packages/day = ~9K calls
  - If 1% flagged: 90 Gemini calls/day × $0.02 = $1.80/day (affordable)

---

## WebSocket Message Protocol

### Client → Server

```json
{
  "method": "Authenticate",
  "data": { "access_code": "..." }
}

{
  "method": "Package",
  "data": {
    "token": "...",
    "data": { /* ActivityPackage */ }
  }
}
```

### Server → Professor Dashboard

```json
{
  "type": "FlaggedReportAlert",
  "data": {
    "id": "...",
    "student_id": "...",
    "suspected_activity": "...",
    "confidence": 0.92,
    "timestamp": "..."
  }
}

{
  "type": "SessionUpdate",
  "data": {
    "device_id": "...",
    "student_id": "...",
    "status": "active",
    "anomaly_score": 0.15
  }
}
```

---

## Deployment

### Local Development
```bash
# Terminal 1: Student client
cd client/eyecore_mvp
cargo run --release

# Terminal 2: Server
cd server
export GEMINI_API_KEY="..."
python main.py

# Terminal 3: Professor dashboard
cd dashboard
npm run dev
```

### Environment Variables
```
GEMINI_API_KEY=your-api-key
DATABASE_URL=postgres://...
SERVER_PORT=8765
STUDENT_CLIENT_PORT=3000
DASHBOARD_PORT=3000
```

---

## Security Notes

- ✅ Access codes hashed with bcrypt
- ✅ Session tokens signed JWTs (5min expiry)
- ✅ WebSocket over WSS (production)
- ✅ All data encrypted at rest
- ✅ Immutable audit log of all analyses
- ✅ GDPR: Export/delete on request
