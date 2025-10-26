# Space Cowboy - Quick System Test
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SPACE COWBOY - SYSTEM TEST" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test Python
Write-Host "[1] Python:" -NoNewline
try {
    $pythonVer = python --version 2>&1
    Write-Host " OK - $pythonVer" -ForegroundColor Green
} catch {
    Write-Host " MISSING" -ForegroundColor Red
}

# Test Rust
Write-Host "[2] Rust:" -NoNewline
try {
    $cargoVer = cargo --version 2>&1
    Write-Host " OK - $cargoVer" -ForegroundColor Green
} catch {
    Write-Host " MISSING" -ForegroundColor Red
}

# Test Node
Write-Host "[3] Node.js:" -NoNewline
try {
    $nodeVer = node --version 2>&1
    Write-Host " OK - $nodeVer" -ForegroundColor Green
} catch {
    Write-Host " MISSING" -ForegroundColor Red
}

# Test client binary
Write-Host "[4] Client Binary:" -NoNewline
if (Test-Path ".\client\eyecore_mvp\target\release\eyecore_mvp.exe") {
    Write-Host " OK" -ForegroundColor Green
} else {
    Write-Host " NOT BUILT (run: cd client/eyecore_mvp; cargo build --release)" -ForegroundColor Yellow
}

# Test ports
Write-Host "[5] Port 3000 (client):" -NoNewline
$port3000 = netstat -ano | Select-String ":3000" | Select-String "LISTENING"
if (-not $port3000) {
    Write-Host " Available" -ForegroundColor Green
} else {
    Write-Host " IN USE" -ForegroundColor Red
}

Write-Host "[6] Port 8765 (server):" -NoNewline
$port8765 = netstat -ano | Select-String ":8765" | Select-String "LISTENING"
if (-not $port8765) {
    Write-Host " Available" -ForegroundColor Green
} else {
    Write-Host " IN USE" -ForegroundColor Red
}

# Test database
Write-Host "[7] Database:" -NoNewline
if (Test-Path ".\server\app.db") {
    Write-Host " EXISTS" -ForegroundColor Green
} else {
    Write-Host " MISSING (run: cd server; python db_init.py)" -ForegroundColor Yellow
}

# Test dependencies
Write-Host "[8] Server Dependencies:" -NoNewline
try {
    python -c "import websockets, peewee" 2>&1 | Out-Null
    Write-Host " OK" -ForegroundColor Green
} catch {
    Write-Host " MISSING (run: cd server; pip install websockets peewee)" -ForegroundColor Yellow
}

Write-Host "[9] Gemini API:" -NoNewline
try {
    python -c "import google.generativeai" 2>&1 | Out-Null
    if ($env:GEMINI_API_KEY) {
        Write-Host " OK (API key set)" -ForegroundColor Green
    } else {
        Write-Host " OK (package installed, but no API key - using fallback)" -ForegroundColor Yellow
    }
} catch {
    Write-Host " NOT INSTALLED (will use fallback analysis)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "To start the system, open 3 terminals:" -ForegroundColor White
Write-Host " Terminal 1: cd server; python main.py" -ForegroundColor Cyan
Write-Host " Terminal 2: cd client\eyecore_mvp; cargo run --release" -ForegroundColor Cyan
Write-Host " Terminal 3: cd dashboard; npm run dev" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
