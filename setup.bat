@echo off
echo ========================================
echo Post Discharge Medical AI Assistant
echo Setup Script
echo ========================================
echo.

echo Step 1: Creating virtual environment...
python -m venv venv
echo.

echo Step 2: Activating virtual environment...
call venv\Scripts\activate
echo.

echo Step 3: Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
echo.

echo Step 4: Setting up database...
python scripts\setup_database.py
echo.

echo Step 5: Setting up vector database...
python scripts\setup_vector_db.py
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Copy .env.example to .env and add your API keys
echo 2. Run start_backend.bat to start the backend server
echo 3. Run start_frontend.bat to start the frontend
echo.

pause
