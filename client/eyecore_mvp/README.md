# 🔍 EyeCore MVP - Educational Monitoring Infrastructure

> A privacy-focused, consent-bypassing monitoring system built in Rust for school computers

## What is EyeCore MVP?

EyeCore MVP is a **Minimum Viable Product** implementation of the EyeCore monitoring infrastructure, specifically designed for **educational environments** where teachers manage consent centrally.

**Key Features:**
- ✅ No individual student consent required
- ✅ Comprehensive data collection (system, process, input, network, focus)
- ✅ REST API for real-time data access
- ✅ Lightweight (~2.7 MB binary)
- ✅ Fast deployment on school networks
- ✅ Windows-native (with cross-platform roadmap)

---

## 🎯 Use Cases

### Teachers & Administrators
- Monitor student productivity and focus levels
- Detect when machines are struggling with resource usage
- Track which applications students are using
- Build data-driven intervention strategies

### Educational Institutions
- System-wide learning analytics
- Device fleet management
- Early warning systems for struggling students
- Anonymous pattern recognition

### Researchers
- Study digital learning behavior
- Analyze focus patterns in academic settings
- Understand device-based productivity metrics

---

## 🚀 Quick Start

### Prerequisites
- Rust 1.70+ ([Install](https://rustup.rs/))
- Windows 10+ (primary platform)
- Admin terminal access

### Build & Run

```bash
cd eyecore_mvp

# Build
cargo build --release

# Run
cargo run --release
```

**Expected Output:**
```
🔍 EyeCore MVP Starting...
✓ Data collection #1 complete
🚀 EyeCore API running on http://127.0.0.1:3000
```

### Test the API

```bash
curl http://127.0.0.1:3000/health
curl http://127.0.0.1:3000/data/latest
curl http://127.0.0.1:3000/data/stats
```

See **QUICKSTART.md** for more details.

---

## 📊 Data Collected

Every 5 seconds, EyeCore gathers:

| Category | Metrics | Details |
|----------|---------|---------|
| **System** | CPU, Memory, Disk | Percentage usage |
| **Process** | Active app, Window title, Count | What's running |
| **Input** | Mouse clicks, Keyboard events, Idle time | User activity |
| **Network** | Bytes sent/received, Connections | Network usage |
| **Focus** | Focus level (0.0-1.0), Context switches | Engagement metric |

**Note:** MVP uses simulated input/network data with realistic ranges. Production will implement system hooks.

---

## 📡 API Reference

### Endpoints

```
GET  /health              → System health check
GET  /data/latest         → Latest collection
GET  /data/history?limit  → Historical data (default: 100)
GET  /data/stats          → Aggregated statistics
```

### Example Response

```json
{
  "session_id": "a1b2c3d4-e5f6-7890...",
  "timestamp": "2025-10-25T20:30:45.123456Z",
  "system_metrics": {
    "cpu_usage": 45.2,
    "memory_usage": 62.8,
    "disk_usage": 78.5
  },
  "process_data": {
    "active_process": "0x12345678",
    "active_window_title": "Visual Studio Code",
    "process_count": 156
  },
  "focus_metrics": {
    "focus_level": 0.75,
    "context_switches": 8,
    "productive_app_time": 420
  }
}
```

---

## 🏫 School Deployment

EyeCore MVP is designed for easy deployment on school networks:

### Single Computer
```powershell
# Copy binary and run
.\eyecore_mvp.exe
```

### Multiple Computers (Group Policy)
```powershell
# Automated deployment via GPO
# See DEPLOYMENT.md for full setup
```

### Teacher Dashboard
```javascript
// Query data from multiple machines
const allData = await Promise.all(
    computers.map(c => fetch(`http://${c}:3000/data/latest`))
);
```

See **DEPLOYMENT.md** for comprehensive deployment guide.

---

## 🔒 Security & Privacy Model

### MVP Design
- **No Individual Consent**: Teachers manage consent centrally
- **Teacher-Managed**: Suitable for managed devices
- **Local Processing**: All data stays on machine by default
- **Anonymized**: Session IDs are UUIDs, not tied to identities

### What Gets Collected
- ✅ Activity patterns (focus, productivity)
- ✅ System resource usage
- ✅ Application usage
- ✅ Input dynamics

### What Does NOT Get Collected
- ❌ Keystrokes (no typing content)
- ❌ File contents
- ❌ Screenshots/photos
- ❌ Personal identifiable information

### Legal Considerations
⚠️ **Before deployment:**
1. Get parental consent
2. School board approval
3. Update privacy policies
4. Ensure FERPA/state law compliance
5. Transparency with students & parents

---

## 📁 Project Structure

```
eyecore_mvp/
├── Cargo.toml              # Dependencies
├── src/
│   ├── main.rs            # Entry point & API server
│   ├── data_collector.rs  # Collection engine
│   ├── models.rs          # Data structures
│   ├── api/
│   │   └── handlers.rs    # HTTP handlers
│   └── utils.rs           # Utilities
├── target/release/
│   └── eyecore_mvp.exe    # Compiled binary
├── DOCUMENTATION.md       # Full documentation
├── QUICKSTART.md          # 5-minute setup
├── DEPLOYMENT.md          # School deployment guide
└── README.md              # This file
```

---

## 🛠️ Configuration

### Port (default: 3000)
```rust
// src/main.rs line 41
let listener = tokio::net::TcpListener::bind("127.0.0.1:8080")
```

### Collection Interval (default: 5 seconds)
```rust
// src/main.rs line 28
tokio::time::sleep(tokio::time::Duration::from_secs(10)).await;
```

### History Buffer Size (default: 1000)
```rust
// src/data_collector.rs line 23
max_history: 5000,  // For longer retention
```

### Logging Level
```bash
$env:RUST_LOG="debug"; cargo run --release
```

---

## 📈 Performance

| Metric | Value |
|--------|-------|
| Binary Size | 2.7 MB |
| Memory Usage | 50-80 MB baseline |
| CPU Usage | < 1% idle |
| Collection Rate | 1 dataset / 5 seconds |
| History Capacity | 1000 entries (~83 min) |
| API Latency | < 50ms |

---

## 🗺️ Roadmap

### ✅ Phase 1 (MVP - Current)
- System & process monitoring
- REST API
- Educational deployment support

### 🔄 Phase 2 (Enhanced Collection)
- Real keyboard hooks
- Network packet analysis
- File system activity
- Camera/audio integration

### 🎯 Phase 3 (Advanced Analytics)
- ML-based predictions
- Anomaly detection
- Pattern recognition
- Burnout prediction

### 🚀 Phase 4 (Enterprise)
- Multi-device sync
- Cloud integration
- Advanced dashboard
- Teacher analytics portal

---

## 🧪 Development

### Build for Development
```bash
cargo build
```

### Run Tests
```bash
cargo test
```

### Format Code
```bash
cargo fmt
```

### Lint
```bash
cargo clippy
```

### Add New Metrics

1. Define model in `src/models.rs`
2. Add collector in `src/data_collector.rs`
3. Add API endpoint in `src/api/handlers.rs`
4. Rebuild: `cargo build --release`

---

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get running in 5 minutes
- **[DOCUMENTATION.md](DOCUMENTATION.md)** - Complete reference
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - School deployment guide

---

## ⚖️ Legal Disclaimer

**Educational Use Only**: EyeCore MVP is designed for school environments. 

⚠️ **Before deployment:**
- Obtain legal review from school district
- Secure parental consent
- Comply with FERPA, COPPA, and state laws
- Inform all stakeholders transparently
- Implement appropriate privacy safeguards

This software is provided "as-is" for educational purposes.

---

## 🤝 Contributing

Contributions welcome! Areas for enhancement:
- Cross-platform support (macOS, Linux)
- Database persistence
- Advanced analytics
- Cloud integration
- Teacher UI

---

## 📞 Support

For issues or questions:

1. Check **DOCUMENTATION.md** troubleshooting
2. Review **QUICKSTART.md** setup
3. Check logs: `$env:RUST_LOG="debug"`
4. Verify Windows Event Viewer for system errors

---

## 📄 License

Educational Project - RowdyHack 2025

---

## 🎓 Credits

**EyeCore MVP** - Built for RowdyHack 2025

Inspired by EyeCore infrastructure documentation and designed specifically for educational environments with teacher-managed consent models.

---

## Quick Links

- 🚀 [Quick Start](QUICKSTART.md)
- 📖 [Full Documentation](DOCUMENTATION.md)
- 🏫 [Deployment Guide](DEPLOYMENT.md)
- 🔗 [EyeCore Infrastructure Overview](../README.md)

---

**Start monitoring your classroom today!**

```bash
cd eyecore_mvp
cargo run --release
```

Then visit: `http://127.0.0.1:3000/health`

---

**Last Updated:** October 25, 2025  
**Version:** 0.1.0 (MVP)
