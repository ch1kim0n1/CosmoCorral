"""
Comprehensive Test Suite for CoreEye System

Tests:
1. CoreEye Workflow (6 stages)
2. TODO Feature Implementations (5 features)
3. Integration between workflow and features
"""

import asyncio
import logging
import json
from datetime import datetime

# Import modules
from coreyee_workflow import (
    CoreEyeWorkflow, DataCollector, DataNormalizer, PatternRecognizer,
    GeminiAnalyzer, FlagDecisionEngine, ReportGenerator
)
from coreyee_todo_features import (
    CoreEyeTodoTracker, ScreenTextExtractor, CommandViolationDetector,
    FaceRecognitionEngine, SuspicionConfidenceCalculator, RemoteScreenLocker
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestResults:
    """Track test results."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def add_pass(self, test_name, message=""):
        self.passed += 1
        self.tests.append(("PASS", test_name, message))
        print(f"✅ PASS: {test_name}")
        if message:
            print(f"   └─ {message}")
    
    def add_fail(self, test_name, error):
        self.failed += 1
        self.tests.append(("FAIL", test_name, str(error)))
        print(f"❌ FAIL: {test_name}")
        print(f"   └─ {error}")
    
    def summary(self):
        total = self.passed + self.failed
        print("\n" + "="*70)
        print(f"TEST SUMMARY: {self.passed}/{total} passed ({self.failed} failed)")
        print("="*70)
        return self.failed == 0


# ============================================================================
# TEST SUITE 1: COREYEE WORKFLOW
# ============================================================================

def test_coreyee_workflow(results):
    """Test CoreEye workflow components."""
    print("\n" + "="*70)
    print("TEST SUITE 1: COREYEE WORKFLOW (6 Stages)")
    print("="*70)
    
    # Create test data
    test_data = {
        "cpu": {"usage": 92, "memory": 81, "process_count": 45},
        "file": {"active": ["file1.txt", "file2.txt"], "types": ["txt", "py"], "mod_freq": 15},
        "keyboard": {"speed": 85, "variance": 0.82, "pattern": "erratic"},
        "mouse": {"speed": 45, "velocity": 120, "pattern": "jumpy"},
        "screen": {"active_window": "Chrome - Google Search", "content_type": "web", "text": "exam answers"},
        "voice": {"sentiment": -0.65, "tone": "stressed", "speech_rate": 120, "transcribed": "help me"},
        "network": {"sent": 52428800, "received": 20971520, "type": "wifi"},
        "system": {"lock_unlock": False, "sleep_wake": False, "peripherals": []}
    }
    
    # Test 1: Data Collector
    try:
        collector = DataCollector()
        for source, data in test_data.items():
            from coreyee_workflow import DataSource
            collector.add_data(DataSource[source.upper()], data)
        results.add_pass("Stage 1: Data Collection", "All sources collected")
    except Exception as e:
        results.add_fail("Stage 1: Data Collection", str(e))
    
    # Test 2: Data Normalizer
    try:
        normalizer = DataNormalizer()
        normalized = normalizer.normalize(test_data)
        assert "system_metrics" in normalized
        assert "input_dynamics" in normalized
        results.add_pass("Stage 2: Data Normalization", f"Normalized into {len(normalized)} categories")
    except Exception as e:
        results.add_fail("Stage 2: Data Normalization", str(e))
    
    # Test 3: Pattern Recognition
    try:
        recognizer = PatternRecognizer()
        patterns = recognizer.recognize_patterns(normalized)
        assert len(patterns) > 0
        results.add_pass("Stage 3: Pattern Recognition", f"Detected {len(patterns)} patterns")
    except Exception as e:
        results.add_fail("Stage 3: Pattern Recognition", str(e))
    
    # Test 4: Flag Decision
    try:
        gemini_response = {
            "anomaly_score": 0.72,
            "confidence": 0.85,
            "flag_recommendation": "SUSPICIOUS"
        }
        decision = FlagDecisionEngine.make_decision(gemini_response, patterns)
        assert decision["flag_status"] in ["clean", "suspicious", "critical", "investigating"]
        results.add_pass("Stage 4: Flag Decision", f"Decision: {decision['flag_status']}")
    except Exception as e:
        results.add_fail("Stage 4: Flag Decision", str(e))
    
    # Test 5: Report Generation
    try:
        if decision["should_generate_report"]:
            generator = ReportGenerator()
            report = generator.generate_report(decision, patterns, normalized, gemini_response)
            assert "report_id" in report
            results.add_pass("Stage 5: Report Generation", f"Report {report['report_id'][:8]}... created")
        else:
            results.add_pass("Stage 5: Report Generation", "No report needed (clean activity)")
    except Exception as e:
        results.add_fail("Stage 5: Report Generation", str(e))
    
    # Test 6: Full Workflow
    try:
        async def run_workflow():
            workflow = CoreEyeWorkflow()
            result = await workflow.process_activity(test_data)
            return result
        
        result = asyncio.run(run_workflow())
        assert "flag_decision" in result
        results.add_pass("Stage 6: Full Workflow", f"Workflow complete - {result['flag_decision']['flag_status']}")
    except Exception as e:
        results.add_fail("Stage 6: Full Workflow", str(e))


# ============================================================================
# TEST SUITE 2: TODO FEATURES
# ============================================================================

def test_todo_features(results):
    """Test TODO feature implementations."""
    print("\n" + "="*70)
    print("TEST SUITE 2: TODO FEATURES (5 Features)")
    print("="*70)
    
    activity_data = {
        "report_count": 8,
        "window_switches": 25,
        "copy_paste_count": 5,
        "patterns": [{"severity": "high"}, {"severity": "high"}],
        "gemini_score": 0.75,
        "face_consistency": 0.85,
        "violations": [{"severity": "high"}]
    }
    
    # Test 1: Screen Text Extraction
    try:
        async def test_text_extraction():
            extractor = ScreenTextExtractor()
            result = await extractor.extract_text(activity_data)
            return result
        
        result = asyncio.run(test_text_extraction())
        assert result["status"] in ["in_progress", "completed"]
        results.add_pass("TODO-1: Screen Text Extraction", f"Status: {result['status']}")
    except Exception as e:
        results.add_fail("TODO-1: Screen Text Extraction", str(e))
    
    # Test 2: Command Violation Detection
    try:
        async def test_violations():
            detector = CommandViolationDetector()
            result = await detector.detect_violations(activity_data)
            return result
        
        result = asyncio.run(test_violations())
        violations_count = result["violations_detected"]
        results.add_pass("TODO-2: Command Violations", f"Detected {violations_count} violations")
    except Exception as e:
        results.add_fail("TODO-2: Command Violations", str(e))
    
    # Test 3: Face Recognition
    try:
        async def test_face():
            engine = FaceRecognitionEngine()
            result = await engine.process_face_data(activity_data)
            return result
        
        result = asyncio.run(test_face())
        assert "consistency_score" in result
        results.add_pass("TODO-3: Face Recognition", f"Consistency: {result['consistency_score']}")
    except Exception as e:
        results.add_fail("TODO-3: Face Recognition", str(e))
    
    # Test 4: Suspicion Confidence
    try:
        result = SuspicionConfidenceCalculator.calculate_confidence(
            patterns=activity_data["patterns"],
            gemini_score=activity_data["gemini_score"],
            face_consistency=activity_data["face_consistency"],
            command_violations=activity_data["violations"]
        )
        assert "total_confidence" in result
        results.add_pass("TODO-4: Confidence Level", f"Confidence: {result['total_confidence']:.1%} ({result['confidence_level']})")
    except Exception as e:
        results.add_fail("TODO-4: Confidence Level", str(e))
    
    # Test 5: Remote Screen Lock
    try:
        async def test_screen_lock():
            locker = RemoteScreenLocker()
            result = await locker.lock_screen("session-123", "student-456", "Suspicious activity detected", {})
            return result
        
        result = asyncio.run(test_screen_lock())
        assert result["action"] == "LOCK_SCREEN_REQUESTED"
        results.add_pass("TODO-5: Remote Screen Lock", f"Status: {result['status']}")
    except Exception as e:
        results.add_fail("TODO-5: Remote Screen Lock", str(e))
    
    # Test 6: TODO Tracker
    try:
        tracker = CoreEyeTodoTracker()
        status = tracker.get_status()
        assert status["total_items"] == 5
        results.add_pass("TODO Tracker: Status", f"{status['completed']} completed, {status['in_progress']} in progress, {status['todo']} todo")
    except Exception as e:
        results.add_fail("TODO Tracker: Status", str(e))


# ============================================================================
# TEST SUITE 3: INTEGRATION
# ============================================================================

def test_integration(results):
    """Test integration of workflow and TODO features."""
    print("\n" + "="*70)
    print("TEST SUITE 3: INTEGRATION")
    print("="*70)
    
    # Test 1: End-to-end with TODO features
    try:
        async def full_system():
            # Run workflow
            workflow = CoreEyeWorkflow()
            test_data = {
                "cpu": {"usage": 92, "memory": 81, "process_count": 45},
                "file": {"active": ["file1.txt"], "types": ["txt"], "mod_freq": 15},
                "keyboard": {"speed": 85, "variance": 0.82},
                "mouse": {"speed": 45, "velocity": 120},
                "screen": {"active_window": "Chrome", "content_type": "web"},
                "voice": {"sentiment": -0.65, "tone": "stressed"},
                "network": {"sent": 52428800, "received": 20971520},
                "system": {}
            }
            
            workflow_result = await workflow.process_activity(test_data)
            
            # Run TODO features
            tracker = CoreEyeTodoTracker()
            activity_data = {
                "report_count": 8,
                "window_switches": 25,
                "copy_paste_count": 5,
                "patterns": workflow_result.get("flag_decision", {}).get("patterns_count", 0),
                "gemini_score": 0.72,
                "face_consistency": 0.85,
                "violations": []
            }
            
            todo_result = await tracker.run_all(activity_data)
            
            return {
                "workflow": workflow_result,
                "todos": todo_result,
                "combined": True
            }
        
        result = asyncio.run(full_system())
        results.add_pass("Integration: Full System", "Workflow + TODO features working together")
    except Exception as e:
        results.add_fail("Integration: Full System", str(e))
    
    # Test 2: Report output format
    try:
        assert "workflow" in result
        assert "flag_decision" in result["workflow"]
        results.add_pass("Integration: Data Format", "Output format is correct")
    except Exception as e:
        results.add_fail("Integration: Data Format", str(e))


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """Run all test suites."""
    print("\n" + "="*70)
    print("COREYEE SYSTEM - COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    results = TestResults()
    
    try:
        test_coreyee_workflow(results)
        test_todo_features(results)
        test_integration(results)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Print summary
    success = results.summary()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! CoreEye system is fully functional.\n")
    else:
        print(f"\n⚠️  {results.failed} test(s) failed. See details above.\n")
    
    return success


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)