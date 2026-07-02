import os

files = [
    "lottery/pages/1_大樂透.py",
    "lottery/pages/2_威力彩.py"
]

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 強制在 import sqlite3 的下面加上 import Path
    content = content.replace("import sqlite3\nDB_PATH", "import sqlite3\nfrom pathlib import Path\nDB_PATH")
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"Fixed {f}")
