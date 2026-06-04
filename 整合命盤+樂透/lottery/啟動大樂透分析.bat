@echo off
:: 切換到腳本所在的目錄
cd /d "%~dp0"
:: 啟動 Streamlit
python -m streamlit run app.py
pause
