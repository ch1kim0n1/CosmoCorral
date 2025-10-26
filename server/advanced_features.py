"""
Advanced Features Module: Tier 1-7 AI-Powered Enhancements

Shifts from "surveillance" to "wellness + performance optimization"
Each tier builds on previous anomaly detection to provide proactive support.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import statistics

logger = logging.getLogger(__name__)

# ============================================================================
# TIER 1: ADAPTIVE COACHING MODE 🤖
# ============================================================================

class CoachingTip(Enum):
    """Real-time coaching suggestions based on detected state."""
    TAKE_BREAK = "Take a 2-minute break - your focus is dropping"
    HYDRATE = "Hydrate! Your stress markers are increasing"
    STEP_OUTSIDE = "Step outside for 5 minutes - refresh your mind"
    SWITCH_TASK = "Consider switching to a different task - you seem stuck"
    SLOW_DOWN = "You're typing very fast - slow down and breathe"
    STRETCH = "Stretch! Your mouse velocity suggests tension"
    FOCUS_TIME = "Block distractions - you're in the zone!"
    VERIFY_CONNECTION = "Check your network - unusual activity detected"
    TAKE_NOTES = "Document your thoughts - you're switching apps a lot"
    LUNCH_BREAK = "Time for lunch - you've been focused for 3+ hours!"


class AdaptiveCoach:
    """Proactive coaching based on real-time metrics."""
    
    def __init__(self):
        self.session_history: Dict[str, List[Dict]] = {}  # session_id -> history
        self.tip_frequency: Dict[str, int] = {}  # Avoid tip fatigue
    
    def analyze_and_coach(self, package: Dict, anomalies: List[Dict]) -> Optional[Dict]:
        """
        Analyze package and suggest real-time coaching tips.
        
        Returns: {
            "suggestion": "Take a 2-minute break - your focus is dropping",
            "confidence": 0.85,
            "estimated_impact": "Estimated +12% focus recovery in 5 minutes",
            "category": "wellness" | "productivity" | "technical"
        }
        """
        session_id = package.get("session_id")
        
        # Initialize session history
        if session_id not in self.session_history:
            self.session_history[session_id] = []
        
        self.session_history[session_id].append(package)
        
        # Keep only last 12 packages (60 seconds)
        if len(self.session_history[session_id]) > 12:
            self.session_history[session_id] = self.session_history[session_id][-12:]
        
        # Analyze trends
        focus_trend = self._get_focus_trend(session_id)
        stress_level = self._get_stress_level(package)
        activity_duration = self._get_focused_duration(session_id)
        typing_speed = package.get("input_dynamics", {}).get("keystroke_rate", 0)
        mouse_velocity = package.get("input_dynamics", {}).get("mouse_velocity", 0)
        
        # Generate coaching tips
        if focus_trend == "declining" and stress_level > 0.7:
            return {
                "suggestion": CoachingTip.TAKE_BREAK.value,
                "confidence": 0.92,
                "estimated_impact": "Estimated +15% focus recovery after break",
                "category": "wellness",
                "action": "suggest_break",
                "duration_minutes": 2
            }
        
        if typing_speed > 120:  # Very fast typing
            return {
                "suggestion": CoachingTip.SLOW_DOWN.value,
                "confidence": 0.78,
                "estimated_impact": "Reduce errors by 20%",
                "category": "productivity",
                "action": "suggest_breathing",
                "breathing_duration_seconds": 30
            }
        
        if activity_duration > 180:  # 3+ hours focused
            return {
                "suggestion": CoachingTip.LUNCH_BREAK.value,
                "confidence": 0.88,
                "estimated_impact": "Recharge mental energy, +25% afternoon productivity",
                "category": "wellness",
                "action": "suggest_break",
                "duration_minutes": 30
            }
        
        if mouse_velocity > 400:  # Very tense mouse movement
            return {
                "suggestion": CoachingTip.STRETCH.value,
                "confidence": 0.81,
                "estimated_impact": "Reduce physical tension, improve focus",
                "category": "wellness",
                "action": "suggest_stretch",
                "duration_minutes": 3
            }
        
        if focus_trend == "stable_high":
            return {
                "suggestion": CoachingTip.FOCUS_TIME.value,
                "confidence": 0.95,
                "estimated_impact": "Leverage your momentum - you're in flow state!",
                "category": "productivity",
                "action": "silence_notifications",
                "duration_minutes": 25
            }
        
        return None
    
    def _get_focus_trend(self, session_id: str) -> str:
        """Analyze focus score trend."""
        if session_id not in self.session_history:
            return "unknown"
        
        history = self.session_history[session_id]
        if len(history) < 3:
            return "unknown"
        
        focus_scores = [
            p.get("focus_metrics", {}).get("focus_score", 0.5)
            for p in history[-6:]
        ]
        
        if len(focus_scores) < 2:
            return "unknown"
        
        recent_avg = statistics.mean(focus_scores[-3:])
        older_avg = statistics.mean(focus_scores[:3])
        
        if recent_avg < 0.3:
            return "declining"
        elif recent_avg > 0.8:
            return "stable_high"
        elif recent_avg > older_avg:
            return "improving"
        else:
            return "declining"
    
    def _get_stress_level(self, package: Dict) -> float:
        """Calculate stress level from multiple signals (0-1)."""
        stress = 0
        
        # Voice stress
        voice = package.get("voice_data", {})
        if voice:
            sentiment = voice.get("sentiment_score", 0)
            stress += max(0, -sentiment) * 0.3  # Negative sentiment = stress
        
        # Input stress
        keystroke_var = package.get("input_dynamics", {}).get("keystroke_rhythm_variance", 0)
        stress += keystroke_var * 0.3
        
        # Cognitive stress
        focus = package.get("focus_metrics", {}).get("focus_score", 0.5)
        stress += (1 - focus) * 0.4
        
        return min(1.0, stress)
    
    def _get_focused_duration(self, session_id: str) -> int:
        """How many seconds has user been focused (focus_score > 0.7)."""
        if session_id not in self.session_history:
            return 0
        
        focused_packages = sum(
            1 for p in self.session_history[session_id]
            if p.get("focus_metrics", {}).get("focus_score", 0) > 0.7
        )
        
        return focused_packages * 5  # Each package = 5 seconds


# ============================================================================
# TIER 2: FLOW STATE DETECTION (FocusRing) 🧠
# ============================================================================

class FlowState(Enum):
    """Flow state classifications."""
    DEEP_FLOW = "deep_flow"        # Perfect conditions for deep work
    FOCUSED = "focused"            # Good focus
    SCATTERED = "scattered"        # Distracted
    STRESSED = "stressed"          # Anxious
    TIRED = "tired"               # Fatigued
    NEUTRAL = "neutral"           # No clear state


class FlowDetector:
    """Detect when users enter 'flow state' (deep work mode)."""
    
    def detect_flow_state(self, package: Dict) -> Dict:
        """
        Detect flow state from multiple signals.
        
        Returns: {
            "flow_state": "deep_flow",
            "flow_score": 0.92,  # 0-1
            "signals": {
                "keystroke_rhythm": 0.05,  # Low variance = consistent = flow
                "mouse_smoothness": 0.88,  # Smooth = focused
                "app_focus": 0.95,         # Minimal switching
                "focus_metric": 0.91,      # From client
                "interaction_density": 0.87  # Consistent interaction
            },
            "interpretation": "User is in deep work mode. Minimize distractions.",
            "recommendations": [
                "Auto-silence notifications",
                "Hide non-essential UI elements",
                "Show 'do not disturb' to others"
            ]
        }
        """
        
        # Extract signals
        keystroke_variance = package.get("input_dynamics", {}).get("keystroke_rhythm_variance", 1.0)
        mouse_velocity = package.get("input_dynamics", {}).get("mouse_velocity", 0)
        app_switches = package.get("process_data", {}).get("app_switches", 0)
        focus_score = package.get("focus_metrics", {}).get("focus_score", 0.5)
        
        # Calculate component scores (0-1, inverted where needed)
        keystroke_rhythm_score = 1.0 - keystroke_variance  # Lower var = higher score
        mouse_smoothness = 1.0 - min(1.0, abs(mouse_velocity - 150) / 300)  # Optimal ~150px/s
        app_focus = 1.0 - min(1.0, app_switches / 5)  # Higher switches = lower score
        
        # Composite flow score
        flow_score = (
            keystroke_rhythm_score * 0.3 +
            mouse_smoothness * 0.2 +
            app_focus * 0.25 +
            focus_score * 0.25
        )
        
        # Classify state
        if flow_score > 0.85 and focus_score > 0.8:
            state = FlowState.DEEP_FLOW
        elif flow_score > 0.7:
            state = FlowState.FOCUSED
        elif focus_score < 0.3:
            state = FlowState.SCATTERED
        elif keystroke_variance > 0.75:
            state = FlowState.STRESSED
        elif mouse_velocity < 50:  # Very slow = fatigue
            state = FlowState.TIRED
        else:
            state = FlowState.NEUTRAL
        
        recommendations = self._get_recommendations(state, flow_score)
        
        return {
            "flow_state": state.value,
            "flow_score": round(flow_score, 2),
            "signals": {
                "keystroke_rhythm": round(keystroke_rhythm_score, 2),
                "mouse_smoothness": round(mouse_smoothness, 2),
                "app_focus": round(app_focus, 2),
                "focus_metric": round(focus_score, 2),
                "interaction_density": round((keystroke_rhythm_score + mouse_smoothness) / 2, 2)
            },
            "interpretation": self._interpret_flow(state, flow_score),
            "recommendations": recommendations
        }
    
    def _interpret_flow(self, state: FlowState, score: float) -> str:
        interpretations = {
            FlowState.DEEP_FLOW: "User is in deep work mode. Excellent focus and consistency. Minimize ALL distractions.",
            FlowState.FOCUSED: "User is focused and productive. Good conditions for work.",
            FlowState.SCATTERED: "User is distracted and context-switching. Consider removing distractions.",
            FlowState.STRESSED: "User shows signs of stress or anxiety. Consider breaks or support.",
            FlowState.TIRED: "User appears fatigued. Recommend rest or task switching.",
            FlowState.NEUTRAL: "User is in normal working state. Performance is average."
        }
        return interpretations.get(state, "Unknown state")
    
    def _get_recommendations(self, state: FlowState, score: float) -> List[str]:
        """Get actionable recommendations based on flow state."""
        if state == FlowState.DEEP_FLOW:
            return [
                "✓ Auto-silence all notifications",
                "✓ Hide chat/social media",
                "✓ Show 'Deep Work - Do Not Disturb' indicator",
                "✓ Block distracting websites",
                "✓ Schedule 25-minute focus sprint timer"
            ]
        elif state == FlowState.FOCUSED:
            return [
                "Silence notifications during this session",
                "Consider a focused work timer"
            ]
        elif state == FlowState.SCATTERED:
            return [
                "Take a 5-minute break",
                "Close unnecessary tabs/apps",
                "Eliminate notifications",
                "Return to one primary task"
            ]
        elif state == FlowState.STRESSED:
            return [
                "Take a 10-minute relaxation break",
                "Practice deep breathing (4-7-8 technique)",
                "Step away from screen",
                "Talk to someone"
            ]
        else:
            return ["Continue your work - you're doing well"]


# ============================================================================
# TIER 3: EMPATHY ENGINE - Emotion Recognition + Wellness 😊
# ============================================================================

class EmotionalState(Enum):
    """Emotional state classifications."""
    CONFIDENT = "confident"
    FOCUSED = "focused"
    NEUTRAL = "neutral"
    STRESSED = "stressed"
    FRUSTRATED = "frustrated"
    FATIGUED = "fatigued"


class EmpathyEngine:
    """Detect emotional states and suggest wellness interventions."""
    
    def analyze_emotional_state(self, package: Dict) -> Dict:
        """
        Analyze emotional state from voice, input patterns, and metrics.
        
        Returns: {
            "emotion": "stressed",
            "confidence": 0.78,
            "wellbeing_score": 45,  # 0-100
            "indicators": {
                "voice_sentiment": -0.6,
                "keystroke_erraticism": 0.72,
                "physical_tension": 0.68
            },
            "suggestions": [
                "Take 5 breathing exercises",
                "Step outside for 2 mins",
                "Switch to easier task first"
            ]
        }
        """
        
        voice = package.get("voice_data", {})
        input_dyn = package.get("input_dynamics", {})
        focus = package.get("focus_metrics", {}).get("focus_score", 0.5)
        
        # Calculate emotional indicators (0-1)
        voice_sentiment = voice.get("sentiment_score", 0) if voice else 0
        keystroke_erraticism = input_dyn.get("keystroke_rhythm_variance", 0)
        physical_tension = min(1.0, input_dyn.get("mouse_velocity", 0) / 400)
        
        # Classify emotional state
        emotion, confidence = self._classify_emotion(
            voice_sentiment,
            keystroke_erraticism,
            physical_tension,
            focus
        )
        
        # Calculate wellbeing score (0-100)
        wellbeing = self._calculate_wellbeing(
            voice_sentiment,
            keystroke_erraticism,
            physical_tension,
            focus
        )
        
        suggestions = self._get_wellness_suggestions(emotion, wellbeing)
        
        return {
            "emotion": emotion.value,
            "confidence": round(confidence, 2),
            "wellbeing_score": round(wellbeing, 0),
            "indicators": {
                "voice_sentiment": round(voice_sentiment, 2),
                "keystroke_erraticism": round(keystroke_erraticism, 2),
                "physical_tension": round(physical_tension, 2),
                "focus_level": round(focus, 2)
            },
            "suggestions": suggestions,
            "resources": {
                "5_min_breathing": "https://example.com/breathing-guide",
                "stress_relief": "https://example.com/stress-relief",
                "wellness_check_in": "https://example.com/wellness-checkin"
            }
        }
    
    def _classify_emotion(self, sentiment: float, erraticism: float, tension: float, focus: float) -> Tuple[EmotionalState, float]:
        """Classify emotional state from indicators."""
        
        if sentiment > 0.5 and erraticism < 0.3 and focus > 0.7:
            return (EmotionalState.CONFIDENT, 0.85)
        elif sentiment > 0 and erraticism < 0.4 and focus > 0.6:
            return (EmotionalState.FOCUSED, 0.80)
        elif sentiment < -0.5 and erraticism > 0.7 and tension > 0.6:
            return (EmotionalState.STRESSED, 0.82)
        elif sentiment < -0.3 and erraticism > 0.65:
            return (EmotionalState.FRUSTRATED, 0.78)
        elif tension < 0.2 and focus < 0.4:
            return (EmotionalState.FATIGUED, 0.75)
        else:
            return (EmotionalState.NEUTRAL, 0.60)
    
    def _calculate_wellbeing(self, sentiment: float, erraticism: float, tension: float, focus: float) -> float:
        """Calculate wellbeing score (0-100)."""
        # Positive sentiment contributes
        sentiment_score = (sentiment + 1) / 2 * 25  # 0-25
        
        # Low erraticism = good
        consistency_score = (1 - erraticism) * 25  # 0-25
        
        # Low tension = good
        relaxation_score = (1 - tension) * 25  # 0-25
        
        # Good focus = good
        focus_score = focus * 25  # 0-25
        
        total = sentiment_score + consistency_score + relaxation_score + focus_score
        return min(100, total)
    
    def _get_wellness_suggestions(self, emotion: EmotionalState, wellbeing: float) -> List[str]:
        """Get wellness suggestions based on emotional state."""
        
        if emotion == EmotionalState.STRESSED and wellbeing < 40:
            return [
                "🧘 Take 5 minutes of guided breathing",
                "🚶 Take a 10-minute walk outside",
                "💧 Drink water and step away from screen",
                "📞 Consider talking to someone",
                "⏸️ Take a longer break if possible"
            ]
        elif emotion == EmotionalState.FRUSTRATED:
            return [
                "🔄 Switch to a different, easier task",
                "😊 Celebrate a small win from earlier",
                "💪 You've got this - you're making progress",
                "🎯 Break the current task into smaller steps",
                "⏰ Take a quick 5-minute reset break"
            ]
        elif emotion == EmotionalState.FATIGUED:
            return [
                "😴 You might be tired - consider a nap or rest",
                "☕ Caffeine or snack might help",
                "💪 Switch to a more engaging task",
                "🌅 Get some fresh air or sunlight",
                "⏸️ Call it a day if possible - rest is productive"
            ]
        elif emotion == EmotionalState.CONFIDENT:
            return [
                "🚀 You're doing great! Keep this momentum",
                "🎯 Tackle that hard task while you're in flow",
                "📈 You're on fire - make the most of it!",
                "💡 Channel this confidence into important work"
            ]
        else:
            return [
                "✓ You're maintaining good balance",
                "💡 Keep focusing on what matters",
                "⚖️ Remember to take breaks regularly"
            ]


# ============================================================================
# TIER 4: PRODUCTIVITY BENCHMARKS - Anonymous Leaderboards 🏆
# ============================================================================

class ProductivityBenchmarks:
    """Compare student productivity to anonymous peer group."""
    
    def __init__(self, peer_data: Optional[Dict] = None):
        """peer_data: {student_id: {"focus_avg": 0.75, "sessions": 5, ...}}"""
        self.peer_data = peer_data or {}
    
    def calculate_percentile(self, student_id: str, focus_score: float, metric: str = "focus") -> Dict:
        """
        Compare student to peers and calculate percentile rank.
        
        Returns: {
            "student_focus": 0.82,
            "class_average": 0.71,
            "top_performer": 0.94,
            "percentile": 78,
            "interpretation": "You're in top 22% of class",
            "insight": "Your focus discipline is 11% better than peers"
        }
        """
        
        if not self.peer_data or len(self.peer_data) < 2:
            return None
        
        # Get all peer scores for this metric
        peer_scores = [
            data.get(f"{metric}_avg", 0.5)
            for sid, data in self.peer_data.items()
            if sid != student_id
        ]
        
        if not peer_scores:
            return None
        
        peer_scores.sort()
        percentile = (len([s for s in peer_scores if s < focus_score]) / len(peer_scores)) * 100
        
        return {
            "student_score": round(focus_score, 2),
            "class_average": round(statistics.mean(peer_scores), 2),
            "top_performer": round(max(peer_scores), 2),
            "bottom_performer": round(min(peer_scores), 2),
            "percentile": round(percentile, 0),
            "rank": self._get_rank_description(percentile),
            "interpretation": self._get_interpretation(percentile, focus_score, statistics.mean(peer_scores)),
            "improvement_opportunity": self._get_improvement_tip(percentile, focus_score, statistics.mean(peer_scores))
        }
    
    def _get_rank_description(self, percentile: float) -> str:
        if percentile >= 90:
            return "🥇 Top 10% - Exceptional!"
        elif percentile >= 75:
            return "🥈 Top 25% - Excellent!"
        elif percentile >= 50:
            return "🥉 Top 50% - Good!"
        elif percentile >= 25:
            return "📈 Below average - room to grow"
        else:
            return "⚠️ Needs improvement"
    
    def _get_interpretation(self, percentile: float, score: float, avg: float) -> str:
        diff_pct = ((score - avg) / avg * 100) if avg > 0 else 0
        
        if percentile >= 75:
            return f"You're {abs(diff_pct):.0f}% better focused than peers!"
        elif percentile >= 50:
            return f"You're {abs(diff_pct):.0f}% better focused than average"
        elif percentile >= 25:
            return f"You're {abs(diff_pct):.0f}% less focused than average - small efforts can help"
        else:
            return f"You're {abs(diff_pct):.0f}% less focused than average - let's work together"
    
    def _get_improvement_tip(self, percentile: float, score: float, avg: float) -> str:
        if percentile < 50:
            return "💡 Try breaking tasks into 25-minute focus sprints (Pomodoro technique)"
        elif percentile < 75:
            return "💡 You're doing well! Small refinements: eliminate one distraction source"
        else:
            return "💡 Maintain your excellent focus - you're an inspiration to others!"


# ============================================================================
# TIER 5: AT-RISK ALERTS - Predictive Early Warning 🚨
# ============================================================================

class AtRiskDetector:
    """Predict when students are at-risk of failure."""
    
    def __init__(self):
        self.student_history: Dict[str, List[Dict]] = {}
    
    def assess_at_risk(self, student_id: str, package: Dict) -> Optional[Dict]:
        """
        Analyze trend to predict if student is at-risk.
        
        Returns: {
            "risk_level": "HIGH",
            "confidence": 0.92,
            "factors": ["declining_focus", "high_stress", "erratic_typing"],
            "intervention": "Suggest 1-on-1 with teacher",
            "draft_message": "Hi [Student], I noticed some patterns. Can we chat?"
        }
        """
        
        if student_id not in self.student_history:
            self.student_history[student_id] = []
        
        self.student_history[student_id].append(package)
        
        # Keep last 24 packages (120 seconds = 2 minutes)
        if len(self.student_history[student_id]) > 24:
            self.student_history[student_id] = self.student_history[student_id][-24:]
        
        if len(self.student_history[student_id]) < 6:
            return None  # Not enough history
        
        # Analyze trends
        focus_trend = self._trend_direction([
            p.get("focus_metrics", {}).get("focus_score", 0.5)
            for p in self.student_history[student_id][-6:]
        ])
        
        stress_trend = self._trend_direction([
            1 - p.get("focus_metrics", {}).get("focus_score", 0.5)
            for p in self.student_history[student_id][-6:]
        ])
        
        erratic_trend = self._trend_direction([
            p.get("input_dynamics", {}).get("keystroke_rhythm_variance", 0)
            for p in self.student_history[student_id][-6:]
        ])
        
        errors_trend = self._trend_direction([
            p.get("input_dynamics", {}).get("keystroke_errors", 0)
            for p in self.student_history[student_id][-6:]
        ])
        
        # Calculate risk factors
        risk_factors = []
        if focus_trend == "declining":
            risk_factors.append("declining_focus")
        if stress_trend == "increasing":
            risk_factors.append("high_stress")
        if erratic_trend == "increasing":
            risk_factors.append("erratic_typing")
        if errors_trend == "increasing":
            risk_factors.append("increasing_errors")
        
        if len(risk_factors) < 2:
            return None  # Not enough risk factors
        
        confidence = min(0.99, len(risk_factors) * 0.25)
        
        if confidence > 0.75:
            return {
                "student_id": student_id,
                "risk_level": "HIGH" if confidence > 0.85 else "MEDIUM",
                "confidence": round(confidence, 2),
                "factors": risk_factors,
                "intervention": "Schedule 1-on-1 check-in with student",
                "draft_message": f"Hi, I noticed you might be struggling with {', '.join(risk_factors)}. Would you like to talk? - Your Teacher",
                "resources": [
                    "📚 Study tips guide",
                    "😊 Wellness resources",
                    "🎯 Goal-setting worksheet"
                ]
            }
        
        return None
    
    def _trend_direction(self, values: List[float]) -> str:
        """Determine if trend is increasing, decreasing, or stable."""
        if len(values) < 2:
            return "unknown"
        
        first_half_avg = statistics.mean(values[:len(values)//2])
        second_half_avg = statistics.mean(values[len(values)//2:])
        
        diff = second_half_avg - first_half_avg
        
        if abs(diff) < 0.05:
            return "stable"
        elif diff > 0:
            return "increasing"
        else:
            return "declining"


# ============================================================================
# TIER 6: CONTEXT UNDERSTANDING - Know What They're Actually Doing 🔍
# ============================================================================

class ContextUnderstanding:
    """Map applications to work contexts (coding, writing, researching, etc)."""
    
    # Application patterns
    APP_CONTEXTS = {
        "coding": {
            "apps": ["vscode", "visualstudio", "xcode", "pycharm", "intellij", "sublime", "atom"],
            "characteristics": {
                "focus_score_min": 0.7,
                "keystroke_rate_min": 40,
                "app_switch_max": 3
            }
        },
        "writing": {
            "apps": ["word", "docs", "notion", "obsidian", "iwriter", "gdocs"],
            "characteristics": {
                "focus_score_min": 0.65,
                "keystroke_rate_min": 30,
                "mouse_velocity_max": 100
            }
        },
        "researching": {
            "apps": ["chrome", "firefox", "safari", "edge"],
            "characteristics": {
                "app_switch_min": 5,
                "focus_score_min": 0.5,
                "keystroke_rate_max": 20
            }
        },
        "video_conferencing": {
            "apps": ["zoom", "teams", "meet", "webex"],
            "characteristics": {
                "network_bandwidth_high": True,
                "mouse_velocity_variable": True
            }
        },
        "presentation": {
            "apps": ["powerpoint", "keynote", "reveal"],
            "characteristics": {
                "app_switch_frequent": True,
                "mouse_velocity_variable": True
            }
        },
        "data_analysis": {
            "apps": ["excel", "tableau", "python", "jupyter", "rstudio"],
            "characteristics": {
                "focus_score_min": 0.7,
                "keystroke_rate_variable": True
            }
        }
    }
    
    def infer_work_context(self, package: Dict) -> Dict:
        """
        Infer what type of work user is doing based on app + patterns.
        
        Returns: {
            "context": "coding",
            "confidence": 0.87,
            "quality_metric": {
                "focus": 0.85,  # Is this good for this context?
                "intensity": "high",
                "productivity_estimate": "strong"
            },
            "interpretation": "Deep coding session - excellent focus"
        }
        """
        
        app_name = package.get("process_data", {}).get("active_process", "").lower()
        focus = package.get("focus_metrics", {}).get("focus_score", 0.5)
        keystroke_rate = package.get("input_dynamics", {}).get("keystroke_rate", 0)
        mouse_velocity = package.get("input_dynamics", {}).get("mouse_velocity", 0)
        app_switches = package.get("process_data", {}).get("app_switches", 0)
        
        # Find best matching context
        best_context = None
        best_score = 0
        
        for context, data in self.APP_CONTEXTS.items():
            if any(app in app_name for app in data.get("apps", [])):
                # Bonus for app match
                match_score = 0.7
                
                # Check characteristics
                chars = data.get("characteristics", {})
                if "focus_score_min" in chars and focus >= chars["focus_score_min"]:
                    match_score += 0.15
                if "keystroke_rate_min" in chars and keystroke_rate >= chars["keystroke_rate_min"]:
                    match_score += 0.15
                
                if match_score > best_score:
                    best_score = match_score
                    best_context = context
        
        if not best_context:
            best_context = "general_work"
            best_score = 0.5
        
        # Quality assessment
        quality = self._assess_quality_for_context(best_context, package)
        
        return {
            "context": best_context,
            "confidence": round(best_score, 2),
            "active_app": app_name,
            "quality_metrics": quality,
            "interpretation": self._get_context_interpretation(best_context, quality),
            "tips": self._get_context_tips(best_context, quality)
        }
    
    def _assess_quality_for_context(self, context: str, package: Dict) -> Dict:
        """Assess work quality for specific context."""
        focus = package.get("focus_metrics", {}).get("focus_score", 0.5)
        keystroke_rate = package.get("input_dynamics", {}).get("keystroke_rate", 0)
        keystroke_var = package.get("input_dynamics", {}).get("keystroke_rhythm_variance", 0)
        
        intensity = "high" if keystroke_rate > 80 else "medium" if keystroke_rate > 40 else "low"
        consistency = "high" if keystroke_var < 0.3 else "medium" if keystroke_var < 0.6 else "low"
        
        if context == "coding" and focus > 0.75 and consistency == "high":
            productivity = "strong"
        elif context == "writing" and focus > 0.7 and intensity in ["high", "medium"]:
            productivity = "strong"
        elif focus > 0.6:
            productivity = "good"
        else:
            productivity = "needs improvement"
        
        return {
            "focus_level": round(focus, 2),
            "intensity": intensity,
            "consistency": consistency,
            "productivity_estimate": productivity
        }
    
    def _get_context_interpretation(self, context: str, quality: Dict) -> str:
        prod = quality.get("productivity_estimate", "unknown")
        
        if prod == "strong":
            return f"Strong {context} session - excellent focus and consistency!"
        elif prod == "good":
            return f"Good {context} work - maintain this momentum"
        else:
            return f"Consider taking a break or eliminating distractions"
    
    def _get_context_tips(self, context: str, quality: Dict) -> List[str]:
        """Get context-specific tips."""
        tips = {
            "coding": [
                "🔇 Silence notifications - deep focus needed",
                "🎯 Consider 50-minute focus sprints",
                "📝 Document complex sections as you go"
            ],
            "writing": [
                "✍️ Don't edit while drafting - keep momentum",
                "🔇 Sound off for flow state",
                "⏱️ Use timed writing sessions (25-50 min)"
            ],
            "researching": [
                "📌 Keep a research log as you browse",
                "⏰ Set a timer to avoid rabbit holes",
                "🎯 Define what you're looking for first"
            ],
            "video_conferencing": [
                "😊 Look at camera for engagement",
                "📱 Silence notifications",
                "💧 Keep water nearby"
            ]
        }
        return tips.get(context, ["💡 You're doing great - keep focused!"])


# ============================================================================
# TIER 7: STUDY PODS - Group Focus Sessions 👥
# ============================================================================

class StudyPod:
    """Synchronized group focus sessions with accountability."""
    
    def __init__(self, pod_id: str, name: str, members: List[str], duration_minutes: int = 50):
        self.pod_id = pod_id
        self.name = name
        self.members = members
        self.duration_minutes = duration_minutes
        self.start_time = datetime.now()
        self.member_metrics = {m: [] for m in members}
        self.is_active = True
    
    def update_member_metrics(self, member_id: str, package: Dict):
        """Update metrics for a pod member."""
        if member_id in self.member_metrics:
            self.member_metrics[member_id].append({
                "focus": package.get("focus_metrics", {}).get("focus_score", 0.5),
                "timestamp": datetime.now()
            })
    
    def get_pod_status(self) -> Dict:
        """
        Get real-time pod status with metrics.
        
        Returns: {
            "pod_id": "pod-123",
            "pod_name": "CS200 Study Group",
            "duration_remaining": "23 min",
            "members": [
                {
                    "name": "Sarah",
                    "status": "focused",
                    "focus_score": 0.85,
                    "emoji": "🟢"
                },
                {
                    "name": "John",
                    "status": "struggling",
                    "focus_score": 0.42,
                    "emoji": "🟡",
                    "encouragement": "Keep going! 💪"
                }
            ],
            "pod_average_focus": 0.74,
            "group_energy": "high"
        }
        """
        
        elapsed = (datetime.now() - self.start_time).total_seconds() / 60
        remaining = max(0, self.duration_minutes - elapsed)
        
        member_statuses = []
        focus_scores = []
        
        for member in self.members:
            if self.member_metrics[member]:
                latest = self.member_metrics[member][-1]
                focus = latest["focus"]
                focus_scores.append(focus)
                
                # Classify status
                if focus > 0.75:
                    status = "focused"
                    emoji = "🟢"
                    encouragement = None
                elif focus > 0.5:
                    status = "okay"
                    emoji = "🟡"
                    encouragement = "Keep focused! 💪"
                else:
                    status = "struggling"
                    emoji = "🔴"
                    encouragement = "You can do it! 💪 Take a quick break if needed"
                
                member_statuses.append({
                    "name": member,
                    "status": status,
                    "focus_score": round(focus, 2),
                    "emoji": emoji,
                    "encouragement": encouragement
                })
        
        avg_focus = statistics.mean(focus_scores) if focus_scores else 0
        
        return {
            "pod_id": self.pod_id,
            "pod_name": self.name,
            "duration_remaining_min": round(remaining, 1),
            "members": member_statuses,
            "pod_average_focus": round(avg_focus, 2),
            "group_energy": self._classify_group_energy(focus_scores),
            "encouragement": self._get_group_encouragement(member_statuses)
        }
    
    def _classify_group_energy(self, focus_scores: List[float]) -> str:
        """Classify collective group energy."""
        if not focus_scores:
            return "unknown"
        
        avg = statistics.mean(focus_scores)
        if avg > 0.75:
            return "🔥 Excellent! Everyone is focused"
        elif avg > 0.6:
            return "💪 Good group momentum"
        elif avg > 0.4:
            return "⚖️ Mixed - some struggling"
        else:
            return "⚠️ Group needs refreshment"
    
    def _get_group_encouragement(self, member_statuses: List[Dict]) -> str:
        """Get group-level encouragement message."""
        focused_count = sum(1 for m in member_statuses if m["status"] == "focused")
        total = len(member_statuses)
        pct = (focused_count / total * 100) if total > 0 else 0
        
        if pct >= 80:
            return "🌟 Amazing group focus! You're all in the zone!"
        elif pct >= 60:
            return "💯 Most of you are focused - great work!"
        elif pct >= 40:
            return "🚀 Come on team - you've got this! 💪"
        else:
            return "😊 Regroup! Take a quick 2-minute break and jump back in"


# ============================================================================
# ADVANCED FEATURES COORDINATOR
# ============================================================================

class AdvancedFeaturesCoordinator:
    """Orchestrates all 7 tiers of advanced features."""
    
    def __init__(self):
        self.coach = AdaptiveCoach()
        self.flow_detector = FlowDetector()
        self.empathy_engine = EmpathyEngine()
        self.benchmarks = ProductivityBenchmarks()
        self.at_risk_detector = AtRiskDetector()
        self.context_analyzer = ContextUnderstanding()
        self.pods: Dict[str, StudyPod] = {}
    
    async def process_with_advanced_features(self, package: Dict, anomalies: List[Dict]) -> Dict:
        """
        Process package through all 7 tiers.
        
        Returns comprehensive analysis with all advanced features.
        """
        
        session_id = package.get("session_id")
        student_id = package.get("student_id")
        
        analysis = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "student_id": student_id,
            
            # Tier 1: Coaching
            "coaching": self.coach.analyze_and_coach(package, anomalies),
            
            # Tier 2: Flow State
            "flow_state": self.flow_detector.detect_flow_state(package),
            
            # Tier 3: Empathy
            "emotional_state": self.empathy_engine.analyze_emotional_state(package),
            
            # Tier 4: Benchmarks
            "productivity_benchmark": self.benchmarks.calculate_percentile(student_id, 
                package.get("focus_metrics", {}).get("focus_score", 0.5)),
            
            # Tier 5: At-Risk
            "at_risk_assessment": self.at_risk_detector.assess_at_risk(student_id, package),
            
            # Tier 6: Context
            "work_context": self.context_analyzer.infer_work_context(package),
        }
        
        return analysis
