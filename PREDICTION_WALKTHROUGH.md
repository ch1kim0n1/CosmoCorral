# Step-by-Step: How a Package Gets Predicted as Suspicious

## Real Example: A Student's Keystroke Suddenly Changes

Let me walk through exactly what happens when the system processes one activity package.

---

## 📦 Input: Raw Activity Package

```json
{
  "package_id": "pkg-001",
  "session_id": "exam-123",
  "student_id": "alice-456",
  "timestamp": "2025-10-26T14:30:45Z",
  "timestamp_ms": 1730000445000,
  
  "input_dynamics": {
    "keystroke_rhythm_variance": 0.82,      // 0=consistent, 1=erratic
    "keystroke_error_rate": 0.07,           // 7% typos
    "keystroke_speed": 120,                 // 120 keys/sec (very fast!)
    "mouse_velocity": 85.5,                 // pixels/sec (tense movement)
    "mouse_idle_duration": 2                // seconds since last mouse move
  },
  
  "focus_metrics": {
    "focus_score": 0.22,                    // Very low focus!
    "eye_contact_percentage": 15            // Looking away a lot
  },
  
  "system_metrics": {
    "cpu_usage": 91.2,                      // Very high CPU
    "memory_usage": 82.3,                   // High memory too
  },
  
  "network_activity": {
    "bytes_sent": 7500000,                  // 7.5 MB sent
    "bytes_received": 1200000               // 1.2 MB received
  },
  
  "process_data": {
    "window_title": "Chrome - Google Search",  // Not the exam!
    "app_switches": 12                      // Switched apps 12 times
  },
  
  "voice_metrics": {
    "sentiment_score": -0.65,               // Negative sentiment (stressed)
    "pitch_variance": 35.2                  // High pitch variance
  }
}
```

---

## 🔄 Step 1: Add to Pattern Detector History

```python
# PatternDetector.add_activity(package)

self.history["keystroke_rhythm_variance"].append(0.82)
self.history["focus_score"].append(0.22)
self.history["stress_level"].append(calculated_stress_from_package)
self.history["network_bytes"].append(8700000)  # 7.5 + 1.2 MB
self.history["cpu_usage"].append(91.2)
self.history["app_switches"].append(12)
self.history["timestamps"].append("2025-10-26T14:30:45Z")

# Result: 7 data points per feature (5-minute rolling window)
# Sample history now:
{
  "keystroke_rhythm_variance": [0.15, 0.18, 0.19, 0.22, 0.35, 0.65, 0.82]
  "focus_score": [0.85, 0.82, 0.81, 0.79, 0.55, 0.35, 0.22]
  "timestamps": [14:24:45, 14:25:45, 14:26:45, ..., 14:30:45]
}
```

---

## 🔍 Step 2: Detect Patterns

### Pattern 1: Biometric Drift

```python
# Check if keystroke pattern changed
recent = [0.65, 0.82]                    # Last 2 samples
older = [0.15, 0.18, 0.19, 0.22, 0.35]  # Earlier samples

recent_mean = (0.65 + 0.82) / 2 = 0.735
older_mean = (0.15 + 0.18 + 0.19 + 0.22 + 0.35) / 5 = 0.218

# Check condition
if recent_mean > older_mean × 1.5:          # 0.735 > 0.218 × 1.5 (0.327)? YES!
   AND recent_mean > 0.5:                  # 0.735 > 0.5? YES!
   
   DETECTED = True ✓
   
   Result:
   {
     "pattern_name": "Biometric Drift",
     "severity": "high",
     "recent_variance": 0.735,
     "older_variance": 0.218,
     "change_magnitude": 3.37,  # 337% increase!
     "confidence": 0.94
   }
```

### Pattern 2: Focus Collapse

