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
        
        # We need to find `dream_database = { ... }`
        matches = list(re.finditer(r"([ \t]*)dream_database\s*=\s*\{", content))
        if not matches:
            continue
        
        for match in matches:
            start_idx = match.start()
            indent = match.group(1)
            # Find the matching closing brace
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
        
        p.write_text(content, encoding="utf-8")
        print(f"Replaced in {f_path}")
    except Exception as e:
        print(e)
