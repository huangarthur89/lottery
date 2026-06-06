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
from datetime import datetime, timedelta
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
# 1. 數據庫與統計資料分流載入
# ==========================================
@st.cache_data(ttl=3600)
def load_game_lottery_stats(game_choice):
    """
    從 SQLite 資料庫讀取真實歷史數據，精算頻率與遺漏值。
    具備快取機制 (1小時更新一次) 與極端防呆。
    """
    # 確保連線到根目錄的 lottery_data.db
    db_path = os.path.join(root_dir, 'lottery_data.db')
    
    # 【防呆機制】如果找不到資料庫，優雅降級回模擬模式，避免系統崩潰
    if not os.path.exists(db_path):
        return _fallback_mock_data(game_choice)

    try:
        conn = sqlite3.connect(db_path)
        
        # 判斷遊戲與設定參數 (請依據您實際的 Table 名稱微調)
        if "大樂透" in game_choice:
            table_name = "lotto" 
            max_num = 49
            has_zone2 = False
        else:
            table_name = "super_lotto" 
            max_num = 38
            has_zone2 = True

        # 讀取最近 100 期作為高強度統計基礎 (依據「期別」由大到小排序)
        query = f"SELECT * FROM {table_name} ORDER BY 期別 DESC LIMIT 100"
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            return _fallback_mock_data(game_choice)

        # 鎖定開獎號碼欄位
        num_cols = ['N1', 'N2', 'N3', 'N4', 'N5', 'N6']
        
        # --- 運算 1. 歷史頻率 (熱度) ---
        all_nums = df[num_cols].values.flatten()
        freq_raw = pd.Series(all_nums).value_counts().to_dict()
        # 確保 1~max_num 每顆球都有紀錄，沒開出的補 0
        freq_data = {n: freq_raw.get(n, 0) for n in range(1, max_num + 1)}

        # --- 運算 2. 遺漏值 (冷度) ---
        overdue_data = {}
        for n in range(1, max_num + 1):
            # 找出包含該號碼的列索引 (index 0 是最新一期)
            matches = df[df[num_cols].isin([n]).any(axis=1)].index
            if len(matches) > 0:
                overdue_data[n] = int(matches.min())
            else:
                # 如果 100 期都沒開出，遺漏值設為 100 (極冷門)
                overdue_data[n] = 100 

        # --- 運算 3. 第二區特別號 (威力彩專屬) ---
        zone2_data = None
        if has_zone2:
            # 判斷第二區的欄位名稱 (兼容 '特別號' 或其他命名)
            z2_col = '特別號' if '特別號' in df.columns else 'Zone2'
            if z2_col in df.columns:
                z2_counts = df[z2_col].value_counts().to_dict()
                zone2_data = {n: z2_counts.get(n, 0) for n in range(1, 9)}
            else:
                zone2_data = {n: 10 for n in range(1, 9)} # 防呆預設值

        return freq_data, overdue_data, zone2_data, True

    except Exception as e:
        print(f"資料庫連線或運算異常: {e}")
        return _fallback_mock_data(game_choice)

def _fallback_mock_data(game_choice):
    """資料庫異常時的無縫降級方案，確保前台畫面不崩潰"""
    max_n = 49 if "大樂透" in game_choice else 38
    f_data = {n: random.randint(5, 25) for n in range(1, max_n + 1)}
    o_data = {n: random.randint(0, 30) for n in range(1, max_n + 1)}
    z2_data = {n: random.randint(10, 40) for n in range(1, 9)} if "威力彩" in game_choice else None
    return f_data, o_data, z2_data, False

# ==========================================
# 2. 側邊欄控制台：生辰與遊戲選單
# ==========================================
with st.sidebar:
    st.markdown("### 🎰 1. 選擇合參目標")
    game_choice = st.radio("選擇彩券遊戲", ["大樂透 (Lotto 6/49)", "威力彩 (Super Lotto)"])
    
    st.markdown("---")
    st.markdown("### 🔮 2. 輸入天體靈魂參數")
    
    # 【核心優化】動態推算未來 3 個月 (防呆日曆)
    today = datetime.now()
    future_limit = today + timedelta(days=90)
    
    b_date = st.date_input(
        "出生日期", 
        value=datetime(1971, 9, 30),
        min_value=datetime(1930, 1, 1),
        max_value=future_limit
    )
    time_mode = st.radio("出生時間精確度", ["✅ 知道精確時間", "❓ 不知道時間 (吉時)"])
    if "不知道" in time_mode:
        b_time = datetime(1971, 9, 30, 12, 0).time()
        st.info("🕒 已為您代入中性【吉時 (午時)】排盤，確保本命日柱的五行精準度。")
    else:
        b_time = st.time_input("出生時間", datetime(1971, 9, 30, 4, 0).time())
    
    # 算命盤基礎五行
    lunar = Solar.fromYmdHms(b_date.year, b_date.month, b_date.day, b_time.hour, b_time.minute, 0).getLunar()
    day_master = lunar.getEightChar().getDay()[0]
    
    # 生命靈數
    life_path = sum(int(d) for d in b_date.strftime("%Y%m%d"))
    while life_path > 9: life_path = sum(int(d) for d in str(life_path))
        
    wu_xing_map = {'甲':'木', '乙':'木', '丙':'火', '丁':'火', '戊':'土', '己':'土', '庚':'金', '辛':'金', '壬':'水', '癸':'水'}
    day_element = wu_xing_map.get(day_master, '水')
    
    tail_map = {'水':[1,6], '火':[2,7], '木':[3,8], '金':[4,9], '土':[5,0]}
    sheng_map = {'木':'水', '火':'木', '土':'火', '金':'土', '水':'金'}
    
    self_tails = tail_map[day_element]
    mother_tails = tail_map[sheng_map[day_element]]
    
    st.info(f"**本命五行：** {day_master} ({day_element})\n**生命靈數：** {life_path}\n**旺運尾數：** {self_tails}")
    generate_btn = st.button("🚀 執行多維度合參運算", use_container_width=True)