```python
# Check if focus dropped suddenly
recent_focus = [0.35, 0.22]        # Last 2
older_focus = [0.85, 0.82, 0.81, 0.79, 0.55]  # Earlier

recent_mean = (0.35 + 0.22) / 2 = 0.285
older_mean = (0.85 + 0.82 + 0.81 + 0.79 + 0.55) / 5 = 0.764

# Check condition
if older_mean > 0.6:                # 0.764 > 0.6? YES!
   AND recent_mean < 0.3:           # 0.285 < 0.3? YES!
   AND (older_mean - recent_mean) > 0.3:  # 0.764 - 0.285 = 0.479 > 0.3? YES!
   
   DETECTED = True ✓
   
   Result:
   {
     "pattern_name": "Focus Collapse",
     "severity": "high",
     "recent_focus": 0.285,
     "older_focus": 0.764,
     "drop_magnitude": 0.479,
     "confidence": 0.96
   }
```

### Pattern 3: Stress Spike

```python
# Calculate stress level from multiple signals
# stress_level = (keystroke_erraticism × 0.4) + (mouse_velocity/100 × 0.3) + (voice_sentiment × 0.3)
#              = (0.82 × 0.4) + (85.5/100 × 0.3) + (abs(-0.65) × 0.3)
#              = 0.328 + 0.2565 + 0.195 = 0.7795

recent_stress = [0.21, 0.24, 0.28, 0.42, 0.65, 0.78]  # Last 6
older_stress = [0.15, 0.18, 0.19]                      # Earlier

recent_mean = 0.463
older_mean = 0.173

# Check condition
if recent_mean > 0.6:               # 0.463 > 0.6? NO...
   DETECTED = False (barely missed!)
   
   But recent trend is VERY concerning:
   0.15 → 0.18 → 0.19 → 0.21 → 0.78  # Huge jump!
```

### Pattern 4: Network Anomaly

```python
# Check for network spike
recent_network = [1000000, 8700000]  # Last 2 packages
older_network = [900000, 950000, 1100000, 1050000, 1200000]

recent_mean = 4850000  # 4.85 MB
older_mean = 1040000   # 1.04 MB

# Check condition
if recent_mean > 5 * 1024 * 1024:    # 4.85MB > 5MB? NO (just barely not)
   DETECTED = False
   
   BUT: recent_mean > older_mean × 3?  # 4.85 > 1.04 × 3 (3.12)? YES!
   
   Result:
   {
     "pattern_name": "Network Anomaly",
     "severity": "high",
     "recent_network_mb": 4.85,
     "older_network_mb": 1.04,
     "spike_multiplier": 4.66,  # 4.66x spike!
     "confidence": 0.88
   }
```

### Pattern 5: Resource Exhaustion

```python
# Check for high CPU usage
recent_cpu = [35, 38, 42, 55, 88, 91.2]
recent_mean = 58.2
recent_max = 91.2

# Check condition
if recent_mean > 80:                # 58.2 > 80? NO...
   DETECTED = False
   
   BUT high_cpu_count = 2 (two samples > 85)
   The trend is going UP though: 35 → 91!
```

### Summary of Patterns Detected

```python
patterns_detected = [
    {
        "pattern_name": "Biometric Drift",
        "severity": "high",
        "confidence": 0.94
    },
    {
        "pattern_name": "Focus Collapse",
        "severity": "high",
        "confidence": 0.96
    },
    {
        "pattern_name": "Network Anomaly",
        "severity": "high",
        "confidence": 0.88
    }
]
# 3 patterns detected! All high severity.
```

---

## 🤖 Step 3: ML Classification - Feature Scoring

