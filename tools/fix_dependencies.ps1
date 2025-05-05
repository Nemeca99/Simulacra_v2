$ErrorActionPreference = "Stop"

# Required packages
$packages = @(
    "pytest",
    "pytest-asyncio",
    "pytest-benchmark",
    "memory-profiler",
    "orjson",
    "aiofiles",
    "numpy",
    "cython"
)

Write-Host "Installing required packages..." -ForegroundColor Cyan
foreach ($package in $packages) {
    Write-Host "Installing $package..." -ForegroundColor Yellow
    python -m pip install --upgrade $package
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install $package" -ForegroundColor Red
        exit 1
    }
}

Write-Host "All dependencies installed successfully!" -ForegroundColor Green