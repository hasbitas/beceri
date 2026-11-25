"""A registry of units defined by chains of exact ratios."""

from fractions import Fraction

from units.fmt import to_fraction


def _check_name(name, what):
    if type(name) is not str:
        raise TypeError(what + ' must be a str')
    if not name:
        raise ValueError(what + ' must not be empty')


class Registry:
    def __init__(self):
        self._units = {}

    def base(self, name, dimension):
        _check_name(name, 'name')
        _check_name(dimension, 'dimension')
        if name in self._units:
            raise ValueError('unit already defined: ' + name)
        self._units[name] = (dimension, Fraction(1))

    def define(self, name, ratio, of):
        _check_name(name, 'name')
        ratio = to_fraction(ratio)
        if ratio < 0:
            raise ValueError('ratio must be positive')
        if type(of) is not str:
            raise TypeError('of must be a str')
        if of not in self._units:
            raise KeyError(of)
        if name in self._units:
            raise ValueError('unit already defined: ' + name)
        dimension, factor = self._units[of]
        self._units[name] = (dimension, ratio * factor)

    def factor(self, name):
        return self._lookup(name)[1]

    def dimension(self, name):
        return self._lookup(name)[0]

    def names(self):
        return list(self._units)

    def _lookup(self, name):
        if type(name) is not str:
            raise TypeError('unit name must be a str')
        if name not in self._units:
            raise KeyError(name)
        return self._units[name]