```python
# MLClassifier.classify(package, patterns)

# Extract the 8 features
features = {
    "keystroke_rhythm_variance": 0.82,
    "keystroke_error_rate": 0.07,
    "network_bytes_sent": 7500000,
    "network_bytes_received": 1200000,
    "cpu_usage": 91.2,
    "memory_usage": 82.3,
    "focus_score": 0.22,
    "app_switches": 12,
    "voice_sentiment": -0.65,
    "mouse_velocity": 85.5,
    "mouse_idle_duration": 2
}

# Normalize each feature to 0-1 scale
# (where 1 = most suspicious)

keystroke_anomaly = min(1.0, 0.82 / 1.0) = 0.82
keystroke_error = min(1.0, 0.07 / 0.1) = 0.70
network_activity = min(1.0, (7500000 + 1200000) / (20 * 1024 * 1024)) 
                 = min(1.0, 8700000 / 20971520) = 0.415
cpu_activity = max(0.0, (91.2 - 50) / 50) = 0.824
focus_anomaly = max(0.0, 1.0 - 0.22) = 0.78
app_switching = min(1.0, 12 / 20) = 0.60
voice_stress = abs(-0.65) = 0.65
mouse_inactivity = 0.0  # Not idle (only 2 sec)

# Result: 8 normalized feature scores
feature_scores = {
    "keystroke_anomaly": 0.82,
    "keystroke_error": 0.70,
    "network_activity": 0.415,
    "cpu_activity": 0.824,
    "focus_anomaly": 0.78,
    "app_switching": 0.60,
    "voice_stress": 0.65,
    "mouse_inactivity": 0.0
}
```

---

## ⚖️ Step 4: Apply Weights

```python
# Multiply each feature score by its importance weight

weights = {
    "keystroke_anomaly": 0.25,
    "network_activity": 0.25,
    "focus_anomaly": 0.15,
    "app_switching": 0.10,
    "cpu_activity": 0.08,
    "voice_stress": 0.10,
    "keystroke_error": 0.05,
    "mouse_inactivity": 0.02
}

contributions = {
    "keystroke_anomaly": 0.82 × 0.25 = 0.205,
    "network_activity": 0.415 × 0.25 = 0.10375,
    "focus_anomaly": 0.78 × 0.15 = 0.117,
    "app_switching": 0.60 × 0.10 = 0.06,
    "cpu_activity": 0.824 × 0.08 = 0.06592,
    "voice_stress": 0.65 × 0.10 = 0.065,
    "keystroke_error": 0.70 × 0.05 = 0.035,
    "mouse_inactivity": 0.0 × 0.02 = 0.0
}

# Sum all weighted contributions
base_suspicious_score = 0.205 + 0.104 + 0.117 + 0.06 + 0.066 + 0.065 + 0.035 + 0.0
                       = 0.652
```

---

## 📈 Step 5: Apply Pattern Multiplier

```python
# Patterns can boost the score

patterns_found = [
    "Biometric Drift" (high, confidence 0.94),
    "Focus Collapse" (high, confidence 0.96),
    "Network Anomaly" (high, confidence 0.88)
]

# Calculate multiplier
multiplier = 1.0
for pattern in patterns_found:
    severity = pattern.severity
    confidence = pattern.confidence
    
    if severity == "high":
        multiplier *= (1.5 * confidence)

# multiplier = 1.0 × (1.5 × 0.94) × (1.5 × 0.96) × (1.5 × 0.88)
#            = 1.0 × 1.41 × 1.44 × 1.32
#            = 2.68 (but capped at 2.5)
#            = 2.5

final_score = base_suspicious_score × multiplier
            = 0.652 × 2.5
            = 1.63 (capped at 1.0)
            = 1.0
```

---

## 🚨 Step 6: Classify Risk Level

```python
# Compare final score to thresholds

final_score = 1.0

if final_score > 0.80:
    risk_level = "critical"  ← THIS ONE
    risk_label = "🚨 CRITICAL - Immediate escalation required"
    should_flag = True

elif final_score > 0.65:
    risk_level = "high"

elif final_score > 0.45:
    risk_level = "medium"

# ... etc

# Result
classification = {
    "suspicious_score": 0.652,  # Base score before multiplier
    "risk_level": "critical",
    "risk_label": "🚨 CRITICAL - Immediate escalation required",
    "should_flag": True,
    "recommendation": "FLAG_IMMEDIATE - Stop exam and flag for review"
}
```

