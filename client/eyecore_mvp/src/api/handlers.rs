use axum::{
    extract::{State, Query},
    http::StatusCode,
    response::IntoResponse,
    Json,
};
use serde_json::json;
use std::sync::Arc;
use tokio::sync::RwLock;
use crate::data_collector::DataCollector;
use serde::Deserialize;

#[derive(Deserialize)]
pub struct HistoryQuery {
    limit: Option<usize>,
}

pub async fn health() -> impl IntoResponse {
    (StatusCode::OK, Json(json!({ "status": "healthy" })))
}

pub async fn get_latest_data(
    State(collector): State<Arc<RwLock<DataCollector>>>,
) -> impl IntoResponse {
    let collector = collector.read().await;
    match collector.get_latest_data() {
        Some(data) => (StatusCode::OK, Json(serde_json::to_value(data).unwrap_or(serde_json::Value::Null))).into_response(),
        None => StatusCode::NO_CONTENT.into_response(),
    }
}

pub async fn get_history(
    State(collector): State<Arc<RwLock<DataCollector>>>,
    Query(query): Query<HistoryQuery>,
) -> impl IntoResponse {
    let collector = collector.read().await;
    let limit = query.limit.unwrap_or(100);
    let history = collector.get_history(limit);
    
    (StatusCode::OK, Json(history))
}

pub async fn get_stats(
    State(collector): State<Arc<RwLock<DataCollector>>>,
) -> impl IntoResponse {
    let collector = collector.read().await;
    let stats = collector.get_aggregated_stats();
    
    (StatusCode::OK, Json(stats))
}

pub async fn get_status(
    State(collector): State<Arc<RwLock<DataCollector>>>,
) -> impl IntoResponse {
    let collector = collector.read().await;
    let status = collector.get_status();
    
    (StatusCode::OK, Json(status))
}

// ===== NEW ENDPOINT HANDLERS =====

pub async fn get_voice_data(
    State(collector): State<Arc<RwLock<DataCollector>>>,
) -> impl IntoResponse {
    let collector = collector.read().await;
    match collector.get_latest_data() {
        Some(data) => {
            match data.voice_data {
                Some(voice) => (StatusCode::OK, Json(voice)).into_response(),
                None => (StatusCode::NO_CONTENT, Json(json!({"message": "Voice data not enabled or unavailable"}))).into_response(),
            }
        }
        None => StatusCode::NOT_FOUND.into_response(),
    }
}

pub async fn get_camera_data(
    State(collector): State<Arc<RwLock<DataCollector>>>,
) -> impl IntoResponse {
    let collector = collector.read().await;
    match collector.get_latest_data() {
        Some(data) => {
            match data.camera_data {
                Some(camera) => (StatusCode::OK, Json(camera)).into_response(),
                None => (StatusCode::NO_CONTENT, Json(json!({"message": "Camera data not enabled or unavailable"}))).into_response(),
            }
        }
        None => StatusCode::NOT_FOUND.into_response(),
    }
}

pub async fn get_keystroke_dynamics(
    State(collector): State<Arc<RwLock<DataCollector>>>,
) -> impl IntoResponse {
    let collector = collector.read().await;
    match collector.get_latest_data() {
        Some(data) => {
            match data.keystroke_dynamics {
                Some(keystrokes) => (StatusCode::OK, Json(keystrokes)).into_response(),
                None => (StatusCode::NO_CONTENT, Json(json!({"message": "Keystroke monitoring not enabled"}))).into_response(),
            }
        }
        None => StatusCode::NOT_FOUND.into_response(),
    }
}

pub async fn get_screen_interactions(
    State(collector): State<Arc<RwLock<DataCollector>>>,
) -> impl IntoResponse {
    let collector = collector.read().await;
    match collector.get_latest_data() {
        Some(data) => {
            match data.screen_interactions {
                Some(screen) => (StatusCode::OK, Json(screen)).into_response(),
                None => (StatusCode::NO_CONTENT, Json(json!({"message": "Screen interaction data unavailable"}))).into_response(),
            }
        }
        None => StatusCode::NOT_FOUND.into_response(),
    }
}

