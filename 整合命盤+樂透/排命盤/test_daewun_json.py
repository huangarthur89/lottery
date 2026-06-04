from saju import calculate_saju
import json

chart = calculate_saju(1971, 9, 20, 12, 0, gender="M", timezone_name="Asia/Taipei")
print(json.dumps(chart.get_daewun_timeline(), ensure_ascii=False, indent=2))
