import math
from saju import get_jdn, calculate_saju, TEN_STEMS, STEMS, BRANCHES

SEXAGENARY_CYCLE = [STEMS[i % 10] + BRANCHES[i % 12] for i in range(60)]

def get_solar_longitude_by_jdn(jdn):
    n = jdn - 2451545.0
    L = (280.460 + 0.9856474 * n) % 360
    g = (357.528 + 0.9856003 * n) % 360
    g_rad = math.radians(g)
    lambda_sun = (L + 1.915 * math.sin(g_rad) + 0.020 * math.sin(2 * g_rad)) % 360
    return lambda_sun

def find_jie_jdn(current_jdn, target_lambda, is_forward):
    left = current_jdn
    right = current_jdn + 35 if is_forward else current_jdn - 35
    if right < left:
        left, right = right, left
    for _ in range(50):
        mid = (left + right) / 2
        mid_lambda = get_solar_longitude_by_jdn(mid)
        diff = (mid_lambda - target_lambda) % 360
        if diff > 180: diff -= 360
        if abs(diff) < 0.0001: return mid
        if diff > 0: right = mid
        else: left = mid
    return (left + right) / 2

# test calculating is_forward
year_pillar = "辛亥"
year_polarity = TEN_STEMS[year_pillar[0]][1]
is_male = True
is_forward = (year_polarity == is_male)
print(f"{year_pillar} 男命 is_forward: {is_forward}")

# test 1971 client case
chart = calculate_saju(1971, 9, 20, 12, 0)
tz_offset = 9
hour, minute = 12, 0
current_jdn = get_jdn(1971, 9, 20) - 0.5 + ((hour - tz_offset) + minute / 60) / 24
lambda_sun = get_solar_longitude_by_jdn(current_jdn)

target_prev = (int((lambda_sun - 15) // 30) * 30 + 15) % 360
target_next = (target_prev + 30) % 360

if is_forward:
    jie_jdn = find_jie_jdn(current_jdn, target_next, True)
    diff_days = jie_jdn - current_jdn
else:
    jie_jdn = find_jie_jdn(current_jdn, target_prev, False)
    diff_days = current_jdn - jie_jdn

start_age = diff_days / 3.0
print("Start Age:", start_age)

