import streamlit as st

# ==========================================
# 1. 頁面基礎設定與全域路由 CSS
# ==========================================
st.set_page_config(page_title="天機合參 · 命盤樂透整合系統", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; font-family: "Noto Serif TC", serif; }
    
    /* 隱藏首頁的側邊欄與頂部導覽列 */
    [data-testid="collapsedControl"] { display: none; }
    header { visibility: hidden; }
    
    .main-title { text-align: center; font-size: 42px; font-weight: 900; margin-top: 50px; margin-bottom: 10px; letter-spacing: 4px; background: -webkit-linear-gradient(45deg, #D4AF37, #FFF8DC); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .sub-title { text-align: center; font-size: 18px; color: #A0AEC0; margin-bottom: 60px; letter-spacing: 2px; }
    
    /* === 究極防彈 CSS：直接把 Streamlit 原生文字隱藏，全用 CSS 畫！ === */
    
    /* 1. 隱藏原生按鈕文字 */
    div.stButton > button p {
        display: none !important;
    }
    
    /* 2. 按鈕本體設定 */
    div.stButton > button {
        width: 100% !important; 
        height: 280px !important; 
        border-radius: 16px !important; 
        border: none !important;
        padding: 0 !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease !important; 
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        text-align: center !important;
    }
    div.stButton > button:hover { 
        transform: translateY(-5px) !important; 
        box-shadow: 0 15px 40px rgba(0,0,0,0.8) !important; 
    }

    /* ========================================================
       3. 直接用 CSS ::after 畫出又大又白、完美置中的字體 
       ======================================================== */

    /* 第 1 欄：命盤分析 */
    div[data-testid="column"]:nth-of-type(1) div.stButton > button { background: linear-gradient(135deg, #4A0000 0%, #B8860B 100%) !important; border: 2px solid #D4AF37 !important; }
    div[data-testid="column"]:nth-of-type(1) div.stButton > button::after {
        content: "🔮 命盤分析\\A\\A深究紫微八字\\A掌握靈魂軌跡";
        color: #FFFFFF !important; font-size: 26px !important; font-weight: 900 !important; white-space: pre-wrap !important; line-height: 1.6 !important;
    }

    /* 第 2 欄：樂透分析 */
    div[data-testid="column"]:nth-of-type(2) div.stButton > button { background: linear-gradient(135deg, #004d1a 0%, #6b8e23 100%) !important; border: 2px solid #A8E6CF !important; }
    div[data-testid="column"]:nth-of-type(2) div.stButton > button::after {
        content: "📊 樂透分析\\A\\A大數據監測\\A冷熱號碼統計";
        color: #FFFFFF !important; font-size: 26px !important; font-weight: 900 !important; white-space: pre-wrap !important; line-height: 1.6 !important;
    }

    /* 第 3 欄：命盤合參 */
    div[data-testid="column"]:nth-of-type(3) div.stButton > button { background: linear-gradient(135deg, #1A237E 0%, #0D47A1 100%) !important; border: 2px solid #64B5F6 !important; }
    div[data-testid="column"]:nth-of-type(3) div.stButton > button::after {
        content: "🌌 命盤 × 樂透合參\\A\\A五行靈數共振\\A專屬高勝率策略";
        color: #FFFFFF !important; font-size: 26px !important; font-weight: 900 !important; white-space: pre-wrap !important; line-height: 1.6 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 首頁 UI 佈局 (3 欄式)
# ==========================================
st.markdown("<div class='main-title'>天機合參決策系統</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>命理軌跡 × 數據統計 · 全方位人生與財富導航</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    # 傳入空白字元，文字全交給 CSS 渲染
    if st.button(" ", key="btn_mingpan", use_container_width=True):
        st.switch_page("pages/1_命盤分析.py")

with col2:
    if st.button(" ", key="btn_lotto", use_container_width=True):
        st.switch_page("pages/2_樂透分析.py")

with col3:
    if st.button(" ", key="btn_hybrid", use_container_width=True):
        st.switch_page("pages/3_命盤_樂透合參.py")

st.markdown("<div style='text-align:center; margin-top:80px; color:#666; font-size:12px;'>© 2026 STAR★START 整合決策引擎</div>", unsafe_allow_html=True)