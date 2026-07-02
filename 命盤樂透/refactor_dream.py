import re
from pathlib import Path

files = [
    "lottery/pages/1_大樂透.py",
    "lottery/pages/2_威力彩.py"
]

# We want to replace the `dream_dict = { ... }` block AND the `if not dream_text: ... else: ... sorted_keys ...` logic with the new logic.

# In the pristine files, there are TWO `dream_dict = {` occurrences.
# We will find each occurrence, find its matching closing brace `}`, and replace it and the subsequent parsing logic.

for f_path in files:
    content = Path(f_path).read_text(encoding="utf-8")
    
    # We will do a generic replacement by finding `dream_dict = {` and `st.success(f"🔍 **捕捉到夢境關鍵字**`
    # and replacing everything in between.
    
    # We need to do this carefully.
    
    pattern = r"([ \t]*)dream_dict\s*=\s*\{[\s\S]*?st\.success\(f?[\"'].*?捕捉到夢境關鍵字.*?[\"'].*?\)"
    
    def replacer(match):
        indent = match.group(1)
        
        pool_limit = "49"
        if "2_威力彩" in f_path:
            pool_limit = "38"
            
        is_tab6 = "if not full_df.empty:" in content[match.end():match.end()+500]
        
        # Determine how to build the replacement logic based on the context
        
        logic = f"""{indent}import sys
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
{indent}    st.success(f"🔍 **捕捉到夢境關鍵字**： {{', '.join(keywords) if keywords else '無 (將全數使用熱門數據推薦)'}}")
{indent}    if matched_descs:
{indent}        st.markdown("### 📖 夢境深度解析")
{indent}        for d in matched_descs:
{indent}            st.markdown(f"> 💡 {{d}}")
"""
        return logic
        
    new_content = re.sub(pattern, replacer, content)
    
    Path(f_path).write_text(new_content, encoding="utf-8")
    print(f"Refactored {f_path}")
