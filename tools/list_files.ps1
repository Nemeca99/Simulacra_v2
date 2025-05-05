function Write-FileContent {
    param(
        [string]$filePath,
        [int]$maxLines = 1000
    )

    Write-Host "`n=== File: $filePath ===" -ForegroundColor Cyan

    if (Test-Path $filePath) {
        $content = Get-Content $filePath -Raw
        if ($content) {
            Write-Host $content
        } else {
            Write-Host "(empty file)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "File not found!" -ForegroundColor Red
    }
    Write-Host "=== End of $filePath ===`n" -ForegroundColor Cyan
}

# Important project files to check
$filesToCheck = @(
    "src\simulacra\core\traits.py",
    "src\simulacra\core\game_types.py",
    "src\simulacra\core\__init__.py",
    "tests\unit\test_traits.py",
    "tests\unit\__init__.py",
    "setup.py",
    "pytest.ini",
    "modules\traits.py",
    "modules\game_types.py"
)

foreach ($file in $filesToCheck) {
    Write-FileContent $file
}