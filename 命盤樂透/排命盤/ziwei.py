from dataclasses import dataclass
from typing import Dict, List

from lunar_python import Solar

STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
PALACE_ORDER = ["命宮", "兄弟", "夫妻", "子女", "財帛", "疾厄", "遷移", "交友", "官祿", "田宅", "福德", "父母"]
MAIN_STARS = ["紫微", "天機", "太陽", "武曲", "天同", "廉貞", "天府", "太陰", "貪狼", "巨門", "天相", "天梁", "七殺", "破軍"]

STAR_BRIGHTNESS = {
    "紫微": ["平", "廟", "廟", "旺", "陷", "旺", "廟", "廟", "旺", "平", "閒", "旺"],
    "天機": ["廟", "陷", "得", "旺", "平", "平", "廟", "陷", "得", "旺", "平", "平"],
    "太陽": ["陷", "陷", "旺", "廟", "廟", "旺", "廟", "得", "平", "閒", "陷", "陷"],
    "武曲": ["旺", "廟", "平", "陷", "廟", "平", "旺", "廟", "平", "陷", "廟", "平"],
    "天同": ["旺", "陷", "平", "廟", "平", "廟", "陷", "陷", "旺", "平", "平", "廟"],
    "廉貞": ["平", "平", "廟", "平", "旺", "陷", "平", "平", "廟", "平", "旺", "陷"],
    "天府": ["廟", "廟", "廟", "得", "廟", "得", "旺", "廟", "廟", "平", "廟", "旺"],
    "太陰": ["廟", "廟", "平", "陷", "陷", "陷", "陷", "平", "平", "旺", "旺", "廟"],
    "貪狼": ["旺", "廟", "平", "平", "廟", "陷", "旺", "廟", "平", "平", "廟", "陷"],
    "巨門": ["旺", "陷", "廟", "廟", "平", "平", "旺", "陷", "廟", "廟", "平", "平"],
    "天相": ["廟", "廟", "廟", "陷", "旺", "得", "廟", "平", "廟", "陷", "旺", "得"],
    "天梁": ["廟", "旺", "廟", "廟", "旺", "陷", "廟", "旺", "陷", "得", "旺", "陷"],
    "七殺": ["旺", "廟", "廟", "陷", "平", "平", "旺", "廟", "廟", "陷", "平", "平"],
    "破軍": ["廟", "旺", "陷", "旺", "旺", "平", "廟", "旺", "陷", "旺", "旺", "平"]
}

NAYIN_ELEMENT = {
    "甲子": "金", "乙丑": "金", "丙寅": "火", "丁卯": "火", "戊辰": "木", "己巳": "木", "庚午": "土", "辛未": "土", "壬申": "金", "癸酉": "金",
    "甲戌": "火", "乙亥": "火", "丙子": "水", "丁丑": "水", "戊寅": "土", "己卯": "土", "庚辰": "金", "辛巳": "金", "壬午": "木", "癸未": "木",
    "甲申": "水", "乙酉": "水", "丙戌": "土", "丁亥": "土", "戊子": "火", "己丑": "火", "庚寅": "木", "辛卯": "木", "壬辰": "水", "癸巳": "水",
    "甲午": "金", "乙未": "金", "丙申": "火", "丁酉": "火", "戊戌": "木", "己亥": "木", "庚子": "土", "辛丑": "土", "壬寅": "金", "癸卯": "金",
    "甲辰": "火", "乙巳": "火", "丙午": "水", "丁未": "水", "戊申": "土", "己酉": "土", "庚戌": "金", "辛亥": "金", "壬子": "木", "癸丑": "木",
    "甲寅": "水", "乙卯": "水", "丙辰": "土", "丁巳": "土", "戊午": "火", "己未": "火", "庚申": "木", "辛酉": "木", "壬戌": "水", "癸亥": "水",
}
JU_BY_ELEMENT = {"水": 2, "木": 3, "金": 4, "土": 5, "火": 6}
JU_NAME_BY_ELEMENT = {"水": "水二局", "木": "木三局", "金": "金四局", "土": "土五局", "火": "火六局"}

