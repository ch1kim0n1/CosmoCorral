use crate::models::*;
use std::path::{Path, PathBuf};
use tokio::fs;
use serde_json::{json, to_string_pretty};
use log::info;
use chrono::Utc;

pub struct DataStorage {
    data_dir: PathBuf,
}

impl DataStorage {
    pub fn new(data_dir: &str) -> Self {
        DataStorage {
            data_dir: PathBuf::from(data_dir),
        }
    }

    /// Initialize data directory structure
    pub async fn initialize(&self) -> std::io::Result<()> {
        // Create main data directory
        fs::create_dir_all(&self.data_dir).await?;
        
        // Create subdirectories for different data types
        let subdirs = vec![
            "timeslots",
            "raw_audio",
            "transcriptions",
            "anomalies",
            "session_logs",
            "hourly_snapshots",
            "daily_reports",
        ];

        for subdir in subdirs {
            fs::create_dir_all(self.data_dir.join(subdir)).await?;
        }

        info!("✓ Data storage initialized at: {:?}", self.data_dir);
        Ok(())
    }

    /// Save complete EyeCore data snapshot with timeslot info
    pub async fn save_data_snapshot(&self, data: &EyeCoreData) -> std::io::Result<PathBuf> {
        let timestamp = data.timestamp.format("%Y-%m-%d_%H-%M-%S-%3f");
        
        // Save to timeslots directory
        let filename = format!("{}_{}.json", timestamp, &data.session_id[0..8]);
        let filepath = self.data_dir.join("timeslots").join(&filename);

        // Add metadata about what data was collected
        let full_data = json!({
            "metadata": {
                "session_id": &data.session_id,
                "timestamp": data.timestamp.to_rfc3339(),
                "data_types_available": {
                    "system_metrics": true,
                    "process_data": true,
                    "input_metrics": true,
                    "network_metrics": true,
                    "focus_metrics": true,
                    "voice_data": data.voice_data.is_some(),
                    "camera_data": data.camera_data.is_some(),
                    "keystroke_dynamics": data.keystroke_dynamics.is_some(),
                    "screen_interactions": data.screen_interactions.is_some(),
                    "file_metadata": data.file_metadata.is_some(),
                    "system_events": data.system_events.is_some(),
                    "mouse_dynamics": data.mouse_dynamics.is_some(),
                    "network_activity_metadata": data.network_activity_metadata.is_some(),
                },
                "saved_at": Utc::now().to_rfc3339(),
            },
            "data": data,
        });

        let json_str = to_string_pretty(&full_data)?;
        fs::write(&filepath, json_str).await?;
        
        info!("✓ Data snapshot saved: {}", filename);
        Ok(filepath)
    }

    /// Save voice/audio data
    pub async fn save_audio(&self, audio_bytes: &[u8], session_id: &str) -> std::io::Result<PathBuf> {
        let timestamp = Utc::now().format("%Y-%m-%d_%H-%M-%S-%3f");
        let filename = format!("{}_{}.wav", timestamp, &session_id[0..8]);
        let filepath = self.data_dir.join("raw_audio").join(&filename);

        fs::write(&filepath, audio_bytes).await?;
        info!("✓ Audio saved: {}", filename);
        Ok(filepath)
    }

    /// Save audio transcription and analysis
    pub async fn save_transcription(
        &self,
        session_id: &str,
        text: &str,
        anomalies: &serde_json::Value,
    ) -> std::io::Result<PathBuf> {
        let timestamp = Utc::now().format("%Y-%m-%d_%H-%M-%S");
        let filename = format!("{}_{}.json", timestamp, &session_id[0..8]);
        let filepath = self.data_dir.join("transcriptions").join(&filename);

        let transcription_data = json!({
            "session_id": session_id,
            "timestamp": Utc::now().to_rfc3339(),
            "text": text,
            "anomalies": anomalies,
        });

        let json_str = to_string_pretty(&transcription_data)?;
        fs::write(&filepath, json_str).await?;
        info!("✓ Transcription saved: {}", filename);
        Ok(filepath)
    }

    /// Save detected audio anomalies
    pub async fn save_audio_anomalies(
        &self,
        session_id: &str,
        anomalies: &serde_json::Value,
    ) -> std::io::Result<PathBuf> {
        let timestamp = Utc::now().format("%Y-%m-%d_%H-%M-%S");
        let filename = format!("anomalies_{}_{}.json", timestamp, &session_id[0..8]);
        let filepath = self.data_dir.join("anomalies").join(&filename);

        let data = json!({
            "session_id": session_id,
            "timestamp": Utc::now().to_rfc3339(),
            "anomalies": anomalies,
            "types": ["background_noise", "distortion", "unusual_sounds", "breaks_in_speech"],
        });

        let json_str = to_string_pretty(&data)?;
        fs::write(&filepath, json_str).await?;
        info!("✓ Anomalies saved: {}", filename);
        Ok(filepath)
    }

    /// Save hourly snapshot for quick historical access
    pub async fn save_hourly_snapshot(&self, data: &EyeCoreData) -> std::io::Result<PathBuf> {
        let hour = data.timestamp.format("%Y-%m-%d_%H");
        let filename = format!("{}_snapshot.json", hour);
        let filepath = self.data_dir.join("hourly_snapshots").join(&filename);

        // Check if file exists, if so append; otherwise create
        let mut hourly_data: serde_json::Value = if filepath.exists() {
            let contents = fs::read_to_string(&filepath).await?;
            serde_json::from_str(&contents).unwrap_or_else(|_| json!({"entries": []}))
        } else {
            json!({"entries": []})
        };

        if let Some(entries) = hourly_data["entries"].as_array_mut() {
            entries.push(json!(data));
        }

        let json_str = to_string_pretty(&hourly_data)?;
        fs::write(&filepath, json_str).await?;
        Ok(filepath)
    }

    /// Get path to data directory
    pub fn get_data_dir(&self) -> &Path {
        &self.data_dir
    }

    /// List all saved sessions
    pub async fn list_sessions(&self) -> std::io::Result<Vec<String>> {
        let timeslots_dir = self.data_dir.join("timeslots");
        let mut entries = fs::read_dir(&timeslots_dir).await?;
        let mut sessions = Vec::new();

        while let Some(entry) = entries.next_entry().await? {
            if let Some(filename) = entry.file_name().to_str() {
                if filename.ends_with(".json") {
                    sessions.push(filename.to_string());
                }
            }
        }

        Ok(sessions)
    }

    /// Get all data files from a specific date
    pub async fn get_data_by_date(&self, date: &str) -> std::io::Result<Vec<PathBuf>> {
        let timeslots_dir = self.data_dir.join("timeslots");
        let mut entries = fs::read_dir(&timeslots_dir).await?;
        let mut files = Vec::new();

        while let Some(entry) = entries.next_entry().await? {
            let path = entry.path();
            if let Some(filename) = path.file_name().and_then(|n| n.to_str()) {
                if filename.contains(date) {
                    files.push(path);
                }
            }
        }

        Ok(files)
    }
}
