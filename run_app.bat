@echo off
REM Double-click to start the Streamlit app on http://localhost:8501
cd /d "%~dp0"
uv run streamlit run src\landing.py
pause
