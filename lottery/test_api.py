import requests

def fetch_lotto_data_api(year, month):
    url = f'https://api.taiwanlottery.com/TLCAPIWeB/Lottery/Lotto649Result?period=&month={year}-{month:02d}&pageNum=1&pageSize=50'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        monthly_draws = []
        if 'content' in data and data['content'] and 'lotto649Res' in data['content']:
            for item in data['content']['lotto649Res']:
                draw_no = item['period']
                date_str = item['lotteryDate'].split('T')[0] # 2026-04-28
                
                # drawNumberSize contains the 6 normal numbers sorted, plus the 7th is the special number.
                # Let's extract them. Note: In some draws the API might return null if not drawn yet.
                nums_sorted = item['drawNumberSize']
                if not nums_sorted or len(nums_sorted) < 7:
                    continue
                
                normal_nums = nums_sorted[:6]
                special_num = nums_sorted[6]
                
                monthly_draws.append({
                    '期別': draw_no,
                    '日期': date_str,
                    'N1': normal_nums[0], 'N2': normal_nums[1], 'N3': normal_nums[2],
                    'N4': normal_nums[3], 'N5': normal_nums[4], 'N6': normal_nums[5],
                    '特別號': special_num,
                    '和值': sum(normal_nums)
                })
        return monthly_draws
    except Exception as e:
        print(f"Error: {e}")
        return []

print(fetch_lotto_data_api(2026, 4))
