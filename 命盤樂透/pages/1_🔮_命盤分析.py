import sys
import os
# 【究極路徑修復】這段必須在最上面！強制 Python 優先讀取根目錄與子資料夾
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
paipan_dir = os.path.join(root_dir, "排命盤")

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if paipan_dir not in sys.path:
    sys.path.insert(0, paipan_dir)

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from lunar_python import Solar

# 現在絕對找得到這兩個檔案了
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

st.set_page_config(page_title="命盤分析", page_icon="🔮", layout="wide", initial_sidebar_state="expanded")

# === 整合版專屬：返回首頁按鈕 ===
if st.button("⬅ 返回整合首頁", use_container_width=False):
    st.switch_page("app.py")
st.markdown("<hr style='margin-top:5px; margin-bottom:20px;'>", unsafe_allow_html=True)

# ==========================================
# 1. 核心 CSS 設定
# ==========================================
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
    /* 👇 加入這段：暴力突破 Streamlit 預設的隱形主容器寬度限制 */
    .block-container {
        max-width: 95% !important;  /* 強制把主畫面撐開到螢幕寬度的 95% */
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    .stApp { background-color: #FFFFFF !important; color: #000000; }
    .ziwei-square-board {
        display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); grid-template-rows: repeat(4, minmax(0, 1fr));
        width: 100%; max-width: 1400px; /* 👈 從 1040px 改成 1400px */
        aspect-ratio: 1 / 1; margin: 0 auto;
        background-color: #FFFFFF; border: 3px solid #000000;
        font-family: "MingLiU", "PMingLiU", "Noto Serif TC", serif; box-sizing: border-box;
    }
    .palace-cell { border: 1px solid #222222; position: relative; padding: 5px; box-sizing: border-box; overflow: hidden; background: #fff; }
    .center-hall { grid-column: 2 / 4; grid-row: 2 / 4; border: 2px solid #000000; position: relative; padding: 16px 18px; background-color: #FDFDFD; box-sizing: border-box; overflow: hidden; }
    .p-left-col { position: absolute; top: 5px; left: 6px; width: 85px; display: grid; grid-template-columns: repeat(2, 1fr); gap: 2px; font-size: 24px; line-height: 1.08; color: #222; font-weight: 700; }
    .vertical-note { writing-mode: vertical-rl; text-orientation: upright; min-height: 58px; white-space: nowrap; }
    .p-right-col { position: absolute; top: 5px; right: 6px; width: 120px; text-align: right; font-size: 20px; line-height: 1.12; color: #111; font-weight: 700; }
    .main-star { font-size: 38px !important; font-weight: 900 !important; color: #111; letter-spacing: 0; line-height: 1.15; }
    .minor-star { color: #333; font-size: 20px !important; font-weight: 600; line-height: 1.4; }
    .transform-line { color: #7B1FA2; font-size: 18px !important; font-weight: 800; margin-top: 4px; }
    .flow-year { position: absolute; left: 58px; top: 56px; color: #D32F2F; font-size: 22px; font-weight: 900; line-height: 1.3; text-align: center; white-space: nowrap; }
    .age-row { position: absolute; left: 24px; right: 26px; bottom: 95px; display: flex; justify-content: space-between; color: #222; font-size: 16px; line-height: 1; }
    .bottom-left { position: absolute; left: 8px; bottom: 6px; font-size: 18px; line-height: 1.25; color: #111; font-weight: 700; }
    .palace-name { color: #C62828; font-size: 24px !important; font-weight: 900 !important; display: block; margin-top: 2px; }
    .bottom-right { position: absolute; right: 7px; bottom: 6px; font-size: 18px; line-height: 1.6; color: #111; text-align: right; font-weight: 800; margin-top: 4px; }
    .gan-branch { font-size: 20px; font-weight: 900; }
    .center-lines { position: absolute; inset: 0; pointer-events: none; z-index: 1; }
    .center-text { position: relative; z-index: 2; font-size: 20px !important; line-height: 1.8 !important; color: #000; }
    .center-title { color: #111; font-size: 22px; font-weight: 900; text-align: left; margin-bottom: 8px; letter-spacing: 0; }
    .center-grid { display: grid; grid-template-columns: 100px 1fr 75px 1fr; gap: 4px 10px; align-items: baseline; max-width: 520px; margin: 0 auto; }
    .center-label { font-weight: 900; text-align: right; }
    .center-value { font-weight: 700; }
    .center-brand { margin-top: 18px; margin-left: 34px; line-height: 1.25; font-weight: 800; }
    .small-blue { color: #1565C0; font-size: 13px; }
    .small-red { color: #C62828; font-weight: 900; }
    .shensha-tag { background-color: #FBE9E7; color: #C62828; padding: 1px 6px; border-radius: 3px; font-size: 13px; font-weight: bold; border: 1px solid #FFCCBC; margin-right: 4px;}
    .body-palace { background-color: #FFFDE7 !important; border: 3px solid #FBC02D !important; box-shadow: inset 0 0 10px rgba(251, 192, 45, 0.5); }
    
    .astro-container { display: flex; justify-content: space-between; gap: 12px; margin-top: 25px; margin-bottom: 25px; max-width: 1400px; margin-left: auto; margin-right: auto;}
    .astro-card { flex: 1; border: 2px solid #000; padding: 15px; background-color: #FAFAFA; text-align: center; font-family: "MingLiU", "PMingLiU", "Noto Serif TC", serif; box-shadow: 3px 3px 0px #1A237E; border-radius: 2px; }
    .astro-title { font-size: 22px; color: #333; font-weight: bold; letter-spacing: 1px; border-bottom: 2px solid #CCC; padding-bottom: 8px; margin-bottom: 12px;}
    .astro-value { font-size: 40px; color: #000; font-weight: bold; letter-spacing: 0; }
    .astro-element { display: inline-block; margin-top: 12px; padding: 6px 16px; background-color: #000; color: #FFF; font-size: 18px; font-weight:bold; border-radius: 4px; }

    .fengshui-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; width: 100%; max-width: 800px; margin: 25px auto; aspect-ratio: 1; font-family: "MingLiU", "PMingLiU", "Noto Serif TC", serif;}
    .fs-cell { border: 3px solid #333; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; background: #FFF; box-shadow: 4px 4px 0px #000; }
    .fs-dir { position: absolute; top: 8px; left: 10px; font-size: 20px; font-weight: bold; color: #555; }
    .fs-star-num { font-size: 80px; font-weight: 900; margin-bottom: 2px; line-height: 1;}
    .fs-star-name { font-size: 24px; font-weight: bold; padding: 4px 12px; border-radius: 4px; color: #FFF; margin-top: 6px;}
    .fs-desc { font-size: 20px; color: #333; margin-top: 10px; font-weight: bold; letter-spacing: 2px;}
    .c-1 { color: #1976D2; } .bg-1 { background-color: #1976D2; }
    .c-2 { color: #424242; } .bg-2 { background-color: #424242; }
    .c-3 { color: #388E3C; } .bg-3 { background-color: #388E3C; }
    .c-4 { color: #4CAF50; } .bg-4 { background-color: #4CAF50; }
    .c-5 { color: #D32F2F; } .bg-5 { background-color: #D32F2F; }
    .c-6 { color: #FBC02D; } .bg-6 { background-color: #FBC02D; }
    .c-7 { color: #E64A19; } .bg-7 { background-color: #E64A19; }
    .c-8 { color: #F57F17; } .bg-8 { background-color: #F57F17; }
    .c-9 { color: #7B1FA2; } .bg-9 { background-color: #7B1FA2; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 演算法模組 (盲派、飛星、占星、靈數)
# ==========================================
def get_blind_bazi_extensions(y_stem, y_branch, m_stem, m_branch, d_stem, d_branch, h_stem, h_branch):
    m_s_idx, m_b_idx = STEMS.index(m_stem), BRANCHES.index(m_branch)
    tai_yuan = f"{STEMS[(m_s_idx + 1) % 10]}{BRANCHES[(m_b_idx + 3) % 12]}"
    
    mg_map = {"寅":1, "卯":2, "辰":3, "巳":4, "午":5, "未":6, "申":7, "酉":8, "戌":9, "亥":10, "子":11, "丑":12}
    mg_rev = {v:k for k, v in mg_map.items()}
    mg_val = 14 - (mg_map[m_branch] + mg_map[h_branch])
    if mg_val <= 0: mg_val += 12
    elif mg_val > 12: mg_val -= 12
    mg_branch = mg_rev[mg_val]
    
    y_s_idx = STEMS.index(y_stem)
    month_stem_start = ((y_s_idx % 5) * 2 + 2) % 10
    mg_stem = STEMS[(month_stem_start + (mg_val - 1)) % 10]
    ming_gong = f"{mg_stem}{mg_branch}"
    
    branches = [y_branch, m_branch, d_branch, h_branch]
    tags = set()
    tian_yi = {'甲':'丑未', '戊':'丑未', '庚':'丑未', '乙':'子申', '己':'子申', '丙':'亥酉', '丁':'亥酉', '壬':'巳卯', '癸':'巳卯', '辛':'寅午'}
    if d_stem in tian_yi and any(b in tian_yi[d_stem] for b in branches): tags.add("天乙貴人")
    wen_chang = {'甲':'巳', '乙':'午', '丙':'申', '戊':'申', '丁':'酉', '己':'酉', '庚':'亥', '辛':'子', '壬':'寅', '癸':'卯'}
    if d_stem in wen_chang and wen_chang[d_stem] in branches: tags.add("文昌貴人")
    yang_ren = {'甲':'卯', '丙':'午', '戊':'午', '庚':'酉', '壬':'子'}
    if d_stem in yang_ren and yang_ren[d_stem] in branches: tags.add("羊刃")
    peach = {'申':'酉','子':'酉','辰':'酉', '寅':'卯','午':'卯','戌':'卯', '亥':'子','卯':'子','未':'子', '巳':'午','酉':'午','丑':'午'}
    if peach.get(y_branch) in branches or peach.get(d_branch) in branches: tags.add("桃花(咸池)")
    horse = {'申':'寅','子':'寅','辰':'寅', '寅':'申','午':'申','戌':'申', '亥':'巳','卯':'巳','未':'巳', '巳':'亥','酉':'亥','丑':'亥'}
    if horse.get(y_branch) in branches or horse.get(d_branch) in branches: tags.add("驛馬星")
    huagai = {'申':'辰','子':'辰','辰':'辰', '寅':'戌','午':'戌','戌':'戌', '亥':'未','卯':'未','未':'未', '巳':'丑','酉':'丑','丑':'丑'}
    if huagai.get(y_branch) in branches or huagai.get(d_branch) in branches: tags.add("華蓋星")

    return tai_yuan, ming_gong, list(tags)

def get_flying_stars(year):
    sum_digits = sum(int(d) for d in str(year))
    while sum_digits > 9: sum_digits = sum(int(d) for d in str(sum_digits))
    center_star = 11 - sum_digits
    if center_star > 9: center_star -= 9

    flight_offsets = {"中": 0, "西北": 1, "西": 2, "東北": 3, "南": 4, "北": 5, "西南": 6, "東": 7, "東南": 8}
    grid_positions = ["東南", "南", "西南", "東", "中", "西", "東北", "北", "西北"]
    star_info = {
        1: ("一白", "桃花星", "吉"), 2: ("二黑", "病符星", "凶"), 3: ("三碧", "是非星", "凶"),
        4: ("四綠", "文昌星", "平"), 5: ("五黃", "災瘟星", "大凶"), 6: ("六白", "武曲星", "吉"),
        7: ("七赤", "破軍星", "凶"), 8: ("八白", "正財星", "大吉"), 9: ("九紫", "喜慶星", "大吉")
    }
    cells_html = ""
    for pos in grid_positions:
        star_num = (center_star + flight_offsets[pos])
        if star_num > 9: star_num -= 9
        name, desc, luck = star_info[star_num]
        cells_html += f'<div class="fs-cell"><div class="fs-dir">{pos}</div><div class="fs-star-num c-{star_num}">{star_num}</div><div class="fs-star-name bg-{star_num}">{name}</div><div class="fs-desc">{desc}</div></div>'
    return cells_html

def calculate_true_solar_time(birth_date, clock_time, longitude, timezone_base=120.0):
    lon_diff_minutes = 4 * (longitude - timezone_base)
    n = birth_date.timetuple().tm_yday
    B = math.radians((360 / 365.24) * (n - 81))
    eot_minutes = 9.87 * math.sin(2 * B) - 7.53 * math.cos(B) - 1.5 * math.sin(B)
    total_offset = lon_diff_minutes + eot_minutes
    return datetime.combine(birth_date, clock_time) + timedelta(minutes=total_offset), total_offset, eot_minutes

def calculate_nasa_astrology(birth_date, clock_time, longitude, latitude, timezone_base=120.0):
    utc_dt = datetime.combine(birth_date, clock_time) - timedelta(hours=timezone_base / 15.0)
    ut_hour_dec = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
    jd_ut = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, ut_hour_dec)
    
    sun_pos = swe.calc_ut(jd_ut, swe.SUN)[0][0]
    moon_pos = swe.calc_ut(jd_ut, swe.MOON)[0][0]
    merc_pos = swe.calc_ut(jd_ut, swe.MERCURY)[0][0]
    ven_pos = swe.calc_ut(jd_ut, swe.VENUS)[0][0]
    mars_pos = swe.calc_ut(jd_ut, swe.MARS)[0][0]
    jup_pos = swe.calc_ut(jd_ut, swe.JUPITER)[0][0]
    sat_pos = swe.calc_ut(jd_ut, swe.SATURN)[0][0]
    
    asc_pos = swe.houses(jd_ut, latitude, longitude, b'P')[1][0]
    
    zodiac_signs = ["白羊座", "金牛座", "雙子座", "巨蟹座", "獅子座", "處女座", "天秤座", "天蠍座", "射手座", "摩羯座", "水瓶座", "雙魚座"]
    elements = ["火象", "土象", "風象", "水象"]
    
    def get_info(deg): return zodiac_signs[int(deg // 30)], elements[int(deg // 30) % 4], deg
    
    s_s, s_e, s_d = get_info(sun_pos)
    m_s, m_e, m_d = get_info(moon_pos)
    me_s, me_e, me_d = get_info(merc_pos)
    v_s, v_e, v_d = get_info(ven_pos)
    ma_s, ma_e, ma_d = get_info(mars_pos)
    j_s, j_e, j_d = get_info(jup_pos)
    sa_s, sa_e, sa_d = get_info(sat_pos)
    a_s, a_e, a_d = get_info(asc_pos)
    
    return {
        "sun": s_s, "sun_element": s_e, "sun_deg": s_d,
        "moon": m_s, "moon_element": m_e, "moon_deg": m_d,
        "mercury": me_s, "mercury_element": me_e, "mercury_deg": me_d,
        "venus": v_s, "venus_element": v_e, "venus_deg": v_d,
        "mars": ma_s, "mars_element": ma_e, "mars_deg": ma_d,
        "jupiter": j_s, "jupiter_element": j_e, "jupiter_deg": j_d,
        "saturn": sa_s, "saturn_element": sa_e, "saturn_deg": sa_d,
        "asc": a_s, "asc_deg": a_d, "jd": jd_ut
    }

def calculate_life_path_number(birth_date):
    total = sum(int(digit) for digit in birth_date.strftime("%Y%m%d"))
    while total > 9: total = sum(int(digit) for digit in str(total))
    meanings = {
        1: ("開創與獨立", "天生領導者，具備強大執行力。"), 2: ("協調與細節", "極佳的傾聽者，擅長團隊合作。"),
        3: ("創意與表達", "充滿藝術天份，善於溝通表達。"), 4: ("穩定與秩序", "務實的建造者，重視邏輯規則。"),
        5: ("自由與冒險", "熱愛變化與挑戰，適應能力強。"), 6: ("關懷與療癒", "富有同理心，重視家庭與和諧。"),
        7: ("探究與真理", "邏輯分析力強，追求知識真理。"), 8: ("權力與豐盛", "具商業頭腦，擅長資源整合。"),
        9: ("大愛與智慧", "充滿人道精神，具備宏觀視野。")
    }
    title, desc = meanings.get(total, ("未知", ""))
    return total, title, desc

# ==========================================
# 3. 側邊欄控制台 (使用 Form 封裝，防止輸入時畫面刷新)
# ==========================================
with st.sidebar:
    # 👇 關鍵 1：建立一個名為 astro_form 的表單保護罩
    with st.form("astro_form"):
        st.markdown("### 🔮 天體與大師校正面板")
        name = st.text_input("命主", "匿名")
        gender = st.radio("性別", ["乾造 (男)", "坤造 (女)"])
        gender_int = 1 if "男" in gender else 0
        
        min_d = date(1930, 1, 1)
        max_d = date.today() + timedelta(days=90)
        
        b_date = st.date_input(
            "公曆出生日", 
            value=date(1971, 1, 1),
            min_value=min_d,
            max_value=max_d
        )
        
        time_options = [
            "🔮 不知出生時間 (自動以吉時排盤)",
            "子時 (23:00 - 01:00)", "丑時 (01:00 - 03:00)", "寅時 (03:00 - 05:00)",
            "卯時 (05:00 - 07:00)", "辰時 (07:00 - 09:00)", "巳時 (09:00 - 11:00)",
            "午時 (11:00 - 13:00)", "未時 (13:00 - 15:00)", "申時 (15:00 - 17:00)",
            "酉時 (17:00 - 19:00)", "戌時 (19:00 - 21:00)", "亥時 (21:00 - 23:00)"
        ]
        b_hour_str = st.selectbox("公曆出生時", time_options)
        
        time_map = {
            "🔮 不知出生時間 (自動以吉時排盤)": datetime(1971, 1, 1, 12, 0).time(),
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
        is_lucky_time = (b_hour_str == "🔮 不知出生時間 (自動以吉時排盤)")
        
        st.markdown("---")
        st.markdown("#### 🧭 天文地理校正")
        
        city_coords = {
            "基隆": (121.74, 25.13), "台北": (121.50, 25.05), "新北": (121.46, 25.01),
            "桃園": (121.30, 24.99), "新竹": (120.96, 24.81), "苗栗": (120.82, 24.56),
            "台中": (120.67, 24.14), "彰化": (120.54, 24.07), "南投": (120.68, 23.90),
            "雲林": (120.43, 23.70), "嘉義": (120.44, 23.48), "台南": (120.20, 22.99),
            "高雄": (120.30, 22.62), "屏東": (120.48, 22.67), "宜蘭": (121.75, 24.75),
            "花蓮": (121.60, 23.97), "台東": (121.14, 22.75), "澎湖": (119.56, 23.56),
            "金門": (118.31, 24.43), "馬祖": (119.93, 26.15)
        }
        
        city_list = list(city_coords.keys())
        selected_city = st.selectbox("出生城市", city_list, index=city_list.index("台北"))
        zi_hour_rule = st.selectbox("子時換日排法", ["早晚子時區分", "一律換日"])

        st.markdown("---")
        # 👇 關鍵 2：把原本的 st.button 換成表單專屬的 st.form_submit_button
        generate_btn = st.form_submit_button("🚀 生成專屬命盤解析", use_container_width=True)

    # 隱藏相容性變數，避免破壞後續判斷 (放在表單外)
    time_mode = "✅ 知道精確時間"
    tz_offset = 8.0

# ==========================================
# 4. 資料生成與排盤佈局
# ==========================================
if generate_btn:
    # 👇 新增這段判斷：如果有勾選吉時，強制將時間設為 12:00 (午時)
    if is_lucky_time:
        # 將 b_time 替換為 12:00
        b_time = datetime(1971, 1, 1, 12, 0).time()
        time_mode = "🔮 不知道時間"
        # 在右側主畫面給予溫馨提示
        st.warning("🔮 您勾選了「不知出生時間」，系統已自動為您切換至陽氣最旺的「午時 (12:00)」作為吉時排盤基準。請留意，時柱與命宮可能會因時間誤差而有所偏移。")

    # 👇 關鍵 3：將真太陽時的計算與提示框，移到按下按鈕後才執行顯示
    longitude, latitude = city_coords[selected_city]
    true_datetime, total_offset, eot = calculate_true_solar_time(b_date, b_time, longitude)
    
    with st.sidebar:
        st.info(f"經度差: {total_offset-eot:.1f} 分\n\n均時差: {eot:.1f} 分\n\n**真太陽時:**\n{true_datetime.strftime('%Y-%m-%d %H:%M:%S')}")

    with st.spinner("🌌 正在為您精算天體運行與命盤參數..."):
        lunar = Solar.fromYmdHms(true_datetime.year, true_datetime.month, true_datetime.day, true_datetime.hour, true_datetime.minute, 0).getLunar()
        eight_char = lunar.getEightChar()
        eight_char.setSect(1 if zi_hour_rule.startswith("一律換日") else 2)
        yun = eight_char.getYun(gender_int)

        y_st, y_br = eight_char.getYear()[0], eight_char.getYear()[1]
        m_st, m_br = eight_char.getMonth()[0], eight_char.getMonth()[1]
        d_st, d_br = eight_char.getDay()[0], eight_char.getDay()[1]
        h_st, h_br = eight_char.getTime()[0], eight_char.getTime()[1]

        tai_yuan, ming_gong, shen_sha_list = get_blind_bazi_extensions(y_st, y_br, m_st, m_br, d_st, d_br, h_st, h_br)
        shen_sha_html = "".join([f"<span class='shensha-tag'>{tag}</span>" for tag in shen_sha_list])
        jiaoyun_text = f"出生後 {yun.getStartYear()} 年 {yun.getStartMonth()} 月交運"

        ziwei_chart = build_ziwei_chart(true_datetime.year, true_datetime.month, true_datetime.day, true_datetime.hour, true_datetime.minute, gender)
        ziwei_palaces = ziwei_chart["palaces"]
        dynamic_palaces = {branch: palace["宮位"] for branch, palace in ziwei_palaces.items()}

        astro_data = calculate_nasa_astrology(b_date, b_time, longitude, latitude, timezone_base=tz_offset*15.0)
        life_path_num, lp_title, lp_desc = calculate_life_path_number(b_date)
        current_year = datetime.now().year
        current_flow_branch, current_flow_ganzhi = Solar.fromYmd(current_year, 6, 1).getLunar().getYearZhi(), Solar.fromYmd(current_year, 6, 1).getLunar().getYearInGanZhi()

        def get_dynamic_san_fang_si_zheng_svg(ming_branch):
            anchors = {"巳":(0,0), "午":(25,0), "未":(75,0), "申":(100,0), "辰":(0,25), "酉":(100,25), "卯":(0,75), "戌":(100,75), "寅":(0,100), "丑":(25,100), "子":(75,100), "亥":(100,100)}
            idx = BRANCHES.index(ming_branch)
            p0, p1, p2, p3 = anchors[ming_branch], anchors[BRANCHES[(idx+4)%12]], anchors[BRANCHES[(idx+6)%12]], anchors[BRANCHES[(idx+8)%12]]
            return f'''<svg class="center-lines" viewBox="0 0 100 100" preserveAspectRatio="none">
                <line x1="{p0[0]}" y1="{p0[1]}" x2="{p1[0]}" y2="{p1[1]}" stroke="#D32F2F" stroke-width="0.6" />
                <line x1="{p0[0]}" y1="{p0[1]}" x2="{p2[0]}" y2="{p2[1]}" stroke="#D32F2F" stroke-width="0.6" />
                <line x1="{p0[0]}" y1="{p0[1]}" x2="{p3[0]}" y2="{p3[1]}" stroke="#D32F2F" stroke-width="0.6" />
                <line x1="{p1[0]}" y1="{p1[1]}" x2="{p2[0]}" y2="{p2[1]}" stroke="#D32F2F" stroke-width="0.4" stroke-dasharray="2,2" />
                <line x1="{p3[0]}" y1="{p3[1]}" x2="{p2[0]}" y2="{p2[1]}" stroke="#D32F2F" stroke-width="0.4" stroke-dasharray="2,2" />
            </svg>'''

        def render_cell(branch_name, p_name):
            p = ziwei_palaces[branch_name]
            main_stars = p.get("主星") or "--"
            lucky = [w for w in str(p.get("吉煞", "")).split() if w]
            minor = [w for w in str(p.get("副星", "")).split() if w]
            left_items = [p.get("博士", ""), p.get("長生", ""), p.get("歲建", "")] + minor[:3]
            right_minor = "<br>".join(lucky[:4] + minor[3:6])
            t_line = "<br>".join([w for w in str(p.get("四化文字", "")).split() if w])
            liunian_html = f"<div class='flow-year'>{current_year}年<br>{current_flow_ganzhi}年<br>流年命宮</div>" if branch_name == current_flow_branch else ""
            try: start = int(str(p.get('大限')).split("-")[0])
            except: start = 1
            ages = "".join(f"<span>{start + i * 12}</span>" for i in range(8))
            
            extra_class = " body-palace" if branch_name == ziwei_chart.get('body_branch') else ""
    
            return f'''
            <div class="palace-cell{extra_class}">
                <div class="p-left-col">{"".join(f"<span class='vertical-note'>{item}</span>" for item in (left_items + ["","","",""])[:6] if item)}</div>
                <div class="p-right-col"><div class="main-star">{main_stars.replace(' ', '<br>')}</div><div class="minor-star">{right_minor}</div><div class="transform-line">{t_line}</div></div>
                {liunian_html}
                <div class="age-row">{ages}</div>
                <div class="bottom-left">{p.get('大限', '')}<br><span class="palace-name">【{p_name}】</span></div>
                <div class="bottom-right"><span class="gan-branch">{p.get('宮干', '')}</span><br>{branch_name}<br>{ziwei_chart.get('nature', '')}</div>
            </div>
            '''

        # 動態判斷顯示的時間字眼
        time_display = "吉時 (未輸入)" if "不知道" in time_mode else b_time.strftime('%H時%M分')
        true_time_display = "--" if "不知道" in time_mode else true_datetime.strftime('%Y年%m月%d日 %H時%M分')
        lunar_hour_display = "吉" if "不知道" in time_mode else ziwei_chart['lunar_hour']

        moon_disclaimer = "<br><span style='font-size:10px; color:#D32F2F;'>*未知時間可能造成交界日誤差</span>" if "不知道" in time_mode else ""

        html_content = f'''
        <div class="ziwei-square-board">
            {render_cell("巳", dynamic_palaces["巳"])}{render_cell("午", dynamic_palaces["午"])}{render_cell("未", dynamic_palaces["未"])}{render_cell("申", dynamic_palaces["申"])}
            {render_cell("辰", dynamic_palaces["辰"])}
            <div class="center-hall">
                {get_dynamic_san_fang_si_zheng_svg(ziwei_chart['ming_branch'])}
                <div class="center-text">
                    <div class="center-grid">
                        <div class="center-label">姓名：</div><div class="center-value">{name}</div>
                        <div class="center-label">現在歲：</div><div class="center-value">{max(0, current_year - b_date.year)}</div>
                        <div class="center-label">命造：</div><div class="center-value">{gender}</div>
                        <div class="center-label">生肖：</div><div class="center-value">{lunar.getYearShengXiao()}</div>
                        <div class="center-label">陽曆：</div><div class="center-value" style="grid-column: span 3;">{b_date.strftime('%Y年%m月%d日')} {time_display}</div>
                        <div class="center-label">真時：</div><div class="center-value" style="grid-column: span 3; color:#1565C0;">{true_time_display}</div>
                        <div class="center-label">農曆：</div><div class="center-value" style="grid-column: span 3;">{ziwei_chart['lunar_txt']} {lunar_hour_display}時</div>
                        <div class="center-label">節氣四柱：</div><div class="center-value" style="grid-column: span 3; font-size:16px; color:#B71C1C;">{eight_char.getYear()}年 {eight_char.getMonth()}月 {eight_char.getDay()}日 {eight_char.getTime() if "精確" in time_mode else "**吉時**"}</div>
                        <div class="center-label" style="color:#C62828;">盲派六柱：</div><div class="center-value" style="grid-column: span 3; color:#C62828;">胎元【{tai_yuan}】&nbsp;&nbsp;命宮【{ming_gong}】</div>
                        <div class="center-label" style="color:#C62828;">本命神煞：</div><div class="center-value" style="grid-column: span 3;">{shen_sha_html if shen_sha_html else '無顯著神煞'}</div>
                        <div class="center-label">命宮：</div><div class="center-value">{ziwei_chart['ming_branch']}</div>
                        <div class="center-label">身宮：</div><div class="center-value">{ziwei_chart['body_branch']}</div>
                        <div class="center-label">交運：</div><div class="center-value" style="grid-column: span 3;">{jiaoyun_text}</div>
                    </div>
                    <div class="center-brand">STAR★START<br><span>從星開始 紫微研究苑</span><br><span class="small-blue">108s.tw</span></div>
                </div>
            </div>
            {render_cell("酉", dynamic_palaces["酉"])}
            {render_cell("卯", dynamic_palaces["卯"])}{render_cell("戌", dynamic_palaces["戌"])}
            {render_cell("寅", dynamic_palaces["寅"])}{render_cell("丑", dynamic_palaces["丑"])}{render_cell("子", dynamic_palaces["子"])}{render_cell("亥", dynamic_palaces["亥"])}
        </div>
        '''

        # --- 本命格局深度診斷引擎 ---
        ming_branch = ziwei_chart["ming_branch"]
        body_branch = ziwei_chart["body_branch"]
        nature = ziwei_chart["nature"] # e.g. 金四局
        
        branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        idx = branches.index(ming_branch)
        
        cai_branch = branches[(idx - 4) % 12]
        guan_branch = branches[(idx + 4) % 12]
        qian_branch = branches[(idx + 6) % 12]
        
        sf_stars = []
        sf_stars.extend(ziwei_palaces[ming_branch].get("主星", "").split())
        sf_stars.extend(ziwei_palaces[cai_branch].get("主星", "").split())
        sf_stars.extend(ziwei_palaces[guan_branch].get("主星", "").split())
        sf_stars.extend(ziwei_palaces[qian_branch].get("主星", "").split())
        
        sf_stars_clean = [s.split('[')[0] for s in sf_stars if s]
        
        geju_text = ""
        if "七殺" in sf_stars_clean or "破軍" in sf_stars_clean or "貪狼" in sf_stars_clean:
            geju_text = "【殺破狼格】三方四正匯聚七殺、破軍或貪狼。此為極具開創力與爆發力的動態格局，人生起伏較大，大破大立，適合在變動中求生存與發展，不喜受傳統體制約束。"
        elif "天機" in sf_stars_clean and "太陰" in sf_stars_clean and "天同" in sf_stars_clean and "天梁" in sf_stars_clean:
            geju_text = "【機月同梁格】三方四正集齊天機、太陰、天同、天梁。此為標準的靜態文職格局，行事穩健、深思熟慮，適合擔任企劃、幕僚、顧問或在大型機構、公教體系中穩定發展。"
        elif "紫微" in sf_stars_clean and "天府" in sf_stars_clean:
            geju_text = "【紫府朝垣/同宮】紫微與天府兩大帝星鎮守三方四正。此為尊貴之格，具備極強的領導慾與管理能力，氣度恢弘，適合創業或擔任高階主管，一生多有貴人提攜。"
        elif "太陽" in sf_stars_clean and "巨門" in sf_stars_clean:
            geju_text = "【巨日同宮/會照】太陽巨門匯聚。此格局主「異族生財」或「口舌生財」，極具說服力與群眾魅力，適合從事外交、跨國貿易、法律、教育或自媒體發言人。"
        else:
            if not sf_stars_clean:
                geju_text = "【命無正曜】命宮無主星，易受環境與他人影響，彈性極大。人生走向多視借入的對宮主星與大限流年而定，屬於「遇強則強、遇弱則弱」的適應型格局。"
            else:
                main_star = sf_stars_clean[0]
                geju_text = f"【{main_star}坐命】以{main_star}為核心能量場。個性與發展軌跡深受此星曜牽引，三方四正氣場交融，適合在自身專業領域穩紮穩打，發揮獨有的星曜特質。"
                
        body_palace_name = ziwei_palaces[body_branch]["宮位"].replace("【", "").replace("】", "")
        body_text = ""
        if "官祿" in body_palace_name:
            body_text = "身宮落於「官祿宮」，代表您人生下半場的重心將徹底轉向「事業成就與社會地位」。工作不僅是賺錢工具，更是您獲得尊嚴與自我實現的終極舞台，事業若成，人生便感圓滿。"
        elif "財帛" in body_palace_name:
            body_text = "身宮落於「財帛宮」，代表您人生下半場對「財富累積與價值轉換」有著極高的渴望與行動力。性格會越來越務實，適合從商或以專業技能直接變現，金錢是您最大的安全感來源。"
        elif "夫妻" in body_palace_name:
            body_text = "身宮落於「夫妻宮」，代表「感情、婚姻與伴侶關係」是您中晚年最深的牽絆。不論早年如何，下半輩子很容易為伴侶付出，或事業發展受配偶深刻影響，家庭圓滿是首要追求。"
        elif "遷移" in body_palace_name:
            body_text = "身宮落於「遷移宮」，代表您注定要「在外奔波、向外發展」。下半場人生不宜死守故里，越往外縣市、跨國或是跨領域去闖蕩，越能激發潛能並獲得絕佳機遇與貴人。"
        elif "福德" in body_palace_name:
            body_text = "身宮落於「福德宮」，代表您中晚年會越來越重視「精神層面的滿足與生活品質」。不再盲目追求世俗名利，反而會轉向宗教、哲學、興趣嗜好，注重內心的寧靜與靈魂的昇華。"
        else:
            body_text = "身宮與命宮重疊，代表您是一個「表裡如一、自我意識極強」的人。一生不易受他人左右，早年與晚年的性格軌跡一致，堅持自己的道路，成敗皆由自己一肩扛起。"

        shensha_text = ""
        if "羊刃" in shen_sha_list or "擎羊" in ziwei_palaces[ming_branch].get("吉煞", ""):
            shensha_text = "命盤帶有「羊刃/擎羊」的強烈煞氣，代表性格中有剛毅、果決且不服輸的一面，極具爆發力與開創性；但也需注意過度銳利易傷人，或有突發性之血光、金屬刀劍傷害，宜修心養性、或從事持刀/拿筆/科技器械之專業以化解。"
        elif "陀羅" in ziwei_palaces[ming_branch].get("吉煞", ""):
            shensha_text = "命帶「陀羅」，做事較易有拖延、糾結或原地打轉的傾向，但也代表您有極強的「耐力與韌性」，適合從事需要長期鑽研、磨練的冷門或深奧專業，大器晚成。"
        else:
            shensha_text = "此命格神煞煞氣較弱，為人處世相對圓融平順，較少經歷極端之大起大落，適合在穩定環境中循序漸進地累積實力與財富。"

        ziwei_diagnosis_html = f'''
        <div style="max-width: 1400px; margin: 0 auto 40px auto; background: linear-gradient(145deg, #ffffff, #FAFAFA); border-left: 6px solid #B71C1C; border-radius: 8px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); font-family: 'MingLiU', 'PMingLiU', 'Noto Serif TC', serif;">
            <h3 style="color: #B71C1C; margin-top: 0; margin-bottom: 20px; font-weight: bold; font-size: 24px; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px;">
                <span style="font-size: 28px;">🔍</span> 紫微斗數 · 本命格局深度診斷
            </h3>
            
            <div style="margin-bottom: 20px;">
                <h4 style="color: #1565C0; margin-bottom: 8px; font-size: 20px; font-weight: bold;">📌 核心格局：三方四正氣場</h4>
                <p style="color: #333; font-size: 18px; line-height: 1.6; margin: 0; background-color: #E3F2FD; padding: 12px; border-radius: 6px;">
                    {geju_text}
                </p>
            </div>
            
            <div style="margin-bottom: 20px;">
                <h4 style="color: #E65100; margin-bottom: 8px; font-size: 20px; font-weight: bold;">📌 命身同參：下半場人生造化</h4>
                <p style="color: #333; font-size: 18px; line-height: 1.6; margin: 0; background-color: #FFF3E0; padding: 12px; border-radius: 6px;">
                    {body_text}
                </p>
            </div>
            
            <div>
                <h4 style="color: #4A148C; margin-bottom: 8px; font-size: 20px; font-weight: bold;">📌 靈魂星局與隱藏神煞</h4>
                <p style="color: #333; font-size: 18px; line-height: 1.6; margin: 0; background-color: #F3E5F5; padding: 12px; border-radius: 6px;">
                    您的靈魂基底為<b>【{nature}】</b>。{shensha_text}
                </p>
            </div>
        </div>
        '''

        html_content += ziwei_diagnosis_html

        # 解析十神
        shishen_map = {"比肩":"比肩", "劫财":"劫財", "食神":"食神", "伤官":"傷官", "偏财":"偏財", "正财":"正財", "七杀":"七殺", "正官":"正官", "偏印":"偏印", "正印":"正印"}
        def tr_shishen(s): return shishen_map.get(s, s)
        
        y_shishen_gan = tr_shishen(eight_char.getYearShiShenGan())
        m_shishen_gan = tr_shishen(eight_char.getMonthShiShenGan())
        d_shishen_gan = "日主"
        t_shishen_gan = tr_shishen(eight_char.getTimeShiShenGan()) if "精確" in time_mode else "--"

        y_shishen_zhi = "<br>".join([tr_shishen(s) for s in eight_char.getYearShiShenZhi()])
        m_shishen_zhi = "<br>".join([tr_shishen(s) for s in eight_char.getMonthShiShenZhi()])
        d_shishen_zhi = "<br>".join([tr_shishen(s) for s in eight_char.getDayShiShenZhi()])
        t_shishen_zhi = "<br>".join([tr_shishen(s) for s in eight_char.getTimeShiShenZhi()]) if "精確" in time_mode else "--"
        
        y_hide = "<br>".join(eight_char.getYearHideGan())
        m_hide = "<br>".join(eight_char.getMonthHideGan())
        d_hide = "<br>".join(eight_char.getDayHideGan())
        t_hide = "<br>".join(eight_char.getTimeHideGan()) if "精確" in time_mode else "--"

        bazi_html = f'''
        <div style="max-width: 1400px; margin: 40px auto; text-align: center; font-family: 'MingLiU', 'PMingLiU', 'Noto Serif TC', serif; background-color: #FAFAFA; border: 2px solid #ccc; border-radius: 8px; padding: 20px;">
            <h2 style="color: #B71C1C; margin-bottom: 20px; font-weight: bold;">【八字四柱十神排盤】</h2>
            <div style="font-size: 20px; color: #1565C0; margin-bottom: 20px; font-weight: bold;">{jiaoyun_text}</div>
            <table style="width: 100%; border-collapse: collapse; font-size: 22px; table-layout: fixed; border: none;">
                <tr style="border-bottom: 2px solid #ccc; font-size: 18px; color: #555;">
                    <th style="padding: 10px;">時柱</th><th style="padding: 10px;">日柱</th><th style="padding: 10px;">月柱</th><th style="padding: 10px;">年柱</th>
                </tr>
                <tr style="color: #4A148C; font-size: 18px; font-weight: bold;">
                    <td style="padding: 10px;">{t_shishen_gan}</td><td style="padding: 10px;">{d_shishen_gan}</td><td style="padding: 10px;">{m_shishen_gan}</td><td style="padding: 10px;">{y_shishen_gan}</td>
                </tr>
                <tr style="font-size: 38px; font-weight: bold; color: #D32F2F;">
                    <td style="padding: 10px;">{eight_char.getTimeGan() if "精確" in time_mode else "？"}</td><td style="padding: 10px;">{eight_char.getDayGan()}</td><td style="padding: 10px;">{eight_char.getMonthGan()}</td><td style="padding: 10px;">{eight_char.getYearGan()}</td>
                </tr>
                <tr style="font-size: 38px; font-weight: bold; color: #1976D2; border-bottom: 2px solid #ccc;">
                    <td style="padding: 10px;">{eight_char.getTimeZhi() if "精確" in time_mode else "？"}</td><td style="padding: 10px;">{eight_char.getDayZhi()}</td><td style="padding: 10px;">{eight_char.getMonthZhi()}</td><td style="padding: 10px;">{eight_char.getYearZhi()}</td>
                </tr>
                <tr style="font-size: 20px; color: #E65100; vertical-align: top; font-weight: bold;">
                    <td style="padding: 15px 10px 5px 10px;">{t_hide}</td><td style="padding: 15px 10px 5px 10px;">{d_hide}</td><td style="padding: 15px 10px 5px 10px;">{m_hide}</td><td style="padding: 15px 10px 5px 10px;">{y_hide}</td>
                </tr>
                <tr style="font-size: 16px; color: #4A148C; vertical-align: top;">
                    <td style="padding: 5px 10px 15px 10px;">{t_shishen_zhi}</td><td style="padding: 5px 10px 15px 10px;">{d_shishen_zhi}</td><td style="padding: 5px 10px 15px 10px;">{m_shishen_zhi}</td><td style="padding: 5px 10px 15px 10px;">{y_shishen_zhi}</td>
                </tr>
            </table>
        </div>
        '''

        html_content += bazi_html

        # --- 八字四柱大師級診斷引擎 ---
        day_master = eight_char.getDayGan()
        dm_traits = {
            "甲": "如參天大木，性格直爽不屈，具備強烈的向上心與仁慈感，適合在組織中擔任骨幹。",
            "乙": "如藤蔓花草，柔軟且適應力強，擅長人際手腕與變通，能在惡劣環境中找到出路。",
            "丙": "如太陽之火，熱情奔放，樂於付出與照亮他人，天生具有群眾魅力與領袖氣質。",
            "丁": "如燭光星火，心思細膩，具備深刻的洞察力與溫暖特質，是絕佳的指路人與幕僚。",
            "戊": "如大地高山，沉穩厚重，重信守諾，給人極強的安全感，是堅若磐石的靠山。",
            "己": "如田園濕土，包容力極強，擅長孕育與培植人才，性格溫和細膩且踏實。",
            "庚": "如刀劍礦石，剛毅果斷，富有正義感與殺伐決斷之氣，適合大破大立的挑戰。",
            "辛": "如珠寶首飾，精緻且愛惜羽毛，對美感與細節要求極高，自尊心強且閃耀。",
            "壬": "如江河之水，豪放不羈，具備廣闊的視野與極強的適應力，才智過人且多變。",
            "癸": "如雨露之水，潤物無聲，直覺極度敏銳，心思百轉千迴，具備高度的靈性與創意。"
        }
        dm_text = dm_traits.get(day_master, "特質獨特，難以單一而論。")

        all_shishen = []
        if t_shishen_gan != "--": all_shishen.append(t_shishen_gan)
        if d_shishen_gan != "日主": all_shishen.append(d_shishen_gan)
        all_shishen.append(m_shishen_gan)
        all_shishen.append(y_shishen_gan)
        for zhi_ss in [t_shishen_zhi, d_shishen_zhi, m_shishen_zhi, y_shishen_zhi]:
            all_shishen.extend([s.strip() for s in zhi_ss.replace('<br>', ' ').split() if s.strip()])
            
        shishen_counts = {ss: all_shishen.count(ss) for ss in set(all_shishen)}
        
        qisha_shangguan = shishen_counts.get("七殺", 0) + shishen_counts.get("傷官", 0) + shishen_counts.get("劫財", 0)
        zhengyin_zhengguan = shishen_counts.get("正印", 0) + shishen_counts.get("正官", 0) + shishen_counts.get("正財", 0)
        piancai_shishen = shishen_counts.get("偏財", 0) + shishen_counts.get("食神", 0) + shishen_counts.get("偏印", 0)

        if qisha_shangguan >= 3:
            shishen_text = "命局中「七殺、傷官、劫財」等動態星能量極強。這賦予您極度敏銳的直覺、強大的顛覆力與抗壓性。您天生不適合死板的打卡體制，適合在競爭激烈、需要大破大立的開創性環境中脫穎而出。您的成功往往來自於突破常規與勇敢冒險。"
        elif zhengyin_zhengguan >= 3:
            shishen_text = "命局中「正官、正印、正財」等靜態星能量主導。您性格循規蹈矩、重視名譽、信用與體制內的階級。這是一組非常穩健的「管理與守成」格局，適合在公家機關、大型企業、或教育體系中，靠著按部就班的累積獲得極高的社會地位。"
        elif piancai_shishen >= 3:
            shishen_text = "命局中「偏財、食神、偏印」等才華星能量活躍。您極具商業嗅覺、創意靈感與藝術天賦。您的人生追求自由與品質，非常適合靠專門技術、投資理財、自媒體或藝術創作來建立事業。您擁有將虛無緲渺的靈感轉化為實際財富的強大能力。"
        else:
            shishen_text = "命局中十神五行分配相對勻稱。這代表您的性格極具彈性，進可攻退可守。在順境中能穩健發展，在逆境中也能迅速適應環境。此格局一生較少極端的大起大落，屬於中流砥柱的平穩雙贏格局。"

        bazi_diagnosis_html = f'''
        <div style="max-width: 1400px; margin: -20px auto 40px auto; background: linear-gradient(145deg, #ffffff, #FAFAFA); border-left: 6px solid #D32F2F; border-radius: 8px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); font-family: 'MingLiU', 'PMingLiU', 'Noto Serif TC', serif;">
            <h3 style="color: #D32F2F; margin-top: 0; margin-bottom: 20px; font-weight: bold; font-size: 24px; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px;">
                <span style="font-size: 28px;">🔥</span> 八字四柱 · 本命靈魂深度診斷
            </h3>
            
            <div style="margin-bottom: 20px;">
                <h4 style="color: #1976D2; margin-bottom: 8px; font-size: 20px; font-weight: bold;">📌 日主元神：先天氣場基底</h4>
                <p style="color: #333; font-size: 18px; line-height: 1.6; margin: 0; background-color: #E3F2FD; padding: 12px; border-radius: 6px;">
                    您的八字日主為<b>【{day_master}】</b>。{dm_text}
                </p>
            </div>
            
            <div>
                <h4 style="color: #E65100; margin-bottom: 8px; font-size: 20px; font-weight: bold;">📌 十神交織：後天行為與天賦軌跡</h4>
                <p style="color: #333; font-size: 18px; line-height: 1.6; margin: 0; background-color: #FFF3E0; padding: 12px; border-radius: 6px;">
                    {shishen_text}
                </p>
            </div>
        </div>
        '''
        html_content += bazi_diagnosis_html

        html_content += f'''
        <div class="astro-container">
            <div class="astro-card"><div class="astro-title">☀️ 太陽 (外在意志)</div><div class="astro-value">{astro_data['sun']}</div><div class="astro-element" style="background-color: #B71C1C;">{astro_data['sun_element']}特質</div><div style="font-size:16px; color:#666; margin-top:8px;">黃經 {astro_data['sun_deg']:.2f}°</div></div>
            <div class="astro-card"><div class="astro-title">🌙 月亮 (潛意識)</div><div class="astro-value">{astro_data['moon']}</div><div class="astro-element" style="background-color: #0D47A1;">情緒與安全感</div><div style="font-size:16px; color:#666; margin-top:8px;">黃經 {astro_data['moon_deg']:.2f}°{moon_disclaimer}</div></div>
            <div class="astro-card"><div class="astro-title">✨ 上升 (社會人格)</div><div class="astro-value">{astro_data['asc'] if "精確" in time_mode else "--"}</div><div class="astro-element" style="background-color: #FBC02D; color:#000;">{ "面具與舵手" if "精確" in time_mode else "需精準時間" }</div><div style="font-size:16px; color:#666; margin-top:8px;">{f"黃經 {astro_data['asc_deg']:.2f}°" if "精確" in time_mode else "無法計算"}</div></div>
            <div class="astro-card" style="box-shadow: 3px 3px 0px #4A148C;"><div class="astro-title">🔢 生命靈數</div><div class="astro-value">{life_path_num}</div><div class="astro-element" style="background-color: #4A148C;">{lp_title}</div><div style="font-size:16px; color:#666; margin-top:8px; line-height:1.4;">{lp_desc}</div></div>
        </div>
        <div class="astro-container">
            <div class="astro-card"><div class="astro-title">💬 水星 (思維溝通)</div><div class="astro-value">{astro_data['mercury']}</div><div class="astro-element" style="background-color: #00838F;">邏輯與學習</div><div style="font-size:16px; color:#666; margin-top:8px;">黃經 {astro_data['mercury_deg']:.2f}°</div></div>
            <div class="astro-card"><div class="astro-title">💖 金星 (價值桃花)</div><div class="astro-value">{astro_data['venus']}</div><div class="astro-element" style="background-color: #E91E63;">美感與愛情</div><div style="font-size:16px; color:#666; margin-top:8px;">黃經 {astro_data['venus_deg']:.2f}°</div></div>
            <div class="astro-card"><div class="astro-title">🔥 火星 (行動脾氣)</div><div class="astro-value">{astro_data['mars']}</div><div class="astro-element" style="background-color: #D84315;">爆發力與慾望</div><div style="font-size:16px; color:#666; margin-top:8px;">黃經 {astro_data['mars_deg']:.2f}°</div></div>
            <div class="astro-card"><div class="astro-title">🍀 木星 (幸運擴張)</div><div class="astro-value">{astro_data['jupiter']}</div><div class="astro-element" style="background-color: #2E7D32;">天賦與機遇</div><div style="font-size:16px; color:#666; margin-top:8px;">黃經 {astro_data['jupiter_deg']:.2f}°</div></div>
            <div class="astro-card"><div class="astro-title">🪐 土星 (業力挑戰)</div><div class="astro-value">{astro_data['saturn']}</div><div class="astro-element" style="background-color: #424242;">壓力與成就</div><div style="font-size:16px; color:#666; margin-top:8px;">黃經 {astro_data['saturn_deg']:.2f}°</div></div>
        </div>
        '''
        # --- 西洋占星大師級診斷引擎 ---
        zodiac_elements = {
            "牡羊座": "火象", "獅子座": "火象", "射手座": "火象",
            "金牛座": "土象", "處女座": "土象", "摩羯座": "土象",
            "雙子座": "風象", "天秤座": "風象", "水瓶座": "風象",
            "巨蟹座": "水象", "天蠍座": "水象", "雙魚座": "水象"
        }
        sun_ele = zodiac_elements.get(astro_data['sun'], "未知")
        moon_ele = zodiac_elements.get(astro_data['moon'], "未知")
        asc_ele = zodiac_elements.get(astro_data['asc'], "未知") if "精確" in time_mode else "未知"
        
        elements = [sun_ele, moon_ele]
        if asc_ele != "未知": elements.append(asc_ele)
        ele_counts = {e: elements.count(e) for e in ["火象", "土象", "風象", "水象"]}
        
        if sun_ele == moon_ele:
            astro_text = f"您的太陽與月亮同屬【{sun_ele}】，這代表您的內外在高度一致，表裡如一。您極少會有自我矛盾的糾結感，做決定時通常乾脆果斷，因為您的社會目標與潛意識需求完美契合。"
        else:
            astro_text = f"您的太陽屬於【{sun_ele}】而月亮屬於【{moon_ele}】。這賦予您極具層次感的靈魂：對外展現出{sun_ele}的特質，但內心卻由{moon_ele}的需求驅動。有時會感到理智與情感的拉扯，但也正是這種矛盾與張力，讓您具備更廣闊的同理心與多面貌的魅力。"
            
        if asc_ele != "未知":
            if asc_ele == sun_ele:
                astro_text += f" 您的上升星座也是【{asc_ele}】，這讓您的外在形象與核心意志完全疊合，給人的第一印象極度鮮明強烈。"
            else:
                astro_text += f" 您的上升星座落在【{asc_ele}】，這是您為了適應社會而戴上的面具，它會巧妙地修飾您原本太陽{sun_ele}的銳利或內向，幫助您在人群中找到最佳的生存姿態。"
        
        dominant_ele = max(ele_counts, key=ele_counts.get) if elements else ""
        ele_text = ""
        if dominant_ele == "火象" and ele_counts["火象"] >= 2:
            ele_text = "命盤中【火象】能量極強，代表您行動力爆棚、直覺敏銳、充滿熱情與開創力，適合扮演開路先鋒的角色。"
        elif dominant_ele == "土象" and ele_counts["土象"] >= 2:
            ele_text = "命盤中【土象】能量主導，賦予您極強的物質具現化能力。務實、可靠、重視結構與效率，是將夢想變為現實的執行者。"
        elif dominant_ele == "風象" and ele_counts["風象"] >= 2:
            ele_text = "命盤中【風象】能量活躍，象徵著資訊、邏輯與人際傳播。您具備極佳的客觀分析能力與溝通技巧，擅長靠腦力與概念變現。"
        elif dominant_ele == "水象" and ele_counts["水象"] >= 2:
            ele_text = "命盤中【水象】能量豐沛，代表您的同理心、情緒感知力與靈性天賦極高。適合從事療癒、藝術或需要深度共情的領域。"

        astro_diagnosis_html = f'''
        <div style="max-width: 1400px; margin: 20px auto 40px auto; background: linear-gradient(145deg, #ffffff, #F3E5F5); border-left: 6px solid #4A148C; border-radius: 8px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); font-family: 'MingLiU', 'PMingLiU', 'Noto Serif TC', serif;">
            <h3 style="color: #4A148C; margin-top: 0; margin-bottom: 20px; font-weight: bold; font-size: 24px; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px;">
                <span style="font-size: 28px;">🌌</span> 西洋占星 · 日月升深度診斷
            </h3>
            
            <div style="margin-bottom: 20px;">
                <h4 style="color: #0D47A1; margin-bottom: 8px; font-size: 20px; font-weight: bold;">📌 內外在靈魂組合</h4>
                <p style="color: #333; font-size: 18px; line-height: 1.6; margin: 0; background-color: #E3F2FD; padding: 12px; border-radius: 6px;">
                    {astro_text}
                </p>
            </div>
            
            <div>
                <h4 style="color: #00838F; margin-bottom: 8px; font-size: 20px; font-weight: bold;">📌 元素主導與天賦</h4>
                <p style="color: #333; font-size: 18px; line-height: 1.6; margin: 0; background-color: #E0F7FA; padding: 12px; border-radius: 6px;">
                    {ele_text if ele_text else "星盤核心元素相對均衡，代表您的人生發展具備極高的全面性，不易陷入單一的盲點，且具有極佳的自我調適能力。"}
                </p>
            </div>
        </div>
        '''
        html_content += astro_diagnosis_html

        st.markdown(re.sub(r'\n\s*', '', html_content), unsafe_allow_html=True)
        # ==========================================
        # 5. 空間擴充：流年九宮飛星
        # ==========================================
        st.markdown("<br><h2 style='color:#000; font-family:serif; text-align:center; font-weight:bold; font-size:26px;'>🧭 流年九宮飛星 (玄空風水空間佈局)</h2>", unsafe_allow_html=True)
        st.markdown(f'<div class="fengshui-grid">{get_flying_stars(current_year)}</div>', unsafe_allow_html=True)

        # --- 流年九宮飛星大師級診斷引擎 ---
        sum_digits = sum(int(d) for d in str(current_year))
        while sum_digits > 9: sum_digits = sum(int(d) for d in str(sum_digits))
        center_star = 11 - sum_digits
        if center_star > 9: center_star -= 9

        flight_offsets = {"中": 0, "西北": 1, "西": 2, "東北": 3, "南": 4, "北": 5, "西南": 6, "東": 7, "東南": 8}
        grid_positions = ["東南", "南", "西南", "東", "中", "西", "東北", "北", "西北"]
        
        pos_5, pos_2, pos_8, pos_9 = "", "", "", ""
        for pos in grid_positions:
            star_num = (center_star + flight_offsets[pos])
            if star_num > 9: star_num -= 9
            if star_num == 5: pos_5 = pos
            if star_num == 2: pos_2 = pos
            if star_num == 8: pos_8 = pos
            if star_num == 9: pos_9 = pos

        fs_diagnosis_html = f'''
        <div style="max-width: 1400px; margin: 20px auto 40px auto; background: linear-gradient(145deg, #ffffff, #F5F5F5); border-left: 6px solid #212121; border-radius: 8px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); font-family: 'MingLiU', 'PMingLiU', 'Noto Serif TC', serif;">
            <h3 style="color: #212121; margin-top: 0; margin-bottom: 20px; font-weight: bold; font-size: 24px; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px;">
                <span style="font-size: 28px;">🧭</span> 流年飛星 · 空間風水催旺化煞指南 ({current_year}年)
            </h3>
            
            <div style="margin-bottom: 20px;">
                <h4 style="color: #B71C1C; margin-bottom: 8px; font-size: 20px; font-weight: bold;">⚠️ 大凶方位化解 (五黃、二黑)</h4>
                <p style="color: #333; font-size: 18px; line-height: 1.6; margin: 0; background-color: #FFEBEE; padding: 12px; border-radius: 6px;">
                    本年度最兇險的「五黃災瘟星」飛臨<b>【{pos_5}方】</b>，而「二黑病符星」飛臨<b>【{pos_2}方】</b>。這兩個方位在今年<b>絕對不可動土、裝修或擺放紅色物品/常綠植物</b>。若家中的大門、臥室或廚房剛好落在此二方，容易引發疾病或破財，建議在此處懸掛六帝錢、銅鈴等金屬製品來洩其土氣化煞。
                </p>
            </div>
            
            <div>
                <h4 style="color: #E65100; margin-bottom: 8px; font-size: 20px; font-weight: bold;">💰 大吉方位催旺 (八白、九紫)</h4>
                <p style="color: #333; font-size: 18px; line-height: 1.6; margin: 0; background-color: #FFF8E1; padding: 12px; border-radius: 6px;">
                    本年度的第一大財星「八白正財星」飛臨<b>【{pos_8}方】</b>，而代表喜慶與桃花的「九紫星」飛臨<b>【{pos_9}方】</b>。強烈建議在您家中的<b>{pos_8}方</b>保持明亮、乾淨，可擺放聚寶盆、撲滿或流動水景來催旺正財；若想求姻緣或懷孕喜事，可在<b>{pos_9}方</b>擺放紅色系花卉或常亮的小燈，讓吉星能量極大化。
                </p>
            </div>
        </div>
        '''
        st.markdown(re.sub(r'\n\s*', '', fs_diagnosis_html), unsafe_allow_html=True)

        # 今日專屬開運指南
        from datetime import date
        today = date.today()
        # 簡單的九宮方位運算 (簡化邏輯，取當日日干支對應的喜神/財神方位)
        lunar_today = Solar.fromYmd(today.year, today.month, today.day).getLunar()
        today_caushen = lunar_today.getDayPositionCaiDesc().replace('东', '東')
        today_xishen = lunar_today.getDayPositionXiDesc().replace('东', '東')
        today_fushen = lunar_today.getDayPositionFuDesc().replace('东', '東')
        
        all_wuxing = eight_char.getYearWuXing() + eight_char.getMonthWuXing() + eight_char.getDayWuXing()
        if "精確" in time_mode: all_wuxing += eight_char.getTimeWuXing()
        count_elements = {e: all_wuxing.count(e) for e in "金木水火土"}
        
        favorable_elements = [k for k, v in count_elements.items() if v <= 1] # 簡單抓欠缺的五行
        if not favorable_elements: favorable_elements = ["水", "木"] # 預設
        
        daily_guide_html = f'''
        <div style="max-width: 1400px; margin: 40px auto; background-color: #FFF3E0; padding: 30px; border-radius: 15px; border-left: 8px solid #FF8F00; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <h2 style="color: #E65100; margin-bottom: 20px; font-family: 'MingLiU', 'PMingLiU', 'Noto Serif TC', serif; font-weight: bold;">🌟 今日專屬開運指南 ({today.strftime("%Y-%m-%d")})</h2>
            <div style="display: flex; flex-wrap: wrap; gap: 20px; font-size: 20px; color: #424242; font-family: 'MingLiU', 'PMingLiU', 'Noto Serif TC', serif;">
                <div style="flex: 1; min-width: 250px; background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                    <div style="font-weight: bold; color: #D84315; margin-bottom: 10px;">🧭 今日大吉方位</div>
                    財神：<b>{today_caushen}方</b><br>
                    喜神：<b>{today_xishen}方</b><br>
                    福神：<b>{today_fushen}方</b><br>
                    <div style="font-size: 16px; color: #757575; margin-top: 10px;">(簽約、買彩券、重要決策請朝此方位)</div>
                </div>
                <div style="flex: 1; min-width: 250px; background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                    <div style="font-weight: bold; color: #1565C0; margin-bottom: 10px;">🎨 今日幸運密碼</div>
                    本命缺補五行：<b style="color: #1976D2;">{'、'.join(favorable_elements)}</b><br>
                    <div style="font-size: 16px; color: #757575; margin-top: 10px;">(今日衣著配飾可多運用此五行相關顏色，水為藍黑、木為青綠、火為紅紫、土為黃棕、金為白金)</div>
                </div>
            </div>
        </div>
        '''
        st.markdown(daily_guide_html, unsafe_allow_html=True)

        # ==========================================
        # 6. 時間擴充：五行能量圖表
        # ==========================================
        st.markdown("<br><h2 style='color:#000; font-family:serif; text-align:center; font-weight:bold; font-size:26px;'>📊 流年五行能量真實起伏軌跡 (1990 - 2040)</h2>", unsafe_allow_html=True)
        # 1. 取得命主日元與五行
        day_master = eight_char.getDayGan()
        WU_XING_MAP = {'甲':'木', '乙':'木', '丙':'火', '丁':'火', '戊':'土', '己':'土', '庚':'金', '辛':'金', '壬':'水', '癸':'水'}
        day_element = WU_XING_MAP.get(day_master, '水')

        # 2. 十神五行映射
        TEN_GODS_MAP = {
            '木': {'resource': '水', 'output': '火'},
            '火': {'resource': '木', 'output': '土'},
            '土': {'resource': '火', 'output': '金'},
            '金': {'resource': '土', 'output': '水'},
            '水': {'resource': '金', 'output': '木'}
        }
        resource_element = TEN_GODS_MAP[day_element]['resource']
        output_element = TEN_GODS_MAP[day_element]['output']

        # 3. 流年五行權重定義 (天干與地支)
        ELEMENT_STEMS = {
            '木': ['甲', '乙'], '火': ['丙', '丁'], '土': ['戊', '己'], '金': ['庚', '辛'], '水': ['壬', '癸']
        }
        ELEMENT_BRANCHES = {
            '木': ['寅', '卯'], '火': ['巳', '午'], '土': ['辰', '戌', '丑', '未'], '金': ['申', '酉'], '水': ['亥', '子']
        }

        def get_real_energy(target_year, target_element):
            lunar_target = Solar.fromYmd(target_year, 6, 1).getLunar()
            year_ganzhi = lunar_target.getYearInGanZhi()
            score = 0
            if year_ganzhi[0] in ELEMENT_STEMS[target_element]: score += 30
            if year_ganzhi[1] in ELEMENT_BRANCHES[target_element]: score += 40
    
            # 加上平滑正弦波動，模擬宇宙週期 (印星用 sin, 食傷用 cos 製造交錯)
            wave = 15 * math.sin(target_year) if target_element == resource_element else 15 * math.cos(target_year)
            return 30 + score + wave

        years = list(range(1990, 2041))
        energy_resource, energy_output, hover_resource, hover_output = [], [], [], []

        rgba_map = {
            "#B71C1C": "rgba(183, 28, 28, ",  # 火
            "#0D47A1": "rgba(13, 71, 161, ",  # 水
            "#2E7D32": "rgba(46, 125, 50, ",  # 木
            "#F57F17": "rgba(245, 127, 23, ", # 土
            "#F9A825": "rgba(249, 168, 37, "  # 金
        }

        for y in years:
            r_val = get_real_energy(y, resource_element)
            o_val = get_real_energy(y, output_element)
            energy_resource.append(r_val)
            energy_output.append(o_val)
            gz = Solar.fromYmd(y, 6, 1).getLunar().getYearInGanZhi()
    
            # 專屬印星文字
            r_color = "#B71C1C" if resource_element == '火' else "#F57F17" if resource_element == '土' else "#0D47A1" if resource_element == '水' else "#2E7D32" if resource_element == '木' else "#F9A825"
            r_text = f"<span style='font-size:15px; color:{r_color};'>🛡️ <b>專屬印星 ({resource_element})：{r_val:.1f}</b></span><br>"
            r_text += "<b>【極旺】</b>貴人顯現，極利系統開發與知識吸收。" if r_val > 70 else ("<b>【平穩】</b>思路清晰，適合穩紮穩打累積專業實力。" if r_val > 45 else "<b>【偏弱】</b>提防決策失誤，凡事宜親力親為。")
            hover_resource.append(r_text)
    
            # 專屬食傷文字
            o_color = "#B71C1C" if output_element == '火' else "#F57F17" if output_element == '土' else "#0D47A1" if output_element == '水' else "#2E7D32" if output_element == '木' else "#F9A825"
            o_text = f"<span style='font-size:15px; color:{o_color};'>✨ <b>專屬食傷 ({output_element})：{o_val:.1f}</b></span><br>"
            o_text += "<b>【極旺】</b>表現慾強，技術變現力佳，靈感大爆發。" if o_val > 70 else ("<b>【平穩】</b>按部就班產出，精細工藝穩定發揮。" if o_val > 45 else "<b>【受制】</b>靈感枯竭，應避免衝動投資。")
            hover_output.append(f"<span style='font-size:18px;'><b>{y}年 ({gz}年)</b></span><br><br>{r_text}<br><br>{o_text}")

        # 自動尋找最高峰
        max_r_val = max(energy_resource)
        max_o_val = max(energy_output)
        peak_r_year = years[energy_resource.index(max_r_val)]
        peak_o_year = years[energy_output.index(max_o_val)]
        gz_r = Solar.fromYmd(peak_r_year, 6, 1).getLunar().getYearInGanZhi()
        gz_o = Solar.fromYmd(peak_o_year, 6, 1).getLunar().getYearInGanZhi()

        fig = go.Figure()

        # 動態替換圖表
        fig.add_trace(go.Scatter(x=years, y=energy_output, mode='lines', name=f'{output_element}能量 (食傷生財)', line=dict(color=o_color, width=3, shape='spline'), fill='tozeroy', fillcolor=rgba_map[o_color] + '0.15)', hoverinfo="text", hovertext=hover_output, hovertemplate="%{hovertext}<extra></extra>"))
        fig.add_trace(go.Scatter(x=years, y=energy_resource, mode='lines+markers', name=f'{resource_element}能量 (印星護身)', line=dict(color=r_color, width=3, dash='dot', shape='spline'), fill='tonexty', fillcolor=rgba_map[r_color] + '0.1)', hoverinfo="none"))

        # 動態標籤
        fig.add_annotation(
            x=peak_o_year, y=max_o_val,
            text=f'<b>{peak_o_year} {gz_o} 食傷大爆發 (才華變現)</b>', showarrow=True, arrowhead=2, ax=-50, ay=-60,
            bgcolor='#FFF9C4', font=dict(size=14, color='#000'),
        )
        fig.add_annotation(
            x=peak_r_year, y=max_r_val,
            text=f'<b>{peak_r_year} {gz_r} 印星極旺 (貴人相助)</b>', showarrow=True, arrowhead=2, ax=50, ay=-50,
            bgcolor='#FFCDD2', font=dict(size=14, color='#000'),
        )

        fig.update_layout(
            height=550,
            plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF', hoverlabel=dict(bgcolor="rgba(255, 255, 255, 0.95)", font_size=13, font_family="Noto Serif TC, serif", bordercolor="#333333"),
            hovermode="x unified",
            xaxis=dict(title=dict(text='<b>西元年份</b>', font=dict(size=16, color="#000")), tickfont=dict(size=14, color="#000"), showgrid=True, gridcolor='#EEEEEE', showspikes=True, spikemode="across", spikethickness=1, spikedash="solid", spikecolor="#666666"),
            yaxis=dict(title=dict(text='<b>能量指數</b>', font=dict(size=16, color="#000")), tickfont=dict(size=14, color="#000"), showgrid=True, gridcolor='#EEEEEE'),
            legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5, font=dict(size=16, color="#000", family="Arial, sans-serif")),
            margin=dict(l=50, r=50, t=50, b=80)
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # ==========================================
        # 7. 現代語意深度解析引擎
        # ==========================================
        STAR_MEANINGS = {
            "紫微": "整合資源、建立秩序與承擔決策責任",
            "天機": "邏輯推演、系統設計、科技工具、企劃與快速學習",
            "太陽": "公開表達、品牌能見度、服務他人與跨部門協作",
            "武曲": "財務紀律、工程實作、效率管理與可量化成果",
            "天同": "服務體驗、身心舒適、教育陪伴與生活美感",
            "廉貞": "規範意識、審美判斷、品牌定位與風險邊界",
            "天府": "資源配置、資料庫管理、後勤穩定與長期累積",
            "太陰": "影像光影、美學感受、資料整理、照顧支持與細膩觀察",
            "貪狼": "市場嗅覺、興趣探索、人際連結、表演與多元技能",
            "巨門": "語言表達、研究分析、議題辨析、顧問諮詢與溝通修正",
            "天相": "流程協調、品質把關、合作關係與制度化服務",
            "天梁": "專業傳承、顧問角色、風險控管、照護與倫理判斷",
            "七殺": "突破限制、危機處理、專案攻堅、轉型與高壓執行",
            "破軍": "創新拆解、舊系統改造、創業嘗試、非典型路線與變革",
        }

        TRANSFORM_MEANINGS = {
            "化祿": "帶來資源、機會與被看見的誘因",
            "化權": "帶來主導權、責任感與推動事情成形的壓力",
            "化科": "帶來名聲、學習力、作品品質與專業認可",
            "化忌": "提示卡點、焦慮源、反覆修正與需要耐心管理的議題",
        }

        def normalize_palace_name(name): return str(name or "").replace("【身】", "")
        def find_palace(keyword):
            for branch, palace in ziwei_palaces.items():
                if keyword in normalize_palace_name(palace.get("宮位", "")): return branch, palace
            return "", {}

        def words(text): return [item for item in str(text or "").split() if item]
        def star_phrase(star): return STAR_MEANINGS.get(star, "保留傳統星曜象意，需搭配宮位與四化細看")

        def palace_snapshot(keyword):
            branch, palace = find_palace(keyword)
            main_stars = words(palace.get("主星"))
            transforms = words(palace.get("四化文字"))
            lucky = words(palace.get("吉煞"))
            minor = words(palace.get("副星"))
            star_text = "、".join(main_stars) if main_stars else "無十四主星"
            transform_text = "、".join(transforms) if transforms else "無生年四化直接引動"
            support_text = "、".join((lucky + minor)[:5]) if (lucky or minor) else "輔星訊號較少"
            return {
                "branch": branch, "palace": palace,
                "name": normalize_palace_name(palace.get("宮位", keyword)) if palace else keyword,
                "stars": main_stars, "transforms": transforms, "support": support_text,
                "star_text": star_text, "transform_text": transform_text,
            }

        def describe_star_set(snapshot, fallback_focus):
            if not snapshot["stars"]: return f"此宮沒有十四主星坐守，判讀上更重視對宮、三方四正與輔星，現代語意上可視為以環境條件塑造{fallback_focus}。"
            phrases = [f"{star}代表{star_phrase(star)}" for star in snapshot["stars"]]
            return "；".join(phrases) + "。"

        def describe_transforms(snapshot):
            if not snapshot["transforms"]: return "此宮沒有生年四化直接落入，表示事件推動較不靠單一強烈觸發點，適合用長期節奏與外部條件慢慢累積。"
            parts = []
            for item in snapshot["transforms"]:
                matched = next((key for key in TRANSFORM_MEANINGS if item.endswith(key)), "")
                if matched: parts.append(f"{item}{TRANSFORM_MEANINGS[matched]}")
                else: parts.append(item)
            return "；".join(parts) + "。"

        def build_modern_report():
            ming = palace_snapshot("命宮")
            career = palace_snapshot("官祿")
            wealth = palace_snapshot("財帛")
            travel = palace_snapshot("遷移")
            children = palace_snapshot("子女")
            spouse = palace_snapshot("夫妻")
            parents = palace_snapshot("父母")
            spirit = palace_snapshot("福德")

            career_focus = describe_star_set(career, "職涯走向")
            career_transform = describe_transforms(career)
            wealth_focus = describe_star_set(wealth, "收入模式")
            ming_focus = describe_star_set(ming, "人格核心")

            travel_focus = describe_star_set(travel, "外在發展")
            travel_transform = describe_transforms(travel)
            spirit_focus = describe_star_set(spirit, "興趣與精神恢復")

            children_focus = describe_star_set(children, "子女互動與作品成果")
            children_transform = describe_transforms(children)
            spouse_focus = describe_star_set(spouse, "伴侶合作")
            parents_focus = describe_star_set(parents, "長輩與制度資源")
    
            path_names = ["中宮", "西北方", "正西方", "東北方", "正南方", "正北方", "西南方", "正東方", "東南方"]
            center_star = 11 - (sum(int(d) for d in str(current_year)) % 9)
            center_star = center_star if center_star <= 9 else center_star - 9
            pos_5 = path_names[(5 - center_star) % 9]
            pos_8 = path_names[(8 - center_star) % 9]
            pos_9 = path_names[(9 - center_star) % 9]

            paragraphs = []
            paragraphs.append(f"<p><b>【職涯規劃與工作定位】</b> 官祿宮落在 <span style='color:#1565C0;font-weight:bold;'>{career['branch']}宮</span>，主星為 <span style='color:#C62828;font-weight:bold;'>{career['star_text']}</span>，四化訊號為 <span style='color:#7B1FA2;font-weight:bold;'>{career['transform_text']}</span>。{career_focus}{career_transform} 以現代職涯語言來看，這代表適合把工作拆成「可被設計、可被驗證、可被交付」的流程；若再參照財帛宮（{wealth['branch']}宮，{wealth['star_text']}），{wealth_focus} 因此職涯上可優先考慮系統規劃、技術工具、內容製作、顧問服務、營運管理或需要長期作品累積的專業路線。</p>")
            paragraphs.append(f"<p><b>【人格優勢與興趣潛能】</b> 命宮位於 <span style='color:#1565C0;font-weight:bold;'>{ming['branch']}宮</span>，主星為 <span style='color:#C62828;font-weight:bold;'>{ming['star_text']}</span>。{ming_focus} 福德宮位於 {spirit['branch']}宮，主星為 {spirit['star_text']}，{spirit_focus} 這組訊號適合轉化為可長期投入的興趣：例如影像、模型、設計、資料整理、語言研究、工具自動化、策展式旅行或任何需要反覆打磨細節的專案。這不是單純娛樂，而是讓命盤能量恢復、沉澱並形成作品的方法。</p>")
            paragraphs.append(f"<p><b>【外在世界與遷移發展】</b> 遷移宮位於 <span style='color:#1565C0;font-weight:bold;'>{travel['branch']}宮</span>，主星為 <span style='color:#C62828;font-weight:bold;'>{travel['star_text']}</span>，四化為 {travel['transform_text']}。{travel_focus}{travel_transform} 現代語意上，遷移宮不只代表旅行，也代表跨城市、跨國、跨領域、跨社群的互動方式。當遷移宮被主星或四化引動時，適合透過外出觀察、國際資訊、遠距合作、展覽參訪、攝影記錄或不同文化場景來擴大視野；若身宮落在遷移或與遷移三方有連動，外在世界更容易成為人生後半段的重要養分。</p>")
            paragraphs.append(f"<p><b>【家庭關係與互動模式】</b> 子女宮位於 <span style='color:#1565C0;font-weight:bold;'>{children['branch']}宮</span>，主星為 <span style='color:#C62828;font-weight:bold;'>{children['star_text']}</span>，四化為 {children['transform_text']}。{children_focus}{children_transform} 在現代解讀中，子女宮也可延伸為作品、學生、晚輩與創作成果，因此它描述的是「如何陪伴下一代，也如何讓自己的成果被延伸」。夫妻宮位於 {spouse['branch']}宮，{spouse_focus} 父母宮位於 {parents['branch']}宮，{parents_focus} 家庭議題建議以溝通節奏、資源分配與界線感來經營，避免把命盤訊號解讀成絕對事件。</p>")
            paragraphs.append(f"<p><b>【三軌合參：八字 × 紫微 × 生命靈數】</b> 主頻率為 <span style='color:#6A1B9A;font-weight:bold;'>生命靈數 {life_path_num}（{lp_title}）</span>。其現代語意為：{lp_desc} 若與東方八字日主「{eight_char.getDay()[0]}」、紫微命宮 {ming['branch']}宮（{ming['star_text']}）一起參照，可把先天氣質拆成三層：八字看能量結構，紫微看人生場域與事件位置，靈數則補充個人動機、表達方式與長期課題。</p>")
            paragraphs.append(f"<p><b>【盲派六柱與本命神煞】</b> 胎元 <span style='color:#C62828;font-weight:bold;'>{tai_yuan}</span>，命宮 <span style='color:#C62828;font-weight:bold;'>{ming_gong}</span>。本命六神煞檢出為 <span style='color:#C62828;font-weight:bold;'>{'、'.join(shen_sha_list) if shen_sha_list else '未明顯引動'}</span>。神煞適合做性格傾向與事件提醒，不宜孤立斷事；它的價值在於指出命盤中比較容易被環境觸發的題目，例如貴人、文書、移動、創作、孤高研究或口舌壓力。</p>")
            paragraphs.append(f"<p><b>【玄空流年九宮飛星】</b> {current_year} 年以數字和化約後代入 11 減年數法，推得 <span style='color:#1565C0;font-weight:bold;'>{center_star} 白</span> 入中宮。年度方位重點為：<span style='color:#B71C1C;font-weight:bold;'>{pos_5}</span> 見五黃需避免動土擾動；<span style='color:#0D47A1;font-weight:bold;'>{pos_8}</span> 見八白可作穩健財務與成果累積位；<span style='color:#0D47A1;font-weight:bold;'>{pos_9}</span> 見九紫利喜慶、曝光與品牌。此盤屬流年層，仍需與住宅坐向、元運、實際格局合看。</p>")
            asc_text = astro_data['asc'] if '精確' in time_mode else '需精確時間'
            paragraphs.append(f"<p><b>【Swiss Ephemeris 星曆校正說明】</b> 本系統底層採用 <code>pyswisseph</code> 與 Swiss Ephemeris 計算天文資料，真太陽時為 <span style='color:#C62828;font-weight:bold;'>{true_datetime.strftime('%H:%M:%S')}</span>。東方八字日主為「{eight_char.getDay()[0]}」；西方占星顯示太陽 <span style='color:#1565C0;font-weight:bold;'>{astro_data['sun']}</span>、月亮 <span style='color:#1565C0;font-weight:bold;'>{astro_data['moon']}</span>、上升 <span style='color:#C62828;font-weight:bold;'>{asc_text}</span>。這些資訊用來輔助理解人格與外在表現，不做絕對斷言；真正有價值的是把命盤傾向轉化成可行的職涯安排、家庭溝通與生活選擇。</p>")
            return "\n".join(paragraphs)

        modern_report_html = build_modern_report()
        st.markdown(f"""
        <div style="border: 3px solid #000000; background-color: #FAFAFA; padding: 25px; border-radius: 4px; font-family: 'PMingLiU', serif; color:#000; box-shadow: 6px 6px 0px rgba(0,0,0,0.8);">
            <h3 style="color: #000; margin-top:0; border-bottom:2px solid #000; padding-bottom:12px; font-weight:bold; font-size:22px;">現代語意·萬象合參深度命理剖析 🔗</h3>
            <div style="font-size: 15px; line-height: 2.0; color: #111; font-weight: 500;">
                {modern_report_html}
            </div>
        </div>
        <br><br>
        """, unsafe_allow_html=True)
