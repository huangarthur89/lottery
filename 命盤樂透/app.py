import streamlit as st

# ==========================================
# 1. 頁面基礎設定與全域路由 CSS
# ==========================================
st.set_page_config(page_title="天機合參 · 命盤樂透整合系統", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; font-family: "Noto Serif TC", serif; }
    
    /* 隱藏首頁的側邊欄與頂部導覽列以保持大氣 */
    [data-testid="collapsedControl"] { display: none; }
    header { visibility: hidden; }
    
    .main-title { text-align: center; font-size: 42px; font-weight: 900; margin-top: 40px; margin-bottom: 10px; letter-spacing: 4px; background: -webkit-linear-gradient(45deg, #D4AF37, #FFF8DC); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .sub-title { text-align: center; font-size: 18px; color: #A0AEC0; margin-bottom: 50px; letter-spacing: 2px; }
    
    /* === 究極 CSS 覆蓋：精準打擊，確保換行與置中 === */
    /* 1. 按鈕主體外框 */
    div[data-testid="column"] button {
        width: 100% !important; 
        height: 220px !important; 
        border-radius: 16px !important; 
        border: none !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease !important; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
        padding: 0 !important;
    }
    
    /* 2. 確保按鈕內的文字容器滿版且置中 */
    div[data-testid="column"] button div[data-testid="stMarkdownContainer"] {
        width: 100% !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }

    /* 3. 🎯 核心修復：精準鎖定文字段落，放大、白字、置中、保留換行 (\n) */
    div[data-testid="column"] button p { 
        color: #FFFFFF !important;
        font-size: 24px !important; 
        font-weight: 900 !important; 
        text-align: center !important;
        white-space: pre-wrap !important; /* ★ 這是讓 \\n 成功換行的絕對關鍵 */
        line-height: 1.6 !important; 
        margin: 0 auto !important; 
        width: 100% !important;
    }
    
    /* 4. 滑鼠懸浮特效 */
    div[data-testid="column"] button:hover { 
        transform: translateY(-5px) !important; 
        box-shadow: 0 15px 40px rgba(0,0,0,0.8) !important; 
    }

    /* 5. 四大按鈕專屬漸層背景 (保留您已成功的完美版本) */
    div[data-testid="column"]:nth-of-type(1) div[data-testid="stVerticalBlock"] > div:nth-child(1) button { background: linear-gradient(135deg, #4A0000 0%, #B8860B 100%) !important; border: 2px solid #D4AF37 !important; }
    div[data-testid="column"]:nth-of-type(1) div[data-testid="stVerticalBlock"] > div:nth-child(3) button { background: linear-gradient(135deg, #E65100 0%, #FFB300 100%) !important; border: 2px solid #FFE082 !important; }
    div[data-testid="column"]:nth-of-type(2) div[data-testid="stVerticalBlock"] > div:nth-child(1) button { background: linear-gradient(135deg, #004d1a 0%, #6b8e23 100%) !important; border: 2px solid #A8E6CF !important; }
    div[data-testid="column"]:nth-of-type(2) div[data-testid="stVerticalBlock"] > div:nth-child(3) button { background: linear-gradient(135deg, #1A237E 0%, #0D47A1 100%) !important; border: 2px solid #64B5F6 !important; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 首頁 UI 佈局 (2x2 網格)
# ==========================================
st.markdown("<div class='main-title'>天機合參決策系統</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>命理軌跡 × 數據統計 · 全方位人生與財富導航</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    if st.button("🔮 命盤分析\n\n深究紫微八字\n掌握靈魂軌跡", use_container_width=True):
        st.switch_page("pages/1_命盤分析.py")
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🎰 威力彩分析\n\n雙區智能健檢\n頭獎大數據回測", use_container_width=True):
        st.switch_page("pages/3_威力彩分析.py")

with col2:
    if st.button("📊 大樂透分析\n\n歷史數據監測\n冷熱號碼統計", use_container_width=True):
        st.switch_page("pages/2_大樂透分析.py")
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🌌 命盤 × 樂透合參\n\n五行靈數共振\n專屬高勝率策略", use_container_width=True):
        st.switch_page("pages/4_命盤_樂透合參.py")

st.markdown("<div style='text-align:center; margin-top:60px; color:#666; font-size:12px;'>© 2026 STAR★START 整合決策引擎</div>", unsafe_allow_html=True)
