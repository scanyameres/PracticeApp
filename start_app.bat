@echo off
REM Start the Streamlit app and open it in the browser (http://localhost:8501).
REM Close this window or press Ctrl+C to stop the server.
cd /d "%~dp0"
uv run streamlit run src\scanya_ae_afa_updated0209_1_6\landing.py
pause
