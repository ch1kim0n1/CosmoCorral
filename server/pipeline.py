"""
Complete Data Pipeline: Ingest → Normalize → Aggregate → Detect → Analyze → Store

Handles the entire flow from raw student activity packages to flagged reports.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from collections import defaultdict, deque
import uuid
import statistics

import google.generativeai as genai
from db_init import db_connect, Device, Report

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

ANOMALY_THRESHOLDS = {
    "cpu_usage_high": 90.0,
    "memory_usage_high": 85.0,
    "keystroke_rhythm_variance_high": 0.75,
    "focus_score_low": 0.3,
    "app_switches_per_minute_high": 15,
    "network_bytes_30s_high": 10 * 1024 * 1024,  # 10 MB
}

RULES = {
    "resource_spike": {
        "enabled": True,
        "severity": "alert",
        "description": "Sudden spike in CPU/Memory/Network usage",
        "escalate_to_gemini": True,
    },
    "distraction_burst": {
        "enabled": True,
        "severity": "warning",
        "description": "Excessive app switching with low focus",
        "escalate_to_gemini": True,
    },
    "pause_inconsistent": {
        "enabled": True,
        "severity": "warning",
        "description": "Erratic keystroke/mouse pattern after pause",
        "escalate_to_gemini": True,
    },
    "network_anomaly": {
        "enabled": True,
        "severity": "critical",
        "description": "Unusual network activity detected",
        "escalate_to_gemini": True,
    },
    "focus_collapse": {
        "enabled": True,
        "severity": "alert",
        "description": "Sudden drop in focus score",
        "escalate_to_gemini": False,
    },
    "impossible_timeline": {
        "enabled": True,
        "severity": "critical",
        "description": "User activity inconsistent with physical possibilities",
        "escalate_to_gemini": True,
    },
}

# ============================================================================
# AGGREGATION ENGINE
# ============================================================================

class AggregationWindow:
    """Manages a time-window buffer for aggregating packages."""

    def __init__(self, window_size_seconds: int):
        self.window_size = window_size_seconds
        self.buffer: deque = deque()  # (timestamp, package)

    def add(self, timestamp: float, package: Dict[str, Any]):
        """Add a package to the window."""
        self.buffer.append((timestamp, package))
        cutoff = timestamp - self.window_size
        while self.buffer and self.buffer[0][0] < cutoff:
            self.buffer.popleft()

    def get_aggregated_stats(self) -> Dict[str, Any]:
        """Compute statistics over buffered packages."""
        if not self.buffer:
            return {}

        packages = [pkg for _, pkg in self.buffer]

        # Aggregate CPU usage
        cpu_values = [p.get("system_metrics", {}).get("cpu_usage", 0) for p in packages]
        # Aggregate focus scores
        focus_values = [p.get("focus_metrics", {}).get("focus_score", 0.5) for p in packages]
        # Aggregate network bytes
        net_sent = sum(p.get("network_activity", {}).get("bytes_sent", 0) for p in packages)
        net_recv = sum(p.get("network_activity", {}).get("bytes_received", 0) for p in packages)
        # App switches
        app_switches = sum(p.get("process_data", {}).get("app_switches", 0) for p in packages)
        # Keystroke rhythm variance
        keystroke_vars = [
            p.get("input_dynamics", {}).get("keystroke_rhythm_variance", 0)
            for p in packages
        ]

        return {
            "package_count": len(packages),
            "cpu_mean": statistics.mean(cpu_values) if cpu_values else 0,
            "cpu_max": max(cpu_values) if cpu_values else 0,
            "cpu_variance": statistics.variance(cpu_values) if len(cpu_values) > 1 else 0,
            "focus_mean": statistics.mean(focus_values) if focus_values else 0.5,
            "focus_min": min(focus_values) if focus_values else 0.5,
            "network_bytes_total": net_sent + net_recv,
            "app_switches_total": app_switches,
            "keystroke_rhythm_mean_variance": statistics.mean(keystroke_vars)
            if keystroke_vars
            else 0,
        }


class AggregationEngine:
    """Manages multiple time windows for efficient anomaly detection."""

    def __init__(self):
        self.windows_30s = defaultdict(lambda: AggregationWindow(30))
        self.windows_60s = defaultdict(lambda: AggregationWindow(60))
        self.windows_5m = defaultdict(lambda: AggregationWindow(300))

    def ingest(self, session_id: str, device_id: str, package: Dict[str, Any]):
        """Add package to all time windows."""
        timestamp = datetime.fromisoformat(package["timestamp"]).timestamp()
        key = f"{session_id}:{device_id}"

        self.windows_30s[key].add(timestamp, package)
        self.windows_60s[key].add(timestamp, package)
        self.windows_5m[key].add(timestamp, package)

    def get_stats(self, session_id: str, device_id: str, window_name: str) -> Dict[str, Any]:
        """Get aggregated stats for a specific window."""
        key = f"{session_id}:{device_id}"

        if window_name == "30s":
            return self.windows_30s[key].get_aggregated_stats()
        elif window_name == "60s":
            return self.windows_60s[key].get_aggregated_stats()
        elif window_name == "5m":
            return self.windows_5m[key].get_aggregated_stats()
        return {}


# ============================================================================
# ANOMALY DETECTION
# ============================================================================

class AnomalyDetector:
    """Detects anomalies in individual signals."""

    def __init__(self):
        self.baselines = defaultdict(
            lambda: {"mean": 0, "std_dev": 1, "count": 0}
        )  # Per (session, signal)

    def compute_z_score(self, session_id: str, signal_name: str, value: float) -> float:
        """Compute z-score against baseline."""
        baseline = self.baselines[f"{session_id}:{signal_name}"]
        if baseline["std_dev"] == 0:
            baseline["std_dev"] = 1
        return (value - baseline["mean"]) / baseline["std_dev"]

    def update_baseline(
        self, session_id: str, signal_name: str, value: float
    ):
        """Update running baseline (exponential moving average)."""
        key = f"{session_id}:{signal_name}"
        baseline = self.baselines[key]

        if baseline["count"] == 0:
            baseline["mean"] = value
            baseline["count"] = 1
        else:
            # Exponential moving average
            alpha = 0.1
            baseline["mean"] = alpha * value + (1 - alpha) * baseline["mean"]
            baseline["count"] += 1

    def detect_anomalies(
        self, session_id: str, package: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Detect anomalies in a single package."""
        anomalies = []

        # CPU usage
        cpu = package.get("system_metrics", {}).get("cpu_usage", 0)
        if cpu > ANOMALY_THRESHOLDS["cpu_usage_high"]:
            z = self.compute_z_score(session_id, "cpu_usage", cpu)
            anomalies.append(
                {
                    "signal_name": "cpu_usage",
                    "modality": "system",
                    "raw_value": cpu,
                    "baseline_expected": self.baselines[f"{session_id}:cpu_usage"]["mean"],
                    "z_score": z,
                    "percentile_anomaly": min(1.0, abs(z) / 3.0),
                    "threshold_breached": True,
                    "breach_magnitude": cpu
                    - ANOMALY_THRESHOLDS["cpu_usage_high"],
                    "reason": f"CPU usage {cpu}% exceeds threshold {ANOMALY_THRESHOLDS['cpu_usage_high']}%",
                    "severity": "high" if cpu > 95 else "medium",
                }
            )
        self.update_baseline(session_id, "cpu_usage", cpu)

        # Focus score
        focus = package.get("focus_metrics", {}).get("focus_score", 0.5)
        if focus < ANOMALY_THRESHOLDS["focus_score_low"]:
            z = self.compute_z_score(session_id, "focus_score", focus)
            anomalies.append(
                {
                    "signal_name": "focus_score",
                    "modality": "focus",
                    "raw_value": focus,
                    "baseline_expected": self.baselines[f"{session_id}:focus_score"]["mean"],
                    "z_score": z,
                    "percentile_anomaly": 1.0 - focus,
                    "threshold_breached": True,
                    "breach_magnitude": ANOMALY_THRESHOLDS["focus_score_low"] - focus,
                    "reason": f"Focus score {focus:.2f} drops below threshold {ANOMALY_THRESHOLDS['focus_score_low']}",
                    "severity": "alert" if focus < 0.2 else "warning",
                }
            )
        self.update_baseline(session_id, "focus_score", focus)

        # Network activity
        net_sent = package.get("network_activity", {}).get("bytes_sent", 0)
        net_recv = package.get("network_activity", {}).get("bytes_received", 0)
        net_total = net_sent + net_recv
        if net_total > ANOMALY_THRESHOLDS["network_bytes_30s_high"]:
            anomalies.append(
                {
                    "signal_name": "network_activity",
                    "modality": "network",
                    "raw_value": net_total,
                    "baseline_expected": self.baselines[f"{session_id}:network_activity"][
                        "mean"
                    ],
                    "z_score": self.compute_z_score(session_id, "network_activity", net_total),
                    "percentile_anomaly": min(1.0, net_total / (50 * 1024 * 1024)),
                    "threshold_breached": True,
                    "breach_magnitude": net_total
                    - ANOMALY_THRESHOLDS["network_bytes_30s_high"],
                    "reason": f"Network activity {net_total / 1024 / 1024:.2f}MB exceeds baseline",
                    "severity": "critical",
                }
            )
        self.update_baseline(session_id, "network_activity", net_total)

        # Keystroke rhythm variance
        keystroke_var = (
            package.get("input_dynamics", {}).get("keystroke_rhythm_variance", 0)
        )
        if keystroke_var > ANOMALY_THRESHOLDS["keystroke_rhythm_variance_high"]:
            anomalies.append(
                {
                    "signal_name": "keystroke_rhythm",
                    "modality": "input",
                    "raw_value": keystroke_var,
                    "baseline_expected": self.baselines[f"{session_id}:keystroke_rhythm"][
                        "mean"
                    ],
                    "z_score": self.compute_z_score(
                        session_id, "keystroke_rhythm", keystroke_var
                    ),
                    "percentile_anomaly": keystroke_var,
                    "threshold_breached": True,
                    "breach_magnitude": keystroke_var
                    - ANOMALY_THRESHOLDS["keystroke_rhythm_variance_high"],
                    "reason": "Keystroke rhythm highly erratic (possible impersonation)",
                    "severity": "high",
                }
            )
        self.update_baseline(session_id, "keystroke_rhythm", keystroke_var)

        return anomalies


