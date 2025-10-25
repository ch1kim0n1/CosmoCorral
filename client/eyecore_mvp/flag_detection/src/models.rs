use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};

/// Wrapper for EyeCore data files
#[derive(Debug, Clone, Deserialize)]
pub struct EyeCoreDataFile {
    pub metadata: Metadata,
    pub data: EyeCoreData,
}

#[derive(Debug, Clone, Deserialize)]
pub struct Metadata {
    pub session_id: String,
    pub timestamp: String,
    pub data_types_available: DataTypesAvailable,
    pub saved_at: String,
}

#[derive(Debug, Clone, Deserialize)]
pub struct DataTypesAvailable {
    pub system_metrics: bool,
    pub process_data: bool,
    pub input_metrics: bool,
    pub network_metrics: bool,
    pub focus_metrics: bool,
    pub voice_data: bool,
    pub camera_data: bool,
    pub keystroke_dynamics: bool,
    pub screen_interactions: bool,
    pub file_metadata: bool,
    pub system_events: bool,
    pub mouse_dynamics: bool,
    pub network_activity_metadata: bool,
}

/// Main EyeCore data structure (simplified for flag detection)
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct EyeCoreData {
    pub session_id: String,
    pub timestamp: DateTime<Utc>,
    pub system_metrics: SystemMetrics,
    pub process_data: ProcessData,
    pub input_metrics: InputMetrics,
    pub network_metrics: NetworkMetrics,
    pub focus_metrics: FocusMetrics,
    
    // Optional enhanced data
    pub voice_data: Option<VoiceData>,
    pub camera_data: Option<CameraData>,
    pub keystroke_dynamics: Option<KeystrokeDynamics>,
    pub screen_interactions: Option<ScreenInteractions>,
    pub file_metadata: Option<FileMetadata>,
    pub system_events: Option<SystemEvents>,
    pub mouse_dynamics: Option<MouseDynamics>,
    pub network_activity_metadata: Option<NetworkActivityMetadata>,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct SystemMetrics {
    pub timestamp: DateTime<Utc>,
    pub cpu_usage: f32,
    pub memory_usage: f32,
    pub disk_usage: f32,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct ProcessData {
    pub timestamp: DateTime<Utc>,
    pub active_process: String,
    pub active_window_title: String,
    pub process_count: usize,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct InputMetrics {
    pub timestamp: DateTime<Utc>,
    pub mouse_clicks: u32,
    pub keyboard_events: u32,
    pub idle_duration_seconds: u32,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct NetworkMetrics {
    pub timestamp: DateTime<Utc>,
    pub bytes_sent: u64,
    pub bytes_received: u64,
    pub active_connections: usize,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct FocusMetrics {
    pub timestamp: DateTime<Utc>,
    pub focus_level: f32,
    pub context_switches: u32,
    pub productive_app_time: u32,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct VoiceData {
    pub timestamp: DateTime<Utc>,
    pub vocal_tone_score: f32,
    pub sentiment_score: f32,
    pub emotion_detected: String,
    pub speaking_duration_ms: u64,
    pub silence_duration_ms: u64,
    pub volume_level: f32,
    pub enabled: bool,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct CameraData {
    pub timestamp: DateTime<Utc>,
    pub facial_emotions: Vec<String>,
    pub dominant_emotion: String,
    pub emotion_confidence: f32,
    pub gaze_direction: String,
    pub face_detected: bool,
    pub posture_score: f32,
    pub enabled: bool,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct KeystrokeDynamics {
    pub timestamp: DateTime<Utc>,
    pub typing_speed_wpm: f32,
    pub avg_key_hold_time_ms: f32,
    pub avg_key_interval_ms: f32,
    pub key_press_variance: f32,
    pub error_correction_rate: f32,
    pub stress_indicator: f32,
    pub fatigue_indicator: f32,
    pub total_keystrokes: u32,
    pub enabled: bool,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct ScreenInteractions {
    pub timestamp: DateTime<Utc>,
    pub click_count: u32,
    pub double_click_count: u32,
    pub right_click_count: u32,
    pub scroll_events: u32,
    pub ui_element_types: Vec<String>,
    pub interaction_speed: f32,
    pub workflow_friction_score: f32,
    pub mouse_travel_distance_px: u64,
    pub screen_region_heatmap: Vec<(u32, u32, u32)>,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct FileMetadata {
    pub timestamp: DateTime<Utc>,
    pub file_types_accessed: Vec<String>,
    pub file_sizes_bytes: Vec<u64>,
    pub modification_events: u32,
    pub file_open_events: u32,
    pub file_close_events: u32,
    pub work_type_inferred: String,
    pub project_switch_count: u32,
    pub avg_file_size_bytes: u64,
    pub enabled: bool,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct SystemEvents {
    pub timestamp: DateTime<Utc>,
    pub event_type: String,
    pub event_subtype: String,
    pub session_start: Option<DateTime<Utc>>,
    pub session_end: Option<DateTime<Utc>>,
    pub break_duration_seconds: u64,
    pub active_session_duration_seconds: u64,
    pub daily_rhythm_score: f32,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct MouseDynamics {
    pub timestamp: DateTime<Utc>,
    pub movement_speed_avg: f32,
    pub movement_speed_variance: f32,
    pub path_smoothness: f32,
    pub click_pattern_regularity: f32,
    pub hesitation_count: u32,
    pub acceleration_avg: f32,
    pub fatigue_indicator: f32,
    pub focus_indicator: f32,
    pub total_distance_px: u64,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct NetworkActivityMetadata {
    pub timestamp: DateTime<Utc>,
    pub bytes_sent: u64,
    pub bytes_received: u64,
    pub active_connections: usize,
    pub traffic_type: String,
    pub activity_context: String,
    pub bandwidth_usage_mbps: f32,
    pub latency_avg_ms: f32,
    pub packet_loss_rate: f32,
    pub connection_stability: f32,
}

/// Flag types for detected anomalies
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type")]
pub enum FlagType {
    SystemAnomaly,
    BehaviorAnomaly,
    PerformanceIssue,
    SecurityConcern,
    HealthConcern,
    ProductivityAlert,
}

/// A flag represents a detected anomaly in the data
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Flag {
    pub id: String,
    pub timestamp: DateTime<Utc>,
    pub session_id: String,
    pub flag_type: FlagType,
    pub severity: Severity,
    pub title: String,
    pub description: String,
    pub data_source: String,
    pub metrics: serde_json::Value,
    pub confidence: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Severity {
    Low,
    Medium,
    High,
    Critical,
}
