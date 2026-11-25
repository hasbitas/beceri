import math


def moving_average(values, window, partial=False):
    if type(window) is not int:
        raise TypeError('window must be an int')
    if window <= 0:
        raise ValueError('window must be positive')
    if type(partial) is not bool:
        raise TypeError('partial must be a bool')

    numbers = []
    for value in values:
        if type(value) not in (int, float):
            raise TypeError('values must contain ints or floats')
        number = float(value)
        if not math.isfinite(number):
            raise ValueError('values must be finite')
        numbers.append(number)

    result = []
    for end in range(1, len(numbers) + 1):
        start = max(0, end - window)
        count = end - start
        if partial or count == window:
            result.append(math.fsum(numbers[start:end]) / count)
    return result
