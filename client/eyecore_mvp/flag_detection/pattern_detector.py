"""
Pattern Detector: Statistical analysis of activity patterns for suspicious behavior.

Detects:
- Anomalous keystroke patterns (biometric drift)
- Unusual network spikes
- Suspicious focus/stress combinations
- Temporal inconsistencies
"""

import statistics
from typing import Dict, List, Any, Optional
from collections import deque
from datetime import datetime, timedelta


class PatternDetector:
    """Detects statistical patterns in activity data."""
    
    def __init__(self, history_window_minutes: int = 5):
        """
        Initialize pattern detector.
        
        Args:
            history_window_minutes: How far back to analyze patterns
        """
        self.history_window = history_window_minutes * 60  # seconds
        self.history: Dict[str, deque] = {
            "keystroke_rhythm_variance": deque(),
            "focus_score": deque(),
            "stress_level": deque(),
            "network_bytes": deque(),
            "cpu_usage": deque(),
            "app_switches": deque(),
            "timestamps": deque(),
        }
        
    def add_activity(self, package: Dict[str, Any]) -> None:
        """Add activity package to history."""
        timestamp = datetime.fromisoformat(package.get("timestamp", datetime.utcnow().isoformat()))
        cutoff = timestamp - timedelta(seconds=self.history_window)
        
        # Remove old entries
        while self.history["timestamps"] and datetime.fromisoformat(self.history["timestamps"][0]) < cutoff:
            self.history["timestamps"].popleft()
            self.history["keystroke_rhythm_variance"].popleft()
            self.history["focus_score"].popleft()
            self.history["stress_level"].popleft()
            self.history["network_bytes"].popleft()
            self.history["cpu_usage"].popleft()
            self.history["app_switches"].popleft()
        
        # Add new entry
        self.history["timestamps"].append(package.get("timestamp", datetime.utcnow().isoformat()))
        self.history["keystroke_rhythm_variance"].append(
            package.get("input_dynamics", {}).get("keystroke_rhythm_variance", 0.0)
        )
        self.history["focus_score"].append(
            package.get("focus_metrics", {}).get("focus_score", 0.5)
        )
        self.history["stress_level"].append(
            self._calculate_stress_level(package)
        )
        self.history["network_bytes"].append(
            package.get("network_activity", {}).get("bytes_sent", 0) + 
            package.get("network_activity", {}).get("bytes_received", 0)
        )
        self.history["cpu_usage"].append(
            package.get("system_metrics", {}).get("cpu_usage", 0.0)
        )
        self.history["app_switches"].append(
            package.get("process_data", {}).get("app_switches", 0)
        )
    
    def _calculate_stress_level(self, package: Dict[str, Any]) -> float:
        """
        Calculate stress level from multiple signals (0-1).
        
        Combines:
        - Keystroke erraticism
        - Mouse velocity (tension)
        - Voice sentiment (if available)
        """
        stress = 0.0
        
        # Keystroke erraticism
        keystroke_var = package.get("input_dynamics", {}).get("keystroke_rhythm_variance", 0.0)
        stress += min(1.0, keystroke_var) * 0.4
        
        # Mouse velocity (jerky = stressed)
        mouse_velocity = package.get("input_dynamics", {}).get("mouse_velocity", 0.0)
        stress += min(1.0, mouse_velocity / 100) * 0.3
        
        # Voice sentiment (if available)
        voice_sentiment = package.get("voice_metrics", {}).get("sentiment_score", 0.0)
        if voice_sentiment < 0:
            stress += abs(voice_sentiment) * 0.3
        
        return min(1.0, stress)
    
    def detect_patterns(self) -> Dict[str, Any]:
        """
        Analyze patterns in historical data.
        
        Returns:
            Dictionary with detected patterns and severity.
        """
        if len(self.history["timestamps"]) < 3:
            return {"patterns_detected": [], "severity": "low", "confidence": 0.0}
        
        patterns = []
        
        # Pattern 1: Biometric Drift (keystroke changes)
        keystroke_drift = self._detect_biometric_drift()
        if keystroke_drift["detected"]:
            patterns.append(keystroke_drift)
        
        # Pattern 2: Focus Collapse
        focus_collapse = self._detect_focus_collapse()
        if focus_collapse["detected"]:
            patterns.append(focus_collapse)
        
        # Pattern 3: Stress Spike
        stress_spike = self._detect_stress_spike()
        if stress_spike["detected"]:
            patterns.append(stress_spike)
        
        # Pattern 4: Network Anomaly
        network_anomaly = self._detect_network_anomaly()
        if network_anomaly["detected"]:
            patterns.append(network_anomaly)
        
        # Pattern 5: Resource Exhaustion
        resource_exhaustion = self._detect_resource_exhaustion()
        if resource_exhaustion["detected"]:
            patterns.append(resource_exhaustion)
        
        # Pattern 6: Temporal Inconsistency
        temporal_inconsistency = self._detect_temporal_inconsistency()
        if temporal_inconsistency["detected"]:
            patterns.append(temporal_inconsistency)
        
        # Calculate overall severity
        severity = self._calculate_overall_severity(patterns)
        
        return {
            "patterns_detected": patterns,
            "severity": severity,
            "confidence": self._calculate_confidence(patterns),
            "recommendation": self._get_recommendation(patterns),
        }
    
    def _detect_biometric_drift(self) -> Dict[str, Any]:
        """
        Detect if keystroke pattern is changing significantly.
        
        Indicates: Impersonation, nervousness, or fatigue.
        """
        if len(self.history["keystroke_rhythm_variance"]) < 5:
            return {"detected": False}
        
        recent = list(self.history["keystroke_rhythm_variance"])[-5:]
        older = list(self.history["keystroke_rhythm_variance"])[-10:-5] if len(self.history["keystroke_rhythm_variance"]) >= 10 else recent
        
        if not older:
            return {"detected": False}
        
        recent_mean = statistics.mean(recent)
        older_mean = statistics.mean(older)
        
        # If keystroke variance is suddenly much higher, something changed
        if recent_mean > older_mean * 1.5 and recent_mean > 0.5:
            return {
                "detected": True,
                "pattern_name": "Biometric Drift",
                "description": "Keystroke pattern changed significantly",
                "severity": "high" if recent_mean > 0.7 else "medium",
                "recent_variance": recent_mean,
                "older_variance": older_mean,
                "change_magnitude": (recent_mean - older_mean) / (older_mean + 0.001),
                "confidence": min(1.0, (recent_mean - older_mean) / 0.5),
            }
        
        return {"detected": False}
    
    def _detect_focus_collapse(self) -> Dict[str, Any]:
        """
        Detect sudden drop in focus score.
        
        Indicates: Sudden distraction, stress, or resource constraints.
        """
        if len(self.history["focus_score"]) < 5:
            return {"detected": False}
        
        recent = list(self.history["focus_score"])[-5:]
        older = list(self.history["focus_score"])[-10:-5] if len(self.history["focus_score"]) >= 10 else [0.7] * 5
        
        recent_mean = statistics.mean(recent)
        older_mean = statistics.mean(older)
        
        # If focus dropped significantly
        if older_mean > 0.6 and recent_mean < 0.3 and (older_mean - recent_mean) > 0.3:
            return {
                "detected": True,
                "pattern_name": "Focus Collapse",
                "description": "Focus score dropped suddenly",
                "severity": "high" if recent_mean < 0.2 else "medium",
                "recent_focus": recent_mean,
                "older_focus": older_mean,
                "drop_magnitude": older_mean - recent_mean,
                "confidence": min(1.0, (older_mean - recent_mean) / 0.5),
            }
        
        return {"detected": False}
    
    def _detect_stress_spike(self) -> Dict[str, Any]:
        """
        Detect sudden spike in stress indicators.
        
        Indicates: Anxiety, time pressure, or panic.
        """
        if len(self.history["stress_level"]) < 5:
            return {"detected": False}
        
        recent = list(self.history["stress_level"])[-5:]
        older = list(self.history["stress_level"])[-10:-5] if len(self.history["stress_level"]) >= 10 else [0.2] * 5
        
        recent_mean = statistics.mean(recent)
        older_mean = statistics.mean(older)
        
        # If stress increased suddenly
        if recent_mean > 0.6 and (recent_mean - older_mean) > 0.3:
            return {
                "detected": True,
                "pattern_name": "Stress Spike",
                "description": "Stress indicators increased suddenly",
                "severity": "high" if recent_mean > 0.75 else "medium",
                "recent_stress": recent_mean,
                "older_stress": older_mean,
                "spike_magnitude": recent_mean - older_mean,
                "confidence": min(1.0, (recent_mean - older_mean) / 0.5),
            }
        
        return {"detected": False}
    
    def _detect_network_anomaly(self) -> Dict[str, Any]:
        """
        Detect unusual network activity spikes.
        
        Indicates: Data exfiltration or background processes.
        """
        if len(self.history["network_bytes"]) < 5:
            return {"detected": False}
        
        recent = list(self.history["network_bytes"])[-5:]
        older = list(self.history["network_bytes"])[-10:-5] if len(self.history["network_bytes"]) >= 10 else [1000] * 5
        
        recent_mean = statistics.mean(recent)
        older_mean = statistics.mean(older)
        
        # If network usage spiked significantly
        if recent_mean > 5 * 1024 * 1024 and recent_mean > older_mean * 3:  # 5MB spike
            return {
                "detected": True,
                "pattern_name": "Network Anomaly",
                "description": "Network activity spiked significantly",
                "severity": "critical" if recent_mean > 20 * 1024 * 1024 else "high",
                "recent_network_mb": recent_mean / (1024 * 1024),
                "older_network_mb": older_mean / (1024 * 1024),
                "spike_multiplier": recent_mean / (older_mean + 1),
                "confidence": min(1.0, (recent_mean - older_mean) / (5 * 1024 * 1024)),
            }
        
        return {"detected": False}
    
    def _detect_resource_exhaustion(self) -> Dict[str, Any]:
        """
        Detect sustained high CPU/Memory usage.
        
        Indicates: Running multiple programs or processes.
        """
        if len(self.history["cpu_usage"]) < 5:
            return {"detected": False}
        
        recent = list(self.history["cpu_usage"])[-5:]
        
        recent_mean = statistics.mean(recent)
        recent_max = max(recent)
        
        # If CPU is consistently high
        if recent_mean > 80 and recent_max > 90:
            return {
                "detected": True,
                "pattern_name": "Resource Exhaustion",
                "description": "CPU usage consistently high",
                "severity": "high" if recent_mean > 90 else "medium",
                "recent_cpu_mean": recent_mean,
                "recent_cpu_max": recent_max,
                "high_cpu_count": sum(1 for c in recent if c > 85),
                "confidence": min(1.0, (recent_mean - 75) / 25),
            }
        
        return {"detected": False}
    
    def _detect_temporal_inconsistency(self) -> Dict[str, Any]:
        """
        Detect if activity pattern violates physical constraints.
        
        Indicates: Multi-location activity or automated behavior.
        """
        if len(self.history["timestamps"]) < 3:
            return {"detected": False}
        
        timestamps = [datetime.fromisoformat(ts) for ts in list(self.history["timestamps"])[-5:]]
        
        # Check if timestamps are physically impossible
        inconsistencies = []
        for i in range(1, len(timestamps)):
            time_diff = (timestamps[i] - timestamps[i-1]).total_seconds()
            
            # If more than 60 seconds apart, something is wrong
            if time_diff > 60:
                inconsistencies.append(time_diff)
            
            # If less than 0.5 seconds apart (impossible for human), suspicious
            if time_diff < 0.5 and time_diff > 0:
                inconsistencies.append(-time_diff)  # Mark as impossible
        
        if any(t < 0 for t in inconsistencies):  # Found impossible gaps
            return {
                "detected": True,
                "pattern_name": "Temporal Inconsistency",
                "description": "Activity pattern violates physical constraints",
                "severity": "critical",
                "impossible_gaps": [abs(t) for t in inconsistencies if t < 0],
                "confidence": 0.9,
            }
        
        return {"detected": False}
    
    def _calculate_overall_severity(self, patterns: List[Dict[str, Any]]) -> str:
        """Calculate overall severity from detected patterns."""
        if not patterns:
            return "low"
        
        severities = [p.get("severity", "medium") for p in patterns]
        
        if "critical" in severities:
            return "critical"
        elif severities.count("high") >= 2:
            return "high"
        elif "high" in severities:
            return "medium"
        else:
            return "low"
    
    def _calculate_confidence(self, patterns: List[Dict[str, Any]]) -> float:
        """Calculate confidence in detected patterns."""
        if not patterns:
            return 0.0
        
        confidences = [p.get("confidence", 0.5) for p in patterns]
        return statistics.mean(confidences)
    
    def _get_recommendation(self, patterns: List[Dict[str, Any]]) -> str:
        """Get recommendation based on detected patterns."""
        if not patterns:
            return "Continue monitoring"
        
        severities = [p.get("severity", "medium") for p in patterns]
        
        if "critical" in severities:
            return "IMMEDIATE REVIEW REQUIRED - Possible impersonation or data exfiltration"
        elif "high" in severities and len(patterns) >= 2:
            return "SEND TO SERVER FOR ANALYSIS - Multiple high-severity patterns detected"
        elif "high" in severities:
            return "Review and consider escalation"
        else:
            return "Low risk - continue monitoring"
