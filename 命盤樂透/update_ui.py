import re
import os
from pathlib import Path

files = [
    "lottery/pages/1_大樂透.py",
    "lottery/pages/2_威力彩.py",
    "pages/3_☯️_命盤_樂透合參.py"
]

target_old1 = r"for kw_tuple, nums in dream_database\.items\(\):"
target_new1 = """matched_descs = []
                for kw_tuple, data in dream_database.items():
                    nums = data['nums']
                    desc = data['desc']
                    
                    matched_kws = [k for k in kw_tuple if k in user_input_lower]
                    if matched_kws:
                        extracted_numbers.update(nums)
                        for k in matched_kws:
                            if k not in keywords:
                                keywords.append(k)
                        desc_text = f"**{', '.join(matched_kws)}**：{desc}"
                        if desc_text not in matched_descs:
                            matched_descs.append(desc_text)"""

for f_path in files:
    try:
        p = Path(f_path)
        if not p.exists(): continue
        content = p.read_text(encoding="utf-8")
        
        # Replace the loop
        # We need to replace the loop carefully.
        # Find `for kw_tuple, nums in dream_database.items():` to the end of the `if any(...)` block
        pattern = r"([ \t]*)for kw_tuple, nums in dream_database\.items\(\):.*?(?=\n[ \t]*valid_base_nums|\n[ \t]*st\.success)"
        
        def replacer(match):
            indent = match.group(1)
            new_block = f"""{indent}matched_descs = []
{indent}for kw_tuple, data in dream_database.items():
{indent}    nums = data['nums']
{indent}    desc = data['desc']
{indent}    matched_kws = [k for k in kw_tuple if k in user_input_lower]
{indent}    if matched_kws:
{indent}        extracted_numbers.update(nums)
{indent}        for k in matched_kws:
{indent}            if k not in keywords:
{indent}                keywords.append(k)
{indent}        desc_text = f"**{{', '.join(matched_kws)}}**：{{desc}}"
{indent}        if desc_text not in matched_descs:
{indent}            matched_descs.append(desc_text)
"""
            return new_block
            
        content = re.sub(pattern, replacer, content, flags=re.DOTALL)
        
        # Now insert the markdown display after st.success
        pattern2 = r"([ \t]*)(st\.success\(f?[\"'].*?捕捉到夢境關鍵字.*?[\"'].*?\))"
        def replacer2(match):
            indent = match.group(1)
            success_call = match.group(2)
            new_block = f"""{indent}{success_call}
{indent}if matched_descs:
{indent}    for d in matched_descs:
{indent}        st.markdown(f"> 💡 {{d}}")"""
            return new_block
            
        content = re.sub(pattern2, replacer2, content)
        
        p.write_text(content, encoding="utf-8")
        print(f"Replaced loop and UI in {f_path}")
    except Exception as e:
        print(e)
