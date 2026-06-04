import streamlit as st
import time
from datetime import datetime
import pytz
from lunar_python import Lunar
from saju import calculate_saju
from ziwei import build_ziwei_chart

# ==========================================
# 1. 命理核心資料庫
# ==========================================

TEN_STEMS = {
    '甲': ('木', True),  '乙': ('木', False),
    '丙': ('火', True),  '丁': ('火', False),
    '戊': ('土', True),  '己': ('土', False),
    '庚': ('金', True),  '辛': ('金', False),
    '壬': ('水', True),  '癸': ('水', False)
}

ELEMENT_RELATION = {
    ('木', '木'): 'BI',    ('木', '火'): 'SHANG', ('木', '土'): 'CAI',   ('木', '金'): 'GUAN',  ('木', '水'): 'YIN',
    ('火', '木'): 'YIN',   ('火', '火'): 'BI',    ('火', '土'): 'SHANG', ('火', '金'): 'CAI',   ('火', '水'): 'GUAN',
    ('土', '木'): 'GUAN',  ('土', '火'): 'YIN',   ('土', '土'): 'BI',    ('土', '金'): 'SHANG', ('土', '水'): 'CAI',
    ('金', '木'): 'CAI',   ('金', '火'): 'GUAN',  ('金', '土'): 'YIN',   ('金', '金'): 'BI',    ('金', '水'): 'SHANG',
    ('水', '木'): 'SHANG', ('水', '火'): 'CAI',   ('水', '土'): 'GUAN',  ('水', '金'): 'YIN',   ('水', '水'): 'BI'
}

TEN_GODS_MATRIX = {
    ('BI', True): '比肩',    ('BI', False): '劫財',
    ('YIN', True): '偏印',   ('YIN', False): '正印',
    ('SHANG', True): '食神', ('SHANG', False): '傷官',
    ('GUAN', True): '七殺',  ('GUAN', False): '正官',
    ('CAI', True): '偏財',   ('CAI', False): '正財'
}

HIDDEN_STEMS_DATA = {
    "子": {"main": "癸", "sub_1": None, "sub_2": None},
    "丑": {"main": "己", "sub_1": "癸", "sub_2": "辛"},
    "寅": {"main": "甲", "sub_1": "丙", "sub_2": "戊"},
    "卯": {"main": "乙", "sub_1": None, "sub_2": None},
    "辰": {"main": "戊", "sub_1": "乙", "sub_2": "癸"},
    "巳": {"main": "丙", "sub_1": "庚", "sub_2": "戊"},
    "午": {"main": "丁", "sub_1": "己", "sub_2": None},
    "未": {"main": "己", "sub_1": "丁", "sub_2": "乙"},
    "申": {"main": "庚", "sub_1": "壬", "sub_2": "戊"},
    "酉": {"main": "辛", "sub_1": None, "sub_2": None},
    "戌": {"main": "戊", "sub_1": "辛", "sub_2": "丁"},
    "亥": {"main": "壬", "sub_1": "甲", "sub_2": None}
}

SEXAGENARY_CYCLE = [
    "甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉",
    "甲戌", "乙亥", "丙子", "丁丑", "戊寅", "己卯", "庚辰", "辛巳", "壬午", "癸未",
    "甲申", "乙酉", "丙戌", "丁亥", "戊子", "己丑", "庚寅", "辛卯", "壬辰", "癸巳",
    "甲午", "乙未", "丙申", "丁酉", "戊戌", "己亥", "庚子", "辛丑", "壬寅", "癸卯",
    "甲辰", "乙巳", "丙午", "丁未", "戊申", "己酉", "庚戌", "辛亥", "壬子", "癸丑",
    "甲寅", "乙卯", "丙辰", "丁巳", "戊午", "己未", "庚申", "辛酉", "壬戌", "癸亥"
]

# ==========================================
# 2. 命理核心演算法
# ==========================================

def calculate_ten_god(day_stem, target_stem):
    if day_stem not in TEN_STEMS or target_stem not in TEN_STEMS:
        return "未知"
    day_element, day_polarity = TEN_STEMS[day_stem]
    tar_element, tar_polarity = TEN_STEMS[target_stem]
    relation_code = ELEMENT_RELATION[(day_element, tar_element)]
    same_polarity = (day_polarity == tar_polarity)
    return TEN_GODS_MATRIX[(relation_code, same_polarity)]

