use log::{info, error, debug};
use serde_json::json;
use std::sync::Arc;
use tokio::sync::Mutex;
use cpal::traits::{HostTrait, DeviceTrait, StreamTrait};
use base64::{Engine as _, engine::general_purpose};

pub struct VoiceCollector {
    elevenlabs_api_key: String,
    client: reqwest::Client,
}

impl VoiceCollector {
    pub fn new(api_key: String) -> Self {
        VoiceCollector {
            elevenlabs_api_key: api_key,
            client: reqwest::Client::new(),
        }
    }

    /// Generate test audio WAV files
    pub async fn collect_audio_chunk(&self, duration_ms: u64) -> Result<Vec<u8>, String> {
        debug!("Generating audio for {} ms", duration_ms);
        
        // Generate synthetic WAV audio for testing
        let sample_rate = 16000; // 16kHz
        let channels = 1; // Mono
        let num_samples = (sample_rate as u64 * duration_ms) / 1000;
        
        // Generate PCM samples (sine wave as test data)
        let mut samples: Vec<i16> = Vec::new();
        for i in 0..num_samples {
            let t = i as f32 / sample_rate as f32;
            let frequency = 440.0; // 440 Hz tone
            let sample = ((t * frequency * 2.0 * std::f32::consts::PI).sin() * 0.3 * i16::MAX as f32) as i16;
            samples.push(sample);
        }
        
        // Encode to WAV format
        let mut wav_data = Vec::new();
        
        // WAV header
        wav_data.extend_from_slice(b"RIFF");
        let file_size = 36 + samples.len() * 2;
        wav_data.extend_from_slice(&(file_size as u32).to_le_bytes());
        wav_data.extend_from_slice(b"WAVE");
        
        // fmt subchunk
        wav_data.extend_from_slice(b"fmt ");
        wav_data.extend_from_slice(&16u32.to_le_bytes()); // Subchunk1Size
        wav_data.extend_from_slice(&1u16.to_le_bytes());   // AudioFormat
        wav_data.extend_from_slice(&(channels as u16).to_le_bytes());
        wav_data.extend_from_slice(&(sample_rate as u32).to_le_bytes());
        let byte_rate = sample_rate * channels * 2;
        wav_data.extend_from_slice(&(byte_rate as u32).to_le_bytes());
        wav_data.extend_from_slice(&(channels as u16 * 2).to_le_bytes());
        wav_data.extend_from_slice(&16u16.to_le_bytes());
        
        // data subchunk
        wav_data.extend_from_slice(b"data");
        wav_data.extend_from_slice(&(samples.len() * 2).to_le_bytes());
        
        // PCM samples
        for sample in samples {
            wav_data.extend_from_slice(&sample.to_le_bytes());
        }
        
        info!("✓ Generated {} bytes of WAV audio data", wav_data.len());
        Ok(wav_data)
    }

    /// Send audio to ElevenLabs for transcription and analysis
    pub async fn analyze_audio_with_elevenlabs(
        &self,
        audio_bytes: &[u8],
    ) -> Result<AudioAnalysis, String> {
        info!("Sending audio to ElevenLabs for analysis...");

        // Encode audio as base64
        let base64_audio = general_purpose::STANDARD.encode(audio_bytes);
        
        // Call ElevenLabs API for speech-to-text
        let transcription = self.transcribe_audio(&base64_audio).await
            .map_err(|e| format!("Transcription error: {}", e))?;
        
        // Analyze for anomalies
        let anomalies = self.detect_anomalies(&base64_audio).await
            .map_err(|e| format!("Anomaly detection error: {}", e))?;

        Ok(AudioAnalysis {
            transcription,
            anomalies,
            audio_length_ms: (audio_bytes.len() as f32 / 16.0) as u32, // rough estimate
            timestamp: chrono::Utc::now(),
        })
    }

    /// Transcribe audio using ElevenLabs Speech-to-Text
    async fn transcribe_audio(&self, base64_audio: &str) -> Result<String, String> {
        let url = "https://api.elevenlabs.io/v1/speech-to-text";

        let response = self
            .client
            .post(url)
            .header("Authorization", format!("Bearer {}", self.elevenlabs_api_key))
            .json(&json!({
                "audio": base64_audio,
                "language": "en",
            }))
            .send()
            .await
            .map_err(|e| format!("Request error: {}", e))?;

        if !response.status().is_success() {
            error!("ElevenLabs API error: {}", response.status());
            return Ok("Transcription unavailable".to_string());
        }

        let result: serde_json::Value = response.json().await
            .map_err(|e| format!("JSON parse error: {}", e))?;
        let text = result["text"]
            .as_str()
            .unwrap_or("Unable to transcribe")
            .to_string();

        info!("✓ Transcription complete: {} chars", text.len());
        Ok(text)
    }

    /// Detect audio anomalies: background noise, distortion, unusual sounds
    async fn detect_anomalies(&self, base64_audio: &str) -> Result<serde_json::Value, String> {
        let url = "https://api.elevenlabs.io/v1/audio-analysis";

        let response = self
            .client
            .post(url)
            .header("Authorization", format!("Bearer {}", self.elevenlabs_api_key))
            .json(&json!({
                "audio": base64_audio,
                "analysis_type": "anomaly_detection",
            }))
            .send()
            .await
            .map_err(|e| format!("Request error: {}", e))?;

        if !response.status().is_success() {
            return Ok(json!({
                "anomalies": [],
                "background_noise_level": 0.0,
                "distortion_detected": false,
            }));
        }

        let result: serde_json::Value = response.json().await
            .map_err(|e| format!("JSON parse error: {}", e))?;
        
        let anomalies = json!({
            "anomalies_detected": result["anomalies"].as_array().unwrap_or(&vec![]).len() > 0,
            "background_noise_level": result["background_noise_level"].as_f64().unwrap_or(0.0),
            "distortion_detected": result["distortion_detected"].as_bool().unwrap_or(false),
            "unusual_sounds": result["unusual_sounds"].as_array().unwrap_or(&vec![]).clone(),
            "breaks_in_speech": result["breaks_in_speech"].as_array().unwrap_or(&vec![]).clone(),
            "confidence_score": result["confidence"].as_f64().unwrap_or(0.0),
        });

        info!("✓ Anomaly detection complete");
        Ok(anomalies)
    }

    /// Detect specific sound patterns (simplified - for production use models)
    pub async fn detect_sound_patterns(&self, _audio_bytes: &[u8]) -> Result<SoundPatterns, String> {
        debug!("Analyzing sound patterns...");

        // In production, this would use ML models to detect:
        // - Keyboard typing sounds
        // - Phone ringing
        // - Background music
        // - Ambient noise patterns
        // - Speech stress indicators

        Ok(SoundPatterns {
            has_speech: true,
            has_keyboard: false,
            has_phone_ring: false,
            ambient_noise_level: 0.3,
            stress_indicators: vec![],
            confidence: 0.85,
        })
    }
}

#[derive(Clone, Debug)]
pub struct AudioAnalysis {
    pub transcription: String,
    pub anomalies: serde_json::Value,
    pub audio_length_ms: u32,
    pub timestamp: chrono::DateTime<chrono::Utc>,
}

#[derive(Clone, Debug, serde::Serialize, serde::Deserialize)]
pub struct SoundPatterns {
    pub has_speech: bool,
    pub has_keyboard: bool,
    pub has_phone_ring: bool,
    pub ambient_noise_level: f32,
    pub stress_indicators: Vec<String>,
    pub confidence: f32,
}

fn err_fn(err: cpal::StreamError) {
    error!("Stream error: {}", err);
}
