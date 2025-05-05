# Create directories if they don't exist
New-Item -Path "src\simulacra\core" -ItemType Directory -Force
New-Item -Path "tests\unit" -ItemType Directory -Force

# Create __init__.py files
New-Item -Path "src\simulacra\__init__.py" -ItemType File -Force
New-Item -Path "src\simulacra\core\__init__.py" -ItemType File -Force
New-Item -Path "tests\__init__.py" -ItemType File -Force
New-Item -Path "tests\unit\__init__.py" -ItemType File -Force

# Save modules
$typeContent = Get-Content -Path "types.txt" -Raw
$traitsContent = Get-Content -Path "traits.txt" -Raw
$playerContent = Get-Content -Path "player.txt" -Raw
$testContent = Get-Content -Path "test_traits.txt" -Raw

Set-Content -Path "src\simulacra\core\types.py" -Value $typeContent
Set-Content -Path "src\simulacra\core\traits.py" -Value $traitsContent
Set-Content -Path "src\simulacra\core\player.py" -Value $playerContent
Set-Content -Path "tests\unit\test_trait_effects.py" -Value $testContent