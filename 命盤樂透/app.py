import streamlit as st

# ==========================================
# 1. 頁面基礎設定與全域路由 CSS
# ==========================================
st.set_page_config(page_title="天機合參 · 命盤樂透整合系統", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* 👇 1. 暴力突破 Streamlit 預設的隱形主容器寬度限制 */
    .block-container {
        max-width: 95% !important;
        padding-top: 3rem !important;
    }
    
    /* 強制將整個網頁背景設定為深色大氣背景，防止漏白 */
    [data-testid="stAppViewContainer"], .stApp { 
        background-color: #0E1117 !important; 
        color: #FFFFFF; 
        font-family: "Noto Serif TC", serif; 
    }
    
    /* 隱藏首頁的側邊欄與頂部導覽列以保持大氣 */
    [data-testid="collapsedControl"] { display: none; }
    header { visibility: hidden; }
    
    .main-title { text-align: center; font-size: 42px; font-weight: 900; margin-top: 50px; margin-bottom: 10px; letter-spacing: 4px; background: -webkit-linear-gradient(45deg, #D4AF37, #FFF8DC); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .sub-title { text-align: center; font-size: 18px; color: #A0AEC0; margin-bottom: 60px; letter-spacing: 2px; }
    
    /* === 究極 CSS 覆蓋：確保顏色絕對上得去！ === */
    
    /* 1. 按鈕主體外框 */
    div.stButton > button {
        width: 100% !important; 
        height: 360px !important;  
        border-radius: 24px !important; 
        border: none !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important; 
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        background-color: transparent !important; /* 清除所有原生底色 */
    }
    
    /* 避免 Streamlit 內部標籤自帶白底，強制透明 */
    div.stButton > button * {
        background-color: transparent !important; 
    }

    div.stButton > button:hover { 
        transform: translateY(-8px) !important; 
        box-shadow: 0 20px 45px rgba(0,0,0,0.8) !important; 
    }

    /* 2. 🎯 文字段落設定：寶石藍、發光陰影、強制換行 */
    div.stButton > button p {
        color: #003399 !important; /* 高質感寶石深藍色 */
        font-size: 26px !important; 
        font-weight: 900 !important; 
        text-align: center !important;
        white-space: pre-wrap !important; /* 確保 \n 換行 */
        line-height: 1.6 !important; 
        margin: 0 !important;
        text-shadow: 2px 2px 10px rgba(255, 255, 255, 0.9) !important; /* 白色光暈 */
    }

    /* ========================================================
       3. 🎯 終極精準打擊：使用 background-image 強制覆蓋漸層
       ======================================================== */
    
    /* 第一欄：命盤分析 (晨曦金橘漸層) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) div.stButton > button { 
        background-image: linear-gradient(135deg, #FFE259 0%, #FFA751 100%) !important; 
        border: 2px solid #FFD194 !important; 
    }
    
    /* 第二欄：樂透分析 (招財爆發紅漸層) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) div.stButton > button { 
        background-image: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%) !important; 
        border: 2px solid #FF8A80 !important; 
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) div.stButton > button p { 
        color: #FFFFFF !important; 
        text-shadow: 2px 2px 10px rgba(0, 0, 0, 0.5) !important; 
    }
    
    /* 第三欄：命盤合參 (星空粉藍漸層) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) div.stButton > button { 
        background-image: linear-gradient(135deg, #E0C3FC 0%, #8EC5FC 100%) !important; 
        border: 2px solid #A5D7E8 !important; 
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
    if st.button("🔮 命盤分析\n\n深究紫微八字\n掌握靈魂軌跡", use_container_width=True):
        st.switch_page("pages/1_命盤分析.py")

with col2:
    if st.button("📊 樂透分析\n\n大數據監測\n冷熱號碼統計", use_container_width=True):
        st.switch_page("pages/2_樂透分析.py")

with col3:
    if st.button("🌌 命盤 × 樂透合參\n\n五行靈數共振\n專屬高勝率策略", use_container_width=True):
        st.switch_page("pages/3_命盤_樂透合參.py")

st.markdown("<div style='text-align:center; margin-top:80px; color:#666; font-size:12px;'>© 2026 STAR★START 整合決策引擎</div>", unsafe_allow_html=True)
