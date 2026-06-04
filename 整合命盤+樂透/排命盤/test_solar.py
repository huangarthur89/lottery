import math

def get_jdn(year, month, day):
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045

def get_solar_longitude(year, month, day, hour, minute, tz_offset=9):
    utc_hour = hour - tz_offset
    jdn = get_jdn(year, month, day) - 0.5 + (utc_hour + minute / 60) / 24
    n = jdn - 2451545.0
    L = (280.460 + 0.9856474 * n) % 360
    g = (357.528 + 0.9856003 * n) % 360
    g_rad = math.radians(g)
    lambda_sun = (L + 1.915 * math.sin(g_rad) + 0.020 * math.sin(2 * g_rad)) % 360
    return lambda_sun

print("2000-02-04 12:00 Seoul:", get_solar_longitude(2000, 2, 4, 12, 0))
