import unittest
from fractions import Fraction

from units.convert import convert, convert_steps
from units.fmt import format_decimal, quantize, to_fraction
from units.registry import Registry


def make_registry():
    reg = Registry()
    reg.base('m', 'length')
    reg.define('km', '1000', 'm')
    reg.define('mi', '1.609344', 'km')
    reg.define('ft', '0.3048', 'm')
    reg.define('in', Fraction(1, 12), 'ft')
    reg.base('kg', 'mass')
    reg.base('u', 'toy')
    reg.define('h', Fraction(1, 2), 'u')
    reg.define('d', '0.1', 'u')
    return reg


class HiddenUnitTests(unittest.TestCase):
    def test_decimal_strings_are_exact(self):
        reg = make_registry()
        self.assertEqual(convert(reg, '1', 'mi', 'm'), Fraction(1609344, 1000))
        self.assertEqual(convert(reg, 1, 'in', 'm'), Fraction(254, 10000))
        self.assertEqual(reg.factor('mi'), Fraction(1609344, 1000))
        self.assertEqual(to_fraction('0.1'), Fraction(1, 10))
        self.assertEqual(to_fraction('+2.50'), Fraction(5, 2))
        self.assertEqual(to_fraction('-0.5'), Fraction(-1, 2))
        self.assertEqual(to_fraction('007'), Fraction(7))
        self.assertEqual(to_fraction(Fraction(1, 3)), Fraction(1, 3))
        self.assertEqual(to_fraction(-4), Fraction(-4))
        self.assertEqual(convert(reg, '0.1', 'km', 'm'), Fraction(100))

    def test_to_fraction_rejects_other_forms(self):
        for bad in ('', ' 1', '1 ', '1.', '.5', '1e3', 'abc', '1/2', '--1', '+', '1,5', '1.2.3'):
            with self.assertRaises(ValueError, msg=repr(bad)):
                to_fraction(bad)
        for bad in (1.5, True, None, [1], b'1', 1 + 0j):
            with self.assertRaises(TypeError, msg=repr(bad)):
                to_fraction(bad)

    def test_quantize_rounds_ties_away_from_zero(self):
        self.assertEqual(quantize(Fraction(1, 8), 2), Fraction(13, 100))
        self.assertEqual(quantize(Fraction(-1, 8), 2), Fraction(-13, 100))
        self.assertEqual(quantize(Fraction(5, 2), 0), Fraction(3))
        self.assertEqual(quantize(Fraction(-5, 2), 0), Fraction(-3))
        self.assertEqual(quantize(Fraction(9, 2), 0), Fraction(5))
        self.assertEqual(quantize(Fraction(7, 2), 0), Fraction(4))
        self.assertEqual(quantize(Fraction(1, 3), 4), Fraction(3333, 10000))
        self.assertEqual(quantize(Fraction(2, 3), 4), Fraction(6667, 10000))
        self.assertEqual(quantize(7, 3), Fraction(7))
        self.assertEqual(quantize(Fraction(-1, 3), 0), Fraction(0))
        with self.assertRaises(ValueError):
            quantize(1, -1)
        with self.assertRaises(TypeError):
            quantize(1, 1.0)
        with self.assertRaises(TypeError):
            quantize(1, True)

    def test_format_decimal(self):
        self.assertEqual(format_decimal(Fraction(-1, 1000), 2), '0.00')
        self.assertEqual(format_decimal(Fraction(5, 2), 0), '3')
        self.assertEqual(format_decimal(Fraction(-5, 2), 0), '-3')
        self.assertEqual(format_decimal(Fraction(1234567, 1000), 2), '1234.57')
        self.assertEqual(format_decimal(Fraction(7, 100), 3), '0.070')
        self.assertEqual(format_decimal(Fraction(-7, 100), 1), '-0.1')
        self.assertEqual(format_decimal(0, 2), '0.00')
        self.assertEqual(format_decimal(Fraction(1, 8), 2), '0.13')
        self.assertEqual(format_decimal(Fraction(-1, 8), 1), '-0.1')
        self.assertEqual(format_decimal(12, 0), '12')
        with self.assertRaises(ValueError):
            format_decimal(1, -1)
        with self.assertRaises(TypeError):
            format_decimal(1, '2')

    def test_registry_rules_and_validation_order(self):
        reg = make_registry()
        before = reg.names()
        with self.assertRaises(TypeError):
            reg.define(5, 'abc', 'zzz')
        with self.assertRaises(ValueError):
            reg.define('', 1, 'm')
        with self.assertRaises(ValueError):
            reg.define('x', 'abc', 'zzz')
        with self.assertRaises(TypeError):
            reg.define('x', 1.5, 'zzz')
        with self.assertRaises(ValueError):
            reg.define('x', '0', 'm')
        with self.assertRaises(ValueError):
            reg.define('x', -1, 'm')
        with self.assertRaises(ValueError):
            reg.define('x', 0, 'zzz')
        with self.assertRaises(TypeError):
            reg.define('x', 1, 5)
        with self.assertRaises(KeyError):
            reg.define('x', 1, 'zzz')
        with self.assertRaises(KeyError):
            reg.define('m', 1, 'zzz')
        with self.assertRaises(ValueError):
            reg.define('m', 1, 'km')
        with self.assertRaises(TypeError):
            reg.base(1, 'length')
        with self.assertRaises(ValueError):
            reg.base('', 5)
        with self.assertRaises(TypeError):
            reg.base('y', None)
        with self.assertRaises(ValueError):
            reg.base('y', '')
        with self.assertRaises(ValueError):
            reg.base('kg', 'mass')
        self.assertEqual(reg.names(), before)
        with self.assertRaises(KeyError):
            reg.factor('x')
        with self.assertRaises(KeyError):
            reg.dimension('y')
        with self.assertRaises(TypeError):
            reg.factor(3)

    def test_convert_error_kinds_and_order(self):
        reg = make_registry()
        self.assertEqual(convert(reg, 2, 'kg', 'kg'), Fraction(2))
        with self.assertRaises(ValueError):
            convert(reg, 1, 'nope', 'm')
        with self.assertRaises(ValueError):
            convert(reg, 1, 'm', 'nope')
        with self.assertRaises(TypeError):
            convert(reg, 1.5, 'nope', 'm')
        with self.assertRaises(ValueError):
            convert(reg, 'x', 5, 5)
        with self.assertRaises(TypeError):
            convert(reg, True, 'm', 'm')
        with self.assertRaises(TypeError):
            convert(reg, 1, 5, 'm')
        with self.assertRaises(ValueError):
            convert(reg, 1, 'nope', 5)
        with self.assertRaises(TypeError):
            convert(reg, 1, 'm', 5)
        with self.assertRaises(ValueError):
            convert(reg, 1, 'm', 'kg')

    def test_convert_steps_rounding_each_step(self):
        reg = make_registry()
        self.assertEqual(convert_steps(reg, '7', ['d', 'u', 'd'], 0), Fraction(10))
        self.assertEqual(convert_steps(reg, -3, ['h', 'u'], 0), Fraction(-2))
        self.assertEqual(convert_steps(reg, '0.7', ['d', 'u', 'd'], 1), Fraction(1))
        self.assertEqual(convert_steps(reg, 14, ['in', 'ft', 'm'], 2), Fraction(36, 100))
        self.assertEqual(convert_steps(reg, 14, ['in', 'ft', 'm'], 4), Fraction(3556, 10000))
        self.assertEqual(convert_steps(reg, '0.04', ['km', 'm'], 0), Fraction(40))
        self.assertEqual(convert_steps(reg, '0.0004', ['km', 'm'], 0), Fraction(0))
        self.assertEqual(convert_steps(reg, Fraction(1, 3), ['u', 'u'], 2), Fraction(33, 100))
        self.assertEqual(convert_steps(reg, Fraction(1, 3), ('u', 'u', 'u'), 1), Fraction(3, 10))

    def test_convert_steps_validation(self):
        reg = make_registry()
        for error, args in (
            (TypeError, (1.5, ['m', 'km'], 0)),
            (ValueError, ('x', 5, 0)),
            (TypeError, (1, 'mm', 0)),
            (TypeError, (1, {'m': 1, 'km': 2}, 0)),
            (ValueError, (1, ['m'], 0)),
            (ValueError, (1, [], 0)),
            (ValueError, (1, ['m', 'km'], -1)),
            (TypeError, (1, ['m', 'km'], 1.0)),
            (TypeError, (1, ['m', 'km'], True)),
            (ValueError, (1, ['m', 'kg', 5], 0)),
            (TypeError, (1, ['m', 'km', 5], 0)),
            (ValueError, (1, ['m', 'nope'], 0)),
            (TypeError, (1, ['m', 5], 0)),
            (ValueError, (1, ['m', 'km', 'kg'], 0)),
        ):
            with self.assertRaises(error, msg=repr(args)):
                convert_steps(reg, *args)

    def test_quantize_and_format_accept_only_int_or_fraction(self):
        for func in (quantize, format_decimal):
            for bad in (1.5, 2.0, '2.5', '3', True, False, None, [1], 1 + 0j):
                with self.subTest(func=func.__name__, bad=bad):
                    with self.assertRaises(TypeError):
                        func(bad, 0)
            with self.assertRaises(TypeError):
                func(1.5, -1)
            with self.assertRaises(TypeError):
                func('1', '2')
            with self.assertRaises(TypeError):
                func(1, 1.0)
            with self.assertRaises(ValueError):
                func(1, -1)
        self.assertEqual(quantize(0, 0), Fraction(0))
        self.assertEqual(format_decimal(-3, 1), '-3.0')

    def test_fraction_subclasses_are_accepted(self):
        class Amount(Fraction):
            pass

        self.assertEqual(quantize(Amount(5, 2), 0), Fraction(3))
        self.assertEqual(format_decimal(Amount(5, 2), 0), "3")
        self.assertEqual(to_fraction(Amount(5, 2)), Fraction(5, 2))
