import re
import os
from pathlib import Path

files = [
    "lottery/pages/1_大樂透.py",
    "lottery/pages/2_威力彩.py",
    "pages/3_☯️_命盤_樂透合參.py"
]

for f_path in files:
    try:
        p = Path(f_path)
        if not p.exists(): continue
        content = p.read_text(encoding="utf-8")
        
        # 1. Replace the inline `dream_database = { ... }` with the import
        matches = list(re.finditer(r"([ \t]*)dream_database\s*=\s*\{", content))
        if matches:
            for match in matches:
                start_idx = match.start()
                indent = match.group(1)
                brace_count = 0
                end_idx = -1
                in_string = False
                escape = False
                start_search = start_idx + len(indent) + len("dream_database = {")
                
                for i in range(start_search, len(content)):
                    c = content[i]
                    if escape:
                        escape = False
                        continue
                    if c == "\\":
                        escape = True
                        continue
                    if c in ('"', "'"):
                        if not in_string:
                            in_string = c
                        elif in_string == c:
                            in_string = False
                    if not in_string:
                        if c == "{":
                            brace_count += 1
                        elif c == "}":
                            if brace_count == 0:
                                end_idx = i
                                break
                            brace_count -= 1
                
                if end_idx != -1:
                    replacement = f"{indent}import sys\n{indent}from pathlib import Path\n{indent}sys.path.insert(0, str(Path(__file__).resolve().parents[2]))\n{indent}from dream_dict import dream_database\n"
                    if "pages/3_" in f_path:
                        replacement = f"{indent}import sys\n{indent}from pathlib import Path\n{indent}sys.path.insert(0, str(Path(__file__).resolve().parents[1]))\n{indent}from dream_dict import dream_database\n"
                    
                    content = content[:start_idx] + replacement + content[end_idx+1:]
                    break # Just replace the first occurrence
                    
        # 2. Replace the logic block
        # Look for `for kw_tuple, nums in dream_database.items():`
        # and replace up to `extracted_numbers.update(nums)` and keyword loops
        logic_pattern = r"([ \t]*)for kw_tuple, nums in dream_database\.items\(\):[\s\S]*?(?=valid_base_nums =|final_raw =|st\.success)"
        
        def replacer_logic(match):
            indent = match.group(1)
            new_logic = f"""{indent}matched_descs = []
{indent}for kw_tuple, data in dream_database.items():
{indent}    nums = data['nums']
{indent}    desc = data['desc']
{indent}    
{indent}    matched_kws = [k for k in kw_tuple if k in user_input_lower]
{indent}    if matched_kws:
{indent}        extracted_numbers.update(nums)
{indent}        for k in matched_kws:
{indent}            if k not in keywords:
{indent}                keywords.append(k)
{indent}        desc_text = f"**{{', '.join(matched_kws)}}**：{{desc}}"
{indent}        if desc_text not in matched_descs:
{indent}            matched_descs.append(desc_text)
{indent}            
{indent}"""
            return new_logic
            
        content = re.sub(logic_pattern, replacer_logic, content)
        
        # 3. Add markdown display after st.success
        # To avoid regex quote issues, find `st.success(...)` and insert after it.
        # We find `st.success(` and then find its closing parenthesis.
        idx = 0
        while True:
            idx = content.find("st.success(", idx)
            if idx == -1: break
            
            # check if it's the right st.success
            if "捕捉到夢境關鍵字" not in content[idx:idx+100]:
                idx += 1
                continue
                
            # Find the start of the line to get indentation
            line_start = content.rfind("\n", 0, idx)
            indent_str = content[line_start+1:idx]
            if not indent_str.isspace():
                indent_str = "                "
                
            # Find matching parenthesis
            p_count = 0
            end_p = -1
            in_str = False
            esc = False
            for i in range(idx, len(content)):
                c = content[i]
                if esc:
                    esc = False
                    continue
                if c == "\\":
                    esc = True
                    continue
                if c in ('"', "'"):
                    if not in_str: in_str = c
                    elif in_str == c: in_str = False
                if not in_str:
                    if c == "(": p_count += 1
                    elif c == ")":
                        p_count -= 1
                        if p_count == 0:
                            end_p = i
                            break
            
            if end_p != -1:
                # Insert the markdown loop after this line
                insert_str = f"\n{indent_str}if matched_descs:\n{indent_str}    st.markdown(\"### 📖 夢境深度解析\")\n{indent_str}    for d in matched_descs:\n{indent_str}        st.markdown(f\"> 💡 {{d}}\")\n"
                content = content[:end_p+1] + insert_str + content[end_p+1:]
                idx = end_p + len(insert_str)
            else:
                idx += 1
                
        # Also fix any syntax errors I might have introduced in pages/3_
        # If there is `st.success(f"🔍 **捕捉到夢境關鍵字**： {', '.join(keywords) if keywords else '無 (將完全依賴八字與大數據)'}")` that was broken, let's fix it manually.
        broken_str = "st.success(f\"🔍 **捕捉到夢境關鍵字**： {', '.join(keywords)\n                if matched_descs:"
        if broken_str in content:
            content = content.replace(broken_str, "st.success(f\"🔍 **捕捉到夢境關鍵字**： {', '.join(keywords) if keywords else '無 (將完全依賴八字與大數據)'}\")\n                if matched_descs:")
            
        p.write_text(content, encoding="utf-8")
        print(f"Successfully processed {f_path}")
        
    except Exception as e:
        print(f"Error on {f_path}: {e}")
