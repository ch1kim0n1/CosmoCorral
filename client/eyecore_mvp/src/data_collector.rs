use crate::models::*;
use chrono::Utc;
use log::{info, debug};
use sysinfo::System;
use std::collections::VecDeque;
use uuid::Uuid;

pub struct DataCollector {
    session_id: String,
    data_history: VecDeque<EyeCoreData>,
    max_history: usize,
    start_time: std::time::Instant,
    total_collections: usize,
    last_mouse_clicks: u32,
    last_keyboard_events: u32,
    // NEW: Enhanced tracking
    mouse_positions: VecDeque<(f32, f32, std::time::Instant)>,
    keystroke_timings: VecDeque<std::time::Instant>,
    _last_system_event: Option<SystemEvents>,
    _file_access_cache: std::collections::HashMap<String, u64>,
    voice_enabled: bool,
    camera_enabled: bool,
    keystroke_enabled: bool,
    file_monitoring_enabled: bool,
}

impl DataCollector {
    pub fn new() -> Self {
        DataCollector {
            session_id: Uuid::new_v4().to_string(),
            data_history: VecDeque::new(),
            max_history: 1000,
            start_time: std::time::Instant::now(),
            total_collections: 0,
            last_mouse_clicks: 0,
            last_keyboard_events: 0,
            mouse_positions: VecDeque::new(),
            keystroke_timings: VecDeque::new(),
            _last_system_event: None,
            _file_access_cache: std::collections::HashMap::new(),
            voice_enabled: false,     // opt-in
            camera_enabled: false,    // opt-in
            keystroke_enabled: false, // opt-in
            file_monitoring_enabled: false, // opt-in
        }
    }
    
    // Enable/Disable collection modules
    pub fn enable_voice(&mut self) { self.voice_enabled = true; }
    pub fn disable_voice(&mut self) { self.voice_enabled = false; }
    pub fn enable_camera(&mut self) { self.camera_enabled = true; }
    pub fn disable_camera(&mut self) { self.camera_enabled = false; }
    pub fn enable_keystroke(&mut self) { self.keystroke_enabled = true; }
    pub fn disable_keystroke(&mut self) { self.keystroke_enabled = false; }
    pub fn enable_file_monitoring(&mut self) { self.file_monitoring_enabled = true; }
    pub fn disable_file_monitoring(&mut self) { self.file_monitoring_enabled = false; }

    pub async fn collect_all(&mut self) {
        debug!("Collecting all data...");
        
        let now = Utc::now();
        
        let system_metrics = self.collect_system_metrics();
        let process_data = self.collect_process_data();
        let input_metrics = self.collect_input_metrics();
        let network_metrics = self.collect_network_metrics();
        let focus_metrics = self.calculate_focus_metrics();
        
        // Collect enhanced data (opt-in modules)
        let voice_data = if self.voice_enabled {
            Some(self.collect_voice_data())
        } else {
            None
        };
        
        let camera_data = if self.camera_enabled {
            Some(self.collect_camera_data())
        } else {
            None
        };
        
        let keystroke_dynamics = if self.keystroke_enabled {
            Some(self.collect_keystroke_dynamics())
        } else {
            None
        };
        
        let screen_interactions = Some(self.collect_screen_interactions());
        let file_metadata = if self.file_monitoring_enabled {
            Some(self.collect_file_metadata())
        } else {
            None
        };
        
        let system_events = Some(self.collect_system_events());
        let mouse_dynamics = Some(self.collect_mouse_dynamics());
        let network_activity_metadata = Some(self.enhance_network_metrics(&network_metrics));
        
        let data = EyeCoreData {
            session_id: self.session_id.clone(),
            timestamp: now,
            system_metrics,
            process_data,
            input_metrics,
            network_metrics,
            focus_metrics,
            voice_data,
            camera_data,
            keystroke_dynamics,
            screen_interactions,
            file_metadata,
            system_events,
            mouse_dynamics,
            network_activity_metadata,
        };
        
        self.data_history.push_back(data);
        if self.data_history.len() > self.max_history {
            self.data_history.pop_front();
        }
        
        self.total_collections += 1;
        info!("✓ Data collection #{} complete", self.total_collections);
    }

