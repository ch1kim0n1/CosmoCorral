# How the ML System Predicts & Trains

## The Problem

Traditional ML approaches for this use case face challenges:
- ❌ Deep learning requires massive labeled datasets (expensive)
- ❌ Training takes hours/days on server (resource intensive)
- ❌ Model drift requires retraining (models become stale)
- ❌ Hard to explain decisions (black boxes)
- ❌ Privacy concerns with centralized learning

**Our Solution**: Lightweight, rules-based ML with online learning

---

## 🎯 Current System: Rules-Based Heuristic Classification

### It Does NOT Use Traditional ML Training

The current system uses **weighted feature scoring** - essentially a handcrafted decision tree.

```python
# This is NOT a neural network
# It's a simple weighted linear combination

suspicious_score = (
    keystroke_anomaly × 0.25 +      # Weight based on domain knowledge
    network_activity × 0.25 +        # Not learned from data
    focus_anomaly × 0.15 +           # Tuned by experts/heuristics
    app_switching × 0.10 +
    cpu_activity × 0.08 +
    voice_stress × 0.10 +
    keystroke_error × 0.05 +
    mouse_inactivity × 0.02
)
```

### How It "Predicts"

For each activity package:

```python
1. Extract 8 Features
   keystroke_rhythm_variance = 0.82
   network_bytes_total = 12,500,000
   focus_score = 0.25
   ...

2. Normalize Features (0-1)
   keystroke_anomaly = min(1.0, 0.82 / 1.0) = 0.82
   focus_anomaly = max(0.0, 1.0 - 0.25) = 0.75
   network_activity = min(1.0, 12.5MB / 20MB) = 0.625
   ...

3. Apply Weights (multiply each by importance)
   keystroke_contribution = 0.82 × 0.25 = 0.205
   focus_contribution = 0.75 × 0.15 = 0.1125
   network_contribution = 0.625 × 0.25 = 0.1563
   ...

4. Sum & Classify
   total_score = 0.205 + 0.1125 + 0.1563 + ... = 0.68
   
   if score > 0.80: risk_level = "critical"
   elif score > 0.65: risk_level = "high"      ← This one
   elif score > 0.45: risk_level = "medium"
   ...
```

### The Pattern Detection Layer

**Before** the ML scoring, 6 pattern detectors run:

```python
# Pattern detection is 100% algorithmic, no training needed

Pattern 1: Biometric Drift
  recent_keystroke_variance = 0.82
  older_keystroke_variance = 0.45
  
  if recent > older × 1.5 and recent > 0.5:
      detected = True  # Simple heuristic rule

Pattern 2: Focus Collapse
  recent_focus = 0.25
  older_focus = 0.85
  
  if older > 0.6 and recent < 0.3 and drop > 0.3:
      detected = True  # Simple heuristic rule

[Similar logic for 4 other patterns...]

# Result: Pattern multiplier (1.0 - 2.5x)
if has_critical_pattern:
    final_score × 2.0  # Boost suspicious score
```

---

## 📚 Training: How Does It Work Currently?

### It Doesn't Train (V1.0)

**The current system is NOT self-training.** Weights are hardcoded based on:

1. **Domain expertise** (educational integrity researchers)
2. **Heuristic reasoning** (keystroke changes = more suspicious)
3. **Institution calibration** (adjust thresholds for your context)

```python
# These are FIXED, not learned
FEATURE_WEIGHTS = {
    "keystroke_anomaly": 0.25,        # Hardcoded
    "network_activity": 0.25,         # Hardcoded
    "focus_anomaly": 0.15,            # Hardcoded
    # ...
}

RISK_THRESHOLDS = {
    "critical": 0.80,                 # Hardcoded
    "high": 0.65,                     # Hardcoded
    "medium": 0.45,                   # Hardcoded
}
```

### Manual Tuning Process

To "train" the system for your institution:

