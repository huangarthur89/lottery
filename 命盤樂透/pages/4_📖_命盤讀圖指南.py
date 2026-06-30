import streamlit as st

import os

# 啟動時自動建立 .streamlit/config.toml 來強制鎖定亮色模式
_config_dir = ".streamlit"
if not os.path.exists(_config_dir):
    try:
        os.makedirs(_config_dir)
    except Exception:
        pass
_config_file = os.path.join(_config_dir, "config.toml")
if not os.path.exists(_config_file):
    try:
        with open(_config_file, "w", encoding="utf-8") as _f:
            _f.write('[theme]\nbase="light"\n')
    except Exception:
        pass

st.set_page_config(
    page_title="命盤讀圖指南 - 阿舍AI命理系統",
    page_icon="📖",
    layout="wide"
)

# 自訂 CSS，維持高質感
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
    .guide-title {
        color: #4A148C;
        font-family: 'Noto Serif TC', serif;
        font-weight: bold;
        border-bottom: 3px solid #4A148C;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    .guide-section {
        background-color: #FAFAFA;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 6px solid #1976D2;
    }
    .guide-h3 {
        color: #1976D2;
        font-weight: bold;
        margin-top: 0;
    }
    .highlight-box {
        background-color: #FFFDE7;
        border: 2px dashed #FBC02D;
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
        color: #F57F17;
        display: inline-block;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='guide-title'>📖 命理大師讀圖指南</h1>", unsafe_allow_html=True)
st.markdown("歡迎來到讀圖指南！這套系統產生的命盤圖表蘊含了海量的大師級資訊。這份手冊將教您如何看懂這些格線、顏色與數字，讓您瞬間晉升為命理內行人。")

st.markdown("---")

st.markdown("## 1. ☯️ 紫微斗數：立體星盤解密")

with st.expander("📍 12 宮位格子：人生的 12 個舞台", expanded=True):
    st.markdown("""
    紫微斗數命盤由 12 個格子組成，代表您人生的 12 個不同領域（稱為「宮位」）。
    - **命宮**：核心性格、天賦、先天的我。
    - **夫妻宮**：感情觀、伴侶特質。
    - **財帛宮**：理財觀念、賺錢方式。
    - **事業宮（官祿）**：工作態度、事業發展。
    - **遷移宮**：外出運、社交給人的第一印象。
    （其他包含：兄弟、子女、疾厄、交友、田宅、福德、父母）
    """)

with st.expander("✨ 黃色發光框：身宮（後天造化）"):
    st.markdown("""
    在 12 個格子中，會有一個格子的邊框被標示為 **黃色發光框**，這稱為**「身宮」**。
    - **意義**：如果說「命宮」是 35 歲以前的先天特質，那「身宮」就是 **35 歲以後的後天造化與人生重心**。
    - **範例**：如果您的黃色框框落在「財帛宮」，代表您人生下半場會非常看重金錢與財務自由。
    """)

with st.expander("🔢 數字密碼：大限與小限（流年）"):
    st.markdown("""
    命盤不只看性格，更能看時間運勢。注意看每個格子裡的數字：
    - **大限（左下角的數字區間，例如 `106-115`）**：
      這代表您的「十年大運」。當您走到這個虛歲年齡區間時，這十年的整體人生舞台就是由這個宮位來掌管。
    - **小限（中間那一長排數字，例如 `106 118 130...`）**：
      這代表您的「單一年度運勢」。因為有 12 個宮位，所以每隔 12 年運勢會繞回來一次。當您剛好是這上面的虛歲年齡時，那一年的流年主軸就在這個宮位！
    """)

with st.expander("🔴 紅色連線：三方四正（吉凶共振）"):
    st.markdown("""
    您會看到盤面上有紅色的線條將幾個宮位連起來，這稱為**「三方四正」**。
    - 在論命時，我們不能只看一個宮位。與它相連的三個宮位，會產生強烈的「共振」效果。
    - **最重要的一組**：通常是「命宮」連到「事業、財帛、遷移」。這四個宮位決定了您在社會上打拼的綜合戰鬥力！
    """)

with st.expander("⭐ 星星的顏色與大小"):
    st.markdown("""
    - **超大字體**：**主星**（如紫微、天機、七殺等），決定了該宮位的主要氣場。
    - **中字體**：**輔星**（如文昌、左輔、擎羊等），負責輔助或破壞主星的能量。
    - **顏色標籤（化星）**：代表動態的引爆點！
        - <span style='color: #C62828; font-weight:bold;'>【化祿】(紅色)</span>：代表順利、財富、桃花。
        - <span style='color: #6A1B9A; font-weight:bold;'>【化權】(紫色)</span>：代表權力、掌控欲、企圖心。
        - <span style='color: #2E7D32; font-weight:bold;'>【化科】(綠色)</span>：代表名聲、考試、貴人。
        - <span style='color: #212121; font-weight:bold;'>【化忌】(黑色)</span>：代表空缺、執著、考驗、糾紛。
    """, unsafe_allow_html=True)

st.markdown("---")

st.markdown("## 2. 🎴 八字四柱：靈魂方程式解密")

with st.expander("🌲 日主元神：天生的氣場基底"):
    st.markdown("""
    八字排盤中，「日柱」上方的那個大字（天干），就是您的**「日主」**，代表最核心的您。
    例如：甲（大樹）、丙（太陽）、戊（高山）、壬（江河）。日主決定了您的基本性格基底。
    """)

with st.expander("🎭 十神陣列：後天天賦與行為模式"):
    st.markdown("""
    圍繞在八字周圍的小字（如七殺、正印、傷官），稱為**「十神」**。
    - 系統會自動幫您計算十神數量，呈現在下方的診斷區塊。
    - **七殺、傷官、劫財多**：適合開創、冒險、創業、打破常規。
    - **正官、正印、正財多**：適合體制內、穩健發展、重視名譽信用。
    - **偏財、食神多**：極具商業嗅覺、創意靈感與藝術天賦。
    """)

with st.expander("🕳️ 地支藏干：隱藏的潛能"):
    st.markdown("""
    在最下方的一排小字，是每個地支裡「暗藏」的天干。這代表您內心深處的潛意識，或者是隱藏的潛能。有時候表面上看不出來的性格，其實都藏在這裡！
    """)

st.markdown("---")

st.markdown("## 3. 🌌 西洋占星：色彩與元素的密碼")

with st.expander("🌈 顏色標籤代表的「四大元素」"):
    st.markdown("""
    占星矩陣中的背景顏色，代表了四大自然元素：
    - <span style='color: #B71C1C; font-weight:bold;'>🔴 紅色 (火象)</span>：牡羊、獅子、射手。代表行動力、熱情、直覺。
    - <span style='color: #424242; font-weight:bold;'>🟤 灰棕色 (土象)</span>：金牛、處女、摩羯。代表務實、落地、物質具現化。
    - <span style='color: #00838F; font-weight:bold;'>🟢 藍綠色 (風象)</span>：雙子、天秤、水瓶。代表邏輯、資訊、溝通傳播。
    - <span style='color: #0D47A1; font-weight:bold;'>🔵 深藍色 (水象)</span>：巨蟹、天蠍、雙魚。代表情緒、同理心、靈性感知。
    """, unsafe_allow_html=True)

with st.expander("🎭 日、月、升的三位一體"):
    st.markdown("""
    - **太陽 (外在)**：您希望讓世界看到您的樣子，您一生的主要社會目標。
    - **月亮 (潛意識)**：您內心深處真正的需求，也是您缺乏安全感時的反應。
    - **上升 (面具)**：您戴上用來適應社會的面具，也是別人對您的第一印象。
    *(系統會自動比對這三者的元素，為您診斷內外在是否衝突或和諧。)*
    """)

st.markdown("---")

st.markdown("## 4. 🧭 流年九宮飛星：風水吉凶視覺化")

with st.expander("🏠 九宮格方位如何看？"):
    st.markdown("""
    請想像這個九宮格就是您家的「平面圖」。
    您可以站在家裡的「正中央」，打開手機的指南針，就可以把螢幕上的「東、南、西、北」對應到真實的居家方位。
    """)

with st.expander("💣 黑色/暗紅色：大凶煞星 (絕對不可動土)"):
    st.markdown("""
    - **五黃 (災瘟星)**：年度最凶的星，代表重大疾病與破財。該方位**絕對不可動土、裝修**，宜靜不宜動。
    - **二黑 (病符星)**：代表小病不斷，該方位同樣不宜見動象。
    - *化解法*：建議在此方位懸掛金屬製品（如六帝錢、銅鈴）來洩煞氣。
    """)

with st.expander("💰 黃色/紫色：大吉喜慶星 (強力催旺)"):
    st.markdown("""
    - **八白 (正財星)**：年度最大的財星！該方位一定要保持明亮、乾淨，可放聚寶盆或流水盆催財。
    - **九紫 (喜慶星)**：代表桃花、結婚、升職。可在此方位擺放紅色物品或常亮的小燈催旺喜氣。
    """)
