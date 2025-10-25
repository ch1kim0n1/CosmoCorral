# EyeCore MVP - Quick Start Guide

## 🚀 Get Running in 5 Minutes

### 1. Build

```powershell
cd eyecore_mvp
cargo build --release
```

**Wait for:** `Finished 'release' profile`

### 2. Run

```powershell
cargo run --release
```

**See:** `🚀 EyeCore API running on http://127.0.0.1:3000`

### 3. Test Endpoints

Open a new terminal:

```powershell
# Health check
curl http://127.0.0.1:3000/health

# Get latest data
curl http://127.0.0.1:3000/data/latest

# Get stats
curl http://127.0.0.1:3000/data/stats

# Get history (last 50 entries)
curl "http://127.0.0.1:3000/data/history?limit=50"
```

---

## 📊 What You Get

EyeCore collects every 5 seconds:

✅ System metrics (CPU, Memory, Disk)  
✅ Process & window tracking  
✅ Input activity (mouse, keyboard)  
✅ Network metrics  
✅ Focus analysis  

All in JSON format, accessible via REST API.

---

## 🎓 For Teachers

**No student consent needed!**

- Teacher/admin deploys on school computers
- EyeCore starts automatically
- Data collected silently
- Query via API for insights

---

## 🔧 Common Tweaks

### Change port (default: 3000)

Edit `src/main.rs` line 41:
```rust
let listener = tokio::net::TcpListener::bind("127.0.0.1:8080")
```

Then rebuild:
```powershell
cargo build --release
```

### Change collection interval (default: 5 seconds)

Edit `src/main.rs` line 28:
```rust
tokio::time::sleep(tokio::time::Duration::from_secs(10)).await;
```

### Increase history buffer (default: 1000)

Edit `src/data_collector.rs` line 23:
```rust
max_history: 5000,
```

---

## 📚 Full Documentation

See **DOCUMENTATION.md** for:
- Complete API reference
- Data collection details
- Security & privacy info
- Troubleshooting
- Development guide

---

## ⚠️ MVP Notes

- **Input metrics** are simulated (realistic random values)
- **Windows-only** for active window tracking
- **Local API** only (no cloud sync)
- Requires **admin privileges** for full functionality

---

**Ready to deploy?** Start the server and query the `/health` endpoint!
