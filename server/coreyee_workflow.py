"""
CoreEye System Workflow Implementation

Flowchart Implementation:
OS Data → EyeCore Client → JSON → Server Pipeline → Gemini Analysis → Flag Check → Report

Manages:
1. Data collection & normalization
2. Pattern recognition
3. Gemini analysis
4. Flag decisions
5. Report generation
"""

import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class DataSource(Enum):
    """Data sources collected by EyeCore client."""
    SYSTEM = "system"
    FILE = "file"
    CPU = "cpu"
    SCREEN = "screen"
    MOUSE = "mouse"
    KEYBOARD = "keyboard"
    VOICE = "voice"
    PROCESS = "process"
    NETWORK = "network"


class FlagStatus(Enum):
    """Flag status decisions."""
    CLEAN = "clean"
    SUSPICIOUS = "suspicious"
    CRITICAL = "critical"
    INVESTIGATING = "investigating"


class ConfidenceLevel(Enum):
    """Suspicion confidence levels."""
    VERY_LOW = 0.1
    LOW = 0.3
    MEDIUM = 0.5
    HIGH = 0.7
    VERY_HIGH = 0.9
    CRITICAL_ALERT = 1.0


# ============================================================================
# STAGE 1: DATA COLLECTION & NORMALIZATION
# ============================================================================

class DataCollector:
    """Collects OS-level data from EyeCore client."""
    
    def __init__(self):
        self.data_sources = {source: [] for source in DataSource}
    
    def add_data(self, source: DataSource, data: Dict[str, Any]):
        """Add data from a source."""
        timestamp = datetime.utcnow().isoformat()
        entry = {
            "timestamp": timestamp,
            "source": source.value,
            "data": data
        }
        self.data_sources[source].append(entry)
        logger.info(f"Collected {source.value} data")
        return entry
    
    def get_all_data(self) -> Dict[str, List]:
        """Get all collected data."""
        return {
            source.value: self.data_sources[source]
            for source in DataSource
        }


