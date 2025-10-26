"""
Automatic Report Generation System

Generates documentation and flag reports automatically when suspicious activity is detected.
Reports are saved as HTML, JSON, and markdown files for easy viewing and sharing.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import uuid

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates automatic documentation and flag reports."""

    def __init__(self, reports_dir: str = "flag_reports"):
        """Initialize report generator with output directory."""
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.html_dir = self.reports_dir / "html"
        self.json_dir = self.reports_dir / "json"
        self.markdown_dir = self.reports_dir / "markdown"
        
        for dir_path in [self.html_dir, self.json_dir, self.markdown_dir]:
            dir_path.mkdir(exist_ok=True)
        
        logger.info(f"✅ Report Generator initialized at: {self.reports_dir}")

    def generate_flag_report(
        self,
        student_id: str,
        analysis_result: Dict[str, Any],
        session_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        """
        Generate comprehensive flag report in multiple formats.
        
        Returns: {
            "report_id": "unique-id",
            "html_path": "path/to/report.html",
            "json_path": "path/to/report.json",
            "markdown_path": "path/to/report.md",
            "timestamp": "ISO8601"
        }
        """
        report_id = str(uuid.uuid4())[:8]
        timestamp = datetime.utcnow().isoformat()
        
        # Prepare report data
        report_data = {
            "report_id": report_id,
            "timestamp": timestamp,
            "student_id": student_id,
            "session_info": session_info or {},
            "analysis": analysis_result,
        }
        
        # Generate reports
        html_path = self._generate_html_report(report_id, report_data)
        json_path = self._generate_json_report(report_id, report_data)
        markdown_path = self._generate_markdown_report(report_id, report_data)
        
        logger.info(f"✅ Generated flag report for {student_id}: {report_id}")
        
        return {
            "report_id": report_id,
            "html_path": str(html_path),
            "json_path": str(json_path),
            "markdown_path": str(markdown_path),
            "timestamp": timestamp,
        }

    def _generate_html_report(self, report_id: str, data: Dict[str, Any]) -> Path:
        """Generate HTML report for browser viewing."""
        html_path = self.html_dir / f"{report_id}.html"
        
        analysis = data.get("analysis", {})
        stage1 = analysis.get("stage1_result", {})
        stage2 = analysis.get("stage2_result", {})
        
        is_safe = analysis.get("skip_stage2", False)
        decision = stage1.get("decision", "unknown").upper()
        
        # Build HTML
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flag Report - {data['student_id']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        
        .header {{ border-bottom: 3px solid #333; padding-bottom: 20px; margin-bottom: 30px; }}
        .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
        .header p {{ color: #666; font-size: 14px; }}
        
        .decision-badge {{
            display: inline-block;
            padding: 10px 20px;
            border-radius: 5px;
            font-weight: bold;
            font-size: 16px;
            margin: 10px 0;
        }}
        .decision-badge.safe {{
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        .decision-badge.suspicious {{
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
        
        .section {{
            margin: 30px 0;
            padding: 20px;
            background: #f9f9f9;
            border-left: 4px solid #007bff;
            border-radius: 4px;
        }}
        .section h2 {{
            font-size: 20px;
            margin-bottom: 15px;
            color: #333;
        }}
        .section h3 {{
            font-size: 16px;
            margin-top: 15px;
            margin-bottom: 10px;
            color: #555;
        }}
        
        .stage1-section {{
            border-left-color: #28a745;
        }}
        .stage2-section {{
            border-left-color: #dc3545;
        }}
        
        .violation-card {{
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #dc3545;
            border-radius: 4px;
        }}
        .violation-type {{
            font-weight: bold;
            color: #dc3545;
            font-size: 14px;
        }}
        .violation-severity {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
            margin-left: 10px;
        }}
        .severity-low {{ background: #d1ecf1; color: #0c5460; }}
        .severity-medium {{ background: #fff3cd; color: #856404; }}
        .severity-high {{ background: #f8d7da; color: #721c24; }}
        .severity-critical {{ background: #d4d8db; color: #1c2529; }}
        
        .evidence-list {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .evidence-list li {{
            list-style: disc;
            margin: 5px 0;
            color: #666;
        }}
        
        .action-item {{
            background: #e7f3ff;
            padding: 12px;
            margin: 10px 0;
            border-radius: 4px;
            border-left: 3px solid #007bff;
        }}
        .action-priority {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: bold;
            margin-right: 8px;
        }}
        .priority-low {{ background: #d1ecf1; color: #0c5460; }}
        .priority-medium {{ background: #fff3cd; color: #856404; }}
        .priority-high {{ background: #f8d7da; color: #721c24; }}
        
        .metadata {{
            font-size: 12px;
            color: #999;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #999;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚨 Student Activity Flag Report</h1>
            <p>Report ID: {data['report_id']} | Generated: {data['timestamp']}</p>
        </div>
        
        <!-- Student Info -->
        <div class="section">
            <h2>Student Information</h2>
            <p><strong>Student ID:</strong> {data['student_id']}</p>
            <p><strong>Course:</strong> {data['session_info'].get('course_name', 'N/A')}</p>
            <p><strong>Assessment:</strong> {data['session_info'].get('assessment_name', 'N/A')}</p>
        </div>
        
        <!-- Stage 1 Decision -->
        <div class="section stage1-section">
            <h2>✓ Stage 1: Quick Safety Assessment</h2>
            <div class="decision-badge {'safe' if is_safe else 'suspicious'}">
                {decision}: {stage1.get('brief_reason', 'N/A')}
            </div>
            <p><strong>Confidence:</strong> {stage1.get('confidence', 0):.1%}</p>
        </div>
        
        {self._generate_html_stage2(stage2) if not is_safe else '<div class="section"><h3>✅ No violations detected - activity marked as safe</h3></div>'}
        
        <!-- Metadata -->
        <div class="metadata">
            <p>Report ID: {data['report_id']}</p>
            <p>Tokens Used: {analysis.get('tokens_used', 0)}</p>
            <p>Model: {analysis.get('model_version', 'N/A')}</p>
        </div>
        
        <div class="footer">
            <p>This report was automatically generated by the Educational Integrity Analysis System.</p>
            <p>For questions, contact your IT department or academic advisor.</p>
        </div>
    </div>
</body>
</html>
"""
        
        html_path.write_text(html_content)
        return html_path

    def _generate_html_stage2(self, stage2: Dict[str, Any]) -> str:
        """Generate HTML for Stage 2 violations section."""
        if not stage2:
            return ""
        
        violations_html = ""
        for violation in stage2.get("violations", []):
            evidence_list = "".join(
                f"<li>{e}</li>" for e in violation.get("evidence", [])
            )
            
            severity = violation.get("severity", "medium").lower()
            violations_html += f"""
            <div class="violation-card">
                <div>
                    <span class="violation-type">{violation.get('type', 'unknown').replace('_', ' ').title()}</span>
                    <span class="violation-severity severity-{severity}">{severity.upper()}</span>
                </div>
                <p><strong>Location:</strong> {violation.get('location', 'N/A')}</p>
                <p><strong>Description:</strong> {violation.get('description', 'N/A')}</p>
                <p><strong>Why it's a violation:</strong> {violation.get('why_violation', 'N/A')}</p>
                <h3>Evidence:</h3>
                <ul class="evidence-list">{evidence_list}</ul>
            </div>
            """
        
        actions_html = ""
        for action in stage2.get("recommended_actions", []):
            priority = action.get("priority", "medium").lower()
            actions_html += f"""
            <div class="action-item">
                <span class="action-priority priority-{priority}">{priority.upper()}</span>
                <strong>{action.get('action', 'N/A').replace('_', ' ').title()}</strong>
                <p>{action.get('description', 'N/A')}</p>
                <p style="font-size: 12px; color: #666;">Reason: {action.get('reason', 'N/A')}</p>
            </div>
            """
        
        return f"""
        <div class="section stage2-section">
            <h2>⚠️ Stage 2: Detailed Violation Analysis</h2>
            <h3>Violations Found ({len(stage2.get('violations', []))})</h3>
            {violations_html}
            
            <h3>Overall Assessment</h3>
            <p>{stage2.get('overall_assessment', 'N/A')}</p>
            
            <h3>Recommended Actions ({len(stage2.get('recommended_actions', []))})</h3>
            {actions_html}
            
            <h3>Teacher Notes</h3>
            <p>{stage2.get('teacher_notes', 'N/A')}</p>
        </div>
        """

    def _generate_json_report(self, report_id: str, data: Dict[str, Any]) -> Path:
        """Generate JSON report for machine processing."""
        json_path = self.json_dir / f"{report_id}.json"
        json_path.write_text(json.dumps(data, indent=2))
        return json_path

    def _generate_markdown_report(self, report_id: str, data: Dict[str, Any]) -> Path:
        """Generate Markdown report for documentation."""
        md_path = self.markdown_dir / f"{report_id}.md"
        
        analysis = data.get("analysis", {})
        stage1 = analysis.get("stage1_result", {})
        stage2 = analysis.get("stage2_result", {})
        is_safe = analysis.get("skip_stage2", False)
        
        md_content = f"""# 🚨 Flag Report: {data['student_id']}

**Report ID:** {data['report_id']}  
**Generated:** {data['timestamp']}

## 📋 Student Information

- **Student ID:** {data['student_id']}
- **Course:** {data['session_info'].get('course_name', 'N/A')}
- **Assessment:** {data['session_info'].get('assessment_name', 'N/A')}
- **Duration:** {data['session_info'].get('duration_minutes', 'N/A')} minutes

---

## ✓ Stage 1: Quick Safety Assessment

**Decision:** {stage1.get('decision', 'unknown').upper()}  
**Confidence:** {stage1.get('confidence', 0):.1%}  
**Reason:** {stage1.get('brief_reason', 'N/A')}

"""
        
        if not is_safe and stage2:
            md_content += f"""
---

## ⚠️ Stage 2: Detailed Violation Analysis

### Violations Found ({len(stage2.get('violations', []))})

"""
            for i, violation in enumerate(stage2.get("violations", []), 1):
                md_content += f"""
#### {i}. {violation.get('type', 'Unknown').replace('_', ' ').title()}

- **Severity:** {violation.get('severity', 'unknown').upper()}
- **Location:** {violation.get('location', 'N/A')}
- **Description:** {violation.get('description', 'N/A')}
- **Why it's a violation:** {violation.get('why_violation', 'N/A')}

**Evidence:**
"""
                for evidence in violation.get("evidence", []):
                    md_content += f"- {evidence}\n"

            md_content += f"""
### Overall Assessment

{stage2.get('overall_assessment', 'N/A')}

### Recommended Actions ({len(stage2.get('recommended_actions', []))})

"""
            for i, action in enumerate(stage2.get("recommended_actions", []), 1):
                md_content += f"""
{i}. **{action.get('action', 'N/A').replace('_', ' ').title()}** [{action.get('priority', 'N/A').upper()}]
   - {action.get('description', 'N/A')}
   - Reason: {action.get('reason', 'N/A')}

"""
            md_content += f"""
### Teacher Notes

{stage2.get('teacher_notes', 'N/A')}

"""
        else:
            md_content += "\n✅ **No violations detected** - Activity marked as safe.\n"
        
        md_content += f"""
---

## 📊 Analysis Details

- **Tokens Used:** {analysis.get('tokens_used', 0)}
- **Model Version:** {analysis.get('model_version', 'N/A')}
- **Analysis ID:** {analysis.get('analysis_id', 'N/A')}

---

*This report was automatically generated by the Educational Integrity Analysis System.*
"""
        
        md_path.write_text(md_content)
        return md_path

    def generate_index_page(self) -> Path:
        """Generate HTML index of all reports."""
        index_path = self.reports_dir / "index.html"
        
        # Collect all reports
        html_files = sorted(self.html_dir.glob("*.html"))
        
        reports_list = "".join(
            f'<tr><td><a href="html/{f.name}">{f.stem}</a></td><td>{f.stat().st_mtime}</td></tr>'
            for f in html_files[-20:]  # Last 20 reports
        )
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Flag Reports - Index</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
        h1 {{ color: #333; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #333; color: white; }}
        tr:hover {{ background: #f5f5f5; }}
        a {{ color: #007bff; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Flag Reports Index</h1>
        <p>Last 20 reports:</p>
        <table>
            <tr>
                <th>Report ID</th>
                <th>Generated</th>
            </tr>
            {reports_list}
        </table>
    </div>
</body>
</html>
"""
        
        index_path.write_text(html_content)
        return index_path


def auto_generate_reports_on_flag(
    student_id: str,
    analysis_result: Dict[str, Any],
    session_info: Optional[Dict[str, Any]] = None,
) -> Dict[str, str]:
    """
    Convenience function to automatically generate reports.
    
    Call this whenever a suspicious activity is flagged.
    """
    generator = ReportGenerator()
    
    # Generate reports
    report_paths = generator.generate_flag_report(
        student_id=student_id,
        analysis_result=analysis_result,
        session_info=session_info,
    )
    
    # Update index
    generator.generate_index_page()
    
    logger.info(f"✅ Auto-generated reports for {student_id}")
    logger.info(f"   HTML: {report_paths['html_path']}")
    logger.info(f"   JSON: {report_paths['json_path']}")
    logger.info(f"   Markdown: {report_paths['markdown_path']}")
    
    return report_paths
