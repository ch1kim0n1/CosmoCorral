"""
Database Schema for Educational Analyzer Results

This module provides SQLAlchemy models and migration scripts for storing
analysis results, violations, and audit trails.

Supports: PostgreSQL, MySQL, SQLite
"""

from datetime import datetime
from sqlalchemy import (
    create_engine, Column, String, Integer, Float, DateTime,
    Text, Boolean, ForeignKey, List, JSON, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import enum

Base = declarative_base()


class SafetyDecisionEnum(str, enum.Enum):
    """Safety classification outcomes."""
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    UNCERTAIN = "uncertain"


class ViolationTypeEnum(str, enum.Enum):
    """Types of academic integrity violations."""
    UNAUTHORIZED_RESOURCES = "unauthorized_resources"
    CHEATING_TOOLS = "cheating_tools"
    EXAM_CHAT = "exam_chat"
    DATA_EXFILTRATION = "data_exfiltration"
    IMPERSONATION = "impersonation"
    UNUSUAL_BEHAVIOR = "unusual_behavior"
    POLICY_VIOLATION = "policy_violation"
    TECHNICAL_ISSUE = "technical_issue"


class SeverityEnum(str, enum.Enum):
    """Violation severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Analysis(Base):
    """
    Stores each analysis run for a student package.
    """
    __tablename__ = 'analyses'
    
    # Primary identifiers
    analysis_id = Column(String(36), primary_key=True, unique=True)
    batch_id = Column(String(36), index=True, nullable=True)  # For batch analyses
    
    # Student & Course info
    student_id = Column(String(50), index=True)
    course_id = Column(String(50), index=True, nullable=True)
    course_name = Column(String(255))
    assessment_type = Column(String(50))  # Exam, Assignment, Quiz
    assessment_name = Column(String(255))
    
    # Analysis metadata
    stage1_decision = Column(SQLEnum(SafetyDecisionEnum))
    stage1_confidence = Column(Float)
    stage1_reason = Column(Text)
    
    skip_stage2 = Column(Boolean, default=False)
    
    # Stage 2 results (if run)
    overall_assessment = Column(Text, nullable=True)
    teacher_notes = Column(Text, nullable=True)
    
    # Resource tracking
    tokens_used = Column(Integer, default=0)
    model_version = Column(String(50), default="gemini-1.5-flash")
    
    # Timestamps
    analyzed_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    violations = relationship(
        "Violation", 
        back_populates="analysis",
        cascade="all, delete-orphan"
    )
    recommended_actions = relationship(
        "RecommendedAction",
        back_populates="analysis",
        cascade="all, delete-orphan"
    )
    audit_entries = relationship(
        "AuditLog",
        back_populates="analysis",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Analysis {self.analysis_id}: {self.student_id} - {self.stage1_decision.value}>"


class Violation(Base):
    """
    Individual violations found in Stage 2 analysis.
    """
    __tablename__ = 'violations'
    
    violation_id = Column(Integer, primary_key=True)
    analysis_id = Column(String(36), ForeignKey('analyses.analysis_id'), index=True)
    
    # Violation details
    violation_type = Column(SQLEnum(ViolationTypeEnum), index=True)
    severity = Column(SQLEnum(SeverityEnum), index=True)
    location = Column(String(255))  # Where in the data
    description = Column(Text)  # What is suspicious
    why_violation = Column(Text)  # Why it violates policy
    
    # Evidence
    evidence = Column(JSON)  # List of evidence strings
    
    # Status tracking
    reviewed = Column(Boolean, default=False)
    reviewed_by = Column(String(50), nullable=True)  # Teacher/IT staff
    reviewed_at = Column(DateTime, nullable=True)
    
    # Relationship
    analysis = relationship("Analysis", back_populates="violations")
    
    def __repr__(self):
        return f"<Violation {self.violation_type.value}: {self.severity.value}>"


class RecommendedAction(Base):
    """
    Recommended actions from Stage 2 analysis.
    """
    __tablename__ = 'recommended_actions'
    
    action_id = Column(Integer, primary_key=True)
    analysis_id = Column(String(36), ForeignKey('analyses.analysis_id'), index=True)
    
    # Action details
    action_name = Column(String(100))  # E.g., "interview_student", "flag_for_review"
    priority = Column(SQLEnum(SeverityEnum))  # low, medium, high
    description = Column(Text)
    reason = Column(Text)
    
    # Status tracking
    status = Column(String(20), default="pending")  # pending, in_progress, completed, dismissed
    assigned_to = Column(String(50), nullable=True)  # Teacher/IT staff
    completed_at = Column(DateTime, nullable=True)
    completion_notes = Column(Text, nullable=True)
    
    # Relationship
    analysis = relationship("Analysis", back_populates="recommended_actions")
    
    def __repr__(self):
        return f"<Action {self.action_name}: {self.status}>"


class AuditLog(Base):
    """
    Audit trail of all actions taken on analyses.
    For compliance and accountability.
    """
    __tablename__ = 'audit_logs'
    
    log_id = Column(Integer, primary_key=True)
    analysis_id = Column(String(36), ForeignKey('analyses.analysis_id'), index=True)
    
    # Action info
    action = Column(String(100))  # analysis_created, violation_reviewed, action_taken, etc.
    actor = Column(String(50))  # User who took action
    actor_role = Column(String(20))  # teacher, it_staff, admin
    
    # Details
    details = Column(JSON)  # Any additional data about the action
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    analysis = relationship("Analysis", back_populates="audit_entries")
    
    def __repr__(self):
        return f"<AuditLog {self.action} at {self.timestamp}>"


class StudentBaseline(Base):
    """
    Store typical behavior patterns for each student to enable
    comparison-based detection of unusual activity.
    """
    __tablename__ = 'student_baselines'
    
    baseline_id = Column(Integer, primary_key=True)
    student_id = Column(String(50), unique=True, index=True)
    course_id = Column(String(50), index=True)
    
    # Average metrics
    avg_focus_score = Column(Float)
    avg_cpu_usage = Column(Float)
    avg_memory_usage = Column(Float)
    avg_app_switches = Column(Float)
    avg_keystroke_variance = Column(Float)
    avg_network_bytes = Column(Float)
    
    # Variance/stddev
    stddev_focus = Column(Float)
    stddev_cpu = Column(Float)
    stddev_memory = Column(Float)
    stddev_app_switches = Column(Float)
    
    # Update info
    samples_analyzed = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Baseline {self.student_id}: {self.samples_analyzed} samples>"


class CoursePolicy(Base):
    """
    Store course-specific policies for analysis customization.
    """
    __tablename__ = 'course_policies'
    
    policy_id = Column(Integer, primary_key=True)
    course_id = Column(String(50), unique=True, index=True)
    
    # Policy details
    course_name = Column(String(255))
    instructor = Column(String(100))
    
    # Exam policies
    allow_external_resources = Column(Boolean, default=False)
    allow_communication = Column(Boolean, default=False)
    allow_multiple_windows = Column(Boolean, default=False)
    max_app_switches = Column(Integer, default=5)
    max_network_mb = Column(Float, default=10.0)
    
    # Automated actions
    auto_escalate_critical = Column(Boolean, default=True)
    require_manual_review = Column(Boolean, default=False)
    
    # Notification
    notify_on_violation = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<CoursePolicy {self.course_id}>"


# SQL Migration Scripts

CREATE_ANALYSES_TABLE = """
CREATE TABLE IF NOT EXISTS analyses (
    analysis_id VARCHAR(36) PRIMARY KEY UNIQUE,
    batch_id VARCHAR(36) INDEX,
    student_id VARCHAR(50) INDEX,
    course_id VARCHAR(50) INDEX,
    course_name VARCHAR(255),
    assessment_type VARCHAR(50),
    assessment_name VARCHAR(255),
    stage1_decision VARCHAR(20),
    stage1_confidence FLOAT,
    stage1_reason TEXT,
    skip_stage2 BOOLEAN DEFAULT FALSE,
    overall_assessment TEXT,
    teacher_notes TEXT,
    tokens_used INTEGER DEFAULT 0,
    model_version VARCHAR(50) DEFAULT 'gemini-1.5-flash',
    analyzed_at DATETIME DEFAULT CURRENT_TIMESTAMP INDEX,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_VIOLATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS violations (
    violation_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    analysis_id VARCHAR(36) FOREIGN KEY REFERENCES analyses(analysis_id) INDEX,
    violation_type VARCHAR(50) INDEX,
    severity VARCHAR(20) INDEX,
    location VARCHAR(255),
    description TEXT,
    why_violation TEXT,
    evidence JSON,
    reviewed BOOLEAN DEFAULT FALSE,
    reviewed_by VARCHAR(50),
    reviewed_at DATETIME
);
"""

CREATE_RECOMMENDED_ACTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS recommended_actions (
    action_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    analysis_id VARCHAR(36) FOREIGN KEY REFERENCES analyses(analysis_id) INDEX,
    action_name VARCHAR(100),
    priority VARCHAR(20),
    description TEXT,
    reason TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    assigned_to VARCHAR(50),
    completed_at DATETIME,
    completion_notes TEXT
);
"""

CREATE_AUDIT_LOGS_TABLE = """
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    analysis_id VARCHAR(36) FOREIGN KEY REFERENCES analyses(analysis_id) INDEX,
    action VARCHAR(100),
    actor VARCHAR(50),
    actor_role VARCHAR(20),
    details JSON,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP INDEX
);
"""

CREATE_STUDENT_BASELINES_TABLE = """
CREATE TABLE IF NOT EXISTS student_baselines (
    baseline_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    student_id VARCHAR(50) UNIQUE INDEX,
    course_id VARCHAR(50) INDEX,
    avg_focus_score FLOAT,
    avg_cpu_usage FLOAT,
    avg_memory_usage FLOAT,
    avg_app_switches FLOAT,
    avg_keystroke_variance FLOAT,
    avg_network_bytes FLOAT,
    stddev_focus FLOAT,
    stddev_cpu FLOAT,
    stddev_memory FLOAT,
    stddev_app_switches FLOAT,
    samples_analyzed INTEGER DEFAULT 0,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_COURSE_POLICIES_TABLE = """
CREATE TABLE IF NOT EXISTS course_policies (
    policy_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    course_id VARCHAR(50) UNIQUE INDEX,
    course_name VARCHAR(255),
    instructor VARCHAR(100),
    allow_external_resources BOOLEAN DEFAULT FALSE,
    allow_communication BOOLEAN DEFAULT FALSE,
    allow_multiple_windows BOOLEAN DEFAULT FALSE,
    max_app_switches INTEGER DEFAULT 5,
    max_network_mb FLOAT DEFAULT 10.0,
    auto_escalate_critical BOOLEAN DEFAULT TRUE,
    require_manual_review BOOLEAN DEFAULT FALSE,
    notify_on_violation BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""


def create_all_tables(database_url: str):
    """Create all tables in the database."""
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    print(f"✅ All tables created in {database_url}")
    return engine


def get_session(database_url: str):
    """Create and return a database session."""
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    return Session()


# Example usage
if __name__ == "__main__":
    # PostgreSQL
    DB_URL = "postgresql://user:password@localhost/eyecore_education"
    
    # SQLite (for testing)
    # DB_URL = "sqlite:///education_analyzer.db"
    
    engine = create_all_tables(DB_URL)
