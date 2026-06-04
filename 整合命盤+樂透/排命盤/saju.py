import calendar
import math
from datetime import datetime, timedelta

import pytz

try:
    import swisseph as swe
except ImportError:
    swe = None

# 天干與地支
STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
SEXAGENARY_CYCLE = [STEMS[i % 10] + BRANCHES[i % 12] for i in range(60)]

# 地支藏干完整數據 (本氣, 中氣, 餘氣)
HIDDEN_STEMS_DATA = {
    "子": {"main": "癸", "sub_1": None, "sub_2": None},
    "丑": {"main": "己", "sub_1": "癸", "sub_2": "辛"},
    "寅": {"main": "甲", "sub_1": "丙", "sub_2": "戊"},
    "卯": {"main": "乙", "sub_1": None, "sub_2": None},
    "辰": {"main": "戊", "sub_1": "乙", "sub_2": "癸"},
    "巳": {"main": "丙", "sub_1": "庚", "sub_2": "戊"},
    "午": {"main": "丁", "sub_1": "己", "sub_2": None},
    "未": {"main": "己", "sub_1": "丁", "sub_2": "乙"},
    "申": {"main": "庚", "sub_1": "壬", "sub_2": "戊"},
    "酉": {"main": "辛", "sub_1": None, "sub_2": None},
    "戌": {"main": "戊", "sub_1": "辛", "sub_2": "丁"},
    "亥": {"main": "壬", "sub_1": "甲", "sub_2": None}
}

TEN_STEMS = {
    '甲': ('木', True),  '乙': ('木', False),
    '丙': ('火', True),  '丁': ('火', False),
    '戊': ('土', True),  '己': ('土', False),
    '庚': ('金', True),  '辛': ('金', False),
    '壬': ('水', True),  '癸': ('水', False)
}

ELEMENT_RELATION = {
    ('木', '木'): 'BI',    ('木', '火'): 'SHANG', ('木', '土'): 'CAI',   ('木', '金'): 'GUAN',  ('木', '水'): 'YIN',
    ('火', '木'): 'YIN',   ('火', '火'): 'BI',    ('火', '土'): 'SHANG', ('火', '金'): 'CAI',   ('火', '水'): 'GUAN',
    ('土', '木'): 'GUAN',  ('土', '火'): 'YIN',   ('土', '土'): 'BI',    ('土', '金'): 'SHANG', ('土', '水'): 'CAI',
    ('金', '木'): 'CAI',   ('金', '火'): 'GUAN',  ('金', '土'): 'YIN',   ('金', '金'): 'BI',    ('金', '水'): 'SHANG',
    ('水', '木'): 'SHANG', ('水', '火'): 'CAI',   ('水', '土'): 'GUAN',  ('水', '金'): 'YIN',   ('水', '水'): 'BI'
}

TEN_GODS_MATRIX = {
    ('BI', True): '比肩',    ('BI', False): '劫財',
    ('YIN', True): '偏印',   ('YIN', False): '正印',
    ('SHANG', True): '食神', ('SHANG', False): '傷官',
    ('GUAN', True): '七殺',  ('GUAN', False): '正官',
    ('CAI', True): '偏財',   ('CAI', False): '正財'
}

def get_ten_god(day_stem, target_stem):
    """計算十神 (以日干為基準)"""
    if day_stem not in TEN_STEMS or target_stem not in TEN_STEMS:
        return "未知"
        
    day_element, day_polarity = TEN_STEMS[day_stem]
    tar_element, tar_polarity = TEN_STEMS[target_stem]
    
    relation_code = ELEMENT_RELATION[(day_element, tar_element)]
    same_polarity = (day_polarity == tar_polarity)
    
    return TEN_GODS_MATRIX[(relation_code, same_polarity)]