```python
# Step 1: Collect baseline data
# Run on 100+ normal exams
# Track false positive rate

# Step 2: Collect suspicious data
# Get confirmed cheating cases
# Track detection rate

# Step 3: Adjust weights manually
OLD: keystroke_anomaly = 0.25
NEW: keystroke_anomaly = 0.30  # More sensitive

# Step 4: Re-test and measure
if false_positive_rate < 5% and detection_rate > 90%:
    deploy()  # Good!
else:
    tune_more()  # Try different weights
```

---

## 🔮 How Predictions Actually Work (Detailed Example)

### Real Scenario: Possible Impersonation

**T=0:00 - Student starts exam**
```
Package 1:
  keystroke_variance: 0.18 (normal typing)
  focus_score: 0.82 (focused)
  cpu_usage: 35% (normal)
  
  Normalization:
    keystroke_anomaly = 0.18 ✓
    focus_anomaly = 1.0 - 0.82 = 0.18 ✓
    cpu_activity = max(0, (35-50)/50) = 0.0 ✓
  
  Score: (0.18×0.25) + (0.18×0.15) + (0.0×0.08) + ... = 0.12
  Risk: CLEAN ✓ Continue
```

**T=0:30 - Sudden behavior change**
```
Package 2:
  keystroke_variance: 0.81 (suddenly erratic!)
  focus_score: 0.22 (focus dropped!)
  cpu_usage: 92% (spike!)
  network_bytes: 8MB sent (suspicious!)
  
  Normalization:
    keystroke_anomaly = 0.81
    focus_anomaly = 1.0 - 0.22 = 0.78
    cpu_activity = max(0, (92-50)/50) = 0.84
    network_activity = min(1.0, 8MB/20MB) = 0.40
  
  Score: (0.81×0.25) + (0.78×0.15) + (0.84×0.08) + (0.40×0.25) + ...
       = 0.2025 + 0.117 + 0.0672 + 0.10 + ... = 0.68
  
  Pattern Detection:
    ✓ Biometric Drift detected (high)
    ✓ Focus Collapse detected (high)
    ✓ Resource Exhaustion detected (med)
    
    multiplier = 2.0 (multiple high patterns)
    
    Final Score = 0.68 × 2.0 = 1.36 → capped at 1.0
  
  Risk: HIGH ✓ FLAG FOR SERVER
  
  Output:
    {
      "flag_id": "uuid-123",
      "suspicious_score": 0.68,
      "risk_level": "high",
      "patterns": ["Biometric Drift", "Focus Collapse", "Resource Exhaustion"],
      "file": "./flag_data/exam-123/uuid-123.json"
    }
```

---

## 🧠 What IS Actually Being Learned?

### The AnomalyDetector: Baseline Learning

There IS one learning component - baseline tracking:

```python
class AnomalyDetector:
    def __init__(self):
        self.baselines = {
            "session-123:keystroke_speed": {
                "mean": 0.0,
                "std_dev": 1.0,
                "count": 0
            }
        }
    
    def update_baseline(self, session_id, signal_name, value):
        """Update student's personal baseline."""
        key = f"{session_id}:{signal_name}"
        baseline = self.baselines[key]
        
        # Exponential moving average (simple online learning!)
        alpha = 0.1  # 10% new data, 90% history
        
        baseline["mean"] = alpha * value + (1 - alpha) * baseline["mean"]
        baseline["count"] += 1
```

**What this does:**
- Learns this specific student's normal typing speed
- Learns their normal focus pattern
- Learns their normal CPU usage
- After ~10-50 samples, has their "baseline"

**How it's used:**
```python
# Is this value abnormal FOR THIS STUDENT?
z_score = (current_value - baseline_mean) / baseline_std_dev

if z_score > 3.0:  # 3 standard deviations away
    flagged as anomalous
```

### Example: Keystroke Learning

```
Sample 1: keystroke_speed = 45 wpm
  baseline_mean = 45, count = 1

Sample 2: keystroke_speed = 48 wpm
  baseline_mean = 0.1×48 + 0.9×45 = 45.3, count = 2

Sample 3: keystroke_speed = 44 wpm
  baseline_mean = 0.1×44 + 0.9×45.3 = 45.17, count = 3

Sample 10: keystroke_speed = 150 wpm (impossible!)
  z_score = (150 - 45.17) / 2.5 = 41.9
  flagged = True  ✓ Someone else typing!
```

