# Space Cowboy - Complete System Test Script
# Tests: Client (Student) -> Server -> Dashboard (Teacher)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SPACE COWBOY - SYSTEM TEST SUITE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"
$testsPassed = 0
$testsFailed = 0

# Test 1: Check Python
Write-Host "[TEST 1] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
    $testsPassed++
} catch {
    Write-Host "✗ Python not found" -ForegroundColor Red
    $testsFailed++
}

# Test 2: Check Rust/Cargo
Write-Host "[TEST 2] Checking Rust installation..." -ForegroundColor Yellow
try {
    $rustVersion = cargo --version 2>&1
    Write-Host "✓ Rust found: $rustVersion" -ForegroundColor Green
    $testsPassed++
} catch {
    Write-Host "✗ Rust/Cargo not found" -ForegroundColor Red
    $testsFailed++
}

# Test 3: Check Node.js
Write-Host "[TEST 3] Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js found: $nodeVersion" -ForegroundColor Green
    $testsPassed++
} catch {
    Write-Host "✗ Node.js not found" -ForegroundColor Red
    $testsFailed++
}

# Test 4: Check if client binary exists
Write-Host "[TEST 4] Checking client binary..." -ForegroundColor Yellow
$clientBinary = ".\client\eyecore_mvp\target\release\eyecore_mvp.exe"
if (Test-Path $clientBinary) {
    Write-Host "✓ Client binary exists" -ForegroundColor Green
    $testsPassed++
} else {
    Write-Host "✗ Client binary not found. Run: cd client/eyecore_mvp && cargo build --release" -ForegroundColor Red
    $testsFailed++
}

# Test 5: Check server dependencies
Write-Host "[TEST 5] Checking Python server dependencies..." -ForegroundColor Yellow
try {
    python -c "import websockets, peewee" 2>&1 | Out-Null
    Write-Host "✓ Basic server dependencies installed" -ForegroundColor Green
    $testsPassed++
} catch {
    Write-Host "⚠ Some server dependencies missing (websockets, peewee)" -ForegroundColor Yellow
    Write-Host "  Run: cd server; pip install websockets peewee" -ForegroundColor Yellow
    $testsFailed++
}

# Test 6: Check Gemini API availability
Write-Host "[TEST 6] Checking Gemini API configuration..." -ForegroundColor Yellow
try {
    python -c "import google.generativeai" 2>&1 | Out-Null
    Write-Host "✓ google-generativeai package installed" -ForegroundColor Green
    
    $geminiKey = $env:GEMINI_API_KEY
    if ($geminiKey -and $geminiKey -ne "" -and $geminiKey -ne "API_IS_NOT_PROVIDED") {
        Write-Host "✓ GEMINI_API_KEY is set" -ForegroundColor Green
    } else {
        Write-Host "⚠ GEMINI_API_KEY not set - will use fallback analysis" -ForegroundColor Yellow
        Write-Host "  Get free API key: https://aistudio.google.com/app/apikeys" -ForegroundColor Yellow
    }
    $testsPassed++
} catch {
    Write-Host "⚠ google-generativeai not installed - will use fallback analysis" -ForegroundColor Yellow
    Write-Host "  Run: pip install google-generativeai" -ForegroundColor Yellow
}

# Test 7: Check if ports are available
Write-Host "[TEST 7] Checking port availability..." -ForegroundColor Yellow
$port3000InUse = netstat -ano | Select-String ":3000" | Select-String "LISTENING"
$port8765InUse = netstat -ano | Select-String ":8765" | Select-String "LISTENING"

if (-not $port3000InUse) {
    Write-Host "✓ Port 3000 (client) is available" -ForegroundColor Green
    $testsPassed++
} else {
    Write-Host "✗ Port 3000 is in use" -ForegroundColor Red
    $testsFailed++
}

if (-not $port8765InUse) {
    Write-Host "✓ Port 8765 (server) is available" -ForegroundColor Green
    $testsPassed++
} else {
    Write-Host "✗ Port 8765 is in use" -ForegroundColor Red
    $testsFailed++
}

# Test 8: Check database
Write-Host "[TEST 8] Checking database..." -ForegroundColor Yellow
if (Test-Path ".\server\app.db") {
    Write-Host "✓ Database exists (server\app.db)" -ForegroundColor Green
    $testsPassed++
} else {
    Write-Host "⚠ Database not found. Run: cd server && python db_init.py" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TEST SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Passed: $testsPassed" -ForegroundColor Green
Write-Host "Failed/Warning: $testsFailed" -ForegroundColor $(if ($testsFailed -eq 0) { "Green" } else { "Yellow" })
Write-Host ""

if ($testsFailed -eq 0) {
    Write-Host "✓ All tests passed! System is ready." -ForegroundColor Green
    Write-Host ""
    Write-Host "To start the system:" -ForegroundColor Cyan
    Write-Host "  1. Server:    cd server; python main.py" -ForegroundColor White
    Write-Host "  2. Client:    cd client\eyecore_mvp; cargo run --release" -ForegroundColor White
    Write-Host "  3. Dashboard: cd dashboard; npm run dev" -ForegroundColor White
} else {
    Write-Host "⚠ Some components need attention. See messages above." -ForegroundColor Yellow
}