class SajuChart:
    def __init__(
        self,
        year_pillar,
        month_pillar,
        day_pillar,
        hour_pillar,
        gender="M",
        is_forward=True,
        start_age=0.0,
        birth_year=2000,
        start_age_detail=None,
        start_solar_datetime=None,
    ):
        self.year_pillar = year_pillar
        self.month_pillar = month_pillar
        self.day_pillar = day_pillar
        self.hour_pillar = hour_pillar
        self.gender = gender
        self.is_forward = is_forward
        self.start_age = start_age
        self.birth_year = birth_year
        self.start_age_detail = start_age_detail or {}
        self.start_solar_datetime = start_solar_datetime

    def get_pillar_info(self, pillar, is_day_pillar=False):
        stem = pillar[0]
        branch = pillar[1]
        day_stem = self.day_pillar[0]
        
        branch_info = HIDDEN_STEMS_DATA.get(branch)
        hidden_stems = {}
        
        if branch_info and branch_info.get("main"):
            hidden_stems["本氣"] = {"stem": branch_info["main"], "ten_god": get_ten_god(day_stem, branch_info["main"])}
        if branch_info and branch_info.get("sub_1"):
            hidden_stems["中氣"] = {"stem": branch_info["sub_1"], "ten_god": get_ten_god(day_stem, branch_info["sub_1"])}
        if branch_info and branch_info.get("sub_2"):
            hidden_stems["餘氣"] = {"stem": branch_info["sub_2"], "ten_god": get_ten_god(day_stem, branch_info["sub_2"])}
            
        return {
            "stem": stem,
            "branch": branch,
            "stem_ten_god": "日主" if is_day_pillar else get_ten_god(day_stem, stem),
            "hidden_stems": hidden_stems
        }

    def get_daewun_timeline(self):
        try:
            current_index = SEXAGENARY_CYCLE.index(self.month_pillar)
        except ValueError:
            current_index = 0
            
        step = 1 if self.is_forward else -1
        
        timeline = {}
        current_age = int(self.start_age)
        if self.start_age > 0 and current_age == 0:
            current_age = 0
        current_year = (
            self.start_solar_datetime.year
            if self.start_solar_datetime is not None
            else self.birth_year + current_age
        )
        
        for i in range(1, 9):
            current_index = (current_index + step) % 60
            pillar_name = SEXAGENARY_CYCLE[current_index]
            
            years_in_yun = []
            for age_offset in range(10):
                loop_age = current_age + age_offset
                loop_year = current_year + age_offset
                
                year_pillar_index = (16 + (loop_year - 2000)) % 60
                year_pillar = SEXAGENARY_CYCLE[year_pillar_index]
                
                years_in_yun.append({
                    "西元年份": loop_year,
                    "實歲": loop_age,
                    "流年干支": year_pillar
                })
                
            timeline[f"第{i}步大運: {pillar_name}"] = {
                "起迄年齡": f"{current_age}歲 - {current_age + 9}歲",
                "起迄年份": f"{current_year}年 - {current_year + 9}年",
                "流年明細": years_in_yun
            }
            
            current_age += 10
            current_year += 10
            
        return timeline

    def as_dict(self):
        return {
            "year": self.get_pillar_info(self.year_pillar),
            "month": self.get_pillar_info(self.month_pillar),
            "day": self.get_pillar_info(self.day_pillar, is_day_pillar=True),
            "hour": self.get_pillar_info(self.hour_pillar),
            "大運流年總覽": self.get_daewun_timeline(),
            "起運歲數_精確": round(self.start_age, 2),
            "起運歲數_詳細": format_start_age_detail(self.start_age_detail),
            "交運日期": format_start_datetime(self.start_solar_datetime),
            "大運方向": "順推" if self.is_forward else "逆推"
        }

def get_jdn(year, month, day):
    """計算儒略日 (Fliegel & Van Flandern)"""
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045

def get_solar_longitude_by_jdn(jdn):
    if swe is not None:
        return swe.calc_ut(jdn, swe.SUN)[0][0] % 360

    n = jdn - 2451545.0
    L = (280.460 + 0.9856474 * n) % 360
    g = (357.528 + 0.9856003 * n) % 360
    g_rad = math.radians(g)
    lambda_sun = (L + 1.915 * math.sin(g_rad) + 0.020 * math.sin(2 * g_rad)) % 360
    return lambda_sun

def get_solar_longitude(year, month, day, hour, minute, tz_offset):
    """使用低精度天文公式計算太陽黃經"""
    utc_hour = hour - tz_offset
    jdn = get_jdn(year, month, day) - 0.5 + (utc_hour + minute / 60) / 24
    return get_solar_longitude_by_jdn(jdn)

def format_start_age_detail(detail):
    if not detail:
        return ""
    return f"{detail['years']}年{detail['months']}月{detail['days']}日{detail['hours']}時"

def format_start_datetime(dt):
    if dt is None:
        return ""
    return dt.strftime("%Y-%m-%d %H:%M")

def add_months(dt, months):
    month_index = dt.month - 1 + months
    year = dt.year + month_index // 12
    month = month_index % 12 + 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)

