import unittest

from ziwei import MAIN_STARS, build_ziwei_chart


class TestZiwei(unittest.TestCase):
    def test_places_all_fourteen_main_stars(self):
        chart = build_ziwei_chart(1971, 9, 30, 4, 0, "乾造 (男)")
        stars = " ".join(p["主星"] for p in chart["palaces"].values()).split()

        self.assertEqual(set(MAIN_STARS), set(stars))
        self.assertEqual(len(stars), len(MAIN_STARS))

    def test_uses_solar_date_to_lunar_conversion(self):
        chart = build_ziwei_chart(1971, 9, 30, 4, 0, "乾造 (男)")

        self.assertEqual(chart["lunar_month"], 8)
        self.assertEqual(chart["lunar_day"], 12)
        self.assertEqual(chart["lunar_hour"], "寅")

    def test_chart_changes_with_birth_data(self):
        chart_a = build_ziwei_chart(1971, 9, 30, 4, 0, "乾造 (男)")
        chart_b = build_ziwei_chart(1976, 6, 20, 6, 0, "陰女")

        self.assertNotEqual(chart_a["ming_branch"], chart_b["ming_branch"])
        self.assertNotEqual(chart_a["nature"], chart_b["nature"])


if __name__ == "__main__":
    unittest.main()