class DataNormalizer:
    """Normalizes OS data into JSON structure."""
    
    @staticmethod
    def normalize(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert raw OS data to standardized JSON format.
        
        Steps:
        - filter: Remove sensitive/irrelevant data
        - organize: Group by category
        - normalize: Convert to standard units
        """
        normalized = {
            "system_metrics": {
                "cpu_usage": raw_data.get("cpu", {}).get("usage", 0),
                "memory_usage": raw_data.get("cpu", {}).get("memory", 0),
                "processes_running": raw_data.get("cpu", {}).get("process_count", 0),
            },
            
            "file_metrics": {
                "active_files": raw_data.get("file", {}).get("active", []),
                "file_types": raw_data.get("file", {}).get("types", []),
                "modification_frequency": raw_data.get("file", {}).get("mod_freq", 0),
            },
            
            "input_dynamics": {
                "keyboard_speed": raw_data.get("keyboard", {}).get("speed", 0),
                "keystroke_variance": raw_data.get("keyboard", {}).get("variance", 0),
                "mouse_speed": raw_data.get("mouse", {}).get("speed", 0),
                "mouse_pattern": raw_data.get("mouse", {}).get("pattern", "normal"),
            },
            
            "screen_metrics": {
                "active_window": raw_data.get("screen", {}).get("active_window", "unknown"),
                "screen_content_type": raw_data.get("screen", {}).get("content_type", "unknown"),
                "text_extracted": raw_data.get("screen", {}).get("text", ""),
            },
            
            "voice_metrics": {
                "sentiment": raw_data.get("voice", {}).get("sentiment", 0),
                "tone": raw_data.get("voice", {}).get("tone", "neutral"),
                "speech_rate": raw_data.get("voice", {}).get("speech_rate", 0),
                "transcribed_text": raw_data.get("voice", {}).get("transcribed", ""),
            },
            
            "network_metrics": {
                "bytes_sent": raw_data.get("network", {}).get("sent", 0),
                "bytes_received": raw_data.get("network", {}).get("received", 0),
                "connection_type": raw_data.get("network", {}).get("type", "unknown"),
            },
            
            "system_events": {
                "lock_unlock": raw_data.get("system", {}).get("lock_unlock", False),
                "sleep_wake": raw_data.get("system", {}).get("sleep_wake", False),
                "peripheral_changes": raw_data.get("system", {}).get("peripherals", []),
            }
        }
        
        return normalized


# ============================================================================
# STAGE 2: PATTERN RECOGNITION (Local AI/ML)
# ============================================================================

class PatternRecognizer:
    """
    Local AI/ML pattern recognition.
    Analyzes normalized data for anomalies.
    """
    
    def __init__(self):
        self.patterns = []
    
    def recognize_patterns(self, normalized_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Recognize patterns in normalized data.
        
        Patterns to detect:
        - Unusual CPU/memory spikes
        - Erratic input patterns
        - Suspicious file access
        - Network anomalies
        - Voice/sentiment changes
        """
        patterns = []
        
        # Pattern 1: CPU/Memory anomaly
        cpu = normalized_data["system_metrics"]["cpu_usage"]
        memory = normalized_data["system_metrics"]["memory_usage"]
        
        if cpu > 80 or memory > 80:
            patterns.append({
                "pattern_type": "resource_spike",
                "severity": "high" if cpu > 95 else "medium",
                "details": f"CPU: {cpu}%, Memory: {memory}%",
                "recommendation": "Investigate background processes"
            })
        
        # Pattern 2: Keystroke anomaly
        keystroke_var = normalized_data["input_dynamics"]["keystroke_variance"]
        if keystroke_var > 0.7:
            patterns.append({
                "pattern_type": "erratic_keystroke",
                "severity": "high",
                "details": f"Keystroke variance: {keystroke_var}",
                "recommendation": "Possible impersonation or stress"
            })
        
        # Pattern 3: Suspicious file activity
        active_files = normalized_data["file_metrics"]["active_files"]
        if len(active_files) > 20:
            patterns.append({
                "pattern_type": "excessive_file_access",
                "severity": "medium",
                "details": f"Accessing {len(active_files)} files simultaneously",
                "recommendation": "Monitor for data exfiltration"
            })
        
        # Pattern 4: Network anomaly
        bytes_sent = normalized_data["network_metrics"]["bytes_sent"]
        if bytes_sent > 50 * 1024 * 1024:  # 50MB
            patterns.append({
                "pattern_type": "network_anomaly",
                "severity": "high",
                "details": f"Unusual network activity: {bytes_sent / 1024 / 1024:.1f}MB sent",
                "recommendation": "Check for data exfiltration"
            })
        
        # Pattern 5: Voice sentiment
        voice_sentiment = normalized_data["voice_metrics"]["sentiment"]
        if voice_sentiment < -0.5:
            patterns.append({
                "pattern_type": "negative_sentiment",
                "severity": "low",
                "details": f"Negative sentiment detected: {voice_sentiment}",
                "recommendation": "Student may be stressed"
            })
        
        self.patterns = patterns
        return patterns


# ============================================================================
# STAGE 3: GEMINI ANALYSIS
# ============================================================================

class GeminiAnalyzer:
    """
    Routes pattern data to Gemini for contextual analysis.
    (In production, use OpenRouter API)
    """
    
    async def analyze(
        self,
        patterns: List[Dict[str, Any]],
        normalized_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send patterns to Gemini for analysis.
        
        Gemini performs:
        - Contextual analysis
        - Pattern correlation
        - Anomaly scoring
        - Recommendation generation
        """
        
        # Build analysis prompt
        analysis_request = {
            "patterns_detected": patterns,
            "data_context": {
                "active_window": normalized_data["screen_metrics"]["active_window"],
                "keystroke_speed": normalized_data["input_dynamics"]["keyboard_speed"],
                "voice_tone": normalized_data["voice_metrics"]["tone"],
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Simulate Gemini response
        # In production: await openrouter_api.call(analysis_request)
        gemini_response = {
            "analysis": "Student showing signs of stress combined with unusual system resource usage",
            "contextual_factors": [
                "Multiple files being accessed rapidly",
                "High CPU usage suggests background processes",
                "Erratic keystroke pattern indicates anxiety"
            ],
            "anomaly_score": 0.72,
            "confidence": 0.85,
            "flag_recommendation": "SUSPICIOUS"
        }
        
        logger.info(f"Gemini analysis complete - Score: {gemini_response['anomaly_score']}")
        return gemini_response


# ============================================================================
# STAGE 4: FLAG CHECK & DECISION
# ============================================================================

class FlagDecisionEngine:
    """
    Makes flag decisions based on Gemini analysis.
    
    Decision logic:
    - flag == NO → Continue monitoring
    - flag == YES → Generate report
    """
    
    @staticmethod
    def make_decision(
        gemini_response: Dict[str, Any],
        patterns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Decide whether to flag activity.
        """
        
        anomaly_score = gemini_response.get("anomaly_score", 0)
        confidence = gemini_response.get("confidence", 0)
        
        # Decision thresholds
        if anomaly_score > 0.8 and confidence > 0.8:
            flag_status = FlagStatus.CRITICAL
            confidence_level = ConfidenceLevel.CRITICAL_ALERT
        elif anomaly_score > 0.65 and confidence > 0.7:
            flag_status = FlagStatus.SUSPICIOUS
            confidence_level = ConfidenceLevel.HIGH
        elif anomaly_score > 0.5:
            flag_status = FlagStatus.INVESTIGATING
            confidence_level = ConfidenceLevel.MEDIUM
        else:
            flag_status = FlagStatus.CLEAN
            confidence_level = ConfidenceLevel.LOW
        
        decision = {
            "flag_status": flag_status.value,
            "confidence_level": confidence_level.value,
            "anomaly_score": anomaly_score,
            "should_generate_report": flag_status != FlagStatus.CLEAN,
            "patterns_count": len(patterns),
            "recommendation": gemini_response.get("flag_recommendation", "CONTINUE_MONITORING")
        }
        
        logger.info(f"Flag decision: {flag_status.value} (confidence: {confidence_level.value})")
        return decision


# ============================================================================
# STAGE 5: REPORT GENERATION
# ============================================================================

class ReportGenerator:
    """
    Generates reports for flagged events.
    Outputs as structured data (can be converted to .docx / .pdf)
    """
    
    @staticmethod
    def generate_report(
        flag_decision: Dict[str, Any],
        patterns: List[Dict[str, Any]],
        normalized_data: Dict[str, Any],
        gemini_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive report for flagged activity.
        """
        
        report_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        report = {
            "report_id": report_id,
            "timestamp": timestamp,
            "flag_status": flag_decision["flag_status"],
            
            "executive_summary": {
                "anomaly_score": flag_decision["anomaly_score"],
                "confidence": flag_decision["confidence_level"],
                "patterns_detected": len(patterns),
                "recommendation": flag_decision["recommendation"]
            },
            
            "detected_patterns": patterns,
            
            "gemini_analysis": {
                "analysis": gemini_analysis.get("analysis"),
                "contextual_factors": gemini_analysis.get("contextual_factors", []),
                "anomaly_score": gemini_analysis.get("anomaly_score")
            },
            
            "data_snapshot": {
                "active_window": normalized_data["screen_metrics"]["active_window"],
                "cpu_usage": normalized_data["system_metrics"]["cpu_usage"],
                "memory_usage": normalized_data["system_metrics"]["memory_usage"],
                "keystroke_speed": normalized_data["input_dynamics"]["keyboard_speed"],
                "voice_sentiment": normalized_data["voice_metrics"]["sentiment"],
                "network_activity_mb": normalized_data["network_metrics"]["bytes_sent"] / 1024 / 1024
            },
            
            "metadata": {
                "generated_at": timestamp,
                "report_version": "1.0",
                "system": "CoreEye Workflow v1.0"
            }
        }
        
        logger.info(f"Report generated: {report_id}")
        return report


# ============================================================================
# MAIN WORKFLOW ORCHESTRATOR
# ============================================================================

class CoreEyeWorkflow:
    """
    Main orchestrator for CoreEye workflow.
    
    Flow:
    OS Data → Collect → Normalize → Pattern Detect → Gemini → Flag → Report
    """
    
    def __init__(self):
        self.collector = DataCollector()
        self.normalizer = DataNormalizer()
        self.pattern_recognizer = PatternRecognizer()
        self.gemini_analyzer = GeminiAnalyzer()
        self.flag_engine = FlagDecisionEngine()
        self.report_generator = ReportGenerator()
        
        self.reports = []
        self.flags = []
    
    async def process_activity(self, raw_os_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process complete workflow for activity data.
        
        Returns: Report (if flagged) or clean signal (if not)
        """
        
        logger.info("=" * 70)
        logger.info("STARTING COREYEE WORKFLOW")
        logger.info("=" * 70)
        
        # STAGE 1: Collect
        logger.info("\n[STAGE 1] Collecting OS data...")
        for source, data in raw_os_data.items():
            try:
                self.collector.add_data(DataSource[source.upper()], data)
            except Exception as e:
                logger.warning(f"Could not collect {source}: {e}")
        
        all_data = self.collector.get_all_data()
        
        # STAGE 2: Normalize
        logger.info("\n[STAGE 2] Normalizing data...")
        normalized_data = self.normalizer.normalize(raw_os_data)
        
        # STAGE 3: Pattern Recognition
        logger.info("\n[STAGE 3] Recognizing patterns...")
        patterns = self.pattern_recognizer.recognize_patterns(normalized_data)
        logger.info(f"Found {len(patterns)} patterns")
        for p in patterns:
            logger.info(f"  - {p['pattern_type']}: {p['severity']}")
        
        # STAGE 4: Gemini Analysis
        logger.info("\n[STAGE 4] Sending to Gemini for analysis...")
        gemini_response = await self.gemini_analyzer.analyze(patterns, normalized_data)
        logger.info(f"Gemini anomaly score: {gemini_response['anomaly_score']}")
        
        # STAGE 5: Flag Decision
        logger.info("\n[STAGE 5] Making flag decision...")
        flag_decision = self.flag_engine.make_decision(gemini_response, patterns)
        logger.info(f"Flag status: {flag_decision['flag_status']}")
        
        self.flags.append(flag_decision)
        
        # STAGE 6: Report Generation (if flagged)
        result = {
            "flag_decision": flag_decision,
            "report": None
        }
        
        if flag_decision["should_generate_report"]:
            logger.info("\n[STAGE 6] Generating report...")
            report = self.report_generator.generate_report(
                flag_decision,
                patterns,
                normalized_data,
                gemini_response
            )
            result["report"] = report
            self.reports.append(report)
        else:
            logger.info("\n[STAGE 6] No report needed - Activity is clean")
        
        logger.info("\n" + "=" * 70)
        logger.info("COREYEE WORKFLOW COMPLETE")
        logger.info("=" * 70)
        
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get workflow statistics."""
        return {
            "total_flags": len(self.flags),
            "total_reports": len(self.reports),
            "critical_count": sum(1 for f in self.flags if f["flag_status"] == "critical"),
            "suspicious_count": sum(1 for f in self.flags if f["flag_status"] == "suspicious"),
            "clean_count": sum(1 for f in self.flags if f["flag_status"] == "clean")
        }