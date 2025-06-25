@echo off
echo Starting Fake News Detection System...

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Start the server
python run.py --debug

pause 