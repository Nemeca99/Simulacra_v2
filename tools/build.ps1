param(
    [switch]$Benchmark
)

$ErrorActionPreference = "Stop"

function Write-Status($Message) { Write-Host "➡️ $Message" -ForegroundColor Cyan }
function Write-Success($Message) { Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Error($Message) { Write-Host "❌ $Message" -ForegroundColor Red }

# Set up paths
Write-Status "Setting up Python paths..."
python setup_paths.py

# Run tests
Write-Status "Running tests..."
if ($Benchmark) {
    pytest tests\benchmark -v
} else {
    pytest tests\unit -v
}

if ($LASTEXITCODE -eq 0) {
    Write-Success "Tests passed!"
} else {
    Write-Error "Tests failed!"
    exit 1
}