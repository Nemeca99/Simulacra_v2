@'
@echo off
echo Launching Simulacra...
.\.venv\Scripts\python.exe launcher.py
'@ | Out-File -FilePath play_game.bat -Encoding ascii