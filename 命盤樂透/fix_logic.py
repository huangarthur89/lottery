import os
from pathlib import Path

files = [
    "lottery/pages/1_大樂透.py",
    "lottery/pages/2_威力彩.py",
]

for f_path in files:
    content = Path(f_path).read_text(encoding="utf-8")
    
    # We will search for `dream_dict = {`
    idx = 0
    while True:
        idx = content.find("dream_dict = {", idx)
        if idx == -1: break
        
        # Find the indentation
        line_start = content.rfind("\n", 0, idx)
        indent = content[line_start+1:idx]
        
        # Now find `if dream_nums:` after this, because the block we want to replace ends right BEFORE `if dream_nums:`
        end_idx = content.find(f"\n{indent}if dream_nums:", idx)
        if end_idx == -1:
            # Let's try `st.write(f"💭 `
            end_idx = content.find(f"st.write(f\"💭", idx)
            end_idx = content.rfind("\n", 0, end_idx)
        
        if end_idx != -1:
            pool_limit = "49" if "1_" in f_path else "38"
            
            logic = f"""
{indent}import sys
{indent}from pathlib import Path
{indent}sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
{indent}from dream_dict import dream_database

{indent}if not dream_text:
{indent}    st.warning("請先輸入您的夢境內容！")
{indent}    st.stop()
{indent}else:
{indent}    extracted_numbers = set()
{indent}    keywords = []
{indent}    matched_descs = []
{indent}    user_input_lower = dream_text.lower()
{indent}    
{indent}    for kw_tuple, data in dream_database.items():
{indent}        nums = data['nums']
{indent}        desc = data['desc']
{indent}        matched_kws = [k for k in kw_tuple if k in user_input_lower]
{indent}        if matched_kws:
{indent}            extracted_numbers.update(nums)
{indent}            for k in matched_kws:
{indent}                if k not in keywords:
{indent}                    keywords.append(k)
{indent}            desc_text = f"**{{', '.join(matched_kws)}}**：{{desc}}"
{indent}            if desc_text not in matched_descs:
{indent}                matched_descs.append(desc_text)
{indent}                
{indent}    dream_nums = list(set([n for n in extracted_numbers if 1 <= n <= {pool_limit}]))
{indent}    
{indent}    st.success(f"🔍 **捕捉到夢境關鍵字**： {{', '.join(keywords) if keywords else '無 (將完全依賴大數據預測)'}}")
{indent}    if matched_descs:
{indent}        st.markdown("### 📖 夢境深度解析")
{indent}        for d in matched_descs:
{indent}            st.markdown(f"> 💡 {{d}}")
"""
            content = content[:line_start] + logic + content[end_idx:]
            idx = line_start + len(logic)
        else:
            idx += 1
            
    Path(f_path).write_text(content, encoding="utf-8")
    print(f"Fixed {f_path}")
