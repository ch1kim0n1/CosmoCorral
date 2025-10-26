# Flag Detection Integration Guide

## Quick Start

The **client-side flag detection system** is now ready to use. It provides real-time suspicious activity detection with ML-powered classification before sending data to the server.

### Location
```
client/eyecore_mvp/flag_detection/
├── __init__.py
├── README.md
├── pattern_detector.py     (6 behavioral patterns)
├── ml_classifier.py        (ML scoring + ensembles)
├── flag_data_generator.py  (JSON flag files)
└── orchestrator.py         (Main orchestrator)
```

---

## How It Works

### Pipeline Overview

```
Activity Package
    ↓
1️⃣  PatternDetector
    Analyzes 6 behavioral patterns:
    • Biometric Drift (keystroke changes)
    • Focus Collapse (sudden focus drop)
    • Stress Spike (stress increase)
    • Network Anomaly (traffic spike)
    • Resource Exhaustion (high CPU)
    • Temporal Inconsistency (impossible timing)
    ↓
2️⃣  MLClassifier
    Scores on 8 weighted features:
    • Keystroke anomaly (25%)
    • Network activity (25%)
    • Focus anomaly (15%)
    • App switching (10%)
    • CPU activity (8%)
    • Voice stress (10%)
    • Keystroke error (5%)
    • Mouse inactivity (2%)
    ↓
3️⃣  Classification Decision
    Risk Levels:
    • 🚨 Critical (>0.80) → STOP exam
    • ⚠️ High (0.65-0.80) → FLAG for Gemini
    • ⚡ Medium (0.45-0.65) → Monitor closely
    • ℹ️ Low (0.25-0.45) → Continue normal
    • ✓ Clean (<0.25) → No action
    ↓
4️⃣  FlagDataGenerator
    Creates standardized JSON files:
    • Risk assessment metadata
    • Detected patterns with confidence
    • Feature analysis and scores
    • Activity snapshot
    • Severity justification
    ↓
5️⃣  Decision
    Send to server OR Continue monitoring
```

---

## Integration into Existing Code

### In Your Activity Package Handler

```python
# client/eyecore_mvp/main.py or equivalent

from flag_detection import FlagDetectionOrchestrator
import asyncio

# 1. Initialize once at startup
FLAG_DETECTION = FlagDetectionOrchestrator(
    output_dir="./flag_data",
    enable_logging=True
)

async def handle_activity_package(package: Dict[str, Any], session_id: str, student_id: str):
    """Process incoming activity package."""
    
    # 2. Run flag detection
    detection_result = FLAG_DETECTION.process_package(
        package=package,
        session_id=session_id,
        student_id=student_id
    )
    
    # 3. Check if flagged
    if detection_result["should_flag"]:
        print(f"🚨 FLAGGED: {detection_result['risk_level']}")
        print(f"   Score: {detection_result['suspicious_score']:.2%}")
        print(f"   Patterns: {detection_result['patterns_detected']}")
        print(f"   File: {detection_result['flag_file']}")
        
        # 4. Send flag file to server
        flag_file_path = detection_result["flag_file"]
        await send_flag_to_server(flag_file_path, session_id, student_id)
    
    # 5. Send original package (always)
    await send_package_to_server(package, session_id, student_id)
    
    # Optional: Update UI with detection result
    await broadcast_to_ui({
        "type": "ActivityProcessed",
        "risk_level": detection_result["risk_level"],
        "recommendation": detection_result["recommendation"]
    })

async def send_flag_to_server(flag_file_path: str, session_id: str, student_id: str):
    """Send flagged data to server for Gemini analysis."""
    import json
    
    # Read flag file
    with open(flag_file_path, 'r') as f:
        flag_data = json.load(f)
    
    # Send to server
    response = await http_client.post(
        f"http://server:8000/api/flagged-activity/{session_id}/{student_id}",
        json=flag_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        print(f"✓ Flag sent to server: {flag_data['flag_id']}")
    else:
        print(f"✗ Failed to send flag: {response.status_code}")
```

