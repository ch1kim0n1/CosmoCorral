use tokio_tungstenite::{connect_async, tungstenite::Message};
use futures_util::{SinkExt, StreamExt};
use serde_json::json;
use log::{info, error, warn};
use std::sync::Arc;
use tokio::sync::RwLock;
use tokio::time::{sleep, Duration};

use crate::models::EyeCoreData;

const SERVER_URL: &str = "ws://localhost:8765";
const RECONNECT_DELAY: Duration = Duration::from_secs(5);

pub struct WebSocketClient {
    server_url: String,
    device_id: String,
    access_token: Option<String>,
}

impl WebSocketClient {
    pub fn new(device_id: String) -> Self {
        Self {
            server_url: SERVER_URL.to_string(),
            device_id,
            access_token: None,
        }
    }

    /// Start the WebSocket client in a background task
    pub async fn start(
        self: Arc<Self>,
        data_receiver: Arc<RwLock<Option<EyeCoreData>>>,
    ) {
        tokio::spawn(async move {
            loop {
                match self.connect_and_run(Arc::clone(&data_receiver)).await {
                    Ok(_) => {
                        info!("WebSocket connection closed normally");
                    }
                    Err(e) => {
                        error!("WebSocket error: {}. Reconnecting in {:?}...", e, RECONNECT_DELAY);
                    }
                }
                sleep(RECONNECT_DELAY).await;
            }
        });
    }

    async fn connect_and_run(
        &self,
        data_receiver: Arc<RwLock<Option<EyeCoreData>>>,
    ) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        info!("🔌 Connecting to server at {}...", self.server_url);
        
        let (ws_stream, _) = connect_async(&self.server_url).await?;
        info!("✅ Connected to server!");

        let (mut write, mut read) = ws_stream.split();

        // First, create a device if we don't have an access code
        // For now, we'll skip authentication and send directly
        // In production, you'd need to get an access_code from the teacher
        
        info!("⚠️  No authentication - sending data without token");
        info!("   To properly authenticate:");
        info!("   1. Teacher creates device via dashboard/API");
        info!("   2. Student uses access_code to authenticate");
        info!("   3. Server returns token for data packages");

        // Handle incoming messages
        let read_handle = tokio::spawn(async move {
            while let Some(msg) = read.next().await {
                match msg {
                    Ok(Message::Text(text)) => {
                        if let Ok(response) = serde_json::from_str::<serde_json::Value>(&text) {
                            info!("📥 Server response: {}", response);
                        }
                    }
                    Ok(Message::Close(_)) => {
                        info!("Server closed connection");
                        break;
                    }
                    Err(e) => {
                        error!("Error reading message: {}", e);
                        break;
                    }
                    _ => {}
                }
            }
        });

        // Send data periodically
        let mut interval = tokio::time::interval(Duration::from_secs(5));
        loop {
            interval.tick().await;

            // Get the latest collected data
            let data_guard = data_receiver.read().await;
            if let Some(data) = data_guard.as_ref() {
                // Send the EyeCoreData directly as the "data" field
                // The server's pipeline expects the full activity package
                let package = json!({
                    "method": "Package",
                    "data": data  // Send the full EyeCoreData object
                });

                match write.send(Message::Text(package.to_string())).await {
                    Ok(_) => {
                        info!("📤 Sent data package to server");
                    }
                    Err(e) => {
                        error!("Failed to send data: {}", e);
                        break;
                    }
                }
            } else {
                warn!("No data available to send yet");
            }

            // Check if read task has finished (connection closed)
            if read_handle.is_finished() {
                break;
            }
        }

        Ok(())
    }
}
