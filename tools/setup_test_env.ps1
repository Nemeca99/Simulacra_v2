$ErrorActionPreference = "Stop"

function Write-Status($Message) { Write-Host "➡️ $Message" -ForegroundColor Cyan }
function Write-Success($Message) { Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Error($Message) { Write-Host "❌ $Message" -ForegroundColor Red }

# Install dependencies in development mode
Write-Status "Installing packages in development mode..."
python -m pip install -e .

# Install test dependencies
Write-Status "Installing test dependencies..."
$testDeps = @(
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-benchmark>=4.0.0",
    "memory-profiler>=0.61.0",
    "orjson>=3.9.0",
    "aiofiles>=23.2.0"
)

foreach ($dep in $testDeps) {
    Write-Host "Installing $dep..." -ForegroundColor Yellow
    python -m pip install $dep --upgrade
}

# Set up PYTHONPATH
Write-Status "Setting up PYTHONPATH..."
$projectRoot = (Get-Location).Path
$env:PYTHONPATH = "$projectRoot;$projectRoot\src;$projectRoot\modules"

Write-Success "Test environment setup complete!"