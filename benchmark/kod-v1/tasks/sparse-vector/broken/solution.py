"""Sparse integer vector arithmetic."""


def _validate(vector):
    if type(vector) is not dict:
        raise TypeError("vectors must be built-in dicts")
    for index, value in vector.items():
        if type(index) is not int:
            raise TypeError("indices must be built-in ints")
        if index < 0:
            raise ValueError("indices must be nonnegative")
        if type(value) is not int:
            raise TypeError("coefficients must be built-in ints")


def add(a, b):
    _validate(a)
    _validate(b)
    result = {index: value for index, value in a.items() if value != 0}
    for index, value in b.items():
        if value != 0:
            result[index] = result.get(index, 0) + value
    return result


def dot(a, b):
    _validate(a)
    _validate(b)
    if len(a) > len(b):
        a, b = b, a
    return sum(value * b.get(index, 0) for index, value in a.items())
