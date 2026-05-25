import streamlit as st
md = """
| 策略名稱 | 第 1 球 | 第 2 球 | 第 3 球 | 第 4 球 | 第 5 球 | 第 6 球 | 特別號 | 預計中獎金額 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 🔥 歷史最熱門 | <span style='color:#FF4B4B; font-weight:bold;'>2</span> | 8 | 15 | 23 | 35 | 41 | 37 | $0 |
"""
st.markdown(md, unsafe_allow_html=True)
