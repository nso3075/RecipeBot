@echo off
REM Activate virtual env here if needed
REM call venv\Scripts\activate

set FLASK_APP=app.py
set FLASK_ENV=development

flask run --host=0.0.0.0 --port=5000

pause