def get_branch_hidden_with_god(day_stem, branch):
    info = HIDDEN_STEMS_DATA.get(branch)
    if not info:
        return ""
    res = f"{info['main']}({calculate_ten_god(day_stem, info['main'])})"
    if info['sub_1']:
        res += f" {info['sub_1']}({calculate_ten_god(day_stem, info['sub_1'])})"
    if info['sub_2']:
        res += f" {info['sub_2']}({calculate_ten_god(day_stem, info['sub_2'])})"
    return res

def generate_fortune_engine(year, month, day, hour, minute, gender_is_male, timezone_name, day_boundary_zi=True):
    gender = "M" if gender_is_male else "F"
    day_boundary = "zi" if day_boundary_zi else "none"
    chart = calculate_saju(
        year,
        month,
        day,
        hour,
        minute,
        gender=gender,
        timezone_name=timezone_name,
        day_boundary=day_boundary,
    )
    chart_data = chart.as_dict()

    def format_hidden_stems(hidden_stems):
        return "、 ".join(f"{v['stem']}({v['ten_god']})" for v in hidden_stems.values())

    y_stem, y_branch = chart_data["year"]["stem"], chart_data["year"]["branch"]
    m_stem, m_branch = chart_data["month"]["stem"], chart_data["month"]["branch"]
    d_stem, d_branch = chart_data["day"]["stem"], chart_data["day"]["branch"]
    h_stem, h_branch = chart_data["hour"]["stem"], chart_data["hour"]["branch"]

    fortune_timeline = []
    for yun_name, yun_data in chart_data["大運流年總覽"].items():
        pillar_name = yun_name.split(": ", 1)[1]
        start_age_text, end_age_text = yun_data["起迄年齡"].replace("歲", "").split(" - ")
        start_year_text, end_year_text = yun_data["起迄年份"].replace("年", "").split(" - ")
        start_year = int(start_year_text)
        end_year = int(end_year_text)

        status = "氣象安穩"
        if "巳" in pillar_name and d_branch == "申":
            status = "巳申刑合 · 驛馬奔波"
        elif "寅" in pillar_name and d_branch == "申":
            status = "寅申相衝 · 環境動盪"

        fortune_timeline.append({
            "大運": pillar_name,
            "期間": f"{start_year} - {end_year}",
            "年齡": f"{start_age_text}-{end_age_text}歲",
            "狀態": status,
            "起運年": start_year,
        })

    start_age = chart_data["起運歲數_精確"]
    start_detail = chart_data.get("起運歲數_詳細", "")
    start_date = chart_data.get("交運日期", "")

    ziwei_chart = build_ziwei_chart(
        year,
        month,
        day,
        hour,
        minute,
        "乾造 (男)" if gender_is_male else "坤造 (女)",
    )
    ziwei_palaces = ziwei_chart["palaces"]


    return {
        "bazi": {
            "年柱": {"天干": y_stem, "地支": y_branch, "天干十神": calculate_ten_god(d_stem, y_stem), "地支藏干": get_branch_hidden_with_god(d_stem, y_branch)},
            "月柱": {"天干": m_stem, "地支": m_branch, "天干十神": calculate_ten_god(d_stem, m_stem), "地支藏干": get_branch_hidden_with_god(d_stem, m_branch)},
            "日柱": {"天干": d_stem, "地支": d_branch, "天干十神": "日主", "地支藏干": get_branch_hidden_with_god(d_stem, d_branch)},
            "時柱": {"天干": h_stem, "地支": h_branch, "天干十神": calculate_ten_god(d_stem, h_stem), "地支藏干": get_branch_hidden_with_god(d_stem, h_branch)}
        },
        "day_start": f"{round(start_age)} 歲起運 (精確 {start_age} 歲；{start_detail}；交運 {start_date}) / {chart_data['大運方向']}",
        "dynamic_運": fortune_timeline,
        "ziwei": ziwei_palaces,
        "ziwei_meta": ziwei_chart,
    }

