import math
from saju import get_jdn, calculate_saju, TEN_STEMS, STEMS, BRANCHES

def get_solar_longitude_by_jdn(jdn):
    n = jdn - 2451545.0
    L = (280.460 + 0.9856474 * n) % 360
    g = (357.528 + 0.9856003 * n) % 360
    g_rad = math.radians(g)
    lambda_sun = (L + 1.915 * math.sin(g_rad) + 0.020 * math.sin(2 * g_rad)) % 360
    return lambda_sun

def find_jie_jdn(current_jdn, target_lambda, is_forward):
    # Binary search for the exact JDN
    # The sun moves about 0.9856 degrees per day.
    # So the distance in days is roughly the diff in degrees / 0.9856
    left = current_jdn
    right = current_jdn + 35 if is_forward else current_jdn - 35
    
    if right < left:
        left, right = right, left
        
    for _ in range(50):
        mid = (left + right) / 2
        mid_lambda = get_solar_longitude_by_jdn(mid)
        # Handle wrap around 360
        diff = (mid_lambda - target_lambda) % 360
        if diff > 180:
            diff -= 360
            
        if abs(diff) < 0.0001:
            return mid
            
        if diff > 0:
            # mid is ahead of target
            # Wait, sun longitude increases with time
            right = mid
        else:
            left = mid
    return (left + right) / 2

# Test for 1971-10-01 (approx Ding You month, wait, 1971 is Xin Hai)
chart = calculate_saju(1971, 9, 20, 12, 0)
print(chart.year_pillar, chart.month_pillar)

jdn = get_jdn(1971, 9, 20) - 0.5 + (12 - 9)/24
lambda_sun = get_solar_longitude_by_jdn(jdn)
print("lambda_sun:", lambda_sun)

target_prev = (int((lambda_sun - 15) // 30) * 30 + 15) % 360
target_next = (target_prev + 30) % 360
print("prev:", target_prev, "next:", target_next)

prev_jdn = find_jie_jdn(jdn, target_prev, False)
next_jdn = find_jie_jdn(jdn, target_next, True)

print("current jdn:", jdn)
print("prev jdn:", prev_jdn, "diff days:", jdn - prev_jdn)
print("next jdn:", next_jdn, "diff days:", next_jdn - jdn)

