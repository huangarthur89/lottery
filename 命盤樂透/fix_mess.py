import os

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

def fix(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace all occurrences back to "import random"
    content = content.replace("import random\n" + func_str, "import random")
    
    # Ensure there is exactly ONE occurrence at the top
    # The first "import random" should be the one at the top.
    content = content.replace("import random", "import random\n" + func_str, 1)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

base_dir = "/Volumes/MSI 2T/Antigravity/阿舍AI/命盤樂透/lottery/pages"
fix(f"{base_dir}/1_大樂透.py")
fix(f"{base_dir}/2_威力彩.py")
