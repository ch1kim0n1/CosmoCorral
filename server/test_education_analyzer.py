"""
Educational Analyzer - Integration Examples & Tests

Demonstrates how to use the two-stage education analyzer with sample data.
"""

import asyncio
import json
from datetime import datetime


# Example 1: Safe Student Activity
SAFE_ACTIVITY_PACKAGE = {
    "student_id": "STU001",
    "package": {
        "process_data": {
            "window_title": "Visual Studio Code - main.py",
            "process_name": "code.exe",
            "app_switches": 3,  # Low - just working on assignment
            "running_processes": ["code.exe", "chrome.exe"]  # Expected apps only
        },
        "system_metrics": {
            "cpu_usage": 35.2,
            "memory_usage": 52.1
        },
        "network_activity": {
            "bytes_sent": 102400,  # ~100KB - minimal
            "bytes_received": 1048576,  # ~1MB - normal for browsing docs
            "active_connections": 1  # Just IDE connection
        },
        "focus_metrics": {
            "focus_score": 0.88,  # High focus
            "distraction_count": 1  # Minimal
        },
        "input_dynamics": {
            "keystroke_rhythm_variance": 0.15,  # Consistent typing
            "mouse_idle_duration": 45  # Normal idle during thinking
        }
    },
    "session_info": {
        "course_name": "CS 101 - Algorithms",
        "assessment_type": "Assignment",
        "assessment_name": "Assignment 2: Sorting",
        "duration_minutes": 120,
        "baseline_behavior": "Student typically codes steadily during assignments"
    }
}


# Example 2: Suspicious Student Activity - Unauthorized Resources
SUSPICIOUS_ACTIVITY_CHEATING = {
    "student_id": "STU002",
    "package": {
        "process_data": {
            "window_title": "Google Search Results - 'quick sort algorithm'",
            "process_name": "chrome.exe",
            "app_switches": 23,  # HIGH - frequent switching
            "running_processes": [
                "chrome.exe",  # Multiple tabs open
                "outlook.exe",  # Email - unusual during exam
                "notepad.exe",
                "discord.exe"   # Communication app
            ]
        },
        "system_metrics": {
            "cpu_usage": 78.5,  # Elevated
            "memory_usage": 81.2  # High
        },
        "network_activity": {
            "bytes_sent": 5242880,  # 5MB - SUSPICIOUS
            "bytes_received": 15728640,  # 15MB - downloading something
            "active_connections": 8  # Multiple external connections
        },
        "focus_metrics": {
            "focus_score": 0.25,  # VERY LOW - distracted
            "distraction_count": 14  # Many distractions
        },
        "input_dynamics": {
            "keystroke_rhythm_variance": 0.72,  # ERRATIC - pasting code?
            "mouse_idle_duration": 300  # Long idle then activity bursts
        }
    },
    "session_info": {
        "course_name": "CS 101 - Algorithms",
        "assessment_type": "Exam",
        "assessment_name": "Midterm Final Exam - Closed Book",
        "duration_minutes": 120,
        "baseline_behavior": "Student typically shows high focus during exams"
    }
}


# Example 3: Suspicious Activity - Possible Impersonation
SUSPICIOUS_ACTIVITY_IMPERSONATION = {
    "student_id": "STU003",
    "package": {
        "process_data": {
            "window_title": "Untitled - Notepad",
            "process_name": "notepad.exe",
            "app_switches": 0,  # NO app switches - unusual
            "running_processes": ["notepad.exe"]  # Only basic app
        },
        "system_metrics": {
            "cpu_usage": 2.1,  # Minimal
            "memory_usage": 15.3  # Very low
        },
        "network_activity": {
            "bytes_sent": 0,  # No network activity
            "bytes_received": 0,
            "active_connections": 0
        },
        "focus_metrics": {
            "focus_score": 1.0,  # Perfect focus - TOO PERFECT
            "distraction_count": 0  # Zero distractions - unrealistic
        },
        "input_dynamics": {
            "keystroke_rhythm_variance": 0.01,  # TOO CONSISTENT - bot-like
            "mouse_idle_duration": 0  # No idle - unrealistic pattern
        }
    },
    "session_info": {
        "course_name": "CS 101 - Algorithms",
        "assessment_type": "Exam",
        "assessment_name": "Midterm Final Exam",
        "duration_minutes": 120,
        "baseline_behavior": "Student typically shows varied focus patterns, normal breaks"
    }
}


