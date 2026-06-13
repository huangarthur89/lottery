import os
import re

func_str = """
import re

def expand_dream_resonance(user_input, base_numbers, max_num=49):
    expanded_set = set(base_numbers)
    arabic_matches = re.findall(r'\\d+', user_input)
    for num_str in arabic_matches:
        num = int(num_str)
        if 1 <= num <= max_num:
            expanded_set.add(num)
            
    chinese_num_map = {"一": 1, "二": 2, "兩": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
    for char in user_input:
        if char in chinese_num_map:
            expanded_set.add(chinese_num_map[char])

    current_numbers = list(expanded_set)
    for num in current_numbers:
        if num > 9:
            rev_num = int(str(num)[::-1])
            if 1 <= rev_num <= max_num:
                expanded_set.add(rev_num)
        if num > 9:
            sum_num = sum(int(digit) for digit in str(num))
            if 1 <= sum_num <= max_num:
                expanded_set.add(sum_num)
        if num < 10:
            if num - 1 >= 1: expanded_set.add(num - 1)
            if num + 1 <= max_num: expanded_set.add(num + 1)
            
    return sorted(list(expanded_set))
"""

def update_file(filepath, max_num):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # insert the function at the top
    if "def expand_dream_resonance" not in content:
        content = content.replace("import random", "import random\n" + func_str)

    # replace block 1
    pattern1 = r"(dream_nums = list\(set\(\[n for n in extracted_numbers if 1 <= n <= \d+\]\)\)\s*st\.success\(f\"🔍 \*\*捕捉到夢境關鍵字\*\*： \{', '\.join\(keywords\) if keywords else '無 \(將完全依賴八字與大數據\)'\}\"\)\s*if dream_nums:\s*st\.write\(f\"💭 \*\*字典初始轉化號碼\*\*： \{sorted\(dream_nums\)\}\"\))"
    
    rep1 = f"""valid_base_nums = list(set([n for n in extracted_numbers if 1 <= n <= {max_num}]))
                final_raw = expand_dream_resonance(dream_text, valid_base_nums, {max_num})
                dream_nums = [n for n in final_raw if 1 <= n <= {max_num}]
                
                st.success(f"🔍 **捕捉到夢境關鍵字**： {{', '.join(keywords) if keywords else '無 (將完全依賴八字與大數據)'}}")
                if valid_base_nums:
                    st.write(f"💭 **字典初始轉化號碼**： {{sorted(valid_base_nums)}}")
                if dream_nums:
                    st.info(f"🌌 **靈數共振擴張後**： {{dream_nums}}")"""
                    
    content = re.sub(pattern1, rep1, content)
    
    # replace block 2
    pattern2 = r"(dream_nums = list\(\{n for n in extracted_numbers if 1 <= n <= \d+\}\)\s*st\.success\(f\"🔍 捕捉到夢境關鍵字：\{', '\.join\(matched_keywords\) if matched_keywords else '無 \(將全數使用熱門數據推薦\)'\}\"\)\s*st\.write\(f\"💭 夢境轉化號碼：\{dream_nums if dream_nums else '無'\}\"\))"

    rep2 = f"""valid_base_nums = list(set([n for n in extracted_numbers if 1 <= n <= {max_num}]))
                final_raw = expand_dream_resonance(dream_text, valid_base_nums, {max_num})
                dream_nums = [n for n in final_raw if 1 <= n <= {max_num}]
                
                st.success(f"🔍 捕捉到夢境關鍵字：{{', '.join(matched_keywords) if matched_keywords else '無 (將全數使用熱門數據推薦)'}}")
                st.write(f"💭 字典初始轉化號碼：{{valid_base_nums if valid_base_nums else '無'}}")
                st.info(f"🌌 靈數共振擴張後：{{dream_nums if dream_nums else '無'}}")"""

    content = re.sub(pattern2, rep2, content)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

base_dir = "/Volumes/MSI 2T/Antigravity/阿舍AI/命盤樂透/lottery/pages"
update_file(f"{base_dir}/1_大樂透.py", 49)
update_file(f"{base_dir}/2_威力彩.py", 38)
