@echo off
chcp 65001 >nul
:: 切換到腳本所在的目錄
cd /d "%~dp0"
:: 啟動 Streamlit
python -m streamlit run saju_ultimate_master.py
pause