FOUR_TRANSFORMS = {
    "甲": {"祿": "廉貞", "權": "破軍", "科": "武曲", "忌": "太陽"},
    "乙": {"祿": "天機", "權": "天梁", "科": "紫微", "忌": "太陰"},
    "丙": {"祿": "天同", "權": "天機", "科": "文昌", "忌": "廉貞"},
    "丁": {"祿": "太陰", "權": "天同", "科": "天機", "忌": "巨門"},
    "戊": {"祿": "貪狼", "權": "太陰", "科": "右弼", "忌": "天機"},
    "己": {"祿": "武曲", "權": "貪狼", "科": "天梁", "忌": "文曲"},
    "庚": {"祿": "太陽", "權": "武曲", "科": "太陰", "忌": "天同"},
    "辛": {"祿": "巨門", "權": "太陽", "科": "文曲", "忌": "文昌"},
    "壬": {"祿": "天梁", "權": "紫微", "科": "左輔", "忌": "武曲"},
    "癸": {"祿": "破軍", "權": "巨門", "科": "太陰", "忌": "貪狼"},
}

LU_CUN = {"甲": "寅", "乙": "卯", "丙": "巳", "戊": "巳", "丁": "午", "己": "午", "庚": "申", "辛": "酉", "壬": "亥", "癸": "子"}
KUI_YUE = {
    "甲": ("丑", "未"), "戊": ("丑", "未"), "庚": ("丑", "未"),
    "乙": ("子", "申"), "己": ("子", "申"),
    "丙": ("亥", "酉"), "丁": ("亥", "酉"),
    "辛": ("午", "寅"),
    "壬": ("卯", "巳"), "癸": ("卯", "巳"),
}
CHANG_SHENG_START = {"水": "申", "土": "申", "木": "亥", "火": "寅", "金": "巳"}
CHANG_SHENG = ["長生", "沐浴", "冠帶", "臨官", "帝旺", "衰", "病", "死", "墓", "絕", "胎", "養"]
SUI_JIAN = ["太歲", "晦氣", "喪門", "貫索", "官符", "小耗", "歲破", "龍德", "白虎", "天德", "弔客", "病符"]
BO_SHI = ["博士", "力士", "青龍", "小耗", "將軍", "奏書", "飛廉", "喜神", "病符", "大耗", "伏兵", "官府"]


def branch_idx(branch: str) -> int:
    return BRANCHES.index(branch)


def add_star(palaces: Dict[str, dict], branch_index: int, star: str, field: str = "副星") -> None:
    branch = BRANCHES[branch_index % 12]
    palaces[branch].setdefault(field, [])
    # 加上亮度標籤
    star_with_brightness = star
    if star in STAR_BRIGHTNESS:
        brightness = STAR_BRIGHTNESS[star][branch_index % 12]
        star_with_brightness = f"{star}[{brightness}]"
    
    if star_with_brightness not in palaces[branch][field] and star not in [s.split('[')[0] for s in palaces[branch][field]]:
        palaces[branch][field].append(star_with_brightness)


def palace_ganzhi(year_stem: str, branch: str) -> str:
    start_stem_idx = ((STEMS.index(year_stem) % 5) * 2 + 2) % 10
    offset = (branch_idx(branch) - branch_idx("寅")) % 12
    return STEMS[(start_stem_idx + offset) % 10] + branch


def get_ming_shen(lunar_month: int, hour_branch_index: int) -> tuple[int, int]:
    ming_idx = (branch_idx("寅") + lunar_month - 1 - hour_branch_index) % 12
    shen_idx = (branch_idx("寅") + lunar_month - 1 + hour_branch_index) % 12
    return ming_idx, shen_idx


