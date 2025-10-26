/**
 * SHARED DATA TYPES
 * Used across: Client (Rust), Server (Python), Dashboard (TypeScript)
 * 
 * Keep in sync: This file is the source of truth for all data structures
 */

// ============================================================================
// EVENT TYPES (Raw Collection)
// ============================================================================

export type Modality = 
  | "system" 
  | "process" 
  | "input" 
  | "voice" 
  | "network" 
  | "focus";

export interface RawEvent {
  session_id: string;
  timestamp: string;  // ISO8601
  device_id: string;
  student_id?: string;
  modality: Modality;
  data: Record<string, any>;
}

// ============================================================================
// ACTIVITY PACKAGE (After Normalization)
// ============================================================================

export interface SystemMetrics {
  cpu_usage: number;        // 0-100 %
  memory_usage: number;     // 0-100 %
  disk_io_rate: number;     // MB/s
  timestamp: string;
}

export interface ProcessData {
  active_process: string;   // e.g., "chrome.exe"
  active_pid: number;
  window_title: string;
  app_switches: number;     // count in interval
  running_process_count: number;
  timestamp: string;
}

export interface InputDynamics {
  keystroke_rate: number;   // keys/sec
  keystroke_rhythm_variance: number;  // 0-1 (0=very consistent, 1=erratic)
  keystroke_errors: number;  // backspaces/corrections per minute
  mouse_velocity: number;    // pixels/sec
  mouse_acceleration: number;
  mouse_idle_duration: number;  // seconds since last movement
  clicks_per_minute: number;
  timestamp: string;
}

export interface NetworkActivity {
  bytes_sent: number;
  bytes_received: number;
  connections_active: number;
  data_transfer_rate: number;  // MB/s
  unusual_protocols: string[];  // e.g., ["TOR", "VPN", "P2P"]
  dns_queries: number;
  timestamp: string;
}

export interface FocusMetrics {
  focus_score: number;        // 0-1 (1 = completely focused)
  attention_drops: number;    // count of sudden drops
  context_switches: number;   // app switches in interval
  time_since_interaction: number;  // seconds (idle time)
  productive_app_time: number; // seconds on work-related apps
  timestamp: string;
}

export interface VoiceData {
  enabled: boolean;
  sentiment_score: number;     // -1 (very negative) to +1 (very positive)
  emotion_detected: string;    // "frustrated" | "confident" | "neutral" | etc
  energy_level: number;        // 0-1
  speech_rate: number;         // words/min
  speech_clarity: number;      // 0-1
  detected_languages: string[];
  timestamp: string;
}

export interface ActivityPackage {
  // Metadata
  session_id: string;
  timestamp: string;  // ISO8601
  device_id: string;
  student_id: string;
  package_id: string;  // Unique per package
  
  // Aggregation metadata
  aggregation_window: "raw" | "30s" | "60s" | "5m";
  
  // Modalities
  system_metrics: SystemMetrics;
  process_data: ProcessData;
  input_dynamics: InputDynamics;
  network_activity: NetworkActivity;
  focus_metrics: FocusMetrics;
  voice_data?: VoiceData;
  
  // Client version for compatibility
  client_version: string;
}

// ============================================================================
// ANOMALY DETECTION
// ============================================================================

export interface AnomalyScore {
  signal_name: string;
  modality: Modality;
  raw_value: number;
  baseline_expected: number;
  baseline_std_dev: number;
  z_score: number;               // deviation in standard deviations
  percentile_anomaly: number;    // 0-1: how anomalous (0=normal, 1=extremely anomalous)
  threshold_breached: boolean;
  breach_magnitude: number;      // % over threshold
  reason: string;
  severity: "low" | "medium" | "high" | "critical";
  timestamp: string;
}

export interface CompositeAnomalyScore {
  overall_score: number;         // 0-1 weighted average
  signal_scores: AnomalyScore[];
  dominant_anomalies: string[];  // Top 3-5 anomalies
  cross_signal_patterns: string[];  // e.g., ["high_network_low_focus", "rapid_app_switches"]
  timestamp: string;
}

// ============================================================================
// RULES ENGINE
// ============================================================================

export interface RuleTriggered {
  rule_id: string;
  rule_name: string;
  description: string;
  severity: "warning" | "alert" | "critical";
  evidence: string[];
  triggered_at: string;
}

export interface RulesEvaluationResult {
  triggered_rules: RuleTriggered[];
  should_escalate_to_gemini: boolean;
  escalation_reason?: string;
}

// ============================================================================
// GEMINI API ANALYSIS
// ============================================================================

export type SuspectedActivity = 
  | "unauthorized_resource_access"
  | "impersonation"
  | "tab_switching_excessive"
  | "copy_paste_detected"
  | "network_exfiltration_attempt"
  | "stress_response"
  | "technical_issue"
  | "legitimate_multitasking"
  | "none";

export interface GeminiAnalysis {
  suspected_activity: SuspectedActivity;
  confidence: number;            // 0-1
  why_suspected: string;         // 1-2 sentence explanation
  evidence: string[];            // List of specific pieces of evidence
  recommendation: string;        // Action professor should take
  alternative_explanations: string[];  // What else could explain this
  tokens_used: number;           // For cost tracking
  model_version: string;
  analyzed_at: string;
}

