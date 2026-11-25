"""Progressive income tax in integer minor units."""


def tax(income, brackets):
    if type(income) is not int:
        raise TypeError('income must be an integer')
    if income < 0:
        raise ValueError('negative income')
    if type(brackets) not in (list, tuple):
        raise TypeError('schedule must be a list or tuple')
    if not brackets:
        raise ValueError('empty schedule')
    previous = 0
    for index, entry in enumerate(brackets):
        if type(entry) not in (list, tuple):
            raise TypeError('entry must be a list or tuple')
        if len(entry) != 2:
            raise ValueError('entry must have two fields')
        upper, rate = entry
        if type(rate) is not int:
            raise TypeError('rate must be an integer')
        if not 0 <= rate <= 10000:
            raise ValueError('rate out of range')
        if index == len(brackets) - 1:
            if upper is not None:
                raise ValueError('missing unlimited bracket')
        else:
            if upper is None:
                raise ValueError('unlimited bracket is not last')
            if type(upper) is not int:
                raise TypeError('upper limit must be an integer')
            if upper <= previous:
                raise ValueError('limits must be positive and increasing')
            previous = upper

    total = 0
    lower = 0
    for upper, rate in brackets:
        ceiling = income if upper is None else min(income, upper)
        taxable = max(0, ceiling - lower)
        total += (taxable * rate + 5000) // 10000
        if upper is not None:
            lower = upper
    return total