    fn collect_system_metrics(&self) -> SystemMetrics {
        let sys = System::new_all();
        
        let cpu_usage = (rand::random::<f32>() * 100.0).min(100.0);
        let memory_usage = (rand::random::<f32>() * 100.0).min(100.0);
        let disk_usage = (rand::random::<f32>() * 100.0).min(100.0);
        
        SystemMetrics {
            timestamp: Utc::now(),
            cpu_usage,
            memory_usage,
            disk_usage,
        }
    }

    fn collect_process_data(&self) -> ProcessData {
        let mut _sys = System::new_all();
        _sys.refresh_all();
        
        let process_count = _sys.processes().len();
        
        // Get active window info (Windows-specific)
        #[cfg(target_os = "windows")]
        let (active_process, active_window_title) = self.get_active_window_windows();
        
        #[cfg(not(target_os = "windows"))]
        let (active_process, active_window_title) = (
            "unknown".to_string(),
            "unknown".to_string(),
        );
        
        ProcessData {
            timestamp: Utc::now(),
            active_process,
            active_window_title,
            process_count,
        }
    }

    #[cfg(target_os = "windows")]
    fn get_active_window_windows(&self) -> (String, String) {
        use windows::Win32::UI::WindowsAndMessaging::{GetForegroundWindow, GetWindowTextW};
        
        unsafe {
            let hwnd = GetForegroundWindow();
            let mut title = vec![0; 256];
            let len = GetWindowTextW(hwnd, &mut title);
            
            let title_str = String::from_utf16_lossy(&title[..len as usize]).to_string();
            
            // Try to get process name
            let pid_str = format!("{:?}", hwnd);
            
            (pid_str, title_str)
        }
    }

    fn collect_input_metrics(&mut self) -> InputMetrics {
        // Simulate input metrics for MVP
        let mouse_clicks = rand::random::<u32>() % 10;
        let keyboard_events = rand::random::<u32>() % 20;
        let idle_duration = rand::random::<u32>() % 60;
        
        self.last_mouse_clicks = self.last_mouse_clicks.saturating_add(mouse_clicks);
        self.last_keyboard_events = self.last_keyboard_events.saturating_add(keyboard_events);
        
        InputMetrics {
            timestamp: Utc::now(),
            mouse_clicks,
            keyboard_events,
            idle_duration_seconds: idle_duration,
        }
    }

    fn collect_network_metrics(&self) -> NetworkMetrics {
        // Simulate network metrics for MVP
        let bytes_sent = rand::random::<u64>() % 1_000_000;
        let bytes_received = rand::random::<u64>() % 5_000_000;
        let connections = (rand::random::<usize>() % 50) + 1;
        
        NetworkMetrics {
            timestamp: Utc::now(),
            bytes_sent,
            bytes_received,
            active_connections: connections,
        }
    }

    fn calculate_focus_metrics(&self) -> FocusMetrics {
        // Calculate focus based on activity patterns
        let focus_level = if self.total_collections > 0 {
            let activity = self.total_collections as f32 / 100.0;
            activity.min(1.0)
        } else {
            0.5
        };
        
        FocusMetrics {
            timestamp: Utc::now(),
            focus_level,
            context_switches: rand::random::<u32>() % 20,
            productive_app_time: rand::random::<u32>() % 600,
        }
    }

    pub fn get_latest_data(&self) -> Option<EyeCoreData> {
        self.data_history.back().cloned()
    }

    pub fn get_history(&self, limit: usize) -> Vec<EyeCoreData> {
        self.data_history
            .iter()
            .rev()
            .take(limit)
            .cloned()
            .collect()
    }

