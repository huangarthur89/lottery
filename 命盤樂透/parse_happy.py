import re
import json

with open("scratch_happylottery.js", "r", encoding="utf-8") as f:
    content = f.read()

# We look for something like const dreamData = [...];
# or look for strings and arrays of numbers.
# Actually, the data is usually JSON.
matches = re.search(r'const\s+dreamData\s*=\s*(\[.*?\]);', content, re.DOTALL)
if matches:
    data = matches.group(1)
    # The JSON might have unquoted keys if it's JS, but let's try to fix it.
    data = re.sub(r'(\w+):', r'"\1":', data)
    data = data.replace("'", '"')
    try:
        j = json.loads(data)
        print("Successfully loaded dreamData array of length:", len(j))
    except Exception as e:
        print("JSON parse failed:", e)
        # Let's just use regex to extract everything that looks like {"keyword": "xxx", "numbers": [1,2,3]} or similar
        items = re.findall(r'keyword["\s]*:\s*["\']([^"\']+)["\']\s*,\s*["\']*numbers["\']*:\s*\[([\d,\s]+)\]', content)
        if not items:
            # Let's try finding pairs of chinese words and numbers
            items = re.findall(r'["\']([\u4e00-\u9fa5]+)["\']\s*:\s*\[([\d,\s]+)\]', content)
        print("Extracted items via regex:", len(items))
else:
    # Just try to find keyword and numbers array
    items = re.findall(r'keyword["\s]*:\s*["\']([^"\']+)["\']\s*,\s*["\']*numbers["\']*:\s*\[([\d,\s]+)\]', content)
    if items:
        print("Extracted items via regex:", len(items))
    else:
        # Maybe it's like "蛇": [6, 16]
        items = re.findall(r'["\']([^"\']+)["\']\s*:\s*\[([\d,\s]+)\]', content)
        print("Extracted items via regex fallback:", len(items))

