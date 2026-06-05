import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import streamlit as st
import sqlite3
import random
import pandas as pd
import numpy as np
from datetime import datetime
from lunar_python import Solar
import plotly.express as px

st.set_page_config(page_title="命盤 × 樂透合參", layout="wide", initial_sidebar_state="expanded")

if st.button("⬅ 返回整合首頁"):
    st.switch_page("app.py")

st.markdown("""
    <style>
    .ball { display:inline-flex; align-items:center; justify-content:center; width:45px; height:45px; border-radius:50%; margin:4px; font-weight:900; font-size:18px; color:#FFF; box-shadow:inset -2px -2px 6px rgba(0,0,0,0.4), 2px 2px 5px rgba(0,0,0,0.3); }
    .ball-gold { background: radial-gradient(circle at 30% 30%, #FFD700, #B8860B); }
    .ball-red { background: radial-gradient(circle at 30% 30%, #FF5252, #B71C1C); }
    .ball-blue { background: radial-gradient(circle at 30% 30%, #42A5F5, #0D47A1); }
    .ball-purple { background: radial-gradient(circle at 30% 30%, #9C27B0, #4A148C); }
    .strategy-card { background:#F8FAFC; border-left:6px solid #1A237E; padding:15px 20px; margin-bottom:20px; border-radius:4px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    .strategy-title { color:#1A237E; font-size:18px; font-weight:bold; margin-bottom:10px; display:flex; justify-content:space-between; }
    .zone2-txt { font-size: 14px; font-weight: bold; color: #4A148C; margin-left: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("🌌 天機天元：雙區彩券深度合參決策引擎")
st.markdown("本系統已將 **大樂透 (Lotto 6/49)** 與 **威力彩 (Super Lotto)** 的物理概率模型徹底與您的先天命理八字、生命靈數進行解耦與動態打分。")

# ==========================================
# 1. 數據庫與統計資料分流載入 (已修正為真實資料庫連線)
# ==========================================
@st.cache_data(ttl=3600)
def load_game_lottery_stats(game_choice):
    """根據選擇的遊戲，讀取真實的歷史冷熱度與遺漏值"""
    db_path = os.path.join(root_dir, 'lottery_data.db')
    table_name = "lotto" if "大樂透" in game_choice else "super_lotto"
    max_n = 49 if "大樂透" in game_choice else 38
    
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql(f'SELECT * FROM {table_name} ORDER BY 期別 DESC', conn)
        conn.close()
        
        if df.empty:
            raise ValueError("No Data")
            
        all_nums = df[['N1', 'N2', 'N3', 'N4', 'N5', 'N6']].values.flatten()
        freq_count = pd.Series(all_nums).value_counts().to_dict()
        freq = {n: freq_count.get(n, 0) for n in range(1, max_n + 1)}
        
        # 精算遺漏值
        overdue = {n: len(df) for n in range(1, max_n + 1)}
        for n in range(1, max_n + 1):
            for i, row in df.iterrows():
                draw = [row['N1'], row['N2'], row['N3'], row['N4'], row['N5'], row['N6']]
                if n in draw:
                    overdue[n] = i
                    break
                    
        zone2_freq = None
        if "威力彩" in game_choice:
            z2_counts = df['特別號'].value_counts().to_dict()
            zone2_freq = {n: z2_counts.get(n, 0) for n in range(1, 9)}
            
        return freq, overdue, zone2_freq, True
    except Exception as e:
        # Fallback 容錯
        return {n: random.randint(5, 25) for n in range(1, max_n + 1)}, {n: random.randint(0, 30) for n in range(1, max_n + 1)}, {n: random.randint(10, 40) for n in range(1, 9)} if "威力彩" in game_choice else None, False

# ==========================================
# 2. 側邊欄控制台：生辰與遊戲選單
# ==========================================
with st.sidebar:
    st.markdown("### 🎰 1. 選擇合參目標")
    game_choice = st.radio("選擇彩券遊戲", ["大樂透 (Lotto 6/49)", "威力彩 (Super Lotto)"])
    
    st.markdown("---")
    st.markdown("### 🔮 2. 輸入天體靈魂參數")
    b_date = st.date_input("出生日期", datetime(1971, 9, 30))
    b_time = st.time_input("出生時間", datetime(1971, 9, 30, 4, 0).time())
    
    # 算命盤基礎五行與生肖地支
    lunar = Solar.fromYmdHms(b_date.year, b_date.month, b_date.day, b_time.hour, b_time.minute, 0).getLunar()
    bazi = lunar.getEightChar()
    day_master = bazi.getDay()[0]
    year_branch = bazi.getYear()[1] # 年支(生肖)
    
    # 建立地支三合局參數
    TRINE_MAP = {
        '申': ['申', '子', '辰'], '子': ['申', '子', '辰'], '辰': ['申', '子', '辰'],
        '巳': ['巳', '酉', '丑'], '酉': ['巳', '酉', '丑'], '丑': ['巳', '酉', '丑'],
        '寅': ['寅', '午', '戌'], '午': ['寅', '午', '戌'], '戌': ['寅', '午', '戌'],
        '亥': ['亥', '卯', '未'], '卯': ['亥', '卯', '未'], '未': ['亥', '卯', '未']
    }
    BRANCH_NUMS = {"子":1, "丑":2, "寅":3, "卯":4, "辰":5, "巳":6, "午":7, "未":8, "申":9, "酉":10, "戌":11, "亥":12}
    my_trines = TRINE_MAP.get(year_branch, [year_branch])
    trine_lucky_nums = [BRANCH_NUMS[b] for b in my_trines]
    trine_lucky_tails = [n % 10 for n in trine_lucky_nums]
    
    # 生命靈數
    life_path = sum(int(d) for d in b_date.strftime("%Y%m%d"))
    while life_path > 9: life_path = sum(int(d) for d in str(life_path))
        
    wu_xing_map = {'甲':'木', '乙':'木', '丙':'火', '丁':'火', '戊':'土', '己':'土', '庚':'金', '辛':'金', '壬':'水', '癸':'水'}
    day_element = wu_xing_map.get(day_master, '水')
    
    tail_map = {'水':[1,6], '火':[2,7], '木':[3,8], '金':[4,9], '土':[5,0]}
    sheng_map = {'木':'水', '火':'木', '土':'火', '金':'土', '水':'金'}
    
    self_tails = tail_map[day_element]
    mother_tails = tail_map[sheng_map[day_element]]
    
    st.info(f"**本命五行：** {day_master} ({day_element})\n**年支生肖：** {year_branch} (三合: {''.join(my_trines)})\n**生命靈數：** {life_path}\n**旺運尾數：** {self_tails}")
    generate_btn = st.button("🚀 執行多維度合參運算", use_container_width=True)

# 載入分流資料
freq_data, overdue_data, zone2_data, db_connected = load_game_lottery_stats(game_choice)

# ==========================================
# 3. 核心雙遊戲計分矩陣
# ==========================================
if generate_btn:
    is_lotto = "大樂透" in game_choice
    max_num = 49 if is_lotto else 38
    all_nums = list(range(1, max_num + 1))
    
    # 動態計算流年九宮飛星 (值年入中宮星)
    current_year = datetime.now().year
    sum_digits = sum(int(d) for d in str(current_year))
    while sum_digits > 9: sum_digits = sum(int(d) for d in str(sum_digits))
    center_star = 11 - sum_digits
    if center_star > 9: center_star -= 9
    ruling_star_tail = center_star # 本年度主宰星
    
    # 取得歷史資料的最大值以供正規化
    max_freq = max(freq_data.values()) if freq_data and max(freq_data.values()) > 0 else 1
    max_overdue = max(overdue_data.values()) if overdue_data and max(overdue_data.values()) > 0 else 1
    
    scores = {}
    
    # 進行第一區（或大樂透全盤）號碼打分
    for n in all_nums:
        score = 0
        tail = n % 10
        
        # 維度一：統計機率 (Max 40) - 正規化處理
        score += (freq_data.get(n, 0) / max_freq) * 20
        score += (overdue_data.get(n, 0) / max_overdue) * 20
        
        # 維度二：五行、生肖三合與九宮飛星 (Max 35)
        if tail in self_tails: score += 15
        elif tail in mother_tails: score += 10
        
        if tail in trine_lucky_tails: score += 10 # 生肖三合共振
        if tail == ruling_star_tail: score += 5   # 流年主宰星
        if tail == 9: score += 5                  # 九紫當令大運財星
            
        # 維度三：生命靈數共振 (Max 30)
        if n == life_path or sum(int(d) for d in str(n)) == life_path or tail == life_path:
            score += 20
        elif n % life_path == 0:
            score += 10
            
        scores[n] = round(score, 1)

    sorted_nums = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    
    # 計算第二區號碼（僅限威力彩 1~8）含溢位防漏邏輯
    zone2_final = None
    if not is_lotto:
        zone2_scores = {}
        max_z2_freq = max(zone2_data.values()) if zone2_data and max(zone2_data.values()) > 0 else 1
        
        # 溢位轉換：將 0 或 9 映射到 1~8 以免吃不到分數
        mapped_life_path = (life_path - 1) % 8 + 1
        mapped_self_tails = [(t - 1) % 8 + 1 for t in self_tails]
        mapped_trine_tails = [(t - 1) % 8 + 1 for t in trine_lucky_tails]
        
        for n in range(1, 9):
            z2_score = (zone2_data.get(n, 0) / max_z2_freq) * 40 # 基礎歷史頻率分
            if n == mapped_life_path: z2_score += 30 # 靈數絕對重合
            if n in mapped_self_tails: z2_score += 20 # 五行尾數重合
            if n in mapped_trine_tails: z2_score += 10 # 三合重合
            zone2_scores[n] = z2_score
            
        zone2_final = sorted(zone2_scores.items(), key=lambda x: x[1], reverse=True)[0][0]

    # 策略衍生
    top_6 = [x[0] for x in sorted_nums[:6]]
    
    res_pool = [n for n in all_nums if n % 10 == life_path or n == life_path or sum(int(d) for d in str(n)) == life_path or (n % 10 in trine_lucky_tails)]
    if len(res_pool) < 6: res_pool = all_nums
    strat_res = random.sample(res_pool, min(6, len(res_pool)))
    while len(strat_res) < 6:
        extra = random.choice([x[0] for x in sorted_nums[:15] if x[0] not in strat_res])
        strat_res.append(extra)
        
    cold_but_lucky = sorted([n for n in all_nums if n % 10 in mother_tails or n % 10 in self_tails], key=lambda x: overdue_data.get(x, 0), reverse=True)
    if len(cold_but_lucky) < 6: cold_but_lucky = all_nums
    strat_cold = cold_but_lucky[:6]

    def format_balls_html(nums, ball_class="ball-gold", z2=None):
        html = "".join([f"<div class='ball {ball_class}'>{n:02d}</div>" for n in sorted(nums)])
        if z2 is not None:
            html += f"<span class='zone2-txt'>➔ 第二區特別加持：</span><div class='ball ball-purple'>{z2:02d}</div>"
        return html

    # --- 前端畫面渲染 ---
    st.markdown(f"### 📊 【{game_choice}】天機爆發潛力分佈")
    if not db_connected:
        st.warning("⚠️ 查無真實資料庫，目前採用量子擬態亂數模式進行展示。")
        
    top_15_df = pd.DataFrame(sorted_nums[:15], columns=['號碼', '合參分數'])
    top_15_df['號碼'] = top_15_df['號碼'].astype(str)
    fig = px.bar(top_15_df, x='號碼', y='合參分數', color='合參分數', color_continuous_scale='Magma', text='合參分數')
    fig.update_layout(height=230, margin=dict(l=20, r=20, t=20, b=20), xaxis_title="", yaxis_title="爆發指數")
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"<div class='strategy-card'><div class='strategy-title'><span>🏆 策略一：天機獨尊組 (綜合分最高)</span><span style='color:#666; font-size:14px;'>整合真實大數據、日元生剋、三合與飛星</span></div>{format_balls_html(top_6, 'ball-red', zone2_final)}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='strategy-card'><div class='strategy-title'><span>🔮 策略二：靈魂生肖共振組</span><span style='color:#666; font-size:14px;'>本命靈數【{life_path}】與三合【{''.join(my_trines)}】對齊</span></div>{format_balls_html(strat_res, 'ball-gold', zone2_final)}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='strategy-card'><div class='strategy-title'><span>💧 策略三：貴人生旺反轉組</span><span style='color:#666; font-size:14px;'>依據相生尾數尋找歷史高遺漏值大冷門</span></div>{format_balls_html(strat_cold, 'ball-blue', zone2_final)}</div>", unsafe_allow_html=True)

    with col2:
        st.success(f"✅ {game_choice} 運算完畢")
        st.markdown(f"**參數庫狀態：** {'已連線真實資料庫' if db_connected else '模擬演算'}")
        st.markdown("---")
        z2_analysis = f"並依據您的靈數與生肖溢位映射，精確鎖定第二區的關鍵獨頭號 **{zone2_final:02d}**。" if zone2_final else ""
        st.markdown(f"💡 **大師深度解讀：**\n\n本次目標為**{game_choice}**。系統已自動鎖定該遊戲的矩陣上限（{max_num} 碼），{z2_analysis}\n\n在目前 {current_year} 年的宏觀氣場下，流年主宰星為【{ruling_star_tail}白星】，結合九運當令【9紫財星】，加上您生肖「{year_branch}」的專屬三合磁場，這在數學模型中會直接加強與您本命五行相生的號碼。若要下注，建議優先採用**策略一**進行配置。")
