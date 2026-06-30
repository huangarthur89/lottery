# -*- coding: utf-8 -*-
import os
import runpy
import sys
from pathlib import Path

import streamlit as st

# 啟動時自動建立 .streamlit/config.toml 來強制鎖定亮色模式，防止自動切換深色模式導致側邊欄文字看不清
_config_dir = ".streamlit"
if not os.path.exists(_config_dir):
    try:
        os.makedirs(_config_dir)
    except Exception:
        pass
_config_file = os.path.join(_config_dir, "config.toml")
if not os.path.exists(_config_file):
    try:
        with open(_config_file, "w", encoding="utf-8") as _f:
            _f.write('[theme]\nbase="light"\n')
    except Exception:
        pass

st.set_page_config(page_title="樂透分析", page_icon="🎰", layout="wide")

st.markdown("""
    <style>
    /* 美化側邊欄導航 */
    [data-testid="stSidebar"] {
        background-color: #FAFAFA !important;
        border-right: 2px solid #E1BEE7 !important;
    }
    [data-testid="stSidebarNav"] {
        background-image: linear-gradient(180deg, #F3E5F5, #FAFAFA) !important;
        padding-top: 15px !important;
        padding-bottom: 15px !important;
        border-bottom: 2px solid #E1BEE7 !important;
        margin-bottom: 20px !important;
    }
    [data-testid="stSidebarNav"] span {
        font-size: 16px !important;
        font-weight: bold !important;
        color: #4A148C !important;
    }
    /* 強制滿版寬度，解決 Streamlit layout="wide" 有時失效的問題 */
    .block-container {
        max-width: 95% !important;
        padding-top: 2rem;
    }
    /* 防止表格文字自動換行，解決擠壓導致變得很長的問題 */
    table th, table td {
        white-space: nowrap !important;
    }
    </style>
""", unsafe_allow_html=True)

if st.button("← 返回整合首頁", use_container_width=False, key="back_home_top"):
    st.switch_page("app.py")
st.divider()

BASE_DIR = Path(__file__).resolve().parents[1]
LOTTERY_DIR = BASE_DIR / "lottery"
PAGES = {
    "大樂透": LOTTERY_DIR / "pages" / "1_大樂透.py",
    "威力彩": LOTTERY_DIR / "pages" / "2_威力彩.py",
}

if st.sidebar.button("← 返回整合首頁", use_container_width=True, key="back_home_side"):
    st.switch_page("app.py")
st.sidebar.divider()
mode = st.sidebar.radio("選擇彩券分析", list(PAGES.keys()), horizontal=True)
st.sidebar.caption("此頁會沿用原本 lottery 資料夾內的分析程式與 lottery_data.db。")

# removed os.chdir to prevent breaking streamlit's sidebar
sys.path.insert(0, str(LOTTERY_DIR))

# 原本彩票頁面各自呼叫 set_page_config；在整合頁已設定過，這裡改成 no-op 避免 Streamlit 重複設定錯誤。
st.set_page_config = lambda *args, **kwargs: None
runpy.run_path(str(PAGES[mode]), run_name="__main__")
