"""
Flag Detection Orchestrator: Coordinates pattern detection, ML classification, and file generation.

This is the main entry point for client-side flag detection.
Processes packages through the pipeline:
1. Extract features & detect patterns
2. Classify with ML
3. Generate flag files if suspicious
4. Optionally send to server
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    from .pattern_detector import PatternDetector
    from .ml_classifier import MLClassifier, EnsembleClassifier
    from .flag_data_generator import FlagDataGenerator, FlagDataCache
except ImportError:
    from pattern_detector import PatternDetector
    from ml_classifier import MLClassifier, EnsembleClassifier
    from flag_data_generator import FlagDataGenerator, FlagDataCache

logger = logging.getLogger(__name__)


class FlagDetectionOrchestrator:
    """Orchestrates the entire client-side flag detection pipeline."""
    
    def __init__(self, output_dir: Optional[str] = None, enable_logging: bool = True):
        """
        Initialize the orchestrator.
        
        Args:
            output_dir: Directory for flag data files
            enable_logging: Whether to log detection activity
        """
        self.pattern_detector = PatternDetector(history_window_minutes=5)
        self.ml_classifier = EnsembleClassifier()
        self.flag_generator = FlagDataGenerator(output_dir)
        self.flag_cache = FlagDataCache(max_cache_size=1000)
        
        self.enable_logging = enable_logging
        if enable_logging:
            logger.setLevel(logging.INFO)
        
        # Statistics
        self.stats = {
            "total_packages": 0,
            "flags_generated": 0,
            "high_risk_flags": 0,
            "critical_flags": 0,
            "sessions_monitored": set(),
        }
    
    def process_package(
        self,
        package: Dict[str, Any],
        session_id: str,
        student_id: str,
        historical_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process a single activity package through the detection pipeline.
        
        Args:
            package: Activity package from client
            session_id: Exam session ID
            student_id: Student identifier
            historical_context: Historical data for context-aware analysis
            
        Returns:
            Detection result with flag info (if flagged)
        """
        self.stats["total_packages"] += 1
        self.stats["sessions_monitored"].add(session_id)
        
        timestamp = datetime.utcnow().isoformat()
        
        # Step 1: Add to pattern detector's history
        self.pattern_detector.add_activity(package)
        
        # Step 2: Detect patterns
        pattern_analysis = self.pattern_detector.detect_patterns()
        patterns = pattern_analysis.get("patterns_detected", [])
        
        if self.enable_logging and patterns:
            logger.info(f"[{student_id}] Patterns detected: {[p.get('pattern_name') for p in patterns]}")
        
        # Step 3: ML Classification
        classification = self.ml_classifier.classify_ensemble(
            package,
            patterns,
            historical_context
        )
        
        # Step 4: Determine if should create flag file
        should_flag = classification.get("should_flag", False)
        risk_level = classification.get("risk_level", "none")
        
        result = {
            "timestamp": timestamp,
            "processed": True,
            "risk_level": risk_level,
            "suspicious_score": classification.get("suspicious_score", 0.0),
            "patterns_detected": len(patterns),
            "should_flag": should_flag,
            "flag_file": None,
            "recommendation": classification.get("recommendation", "Continue normal monitoring"),
        }
        
        # Step 5: Create flag file if needed
        if should_flag:
            flag_result = self.flag_generator.create_flag_file(
                package,
                classification,
                patterns,
                session_id,
                student_id
            )
            
            flag_file = flag_result["data"]
            result["flag_file"] = flag_result["filename"]
            result["flag_id"] = flag_result["flag_id"]
            
            # Cache the flag
            self.flag_cache.cache_flag(flag_result["flag_id"], flag_file)
            
            # Update statistics
            self.stats["flags_generated"] += 1
            if risk_level == "critical":
                self.stats["critical_flags"] += 1
            elif risk_level == "high":
                self.stats["high_risk_flags"] += 1
            
            if self.enable_logging:
                logger.warning(f"🚨 FLAG CREATED: {risk_level.upper()} risk - {flag_result['flag_id']}")
        
        return result
    
    def process_batch(
        self,
        packages: List[Dict[str, Any]],
        session_id: str,
        student_id: str,
        historical_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process multiple packages in a batch.
        
        Args:
            packages: List of activity packages
            session_id: Exam session ID
            student_id: Student identifier
            historical_context: Historical context for analysis
            
        Returns:
            Batch processing results
        """
        results = []
        flagged_packages = []
        
        for package in packages:
            result = self.process_package(
                package,
                session_id,
                student_id,
                historical_context
            )
            results.append(result)
            
            if result["should_flag"]:
                flagged_packages.append(result)
        
        # Create batch report if there are flags
        batch_report = None
        if flagged_packages:
            batch_report = self.flag_generator.create_batch_flag_report(
                session_id,
                student_id,
                flagged_packages
            )
            
            if self.enable_logging:
                logger.info(f"📊 Batch report created: {batch_report['report_id']}")
        
        return {
            "batch_processed": True,
            "total_packages": len(packages),
            "flagged_count": len(flagged_packages),
            "results": results,
            "batch_report": batch_report,
            "statistics": {
                "critical": sum(1 for r in results if r["risk_level"] == "critical"),
                "high": sum(1 for r in results if r["risk_level"] == "high"),
                "medium": sum(1 for r in results if r["risk_level"] == "medium"),
                "low": sum(1 for r in results if r["risk_level"] == "low"),
                "clean": sum(1 for r in results if r["risk_level"] == "none"),
            }
        }
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of flags for a session."""
        session_flags = self.flag_generator.get_session_flags(session_id)
        
        return {
            "session_id": session_id,
            "total_flags": len(session_flags),
            "critical_count": sum(1 for f in session_flags if f.get("risk_level") == "critical"),
            "high_count": sum(1 for f in session_flags if f.get("risk_level") == "high"),
            "medium_count": sum(1 for f in session_flags if f.get("risk_level") == "medium"),
            "flags": session_flags,
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall detection statistics."""
        return {
            "total_packages_processed": self.stats["total_packages"],
            "total_flags_generated": self.stats["flags_generated"],
            "critical_flags": self.stats["critical_flags"],
            "high_risk_flags": self.stats["high_risk_flags"],
            "sessions_monitored": len(self.stats["sessions_monitored"]),
            "cache_stats": self.flag_cache.get_stats(),
        }
    
    def export_session_data(
        self,
        session_id: str,
        include_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Export all flag data for a session (for server transmission).
        
        Args:
            session_id: Session to export
            include_cache: Whether to include cached data
            
        Returns:
            Exportable session data
        """
        session_flags = self.flag_generator.get_session_flags(session_id)
        
        export_data = {
            "session_id": session_id,
            "exported_at": datetime.utcnow().isoformat(),
            "flags": session_flags,
            "summary": self.get_session_summary(session_id),
            "client_statistics": self.get_statistics(),
        }
        
        if include_cache:
            export_data["cached_flags"] = self.flag_cache.get_all_flags()
        
        return export_data
    
    def reset_session(self, session_id: str) -> None:
        """Reset detection for a session."""
        self.pattern_detector = PatternDetector(history_window_minutes=5)
        if self.enable_logging:
            logger.info(f"Session {session_id} detection reset")
    
    def reset_all(self) -> None:
        """Complete reset of orchestrator."""
        self.pattern_detector = PatternDetector()
        self.flag_cache.clear()
        self.stats = {
            "total_packages": 0,
            "flags_generated": 0,
            "high_risk_flags": 0,
            "critical_flags": 0,
            "sessions_monitored": set(),
        }
        if self.enable_logging:
            logger.info("Complete orchestrator reset")


# ============================================================================
# RECOMMENDED USAGE
# ============================================================================
"""
# Initialize orchestrator (once per application)
orchestrator = FlagDetectionOrchestrator(
    output_dir="./flag_data",
    enable_logging=True
)

# Process packages as they arrive
for package in incoming_packages:
    result = orchestrator.process_package(
        package=package,
        session_id="exam-123",
        student_id="student-456"
    )
    
    if result["should_flag"]:
        # Send flag file to server
        flag_file = result["flag_file"]
        # Upload flag_file to server for Gemini analysis
    
    # Display result to UI
    print(f"Risk Level: {result['risk_level']}")
    print(f"Recommendation: {result['recommendation']}")

# At session end, get summary
summary = orchestrator.get_session_summary("exam-123")
export_data = orchestrator.export_session_data("exam-123")

# Send export_data to server
send_to_server(export_data)
"""
