@echo off
chcp 65001 >nul
echo 啟動 Gemini 多模態對話助理...
cd /d "%~dp0"
python -m streamlit run app.py
pause
