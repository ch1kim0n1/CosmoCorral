use crate::models::*;
use chrono::Utc;
use log::debug;
use serde_json::json;
use uuid::Uuid;

pub struct FlagDetector {
    // Thresholds for anomaly detection
    cpu_threshold: f32,
    memory_threshold: f32,
    idle_threshold: u32,
    focus_threshold: f32,
    stress_threshold: f32,
    fatigue_threshold: f32,
}

impl FlagDetector {
    pub fn new() -> Self {
        FlagDetector {
            cpu_threshold: 90.0,       // CPU usage > 90%
            memory_threshold: 85.0,    // Memory usage > 85%
            idle_threshold: 300,       // Idle > 5 minutes
            focus_threshold: 0.3,      // Focus < 0.3
            stress_threshold: 0.7,     // Stress > 0.7
            fatigue_threshold: 0.8,    // Fatigue > 0.8
        }
    }
    
    /// Analyze EyeCore data and detect anomalies
    pub async fn analyze_data(&self, data: &EyeCoreData) -> Result<Vec<Flag>, String> {
        let mut flags = Vec::new();
        
        debug!("Analyzing data for session: {}", data.session_id);
        
        // Check system metrics
        flags.extend(self.check_system_metrics(&data.system_metrics, &data.session_id));
        
        // Check input patterns
        flags.extend(self.check_input_metrics(&data.input_metrics, &data.session_id));
        
        // Check focus metrics
        flags.extend(self.check_focus_metrics(&data.focus_metrics, &data.session_id));
        
        // Check keystroke dynamics if available
        if let Some(ref keystroke) = data.keystroke_dynamics {
            flags.extend(self.check_keystroke_dynamics(keystroke, &data.session_id));
        }
        
        // Check mouse dynamics if available
        if let Some(ref mouse) = data.mouse_dynamics {
            flags.extend(self.check_mouse_dynamics(mouse, &data.session_id));
        }
        
        // Check voice data if available
        if let Some(ref voice) = data.voice_data {
            flags.extend(self.check_voice_data(voice, &data.session_id));
        }
        
        // Check camera data if available
        if let Some(ref camera) = data.camera_data {
            flags.extend(self.check_camera_data(camera, &data.session_id));
        }
        
        // Check network activity if available
        if let Some(ref network) = data.network_activity_metadata {
            flags.extend(self.check_network_activity(network, &data.session_id));
        }
        
        // Check screen interactions if available
        if let Some(ref screen) = data.screen_interactions {
            flags.extend(self.check_screen_interactions(screen, &data.session_id));
        }
        
        Ok(flags)
    }
    
    /// Check system metrics for anomalies
    fn check_system_metrics(&self, metrics: &SystemMetrics, session_id: &str) -> Vec<Flag> {
        let mut flags = Vec::new();
        
        // High CPU usage
        if metrics.cpu_usage > self.cpu_threshold {
            flags.push(Flag {
                id: Uuid::new_v4().to_string(),
                timestamp: Utc::now(),
                session_id: session_id.to_string(),
                flag_type: FlagType::PerformanceIssue,
                severity: if metrics.cpu_usage > 95.0 { Severity::Critical } else { Severity::High },
                title: "High CPU Usage".to_string(),
                description: format!("CPU usage at {:.1}% exceeds threshold of {:.1}%", 
                    metrics.cpu_usage, self.cpu_threshold),
                data_source: "system_metrics".to_string(),
                metrics: json!({
                    "cpu_usage": metrics.cpu_usage,
                    "threshold": self.cpu_threshold,
                }),
                confidence: 0.95,
            });
        }
        
        // High memory usage
        if metrics.memory_usage > self.memory_threshold {
            flags.push(Flag {
                id: Uuid::new_v4().to_string(),
                timestamp: Utc::now(),
                session_id: session_id.to_string(),
                flag_type: FlagType::PerformanceIssue,
                severity: if metrics.memory_usage > 95.0 { Severity::Critical } else { Severity::High },
                title: "High Memory Usage".to_string(),
                description: format!("Memory usage at {:.1}% exceeds threshold of {:.1}%", 
                    metrics.memory_usage, self.memory_threshold),
                data_source: "system_metrics".to_string(),
                metrics: json!({
                    "memory_usage": metrics.memory_usage,
                    "threshold": self.memory_threshold,
                }),
                confidence: 0.95,
            });
        }
        
        flags
    }
    
