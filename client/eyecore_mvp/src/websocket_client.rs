use tokio_tungstenite::{connect_async, tungstenite::Message};
use futures_util::{SinkExt, StreamExt};
use serde_json::json;
use log::{info, error, warn};
use std::sync::Arc;
use std::env;
use tokio::sync::RwLock;
use tokio::time::{sleep, Duration};

use crate::models::EyeCoreData;

const SERVER_URL: &str = "ws://localhost:8765";
const RECONNECT_DELAY: Duration = Duration::from_secs(5);

pub struct WebSocketClient {
    server_url: String,
    device_id: String,
    access_token: Arc<RwLock<Option<String>>>,
}

impl WebSocketClient {
    pub fn new(device_id: String) -> Self {
        Self {
            server_url: SERVER_URL.to_string(),
            device_id,
            access_token: Arc::new(RwLock::new(None)),
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

        // Send authentication request
        let access_code = env::var("ACCESS_CODE").unwrap_or_else(|_| "W9RFCDJG36".to_string());

        let auth_payload = json!({
            "method": "Authenticate",
            "data": {
                "access_code": access_code
            }
        });

        if let Err(e) = write.send(Message::Text(auth_payload.to_string())).await {
            error!("Failed to send authentication payload: {}", e);
            return Err(Box::new(e));
        }
        info!("✅ Authentication request sent");

        // Wait for authentication response and extract token
        if let Some(Ok(Message::Text(text))) = read.next().await {
            if let Ok(response) = serde_json::from_str::<serde_json::Value>(&text) {
                info!("📥 Server response: {}", response);
                
                if response.get("status") == Some(&json!("success")) {
                    if let Some(token) = response.get("data").and_then(|d| d.get("token")).and_then(|t| t.as_str()) {
                        let mut token_lock = self.access_token.write().await;
                        *token_lock = Some(token.to_string());
                        info!("✅ Token received and stored: {}", token);
                    } else {
                        error!("Authentication response missing token.");
                    }
                } else {
                    error!("Authentication failed: {}", response);
                }
            }
        }

        // Clone the access_token Arc for the read task
        let access_token_clone = Arc::clone(&self.access_token);

        // Handle incoming messages in background
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
                // Convert data to JSON value so we can add token field
                let mut data_json = serde_json::to_value(data).unwrap();
                
                // Add token to the data object if we have one
                let token_guard = self.access_token.read().await;
                if let Some(ref token) = *token_guard {
                    data_json["token"] = json!(token);
                }
                drop(token_guard); // Release lock

                // Send the full package with data containing token
                let package = json!({
                    "method": "Package",
                    "data": data_json,
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