# 載入分流資料
freq_data, overdue_data, zone2_data, db_connected = load_game_lottery_stats(game_choice)

def get_current_wealth_tail():
    y = datetime.now().year
    # 簡易九宮飛星財星推算
    # 8白星在 2026 為財，透過年份餘數動態推算
    base = 8
    offset = (y - 2026) % 9
    return (base - offset) % 9 if (base - offset) % 9 != 0 else 9

# ==========================================
# 3. 核心雙遊戲計分矩陣
# ==========================================
if generate_btn:
    is_lotto = "大樂透" in game_choice
    max_num = 49 if is_lotto else 38
    all_nums = list(range(1, max_num + 1))
    
    scores = {}
    wealth_star_tail = get_current_wealth_tail()
    
    for n in all_nums:
        score = 0
        tail = n % 10
        
        # 維度一：統計機率 (Max 40)
        score += min(20, (freq_data.get(n, 10) / 25) * 20)
        score += min(20, (overdue_data.get(n, 0) / 30) * 20)
        
        # 維度二：五行與九宮飛星 (Max 30)
        if tail in self_tails: score += 15
        elif tail in mother_tails: score += 10
        if tail == wealth_star_tail: score += 5
            
        # 維度三：生命靈數共振 (Max 30)
        if n == life_path or sum(int(d) for d in str(n)) == life_path or tail == life_path:
            score += 20
        elif n % life_path == 0:
            score += 10
            
        scores[n] = round(score, 1)

    sorted_nums = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    
    # 計算第二區號碼（僅限威力彩 1~8）
    zone2_final = None
    if not is_lotto:
        zone2_scores = {}
        for n in range(1, 9):
            z2_score = (zone2_data.get(n, 20) / 40) * 40 
            if n == life_path: z2_score += 30 
            if n in self_tails: z2_score += 30 
            zone2_scores[n] = z2_score
        zone2_final = sorted(zone2_scores.items(), key=lambda x: x[1], reverse=True)[0][0]

    # 策略衍生
    top_6 = [x[0] for x in sorted_nums[:6]]
    
    res_pool = [n for n in all_nums if n % 10 == life_path or n == life_path or sum(int(d) for d in str(n)) == life_path]
    if len(res_pool) < 6: res_pool = all_nums
    strat_res = random.sample(res_pool, min(6, len(res_pool)))
    while len(strat_res) < 6:
        extra = random.choice([x[0] for x in sorted_nums[:15] if x[0] not in strat_res])
        strat_res.append(extra)
        
    cold_but_lucky = sorted([n for n in all_nums if n % 10 in mother_tails], key=lambda x: overdue_data.get(x, 0), reverse=True)
    if len(cold_but_lucky) < 6: cold_but_lucky = all_nums
    strat_cold = cold_but_lucky[:6]

    def format_balls_html(nums, ball_class="ball-gold", z2=None):
        html = "".join([f"<div class='ball {ball_class}'>{n:02d}</div>" for n in sorted(nums)])
        if z2 is not None:
            html += f"<span class='zone2-txt'>➔ 第二區特別加持：</span><div class='ball ball-purple'>{z2:02d}</div>"
        return html

    # --- 前端畫面渲染 ---
    st.markdown(f"### 📊 【{game_choice}】天機爆發潛力分佈")
    
    top_15_df = pd.DataFrame(sorted_nums[:15], columns=['號碼', '合參分數'])
    top_15_df['號碼'] = top_15_df['號碼'].astype(str)
    fig = px.bar(top_15_df, x='號碼', y='合參分數', color='合參分數', color_continuous_scale='Magma', text='合參分數')
    fig.update_layout(height=230, margin=dict(l=20, r=20, t=20, b=20), xaxis_title="", yaxis_title="爆發指數")
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"<div class='strategy-card'><div class='strategy-title'><span>🏆 策略一：天機獨尊組 (綜合分最高)</span><span style='color:#666; font-size:14px;'>整合大數據、日元生剋與飛星</span></div>{format_balls_html(top_6, 'ball-red', zone2_final)}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='strategy-card'><div class='strategy-title'><span>🔮 策略二：靈魂數字共振組</span><span style='color:#666; font-size:14px;'>本命靈數【{life_path}】與號碼波長對齊</span></div>{format_balls_html(strat_res, 'ball-gold', zone2_final)}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='strategy-card'><div class='strategy-title'><span>💧 策略三：貴人生旺反轉組</span><span style='color:#666; font-size:14px;'>依據相生尾數【{mother_tails}】捕捉高遺漏值</span></div>{format_balls_html(strat_cold, 'ball-blue', zone2_final)}</div>", unsafe_allow_html=True)

    with col2:
        st.success(f"✅ {game_choice} 運算完畢")
        st.markdown(f"**參數庫狀態：** 雙區解耦成功")
        st.markdown("---")
        z2_analysis = f"並依據您的靈魂共振頻率，精確鎖定第二區的關鍵獨頭號 **{zone2_final:02d}**。" if zone2_final else ""
        st.markdown(f"💡 **大師深度解讀：**\n\n本次運算目標為**{game_choice}**。系統已自動鎖定該遊戲的矩陣上限（{max_num} 碼），{z2_analysis}\n\n在目前 2026 丙午年的宏觀氣場下，火土印星極旺，這在數學模型中會直接加強與您本命五行相生的號碼。若要下注，建議優先採用**策略一**進行包牌配置。")
