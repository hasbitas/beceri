import unittest
from fractions import Fraction

from units.convert import convert, convert_steps
from units.registry import Registry


def make_registry():
    reg = Registry()
    reg.base('m', 'length')
    reg.define('km', 1000, 'm')
    reg.define('cm', Fraction(1, 100), 'm')
    reg.define('mm', Fraction(1, 10), 'cm')
    reg.base('u', 'toy')
    reg.define('h', Fraction(1, 2), 'u')
    reg.define('d', Fraction(1, 10), 'u')
    return reg


class VisibleUnitTests(unittest.TestCase):
    def test_chained_definitions_compose(self):
        reg = make_registry()
        self.assertEqual(reg.factor('mm'), Fraction(1, 1000))
        self.assertEqual(reg.dimension('mm'), 'length')
        self.assertEqual(convert(reg, 5, 'km', 'cm'), Fraction(500000))
        self.assertEqual(convert(reg, 1, 'km', 'mm'), Fraction(1000000))
        self.assertEqual(reg.names(), ['m', 'km', 'cm', 'mm', 'u', 'h', 'd'])

    def test_every_step_is_rounded(self):
        reg = make_registry()
        self.assertEqual(convert_steps(reg, 3, ['h', 'u', 'h'], 0), Fraction(4))
        self.assertEqual(convert_steps(reg, 3, ['h', 'u'], 0), Fraction(2))
        self.assertIsInstance(convert_steps(reg, 3, ['h', 'u'], 0), Fraction)

    def test_rejects_bad_input(self):
        reg = make_registry()
        with self.assertRaises(TypeError):
            convert(reg, 1.5, 'm', 'cm')
        with self.assertRaises(ValueError):
            convert(reg, 1, 'm', 'h')
        with self.assertRaises(ValueError):
            convert(reg, 1, 'm', 'parsec')
        with self.assertRaises(ValueError):
            reg.define('m', 2, 'cm')
