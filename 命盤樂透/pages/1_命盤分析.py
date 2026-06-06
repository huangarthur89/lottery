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
from datetime import datetime, timedelta
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

st.set_page_config(page_title="命盤分析", layout="wide", initial_sidebar_state="expanded")

# === 整合版專屬：返回首頁按鈕 ===
if st.button("⬅ 返回整合首頁", use_container_width=False):
    st.switch_page("app.py")
st.markdown("<hr style='margin-top:5px; margin-bottom:20px;'>", unsafe_allow_html=True)

# ==========================================
# 1. 核心 CSS 設定
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; color: #000000; }
    .ziwei-square-board {
        display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); grid-template-rows: repeat(4, minmax(0, 1fr));
        width: min(100%, 1040px); aspect-ratio: 1 / 1; margin: 0 auto;
        background-color: #FFFFFF; border: 3px solid #000000;
        font-family: "MingLiU", "PMingLiU", "Noto Serif TC", serif; box-sizing: border-box;
    }
    .palace-cell { border: 1px solid #222222; position: relative; padding: 5px; box-sizing: border-box; overflow: hidden; background: #fff; }
    .center-hall { grid-column: 2 / 4; grid-row: 2 / 4; border: 2px solid #000000; position: relative; padding: 16px 18px; background-color: #FDFDFD; box-sizing: border-box; overflow: hidden; }
    .p-left-col { position: absolute; top: 5px; left: 6px; width: 48px; display: grid; grid-template-columns: repeat(2, 1fr); gap: 2px; font-size: 13px; line-height: 1.08; color: #222; font-weight: 700; }
    .vertical-note { writing-mode: vertical-rl; text-orientation: upright; min-height: 58px; white-space: nowrap; }
    .p-right-col { position: absolute; top: 5px; right: 6px; width: 82px; text-align: right; font-size: 13px; line-height: 1.12; color: #111; font-weight: 700; }
    .main-star { font-size: 20px; font-weight: 900; color: #111; letter-spacing: 0; line-height: 1.12; }
    .minor-star { color: #333; font-size: 12px; font-weight: 600; }
    .transform-line { color: #7B1FA2; font-size: 12px; font-weight: 800; margin-top: 2px; }
    .flow-year { position: absolute; left: 58px; top: 56px; color: #D32F2F; font-size: 17px; font-weight: 900; line-height: 1.25; text-align: center; white-space: nowrap; }
    .age-row { position: absolute; left: 24px; right: 26px; bottom: 41px; display: flex; justify-content: space-between; color: #222; font-size: 11px; line-height: 1; }
    .bottom-left { position: absolute; left: 8px; bottom: 6px; font-size: 12px; line-height: 1.15; color: #111; font-weight: 700; }
    .palace-name { color: #C62828; font-size: 15px; font-weight: 900; display: block; margin-top: 2px; }
    .bottom-right { position: absolute; right: 7px; bottom: 6px; font-size: 12px; line-height: 1.12; color: #111; text-align: right; font-weight: 800; }
    .gan-branch { font-size: 13px; font-weight: 900; }
    .center-lines { position: absolute; inset: 0; pointer-events: none; z-index: 1; }
    .center-text { position: relative; z-index: 2; font-size: 15px; line-height: 1.55; color: #000; }
    .center-title { color: #111; font-size: 16px; font-weight: 900; text-align: left; margin-bottom: 8px; letter-spacing: 0; }
    .center-grid { display: grid; grid-template-columns: 68px 1fr 58px 1fr; gap: 2px 8px; align-items: baseline; max-width: 380px; margin: 0 auto; }
    .center-label { font-weight: 900; text-align: right; }
    .center-value { font-weight: 700; }
    .center-brand { margin-top: 18px; margin-left: 34px; line-height: 1.25; font-weight: 800; }
    .small-blue { color: #1565C0; font-size: 13px; }
    .small-red { color: #C62828; font-weight: 900; }
    .shensha-tag { background-color: #FBE9E7; color: #C62828; padding: 1px 6px; border-radius: 3px; font-size: 13px; font-weight: bold; border: 1px solid #FFCCBC; margin-right: 4px;}
    
    .astro-container { display: flex; justify-content: space-between; gap: 12px; margin-top: 25px; margin-bottom: 25px; max-width: 1040px; margin-left: auto; margin-right: auto;}
    .astro-card { flex: 1; border: 2px solid #000; padding: 15px; background-color: #FAFAFA; text-align: center; font-family: "MingLiU", "PMingLiU", "Noto Serif TC", serif; box-shadow: 3px 3px 0px #1A237E; border-radius: 2px; }
    .astro-title { font-size: 15px; color: #333; font-weight: bold; letter-spacing: 1px; border-bottom: 1px solid #CCC; padding-bottom: 5px; margin-bottom: 10px;}
    .astro-value { font-size: 26px; color: #000; font-weight: bold; letter-spacing: 0; }
    .astro-element { display: inline-block; margin-top: 10px; padding: 4px 10px; background-color: #000; color: #FFF; font-size: 13px; font-weight:bold; border-radius: 2px; }

    .fengshui-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; width: 100%; max-width: 420px; margin: 15px auto; aspect-ratio: 1; font-family: "MingLiU", "PMingLiU", "Noto Serif TC", serif;}
    .fs-cell { border: 2px solid #333; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; background: #FFF; box-shadow: 2px 2px 0px #000; }
    .fs-dir { position: absolute; top: 4px; left: 6px; font-size: 14px; font-weight: bold; color: #555; }
    .fs-star-num { font-size: 42px; font-weight: 900; margin-bottom: -5px; line-height: 1;}
    .fs-star-name { font-size: 15px; font-weight: bold; padding: 2px 8px; border-radius: 3px; color: #FFF; margin-top: 4px;}
    .fs-desc { font-size: 13px; color: #333; margin-top: 5px; font-weight: bold; letter-spacing: 1px;}
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
    asc_pos = swe.houses(jd_ut, latitude, longitude, b'P')[1][0]
    zodiac_signs = ["白羊座", "金牛座", "雙子座", "巨蟹座", "獅子座", "處女座", "天秤座", "天蠍座", "射手座", "摩羯座", "水瓶座", "雙魚座"]
    elements = ["火象", "土象", "風象", "水象"]
    def get_info(deg): return zodiac_signs[int(deg // 30)], elements[int(deg // 30) % 4], deg
    s_s, s_e, s_d = get_info(sun_pos)
    m_s, m_e, m_d = get_info(moon_pos)
    a_s, a_e, a_d = get_info(asc_pos)
    return {"sun": s_s, "sun_element": s_e, "sun_deg": s_d, "moon": m_s, "moon_element": m_e, "moon_deg": m_d, "asc": a_s, "asc_deg": a_d, "jd": jd_ut}

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
# 3. 側邊欄控制台 (結合地理庫與防呆日期)
# ==========================================
LOCATION_DB = {
    "基隆市": (121.74, 25.13, 8.0),
    "台北市": (121.56, 25.04, 8.0),
    "新北市": (121.46, 25.01, 8.0),
    "桃園市": (121.30, 24.99, 8.0),
    "新竹市": (120.96, 24.81, 8.0),
    "苗栗縣": (120.82, 24.56, 8.0),
    "台中市": (120.67, 24.14, 8.0),
    "彰化縣": (120.54, 24.05, 8.0),
    "南投縣": (120.68, 23.90, 8.0),
    "雲林縣": (120.52, 23.70, 8.0),
    "嘉義市": (120.44, 23.48, 8.0),
    "台南市": (120.22, 22.99, 8.0),
    "高雄市": (120.30, 22.62, 8.0),
    "屏東縣": (120.48, 22.67, 8.0),
    "宜蘭縣": (121.75, 24.76, 8.0),
    "花蓮縣": (121.60, 23.98, 8.0),
    "台東縣": (121.14, 22.75, 8.0),
    "日本大阪": (135.50, 34.69, 9.0),
    "日本京都": (135.76, 35.01, 9.0),
    "日本名古屋": (136.90, 35.18, 9.0),
    "澳洲雪梨": (151.20, -33.86, 10.0),
    "美國波士頓": (-71.05, 42.36, -5.0),
    "手動輸入經緯度": (None, None, None)
}

with st.sidebar:
    st.markdown("### 🔮 天體與大師校正面板")
    name = st.text_input("命主", "匿名")
    gender = st.radio("性別", ["乾造 (男)", "坤造 (女)"])
    gender_int = 1 if "男" in gender else 0
    
    # 動態推算未來 3 個月 (擇日剖腹防呆)
    today = datetime.now()
    future_limit = today + timedelta(days=90)
    
    b_date = st.date_input(
        "公曆出生日", 
        value=datetime(1971, 9, 30),
        min_value=datetime(1930, 1, 1),
        max_value=future_limit
    )
    
    # 【修復重點】：正確補上時間精確度選擇鈕！
    time_mode = st.radio("出生時間精確度", ["✅ 知道精確時間", "❓ 不知道時間 (吉時)"])
    
    if "不知道" in time_mode:
        # 代入中性時間確保底層不崩潰
        b_time = datetime(1971, 9, 30, 12, 0).time()
        st.info("🕒 已為您代入中性【吉時 (午時)】排盤，確保年月日的五行精準度。")
    else:
        b_time = st.time_input("公曆出生時", datetime(1971, 9, 30, 4, 0).time())
    
    st.markdown("---")
    st.markdown("#### 🧭 出生地與天文校正")
    
    loc_choice = st.selectbox("出生地", list(LOCATION_DB.keys()), index=0)
    
    if loc_choice == "手動輸入經緯度":
        longitude = st.number_input("經度 (東經)", value=121.74, step=0.01, format="%.2f")
        latitude = st.number_input("緯度 (北緯)", value=25.13, step=0.01, format="%.2f")
        tz_offset = st.number_input("時區偏移 (UTC+)", value=8.0, step=0.5, format="%.1f")
    else:
        longitude, latitude, tz_offset = LOCATION_DB[loc_choice]
        st.info(f"📍 自動代入 {loc_choice} 天文座標\n\n經度：{longitude}\n\n緯度：{latitude}\n\n時區：UTC{tz_offset:+.1f}")
    
    true_datetime, total_offset, eot = calculate_true_solar_time(b_date, b_time, longitude, timezone_base=tz_offset*15.0)
    
    if "不知道" in time_mode:
        st.success("**系統提示:**\n吉時排盤 (真時僅供參考)")
    else:
        st.success(f"**真太陽時:**\n{true_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
        
    st.markdown("---")
    st.markdown("#### ⚙️ 流派排盤精密設定")
    zi_hour_rule = st.selectbox("子時換日排法", ["早晚子時區分", "一律換日"])

# ==========================================
# 4. 資料生成與排盤佈局
# ==========================================
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
    
    return f'''
    <div class="palace-cell">
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

<div class="astro-container">
    <div class="astro-card"><div class="astro-title">☀️ 太陽 (外在意志)</div><div class="astro-value">{astro_data['sun']}</div><div class="astro-element" style="background-color: #B71C1C;">{astro_data['sun_element']}特質</div><div style="font-size:12px; color:#666; margin-top:5px;">黃經 {astro_data['sun_deg']:.2f}°</div></div>
    <div class="astro-card"><div class="astro-title">🌙 月亮 (潛意識)</div><div class="astro-value">{astro_data['moon']}</div><div class="astro-element" style="background-color: #0D47A1;">情緒與安全感</div><div style="font-size:12px; color:#666; margin-top:5px;">黃經 {astro_data['moon_deg']:.2f}°{moon_disclaimer}</div></div>
    <div class="astro-card"><div class="astro-title">✨ 上升 (社會人格)</div><div class="astro-value">{astro_data['asc'] if "精確" in time_mode else "--"}</div><div class="astro-element" style="background-color: #FBC02D; color:#000;">{ "面具與舵手" if "精確" in time_mode else "需精準時間" }</div><div style="font-size:12px; color:#666; margin-top:5px;">{f"黃經 {astro_data['asc_deg']:.2f}°" if "精確" in time_mode else "無法計算"}</div></div>
    <div class="astro-card" style="box-shadow: 3px 3px 0px #4A148C;"><div class="astro-title">🔢 生命靈數</div><div class="astro-value">{life_path_num}</div><div class=\"astro-element\" style="background-color: #4A148C;">{lp_title}</div><div style="font-size:12px; color:#666; margin-top:5px;">{lp_desc}</div></div>
</div>
'''
st.markdown(re.sub(r'\n\s*', '', html_content), unsafe_allow_html=True)

# ==========================================
# 5. 空間擴充：流年九宮飛星
# ==========================================
st.markdown("<br><h2 style='color:#000; font-family:serif; text-align:center; font-weight:bold; font-size:26px;'>🧭 流年九宮飛星 (玄空風水空間佈局)</h2>", unsafe_allow_html=True)
st.markdown(f'<div class="fengshui-grid">{get_flying_stars(current_year)}</div>', unsafe_allow_html=True)

# ==========================================
# 6. 時間擴充：五行能量圖表
# ==========================================
st.markdown("<br><h2 style='color:#000; font-family:serif; text-align:center; font-weight:bold; font-size:26px;'>📊 流年五行能量真實起伏軌跡 (1990 - 2040)</h2>", unsafe_allow_html=True)
FIRE_ELEMENTS = {"丙": 30, "丁": 30, "巳": 40, "午": 40, "寅": 15, "戌": 10}
WATER_ELEMENTS = {"壬": 30, "癸": 30, "亥": 40, "子": 40, "申": 15, "丑": 10}

def get_real_energy(target_year):
    lunar_target = Solar.fromYmd(target_year, 6, 1).getLunar()
    year_ganzhi = lunar_target.getYearInGanZhi()
    score_fire = FIRE_ELEMENTS.get(year_ganzhi[0], 0) + FIRE_ELEMENTS.get(year_ganzhi[1], 0)
    score_water = WATER_ELEMENTS.get(year_ganzhi[0], 0) + WATER_ELEMENTS.get(year_ganzhi[1], 0)
    return 30 + score_fire + 15 * math.sin(target_year), 30 + score_water + 15 * math.cos(target_year)

years = list(range(1990, 2041))
energy_fire, energy_water, hover_fire, hover_water = [], [], [], []

for y in years:
    f_val, w_val = get_real_energy(y)
    energy_fire.append(f_val); energy_water.append(w_val)
    gz = Solar.fromYmd(y, 6, 1).getLunar().getYearInGanZhi()
    
    f_text = f"<span style='font-size:15px; color:#B71C1C;'>🔥 <b>火土印星：{f_val:.1f}</b></span><br>"
    f_text += "<b>【極旺】</b>貴人顯現，極利系統開發與知識吸收。" if f_val > 70 else ("<b>【平穩】</b>思路清晰，適合穩紮穩打累積專業實力。" if f_val > 45 else "<b>【偏弱】</b>提防決策失誤，凡事宜親力親為。")
    hover_fire.append(f_text)
    
    w_text = f"<span style='font-size:15px; color:#0D47A1;'>💧 <b>金水食傷：{w_val:.1f}</b></span><br>"
    w_text += "<b>【極旺】</b>表現慾強，技術變現力佳，利於攝影創作。" if w_val > 70 else ("<b>【平穩】</b>按部就班產出，精細工藝穩定發揮。" if w_val > 45 else "<b>【受制】</b>靈感枯竭，應避免衝動投資。")
    hover_water.append(f"<span style='font-size:18px;'><b>{y}年 ({gz}年)</b></span><br><br>{w_text}")

fig = go.Figure()
fig.add_trace(go.Scatter(x=years, y=energy_water, mode='lines', name='金水能量 (食傷生財)', line=dict(color='#0D47A1', width=3, shape='spline'), fill='tozeroy', fillcolor='rgba(13, 71, 161, 0.15)', hoverinfo="text", hovertext=hover_water, hovertemplate="%{hovertext}<extra></extra>"))
fig.add_trace(go.Scatter(x=years, y=energy_fire, mode='lines+markers', name='火土能量 (印星護身)', line=dict(color='#B71C1C', width=3, dash='dot', shape='spline'), fill='tonexty', fillcolor='rgba(183, 28, 28, 0.1)', hoverinfo="text", hovertext=hover_fire, hovertemplate="%{hovertext}<extra></extra>"))

fig.add_annotation(
    x=2017, y=energy_water[years.index(2017)],
    text='<b>事業大轉折</b>', showarrow=True, arrowhead=2, ax=-50, ay=-60,
    bgcolor='#FFD54F', font=dict(size=14, color='#000'),
)
fig.add_annotation(
    x=2026, y=energy_fire[years.index(2026)],
    text='<b>2026 丙午印星偏旺</b>', showarrow=True, arrowhead=2, ax=50, ay=-50,
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
