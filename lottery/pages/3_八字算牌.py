import streamlit as st
import pandas as pd
import sqlite3
import random
from datetime import datetime
from collections import Counter

st.set_page_input = {
    "page_title": "🌙 阿舍的八字五行算牌術",
    "page_icon": "🔮",
    "layout": "wide"
}

st.title("🔮 🌙 阿舍的八字五行算牌術")
st.markdown("將您的**生辰八字**轉化為天干地支五行矩陣，並結合**歷史大數據**，精算專屬於您的開運發財號碼！")

# --- 天文曆法與五行資料庫 ---
STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 五行歸屬
STEM_ELEMENTS = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"
}
BRANCH_ELEMENTS = {
    "寅": "木", "卯": "木", 
    "巳": "火", "午": "火", 
    "申": "金", "酉": "金", 
    "子": "水", "亥": "水", 
    "辰": "土", "戌": "土", "丑": "土", "未": "土"
}

# 五行對應的數字尾數 (河圖洛書)
ELEMENT_NUMS = {
    "水": [1, 6],
    "火": [2, 7],
    "木": [3, 8],
    "金": [4, 9],
    "土": [5, 0]
}

def get_day_master(birth_date):
    """🔮 天文公式：計算 Gregorian 日期對應的日柱天干地支"""
    # 以 1900-01-01 (甲戌日) 為基期
    base_date = datetime(1900, 1, 1)
    delta_days = (birth_date - base_date.date()).days
    
    stem_idx = (0 + delta_days) % 10
    branch_idx = (10 + delta_days) % 12
    
    day_stem = STEMS[stem_idx]
    day_branch = BRANCHES[branch_idx]
    return day_stem, day_branch

# --- UI 介面設計 ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("✍️ 輸入您的生辰資訊")
    
    # 選擇彩券類型
    lotto_type = st.radio("選擇欲投注的彩券：", ["大樂透", "威力彩"], horizontal=True)
    
    # 輸入生日與時辰
    # 加上 min_value 與 max_value，讓年份可以從 1900 選到今天
    birth_date = st.date_input(
        "選擇出生公曆日期：", 
        value=datetime(1990, 1, 1),
        min_value=datetime(1900, 1, 1),
        max_value=datetime.today()
    )
    
    hour_options = [
        "子時 (23:00-01:00)", "丑時 (01:00-03:00)", "寅時 (03:00-05:00)", 
        "卯時 (05:00-07:00)", "辰時 (07:00-09:00)", "巳時 (09:00-11:00)", 
        "午時 (11:00-13:00)", "未時 (13:00-15:00)", "申時 (15:00-17:00)", 
        "酉時 (17:00-19:00)", "戌時 (19:00-21:00)", "亥時 (21:00-23:00)"
    ]
    birth_hour = st.selectbox("選擇出生時辰：", hour_options)
    
    calculate_btn = st.button("🔮 開始八字五行精算", use_container_width=True)

with col2:
    if calculate_btn:
        st.subheader("🧬 您的八字五行命盤解析")
        
        # 1. 計算日主與時辰支
        day_stem, day_branch = get_day_master(birth_date)
        hour_branch = birth_hour[0] # 抓出「子、丑、寅...」
        
        day_element = STEM_ELEMENTS[day_stem]
        hour_element = BRANCH_ELEMENTS[hour_branch]
        
        # 顯示命盤小字卡
        st.success(f"【您的本命日柱】：{day_stem}{day_branch}日（{day_element}命）｜【出生時辰】：{hour_branch}時（屬{hour_element}）")
        
        # 2. 根據五行生成幸運號碼母體池 (大樂透 49 碼，威力彩 38 碼)
        pool_max = 49 if lotto_type == "大樂透" else 38
        
        # 抓出日主與時辰對應的所有尾數號碼
        lucky_tails = list(set(ELEMENT_NUMS[day_element] + ELEMENT_NUMS[hour_element]))
        
        lucky_pool = []
        for n in range(1, pool_max + 1):
            if n % 10 in lucky_tails or (n % 10 == 0 and 0 in lucky_tails):
                lucky_pool.append(n)
                
        # 3. 讀取歷史數據庫，加入大數據權重
        try:
            conn = sqlite3.connect('lottery_data.db')
            table_name = 'lotto' if lotto_type == "大樂透" else 'super_lotto'
            df = pd.read_sql(f'SELECT * FROM {table_name} ORDER BY 期別 DESC', conn)
            conn.close()
        except Exception:
            df = pd.DataFrame() # 防呆：如果沒資料庫就給空 DataFrame
            
        if not df.empty:
            # 統計歷史開出次數
            all_nums = df[['N1', 'N2', 'N3', 'N4', 'N5', 'N6']].values.flatten()
            freq = Counter(all_nums)
            
            # 從你的五行幸運池中，挑選出歷史開出次數最多的前 12 個號碼
            lucky_pool_with_freq = {n: freq[n] for n in lucky_pool}
            sorted_lucky_pool = sorted(lucky_pool_with_freq.items(), key=lambda x: x[1], reverse=True)
            final_pool = [x[0] for x in sorted_lucky_pool[:12]]
        else:
            # 如果資料庫是空的，直接拿幸運池當作最終選號池
            final_pool = lucky_pool
            
        # 防呆：如果幸運池號碼不夠 6 個，用全隨機補足
        while len(final_pool) < 6:
            r_num = random.randint(1, pool_max)
            if r_num not in final_pool:
                final_pool.append(r_num)
                
        # 4. 最終精選 6 顆黃金開運球
        final_6 = sorted(random.sample(final_pool, 6))
        
        # 5. 產生特別號
        if lotto_type == "大樂透":
            special_num = random.choice(ELEMENT_NUMS[day_element]) # 大樂透特別號直接用五行本命數
            if special_num == 0: special_num = 10
        else:
            special_num = random.randint(1, 8) # 威力彩第二區 1~8 號
            
        # --- 美化輸出呈現 ---
        st.markdown("---")
        st.markdown(f"### 🎯 專屬於您的【{lotto_type}】八字開運發財組合")
        
        def format_num(n):
            return f"<span style='font-size: 26px; font-weight:bold; background-color:#F0F2F6; padding: 5px 12px; border-radius: 50%; margin-right: 10px;'>{str(n).zfill(2)}</span>"
        def format_sp(n):
            return f"<span style='color:#FFFFFF; font-size: 26px; font-weight:bold; background-color:#FF4B4B; padding: 5px 12px; border-radius: 50%; margin-right: 10px;'>{str(n).zfill(2)}</span>"
            
        nums_html = "".join([format_num(n) for n in final_6])
        sp_html = format_sp(special_num)
        
        st.markdown(f"<div style='margin: 20px 0;'>{nums_html} <span style='font-size:24px; font-weight:bold;'>➕</span> {sp_html}</div>", unsafe_allow_html=True)
        
        # 命理學建議
        st.info(f"💡 **命理開運建議**：您的日主屬 **{day_element}**，今日算牌磁場與 **{lotto_type}** 產生強烈共振。建議可往您出生地的**{ '正東、東南' if day_element=='木' else '正南' if day_element=='火' else '東北、西南' if day_element=='土' else '正西、西北' if day_element=='金' else '正北'}**方的彩券行下注，能更有效催旺您的財運天線！")
        st.balloons()
    else:
        # 初始畫面提示
        st.info("🔮 請在左側輸入您的出生年月日與時間，AI 將為您排盤並篩選大數據開運號碼。")
