"""Integer money arithmetic (all amounts are integer cents)."""


def _is_int(value):
    return type(value) is int


def round_div(n, d):
    if not _is_int(n) or not _is_int(d):
        raise TypeError('round_div needs ints')
    if d <= 0:
        raise ValueError('divisor must be positive')
    return (2 * n + d) // (2 * d)


def round_to(n, step):
    return round_div(n, step) * step


def allocate(total, weights):
    if not _is_int(total):
        raise TypeError('total must be an int')
    if type(weights) not in (list, tuple):
        raise TypeError('weights must be a list or tuple')
    if not all(_is_int(weight) for weight in weights):
        raise TypeError('weights must be ints')
    if any(weight < 0 for weight in weights):
        raise ValueError('weights must not be negative')
    weight_sum = sum(weights)
    if weight_sum == 0:
        raise ValueError('weights must not sum to zero')
    magnitude = abs(total)
    shares = [magnitude * weight // weight_sum for weight in weights]
    leftover = magnitude - sum(shares)
    order = sorted(range(len(weights)), key=lambda i: (-(magnitude * weights[i] % weight_sum), -i))
    for index in order[:leftover]:
        shares[index] += 1
    return shares if total >= 0 else [-share for share in shares]
