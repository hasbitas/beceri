"""Conversions between units of one registry."""

from units.fmt import quantize, to_fraction


def _lookup(registry, name):
    if type(name) is not str:
        raise TypeError('unit name must be a str')
    try:
        return registry.dimension(name), registry.factor(name)
    except KeyError:
        raise ValueError('unknown unit: ' + name) from None


def convert(registry, value, src, dst):
    amount = to_fraction(value)
    src_dimension, src_factor = _lookup(registry, src)
    dst_dimension, dst_factor = _lookup(registry, dst)
    if src_dimension != dst_dimension:
        raise ValueError('dimension mismatch')
    return amount * src_factor / dst_factor


def convert_steps(registry, value, units, places):
    current = to_fraction(value)
    if type(units) not in (list, tuple):
        raise TypeError('units must be a list or tuple')
    if len(units) < 2:
        raise ValueError('at least two units are needed')
    quantize(0, places)
    for src, dst in zip(units, units[1:]):
        current = convert(registry, current, src, dst)
    return quantize(current, places)