    /// Check input metrics for anomalies
    fn check_input_metrics(&self, metrics: &InputMetrics, session_id: &str) -> Vec<Flag> {
        let mut flags = Vec::new();
        
        // Prolonged idle time
        if metrics.idle_duration_seconds > self.idle_threshold {
            flags.push(Flag {
                id: Uuid::new_v4().to_string(),
                timestamp: Utc::now(),
                session_id: session_id.to_string(),
                flag_type: FlagType::ProductivityAlert,
                severity: Severity::Low,
                title: "Prolonged Idle Time".to_string(),
                description: format!("User idle for {} seconds (>{} seconds)", 
                    metrics.idle_duration_seconds, self.idle_threshold),
                data_source: "input_metrics".to_string(),
                metrics: json!({
                    "idle_duration_seconds": metrics.idle_duration_seconds,
                    "threshold": self.idle_threshold,
                }),
                confidence: 0.85,
            });
        }
        
        // Unusual activity pattern - no input at all
        if metrics.mouse_clicks == 0 && metrics.keyboard_events == 0 && metrics.idle_duration_seconds < 10 {
            flags.push(Flag {
                id: Uuid::new_v4().to_string(),
                timestamp: Utc::now(),
                session_id: session_id.to_string(),
                flag_type: FlagType::BehaviorAnomaly,
                severity: Severity::Low,
                title: "No User Input Detected".to_string(),
                description: "System active but no mouse/keyboard activity detected".to_string(),
                data_source: "input_metrics".to_string(),
                metrics: json!({
                    "mouse_clicks": metrics.mouse_clicks,
                    "keyboard_events": metrics.keyboard_events,
                    "idle_duration_seconds": metrics.idle_duration_seconds,
                }),
                confidence: 0.7,
            });
        }
        
        flags
    }
    
    /// Check focus metrics for anomalies
    fn check_focus_metrics(&self, metrics: &FocusMetrics, session_id: &str) -> Vec<Flag> {
        let mut flags = Vec::new();
        
        // Low focus level
        if metrics.focus_level < self.focus_threshold {
            flags.push(Flag {
                id: Uuid::new_v4().to_string(),
                timestamp: Utc::now(),
                session_id: session_id.to_string(),
                flag_type: FlagType::ProductivityAlert,
                severity: Severity::Medium,
                title: "Low Focus Level".to_string(),
                description: format!("Focus level at {:.2} is below threshold of {:.2}", 
                    metrics.focus_level, self.focus_threshold),
                data_source: "focus_metrics".to_string(),
                metrics: json!({
                    "focus_level": metrics.focus_level,
                    "context_switches": metrics.context_switches,
                    "threshold": self.focus_threshold,
                }),
                confidence: 0.8,
            });
        }
        
        // Excessive context switching
        if metrics.context_switches > 50 {
            flags.push(Flag {
                id: Uuid::new_v4().to_string(),
                timestamp: Utc::now(),
                session_id: session_id.to_string(),
                flag_type: FlagType::ProductivityAlert,
                severity: Severity::Medium,
                title: "Excessive Context Switching".to_string(),
                description: format!("Detected {} context switches, indicating possible distraction", 
                    metrics.context_switches),
                data_source: "focus_metrics".to_string(),
                metrics: json!({
                    "context_switches": metrics.context_switches,
                }),
                confidence: 0.75,
            });
        }
        
        flags
    }
    
