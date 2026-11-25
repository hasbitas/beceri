"""Signed polygon area with exact validation of binary coordinates."""
from fractions import Fraction
import math


def area(points):
    if type(points) not in (list, tuple):
        raise TypeError('points must be a list or tuple')
    vertices = []
    for point in points:
        if type(point) not in (list, tuple):
            raise TypeError('each point must be a list or tuple')
        if len(point) != 2:
            raise ValueError('each point must have two coordinates')
        for value in point:
            if type(value) not in (int, float):
                raise TypeError('coordinates must be built-in numbers')
            if abs(value) > 1000000000 or not math.isfinite(value):
                raise ValueError('coordinate outside finite range')
        vertices.append(tuple(Fraction(value) for value in point))
    if len(vertices) > 1 and vertices[-1] == vertices[0]:
        vertices.pop()
    if len(vertices) < 3 or len(set(vertices)) != len(vertices):
        raise ValueError('need at least three distinct vertices')
    twice_area = sum(
        x * vertices[(i + 1) % len(vertices)][1]
        - y * vertices[(i + 1) % len(vertices)][0]
        for i, (x, y) in enumerate(vertices)
    )
    if twice_area == 0:
        raise ValueError('degenerate polygon')
    return float(twice_area / 2)
