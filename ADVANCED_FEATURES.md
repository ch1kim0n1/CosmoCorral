# Space Cowboy: Advanced Features Guide (Tier 1-7)

## The Shift: From Surveillance → Wellness Coaching

The original system detects **problems**. These 7 tiers transform it into a system that **helps users succeed**.

**Old Model**: "Alert: cheating detected"
**New Model**: "Your focus is dropping - take a 2-min break and you'll recover +15%"

---

## 🤖 Tier 1: Adaptive Coaching Mode

**Purpose**: Real-time proactive suggestions based on detected state

### How It Works

Every 5 seconds, the coaching engine analyzes:
- Focus trend (improving? declining?)
- Stress level (from voice + keystrokes + focus)
- Activity duration (have you been working too long?)
- Typing speed (are you tense?)
- Mouse movement (physical tension?)

### Examples

**Scenario 1: Declining Focus + High Stress**
```
System detects: Focus 0.8 → 0.6 → 0.4, stress rising
Coaching tip: "Take a 2-minute break - your focus is dropping"
Confidence: 92%
Impact: Estimated +15% focus recovery
Category: Wellness
```

**Scenario 2: After 3+ Hours of Intense Work**
```
System detects: 180+ seconds of sustained focus (0.7+)
Coaching tip: "Time for lunch - you've been focused for 3+ hours!"
Impact: Recharge mental energy, +25% afternoon productivity
```

**Scenario 3: Very Fast Typing**
```
System detects: Keystroke rate 120+/sec (feverish pace)
Coaching tip: "You're typing very fast - slow down and breathe"
Impact: Reduce errors by 20%
Action: Suggest 30-second breathing exercise
```

### When It Helps
- ✅ Prevents burnout by detecting fatigue early
- ✅ Reduces mistakes by suggesting pacing
- ✅ Maintains productivity through strategic breaks
- ✅ Shifts from "monitor" to "coach" mentality

---

## 🧠 Tier 2: Flow State Detection (FocusRing)

**Purpose**: Detect & quantify when users enter "deep work mode"

### The Science

Flow state is characterized by:
- **Consistent keystroke rhythm** (not erratic)
- **Smooth mouse movement** (not jerky/tense)
- **Minimal app switching** (focused on one task)
- **High focus score** (from client metrics)
- **Steady interaction** (predictable patterns)

### How It Works

```python
FlowScore = 
    keystroke_consistency × 0.3 +
    mouse_smoothness × 0.2 +
    app_focus × 0.25 +
    reported_focus × 0.25
```

### States Detected

| State | Score | Interpretation |
|-------|-------|-----------------|
| **Deep Flow** | 0.85+ | Perfect for deep work - minimize distractions |
| **Focused** | 0.7-0.84 | Good focus - maintain momentum |
| **Scattered** | 0.3-0.69 | Distracted - consider breaks |
| **Stressed** | High variance + low score | Anxiety - suggest relaxation |
| **Tired** | Low velocity + low score | Fatigued - suggest rest |

### Real Example

```json
{
  "flow_state": "deep_flow",
  "flow_score": 0.92,
  "signals": {
    "keystroke_rhythm": 0.95,  // Very consistent!
    "mouse_smoothness": 0.88,  // Smooth movements
    "app_focus": 0.95,         // No switching
    "focus_metric": 0.91,      // Very focused
    "interaction_density": 0.91 // Steady pace
  },
  "interpretation": "User is in deep work mode. Excellent focus.",
  "recommendations": [
    "✓ Auto-silence all notifications",
    "✓ Hide chat/social media",
    "✓ Show 'Deep Work - Do Not Disturb' indicator",
    "✓ Block distracting websites"
  ]
}
```

### When It Helps
- ✅ Respects deep work - don't interrupt
- ✅ Shows others "do not disturb" status
- ✅ Auto-blocks distractions during flow
- ✅ Tracks flow time for productivity insights

---

## 😊 Tier 3: Empathy Engine - Emotion Recognition + Wellness

**Purpose**: Detect emotional states and suggest wellness interventions

### Signals Analyzed

1. **Voice Sentiment** (from ElevenLabs)
   - Positive sentiment = confidence
   - Negative sentiment = stress/frustration

2. **Keystroke Erraticism**
   - Low variance = calm & focused
   - High variance = anxious/rushed

3. **Physical Tension**
   - Mouse velocity indicates hand tension
   - Very fast/jerky = stressed