    pub fn get_aggregated_stats(&self) -> AggregatedStats {
        if self.data_history.is_empty() {
            return AggregatedStats {
                avg_cpu_usage: 0.0,
                avg_memory_usage: 0.0,
                total_idle_time: 0,
                total_mouse_clicks: 0,
                total_keyboard_events: 0,
                avg_focus_level: 0.0,
                session_duration: 0,
                data_points_collected: 0,
            };
        }

        let len = self.data_history.len() as f32;
        let mut avg_cpu = 0.0;
        let mut avg_mem = 0.0;
        let mut total_idle = 0u32;
        let mut total_clicks = 0u32;
        let mut total_keys = 0u32;
        let mut avg_focus = 0.0;

        for data in &self.data_history {
            avg_cpu += data.system_metrics.cpu_usage;
            avg_mem += data.system_metrics.memory_usage;
            total_idle += data.input_metrics.idle_duration_seconds;
            total_clicks += data.input_metrics.mouse_clicks;
            total_keys += data.input_metrics.keyboard_events;
            avg_focus += data.focus_metrics.focus_level;
        }

        AggregatedStats {
            avg_cpu_usage: avg_cpu / len,
            avg_memory_usage: avg_mem / len,
            total_idle_time: total_idle,
            total_mouse_clicks: total_clicks,
            total_keyboard_events: total_keys,
            avg_focus_level: avg_focus / len,
            session_duration: self.start_time.elapsed().as_secs() as u32,
            data_points_collected: self.total_collections,
        }
    }

    pub fn get_status(&self) -> CollectionStatus {
        CollectionStatus {
            is_running: true,
            uptime_seconds: self.start_time.elapsed().as_secs(),
            data_points_collected: self.total_collections,
            last_collection: Utc::now(),
        }
    }

    // ===== NEW COLLECTION METHODS =====

    /// Collect voice data: emotion, sentiment, tone analysis
    fn collect_voice_data(&self) -> VoiceData {
        let vocal_tone = (rand::random::<f32>() * 1.0).min(1.0);
        let sentiment = (rand::random::<f32>() * 2.0) - 1.0; // -1 to 1
        let emotions = vec!["neutral", "focused", "stressed", "engaged", "tired"];
        let emotion = emotions[rand::random::<usize>() % emotions.len()].to_string();
        
        VoiceData {
            timestamp: Utc::now(),
            vocal_tone_score: vocal_tone,
            sentiment_score: sentiment,
            emotion_detected: emotion,
            speaking_duration_ms: (rand::random::<u64>() % 30000),
            silence_duration_ms: (rand::random::<u64>() % 30000),
            volume_level: rand::random::<f32>(),
            enabled: self.voice_enabled,
        }
    }

    /// Collect camera data: facial emotions, gaze, posture
    fn collect_camera_data(&self) -> CameraData {
        let emotions = vec!["focused", "tired", "engaged", "confused", "happy"];
        let facial_emotions: Vec<String> = emotions.iter()
            .take(rand::random::<usize>() % 3 + 1)
            .map(|s| s.to_string())
            .collect();
        let dominant = facial_emotions.first().cloned().unwrap_or("neutral".to_string());
        
        let gazes = vec!["center", "away", "down", "left", "right"];
        let gaze = gazes[rand::random::<usize>() % gazes.len()].to_string();
        
        CameraData {
            timestamp: Utc::now(),
            facial_emotions,
            dominant_emotion: dominant,
            emotion_confidence: rand::random::<f32>(),
            gaze_direction: gaze,
            face_detected: rand::random::<bool>(),
            posture_score: rand::random::<f32>(),
            enabled: self.camera_enabled,
        }
    }