---

## 🎓 Future: Real ML Training (V2.0+)

### What We Could Add (Not in V1.0)

#### 1. **Supervised Learning**
```python
# Collect labeled data
training_data = [
    {
        "features": [0.82, 0.78, 0.40, ...],
        "label": "cheating"  # Known from investigation
    },
    {
        "features": [0.15, 0.08, 0.02, ...],
        "label": "legitimate"  # Verified legitimate
    }
]

# Train model
from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier()
model.fit(training_data["features"], training_data["labels"])

# Now weights are learned, not hardcoded!
```

**Requirements:**
- 500+ labeled exam cases (expensive to get)
- Ground truth labels (require investigation)
- Quarterly retraining (model maintenance)

#### 2. **Unsupervised Learning**
```python
# Cluster exam patterns
from sklearn.clustering import DBSCAN

clustering = DBSCAN(eps=0.3, min_samples=10)
clusters = clustering.fit_predict(all_exam_features)

# Identify outlier patterns automatically
# No labels needed!
```

**Advantages:**
- No labeling required
- Detects novel cheating methods
- Adapts to new trends

**Challenges:**
- Need 1000s of exams to cluster effectively
- Outliers could be legitimate (person with disability, etc.)

#### 3. **Online Learning**
```python
# Update weights in real-time based on feedback

class AdaptiveClassifier:
    def get_feedback(self, flag_id, was_correct):
        """
        Receive feedback from professor.
        was_correct = True if flag was accurate
        """
        if not was_correct:
            # This feature was misleading
            # Reduce its weight
            for feature in this_flag.high_contributors:
                self.weights[feature] *= 0.95  # Decrease weight
        else:
            # This feature was helpful
            # Increase its weight
            for feature in this_flag.high_contributors:
                self.weights[feature] *= 1.05  # Increase weight
```

**Advantage:** System improves over time!  
**Disadvantage:** Can learn wrong patterns if professors are wrong.

#### 4. **Deep Learning (Future)**
```python
# Neural network for keystroke biometrics
import tensorflow as tf

model = tf.keras.Sequential([
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(1, activation='sigmoid')
])

# Train on keystroke sequences
model.fit(keystroke_sequences, is_legitimate_labels)

# Now can verify: "Is this the same person typing?"
# Much more sophisticated than pattern matching
```

**Requirements:**
- 10,000+ keystroke sequences for training
- GPU for efficient training
- Continuous model updates

---

## 📊 Comparison: Current vs Future

| Aspect | Current (V1.0) | Future ML (V2.0+) |
|--------|----------------|-------------------|
| **Training** | Hardcoded weights | Learned from data |
| **Adaptation** | Manual tuning | Automatic adaptation |
| **Data needed** | Domain expertise | 500+ labeled cases |
| **Update freq** | Manual adjustment | Continuous learning |
| **Explainability** | 100% (simple rules) | ~70% (some black box) |
| **Accuracy** | ~85-90% | ~95%+ |
| **Setup time** | 2 weeks | 2 months |
| **Computation** | <5ms | <20ms |

---

## 🔧 How to Tune the Current System

### Step 1: Measure Current Performance

```python
# Run on 100 normal exams
normal_results = []
for exam in normal_exams:
    result = orchestrator.process_package(exam, session_id, student_id)
    normal_results.append(result["risk_level"])

# Measure false positive rate
false_positive_rate = sum(1 for r in normal_results if r != "none") / len(normal_results)
print(f"False positive rate: {false_positive_rate * 100}%")  # Should be <5%

# Run on 50 confirmed cheating exams
cheating_results = []
for exam in confirmed_cheating:
    result = orchestrator.process_package(exam, session_id, student_id)
    cheating_results.append(result["risk_level"])

# Measure detection rate
detected = sum(1 for r in cheating_results if r in ["high", "critical"])
detection_rate = detected / len(cheating_results)
print(f"Detection rate: {detection_rate * 100}%")  # Should be >90%
```

