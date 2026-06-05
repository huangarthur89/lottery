import streamlit as st
from datetime import datetime
from lunar_python import Solar
from saju import calculate_saju
from ziwei import build_ziwei_chart, transform_badges

# ==========================================
# 1. 專業級星曜與宮位排版引擎
# ==========================================
def get_pro_max_chart(year, month, day, hour, minute, name, gender_text):
    ziwei_chart = build_ziwei_chart(year, month, day, hour, minute, gender_text)
    chart = calculate_saju(year, month, day, hour, minute, gender="M" if "男" in gender_text else "F", timezone_name="Asia/Taipei")

    palaces_data = {}
    for branch, palace in ziwei_chart["palaces"].items():
        palaces_data[branch] = {
            "宮位": palace["宮位"],
            "大限": palace["大限"],
            "宮干": palace["宮干"],
            "主星": palace["主星"] or "--",
            "吉煞": palace["吉煞"],
            "四化": transform_badges(palace.get("四化文字", "")),
            "副星": palace["副星"],
            "博士": palace["博士"],
            "長生": palace["長生"],
            "歲建": palace["歲建"],
        }

    return {
        "name": name,
        "gender": gender_text,
        "nature": ziwei_chart["nature"],
        "body_palace": f"{ziwei_chart['body_branch']}宮",
        "true_time": f"{year}年{month:02d}月{day:02d}日 {hour:02d}:{minute:02d}",
        "lunar_txt": ziwei_chart["lunar_txt"],
        "four_pillars": [
            {"label": "年柱", "st": chart.year_pillar[0], "br": chart.year_pillar[1]},
            {"label": "月柱", "st": chart.month_pillar[0], "br": chart.month_pillar[1]},
            {"label": "日柱", "st": chart.day_pillar[0], "br": chart.day_pillar[1]},
            {"label": "時柱", "st": chart.hour_pillar[0], "br": chart.hour_pillar[1]},
        ],
        "palaces": palaces_data,
        "algorithm_note": ziwei_chart["algorithm_note"],
    }