def get_ziwei_position(lunar_day: int, ju_number: int) -> int:
    quotient = (lunar_day + ju_number - 1) // ju_number
    added = quotient * ju_number - lunar_day
    base = (branch_idx("寅") + quotient - 1) % 12
    return (base + added) % 12 if added % 2 == 0 else (base - added) % 12


def get_tianfu_position(ziwei_idx: int) -> int:
    return (branch_idx("辰") - ziwei_idx) % 12


def build_ziwei_chart(year: int, month: int, day: int, hour: int, minute: int, gender_text: str = "乾造") -> dict:
    solar = Solar.fromYmdHms(year, month, day, hour, minute, 0)
    lunar = solar.getLunar()
    lunar_month = abs(lunar.getMonth())
    lunar_day = lunar.getDay()
    hour_idx = ((hour + 1) % 24) // 2
    year_stem = lunar.getYearGan()
    year_branch = lunar.getYearZhi()

    ming_idx, shen_idx = get_ming_shen(lunar_month, hour_idx)
    palaces: Dict[str, dict] = {}
    for i, palace_name in enumerate(PALACE_ORDER):
        idx = (ming_idx - i) % 12
        branch = BRANCHES[idx]
        gz = palace_ganzhi(year_stem, branch)
        palaces[branch] = {
            "宮位": f"【身】{palace_name}" if idx == shen_idx else palace_name,
            "宮干": gz,
            "主星": [],
            "副星": [],
            "吉煞": [],
            "煞吉": [],
            "四化": [],
            "大限": "",
            "博士": "",
            "長生": "",
            "歲建": "",
        }

    ming_gz = palaces[BRANCHES[ming_idx]]["宮干"]
    element = NAYIN_ELEMENT[ming_gz]
    ju_number = JU_BY_ELEMENT[element]
    nature = JU_NAME_BY_ELEMENT[element]

    ziwei_idx = get_ziwei_position(lunar_day, ju_number)
    main_positions = {
        "紫微": ziwei_idx,
        "天機": ziwei_idx - 1,
        "太陽": ziwei_idx - 3,
        "武曲": ziwei_idx - 4,
        "天同": ziwei_idx - 5,
        "廉貞": ziwei_idx - 8,
    }
    tianfu_idx = get_tianfu_position(ziwei_idx)
    main_positions.update({
        "天府": tianfu_idx,
        "太陰": tianfu_idx + 1,
        "貪狼": tianfu_idx + 2,
        "巨門": tianfu_idx + 3,
        "天相": tianfu_idx + 4,
        "天梁": tianfu_idx + 5,
        "七殺": tianfu_idx + 6,
        "破軍": tianfu_idx + 10,
    })
    for star, idx in main_positions.items():
        add_star(palaces, idx, star, "主星")

    # 月系與時系輔星
    add_star(palaces, branch_idx("辰") + lunar_month - 1, "左輔", "吉煞")
    add_star(palaces, branch_idx("戌") - (lunar_month - 1), "右弼", "吉煞")
    add_star(palaces, branch_idx("戌") - hour_idx, "文昌", "吉煞")
    add_star(palaces, branch_idx("辰") + hour_idx, "文曲", "吉煞")
    add_star(palaces, branch_idx("亥") + hour_idx, "地劫", "副星")
    add_star(palaces, branch_idx("亥") - hour_idx, "地空", "副星")

    lu_idx = branch_idx(LU_CUN[year_stem])
    add_star(palaces, lu_idx, "祿存", "吉煞")
    add_star(palaces, lu_idx + 1, "擎羊", "吉煞")
    add_star(palaces, lu_idx - 1, "陀羅", "吉煞")

    kui, yue = KUI_YUE[year_stem]
    add_star(palaces, branch_idx(kui), "天魁", "吉煞")
    add_star(palaces, branch_idx(yue), "天鉞", "吉煞")

    horse_group = {
        "寅午戌": "申", "申子辰": "寅", "巳酉丑": "亥", "亥卯未": "巳"
    }
    for group, horse in horse_group.items():
        if year_branch in group:
            add_star(palaces, branch_idx(horse), "天馬", "副星")
            break

    red_idx = (branch_idx("卯") - branch_idx(year_branch)) % 12
    add_star(palaces, red_idx, "紅鸞", "副星")
    add_star(palaces, red_idx + 6, "天喜", "副星")

    # 四化依生年干標記在對應星曜所在宮位。
    for transform, star in FOUR_TRANSFORMS[year_stem].items():
        for branch, palace in palaces.items():
            found = False
            for s_field in ["主星", "吉煞", "副星"]:
                for s in palace[s_field]:
                    if s.startswith(star):
                        palace["四化"].append(f"{star}化{transform}")
                        found = True
                        break
                if found: break

    forward = (year_stem in {"甲", "丙", "戊", "庚", "壬"} and "男" in gender_text) or (year_stem in {"乙", "丁", "己", "辛", "癸"} and "女" in gender_text)
    for i in range(12):
        idx = (ming_idx + i) % 12 if forward else (ming_idx - i) % 12
        start_age = ju_number + i * 10
        palaces[BRANCHES[idx]]["大限"] = f"{start_age}-{start_age + 9}"

    chang_start = branch_idx(CHANG_SHENG_START[element])
    sui_start = branch_idx(year_branch)
    for i in range(12):
        branch = BRANCHES[i]
        palaces[branch]["長生"] = CHANG_SHENG[(i - chang_start) % 12]
        palaces[branch]["歲建"] = SUI_JIAN[(i - sui_start) % 12]
        palaces[branch]["博士"] = BO_SHI[(i - lu_idx) % 12]
        palaces[branch]["煞吉"] = " ".join(palaces[branch]["吉煞"])
        palaces[branch]["主星"] = " ".join(palaces[branch]["主星"])
        palaces[branch]["副星"] = " ".join(palaces[branch]["副星"])
        palaces[branch]["吉煞"] = " ".join(palaces[branch]["吉煞"])
        palaces[branch]["四化文字"] = " ".join(palaces[branch]["四化"])

    return {
        "palaces": palaces,
        "nature": nature,
        "ming_branch": BRANCHES[ming_idx],
        "body_branch": BRANCHES[shen_idx],
        "lunar_month": lunar_month,
        "lunar_day": lunar_day,
        "lunar_hour": BRANCHES[hour_idx],
        "lunar_txt": f"{lunar.getYearInGanZhi()}年 {lunar.getMonthInChinese()}月{lunar.getDayInChinese()}日",
        "year_stem": year_stem,
        "year_branch": year_branch,
        "is_leap_month": lunar.getMonth() < 0,
        "algorithm_note": "十四主星、命身宮、五行局、大限、常用輔煞與生年四化依傳統通行公式動態安星；細部小星可依流派再擴充。",
    }


def palace_to_compact_html(palace: dict, branch: str) -> str:
    main = palace.get("主星") or "--"
    aux = palace.get("煞吉") or palace.get("副星") or ""
    transforms = palace.get("四化文字", "")
    return (
        f"{branch}宮<br/>"
        f"<span style='color:#718096;font-size:0.8rem'>【{palace['宮位']}】 {palace['大限']}</span><br/>"
        f"<span style='color:#e2e8f0;font-weight:bold'>{main}</span><br/>"
        f"<span style='color:#d4af37;font-size:0.75rem'>{transforms}</span><br/>"
        f"<span style='color:#a0aec0;font-size:0.72rem'>{aux}</span>"
    )


def transform_badges(text: str) -> str:
    html = ""
    for item in text.split():
        if item.endswith("化祿"):
            html += f"<span class='badge-zw m-lu'>{item[-1]}</span>"
        elif item.endswith("化權"):
            html += f"<span class='badge-zw m-quan'>{item[-1]}</span>"
        elif item.endswith("化科"):
            html += f"<span class='badge-zw m-ke'>{item[-1]}</span>"
        elif item.endswith("化忌"):
            html += f"<span class='badge-zw m-ji'>{item[-1]}</span>"
    return html