### Server-Side Handler

```python
# server/main.py

@app.post("/api/flagged-activity/{session_id}/{student_id}")
async def receive_flagged_activity(
    session_id: str,
    student_id: str,
    flag_data: dict
):
    """
    Receive flagged activity from client.
    Client already did pattern detection + ML scoring.
    Now we do deep analysis with Gemini.
    """
    
    logger.info(f"Received flag from client: {flag_data['flag_id']}")
    
    # Get the pipeline
    pipeline = get_pipeline()
    
    # Extract client's assessment
    client_score = flag_data["risk_assessment"]["suspicious_score"]
    client_risk = flag_data["risk_assessment"]["risk_level"]
    detected_patterns = flag_data["detected_patterns"]
    
    # Run Gemini analysis (different from client ML)
    gemini_result = await pipeline.gemini_analyzer.analyze(
        package=flag_data,
        anomalies=[],  # Already detected by client
        triggered_rules=[]
    )
    
    # Create comprehensive report
    report = {
        "report_id": str(uuid.uuid4()),
        "session_id": session_id,
        "student_id": student_id,
        "flag_id": flag_data["flag_id"],
        "timestamp": datetime.utcnow().isoformat(),
        
        # Client assessment
        "client_assessment": {
            "suspicious_score": client_score,
            "risk_level": client_risk,
            "patterns_detected": detected_patterns,
            "confidence": flag_data["risk_assessment"]["confidence"],
        },
        
        # Server's Gemini analysis
        "gemini_assessment": gemini_result,
        
        # Combined decision
        "final_decision": determine_action(
            client_score,
            gemini_result["suspected_activity"],
            gemini_result["confidence"]
        ),
        
        "evidence": flag_data["explanation"],
        "recommendation": gemini_result["recommendation"],
    }
    
    # Store in database
    device = Device.get_or_none(Device.id == flag_data["original_package_summary"]["device_id"])
    if device:
        Report.create(
            device=device,
            session_id=session_id,
            student_id=student_id,
            timestamp=datetime.utcnow(),
            reason="flagged_activity_analyzed",
            message=f"{client_risk} - {gemini_result['suspected_activity']}",
            data=report
        )
    
    # Broadcast to professor dashboard
    await broadcast_to_professors({
        "type": "FlagAnalysisComplete",
        "data": report
    })
    
    return {"status": "processed", "report_id": report["report_id"]}

def determine_action(client_score: float, gemini_activity: str, gemini_confidence: float) -> str:
    """Determine final action from client + server assessment."""
    
    if client_score > 0.8 or gemini_confidence > 0.8:
        return "STOP_EXAM_IMMEDIATE"
    elif client_score > 0.6 and "cheating" in gemini_activity.lower():
        return "FLAG_FOR_PROFESSOR_REVIEW"
    elif client_score > 0.4 and gemini_confidence > 0.6:
        return "MONITOR_CLOSELY"
    else:
        return "CONTINUE_NORMAL"
```

---

## Configuration

### Environment Variables

```bash
# In your .env file
FLAG_DETECTION_OUTPUT_DIR=./client/eyecore_mvp/flag_data
FLAG_DETECTION_LOGGING=true
FLAG_DETECTION_CACHE_SIZE=1000
```

### Code Configuration

```python
from flag_detection import FlagDetectionOrchestrator

# Custom output directory
orchestrator = FlagDetectionOrchestrator(
    output_dir="./custom/path/flag_data",
    enable_logging=True
)

# Adjust risk thresholds (if needed)
# Edit ml_classifier.py _classify_risk_level() method:
"""
Change these thresholds:
- critical: 0.80 (default)
- high: 0.65 (default)
- medium: 0.45 (default)
- low: 0.25 (default)
"""
```

---

## Data Flow Example

### Scenario: Student Typing Changes Dramatically

**T=0:00 - Normal Behavior**
```json
Package: {
  "keystroke_rhythm_variance": 0.15,  // Consistent
  "focus_score": 0.85,                 // Good focus
  "cpu_usage": 35                      // Normal
}
Result: ✓ Low risk - continue
```

