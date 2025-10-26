"""
Dashboard API Routes for Education Analyzer

Handles:
1. Receiving student activity packages from dashboard
2. Running two-stage educational integrity analysis
3. Returning results with violation reports (if suspicious)
4. Managing analysis history
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime
from education_analyzer import EducationAnalyzer

logger = logging.getLogger(__name__)

# Global analyzer instance
_analyzer: Optional[EducationAnalyzer] = None


def get_analyzer() -> EducationAnalyzer:
    """Get or create the analyzer instance."""
    global _analyzer
    if _analyzer is None:
        import os
        api_key = os.getenv("GEMINI_API_KEY", "")
        _analyzer = EducationAnalyzer(api_key)
    return _analyzer


router = APIRouter(prefix="/api/analysis", tags=["educational_analysis"])


@router.post("/analyze-package")
async def analyze_package(
    request: Dict[str, Any],
    analyzer: EducationAnalyzer = Depends(get_analyzer)
) -> Dict[str, Any]:
    """
    Analyze a student activity package using the two-stage process.
    
    Request body:
    {
        "student_id": "string (required)",
        "package": {
            "process_data": {...},
            "system_metrics": {...},
            "network_activity": {...},
            "focus_metrics": {...},
            "input_dynamics": {...}
        },
        "session_info": {
            "course_name": "string",
            "assessment_type": "string (Exam|Assignment|Quiz)",
            "assessment_name": "string",
            "duration_minutes": "int",
            "baseline_behavior": "string"
        }
    }
    
    Response:
    {
        "analysis_id": "uuid",
        "timestamp": "ISO8601",
        "student_id": "string",
        "stage1_result": {
            "decision": "safe|suspicious|uncertain",
            "confidence": float,
            "brief_reason": "string"
        },
        "stage2_result": {  // Only if suspicious
            "violations": [...],
            "overall_assessment": "string",
            "recommended_actions": [...],
            "teacher_notes": "string"
        },
        "skip_stage2": bool,
        "tokens_used": int
    }
    """
    try:
        # Validate input
        student_id = request.get("student_id")
        package = request.get("package")
        session_info = request.get("session_info")
        
        if not student_id:
            raise HTTPException(status_code=400, detail="student_id is required")
        if not package:
            raise HTTPException(status_code=400, detail="package is required")
        
        logger.info(f"Starting analysis for student: {student_id}")
        
        # Run the two-stage analysis
        result = await analyzer.analyze_package(
            package=package,
            student_id=student_id,
            session_info=session_info
        )
        
        logger.info(
            f"Analysis complete [ID: {result['analysis_id']}] - "
            f"Decision: {result['stage1_result']['decision']}, "
            f"Skip Stage 2: {result['skip_stage2']}"
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze-batch")
async def analyze_batch(
    request: Dict[str, Any],
    analyzer: EducationAnalyzer = Depends(get_analyzer)
) -> Dict[str, Any]:
    """
    Analyze multiple student packages in batch.
    
    Request body:
    {
        "packages": [
            {
                "student_id": "string",
                "package": {...},
                "session_info": {...}
            }
        ]
    }
    
    Response:
    {
        "batch_id": "uuid",
        "total_packages": int,
        "results": [
            {analysis results for each package}
        ],
        "summary": {
            "safe_count": int,
            "suspicious_count": int,
            "uncertain_count": int,
            "total_violations": int
        }
    }
    """
    try:
        import uuid
        import asyncio
        
        packages = request.get("packages", [])
        if not packages:
            raise HTTPException(status_code=400, detail="packages list is required")
        
        batch_id = str(uuid.uuid4())
        logger.info(f"Starting batch analysis [ID: {batch_id}] for {len(packages)} packages")
        
        # Analyze all packages
        results = []
        for pkg_data in packages:
            result = await analyzer.analyze_package(
                package=pkg_data.get("package"),
                student_id=pkg_data.get("student_id"),
                session_info=pkg_data.get("session_info")
            )
            results.append(result)
        
        # Compute summary
        safe_count = sum(1 for r in results if r["stage1_result"]["decision"] == "safe")
        suspicious_count = sum(1 for r in results if r["stage1_result"]["decision"] == "suspicious")
        uncertain_count = sum(1 for r in results if r["stage1_result"]["decision"] == "uncertain")
        
        total_violations = sum(
            len(r.get("stage2_result", {}).get("violations", []))
            for r in results
            if not r.get("skip_stage2")
        )
        
        summary = {
            "batch_id": batch_id,
            "total_packages": len(packages),
            "safe_count": safe_count,
            "suspicious_count": suspicious_count,
            "uncertain_count": uncertain_count,
            "total_violations": total_violations,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Batch analysis complete: {summary}")
        
        return {
            "batch_id": batch_id,
            "total_packages": len(packages),
            "results": results,
            "summary": summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")


@router.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str) -> Dict[str, Any]:
    """
    Retrieve a specific analysis result.
    
    Note: In a real implementation, this would query the database.
    For now, returns a placeholder.
    """
    # This would be implemented with database storage
    # For now, returning a template response
    return {
        "analysis_id": analysis_id,
        "message": "Analysis retrieval would query database",
        "status": "not_implemented_yet"
    }


@router.get("/dashboard/statistics")
async def get_statistics(
    course_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get statistical summary of analyses for dashboard display.
    
    This would be implemented with database queries.
    """
    return {
        "course_id": course_id,
        "start_date": start_date,
        "end_date": end_date,
        "stats": {
            "total_analyses": 0,
            "safe": 0,
            "suspicious": 0,
            "uncertain": 0,
            "violations_total": 0,
            "top_violations": []
        },
        "message": "Statistics retrieval requires database implementation"
    }


@router.post("/export-report")
async def export_report(
    request: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Export a detailed report for teacher/IT staff review.
    
    Request body:
    {
        "analysis_id": "string",
        "student_id": "string",
        "format": "pdf|html|json"
    }
    """
    analysis_id = request.get("analysis_id")
    student_id = request.get("student_id")
    export_format = request.get("format", "json").lower()
    
    if export_format not in ["json", "html", "pdf"]:
        raise HTTPException(status_code=400, detail="format must be json, html, or pdf")
    
    # This would generate a formatted report from the analysis
    return {
        "analysis_id": analysis_id,
        "student_id": student_id,
        "format": export_format,
        "export_url": f"/reports/{analysis_id}.{export_format}",
        "message": "Report export would be generated here"
    }
