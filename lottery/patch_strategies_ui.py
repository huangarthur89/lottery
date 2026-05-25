import re

ui_code_template = """        st.markdown("基於歷史大數據庫，為您自動產生的五組不同策略預測號碼：")
        
        # 1. 歷史最熱門
        all_nums_flat = full_df[['N1', 'N2', 'N3', 'N4', 'N5', 'N6']].values.flatten()
        freq = Counter(all_nums_flat)
        hot_6 = sorted([x[0] for x in freq.most_common(6)])
        
        # 2. 絕地反彈
        max_om_6 = strategy_max_omission(full_df, pool_size={POOL_SIZE})
        
        # 3. 上期拖牌
        trail_6 = strategy_trailing_numbers(full_df, pool_size={POOL_SIZE})
        
        # 4. 完美統計學
        gold_6 = strategy_golden_ratio(pool_size={POOL_SIZE}, min_sum={MIN_SUM}, max_sum={MAX_SUM})
        
        # 5. 連號與連莊組合
        pattern_6 = strategy_pattern_combo(full_df, pool_size={POOL_SIZE})
        
        # 產生特別號 (從前 5 大熱門中隨機挑選)
        special_pool = [n for n, c in Counter(full_df['特別號']).most_common(5)]
        if not special_pool:
            special_pool = list(range(1, 9)) # Fallback
            
        pred_data = [
            ["🔥 歷史最熱門 (出現最多次)", *hot_6, random.choice(special_pool)],
            ["⏳ 絕地反彈 (極限遺漏值選號)", *max_om_6, random.choice(special_pool)],
            ["🎯 上期拖牌 (關聯性預測)", *trail_6, random.choice(special_pool)],
            ["⚖️ 完美統計學 (黃金比例選號)", *gold_6, random.choice(special_pool)],
            ["👯 連號與連莊組合 (型態學選號)", *pattern_6, random.choice(special_pool)],
        ]
        pred_df = pd.DataFrame(pred_data, columns=['策略名稱', '第 1 球', '第 2 球', '第 3 球', '第 4 球', '第 5 球', '第 6 球', '特別號'])
        st.dataframe(pred_df, hide_index=True)
        
        if st.button("🔄 重新產生預測組合"):
            st.rerun()"""

def process_file(file_path, pool_size, min_sum, max_sum):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    start_str = 'st.markdown("請透過下拉選單選擇您想要的 AI 分析模型，系統將動態為您產生下注組合：")'
    end_str = 'st.info("💡 提示：再次點擊按鈕可產生另一組預測 (部分策略帶有隨機性)。")'
    
    start_idx = content.find(start_str)
    end_idx = content.find(end_str) + len(end_str)
    
    if start_idx != -1 and end_idx != -1:
        old_block = content[start_idx:end_idx]
        new_block = ui_code_template.replace('{POOL_SIZE}', str(pool_size)).replace('{MIN_SUM}', str(min_sum)).replace('{MAX_SUM}', str(max_sum))
        content = content.replace(old_block, new_block.strip())
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Patched {file_path}")
    else:
        print(f"Could not find block in {file_path}")

process_file('pages/1_大樂透.py', 49, 130, 170)
process_file('pages/2_威力彩.py', 38, 95, 139)

