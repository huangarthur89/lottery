import os
import re

def fix_file(filepath, is_49):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    pattern1 = r"(\s+if any\(k in user_input_lower for k in kw_tuple\):)[\s\n]+extracted_numbers\.update\(nums\)[\s\n]+for k in kw_tuple:[\s\n]+if k in user_input_lower and k not in keywords:[\s\n]+keywords\.append\(k\)[\s\n]+dream_nums = list\(set\(\[n for n in extracted_numbers if 1 <= n <= \d+\]\)\)"
    
    max_num = 49 if is_49 else 38
    
    replacement1 = f"""\\1
                        extracted_numbers.update(nums)
                        for k in kw_tuple:
                            if k in user_input_lower and k not in keywords:
                                keywords.append(k)
                                
                dream_nums = list(set([n for n in extracted_numbers if 1 <= n <= {max_num}]))"""
                
    content = re.sub(pattern1, replacement1, content)
    
    pattern2 = r"(\s+if any\(k in user_input_lower for k in kw_tuple\):)[\s\n]+extracted_numbers\.update\(nums\)[\s\n]+for k in kw_tuple:[\s\n]+if k in user_input_lower and k not in matched_keywords:[\s\n]+matched_keywords\.append\(k\)[\s\n]+dream_nums = list\(\{n for n in extracted_numbers if 1 <= n <= \d+\}\)"
    
    replacement2 = f"""\\1
                        extracted_numbers.update(nums)
                        for k in kw_tuple:
                            if k in user_input_lower and k not in matched_keywords:
                                matched_keywords.append(k)
                
                dream_nums = list({{n for n in extracted_numbers if 1 <= n <= {max_num}}})"""
                
    content = re.sub(pattern2, replacement2, content)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Fixed {filepath}")

base_dir = "/Volumes/MSI 2T/Antigravity/阿舍AI/命盤樂透/lottery/pages"
fix_file(f"{base_dir}/1_大樂透.py", True)
fix_file(f"{base_dir}/2_威力彩.py", False)
