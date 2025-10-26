"""
Flag Data Generator: Creates standardized data files for flagged suspicious activities.

Generates:
- JSON flag files for server analysis
- Metadata about flag detection confidence
- Historical context for pattern matching
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import uuid


class FlagDataGenerator:
    """Generates standardized flagged data files."""
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize flag data generator.
        
        Args:
            output_dir: Directory to save flag files (default: ./flag_data/)
        """
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(__file__), "..", "flag_data")
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.flagged_sessions: Dict[str, List[Dict[str, Any]]] = {}
    
    def create_flag_file(
        self,
        package: Dict[str, Any],
        classification: Dict[str, Any],
        patterns: List[Dict[str, Any]],
        session_id: str,
        student_id: str,
    ) -> Dict[str, Any]:
        """
        Create a standardized flag file for suspicious activity.
        
        Args:
            package: Original activity package
            classification: ML classification result
            patterns: Detected patterns
            session_id: Exam session ID
            student_id: Student identifier
            
        Returns:
            Flag file metadata
        """
        flag_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        # Build flag data structure
        flag_data = {
            "flag_id": flag_id,
            "timestamp": timestamp.isoformat(),
            "session_id": session_id,
            "student_id": student_id,
            "risk_assessment": {
                "risk_level": classification.get("risk_level"),
                "risk_label": classification.get("risk_label"),
                "suspicious_score": classification.get("suspicious_score"),
                "confidence": classification.get("confidence", 0.0) if isinstance(classification, dict) else 0.0,
                "should_flag": classification.get("should_flag", False),
                "recommendation": classification.get("recommendation"),
            },
            "detected_patterns": patterns,
            "feature_analysis": {
                "analyzed_features": classification.get("features_analyzed", {}),
                "feature_scores": classification.get("feature_scores", {}),
            },
            "explanation": classification.get("explanation", {}),
            "original_package_summary": self._summarize_package(package),
            "activity_snapshot": {
                "active_application": package.get("process_data", {}).get("window_title", "Unknown"),
                "focus_score": package.get("focus_metrics", {}).get("focus_score", 0.0),
                "keystroke_variance": package.get("input_dynamics", {}).get("keystroke_rhythm_variance", 0.0),
                "network_bytes_total": (
                    package.get("network_activity", {}).get("bytes_sent", 0) +
                    package.get("network_activity", {}).get("bytes_received", 0)
                ),
                "cpu_usage": package.get("system_metrics", {}).get("cpu_usage", 0.0),
                "app_switches": package.get("process_data", {}).get("app_switches", 0),
                "stress_indicators": self._calculate_stress_indicators(package),
            },
            "severity_justification": self._generate_justification(patterns, classification),
            "server_analysis_needed": classification.get("should_flag", False),
        }
        
        # Save flag file
        filename = self._save_flag_file(flag_data, session_id, student_id)
        
        # Track in memory
        if session_id not in self.flagged_sessions:
            self.flagged_sessions[session_id] = []
        self.flagged_sessions[session_id].append({
            "flag_id": flag_id,
            "filename": filename,
            "timestamp": timestamp,
            "risk_level": classification.get("risk_level"),
        })
        
        return {
            "flag_id": flag_id,
            "filename": filename,
            "data": flag_data,
        }
    
    def create_batch_flag_report(
        self,
        session_id: str,
        student_id: str,
        flags: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Create a batch report of multiple flags in a session.
        
        Args:
            session_id: Session identifier
            student_id: Student identifier
            flags: List of individual flags
            
        Returns:
            Batch report metadata
        """
        report_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        report = {
            "report_id": report_id,
            "timestamp": timestamp.isoformat(),
            "session_id": session_id,
            "student_id": student_id,
            "total_flags": len(flags),
            "critical_count": sum(1 for f in flags if f.get("risk_level") == "critical"),
            "high_count": sum(1 for f in flags if f.get("risk_level") == "high"),
            "medium_count": sum(1 for f in flags if f.get("risk_level") == "medium"),
            "flags": flags,
            "summary": self._generate_batch_summary(flags),
            "recommendation": self._get_batch_recommendation(flags),
        }
        
        # Save batch report
        filename = self._save_batch_report(report, session_id)
        
        return {
            "report_id": report_id,
            "filename": filename,
            "report": report,
        }
    
    def get_session_flags(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all flags for a session."""
        return self.flagged_sessions.get(session_id, [])
    
    def get_flag_file_path(self, flag_id: str) -> Optional[Path]:
        """Get path to a flag file by ID."""
        for session_dir in self.output_dir.iterdir():
            if session_dir.is_dir():
                flag_file = session_dir / f"{flag_id}.json"
                if flag_file.exists():
                    return flag_file
        return None
    
    def _save_flag_file(self, flag_data: Dict[str, Any], session_id: str, student_id: str) -> str:
        """Save individual flag file to disk."""
        session_dir = self.output_dir / session_id
        session_dir.mkdir(exist_ok=True)
        
        filename = f"{flag_data['flag_id']}.json"
        filepath = session_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(flag_data, f, indent=2)
        
        return str(filepath)
    
    def _save_batch_report(self, report: Dict[str, Any], session_id: str) -> str:
        """Save batch report to disk."""
        session_dir = self.output_dir / session_id
        session_dir.mkdir(exist_ok=True)
        
        filename = f"batch_report_{report['report_id']}.json"
        filepath = session_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        return str(filepath)
    
    def _summarize_package(self, package: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of the original package."""
        return {
            "package_id": package.get("package_id"),
            "device_id": package.get("device_id"),
            "timestamp": package.get("timestamp"),
            "session_id": package.get("session_id"),
            "student_id": package.get("student_id"),
        }
    
    def _calculate_stress_indicators(self, package: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate multiple stress indicators."""
        return {
            "keystroke_erraticism": package.get("input_dynamics", {}).get("keystroke_rhythm_variance", 0.0),
            "mouse_velocity": package.get("input_dynamics", {}).get("mouse_velocity", 0.0),
            "voice_sentiment": package.get("voice_metrics", {}).get("sentiment_score", 0.0),
            "eye_contact": package.get("focus_metrics", {}).get("eye_contact_percentage", 0.0),
            "calculated_stress_level": self._compute_stress_level(package),
        }
    
    def _compute_stress_level(self, package: Dict[str, Any]) -> float:
        """Compute overall stress level (0-1)."""
        stress = 0.0
        
        # Keystroke erraticism
        keystroke_var = package.get("input_dynamics", {}).get("keystroke_rhythm_variance", 0.0)
        stress += min(1.0, keystroke_var) * 0.4
        
        # Mouse velocity (jerky = stressed)
        mouse_velocity = package.get("input_dynamics", {}).get("mouse_velocity", 0.0)
        stress += min(1.0, mouse_velocity / 100) * 0.3
        
        # Voice sentiment
        voice_sentiment = package.get("voice_metrics", {}).get("sentiment_score", 0.0)
        if voice_sentiment < 0:
            stress += abs(voice_sentiment) * 0.3
        
        return min(1.0, stress)
    
    def _generate_justification(self, patterns: List[Dict[str, Any]], classification: Dict[str, Any]) -> str:
        """Generate human-readable justification for flag severity."""
        risk_level = classification.get("risk_level", "unknown")
        
        if risk_level == "critical":
            pattern_names = [p.get("pattern_name", "Unknown") for p in patterns]
            return f"CRITICAL: Multiple high-severity patterns detected: {', '.join(pattern_names)}. Possible impersonation or data exfiltration."
        
        elif risk_level == "high":
            risk_indicators = classification.get("explanation", {}).get("risk_indicators", [])
            return f"HIGH: {len(risk_indicators)} risk indicators detected. Primary concerns: {'; '.join(risk_indicators[:2])}"
        
        elif risk_level == "medium":
            return "MEDIUM: Some suspicious indicators detected. Recommend closer monitoring or manual review."
        
        else:
            return "LOW: Activity appears legitimate with minimal suspicious indicators."
    
    def _generate_batch_summary(self, flags: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary for batch report."""
        if not flags:
            return {"summary": "No flags detected"}
        
        pattern_types = {}
        for flag in flags:
            patterns = flag.get("detected_patterns", [])
            for pattern in patterns:
                pattern_name = pattern.get("pattern_name", "Unknown")
                pattern_types[pattern_name] = pattern_types.get(pattern_name, 0) + 1
        
        return {
            "flags_by_risk": {
                "critical": sum(1 for f in flags if f.get("risk_level") == "critical"),
                "high": sum(1 for f in flags if f.get("risk_level") == "high"),
                "medium": sum(1 for f in flags if f.get("risk_level") == "medium"),
                "low": sum(1 for f in flags if f.get("risk_level") == "low"),
            },
            "pattern_frequency": pattern_types,
            "average_suspicion_score": sum(f.get("suspicious_score", 0) for f in flags) / len(flags) if flags else 0.0,
        }
    
    def _get_batch_recommendation(self, flags: List[Dict[str, Any]]) -> str:
        """Get overall recommendation for batch."""
        if not flags:
            return "No flags detected - continue normal monitoring"
        
        critical_count = sum(1 for f in flags if f.get("risk_level") == "critical")
        high_count = sum(1 for f in flags if f.get("risk_level") == "high")
        
        if critical_count > 0:
            return f"🚨 IMMEDIATE ACTION: {critical_count} critical flags detected. Exam should be stopped and reviewed."
        elif high_count >= 2:
            return f"⚠️ ESCALATE TO SERVER: {high_count} high-risk flags detected. Send to Gemini for analysis."
        elif high_count == 1:
            return "Send to server for analysis. Monitor remaining session closely."
        else:
            return "Monitor session. Continue with normal detection."


class FlagDataCache:
    """Caches flag data for quick access during session."""
    
    def __init__(self, max_cache_size: int = 1000):
        """Initialize cache."""
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_cache_size = max_cache_size
        self.access_count = 0
    
    def cache_flag(self, flag_id: str, flag_data: Dict[str, Any]) -> None:
        """Cache a flag."""
        if len(self.cache) >= self.max_cache_size:
            # Remove oldest entries (simple FIFO)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[flag_id] = flag_data
    
    def get_flag(self, flag_id: str) -> Optional[Dict[str, Any]]:
        """Get a flag from cache."""
        self.access_count += 1
        return self.cache.get(flag_id)
    
    def get_all_flags(self) -> List[Dict[str, Any]]:
        """Get all cached flags."""
        return list(self.cache.values())
    
    def clear(self) -> None:
        """Clear cache."""
        self.cache.clear()
        self.access_count = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cached_flags": len(self.cache),
            "max_size": self.max_cache_size,
            "total_accesses": self.access_count,
            "usage_percent": (len(self.cache) / self.max_cache_size) * 100,
        }
