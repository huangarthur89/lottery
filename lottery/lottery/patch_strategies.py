import re

strategies_code = """
# --- 進階專家策略函數 ---
def strategy_max_omission(df, pool_size=49):
    gaps = {n: len(df) for n in range(1, pool_size + 1)}
    for n in range(1, pool_size + 1):
        for i, row in df.iterrows():
            draw = [row['N1'], row['N2'], row['N3'], row['N4'], row['N5'], row['N6']]
            if n in draw:
                gaps[n] = i
                break
    sorted_gaps = sorted(gaps.items(), key=lambda x: x[1], reverse=True)
    best_picks = [x[0] for x in sorted_gaps[:6]]
    return sorted(best_picks)

def strategy_trailing_numbers(df, pool_size=49):
    if len(df) < 2:
        return sorted(random.sample(range(1, pool_size + 1), 6))
    last_draw = set([df.iloc[0]['N1'], df.iloc[0]['N2'], df.iloc[0]['N3'], df.iloc[0]['N4'], df.iloc[0]['N5'], df.iloc[0]['N6']])
    next_draw_nums = []
    for i in range(1, len(df) - 1):
        current_draw = set([df.iloc[i]['N1'], df.iloc[i]['N2'], df.iloc[i]['N3'], df.iloc[i]['N4'], df.iloc[i]['N5'], df.iloc[i]['N6']])
        if current_draw.intersection(last_draw):
            next_draw = [df.iloc[i-1]['N1'], df.iloc[i-1]['N2'], df.iloc[i-1]['N3'], df.iloc[i-1]['N4'], df.iloc[i-1]['N5'], df.iloc[i-1]['N6']]
            next_draw_nums.extend(next_draw)
    freq = Counter(next_draw_nums)
    best_picks = [x[0] for x in freq.most_common(6)]
    pool = set(range(1, pool_size + 1)) - set(best_picks)
    while len(best_picks) < 6:
        pick = random.choice(list(pool))
        best_picks.append(pick)
        pool.remove(pick)
    return sorted(best_picks)

def strategy_golden_ratio(pool_size=49, min_sum=130, max_sum=170):
    while True:
        nums = random.sample(range(1, pool_size + 1), 6)
        odd_count = sum(1 for n in nums if n % 2 != 0)
        total_sum = sum(nums)
        if odd_count == 3 and (min_sum <= total_sum <= max_sum):
            return sorted(nums)

def strategy_pattern_combo(df, pool_size=49):
    if df.empty:
        return sorted(random.sample(range(1, pool_size + 1), 6))
    last_draw = [df.iloc[0]['N1'], df.iloc[0]['N2'], df.iloc[0]['N3'], df.iloc[0]['N4'], df.iloc[0]['N5'], df.iloc[0]['N6']]
    repeater = random.choice(last_draw)
    while True:
        start_num = random.randint(1, pool_size - 1)
        pair = [start_num, start_num + 1]
        if repeater not in pair:
            break
    selected_nums = set([repeater] + pair)
    while len(selected_nums) < 6:
        selected_nums.add(random.randint(1, pool_size))
    return sorted(list(selected_nums))
"""

ui_code_template = """        st.markdown("請透過下拉選單選擇您想要的 AI 分析模型，系統將動態為您產生下注組合：")
        
        strategy_choice = st.selectbox("選擇 AI 預測策略：", [
            "🔥 歷史最熱門 (出現最多次的號碼)",
            "⏳ 絕地反彈 (極限遺漏值選號)",
            "🎯 上期拖牌 (關聯性預測)",
            "⚖️ 完美統計學 (黃金比例選號)",
            "👯 連號與連莊組合 (型態學選號)"
        ], label_visibility="collapsed")
        
        if st.button("✨ 產生預測號碼"):
            result_nums = []
            
            if strategy_choice == "🔥 歷史最熱門 (出現最多次的號碼)":
                all_nums_flat = full_df[['N1', 'N2', 'N3', 'N4', 'N5', 'N6']].values.flatten()
                freq = Counter(all_nums_flat)
                result_nums = sorted([x[0] for x in freq.most_common(6)])
            elif strategy_choice == "⏳ 絕地反彈 (極限遺漏值選號)":
                result_nums = strategy_max_omission(full_df, pool_size={POOL_SIZE})
            elif strategy_choice == "🎯 上期拖牌 (關聯性預測)":
                result_nums = strategy_trailing_numbers(full_df, pool_size={POOL_SIZE})
            elif strategy_choice == "⚖️ 完美統計學 (黃金比例選號)":
                result_nums = strategy_golden_ratio(pool_size={POOL_SIZE}, min_sum={MIN_SUM}, max_sum={MAX_SUM})
            elif strategy_choice == "👯 連號與連莊組合 (型態學選號)":
                result_nums = strategy_pattern_combo(full_df, pool_size={POOL_SIZE})
                
            # 產生特別號 (從前 5 大熱門中隨機挑選)
            special_num = random.choice([n for n, c in Counter(full_df['特別號']).most_common(5)])
            
            # 美化輸出
            def format_num(n):
                return f"<span style='font-size: 20px; font-weight:bold;'>{str(n).zfill(2)}</span>"
            def format_sp(n):
                return f"<span style='color:#FF4B4B; font-size: 20px; font-weight:bold;'>{str(n).zfill(2)}</span>"
                
            nums_str = "、".join([format_num(n) for n in result_nums])
            sp_str = format_sp(special_num)
            
            st.success("🎯 AI 運算完成！為您推薦的專屬組合：")
            st.markdown(f"**推薦號碼**： {nums_str} ➕ **特別號**： {sp_str}", unsafe_allow_html=True)
            st.info("💡 提示：再次點擊按鈕可產生另一組預測 (部分策略帶有隨機性)。")"""


def process_file(file_path, pool_size, min_sum, max_sum):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Insert strategies_code after the first block of imports
    if "# --- 設定網頁標題與風格 ---" in content:
        content = content.replace("# --- 設定網頁標題與風格 ---", strategies_code + "\n\n# --- 設定網頁標題與風格 ---")

    # Replace the old UI
    # We find the block starting with '        st.markdown("基於歷史大數據庫，為您自動產生的五組不同策略預測號碼：")'
    # up to '        st.dataframe(pred_df, hide_index=True)'
    
    start_str = 'st.markdown("基於歷史大數據庫，為您自動產生的五組不同策略預測號碼：")'
    end_str = 'st.dataframe(pred_df, hide_index=True)'
    
    start_idx = content.find(start_str)
    end_idx = content.find(end_str) + len(end_str)
    
    if start_idx != -1 and end_idx != -1:
        old_block = content[start_idx:end_idx]
        new_block = ui_code_template.replace('{POOL_SIZE}', str(pool_size)).replace('{MIN_SUM}', str(min_sum)).replace('{MAX_SUM}', str(max_sum))
        content = content.replace(old_block, new_block.strip())
        
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

# Process pages/1_大樂透.py
process_file('pages/1_大樂透.py', 49, 130, 170)

# Process pages/2_威力彩.py
process_file('pages/2_威力彩.py', 38, 95, 139)

