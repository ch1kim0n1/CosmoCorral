mod models;
mod detector;
mod flag_storage;

use log::{info, error};
use notify::{Watcher, RecursiveMode, Event, EventKind};
use std::path::PathBuf;
use std::sync::Arc;
use tokio::sync::RwLock;

#[tokio::main]
async fn main() {
    env_logger::init();
    
    info!("🚩 Flag Detection System Starting...");
    
    // Initialize flag storage
    let flag_storage = Arc::new(RwLock::new(
        flag_storage::FlagStorage::new("../data/flags")
    ));
    
    if let Err(e) = flag_storage.write().await.initialize().await {
        error!("Failed to initialize flag storage: {}", e);
        return;
    }
    
    // Initialize detector with thresholds
    let detector = Arc::new(detector::FlagDetector::new());
    
    info!("✓ Flag detector initialized");
    
    // Watch for new data files in ../data/timeslots
    let data_dir = PathBuf::from("../data/timeslots");
    
    if !data_dir.exists() {
        error!("Data directory does not exist: {:?}", data_dir);
        error!("Please ensure EyeCore is running and generating data");
        return;
    }
    
    info!("📂 Watching directory: {:?}", data_dir);
    
    // Create file watcher
    let (tx, mut rx) = tokio::sync::mpsc::channel(100);
    
    let mut watcher = notify::recommended_watcher(move |res: Result<Event, notify::Error>| {
        match res {
            Ok(event) => {
                if let EventKind::Create(_) | EventKind::Modify(_) = event.kind {
                    for path in event.paths {
                        if path.extension().and_then(|s| s.to_str()) == Some("json") {
                            let _ = tx.blocking_send(path);
                        }
                    }
                }
            }
            Err(e) => error!("Watch error: {:?}", e),
        }
    }).expect("Failed to create watcher");
    
    watcher.watch(&data_dir, RecursiveMode::NonRecursive)
        .expect("Failed to watch directory");
    
    info!("✓ File watcher started");
    info!("🔍 Monitoring for anomalies in real-time...");
    
    // Process incoming data files
    while let Some(file_path) = rx.recv().await {
        info!("📄 New data file detected: {:?}", file_path);
        
        let detector_clone = Arc::clone(&detector);
        let storage_clone = Arc::clone(&flag_storage);
        
        tokio::spawn(async move {
            // Read and analyze the data file
            match tokio::fs::read_to_string(&file_path).await {
                Ok(content) => {
                    match serde_json::from_str::<models::EyeCoreDataFile>(&content) {
                        Ok(data_file) => {
                            // Detect anomalies
                            match detector_clone.analyze_data(&data_file.data).await {
                                Ok(flags) if !flags.is_empty() => {
                                    info!("🚩 Found {} flags in data", flags.len());
                                    
                                    // Save flags to file
                                    for flag in flags {
                                        if let Err(e) = storage_clone.write().await.save_flag(&flag).await {
                                            error!("Failed to save flag: {}", e);
                                        }
                                    }
                                }
                                Ok(_) => {
                                    // No flags - data looks normal
                                }
                                Err(e) => error!("Flag detection failed: {}", e),
                            }
                        }
                        Err(e) => error!("Failed to parse data file: {}", e),
                    }
                }
                Err(e) => error!("Failed to read file: {}", e),
            }
        });
    }
    
    info!("🛑 Flag detection system shutting down");
}