---

## 📄 Step 7: Generate Flag File

```python
# FlagDataGenerator.create_flag_file()

flag_file = {
    "flag_id": "a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6",
    "timestamp": "2025-10-26T14:30:45Z",
    "session_id": "exam-123",
    "student_id": "alice-456",
    
    "risk_assessment": {
        "risk_level": "critical",
        "risk_label": "🚨 CRITICAL - Immediate escalation required",
        "suspicious_score": 0.652,
        "confidence": 0.92,
        "should_flag": True,
        "recommendation": "FLAG_IMMEDIATE - Stop exam and flag for review"
    },
    
    "detected_patterns": [
        {
            "pattern_name": "Biometric Drift",
            "severity": "high",
            "description": "Keystroke pattern changed significantly",
            "recent_variance": 0.735,
            "older_variance": 0.218,
            "change_magnitude": 3.37,
            "confidence": 0.94
        },
        {
            "pattern_name": "Focus Collapse",
            "severity": "high",
            "description": "Focus score dropped suddenly",
            "recent_focus": 0.285,
            "older_focus": 0.764,
            "drop_magnitude": 0.479,
            "confidence": 0.96
        },
        {
            "pattern_name": "Network Anomaly",
            "severity": "high",
            "description": "Network activity spiked significantly",
            "recent_network_mb": 4.85,
            "older_network_mb": 1.04,
            "spike_multiplier": 4.66,
            "confidence": 0.88
        }
    ],
    
    "feature_analysis": {
        "analyzed_features": {
            "keystroke_rhythm_variance": 0.82,
            "network_bytes_total": 8700000,
            "focus_score": 0.22,
            "cpu_usage": 91.2,
            "app_switches": 12,
            "voice_sentiment": -0.65,
            "keystroke_error_rate": 0.07,
            "mouse_velocity": 85.5
        },
        "feature_scores": {
            "keystroke_anomaly": 0.82,
            "network_activity": 0.415,
            "focus_anomaly": 0.78,
            "app_switching": 0.60,
            "cpu_activity": 0.824,
            "voice_stress": 0.65,
            "keystroke_error": 0.70,
            "mouse_inactivity": 0.0
        }
    },
    
    "activity_snapshot": {
        "active_application": "Chrome - Google Search",
        "focus_score": 0.22,
        "keystroke_variance": 0.82,
        "network_bytes_total": 8700000,
        "cpu_usage": 91.2,
        "app_switches": 12,
        "stress_indicators": {
            "keystroke_erraticism": 0.82,
            "mouse_velocity": 85.5,
            "voice_sentiment": -0.65,
            "calculated_stress_level": 0.78
        }
    },
    
    "explanation": {
        "risk_indicators": [
            "Highly erratic keystroke pattern (variance: 82%)",
            "Significant network activity (spike to 4.85 MB)",
            "Very low focus score (22%)",
            "Excessive app switching (12 switches)",
            "Significant voice stress detected",
            "Very high CPU usage (91%)"
        ],
        "normal_indicators": [],
        "detected_patterns": [
            {
                "pattern": "Biometric Drift",
                "severity": "high",
                "description": "Keystroke pattern changed significantly"
            },
            {
                "pattern": "Focus Collapse",
                "severity": "high",
                "description": "Focus score dropped suddenly"
            },
            {
                "pattern": "Network Anomaly",
                "severity": "high",
                "description": "Network activity spiked significantly"
            }
        ]
    },
    
    "severity_justification": "CRITICAL: Multiple high-severity patterns detected: Biometric Drift, Focus Collapse, Network Anomaly. Possible impersonation or data exfiltration.",
    
    "server_analysis_needed": True
}

# Save to file
# ./flag_data/exam-123/a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6.json
```

