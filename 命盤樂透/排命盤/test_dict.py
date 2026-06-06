from saju import calculate_saju
import json
chart = calculate_saju(2000, 1, 1, 12, 0)
print(json.dumps(chart.as_dict(), ensure_ascii=False, indent=2))