    /// Check keystroke dynamics for stress/fatigue
    fn check_keystroke_dynamics(&self, keystroke: &KeystrokeDynamics, session_id: &str) -> Vec<Flag> {
        let mut flags = Vec::new();
        
        // High stress indicator
        if keystroke.stress_indicator > self.stress_threshold {
            flags.push(Flag {
                id: Uuid::new_v4().to_string(),
                timestamp: Utc::now(),
                session_id: session_id.to_string(),
                flag_type: FlagType::HealthConcern,
                severity: Severity::Medium,
                title: "High Stress Detected".to_string(),
                description: format!("Keystroke patterns indicate stress level of {:.2}", 
                    keystroke.stress_indicator),
                data_source: "keystroke_dynamics".to_string(),
                metrics: json!({
                    "stress_indicator": keystroke.stress_indicator,
                    "typing_speed_wpm": keystroke.typing_speed_wpm,
                    "error_correction_rate": keystroke.error_correction_rate,
                }),
                confidence: 0.75,
            });
        }
        
        // High fatigue indicator
        if keystroke.fatigue_indicator > self.fatigue_threshold {
            flags.push(Flag {
                id: Uuid::new_v4().to_string(),
                timestamp: Utc::now(),
                session_id: session_id.to_string(),
                flag_type: FlagType::HealthConcern,
                severity: Severity::Medium,
                title: "Fatigue Detected".to_string(),
                description: format!("Keystroke patterns indicate fatigue level of {:.2}", 
                    keystroke.fatigue_indicator),
                data_source: "keystroke_dynamics".to_string(),
                metrics: json!({
                    "fatigue_indicator": keystroke.fatigue_indicator,
                    "typing_speed_wpm": keystroke.typing_speed_wpm,
                    "key_press_variance": keystroke.key_press_variance,
                }),
                confidence: 0.75,
            });
        }
        
        // High error rate
        if keystroke.error_correction_rate > 0.15 {
            flags.push(Flag {
                id: Uuid::new_v4().to_string(),
                timestamp: Utc::now(),
                session_id: session_id.to_string(),
                flag_type: FlagType::HealthConcern,
                severity: Severity::Low,
                title: "High Typing Error Rate".to_string(),
                description: format!("Error correction rate at {:.1}% suggests possible fatigue or distraction", 
                    keystroke.error_correction_rate * 100.0),
                data_source: "keystroke_dynamics".to_string(),
                metrics: json!({
                    "error_correction_rate": keystroke.error_correction_rate,
                }),
                confidence: 0.7,
            });
        }
        
        flags
    }
    
    /// Check mouse dynamics for anomalies
    fn check_mouse_dynamics(&self, mouse: &MouseDynamics, session_id: &str) -> Vec<Flag> {
        let mut flags = Vec::new();
        
        // High fatigue from mouse patterns
        if mouse.fatigue_indicator > self.fatigue_threshold {
            flags.push(Flag {
                id: Uuid::new_v4().to_string(),
                timestamp: Utc::now(),
                session_id: session_id.to_string(),
                flag_type: FlagType::HealthConcern,
                severity: Severity::Medium,
                title: "Mouse Movement Fatigue".to_string(),
                description: format!("Mouse patterns indicate fatigue level of {:.2}", 
                    mouse.fatigue_indicator),
                data_source: "mouse_dynamics".to_string(),
                metrics: json!({
                    "fatigue_indicator": mouse.fatigue_indicator,
                    "path_smoothness": mouse.path_smoothness,
                    "hesitation_count": mouse.hesitation_count,
                }),
                confidence: 0.7,
            });
        }
        
        // Erratic mouse movement
        if mouse.path_smoothness < 0.3 && mouse.hesitation_count > 15 {
            flags.push(Flag {
                id: Uuid::new_v4().to_string(),
                timestamp: Utc::now(),
                session_id: session_id.to_string(),
                flag_type: FlagType::BehaviorAnomaly,
                severity: Severity::Low,
                title: "Erratic Mouse Movement".to_string(),
                description: "Mouse movement patterns are irregular with many hesitations".to_string(),
                data_source: "mouse_dynamics".to_string(),
                metrics: json!({
                    "path_smoothness": mouse.path_smoothness,
                    "hesitation_count": mouse.hesitation_count,
                }),
                confidence: 0.65,
            });
        }
        
        flags
    }
    
    /// Check voice data for emotional anomalies
    fn check_voice_data(&self, voice: &VoiceData, session_id: &str) -> Vec<Flag> {
        let mut flags = Vec::new();
        
        // Negative sentiment
        if voice.sentiment_score < -0.5 {
            flags.push(Flag {
                id: Uuid::new_v4().to_string(),
                timestamp: Utc::now(),
                session_id: session_id.to_string(),
                flag_type: FlagType::HealthConcern,
                severity: Severity::Medium,
                title: "Negative Emotional State".to_string(),
                description: format!("Voice sentiment at {:.2} indicates negative emotional state", 
                    voice.sentiment_score),
                data_source: "voice_data".to_string(),
                metrics: json!({
                    "sentiment_score": voice.sentiment_score,
                    "emotion_detected": voice.emotion_detected,
                    "vocal_tone_score": voice.vocal_tone_score,
                }),
                confidence: 0.75,
            });
        }
        
        // Stress-related emotions
        if voice.emotion_detected == "stressed" || voice.emotion_detected == "frustrated" {
            flags.push(Flag {
                id: Uuid::new_v4().to_string(),
                timestamp: Utc::now(),
                session_id: session_id.to_string(),
                flag_type: FlagType::HealthConcern,
                severity: Severity::Medium,
                title: "Stress Detected in Voice".to_string(),
                description: format!("Voice analysis detected emotion: {}", voice.emotion_detected),
                data_source: "voice_data".to_string(),
                metrics: json!({
                    "emotion_detected": voice.emotion_detected,
                    "vocal_tone_score": voice.vocal_tone_score,
                }),
                confidence: 0.8,
            });
        }
        
        flags
    }
    
