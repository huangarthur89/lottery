import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
from lunar_python import Solar
from ziwei import build_ziwei_chart
import swisseph as swe
import math
import re

# ==========================================
# 0. 全域變數定義
# ==========================================
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

# ==========================================
# 1. 頁面與核心 CSS 設定
# ==========================================
st.set_page_config(page_title="大師級·萬象合參運算系統", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; color: #000000; }
    .ziwei-square-board {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        grid-template-rows: repeat(4, minmax(0, 1fr));
        width: min(100%, 1040px);
        aspect-ratio: 1 / 1;
        margin: 0 auto;
        background-color: #FFFFFF;
        border: 3px solid #000000;
        font-family: "MingLiU", "PMingLiU", "Noto Serif TC", serif;
        box-sizing: border-box;
    }
    .palace-cell {
        border: 1px solid #222222;
        position: relative;
        padding: 5px;
        box-sizing: border-box;
        overflow: hidden;
        background: #fff;
    }
    .center-hall {
        grid-column: 2 / 4;
        grid-row: 2 / 4;
        border: 2px solid #000000;
        position: relative;
        padding: 16px 18px;
        background-color: #FDFDFD;
        box-sizing: border-box;
        overflow: hidden;
    }
    .p-left-col {
        position: absolute; top: 5px; left: 6px; width: 48px;
        display: grid; grid-template-columns: repeat(2, 1fr); gap: 2px;
        font-size: 13px; line-height: 1.08; color: #222; font-weight: 700;
    }
    .vertical-note { writing-mode: vertical-rl; text-orientation: upright; min-height: 58px; white-space: nowrap; }
    .p-right-col {
        position: absolute; top: 5px; right: 6px; width: 82px;
        text-align: right; font-size: 13px; line-height: 1.12; color: #111; font-weight: 700;
    }
    .main-star { font-size: 20px; font-weight: 900; color: #111; letter-spacing: 0; line-height: 1.12; }
    .minor-star { color: #333; font-size: 12px; font-weight: 600; }
    .transform-line { color: #7B1FA2; font-size: 12px; font-weight: 800; margin-top: 2px; }
    .flow-year {
        position: absolute; left: 58px; top: 56px; color: #D32F2F;
        font-size: 17px; font-weight: 900; line-height: 1.25; text-align: center; white-space: nowrap;
    }
    .age-row {
        position: absolute; left: 24px; right: 26px; bottom: 41px;
        display: flex; justify-content: space-between; color: #222; font-size: 11px; line-height: 1;
    }
    .bottom-left { position: absolute; left: 8px; bottom: 6px; font-size: 12px; line-height: 1.15; color: #111; font-weight: 700; }
    .palace-name { color: #C62828; font-size: 15px; font-weight: 900; display: block; margin-top: 2px; }
    .bottom-right { position: absolute; right: 7px; bottom: 6px; font-size: 12px; line-height: 1.12; color: #111; text-align: right; font-weight: 800; }
    .gan-branch { font-size: 13px; font-weight: 900; }
    .center-lines { position: absolute; inset: 0; pointer-events: none; z-index: 1; }
    .center-text { position: relative; z-index: 2; font-size: 15px; line-height: 1.55; color: #000; }
    .center-title { color: #111; font-size: 16px; font-weight: 900; text-align: left; margin-bottom: 8px; letter-spacing: 0; }
    .center-grid { display: grid; grid-template-columns: 68px 1fr 58px 1fr; gap: 2px 8px; align-items: baseline; max-width: 360px; margin: 0 auto; }
    .center-label { font-weight: 900; text-align: right; }
    .center-value { font-weight: 700; }
    .center-brand { margin-top: 18px; margin-left: 34px; line-height: 1.25; font-weight: 800; }
    .small-blue { color: #1565C0; font-size: 13px; }
    .small-red { color: #C62828; font-weight: 900; }
    .astro-container { display: flex; justify-content: space-between; gap: 12px; margin-top: 25px; margin-bottom: 25px; max-width: 1040px; margin-left: auto; margin-right: auto;}
    .astro-card {
        flex: 1; border: 2px solid #000; padding: 15px; background-color: #FAFAFA;
        text-align: center; font-family: "MingLiU", "PMingLiU", "Noto Serif TC", serif;
        box-shadow: 3px 3px 0px #1A237E; border-radius: 2px;
    }
    .astro-title { font-size: 15px; color: #333; font-weight: bold; letter-spacing: 1px; border-bottom: 1px solid #CCC; padding-bottom: 5px; margin-bottom: 10px;}
    .astro-value { font-size: 26px; color: #000; font-weight: bold; letter-spacing: 0; }
    .astro-element { display: inline-block; margin-top: 10px; padding: 4px 10px; background-color: #000; color: #FFF; font-size: 13px; font-weight:bold; border-radius: 2px; }
    .blind-tag {
        display: inline-block; margin: 1px 4px 1px 0; padding: 1px 6px;
        background-color: #FBE9E7; color: #C62828; border: 1px solid #FFCCBC;
        border-radius: 2px; font-size: 13px; font-weight: 900; line-height: 1.35;
    }
    .fengshui-panel {
        max-width: 1040px; margin: 8px auto 28px auto; padding: 16px 18px 20px;
        border: 2px solid #111; background: #FFFFFF; font-family: "MingLiU", "PMingLiU", "Noto Serif TC", serif;
        box-shadow: 3px 3px 0 #111; box-sizing: border-box;
    }
    .fengshui-title { text-align: center; font-size: 24px; font-weight: 900; margin: 0 0 6px; color: #000; }
    .fengshui-subtitle { text-align: center; font-size: 14px; font-weight: 800; color: #555; margin-bottom: 12px; }
    .fengshui-grid {
        display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 6px;
        width: min(100%, 430px); aspect-ratio: 1 / 1; margin: 0 auto;
    }
    .fs-cell {
        position: relative; display: flex; flex-direction: column; align-items: center; justify-content: center;
        min-width: 0; border: 2px solid #333; background: #FAFAFA; box-shadow: 2px 2px 0 #111;
        overflow: hidden;
    }
    .fs-dir { position: absolute; top: 5px; left: 7px; font-size: 14px; font-weight: 900; color: #555; }
    .fs-star-num { font-size: 42px; line-height: 1; font-weight: 900; }
    .fs-star-name { margin-top: 4px; padding: 2px 8px; border-radius: 2px; color: #FFF; font-size: 15px; font-weight: 900; }
    .fs-desc { margin-top: 5px; font-size: 13px; color: #333; font-weight: 800; }
    .fs-luck { position: absolute; right: 6px; bottom: 5px; font-size: 12px; color: #111; font-weight: 900; }
    .c-1 { color: #1565C0; } .bg-1 { background-color: #1565C0; }
    .c-2 { color: #424242; } .bg-2 { background-color: #424242; }
    .c-3 { color: #2E7D32; } .bg-3 { background-color: #2E7D32; }
    .c-4 { color: #00897B; } .bg-4 { background-color: #00897B; }
    .c-5 { color: #C62828; } .bg-5 { background-color: #C62828; }
    .c-6 { color: #B28704; } .bg-6 { background-color: #B28704; }
    .c-7 { color: #E64A19; } .bg-7 { background-color: #E64A19; }
    .c-8 { color: #F57F17; } .bg-8 { background-color: #F57F17; color:#111; }
    .c-9 { color: #7B1FA2; } .bg-9 { background-color: #7B1FA2; }
    .fengshui-note { max-width: 760px; margin: 12px auto 0; font-size: 14px; line-height: 1.55; color: #333; font-weight: 700; text-align:center; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 演算法模組：真太陽時與均時差
# ==========================================
def calculate_true_solar_time(birth_date, clock_time, longitude, timezone_base=120.0):
    lon_diff_minutes = 4 * (longitude - timezone_base)
    n = birth_date.timetuple().tm_yday
    B = math.radians((360 / 365.24) * (n - 81))
    eot_minutes = 9.87 * math.sin(2 * B) - 7.53 * math.cos(B) - 1.5 * math.sin(B)
    total_offset = lon_diff_minutes + eot_minutes
    true_time = datetime.combine(birth_date, clock_time) + timedelta(minutes=total_offset)
    return true_time, total_offset, eot_minutes

# ==========================================
# 3. 瑞士星曆表 (Swiss Ephemeris)
# ==========================================
LIFE_PATH_MEANINGS = {
    1: {
        "title": "開創領導型",
        "keywords": "開創 / 領導 / 自主",
        "summary": "適合主導新計畫、建立方法與扛起關鍵決策；課題是把衝勁轉成可合作的節奏。",
    },
    2: {
        "title": "協調洞察型",
        "keywords": "協調 / 細節 / 關係",
        "summary": "擅長觀察情緒與細節，適合幕僚、顧問、服務與關係整合；課題是建立明確界線。",
    },
    3: {
        "title": "創意表達型",
        "keywords": "創意 / 表達 / 內容",
        "summary": "具備語言、影像、企劃與表演式輸出能力；課題是把靈感落成穩定作品。",
    },
    4: {
        "title": "秩序建構型",
        "keywords": "穩定 / 系統 / 執行",
        "summary": "重視規則、流程與可驗證成果，適合管理、工程、財務、研究與長期專案；課題是避免過度僵化。",
    },
    5: {
        "title": "自由探索型",
        "keywords": "自由 / 變化 / 體驗",
        "summary": "需要移動、學習與新刺激，適合跨域、旅行、行銷、媒體與彈性工作；課題是聚焦與承諾。",
    },
    6: {
        "title": "關懷療癒型",
        "keywords": "關懷 / 責任 / 美感",
        "summary": "適合照顧、教育、設計、家庭經營與社群支持；課題是不要把所有責任都攬到自己身上。",
    },
    7: {
        "title": "真理分析型",
        "keywords": "分析 / 研究 / 內省",
        "summary": "偏好深入鑽研、資料判讀與獨立思考，適合研究、技術、神秘學與專業顧問；課題是保持情感連結。",
    },
    8: {
        "title": "資源成就型",
        "keywords": "權力 / 成就 / 豐盛",
        "summary": "對資源配置、商業槓桿與成果規模敏感，適合經營、投資、管理與談判；課題是讓權力服務價值。",
    },
    9: {
        "title": "智慧大愛型",
        "keywords": "智慧 / 願景 / 服務",
        "summary": "具有人文關懷、整合視野與收束能力，適合教育、公益、藝術、諮詢與文化工作；課題是完成而非無限消耗。",
    },
}

MASTER_NUMBER_MEANINGS = {
    11: "高敏感直覺與啟發力，需要把靈感轉譯成清楚表達。",
    22: "大型建構與落地能力，需要把理想拆成可執行工程。",
    33: "服務、療癒與教育性的高責任頻率，需要先照顧自身界線。",
}


def reduce_number_with_steps(number, keep_master=False):
    steps = []
    current = number
    while current > 9:
        if keep_master and current in MASTER_NUMBER_MEANINGS:
            break
        digits = [int(ch) for ch in str(current)]
        next_value = sum(digits)
        steps.append(f"{'+'.join(str(d) for d in digits)}={next_value}")
        current = next_value
    return current, steps


def calculation_text(original, steps):
    if not steps:
        return str(original)
    return " -> ".join(steps)


def calculate_life_path_number(birth_date):
    month_value, month_steps = reduce_number_with_steps(birth_date.month, keep_master=True)
    day_value, day_steps = reduce_number_with_steps(birth_date.day, keep_master=True)
    year_value, year_steps = reduce_number_with_steps(birth_date.year, keep_master=True)

    component_total = month_value + day_value + year_value
    number, final_steps = reduce_number_with_steps(component_total, keep_master=False)

    direct_digits = [int(ch) for ch in birth_date.strftime("%Y%m%d")]
    direct_total = sum(direct_digits)
    direct_number, direct_steps = reduce_number_with_steps(direct_total, keep_master=False)

    master_candidates = [month_value, day_value, year_value, component_total, direct_total]
    master_candidates += [int(step.split('=')[-1]) for step in final_steps + direct_steps]
    master_number = next((part for part in master_candidates if part in MASTER_NUMBER_MEANINGS), None)

    meaning = LIFE_PATH_MEANINGS[number]
    standard_parts = [
        f"月={calculation_text(birth_date.month, month_steps)}",
        f"日={calculation_text(birth_date.day, day_steps)}",
        f"年={calculation_text(birth_date.year, year_steps)}",
        f"{month_value}+{day_value}+{year_value}={component_total}",
    ] + final_steps
    direct_parts = [f"{'+'.join(str(d) for d in direct_digits)}={direct_total}"] + direct_steps
    return {
        "number": number,
        "raw_total": component_total,
        "direct_number": direct_number,
        "direct_total": direct_total,
        "master_number": master_number,
        "master_note": MASTER_NUMBER_MEANINGS.get(master_number, ""),
        "title": meaning["title"],
        "keywords": meaning["keywords"],
        "summary": meaning["summary"],
        "calculation": " -> ".join(standard_parts),
        "direct_calculation": " -> ".join(direct_parts),
    }


FENGSHUI_STAR_INFO = {
    1: {"name": "一白", "desc": "桃花人緣", "luck": "吉", "advice": "利人脈、感情、學習與流動性資源。"},
    2: {"name": "二黑", "desc": "病符健康", "luck": "凶", "advice": "宜保持安靜清潔，減少動土與雜物堆積。"},
    3: {"name": "三碧", "desc": "是非口舌", "luck": "凶", "advice": "留意爭執、合約與溝通火氣。"},
    4: {"name": "四綠", "desc": "文昌學業", "luck": "平吉", "advice": "利讀書、考證、寫作與專業精進。"},
    5: {"name": "五黃", "desc": "災煞阻滯", "luck": "大凶", "advice": "忌動土、敲打、施工與高風險擾動。"},
    6: {"name": "六白", "desc": "權貴偏財", "luck": "吉", "advice": "利貴人、權責、管理與副業機會。"},
    7: {"name": "七赤", "desc": "破耗盜損", "luck": "凶", "advice": "留意破財、口舌、刀火與金屬傷害。"},
    8: {"name": "八白", "desc": "正財置產", "luck": "大吉", "advice": "利穩健財務、資產配置與長期成果。"},
    9: {"name": "九紫", "desc": "喜慶未來", "luck": "大吉", "advice": "利曝光、喜事、品牌與未來運勢啟動。"},
}

FLYING_STAR_SEQUENCE = ["中", "西北", "西", "東北", "南", "北", "西南", "東", "東南"]
FENGSHUI_GRID_POSITIONS = ["東南", "南", "西南", "東", "中", "西", "東北", "北", "西北"]


def digit_sum_until_single(number):
    current = sum(int(ch) for ch in str(number))
    steps = [current]
    while current > 9:
        current = sum(int(ch) for ch in str(current))
        steps.append(current)
    return current, steps


def calculate_annual_flying_stars(year):
    year_digit, digit_steps = digit_sum_until_single(year)
    center_star = 11 - year_digit
    while center_star <= 0:
        center_star += 9
    while center_star > 9:
        center_star -= 9

    offsets = {direction: index for index, direction in enumerate(FLYING_STAR_SEQUENCE)}
    stars = {}
    for direction in FENGSHUI_GRID_POSITIONS:
        star_num = ((center_star + offsets[direction] - 1) % 9) + 1
        stars[direction] = {"number": star_num, **FENGSHUI_STAR_INFO[star_num]}

    return {
        "year": year,
        "digit_steps": digit_steps,
        "center_star": center_star,
        "stars": stars,
    }


def render_flying_star_grid(chart):
    cells = []
    for direction in FENGSHUI_GRID_POSITIONS:
        info = chart["stars"][direction]
        star_num = info["number"]
        cells.append(f"""
        <div class="fs-cell">
            <div class="fs-dir">{direction}</div>
            <div class="fs-star-num c-{star_num}">{star_num}</div>
            <div class="fs-star-name bg-{star_num}">{info['name']}</div>
            <div class="fs-desc">{info['desc']}</div>
            <div class="fs-luck">{info['luck']}</div>
        </div>
        """)
    return "".join(cells)


def ganzhi_parts(pillar):
    return pillar[0], pillar[1]


def calculate_blind_bazi_extensions(year_pillar, month_pillar, day_pillar, hour_pillar):
    y_stem, y_branch = ganzhi_parts(year_pillar)
    m_stem, m_branch = ganzhi_parts(month_pillar)
    d_stem, d_branch = ganzhi_parts(day_pillar)
    h_stem, h_branch = ganzhi_parts(hour_pillar)

    tai_yuan = f"{STEMS[(STEMS.index(m_stem) + 1) % 10]}{BRANCHES[(BRANCHES.index(m_branch) + 3) % 12]}"

    palace_order = {"寅": 1, "卯": 2, "辰": 3, "巳": 4, "午": 5, "未": 6, "申": 7, "酉": 8, "戌": 9, "亥": 10, "子": 11, "丑": 12}
    palace_reverse = {value: key for key, value in palace_order.items()}
    branch_index = 14 - (palace_order[m_branch] + palace_order[h_branch])
    if branch_index <= 0:
        branch_index += 12
    ming_branch = palace_reverse[branch_index]

    tiger_start = {"甲": "丙", "己": "丙", "乙": "戊", "庚": "戊", "丙": "庚", "辛": "庚", "丁": "壬", "壬": "壬", "戊": "甲", "癸": "甲"}
    ming_stem = STEMS[(STEMS.index(tiger_start[y_stem]) + branch_index - 1) % 10]
    blind_ming = f"{ming_stem}{ming_branch}"

    branches = [y_branch, m_branch, d_branch, h_branch]
    shensha = []

    def add_if(name, target_branches):
        targets = [branch for branch in target_branches if branch]
        if any(branch in targets for branch in branches) and name not in shensha:
            shensha.append(name)

    tianyi_map = {"甲": ["丑", "未"], "戊": ["丑", "未"], "庚": ["丑", "未"], "乙": ["子", "申"], "己": ["子", "申"], "丙": ["亥", "酉"], "丁": ["亥", "酉"], "辛": ["寅", "午"], "壬": ["卯", "巳"], "癸": ["卯", "巳"]}
    wenchang_map = {"甲": ["巳"], "乙": ["午"], "丙": ["申"], "戊": ["申"], "丁": ["酉"], "己": ["酉"], "庚": ["亥"], "辛": ["子"], "壬": ["寅"], "癸": ["卯"]}
    yangren_map = {"甲": ["卯"], "丙": ["午"], "戊": ["午"], "庚": ["酉"], "壬": ["子"]}
    peach_map = {"申": "酉", "子": "酉", "辰": "酉", "寅": "卯", "午": "卯", "戌": "卯", "亥": "子", "卯": "子", "未": "子", "巳": "午", "酉": "午", "丑": "午"}
    horse_map = {"申": "寅", "子": "寅", "辰": "寅", "寅": "申", "午": "申", "戌": "申", "亥": "巳", "卯": "巳", "未": "巳", "巳": "亥", "酉": "亥", "丑": "亥"}
    huagai_map = {"申": "辰", "子": "辰", "辰": "辰", "寅": "戌", "午": "戌", "戌": "戌", "亥": "未", "卯": "未", "未": "未", "巳": "丑", "酉": "丑", "丑": "丑"}

    add_if("天乙貴人", tianyi_map.get(d_stem, []))
    add_if("文昌貴人", wenchang_map.get(d_stem, []))
    add_if("羊刃", yangren_map.get(d_stem, []))
    add_if("桃花", [peach_map.get(y_branch), peach_map.get(d_branch)])
    add_if("驛馬", [horse_map.get(y_branch), horse_map.get(d_branch)])
    add_if("華蓋", [huagai_map.get(y_branch), huagai_map.get(d_branch)])

    return {
        "tai_yuan": tai_yuan,
        "ming_gong": blind_ming,
        "shensha": shensha,
        "pillars": {"year": year_pillar, "month": month_pillar, "day": day_pillar, "hour": hour_pillar},
    }


def calculate_nasa_astrology(birth_date, clock_time, longitude, latitude, timezone_base=120.0):
    utc_offset_hours = timezone_base / 15.0
    local_dt = datetime.combine(birth_date, clock_time)
    utc_dt = local_dt - timedelta(hours=utc_offset_hours)
    ut_hour_dec = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
    
    jd_ut = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, ut_hour_dec)
    sun_pos = swe.calc_ut(jd_ut, swe.SUN)[0][0]
    moon_pos = swe.calc_ut(jd_ut, swe.MOON)[0][0]
    cusps, ascmc = swe.houses(jd_ut, latitude, longitude, b'P')
    asc_pos = ascmc[0]
    
    zodiac_signs = ["白羊座", "金牛座", "雙子座", "巨蟹座", "獅子座", "處女座", 
                    "天秤座", "天蠍座", "射手座", "摩羯座", "水瓶座", "雙魚座"]
    elements = ["火象", "土象", "風象", "水象"]
    
    def get_info(degree):
        idx = int(degree // 30)
        return zodiac_signs[idx], elements[idx % 4], degree
        
    sun_sign, sun_elem, sun_deg = get_info(sun_pos)
    moon_sign, moon_elem, moon_deg = get_info(moon_pos)
    asc_sign, asc_elem, asc_deg = get_info(asc_pos)
    
    return {
        "sun": sun_sign, "sun_element": sun_elem, "sun_deg": sun_deg,
        "moon": moon_sign, "moon_element": moon_elem, "moon_deg": moon_deg,
        "asc": asc_sign, "asc_element": asc_elem, "asc_deg": asc_deg,
        "jd": jd_ut
    }

# ==========================================
# 4. 側邊欄：參數輸入
# ==========================================
with st.sidebar:
    st.markdown("### 🔮 天體與大師校正面板")
    name = st.text_input("命主", "匿名")
    gender = st.radio("性別", ["乾造 (男)", "坤造 (女)"])
    gender_int = 1 if "男" in gender else 0
    
    b_date = st.date_input("公曆出生日", datetime(1971, 9, 30))
    b_time = st.time_input("公曆出生時", datetime(1971, 9, 30, 4, 0).time())
    
    st.markdown("---")
    st.markdown("#### 🧭 地理經緯度與天文校正")
    longitude = st.number_input("出生地經度 (東經為正)", value=121.74, step=0.01, format="%.2f")
    latitude = st.number_input("出生地緯度 (上升關鍵)", value=25.03, step=0.01, format="%.2f")
    
    true_datetime, total_offset, eot = calculate_true_solar_time(b_date, b_time, longitude)
    st.info(f"經度差: {total_offset-eot:.1f} 分\n\n均時差: {eot:.1f} 分\n\n**真太陽時:**\n{true_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    
    st.markdown("---")
    st.markdown("#### ⚙️ 流派排盤精密設定")
    leap_month_rule = st.selectbox("紫微閏月排法", ["以十五日為界切分", "一律作下半月", "維持本月"])
    zi_hour_rule = st.selectbox("子時換日排法", ["早晚子時區分 (23:00不換日)", "一律換日 (23:00算隔天)"])

# ==========================================
# 5. 生成紫微斗數與西方占星資料
# ==========================================
lunar = Solar.fromYmdHms(true_datetime.year, true_datetime.month, true_datetime.day, true_datetime.hour, true_datetime.minute, 0).getLunar()
eight_char = lunar.getEightChar()
eight_char.setSect(1 if zi_hour_rule.startswith("一律換日") else 2)
yun = eight_char.getYun(gender_int)

jiaoyun_date = yun.getStartSolar()
jiaoyun_text = f"出生後 {yun.getStartYear()} 年 {yun.getStartMonth()} 月交運"

ziwei_chart = build_ziwei_chart(true_datetime.year, true_datetime.month, true_datetime.day, true_datetime.hour, true_datetime.minute, gender)
ziwei_palaces = ziwei_chart["palaces"]
dynamic_palaces = {branch: palace["宮位"] for branch, palace in ziwei_palaces.items()}
astro_data = calculate_nasa_astrology(b_date, b_time, longitude, latitude)
life_path = calculate_life_path_number(b_date)
life_path_master_line = f"大師數底頻 {life_path['master_number']}：{life_path['master_note']}" if life_path["master_number"] else "生日數字化約至 1-9 主頻率"
blind_bazi = calculate_blind_bazi_extensions(eight_char.getYear(), eight_char.getMonth(), eight_char.getDay(), eight_char.getTime())
shensha_tags_html = "".join(f"<span class='blind-tag'>{tag}</span>" for tag in blind_bazi["shensha"]) or "<span class='blind-tag'>六神煞未明顯引動</span>"

# ==========================================
# 6. 動態生成「三方四正」飛線 SVG
# ==========================================
def get_dynamic_san_fang_si_zheng_svg(ming_branch):
    """根據命主真實的命宮位置，動態運算三方四正的幾何座標點"""
    anchors = {
        "巳": (0, 0),   "午": (25, 0),  "未": (75, 0),  "申": (100, 0),
        "辰": (0, 25),                                  "酉": (100, 25),
        "卯": (0, 75),                                  "戌": (100, 75),
        "寅": (0, 100), "丑": (25, 100),"子": (75, 100),"亥": (100, 100)
    }
    
    ming_idx = BRANCHES.index(ming_branch)
    trine1 = BRANCHES[(ming_idx + 4) % 12]
    opposite = BRANCHES[(ming_idx + 6) % 12]
    trine2 = BRANCHES[(ming_idx + 8) % 12]
    
    p0 = anchors[ming_branch]
    p1 = anchors[trine1]
    p2 = anchors[opposite]
    p3 = anchors[trine2]
    
    return f"""
    <svg class="center-lines" viewBox="0 0 100 100" preserveAspectRatio="none">
        <line x1="{p0[0]}" y1="{p0[1]}" x2="{p1[0]}" y2="{p1[1]}" stroke="#D32F2F" stroke-width="0.6" />
        <line x1="{p0[0]}" y1="{p0[1]}" x2="{p2[0]}" y2="{p2[1]}" stroke="#D32F2F" stroke-width="0.6" />
        <line x1="{p0[0]}" y1="{p0[1]}" x2="{p3[0]}" y2="{p3[1]}" stroke="#D32F2F" stroke-width="0.6" />
        <line x1="{p1[0]}" y1="{p1[1]}" x2="{p2[0]}" y2="{p2[1]}" stroke="#D32F2F" stroke-width="0.4" stroke-dasharray="2,2" />
        <line x1="{p3[0]}" y1="{p3[1]}" x2="{p2[0]}" y2="{p2[1]}" stroke="#D32F2F" stroke-width="0.4" stroke-dasharray="2,2" />
    </svg>
    """

# ==========================================
# 7. 主排盤介面繪製
# ==========================================
def split_words(text, fallback=""):
    words = [w for w in str(text or "").split() if w]
    return words if words else ([fallback] if fallback else [])

def vertical_pair_html(items, limit=4):
    picked = (items + ["", "", "", ""])[:limit]
    return "".join(f"<span class='vertical-note'>{item}</span>" for item in picked if item)

def age_sequence_text(da_xian):
    try: start = int(str(da_xian).split("-")[0])
    except (TypeError, ValueError): start = 1
    return "".join(f"<span>{start + i * 12}</span>" for i in range(8))

def flow_year_branch(year):
    lunar_year = Solar.fromYmd(year, 6, 1).getLunar()
    return lunar_year.getYearZhi(), lunar_year.getYearInGanZhi()

current_year = datetime.now().year
current_flow_branch, current_flow_ganzhi = flow_year_branch(current_year)
flying_star_chart = calculate_annual_flying_stars(current_year)
flying_star_cells_html = render_flying_star_grid(flying_star_chart)
center_star_info = FENGSHUI_STAR_INFO[flying_star_chart["center_star"]]

def render_cell(branch_name, p_name):
    palace = ziwei_palaces[branch_name]
    main_stars = palace.get("主星") or "--"
    lucky = split_words(palace.get("吉煞"))
    minor = split_words(palace.get("副星"))
    transforms = split_words(palace.get("四化文字"))
    left_items = [palace.get("博士", ""), palace.get("長生", ""), palace.get("歲建", "")] + minor[:3]
    right_minor = "<br>".join(lucky[:4] + minor[3:6])
    transform_line = "<br>".join(transforms)
    liunian_html = f"<div class='flow-year'>{current_year}年<br>{current_flow_ganzhi}年<br>流年命宮</div>" if branch_name == current_flow_branch else ""
    
    return f"""
    <div class="palace-cell">
        <div class="p-left-col">{vertical_pair_html(left_items, 6)}</div>
        <div class="p-right-col">
            <div class="main-star">{main_stars.replace(' ', '<br>')}</div>
            <div class="minor-star">{right_minor}</div>
            <div class="transform-line">{transform_line}</div>
        </div>
        {liunian_html}
        <div class="age-row">{age_sequence_text(palace.get('大限'))}</div>
        <div class="bottom-left">
            {palace.get('大限', '')}<br>
            <span class="palace-name">【{p_name}】</span>
        </div>
        <div class="bottom-right">
            <span class="gan-branch">{palace.get('宮干', '')}</span><br>
            {branch_name}<br>{ziwei_chart.get('nature', '')}
        </div>
    </div>
    """

dynamic_svg_lines = get_dynamic_san_fang_si_zheng_svg(ziwei_chart['ming_branch'])

html_content = f"""
<div class="ziwei-square-board">
    {render_cell("巳", dynamic_palaces["巳"])}
    {render_cell("午", dynamic_palaces["午"])}
    {render_cell("未", dynamic_palaces["未"])}
    {render_cell("申", dynamic_palaces["申"])}
    {render_cell("辰", dynamic_palaces["辰"])}
    
    <div class="center-hall">
        {dynamic_svg_lines} <div class="center-text">
            <div class="center-grid">
                <div class="center-label">姓名：</div><div class="center-value">{name}</div>
                <div class="center-label">現在歲：</div><div class="center-value">{max(0, current_year - b_date.year)}</div>
                <div class="center-label">命造：</div><div class="center-value">{gender}</div>
                <div class="center-label">生肖：</div><div class="center-value">{lunar.getYearShengXiao()}</div>
                <div class="center-label">陽曆：</div><div class="center-value" style="grid-column: span 3;">{b_date.strftime('%Y年%m月%d日')} {b_time.strftime('%H時%M分')}</div>
                <div class="center-label">真時：</div><div class="center-value" style="grid-column: span 3; color:#1565C0;">{true_datetime.strftime('%Y年%m月%d日 %H時%M分')}</div>
                <div class="center-label">農曆：</div><div class="center-value" style="grid-column: span 3;">{ziwei_chart['lunar_txt']} {ziwei_chart['lunar_hour']}時</div>
                <div class="center-label">節氣四柱：</div><div class="center-value" style="grid-column: span 3;">{eight_char.getYear()}年 {eight_char.getMonth()}月 {eight_char.getDay()}日 {eight_char.getTime()}時</div>
                <div class="center-label">命局：</div><div class="center-value">{ziwei_chart['nature']}</div>
                <div class="center-label">命宮：</div><div class="center-value">{ziwei_chart['ming_branch']}</div>
                <div class="center-label">身宮：</div><div class="center-value">{ziwei_chart['body_branch']}</div>
                <div class="center-label">交運：</div><div class="center-value" style="grid-column: span 3;">{jiaoyun_text}</div>
                <div class="center-label">靈數：</div><div class="center-value" style="grid-column: span 3; color:#6A1B9A;">生命靈數 {life_path['number']}，{life_path['title']}</div>
                <div class="center-label">盲派：</div><div class="center-value" style="grid-column: span 3; color:#C62828;">胎元 {blind_bazi['tai_yuan']}，命宮 {blind_bazi['ming_gong']}</div>
                <div class="center-label">神煞：</div><div class="center-value" style="grid-column: span 3;">{shensha_tags_html}</div>
                <div class="center-label">年干四化：</div><div class="center-value" style="grid-column: span 3; color:#7B1FA2;">{', '.join(ziwei_chart['palaces'][b].get('四化文字', '') for b in BRANCHES if ziwei_chart['palaces'][b].get('四化文字', ''))}</div>
                <div class="center-label">流年：</div><div class="center-value" style="grid-column: span 3;"><span class="small-red">{current_year}年 {current_flow_ganzhi}年</span>，流年命宮落 {current_flow_branch} 宮</div>
            </div>
            <div class="center-brand">
                STAR★START<br>
                <span>從星開始 紫微研究苑</span><br>
                <span class="small-blue">108s.tw</span><br>
                <span class="small-blue">{ziwei_chart['algorithm_note']}</span>
            </div>
        </div>
    </div>
    
    {render_cell("酉", dynamic_palaces["酉"])}
    {render_cell("卯", dynamic_palaces["卯"])}
    {render_cell("戌", dynamic_palaces["戌"])}
    {render_cell("寅", dynamic_palaces["寅"])}
    {render_cell("丑", dynamic_palaces["丑"])}
    {render_cell("子", dynamic_palaces["子"])}
    {render_cell("亥", dynamic_palaces["亥"])}
</div>

<div class="astro-container">
    <div class="astro-card">
        <div class="astro-title">☀️ 太陽 (外在意志)</div>
        <div class="astro-value">{astro_data['sun']}</div>
        <div class="astro-element" style="background-color: #B71C1C;">{astro_data['sun_element']}特質</div>
        <div style="font-size:12px; color:#666; margin-top:5px;">黃經 {astro_data['sun_deg']:.2f}°</div>
    </div>
    <div class="astro-card">
        <div class="astro-title">🌙 月亮 (潛意識)</div>
        <div class="astro-value">{astro_data['moon']}</div>
        <div class="astro-element" style="background-color: #0D47A1;">內在情緒與安全感</div>
        <div style="font-size:12px; color:#666; margin-top:5px;">黃經 {astro_data['moon_deg']:.2f}°</div>
    </div>
    <div class="astro-card">
        <div class="astro-title">✨ 上升 (社會人格)</div>
        <div class="astro-value">{astro_data['asc']}</div>
        <div class="astro-element" style="background-color: #FBC02D; color:#000;">面具與命運舵手</div>
        <div style="font-size:12px; color:#666; margin-top:5px;">黃經 {astro_data['asc_deg']:.2f}°</div>
    </div>
    <div class="astro-card">
        <div class="astro-title">生命靈數 (靈魂天賦)</div>
        <div class="astro-value" style="color:#6A1B9A;">{life_path['number']}</div>
        <div class="astro-element" style="background-color: #6A1B9A;">{life_path['title']}</div>
        <div style="font-size:12px; color:#666; margin-top:5px;">{life_path['keywords']}</div>
    </div>
</div>

<div class="fengshui-panel">
    <div class="fengshui-title">{current_year} 流年九宮飛星羅盤</div>
    <div class="fengshui-subtitle">入中主星：{flying_star_chart['center_star']} {center_star_info['name']}，{center_star_info['desc']}；飛佈順序：中 → 西北 → 西 → 東北 → 南 → 北 → 西南 → 東 → 東南</div>
    <div class="fengshui-grid">{flying_star_cells_html}</div>
    <div class="fengshui-note">玄空流年飛星用於年度方位提示；實務判讀仍需合併住宅坐向、元運、室內格局與是否動土，不建議只憑單一年星做絕對吉凶判斷。</div>
</div>
"""
clean_html = re.sub(r'\n\s*', '', html_content)
st.markdown(clean_html, unsafe_allow_html=True)


# ==========================================
# 8. 五行能量圖表 (動態懸浮註解與追蹤線)
# ==========================================
st.markdown("<br><h2 style='color:#000; font-family:serif; text-align:center; font-weight:bold; font-size:26px;'>流年五行能量真實起伏軌跡 (1990 - 2040)</h2>", unsafe_allow_html=True)

FIRE_ELEMENTS = {"丙": 30, "丁": 30, "巳": 40, "午": 40, "寅": 15, "戌": 10}
WATER_ELEMENTS = {"壬": 30, "癸": 30, "亥": 40, "子": 40, "申": 15, "丑": 10}


def get_real_energy(target_year):
    # 以年中採樣點取得該年干支，讓每一年的能量提示保持一致。
    lunar_target = Solar.fromYmd(target_year, 6, 1).getLunar()
    year_ganzhi = lunar_target.getYearInGanZhi()
    score_fire = FIRE_ELEMENTS.get(year_ganzhi[0], 0) + FIRE_ELEMENTS.get(year_ganzhi[1], 0)
    score_water = WATER_ELEMENTS.get(year_ganzhi[0], 0) + WATER_ELEMENTS.get(year_ganzhi[1], 0)
    return 30 + score_fire + 15 * math.sin(target_year), 30 + score_water + 15 * math.cos(target_year)


def fire_diagnosis(value):
    if value > 70:
        return "<b>【偏旺】</b>知識吸收、系統建置與研究考證能量較強，適合整理方法論、推進技術型專案。"
    if value > 45:
        return "<b>【平穩】</b>思路較清楚，適合穩紮穩打累積專業實力，避免急於求成。"
    return "<b>【需留意】</b>容易感到耗力或判斷分散，重要決策宜放慢節奏並保留驗證流程。"


def water_diagnosis(value):
    if value > 70:
        return "<b>【偏旺】</b>表達、創作、技術輸出與變現動能較明顯，利於影像、文字、展示或作品發表。"
    if value > 45:
        return "<b>【平穩】</b>適合按部就班產出，精細工藝、專業技能與溝通表達可穩定發揮。"
    return "<b>【需留意】</b>靈感與輸出節奏可能較保守，應避免衝動投資或一次擴大過多專案。"


years = list(range(1990, 2041))
energy_fire = []
energy_water = []
hover_fire = []
hover_water = []

for target_year in years:
    fire_value, water_value = get_real_energy(target_year)
    energy_fire.append(fire_value)
    energy_water.append(water_value)

    year_ganzhi = Solar.fromYmd(target_year, 6, 1).getLunar().getYearInGanZhi()
    header = f"<b>{target_year}年 ({year_ganzhi}年)</b><br><br>"

    hover_fire.append(
        header
        + f"<b>火土印星：{fire_value:.1f}</b><br>"
        + fire_diagnosis(fire_value)
    )
    hover_water.append(
        header
        + f"<b>金水食傷：{water_value:.1f}</b><br>"
        + water_diagnosis(water_value)
    )

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=years,
    y=energy_water,
    mode='lines',
    name='金水能量 (食傷生財)',
    line=dict(color='#0D47A1', width=4, shape='spline'),
    hoverinfo='text',
    hovertext=hover_water,
    hovertemplate='%{hovertext}<extra></extra>',
))

fig.add_trace(go.Scatter(
    x=years,
    y=energy_fire,
    mode='lines+markers',
    name='火土能量 (印星護身)',
    line=dict(color='#B71C1C', width=3, dash='dot', shape='spline'),
    hoverinfo='text',
    hovertext=hover_fire,
    hovertemplate='%{hovertext}<extra></extra>',
))

fig.add_annotation(
    x=2017,
    y=energy_water[years.index(2017)],
    text='<b>事業大轉折</b>',
    showarrow=True,
    arrowhead=2,
    ax=-50,
    ay=-60,
    bgcolor='#FFD54F',
    font=dict(size=14, color='#000'),
)
fig.add_annotation(
    x=2026,
    y=energy_fire[years.index(2026)],
    text='<b>2026 丙午印星偏旺</b>',
    showarrow=True,
    arrowhead=2,
    ax=50,
    ay=-50,
    bgcolor='#FFCDD2',
    font=dict(size=14, color='#000'),
)

fig.update_layout(
    plot_bgcolor='#FFFFFF',
    paper_bgcolor='#FFFFFF',
    hoverlabel=dict(
        bgcolor='rgba(255, 255, 255, 0.96)',
        font_size=13,
        font_family='Noto Serif TC, PMingLiU, serif',
        bordercolor='#333333',
    ),
    hovermode='x unified',
    xaxis=dict(
        title=dict(text='<b>西元年份</b>', font=dict(size=16, color='#000')),
        tickfont=dict(size=14, color='#000'),
        showgrid=True,
        gridcolor='#DDD',
        showspikes=True,
        spikemode='across',
        spikethickness=1,
        spikedash='solid',
        spikecolor='#666666',
    ),
    yaxis=dict(
        title=dict(text='<b>能量指數</b>', font=dict(size=16, color='#000')),
        tickfont=dict(size=14, color='#000'),
        showgrid=True,
        gridcolor='#DDD',
    ),
    legend=dict(
        orientation='h',
        yanchor='top',
        y=-0.15,
        xanchor='center',
        x=0.5,
        font=dict(size=16, color='#000', family='Arial, sans-serif'),
    ),
    margin=dict(l=50, r=50, t=50, b=80),
)

st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# ==========================================
# 9. 現代語意深度解析引擎
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

PALACE_CONTEXTS = {
    "命宮": "人格核心與做事風格",
    "官祿": "職涯方向與工作方法",
    "財帛": "收入模式與資源管理",
    "遷移": "外在世界、旅行移動、跨域合作與社會舞台",
    "子女": "子女互動、創作成果、學生晚輩與作品延伸",
    "夫妻": "伴侶關係、合作默契與親密互動",
    "父母": "長輩、制度資源、原生支持與上位協助",
    "福德": "興趣潛能、精神能量、休閒恢復與內在滿足",
}


def normalize_palace_name(name):
    return str(name or "").replace("【身】", "")


def find_palace(keyword):
    for branch, palace in ziwei_palaces.items():
        if keyword in normalize_palace_name(palace.get("宮位", "")):
            return branch, palace
    return "", {}


def words(text):
    return [item for item in str(text or "").split() if item]


def star_phrase(star):
    return STAR_MEANINGS.get(star, "保留傳統星曜象意，需搭配宮位與四化細看")


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
        "branch": branch,
        "palace": palace,
        "name": normalize_palace_name(palace.get("宮位", keyword)) if palace else keyword,
        "stars": main_stars,
        "transforms": transforms,
        "support": support_text,
        "star_text": star_text,
        "transform_text": transform_text,
    }


def describe_star_set(snapshot, fallback_focus):
    if not snapshot["stars"]:
        return f"此宮沒有十四主星坐守，判讀上更重視對宮、三方四正與輔星，現代語意上可視為以環境條件塑造{fallback_focus}。"
    phrases = [f"{star}代表{star_phrase(star)}" for star in snapshot["stars"]]
    return "；".join(phrases) + "。"


def describe_transforms(snapshot):
    if not snapshot["transforms"]:
        return "此宮沒有生年四化直接落入，表示事件推動較不靠單一強烈觸發點，適合用長期節奏與外部條件慢慢累積。"
    parts = []
    for item in snapshot["transforms"]:
        matched = next((key for key in TRANSFORM_MEANINGS if item.endswith(key)), "")
        if matched:
            parts.append(f"{item}{TRANSFORM_MEANINGS[matched]}")
        else:
            parts.append(item)
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

    paragraphs = []
    paragraphs.append(
        f"<p><b>【職涯規劃與工作定位】</b> 官祿宮落在 <span style='color:#1565C0;font-weight:bold;'>{career['branch']}宮</span>，主星為 <span style='color:#C62828;font-weight:bold;'>{career['star_text']}</span>，四化訊號為 <span style='color:#7B1FA2;font-weight:bold;'>{career['transform_text']}</span>。{career_focus}{career_transform} 以現代職涯語言來看，這代表適合把工作拆成「可被設計、可被驗證、可被交付」的流程；若再參照財帛宮（{wealth['branch']}宮，{wealth['star_text']}），{wealth_focus} 因此職涯上可優先考慮系統規劃、技術工具、內容製作、顧問服務、營運管理或需要長期作品累積的專業路線。</p>"
    )
    paragraphs.append(
        f"<p><b>【人格優勢與興趣潛能】</b> 命宮位於 <span style='color:#1565C0;font-weight:bold;'>{ming['branch']}宮</span>，主星為 <span style='color:#C62828;font-weight:bold;'>{ming['star_text']}</span>。{ming_focus} 福德宮位於 {spirit['branch']}宮，主星為 {spirit['star_text']}，{spirit_focus} 這組訊號適合轉化為可長期投入的興趣：例如影像、模型、設計、資料整理、語言研究、工具自動化、策展式旅行或任何需要反覆打磨細節的專案。這不是單純娛樂，而是讓命盤能量恢復、沉澱並形成作品的方法。</p>"
    )
    paragraphs.append(
        f"<p><b>【外在世界與遷移發展】</b> 遷移宮位於 <span style='color:#1565C0;font-weight:bold;'>{travel['branch']}宮</span>，主星為 <span style='color:#C62828;font-weight:bold;'>{travel['star_text']}</span>，四化為 {travel['transform_text']}。{travel_focus}{travel_transform} 現代語意上，遷移宮不只代表旅行，也代表跨城市、跨國、跨領域、跨社群的互動方式。當遷移宮被主星或四化引動時，適合透過外出觀察、國際資訊、遠距合作、展覽參訪、攝影記錄或不同文化場景來擴大視野；若身宮落在遷移或與遷移三方有連動，外在世界更容易成為人生後半段的重要養分。</p>"
    )
    paragraphs.append(
        f"<p><b>【家庭關係與互動模式】</b> 子女宮位於 <span style='color:#1565C0;font-weight:bold;'>{children['branch']}宮</span>，主星為 <span style='color:#C62828;font-weight:bold;'>{children['star_text']}</span>，四化為 {children['transform_text']}。{children_focus}{children_transform} 在現代解讀中，子女宮也可延伸為作品、學生、晚輩與創作成果，因此它描述的是「如何陪伴下一代，也如何讓自己的成果被延伸」。夫妻宮位於 {spouse['branch']}宮，{spouse_focus} 父母宮位於 {parents['branch']}宮，{parents_focus} 家庭議題建議以溝通節奏、資源分配與界線感來經營，避免把命盤訊號解讀成絕對事件。</p>"
    )
    paragraphs.append(
        f"<p><b>【三軌合參：八字 × 紫微 × 生命靈數】</b> 生命靈數以公曆生日的月、日、年分段化約，{b_date.strftime('%Y-%m-%d')} 的標準三段式為 <span style='color:#6A1B9A;font-weight:bold;'>{life_path['calculation']}</span>；直加驗算為 <span style='color:#6A1B9A;font-weight:bold;'>{life_path['direct_calculation']}</span>。主頻率為 <span style='color:#6A1B9A;font-weight:bold;'>生命靈數 {life_path['number']}（{life_path['title']}）</span>。其現代語意為「{life_path['keywords']}」：{life_path['summary']} 若與東方八字日主「{eight_char.getDay()[0]}」、紫微命宮 {ming['branch']}宮（{ming['star_text']}）一起參照，可把先天氣質拆成三層：八字看能量結構，紫微看人生場域與事件位置，靈數則補充個人動機、表達方式與長期課題。{life_path_master_line}</p>"
    )
    paragraphs.append(
        f"<p><b>【盲派六柱與本命神煞】</b> 本系統以節氣四柱為基準，月柱順推得到胎元 <span style='color:#C62828;font-weight:bold;'>{blind_bazi['tai_yuan']}</span>，再以月支、時支序數定命宮地支，並用五虎遁推得盲派命宮 <span style='color:#C62828;font-weight:bold;'>{blind_bazi['ming_gong']}</span>。本命六神煞檢出為 <span style='color:#C62828;font-weight:bold;'>{'、'.join(blind_bazi['shensha']) if blind_bazi['shensha'] else '未明顯引動'}</span>。神煞適合做性格傾向與事件提醒，不宜孤立斷事；它的價值在於指出命盤中比較容易被環境觸發的題目，例如貴人、文書、移動、創作、孤高研究或口舌壓力。</p>"
    )
    paragraphs.append(
        f"<p><b>【玄空流年九宮飛星】</b> {current_year} 年以數字和化約後代入 11 減年數法，推得 <span style='color:#1565C0;font-weight:bold;'>{flying_star_chart['center_star']} {center_star_info['name']}</span> 入中宮。年度方位重點為：南方見五黃需避免動土擾動；東方見八白可作穩健財務與成果累積位；東南見九紫利喜慶、曝光與品牌；北方六白利貴人與副業。此盤屬流年層，仍需與住宅坐向、元運、實際格局合看。</p>"
    )
    paragraphs.append(
        f"<p><b>【Swiss Ephemeris 星曆校正說明】</b> 本系統底層採用 <code>pyswisseph</code> 與 Swiss Ephemeris 計算天文資料，真太陽時為 <span style='color:#C62828;font-weight:bold;'>{true_datetime.strftime('%H:%M:%S')}</span>。東方八字日主為「{eight_char.getDay()[0]}」；西方占星顯示太陽 <span style='color:#1565C0;font-weight:bold;'>{astro_data['sun']}</span>、月亮 <span style='color:#1565C0;font-weight:bold;'>{astro_data['moon']}</span>、上升 <span style='color:#C62828;font-weight:bold;'>{astro_data['asc']}</span>。這些資訊用來輔助理解人格與外在表現，不做絕對斷言；真正有價值的是把命盤傾向轉化成可行的職涯安排、家庭溝通與生活選擇。</p>"
    )
    return "\n".join(paragraphs)


modern_report_html = build_modern_report()
st.markdown(f"""
<div style="border: 3px solid #000000; background-color: #FAFAFA; padding: 25px; border-radius: 4px; font-family: 'PMingLiU', serif; color:#000;">
    <h3 style="color: #000; margin-top:0; border-bottom:2px solid #000; padding-bottom:12px; font-weight:bold; font-size:22px;">現代語意·萬象合參深度命理剖析</h3>
    <div style="font-size: 17px; line-height: 2.0; color: #111; font-weight: 500;">
        {modern_report_html}
    </div>
</div>
""", unsafe_allow_html=True)