// ============================================================================
// FLAGGED REPORT
// ============================================================================

export interface FlaggedReport {
  // Metadata
  id: string;
  package_id: string;
  session_id: string;
  timestamp: string;
  device_id: string;
  student_id: string;
  
  // Anomalies
  anomalies: AnomalyScore[];
  composite_anomaly_score: CompositeAnomalyScore;
  
  // Rules
  triggered_rules: RuleTriggered[];
  
  // Gemini Analysis
  gemini_analysis: GeminiAnalysis;
  
  // Status & Actions
  status: "new" | "acknowledged" | "under_review" | "resolved" | "false_positive";
  professor_notes?: string;
  professor_id?: string;
  resolution?: string;
  
  // Audit
  created_at: string;
  updated_at: string;
  reviewed_at?: string;
}

// ============================================================================
// STUDENT SESSION
// ============================================================================

export interface StudentSession {
  session_id: string;
  student_id: string;
  device_id: string;
  exam_id: string;
  started_at: string;
  ended_at?: string;
  
  // Session statistics
  total_packages_received: number;
  flagged_count: number;
  clean_count: number;
  anomaly_score_avg: number;
  anomaly_score_max: number;
  
  // Flags
  is_active: boolean;
  is_flagged: boolean;
}

// ============================================================================
// PROFESSOR DASHBOARD MODELS
// ============================================================================

export interface ExamMonitoring {
  exam_id: string;
  exam_name: string;
  professor_id: string;
  started_at: string;
  ended_at?: string;
  total_students: number;
  
  student_sessions: StudentSession[];
  flagged_reports: FlaggedReport[];
  
  stats: {
    total_flags: number;
    critical_flags: number;
    average_anomaly_score: number;
    students_flagged: number;
    suspicious_activity_types: Map<SuspectedActivity, number>;
  };
}

export interface ProfessorAction {
  id: string;
  report_id: string;
  professor_id: string;
  action_type: "flag_as_false_positive" | "request_verification" | "terminate_session" | "add_notes";
  details: string;
  timestamp: string;
}

// ============================================================================
// DATABASE MODELS
// ============================================================================

export interface ActivityPackageRecord {
  id: string;
  session_id: string;
  device_id: string;
  student_id: string;
  timestamp: string;
  package_data: ActivityPackage;
  created_at: string;
}

export interface FlaggedReportRecord {
  id: string;
  package_id: string;
  session_id: string;
  student_id: string;
  professor_id?: string;
  
  anomalies: AnomalyScore[];
  composite_score: number;
  triggered_rules: RuleTriggered[];
  
  gemini_analysis: GeminiAnalysis;
  
  status: string;
  notes?: string;
  
  created_at: string;
  updated_at: string;
  reviewed_at?: string;
}

export interface AuditLogRecord {
  id: string;
  event_type: string;
  report_id?: string;
  actor_id: string;           // Professor ID
  actor_role: "professor" | "admin" | "system";
  action: string;
  details: Record<string, any>;
  timestamp: string;
}

// ============================================================================
// WEBSOCKET MESSAGES
// ============================================================================

export interface WSMessage<T = any> {
  type: string;
  data: T;
  timestamp: string;
}

// Client → Server
export interface AuthenticateMessage {
  method: "Authenticate";
  data: {
    access_code: string;
  };
}

export interface PackageMessage {
  method: "Package";
  data: {
    token: string;
    student_id: string;
    data: ActivityPackage;
  };
}

export type ClientMessage = AuthenticateMessage | PackageMessage;

// Server → Dashboard
export interface FlaggedReportAlertMessage {
  type: "FlaggedReportAlert";
  data: FlaggedReport;
}

export interface SessionUpdateMessage {
  type: "SessionUpdate";
  data: {
    session_id: string;
    student_id: string;
    device_id: string;
    status: "active" | "inactive" | "ended";
    anomaly_score: number;
    timestamp: string;
  };
}

export interface StatsUpdateMessage {
  type: "StatsUpdate";
  data: {
    exam_id: string;
    total_flags: number;
    critical_flags: number;
    average_anomaly_score: number;
    timestamp: string;
  };
}

export type DashboardMessage = FlaggedReportAlertMessage | SessionUpdateMessage | StatsUpdateMessage;

// ============================================================================
// CONFIGURATION
// ============================================================================

export interface AnomalyThresholds {
  cpu_usage: number;
  memory_usage: number;
  network_bytes_per_30s: number;
  keystroke_rhythm_variance: number;
  focus_score_min: number;
  app_switches_per_minute: number;
}

export interface RuleConfig {
  enabled: boolean;
  severity: "warning" | "alert" | "critical";
  threshold: number;
  escalate_to_gemini: boolean;
}

export interface SystemConfig {
  anomaly_thresholds: AnomalyThresholds;
  rules: Record<string, RuleConfig>;
  gemini_api_key: string;
  database_url: string;
  server_port: number;
  aggregation_windows: number[];  // [30, 60, 300] for 30s, 60s, 5m
}