    /// Check camera data for emotional/posture anomalies
    fn check_camera_data(&self, camera: &CameraData, session_id: &str) -> Vec<Flag> {
        let mut flags = Vec::new();
        
        // Poor posture
        if camera.posture_score < 0.4 {
            flags.push(Flag {
                id: Uuid::new_v4().to_string(),
                timestamp: Utc::now(),
                session_id: session_id.to_string(),
                flag_type: FlagType::HealthConcern,
                severity: Severity::Low,
                title: "Poor Posture Detected".to_string(),
                description: format!("Posture score of {:.2} suggests poor ergonomics", 
                    camera.posture_score),
                data_source: "camera_data".to_string(),
                metrics: json!({
                    "posture_score": camera.posture_score,
                }),
                confidence: 0.7,
            });
        }
        
        // Gaze away from screen
        if camera.gaze_direction == "away" {
            flags.push(Flag {
                id: Uuid::new_v4().to_string(),
                timestamp: Utc::now(),
                session_id: session_id.to_string(),
                flag_type: FlagType::ProductivityAlert,
                severity: Severity::Low,
                title: "User Not Looking at Screen".to_string(),
                description: "Camera detected user gaze is away from screen".to_string(),
                data_source: "camera_data".to_string(),
                metrics: json!({
                    "gaze_direction": camera.gaze_direction,
                }),
                confidence: 0.75,
            });
        }
        
        flags
    }
    
    /// Check network activity for suspicious patterns
    fn check_network_activity(&self, network: &NetworkActivityMetadata, session_id: &str) -> Vec<Flag> {
        let mut flags = Vec::new();
        
        // Excessive bandwidth usage
        if network.bandwidth_usage_mbps > 500.0 {
            flags.push(Flag {
                id: Uuid::new_v4().to_string(),
                timestamp: Utc::now(),
                session_id: session_id.to_string(),
                flag_type: FlagType::SystemAnomaly,
                severity: Severity::Medium,
                title: "High Bandwidth Usage".to_string(),
                description: format!("Bandwidth usage at {:.1} Mbps is unusually high", 
                    network.bandwidth_usage_mbps),
                data_source: "network_activity_metadata".to_string(),
                metrics: json!({
                    "bandwidth_usage_mbps": network.bandwidth_usage_mbps,
                    "traffic_type": network.traffic_type,
                }),
                confidence: 0.8,
            });
        }
        
        // High packet loss
        if network.packet_loss_rate > 0.05 {
            flags.push(Flag {
                id: Uuid::new_v4().to_string(),
                timestamp: Utc::now(),
                session_id: session_id.to_string(),
                flag_type: FlagType::PerformanceIssue,
                severity: Severity::Medium,
                title: "High Network Packet Loss".to_string(),
                description: format!("Packet loss rate at {:.1}% indicates network issues", 
                    network.packet_loss_rate * 100.0),
                data_source: "network_activity_metadata".to_string(),
                metrics: json!({
                    "packet_loss_rate": network.packet_loss_rate,
                    "connection_stability": network.connection_stability,
                }),
                confidence: 0.85,
            });
        }
        
        flags
    }
    
    /// Check screen interactions for workflow friction
    fn check_screen_interactions(&self, screen: &ScreenInteractions, session_id: &str) -> Vec<Flag> {
        let mut flags = Vec::new();
        
        // High workflow friction
        if screen.workflow_friction_score > 0.7 {
            flags.push(Flag {
                id: Uuid::new_v4().to_string(),
                timestamp: Utc::now(),
                session_id: session_id.to_string(),
                flag_type: FlagType::ProductivityAlert,
                severity: Severity::Medium,
                title: "High Workflow Friction".to_string(),
                description: format!("Workflow friction score of {:.2} indicates UI/UX issues", 
                    screen.workflow_friction_score),
                data_source: "screen_interactions".to_string(),
                metrics: json!({
                    "workflow_friction_score": screen.workflow_friction_score,
                    "click_count": screen.click_count,
                }),
                confidence: 0.7,
            });
        }
        
        flags
    }
}
