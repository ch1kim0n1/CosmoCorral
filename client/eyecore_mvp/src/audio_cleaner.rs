use log::{info, debug};
use serde_json::json;
use std::path::Path;

pub struct AudioCleaner;

impl AudioCleaner {
    /// Clean audio by removing silence, static, and inactivity segments
    pub async fn clean_audio_segment(
        audio_path: &Path,
        silence_threshold_db: f32,
        _min_speech_duration_ms: u32,
    ) -> Result<CleanedAudio, String> {
        info!("Starting audio cleaning for: {:?}", audio_path);

        // Read audio file
        let mut reader = hound::WavReader::open(audio_path).map_err(|e| format!("Failed to open WAV: {}", e))?;
        let spec = reader.spec();
        
        debug!(
            "Audio spec - Channels: {}, Sample rate: {}, Duration: {}ms",
            spec.channels,
            spec.sample_rate,
            (reader.len() / spec.sample_rate as u32) * 1000
        );

        // Convert to samples and analyze
        let samples = Self::read_samples(&mut reader).map_err(|e| format!("Failed to read samples: {}", e))?;
        
        // Detect voice activity
        let voice_segments = Self::detect_voice_activity(&samples, spec.sample_rate, silence_threshold_db).map_err(|e| format!("VAD failed: {}", e))?;
        
        // Remove silence and combine segments
        let cleaned_samples = Self::remove_silence(&samples, &voice_segments).map_err(|e| format!("Silence removal failed: {}", e))?;
        
        // Calculate statistics
        let original_duration_ms = (samples.len() as f32 / spec.sample_rate as f32) * 1000.0;
        let cleaned_duration_ms = (cleaned_samples.len() as f32 / spec.sample_rate as f32) * 1000.0;
        let compression_ratio = original_duration_ms / cleaned_duration_ms.max(1.0);

        info!(
            "✓ Audio cleaned: {:.1}ms -> {:.1}ms (compression ratio: {:.2}x)",
            original_duration_ms, cleaned_duration_ms, compression_ratio
        );

        Ok(CleanedAudio {
            samples: cleaned_samples,
            voice_segments,
            original_duration_ms: original_duration_ms as u32,
            cleaned_duration_ms: cleaned_duration_ms as u32,
            compression_ratio,
            spec,
        })
    }

    /// Detect voice activity in audio using energy-based VAD
    fn detect_voice_activity(
        samples: &[f32],
        sample_rate: u32,
        silence_threshold_db: f32,
    ) -> Result<Vec<(usize, usize)>, String> {
        let frame_size = (sample_rate as usize) / 100; // 10ms frames
        let mut segments = Vec::new();
        let mut in_speech = false;
        let mut segment_start = 0;

        // Convert dB threshold to linear amplitude
        let threshold_linear = 10f32.powf(silence_threshold_db / 20.0) * 0.001; // normalize

        for (i, chunk) in samples.chunks(frame_size).enumerate() {
            // Calculate energy of frame
            let energy: f32 = chunk.iter().map(|s| s * s).sum::<f32>() / chunk.len() as f32;
            let is_speech = energy.sqrt() > threshold_linear;

            if is_speech && !in_speech {
                segment_start = i * frame_size;
                in_speech = true;
            } else if !is_speech && in_speech {
                segments.push((segment_start, i * frame_size));
                in_speech = false;
            }
        }

        // Close last segment if still in speech
        if in_speech {
            segments.push((segment_start, samples.len()));
        }

        debug!("Found {} voice segments", segments.len());
        Ok(segments)
    }

    /// Remove silence segments and concatenate voice segments
    fn remove_silence(
        samples: &[f32],
        voice_segments: &[(usize, usize)],
    ) -> Result<Vec<f32>, String> {
        let mut cleaned = Vec::new();

        for (start, end) in voice_segments {
            if *start < samples.len() && *end <= samples.len() {
                cleaned.extend_from_slice(&samples[*start..*end]);
            }
        }

        debug!("Removed {} silence frames", samples.len() - cleaned.len());
        Ok(cleaned)
    }

