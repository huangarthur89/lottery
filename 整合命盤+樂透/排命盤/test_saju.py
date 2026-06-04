import unittest
from saju import calculate_saju, get_solar_longitude

class TestSaju(unittest.TestCase):
    def test_2000_01_01(self):
        # 2000-01-01 12:00 Seoul
        # 己卯年 丙子月 戊午日 戊午時
        chart = calculate_saju(2000, 1, 1, 12, 0, timezone_name="Asia/Seoul")
        self.assertEqual(chart.year_pillar, "己卯")
        self.assertEqual(chart.month_pillar, "丙子")
        self.assertEqual(chart.day_pillar, "戊午")
        self.assertEqual(chart.hour_pillar, "戊午")

    def test_lichun_transition(self):
        # 2000-02-04 12:00 Seoul 剛好是立春附近，黃經約 314.59，還沒立春
        chart_before = calculate_saju(2000, 2, 4, 12, 0)
        self.assertEqual(chart_before.year_pillar, "己卯")
        self.assertEqual(chart_before.month_pillar, "丁丑")
        
        # 2000-02-05 應該立春了
        chart_after = calculate_saju(2000, 2, 5, 12, 0)
        self.assertEqual(chart_after.year_pillar, "庚辰")
        self.assertEqual(chart_after.month_pillar, "戊寅")

    def test_zi_hour(self):
        # 2000-01-01 23:30 Seoul (day_boundary="zi")
        # 應該進到下一天的日子
        chart = calculate_saju(2000, 1, 1, 23, 30, day_boundary="zi")
        # 1/1 是 戊午，下一天是 己未
        self.assertEqual(chart.day_pillar, "己未")
        # 甲己起甲子
        self.assertEqual(chart.hour_pillar, "甲子")

    def test_1971_reference_case(self):
        chart = calculate_saju(1971, 9, 30, 4, 0, gender="M", timezone_name="Asia/Taipei")
        self.assertEqual(chart.year_pillar, "辛亥")
        self.assertEqual(chart.month_pillar, "丁酉")
        self.assertEqual(chart.day_pillar, "戊午")
        self.assertEqual(chart.hour_pillar, "甲寅")
        self.assertEqual(chart.as_dict()["大運方向"], "逆推")

    def test_zi_boundary_does_not_shift_daewun_start(self):
        chart_zi = calculate_saju(1971, 9, 30, 23, 30, gender="M", timezone_name="Asia/Taipei", day_boundary="zi")
        chart_none = calculate_saju(1971, 9, 30, 23, 30, gender="M", timezone_name="Asia/Taipei", day_boundary="none")

        self.assertNotEqual(chart_zi.day_pillar, chart_none.day_pillar)
        self.assertAlmostEqual(chart_zi.start_age, chart_none.start_age, places=9)
        self.assertEqual(chart_zi.as_dict()["交運日期"], chart_none.as_dict()["交運日期"])

    def test_start_age_has_professional_detail(self):
        chart = calculate_saju(1971, 9, 30, 4, 0, gender="M", timezone_name="Asia/Taipei")
        data = chart.as_dict()

        self.assertIn("年", data["起運歲數_詳細"])
        self.assertRegex(data["交運日期"], r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")

if __name__ == '__main__':
    unittest.main()
