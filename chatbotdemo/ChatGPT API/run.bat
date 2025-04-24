@echo off
REM ===============================
REM  Windows Batch Script to Run App using .env
REM ===============================

REM Load environment variables from .env (requires dotenv-cli)
call npx dotenv -e .env -- echo Loading environment variables

REM Set Flask variables
set FLASK_APP=app.py
set FLASK_ENV=development

REM Start the Flask server
npx dotenv -e .env -- flask run --host=0.0.0.0 --port=5000

pause