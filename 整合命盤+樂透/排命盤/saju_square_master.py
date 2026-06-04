import streamlit as st

# ==========================================
# 1. 頁面基礎設定 (全白高對比印刷感)
# ==========================================
st.set_page_config(page_title="大師級正方形八紫合參天盤", layout="wide")

# ==========================================
# 2. 注入極致放大的 CSS Grid 正方形樣式
# ==========================================
css_style = """
<style>
    /* 強制全白背景與明體字型 */
    .stApp { background-color: #FFFFFF !important; }
    
    /* 命盤主容器：強制鎖定為完美的正方形 1:1 比例 */
    .ziwei-square-board {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        grid-template-rows: repeat(4, 1fr);
        width: 100%;
        max-width: 850px; /* 控制在螢幕上的適中大小 */
        aspect-ratio: 1 / 1; /* 核心關鍵：強制寬高比 1:1 形成正方形 */
        margin: 0 auto;
        background-color: #FFFFFF;
        border: 3px solid #000000;
        font-family: "MingLiU", "PMingLiU", "Noto Serif TC", serif;
        color: #000000;
        box-sizing: border-box;
    }
    
    /* 十二宮位單一方格：同樣鎖定 1:1 */
    .palace-cell {
        border: 1px solid #333333;
        position: relative;
        padding: 8px;
        box-sizing: border-box;
        background-color: #FFFFFF;
    }
    
    /* 中堂核心（跨越中間 2x2 的正方形區域） */
    .center-hall {
        grid-column: 2 / 4;
        grid-row: 2 / 4;
        border: 2px solid #000000;
        position: relative;
        padding: 18px;
        background-color: #FDFDFD;
        box-sizing: border-box;
    }

    /* === 宮位內部四角定位 (字體全面放大版) === */
    /* 左上：小星群 (由 11px 放大至 14px) */
    .p-tl { position: absolute; top: 6px; left: 8px; font-size: 14px; color: #333333; width: 45%; line-height: 1.3; text-align: left; }
    
    /* 右上：主星與重要副星 (直書感，由 14px 放大至 19px) */
    .p-tr { position: absolute; top: 6px; right: 8px; font-size: 19px; color: #000000; width: 50%; line-height: 1.2; text-align: right; }
    
    /* 主星特大號字體 (由 17px 放大至 23px) */
    .main-star { font-size: 23px; font-weight: bold; color: #000000; }
    
    /* 吉凶星與煞星標記 */
    .red-star { color: #D32F2F; font-weight: bold;}
    .blue-star { color: #1976D2; font-weight: bold;}
    
    /* 左下：大限與宮位名稱 (宮位名稱放大至 17px 紅字) */
    .p-bl { position: absolute; bottom: 6px; left: 8px; font-size: 13px; text-align: left; line-height: 1.3; }
    .palace-name { font-size: 17px; font-weight: bold; color: #D32F2F; display: block; margin-top: 3px; }
    
    /* 右下：天干地支與五行 (由 13px 放大至 16px) */
    .p-br { position: absolute; bottom: 6px; right: 8px; font-size: 16px; font-weight: bold; text-align: center; line-height: 1.2; }
    
    /* 四化標記 (加大方塊面積) */
    .sihua { display: inline-block; padding: 2px 4px; color: #FFFFFF; font-size: 12px; font-weight: bold; border-radius: 3px; margin-top: 3px;}
    .s-lu { background-color: #2E7D32; } 
    .s-quan { background-color: #6A1B9A; } 
    .s-ke { background-color: #1565C0; } 
    .s-ji { background-color: #C62828; } 
    
    /* 中堂文字排版放大 (14px 放大至 16px) */
    .center-text { font-size: 16px; line-height: 1.8; color: #000000; }
    .center-title { color: #D32F2F; font-size: 22px; font-weight: bold; text-align: center; margin-bottom: 12px; letter-spacing: 2px;}
</style>
"""