    /// Remove static/noise segments
    pub async fn remove_static(
        audio: &[f32],
        noise_threshold: f32,
    ) -> Result<Vec<f32>, String> {
        let mut cleaned = Vec::new();
        let window_size = 512;

        for chunk in audio.chunks(window_size) {
            // Calculate spectral variance (simple noise detection)
            let mean = chunk.iter().sum::<f32>() / chunk.len() as f32;
            let variance = chunk
                .iter()
                .map(|x| (x - mean).powi(2))
                .sum::<f32>()
                / chunk.len() as f32;

            if variance > noise_threshold {
                cleaned.extend_from_slice(chunk);
            }
        }

        debug!("Removed {} static frames", audio.len() - cleaned.len());
        Ok(cleaned)
    }

    /// Detect inactivity periods (no meaningful audio)
    pub async fn detect_inactivity_segments(
        samples: &[f32],
        sample_rate: u32,
        min_activity_duration_ms: u32,
    ) -> Result<Vec<(u32, u32)>, String> {
        let frame_size = (sample_rate as usize) / 100;
        let mut inactivity_segments = Vec::new();
        let mut inactive_start = 0;
        let mut is_inactive = true;

        for (i, chunk) in samples.chunks(frame_size).enumerate() {
            let energy: f32 = chunk.iter().map(|s| s * s).sum();
            let has_activity = energy > 0.0001;

            if has_activity && is_inactive {
                let inactive_duration_ms = ((i * frame_size) - inactive_start) as u32 * 1000 / sample_rate;
                if inactive_duration_ms > min_activity_duration_ms {
                    inactivity_segments.push((inactive_start as u32, i as u32 * frame_size as u32));
                }
                is_inactive = false;
            } else if !has_activity && !is_inactive {
                inactive_start = i * frame_size;
                is_inactive = true;
            }
        }

        info!("Found {} inactivity segments", inactivity_segments.len());
        Ok(inactivity_segments)
    }

    /// Read audio samples from WAV file
    fn read_samples(reader: &mut hound::WavReader<std::io::BufReader<std::fs::File>>) -> Result<Vec<f32>, String> {
        let mut samples = Vec::new();
        let spec = reader.spec();

        match spec.bits_per_sample {
            16 => {
                for sample in reader.samples::<i16>() {
                    let s = sample.map_err(|e| format!("Sample read error: {}", e))? as f32 / 32768.0; // normalize to -1.0..1.0
                    samples.push(s);
                }
            }
            32 => {
                for sample in reader.samples::<i32>() {
                    let s = sample.map_err(|e| format!("Sample read error: {}", e))? as f32 / i32::MAX as f32;
                    samples.push(s);
                }
            }
            _ => {
                for sample in reader.samples::<i16>() {
                    let s = sample.map_err(|e| format!("Sample read error: {}", e))? as f32 / 32768.0;
                    samples.push(s);
                }
            }
        }

        Ok(samples)
    }

    /// Generate cleaning report
    pub fn generate_report(
        original_duration_ms: u32,
        cleaned_duration_ms: u32,
        voice_segments_count: usize,
        inactivity_segments_count: usize,
    ) -> serde_json::Value {
        let removed_duration_ms = original_duration_ms - cleaned_duration_ms;
        let efficiency = ((removed_duration_ms as f32 / original_duration_ms as f32) * 100.0) as u32;

        json!({
            "original_duration_ms": original_duration_ms,
            "cleaned_duration_ms": cleaned_duration_ms,
            "removed_duration_ms": removed_duration_ms,
            "efficiency_percent": efficiency,
            "voice_segments_found": voice_segments_count,
            "inactivity_segments_found": inactivity_segments_count,
            "status": "cleaned",
        })
    }
}

pub struct CleanedAudio {
    pub samples: Vec<f32>,
    pub voice_segments: Vec<(usize, usize)>,
    pub original_duration_ms: u32,
    pub cleaned_duration_ms: u32,
    pub compression_ratio: f32,
    pub spec: hound::WavSpec,
}

impl CleanedAudio {
    /// Save cleaned audio to new file
    pub async fn save(&self, output_path: &Path) -> Result<(), String> {
        let mut writer = hound::WavWriter::create(output_path, self.spec).map_err(|e| format!("Failed to create WAV: {}", e))?;

        for sample in &self.samples {
            let normalized = (*sample * 32767.0).clamp(-32768.0, 32767.0) as i16;
            writer.write_sample(normalized).map_err(|e| format!("Write sample error: {}", e))?;
        }

        writer.finalize().map_err(|e| format!("Finalize WAV error: {}", e))?;
        info!("✓ Cleaned audio saved to: {:?}", output_path);
        Ok(())
    }
}
