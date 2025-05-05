@echo off
echo Building Simulacra...

:: Clean previous builds
if exist "build" rd /s /q build
if exist "dist" rd /s /q dist

:: Create virtual environment if it doesn't exist
if not exist ".venv" (
    python -m venv .venv
    call .venv\Scripts\activate
    python -m pip install -U pip setuptools wheel
    python -m pip install -r requirements.txt
)

:: Build Cython modules
python setup.py build_ext --inplace

:: Create wheel
python -m build