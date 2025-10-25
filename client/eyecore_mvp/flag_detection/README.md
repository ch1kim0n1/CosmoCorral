# Flag Detection System

A real-time anomaly detection system that monitors EyeCore data and flags suspicious behavior, performance issues, health concerns, and productivity alerts.

## Overview

The Flag Detection system runs independently from EyeCore and monitors the `data/timeslots` directory for new data files. When new data appears, it analyzes it in real-time and creates flag entries in `data/flags` for any detected anomalies.

## Features

### Detection Categories

1. **System Anomalies**
   - High CPU usage (>90%)
   - High memory usage (>85%)
   - Excessive bandwidth usage
   - High network packet loss

2. **Behavior Anomalies**
   - No user input detected
   - Erratic mouse movements
   - Unusual activity patterns

3. **Performance Issues**
   - Resource bottlenecks
   - Network connectivity problems
   - System degradation

4. **Health Concerns**
   - High stress indicators (from keystroke/voice analysis)
   - Fatigue detection (from typing/mouse patterns)
   - Poor posture (from camera data)
   - Negative emotional states (from voice/camera)

5. **Productivity Alerts**
   - Prolonged idle time (>5 minutes)
   - Low focus levels (<0.3)
   - Excessive context switching
   - High workflow friction

6. **Security Concerns**
   - Suspicious network activity
   - Unusual system behavior

## Installation

```bash
cd flag_detection
cargo build --release
```

## Usage

### Running the Flag Detector

```bash
# Set environment variables if needed
export RUST_LOG=info

# Run the detector
cargo run --release
```

The system will:
1. Create the `../data/flags` directory if it doesn't exist
2. Watch `../data/timeslots` for new EyeCore data files
3. Analyze each file in real-time
4. Save detected flags as individual JSON files in `../data/flags`

### Flag File Format

Each flag is saved as a JSON file with the following structure:

```json
{
  "id": "uuid-v4",
  "timestamp": "2025-10-25T21:30:00Z",
  "session_id": "eyecore-session-id",
  "flag_type": "HealthConcern",
  "severity": "Medium",
  "title": "High Stress Detected",
  "description": "Keystroke patterns indicate stress level of 0.82",
  "data_source": "keystroke_dynamics",
  "metrics": {
    "stress_indicator": 0.82,
    "typing_speed_wpm": 85.3,
    "error_correction_rate": 0.12
  },
  "confidence": 0.75
}
```

## Configuration

Thresholds can be adjusted in `src/detector.rs`:

```rust
FlagDetector {
    cpu_threshold: 90.0,       // CPU usage > 90%
    memory_threshold: 85.0,    // Memory usage > 85%
    idle_threshold: 300,       // Idle > 5 minutes
    focus_threshold: 0.3,      // Focus < 0.3
    stress_threshold: 0.7,     // Stress > 0.7
    fatigue_threshold: 0.8,    // Fatigue > 0.8
}
```

## Architecture

### Components

- **main.rs**: File watcher and orchestration
- **detector.rs**: Anomaly detection logic
- **models.rs**: Data structures for EyeCore data and flags
- **flag_storage.rs**: Flag persistence

### Data Flow

```
EyeCore → data/timeslots/*.json
    ↓
File Watcher (notify)
    ↓
FlagDetector (analyze_data)
    ↓
FlagStorage (save_flag)
    ↓
data/flags/flag_*.json
```

## Integration with EyeCore

The flag detection system reads from the same `data` directory that EyeCore writes to:

```
data/
├── timeslots/          # EyeCore writes here
├── raw_audio/          # EyeCore writes here
├── transcriptions/     # EyeCore writes here
├── anomalies/          # EyeCore writes here
└── flags/              # Flag Detection writes here
```

## Real-Time Monitoring

The system uses the `notify` crate to watch for file system events, ensuring near-instant detection of new data files and rapid flag generation.

## Extending Detection Logic

To add new detection rules:

1. Open `src/detector.rs`
2. Add a new `check_*` method
3. Call it from `analyze_data()`
4. Define appropriate thresholds and flag types

Example:

```rust
fn check_custom_metric(&self, data: &CustomData, session_id: &str) -> Vec<Flag> {
    let mut flags = Vec::new();
    
    if data.custom_value > threshold {
        flags.push(Flag {
            // ... flag definition
        });
    }
    
    flags
}
```

## Viewing Flags

All flags are stored as individual JSON files in `data/flags/`. You can:

- Read them directly
- Parse them with any JSON tool
- Build a dashboard to visualize them
- Query them programmatically using `FlagStorage::load_all_flags()`

## Performance

- **Latency**: <100ms from data file creation to flag generation
- **Throughput**: Can process hundreds of data files per second
- **Resource Usage**: Minimal CPU/memory footprint
- **Scalability**: Handles continuous 24/7 monitoring

## Logging

Set log level with `RUST_LOG`:

```bash
RUST_LOG=debug cargo run    # Verbose logging
RUST_LOG=info cargo run     # Standard logging
RUST_LOG=warn cargo run     # Warnings only
```

## Troubleshooting

### "Data directory does not exist"

Make sure EyeCore is running and has created the `data/timeslots` directory.

### No flags being generated

- Check that EyeCore is actively collecting data
- Verify thresholds aren't too strict
- Enable debug logging to see analysis details

### Permission errors

Ensure the flag_detection program has write access to the `data/flags` directory.
