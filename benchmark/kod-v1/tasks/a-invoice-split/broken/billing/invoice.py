"""Invoice computation with proportional discounts and per-line tax."""

from billing.money import allocate, round_to
from billing.tax import line_tax, tax_by_rate

_KEYS = {'sku', 'qty', 'unit_price', 'rate_bp'}


def _check_int(name, value, minimum, maximum=None):
    if type(value) is not int:
        raise TypeError(name + ' must be an int')
    if value < minimum or (maximum is not None and value > maximum):
        raise ValueError(name + ' is out of range')


def _check_line(line):
    if type(line) is not dict:
        raise TypeError('line must be a dict')
    if set(line) != _KEYS:
        raise ValueError('line keys must be sku, qty, unit_price, rate_bp')
    if type(line['sku']) is not str:
        raise TypeError('sku must be a str')
    if not line['sku']:
        raise ValueError('sku must not be empty')
    if type(line['qty']) is not int:
        raise TypeError('qty must be an int')
    if line['qty'] == 0:
        raise ValueError('qty must not be zero')
    _check_int('unit_price', line['unit_price'], 0)
    _check_int('rate_bp', line['rate_bp'], 0, 10000)


def build_invoice(lines, discount_cents=0, cash_step=1):
    if type(lines) not in (list, tuple):
        raise TypeError('lines must be a list or tuple')
    for line in lines:
        _check_line(line)
    _check_int('discount_cents', discount_cents, 0)
    _check_int('cash_step', cash_step, 1)
    nets = [line['qty'] * line['unit_price'] for line in lines]
    subtotal = sum(nets)
    if discount_cents and (discount_cents > subtotal or min(nets) < 0):
        raise ValueError('discount cannot be applied')
    shares = allocate(discount_cents, nets) if discount_cents else [0] * len(lines)
    rows = []
    taxes = []
    for line, net, share in zip(lines, nets, shares):
        taxable = net - share
        tax = line_tax(net, line['rate_bp'])
        taxes.append(tax)
        rows.append({'sku': line['sku'], 'net': net, 'discount': share, 'taxable': taxable, 'tax': tax})
    total_tax = sum(taxes)
    total = subtotal - discount_cents + total_tax
    payable = round_to(total, cash_step)
    return {
        'lines': rows,
        'subtotal': subtotal,
        'discount': discount_cents,
        'tax': total_tax,
        'tax_by_rate': tax_by_rate(taxes, [line['rate_bp'] for line in lines]),
        'total': total,
        'rounding': payable - total,
        'payable': payable,
    }
