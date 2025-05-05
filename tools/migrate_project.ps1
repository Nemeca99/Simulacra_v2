$ErrorActionPreference = "Stop"

# Colorful output functions
function Write-Status($Message) { Write-Host "➡️ $Message" -ForegroundColor Cyan }
function Write-Success($Message) { Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Error($Message) { Write-Host "❌ $Message" -ForegroundColor Red }

# Project structure definition
$ProjectStructure = @{
    "src/simulacra/core" = @{
        Files = @{
            "stats.pyx" = "modules/stats.py"
            "mutations.pyx" = "modules/mutations.py"
            "__init__.py" = $null
        }
    }
    "src/simulacra/systems" = @{
        Files = @{
            "combat.py" = "modules/combat.py"
            "economy.py" = "modules/economy.py"
            "__init__.py" = $null
        }
    }
    "src/simulacra/ui" = @{
        Files = @{
            "hud.py" = "modules/hud.py"
            "__init__.py" = $null
        }
    }
    "tests/unit" = @{}
    "tests/benchmarks" = @{
        Files = @{
            "test_core_benchmarks.py" = "tests/benchmarks/test_core_benchmarks.py"
        }
    }
    "tools" = @{
        Files = @{
            "build.ps1" = "build.ps1"
            "cleanup.ps1" = "tools/cleanup.ps1"
        }
    }
    "docs" = @{}
    "data" = @{
        Files = @{
            ".gitkeep" = $null
        }
    }
}

# Create project structure
Write-Status "Creating project structure..."
foreach ($dir in $ProjectStructure.Keys) {
    New-Item -Path $dir -ItemType Directory -Force | Out-Null
    Write-Host "  Created: $dir"
}

# Move/Create files
Write-Status "Moving files to new structure..."
foreach ($dir in $ProjectStructure.Keys) {
    $files = $ProjectStructure[$dir].Files
    if ($files) {
        foreach ($file in $files.Keys) {
            $destination = Join-Path $dir $file
            $source = $files[$file]

            if ($source -and (Test-Path $source)) {
                # Move existing file
                Move-Item -Path $source -Destination $destination -Force
                Write-Host "  Moved: $source -> $destination"
            } elseif (-not (Test-Path $destination)) {
                # Create empty file
                New-Item -Path $destination -ItemType File -Force | Out-Null
                Write-Host "  Created: $destination"
            }
        }
    }
}

# Create .vscode settings
Write-Status "Creating VS Code configuration..."
$VsCodePath = ".vscode"
New-Item -Path $VsCodePath -ItemType Directory -Force | Out-Null

# Create settings.json
$Settings = @{
    "python.analysis.extraPaths" = @("src")
    "python.analysis.typeCheckingMode" = "basic"
    "python.testing.pytestEnabled" = $true
    "python.testing.unittestEnabled" = $false
    "python.testing.pytestArgs" = @("tests")
    "editor.formatOnSave" = $true
    "files.exclude" = @{
        "**/__pycache__" = $true
        "**/*.pyc" = $true
        "**/*.pyd" = $true
        "build/" = $true
        ".pytest_cache/" = $true
    }
}

$Settings | ConvertTo-Json -Depth 10 | Set-Content (Join-Path $VsCodePath "settings.json")

Write-Success "Project structure migration complete!"
Write-Host "`nNext steps:" -ForegroundColor Magenta
Write-Host "1. Review moved files for any issues"
Write-Host "2. Update import statements in Python files"
Write-Host "3. Run build script: .\tools\build.ps1"