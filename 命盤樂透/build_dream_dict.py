import urllib.request
import re
import json

urls = [
    "https://www.golla.tw/meng/%E5%A4%A2%E6%A8%82%E9%80%8F%E8%99%9F%E7%A2%BC%E8%A1%A8.html",
    "https://happylottery.tw/dreamNumber.html",
    "https://dlg8888.tw/dream-interpretation-lottery-and-539-numbers/",
    "https://gameapp.tw/lotto/big-lotto-dream"
]

headers = {'User-Agent': 'Mozilla/5.0'}

# Store extracted data
dream_dict = {}

def add_entry(word, nums):
    if not word or not nums:
        return
    word = word.strip()
    if not word: return
    # Remove weird chars
    word = re.sub(r'[^\w\u4e00-\u9fa5]', '', word)
    if not word: return
    
    valid_nums = []
    for n in nums:
        try:
            val = int(n)
            if 0 <= val <= 49:
                valid_nums.append(val)
        except:
            pass
            
    if not valid_nums: return
    
    if word not in dream_dict:
        dream_dict[word] = set()
    for n in valid_nums:
        dream_dict[word].add(n)

def fetch_url(url):
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return ""

print("Fetching golla.tw...")
html = fetch_url(urls[0])
# golla has rows like <tr><td>word</td><td>nums</td></tr>
# We can just extract text using regex
rows = re.findall(r'<tr[^>]*>.*?<td[^>]*>(.*?)</td>.*?<td[^>]*>(.*?)</td>', html, re.DOTALL | re.IGNORECASE)
for w_raw, n_raw in rows:
    w = re.sub(r'<[^>]+>', '', w_raw).strip()
    n_str = re.sub(r'<[^>]+>', '', n_raw).strip()
    nums = re.findall(r'\d+', n_str)
    add_entry(w, nums)

print("Fetching happylottery.tw...")
html = fetch_url(urls[1])
# Need to check structure. Wait, we fetched it earlier and it was mostly JS powered?
# Let's see if the data is in the HTML.
# In the previous read_url_content, happylottery.tw seemed to load data dynamically via Firebase (URL: happy-lottery-a3486-default-rtdb.asia-southeast1.firebasedatabase.app).
# We might miss data if it's rendered by JS. Let's see if there's any JSON in the script tags.
script_data = re.search(r'const\s+dreamData\s*=\s*(\[.*?\]);', html, re.DOTALL)
if script_data:
    pass # we could parse it

# Actually, let's just dump all text from HTML and find word-number patterns.
# Many sites just use tables.
print("Fetching dlg8888.tw...")
html = fetch_url(urls[2])
# dlg8888 has tables or lists. Let's extract anything like "蛇：06、16、26" or "狗(09)"
matches = re.findall(r'([\u4e00-\u9fa5]+)\s*[:：]\s*([\d、,\s]+)', html)
for w, n_raw in matches:
    nums = re.findall(r'\d+', n_raw)
    add_entry(w, nums)

matches2 = re.findall(r'([\u4e00-\u9fa5]+)\s*[\(（]([\d、,\s]+)[\)）]', html)
for w, n_raw in matches2:
    nums = re.findall(r'\d+', n_raw)
    add_entry(w, nums)

print("Fetching gameapp.tw...")
html = fetch_url(urls[3])
matches = re.findall(r'([\u4e00-\u9fa5]+)\s*[:：]\s*([\d、,\s]+)', html)
for w, n_raw in matches:
    nums = re.findall(r'\d+', n_raw)
    add_entry(w, nums)

print(f"Total unique words collected: {len(dream_dict)}")

# Group words that have the exact same set of numbers to shrink dictionary size
grouped_dict = {}
for w, nums in dream_dict.items():
    nums_tuple = tuple(sorted(list(nums)))
    if nums_tuple not in grouped_dict:
        grouped_dict[nums_tuple] = []
    grouped_dict[nums_tuple].append(w)

out_lines = []
out_lines.append("dream_database = {")
for nums_tuple, words in grouped_dict.items():
    words_tup = tuple(words)
    out_lines.append(f"    {words_tup}: {list(nums_tuple)},")
out_lines.append("}")

with open("dream_dict.py", "w", encoding="utf-8") as f:
    f.write("\n".join(out_lines))
print("Saved to dream_dict.py")
