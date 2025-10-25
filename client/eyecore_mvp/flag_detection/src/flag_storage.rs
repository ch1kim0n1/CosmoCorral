use crate::models::Flag;
use chrono::Utc;
use log::{info, error};
use serde_json::to_string_pretty;
use std::path::{Path, PathBuf};
use tokio::fs;

pub struct FlagStorage {
    flags_dir: PathBuf,
}

impl FlagStorage {
    pub fn new(flags_dir: &str) -> Self {
        FlagStorage {
            flags_dir: PathBuf::from(flags_dir),
        }
    }
    
    /// Initialize flags storage directory
    pub async fn initialize(&self) -> std::io::Result<()> {
        fs::create_dir_all(&self.flags_dir).await?;
        info!("✓ Flag storage initialized at: {:?}", self.flags_dir);
        Ok(())
    }
    
    /// Save a single flag to JSON file
    pub async fn save_flag(&self, flag: &Flag) -> std::io::Result<PathBuf> {
        let timestamp = Utc::now().format("%Y-%m-%d_%H-%M-%S-%3f");
        let filename = format!("flag_{}_{}.json", timestamp, &flag.id[0..8]);
        let filepath = self.flags_dir.join(&filename);
        
        let json_str = to_string_pretty(flag)?;
        fs::write(&filepath, json_str).await?;
        
        info!("🚩 Flag saved: {} - {}", flag.title, filename);
        Ok(filepath)
    }
    
    /// Load all flags from the directory
    pub async fn load_all_flags(&self) -> std::io::Result<Vec<Flag>> {
        let mut flags = Vec::new();
        let mut entries = fs::read_dir(&self.flags_dir).await?;
        
        while let Some(entry) = entries.next_entry().await? {
            let path = entry.path();
            if path.extension().and_then(|s| s.to_str()) == Some("json") {
                match fs::read_to_string(&path).await {
                    Ok(content) => {
                        match serde_json::from_str::<Flag>(&content) {
                            Ok(flag) => flags.push(flag),
                            Err(e) => error!("Failed to parse flag file {:?}: {}", path, e),
                        }
                    }
                    Err(e) => error!("Failed to read flag file {:?}: {}", path, e),
                }
            }
        }
        
        Ok(flags)
    }
    
    /// Get all flags for a specific session
    pub async fn get_flags_by_session(&self, session_id: &str) -> std::io::Result<Vec<Flag>> {
        let all_flags = self.load_all_flags().await?;
        Ok(all_flags.into_iter().filter(|f| f.session_id == session_id).collect())
    }
    
    /// Get path to flags directory
    pub fn get_flags_dir(&self) -> &Path {
        &self.flags_dir
    }
}
