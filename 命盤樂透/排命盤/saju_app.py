import streamlit as st
import time
from datetime import datetime
from saju import calculate_saju
from ziwei import build_ziwei_chart, palace_to_compact_html

# ==========================================
# 1. 命理核心資料庫（十神矩陣與地支藏干）
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
# 2. 命理核心演算法（核心運算邏輯）
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
        res += f"、 {info['sub_1']}({calculate_ten_god(day_stem, info['sub_1'])})"
    if info['sub_2']:
        res += f"、 {info['sub_2']}({calculate_ten_god(day_stem, info['sub_2'])})"
    return res

def generate_saju_engine(year, month, day, hour, minute, gender_is_male, timezone_name, day_boundary_zi=True):
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
    current_year_now = datetime.now().year
    for yun_name, yun_data in chart_data["大運流年總覽"].items():
        pillar_name = yun_name.split(": ", 1)[1]
        start_age_text, end_age_text = yun_data["起迄年齡"].replace("歲", "").split(" - ")
        start_year_text, end_year_text = yun_data["起迄年份"].replace("年", "").split(" - ")
        start_year = int(start_year_text)
        end_year = int(end_year_text)

        status = "未到"
        if current_year_now > end_year:
            status = "已過"
        elif start_year <= current_year_now <= end_year:
            status = "現行大運"

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
    ziwei_data = {
        branch: palace_to_compact_html(palace, branch)
        for branch, palace in ziwei_chart["palaces"].items()
    }


    return {
        "bazi": {
            "年柱": {"天干": y_stem, "地支": y_branch, "天干十神": calculate_ten_god(d_stem, y_stem), "地支藏干": get_branch_hidden_with_god(d_stem, y_branch)},
            "月柱": {"天干": m_stem, "地支": m_branch, "天干十神": calculate_ten_god(d_stem, m_stem), "地支藏干": get_branch_hidden_with_god(d_stem, m_branch)},
            "日柱": {"天干": d_stem, "地支": d_branch, "天干十神": "日主", "地支藏干": get_branch_hidden_with_god(d_stem, d_branch)},
            "時柱": {"天干": h_stem, "地支": h_branch, "天干十神": calculate_ten_god(d_stem, h_stem), "地支藏干": get_branch_hidden_with_god(d_stem, h_branch)}
        },
        "day_start": f"{round(start_age)} 歲起運 (精確 {start_age} 歲；{start_detail}；交運 {start_date}) / {chart_data['大運方向']}",
        "dynamic_運": fortune_timeline,
        "ziwei": ziwei_data,
        "ziwei_params": {
            "year_stem": ziwei_chart["year_stem"],
            "month": ziwei_chart["lunar_month"],
            "day": ziwei_chart["lunar_day"],
            "hour": ziwei_chart["lunar_hour"],
            "nature": ziwei_chart["nature"],
            "ming": ziwei_chart["ming_branch"],
            "body": ziwei_chart["body_branch"],
        },
        "timezone": timezone_name,
    }

# ==========================================
# 3. Streamlit 網頁美學與視覺設定
# ==========================================

