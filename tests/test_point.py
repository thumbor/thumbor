# # -*- coding: utf-8 -*-

# # thumbor imaging service
# # https://github.com/thumbor/thumbor/wiki

# # Licensed under the MIT license:
# # http://www.opensource.org/licenses/mit-license
# # Copyright (c) 2011 globo.com thumbor@googlegroups.com

import pytest

from tests.base import TestCase
from thumbor.point import FocalPoint


class FocalPointTestCase(TestCase):
    def test_default_alignment_percentages(self):
        percentages = FocalPoint.ALIGNMENT_PERCENTAGES
        assert percentages["left"] == pytest.approx(0.0)
        assert percentages["center"] == pytest.approx(0.5)
        assert percentages["right"] == pytest.approx(1.0)
        assert percentages["top"] == pytest.approx(0.0)
        assert percentages["middle"] == pytest.approx(0.5)
        assert percentages["bottom"] == pytest.approx(1.0)

    def test_new_point_default_weight(self):
        point = FocalPoint(10, 20)
        assert point.x == 10
        assert point.y == 20

    def test_new_point_weighted(self):
        point = FocalPoint(x=10, y=20, height=1.0, width=3.0, weight=3.0)
        assert point.weight == pytest.approx(3.0)
        assert str(point) == (
            "FocalPoint(x: 10, y: 20, width: 3, height: 1, weight: 3, origin: alignment)"
        )

    def test_new_point_from_dict(self):
        point = FocalPoint.from_dict({"x": 10, "y": 20, "z": 5})
        assert point.x == 10
        assert point.y == 20
        assert point.weight == 5

    def test_new_point_to_dict(self):
        point = FocalPoint.from_dict(
            {"x": 10.1, "y": 20.1, "z": 5.1, "width": 1.1, "height": 1.6}
        )
        assert point.to_dict() == {
            "x": 10,
            "y": 20,
            "z": 5,
            "origin": "alignment",
            "width": 1,
            "height": 1,
        }

    def test_new_point_square_point(self):
        point = FocalPoint.from_square(x=350, y=50, width=110, height=110)
        assert point.x == 405
        assert point.y == 105
        assert point.weight == 12100

    def test_aligned_point_center_middle(self):
        point = FocalPoint.from_alignment("center", "middle", 300, 200)
        assert point.x == 150
        assert point.y == 100
        assert point.weight == pytest.approx(1.0)

    def test_aligned_point_top_left(self):
        point = FocalPoint.from_alignment("left", "top", 300, 200)
        assert point.x == 0
        assert point.y == 0
        assert point.weight == pytest.approx(1.0)

    def test_aligned_point_bottom_right(self):
        point = FocalPoint.from_alignment("right", "bottom", 300, 200)
        assert point.x == 300
        assert point.y == 200
        assert point.weight == pytest.approx(1.0)
