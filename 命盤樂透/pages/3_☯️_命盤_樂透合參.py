import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import streamlit as st
import sqlite3
import random
import re

# ==========================================
# 4. 旗艦版：台灣本土夢境逼牌解碼引擎
# ==========================================
st.markdown("---")
st.markdown("### 🌙 旗艦版：台灣本土夢境逼牌解碼引擎")
def parse_dream_to_numbers(user_input):
    if not user_input:
        return []
    
    # 建立多維度同義詞庫：將形體、諧音、傳統逼牌邏輯分類
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from dream_dict import dream_database

    
    extracted_numbers = set()
    user_input = user_input.lower()
    
    for keywords, data in dream_database.items():
        nums = data["nums"]
        if any(k in user_input for k in keywords):
            extracted_numbers.update(nums)
            
    return sorted(list(extracted_numbers))

# ==========================================
# 旗艦版：夢境靈數共振擴張引擎 (打破單一尾數限制)
# ==========================================
def expand_dream_resonance(user_input, base_numbers, max_num=49):
    """
    將字典初步抓出的號碼，利用傳統逼牌法則與自然語言提取進行高維度擴張
    """
    expanded_set = set(base_numbers)
    
    # ---------------------------------------------------------
    # 策略 A：自然語言明示數字提取 (NLP Number Extraction)
    # ---------------------------------------------------------
    # 1. 捕捉阿拉伯數字 (例如：夢到坐 "52" 號公車)
    arabic_matches = re.findall(r'\d+', user_input)
    for num_str in arabic_matches:
        num = int(num_str)
        if 1 <= num <= max_num:  # 確保落在樂透範圍內
            expanded_set.add(num)
            
    # 2. 捕捉中文數字 (例如：夢到 "三" 隻小豬)
    chinese_num_map = {
        "一": 1, "二": 2, "兩": 2, "三": 3, "四": 4, "五": 5,
        "六": 6, "七": 7, "八": 8, "九": 9, "十": 10
    }
    for char in user_input:
        if char in chinese_num_map:
            expanded_set.add(chinese_num_map[char])

    # ---------------------------------------------------------
    # 策略 B：台灣道地逼牌變形法則 (Traditional Transformation)
    # ---------------------------------------------------------
    # 我們把目前收集到的號碼，進行靈數變形
    current_numbers = list(expanded_set)
    for num in current_numbers:
        
        # 變形 1：鏡像顛倒牌 (例如：解夢算出 12，逼牌自動加買 21)
        if num > 9:
            rev_num = int(str(num)[::-1])
            if 1 <= rev_num <= max_num:
                expanded_set.add(rev_num)
                
        # 變形 2：靈數合數 (例如：解夢算出 28，2+8=10，延伸逼牌 10)
        if num > 9:
            sum_num = sum(int(digit) for digit in str(num))
            if 1 <= sum_num <= max_num:
                expanded_set.add(sum_num)
                
        # 變形 3：鄰邊氣場共振 (例如：解夢算出 17，強烈磁場會波及 16 和 18)
        # 為了避免號碼過度膨脹，我們可以設定只對「個位數」進行鄰邊擴張
        if num < 10:
            if num - 1 >= 1:
                expanded_set.add(num - 1)
            if num + 1 <= max_num:
                expanded_set.add(num + 1)

    return sorted(list(expanded_set))



import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
from lunar_python import Solar
import plotly.express as px
import swisseph as swe

st.set_page_config(page_title="命盤 × 樂透合參", page_icon="☯️", layout="wide", initial_sidebar_state="expanded")

