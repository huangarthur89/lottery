import sqlite3
import pandas as pd
from collections import Counter

conn = sqlite3.connect('lottery_data.db')
df = pd.read_sql('SELECT * FROM lotto ORDER BY 期別 DESC', conn)
conn.close()

nums = [2, 4, 7, 9, 11, 30]

if df.empty:
    print("Database is empty.")
else:
    all_nums = df[['N1', 'N2', 'N3', 'N4', 'N5', 'N6']].values.flatten()
    freq = Counter(all_nums)
    
    print("=== 冷熱次數 ===")
    for n in nums:
        print(f"號碼 {n}: {freq[n]} 次")
        
    print("\n=== 遺漏值 (Gap) ===")
    gaps = {n: -1 for n in nums}
    for n in nums:
        for i, row in df.iterrows():
            draw = [row['N1'], row['N2'], row['N3'], row['N4'], row['N5'], row['N6']]
            if n in draw:
                gaps[n] = i
                break
        if gaps[n] == -1: gaps[n] = len(df) # never appeared
    for n in nums:
        print(f"號碼 {n}: 遺漏 {gaps[n]} 期")

