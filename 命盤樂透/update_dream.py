import os

new_dream_dict_str = """
            dream_database = {
                # === 動物與生肖篇 ===
                ("鼠", "老鼠", "米奇"): [1, 13, 25, 37, 49],
                ("牛", "黃牛", "水牛"): [2, 14, 26, 38],
                ("虎", "老虎", "石虎"): [3, 15, 27, 39],
                ("兔", "兔子", "野兔"): [4, 16, 28, 40],
                ("龍", "神龍", "恐龍"): [5, 17, 29, 41],
                ("蛇", "蟒蛇", "毒蛇"): [6, 9, 16, 18, 30, 42],
                ("馬", "白馬", "賽馬"): [7, 19, 31, 43],
                ("羊", "山羊", "綿羊"): [8, 20, 32, 44],
                ("猴", "猴子", "猩猩"): [9, 21, 33, 45],
                ("雞", "公雞", "母雞", "小雞"): [10, 22, 34, 46],
                ("狗", "犬", "小狗", "黑狗"): [9, 11, 23, 35, 47],
                ("豬", "山豬", "小豬", "野豬"): [12, 24, 36, 48],
                ("貓", "小貓", "野貓", "貓咪"): [12, 13, 19],
                ("魚", "釣魚", "鯉魚", "鯊魚"): [8, 17, 37],
                ("鳥", "小鳥", "烏鴉", "老鷹"): [3, 11],
                ("烏龜", "海龜", "龜"): [8, 9],
                
                # === 象形與物品篇 (形體逼牌) ===
                ("眼鏡", "雙環", "望遠鏡"): [8],
                ("筷子", "香", "筆", "竹子"): [1, 11],
                ("洞", "圓圈", "球", "輪胎"): [0, 10, 20, 30],
                ("鉤子", "釣魚鉤", "雨傘把"): [9],
                ("船", "帆船", "船隻", "遊艇"): [4, 14, 24],
                ("傘", "雨傘"): [3],
                ("鞋", "靴子", "皮鞋", "布鞋"): [10, 20],
                ("棺材", "墓碑", "墳墓"): [4, 14],
                ("腳踏車", "單車", "自行車"): [8],
                
                # === 事件與情境篇 ===
                ("水", "下雨", "淹水", "游泳", "海", "河"): [6, 10, 24],
                ("火", "火災", "燒火", "爆炸"): [3, 9, 13, 23],
                ("血", "流血", "受傷", "開刀"): [4, 14, 24, 34],
                ("死", "死人", "死亡", "喪事", "屍體"): [4, 14, 44],
                ("車禍", "撞車", "出車禍"): [4, 14],
                ("屎", "大便", "廁所", "拉肚子", "糞便"): [8, 18, 28, 38],
                ("錢", "鈔票", "硬幣", "發財", "中獎", "發票"): [7, 17, 27, 37],
                ("結婚", "新娘", "喜事", "婚禮"): [26, 36],
                ("懷孕", "孕婦", "生小孩", "大肚子"): [0, 10, 20],
                ("地震", "搖晃", "地動"): [7, 17, 27],
                ("飛機", "飛行", "出國"): [2, 12, 22],
                
                # === 人物與神鬼篇 ===
                ("鬼", "阿飄", "女鬼", "殭屍", "魔鬼"): [7, 14, 19],
                ("神", "神明", "拜拜", "土地公", "佛祖", "菩薩"): [16, 26, 36, 1],
                ("警察", "警車", "報警", "抓賊"): [10, 11],
                ("小孩", "嬰兒", "兒童", "兒子", "女兒"): [1, 11],
                ("女人", "女孩", "老婆", "阿嬤", "媽媽"): [2, 12, 22],
                ("男人", "男孩", "老公", "阿公", "爸爸"): [1, 11, 21],
                ("小偷", "盜賊", "被偷"): [3, 13]
            }
"""

