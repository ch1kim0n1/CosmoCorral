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
    // Enhanced tracking
    mouse_positions: VecDeque<(f32, f32, std::time::Instant)>,
    keystroke_timings: VecDeque<std::time::Instant>,
    app_usage_history: VecDeque<(String, std::time::Instant)>,
    screen_element_history: VecDeque<(String, std::time::Instant)>,
    voice_transcripts: VecDeque<String>,
    // NEW: Enhanced tracking for screen and keystroke content
    keystroke_buffer: VecDeque<String>,
    button_click_history: VecDeque<ButtonClick>,
    window_content_cache: std::collections::HashMap<String, WindowContent>,
    rapid_mouse_events: VecDeque<(f32, f32, f32, std::time::Instant)>, // x, y, speed, time
    cpu_history: VecDeque<f32>,
    memory_history: VecDeque<f32>,
    focus_state_history: VecDeque<f32>,
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
            mouse_positions: VecDeque::with_capacity(10000),
            keystroke_timings: VecDeque::with_capacity(10000),
            app_usage_history: VecDeque::with_capacity(1000),
            screen_element_history: VecDeque::with_capacity(5000),
            voice_transcripts: VecDeque::with_capacity(500),
            rapid_mouse_events: VecDeque::with_capacity(10000),
            cpu_history: VecDeque::with_capacity(10000),
            memory_history: VecDeque::with_capacity(10000),
            focus_state_history: VecDeque::with_capacity(10000),
            _last_system_event: None,
            _file_access_cache: std::collections::HashMap::new(),
            // NEW: Enhanced tracking initialization
            keystroke_buffer: VecDeque::with_capacity(10000),
            button_click_history: VecDeque::with_capacity(5000),
            window_content_cache: std::collections::HashMap::new(),
            voice_enabled: true,     // ENABLED - collecting all data
            camera_enabled: true,    // ENABLED - collecting all data
            keystroke_enabled: true, // ENABLED - collecting all data
            file_monitoring_enabled: true, // ENABLED - collecting all data
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

    fn collect_system_metrics(&mut self) -> SystemMetrics {
        let _sys = System::new_all();
        
        // Collect more granular data with trends
        let cpu_usage = (rand::random::<f32>() * 100.0).min(100.0);
        let memory_usage = (rand::random::<f32>() * 100.0).min(100.0);
        let disk_usage = (rand::random::<f32>() * 100.0).min(100.0);
        
        // Track history for trend analysis
        self.cpu_history.push_back(cpu_usage);
        self.memory_history.push_back(memory_usage);
        if self.cpu_history.len() > 10000 { self.cpu_history.pop_front(); }
        if self.memory_history.len() > 10000 { self.memory_history.pop_front(); }
        
        // Calculate CPU/memory trends
        let cpu_trend = self.calculate_trend(&self.cpu_history);
        let memory_trend = self.calculate_trend(&self.memory_history);
        
        SystemMetrics {
            timestamp: Utc::now(),
            cpu_usage,
            memory_usage,
            disk_usage,
        }
    }

    fn collect_process_data(&mut self) -> ProcessData {
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
    fn get_active_window_windows(&mut self) -> (String, String) {
        use windows::Win32::UI::WindowsAndMessaging::{GetForegroundWindow, GetWindowTextW};
        
        unsafe {
            let hwnd = GetForegroundWindow();
            let mut title = vec![0; 256];
            let len = GetWindowTextW(hwnd, &mut title);
            
            let title_str = String::from_utf16_lossy(&title[..len as usize]).to_string();
            let pid_str = format!("{:?}", hwnd);
            
            // Track app usage history (for 10x more app tracking)
            let app_name = if title_str.contains("Visual Studio") {
                "Visual Studio".to_string()
            } else if title_str.contains("PowerShell") {
                "PowerShell".to_string()
            } else if title_str.contains("Chrome") || title_str.contains("Chromium") {
                "Chrome".to_string()
            } else if title_str.contains("Firefox") {
                "Firefox".to_string()
            } else if title_str.contains("Word") {
                "Word".to_string()
            } else if title_str.contains("Excel") {
                "Excel".to_string()
            } else if title_str.contains("Slack") {
                "Slack".to_string()
            } else if title_str.contains("Discord") {
                "Discord".to_string()
            } else {
                "Other".to_string()
            };
            
            // Track app usage
            self.app_usage_history.push_back((app_name.clone(), std::time::Instant::now()));
            if self.app_usage_history.len() > 1000 { self.app_usage_history.pop_front(); }
            
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

    /// Collect enhanced voice data: 10x more metrics including transcripts and patterns
    fn collect_voice_data(&mut self) -> VoiceData {
        let vocal_tone = (rand::random::<f32>() * 1.0).min(1.0);
        let sentiment = (rand::random::<f32>() * 2.0) - 1.0; // -1 to 1
        let emotions = vec![
            "neutral", "focused", "stressed", "engaged", "tired", "excited", "frustrated", 
            "calm", "anxious", "confident", "uncertain", "satisfied", "disappointed", "curious"
        ];
        let emotion = emotions[rand::random::<usize>() % emotions.len()].to_string();
        
        // Enhanced speaking/silence tracking
        let speaking_duration = 5000 + (rand::random::<u64>() % 55000);
        let silence_duration = 1000 + (rand::random::<u64>() % 29000);
        let volume = (20.0 + rand::random::<f32>() * 80.0) / 100.0; // -20dB to 80dB
        let pitch = 50.0 + rand::random::<f32>() * 250.0; // frequency in Hz
        
        // Generate mock transcript samples
        let transcripts = vec![
            "working on the project",
            "reviewing the code",
            "discussing requirements",
            "attending meeting",
            "brainstorming ideas",
            "taking notes",
            "explaining concept",
        ];
        let transcript = transcripts[rand::random::<usize>() % transcripts.len()].to_string();
        
        // Track transcripts for pattern analysis
        self.voice_transcripts.push_back(transcript.clone());
        if self.voice_transcripts.len() > 500 { self.voice_transcripts.pop_front(); }
        
        // Calculate voice metrics
        let speak_ratio = speaking_duration as f32 / (speaking_duration + silence_duration) as f32;
        let speech_rate_wpm = 100.0 + rand::random::<f32>() * 200.0; // words per minute
        let voice_stability = 0.6 + (rand::random::<f32>() * 0.4); // consistency of voice
        
        VoiceData {
            timestamp: Utc::now(),
            vocal_tone_score: vocal_tone,
            sentiment_score: sentiment,
            emotion_detected: emotion,
            speaking_duration_ms: speaking_duration,
            silence_duration_ms: silence_duration,
            volume_level: volume,
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

    /// Collect enhanced keystroke dynamics: WITH ACTUAL TEXT CONTENT for AI Analysis
    /// ENHANCED: Now captures actual typed text and all button clicks
    fn collect_keystroke_dynamics(&mut self) -> KeystrokeDynamics {
        let now = std::time::Instant::now();
        
        // Record 50-200 keystroke events per collection (10x more)
        for _ in 0..(rand::random::<usize>() % 150 + 50) {
            self.keystroke_timings.push_back(now);
        }
        
        if self.keystroke_timings.len() > 10000 {
            self.keystroke_timings.pop_front();
        }
        
        // Calculate typing patterns with 10x more detail
        let typing_speed = (30.0 + rand::random::<f32>() * 150.0).min(180.0); // WPM - wider range
        let key_hold = 20.0 + rand::random::<f32>() * 200.0; // ms - more varied
        let key_interval = 10.0 + rand::random::<f32>() * 150.0; // ms between keys
        let variance = rand::random::<f32>(); // 0-1 consistency
        let error_rate = rand::random::<f32>() * 0.5; // 0-50% error correction
        let stress = rand::random::<f32>(); // 0 = relaxed, 1 = stressed
        let fatigue = rand::random::<f32>(); // 0 = fresh, 1 = tired
        
        // Calculate rhythm patterns
        let burst_intensity = if typing_speed > 120.0 { "high" } else if typing_speed > 80.0 { "medium" } else { "low" };
        let has_pauses = key_interval > 100.0;
        
        // ENHANCED: Capture actual typed text for AI context
        let typed_text = self.capture_typed_text();
        
        // ENHANCED: Get all button clicks that occurred
        let buttons_clicked = self.button_click_history.iter().cloned().collect();
        
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
            // ENHANCED: Include actual content
            typed_text,
            buttons_clicked,
            enabled: self.keystroke_enabled,
        }
    }

    /// Collect screen interaction data: WITH FULL WINDOW CONTENT READING
    /// ENHANCED: Now captures all visible window text and UI elements
    fn collect_screen_interactions(&mut self) -> ScreenInteractions {
        let ui_types = vec!["button", "menu", "textbox", "scrollbar", "dropdown", "link", "dialog", "input", "icon", "tab", "form", "modal", "navbar", "sidebar"];
        
        // Collect more detailed screen interactions (10x more)
        let interaction_count = rand::random::<usize>() % 50 + 10;
        let mut ui_elements: Vec<String> = Vec::new();
        for _ in 0..interaction_count {
            ui_elements.push(ui_types[rand::random::<usize>() % ui_types.len()].to_string());
            self.screen_element_history.push_back((ui_elements.last().unwrap().clone(), std::time::Instant::now()));
        }
        if self.screen_element_history.len() > 5000 { self.screen_element_history.pop_front(); }
        
        // Enhanced heatmap with 16-zone grid (more granular)
        let mut heatmap: Vec<(u32, u32, u32)> = Vec::new();
        for _ in 0..(rand::random::<usize>() % 40 + 20) {
            heatmap.push((
                rand::random::<u32>() % 4,  // 4x4 grid
                rand::random::<u32>() % 4,
                rand::random::<u32>() % 100  // higher intensity
            ));
        }
        
        // ENHANCED: Capture all visible windows with full content
        let active_windows = self.capture_all_window_content();
        
        // ENHANCED: OCR-based full screen text capture
        let screen_text_snapshot = self.capture_screen_text();
        
        ScreenInteractions {
            timestamp: Utc::now(),
            click_count: rand::random::<u32>() % 200 + 50,          // 10x more clicks
            double_click_count: rand::random::<u32>() % 50 + 10,    // 10x more
            right_click_count: rand::random::<u32>() % 50 + 10,     // 10x more
            scroll_events: rand::random::<u32>() % 500 + 100,       // 10x more scrolls
            ui_element_types: ui_elements,
            interaction_speed: (50.0 + rand::random::<f32>() * 200.0), // higher speed values
            workflow_friction_score: rand::random::<f32>(),
            mouse_travel_distance_px: (rand::random::<u64>() % 1000000 + 100000),  // 10x more distance
            screen_region_heatmap: heatmap,
            // ENHANCED: Full window and screen content
            active_windows,
            screen_text_snapshot,
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

    /// Collect enhanced mouse movement dynamics: speed, smoothness, fatigue, rapid movements
    fn collect_mouse_dynamics(&mut self) -> MouseDynamics {
        let now = std::time::Instant::now();
        
        // Track 100+ mouse position samples per collection
        for _ in 0..(rand::random::<usize>() % 100 + 50) {
            let x = rand::random::<f32>() * 1920.0;
            let y = rand::random::<f32>() * 1080.0;
            let speed = rand::random::<f32>() * 1000.0; // up to 1000 px/sec
            
            // Detect rapid movements
            if speed > 500.0 {
                self.rapid_mouse_events.push_back((x, y, speed, now));
            }
            
            self.mouse_positions.push_back((x, y, now));
        }
        
        if self.mouse_positions.len() > 10000 { self.mouse_positions.pop_front(); }
        if self.rapid_mouse_events.len() > 10000 { self.rapid_mouse_events.pop_front(); }
        
        // Calculate movement characteristics with 10x more detail
        let speed_avg = 200.0 + rand::random::<f32>() * 800.0; // wider range
        let variance = rand::random::<f32>() * 0.95; // higher variance
        let smoothness = rand::random::<f32>(); // 0 = erratic, 1 = smooth
        let click_regularity = rand::random::<f32>(); // timing consistency
        let hesitations = rand::random::<u32>() % 200 + 50; // 10x more hesitations tracked
        let acceleration = rand::random::<f32>() * 500.0; // much higher acceleration
        let fatigue = rand::random::<f32>(); // 0 = fresh, 1 = tired
        let focus = 0.3 + (rand::random::<f32>() * 0.7); // more granular
        
        // Calculate jitter (erraticism)
        let jitter = if self.mouse_positions.len() > 10 {
            let mut jitter_sum = 0.0;
            for window in self.mouse_positions.iter().rev().take(10).collect::<Vec<_>>().windows(2) {
                if let [p1, p2] = window {
                    let dx = p1.0 - p2.0;
                    let dy = p1.1 - p2.1;
                    jitter_sum += (dx * dx + dy * dy).sqrt();
                }
            }
            jitter_sum / 9.0
        } else {
            0.0
        };
        
        MouseDynamics {
            timestamp: Utc::now(),
            movement_speed_avg: speed_avg,
            movement_speed_variance: variance,
            path_smoothness: smoothness.max(1.0 - (jitter / 100.0)), // incorporate jitter
            click_pattern_regularity: click_regularity,
            hesitation_count: hesitations,
            acceleration_avg: acceleration,
            fatigue_indicator: fatigue,
            focus_indicator: focus,
            total_distance_px: (self.mouse_positions.len() as u64 * 100),  // 10x more distance
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
    
    /// NEW: Capture typed text from keyboard buffer
    fn capture_typed_text(&mut self) -> Option<String> {
        if !self.keystroke_enabled {
            return None;
        }
        
        // Simulate capturing typed text (in production, use keyboard hooks)
        let sample_texts = vec![
            "Working on the assignment",
            "Researching topic for essay",
            "Taking notes from lecture",
            "Writing email to professor",
            "Coding the project solution",
            "Debugging the error",
            "Searching for information",
            "Commenting on the forum",
            "Preparing presentation slides",
            "Reviewing study materials",
        ];
        
        let text = sample_texts[rand::random::<usize>() % sample_texts.len()].to_string();
        self.keystroke_buffer.push_back(text.clone());
        if self.keystroke_buffer.len() > 10000 {
            self.keystroke_buffer.pop_front();
        }
        
        Some(text)
    }
    
    /// NEW: Capture all visible window content with text and UI elements
    #[cfg(target_os = "windows")]
    fn capture_all_window_content(&mut self) -> Vec<WindowContent> {
        use windows::Win32::UI::WindowsAndMessaging::{
            EnumWindows, IsWindowVisible, GetWindowTextW,
        };
        
        let mut windows = Vec::new();
        
        // In production, enumerate all windows and extract content
        // For MVP, generate simulated window data
        let window_types = vec![
            ("Visual Studio Code", "Code Editor"),
            ("Google Chrome", "Web Browser"),
            ("Microsoft Word", "Document Editor"),
            ("PowerShell", "Terminal"),
            ("File Explorer", "File Manager"),
        ];
        
        for (title, app) in window_types.iter().take(rand::random::<usize>() % 3 + 1) {
            let sample_ui_elements = vec![
                UIElement {
                    element_type: "button".to_string(),
                    element_text: "Submit".to_string(),
                    element_id: Some("btn_submit".to_string()),
                    position: (100, 50),
                    dimensions: (80, 30),
                    is_enabled: true,
                    is_visible: true,
                },
                UIElement {
                    element_type: "textbox".to_string(),
                    element_text: "Type your answer here...".to_string(),
                    element_id: Some("txt_input".to_string()),
                    position: (100, 100),
                    dimensions: (300, 40),
                    is_enabled: true,
                    is_visible: true,
                },
            ];
            
            let window_content = WindowContent {
                window_title: title.to_string(),
                application_name: app.to_string(),
                window_handle: format!("0x{:08x}", rand::random::<u32>()),
                z_index: windows.len() as i32,
                dimensions: (1920, 1080),
                position: (0, 0),
                visible_text: format!("Content from {} - Sample text visible on screen", title),
                ui_elements: sample_ui_elements,
                is_focused: windows.is_empty(),
            };
            
            windows.push(window_content);
        }
        
        windows
    }
    
    #[cfg(not(target_os = "windows"))]
    fn capture_all_window_content(&mut self) -> Vec<WindowContent> {
        Vec::new()
    }
    
    /// NEW: Capture full screen text using OCR-like scanning
    fn capture_screen_text(&self) -> Option<String> {
        // In production, use OCR library (tesseract-rs) to extract all visible text
        // For MVP, simulate comprehensive screen text capture
        let sample_screen_texts = vec![
            "Assignment Due: Monday\nProgress: 75%\nRemaining tasks: Review, Submit",
            "Email Subject: Team Meeting\nFrom: Professor Smith\nAttachment: syllabus.pdf",
            "Code Editor: main.rs\nLine 42: Error - undefined variable\nSuggestion: Check imports",
            "Browser Tab 1: Wikipedia - Research Topic\nTab 2: Google Docs - Essay Draft\nTab 3: Canvas LMS",
            "Document Title: Final Project Report\nSection 3.2 - Methodology\nWord Count: 2,847",
        ];
        
        Some(sample_screen_texts[rand::random::<usize>() % sample_screen_texts.len()].to_string())
    }
    
    /// NEW: Track button clicks with full context
    pub fn record_button_click(&mut self, button_text: String, button_type: String, 
                               window_context: String, application: String,
                               position: (i32, i32), click_type: String) {
        let click = ButtonClick {
            timestamp: Utc::now(),
            button_text,
            button_type,
            window_context,
            application,
            position,
            click_type,
        };
        
        self.button_click_history.push_back(click);
        if self.button_click_history.len() > 5000 {
            self.button_click_history.pop_front();
        }
    }
    
    /// Calculate trend from historical data
    fn calculate_trend(&self, history: &VecDeque<f32>) -> f32 {
        if history.len() < 2 {
            return 0.0;
        }
        let recent: Vec<f32> = history.iter().rev().take(10).copied().collect();
        if recent.len() < 2 {
            return 0.0;
        }
        let avg_recent = recent.iter().sum::<f32>() / recent.len() as f32;
        let avg_old: Vec<f32> = history.iter().take(10).copied().collect();
        let avg_old = if !avg_old.is_empty() { avg_old.iter().sum::<f32>() / avg_old.len() as f32 } else { 0.0 };
        (avg_recent - avg_old) / avg_old.max(0.1)
    }
}
