"""Validated letter-grade assignment."""

import math


def letters(scores, thresholds):
    if type(thresholds) is not dict:
        raise TypeError("thresholds must be a dict")
    if set(thresholds) != {"A", "B", "C", "D"}:
        raise ValueError("expected A, B, C, D")
    cuts = [thresholds[g] for g in "ABCD"]
    if any(type(cut) is not int for cut in cuts):
        raise TypeError("thresholds must be integers")
    if any(not 0 <= cut <= 100 for cut in cuts):
        raise ValueError("threshold out of range")
    if any(left <= right for left, right in zip(cuts, cuts[1:])):
        raise ValueError("thresholds must strictly decrease")
    if type(scores) not in (list, tuple):
        raise TypeError("scores must be a list or tuple")
    result = []
    for score in scores:
        if type(score) not in (int, float):
            raise TypeError("score must be an int or float")
        if type(score) is float and not math.isfinite(score):
            raise ValueError("score must be finite")
        if not 0 <= score <= 100:
            raise ValueError("score out of range")
        rounded = round(score)
        grade = "F"
        for label, cut in zip("ABCD", cuts):
            if rounded >= cut:
                grade = label
                break
        result.append(grade)
    return result
