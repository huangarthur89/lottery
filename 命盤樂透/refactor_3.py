import os
import re

def refactor(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Move `parse_dream_to_numbers` and `expand_dream_resonance` to the top.
    # Extract them from the bottom.
    pattern_funcs = r"(# ==========================================\n# 4\. 旗艦版：台灣本土夢境逼牌解碼引擎\n# ==========================================\n.*)(dream_input = st\.text_input\(\"💭 輸入您的夢境)"
    
    match = re.search(pattern_funcs, content, flags=re.DOTALL)
    if match:
        funcs_str = match.group(1)
        # Remove it from bottom, also remove the old dream UI logic
        content = content[:match.start()]
        
        # Insert funcs_str after `import re`
        content = content.replace("import re\n", "import re\n\n" + funcs_str + "\n\n", 1)
    
    # 2. Add the Dream Input UI and integrate logic
    # Find `generate_btn = st.button("🚀 執行多維度合參運算", use_container_width=True)`
    # And replace it with the new UI and logic
    
    old_btn_logic = """    st.info(f"**本命五行：** {day_master} ({day_element})\\n**生命靈數：** {life_path}\\n**旺運尾數：** {self_tails}")
    generate_btn = st.button("🚀 執行多維度合參運算", use_container_width=True)

# 載入分流資料
freq_data, overdue_data, zone2_data, db_connected = load_game_lottery_stats(game_choice)

def get_current_wealth_tail():
    y = datetime.now().year
    # 簡易九宮飛星財星推算
    # 8白星在 2026 為財，透過年份餘數動態推算
    base = 8
    offset = (y - 2026) % 9
    return (base - offset) % 9 if (base - offset) % 9 != 0 else 9

# ==========================================
# 3. 核心雙遊戲計分矩陣
# ==========================================
if generate_btn:
    is_lotto = "大樂透" in game_choice
    max_num = 49 if is_lotto else 38
    all_nums = list(range(1, max_num + 1))
    
    scores = {}"""

    new_btn_logic = """    st.info(f"**本命五行：** {day_master} ({day_element})\\n**生命靈數：** {life_path}\\n**旺運尾數：** {self_tails}")
    
    st.markdown("---")
    st.markdown("### 💭 潛意識逼牌解碼 (選填)")
    dream_input = st.text_area("請簡述您近期的夢境或強烈直覺：", placeholder="例如：我夢到好多鈔票被小偷拿走...")

    generate_btn = st.button("🚀 執行多維度合參運算", use_container_width=True)

# 載入分流資料
freq_data, overdue_data, zone2_data, db_connected = load_game_lottery_stats(game_choice)

def get_current_wealth_tail():
    y = datetime.now().year
    # 簡易九宮飛星財星推算
    # 8白星在 2026 為財，透過年份餘數動態推算
    base = 8
    offset = (y - 2026) % 9
    return (base - offset) % 9 if (base - offset) % 9 != 0 else 9

# ==========================================
# 3. 核心雙遊戲計分矩陣
# ==========================================
if generate_btn:
    is_lotto = "大樂透" in game_choice
    max_num = 49 if is_lotto else 38
    all_nums = list(range(1, max_num + 1))
    
    dream_nums_for_engine = []
    if dream_input:
        base_nums = parse_dream_to_numbers(dream_input)
        valid_base_nums = [n for n in base_nums if 1 <= n <= max_num]
        dream_nums_for_engine = [n for n in expand_dream_resonance(dream_input, valid_base_nums, max_num) if 1 <= n <= max_num]
        
        if dream_nums_for_engine:
            st.success(f"🔮 潛意識共振捕捉成功！已將號碼注入運算核心：{', '.join(map(str, dream_nums_for_engine))}")
        else:
            st.warning("暫無捕捉到強烈靈動數字，將以純命理與大數據為您推演。")
    
    scores = {}"""

    content = content.replace(old_btn_logic, new_btn_logic)

    # 3. Add Dream Bonus to `scores` calculation
    old_score_calc = """        # 維度三：生命靈數共振 (Max 30)
        if n == life_path or sum(int(d) for d in str(n)) == life_path or tail == life_path:
            score += 20
        elif n % life_path == 0:
            score += 10
            
        scores[n] = round(score, 1)"""

    new_score_calc = """        # 維度三：生命靈數共振 (Max 30)
        if n == life_path or sum(int(d) for d in str(n)) == life_path or tail == life_path:
            score += 20
        elif n % life_path == 0:
            score += 10
            
        # ==========================================
        # 🌌 核心植入：夢境靈數強制共振加權
        # ==========================================
        if dream_nums_for_engine and n in dream_nums_for_engine:
            score += 50  # 超級權重，強勢擠進前段班
            
        scores[n] = round(score, 1)"""

    content = content.replace(old_score_calc, new_score_calc)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

base_dir = "/Volumes/MSI 2T/Antigravity/阿舍AI/命盤樂透/pages"
refactor(f"{base_dir}/3_命盤_樂透合參.py")
