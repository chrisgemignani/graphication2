
import unittest

from graphication.series import Series

class SeriesTest(unittest.TestCase):

    def createSeries(self):
        return Series("Test Series", {
            1: 4.5,
            2.5: 5,
            88: 4.25,
            -4: 3,
            7: 12.125,
        })

    def createEmptySeries(self):
        return Series("Empty Series", {})

    def test_iterators(self):
        "Are we getting the right key and value sequences?"
        series = self.createSeries()
        self.assertEqual(
            series.keys(),
            [-4, 1, 2.5, 7, 88],
        )
        self.assertEqual(
            series.values(),
            [3, 4.5, 5, 12.125, 4.25],
        )
        series = self.createEmptySeries()
        self.assertEqual(
            series.keys(),
            [],
        )
        self.assertEqual(
            series.values(),
            [],
        )


    def test_ranges(self):
        "Are the ranges coming out right?"
        series = self.createSeries()
        self.assertEqual(
            series.key_range(),
            (-4, 88),
        )
        self.assertEqual(
            series.value_range(),
            (3, 12.125),
        )
        series = self.createEmptySeries()
        self.assertEqual(
            series.key_range(),
            (None, None),
        )
        self.assertEqual(
            series.value_range(),
            (None, None),
        )


    def test_interpolation(self):
        "Interpolation should work, linearly, and extrapolation constantly"
        series = self.createSeries()
        self.assertEqual(series.interpolate(0), 4.2)
        self.assertEqual(series.interpolate(-3), 3.3)
        self.assertEqual(series.interpolate(-4), 3)
        self.assertEqual(series.interpolate(-7), 3)
        self.assertEqual(series.interpolate(424324.5), 4.25)


    def test_style(self):
        "Ensure series styles work correctly"
        series = Series(
            "Test",
            {0:1,1:2,2:3,3:4},
            styles={
                0: Series.STYLE_NONE,
                2: Series.STYLE_DASHED,
            },
        )
        self.assertEqual(series.style_at(0), Series.STYLE_NONE)
        self.assertEqual(series.style_at(1), Series.STYLE_NONE)
        self.assertEqual(series.style_at(2), Series.STYLE_DASHED)
        self.assertEqual(series.style_at(3), Series.STYLE_DASHED)