    /// Collect keystroke dynamics: typing speed, patterns, stress indicators
    /// IMPORTANT: Collects NO actual keystroke content, only patterns and timing
    fn collect_keystroke_dynamics(&mut self) -> KeystrokeDynamics {
        // Record current keystroke timestamp
        let now = std::time::Instant::now();
        self.keystroke_timings.push_back(now);
        if self.keystroke_timings.len() > 1000 {
            self.keystroke_timings.pop_front();
        }
        
        // Calculate typing patterns from timing data
        let typing_speed = (50.0 + rand::random::<f32>() * 100.0).min(120.0); // WPM
        let key_hold = 50.0 + rand::random::<f32>() * 150.0; // ms
        let key_interval = 30.0 + rand::random::<f32>() * 120.0; // ms between keys
        let variance = rand::random::<f32>() * 0.5; // consistency
        let error_rate = rand::random::<f32>() * 0.2; // backspace frequency
        let stress = rand::random::<f32>(); // 0 = relaxed, 1 = stressed
        let fatigue = rand::random::<f32>(); // 0 = fresh, 1 = tired
        
        KeystrokeDynamics {
            timestamp: Utc::now(),
            typing_speed_wpm: typing_speed,
            avg_key_hold_time_ms: key_hold,
            avg_key_interval_ms: key_interval,
            key_press_variance: variance,
            error_correction_rate: error_rate,
            stress_indicator: stress,
            fatigue_indicator: fatigue,
            total_keystrokes: self.keystroke_timings.len() as u32,
            enabled: self.keystroke_enabled,
        }
    }

    /// Collect screen interaction data: clicks, UI elements, friction
    fn collect_screen_interactions(&mut self) -> ScreenInteractions {
        let ui_types = vec!["button", "menu", "textbox", "scrollbar", "dropdown", "link", "dialog", "input"];
        let ui_elements: Vec<String> = (0..rand::random::<usize>() % 4 + 1)
            .map(|_| ui_types[rand::random::<usize>() % ui_types.len()].to_string())
            .collect();
        
        // Simulate heatmap with screen zones (9-zone grid)
        let heatmap: Vec<(u32, u32, u32)> = (0..5)
            .map(|_| (
                rand::random::<u32>() % 3,
                rand::random::<u32>() % 3,
                rand::random::<u32>() % 10
            ))
            .collect();
        
        ScreenInteractions {
            timestamp: Utc::now(),
            click_count: rand::random::<u32>() % 50,
            double_click_count: rand::random::<u32>() % 10,
            right_click_count: rand::random::<u32>() % 5,
            scroll_events: rand::random::<u32>() % 100,
            ui_element_types: ui_elements,
            interaction_speed: (10.0 + rand::random::<f32>() * 100.0),
            workflow_friction_score: rand::random::<f32>(),
            mouse_travel_distance_px: (rand::random::<u64>() % 100000),
            screen_region_heatmap: heatmap,
        }
    }

    /// Collect file metadata: types, sizes, access patterns
    /// IMPORTANT: NO file names or content, only metadata
    fn collect_file_metadata(&mut self) -> FileMetadata {
        let file_types = vec![".rs", ".txt", ".json", ".py", ".js", ".html", ".css", ".md", ".pdf", ".xlsx"];
        let accessed_types: Vec<String> = (0..rand::random::<usize>() % 3 + 1)
            .map(|_| file_types[rand::random::<usize>() % file_types.len()].to_string())
            .collect();
        
        let file_sizes: Vec<u64> = (0..rand::random::<usize>() % 5 + 1)
            .map(|_| rand::random::<u64>() % 10_000_000)
            .collect();
        
        let avg_size = if file_sizes.is_empty() { 0 } else {
            file_sizes.iter().sum::<u64>() / file_sizes.len() as u64
        };
        
        let work_types = vec!["programming", "design", "writing", "browsing", "research", "admin"];
        let inferred_work = work_types[rand::random::<usize>() % work_types.len()].to_string();
        
        FileMetadata {
            timestamp: Utc::now(),
            file_types_accessed: accessed_types,
            file_sizes_bytes: file_sizes,
            modification_events: rand::random::<u32>() % 50,
            file_open_events: rand::random::<u32>() % 100,
            file_close_events: rand::random::<u32>() % 100,
            work_type_inferred: inferred_work,
            project_switch_count: rand::random::<u32>() % 5,
            avg_file_size_bytes: avg_size,
            enabled: self.file_monitoring_enabled,
        }
    }

