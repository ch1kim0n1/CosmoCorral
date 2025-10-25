mod data_collector;
mod models;
mod api;
mod utils;
mod storage;
mod voice;
mod audio_cleaner;

use axum::{
    routing::get,
    Router,
};
use std::sync::Arc;
use tokio::sync::{RwLock, mpsc};
use log::info;
use std::path::PathBuf;

#[tokio::main]
async fn main() {
    env_logger::init();
    
    info!("🔍 EyeCore MVP Starting...");
    
    // Initialize data storage
    let storage = Arc::new(storage::DataStorage::new("./data"));
    storage.initialize().await.expect("Failed to initialize data storage");
    
    // Initialize data collector
    let collector = Arc::new(RwLock::new(data_collector::DataCollector::new()));
    
    // Create channel for audio cleaning pipeline
    let (audio_tx, mut audio_rx) = mpsc::channel::<PathBuf>(100);
    
    // Start background collection tasks
    let collector_clone = Arc::clone(&collector);
    let storage_clone = Arc::clone(&storage);
    tokio::spawn(async move {
        loop {
            collector_clone.write().await.collect_all().await;
            
            // Save collected data to disk
            if let Some(data) = collector_clone.read().await.get_latest_data() {
                if let Err(e) = storage_clone.save_data_snapshot(&data).await {
                    log::error!("Failed to save data snapshot: {}", e);
                }
            }
            
            tokio::time::sleep(tokio::time::Duration::from_secs(5)).await;
        }
    });
    
    // Start voice collection task (if API key available)
    if let Ok(api_key) = std::env::var("ELEVENLABS_API_KEY") {
        let storage_clone = Arc::clone(&storage);
        let audio_tx_clone = audio_tx.clone();
        let collector_clone = Arc::clone(&collector);
        
        tokio::spawn(async move {
            let voice_collector = voice::VoiceCollector::new(api_key);
            
            loop {
                // Check if voice is enabled
                let voice_enabled = {
                    let collector_guard = collector_clone.read().await;
                    collector_guard.get_latest_data()
                        .and_then(|d| d.voice_data)
                        .map(|v| v.enabled)
                        .unwrap_or(false)
                };
                
                if voice_enabled {
                    info!("📢 Collecting voice data...");
                    
                    // Collect 5 seconds of audio
                    let audio_result = voice_collector.collect_audio_chunk(5000).await;
                    match audio_result {
                        Ok(audio_bytes) if !audio_bytes.is_empty() => {
                            let session_id = uuid::Uuid::new_v4().to_string();
                            
                            // Save raw audio
                            match storage_clone.save_audio(&audio_bytes, &session_id).await {
                                Ok(audio_path) => {
                                    info!("✓ Audio saved: {:?}", audio_path);
                                    
                                    // Send to cleaning pipeline
                                    let _ = audio_tx_clone.send(audio_path.clone()).await;
                                    
                                    // Analyze with ElevenLabs
                                    let analysis_result = voice_collector.analyze_audio_with_elevenlabs(&audio_bytes).await;
                                    match analysis_result {
                                        Ok(analysis) => {
                                            info!("✓ Audio analysis complete: {} chars transcribed", analysis.transcription.len());
                                            
                                            // Save transcription and anomalies
                                            let _ = storage_clone.save_transcription(
                                                &session_id,
                                                &analysis.transcription,
                                                &analysis.anomalies,
                                            ).await;
                                            
                                            let _ = storage_clone.save_audio_anomalies(
                                                &session_id,
                                                &analysis.anomalies,
                                            ).await;
                                        }
                                        Err(e) => log::error!("Voice analysis failed: {}", e),
                                    }
                                }
                                Err(e) => log::error!("Failed to save audio: {}", e),
                            }
                        }
                        Ok(_) => log::debug!("No audio data collected"),
                        Err(e) => log::error!("Audio collection failed: {}", e),
                    }
                }
                
                tokio::time::sleep(tokio::time::Duration::from_secs(10)).await;
            }
        });
        
        info!("✓ Voice collection task started");
    } else {
        info!("⚠ ELEVENLABS_API_KEY not set - voice collection disabled");
    }
    
    // Start audio cleaning pipeline
    let storage_clone = Arc::clone(&storage);
    tokio::spawn(async move {
        info!("🧹 Audio cleaning pipeline started");
        
        while let Some(audio_path) = audio_rx.recv().await {
            info!("Cleaning audio file: {:?}", audio_path);
            
            let clean_result = audio_cleaner::AudioCleaner::clean_audio_segment(
                &audio_path,
                -40.0, // silence threshold in dB
                500,   // minimum speech duration in ms
            ).await;
            
            match clean_result {
                Ok(cleaned) => {
                    // Save cleaned audio
                    let cleaned_filename = audio_path
                        .file_name()
                        .and_then(|n| n.to_str())
                        .map(|n| n.replace(".wav", "_cleaned.wav"))
                        .unwrap_or_else(|| "cleaned.wav".to_string());
                    
                    let cleaned_path = storage_clone
                        .get_data_dir()
                        .join("raw_audio")
                        .join(cleaned_filename);
                    
                    let save_result = cleaned.save(&cleaned_path).await;
                    if let Err(e) = save_result {
                        log::error!("Failed to save cleaned audio: {}", e);
                    } else {
                        info!("✓ Audio cleaned: {:.1}ms -> {:.1}ms", 
                            cleaned.original_duration_ms, 
                            cleaned.cleaned_duration_ms
                        );
                    }
                }
                Err(e) => log::error!("Audio cleaning failed: {}", e),
            }
        }
    });
    
    // Build router with all endpoints
    let app = Router::new()
        // Health & core endpoints
        .route("/health", get(api::handlers::health))
        .route("/data/latest", get(api::handlers::get_latest_data))
        .route("/data/history", get(api::handlers::get_history))
        .route("/data/stats", get(api::handlers::get_stats))
        .route("/status", get(api::handlers::get_status))
        
        // Data endpoints for individual metrics
        .route("/data/voice", get(api::handlers::get_voice_data))
        .route("/data/camera", get(api::handlers::get_camera_data))
        .route("/data/keystroke", get(api::handlers::get_keystroke_dynamics))
        .route("/data/screen", get(api::handlers::get_screen_interactions))
        .route("/data/files", get(api::handlers::get_file_metadata))
        .route("/data/system-events", get(api::handlers::get_system_events))
        .route("/data/mouse", get(api::handlers::get_mouse_dynamics))
        .route("/data/network", get(api::handlers::get_network_metadata))
        
        // Control endpoints for enabling/disabling modules
        .route("/control/voice/enable", get(api::handlers::enable_voice))
        .route("/control/voice/disable", get(api::handlers::disable_voice))
        .route("/control/camera/enable", get(api::handlers::enable_camera))
        .route("/control/camera/disable", get(api::handlers::disable_camera))
        .route("/control/keystroke/enable", get(api::handlers::enable_keystroke))
        .route("/control/keystroke/disable", get(api::handlers::disable_keystroke))
        .route("/control/files/enable", get(api::handlers::enable_file_monitoring))
        .route("/control/files/disable", get(api::handlers::disable_file_monitoring))
        
        .with_state(collector);
    
    // Start server
    let listener = tokio::net::TcpListener::bind("127.0.0.1:3000")
        .await
        .unwrap();
    
    info!("🚀 EyeCore API running on http://127.0.0.1:3000");
    
    axum::serve(listener, app).await.unwrap();
}