**T=0:30 - Pattern Detected**
```json
Package: {
  "keystroke_rhythm_variance": 0.72,  // Suddenly erratic!
  "focus_score": 0.22,                 // Focus dropped!
  "cpu_usage": 91                      // CPU spiked!
}

PatternDetector:
  - Biometric Drift detected (high severity)
  - Focus Collapse detected (high severity)
  - Resource Exhaustion detected (medium severity)

MLClassifier:
  - keystroke_anomaly: 0.72
  - focus_anomaly: 0.78
  - cpu_activity: 0.82
  - suspicious_score: (0.72 × 0.25) + (0.78 × 0.15) + (0.82 × 0.08) = 0.68

Result: ⚠️ HIGH RISK (0.68)
Action: Create flag file, send to server
```

**On Server:**
```python
# Server receives flag file
gemini_analysis = await analyze(flag_file)

# Gemini response
{
  "suspected_activity": "possible_impersonation",
  "confidence": 0.85,
  "why_suspected": "Sudden keystroke pattern change...",
  "evidence": ["Biometric drift", "Focus collapse", "Resource spike"],
  "recommendation": "Request verification from student"
}

# Final decision
if gemini_confidence > 0.8:
    action = "FLAG_FOR_PROFESSOR_REVIEW"
```

---

## API Reference

### FlagDetectionOrchestrator

#### `process_package(package, session_id, student_id, historical_context=None)`

Process a single activity package.

**Returns:**
```python
{
    "timestamp": "2025-10-26T12:34:56Z",
    "processed": True,
    "risk_level": "high|medium|low|critical|none",
    "suspicious_score": 0.0-1.0,
    "patterns_detected": 2,
    "should_flag": True/False,
    "flag_file": "/path/to/flag.json" or None,
    "flag_id": "uuid" or None,
    "recommendation": "FLAG_SERVER | MONITOR_CLOSE | CONTINUE_NORMAL"
}
```

#### `process_batch(packages, session_id, student_id, historical_context=None)`

Process multiple packages at once.

**Returns:**
```python
{
    "batch_processed": True,
    "total_packages": 100,
    "flagged_count": 3,
    "results": [...],  # List of individual results
    "batch_report": {...},  # If any flags
    "statistics": {
        "critical": 1,
        "high": 2,
        "medium": 5,
        "low": 10,
        "clean": 82
    }
}
```

#### `get_session_summary(session_id)`

Get all flags for a session.

#### `export_session_data(session_id, include_cache=True)`

Export all data for server transmission.

#### `get_statistics()`

Get overall system statistics.

---

## Testing

### Quick Test

```python
from flag_detection import FlagDetectionOrchestrator

# Create orchestrator
orchestrator = FlagDetectionOrchestrator()

# Create test package
test_package = {
    "package_id": "test-1",
    "session_id": "exam-123",
    "student_id": "student-456",
    "timestamp": datetime.utcnow().isoformat(),
    
    "input_dynamics": {
        "keystroke_rhythm_variance": 0.8,  # High = suspicious
        "keystroke_error_rate": 0.08,
        "mouse_velocity": 120.0,
    },
    
    "focus_metrics": {
        "focus_score": 0.25,  # Low = suspicious
        "eye_contact_percentage": 30.0,
    },
    
    "system_metrics": {
        "cpu_usage": 89.0,  # High = suspicious
        "memory_usage": 78.0,
    },
    
    "network_activity": {
        "bytes_sent": 8000000,  # 8MB = suspicious
        "bytes_received": 2000000,
    },
    
    "process_data": {
        "window_title": "Chrome",
        "app_switches": 18,  # High = suspicious
    },
    
    "voice_metrics": {
        "sentiment_score": -0.6,  # Negative = stressed
        "pitch_variance": 25.0,
    }
}

# Process
result = orchestrator.process_package(
    package=test_package,
    session_id="exam-123",
    student_id="student-456"
)

# Check result
print(f"Risk Level: {result['risk_level']}")  # Should be "high" or "critical"
print(f"Score: {result['suspicious_score']:.2%}")
print(f"Patterns: {result['patterns_detected']}")
print(f"Flagged: {result['should_flag']}")  # Should be True

# Verify flag file was created
if result['should_flag']:
    import json
    with open(result['flag_file'], 'r') as f:
        flag_data = json.load(f)
    print(f"Flag ID: {flag_data['flag_id']}")
    print(f"Patterns: {[p['pattern_name'] for p in flag_data['detected_patterns']]}")
```