# ==========================================
# 3. Streamlit UI 視覺客製化
# ==========================================

st.set_page_config(
    page_title="사주팔자 · 東方星軌命理雙盤系統",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #090a10 0%, #121420 100%);
        color: #e2e8f0;
    }
    h1, h2, h3, h4 {
        color: #d4af37 !important;
        font-family: 'Cinzel', 'Noto Serif TC', serif;
        text-shadow: 0px 0px 8px rgba(212, 175, 55, 0.2);
    }
    .bazi-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(212, 175, 55, 0.15);
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    }
    /* 紫微斗數十二宮方格專用 CSS */
    .ziwei-palace-box {
        background: rgba(15, 17, 26, 0.7);
        border: 1px solid rgba(212, 175, 55, 0.25);
        border-radius: 6px;
        height: 160px;
        padding: 10px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: inset 0 0 10px rgba(212, 175, 55, 0.05);
        transition: all 0.3s ease;
    }
    .ziwei-palace-box:hover {
        border: 1px solid rgba(212, 175, 55, 0.7);
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.15);
    }
    .zw-title {
        color: #718096;
        font-size: 0.85rem;
        display: flex;
        justify-content: space-between;
    }
    .zw-main-stars {
        color: #ffffff;
        font-size: 1.2rem;
        font-weight: bold;
        text-align: center;
        margin-top: 10px;
        letter-spacing: 2px;
    }
    .zw-sub-stars {
        color: #e53e3e; /* 煞星用亮紅 */
        font-size: 0.8rem;
        text-align: center;
    }
    .zw-footer {
        color: #d4af37;
        font-size: 0.8rem;
        display: flex;
        justify-content: space-between;
        border-top: 1px solid rgba(255,255,255,0.05);
        padding-top: 4px;
    }
    .stem-style { font-size: 2.5rem; font-weight: bold; color: #ffffff; }
    .branch-style { font-size: 2.5rem; font-weight: bold; color: #d4af37; }
    .god-style { font-size: 0.85rem; color: #a0aec0; background: rgba(255,255,255,0.05); padding: 2px 6px; border-radius: 4px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 4. 側邊欄輸入控制
# ==========================================

with st.sidebar:
    st.markdown("### 🔮 天體時空參數")
    st.markdown("---")
    
    name = st.text_input("🧙‍♂️ 命主尊稱/代號", "神秘諮詢客")
    gender = st.radio("☯️ 性別設定", ["乾造 (男)", "坤造 (女)"])
    gender_is_male = (gender == "乾造 (男)")
    
    birth_date = st.date_input("📅 出生日期 (公曆)", datetime(1971, 9, 30))
    birth_time = st.time_input("⏰ 出生時間", datetime(1971, 9, 30, 4, 0).time())
    
    timezone_input = st.selectbox("🌐 觀測時區", ["Asia/Taipei (UTC+8)", "Asia/Seoul (UTC+9)"])
    timezone_name = timezone_input.split(" ")[0]
    day_boundary = st.checkbox("子時更換日柱 (day_boundary='zi')", value=True)
    
    st.markdown("---")
    start_btn = st.button("🔮 啟動天水雙盤核心 🔮", use_container_width=True)

# ==========================================
# 5. 主視覺看板渲染
# ==========================================

st.title("사주팔자 × 紫微斗數 命理雙盤系統")
st.caption("融合四柱八字五行與紫微斗數十二宮天盤，還原傳統諮詢師合參的高階式視野佈局")

if not start_btn and 'initialized' not in st.session_state:
    st.markdown("""
        <div style="text-align: center; padding: 80px 0;">
            <h2 style="color: #d4af37;">「地載四柱定格局，天懸斗數看吉凶。」</h2>
            <p style="color: #718096; max-width: 600px; margin: 20px auto;">
                請於左側輸入天體觀測參數。系統將同步排定<b>四柱八字乾坤盤</b>與<b>紫微斗數方格天盤</b>，完成高精度的占卜合參。
            </p>
        </div>
    """, unsafe_allow_html=True)

if start_btn:
    st.session_state['initialized'] = True
    progress_bar = st.progress(0)
    status_text = st.empty()
    stages = [
        "🪐 正在鎖定曆法儒略日與四柱八字...",
        "✨ 正在精確捕捉二十四節氣點與起運交會期...",
        "🌌 正在切分紫微斗數命宮與五行局...",
        "💎 正在依干支四化排列十四主星曜...",
        "☯️ 雙盤同步對齊完畢！"
    ]
    for i, stage in enumerate(stages):
        status_text.markdown(f"<p style='color:#d4af37; text-align:center;'>{stage}</p>", unsafe_allow_html=True)
        progress_bar.progress((i + 1) * 20)
        time.sleep(0.25)
    progress_bar.empty()
    status_text.empty()

# 顯示核心雙盤結果
if 'initialized' in st.session_state:
    res_data = generate_fortune_engine(
        birth_date.year, birth_date.month, birth_date.day,
        birth_time.hour, birth_time.minute, gender_is_male, timezone_name, day_boundary
    )
    
    # ==========================================
    # 區塊 A：四柱八字聖殿面
    # ==========================================
    st.markdown("### 🎴 第一盤：四柱八字乾坤格局")
    col1, col2, col3, col4 = st.columns(4)
    columns_list = [col4, col3, col2, col1] 
    keys_order = ["時柱", "日柱", "月柱", "年柱"]
    
    for col, key in zip(columns_list, keys_order):
        pillar = res_data["bazi"][key]
        with col:
            st.markdown(f"""
                <div class="bazi-card">
                    <div style="color: #718096; font-size: 0.85rem; margin-bottom: 8px;">{key}</div>
                    <div class="god-style">{pillar['天干十神']}</div>
                    <div class="stem-style">{pillar['天干']}</div>
                    <div class="branch-style">{pillar['地支']}</div>
                    <div class="god-style" style="margin-top:8px; font-size:0.75rem; background:rgba(212,175,55,0.06);">藏: {pillar['地支藏干']}</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ==========================================
    # 區塊 B：紫微斗數 4x4 天盤（核心視覺挑戰！）
    # ==========================================
    st.markdown("### 🌌 第二盤：紫微斗數十二宮方格天盤")
    zw = res_data["ziwei"]
    
    def render_palace(palace_key):
        p = zw[palace_key]
        
        # 處理資料中可能是 "主星" 或 "st_stars" 的 key
        main_star = p.get('主星', p.get('st_stars', ''))
        
        return f"""
        <div class="ziwei-palace-box">
            <div class="zw-title">
                <span style="color:#ffffff; font-weight:bold;">{p['宮位']}</span>
                <span style="color:#718096;">{palace_key}</span>
            </div>
            <div class="zw-main-stars">{main_star}</div>
            <div class="zw-sub-stars">{p.get('四化文字', '')} {p.get('煞吉', '')} {p.get('副星', '')}</div>
            <div class="zw-footer">
                <span>{p.get('宮干', '')}</span>
                <span style="font-size:0.7rem; color:#718096;">身宮參見</span>
            </div>
        </div>
        """

    # 第一排宮位：巳 -> 午 -> 未 -> 申
    r1 = st.columns(4)
    with r1[0]: st.markdown(render_palace("巳"), unsafe_allow_html=True)
    with r1[1]: st.markdown(render_palace("午"), unsafe_allow_html=True)
    with r1[2]: st.markdown(render_palace("未"), unsafe_allow_html=True)
    with r1[3]: st.markdown(render_palace("申"), unsafe_allow_html=True)

    # 第二排宮位：辰 與 酉（中間放太極中堂核心）
    r2 = st.columns(4)
    with r2[0]: st.markdown(render_palace("辰"), unsafe_allow_html=True)
    with r2[1]: # 中堂核心左側
        st.markdown(f"""
            <div style="text-align:center; padding-top:25px;">
                <h4 style="margin:0; font-size:1rem; color:#718096 !important;">觀測對象</h4>
                <p style="color:#ffffff; font-size:1.2rem; font-weight:bold; margin:0;">{name}</p>
                <p style="color:#718096; font-size:0.8rem; margin:0;">{gender}</p>
            </div>
        """, unsafe_allow_html=True)
    with r2[2]: # 中堂核心右側
        st.markdown(f"""
            <div style="text-align:center; padding-top:25px;">
                <h4 style="margin:0; font-size:1rem; color:#718096 !important;">交運時空點</h4>
                <p style="color:#d4af37; font-size:0.85rem; font-weight:bold; margin:5px 0 0 0;">{res_data['day_start']}</p>
            </div>
        """, unsafe_allow_html=True)
    with r2[3]: st.markdown(render_palace("酉"), unsafe_allow_html=True)

    # 第三排宮位：卯 與 戌（中間繼續留空保持大氣佈局）
    r3 = st.columns(4)
    with r3[0]: st.markdown(render_palace("卯"), unsafe_allow_html=True)
    with r3[1]: st.markdown("<div style='text-align:center; color:#d4af37; font-size:2.5rem; opacity:0.15; padding-top:10px;'>☯️</div>", unsafe_allow_html=True)
    with r3[2]: st.markdown("<div style='text-align:center; color:#d4af37; font-size:2.5rem; opacity:0.15; padding-top:10px;'>🔮</div>", unsafe_allow_html=True)
    with r3[3]: st.markdown(render_palace("戌"), unsafe_allow_html=True)

    # 第四排宮位：寅 -> 丑 -> 子 -> 亥
    r4 = st.columns(4)
    with r4[0]: st.markdown(render_palace("寅"), unsafe_allow_html=True)
    with r4[1]: st.markdown(render_palace("丑"), unsafe_allow_html=True)
    with r4[2]: st.markdown(render_palace("子"), unsafe_allow_html=True)
    with r4[3]: st.markdown(render_palace("亥"), unsafe_allow_html=True)

    st.markdown("---")

    # ==========================================
    # 區塊 C：大運流年編年史
    # ==========================================
    st.markdown("### 🗺️ 第三盤：大運流年編年史軌跡")
    运_cols = st.columns(len(res_data["dynamic_運"]))
    current_year_now = 2026 # 當前2026年時間線脈絡
    
    for col, u_data in zip(运_cols, res_data["dynamic_運"]):
        with col:
            is_current = u_data["起運年"] <= current_year_now < (u_data["起運年"] + 10)
            border_color = "rgba(212, 175, 55, 0.9)" if is_current else "rgba(255, 255, 255, 0.1)"
            bg_color = "rgba(212, 175, 55, 0.08)" if is_current else "rgba(255, 255, 255, 0.01)"
            tag = " <span style='color:#d4af37; font-size:0.75rem; border:1px solid #d4af37; padding:1px 4px; border-radius:2px;'>現行運</span>" if is_current else ""
            
            st.markdown(f"""
                <div style="border: 1px solid {border_color}; background: {bg_color}; padding: 12px; border-radius: 6px;">
                    <h5 style="margin: 0; color: #ffffff; font-size:1rem;">【{u_data['大運']}】{tag}</h5>
                    <p style="margin: 4px 0; font-size: 0.8rem; color: #a0aec0;">{u_data['期間']} ({u_data['年齡']})</p>
                    <p style="margin: 4px 0 0 0; color: #d4af37; font-size: 0.8rem; font-weight:bold;">🔮 {u_data['狀態']}</p>
                </div>
            """, unsafe_allow_html=True)

    # 諮詢師專用智能備忘
    st.markdown("---")
    st.markdown("### 📝 諮詢師大師級「八紫合參」備忘錄")
    if res_data["bazi"]["日柱"]["天干"] == "戊":
        st.info("💡 **合參核心精要：** 本局八字『傷官佩印』，口才極佳、大有主見。對照【紫微斗數天盤】，命宮坐午宮【巨門】廟旺，外在神態正巧對應巨門口舌洩秀、眼神犀利、能言善道、一針見血之特徵。目前2026年正交八字【壬寅】大運，與日支形成兩寅沖一申（夫妻、驛馬宮受衝）；對照紫微斗數天盤，流年引動申宮與寅宮的【天機、天同、天梁】動星磁場，主這十年居住環境、職涯賽道將迎來大步跨越之變動，充實忙碌，大有可為！")
