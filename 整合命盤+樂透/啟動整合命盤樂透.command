#!/bin/bash
# 切換到腳本所在的目錄
cd "$(dirname "$0")"
# 啟動整合首頁 app.py
python3 -m streamlit run app.py