4. **Focus Level**
   - Sustained focus = engaged
   - Dropping focus = fatigued/frustrated

### Emotions Detected

| Emotion | Indicators | Suggestions |
|---------|-----------|------------|
| **Confident** | +sentiment, low variance, high focus | 🚀 Keep momentum! Tackle hard tasks |
| **Stressed** | -sentiment, high variance, tense | 🧘 Breathing exercise, 10-min break |
| **Frustrated** | -sentiment, low focus | 🔄 Switch to easier task, celebrate win |
| **Fatigued** | Low mouse velocity, low focus | 😴 Rest, caffeine, or task switch |

### Real Example

```json
{
  "emotion": "stressed",
  "wellbeing_score": 42,  // 0-100 scale
  "confidence": 0.78,
  "indicators": {
    "voice_sentiment": -0.6,
    "keystroke_erraticism": 0.72,
    "physical_tension": 0.68
  },
  "suggestions": [
    "🧘 Take 5 minutes of guided breathing",
    "🚶 Take a 10-minute walk outside",
    "💧 Drink water and step away from screen",
    "📞 Consider talking to someone"
  ],
  "resources": {
    "5_min_breathing": "https://example.com/breathing",
    "stress_relief": "https://example.com/stress",
    "wellness_checkin": "https://example.com/checkin"
  }
}
```

### When It Helps
- ✅ Privacy-first wellness (no surveill, helping!)
- ✅ Early intervention before burnout
- ✅ Personalized support suggestions
- ✅ Links to wellness resources

---

## 🏆 Tier 4: Productivity Benchmarks - Anonymous Leaderboards

**Purpose**: Motivation without judgment - see how you compare to peers

### How It Works

Compare each student to anonymized peer data:

```python
peers = [0.75, 0.68, 0.82, 0.71, 0.79, 0.65, 0.88]
student_score = 0.82

percentile = 78th  # 78% of peers score lower
```

### Real Example

```json
{
  "student_score": 0.82,
  "class_average": 0.71,
  "top_performer": 0.94,
  "percentile": 78,
  "rank": "🥈 Top 25% - Excellent!",
  "interpretation": "You're 11% better focused than peers!",
  "improvement_opportunity": "You're doing well! Small refinements: eliminate one distraction source"
}
```

### Dashboard Display

```
📊 Your Focus vs. Class
━━━━━━━━━━━━━━━━━━━━━━━━━━
You:       ████████░░ 0.82
Average:   ███████░░░ 0.71
Top:       █████████░ 0.94
↓
You're in top 22% of class! 🥈
11% better focused than peers
```

### Ranking System

| Percentile | Rank | Message |
|-----------|------|---------|
| 90+% | 🥇 Top 10% | Exceptional! |
| 75-89% | 🥈 Top 25% | Excellent! |
| 50-74% | 🥉 Top 50% | Good! |
| 25-49% | 📈 Below Avg | Room to grow |
| <25% | ⚠️ Needs Improvement | Let's work together |

### When It Helps
- ✅ Healthy competition (not creepy)
- ✅ Motivation without pressure
- ✅ Personalized improvement tips
- ✅ Peer learning insights

---

## 🚨 Tier 5: At-Risk Alerts - Predictive Early Warning

**Purpose**: Catch struggling students BEFORE they fail

### Trends Analyzed

Track over 2 minutes (24 packages):
1. **Declining Focus Trend** (focus scores dropping)
2. **Increasing Stress** (stress markers rising)
3. **Erratic Typing** (keystroke variance increasing)
4. **Rising Errors** (keystroke mistakes increasing)

### Risk Calculation

```
Risk factors detected:
  - Declining focus: ✓
  - High stress: ✓
  - Erratic typing: ✓
  
Confidence = 3 factors × 0.25 = 0.75
Risk Level = HIGH (>0.85) or MEDIUM (0.75+)
```

### Real Example

```json
{
  "risk_level": "HIGH",
  "confidence": 0.92,
  "factors": [
    "declining_focus",
    "high_stress", 
    "erratic_typing",
    "increasing_errors"
  ],
  "intervention": "Schedule 1-on-1 check-in with student",
  "draft_message": "Hi, I noticed you might be struggling with declining_focus, high_stress, erratic_typing. Would you like to talk? - Your Teacher",
  "resources": [
    "📚 Study tips guide",
    "😊 Wellness resources",
    "🎯 Goal-setting worksheet"
  ]
}
```

