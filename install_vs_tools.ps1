$ErrorActionPreference = "Stop"

function Write-Status($Message) {
    Write-Host "➡️ $Message" -ForegroundColor Cyan
}

function Write-Success($Message) {
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error($Message) {
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Show-Spinner($Message) {
    $spinChars = "⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"
    $i = 0

    Write-Host "`r$Message " -NoNewline
    while (Get-Process "vs_installer" -ErrorAction SilentlyContinue) {
        Write-Host "`r$Message $($spinChars[$i])" -NoNewline
        Start-Sleep -Milliseconds 100
        $i = ($i + 1) % $spinChars.Length
    }
    Write-Host "`r$Message Done!" -ForegroundColor Green
}

# Download VS Build Tools
Write-Status "Downloading Visual Studio Build Tools..."
$Url = "https://aka.ms/vs/17/release/vs_buildtools.exe"
$Installer = "$env:TEMP\vs_buildtools.exe"

try {
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $Url -OutFile $Installer
    Write-Success "Download complete!"
} catch {
    Write-Error "Failed to download VS Build Tools: $_"
    exit 1
}

# Install Build Tools
Write-Status "Installing VS Build Tools (this may take 10-15 minutes)..."
$Arguments = @(
    "--quiet",
    "--wait",
    "--norestart",
    "--nocache",
    "--installPath", "$env:ProgramFiles\Microsoft Visual Studio\2022\BuildTools",
    "--add", "Microsoft.VisualStudio.Workload.VCTools",
    "--add", "Microsoft.VisualStudio.Component.Windows10SDK",
    "--includeRecommended"
)

try {
    $process = Start-Process -FilePath $Installer -ArgumentList $Arguments -PassThru
    Show-Spinner "Installing Visual Studio Build Tools"

    if ($process.ExitCode -eq 0 -or $process.ExitCode -eq 3010) {
        Write-Success "VS Build Tools installed successfully!"
    } else {
        Write-Error "Installation failed with exit code: $($process.ExitCode)"
        exit 1
    }
} catch {
    Write-Error "Failed to install VS Build Tools: $_"
    exit 1
} finally {
    Remove-Item $Installer -Force -ErrorAction SilentlyContinue
}

Write-Host "`nInstallation completed! You can now run .\build.ps1" -ForegroundColor Green