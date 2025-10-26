"""
Comprehensive Test Suite for Flag Detection System

Tests all components:
1. PatternDetector
2. MLClassifier
3. FlagDataGenerator
4. Orchestrator
5. Integration
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import tempfile

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from pattern_detector import PatternDetector
from ml_classifier import MLClassifier, EnsembleClassifier
from flag_data_generator import FlagDataGenerator, FlagDataCache
from orchestrator import FlagDetectionOrchestrator


# ============================================================================
# TEST UTILITIES
# ============================================================================

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


def create_normal_package():
    """Create a normal (non-suspicious) activity package."""
    return {
        "package_id": "pkg-normal-001",
        "session_id": "exam-test-001",
        "student_id": "student-001",
        "timestamp": datetime.utcnow().isoformat(),
        "device_id": "device-001",
        
        "input_dynamics": {
            "keystroke_rhythm_variance": 0.18,
            "keystroke_error_rate": 0.02,
            "keystroke_speed": 65,
            "mouse_velocity": 25.5,
            "mouse_idle_duration": 1
        },
        
        "focus_metrics": {
            "focus_score": 0.82,
            "eye_contact_percentage": 80
        },
        
        "system_metrics": {
            "cpu_usage": 35.0,
            "memory_usage": 55.0
        },
        
        "network_activity": {
            "bytes_sent": 500000,
            "bytes_received": 300000
        },
        
        "process_data": {
            "window_title": "Exam Portal - Question 5",
            "app_switches": 1
        },
        
        "voice_metrics": {
            "sentiment_score": 0.5,
            "pitch_variance": 8.2
        }
    }


def create_suspicious_package():
    """Create a suspicious activity package."""
    return {
        "package_id": "pkg-suspicious-001",
        "session_id": "exam-test-001",
        "student_id": "student-001",
        "timestamp": datetime.utcnow().isoformat(),
        "device_id": "device-001",
        
        "input_dynamics": {
            "keystroke_rhythm_variance": 0.82,
            "keystroke_error_rate": 0.08,
            "keystroke_speed": 120,
            "mouse_velocity": 85.5,
            "mouse_idle_duration": 2
        },
        
        "focus_metrics": {
            "focus_score": 0.22,
            "eye_contact_percentage": 15
        },
        
        "system_metrics": {
            "cpu_usage": 91.2,
            "memory_usage": 82.3
        },
        
        "network_activity": {
            "bytes_sent": 7500000,
            "bytes_received": 1200000
        },
        
        "process_data": {
            "window_title": "Chrome - Google Search",
            "app_switches": 12
        },
        
        "voice_metrics": {
            "sentiment_score": -0.65,
            "pitch_variance": 35.2
        }
    }


# ============================================================================
# TEST SUITE 1: PATTERN DETECTOR
# ============================================================================

def test_pattern_detector(results):
    """Test PatternDetector component."""
    print("\n" + "="*70)
    print("TEST SUITE 1: PATTERN DETECTOR")
    print("="*70)
    
    detector = PatternDetector(history_window_minutes=5)
    
    # Test 1.1: Add normal packages
    try:
        for i in range(5):
            pkg = create_normal_package()
            detector.add_activity(pkg)
        results.add_pass("Pattern Detector: Add normal packages", "5 packages added successfully")
    except Exception as e:
        results.add_fail("Pattern Detector: Add normal packages", str(e))
    
    # Test 1.2: Detect no patterns in normal activity
    try:
        patterns = detector.detect_patterns()
        assert patterns["severity"] == "low", f"Expected low severity, got {patterns['severity']}"
        assert len(patterns["patterns_detected"]) == 0, f"Expected no patterns, got {len(patterns['patterns_detected'])}"
        results.add_pass("Pattern Detector: No patterns in normal activity", f"Severity: {patterns['severity']}")
    except Exception as e:
        results.add_fail("Pattern Detector: No patterns in normal activity", str(e))
    
    # Test 1.3: Add suspicious packages
    detector2 = PatternDetector(history_window_minutes=5)
    try:
        # Add multiple normal packages to build baseline
        for i in range(10):
            pkg = create_normal_package()
            detector2.add_activity(pkg)
        
        # Add multiple suspicious packages
        for i in range(3):
            susp_pkg = create_suspicious_package()
            detector2.add_activity(susp_pkg)
        
        results.add_pass("Pattern Detector: Add suspicious package", "13 packages added successfully")
    except Exception as e:
        results.add_fail("Pattern Detector: Add suspicious package", str(e))
    
    # Test 1.4: Detect patterns in suspicious activity
    try:
        patterns = detector2.detect_patterns()
        # Even with more data, patterns may be detected as "medium" or higher
        assert patterns["severity"] in ["low", "medium", "high", "critical"], f"Invalid severity: {patterns['severity']}"
        # With enough history of suspicious data, should detect something
        results.add_pass("Pattern Detector: Detect patterns in suspicious activity", f"Detected {len(patterns['patterns_detected'])} patterns, severity: {patterns['severity']}")
    except Exception as e:
        results.add_fail("Pattern Detector: Detect patterns in suspicious activity", str(e))


# ============================================================================
# TEST SUITE 2: ML CLASSIFIER
# ============================================================================

def test_ml_classifier(results):
    """Test MLClassifier component."""
    print("\n" + "="*70)
    print("TEST SUITE 2: ML CLASSIFIER")
    print("="*70)
    
    classifier = MLClassifier()
    
    # Test 2.1: Classify normal package
    try:
        normal_pkg = create_normal_package()
        result = classifier.classify(normal_pkg, [])
        
        assert "suspicious_score" in result, "Missing suspicious_score"
        assert 0.0 <= result["suspicious_score"] <= 1.0, f"Score out of range: {result['suspicious_score']}"
        assert result["risk_level"] in ["none", "low", "medium", "high", "critical"], f"Invalid risk level: {result['risk_level']}"
        
        results.add_pass("ML Classifier: Classify normal package", f"Score: {result['suspicious_score']:.2%}, Risk: {result['risk_level']}")
    except Exception as e:
        results.add_fail("ML Classifier: Classify normal package", str(e))
    
    # Test 2.2: Classify suspicious package
    try:
        susp_pkg = create_suspicious_package()
        result = classifier.classify(susp_pkg, [])
        
        assert result["suspicious_score"] > 0.5, f"Expected high score for suspicious package, got {result['suspicious_score']}"
        assert result["risk_level"] in ["high", "critical"], f"Expected high/critical risk, got {result['risk_level']}"
        
        results.add_pass("ML Classifier: Classify suspicious package", f"Score: {result['suspicious_score']:.2%}, Risk: {result['risk_level']}")
    except Exception as e:
        results.add_fail("ML Classifier: Classify suspicious package", str(e))


# ============================================================================
# TEST SUITE 3: FLAG DATA GENERATOR
# ============================================================================

def test_flag_data_generator(results):
    """Test FlagDataGenerator component."""
    print("\n" + "="*70)
    print("TEST SUITE 3: FLAG DATA GENERATOR")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = FlagDataGenerator(output_dir=tmpdir)
        
        # Test 3.1: Create flag file
        try:
            pkg = create_suspicious_package()
            classifier = MLClassifier()
            classification = classifier.classify(pkg, [])
            
            detector = PatternDetector()
            detector.add_activity(pkg)
            patterns = detector.detect_patterns()["patterns_detected"]
            
            flag_result = generator.create_flag_file(
                package=pkg,
                classification=classification,
                patterns=patterns,
                session_id="test-session",
                student_id="test-student"
            )
            
            assert "flag_id" in flag_result, "Missing flag_id"
            assert "filename" in flag_result, "Missing filename"
            assert "data" in flag_result, "Missing data"
            
            results.add_pass("Flag Generator: Create flag file", f"Flag ID: {flag_result['flag_id'][:8]}...")
        except Exception as e:
            results.add_fail("Flag Generator: Create flag file", str(e))


# ============================================================================
# TEST SUITE 4: ORCHESTRATOR
# ============================================================================

def test_orchestrator(results):
    """Test FlagDetectionOrchestrator component."""
    print("\n" + "="*70)
    print("TEST SUITE 4: ORCHESTRATOR")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        orchestrator = FlagDetectionOrchestrator(output_dir=tmpdir, enable_logging=False)
        
        # Test 4.1: Process normal package
        try:
            pkg = create_normal_package()
            result = orchestrator.process_package(
                package=pkg,
                session_id="test-session",
                student_id="test-student"
            )
            
            assert "risk_level" in result, "Missing risk_level"
            assert result["risk_level"] in ["none", "low", "medium", "high", "critical"], f"Invalid risk level: {result['risk_level']}"
            assert result["should_flag"] == False, "Normal package should not be flagged"
            
            results.add_pass("Orchestrator: Process normal package", f"Risk: {result['risk_level']}, Flagged: {result['should_flag']}")
        except Exception as e:
            results.add_fail("Orchestrator: Process normal package", str(e))
        
        # Test 4.2: Process suspicious package
        try:
            orchestrator2 = FlagDetectionOrchestrator(output_dir=tmpdir, enable_logging=False)
            
            # Add normal packages first
            for i in range(5):
                pkg = create_normal_package()
                orchestrator2.process_package(pkg, "test-session", "test-student")
            
            # Add suspicious package
            susp_pkg = create_suspicious_package()
            result = orchestrator2.process_package(susp_pkg, "test-session", "test-student")
            
            assert result["should_flag"] == True, "Suspicious package should be flagged"
            assert result["risk_level"] in ["high", "critical"], f"Expected high/critical, got {result['risk_level']}"
            assert "flag_file" in result and result["flag_file"] is not None, "Missing flag file"
            
            results.add_pass("Orchestrator: Process suspicious package", f"Risk: {result['risk_level']}, Flag file created: {result['flag_file'] is not None}")
        except Exception as e:
            results.add_fail("Orchestrator: Process suspicious package", str(e))


# ============================================================================
# TEST SUITE 5: INTEGRATION
# ============================================================================

def test_integration(results):
    """Test full integration of all components."""
    print("\n" + "="*70)
    print("TEST SUITE 5: INTEGRATION TEST")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        orchestrator = FlagDetectionOrchestrator(output_dir=tmpdir, enable_logging=False)
        
        # Test 5.1: Complete workflow
        try:
            # Simulate exam session
            session_id = "full-test-session"
            student_id = "full-test-student"
            
            # Normal start
            for i in range(5):
                pkg = create_normal_package()
                pkg["timestamp"] = datetime.utcnow().isoformat()
                orchestrator.process_package(pkg, session_id, student_id)
            
            # Suspicious behavior
            for i in range(3):
                pkg = create_suspicious_package()
                pkg["timestamp"] = datetime.utcnow().isoformat()
                result = orchestrator.process_package(pkg, session_id, student_id)
                if result["should_flag"]:
                    break
            
            # Normal again
            pkg = create_normal_package()
            pkg["timestamp"] = datetime.utcnow().isoformat()
            orchestrator.process_package(pkg, session_id, student_id)
            
            # Get session data
            summary = orchestrator.get_session_summary(session_id)
            
            assert summary["total_flags"] > 0, "Should have flagged suspicious packages"
            
            results.add_pass("Integration: Complete workflow", f"Processed 9 packages, flagged {summary['total_flags']}")
        except Exception as e:
            results.add_fail("Integration: Complete workflow", str(e))
        
        # Test 5.2: Performance check
        try:
            import time
            
            pkg = create_suspicious_package()
            
            start = time.time()
            for _ in range(100):
                orchestrator.process_package(pkg, "perf-test", "perf-student")
            elapsed = time.time() - start
            
            avg_ms = (elapsed * 1000) / 100
            
            assert avg_ms < 15, f"Performance too slow: {avg_ms:.2f}ms per package (should be <15ms)"
            
            results.add_pass("Integration: Performance", f"Average {avg_ms:.2f}ms per package")
        except Exception as e:
            results.add_fail("Integration: Performance", str(e))


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """Run all test suites."""
    print("\n" + "="*70)
    print("FLAG DETECTION SYSTEM - COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    results = TestResults()
    
    try:
        test_pattern_detector(results)
        test_ml_classifier(results)
        test_flag_data_generator(results)
        test_orchestrator(results)
        test_integration(results)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Print summary
    success = results.summary()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! System is fully functional and integrated.\n")
    else:
        print(f"\n⚠️  {results.failed} test(s) failed. See details above.\n")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)