pub async fn get_file_metadata(
    State(collector): State<Arc<RwLock<DataCollector>>>,
) -> impl IntoResponse {
    let collector = collector.read().await;
    match collector.get_latest_data() {
        Some(data) => {
            match data.file_metadata {
                Some(files) => (StatusCode::OK, Json(files)).into_response(),
                None => (StatusCode::NO_CONTENT, Json(json!({"message": "File monitoring not enabled"}))).into_response(),
            }
        }
        None => StatusCode::NOT_FOUND.into_response(),
    }
}

pub async fn get_system_events(
    State(collector): State<Arc<RwLock<DataCollector>>>,
) -> impl IntoResponse {
    let collector = collector.read().await;
    match collector.get_latest_data() {
        Some(data) => {
            match data.system_events {
                Some(events) => (StatusCode::OK, Json(events)).into_response(),
                None => (StatusCode::NO_CONTENT, Json(json!({"message": "System events unavailable"}))).into_response(),
            }
        }
        None => StatusCode::NOT_FOUND.into_response(),
    }
}

pub async fn get_mouse_dynamics(
    State(collector): State<Arc<RwLock<DataCollector>>>,
) -> impl IntoResponse {
    let collector = collector.read().await;
    match collector.get_latest_data() {
        Some(data) => {
            match data.mouse_dynamics {
                Some(mouse) => (StatusCode::OK, Json(mouse)).into_response(),
                None => (StatusCode::NO_CONTENT, Json(json!({"message": "Mouse dynamics data unavailable"}))).into_response(),
            }
        }
        None => StatusCode::NOT_FOUND.into_response(),
    }
}

pub async fn get_network_metadata(
    State(collector): State<Arc<RwLock<DataCollector>>>,
) -> impl IntoResponse {
    let collector = collector.read().await;
    match collector.get_latest_data() {
        Some(data) => {
            match data.network_activity_metadata {
                Some(network) => (StatusCode::OK, Json(network)).into_response(),
                None => (StatusCode::NO_CONTENT, Json(json!({"message": "Network metadata unavailable"}))).into_response(),
            }
        }
        None => StatusCode::NOT_FOUND.into_response(),
    }
}

// Control endpoints for enabling/disabling collection modules
pub async fn enable_voice(
    State(collector): State<Arc<RwLock<DataCollector>>>,
) -> impl IntoResponse {
    let mut collector = collector.write().await;
    collector.enable_voice();
    (StatusCode::OK, Json(json!({"status": "voice_enabled"})))
}

pub async fn disable_voice(
    State(collector): State<Arc<RwLock<DataCollector>>>,
) -> impl IntoResponse {
    let mut collector = collector.write().await;
    collector.disable_voice();
    (StatusCode::OK, Json(json!({"status": "voice_disabled"})))
}

pub async fn enable_camera(
    State(collector): State<Arc<RwLock<DataCollector>>>,
) -> impl IntoResponse {
    let mut collector = collector.write().await;
    collector.enable_camera();
    (StatusCode::OK, Json(json!({"status": "camera_enabled"})))
}

pub async fn disable_camera(
    State(collector): State<Arc<RwLock<DataCollector>>>,
) -> impl IntoResponse {
    let mut collector = collector.write().await;
    collector.disable_camera();
    (StatusCode::OK, Json(json!({"status": "camera_disabled"})))
}

pub async fn enable_keystroke(
    State(collector): State<Arc<RwLock<DataCollector>>>,
) -> impl IntoResponse {
    let mut collector = collector.write().await;
    collector.enable_keystroke();
    (StatusCode::OK, Json(json!({"status": "keystroke_enabled"})))
}

pub async fn disable_keystroke(
    State(collector): State<Arc<RwLock<DataCollector>>>,
) -> impl IntoResponse {
    let mut collector = collector.write().await;
    collector.disable_keystroke();
    (StatusCode::OK, Json(json!({"status": "keystroke_disabled"})))
}

pub async fn enable_file_monitoring(
    State(collector): State<Arc<RwLock<DataCollector>>>,
) -> impl IntoResponse {
    let mut collector = collector.write().await;
    collector.enable_file_monitoring();
    (StatusCode::OK, Json(json!({"status": "file_monitoring_enabled"})))
}

pub async fn disable_file_monitoring(
    State(collector): State<Arc<RwLock<DataCollector>>>,
) -> impl IntoResponse {
    let mut collector = collector.write().await;
    collector.disable_file_monitoring();
    (StatusCode::OK, Json(json!({"status": "file_monitoring_disabled"})))
}
