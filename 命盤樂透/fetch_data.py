import pandas as pd
import requests
import urllib3
import datetime
import sqlite3
import os

# 隱藏不安全連線的警告提示
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DB_PATH = 'lottery_data.db'

def save_to_db(new_df, table_name):
    if new_df.empty:
        print(f"[{table_name}] 沒有新資料需要寫入。")
        return
    try:
        conn = sqlite3.connect(DB_PATH)
        try:
            old_df = pd.read_sql(f'SELECT * FROM {table_name}', conn)
            old_df['日期'] = pd.to_datetime(old_df['日期']).dt.date
        except Exception:
            old_df = pd.DataFrame()
        
        # 合併新舊資料
        combined = pd.concat([old_df, new_df])
        # 根據「期別」去重複，保留最新的
        combined = combined.drop_duplicates(subset=['期別'], keep='last')
        combined = combined.sort_values('日期', ascending=False)
        
        # 存回資料庫
        combined.to_sql(table_name, conn, if_exists='replace', index=False)
        conn.close()
        print(f"[{table_name}] 成功更新資料庫。目前總筆數: {len(combined)}")
    except Exception as e:
        print(f"[{table_name}] 資料庫寫入失敗: {e}")

def fetch_lotto649(year, month):
    print(f"[大樂透] 正在抓取 {year} 年 {month} 月資料...")
    url = f'https://api.taiwanlottery.com/TLCAPIWeB/Lottery/Lotto649Result?period=&month={year}-{month:02d}&pageNum=1&pageSize=50'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        data = response.json()
        
        monthly_draws = []
        if 'content' in data and data['content'] and 'lotto649Res' in data['content']:
            for item in data['content']['lotto649Res']:
                draw_no = item['period']
                date_str = item['lotteryDate'].split('T')[0]
                date_parts = date_str.split('-')
                date_obj = datetime.date(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
                
                nums_sorted = item.get('drawNumberSize', [])
                if not nums_sorted or len(nums_sorted) < 7:
                    continue
                
                normal_nums = nums_sorted[:6]
                special_num = nums_sorted[6]
                
                monthly_draws.append({
                    '期別': draw_no,
                    '日期': date_obj,
                    'N1': normal_nums[0], 'N2': normal_nums[1], 'N3': normal_nums[2],
                    'N4': normal_nums[3], 'N5': normal_nums[4], 'N6': normal_nums[5],
                    '特別號': special_num,
                    '和值': sum(normal_nums)
                })
        return monthly_draws
    except Exception as e:
        print(f"[大樂透] 抓取 {year}/{month} 失敗: {e}")
        return []

def fetch_super_lotto(year, month):
    print(f"[威力彩] 正在抓取 {year} 年 {month} 月資料...")
    url = f'https://api.taiwanlottery.com/TLCAPIWeB/Lottery/SuperLotto638Result?period=&month={year}-{month:02d}&pageNum=1&pageSize=50'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        data = response.json()
        
        monthly_draws = []
        if 'content' in data and data['content'] and 'superLotto638Res' in data['content']:
            for item in data['content']['superLotto638Res']:
                draw_no = item['period']
                date_str = item['lotteryDate'].split('T')[0]
                date_parts = date_str.split('-')
                date_obj = datetime.date(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
                
                nums_sorted = item.get('drawNumberSize', [])
                if not nums_sorted or len(nums_sorted) < 7:
                    continue
                
                normal_nums = nums_sorted[:6]
                special_num = nums_sorted[6]
                
                if any(n > 38 or n < 1 for n in normal_nums) or not (1 <= special_num <= 8):
                    continue
                    
                monthly_draws.append({
                    '期別': draw_no,
                    '日期': date_obj,
                    'N1': normal_nums[0], 'N2': normal_nums[1], 'N3': normal_nums[2],
                    'N4': normal_nums[3], 'N5': normal_nums[4], 'N6': normal_nums[5],
                    '特別號': special_num,
                    '和值': sum(normal_nums)
                })
        return monthly_draws
    except Exception as e:
        print(f"[威力彩] 抓取 {year}/{month} 失敗: {e}")
        return []

if __name__ == "__main__":
    print("🚀 開始執行自動抓取樂透資料任務...")
    # 確保資料庫在對的路徑
    work_dir = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(work_dir, 'lottery_data.db')
    
    today = datetime.date.today()
    
    # 計算這個月跟上個月 (避免月初漏抓上個月的資料)
    months_to_fetch = []
    months_to_fetch.append((today.year, today.month))
    
    if today.month == 1:
        months_to_fetch.append((today.year - 1, 12))
    else:
        months_to_fetch.append((today.year, today.month - 1))
        
    lotto_data = []
    super_lotto_data = []
    
    for y, m in reversed(months_to_fetch): # 先抓舊的再抓新的
        lotto_data.extend(fetch_lotto649(y, m))
        super_lotto_data.extend(fetch_super_lotto(y, m))
        
    df_lotto = pd.DataFrame(lotto_data)
    save_to_db(df_lotto, 'lotto')
    
    df_super_lotto = pd.DataFrame(super_lotto_data)
    save_to_db(df_super_lotto, 'super_lotto')
    
    print("✅ 任務執行完畢！")