replacement_logic1 = """
                extracted_numbers = set()
                keywords = []
                user_input_lower = dream_text.lower()
                for kw_tuple, nums in dream_database.items():
                    if any(k in user_input_lower for k in kw_tuple):
                        extracted_numbers.update(nums)
                        for k in kw_tuple:
                            if k in user_input_lower and k not in keywords:
                                keywords.append(k)
                                
                dream_nums = list(set([n for n in extracted_numbers if 1 <= n <= MAX_NUM]))
                
                st.success(f"🔍 **捕捉到夢境關鍵字**： {', '.join(keywords) if keywords else '無 (將完全依賴八字與大數據)'}")
                if dream_nums:
                    st.write(f"💭 **字典初始轉化號碼**： {sorted(dream_nums)}")
"""

replacement_logic2 = """
                extracted_numbers = set()
                matched_keywords = []
                user_input_lower = dream_text.lower()
                for kw_tuple, nums in dream_database.items():
                    if any(k in user_input_lower for k in kw_tuple):
                        extracted_numbers.update(nums)
                        for k in kw_tuple:
                            if k in user_input_lower and k not in matched_keywords:
                                matched_keywords.append(k)
                
                dream_nums = list({n for n in extracted_numbers if 1 <= n <= MAX_NUM})
                
                st.success(f"🔍 捕捉到夢境關鍵字：{', '.join(matched_keywords) if matched_keywords else '無 (將全數使用熱門數據推薦)'}")
                st.write(f"💭 夢境轉化號碼：{dream_nums if dream_nums else '無'}")
"""

import re

def process_file(filepath, max_num):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Block 1: The AI/Bazi combined one (lines ~796 to ~923)
    # The regex targets `dream_dict = { ... }` up to the `st.write(f"💭 **字典初始轉化號碼**： {sorted(dream_nums)}")`
    # We will use re.sub with DOTALL.

    pattern1 = r"(\s+)(dream_dict = \{.*?\n\s+if not dream_text:\n\s+st.warning\(\"請先輸入您的夢境內容！\"\)\n\s+st.stop\(\)\n\s+else:\n)(.*?)(\s+st\.success\(f\"🔍 \*\*捕捉到夢境關鍵字\*\*(.*?)\n.*?st\.write\(f\"💭 \*\*字典初始轉化號碼\*\*(.*?)\n)"
    
    def replacer1(match):
        indent = match.group(1)
        new_dict = new_dream_dict_str.replace("            ", indent)
        new_logic = replacement_logic1.replace("            ", indent).replace("MAX_NUM", str(max_num))
        
        pre_check = f"""{new_dict}
{indent}if not dream_text:
{indent}    st.warning("請先輸入您的夢境內容！")
{indent}    st.stop()
{indent}else:"""
        return indent + pre_check.strip() + "\n" + new_logic

    content = re.sub(pattern1, replacer1, content, flags=re.DOTALL)

    # Block 2: The simple random append one (lines ~1185 to ~1279)
    # We target `dream_dict = { ... }` to `st.write(f"💭 夢境轉化號碼：{dream_nums if dream_nums else '無'}")`
    
    pattern2 = r"(\s+)(dream_dict = \{.*?\n\s+if st\.button\(\"🔮 解析夢境並產生號碼\"\):\n\s+if not dream_text:\n\s+st\.warning\(\"還沒輸入夢境啦！\"\)\n\s+st\.stop\(\)\n\s+else:\n)(.*?)(\s+st\.success\(f\"🔍 捕捉到夢境關鍵字(.*?)\n.*?st\.write\(f\"💭 夢境轉化號碼(.*?)\n)"
    
    def replacer2(match):
        indent = match.group(1)
        # Note: the second dream_dict is before the button
        new_dict_shifted = new_dream_dict_str.replace("            ", indent)
        new_logic2 = replacement_logic2.replace("            ", indent + "    ").replace("MAX_NUM", str(max_num))
        
        return f"{indent}{new_dict_shifted.strip()}\n\n{indent}if st.button(\"🔮 解析夢境並產生號碼\"):\n{indent}    if not dream_text:\n{indent}        st.warning(\"還沒輸入夢境啦！\")\n{indent}        st.stop()\n{indent}    else:\n{new_logic2}"

    content = re.sub(pattern2, replacer2, content, flags=re.DOTALL)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Processed {filepath}")

base_dir = "/Volumes/MSI 2T/Antigravity/阿舍AI/命盤樂透/lottery/pages"
process_file(f"{base_dir}/1_大樂透.py", 49)
process_file(f"{base_dir}/2_威力彩.py", 38)
