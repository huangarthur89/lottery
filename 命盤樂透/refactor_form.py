import os

filepath = "/Volumes/MSI 2T/Antigravity/阿舍AI/命盤樂透/pages/1_命盤分析.py"

with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find the start of Section 3 and Section 4
sec3_start = -1
sec4_start = -1

for i, line in enumerate(lines):
    if line.startswith("# 3. 側邊欄控制台"):
        sec3_start = i - 1  # include the # ====== line above it
    if line.startswith("# 4. 資料生成與排盤佈局"):
        sec4_start = i - 1  # include the # ====== line above it

if sec3_start != -1 and sec4_start != -1:
    top_part = lines[:sec3_start]
    
    # Locate where the actual data generation starts in section 4
    data_gen_start = -1
    for i in range(sec4_start, len(lines)):
        if "lunar = Solar.fromYmdHms" in lines[i]:
            data_gen_start = i
            break
            
    if data_gen_start != -1:
        bottom_part = lines[data_gen_start:]
        
        new_sec3_4 = """# ==========================================
# 3. 側邊欄控制台 (使用 Form 封裝，防止輸入時畫面刷新)
# ==========================================
with st.sidebar:
    # 👇 關鍵 1：建立一個名為 astro_form 的表單保護罩
    with st.form("astro_form"):
        st.markdown("### 🔮 天體與大師校正面板")
        name = st.text_input("命主", "匿名")
        gender = st.radio("性別", ["乾造 (男)", "坤造 (女)"])
        gender_int = 1 if "男" in gender else 0
        
        min_d = date(1930, 1, 1)
        max_d = date.today() + timedelta(days=90)
        
        b_date = st.date_input(
            "公曆出生日", 
            value=date(1971, 1, 1),
            min_value=min_d,
            max_value=max_d
        )
        b_time = st.time_input("公曆出生時", datetime(1971, 1, 1, 0, 0).time())
        
        st.markdown("---")
        st.markdown("#### 🧭 天文地理校正")
        
        city_coords = {
            "基隆": (121.74, 25.13), "台北": (121.50, 25.05), "新北": (121.46, 25.01),
            "桃園": (121.30, 24.99), "新竹": (120.96, 24.81), "苗栗": (120.82, 24.56),
            "台中": (120.67, 24.14), "彰化": (120.54, 24.07), "南投": (120.68, 23.90),
            "雲林": (120.43, 23.70), "嘉義": (120.44, 23.48), "台南": (120.20, 22.99),
            "高雄": (120.30, 22.62), "屏東": (120.48, 22.67), "宜蘭": (121.75, 24.75),
            "花蓮": (121.60, 23.97), "台東": (121.14, 22.75), "澎湖": (119.56, 23.56),
            "金門": (118.31, 24.43), "馬祖": (119.93, 26.15)
        }
        
        city_list = list(city_coords.keys())
        selected_city = st.selectbox("出生城市", city_list, index=city_list.index("台北"))
        zi_hour_rule = st.selectbox("子時換日排法", ["早晚子時區分", "一律換日"])

        st.markdown("---")
        # 👇 關鍵 2：把原本的 st.button 換成表單專屬的 st.form_submit_button
        generate_btn = st.form_submit_button("🚀 生成專屬命盤解析", use_container_width=True)

    # 隱藏相容性變數，避免破壞後續判斷 (放在表單外)
    time_mode = "✅ 知道精確時間"
    tz_offset = 8.0

# ==========================================
# 4. 資料生成與排盤佈局
# ==========================================
if generate_btn:
    # 👇 關鍵 3：將真太陽時的計算與提示框，移到按下按鈕後才執行顯示
    longitude, latitude = city_coords[selected_city]
    true_datetime, total_offset, eot = calculate_true_solar_time(b_date, b_time, longitude)
    
    with st.sidebar:
        st.info(f"經度差: {total_offset-eot:.1f} 分\\n\\n均時差: {eot:.1f} 分\\n\\n**真太陽時:**\\n{true_datetime.strftime('%Y-%m-%d %H:%M:%S')}")

    with st.spinner("🌌 正在為您精算天體運行與命盤參數..."):
"""
        indented_bottom = []
        for line in bottom_part:
            if line.strip() == "":
                indented_bottom.append(line)
            else:
                indented_bottom.append("        " + line)
                
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(top_part)
            f.write(new_sec3_4)
            f.writelines(indented_bottom)
        print("File updated successfully.")
    else:
        print("data_gen_start not found")
else:
    print("section 3 or 4 not found")
