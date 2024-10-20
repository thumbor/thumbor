#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com


class FocalPoint:
    ALIGNMENT_PERCENTAGES = {
        "left": 0.0,
        "center": 0.5,
        "right": 1.0,
        "top": 0.0,
        "middle": 0.5,
        "bottom": 1.0,
    }

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.weight,
            "height": self.height,
            "width": self.width,
            "origin": self.origin,
        }

    @classmethod
    def from_dict(cls, values):
        return cls(
            x=int(values["x"]),
            y=int(values["y"]),
            weight=int(values["z"]),
            width=int(values.get("width", 1)),
            height=int(values.get("height", 1)),
            origin=values.get("origin", "alignment"),
        )

    def __init__(  # pylint: disable=too-many-positional-arguments
        self,
        x,  # pylint: disable=invalid-name
        y,  # pylint: disable=invalid-name
        height=1,
        width=1,
        weight=1.0,
        origin="alignment",
    ):
        self.x = int(x)  # pylint: disable=invalid-name
        self.y = int(y)  # pylint: disable=invalid-name
        self.height = int(height)
        self.width = int(width)
        self.weight = weight
        self.origin = origin

    @classmethod
    def from_square(  # pylint: disable=too-many-positional-arguments
        cls, x, y, width, height, origin="detection"
    ):  # pylint: disable=invalid-name
        center_x = x + width // 2
        center_y = y + height // 2
        return cls(
            center_x,
            center_y,
            height=height,
            width=width,
            weight=width * height,
            origin=origin,
        )

    @classmethod
    def from_alignment(cls, halign, valign, width, height):
        x_coord = width * cls.ALIGNMENT_PERCENTAGES[halign]
        y_coord = height * cls.ALIGNMENT_PERCENTAGES[valign]

        return cls(x_coord, y_coord)

    def __repr__(self):
        return (
            f"FocalPoint(x: {self.x}, y: {self.y}, width: {self.width}, "
            f"height: {self.height}, weight: {self.weight:.0f}, origin: {self.origin})"
        )
