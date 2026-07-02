import urllib.request
import re
import json
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

# The JS data on happylottery.tw
url = "https://happylottery.tw/js/dreamData.js" # Usually stored in a separate js or inline
req = urllib.request.Request("https://happylottery.tw/dreamNumber.html", headers={'User-Agent': 'Mozilla/5.0'})
try:
    html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
    # Try to find the external JS file
    js_links = re.findall(r'<script\s+src="([^"]+)"', html)
    for link in js_links:
        if 'dream' in link.lower() or 'data' in link.lower() or 'main' in link.lower():
            if not link.startswith('http'):
                link = "https://happylottery.tw/" + link.lstrip('/')
            js_text = urllib.request.urlopen(urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'})).read().decode('utf-8')
            with open("scratch_happylottery.js", "w") as f:
                f.write(js_text)
except Exception as e:
    pass

# For gameapp.tw
try:
    req = urllib.request.Request("https://gameapp.tw/lotto/big-lotto-dream", headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
    with open("scratch_gameapp.html", "w") as f:
        f.write(html)
except:
    pass

# For dlg8888.tw
try:
    req = urllib.request.Request("https://dlg8888.tw/dream-interpretation-lottery-and-539-numbers/", headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
    with open("scratch_dlg.html", "w") as f:
        f.write(html)
except:
    pass