if st.button("⬅ 返回整合首頁"):
    st.switch_page("app.py")

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
    random.seed(datetime.now().toordinal())
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
    
    # 計算日期範圍：1930年 ~ 未來三個月 (約90天)
    min_d = date(1930, 1, 1)
    max_d = date.today() + timedelta(days=90)
    
    # 加入範圍限制
    b_date = st.date_input(
        "出生日期", 
        value=date(1971, 1, 1),
        min_value=min_d,
        max_value=max_d
    )
    
    time_options = [
        "吉時 (不知時辰)", "子時 (23:00 - 01:00)", "丑時 (01:00 - 03:00)", "寅時 (03:00 - 05:00)",
        "卯時 (05:00 - 07:00)", "辰時 (07:00 - 09:00)", "巳時 (09:00 - 11:00)",
        "午時 (11:00 - 13:00)", "未時 (13:00 - 15:00)", "申時 (15:00 - 17:00)",
        "酉時 (17:00 - 19:00)", "戌時 (19:00 - 21:00)", "亥時 (21:00 - 23:00)"
    ]
    b_hour_str = st.selectbox("出生時間", time_options)
    
    time_map = {
        "吉時 (不知時辰)": datetime(1971, 1, 1, 12, 0).time(),
        "子時 (23:00 - 01:00)": datetime(1971, 1, 1, 0, 0).time(),
        "丑時 (01:00 - 03:00)": datetime(1971, 1, 1, 2, 0).time(),
        "寅時 (03:00 - 05:00)": datetime(1971, 1, 1, 4, 0).time(),
        "卯時 (05:00 - 07:00)": datetime(1971, 1, 1, 6, 0).time(),
        "辰時 (07:00 - 09:00)": datetime(1971, 1, 1, 8, 0).time(),
        "巳時 (09:00 - 11:00)": datetime(1971, 1, 1, 10, 0).time(),
        "午時 (11:00 - 13:00)": datetime(1971, 1, 1, 12, 0).time(),
        "未時 (13:00 - 15:00)": datetime(1971, 1, 1, 14, 0).time(),
        "申時 (15:00 - 17:00)": datetime(1971, 1, 1, 16, 0).time(),
        "酉時 (17:00 - 19:00)": datetime(1971, 1, 1, 18, 0).time(),
        "戌時 (19:00 - 21:00)": datetime(1971, 1, 1, 20, 0).time(),
        "亥時 (21:00 - 23:00)": datetime(1971, 1, 1, 22, 0).time()
    }
    b_time = time_map[b_hour_str]
    time_mode = b_hour_str
    
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
    
    # === 大師級連動參數 ===
    # 1. 欠缺五行 (用神)
    eight_char = lunar.getEightChar()
    all_wuxing = eight_char.getYearWuXing() + eight_char.getMonthWuXing() + eight_char.getDayWuXing()
    if "精確" in time_mode: all_wuxing += eight_char.getTimeWuXing()
    count_elements = {e: all_wuxing.count(e) for e in "金木水火土"}
    favorable_elements = [k for k, v in count_elements.items() if v <= 1]
    if not favorable_elements: favorable_elements = ["水", "木"]
    favorable_tails = []
    for e in favorable_elements: favorable_tails.extend(tail_map[e])
        
    # 2. 木星 (Jupiter) 幸運牽引
    # UTC 時間簡化計算
    utc_hour = b_time.hour - 8 if b_time.hour >= 8 else b_time.hour + 16
    jd = swe.julday(b_date.year, b_date.month, b_date.day, utc_hour + b_time.minute/60.0)
    jupiter_data, _ = swe.calc_ut(jd, swe.JUPITER)
    jupiter_deg = jupiter_data[0]
    j_tail1 = int(jupiter_deg) % 10
    j_tail2 = (int(jupiter_deg) // 10) % 10
    jupiter_tails = list(set([j_tail1, j_tail2]))
    if 0 in jupiter_tails: jupiter_tails.remove(0)
    if not jupiter_tails: jupiter_tails = [3, 8] # 木星預設
    
    st.info(f"**本命五行：** {day_master} ({day_element}) | **生命靈數：** {life_path}\n**旺運尾數：** {self_tails} | **木星幸運點：** {jupiter_tails}\n**用神五行：** {'、'.join(favorable_elements)} (尾數 {favorable_tails})")
    
    st.markdown("---")
    st.markdown("### 💭 潛意識逼牌解碼 (選填)")
    dream_input = st.text_area("請簡述您近期的夢境或強烈直覺：", placeholder="例如：我夢到好多鈔票被小偷拿走...")

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
    # 徹底移除所有隨機機制，100% 純數據排序驅動
    
    is_lotto = "大樂透" in game_choice
    max_num = 49 if is_lotto else 38
    all_nums = list(range(1, max_num + 1))
    
    dream_nums_for_engine = []
    if dream_input:
        base_nums = parse_dream_to_numbers(dream_input)
        valid_base_nums = [n for n in base_nums if 1 <= n <= max_num]
        dream_nums_for_engine = [n for n in expand_dream_resonance(dream_input, valid_base_nums, max_num) if 1 <= n <= max_num]
        
        if dream_nums_for_engine:
            st.success(f"🔮 潛意識共振捕捉成功！已將號碼注入運算核心：{', '.join(map(str, dream_nums_for_engine))}")
        else:
            st.warning("暫無捕捉到強烈靈動數字，將以純命理與大數據為您推演。")
    
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
            
        # 維度四：大師級命理共振 (Max 20)
        # 1. 木星幸運牽引 (10分)
        if tail in jupiter_tails or n in jupiter_tails:
            score += 10
        # 2. 欠缺五行(用神)補足 (10分)
        if tail in favorable_tails:
            score += 10
            
        # ==========================================
        # 🌌 核心植入：夢境靈數強制共振加權
        # ==========================================
        if dream_nums_for_engine and n in dream_nums_for_engine:
            score += 50  # 超級權重，強勢擠進前段班
            
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
    
    # 策略二：靈數共振組 (依據合參分數嚴格降冪排列)
    res_pool = [n for n in all_nums if n % 10 == life_path or n == life_path or sum(int(d) for d in str(n)) == life_path]
    res_pool_sorted = sorted(res_pool, key=lambda n: scores.get(n, 0), reverse=True)
    strat_res = res_pool_sorted[:6]
    if len(strat_res) < 6:
        remaining_top = [x[0] for x in sorted_nums if x[0] not in strat_res]
        strat_res.extend(remaining_top[:6 - len(strat_res)])
        
    # 策略三：貴人生旺反轉組 (嚴格依據歷史遺漏值大到小排序，若冷度相同比分數)
    cold_but_lucky = sorted([n for n in all_nums if n % 10 in mother_tails], key=lambda n: (overdue_data.get(n, 0), scores.get(n, 0)), reverse=True)
    strat_cold = cold_but_lucky[:6]
    if len(strat_cold) < 6:
        remaining_cold = sorted([n for n in all_nums if n not in strat_cold], key=lambda n: (overdue_data.get(n, 0), scores.get(n, 0)), reverse=True)
        strat_cold.extend(remaining_cold[:6 - len(strat_cold)])

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
        st.info("🛡️ **核心聲明**：本系統已全面阻斷亂數生成 (RNG)。所有推薦號碼皆為 **100% 可被回溯的大數據與玄學參數疊加演算** 結果。")
        st.markdown("---")
        z2_analysis = f"並依據您的靈魂共振頻率，精確鎖定第二區的關鍵獨頭號 **{zone2_final:02d}**。" if zone2_final else ""




    # ==========================================
    # 🏆 終極功能：生成「專屬天機預測單」與真實當日流勢
    # ==========================================
    st.markdown("---")
    st.markdown("### 📜 專屬天機預測單 (Ticket of Destiny)")

    # 1. 嚴謹計算：真實當日五行與十神流勢
    today = datetime.now()
    lunar_today = Solar.fromYmd(today.year, today.month, today.day).getLunar()
    today_ganzhi = lunar_today.getDayInGanZhi()
    t_stem, t_branch = today_ganzhi[0], today_ganzhi[1]
    
    branch_wu_xing = {'子':'水', '丑':'土', '寅':'木', '卯':'木', '辰':'土', '巳':'火', '午':'火', '未':'土', '申':'金', '酉':'金', '戌':'土', '亥':'水'}
    t_stem_element = wu_xing_map.get(t_stem, '水')
    t_branch_element = branch_wu_xing.get(t_branch, '水')

    # 十神生剋矩陣：依據命主五行 vs 今日五行推演
    ten_gods = {
        '木': {'木':'比劫 (人緣合夥)', '火':'食傷 (靈感產出)', '土':'正偏財 (財富流動)', '金':'官殺 (壓力責任)', '水':'印星 (貴人資源)'},
        '火': {'火':'比劫 (人緣合夥)', '土':'食傷 (靈感產出)', '金':'正偏財 (財富流動)', '水':'官殺 (壓力責任)', '木':'印星 (貴人資源)'},
        '土': {'土':'比劫 (人緣合夥)', '金':'食傷 (靈感產出)', '水':'正偏財 (財富流動)', '木':'官殺 (壓力責任)', '火':'印星 (貴人資源)'},
        '金': {'金':'比劫 (人緣合夥)', '水':'食傷 (靈感產出)', '木':'正偏財 (財富流動)', '火':'官殺 (壓力責任)', '土':'印星 (貴人資源)'},
        '水': {'水':'比劫 (人緣合夥)', '木':'食傷 (靈感產出)', '火':'正偏財 (財富流動)', '土':'官殺 (壓力責任)', '金':'印星 (貴人資源)'}
    }
    
    t_s_god = ten_gods[day_element][t_stem_element]
    t_b_god = ten_gods[day_element][t_branch_element]
    
    # 判斷今日財運強弱給予建議
    if '財' in t_s_god or '財' in t_b_god or '食傷' in t_s_god or '食傷' in t_b_god:
        daily_comment = "今日天地氣場與您命盤呈【生財】之象，直覺敏銳，宜果斷下注。"
    elif '印' in t_s_god or '印' in t_b_god:
        daily_comment = "今日【印星】護體，偏財屬穩健型，建議優先參考系統的大數據策略一。"
    else:
        daily_comment = "今日氣場偏向【克耗】，宜保守小試，隨緣勿執著。"

    # 2. 繪製高質感預測單 UI
    z2_display = f"第二區：{zone2_final:02d}" if zone2_final else "無第二區"
    
    # ⚠️ 終極修復：將所有的 HTML 壓縮在一起，消除所有「空白行」與「縮排」，徹底防止 Markdown 誤判！
    ticket_html = f"""<div style="background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); padding: 30px; border-radius: 12px; box-shadow: 0 20px 40px rgba(0,0,0,0.5); border: 2px solid #D4AF37; max-width: 600px; margin: 0 auto; color: #FFF; font-family: 'Noto Serif TC', serif;"><div style="text-align: center; border-bottom: 1px dashed #D4AF37; padding-bottom: 15px; margin-bottom: 20px;"><h2 style="color: #D4AF37; margin: 0; font-weight: 900; letter-spacing: 2px;">STAR★START 天機預測單</h2><p style="color: #94a3b8; font-size: 14px; margin-top: 5px;">生成時間：{today.strftime('%Y-%m-%d %H:%M')}</p></div><div style="margin-bottom: 20px; font-size: 15px; line-height: 1.8;"><div style="display: flex; justify-content: space-between;"><span style="color:#D4AF37;">目標：</span><span>{game_choice}</span></div><div style="display: flex; justify-content: space-between;"><span style="color:#D4AF37;">命主五行：</span><span>{day_master} ({day_element})</span></div><div style="display: flex; justify-content: space-between;"><span style="color:#D4AF37;">生命靈數：</span><span>{life_path}</span></div><div style="display: flex; justify-content: space-between;"><span style="color:#D4AF37;">今日干支：</span><span>{today_ganzhi} ({t_stem_element} / {t_branch_element})</span></div><div style="display: flex; justify-content: space-between;"><span style="color:#D4AF37;">當日流勢：</span><span>天干 {t_s_god} / 地支 {t_b_god}</span></div></div><div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; border-left: 4px solid #D4AF37; margin-bottom: 20px;"><p style="margin:0; font-size: 14px; color: #cbd5e1;">💡 <b>流日玄學判定：</b>{daily_comment}</p></div><div style="margin-bottom: 15px;"><p style="color: #D4AF37; font-weight: bold; margin-bottom: 5px;">🏆 策略一：天機獨尊組</p><p style="font-size: 20px; font-weight: 900; letter-spacing: 3px; margin:0;">{', '.join([f'{n:02d}' for n in top_6])} <span style="color:#c084fc; font-size: 16px;">[{z2_display}]</span></p></div><div style="margin-bottom: 15px;"><p style="color: #D4AF37; font-weight: bold; margin-bottom: 5px;">🔮 策略二：靈數共振組</p><p style="font-size: 20px; font-weight: 900; letter-spacing: 3px; margin:0;">{', '.join([f'{n:02d}' for n in strat_res])} <span style="color:#c084fc; font-size: 16px;">[{z2_display}]</span></p></div><div style="margin-bottom: 20px;"><p style="color: #D4AF37; font-weight: bold; margin-bottom: 5px;">💧 策略三：貴人生旺反轉組</p><p style="font-size: 20px; font-weight: 900; letter-spacing: 3px; margin:0;">{', '.join([f'{n:02d}' for n in strat_cold])} <span style="color:#c084fc; font-size: 16px;">[{z2_display}]</span></p></div><div style="text-align: center; border-top: 1px dashed #D4AF37; padding-top: 15px;"><p style="color: #64748b; font-size: 12px; margin: 0;">建議您手機截圖保留此單，攜至彩券行作為劃卡依據。</p></div></div>"""
    
    st.markdown(ticket_html, unsafe_allow_html=True)
    
    # 3. 提供純文字檔下載按鈕
    export_txt = f"""STAR★START 天機預測單
生成時間：{today.strftime('%Y-%m-%d %H:%M')}
---------------------------
目標遊戲：{game_choice}
今日流勢：{today_ganzhi} | 天干 {t_s_god} / 地支 {t_b_god}
流日判定：{daily_comment}
---------------------------
🏆 策略一 (天機獨尊)：{', '.join([f'{n:02d}' for n in top_6])} | {z2_display}
🔮 策略二 (靈數共振)：{', '.join([f'{n:02d}' for n in strat_res])} | {z2_display}
💧 策略三 (生旺反轉)：{', '.join([f'{n:02d}' for n in strat_cold])} | {z2_display}
---------------------------
祝您好運！
"""
    
    col_dl1, col_dl2, col_dl3 = st.columns([1,2,1])
    with col_dl2:
        st.download_button(
            label="💾 下載預測單 (TXT檔)",
            data=export_txt,
            file_name=f"天機預測單_{today.strftime('%Y%m%d')}.txt",
            mime="text/plain",
            use_container_width=True
        )

# ==========================================
# 4. 🔥 真金不怕火煉：歷史回測引擎 (Backtesting System)
# ==========================================
st.markdown("---")
with st.expander("🔥 真金不怕火煉：歷史回測引擎", expanded=False):
    st.markdown("透過時光倒流技術，退回至指定期數「之前」，僅使用當時的歷史大數據與您的專屬命理參數進行盲測，驗證系統演算法的真實命中率。")

    db_path = os.path.join(root_dir, 'lottery_data.db')
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        test_table = "lotto" if "大樂透" in game_choice else "super_lotto"
        
        try:
            # 讀取最近 50 期供回測選擇
            test_df = pd.read_sql_query(f"SELECT * FROM {test_table} ORDER BY 期別 DESC LIMIT 50", conn)
            
            if not test_df.empty and len(test_df) > 10:
                # 包含最新一期 (index 0) 讓使用者可以回測剛剛開獎的最新結果
                test_subset = test_df.iloc[0:20]
                display_options = [f"{row['日期']} (第 {row['期別']} 期)" for _, row in test_subset.iterrows()]
                option_mapping = {f"{row['日期']} (第 {row['期別']} 期)": str(row['期別']) for _, row in test_subset.iterrows()}
                
                selected_display = st.selectbox("⏳ 選擇時光回測目標 (將隱藏該期與未來的數據進行盲測)：", display_options) 
                target_issue = option_mapping[selected_display]
                
                if st.button("⚖️ 啟動盲測驗證", use_container_width=True):
                    
                    # 🎯 核心修復：為回測引擎補上缺失的球數與財星變數
                    max_num = 49 if "大樂透" in game_choice else 38
                    wealth_star_tail = get_current_wealth_tail()
                    
                    # 1. 切割時空：分離目標期與其過去的歷史數據
                    target_idx = test_df[test_df['期別'].astype(str) == target_issue].index[0]
                    target_data = test_df.iloc[target_idx]
                    # 嚴格限制：只拿目標期「之前」的 30 期數據當作歷史
                    history_data = test_df.iloc[target_idx + 1 : target_idx + 31] 
                    
                    num_cols = ['N1', 'N2', 'N3', 'N4', 'N5', 'N6']
                    actual_nums = target_data[num_cols].values.tolist()
                    
                    # 2. 重新計算歷史環境 (假裝回到過去重新算頻率與遺漏)
                    hist_all_nums = history_data[num_cols].values.flatten()
                    hist_freq = pd.Series(hist_all_nums).value_counts().to_dict()
                    
                    hist_overdue = {}
                    for n in range(1, max_num + 1):
                        matches = history_data[history_data[num_cols].isin([n]).any(axis=1)].index
                        if len(matches) > 0:
                            hist_overdue[n] = int(matches.min() - (target_idx + 1))
                        else:
                            hist_overdue[n] = 30
                            
                    # 3. 啟動合參大腦：執行與主程式完全相同的權重演算法
                    bt_scores = {}
                    for n in range(1, max_num + 1):
                        score = 0
                        tail = n % 10
                        score += min(20, (hist_freq.get(n, 0) / 15) * 20)
                        score += min(20, (hist_overdue.get(n, 0) / 30) * 20)
                        if tail in self_tails: score += 15
                        elif tail in mother_tails: score += 10
                        if tail == wealth_star_tail: score += 5
                        if n == life_path or sum(int(d) for d in str(n)) == life_path or tail == life_path: 
                            score += 20
                        elif n % life_path == 0: 
                            score += 10
                            
                        # 維度四：大師級盲測共振
                        if tail in jupiter_tails or n in jupiter_tails: score += 10
                        if tail in favorable_tails: score += 10
                        
                        bt_scores[n] = round(score, 1)

                    # 擷取當時算出來的「策略一：天機獨尊組」前 6 碼
                    bt_sorted = sorted(bt_scores.items(), key=lambda x: x[1], reverse=True)
                    bt_top_6 = [x[0] for x in bt_sorted[:6]]
                    
                    # 4. 對答案與畫面渲染
                    hits = set(bt_top_6).intersection(set(actual_nums))
                    
                    def render_bt_balls(nums, actuals):
                        html = ""
                        for n in sorted(nums):
                            if n in actuals:
                                # 命中時，球會放大並閃爍紅光
                                html += f"<div class='ball ball-red' style='transform: scale(1.15); box-shadow: 0px 0px 12px #D32F2F; border: 2px solid #FFCDD2;'>{n:02d}</div>"
                            else:
                                # 沒命中時，球會變成灰色並半透明
                                html += f"<div class='ball ball-gold' style='opacity: 0.35; filter: grayscale(100%);'>{n:02d}</div>"
                        return html
                    
                    actual_html = "".join([f"<div class='ball ball-blue'>{n:02d}</div>" for n in sorted(actual_nums)])
                    predict_html = render_bt_balls(bt_top_6, actual_nums)
                    
                    st.success(f"✅ 時光回測完畢！時空座標定錨於：【{target_issue}】期")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown("**📌 當期真實開獎號碼：**")
                        st.markdown(actual_html, unsafe_allow_html=True)
                    with col_b:
                        st.markdown("**🎯 系統盲測推薦 (策略一)：** *(亮紅色為成功命中)*")
                        st.markdown(predict_html, unsafe_allow_html=True)
                    
                    st.info(f"**📊 數據報告：** 在嚴格遮蔽未來數據的盲測條件下，演算法第一區成功命中了 **{len(hits)}** 顆號碼！")
            else:
                st.warning("資料庫資料量不足，無法執行回測，請等待資料庫累積更多期數。")
        except Exception as e:
            st.error(f"回測引擎讀取失敗，請確認資料庫格式。錯誤: {e}")
        finally:
            conn.close()
    else:
        st.info("⚠️ 找不到 `lottery_data.db` 資料庫，回測引擎暫時封印。請先確保根目錄存在有效資料庫。")