# ==========================================
# 2. 高仿真排盤軟體視覺 CSS 注入
# ==========================================
st.set_page_config(page_title="專業商用級·八紫合參天盤", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F4F5F7; color: #333333; }
    
    /* 仿照文墨天機的標準宮位方格 */
    .pro-palace-box {
        border: 1px solid #999999;
        height: 185px;
        background-color: #FFFFFF;
        padding: 6px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        position: relative;
    }
    
    /* 內部小星群左右分流排版 */
    .p-top-row { display: flex; justify-content: space-between; font-size: 0.75rem; color: #666666; }
    .p-middle-row { display: flex; justify-content: space-between; margin-top: 5px; height: 95px; }
    
    .left-stars { display: flex; flex-direction: column; text-align: left; font-size: 0.8rem; color: #C62828; font-weight: bold; }
    .right-stars { display: flex; flex-direction: column; text-align: right; font-size: 1.15rem; font-weight: bold; color: #1A237E; }
    .sub-stars-area { font-size: 0.7rem; color: #555555; text-align: left; line-height: 1.2; margin-top: auto; }
    
    .p-bottom-row { display: flex; justify-content: space-between; font-size: 0.95rem; font-weight: bold; border-top: 1px solid #E0E0E0; padding-top: 3px; }
    
    /* 專業四化小方塊 */
    .badge-zw { padding: 1px 3px; border-radius: 2px; color: #FFFFFF; font-size: 0.7rem; font-weight: bold; display: inline-block; margin-top: 2px; }
    .m-lu { background-color: #2E7D32; }
    .m-quan { background-color: #6A1B9A; }
    .m-ke { background-color: #1565C0; }
    .m-ji { background-color: #C62828; }

    /* 中堂佈局 */
    .center-hall-pro {
        border: 2px solid #555555;
        height: 390px;
        background-color: #FFFFFF;
        padding: 12px;
        position: relative;
    }
    .bazi-inline-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    .bazi-cell { text-align: center; padding: 4px; border: 1px solid #E0E0E0; }
    .bz-st { font-size: 1.6rem; font-weight: bold; color: #00695C; }
    .bz-br { font-size: 1.6rem; font-weight: bold; color: #D84315; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 側邊欄與資料載入
# ==========================================
with st.sidebar:
    st.markdown("### 🔮 大師排盤控制台")
    name = st.text_input("姓名", "排盤教學")
    gender = st.radio("命造屬性", ["陽女", "陰女", "陽男", "陰男"])
    b_date = st.date_input("出生日期", datetime(1976, 6, 20))
    b_time = st.time_input("出生時間", datetime(1976, 6, 20, 6, 0).time())

res = get_pro_max_chart(b_date.year, b_date.month, b_date.day, b_time.hour, b_time.minute, name, gender)

# ==========================================
# 4. 4x4 方格渲染（左吉右主、小星繞邊）
# ==========================================
def render_pro_cell(key):
    p = res["palaces"][key]
    return f"""
    <div class="pro-palace-box">
        <div class="p-top-row">
            <span>{p['博士']} {p['長生']} {p['歲建']}</span>
            <span style="color:#1565C0; font-weight:bold;">{p['大限']}</span>
        </div>
        <div class="p-middle-row">
            <div class="left-stars">
                <span>{p['吉煞']}</span>
                {p['四化']}
            </div>
            <div class="right-stars">
                {p['主星'].replace(' ', '<br>')}
            </div>
        </div>
        <div class="sub-stars-area">{p['副星']}</div>
        <div class="p-bottom-row">
            <span style="color:#C62828;">【{p['宮位']}】</span>
            <span style="color:#333333;">{p['宮干']}</span>
        </div>
    </div>
    """

# --- 第一排：巳、午、未、申 ---
r1 = st.columns(4)
with r1[0]: st.markdown(render_pro_cell("巳"), unsafe_allow_html=True)
with r1[1]: st.markdown(render_pro_cell("午"), unsafe_allow_html=True)
with r1[2]: st.markdown(render_pro_cell("未"), unsafe_allow_html=True)
with r1[3]: st.markdown(render_pro_cell("申"), unsafe_allow_html=True)

# --- 第二排：辰、中堂、酉 ---
r2 = st.columns([1, 2, 1])
with r2[0]:
    st.markdown(render_pro_cell("辰"), unsafe_allow_html=True)
    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    st.markdown(render_pro_cell("卯"), unsafe_allow_html=True)

with r2[1]:
    # 完美還原第二張圖的中堂資訊卡排版
    st.markdown(f"""
        <div class="center-hall-pro">
            <div style="text-align:center; font-weight:bold; font-size:1.1rem; letter-spacing:2px;">從星開始 紫微研究苑</div>
            <hr style="margin:6px 0;">
            <div style="font-size:0.85rem; line-height:1.5; padding-left:10px;">
                <b>姓名：</b> {res['name']} &nbsp;&nbsp;&nbsp;&nbsp; <b>命造：</b> {res['gender']}<br>
                <b>陽曆：</b> {res['true_time']} &nbsp;&nbsp;&nbsp;&nbsp; <b>局數：</b> {res['nature']}<br>
                <b>農曆：</b> {res['lunar_txt']} &nbsp;&nbsp;&nbsp;&nbsp; <b>身宮：</b> {res['body_palace']}
            </div>
            
            <table class="bazi-inline-table">
                <tr>
                    <td class="bazi-cell" style="color:#666666;">{res['four_pillars'][3]['label']}</td>
                    <td class="bazi-cell" style="color:#666666;">{res['four_pillars'][2]['label']}</td>
                    <td class="bazi-cell" style="color:#666666;">{res['four_pillars'][1]['label']}</td>
                    <td class="bazi-cell" style="color:#666666;">{res['four_pillars'][0]['label']}</td>
                </tr>
                <tr>
                    <td class="bazi-cell bz-st">{res['four_pillars'][3]['st']}</td>
                    <td class="bazi-cell bz-st">{res['four_pillars'][2]['st']}</td>
                    <td class="bazi-cell bz-st">{res['four_pillars'][1]['st']}</td>
                    <td class="bazi-cell bz-st">{res['four_pillars'][0]['st']}</td>
                </tr>
                <tr>
                    <td class="bazi-cell bz-br">{res['four_pillars'][3]['br']}</td>
                    <td class="bazi-cell bz-br">{res['four_pillars'][2]['br']}</td>
                    <td class="bazi-cell bz-br">{res['four_pillars'][1]['br']}</td>
                    <td class="bazi-cell bz-br">{res['four_pillars'][0]['br']}</td>
                </tr>
            </table>
            
            <canvas id="canvas-lines" width="400" height="150" style="position:absolute; bottom:5px; left:20px; pointer-events:none;"></canvas>
        </div>
    """, unsafe_allow_html=True)

with r2[2]:
    st.markdown(render_pro_cell("酉"), unsafe_allow_html=True)
    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    st.markdown(render_pro_cell("戌"), unsafe_allow_html=True)

# --- 第四排：寅、丑、子、亥 ---
r4 = st.columns(4)
with r4[0]: st.markdown(render_pro_cell("寅"), unsafe_allow_html=True)
with r4[1]: st.markdown(render_pro_cell("丑"), unsafe_allow_html=True)
with r4[2]: st.markdown(render_pro_cell("子"), unsafe_allow_html=True)
with r4[3]: st.markdown(render_pro_cell("亥"), unsafe_allow_html=True)

# 注入三方四正的動態紅線 JavaScript 特效
st.components.v1.html("""
<script>
    window.addEventListener('load', function() {
        var canvas = window.parent.document.getElementById('canvas-lines');
        if(canvas) {
            var ctx = canvas.getContext('2d');
            ctx.strokeStyle = '#E53935';
            ctx.lineWidth = 1.5;
            // 繪製對角會合與官祿財帛交會的淡紅色三角網絡
            ctx.beginPath();
            ctx.moveTo(30, 20);
            ctx.lineTo(370, 20);
            ctx.lineTo(200, 130);
            ctx.closePath();
            ctx.stroke();
        }
    });
</script>
""", height=0)