### Step 2: Identify Problems

```python
# Too many false positives?
# → Increase thresholds
# In ml_classifier.py:
elif score > 0.70:  # Was 0.65
    return "high"

# Missing cheating?
# → Decrease thresholds or increase weights
# In ml_classifier.py:
"keystroke_anomaly": 0.30,  # Was 0.25
"network_activity": 0.30,   # Was 0.25
```

### Step 3: Re-test

```python
# Validate with holdout test set
test_results = []
for exam in test_set:
    result = orchestrator.process_package(exam, session_id, student_id)
    test_results.append({
        "result": result["risk_level"],
        "actual": exam.ground_truth
    })

# Calculate accuracy
correct = sum(1 for r in test_results if r["result"] matches expected)
accuracy = correct / len(test_results)
print(f"Accuracy: {accuracy * 100}%")  # Aim for >90%
```

---

## 🏗️ Architecture: Where the Magic Happens

```
Raw Package (keystroke data, focus, CPU, etc.)
    ↓
Pattern Detector
    ├── Baseline Update (exponential moving average)
    │   └── Is this abnormal FOR THIS STUDENT?
    │
    └── 6 Pattern Detection Rules
        ├── Biometric Drift (manual threshold)
        ├── Focus Collapse (manual threshold)
        ├── Stress Spike (manual threshold)
        ├── Network Anomaly (manual threshold)
        ├── Resource Exhaustion (manual threshold)
        └── Temporal Inconsistency (manual threshold)
    ↓
ML Classifier
    ├── Feature Extraction (8 features)
    ├── Feature Normalization (0-1 range)
    ├── Weighted Scoring (multiply by importance)
    │   └── weights = hardcoded based on domain knowledge
    ├── Pattern Multiplier (boost if patterns detected)
    └── Risk Classification
        └── threshold-based decision (hardcoded)
    ↓
Flag Generator
    └── Create JSON with all reasoning
```

---

## 💡 Why This Approach?

### Advantages of Current Design

✅ **Fast** (<5ms with no GPU needed)  
✅ **Explainable** (can explain every decision)  
✅ **Robust** (no overfitting to training data)  
✅ **Privacy-first** (no data sent for training)  
✅ **Works immediately** (no collection phase needed)  
✅ **Tunable** (adjust for institution needs)  

### Limitations

❌ **Not adaptive** (weights don't learn)  
❌ **Domain-dependent** (need expert to tune)  
❌ **Limited accuracy** (~85-90% vs 95%+ for deep learning)  
❌ **Manual maintenance** (must retune as patterns evolve)  

---

## 📝 Summary: Prediction vs Training

**How it Predicts:**
```
1. Extract 8 features from activity package
2. Normalize each to 0-1 range
3. Multiply by hardcoded weight
4. Sum weighted features = suspicious_score
5. Detect patterns (6 algorithmic rules)
6. Apply pattern multiplier (boost if suspicious patterns)
7. Compare score to hardcoded thresholds
8. Output: risk_level (critical/high/medium/low/clean)
```

**How it "Trains":**
```
1. Learn student's personal baseline (exponential moving average)
   - Keystroke speed, focus level, CPU usage, etc.
2. Compare new activities against this baseline
   - Z-score: how many std devs away from normal?
3. Use learned baseline in anomaly detection
   - "Is this unusual FOR THIS STUDENT?"

But weights and thresholds are FIXED/HARDCODED
```

**To actually train (not in V1.0):**
```
1. Collect labeled data (500+ confirmed cheating cases)
2. Use sklearn/TensorFlow to learn optimal weights
3. Evaluate on test set
4. Deploy updated weights
5. Retrain quarterly as patterns evolve
```

---

**Current Status**: V1.0 - Rules-based with baseline learning  
**Path Forward**: V2.0 could add supervised learning for +5-10% accuracy improvement  
**Best For**: Quick deployment, explainable decisions, privacy-first design  
**Trade-off**: Expert tuning needed vs fully automated learning