---

## Monitoring & Debugging

### Enable Detailed Logging

```python
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("flag_detection")

# Now you'll see:
# INFO: [student-456] Patterns detected: ['Biometric Drift', 'Focus Collapse']
# WARNING: 🚨 FLAG CREATED: HIGH risk - uuid-here
```

### Get System Statistics

```python
stats = orchestrator.get_statistics()
print(f"Total packages: {stats['total_packages_processed']}")
print(f"Flags generated: {stats['total_flags_generated']}")
print(f"Critical flags: {stats['critical_flags']}")
print(f"Cache usage: {stats['cache_stats']['usage_percent']:.1f}%")
```

### Check Flag Files

```python
# List all flags for a session
summary = orchestrator.get_session_summary("exam-123")
print(f"Total flags: {summary['total_flags']}")
print(f"Critical: {summary['critical_count']}")
print(f"High: {summary['high_count']}")

for flag in summary['flags']:
    print(f"  - {flag['flag_id']}: {flag['risk_level']}")
```

---

## Performance Tips

### 1. Batch Processing

Process multiple packages together:
```python
# Fast - batches patterns
batch_result = orchestrator.process_batch(packages, session_id, student_id)

# Slower - individual processing
for pkg in packages:
    orchestrator.process_package(pkg, session_id, student_id)
```

### 2. Clear Cache Periodically

```python
# Clear old flags from memory
orchestrator.flag_cache.clear()

# But keep them on disk - they're small (~20KB each)
```

### 3. Monitor Resource Usage

```python
stats = orchestrator.get_statistics()
if stats['cache_stats']['usage_percent'] > 80:
    print("Cache usage high - clear it")
    orchestrator.flag_cache.clear()
```

---

## Troubleshooting

### Issue: All packages flagged

**Possible causes:**
1. ML weights too aggressive
2. Test environment with synthetic data
3. Student baseline not learned yet

**Solution:**
```python
# Reduce keystroke sensitivity
# In ml_classifier.py, change:
"keystroke_anomaly": 0.15,  # from 0.25

# Or increase thresholds:
# In _classify_risk_level(), change:
elif score > 0.50:  # from 0.65
    return "high"
```

### Issue: Not catching suspicious activity

**Possible causes:**
1. Thresholds too high
2. Insufficient pattern history
3. Student is good at cheating (legitimate concern)

**Solution:**
```python
# Increase pattern detection sensitivity
orchestrator.pattern_detector.history_window = 3 * 60  # 3 minutes instead of 5

# Lower risk threshold
# In _classify_risk_level(), change:
elif score > 0.55:  # from 0.65
    return "high"
```

### Issue: File permission errors

**Solution:**
```python
import os

# Ensure directory exists and is writable
flag_dir = "./flag_data"
os.makedirs(flag_dir, exist_ok=True)
os.chmod(flag_dir, 0o755)
```

---

## Next Steps

1. **Integrate** into your activity package handler
2. **Test** with sample suspicious packages
3. **Deploy** to production
4. **Monitor** statistics and adjust thresholds
5. **Train** baseline on first week of normal usage
6. **Iterate** based on false positive/negative rates

---

## Support

For issues or questions:
1. Check flag files in `./flag_data/`
2. Review logs for error messages
3. See `README.md` in flag_detection folder for detailed documentation
4. See `ADVANCED_FEATURES.md` for broader system context

---

**Last Updated:** October 26, 2025  
**Status:** ✅ Ready for Production