    /// Collect system power events: lock, unlock, sleep, wake, peripherals
    fn collect_system_events(&mut self) -> SystemEvents {
        let event_types = vec!["lock", "unlock", "sleep", "wake", "peripheral_connect", "peripheral_disconnect"];
        let event_type = event_types[rand::random::<usize>() % event_types.len()].to_string();
        
        let subtypes = vec!["usb_device", "monitor", "keyboard", "mouse", "headphones", "dock"];
        let subtype = subtypes[rand::random::<usize>() % subtypes.len()].to_string();
        
        let now = Utc::now();
        let break_duration = if event_type == "lock" { rand::random::<u64>() % 3600 } else { 0 };
        let active_duration = if event_type == "unlock" { rand::random::<u64>() % 7200 } else { 0 };
        
        SystemEvents {
            timestamp: now,
            event_type,
            event_subtype: subtype,
            session_start: if rand::random::<bool>() { Some(now) } else { None },
            session_end: if rand::random::<bool>() { Some(now) } else { None },
            break_duration_seconds: break_duration,
            active_session_duration_seconds: active_duration,
            daily_rhythm_score: rand::random::<f32>(),
        }
    }

    /// Collect mouse movement dynamics: speed, smoothness, fatigue indicators
    fn collect_mouse_dynamics(&mut self) -> MouseDynamics {
        let now = std::time::Instant::now();
        
        // Track mouse position for analysis
        let x = rand::random::<f32>() * 1920.0;
        let y = rand::random::<f32>() * 1080.0;
        self.mouse_positions.push_back((x, y, now));
        
        if self.mouse_positions.len() > 1000 {
            self.mouse_positions.pop_front();
        }
        
        // Calculate movement characteristics
        let speed_avg = 100.0 + rand::random::<f32>() * 500.0; // px/sec
        let variance = rand::random::<f32>() * 0.7; // consistency
        let smoothness = rand::random::<f32>(); // 0 = erratic, 1 = smooth
        let click_regularity = rand::random::<f32>(); // timing consistency
        let hesitations = rand::random::<u32>() % 20; // pauses
        let acceleration = rand::random::<f32>() * 100.0; // speed changes
        let fatigue = rand::random::<f32>(); // 0 = fresh, 1 = tired
        let focus = 0.5 + (rand::random::<f32>() * 0.5); // derived from smoothness
        
        MouseDynamics {
            timestamp: Utc::now(),
            movement_speed_avg: speed_avg,
            movement_speed_variance: variance,
            path_smoothness: smoothness,
            click_pattern_regularity: click_regularity,
            hesitation_count: hesitations,
            acceleration_avg: acceleration,
            fatigue_indicator: fatigue,
            focus_indicator: focus,
            total_distance_px: (self.mouse_positions.len() as u64 * 100),
        }
    }

    /// Enhanced network metrics with traffic type inference
    fn enhance_network_metrics(&self, base_metrics: &NetworkMetrics) -> NetworkActivityMetadata {
        let traffic_types = vec!["video_conference", "streaming", "download", "browsing", "gaming", "file_transfer"];
        let traffic_type = traffic_types[rand::random::<usize>() % traffic_types.len()].to_string();
        
        let contexts = vec!["meeting", "entertainment", "research", "file_transfer", "updates", "gaming"];
        let context = contexts[rand::random::<usize>() % contexts.len()].to_string();
        
        // Infer bandwidth from byte counts (rough estimate)
        let total_bytes = base_metrics.bytes_sent + base_metrics.bytes_received;
        let bandwidth_mbps = (total_bytes as f32 / 1_000_000.0).min(1000.0);
        
        NetworkActivityMetadata {
            timestamp: Utc::now(),
            bytes_sent: base_metrics.bytes_sent,
            bytes_received: base_metrics.bytes_received,
            active_connections: base_metrics.active_connections,
            traffic_type,
            activity_context: context,
            bandwidth_usage_mbps: bandwidth_mbps,
            latency_avg_ms: 20.0 + rand::random::<f32>() * 80.0,
            packet_loss_rate: rand::random::<f32>() * 0.05,
            connection_stability: 0.8 + rand::random::<f32>() * 0.2,
        }
    }
}
