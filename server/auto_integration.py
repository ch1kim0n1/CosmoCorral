"""
Automatic Integration Module

Hooks into the main server to automatically analyze packages, generate reports,
and send results back to the dashboard in real-time.

This is the "glue" between the WebSocket server and the analysis/report system.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime

from education_analyzer import EducationAnalyzer
from auto_report_generator import auto_generate_reports_on_flag

logger = logging.getLogger(__name__)


class AutomaticAnalysisOrchestrator:
    """
    Orchestrates automatic analysis and report generation.
    
    When a package is received from the dashboard:
    1. Auto-analyze it using EducationAnalyzer
    2. If suspicious: Auto-generate reports
    3. Send results back to dashboard via WebSocket
    """

    def __init__(self, analysis_callback: Optional[Callable] = None):
        """
        Initialize orchestrator.
        
        Args:
            analysis_callback: Async function to send results to WebSocket clients
                              Signature: async def callback(message: Dict, client_id: Optional[str])
        """
        self.analyzer = EducationAnalyzer()
        self.analysis_callback = analysis_callback
        self.active_analyses: Dict[str, Dict[str, Any]] = {}
        
        logger.info("✅ AutomaticAnalysisOrchestrator initialized")

    async def process_package(
        self,
        package_data: Dict[str, Any],
        student_id: str,
        course_id: Optional[str] = None,
        client_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Automatically process a package: analyze + generate reports + send results.
        
        This is the main entry point - call this when WebSocket receives a package.
        
        Args:
            package_data: The package JSON from student's device
            student_id: Student ID to analyze
            course_id: Course ID (optional)
            client_id: WebSocket client ID to send results to (optional)
            
        Returns:
            Result dictionary with analysis, reports, and status
        """
        try:
            logger.info(f"📦 Processing package for {student_id}...")
            
            # Track this analysis
            analysis_id = f"{student_id}_{datetime.utcnow().isoformat()}"
            self.active_analyses[analysis_id] = {
                "status": "analyzing",
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            # Send status update
            await self._send_status_update(
                client_id,
                "analyzing",
                f"Stage 1: Running quick safety assessment...",
                analysis_id,
            )
            
            # Analyze the package
            analysis_result = await self.analyzer.analyze_package(package_data)
            
            # Update tracking
            self.active_analyses[analysis_id]["analysis"] = analysis_result
            
            # Check if suspicious
            is_suspicious = not analysis_result.get("skip_stage2", False)
            
            if is_suspicious:
                logger.info(f"🚨 Package flagged as suspicious for {student_id}")
                
                # Send update
                await self._send_status_update(
                    client_id,
                    "generating_reports",
                    f"Stage 2 analysis complete - Generating reports...",
                    analysis_id,
                )
                
                # Auto-generate reports
                session_info = {
                    "student_id": student_id,
                    "course_id": course_id or "N/A",
                    "assessment_name": package_data.get("assessment_name", "Unknown"),
                    "duration_minutes": package_data.get("duration_minutes", 0),
                }
                
                report_paths = auto_generate_reports_on_flag(
                    student_id=student_id,
                    analysis_result=analysis_result,
                    session_info=session_info,
                )
                
                # Add report paths to result
                analysis_result["auto_generated_reports"] = report_paths
                
                # Send report notification
                await self._send_flag_notification(
                    client_id,
                    student_id,
                    analysis_result,
                    report_paths,
                    analysis_id,
                )
                
            else:
                logger.info(f"✅ Package marked as safe for {student_id}")
                
                # Send completion status
                await self._send_status_update(
                    client_id,
                    "complete",
                    f"Activity marked as SAFE - No violations detected",
                    analysis_id,
                )
            
            # Update final status
            self.active_analyses[analysis_id]["status"] = "complete"
            
            return {
                "status": "success",
                "analysis_id": analysis_id,
                "student_id": student_id,
                "is_suspicious": is_suspicious,
                "analysis": analysis_result,
                "reports": analysis_result.get("auto_generated_reports", {}) if is_suspicious else None,
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing package: {str(e)}", exc_info=True)
            
            # Send error notification
            await self._send_error_notification(client_id, str(e), student_id)
            
            return {
                "status": "error",
                "student_id": student_id,
                "error": str(e),
            }

    async def _send_status_update(
        self,
        client_id: Optional[str],
        status: str,
        message: str,
        analysis_id: str,
    ) -> None:
        """Send status update to client."""
        if not self.analysis_callback:
            return
        
        payload = {
            "type": "AnalysisStatus",
            "analysis_id": analysis_id,
            "status": status,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        await self.analysis_callback(payload, client_id)

    async def _send_flag_notification(
        self,
        client_id: Optional[str],
        student_id: str,
        analysis_result: Dict[str, Any],
        report_paths: Dict[str, str],
        analysis_id: str,
    ) -> None:
        """Send flag notification with report links."""
        stage2 = analysis_result.get("stage2_result", {})
        violations = stage2.get("violations", [])
        
        payload = {
            "type": "FlagNotification",
            "analysis_id": analysis_id,
            "student_id": student_id,
            "severity": "High",
            "title": f"🚨 Suspicious Activity Detected for {student_id}",
            "violation_count": len(violations),
            "violations_summary": [
                {
                    "type": v.get("type"),
                    "severity": v.get("severity"),
                    "description": v.get("description"),
                }
                for v in violations[:3]  # Top 3 violations
            ],
            "report_links": {
                "html": report_paths.get("html_path"),
                "json": report_paths.get("json_path"),
                "markdown": report_paths.get("markdown_path"),
            },
            "recommended_actions": stage2.get("recommended_actions", [])[:3],
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        await self.analysis_callback(payload, client_id)

    async def _send_error_notification(
        self,
        client_id: Optional[str],
        error_msg: str,
        student_id: str,
    ) -> None:
        """Send error notification to client."""
        if not self.analysis_callback:
            return
        
        payload = {
            "type": "AnalysisError",
            "student_id": student_id,
            "error": error_msg,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        await self.analysis_callback(payload, client_id)

    def get_analysis_status(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an ongoing or completed analysis."""
        return self.active_analyses.get(analysis_id)

    def get_all_active_analyses(self) -> Dict[str, Dict[str, Any]]:
        """Get all active analyses."""
        return {
            aid: info
            for aid, info in self.active_analyses.items()
            if info.get("status") != "complete"
        }


# Global instance
_orchestrator: Optional[AutomaticAnalysisOrchestrator] = None


def initialize_orchestrator(callback: Optional[Callable] = None) -> AutomaticAnalysisOrchestrator:
    """Initialize the global orchestrator instance."""
    global _orchestrator
    _orchestrator = AutomaticAnalysisOrchestrator(callback)
    return _orchestrator


def get_orchestrator() -> AutomaticAnalysisOrchestrator:
    """Get the global orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AutomaticAnalysisOrchestrator()
    return _orchestrator


# Example usage - call this from your WebSocket handler
async def handle_package_auto(
    package_data: Dict[str, Any],
    student_id: str,
    course_id: Optional[str] = None,
    client_id: Optional[str] = None,
    send_callback: Optional[Callable] = None,
) -> Dict[str, Any]:
    """
    Handle package with automatic analysis and reporting.
    
    INTEGRATION EXAMPLE:
    =====================
    In your main.py WebSocket handler, replace manual analysis calls with:
    
        from auto_integration import handle_package_auto
        
        # When you receive a "Package" method from client:
        result = await handle_package_auto(
            package_data=data,
            student_id=data.get("student_id"),
            course_id=data.get("course_id"),
            client_id=websocket.remote_address[1],  # or unique client ID
            send_callback=async_send_to_client,  # function to send WebSocket messages
        )
    """
    # Initialize if needed
    orchestrator = get_orchestrator()
    
    # Set callback if provided
    if send_callback:
        orchestrator.analysis_callback = send_callback
    
    # Process package
    return await orchestrator.process_package(
        package_data=package_data,
        student_id=student_id,
        course_id=course_id,
        client_id=client_id,
    )
