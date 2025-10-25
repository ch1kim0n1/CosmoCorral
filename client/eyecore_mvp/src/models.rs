use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SystemMetrics {
    pub timestamp: DateTime<Utc>,
    pub cpu_usage: f32,
    pub memory_usage: f32,
    pub disk_usage: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProcessData {
    pub timestamp: DateTime<Utc>,
    pub active_process: String,
    pub active_window_title: String,
    pub process_count: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InputMetrics {
    pub timestamp: DateTime<Utc>,
    pub mouse_clicks: u32,
    pub keyboard_events: u32,
    pub idle_duration_seconds: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NetworkMetrics {
    pub timestamp: DateTime<Utc>,
    pub bytes_sent: u64,
    pub bytes_received: u64,
    pub active_connections: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FocusMetrics {
    pub timestamp: DateTime<Utc>,
    pub focus_level: f32, // 0.0 to 1.0
    pub context_switches: u32,
    pub productive_app_time: u32, // seconds
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EyeCoreData {
    pub session_id: String,
    pub timestamp: DateTime<Utc>,
    pub system_metrics: SystemMetrics,
    pub process_data: ProcessData,
    pub input_metrics: InputMetrics,
    pub network_metrics: NetworkMetrics,
    pub focus_metrics: FocusMetrics,
    // NEW: Enhanced data collection
    pub voice_data: Option<VoiceData>,
    pub camera_data: Option<CameraData>,
    pub keystroke_dynamics: Option<KeystrokeDynamics>,
    pub screen_interactions: Option<ScreenInteractions>,
    pub file_metadata: Option<FileMetadata>,
    pub system_events: Option<SystemEvents>,
    pub mouse_dynamics: Option<MouseDynamics>,
    pub network_activity_metadata: Option<NetworkActivityMetadata>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AggregatedStats {
    pub avg_cpu_usage: f32,
    pub avg_memory_usage: f32,
    pub total_idle_time: u32,
    pub total_mouse_clicks: u32,
    pub total_keyboard_events: u32,
    pub avg_focus_level: f32,
    pub session_duration: u32,
    pub data_points_collected: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CollectionStatus {
    pub is_running: bool,
    pub uptime_seconds: u64,
    pub data_points_collected: usize,
    pub last_collection: DateTime<Utc>,
}

// NEW: Voice Data Collection
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VoiceData {
    pub timestamp: DateTime<Utc>,
    pub vocal_tone_score: f32,      // 0.0 to 1.0
    pub sentiment_score: f32,        // -1.0 (negative) to 1.0 (positive)
    pub emotion_detected: String,    // "neutral", "happy", "stressed", "focused"
    pub speaking_duration_ms: u64,   // milliseconds of speech detected
    pub silence_duration_ms: u64,    // milliseconds of silence
    pub volume_level: f32,           // 0.0 to 1.0
    pub enabled: bool,               // privacy: user consent status
}

// NEW: Camera Data Collection
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CameraData {
    pub timestamp: DateTime<Utc>,
    pub facial_emotions: Vec<String>, // ["focused", "tired", "engaged"]
    pub dominant_emotion: String,     // Primary emotion detected
    pub emotion_confidence: f32,      // 0.0 to 1.0
    pub gaze_direction: String,       // "center", "away", "down", "left", "right"
    pub face_detected: bool,
    pub posture_score: f32,           // 0.0 (poor) to 1.0 (good)
    pub enabled: bool,                // privacy: user consent status
}

// NEW: Keystroke Dynamics (NO CONTENT - only patterns)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KeystrokeDynamics {
    pub timestamp: DateTime<Utc>,
    pub typing_speed_wpm: f32,           // words per minute
    pub avg_key_hold_time_ms: f32,       // average time key is held down
    pub avg_key_interval_ms: f32,        // average time between keys
    pub key_press_variance: f32,         // consistency indicator
    pub error_correction_rate: f32,      // backspace/delete frequency
    pub stress_indicator: f32,           // 0.0 (relaxed) to 1.0 (stressed)
    pub fatigue_indicator: f32,          // 0.0 (fresh) to 1.0 (tired)
    pub total_keystrokes: u32,           // count only, no content
    pub enabled: bool,                   // privacy: user consent status
}

// NEW: Screen Interaction Analysis
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScreenInteractions {
    pub timestamp: DateTime<Utc>,
    pub click_count: u32,
    pub double_click_count: u32,
    pub right_click_count: u32,
    pub scroll_events: u32,
    pub ui_element_types: Vec<String>,   // ["button", "menu", "textbox"] - abstract types only
    pub interaction_speed: f32,          // interactions per minute
    pub workflow_friction_score: f32,    // 0.0 (smooth) to 1.0 (frustrated)
    pub mouse_travel_distance_px: u64,   // total pixel distance
    pub screen_region_heatmap: Vec<(u32, u32, u32)>, // (x_zone, y_zone, count)
}

// NEW: File Metadata Analysis (NO NAMES OR CONTENT)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FileMetadata {
    pub timestamp: DateTime<Utc>,
    pub file_types_accessed: Vec<String>,    // [".rs", ".txt", ".json"]
    pub file_sizes_bytes: Vec<u64>,          // sizes only
    pub modification_events: u32,            // count of file saves
    pub file_open_events: u32,               // count of file opens
    pub file_close_events: u32,              // count of file closes
    pub work_type_inferred: String,          // "programming", "design", "writing", "browsing"
    pub project_switch_count: u32,           // working directory changes
    pub avg_file_size_bytes: u64,
    pub enabled: bool,                       // privacy: user consent status
}

// NEW: System & Power Events
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SystemEvents {
    pub timestamp: DateTime<Utc>,
    pub event_type: String,        // "lock", "unlock", "sleep", "wake", "peripheral_connect", "peripheral_disconnect"
    pub event_subtype: String,     // "usb_device", "monitor", "keyboard", "mouse"
    pub session_start: Option<DateTime<Utc>>,
    pub session_end: Option<DateTime<Utc>>,
    pub break_duration_seconds: u64,
    pub active_session_duration_seconds: u64,
    pub daily_rhythm_score: f32,   // consistency of work hours
}

// NEW: Mouse Movement Dynamics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MouseDynamics {
    pub timestamp: DateTime<Utc>,
    pub movement_speed_avg: f32,      // pixels per second
    pub movement_speed_variance: f32,  // consistency
    pub path_smoothness: f32,          // 0.0 (erratic) to 1.0 (smooth)
    pub click_pattern_regularity: f32, // timing consistency
    pub hesitation_count: u32,         // pauses during movement
    pub acceleration_avg: f32,         // speed changes
    pub fatigue_indicator: f32,        // 0.0 (fresh) to 1.0 (tired)
    pub focus_indicator: f32,          // 0.0 (distracted) to 1.0 (focused)
    pub total_distance_px: u64,        // total pixels traveled
}

// ENHANCED: Network Activity Metadata
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NetworkActivityMetadata {
    pub timestamp: DateTime<Utc>,
    pub bytes_sent: u64,
    pub bytes_received: u64,
    pub active_connections: usize,
    pub traffic_type: String,          // "video_conference", "streaming", "download", "browsing", "gaming"
    pub activity_context: String,      // "meeting", "entertainment", "research", "file_transfer"
    pub bandwidth_usage_mbps: f32,     // megabits per second
    pub latency_avg_ms: f32,           // average ping
    pub packet_loss_rate: f32,         // 0.0 to 1.0
    pub connection_stability: f32,     // 0.0 (unstable) to 1.0 (stable)
}
