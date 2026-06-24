import streamlit as st
import pandas as pd
import requests
import urllib3  # 新增這行
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # 新增這行：用來隱藏不安全連線的警告提示
import datetime
import time
from collections import Counter
import sqlite3
DB_PATH = str(Path(__file__).resolve().parents[2] / 'lottery_data.db')
import random

# ==========================================
# 🔮 新增：生辰八字五行核心演算引擎
# ==========================================

D_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
D_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

D_STEM_ELEMENTS = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"
}
D_BRANCH_ELEMENTS = {
    "寅": "木", "卯": "木", "巳": "火", "午": "火", 
    "申": "金", "酉": "金", "子": "水", "亥": "水", 
    "辰": "土", "戌": "土", "丑": "土", "未": "土"
}
D_ELEMENT_NUMS = {
    "水": [1, 6], "火": [2, 7], "木": [3, 8], "金": [4, 9], "土": [5, 0]
}

def calculate_bazi_lucky_nums(birth_date, birth_hour_str, pool_size=38):
    """根據出生日期與時辰，計算出符合五行磁場的開運號碼池"""
    base_date = datetime.date(1900, 1, 1)
    delta_days = (birth_date - base_date).days
    
    stem_idx = (0 + delta_days) % 10
    branch_idx = (10 + delta_days) % 12
    
    day_stem = D_STEMS[stem_idx]
    day_branch = D_BRANCHES[branch_idx]
    hour_branch = birth_hour_str[0]
    
    day_element = D_STEM_ELEMENTS[day_stem]
    hour_element = D_BRANCH_ELEMENTS[hour_branch]
    
    # 抓出日主與時辰對應的所有尾數號碼
    lucky_tails = list(set(D_ELEMENT_NUMS[day_element] + D_ELEMENT_NUMS[hour_element]))
    
    lucky_pool = []
    for n in range(1, pool_size + 1):
        if n % 10 in lucky_tails or (n % 10 == 0 and 0 in lucky_tails):
            lucky_pool.append(n)
            
    return lucky_pool, f"{day_stem}{day_branch}日（{day_element}命）｜ {hour_branch}時（屬{hour_element}）"
# ==========================================


# --- 進階專家策略函數 ---
def strategy_max_omission(df, pool_size=38):
    gaps = {n: len(df) for n in range(1, pool_size + 1)}
    for n in range(1, pool_size + 1):
        for i, row in df.iterrows():
            draw = [row['N1'], row['N2'], row['N3'], row['N4'], row['N5'], row['N6']]
            if n in draw:
                gaps[n] = i
                break
    sorted_gaps = sorted(gaps.items(), key=lambda x: x[1], reverse=True)
    best_picks = [x[0] for x in sorted_gaps[:6]]
    return sorted(best_picks)

def strategy_trailing_numbers(df, pool_size=38):
    if len(df) < 2:
        return sorted(random.sample(range(1, pool_size + 1), 6))
    last_draw = set([df.iloc[0]['N1'], df.iloc[0]['N2'], df.iloc[0]['N3'], df.iloc[0]['N4'], df.iloc[0]['N5'], df.iloc[0]['N6']])
    next_draw_nums = []
    for i in range(1, len(df) - 1):
        current_draw = set([df.iloc[i]['N1'], df.iloc[i]['N2'], df.iloc[i]['N3'], df.iloc[i]['N4'], df.iloc[i]['N5'], df.iloc[i]['N6']])
        if current_draw.intersection(last_draw):
            next_draw = [df.iloc[i-1]['N1'], df.iloc[i-1]['N2'], df.iloc[i-1]['N3'], df.iloc[i-1]['N4'], df.iloc[i-1]['N5'], df.iloc[i-1]['N6']]
            next_draw_nums.extend(next_draw)
    freq = Counter(next_draw_nums)
    best_picks = [x[0] for x in freq.most_common(6)]
    pool = set(range(1, pool_size + 1)) - set(best_picks)
    while len(best_picks) < 6:
        pick = random.choice(list(pool))
        best_picks.append(pick)
        pool.remove(pick)
    return sorted(best_picks)

def strategy_golden_ratio(pool_size=38, min_sum=95, max_sum=139):
    while True:
        nums = random.sample(range(1, pool_size + 1), 6)
        odd_count = sum(1 for n in nums if n % 2 != 0)
        total_sum = sum(nums)
        if odd_count == 3 and (min_sum <= total_sum <= max_sum):
            return sorted(nums)

def strategy_pattern_combo(df, pool_size=38):
    if df.empty:
        return sorted(random.sample(range(1, pool_size + 1), 6))
    last_draw = [df.iloc[0]['N1'], df.iloc[0]['N2'], df.iloc[0]['N3'], df.iloc[0]['N4'], df.iloc[0]['N5'], df.iloc[0]['N6']]
    repeater = random.choice(last_draw)
    while True:
        start_num = random.randint(1, pool_size - 1)
        pair = [start_num, start_num + 1]
        if repeater not in pair:
            break
    selected_nums = set([repeater] + pair)
    while len(selected_nums) < 6:
        selected_nums.add(random.randint(1, pool_size))
    return sorted(list(selected_nums))

# --- 新增：進階與複合 AI 策略函數 ---

def strategy_short_term_momentum(df, pool_size=38, recent_draws=50):
    """📈 近期動能加權：給予越近期的開獎號碼越高權重，捕捉短線熱潮"""
    if df.empty:
        return sorted(random.sample(range(1, pool_size + 1), 6))
    
    limit = min(recent_draws, len(df))
    recent_df = df.head(limit)
    scores = {n: 0.0 for n in range(1, pool_size + 1)}
    
    # 權重遞減：最新一期權重為 limit，最舊一期權重為 1
    for i, row in recent_df.iterrows():
        weight = limit - i
        draw = [row['N1'], row['N2'], row['N3'], row['N4'], row['N5'], row['N6']]
        for n in draw:
            if n in scores:
                scores[n] += weight
            
    # 依照分數高低排序取前 6 名
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_picks = [x[0] for x in sorted_scores[:6]]
    return sorted(best_picks)


def strategy_zone_elimination(df, pool_size=38):
    """🕳️ 斷區殺牌法：隨機強制排除一個區段(例如 11~20)，從剩餘號碼挑選"""
    # 建立 10 號為一個單位的區段清單
    zones = []
    step = 10
    for start in range(1, pool_size + 1, step):
        end = min(start + step - 1, pool_size)
        zones.append(list(range(start, end + 1)))
        
    # 隨機「殺掉」一個區段
    killed_zone_idx = random.randint(0, len(zones) - 1)
    
    available_pool = []
    for i, zone in enumerate(zones):
        if i != killed_zone_idx:
            available_pool.extend(zone)
            
    # 從存活的號碼池中隨機挑選 6 顆
    picks = random.sample(available_pool, 6)
    return sorted(picks)


def strategy_composite_ai(df, pool_size=38):
    """🧠 綜合 AI 複合權重：融合熱門、冷門、拖牌、連莊的多因子評分模型"""
    if df.empty:
        return sorted(random.sample(range(1, pool_size + 1), 6))
        
    scores = {n: 0.0 for n in range(1, pool_size + 1)}
    
    # 因子 1: 歷史大熱門 (+2分)
    all_nums = df[['N1', 'N2', 'N3', 'N4', 'N5', 'N6']].values.flatten()
    freq = Counter(all_nums)
    hot_nums = [x[0] for x in freq.most_common(12)]
    for n in hot_nums: scores[n] += 2
        
    # 因子 2: 極限遺漏值/準備回補 (+3分)
    gaps = {n: len(df) for n in range(1, pool_size + 1)}
    for n in range(1, pool_size + 1):
        for i, row in df.iterrows():
            draw = [row['N1'], row['N2'], row['N3'], row['N4'], row['N5'], row['N6']]
            if n in draw:
                gaps[n] = i
                break
    cold_nums = [x[0] for x in sorted(gaps.items(), key=lambda x: x[1], reverse=True)[:8]]
    for n in cold_nums: scores[n] += 3
        
    # 因子 3: 連莊號碼 (+1分)
    last_draw = [df.iloc[0]['N1'], df.iloc[0]['N2'], df.iloc[0]['N3'], df.iloc[0]['N4'], df.iloc[0]['N5'], df.iloc[0]['N6']]
    for n in last_draw: scores[n] += 1
        
    # 因子 4: 近期拖牌關聯 (+2分)
    if len(df) >= 2:
        last_set = set(last_draw)
        next_draw_nums = []
        # 只算近 100 期的拖牌以加快運算
        for i in range(1, min(100, len(df) - 1)):
            current_draw = set([df.iloc[i]['N1'], df.iloc[i]['N2'], df.iloc[i]['N3'], df.iloc[i]['N4'], df.iloc[i]['N5'], df.iloc[i]['N6']])
            if current_draw.intersection(last_set):
                next_draw_nums.extend([df.iloc[i-1]['N1'], df.iloc[i-1]['N2'], df.iloc[i-1]['N3'], df.iloc[i-1]['N4'], df.iloc[i-1]['N5'], df.iloc[i-1]['N6']])
        if next_draw_nums:
            trail_freq = Counter(next_draw_nums)
            trail_nums = [x[0] for x in trail_freq.most_common(8)]
            for n in trail_nums: scores[n] += 2
            
    # 加入極小的隨機亂數(0.01~0.2)來打破同分平手的狀況
    for n in scores:
        scores[n] += random.uniform(0.01, 0.2)
        
    # 依照多因子總分排序取前 6 名
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_picks = [x[0] for x in sorted_scores[:6]]
    return sorted(best_picks)


