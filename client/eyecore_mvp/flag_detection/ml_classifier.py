"""
ML Classifier: Lightweight ML model for suspicious activity classification.

Uses simple decision tree logic with weighted features to classify:
- Legitimate behavior (low risk)
- Suspicious but explainable (medium risk)
- Highly suspicious (high risk)
- Critical behavior (immediate escalation)
"""

from typing import Dict, List, Any, Tuple, Optional
import statistics


class MLClassifier:
    """Lightweight ML classifier for activity scoring."""
    
    def __init__(self):
        """Initialize with pre-trained feature weights (based on patterns)."""
        self.feature_weights = {
            # Input dynamics
            "keystroke_rhythm_variance": {"weight": 0.3, "threshold": 0.7, "type": "high_bad"},
            "keystroke_error_rate": {"weight": 0.15, "threshold": 0.05, "type": "high_bad"},
            
            # Network activity
            "network_bytes_sent": {"weight": 0.25, "threshold": 5 * 1024 * 1024, "type": "high_bad"},
            "network_bytes_received": {"weight": 0.15, "threshold": 10 * 1024 * 1024, "type": "high_bad"},
            
            # System metrics
            "cpu_usage": {"weight": 0.1, "threshold": 85, "type": "high_bad"},
            "memory_usage": {"weight": 0.08, "threshold": 80, "type": "high_bad"},
            
            # Focus & attention
            "focus_score": {"weight": 0.2, "threshold": 0.3, "type": "low_bad"},
            "app_switches": {"weight": 0.12, "threshold": 15, "type": "high_bad"},
            
            # Behavior patterns
            "stress_level": {"weight": 0.15, "threshold": 0.7, "type": "high_bad"},
            "mouse_idle_duration": {"weight": 0.08, "threshold": 30, "type": "high_bad"},
        }
    
    def classify(self, package: Dict[str, Any], patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Classify activity as suspicious or legitimate.
        
        Args:
            package: Activity package from client
            patterns: Detected patterns from PatternDetector
            
        Returns:
            Classification with risk level, score, and reasoning
        """
        # Extract features from package
        features = self._extract_features(package)
        
        # Calculate feature scores
        feature_scores = self._calculate_feature_scores(features)
        
        # Calculate composite suspicious score
        suspicious_score = self._calculate_composite_score(feature_scores)
        
        # Get patterns-based risk multiplier
        pattern_multiplier = self._get_pattern_multiplier(patterns)
        
        # Final suspicious score
        final_score = min(1.0, suspicious_score * pattern_multiplier)
        
        # Classify risk level
        risk_level, risk_label = self._classify_risk_level(final_score, patterns)
        
        # Get explanation
        explanation = self._generate_explanation(features, feature_scores, patterns, risk_level)
        
        return {
            "suspicious_score": final_score,
            "risk_level": risk_level,
            "risk_label": risk_label,
            "features_analyzed": features,
            "feature_scores": feature_scores,
            "explanation": explanation,
            "should_flag": risk_level in ["high", "critical"],
            "recommendation": self._get_recommendation(risk_level, patterns),
        }
    
    def _extract_features(self, package: Dict[str, Any]) -> Dict[str, float]:
        """Extract numerical features from activity package."""
        return {
            # Input dynamics
            "keystroke_rhythm_variance": package.get("input_dynamics", {}).get("keystroke_rhythm_variance", 0.0),
            "keystroke_error_rate": package.get("input_dynamics", {}).get("keystroke_error_rate", 0.0),
            "keystroke_speed": package.get("input_dynamics", {}).get("keystroke_speed", 0.0),
            "mouse_velocity": package.get("input_dynamics", {}).get("mouse_velocity", 0.0),
            "mouse_idle_duration": package.get("input_dynamics", {}).get("mouse_idle_duration", 0.0),
            
            # Network activity
            "network_bytes_sent": package.get("network_activity", {}).get("bytes_sent", 0),
            "network_bytes_received": package.get("network_activity", {}).get("bytes_received", 0),
            
            # System metrics
            "cpu_usage": package.get("system_metrics", {}).get("cpu_usage", 0.0),
            "memory_usage": package.get("system_metrics", {}).get("memory_usage", 0.0),
            
            # Focus & attention
            "focus_score": package.get("focus_metrics", {}).get("focus_score", 0.5),
            "eye_contact": package.get("focus_metrics", {}).get("eye_contact_percentage", 0.0),
            
            # Process data
            "app_switches": package.get("process_data", {}).get("app_switches", 0),
            "active_window_title": package.get("process_data", {}).get("window_title", ""),
            
            # Voice metrics
            "voice_sentiment": package.get("voice_metrics", {}).get("sentiment_score", 0.0),
            "voice_pitch_variance": package.get("voice_metrics", {}).get("pitch_variance", 0.0),
        }
    
    def _calculate_feature_scores(self, features: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate normalized scores for each feature (0-1, where 1 = very suspicious).
        """
        scores = {}
        
        # Keystroke rhythm variance (higher = more suspicious)
        scores["keystroke_anomaly"] = min(1.0, features["keystroke_rhythm_variance"] / 1.0)
        
        # Keystroke error rate
        scores["keystroke_error"] = min(1.0, features["keystroke_error_rate"] / 0.1)
        
        # Network activity (higher = more suspicious)
        scores["network_activity"] = min(
            1.0,
            (features["network_bytes_sent"] + features["network_bytes_received"]) / (20 * 1024 * 1024)
        )
        
        # CPU usage (higher = more suspicious)
        scores["cpu_activity"] = max(0.0, (features["cpu_usage"] - 50) / 50)
        
        # Focus score (lower = more suspicious)
        scores["focus_anomaly"] = max(0.0, 1.0 - features["focus_score"])
        
        # App switches (higher = more suspicious)
        scores["app_switching"] = min(1.0, features["app_switches"] / 20)
        
        # Mouse idle (very high or very low = suspicious)
        if features["mouse_idle_duration"] > 30:
            scores["mouse_inactivity"] = min(1.0, (features["mouse_idle_duration"] - 30) / 60)
        else:
            scores["mouse_inactivity"] = 0.0
        
        # Voice sentiment (negative = suspicious)
        if features["voice_sentiment"] < 0:
            scores["voice_stress"] = abs(features["voice_sentiment"])
        else:
            scores["voice_stress"] = 0.0
        
        return scores
    
    def _calculate_composite_score(self, feature_scores: Dict[str, float]) -> float:
        """
        Calculate composite suspicious score using weighted features.
        
        Returns: 0-1 score where 1 = most suspicious
        """
        weights = {
            "keystroke_anomaly": 0.25,
            "network_activity": 0.25,
            "focus_anomaly": 0.15,
            "app_switching": 0.1,
            "cpu_activity": 0.08,
            "voice_stress": 0.1,
            "keystroke_error": 0.05,
            "mouse_inactivity": 0.02,
        }
        
        composite = 0.0
        for feature_name, weight in weights.items():
            if feature_name in feature_scores:
                composite += feature_scores[feature_name] * weight
        
        return min(1.0, composite)
    
    def _get_pattern_multiplier(self, patterns: List[Dict[str, Any]]) -> float:
        """
        Get multiplier for pattern-based risk elevation.
        
        Returns: 1.0 - 2.0+ based on detected patterns
        """
        if not patterns:
            return 1.0
        
        multiplier = 1.0
        
        for pattern in patterns:
            severity = pattern.get("severity", "medium")
            confidence = pattern.get("confidence", 0.5)
            
            if severity == "critical":
                multiplier *= (2.0 * confidence)
            elif severity == "high":
                multiplier *= (1.5 * confidence)
            elif severity == "medium":
                multiplier *= (1.2 * confidence)
        
        # Cap multiplier at 2.5x
        return min(2.5, multiplier)
    
    def _classify_risk_level(self, score: float, patterns: List[Dict[str, Any]]) -> Tuple[str, str]:
        """
        Classify risk level based on score and patterns.
        
        Returns: (risk_level, risk_label)
        """
        # Check for critical patterns
        has_critical_pattern = any(p.get("severity") == "critical" for p in patterns)
        
        if has_critical_pattern or score > 0.8:
            return "critical", "🚨 CRITICAL - Immediate escalation required"
        elif score > 0.65:
            return "high", "⚠️ HIGH RISK - Multiple suspicious indicators"
        elif score > 0.45:
            return "medium", "⚡ MEDIUM RISK - Monitor closely"
        elif score > 0.25:
            return "low", "ℹ️ LOW RISK - Minimal suspicious indicators"
        else:
            return "none", "✓ CLEAN - No suspicious activity detected"
    
    def _generate_explanation(
        self,
        features: Dict[str, float],
        feature_scores: Dict[str, float],
        patterns: List[Dict[str, Any]],
        risk_level: str
    ) -> Dict[str, Any]:
        """Generate human-readable explanation of classification."""
        
        explanation = {
            "risk_indicators": [],
            "normal_indicators": [],
            "detected_patterns": [],
        }
        
        # High-risk indicators
        if feature_scores.get("keystroke_anomaly", 0) > 0.6:
            explanation["risk_indicators"].append(
                f"Highly erratic keystroke pattern (variance: {feature_scores['keystroke_anomaly']:.1%})"
            )
        
        if feature_scores.get("network_activity", 0) > 0.6:
            explanation["risk_indicators"].append(
                f"Significant network activity (score: {feature_scores['network_activity']:.1%})"
            )
        
        if feature_scores.get("focus_anomaly", 0) > 0.6:
            explanation["risk_indicators"].append(
                f"Very low focus score ({1 - feature_scores['focus_anomaly']:.1%})"
            )
        
        if feature_scores.get("app_switching", 0) > 0.5:
            explanation["risk_indicators"].append(
                f"Excessive app switching ({features['app_switches']} switches)"
            )
        
        if feature_scores.get("voice_stress", 0) > 0.5:
            explanation["risk_indicators"].append(
                f"Significant voice stress detected"
            )
        
        # Normal indicators
        if features["focus_score"] > 0.7:
            explanation["normal_indicators"].append(f"Maintaining good focus ({features['focus_score']:.0%})")
        
        if features["cpu_usage"] < 60:
            explanation["normal_indicators"].append(f"Normal CPU usage ({features['cpu_usage']:.0f}%)")
        
        if features["keystroke_rhythm_variance"] < 0.3:
            explanation["normal_indicators"].append("Consistent keystroke pattern")
        
        # Detected patterns
        for pattern in patterns:
            explanation["detected_patterns"].append({
                "pattern": pattern.get("pattern_name", "Unknown"),
                "severity": pattern.get("severity", "unknown"),
                "description": pattern.get("description", ""),
            })
        
        return explanation
    
    def _get_recommendation(self, risk_level: str, patterns: List[Dict[str, Any]]) -> str:
        """Get recommended action based on risk level."""
        
        if risk_level == "critical":
            return "FLAG_IMMEDIATE - Stop exam and flag for review"
        elif risk_level == "high":
            return "FLAG_SERVER - Send to server for Gemini analysis"
        elif risk_level == "medium":
            return "MONITOR_CLOSE - Continue monitoring with increased sensitivity"
        elif risk_level == "low":
            return "CONTINUE_NORMAL - Normal monitoring"
        else:
            return "CONTINUE_NORMAL - No action needed"


class EnsembleClassifier:
    """Ensemble of multiple classifiers for robust decision-making."""
    
    def __init__(self):
        """Initialize ensemble classifiers."""
        self.primary_classifier = MLClassifier()
    
    def classify_ensemble(
        self,
        package: Dict[str, Any],
        patterns: List[Dict[str, Any]],
        historical_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Classify using ensemble method.
        
        Returns consensus with confidence.
        """
        # Primary ML classification
        primary_result = self.primary_classifier.classify(package, patterns)
        
        # Historical context adjustment
        if historical_context and historical_context.get("student_baseline"):
            adjusted_score = self._adjust_for_baseline(
                primary_result["suspicious_score"],
                historical_context["student_baseline"]
            )
            primary_result["suspicious_score_adjusted"] = adjusted_score
        
        return primary_result
    
    def _adjust_for_baseline(self, score: float, baseline: Dict[str, float]) -> float:
        """Adjust score based on student's historical baseline."""
        # If score is way above baseline, increase suspicion
        baseline_score = baseline.get("average_score", 0.2)
        baseline_std = baseline.get("std_dev", 0.1)
        
        z_score = (score - baseline_score) / (baseline_std + 0.001)
        
        # If z-score is high (>2.5), increase adjustment
        if z_score > 2.5:
            return min(1.0, score * 1.3)
        elif z_score > 1.5:
            return min(1.0, score * 1.15)
        else:
            return score