---

## ✅ Step 8: Return Result to Client

```python
result = {
    "timestamp": "2025-10-26T14:30:45Z",
    "processed": True,
    "risk_level": "critical",
    "suspicious_score": 0.652,
    "patterns_detected": 3,
    "should_flag": True,
    "flag_file": "./flag_data/exam-123/a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6.json",
    "flag_id": "a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6",
    "recommendation": "FLAG_IMMEDIATE - Stop exam and flag for review"
}

# Client sees:
print(f"🚨 FLAGGED: {result['risk_level']}")
print(f"   Score: {result['suspicious_score']:.1%}")
print(f"   Patterns: {result['patterns_detected']}")
print(f"   File: {result['flag_file']}")
print(f"   Action: {result['recommendation']}")

# Output:
# 🚨 FLAGGED: critical
#    Score: 65.2%
#    Patterns: 3
#    File: ./flag_data/exam-123/a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6.json
#    Action: FLAG_IMMEDIATE - Stop exam and flag for review
```

---

## 📤 Step 9: Send to Server

```python
# Client sends flag file to server

POST /api/flagged-activity/exam-123/alice-456

Body: (the entire flag_file JSON from step 7)

# Server receives it
# Server runs Gemini analysis
# Server creates comprehensive report
# Server broadcasts to professor dashboard

Professor sees:
🚨 CRITICAL ALERT - Alice Chen
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Client Assessment:
• Risk: CRITICAL (65.2%)
• Patterns: Biometric Drift, Focus Collapse, Network Anomaly
• Active App: Chrome - Google Search (NOT the exam!)

Evidence:
• Keystrokes suddenly changed (3.37x difference)
• Focus collapsed from 76% to 28%
• Network spike (4.85 MB in one packet)
• Very high CPU (91%)
• App switched 12 times

Recommendation: IMMEDIATE ACTION REQUIRED
```

---

## 🎯 Time Breakdown

```
Step 1: Add to history       0.1 ms
Step 2: Detect patterns      0.8 ms
Step 3: Extract features     0.3 ms
Step 4: Apply weights        0.4 ms
Step 5: Apply multiplier     0.1 ms
Step 6: Classify             0.1 ms
Step 7: Generate flag file   2.0 ms
━━━━━━━━━━━━━━━━━━━━━━━
TOTAL:                       ~4.0 ms ✓

All done in < 5ms!
```

---

## 🔑 Key Insights

### Why This Package Was Flagged as CRITICAL

1. **Biometric Drift** (0.94 confidence)
   - Keystroke variance jumped from 0.22 → 0.74 (3.4x increase)
   - Indicates different person typing OR extreme stress

2. **Focus Collapse** (0.96 confidence)
   - Focus dropped from 0.76 → 0.29 in seconds
   - Indicates loss of concentration OR attention switched

3. **Network Spike** (0.88 confidence)
   - 4.85 MB sent in single package (4.66x normal)
   - Indicates downloading/uploading suspicious files

4. **Multiple High-Severity Patterns**
   - 3 different indicators all screaming "suspicious"
   - Pattern multiplier boosted score 2.5x
   - Final score pushed over 0.80 → CRITICAL

### Why It COULD Be False Alarm

- Student got stressed during hard question
- System crash made them restart browser (network spike)
- Changed seating position (new keyboard, mouse)
- Accessibility device started (explains erratic input)

### Why Gemini Analysis Needed

Server sends flag to Gemini with all this context.

Gemini considers:
- Historical pattern for this student (usually calm)
- Question difficulty (was it particularly hard?)
- Time in exam (end time = higher stress normal)
- Similar flags from other students (cheating trend?)

Gemini might conclude:
- "CONFIRMED CHEATING" - different person took over
- "FALSE ALARM" - student just very stressed
- "INVESTIGATE" - suspicious but not conclusive

---

**This entire process takes < 5ms per package!**