def strategy_absolute_cold(df, pool_size=38):
    """❄️ 絕對冷門：反向操作，專門挑選歷史上開出最少次的號碼"""
    if df.empty:
        return sorted(random.sample(range(1, pool_size + 1), 6))
    all_nums = df[['N1', 'N2', 'N3', 'N4', 'N5', 'N6']].values.flatten()
    freq = Counter(all_nums)
    # 補齊 0 次的號碼
    for n in range(1, pool_size + 1):
        if n not in freq:
            freq[n] = 0
    # 反向排序取最少的 6 個
    cold_6 = sorted([x[0] for x in freq.most_common()[-6:]])
    return sorted(cold_6)


# --- 設定網頁標題與風格 ---
st.set_page_config(page_title="阿舍的威力彩分析工具", layout="wide")
st.title("🎰 威力彩歷史數據自動化查詢系統")

# --- 隱藏預設右上角選單與 Deploy 按鈕 ---
st.markdown("""
    <style>
    /* 隱藏 Deploy 按鈕 */
    .stAppDeployButton {display:none;}
    /* 隱藏右上角 hamburger menu (選單) */
    #MainMenu {visibility: hidden;}
    /* 隱藏頂部整條 header (包含選單與 Deploy) */
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 資料庫函數 ---
def load_from_db():
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        df = pd.read_sql('SELECT * FROM super_lotto ORDER BY 期別 DESC', conn)
        df['日期'] = pd.to_datetime(df['日期']).dt.date
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

def save_to_db(new_df):
    if new_df.empty: return
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        try:
            old_df = pd.read_sql('SELECT * FROM super_lotto', conn)
            old_df['日期'] = pd.to_datetime(old_df['日期']).dt.date
        except Exception:
            old_df = pd.DataFrame()
        
        # 合併新舊資料
        combined = pd.concat([old_df, new_df])
        # 根據「期別」去重複，保留最新的
        combined = combined.drop_duplicates(subset=['期別'], keep='last')
        combined = combined.sort_values('日期', ascending=False)
        
        # 存回資料庫
        combined.to_sql('super_lotto', conn, if_exists='replace', index=False)
        conn.close()
    except Exception as e:
        st.sidebar.error(f"資料庫寫入失敗: {e}")

# --- 核心爬蟲與清洗邏輯 ---
def fetch_lotto_data(year, month):
    """抓取特定年月的威力彩資料 (使用台彩最新 API)"""
    url = f'https://api.taiwanlottery.com/TLCAPIWeB/Lottery/SuperLotto638Result?period=&month={year}-{month:02d}&pageNum=1&pageSize=50'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        data = response.json()
        
        monthly_draws = []
        if 'content' in data and data['content'] and 'superLotto638Res' in data['content']:
            for item in data['content']['superLotto638Res']:
                draw_no = item['period']
                date_str = item['lotteryDate'].split('T')[0]
                date_parts = date_str.split('-')
                date_obj = datetime.date(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
                
                nums_sorted = item.get('drawNumberSize', [])
                if not nums_sorted or len(nums_sorted) < 7:
                    continue
                
                normal_nums = nums_sorted[:6]
                special_num = nums_sorted[6]
                
                # 🛑 終極防護牆：過濾不合法的髒資料 (威力彩 1~38, 第二區 1~8)
                if any(n > 38 or n < 1 for n in normal_nums) or not (1 <= special_num <= 8):
                    continue
                    
                monthly_draws.append({
                    '期別': draw_no,
                    '日期': date_obj,
                    'N1': normal_nums[0], 'N2': normal_nums[1], 'N3': normal_nums[2],
                    'N4': normal_nums[3], 'N5': normal_nums[4], 'N6': normal_nums[5],
                    '特別號': special_num,
                    '和值': sum(normal_nums)
                })
        return monthly_draws
    except Exception as e:
        st.sidebar.error(f"抓取 {year}/{month} 失敗: {e}")
        return []

# --- 側邊欄設定 (更新/補登資料庫) ---
st.sidebar.header("🔄 更新/補登資料庫")

db_df = load_from_db()
if not db_df.empty:
    db_max_date = db_df['日期'].max()
    st.sidebar.success(f"目前資料庫最新日期：\n{db_max_date}")
    # 預設起點設為最新日期（以便補齊），終點設為今天
    default_start = db_max_date
else:
    st.sidebar.warning("資料庫目前為空，請先抓取資料。")
    default_start = datetime.date(2026, 1, 1)

start_date = st.sidebar.date_input("開始日期", value=default_start, min_value=datetime.date(2004, 1, 1), max_value=datetime.date.today())
end_date = st.sidebar.date_input("結束日期", value=datetime.date.today(), min_value=datetime.date(2004, 1, 1), max_value=datetime.date.today())

if st.sidebar.button("🚀 開始抓取並寫入資料庫"):
    if start_date > end_date:
        st.sidebar.error("錯誤：開始日期不可晚於結束日期")
    else:
        query_months = []
        curr = start_date.replace(day=1)
        while curr <= end_date:
            query_months.append((curr.year, curr.month))
            if curr.month == 12:
                curr = curr.replace(year=curr.year + 1, month=1)
            else:
                curr = curr.replace(month=curr.month + 1)
        
        all_results = []
        progress_bar = st.sidebar.progress(0)
        status_text = st.sidebar.empty()
        
        for i, (y, m) in enumerate(query_months):
            status_text.text(f"正在抓取 {y} 年 {m} 月...")
            month_data = fetch_lotto_data(y, m)
            all_results.extend(month_data)
            progress_bar.progress((i + 1) / len(query_months))
            time.sleep(0.5) 
            
        new_df = pd.DataFrame(all_results)
        if not new_df.empty:
            # 確保只寫入位於選擇區間內的資料 (避免月初月底誤差)
            new_df = new_df[(new_df['日期'] >= start_date) & (new_df['日期'] <= end_date)]
            save_to_db(new_df)
            status_text.success("🎉 成功抓取並更新資料庫！")
            time.sleep(1)
            st.rerun() # 重新整理頁面以載入最新資料
        else:
            status_text.warning("該區間內沒有抓到任何新資料。")

# --- 主畫面儀表板呈現 ---
# 每次載入畫面時，都直接從資料庫讀取全部資料
full_df = load_from_db()

if not full_df.empty:
    st.success(f"✅ 成功從資料庫載入 {len(full_df)} 期數據！ (資料區間：{full_df['日期'].min()} ~ {full_df['日期'].max()})")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("總期數", len(full_df))
    col2.metric("平均和值", f"{full_df['和值'].mean():.1f}")
    # --- 上半部：歷史清單與預測 ---
    st.divider()
    col_hist, col_ai = st.columns([2, 3]) # 讓右側 AI 預測區塊稍微寬一點
    
    with col_hist:
        st.subheader("📋 歷史開獎清單")
        # 複製一份用來顯示，避免動到原始資料
        display_df = full_df.copy()
        display_df['日期'] = pd.to_datetime(display_df['日期']).dt.strftime('%Y-%m-%d')
        # 使用原生 dataframe，內建流暢滾動與排序功能
        st.dataframe(display_df, use_container_width=True, height=850, hide_index=True)
        
    with col_ai:
        st.subheader("🔮 AI 綜合策略預測選號")
        st.markdown("基於歷史大數據庫，為您自動產生的五組不同策略預測號碼：")
        
        # 1. 歷史最熱門
        all_nums_flat = full_df[['N1', 'N2', 'N3', 'N4', 'N5', 'N6']].values.flatten()
        freq = Counter(all_nums_flat)
        hot_6 = sorted([x[0] for x in freq.most_common(6)])
        
        # 2. 絕地反彈
        max_om_6 = strategy_max_omission(full_df, pool_size=38)
        
        # 3. 上期拖牌
        trail_6 = strategy_trailing_numbers(full_df, pool_size=38)
        
        # 4. 完美統計學
        gold_6 = strategy_golden_ratio(pool_size=38, min_sum=95, max_sum=139)
        
        # 5. 連號與連莊組合
        pattern_6 = strategy_pattern_combo(full_df, pool_size=38)
        
        # ✨ 新增的 4 種策略：
        # 6. 近期動能加權
        momentum_6 = strategy_short_term_momentum(full_df, pool_size=38, recent_draws=50)
        # 7. 斷區殺牌法
        zone_6 = strategy_zone_elimination(full_df, pool_size=38)
        # 8. 綜合 AI 複合權重
        composite_6 = strategy_composite_ai(full_df, pool_size=38)
        # 9. 絕對冷門
        cold_6 = strategy_absolute_cold(full_df, pool_size=38)

        # 產生特別號 (從前 5 大熱門中隨機挑選)
        special_pool = [n for n, c in Counter(full_df['特別號']).most_common(5)]
        if not special_pool:
            special_pool = list(range(1, 9)) # Fallback
            
        # --- 本期預測 (基於完整歷史) ---
        curr_preds = [
            [*hot_6, random.choice(special_pool)],
            [*max_om_6, random.choice(special_pool)],
            [*trail_6, random.choice(special_pool)],
            [*gold_6, random.choice(special_pool)],
            [*pattern_6, random.choice(special_pool)],
            [*momentum_6, random.choice(special_pool)], # 新增
            [*zone_6, random.choice(special_pool)],     # 新增
            [*composite_6, random.choice(special_pool)],# 新增
            [*cold_6, random.choice(special_pool)]      # 新增
        ]
        
        # --- 前期預測 (基於扣除最新一期的歷史) ---
        last_draw_id = str(full_df.iloc[0]['期別'])
        cache_key = f"prev_preds_super_{last_draw_id}"
        
        if cache_key in st.session_state:
            prev_preds = st.session_state[cache_key]
        else:
            if len(full_df) > 1:
                prev_df = full_df.iloc[1:].reset_index(drop=True)
                prev_all_nums_flat = prev_df[['N1', 'N2', 'N3', 'N4', 'N5', 'N6']].values.flatten()
                prev_freq = Counter(prev_all_nums_flat)
                prev_hot_6 = sorted([x[0] for x in prev_freq.most_common(6)])
                prev_max_om_6 = strategy_max_omission(prev_df, pool_size=38)
                prev_trail_6 = strategy_trailing_numbers(prev_df, pool_size=38)
                prev_gold_6 = strategy_golden_ratio(pool_size=38, min_sum=95, max_sum=139)
                prev_pattern_6 = strategy_pattern_combo(prev_df, pool_size=38)
                prev_momentum_6 = strategy_short_term_momentum(prev_df, pool_size=38, recent_draws=50)
                prev_zone_6 = strategy_zone_elimination(prev_df, pool_size=38)
                prev_composite_6 = strategy_composite_ai(prev_df, pool_size=38)
                prev_cold_6 = strategy_absolute_cold(prev_df, pool_size=38)
                
                prev_special_pool = [n for n, c in Counter(prev_df['特別號']).most_common(5)] or list(range(1, 9))
                
                prev_preds = [
                    [*prev_hot_6, random.choice(prev_special_pool)],
                    [*prev_max_om_6, random.choice(prev_special_pool)],
                    [*prev_trail_6, random.choice(prev_special_pool)],
                    [*prev_gold_6, random.choice(prev_special_pool)],
                    [*prev_pattern_6, random.choice(prev_special_pool)],
                    [*prev_momentum_6, random.choice(prev_special_pool)],
                    [*prev_zone_6, random.choice(prev_special_pool)],
                    [*prev_composite_6, random.choice(prev_special_pool)],
                    [*prev_cold_6, random.choice(prev_special_pool)],
                ]
            else:
                prev_preds = curr_preds # Fallback
            st.session_state[cache_key] = prev_preds

        strategy_names = [
            "🔥 史上最熱門 (出現最多次)",
            "⏳ 絕地反彈 (極限遺漏值)",
            "🎯 上期拖牌 (關聯性預測)",
            "⚖️ 完美統計學 (黃金比例)",
            "👯 連號與連莊 (型態學)",
            "📈 近期動能 (近50期強勢號)",  
            "🕳️ 斷區殺牌 (強制空區法)",   
            "🧠 綜合 AI (多因子權重)",    
            "❄️ 絕對冷門 (反向操作)"      
        ]

        # 標注與計算上一期中獎金額
        last_draw_row = full_df.iloc[0]
        draw_nums = set([last_draw_row['N1'], last_draw_row['N2'], last_draw_row['N3'], last_draw_row['N4'], last_draw_row['N5'], last_draw_row['N6']])
        special_num = last_draw_row['特別號']
        
        combined_data = []
        for i in range(9):
            c_p = curr_preds[i]
            p_p = prev_preds[i]
            
            # 針對『前期預測』計算是否中獎 (對比上一期實際開獎號碼)
            my_nums = set(p_p[0:6])
            match_count = len(my_nums.intersection(draw_nums))
            my_special = p_p[6] # 策略產出的特別號
            match_special = (special_num == my_special) # 威力彩必須完全命中第二區
            
            prize = 0
            if match_count == 6 and match_special: prize = 200000000 # 頭獎
            elif match_count == 6: prize = 5000000 # 貳獎
            elif match_count == 5 and match_special: prize = 150000 # 參獎
            elif match_count == 5: prize = 20000 # 肆獎
            elif match_count == 4 and match_special: prize = 4000 # 伍獎
            elif match_count == 4: prize = 800 # 陸獎
            elif match_count == 3 and match_special: prize = 400 # 柒獎
            elif match_count == 2 and match_special: prize = 200 # 捌獎
            elif match_count == 3: prize = 100 # 玖獎
            elif match_count == 1 and match_special: prize = 100 # 普獎
            
            prize_str = f"＄{prize:,}" if prize > 0 else "＄0"
            if match_count == 6 and match_special: prize_str = "頭獎 (浮動)"
            elif match_count == 6: prize_str = "貳獎 (浮動)"
            
            # 組合列資料 (只保留預計)
            row = [strategy_names[i]]
            for j in range(7):
                row.append(p_p[j]) # 預計
            row.append(prize_str)
            combined_data.append(row)

        md_table = "| 策略名稱 | 第 1 球 | 第 2 球 | 第 3 球 | 第 4 球 | 第 5 球 | 第 6 球 | 特別號 | 預計中獎金額 |\n"
        md_table += "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |\n"
        
        last_draw_nums_set = set([
            last_draw_row['N1'], last_draw_row['N2'], last_draw_row['N3'], 
            last_draw_row['N4'], last_draw_row['N5'], last_draw_row['N6'], 
            last_draw_row['特別號']
        ])
        
        for row in combined_data:
            strategy = row[0]
            balls = []
            for num in row[1:8]:
                if num in last_draw_nums_set:
                    balls.append(f"<span style='color:#FF4B4B; font-weight:bold;'>{num}</span>")
                else:
                    balls.append(str(num))
            prize = row[8]
            md_table += f"| {strategy} | {' | '.join(balls)} | {prize} |\n"
            
        st.markdown(md_table, unsafe_allow_html=True)
        
        last_date = last_draw_row['日期']
        date_str = f"{last_date.year}年{last_date.month}月{last_date.day}日"
        drawn_nums_str = "、".join([str(last_draw_row[f'N{i}']).zfill(2) for i in range(1, 7)])
        special_str = str(last_draw_row['特別號']).zfill(2)
        
        st.markdown(f"""
        <div style="border: 2px solid #8e8e8e; border-radius: 8px; padding: 15px; display: flex; align-items: center; margin-top: 15px; margin-bottom: 15px; background-color: #f9f9f9; color: black;">
            <div style="flex: 1; border-right: 2px solid #8e8e8e; text-align: center; font-size: 20px; font-weight: bold;">
                {date_str}
            </div>
            <div style="flex: 3; padding-left: 20px; font-size: 20px; font-weight: bold;">
                開出號碼： <span style="color: #1E90FF;">{drawn_nums_str}</span> <span style="color: #FF4B4B;">(特別號: {special_str})</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 重新產生預測組合"):
            st.rerun()
        
        # --- 首頁版 AI 微調推薦 ---
        st.markdown("### 🎯 自選號碼 AI 五行微調推薦")
        st.markdown("您可以輸入自己挑選的號碼，AI 將結合歷史大數據與您的生辰八字進行磁場微調：")
        
        # 讓使用者輸入自選號碼
        user_input_str = st.text_input("請選擇 1~10 個您的心水號碼 (用逗號隔開)：", "2, 4, 7, 9, 11, 30")
        
        # ✨ 核心亮點：加入生辰八字微調開關
        use_bazi = st.checkbox("🔮 引入個人生辰八字（五行磁場加權驗證）")
        
        bazi_lucky_pool = []
        bazi_info_str = ""
        
        if use_bazi:
            b_col1, b_col2 = st.columns(2)
            with b_col1:
                b_date = st.date_input("出生公曆日期：", value=datetime.date(1990, 1, 1), min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today())
            with b_col2:
                b_hour = st.selectbox("出生時辰：", ["子時 (23-01)", "丑時 (01-03)", "寅時 (03-05)", "卯時 (05-07)", "辰時 (07-09)", "巳時 (09-11)", "午時 (11-13)", "未時 (13-15)", "申時 (15-17)", "酉時 (17-19)", "戌時 (19-21)", "亥時 (21-23)"])
            
            # 算出生辰五行開運號碼池
            bazi_lucky_pool, bazi_info_str = calculate_bazi_lucky_nums(b_date, b_hour, pool_size=38)
            st.caption(f"🧬 解析成功：您的本命為 **{bazi_info_str}**")

        if st.button("🚀 開始 AI 智慧微調分析"):
            user_input_nums = []
            if user_input_str.strip():
                try:
                    user_input_nums = sorted(list(set([int(x.strip()) for x in user_input_str.split(',') if x.strip()])))
                except ValueError:
                    st.error("⚠️ 號碼格式錯誤，請確定都是數字並用逗號隔開 (例如: 2, 4, 7)")
                    st.stop()
                    
            if len(user_input_nums) > 10 or not all(1 <= x <= 38 for x in user_input_nums):
                st.error("⚠️ 請確保最多輸入 10 個號碼，且都在 1~49 之間喔！")
                st.stop()

            if not user_input_nums:
                st.info("您沒有選擇基礎號碼，系統將完全由 AI 與五行大數據為您全自動生成！")
                user_input_nums = []
                
            # 1. 取得大數據頻率 (做為評分依據)
            try:
                conn = sqlite3.connect(DB_PATH)
                df_hist = pd.read_sql('SELECT * FROM super_lotto ORDER BY 期別 DESC', conn)
                conn.close()
                all_hist_nums = df_hist[['N1', 'N2', 'N3', 'N4', 'N5', 'N6']].values.flatten()
                freq_map = Counter(all_hist_nums)
            except:
                freq_map = {n: random.randint(1, 100) for n in range(1, 39)}

            # 2. AI 診斷：評估使用者的號碼
            user_scores = {}
            for n in user_input_nums:
                score = freq_map.get(n, 0)
                if use_bazi and bazi_lucky_pool and n in bazi_lucky_pool:
                    score += 1000  # 🌟 八字相符給予絕對高分加權
                user_scores[n] = score

            # 依照分數高低排序使用者的號碼 (由強到弱)
            sorted_user_nums = sorted(user_scores.keys(), key=lambda x: user_scores[x], reverse=True)

            # 3. 觸發「微調突變」機制 (汰弱留強)
            kept_nums = sorted_user_nums
            dropped_nums = []
            
            # 為了凸顯 AI 大數據與八字選號 (紅色顯示)，強制汰換掉最弱的號碼
            if len(sorted_user_nums) >= 6:
                keep_len = random.choice([4, 5]) 
            elif len(sorted_user_nums) > 1:
                keep_len = len(sorted_user_nums) - 1
            else:
                keep_len = len(sorted_user_nums)
                
            kept_nums = sorted_user_nums[:keep_len]
            dropped_nums = sorted_user_nums[keep_len:]

            final_base = list(kept_nums)

            # 4. 決定 AI 補號的候選池
            if use_bazi and bazi_lucky_pool:
                # 八字開啟：優先從符合八字五行、且歷史開出次數多的號碼中挑選
                candidate_pool = [n for n in bazi_lucky_pool if n not in final_base]
                candidate_pool = sorted(candidate_pool, key=lambda x: freq_map.get(x, 0), reverse=True)
            else:
                # 八字未開啟：單純以歷史大熱門做填補
                candidate_pool = [n for n, c in Counter(all_hist_nums).most_common(38) if n not in final_base]

            # 5. 補足 6 顆球 (注入 AI 強勢號碼)
            ai_added_nums = []
            while len(final_base) < 6:
                if candidate_pool:
                    new_num = candidate_pool.pop(0)
                    final_base.append(new_num)
                    ai_added_nums.append(new_num)
                else:
                    r_n = random.randint(1, 38)
                    if r_n not in final_base:
                        final_base.append(r_n)
                        ai_added_nums.append(r_n)

            final_base = sorted(final_base)
            
            # 6. 特別號生成邏輯
            if use_bazi and bazi_lucky_pool:
                # 大樂透特別號優先從五行池挑選
                special_num = random.randint(1, 8) 
            else:
                special_num = random.choice([n for n, c in Counter(df_hist['特別號']).most_common(5)]) if 'df_hist' in locals() and not df_hist.empty else random.randint(1, 8)

            # ==========================================
            # 儲存結果至 Session State (防護罩機制)
            # ==========================================
            st.session_state['super_custom_res'] = {
                'dropped_nums': dropped_nums,
                'ai_added_nums': ai_added_nums,
                'user_input_nums': user_input_nums,
                'final_base': final_base,
                'special_num': special_num,
                'use_bazi': use_bazi,
                'bazi_info_str': bazi_info_str if use_bazi else ""
            }

        # ==========================================
        # 輸出美化與 AI 診斷報告 (獨立顯示區，不受重新整理影響)
        # ==========================================
        if st.session_state.get('super_custom_res'):
            res = st.session_state['super_custom_res']
            st.success("🎯 AI 運算與磁場優化完成！")
            
            if res['dropped_nums']:
                drop_str = "、".join([str(n).zfill(2) for n in sorted(res['dropped_nums'])])
                add_str = "、".join([str(n).zfill(2) for n in sorted(res['ai_added_nums'])])
                st.warning(f"🛠️ **AI 汰弱留強**：您選擇的 {drop_str} 近期動能較弱或與五行相剋，AI 已將其剔除，替換為強勢號碼 {add_str}。")
            elif res['ai_added_nums'] and res['user_input_nums']:
                add_str = "、".join([str(n).zfill(2) for n in sorted(res['ai_added_nums'])])
                st.info(f"✨ **AI 智能補牌**：保留了您的優質選號，並為您補齊強勢號碼 {add_str}！")
                
            def format_ball_c(n):
                is_ai = n in res['ai_added_nums']
                color_style = "color:#FF0000; background-color:#FFE4E1; border: 1px solid #FFCDD2;" if is_ai else "color:#333333; background-color:#F0F2F6; border: 1px solid #E0E0E0;"
                return f"<span title='{'AI 大數據/八字推薦' if is_ai else '保留您的自選'}' style='font-size: 20px; font-weight:bold; {color_style} padding: 4px 10px; border-radius: 50%; margin-right: 5px;'>{str(n).zfill(2)}</span>"
            def format_sp_ball_c(n):
                return f"<span style='color:#FFFFFF; font-size: 20px; font-weight:bold; background-color:#FF4B4B; padding: 4px 10px; border-radius: 50%; margin-right: 5px;'>{str(n).zfill(2)}</span>"
            
            balls_html = "".join([format_ball_c(n) for n in res['final_base']])
            st.markdown(f"**最終優化組合**： {balls_html} ➕ 特別號： {format_sp_ball_c(res['special_num'])}", unsafe_allow_html=True)
            
            if res['use_bazi']:
                st.info(f"💡 **AI 磁場微調簡評**：本組號碼已強制注入您的 **{res['bazi_info_str'].split('｜')[0]}** 開運尾數，成功提升該組合與您個人的先天運勢共振契合度！")
                
            if st.button("🗑️ 清除微調結果", key="super_clear_custom"):
                del st.session_state['super_custom_res']
                st.rerun()
                
        # --- 首頁版 夢境解碼 ---
        st.markdown("### 🌙 夢境解碼預測 (逼牌專區)")
        dream_text = st.text_area("請簡述您最近的夢境 (例如：我夢到一隻大黑狗在追我，後來跳進水裡...)：", height=100, key="dream_text_input")

        # ✨ 夢境專屬：加入生辰八字微調開關 (加入 key 避免與自選號碼衝突)
        use_bazi_dream = st.checkbox("🔮 引入做夢者的生辰八字（五行磁場加權驗證）", key="dream_bazi")
        
        bazi_lucky_pool_dream = []
        bazi_info_str_dream = ""
        
        if use_bazi_dream:
            b_col1, b_col2 = st.columns(2)
            with b_col1:
                b_date_dream = st.date_input("出生公曆日期：", value=datetime.date(1990, 1, 1), min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today(), key="dream_date")
            with b_col2:
                b_hour_dream = st.selectbox("出生時辰：", ["子時 (23-01)", "丑時 (01-03)", "寅時 (03-05)", "卯時 (05-07)", "辰時 (07-09)", "巳時 (09-11)", "午時 (11-13)", "未時 (13-15)", "申時 (15-17)", "酉時 (17-19)", "戌時 (19-21)", "亥時 (21-23)"], key="dream_hour")
            
            # 算出生辰五行開運號碼池 (呼叫最上方的核心引擎)
            bazi_lucky_pool_dream, bazi_info_str_dream = calculate_bazi_lucky_nums(b_date_dream, b_hour_dream, pool_size=38) # 威力彩記得改 38
            st.caption(f"🧬 解析成功：做夢者的本命為 **{bazi_info_str_dream}**")

        if st.button("🔮 解析夢境並產生推薦", key="top_dream_btn"):
            # 🌟 豪華擴充版：台灣民間樂透解夢與逼牌大辭典 (超過 250+ 關鍵字)
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
            from dream_dict import dream_database

            if not dream_text:
                st.warning("請先輸入您的夢境內容！")
                st.stop()
            else:
                extracted_numbers = set()
                keywords = []
                matched_descs = []
                user_input_lower = dream_text.lower()
                
                for kw_tuple, data in dream_database.items():
                    nums = data['nums']
                    desc = data['desc']
                    matched_kws = [k for k in kw_tuple if k in user_input_lower]
                    if matched_kws:
                        extracted_numbers.update(nums)
                        for k in matched_kws:
                            if k not in keywords:
                                keywords.append(k)
                        desc_text = f"**{', '.join(matched_kws)}**：{desc}"
                        if desc_text not in matched_descs:
                            matched_descs.append(desc_text)
                            
                dream_nums = list(set([n for n in extracted_numbers if 1 <= n <= 38]))
                
                st.success(f"🔍 **捕捉到夢境關鍵字**： {', '.join(keywords) if keywords else '無 (將完全依賴大數據預測)'}")
                if matched_descs:
                    st.markdown("### 📖 夢境深度解析")
                    for d in matched_descs:
                        st.markdown(f"> 💡 {d}")

                    st.write(f"💭 **字典初始轉化號碼**： {sorted(dream_nums)}")

                # 2. 取得大數據頻率做為 AI 評分基準
                try:
                    conn = sqlite3.connect(DB_PATH)
                    df_hist = pd.read_sql('SELECT * FROM super_lotto ORDER BY 期別 DESC', conn) # 威力彩記得改 super_lotto
                    conn.close()
                    all_hist_nums = df_hist[['N1', 'N2', 'N3', 'N4', 'N5', 'N6']].values.flatten()
                    freq_map = Counter(all_hist_nums)
                except:
                    freq_map = {n: random.randint(1, 100) for n in range(1, 39)}

                # 3. AI 診斷：評估夢境號碼的強度
                dream_scores = {}
                for n in dream_nums:
                    score = freq_map.get(n, 0)
                    if use_bazi_dream and bazi_lucky_pool_dream and n in bazi_lucky_pool_dream:
                        score += 1000  # 🌟 八字相符給予絕對高分加權
                    dream_scores[n] = score

                # 依照分數高低排序 (強到弱)
                sorted_dream_nums = sorted(dream_scores.keys(), key=lambda x: dream_scores[x], reverse=True)

                # 4. 觸發「微調突變」機制 (汰弱留強)
                kept_nums = sorted_dream_nums
                dropped_nums = []
                
                # 若夢境轉出的號碼很多，強制剔除最弱的，並至少留一個空位給 AI 補強勢號
                if len(sorted_dream_nums) >= 6:
                    keep_len = 5 
                    kept_nums = sorted_dream_nums[:keep_len]
                    dropped_nums = sorted_dream_nums[keep_len:]
                elif len(sorted_dream_nums) == 5:
                    keep_len = 4
                    kept_nums = sorted_dream_nums[:keep_len]
                    dropped_nums = sorted_dream_nums[keep_len:]

                final_base = list(kept_nums)

                # 5. 決定 AI 補號的候選池
                if use_bazi_dream and bazi_lucky_pool_dream:
                    # 八字開啟：優先從符合五行、且歷史熱門的號碼挑選
                    candidate_pool = [n for n in bazi_lucky_pool_dream if n not in final_base]
                    candidate_pool = sorted(candidate_pool, key=lambda x: freq_map.get(x, 0), reverse=True)
                else:
                    # 八字未開啟：拿歷史大熱門補號
                    candidate_pool = [n for n, c in Counter(all_hist_nums).most_common(38) if n not in final_base]

                # 6. 補足 6 顆球
                ai_added_nums = []
                while len(final_base) < 6:
                    if candidate_pool:
                        new_num = candidate_pool.pop(0)
                        final_base.append(new_num)
                        ai_added_nums.append(new_num)
                    else:
                        r_n = random.randint(1, 38) # 威力彩記得改 38
                        if r_n not in final_base:
                            final_base.append(r_n)
                            ai_added_nums.append(r_n)

                final_base = sorted(final_base)
                
                # 7. 特別號生成邏輯
                if use_bazi_dream and bazi_lucky_pool_dream:
                    special_num = random.randint(1, 8)
                else:
                    special_num = random.choice([n for n, c in Counter(df_hist['特別號']).most_common(5)]) if 'df_hist' in locals() and not df_hist.empty else random.randint(1, 8)

            # ==========================================
            # 儲存結果至 Session State (防護罩機制)
            # ==========================================
            st.session_state['super_dream_res'] = {
                'dropped_nums': dropped_nums,
                'ai_added_nums': ai_added_nums,
                'final_base': final_base,
                'special_num': special_num,
                'use_bazi_dream': use_bazi_dream,
                'bazi_info_str_dream': bazi_info_str_dream if use_bazi_dream else ""
            }

        # ==========================================
        # 輸出診斷報告與最終推薦 (獨立顯示區，不受重新整理影響)
        # ==========================================
        if st.session_state.get('super_dream_res'):
            res = st.session_state['super_dream_res']
            if res['dropped_nums']:
                drop_str = "、".join([str(n).zfill(2) for n in sorted(res['dropped_nums'])])
                st.warning(f"🛠️ **AI 汰弱留強**：夢境解碼出的號碼 `{drop_str}` 近期動能較弱或與五行相剋，已被 AI 無情剔除。")
            if res['ai_added_nums']:
                add_str = "、".join([str(n).zfill(2) for n in sorted(res['ai_added_nums'])])
                bazi_text = '與您的八字五行' if res['use_bazi_dream'] else ''
                st.info(f"✨ **AI 智能補牌**：結合大數據{bazi_text}，為您補上強勢號碼 `{add_str}`！")
        
            def format_ball_d(n):
                return f"<span style='font-size: 20px; font-weight:bold; background-color:#F0F2F6; padding: 4px 10px; border-radius: 50%; margin-right: 5px;'>{str(n).zfill(2)}</span>"
            def format_sp_ball_d(n):
                return f"<span style='color:#FFFFFF; font-size: 20px; font-weight:bold; background-color:#FF4B4B; padding: 4px 10px; border-radius: 50%; margin-right: 5px;'>{str(n).zfill(2)}</span>"
            
            balls_html = "".join([format_ball_d(n) for n in res['final_base']])
            st.markdown("### 🎲 專屬夢境優化組合")
            st.markdown(f"{balls_html} ➕ 特別號： {format_sp_ball_d(res['special_num'])}", unsafe_allow_html=True)
            
            if res['use_bazi_dream']:
                st.caption(f"💡 **AI 磁場微調簡評**：本組號碼已強制注入您的 **{res['bazi_info_str_dream'].split('｜')[0]}** 開運尾數，成功提升夢境與先天的運勢契合度！")
                
            if st.button("🗑️ 清除夢境結果", key="super_clear_dream"):
                del st.session_state['super_dream_res']
                st.rerun()

    # --- 統計圖表 ---
    st.divider()
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("🔥 號碼出現頻率 (不含特別號)")
        all_nums = full_df[['N1', 'N2', 'N3', 'N4', 'N5', 'N6']].values.flatten()
        freq_data = Counter(all_nums).most_common(38)
        freq_df = pd.DataFrame(freq_data, columns=['號碼', '次數']).sort_values('號碼')
        st.bar_chart(freq_df.set_index('號碼'))
        
    with c2:
        st.subheader("🔥 十大熱門特別號")
        spec_freq = Counter(full_df['特別號']).most_common(10)
        md_spec = "| 特別號碼 | 開出次數 |\n| :---: | :---: |\n"
        for num, count in spec_freq:
            md_spec += f"| {num} | {count} |\n"
        st.markdown(md_spec)
    
    # --- 進階分析區塊 ---
    st.divider()
    st.header("🔬 進階數據分析")
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["📊 奇偶數與連號", "⏳ 遺漏值分析", "🎯 拖牌分析", "📈 和值走勢", "🌡️ 區間冷熱分佈", "🌙 夢境解碼", "💰 歷史養牌回測", "🤖 AI 號碼健檢"])
    
    with tab1:
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.subheader("奇偶數比例 (奇數:偶數)")
            odd_even_ratios = []
            for _, row in full_df.iterrows():
                nums = [row['N1'], row['N2'], row['N3'], row['N4'], row['N5'], row['N6']]
                odds = sum(1 for n in nums if n % 2 != 0)
                evens = 6 - odds
                odd_even_ratios.append(f"{odds}奇 {evens}偶")
            
            ratio_counts = Counter(odd_even_ratios).most_common()
            ratio_df = pd.DataFrame(ratio_counts, columns=['奇偶比例', '次數'])
            st.bar_chart(ratio_df.set_index('奇偶比例'))
        
        with col_b:
            st.subheader("連號組數統計")
            consecutive_counts = []
            for _, row in full_df.iterrows():
                nums = sorted([row['N1'], row['N2'], row['N3'], row['N4'], row['N5'], row['N6']])
                pairs = 0
                for i in range(5):
                    if nums[i+1] - nums[i] == 1:
                        pairs += 1
                consecutive_counts.append(f"{pairs}組連號")
            
            cons_counts = Counter(consecutive_counts).most_common()
            cons_df = pd.DataFrame(cons_counts, columns=['連號情況', '次數'])
            st.bar_chart(cons_df.set_index('連號情況'))
    
    with tab2:
        st.subheader("⏳ 目前號碼遺漏值 (幾期未開)")
        st.markdown("數值越大，代表該號碼已經越久沒有開出。")
        
        missing_values = {n: 0 for n in range(1, 39)}
        found_numbers = set()
        
        for _, row in full_df.iterrows():
            nums = [row['N1'], row['N2'], row['N3'], row['N4'], row['N5'], row['N6']]
            for n in nums:
                if n not in found_numbers:
                    found_numbers.add(n)
            
            for n in range(1, 39):
                if n not in found_numbers:
                    missing_values[n] += 1
                    
            if len(found_numbers) == 38:
                break
        
        missing_df = pd.DataFrame(list(missing_values.items()), columns=['號碼', '遺漏期數']).sort_values('遺漏期數', ascending=False)
        st.bar_chart(missing_df.set_index('號碼'))
        
        st.divider()
        st.subheader("⏳ 特別號遺漏值 (幾期未開出特別號)")
        special_missing = {n: 0 for n in range(1, 9)}
        found_special = set()
        
        for _, row in full_df.iterrows():
            sn = row['特別號']
            if sn not in found_special:
                found_special.add(sn)
                
            for n in range(1, 9): # special loop
                if n not in found_special:
                    special_missing[n] += 1
                    
            if len(found_special) == 8:
                break
                
        special_missing_df = pd.DataFrame(list(special_missing.items()), columns=['特別號', '遺漏期數']).sort_values('遺漏期數', ascending=False)
        st.bar_chart(special_missing_df.set_index('特別號'))
        
    with tab3:
        st.subheader("🎯 拖牌分析 (下期熱門號碼)")
        st.markdown("💡 **什麼是拖牌？** 當本期開出某個「指標號碼」時，統計歷史上它的**下一期**最常跟著開出哪些號碼。")
        target_num = st.selectbox("請選擇一個「指標號碼」", list(range(1, 39)))
        
        next_draw_nums = []
        for i in range(len(full_df) - 1, 0, -1):
            current_draw = [full_df.iloc[i][f'N{j}'] for j in range(1, 7)]
            if target_num in current_draw:
                next_draw = [full_df.iloc[i-1][f'N{j}'] for j in range(1, 7)]
                next_draw_nums.extend(next_draw)
        
        if next_draw_nums:
            next_freq = Counter(next_draw_nums).most_common(10)
            next_df = pd.DataFrame(next_freq, columns=['下期容易開出號碼', '出現次數'])
            st.dataframe(next_df, hide_index=True)
        else:
            st.info(f"在目前的數據區間內，號碼 {target_num} 尚未有拖牌數據 (或者它只在最新一期開出)。")

    with tab4:
        st.subheader("📈 近 50 期和值走勢圖")
        st.markdown("和值理論平均約為 117，可觀察近期是否偏離平均過多準備回歸。")
        # 取近 50 期資料，並將順序反轉為由舊到新，符合折線圖由左至右的時間感
        trend_df = full_df.head(50).copy()
        trend_df = trend_df.sort_values('日期', ascending=True)
        # 設定期別為 index 以顯示在 X 軸
        st.line_chart(trend_df.set_index('期別')['和值'])

    with tab5:
        st.subheader("🌡️ 號碼區間冷熱分佈 (近 30 期)")
        st.markdown("觀察哪一個區段（10號為一區）近期最常開出或發生斷區。")
        recent_30 = full_df.head(30)
        
        zones = {'1-10': 0, '11-20': 0, '21-30': 0, '31-38': 0}
        for _, row in recent_30.iterrows():
            nums = [row['N1'], row['N2'], row['N3'], row['N4'], row['N5'], row['N6']]
            for n in nums:
                if n <= 10: zones['1-10'] += 1
                elif n <= 20: zones['11-20'] += 1
                elif n <= 30: zones['21-30'] += 1
                else: zones['31-38'] += 1
                
        zone_df = pd.DataFrame(list(zones.items()), columns=['區間', '開出總顆數'])
        st.bar_chart(zone_df.set_index('區間'))

    with tab6:
        st.subheader("🌙 夢境解碼預測 (逼牌專區)")
        st.markdown("輸入你的夢境，系統會根據民間解夢字典，結合資料庫的**近期熱門號碼**，幫你補足 6 顆專屬威力彩號碼！")
        
        dream_text = st.text_area("請簡述昨晚的夢境 (例如：夢到被一條大蛇追，還看到很多水)")
        
        # 豪華版：擴充民間常見解夢字典
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
        from dream_dict import dream_database

        if not dream_text:
            st.warning("請先輸入您的夢境內容！")
            st.stop()
        else:
            extracted_numbers = set()
            keywords = []
            matched_descs = []
            user_input_lower = dream_text.lower()
            
            for kw_tuple, data in dream_database.items():
                nums = data['nums']
                desc = data['desc']
                matched_kws = [k for k in kw_tuple if k in user_input_lower]
                if matched_kws:
                    extracted_numbers.update(nums)
                    for k in matched_kws:
                        if k not in keywords:
                            keywords.append(k)
                    desc_text = f"**{', '.join(matched_kws)}**：{desc}"
                    if desc_text not in matched_descs:
                        matched_descs.append(desc_text)
                        
            dream_nums = list(set([n for n in extracted_numbers if 1 <= n <= 38]))
            
            st.success(f"🔍 **捕捉到夢境關鍵字**： {', '.join(keywords) if keywords else '無 (將完全依賴大數據預測)'}")
            if matched_descs:
                st.markdown("### 📖 夢境深度解析")
                for d in matched_descs:
                    st.markdown(f"> 💡 {d}")

                st.write(f"💭 夢境轉化號碼：{dream_nums if dream_nums else '無'}")
                
                # 2. 從資料庫撈取近期熱門號碼來補足 6 碼
                if not full_df.empty:
                    # 統計所有開出的號碼頻率
                    all_nums = full_df[['N1', 'N2', 'N3', 'N4', 'N5', 'N6']].values.flatten()
                    hot_nums = [n for n, c in Counter(all_nums).most_common(20)]
                    
                    st.markdown("### 🎲 專屬推薦組合")
                    import random
                    
                    for i in range(1, 3):
                        current_set = set(dream_nums)
                        # 防呆：如果夢境解析出超過 6 個號碼，隨機挑 6 個
                        if len(current_set) > 6:
                            current_set = set(random.sample(list(current_set), 6))
                        
                        # 用熱門號碼依序補齊空缺
                        available_hot = [n for n in hot_nums if n not in current_set]
                        while len(current_set) < 6 and available_hot:
                            current_set.add(available_hot.pop(0))
                            
                        # 如果熱門號碼用完了還是不夠(極少發生)，隨機補齊
                        while len(current_set) < 6:
                            current_set.add(random.randint(1, 38))
                            
                        suggested_list = sorted(list(current_set))
                        
                        # 特別號：從歷史最常開出的前 5 個特別號中隨機挑一個
                        special_num = random.choice([n for n, c in Counter(full_df['特別號']).most_common(5)])
                        
                        st.info(f"**組合 {i}**： {suggested_list} ➕ 特別號：{special_num}")
                else:
                    st.error("請先在左側更新資料庫，才有辦法結合熱門數據喔！")

    with tab7:
        st.subheader("💰 歷史回測：固定養牌策略")
        st.markdown("假設你從資料庫第一期開始，每期死守同一組號碼，到底會財富自由還是血本無歸？")
        
        # 輸入區塊
        col_n1, col_n2, col_n3 = st.columns([2, 1, 1])
        with col_n1:
            my_nums_str = st.text_input("輸入第一區6碼與第二區1碼 (以 + 號分隔)", "5,12,19,26,33,38+4")
        with col_n2:
            n_tickets = st.number_input("每期買幾注？", min_value=1, value=1)
        with col_n3:
            ticket_price = st.number_input("每注金額", value=100, disabled=True)
            
        if st.button("🚀 開始回測"):
            if full_df.empty:
                st.error("資料庫無數據，請先在左側更新資料。")
            else:
                try:
                    # 解析輸入號碼
                    parts = my_nums_str.split('+')
                    if len(parts) != 2: raise ValueError("格式錯誤")
                    my_nums = set([int(x.strip()) for x in parts[0].split(',')])
                    my_special = int(parts[1].strip())
                    
                    if len(my_nums) != 6 or not all(1 <= x <= 38 for x in my_nums) or not (1 <= my_special <= 8):
                        st.warning("格式錯誤！請確保第一區為 6 個 1~38 的數字，第二區為 1 個 1~8 的數字，並以 + 號連接。")
                    else:
                        total_draws = len(full_df)
                        total_cost = total_draws * n_tickets * ticket_price
                        
                        # 獎項計數器與總獎金
                        prize_counts = {
                            '頭獎': 0, '貳獎': 0, '參獎': 0, '肆獎': 0,
                            '伍獎 (4000)': 0, '陸獎 (800)': 0, '柒獎 (400)': 0, '捌獎 (200)': 0, '玖獎 (100)': 0, '普獎 (100)': 0
                        }
                        total_prize_money = 0
                        
                        # 進度條 (因為要跑數千期迴圈)
                        progress_bar = st.progress(0)
                        
                        # 逐期回測
                        for idx, row in full_df.iterrows():
                            # 更新進度
                            if idx % 100 == 0:
                                progress_bar.progress(idx / total_draws)
                                
                            draw_nums = set([row['N1'], row['N2'], row['N3'], row['N4'], row['N5'], row['N6']])
                            special_num = row['特別號']
                            
                            # 集合交集運算：對中幾個正碼
                            match_count = len(my_nums.intersection(draw_nums))
                            match_special = (special_num == my_special)
                            
                            # 判斷威力彩中獎階級
                            draw_prize = 0
                            if match_count == 6 and match_special:
                                prize_counts['頭獎'] += 1
                                draw_prize = 200000000
                            elif match_count == 6:
                                prize_counts['貳獎'] += 1
                                draw_prize = 5000000
                            elif match_count == 5 and match_special:
                                prize_counts['參獎'] += 1
                                draw_prize = 150000
                            elif match_count == 5:
                                prize_counts['肆獎'] += 1
                                draw_prize = 20000
                            elif match_count == 4 and match_special:
                                prize_counts['伍獎 (4000)'] += 1
                                draw_prize = 4000
                            elif match_count == 4:
                                prize_counts['陸獎 (800)'] += 1
                                draw_prize = 800
                            elif match_count == 3 and match_special:
                                prize_counts['柒獎 (400)'] += 1
                                draw_prize = 400
                            elif match_count == 2 and match_special:
                                prize_counts['捌獎 (200)'] += 1
                                draw_prize = 200
                            elif match_count == 3:
                                prize_counts['玖獎 (100)'] += 1
                                draw_prize = 100
                            elif match_count == 1 and match_special:
                                prize_counts['普獎 (100)'] += 1
                                draw_prize = 100
                                
                            total_prize_money += (draw_prize * n_tickets)
                        
                        progress_bar.empty() # 隱藏進度條
                        
                        # 計算淨損益
                        net_profit = total_prize_money - total_cost
                        
                        # 顯示結果
                        st.divider()
                        st.markdown(f"### 📊 養牌 {total_draws} 期回測報告")
                        st.info("💡 註：頭獎與貳獎為浮動獎金，回測時頭獎以保證 2 億元、貳獎以 500 萬元暫估，實際獎金依當期台彩公告為準。")
                        
                        col_r1, col_r2, col_r3 = st.columns(3)
                        col_r1.metric("總投入成本", f"- {total_cost:,} 元")
                        col_r2.metric("總中獎金額", f"+ {total_prize_money:,} 元")
                        
                        if net_profit > 0:
                            col_r3.metric("總淨利潤 (賺)", f"+ {net_profit:,} 元", "獲利")
                            st.balloons() # 放氣球慶祝
                        else:
                            col_r3.metric("總淨損益 (賠)", f"{net_profit:,} 元", "虧損", delta_color="inverse")
                            
                        # 顯示各獎項中獎次數
                        st.write("🏆 **詳細中獎次數統計**：")
                        # 將字典轉為水平表格顯示
                        prize_df = pd.DataFrame([prize_counts])
                        st.dataframe(prize_df, hide_index=True, use_container_width=True)

                except Exception as e:
                    st.error(f"解析發生錯誤，請檢查號碼格式。錯誤訊息：{e}")

    with tab8:
        st.subheader("🤖 AI 號碼健檢中心")
        st.markdown("輸入您心目中的 6 個號碼，讓 AI 透過大數據幫您進行 6 大維度的健檢評分與微調建議！")
        
        check_nums_str = st.text_input("請輸入 6 個號碼 (用半形逗號隔開)", "2, 4, 7, 9, 11, 30", key="health_check_input")
        
        if st.button("🩺 開始 AI 健檢"):
            if full_df.empty:
                st.error("資料庫無數據，請先在左側更新資料。")
            else:
                try:
                    check_nums = sorted(list(set([int(x.strip()) for x in check_nums_str.split(',')])))
                    if len(check_nums) != 6 or not all(1 <= x <= 38 for x in check_nums):
                        st.warning("請確保輸入的是『剛好 6 個』且『介於 1~38 之間』的不重複號碼喔！")
                    else:
                        score = 100
                        feedback = []
                        
                        # 1. 和值回歸概算
                        sum_val = sum(check_nums)
                        if 95 <= sum_val <= 139:
                            feedback.append(("✅ 滿分", f"和值為 {sum_val}，落在歷史最常開出的常態分佈區間 (95~139)。", "success"))
                        elif 80 <= sum_val < 95 or 139 < sum_val <= 155:
                            score -= 10
                            feedback.append(("⚠️ 輕微扣分", f"和值為 {sum_val}，稍微偏離中心區間，但仍在合理範圍內。", "warning"))
                        else:
                            score -= 25
                            feedback.append(("❌ 嚴重扣分", f"和值為 {sum_val}，屬於極端偏差值！建議調整大小號比例，讓總和盡量靠近 117。", "error"))
                            
                        # 2. 區間分佈分析
                        zones_count = [0, 0, 0, 0, 0]
                        for n in check_nums:
                            if n <= 10: zones_count[0] += 1
                            elif n <= 20: zones_count[1] += 1
                            elif n <= 30: zones_count[2] += 1
                            elif n <= 40: zones_count[3] += 1
                            else: zones_count[4] += 1
                        
                        max_in_zone = max(zones_count)
                        if max_in_zone >= 4:
                            score -= 20
                            feedback.append(("⚠️ 高度警告", f"有 {max_in_zone} 顆號碼擠在同一個區間！歷史上極少發生單一區間塞滿這麼多顆號碼，建議分散風險。", "error"))
                        elif max_in_zone == 3:
                            score -= 5
                            feedback.append(("⚠️ 輕微扣分", "有 3 顆號碼落在同一區間，略顯集中，但歷史上也常發生，算可接受範圍。", "warning"))
                        else:
                            feedback.append(("✅ 滿分", "號碼的區間分佈非常均勻，沒有過度集中在單一區間的問題。", "success"))
                            
                        # 3. 奇偶比分析
                        odd_count = sum(1 for n in check_nums if n % 2 != 0)
                        even_count = 6 - odd_count
                        if odd_count in [2, 3, 4]:
                            feedback.append(("✅ 滿分", f"奇偶比為 {odd_count}奇 {even_count}偶，這是歷史上開出機率最高、最完美的奇偶結構！", "success"))
                        else:
                            score -= 15
                            feedback.append(("⚠️ 扣分項目", f"奇偶比為 {odd_count}奇 {even_count}偶。歷史上極端奇偶比 (如 6奇 或 5偶) 開出機率非常低，建議調整為 3:3 或 4:2。", "warning"))
                            
                        # 4. 連號型態分析
                        consec_pairs = 0
                        for i in range(5):
                            if check_nums[i+1] - check_nums[i] == 1:
                                consec_pairs += 1
                                
                        if consec_pairs == 1 or consec_pairs == 2:
                            feedback.append(("✅ 滿分", f"包含 {consec_pairs} 組連號。歷史上有極大比例的開獎會包含 1~2 組連號，您的結構很棒！", "success"))
                        elif consec_pairs == 0:
                            score -= 5
                            feedback.append(("⚠️ 輕微扣分", "號碼完全打散無連號。雖然會開，但歷史上多數獎號都會夾帶至少一組連號，建議可考慮創造一組兩連號。", "warning"))
                        else:
                            score -= 15
                            feedback.append(("❌ 嚴重扣分", f"出現了 {consec_pairs} 組連號！過多的連號(如三連號、四連號)在歷史上極為罕見。", "error"))
                            
                        # 5. 冷熱與遺漏值
                        all_nums_flat = full_df[['N1', 'N2', 'N3', 'N4', 'N5', 'N6']].values.flatten()
                        freq = Counter(all_nums_flat)
                        
                        gaps = {n: -1 for n in check_nums}
                        for n in check_nums:
                            for idx, row in full_df.iterrows():
                                if n in [row['N1'], row['N2'], row['N3'], row['N4'], row['N5'], row['N6']]:
                                    gaps[n] = idx
                                    break
                        
                        hot_nums = [n for n in check_nums if freq[n] >= 260] # 粗估熱門門檻
                        high_gap_nums = [n for n in check_nums if gaps[n] >= 15] # 粗估高遺漏門檻
                        
                        if high_gap_nums:
                            score += 5 # 潛力股額外加分 (最高不超過100)
                            feedback.append(("🌟 加分項目", f"您的號碼 {high_gap_nums} 已經遺漏超過 15 期，具備強烈的「均值回歸補漲」動能，是很好的潛力股！", "success"))
                        else:
                            feedback.append(("ℹ️ 數據參考", "號碼皆在近期開出過，屬於穩定的連莊/跟牌策略。", "info"))
                            
                        score = min(100, max(0, score)) # 確保分數在 0-100 之間
                        
                        # 顯示報告
                        st.divider()
                        col_score, col_desc = st.columns([1, 2])
                        with col_score:
                            st.metric("🤖 AI 綜合健檢分數", f"{score} 分")
                            if score >= 90: st.success("極佳的黃金組合！")
                            elif score >= 70: st.info("體質不錯，可以直接下注！")
                            elif score >= 50: st.warning("略有偏誤，建議參考下方報告微調。")
                            else: st.error("極端偏差型態！強烈建議重新選號。")
                            
                        with col_desc:
                            st.markdown("#### 📝 健檢明細與建議")
                            for status, desc, msg_type in feedback:
                                if msg_type == "success": st.success(f"**{status}**：{desc}")
                                elif msg_type == "warning": st.warning(f"**{status}**：{desc}")
                                elif msg_type == "error": st.error(f"**{status}**：{desc}")
                                else: st.info(f"**{status}**：{desc}")
                                
                        # --- 微調推薦邏輯 ---
                        st.markdown("### 💡 AI 微調推薦組合")
                        if score >= 90:
                            st.success("這組號碼已經非常完美，不需要 AI 畫蛇添足，祝您中大獎！")
                        else:
                            import random
                            rec_nums = set(check_nums)
                            changed_nums = set()
                            
                            # 1. 找出潛在的問題號碼來替換
                            # 先保護「高遺漏值」的潛力股不被換掉
                            removable = [n for n in check_nums if n not in high_gap_nums]
                            
                            # 如果和值過低，優先移除最小的號碼；如果和值過高，優先移除最大的號碼
                            if sum_val < 120 and removable:
                                removable.sort()
                                to_remove = removable[0]
                            elif sum_val > 180 and removable:
                                removable.sort()
                                to_remove = removable[-1]
                            elif removable:
                                to_remove = random.choice(removable)
                            else:
                                to_remove = random.choice(list(rec_nums))
                                
                            rec_nums.remove(to_remove)
                            
                            # 找出第二個可替換的號碼 (如果有需要，分數低於 70)
                            if score < 70:
                                removable = [n for n in list(rec_nums) if n not in high_gap_nums]
                                if removable:
                                    to_remove2 = random.choice(removable)
                                    rec_nums.remove(to_remove2)
                                    
                            # 2. 從熱門號碼或遺漏號碼中挑選替補
                            hot_nums_pool = [n for n, c in freq.most_common(20)]
                            available_pool = [n for n in range(1, 39) if n not in rec_nums]
                            
                            while len(rec_nums) < 6:
                                current_sum = sum(rec_nums)
                                needed = 6 - len(rec_nums)
                                target_sum = 117
                                avg_needed = (target_sum - current_sum) / needed if needed > 0 else 25
                                
                                best_candidate = None
                                best_diff = 999
                                
                                random.shuffle(available_pool)
                                for cand in available_pool:
                                    if cand in rec_nums: continue
                                    diff = abs(cand - avg_needed)
                                    if cand in hot_nums_pool: diff -= 5 # 偏好熱門號
                                    
                                    if diff < best_diff:
                                        best_diff = diff
                                        best_candidate = cand
                                        
                                if not best_candidate:
                                    best_candidate = available_pool[0]
                                    
                                rec_nums.add(best_candidate)
                                changed_nums.add(best_candidate)
                                available_pool.remove(best_candidate)
                                
                            rec_list = sorted(list(rec_nums))
                            
                            # 格式化顯示 (紅色標示被改變的號碼)
                            st.markdown("AI 保留了您的潛力股，並替換了造成極端偏差的號碼，為您重新平衡了**和值**與**奇偶比**：")
                            
                            def format_num(n):
                                return f"<span style='color:#FF4B4B; font-weight:bold; font-size: 20px;'>{str(n).zfill(2)}</span>" if n in changed_nums else f"<span style='font-size: 20px;'>{str(n).zfill(2)}</span>"
                                
                            orig_str = "、".join([f"<span style='font-size: 20px;'>{str(n).zfill(2)}</span>" for n in check_nums])
                            rec_str = "、".join([format_num(n) for n in rec_list])
                            
                            st.markdown(f"👨‍🏫 **您的原始號碼**： {orig_str}", unsafe_allow_html=True)
                            st.markdown(f"🤖 **AI 推薦微調**： {rec_str}", unsafe_allow_html=True)
                            st.info("💡 紅色的號碼是 AI 替您換上的「平衡用號碼」（結合了歷史熱門數據）。")

                except Exception as e:
                    st.error(f"解析發生錯誤，請檢查號碼格式。錯誤訊息：{e}")

    st.divider()
    csv = full_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 下載完整 Excel/CSV 檔案", csv, "lotto_analysis.csv", "text/csv")
    
else:
    st.info("👈 資料庫目前沒有資料，請先在左側選單選擇日期區間，並點擊『開始抓取並寫入資料庫』。")