# Example 4: Legitimate Multitasking (Not Suspicious)
LEGITIMATE_MULTITASKING = {
    "student_id": "STU004",
    "package": {
        "process_data": {
            "window_title": "Assignment 3 Document - Google Docs",
            "process_name": "chrome.exe",
            "app_switches": 8,  # Moderate - checking docs and typing
            "running_processes": [
                "chrome.exe",  # Google Docs
                "slack.exe"    # Instructor clarification chat - allowed
            ]
        },
        "system_metrics": {
            "cpu_usage": 42.3,
            "memory_usage": 59.8
        },
        "network_activity": {
            "bytes_sent": 512000,  # ~500KB - normal for cloud docs
            "bytes_received": 2097152,  # ~2MB - normal
            "active_connections": 2  # Google + Slack
        },
        "focus_metrics": {
            "focus_score": 0.75,  # Good focus
            "distraction_count": 3  # Some distractions - normal
        },
        "input_dynamics": {
            "keystroke_rhythm_variance": 0.35,  # Normal variance
            "mouse_idle_duration": 120  # Normal breaks for thinking
        }
    },
    "session_info": {
        "course_name": "CS 101 - Algorithms",
        "assessment_type": "Assignment",
        "assessment_name": "Assignment 3: Dynamic Programming",
        "duration_minutes": 240,
        "baseline_behavior": "Student often collaborates with instructor via Slack"
    }
}


def print_analysis_result(result: dict, title: str):
    """Pretty print analysis result."""
    print("\n" + "="*80)
    print(f"ANALYSIS RESULT: {title}")
    print("="*80)
    
    print(f"\nAnalysis ID: {result['analysis_id']}")
    print(f"Student ID: {result['student_id']}")
    print(f"Timestamp: {result['timestamp']}")
    
    # Stage 1 result
    print("\n--- STAGE 1: QUICK DECISION ---")
    stage1 = result['stage1_result']
    print(f"Decision: {stage1['decision'].upper()}")
    print(f"Confidence: {stage1['confidence']:.1%}")
    print(f"Reason: {stage1['brief_reason']}")
    
    # Stage 2 result (if not skipped)
    if not result['skip_stage2'] and 'stage2_result' in result:
        print("\n--- STAGE 2: DETAILED ANALYSIS ---")
        stage2 = result['stage2_result']
        
        print(f"\nViolations Found: {len(stage2['violations'])}")
        for i, violation in enumerate(stage2['violations'], 1):
            print(f"\n  {i}. {violation['type'].upper()}")
            print(f"     Severity: {violation['severity']}")
            print(f"     Location: {violation['location']}")
            print(f"     Description: {violation['description']}")
            print(f"     Why it's a violation: {violation['why_violation']}")
            print(f"     Evidence:")
            for evidence in violation['evidence']:
                print(f"       • {evidence}")
        
        print(f"\nOverall Assessment:")
        print(f"  {stage2['overall_assessment']}")
        
        print(f"\nRecommended Actions:")
        for action in stage2['recommended_actions']:
            print(f"  • [{action['priority'].upper()}] {action['action']}")
            print(f"    {action['description']}")
            print(f"    (Reason: {action['reason']})")
        
        print(f"\nTeacher Notes:")
        print(f"  {stage2['teacher_notes']}")
    else:
        print("\n--- STAGE 2: SKIPPED ---")
        print("Activity marked as SAFE - no detailed analysis needed.")
    
    print(f"\nTokens Used: {result['tokens_used']}")


# Async test function
async def test_education_analyzer():
    """
    Test the education analyzer with sample data.
    
    Note: This requires GEMINI_API_KEY to be set.
    Run with: GEMINI_API_KEY="your-key" python test_education_analyzer.py
    """
    
    from education_analyzer import EducationAnalyzer
    import os
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable not set")
        print("To test with Gemini API, run:")
        print("  set GEMINI_API_KEY=your-api-key")
        print("  python test_education_analyzer.py")
        return
    
    analyzer = EducationAnalyzer(api_key=api_key)
    
    test_cases = [
        ("Safe - Normal Assignment Work", SAFE_ACTIVITY_PACKAGE),
        ("Suspicious - Unauthorized Resources & Cheating", SUSPICIOUS_ACTIVITY_CHEATING),
        ("Suspicious - Impersonation (Bot-like)", SUSPICIOUS_ACTIVITY_IMPERSONATION),
        ("Legitimate - Allowed Multitasking", LEGITIMATE_MULTITASKING),
    ]
    
    print("\n" + "="*80)
    print("EDUCATION ANALYZER - TEST SUITE")
    print("="*80)
    print(f"Testing with {len(test_cases)} examples...")
    print(f"API Status: {'✅ Configured' if analyzer.api_available else '⚠️ Fallback Mode'}")
    
    for test_name, test_data in test_cases:
        try:
            result = await analyzer.analyze_package(
                package=test_data['package'],
                student_id=test_data['student_id'],
                session_info=test_data['session_info']
            )
            print_analysis_result(result, test_name)
            
        except Exception as e:
            print(f"\n❌ Test failed for {test_name}: {e}")
    
    print("\n" + "="*80)
    print("TEST SUITE COMPLETE")
    print("="*80)


