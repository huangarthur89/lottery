import streamlit as st
import time
from datetime import datetime
import pytz
from saju import calculate_saju

# ==========================================
# 1. 網頁初始設定：打造神祕黑金視覺基調
# ==========================================
st.set_page_config(
    page_title="사주팔자 · 東方星軌命理系統",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 注入 CSS 定製：深邃星夜背景、琥珀金文字、神祕學邊框
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f111a 0%, #171926 100%);
        color: #e2e8f0;
    }
    h1, h2, h3 {
        color: #d4af37 !important; /* 琥珀金 */
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
        font-size: 2.5rem;
        font-weight: bold;
        color: #ffffff;
    }
    .branch-style {
        font-size: 2.5rem;
        font-weight: bold;
        color: #d4af37;
    }
    .god-style {
        font-size: 1rem;
        color: #a0aec0;
        background: rgba(255,255,255,0.05);
        padding: 2px 8px;
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 串接 saju.py 排盤核心
# ==========================================
def get_real_saju_data(year, month, day, hour, minute, gender, timezone, day_boundary):
    chart = calculate_saju(year, month, day, hour, minute, gender=gender, timezone_name=timezone, day_boundary=day_boundary)
    chart_data = chart.as_dict()
    
    def format_hidden_stems(hs_dict):
        parts = []
        for v in hs_dict.values():
            parts.append(f"{v['stem']} ({v['ten_god']})")
        return "、 ".join(parts)
        
    bazi = {
        "年柱": {
            "天干": chart_data["year"]["stem"],
            "地支": chart_data["year"]["branch"],
            "天干十神": chart_data["year"]["stem_ten_god"],
            "地支藏干": format_hidden_stems(chart_data["year"]["hidden_stems"])
        },
        "月柱": {
            "天干": chart_data["month"]["stem"],
            "地支": chart_data["month"]["branch"],
            "天干十神": chart_data["month"]["stem_ten_god"],
            "地支藏干": format_hidden_stems(chart_data["month"]["hidden_stems"])
        },
        "日柱": {
            "天干": chart_data["day"]["stem"],
            "地支": chart_data["day"]["branch"],
            "天干十神": chart_data["day"]["stem_ten_god"],
            "地支藏干": format_hidden_stems(chart_data["day"]["hidden_stems"])
        },
        "時柱": {
            "天干": chart_data["hour"]["stem"],
            "地支": chart_data["hour"]["branch"],
            "天干十神": chart_data["hour"]["stem_ten_god"],
            "地支藏干": format_hidden_stems(chart_data["hour"]["hidden_stems"])
        }
    }
    
    dynamic_yun = []
    current_year = datetime.now().year
    
    for yun_name, yun_data in chart_data["大運流年總覽"].items():
        stem_branch = yun_name.split(": ")[1]
        start_y = int(yun_data["起迄年份"].split("年")[0])
        end_y = int(yun_data["起迄年份"].split(" - ")[1].split("年")[0])
        
        status = "未到" if current_year < start_y else "已過"
        if start_y <= current_year <= end_y:
            status = "當前大運"
            
        dynamic_yun.append({
            "大運": stem_branch,
            "期間": f"{start_y}-{end_y}",
            "狀態": status
        })
        
    start_age = chart_data["起運歲數_精確"]
    start_detail = chart_data.get("起運歲數_詳細", "")
    start_date = chart_data.get("交運日期", "")
    day_start = f"{round(start_age)} 歲起運 (精確 {start_age} 歲；{start_detail}；交運 {start_date}) / {chart_data['大運方向']}"
    
    return {
        "bazi": bazi,
        "day_start": day_start,
        "dynamic_運": dynamic_yun
    }

# ==========================================
# 3. 側邊欄：充滿儀式感的輸入面板
# ==========================================
with st.sidebar:
    st.markdown("### 🔮 天體時空參數")
    st.markdown("---")
    
    name = st.text_input("🧙‍♂️ 命主尊稱/代號", "神秘諮詢客")
    gender_input = st.radio("☯️ 性別設定", ["乾造 (男)", "坤造 (女)"])
    gender = "M" if "男" in gender_input else "F"
    
    # 日期與時間選擇
    birth_date = st.date_input("📅 出生日期 (公曆)", datetime(1971, 9, 30))
    birth_time = st.time_input("⏰ 出生時間", datetime(1971, 9, 30, 4, 0).time())
    
    # 時區選擇
    timezone_input = st.selectbox("🌐 觀測觀測時區", ["Asia/Seoul (UTC+9)", "Asia/Taipei (UTC+8)"])
    timezone = timezone_input.split(" ")[0]
    
    day_boundary_input = st.checkbox("子時更換日柱 (day_boundary='zi')", value=True)
    day_boundary = "zi" if day_boundary_input else "none"
    
    st.markdown("---")
    start_btn = st.button("🔮 開啟命運星軌 🔮", use_container_width=True)

# ==========================================
# 4. 主畫面：動態啟動動畫與排盤 UI
# ==========================================
st.title("사주팔자 東方星軌四柱系統")
st.caption("融合傳統《滴天髓》、盲派象法與現代精緻視覺的四柱占卜諮詢演算核心")

# 如果尚未點擊啟動，顯示神祕的大門畫面
if not start_btn and 'initialized' not in st.session_state:
    st.markdown("""
        <div style="text-align: center; padding: 100px 0;">
            <h2 style="color: #d4af37;">「欲知平生性情，先向四柱尋明。」</h2>
            <p style="color: #718096; max-width: 600px; margin: 20px auto;">
                請於左側面板輸入天體觀測參數（出生年月日時），系統將依據儒略日（JDN）與高精度節氣切分演算法，為您撥開命運的星雲。
            </p>
        </div>
    """, unsafe_allow_html=True)

# 觸發啟動：極具儀式感的加載動畫
if start_btn:
    st.session_state['initialized'] = True
    
    # 占卜感啟動特效
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    stages = [
        "🪐 正在計算儒略日 (Julian Day Number)...",
        "✨ 正在精確切分二十四節氣交界點...",
        "🎴 正在配置五行生剋十神矩陣...",
        "🔮 正在由日干推導時柱天干 (五鼠遁)...",
        "🌌 星軌對齊完畢，命盤生成中..."
    ]
    
    for i, stage in enumerate(stages):
        status_text.markdown(f"<p style='color:#d4af37; text-align:center;'>{stage}</p>", unsafe_allow_html=True)
        progress_bar.progress((i + 1) * 20)
        time.sleep(0.4)
        
    progress_bar.empty()
    status_text.empty()

# 顯示排盤結果
if 'initialized' in st.session_state:
    # 呼叫我們的 saju API
    data = get_real_saju_data(
        birth_date.year, birth_date.month, birth_date.day,
        birth_time.hour, birth_time.minute,
        gender, timezone, day_boundary
    )
    
    st.markdown(f"### 🪐 命主 【{name}】 的玄宇八字聖殿")
    st.markdown(f"**基本設定：** {gender_input} | 時區 {timezone} | 起運：{data['day_start']}")
    
    # 四柱並排佈局 (年、月、日、時)
    col1, col2, col3, col4 = st.columns(4)
    columns_list = [col4, col3, col2, col1] # 依傳統從右到左排列：時 -> 日 -> 月 -> 年
    keys_order = ["時柱", "日柱", "月柱", "年柱"]
    
    for col, key in zip(columns_list, keys_order):
        pillar = data["bazi"][key]
        with col:
            st.markdown(f"""
                <div class="bazi-card">
                    <div style="color: #718096; font-size: 0.9rem; margin-bottom: 10px;">{key}</div>
                    <div class="god-style">{pillar['天干十神']}</div>
                    <div class="stem-style">{pillar['天干']}</div>
                    <div class="branch-style">{pillar['地支']}</div>
                    <div class="god-style" style="margin-top:10px;">藏: {pillar['地支藏干']}</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    
    # 大運編年史區塊
    st.markdown("### 🗺️ 大運流年星圖軌跡 (Fortune Timeline)")
    
    cols = st.columns(4)
    
    for i, u_data in enumerate(data["dynamic_運"]):
        col = cols[i % 4]
        with col:
            is_current = "當前大運" in u_data["狀態"]
            border_color = "rgba(212, 175, 55, 0.8)" if is_current else "rgba(255, 255, 255, 0.1)"
            bg_color = "rgba(212, 175, 55, 0.05)" if is_current else "rgba(255, 255, 255, 0.02)"
            
            st.markdown(f"""
                <div style="border: 1px solid {border_color}; background: {bg_color}; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                    <h4 style="margin: 0; color: #ffffff;">大運 【{u_data['大運']}】</h4>
                    <p style="margin: 5px 0; font-size: 0.85rem; color: #a0aec0;">適用期間: {u_data['期間']}</p>
                    <hr style="margin: 8px 0; border-top: 1px solid rgba(255,255,255,0.05);">
                    <p style="margin: 0; color: #d4af37; font-size: 0.9rem;">🔮 狀態: {u_data['狀態']}</p>
                </div>
            """, unsafe_allow_html=True)

    # 底部諮詢師備忘錄
    st.markdown("---")
    st.markdown("### 📝 系統自動判定備忘")
    exact_age = float(data['day_start'].split('精確 ')[1].split(' 歲')[0])
    st.info(f"💡 系統偵測到命主的大運方向為：**{data['day_start'].split(' / ')[1]}**，交運時間點為實歲 **{round(exact_age, 2)}** 歲。排盤核心已處理子時跨日換算與時區轉換，盤面資訊為精確天文觀測結果。")