# ============================================================================
# RULES ENGINE
# ============================================================================

class RulesEngine:
    """Evaluates rules to decide if package should be escalated to Gemini."""

    def __init__(self):
        self.anomaly_detector = AnomalyDetector()
        self.agg_engine = AggregationEngine()

    def evaluate(
        self,
        session_id: str,
        device_id: str,
        package: Dict[str, Any],
        anomalies: List[Dict[str, Any]],
    ) -> tuple[List[Dict[str, Any]], bool]:
        """
        Evaluate rules against package and anomalies.

        Returns: (triggered_rules, should_escalate_to_gemini)
        """
        triggered_rules = []

        # Rule: Resource Spike
        if any(a["signal_name"] in ["cpu_usage", "network_activity"] for a in anomalies):
            triggered_rules.append(
                {
                    "rule_id": "resource_spike",
                    "rule_name": "Resource Spike",
                    "description": RULES["resource_spike"]["description"],
                    "severity": RULES["resource_spike"]["severity"],
                    "evidence": [a["reason"] for a in anomalies if a["signal_name"] in ["cpu_usage", "network_activity"]],
                }
            )

        # Rule: Distraction Burst
        app_switches = package.get("process_data", {}).get("app_switches", 0)
        if app_switches > ANOMALY_THRESHOLDS["app_switches_per_minute_high"]:
            focus = package.get("focus_metrics", {}).get("focus_score", 0.5)
            if focus < ANOMALY_THRESHOLDS["focus_score_low"]:
                triggered_rules.append(
                    {
                        "rule_id": "distraction_burst",
                        "rule_name": "Distraction Burst",
                        "description": RULES["distraction_burst"]["description"],
                        "severity": RULES["distraction_burst"]["severity"],
                        "evidence": [
                            f"App switches: {app_switches}",
                            f"Focus score: {focus:.2f}",
                        ],
                    }
                )

        # Rule: Keystroke Pause Inconsistency
        keystroke_var = package.get("input_dynamics", {}).get("keystroke_rhythm_variance", 0)
        mouse_idle = package.get("input_dynamics", {}).get("mouse_idle_duration", 0)
        if keystroke_var > ANOMALY_THRESHOLDS["keystroke_rhythm_variance_high"] and mouse_idle > 20:
            triggered_rules.append(
                {
                    "rule_id": "pause_inconsistent",
                    "rule_name": "Pause Inconsistency",
                    "description": RULES["pause_inconsistent"]["description"],
                    "severity": RULES["pause_inconsistent"]["severity"],
                    "evidence": [
                        f"Keystroke variance: {keystroke_var:.2f}",
                        f"Mouse idle: {mouse_idle}s",
                    ],
                }
            )

        # Rule: Network Anomaly
        if any(a["signal_name"] == "network_activity" and a["severity"] == "critical" for a in anomalies):
            triggered_rules.append(
                {
                    "rule_id": "network_anomaly",
                    "rule_name": "Network Anomaly",
                    "description": RULES["network_anomaly"]["description"],
                    "severity": RULES["network_anomaly"]["severity"],
                    "evidence": [a["reason"] for a in anomalies if a["signal_name"] == "network_activity"],
                }
            )

        # Determine if should escalate to Gemini
        should_escalate = any(rule["severity"] in ["alert", "critical"] for rule in triggered_rules)

        return triggered_rules, should_escalate


