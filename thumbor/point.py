#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com


from typing import TypeVar, Type
T = TypeVar('T', bound='FocalPoint')  # pylint: disable=invalid-name


class FocalPoint:
    ALIGNMENT_PERCENTAGES = {
        "left": 0.0,
        "center": 0.5,
        "right": 1.0,
        "top": 0.0,
        "middle": 0.5,
        "bottom": 1.0,
    }

    def to_dict(self: T) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "z": self.weight,
            "height": self.height,
            "width": self.width,
            "origin": self.origin,
        }

    @classmethod
    def from_dict(cls: Type[T], values: dict) -> T:
        return cls(
            x=int(values["x"]),
            y=int(values["y"]),
            weight=int(values["z"]),
            width=int(values.get("width", 1)),
            height=int(values.get("height", 1)),
            origin=values.get("origin", "alignment"),
        )

    def __init__(
        self: T,
        x: float,  # pylint: disable=invalid-name
        y: float,  # pylint: disable=invalid-name
        height: float = 1,
        width: float = 1,
        weight: float = 1.0,
        origin: str = "alignment",
    ) -> None:
        self.x = int(x)  # pylint: disable=invalid-name
        self.y = int(y)  # pylint: disable=invalid-name
        self.height = int(height)
        self.width = int(width)
        self.weight = weight
        self.origin = origin

    @classmethod
    def from_square(
        cls: Type[T],  # pylint: disable=invalid-name
        x: float,  # pylint: disable=invalid-name
        y: float,  # pylint: disable=invalid-name
        width: float,
        height: float,
        origin: str = "detection"
    ) -> T:
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
    def from_alignment(cls: Type[T], halign: str, valign: str, width: float, height: float) -> T:
        x_coord = width * cls.ALIGNMENT_PERCENTAGES[halign]
        y_coord = height * cls.ALIGNMENT_PERCENTAGES[valign]

        return cls(x_coord, y_coord)

    def __repr__(self: T) -> str:
        return (
            f"FocalPoint(x: {self.x}, y: {self.y}, width: {self.width}, "
            f"height: {self.height}, weight: {self.weight:.0f}, origin: {self.origin})"
        )  # pylint: disable=invalid-name
