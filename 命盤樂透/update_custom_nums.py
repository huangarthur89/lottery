import os
from pathlib import Path
import re

files = [
    "lottery/pages/1_大樂透.py",
    "lottery/pages/2_威力彩.py"
]

for f_path in files:
    content = Path(f_path).read_text(encoding="utf-8")
    
    # 1. 替換輸入框的文字與邏輯限制 (6 -> 10)
    content = content.replace("請選擇 1~6 個您的心水號碼", "請選擇 1~10 個您的心水號碼")
    content = content.replace("len(user_input_nums) > 6", "len(user_input_nums) > 10")
    content = content.replace("最多輸入 6 個號碼", "最多輸入 10 個號碼")
    
    # 2. 汰弱留強機制
    old_drop_logic = """            # 如果使用者選滿了 6 個，AI 強制替換最弱的 1~2 個；選 5 個則替換最弱的 1 個
            if len(sorted_user_nums) == 6:
                keep_len = random.choice([4, 5]) 
                kept_nums = sorted_user_nums[:keep_len]
                dropped_nums = sorted_user_nums[keep_len:]
            elif len(sorted_user_nums) == 5:
                keep_len = 4
                kept_nums = sorted_user_nums[:keep_len]
                dropped_nums = sorted_user_nums[keep_len:]"""
    
    new_drop_logic = """            # 為了凸顯 AI 大數據與八字選號 (紅色顯示)，強制汰換掉最弱的號碼
            if len(sorted_user_nums) >= 6:
                keep_len = random.choice([4, 5]) 
            elif len(sorted_user_nums) > 1:
                keep_len = len(sorted_user_nums) - 1
            else:
                keep_len = len(sorted_user_nums)
                
            kept_nums = sorted_user_nums[:keep_len]
            dropped_nums = sorted_user_nums[keep_len:]"""
            
    content = content.replace(old_drop_logic, new_drop_logic)
    
    # 3. 變更號碼顏色
    old_format_ball = """            def format_ball_c(n):
                return f"<span style='font-size: 20px; font-weight:bold; background-color:#F0F2F6; padding: 4px 10px; border-radius: 50%; margin-right: 5px;'>{str(n).zfill(2)}</span>\""""
                
    new_format_ball = """            def format_ball_c(n):
                is_ai = n in res['ai_added_nums']
                color_style = "color:#FF0000; background-color:#FFE4E1; border: 1px solid #FFCDD2;" if is_ai else "color:#333333; background-color:#F0F2F6; border: 1px solid #E0E0E0;"
                return f"<span title='{'AI 大數據/八字推薦' if is_ai else '保留您的自選'}' style='font-size: 20px; font-weight:bold; {color_style} padding: 4px 10px; border-radius: 50%; margin-right: 5px;'>{str(n).zfill(2)}</span>\""""
                
    content = content.replace(old_format_ball, new_format_ball)
    
    Path(f_path).write_text(content, encoding="utf-8")
    print(f"Updated {f_path}")