# FastAPI integration example
async def fastapi_integration_example():
    """
    Example of how to integrate with FastAPI.
    """
    
    example_code = """
    # In main.py or app.py
    
    from fastapi import FastAPI
    from education_api import router as education_router
    from education_analyzer import EducationAnalyzer
    import os
    
    app = FastAPI()
    
    # Include analysis routes
    app.include_router(education_router)
    
    # Example usage
    @app.post("/api/test-analysis")
    async def test_analysis(request: dict):
        analyzer = EducationAnalyzer(os.getenv("GEMINI_API_KEY"))
        
        result = await analyzer.analyze_package(
            package=request.get("package"),
            student_id=request.get("student_id"),
            session_info=request.get("session_info")
        )
        
        return result
    """
    
    print(example_code)


# Frontend integration example
def frontend_integration_example():
    """
    Example of how to call from Next.js dashboard.
    """
    
    example_code = """
    // In dashboard/components/StudentAnalysis.tsx
    
    import { useState } from 'react';
    
    export function StudentAnalysisCard({ studentId, activityData, sessionInfo }) {
      const [analysis, setAnalysis] = useState(null);
      const [loading, setLoading] = useState(false);
      
      async function runAnalysis() {
        setLoading(true);
        try {
          const response = await fetch('/api/analysis/analyze-package', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              student_id: studentId,
              package: activityData,
              session_info: sessionInfo
            })
          });
          
          const result = await response.json();
          setAnalysis(result);
          
        } finally {
          setLoading(false);
        }
      }
      
      if (!analysis) {
        return <button onClick={runAnalysis}>Analyze Activity</button>;
      }
      
      const isSafe = analysis.skip_stage2;
      
      return (
        <div className={isSafe ? 'bg-green-50' : 'bg-red-50'}>
          <h3>Analysis Results</h3>
          
          {isSafe ? (
            <div className="text-green-600">
              ✅ Safe - {analysis.stage1_result.brief_reason}
            </div>
          ) : (
            <div className="text-red-600">
              ⚠️ Suspicious - Found {analysis.stage2_result.violations.length} violations
              
              {analysis.stage2_result.violations.map((v, i) => (
                <div key={i} className="mt-2 p-2 bg-red-100">
                  <strong>{v.type}</strong> (Severity: {v.severity})
                  <p>{v.description}</p>
                  <p>Evidence: {v.evidence.join(', ')}</p>
                </div>
              ))}
            </div>
          )}
          
          <button onClick={() => exportReport(analysis.analysis_id)}>
            Export Report
          </button>
        </div>
      );
    }
    """
    
    print(example_code)


if __name__ == "__main__":
    import sys
    
    print("\n" + "="*80)
    print("EDUCATION ANALYZER - EXAMPLES & TESTS")
    print("="*80)
    
    if "--test" in sys.argv:
        print("\n🧪 Running async tests...")
        asyncio.run(test_education_analyzer())
    
    elif "--fastapi" in sys.argv:
        print("\n📚 FastAPI Integration Example:")
        asyncio.run(fastapi_integration_example())
    
    elif "--frontend" in sys.argv:
        print("\n🎨 Frontend Integration Example:")
        frontend_integration_example()
    
    else:
        print("\nUsage:")
        print("  python test_education_analyzer.py --test        # Run tests with Gemini API")
        print("  python test_education_analyzer.py --fastapi     # Show FastAPI integration")
        print("  python test_education_analyzer.py --frontend    # Show Frontend integration")
        print("\nRequirements:")
        print("  - Set GEMINI_API_KEY environment variable for full testing")
        print("  - Install: pip install google-generativeai fastapi")