def get_start_age_detail(diff_days):
    years = int(diff_days // 3)
    remaining_days = diff_days - years * 3

    months_float = remaining_days * 4
    months = int(months_float)

    days_float = (months_float - months) * 30
    days = int(days_float)

    hours = int(round((days_float - days) * 24))
    if hours >= 24:
        days += 1
        hours -= 24
    if days >= 30:
        months += days // 30
        days %= 30
    if months >= 12:
        years += months // 12
        months %= 12

    return {"years": years, "months": months, "days": days, "hours": hours}

def get_start_solar_datetime(birth_dt, detail):
    start_dt = add_months(birth_dt, detail["years"] * 12 + detail["months"])
    return start_dt + timedelta(days=detail["days"], hours=detail["hours"])

def find_jie_jdn(current_jdn, target_lambda, is_forward):
    left = current_jdn
    right = current_jdn + 35 if is_forward else current_jdn - 35
    if right < left:
        left, right = right, left
    for _ in range(50):
        mid = (left + right) / 2
        mid_lambda = get_solar_longitude_by_jdn(mid)
        diff = (mid_lambda - target_lambda) % 360
        if diff > 180:
            diff -= 360
        if abs(diff) < 0.0001:
            return mid
        if diff > 0:
            right = mid
        else:
            left = mid
    return (left + right) / 2

def calculate_saju(year, month, day, hour, minute, gender="M", timezone_name="Asia/Seoul", day_boundary="zi"):
    tz = pytz.timezone(timezone_name)
    # 計算 UTC offset (考慮夏令時間)
    dt = tz.localize(datetime(year, month, day, hour, minute))
    tz_offset = dt.utcoffset().total_seconds() / 3600

    # 處理子時換日
    # 韓國時間若超過 23:00，是否算隔天？
    # day_boundary="zi" 代表 23:00 後就算隔天的日柱
    calc_year, calc_month, calc_day = year, month, day
    if day_boundary == "zi" and hour >= 23:
        # 子時換日只影響日柱/時柱，不應改變實際出生瞬間。
        dt_next = dt + timedelta(days=1)
        calc_year, calc_month, calc_day = dt_next.year, dt_next.month, dt_next.day
        
    # 計算日柱 (基於 calc_year, calc_month, calc_day)
    jdn = get_jdn(calc_year, calc_month, calc_day)
    # 1900-01-01 JDN: 2415021 -> 甲戌(10, 10). 2451545 (2000-01-01) -> 戊午(54)
    # 2451545 % 60 = 5. 5 + 49 = 54.
    day_idx = (jdn + 49) % 60
    day_stem_idx = day_idx % 10
    day_branch_idx = day_idx % 12
    day_pillar = STEMS[day_stem_idx] + BRANCHES[day_branch_idx]

    # 計算時柱
    # 23-01: 子(0), 01-03: 丑(1), ...
    hour_branch_idx = ((hour + 1) % 24) // 2
    # 五鼠遁: 甲己起甲子(0), 乙庚起丙子(2), 丙辛起戊子(4), 丁壬起庚子(6), 戊癸起壬子(8)
    hour_stem_idx = (day_stem_idx % 5 * 2 + hour_branch_idx) % 10
    hour_pillar = STEMS[hour_stem_idx] + BRANCHES[hour_branch_idx]

    # 計算月柱與年柱 (以原始出生時間計算太陽黃經)
    lambda_sun = get_solar_longitude(year, month, day, hour, minute, tz_offset)
    
    # 太陽黃經轉換為節氣月 (0-11, 0為寅月, 1為卯月...)
    # 立春為 315 度，對應寅月
    shifted_lambda = (lambda_sun + 45) % 360
    month_idx = int(shifted_lambda // 30)
    month_branch_idx = (month_idx + 2) % 12 # 0->2(寅), 1->3(卯)...

    # 判斷八字年份 (立春切割)
    # 立春約在2月4日。若在1、2月且尚未立春，則年份為前一年
    bazi_year = year
    if month <= 2:
        # 如果計算出的月支是 子(0) 或 丑(1)，代表尚未立春 (寅月)
        if month_branch_idx == 0 or month_branch_idx == 1:
            bazi_year -= 1
    
    # 計算年干支
    # 1984年為甲子年 (0, 0)
    year_idx = (bazi_year - 4) % 60
    year_stem_idx = year_idx % 10
    year_branch_idx = year_idx % 12
    year_pillar = STEMS[year_stem_idx] + BRANCHES[year_branch_idx]

    # 計算月干 (五虎遁)
    # 甲己之年丙作首...
    # 若為子(0)丑(1)月，其屬於前一年的尾巴，但天干仍依循該年的五虎遁序列
    # (month_branch_idx if month_branch_idx >= 2 else month_branch_idx + 12) 讓 寅=2, ... 子=12, 丑=13
    adjusted_month_branch = month_branch_idx if month_branch_idx >= 2 else month_branch_idx + 12
    month_stem_idx = (year_stem_idx % 5 * 2 + adjusted_month_branch) % 10
    month_pillar = STEMS[month_stem_idx] + BRANCHES[month_branch_idx]

    # 計算大運順逆推
    year_polarity = TEN_STEMS[year_pillar[0]][1]
    is_male = (gender.upper() == "M")
    is_forward = (year_polarity == is_male)
    
    # 計算起運歲數
    target_prev = (int((lambda_sun - 15) // 30) * 30 + 15) % 360
    target_next = (target_prev + 30) % 360
    
    current_jdn = get_jdn(year, month, day) - 0.5 + ((hour - tz_offset) + minute / 60) / 24
    
    if is_forward:
        jie_jdn = find_jie_jdn(current_jdn, target_next, True)
        diff_days = jie_jdn - current_jdn
    else:
        jie_jdn = find_jie_jdn(current_jdn, target_prev, False)
        diff_days = current_jdn - jie_jdn
        
    start_age = diff_days / 3.0
    start_age_detail = get_start_age_detail(diff_days)
    start_solar_datetime = get_start_solar_datetime(dt, start_age_detail)
    
    return SajuChart(
        year_pillar,
        month_pillar,
        day_pillar,
        hour_pillar,
        gender,
        is_forward,
        start_age,
        year,
        start_age_detail,
        start_solar_datetime,
    )

def print_chart(chart):
    print(f"年柱: {chart.year_pillar}")
    print(f"月柱: {chart.month_pillar}")
    print(f"日柱: {chart.day_pillar}")
    print(f"時柱: {chart.hour_pillar}")
