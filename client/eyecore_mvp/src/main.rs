mod data_collector;
mod models;
mod api;
mod utils;

use axum::{
    routing::get,
    Router,
};
use std::sync::Arc;
use tokio::sync::RwLock;
use log::info;

#[tokio::main]
async fn main() {
    env_logger::init();
    
    info!("🔍 EyeCore MVP Starting...");
    
    // Initialize data collector
    let collector = Arc::new(RwLock::new(data_collector::DataCollector::new()));
    
    // Start background collection tasks
    let collector_clone = Arc::clone(&collector);
    tokio::spawn(async move {
        loop {
            collector_clone.write().await.collect_all().await;
            tokio::time::sleep(tokio::time::Duration::from_secs(5)).await;
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
