"""
Two-Stage Educational Integrity Analyzer for University Computer Monitoring

This module implements a dual-stage Gemini analysis system:
  Stage 1: Quick Safety Assessment - Determines if content is "safe" or "suspicious"
  Stage 2: Detailed Violation Report - Only if flagged as suspicious, creates detailed report

Context: University student monitoring (teacher/IT Department oversight)
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Optional, Dict, List, Any, Tuple
from enum import Enum
import uuid

import google.generativeai as genai

logger = logging.getLogger(__name__)


class SafetyDecision(Enum):
    """Safety classification for student activity."""
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    UNCERTAIN = "uncertain"


class ViolationType(Enum):
    """Types of academic integrity violations."""
    UNAUTHORIZED_RESOURCES = "unauthorized_resources"
    CHEATING_TOOLS = "cheating_tools"
    EXAM_CHAT = "exam_chat"
    DATA_EXFILTRATION = "data_exfiltration"
    IMPERSONATION = "impersonation"
    UNUSUAL_BEHAVIOR = "unusual_behavior"
    POLICY_VIOLATION = "policy_violation"
    TECHNICAL_ISSUE = "technical_issue"


class EducationAnalyzer:
    """
    Two-stage analyzer for university student computer monitoring.
    
    Stage 1: Binary classification (safe/suspicious)
    Stage 2: Detailed analysis only if suspicious (what, where, why, action)
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_available = False
        self.session_id = str(uuid.uuid4())[:8]
        
        if api_key and api_key != "API_IS_NOT_PROVIDED":
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel("gemini-1.5-flash")
                self.api_available = True
                logger.info(f"✅ EducationAnalyzer initialized [Session: {self.session_id}]")
            except Exception as e:
                logger.warning(f"⚠️ Failed to configure Gemini API: {e}")
                self.api_available = False
        else:
            logger.warning("⚠️ GEMINI_API_KEY not provided. Using fallback analysis.")

    async def analyze_package(
        self,
        package: Dict[str, Any],
        student_id: str,
        session_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute two-stage analysis pipeline.
        
        Args:
            package: Student activity data package (JSON)
            student_id: Student identifier
            session_info: Optional session metadata (course, exam name, etc.)
        
        Returns:
            {
                "analysis_id": "uuid",
                "timestamp": "ISO8601",
                "student_id": "student_id",
                "stage1_result": {
                    "decision": "safe|suspicious|uncertain",
                    "confidence": 0.0-1.0,
                    "brief_reason": "..."
                },
                "stage2_result": {  # Only if suspicious
                    "violations": [
                        {
                            "type": "violation_type",
                            "severity": "low|medium|high|critical",
                            "location": "where in the data",
                            "description": "what is suspicious",
                            "evidence": ["evidence1", "evidence2"],
                            "why_violation": "why this is a violation"
                        }
                    ],
                    "overall_assessment": "summary",
                    "recommended_actions": [
                        {
                            "action": "action_name",
                            "priority": "low|medium|high",
                            "description": "what to do",
                            "reason": "why this action"
                        }
                    ],
                    "teacher_notes": "notes for teacher/IT staff"
                },
                "skip_stage2": True,  # If safe, skip detailed analysis
                "tokens_used": int,
                "model_version": "gemini-1.5-flash"
            }
        """
        analysis_id = str(uuid.uuid4())
        result = {
            "analysis_id": analysis_id,
            "timestamp": datetime.utcnow().isoformat(),
            "student_id": student_id,
            "skip_stage2": False,
            "tokens_used": 0,
            "model_version": "gemini-1.5-flash"
        }

        try:
            # STAGE 1: Quick Safety Assessment
            stage1 = await self._stage1_safety_check(package, session_info)
            result["stage1_result"] = stage1
            result["tokens_used"] += stage1.get("tokens_used", 0)

            # STAGE 2: Detailed Analysis (only if suspicious)
            if stage1["decision"] == "safe":
                logger.info(f"[{analysis_id}] Student {student_id}: SAFE ✅ - Skipping Stage 2")
                result["skip_stage2"] = True
                return result

            logger.info(f"[{analysis_id}] Student {student_id}: SUSPICIOUS ⚠️ - Running Stage 2 analysis")
            stage2 = await self._stage2_detailed_analysis(package, stage1, session_info)
            result["stage2_result"] = stage2
            result["tokens_used"] += stage2.get("tokens_used", 0)

        except Exception as e:
            logger.error(f"Analysis failed for {student_id}: {e}")
            result["error"] = str(e)
            result["stage1_result"] = {
                "decision": "uncertain",
                "confidence": 0.0,
                "brief_reason": "Analysis service error"
            }

        return result

    async def _stage1_safety_check(
        self,
        package: Dict[str, Any],
        session_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        STAGE 1: Quick binary classification - Is this SAFE or SUSPICIOUS?
        
        This is a fast, lightweight check that runs on all packages.
        Decision: "safe" → STOP (skip Stage 2)
                 "suspicious" → Proceed to Stage 2
        """
        
        if not self.api_available:
            return self._fallback_stage1(package)

        # Prepare context summary
        context = self._extract_context_summary(package, session_info)

        prompt = f"""You are an academic integrity monitor for a university computer system.
Your task is to make a QUICK BINARY DECISION: Is this student activity SAFE or SUSPICIOUS?

CONTEXT:
{self._format_context(context)}

ACTIVITY SUMMARY:
{self._format_package_summary(package)}

Based on this snapshot, make a QUICK decision:
- SAFE: Normal, legitimate student behavior - no concerns
- SUSPICIOUS: Something warrants deeper investigation
- UNCERTAIN: Mixed signals, needs investigation

Respond ONLY with valid JSON (no markdown, no extra text):
{{
  "decision": "safe|suspicious|uncertain",
  "confidence": 0.0-1.0,
  "brief_reason": "1-2 sentences explaining decision"
}}
"""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Clean markdown if present
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()
            if text.endswith("```"):
                text = text[:-3].strip()

            result = json.loads(text)
            result["tokens_used"] = getattr(response.usage_metadata, 'total_token_count', 0) if hasattr(response, 'usage_metadata') else 0
            
            # Ensure valid decision values
            if result.get("decision") not in ["safe", "suspicious", "uncertain"]:
                result["decision"] = "uncertain"
            
            return result

        except Exception as e:
            logger.error(f"Stage 1 analysis failed: {e}")
            return {
                "decision": "uncertain",
                "confidence": 0.0,
                "brief_reason": f"Analysis error: {str(e)}",
                "tokens_used": 0
            }

    async def _stage2_detailed_analysis(
        self,
        package: Dict[str, Any],
        stage1_result: Dict[str, Any],
        session_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        STAGE 2: Deep Analysis - Answer "What is sus, where is sus, why is sus, what to do?"
        
        This runs ONLY when Stage 1 decides something is suspicious.
        Creates a detailed violation report for teacher/IT review.
        """

        if not self.api_available:
            return self._fallback_stage2(package, stage1_result)

        context = self._extract_context_summary(package, session_info)

        prompt = f"""You are creating a detailed academic integrity violation report.
A student's computer activity has been flagged as SUSPICIOUS. Investigate thoroughly.

CONTEXT:
{self._format_context(context)}

DETAILED ACTIVITY DATA:
{self._format_detailed_package(package)}

Your task: Identify ALL violations, explain what's wrong, where it is, why it's a violation, and recommend actions.

Respond ONLY with valid JSON (no markdown, no extra text):
{{
  "violations": [
    {{
      "type": "unauthorized_resources|cheating_tools|exam_chat|data_exfiltration|impersonation|unusual_behavior|policy_violation|technical_issue",
      "severity": "low|medium|high|critical",
      "location": "where this was detected (e.g., 'In window title: ...')",
      "description": "What is suspicious about this activity",
      "evidence": ["evidence1", "evidence2", "evidence3"],
      "why_violation": "Why this violates academic integrity policy"
    }}
  ],
  "overall_assessment": "2-3 sentence summary of the situation",
  "recommended_actions": [
    {{
      "action": "action_name",
      "priority": "low|medium|high",
      "description": "Specific action to take",
      "reason": "Why this action is needed"
    }}
  ],
  "teacher_notes": "Additional context for teacher/IT staff (e.g., whether this looks intentional, if system error possible, etc.)"
}}
"""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Clean markdown if present
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()
            if text.endswith("```"):
                text = text[:-3].strip()

            result = json.loads(text)
            result["tokens_used"] = getattr(response.usage_metadata, 'total_token_count', 0) if hasattr(response, 'usage_metadata') else 0
            
            return result

        except Exception as e:
            logger.error(f"Stage 2 analysis failed: {e}")
            return {
                "violations": [
                    {
                        "type": "technical_issue",
                        "severity": "medium",
                        "location": "Analysis service",
                        "description": "Automated analysis encountered an error",
                        "evidence": [str(e)],
                        "why_violation": "Unable to complete analysis"
                    }
                ],
                "overall_assessment": "Analysis service error. Manual review recommended.",
                "recommended_actions": [
                    {
                        "action": "manual_review",
                        "priority": "medium",
                        "description": "Review this package manually",
                        "reason": "Automated analysis failed"
                    }
                ],
                "teacher_notes": f"Error during analysis: {str(e)}",
                "tokens_used": 0
            }

    def _extract_context_summary(
        self,
        package: Dict[str, Any],
        session_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Extract key context from package and session info."""
        return {
            "course_name": session_info.get("course_name", "Unknown Course") if session_info else "Unknown",
            "assessment_type": session_info.get("assessment_type", "Exam") if session_info else "Exam",
            "assessment_name": session_info.get("assessment_name", "Assessment") if session_info else "Assessment",
            "duration_minutes": session_info.get("duration_minutes", 0) if session_info else 0,
            "student_behavior_baseline": session_info.get("baseline_behavior", "Standard exam") if session_info else "Standard",
        }

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context for the prompt."""
        return f"""Course: {context.get('course_name')}
Assessment: {context.get('assessment_type')} - {context.get('assessment_name')}
Duration: {context.get('duration_minutes')} minutes
Student Baseline: {context.get('student_behavior_baseline')}"""

    def _format_package_summary(self, package: Dict[str, Any]) -> str:
        """Format package summary for Stage 1 prompt."""
        summary = []
        
        # Active application
        window_title = package.get('process_data', {}).get('window_title', 'Unknown')
        summary.append(f"Active Window: {window_title}")
        
        # CPU/Memory
        cpu = package.get('system_metrics', {}).get('cpu_usage', 0)
        memory = package.get('system_metrics', {}).get('memory_usage', 0)
        summary.append(f"System: CPU {cpu}%, Memory {memory}%")
        
        # Focus
        focus = package.get('focus_metrics', {}).get('focus_score', 0.5)
        summary.append(f"Focus Score: {focus:.2f}/1.0")
        
        # Network
        bytes_sent = package.get('network_activity', {}).get('bytes_sent', 0)
        bytes_recv = package.get('network_activity', {}).get('bytes_received', 0)
        summary.append(f"Network: {bytes_sent/(1024*1024):.2f}MB up, {bytes_recv/(1024*1024):.2f}MB down")
        
        # App switches
        app_switches = package.get('process_data', {}).get('app_switches', 0)
        summary.append(f"App Switches: {app_switches}")
        
        return "\n".join(summary)

    def _format_detailed_package(self, package: Dict[str, Any]) -> str:
        """Format detailed package data for Stage 2 prompt."""
        details = []
        
        # Process data
        process_data = package.get('process_data', {})
        if process_data:
            details.append("PROCESS DATA:")
            details.append(f"  - Active Window: {process_data.get('window_title', 'Unknown')}")
            details.append(f"  - Process Name: {process_data.get('process_name', 'Unknown')}")
            details.append(f"  - App Switches: {process_data.get('app_switches', 0)}")
            
            # App list
            apps = process_data.get('running_processes', [])
            if apps:
                details.append(f"  - Running Apps: {', '.join(apps[:5])}")
        
        # Network activity
        network = package.get('network_activity', {})
        if network:
            details.append("NETWORK ACTIVITY:")
            details.append(f"  - Bytes Sent: {network.get('bytes_sent', 0)/(1024*1024):.2f}MB")
            details.append(f"  - Bytes Received: {network.get('bytes_received', 0)/(1024*1024):.2f}MB")
            details.append(f"  - Connections: {network.get('active_connections', 0)}")
        
        # Focus metrics
        focus = package.get('focus_metrics', {})
        if focus:
            details.append("FOCUS METRICS:")
            details.append(f"  - Focus Score: {focus.get('focus_score', 0):.2f}/1.0")
            details.append(f"  - Distractions: {focus.get('distraction_count', 0)}")
        
        # Input dynamics
        input_data = package.get('input_dynamics', {})
        if input_data:
            details.append("INPUT DYNAMICS:")
            details.append(f"  - Keystroke Variance: {input_data.get('keystroke_rhythm_variance', 0):.2f}")
            details.append(f"  - Mouse Idle: {input_data.get('mouse_idle_duration', 0)}s")
        
        return "\n".join(details)

    def _fallback_stage1(self, package: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback Stage 1 analysis when API not available."""
        # Quick heuristics for Stage 1
        cpu = package.get('system_metrics', {}).get('cpu_usage', 0)
        memory = package.get('system_metrics', {}).get('memory_usage', 0)
        focus = package.get('focus_metrics', {}).get('focus_score', 0.5)
        network_sent = package.get('network_activity', {}).get('bytes_sent', 0)
        app_switches = package.get('process_data', {}).get('app_switches', 0)
        
        # Decision logic
        decision = "safe"
        confidence = 0.8
        reason = "Activity appears normal"
        
        # Check for obvious red flags
        if network_sent > 50 * 1024 * 1024:  # 50MB upload
            decision = "suspicious"
            confidence = 0.9
            reason = "Excessive network upload detected"
        elif app_switches > 20:
            decision = "suspicious"
            confidence = 0.7
            reason = "Excessive application switching"
        elif focus < 0.2 and (cpu > 80 or app_switches > 10):
            decision = "suspicious"
            confidence = 0.6
            reason = "Low focus with high activity"
        elif cpu > 95 or memory > 95:
            decision = "suspicious"
            confidence = 0.5
            reason = "Extreme system resource usage"
        
        return {
            "decision": decision,
            "confidence": confidence,
            "brief_reason": reason,
            "tokens_used": 0
        }

    def _fallback_stage2(
        self,
        package: Dict[str, Any],
        stage1: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback Stage 2 analysis when API not available."""
        violations = []
        
        # Check network
        network_sent = package.get('network_activity', {}).get('bytes_sent', 0)
        if network_sent > 50 * 1024 * 1024:
            violations.append({
                "type": "data_exfiltration",
                "severity": "critical",
                "location": "Network Activity",
                "description": f"Uploaded {network_sent/(1024*1024):.2f}MB - excessive for exam",
                "evidence": [f"Network sent: {network_sent/(1024*1024):.2f}MB"],
                "why_violation": "Large data uploads could indicate copying exam data or answers"
            })
        
        # Check app switching
        app_switches = package.get('process_data', {}).get('app_switches', 0)
        if app_switches > 20:
            violations.append({
                "type": "unauthorized_resources",
                "severity": "high",
                "location": "Application Usage",
                "description": f"{app_switches} application switches detected",
                "evidence": [f"App switches: {app_switches}"],
                "why_violation": "Frequent switching suggests looking for external resources"
            })
        
        return {
            "violations": violations if violations else [{
                "type": "unusual_behavior",
                "severity": "medium",
                "location": "Overall Activity",
                "description": stage1.get("brief_reason", "Suspicious activity detected"),
                "evidence": ["Activity flagged by Stage 1"],
                "why_violation": "Further review recommended"
            }],
            "overall_assessment": "Automatic analysis completed. Manual review by instructor recommended.",
            "recommended_actions": [
                {
                    "action": "manual_review",
                    "priority": "medium",
                    "description": "Have instructor review the activity",
                    "reason": "Automated tools suggest closer examination needed"
                }
            ],
            "teacher_notes": "Fallback analysis used - consider enabling Gemini API for full analysis",
            "tokens_used": 0
        }