### Teacher Dashboard Alert

```
🚨 MEDIUM RISK - Sarah Chen
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Factors: Declining focus, high stress, erratic typing
Confidence: 92%

Suggestion: Reach out for a check-in
Draft Message: [pre-written, ready to send]

Resources to share:
- Study tips guide
- Wellness resources  
- Goal-setting worksheet
```

### When It Helps
- ✅ Catches problems early (preventive, not reactive)
- ✅ Data-backed intervention recommendations
- ✅ Pre-written support messages
- ✅ Connects students to resources

---

## 🔍 Tier 6: Context Understanding - Know What They're Actually Doing

**Purpose**: Understand **quality** of work, not just time spent

### App-to-Context Mapping

```python
APP_CONTEXTS = {
    "coding": {
        "apps": ["vscode", "visualstudio", "pycharm"],
        "expects": {
            "focus": 0.7+,
            "keystroke_rate": 40+,
            "app_switches": <3
        }
    },
    "writing": {
        "apps": ["word", "docs", "notion"],
        "expects": {
            "focus": 0.65+,
            "keystroke_rate": 30+,
            "typing": "steady"
        }
    },
    "researching": {
        "apps": ["chrome", "firefox"],
        "expects": {
            "focus": 0.5+,
            "app_switches": 5+,
            "keystroke_rate": <20
        }
    },
    "video_conferencing": {...},
    "presentation": {...},
    "data_analysis": {...}
}
```

### Real Example

```json
{
  "context": "coding",
  "confidence": 0.87,
  "active_app": "vscode",
  "quality_metrics": {
    "focus_level": 0.85,
    "intensity": "high",
    "consistency": "high",
    "productivity_estimate": "strong"
  },
  "interpretation": "Strong coding session - excellent focus and consistency!",
  "tips": [
    "🔇 Silence notifications - deep focus needed",
    "🎯 Consider 50-minute focus sprints",
    "📝 Document complex sections as you go"
  ]
}
```

### Dashboard Shows

```
🖥️ Current Activity: Coding (VSCode)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Focus: 0.85 ████████░░ Excellent
Intensity: High (85 keys/sec)
Consistency: High (smooth typing)

→ Strong coding session!
  Excellent focus and consistency

Suggestions:
✓ Silence notifications
✓ Consider 50-minute sprints
✓ Document as you go
```

### When It Helps
- ✅ Understand **what** they're doing, not just **that** they're working
- ✅ Context-aware quality assessment
- ✅ Tailored tips for each activity type
- ✅ Distinguishes "busy" from "productive"

---

## 👥 Tier 7: Study Pods - Synchronized Group Focus Sessions

**Purpose**: Group focus with social accountability

### How Study Pods Work

```
1. Create pod: "CS200 Study Group"
2. Invite: Sarah, John, Maya (3 members)
3. Duration: 50 minutes
4. Start session

System tracks each member's focus in real-time
Shows group status and encouragement
```

### Real-Time Pod Status

```json
{
  "pod_id": "pod-cs200-001",
  "pod_name": "CS200 Study Group",
  "duration_remaining_min": 23,
  "members": [
    {
      "name": "Sarah",
      "status": "focused",
      "focus_score": 0.85,
      "emoji": "🟢"
    },
    {
      "name": "John",
      "status": "okay",
      "focus_score": 0.62,
      "emoji": "🟡",
      "encouragement": "Keep focused! 💪"
    },
    {
      "name": "Maya",
      "status": "struggling",
      "focus_score": 0.28,
      "emoji": "🔴",
      "encouragement": "You can do it! 💪 Take a quick break if needed"
    }
  ],
  "pod_average_focus": 0.58,
  "group_energy": "💪 Good group momentum",
  "encouragement": "Come on team - you've got this! 💪"
}
```

### Dashboard Display

```
📚 Study Pod: CS200 Study Group
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏱️ Time Remaining: 23 min

Members:
  🟢 Sarah    Focus: 0.85  ████████░░
  🟡 John     Focus: 0.62  ██████░░░░  "Keep focused! 💪"
  🔴 Maya     Focus: 0.28  ███░░░░░░░  "Take a quick break! 💪"

Pod Average: 0.58
Group Energy: 💪 Good momentum
Message: Come on team - you've got this! 💪
```

### Group Energy Classification

