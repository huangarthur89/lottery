import re

with open('pages/2_威力彩.py', 'r', encoding='utf-8') as f:
    content = f.read()

# basic replacements
content = content.replace('阿舍的大樂透分析工具', '阿舍的威力彩分析工具')
content = content.replace('大樂透歷史數據自動化查詢系統', '威力彩歷史數據自動化查詢系統')
content = content.replace('Lotto649Result', 'SuperLotto638Result')
content = content.replace('lotto649Res', 'superLotto638Res')
content = content.replace('lotto', 'super_lotto')
content = content.replace('大樂透', '威力彩')

# Restore DB name
content = content.replace('super_lottery_data.db', 'lottery_data.db')

# Bounds
content = content.replace('range(1, 50)', 'range(1, 39)')
content = content.replace('1 <= x <= 49', '1 <= x <= 38')
content = content.replace('1 <= n <= 49', '1 <= n <= 38')
content = content.replace('random.randint(1, 49)', 'random.randint(1, 38)')
content = content.replace('most_common(49)', 'most_common(38)')
content = content.replace('len(found_numbers) == 49', 'len(found_numbers) == 38')
content = content.replace('len(found_special) == 49', 'len(found_special) == 8')
content = content.replace("else random.randint(1, 38)", "else random.randint(1, 8)")
content = content.replace("random.choice([n for n in bazi_lucky_pool])", "random.choice([n for n in bazi_lucky_pool if n <= 8] or [random.randint(1, 8)])")
# Special Number bound changes
content = content.replace('spec_counts = {n: 0 for n in range(1, 39)}', 'spec_counts = {n: 0 for n in range(1, 9)}')
content = content.replace('mix_sp = random.randint(1, 38)', 'mix_sp = random.randint(1, 8)')
content = content.replace('rand_sp = random.randint(1, 38)', 'rand_sp = random.randint(1, 8)')
content = content.replace('special_missing = {n: 0 for n in range(1, 39)}', 'special_missing = {n: 0 for n in range(1, 9)}')
content = content.replace('list(range(1, 39)) # Fallback', 'list(range(1, 9)) # Fallback')
content = content.replace('or list(range(1, 39))', 'or list(range(1, 9))')

# For average logic
content = content.replace('(150 - current_sum)', '(117 - current_sum)')
content = content.replace('靠近 150', '靠近 117')
content = content.replace('約為 150', '約為 117')
content = content.replace('120~180', '95~139')
content = content.replace('else 25', 'else 19')

# Backtesting ticket price
content = content.replace('value=50, disabled=True', 'value=100, disabled=True')

# AI check sum values
content = content.replace('120 <= sum_val <= 180', '95 <= sum_val <= 139')
content = content.replace('100 <= sum_val < 120 or 180 < sum_val <= 200', '80 <= sum_val < 95 or 139 < sum_val <= 150')

# Rewrite backtest logic
prize_logic_old = """                            draw_prize = 0
                            if match_count == 6:
                                prize_counts['頭獎'] += 1
                                draw_prize = 100000000
                            elif match_count == 5 and match_special:
                                prize_counts['貳獎'] += 1
                                draw_prize = 2000000
                            elif match_count == 5:
                                prize_counts['參獎'] += 1
                                draw_prize = 60000
                            elif match_count == 4 and match_special:
                                prize_counts['肆獎'] += 1
                                draw_prize = 15000
                            elif match_count == 4:
                                prize_counts['伍獎 (2000)'] += 1
                                draw_prize = 2000
                            elif match_count == 3 and match_special:
                                prize_counts['陸獎 (1000)'] += 1
                                draw_prize = 1000
                            elif match_count == 2 and match_special:
                                prize_counts['柒獎 (400)'] += 1
                                draw_prize = 400
                            elif match_count == 3:
                                prize_counts['普獎 (400)'] += 1
                                draw_prize = 400"""

prize_logic_new = """                            draw_prize = 0
                            if match_count == 6 and match_special:
                                prize_counts['頭獎'] += 1
                                draw_prize = 200000000
                            elif match_count == 6:
                                prize_counts['貳獎'] += 1
                                draw_prize = 10000000
                            elif match_count == 5 and match_special:
                                prize_counts['參獎'] += 1
                                draw_prize = 150000
                            elif match_count == 5:
                                prize_counts['肆獎'] += 1
                                draw_prize = 20000
                            elif match_count == 4 and match_special:
                                prize_counts['伍獎 (4000)'] += 1
                                draw_prize = 4000
                            elif match_count == 4:
                                prize_counts['陸獎 (800)'] += 1
                                draw_prize = 800
                            elif match_count == 3 and match_special:
                                prize_counts['柒獎 (400)'] += 1
                                draw_prize = 400
                            elif match_count == 2 and match_special:
                                prize_counts['捌獎 (200)'] += 1
                                draw_prize = 200
                            elif match_count == 3:
                                prize_counts['玖獎 (100)'] += 1
                                draw_prize = 100
                            elif match_count == 1 and match_special:
                                prize_counts['普獎 (100)'] += 1
                                draw_prize = 100"""

content = content.replace(prize_logic_old, prize_logic_new)

# prize dict init update
prize_init_old = """                        prize_counts = {
                            '頭獎': 0, '貳獎': 0, '參獎': 0, '肆獎': 0,
                            '伍獎 (2000)': 0, '陸獎 (1000)': 0, '柒獎 (400)': 0, '普獎 (400)': 0
                        }"""
prize_init_new = """                        prize_counts = {
                            '頭獎': 0, '貳獎': 0, '參獎': 0, '肆獎': 0,
                            '伍獎 (4000)': 0, '陸獎 (800)': 0, '柒獎 (400)': 0, '捌獎 (200)': 0, '玖獎 (100)': 0, '普獎 (100)': 0
                        }"""
content = content.replace(prize_init_old, prize_init_new)

# write file
with open('pages/2_威力彩.py', 'w', encoding='utf-8') as f:
    f.write(content)

