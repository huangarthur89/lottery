#!/bin/bash
# 切換到腳本所在的目錄
cd "$(dirname "$0")"
# 啟動 Streamlit
python3 -m streamlit run app.py
