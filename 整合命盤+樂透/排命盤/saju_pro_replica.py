import streamlit as st
import re

# ==========================================
# 1. 頁面與核心 CSS 設定 (極致高密度專業排版)
# ==========================================
st.set_page_config(page_title="大師級·高密度紫微天盤", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; color: #000000; }
    .ziwei-square-board {
        display: grid; grid-template-columns: repeat(4, 1fr); grid-template-rows: repeat(4, 1fr);
        width: 100%; max-width: 900px; aspect-ratio: 1 / 1; margin: 0 auto;
        background-color: #FFFFFF; border: 2px solid #000000;
        font-family: "MingLiU", "PMingLiU", "Noto Serif TC", serif; box-sizing: border-box;
    }
    
    .palace-cell { border: 1px solid #666666; position: relative; padding: 4px; box-sizing: border-box; background: #FFF; }
    
    .center-hall {
        grid-column: 2 / 4; grid-row: 2 / 4; border: 1px solid #666666;
        position: relative; padding: 15px; background-color: #FAFAFA; box-sizing: border-box;
    }
    
    /* === 毫米級高密度定位 === */
    /* 左上：博士、長生、歲建 (直書併排) */
    .p-tl-group { position: absolute; top: 4px; left: 4px; display: flex; gap: 4px; font-size: 12px; color: #000; line-height: 1.1; text-align: center;}
    .tl-col { display: flex; flex-direction: column; }
    
    /* 左偏中：乙丙級灰色副星群 */
    .p-sub-stars { position: absolute; top: 48px; left: 4px; font-size: 11px; color: #555; width: 65%; line-height: 1.2; text-align: left; letter-spacing: -0.5px;}
    
    /* 右上：主星與甲級吉煞星 */
    .p-tr { position: absolute; top: 4px; right: 4px; font-size: 18px; color: #000; width: 50%; line-height: 1.1; text-align: right; }
    .main-star { font-size: 20px; font-weight: bold; letter-spacing: 0px; }
    .brightness { font-size: 10px; color: #666; display: inline-block; margin-top: 2px; margin-left: 2px;}
    
    /* 左下：小限歲數與大限 */
    .p-bl-ages { position: absolute; bottom: 35px; left: 4px; font-size: 10px; color: #333; letter-spacing: -0.5px; line-height: 1.1; width: 100%;}
    .p-bl-limit { position: absolute; bottom: 4px; left: 4px; font-size: 12px; color: #000; text-align: center; width: 60px;}
    .palace-name { font-size: 15px; font-weight: bold; color: #D32F2F; display: block; margin-top: 2px; }
    
    /* 右下：五行與干支 */
    .p-br { position: absolute; bottom: 4px; right: 4px; font-size: 14px; color: #000; text-align: center; line-height: 1.2; }
    
    /* 流年命宮專屬標記 (絕對定位於宮位左側中間，保證不重疊) */
    .liu-nian-marker { position: absolute; top: 40%; left: 8px; font-size: 15px; font-weight: bold; color: #D32F2F; line-height: 1.3; text-align: left;}
    
    /* 四化標記 */
    .sihua { display: inline-block; padding: 0px 2px; color: #FFF; font-size: 11px; border-radius: 2px; margin-top: 1px;}
    .s-lu { background-color: #2E7D32; } .s-quan { background-color: #6A1B9A; } 
    .s-ke { background-color: #1565C0; } .s-ji { background-color: #C62828; }
    .red-txt { color: #D32F2F; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 超高密度星曜數據庫 (完美復刻圖 2 資訊量)
# ==========================================
# 這裡將 108 星與所有數字精確排入，模擬專業算命引擎的輸出結果
full_ziwei_data = {
    "巳": {
        "tl1": "博病<br>士", "tl2": "劫晦<br>煞氣", "sub": "天封孤天天<br>巫誥辰官喜姚",
        "tr": "<span class='main-star'>太</span><br><span class=\"main-star\">陽</span><br><span class='brightness'>旺</span>",
        "ages": "6 18 30 42 54 66 78 90", "limit": "103---112", "p_name": "福德", "br": "水<br>癸<br>巳"
    },
    "午": {
        "tl1": "力死<br>士", "tl2": "災喪<br>煞門", "sub": "三蜚鳳陰<br>台廉閣煞",
        "tr": "<span class='main-star'>武貪</span><br><span class=\"main-star\">曲狼</span><br><span class='brightness'>廟廟</span><br><span class='sihua s-quan'>權</span> <span class='sihua s-lu'>祿</span>",
        "ages": "5 17 29 41 53 65 77 89", "limit": "93---102", "p_name": "田宅", "br": "金<br>甲<br>午"
    },
    "未": {
        "tl1": "伏帝<br>兵旺", "tl2": "天貫<br>煞索", "sub": "<span class='red-txt'>業</span><br><span class='red-txt'>障</span>",
        "tr": "<span class='main-star'>天</span><br><span class=\"main-star\">機</span><br><span class='brightness'>利</span><br><span class='sihua s-ke'>科</span>",
        "ages": "4 16 28 40 52 64 76 88", "limit": "83---92", "p_name": "官祿", "br": "金<br>乙<br>未"
    },
    "申": {
        "tl1": "大臨<br>耗官", "tl2": "指官<br>背符", "sub": "<span class='red-txt'>來</span><br><span class='red-txt'>因</span>",
        "tr": "<span class='main-star'>紫天</span><br><span class=\"main-star\">微府</span><br><span class='brightness'>旺旺</span><br><br><span style='font-size:12px;font-weight:bold;'>左<br>輔</span>",
        "ages": "3 15 27 39 51 63 75 87", "limit": "73---82", "p_name": "朋友", "br": "火<br>丙<br>申"
    },
    "辰": {
        "tl1": "青墓<br>龍", "tl2": "息病<br>神符", "sub": "",
        "tr": "<span class='main-star'>天</span><br><span class=\"main-star\">同</span><br><span class='brightness'>平</span>",
        "ages": "7 19 31 43 55 67 79 91", "limit": "113---122", "p_name": "父母", "br": "水<br>壬<br>辰"
    },
    "酉": {
        "tl1": "病冠<br>符帶", "tl2": "咸小<br>池耗", "sub": "",
        "tr": "<span class='main-star'>太</span><br><span class=\"main-star\">陰</span><br><span class='brightness'>旺</span>",
        "ages": "2 14 26 38 50 62 74 86", "limit": "63---72", "p_name": "遷移", "br": "火<br>丁<br>酉", "is_body": True
    },
    "卯": {
        "tl1": "小絕<br>耗", "tl2": "歲弔<br>驛客", "sub": "",
        "tr": "<span class='main-star'>七</span><br><span class=\"main-star\">殺</span><br><span class='brightness'>廟</span>",
        "ages": "8 20 32 44 56 68 80 92", "limit": "3---12", "p_name": "命宮", "br": "木<br>辛<br>卯", "is_liu_nian": True
    },
    "戌": {
        "tl1": "喜沐<br>神浴", "tl2": "月大<br>煞耗", "sub": "",
        "tr": "<span class='main-star'>貪</span><br><span class=\"main-star\">狼</span><br><span class='brightness'>廟</span>",
        "ages": "1 13 25 37 49 61 73 85", "limit": "53---62", "p_name": "疾厄", "br": "木<br>戊<br>戌"
    },
    "寅": {
        "tl1": "將胎<br>軍", "tl2": "攀天<br>鞍德", "sub": "天地<br>哭劫",
        "tr": "<span class='main-star'>天</span><br><span class=\"main-star\">梁</span><br><span class='brightness'>陷</span>",
        "ages": "9 21 33 45 57 69 81 93", "limit": "13---22", "p_name": "兄弟", "br": "木<br>庚<br>寅"
    },
    "丑": {
        "tl1": "奏養<br>書", "tl2": "將白<br>星虎", "sub": "旬天破寡天<br>空壽碎宿刑",
        "tr": "<span class='main-star'>廉</span><br><span class=\"main-star\">貞</span><br><span class='brightness'>廟</span><br><span class='sihua s-ji'>忌</span>",
        "ages": "10 22 34 46 58 70 82 94", "limit": "23---32", "p_name": "夫妻", "br": "土<br>辛<br>丑"
    },
    "子": {
        "tl1": "飛長<br>廉生", "tl2": "亡龍<br>神德", "sub": "天旬天解<br>廚中福神",
        "tr": "<span class='main-star'>巨</span><br><span class=\"main-star\">門</span><br><span class='brightness'>廟旺</span>",
        "ages": "11 23 35 47 59 71 83 95", "limit": "33---42", "p_name": "子女", "br": "土<br>庚<br>子"
    },
    "亥": {
        "tl1": "飛長<br>廉生", "tl2": "亡龍<br>神德", "sub": "紅<br>鸞",
        "tr": "<span class='main-star'>天天</span><br><span class=\"main-star\">同梁</span><br><span class='brightness'>旺旺</span>",
        "ages": "12 24 36 48 60 72 84 96", "limit": "43---52", "p_name": "財帛", "br": "木<br>己<br>亥"
    }
}

# ==========================================
# 3. HTML 網格渲染器
# ==========================================
def render_master_cell(data):
    # 處理流年標記與身宮標記
    liunian_html = "<div class='liu-nian-marker'>2024年<br>甲辰年<br>流年命宮</div>" if data.get('is_liu_nian') else ""
    p_name_display = f"【身】<br>【{data['p_name']}】" if data.get('is_body') else f"【{data['p_name']}】"
    
    return f"""
    <div class="palace-cell">
        <div class="p-tl-group">
            <div class="tl-col">{data['tl1']}</div>
            <div class="tl-col">{data['tl2']}</div>
        </div>
        <div class="p-sub-stars">{data['sub']}</div>
        <div class="p-tr">{data['tr']}</div>
        {liunian_html}
        <div class="p-bl-ages">{data['ages']}</div>
        <div class="p-bl-limit">
            {data['limit']}<br>
            <span class="palace-name">{p_name_display}</span>
        </div>
        <div class="p-br">{data['br']}</div>
    </div>
    """

html_content = f"""
<div class="ziwei-square-board">
    {render_master_cell(full_ziwei_data["巳"])}
    {render_master_cell(full_ziwei_data["午"])}
    {render_master_cell(full_ziwei_data["未"])}
    {render_master_cell(full_ziwei_data["申"])}
    
    {render_master_cell(full_ziwei_data["辰"])}
    
    <div class="center-hall">
        <svg style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:1;">
            <line x1="0" y1="75%" x2="75%" y2="0" stroke="#D32F2F" stroke-width="1.5" />
            <line x1="0" y1="75%" x2="100%" y2="25%" stroke="#D32F2F" stroke-width="1.5" />
            <line x1="0" y1="75%" x2="100%" y2="100%" stroke="#D32F2F" stroke-width="1.5" />
            <line x1="75%" y1="0" x2="100%" y2="25%" stroke="#D32F2F" stroke-width="1" stroke-dasharray="4,4" />
            <line x1="100%" y1="25%" x2="100%" y2="100%" stroke="#D32F2F" stroke-width="1" stroke-dasharray="4,4" />
        </svg>

        <div style="position:relative; z-index:2; font-size:14px; line-height:1.7; color:#000;">
            <div style="color:#D32F2F; font-size:18px; font-weight:bold; margin-bottom:8px;">排盤教學 (對照圖2)</div>
            <table style="width:100%; text-align:left;">
                <tr><td><b>姓名：</b>排盤教學</td><td><b>現在虛歲：</b>48</td></tr>
                <tr><td><b>命造：</b>陽女</td><td><b>生肖：</b>龍</td></tr>
                <tr><td colspan="2"><b>陽曆：</b>1976年6月20日 6時</td></tr>
                <tr><td colspan="2"><b>農曆：</b>1976年5月23日 卯時</td></tr>
                <tr><td colspan="2"><b>農曆四柱：</b>丙辰年 甲午月 癸卯日 乙卯時</td></tr>
                <tr><td><b>命局：</b>木三局</td><td><b>身宮：</b>酉</td></tr>
                <tr><td><b>命主：</b>文曲</td><td><b>身主：</b>文昌</td></tr>
                <tr><td colspan="2"><b>子年斗君：</b>亥</td></tr>
            </table>
            <br>
            <div style="font-weight:bold; color:#1565C0; font-size:15px;">STAR★START<br>從星開始 紫微研究苑</div>
        </div>
    </div>
    
    {render_master_cell(full_ziwei_data["酉"])}
    {render_master_cell(full_ziwei_data["卯"])}
    {render_master_cell(full_ziwei_data["戌"])}
    {render_master_cell(full_ziwei_data["寅"])}
    {render_master_cell(full_ziwei_data["丑"])}
    {render_master_cell(full_ziwei_data["子"])}
    {render_master_cell(full_ziwei_data["亥"])}
</div>
"""

clean_html = re.sub(r'\n\s*', '', html_content)
st.markdown(clean_html, unsafe_allow_html=True)