st.set_page_config(
    page_title="사주팔자 · 東方星軌命理系統",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f111a 0%, #171926 100%);
        color: #e2e8f0;
    }
    h1, h2, h3 {
        color: #d4af37 !important;
        font-family: 'Cinzel', 'Noto Serif TC', serif;
        text-shadow: 0px 0px 10px rgba(212, 175, 55, 0.3);
    }
    .bazi-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        transition: all 0.3s ease;
    }
    .bazi-card:hover {
        border: 1px solid rgba(212, 175, 55, 0.6);
        box-shadow: 0 4px 25px rgba(212, 175, 55, 0.2);
    }
    .stem-style {
        font-size: 2.8rem;
        font-weight: bold;
        color: #ffffff;
        margin: 5px 0;
    }
    .branch-style {
        font-size: 2.8rem;
        font-weight: bold;
        color: #d4af37;
        margin: 5px 0;
    }
    .god-style {
        font-size: 0.9rem;
        color: #a0aec0;
        background: rgba(255,255,255,0.05);
        padding: 4px 10px;
        border-radius: 4px;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 4. 互動控制側邊欄 (Sidebar)
# ==========================================

with st.sidebar:
    st.markdown("### 🔮 天體時空參數")
    st.markdown("---")
    
    name = st.text_input("🧙‍♂️ 命主尊稱/代號", "神秘諮詢客")
    gender = st.radio("☯️ 性別設定", ["乾造 (男)", "坤造 (女)"])
    gender_is_male = (gender == "乾造 (男)")
    
    # 預設載入你提供的 1971/09/30 寅時案例
    birth_date = st.date_input("📅 出生日期 (公曆)", datetime(1971, 9, 30))
    birth_time = st.time_input("⏰ 出生時間", datetime(1971, 9, 30, 4, 0).time())
    
    timezone_input = st.selectbox("🌐 觀測時區", ["Asia/Taipei (UTC+8)", "Asia/Seoul (UTC+9)"])
    timezone_name = timezone_input.split(" ")[0]
    day_boundary = st.checkbox("子時更換日柱 (day_boundary='zi')", value=True)
    
    st.markdown("---")
    start_btn = st.button("🔮 開啟命運星軌 🔮", use_container_width=True)

# ==========================================
# 5. 主視覺畫面渲染
# ==========================================

st.title("사주팔자 東方星軌四柱系統")
st.caption("融合傳統《滴天髓》、盲派象法與現代精緻視覺的四柱占卜諮詢演算核心")

if not start_btn and 'initialized' not in st.session_state:
    st.markdown("""
        <div style="text-align: center; padding: 100px 0;">
            <h2 style="color: #d4af37;">「欲知平生性情，先向四柱尋明。」</h2>
            <p style="color: #718096; max-width: 600px; margin: 20px auto;">
                請於左側面板輸入天體觀測參數（出生年月日時），系統將依據儒略日（JDN）與高精度節氣切分演算法，為您撥開命運的星雲。
            </p>
        </div>
    """, unsafe_allow_html=True)

if start_btn:
    st.session_state['initialized'] = True
    
    # 儀式感加載動畫
    progress_bar = st.progress(0)
    status_text = st.empty()
    stages = [
        "🪐 正在計算天文儒略日 (Julian Day Number)...",
        "✨ 正在依黃道太陽經度切分精確節氣點...",
        "🎴 正在配置五行陰陽生剋十神矩陣...",
        "🔮 正在由日干推導時柱天干 (五鼠遁)...",
        "🌌 星軌對齊完畢，命盤生成中..."
    ]
    for i, stage in enumerate(stages):
        status_text.markdown(f"<p style='color:#d4af37; text-align:center;'>{stage}</p>", unsafe_allow_html=True)
        progress_bar.progress((i + 1) * 20)
        time.sleep(0.3)
    progress_bar.empty()
    status_text.empty()

# 渲染精美占卜結果
if 'initialized' in st.session_state:
    # 呼叫純算法後端
    res_data = generate_saju_engine(
        birth_date.year, birth_date.month, birth_date.day,
        birth_time.hour, birth_time.minute, gender_is_male, timezone_name, day_boundary
    )
    
    st.markdown(f"### 🪐 命主 【{name}】 的玄宇八字聖殿")
    st.markdown(f"**基本設定：** {gender} | 時區 {res_data['timezone']} | 觀測交運點：{res_data['day_start']}")
    
    # 依傳統排盤：從右到左（時柱 -> 日柱 -> 月柱 -> 年柱）
    col1, col2, col3, col4 = st.columns(4)
    columns_list = [col4, col3, col2, col1] 
    keys_order = ["時柱", "日柱", "月柱", "年柱"]
    
    for col, key in zip(columns_list, keys_order):
        pillar = res_data["bazi"][key]
        with col:
            st.markdown(f"""
                <div class="bazi-card">
                    <div style="color: #718096; font-size: 0.95rem; margin-bottom: 12px; letter-spacing:2px;">{key}</div>
                    <div class="god-style">{pillar['天干十神']}</div>
                    <div class="stem-style">{pillar['天干']}</div>
                    <div class="branch-style">{pillar['地支']}</div>
                    <div class="god-style" style="margin-top:12px; font-size:0.8rem; background:rgba(212,175,55,0.08); color:#e2e8f0;">
                        藏: {pillar['地支藏干']}
                    </div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    
    # 大運流年展示
    st.markdown("### 🗺️ 大運編年史軌跡 (Fortune Timeline)")
    运_cols = st.columns(len(res_data["dynamic_運"]))
    
    current_year_now = datetime.now().year
    
    for col, u_data in zip(运_cols, res_data["dynamic_運"]):
        with col:
            # 判斷目前年份是否落在該大運區間
            is_current = u_data["狀態"] == "現行大運"
            
            border_color = "rgba(212, 175, 55, 0.9)" if is_current else "rgba(255, 255, 255, 0.1)"
            bg_color = "rgba(212, 175, 55, 0.08)" if is_current else "rgba(255, 255, 255, 0.02)"
            tag = " <span style='color:#d4af37; font-size:0.8rem; border:1px solid #d4af37; padding:2px 5px; border-radius:3px;'>現行大運</span>" if is_current else ""
            
            st.markdown(f"""
                <div style="border: 1px solid {border_color}; background: {bg_color}; padding: 18px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                    <h4 style="margin: 0; color: #ffffff; font-size:1.2rem;">【{u_data['大運']}】大運 {tag}</h4>
                    <p style="margin: 6px 0; font-size: 0.85rem; color: #a0aec0;">區間: {u_data['期間']} ({u_data['年齡']})</p>
                    <hr style="margin: 8px 0; border-top: 1px solid rgba(212,175,55,0.15);">
                    <p style="margin: 0; color: #d4af37; font-size: 0.9rem; font-weight:bold;">🔮 象意: {u_data['狀態']}</p>
                </div>
            """, unsafe_allow_html=True)

    # 底部諮詢師智能备忘
    st.markdown("---")
    st.markdown("### 🌌 紫微斗數星曜天盤 (Zi Wei Dou Shu Chart)")

    ziwei_data = res_data["ziwei"]
    
    r1_cols = st.columns(4)
    with r1_cols[0]: st.markdown(f'<div class="bazi-card" style="height:120px; font-size:1.0rem;">{ziwei_data["巳"]}</div>', unsafe_allow_html=True)
    with r1_cols[1]: st.markdown(f'<div class="bazi-card" style="height:120px; font-size:1.0rem;">{ziwei_data["午"]}</div>', unsafe_allow_html=True)
    with r1_cols[2]: st.markdown(f'<div class="bazi-card" style="height:120px; font-size:1.0rem;">{ziwei_data["未"]}</div>', unsafe_allow_html=True)
    with r1_cols[3]: st.markdown(f'<div class="bazi-card" style="height:120px; font-size:1.0rem;">{ziwei_data["申"]}</div>', unsafe_allow_html=True)

    r2_cols = st.columns(4)
    with r2_cols[0]: st.markdown(f'<div class="bazi-card" style="height:120px; font-size:1.0rem;">{ziwei_data["辰"]}</div>', unsafe_allow_html=True)
    with r2_cols[1]: 
        st.markdown(f"""
        <div style="text-align:center; padding-top:20px;">
            <div style="color:#d4af37; font-size:1.2rem; font-weight:bold; letter-spacing: 2px;">中天斗數</div>
            <div style="color:#a0aec0; font-size:0.85rem; margin-top:5px;">紫微天盤</div>
        </div>
        """, unsafe_allow_html=True)
    with r2_cols[2]: 
        st.markdown(f"""
        <div style="text-align:center; padding-top:20px;">
            <div style="color:#a0aec0; font-size:0.85rem; margin-top:5px;">農曆參數</div>
            <div style="color:#d4af37; font-size:0.95rem;">{res_data['ziwei_params']['month']}月 {res_data['ziwei_params']['day']}日 {res_data['ziwei_params']['hour']}時</div>
        </div>
        """, unsafe_allow_html=True)
    with r2_cols[3]: st.markdown(f'<div class="bazi-card" style="height:120px; font-size:1.0rem;">{ziwei_data["酉"]}</div>', unsafe_allow_html=True)

    r3_cols = st.columns(4)
    with r3_cols[0]: st.markdown(f'<div class="bazi-card" style="height:120px; font-size:1.0rem;">{ziwei_data["卯"]}</div>', unsafe_allow_html=True)
    with r3_cols[1]: st.empty() # 中間留空
    with r3_cols[2]: st.empty() # 中間留空
    with r3_cols[3]: st.markdown(f'<div class="bazi-card" style="height:120px; font-size:1.0rem;">{ziwei_data["戌"]}</div>', unsafe_allow_html=True)

    r4_cols = st.columns(4)
    with r4_cols[0]: st.markdown(f'<div class="bazi-card" style="height:120px; font-size:1.0rem;">{ziwei_data["寅"]}</div>', unsafe_allow_html=True)
    with r4_cols[1]: st.markdown(f'<div class="bazi-card" style="height:120px; font-size:1.0rem;">{ziwei_data["丑"]}</div>', unsafe_allow_html=True)
    with r4_cols[2]: st.markdown(f'<div class="bazi-card" style="height:120px; font-size:1.0rem;">{ziwei_data["子"]}</div>', unsafe_allow_html=True)
    with r4_cols[3]: st.markdown(f'<div class="bazi-card" style="height:120px; font-size:1.0rem;">{ziwei_data["亥"]}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📝 盲派形體與氣場解析備忘錄")
    
    # 根據排出日主進行動態提示
    d_stem_detected = res_data["bazi"]["日柱"]["天干"]
    current_yun = next((u for u in res_data["dynamic_運"] if u["狀態"] == "現行大運"), None)
    if d_stem_detected == "戊":
        current_yun_text = f"目前正交【{current_yun['大運']}】大運（{current_yun['期間']}）" if current_yun else "目前未落在已列出的大運區間"
        st.info(f"💡 **諮詢師專用解盤提示：** 本局日元【戊土】，請先以月令、透干、地支藏干與大運流年交互判讀。{current_yun_text}，宜再結合刑沖合害、格局與用神取捨做細部解盤。")
    else:
        st.info(f"💡 **目前盤面動態提示：** 日主為【{d_stem_detected}】，系統已自動對齊生剋磁場。大運流年已依據男女順逆排定，請結合地支藏干十神進行格局與用神取捨。")
