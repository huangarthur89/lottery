STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

def get_ten_god(day_stem, other_stem):
    s_idx = STEMS.index(day_stem)
    o_idx = STEMS.index(other_stem)
    
    diff = (o_idx // 2 - s_idx // 2) % 5
    same_yy = (s_idx % 2 == o_idx % 2)
    
    gods = {
        0: ("比肩", "劫財"),
        1: ("食神", "傷官"),
        2: ("偏財", "正財"),
        3: ("七殺", "正官"),
        4: ("偏印", "正印"),
    }
    return gods[diff][0] if same_yy else gods[diff][1]

print(f"甲 meet 庚: {get_ten_god('甲', '庚')}")
print(f"甲 meet 辛: {get_ten_god('甲', '辛')}")
print(f"丙 meet 壬: {get_ten_god('丙', '壬')}")
print(f"丁 meet 庚: {get_ten_god('丁', '庚')}")
