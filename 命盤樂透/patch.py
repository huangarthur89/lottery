import os

with open('/Users/huangarthur/Desktop/命盤樂透/排命盤/saju_ultimate_master.py', 'r', encoding='utf-8') as f:
    master_content = f.read()

css_start = master_content.find('st.markdown("""\n    <style>')

new_header = """import sys
import os
# 【究極路徑修復】這段必須在最上面！強制 Python 優先讀取根目錄
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
paipan_dir = os.path.join(root_dir, '排命盤')
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if paipan_dir not in sys.path:
    sys.path.insert(0, paipan_dir)

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
from lunar_python import Solar
from ziwei import build_ziwei_chart
from saju import calculate_saju
import swisseph as swe
import math
import re

# ==========================================
# 0. 全域變數定義 & 頁面設定
# ==========================================
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

st.set_page_config(page_title="命盤分析", layout="wide", initial_sidebar_state="expanded")

# === 整合版專屬：返回首頁按鈕 ===
if st.button("⬅ 返回整合首頁", use_container_width=False):
    st.switch_page("app.py")
st.markdown("<hr style='margin-top:5px; margin-bottom:20px;'>", unsafe_allow_html=True)

"""

final_content = new_header + master_content[css_start:]

with open('/Users/huangarthur/Desktop/命盤樂透/pages/1_命盤分析.py', 'w', encoding='utf-8') as f:
    f.write(final_content)

print("Replacement successful")
