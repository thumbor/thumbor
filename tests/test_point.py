# #!/usr/bin/python
# # -*- coding: utf-8 -*-

# # thumbor imaging service
# # https://github.com/thumbor/thumbor/wiki

# # Licensed under the MIT license:
# # http://www.opensource.org/licenses/mit-license
# # Copyright (c) 2011 globo.com thumbor@googlegroups.com

from preggy import expect

from tests.base import TestCase
from thumbor.point import FocalPoint


class FocalPointTestCase(TestCase):
    def test_default_alignment_percentages(self):
        percentages = FocalPoint.ALIGNMENT_PERCENTAGES
        expect(percentages["left"]).to_equal(0.0)
        expect(percentages["center"]).to_equal(0.5)
        expect(percentages["right"]).to_equal(1.0)
        expect(percentages["top"]).to_equal(0.0)
        expect(percentages["middle"]).to_equal(0.5)
        expect(percentages["bottom"]).to_equal(1.0)

    def test_new_point_default_weight(self):
        point = FocalPoint(10, 20)
        expect(point.x).to_equal(10)
        expect(point.y).to_equal(20)

    def test_new_point_weighted(self):
        point = FocalPoint(x=10, y=20, height=1.0, width=3.0, weight=3.0)
        expect(point.weight).to_equal(3.0)
        expect(str(point)).to_equal(
            "FocalPoint(x: 10, y: 20, width: 3, height: 1, weight: 3, origin: alignment)"
        )

    def test_new_point_from_dict(self):
        point = FocalPoint.from_dict({"x": 10, "y": 20, "z": 5})
        expect(point.x).to_equal(10)
        expect(point.y).to_equal(20)
        expect(point.weight).to_equal(5)

    def test_new_point_to_dict(self):
        point = FocalPoint.from_dict(
            {"x": 10.1, "y": 20.1, "z": 5.1, "width": 1.1, "height": 1.6}
        )
        expect(point.to_dict()).to_be_like(
            {
                "x": 10,
                "y": 20,
                "z": 5,
                "origin": "alignment",
                "width": 1,
                "height": 1,
            }
        )

    def test_new_point_square_point(self):
        point = FocalPoint.from_square(x=350, y=50, width=110, height=110)
        expect(point.x).to_equal(405)
        expect(point.y).to_equal(105)
        expect(point.weight).to_equal(12100)

    def test_aligned_point_center_middle(self):
        point = FocalPoint.from_alignment("center", "middle", 300, 200)
        expect(point.x).to_equal(150)
        expect(point.y).to_equal(100)
        expect(point.weight).to_equal(1.0)

    def test_aligned_point_top_left(self):
        point = FocalPoint.from_alignment("left", "top", 300, 200)
        expect(point.x).to_equal(0)
        expect(point.y).to_equal(0)
        expect(point.weight).to_equal(1.0)

    def test_aligned_point_bottom_right(self):
        point = FocalPoint.from_alignment("right", "bottom", 300, 200)
        expect(point.x).to_equal(300)
        expect(point.y).to_equal(200)
        expect(point.weight).to_equal(1.0)
