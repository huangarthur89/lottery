import os
from pathlib import Path
import re

files = [
    "lottery/pages/1_大樂透.py",
    "lottery/pages/2_威力彩.py"
]

for f_path in files:
    content = Path(f_path).read_text(encoding="utf-8")
    
    # 確保已經 import pathlib
    if "from pathlib import Path" not in content:
        content = "from pathlib import Path\n" + content
        
    # 定義絕對路徑
    abs_db_def = "DB_PATH = str(Path(__file__).resolve().parents[2] / 'lottery_data.db')"
    
    if "DB_PATH =" not in content:
        # 在 import sqlite3 後面加上
        content = content.replace("import sqlite3", f"import sqlite3\n{abs_db_def}")
        
    # 把所有的 'lottery_data.db' 替換為 DB_PATH
    content = content.replace("'lottery_data.db'", "DB_PATH")
    content = content.replace('"lottery_data.db"', "DB_PATH")
    
    Path(f_path).write_text(content, encoding="utf-8")
    print(f"Updated absolute DB path in {f_path}")
