# Check if GitHub CLI is installed
$ghPath = "${env:LOCALAPPDATA}\Programs\GitHub CLI"
$systemPath = [Environment]::GetEnvironmentVariable("Path", "Machine")

if (Test-Path $ghPath) {
    # Add to system PATH if not already present
    if ($systemPath -notlike "*GitHub CLI*") {
        [Environment]::SetEnvironmentVariable(
            "Path",
            "$systemPath;$ghPath",
            "Machine"
        )
        Write-Host "✅ Added GitHub CLI to PATH"
    } else {
        Write-Host "GitHub CLI already in PATH"
    }
} else {
    Write-Host "❌ GitHub CLI not found. Attempting reinstall..."
    # Reinstall GitHub CLI
    winget install GitHub.cli --force
}

# Refresh current session's PATH
$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine")

# Verify installation
try {
    $version = gh --version
    Write-Host "✅ GitHub CLI installed: $version"
} catch {
    Write-Host "❌ GitHub CLI still not accessible. Please restart your computer."
}