# ==========================================
# 3. 建立網頁實體結構
# ==========================================
# 內部完全填滿你提供的標準排盤教學範例數據
html_content = f"""
{css_style}
<div class="ziwei-square-board">
    <div class="palace-cell">
        <div class="p-tl">博病<br>士<br><br>劫晦<br>煞氣<br><br><span style="color:#666;">天封孤天<br>巫誥辰官</span></div>
        <div class="p-tr"><span class="main-star">太</span><br><span class="main-star">陽</span><br><span style="font-size:14px;color:#666;">廟旺</span></div>
        <div class="p-bl">6 18 30 42 54 66<br>103---112<br><span class="palace-name">【福德】</span></div>
        <div class="p-br">水<br>癸<br>巳</div>
    </div>
    
    <div class="palace-cell">
        <div class="p-tl">力死<br>士<br><br>華歲<br>蓋建<br><br><span style="color:#666;">三蜚鳳陰<br>台廉閣煞</span></div>
        <div class="p-tr"><span class="main-star">武貪</span><br><span class="main-star">曲狼</span><br><span style="font-size:14px;color:#666;">廟廟</span><br><span class="sihua s-quan">權</span> <span class="sihua s-lu">祿</span></div>
        <div class="p-bl">5 17 29 41 53 65<br>93---102<br><span class="palace-name">【田宅】</span></div>
        <div class="p-br">金<br>甲<br>午</div>
    </div>
    
    <div class="palace-cell">
        <div class="p-tl">伏帝<br>兵旺<br><br>天貫<span class="red-star">業</span><br>煞索<span class="red-star">障</span></div>
        <div class="p-tr"><span class="main-star">天</span><br><span class="main-star">機</span><br><span style="font-size:14px;color:#666;">旺利</span><br><span class="sihua s-ke">科</span></div>
        <div class="p-bl">4 16 28 40 52 64<br>83---92<br><span class="palace-name">【官祿】</span></div>
        <div class="p-br">金<br>乙<br>未</div>
    </div>
    
    <div class="palace-cell">
        <div class="p-tl">大臨<br>耗官<br><br>指官<span class="red-star">來</span><br>背符<span class="red-star">因</span></div>
        <div class="p-tr"><span class="main-star">紫天</span><br><span class="main-star">微府</span><br><span style="font-size:14px;color:#666;">旺旺</span><br><br><span style="font-size:15px; font-weight:bold; color:#1565C0;">左<br>輔</span></div>
        <div class="p-bl">3 15 27 39 51 63<br>73---82<br><span class="palace-name">【朋友】</span></div>
        <div class="p-br">火<br>丙<br>申</div>
    </div>

    <div class="palace-cell">
        <div class="p-tl">青墓<br>幕<br><br>息病<br>神符</div>
        <div class="p-tr"><span class="main-star">天</span><br><span class="main-star">同</span><br><span style="font-size:14px;color:#666;">平</span></div>
        <div class="p-bl" style="color:#D32F2F; font-weight:bold; font-size:15px; bottom:55px; line-height:1.3;">2024年<br>甲辰年<br>流年命宮</div>
        <div class="p-bl">7 19 31 43 55 67<br>113---122<br><span class="palace-name">【父母】</span></div>
        <div class="p-br">水<br>壬<br>辰</div>
    </div>
    
    <div class="center-hall">
        <svg style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:1;">
            <line x1="0" y1="75%" x2="75%" y2="0" stroke="#D32F2F" stroke-width="2" />
            <line x1="0" y1="75%" x2="100%" y2="25%" stroke="#D32F2F" stroke-width="2" />
            <line x1="0" y1="75%" x2="100%" y2="100%" stroke="#D32F2F" stroke-width="2" />
            <line x1="75%" y1="0" x2="100%" y2="25%" stroke="#D32F2F" stroke-width="1.5" stroke-dasharray="5,5" />
            <line x1="100%" y1="25%" x2="100%" y2="100%" stroke="#D32F2F" stroke-width="1.5" stroke-dasharray="5,5" />
        </svg>

        <div style="position:relative; z-index:2;" class="center-text">
            <div class="center-title">從星開始 紫微研究苑</div>
            <table style="width:100%; text-align:left; font-size:15px; border-collapse:collapse; line-height:1.8;">
                <tr><td><b>姓名：</b>排盤教學</td><td><b>現在虛歲：</b>48 歲</td></tr>
                <tr><td><b>命造：</b>陽女</td><td><b>生肖屬相：</b>龍</td></tr>
                <tr><td colspan="2"><b>陽曆時間：</b>1976年6月20日 早上 6時</td></tr>
                <tr><td colspan="2"><b>農曆時間：</b>1976年5月23日 卯時生</td></tr>
                <tr><td colspan="2"><b>農曆四柱：</b>丙辰年 甲午月 癸卯日 乙卯時</td></tr>
                <tr><td colspan="2"><b>節氣四柱：</b>丙辰年 甲午月 癸卯日 乙卯時</td></tr>
                <tr><td><b>五行局數：</b>木三局</td><td><b>身宮落點：</b>酉宮</td></tr>
                <tr><td><b>命主星曜：</b>文曲</td><td><b>身主星曜：</b>文昌</td></tr>
                <tr><td colspan="2"><b>子年運行斗君：</b>亥宮</td></tr>
            </table>
            <div style="text-align:center; margin-top:15px; font-weight:bold; color:#1565C0; font-size:14px; letter-spacing:1px;">
                1.2.2 公眾免費版 · #E43B
            </div>
        </div>
    </div>
    
    <div class="palace-cell">
        <div class="p-tl">病冠<br>符帶<br><br>咸小<br>池耗</div>
        <div class="p-tr"><span class="main-star">太</span><br><span class="main-star">陰</span><br><span style="font-size:14px;color:#666;">廟旺</span></div>
        <div class="p-bl">2 14 26 38 50 62<br>63---72<br><span class="palace-name" style="color:#000000;">【身宮】</span><span class="palace-name">【遷移】</span></div>
        <div class="p-br">火<br>丁<br>酉</div>
    </div>

    <div class="palace-cell">
        <div class="p-tl">小絕<br>耗<br><br>歲弔<br>驛客</div>
        <div class="p-tr"><span class="main-star">七</span><br><span class="main-star">殺</span><br><span style="font-size:14px;color:#666;">廟</span></div>
        <div class="p-bl">8 20 32 44 56 68<br>3---12<br><span class="palace-name">【命宮】</span></div>
        <div class="p-br">木<br>辛<br>卯</div>
    </div>
    
    <div class="palace-cell">
        <div class="p-tl">喜沐<br>神浴<br><br>月大<br>煞耗</div>
        <div class="p-tr"><span class="main-star">破</span><br><span class="main-star">軍</span><br><span style="font-size:14px;color:#666;">廟旺</span></div>
        <div class="p-bl">1 13 25 37 49 61<br>53---62<br><span class="palace-name">【疾厄】</span></div>
        <div class="p-br">木<br>戊<br>戌</div>
    </div>

    <div class="palace-cell">
        <div class="p-tl">將胎<br>軍<br><br>攀天<br>鞍德</div>
        <div class="p-tr"><span class="main-star">天</span><br><span class="main-star">梁</span><br><span style="font-size:14px;color:#666;">陷</span></div>
        <div class="p-bl">9 21 33 45 57 69<br>13---22<br><span class="palace-name">【兄弟】</span></div>
        <div class="p-br">木<br>庚<br>寅</div>
    </div>
    
    <div class="palace-cell">
        <div class="p-tl">鈴天奏養<br>星梁書<br>旺旺<br><br>將白<br>星虎</div>
        <div class="p-tr"><span class="main-star">廉</span><br><span class="main-star">貞</span><br><span style="font-size:14px;color:#666;">廟</span><br><span class="sihua s-ji">忌</span></div>
        <div class="p-bl">10 22 34 46 58 70<br>23---32<br><span class="palace-name">【夫妻】</span></div>
        <div class="p-br">土<br>辛<br>丑</div>
    </div>
    
    <div class="palace-cell">
        <div class="p-tl">天解<br>廚神</div>
        <div class="p-tr"><span class="main-star">巨</span><br><span class="main-star">門</span><br><span style="font-size:14px;color:#666;">廟旺</span></div>
        <div class="p-bl">11 23 35 47 59 71<br>33---42<br><span class="palace-name">【子女】</span></div>
        <div class="p-br">土<br>庚<br>子</div>
    </div>
    
    <div class="palace-cell">
        <div class="p-tl">飛長<br>廉生<br><br>亡龍<br>神德</div>
        <div class="p-tr"><span class="main-star">天天</span><br><span class="main-star">同梁</span><br><span style="font-size:14px;color:#666;">旺旺</span></div>
        <div class="p-bl">12 24 36 48 60 72<br>43---52<br><span class="palace-name">【財帛】</span></div>
        <div class="p-br">木<br>己<br>亥</div>
    </div>
</div>
"""

# 將全新比例的正方形 HTML 渲染進網頁中
st.markdown(html_content, unsafe_allow_html=True)