# ============================================================================
# GEMINI API INTEGRATION
# ============================================================================

class GeminiAnalyzer:
    """Analyzes flagged packages using Gemini API."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_available = False
        if api_key and api_key != "API_IS_NOT_PROVIDED":
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel("gemini-1.5-flash")
                self.api_available = True
                logger.info("✅ Gemini API configured successfully")
            except Exception as e:
                logger.warning(f"⚠️ Failed to configure Gemini API: {e}. Using fallback analysis.")
                self.api_available = False
        else:
            logger.warning("⚠️ GEMINI_API_KEY not provided. Using fallback analysis.")

    async def analyze(
        self,
        package: Dict[str, Any],
        anomalies: List[Dict[str, Any]],
        triggered_rules: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Analyze flagged activity using Gemini or fallback logic."""

        # If API is not available, use fallback analysis
        if not self.api_available:
            return self._fallback_analysis(package, anomalies, triggered_rules)

        # Build prompt
        anomalies_text = "\n".join(
            [f"- {a['reason']} (severity: {a['severity']})" for a in anomalies]
        )
        rules_text = "\n".join([f"- {r['rule_name']}: {r['description']}" for r in triggered_rules])

        prompt = f"""You are an academic integrity AI analyzing student activity during a proctored exam.

STUDENT ACTIVITY SNAPSHOT:
- Active Application: {package.get('process_data', {}).get('window_title', 'Unknown')}
- CPU Usage: {package.get('system_metrics', {}).get('cpu_usage', 0)}%
- Focus Score: {package.get('focus_metrics', {}).get('focus_score', 0.5):.2f} (0=distracted, 1=focused)
- App Switches: {package.get('process_data', {}).get('app_switches', 0)}
- Network Sent: {package.get('network_activity', {}).get('bytes_sent', 0) / 1024 / 1024:.2f} MB
- Keystroke Rhythm Variance: {package.get('input_dynamics', {}).get('keystroke_rhythm_variance', 0):.2f} (0=consistent, 1=erratic)
- Mouse Idle: {package.get('input_dynamics', {}).get('mouse_idle_duration', 0)}s

ANOMALIES DETECTED:
{anomalies_text}

TRIGGERED RULES:
{rules_text}

Based on this data, determine if there's suspicious activity.

Respond ONLY with valid JSON (no markdown, no extra text):
{{
  "suspected_activity": "unauthorized_resource_access | impersonation | tab_switching_excessive | copy_paste_detected | network_exfiltration_attempt | stress_response | technical_issue | legitimate_multitasking | none",
  "confidence": 0.0-1.0,
  "why_suspected": "1-2 sentence explanation",
  "evidence": ["specific evidence 1", "specific evidence 2"],
  "recommendation": "action professor should take",
  "alternative_explanations": ["possible explanation 1", "possible explanation 2"]
}}
"""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()

            # Remove markdown code blocks if present
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()
            if text.endswith("```"):
                text = text[:-3].strip()

            analysis = json.loads(text)
            analysis["tokens_used"] = response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
            analysis["model_version"] = "gemini-1.5-flash"
            analysis["analyzed_at"] = datetime.utcnow().isoformat()

            logger.info(f"Gemini analysis: {analysis['suspected_activity']} (confidence: {analysis['confidence']})")
            return analysis
        except (json.JSONDecodeError, ValueError, AttributeError) as e:
            logger.error(f"Gemini analysis failed: {e}")
            return {
                "suspected_activity": "technical_issue",
                "confidence": 0.0,
                "why_suspected": "Analysis service error",
                "evidence": [str(e)],
                "recommendation": "Review manually",
                "alternative_explanations": [],
                "tokens_used": 0,
                "model_version": "gemini-1.5-flash",
                "analyzed_at": datetime.utcnow().isoformat(),
            }

    def _fallback_analysis(
        self,
        package: Dict[str, Any],
        anomalies: List[Dict[str, Any]],
        triggered_rules: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Simple rule-based analysis when Gemini API is not available."""
        
        # Determine suspected activity based on anomalies and rules
        high_severity_count = sum(1 for a in anomalies if a.get('severity') == 'critical')
        alert_count = sum(1 for r in triggered_rules if r.get('severity') == 'alert')
        
        # Simple heuristic analysis
        suspected_activity = "none"
        confidence = 0.0
        why_suspected = "API IS NOT PROVIDED - Using basic rule-based detection"
        evidence = []
        recommendation = "Review student activity manually"
        
        # Check for high network usage
        network_bytes = package.get('network_activity', {}).get('bytes_sent', 0)
        if network_bytes > 5 * 1024 * 1024:  # 5MB
            suspected_activity = "network_exfiltration_attempt"
            confidence = 0.6
            evidence.append(f"High network upload: {network_bytes / 1024 / 1024:.2f} MB")
        
        # Check for excessive app switching
        app_switches = package.get('process_data', {}).get('app_switches', 0)
        if app_switches > 10:
            suspected_activity = "tab_switching_excessive"
            confidence = 0.5
            evidence.append(f"Excessive app switches: {app_switches}")
        
        # Check for low focus with high activity
        focus_score = package.get('focus_metrics', {}).get('focus_score', 0.5)
        if focus_score < 0.3 and high_severity_count > 0:
            suspected_activity = "unauthorized_resource_access"
            confidence = 0.4
            evidence.append(f"Low focus score: {focus_score:.2f}")
        
        # Check CPU/Memory spikes
        cpu_usage = package.get('system_metrics', {}).get('cpu_usage', 0)
        memory_usage = package.get('system_metrics', {}).get('memory_usage', 0)
        if cpu_usage > 90 or memory_usage > 85:
            if suspected_activity == "none":
                suspected_activity = "technical_issue"
                confidence = 0.3
            evidence.append(f"Resource spike - CPU: {cpu_usage}%, Memory: {memory_usage}%")
        
        # Add anomaly descriptions to evidence
        for anomaly in anomalies[:3]:  # Top 3 anomalies
            evidence.append(anomaly.get('reason', 'Unknown anomaly'))
        
        return {
            "suspected_activity": suspected_activity,
            "confidence": confidence,
            "why_suspected": why_suspected,
            "evidence": evidence if evidence else ["No significant anomalies detected"],
            "recommendation": recommendation,
            "alternative_explanations": [
                "Normal exam behavior",
                "Technical system issue",
                "Background processes"
            ],
            "tokens_used": 0,
            "model_version": "fallback-rule-based",
            "analyzed_at": datetime.utcnow().isoformat(),
        }


# ============================================================================
# MAIN PIPELINE
# ============================================================================

class MonitoringPipeline:
    """Complete data processing pipeline."""

    def __init__(self, gemini_api_key: str):
        self.db = db_connect()
        self.anomaly_detector = AnomalyDetector()
        self.agg_engine = AggregationEngine()
        self.rules_engine = RulesEngine()
        self.gemini_analyzer = GeminiAnalyzer(gemini_api_key)
        self.professors_connected = {}  # Map of professor to WebSocket connection

    async def process_package(
        self,
        package: Dict[str, Any],
        professor_broadcast_callback=None,
    ) -> Optional[Dict[str, Any]]:
        """
        Process a student activity package through the complete pipeline.

        Returns: FlaggedReport if flagged, None otherwise
        """

        session_id = package["session_id"]
        device_id = package["device_id"]
        student_id = package["student_id"]
        timestamp = package["timestamp"]

        # 1. Normalize & validate (already done by client)
        logger.info(
            f"Processing package from {student_id} on device {device_id}"
        )

        # 2. Store raw package
        report_data = {
            "session_id": session_id,
            "student_id": student_id,
            "timestamp": datetime.fromisoformat(timestamp),
            "reason": "raw_activity",
            "message": "Raw activity package",
            "data": package,
        }

        # Find device and associate
        device = Device.get_or_none(Device.id == device_id)
        if device:
            report = Report.create(device=device, **report_data)
            logger.debug(f"Stored raw package: {report.id}")

        # 3. Add to aggregation windows
        self.agg_engine.ingest(session_id, device_id, package)

        # 4. Detect anomalies
        anomalies = self.anomaly_detector.detect_anomalies(session_id, package)

        # 5. Evaluate rules
        triggered_rules, should_escalate = self.rules_engine.evaluate(
            session_id, device_id, package, anomalies
        )

        # 6. Conditional Gemini analysis
        gemini_analysis = None
        if should_escalate:
            gemini_analysis = await self.gemini_analyzer.analyze(
                package, anomalies, triggered_rules
            )
            logger.info(f"Gemini flagged: {gemini_analysis['suspected_activity']}")

        # 7. Create flagged report if needed
        flagged_report = None
        if should_escalate and gemini_analysis:
            flagged_report = {
                "id": str(uuid.uuid4()),
                "package_id": package.get("package_id", str(uuid.uuid4())),
                "session_id": session_id,
                "timestamp": timestamp,
                "device_id": device_id,
                "student_id": student_id,
                "anomalies": anomalies,
                "composite_anomaly_score": {
                    "overall_score": statistics.mean(
                        [a["percentile_anomaly"] for a in anomalies]
                    )
                    if anomalies
                    else 0.0,
                    "signal_scores": anomalies,
                    "dominant_anomalies": [a["signal_name"] for a in anomalies[:3]],
                    "cross_signal_patterns": [],
                    "timestamp": timestamp,
                },
                "triggered_rules": triggered_rules,
                "gemini_analysis": gemini_analysis,
                "status": "new",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }

            # Store flagged report
            flagged_report_data = {
                "session_id": session_id,
                "student_id": student_id,
                "timestamp": datetime.fromisoformat(timestamp),
                "reason": "flagged_activity",
                "message": f"Flagged: {gemini_analysis['suspected_activity']}",
                "data": flagged_report,
            }
            if device:
                flagged_db_record = Report.create(device=device, **flagged_report_data)
                logger.info(f"Stored flagged report: {flagged_db_record.id}")

            # 8. Broadcast to professor dashboard
            if professor_broadcast_callback:
                await professor_broadcast_callback(flagged_report)

        return flagged_report


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_pipeline_instance: Optional[MonitoringPipeline] = None


def get_pipeline() -> MonitoringPipeline:
    """Get or create the monitoring pipeline."""
    global _pipeline_instance
    if _pipeline_instance is None:
        import os

        gemini_key = os.getenv("GEMINI_API_KEY", "API_IS_NOT_PROVIDED")
        _pipeline_instance = MonitoringPipeline(gemini_key)
    return _pipeline_instance