| Average Focus | Energy | Message |
|---------------|--------|---------|
| 0.75+ | 🔥 Excellent | Everyone is focused! |
| 0.6-0.74 | 💪 Good | Great momentum! |
| 0.4-0.59 | ⚖️ Mixed | Some struggling |
| <0.4 | ⚠️ Low | Take a 2-min break |

### When It Helps
- ✅ Social accountability (group pressure + support)
- ✅ Real-time peer support ("You can do it!")
- ✅ Visible progress (see everyone's focus)
- ✅ Breaks fatigue (gamified with emojis)
- ✅ Group motivation (compare as team, not individuals)

---

## 🎯 How All 7 Tiers Work Together

### Example: Sarah's 50-Minute Coding Session

**T=0:00 - Session Starts**
```
Tier 2 (Flow): Flow score 0.45 - scattered
Tier 1 (Coaching): "Close those tabs first!"
Tier 7 (Pod): Joins CS200 pod, 🟡 status
```

**T=5:00 - Getting Focused**
```
Tier 2 (Flow): Flow score 0.72 - focused
Tier 3 (Empathy): Emotion = focused, wellbeing 72/100
Tier 6 (Context): Strong coding session detected
Tier 1 (Coaching): "You're in the zone! Silence notifications"
```

**T=15:00 - Deep Work**
```
Tier 2 (Flow): Flow score 0.91 - DEEP FLOW
Tier 7 (Pod): Status 🟢 focused (everyone focused!)
Group encouragement: "🌟 Amazing group focus!"
```

**T=25:00 - Fatigue Starts**
```
Tier 3 (Empathy): Wellbeing dropping to 55/100
Tier 1 (Coaching): "Take a 2-min break? You're at 25 min..."
```

**T=30:00 - Takes Break, Returns**
```
Tier 3 (Empathy): Wellbeing back to 70/100
Tier 1 (Coaching): "Nice break! Ready to finish strong?"
```

**T=50:00 - Session Ends**
```
Tier 4 (Benchmarks): "Sarah, your focus (0.78) is 9% better than class!"
Tier 5 (At-Risk): Not flagged - staying healthy
Tier 7 (Pod): Pod average 0.81 - excellent session!

Summary:
- 50 min focused work
- Peak flow: 0.91
- No at-risk factors
- Top 25% peer comparison
- Great group session!
```

---

## 🚀 Implementation Summary

### For Students
- Real-time coaching (not judgment)
- Wellness suggestions (not demands)
- Peer comparison (motivation, not pressure)
- Group accountability (social support)
- Emotion recognition (someone cares)

### For Teachers
- Early warning system (catch problems early)
- Context understanding (meaningful work assessment)
- Peer insights (identify top/struggling students)
- Automated suggestions (draft emails, resources)
- Group dynamics (monitor study pods)

### For Administrators
- Productivity metrics (data-driven decisions)
- Wellness programs (see who needs support)
- Resource allocation (where to focus support)
- Success tracking (measure interventions)

---

## 💡 Why This Matters

**Before (Surveillance Model)**:
- "Your focus dropped to 0.2 - flagged for cheating"
- Student feels watched and stressed

**After (Wellness Model)**:
- "Your focus dropped to 0.2 - take a 2-min break?"
- "You could recover 15% focus with a walk"
- "Your peer John is also struggling - want to join his study pod?"
- Student feels supported and empowered

---

## 📊 Feature Activation

Add to `server/main.py`:

```python
from advanced_features import AdvancedFeaturesCoordinator

# Initialize
coordinator = AdvancedFeaturesCoordinator()

# In package handler:
advanced_analysis = await coordinator.process_with_advanced_features(package, anomalies)

# Broadcast to dashboard
await ws.send(json.dumps({
    "type": "AdvancedAnalysis",
    "data": advanced_analysis
}))
```

---

## 📈 System Evolution

| Stage | Focus | Tiers |
|-------|-------|-------|
| **v1** | Cheating detection | Anomalies + Gemini |
| **v2** | Coaching + wellness | Tiers 1-3 |
| **v3** | Peer comparison | Tier 4 |
| **v4** | Early warning | Tier 5 |
| **v5** | Context understanding | Tier 6 |
| **v6** | Group collaboration | Tier 7 |
| **v7** | Full ecosystem | All tiers integrated |

---

**Everything is implemented in `server/advanced_features.py` and ready to use!** 🚀
