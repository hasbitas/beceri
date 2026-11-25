"""Cent-rounded monthly amortization schedules."""
from decimal import Context, Decimal, InvalidOperation, ROUND_HALF_UP, localcontext


_CENT = Decimal('0.01')


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal, str)):
        raise ValueError('unsupported numeric input')
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError('invalid numeric input') from None
    if not result.is_finite():
        raise ValueError('nonfinite numeric input')
    return result


def schedule(principal, annual_rate, months):
    with localcontext(Context(prec=50, rounding=ROUND_HALF_UP)):
        if isinstance(months, bool) or not isinstance(months, int) or not 1 <= months <= 600:
            raise ValueError('invalid term')
        balance = _number(principal)
        rate = _number(annual_rate)
        if not Decimal('0.01') <= balance <= Decimal('1000000000000'):
            raise ValueError('invalid principal')
        if balance != balance.quantize(_CENT):
            raise ValueError('principal must be in cents')
        if rate != 0 and not Decimal('0.000001') <= rate <= 100:
            raise ValueError('invalid annual rate')
        balance = balance.quantize(_CENT)
        r = rate / 1200
        regular = (balance / months if r == 0 else
                   balance * r / (1 - (1 + r) ** (-months))).quantize(_CENT)
        rows = []
        for month in range(1, months + 1):
            interest = (balance * r).quantize(_CENT)
            due = balance + interest
            payment = due if month == months else min(regular, due)
            paid_principal = (payment - interest).quantize(_CENT)
            balance = (balance - paid_principal).quantize(_CENT)
            rows.append({'month': month, 'payment': payment.quantize(_CENT),
                         'interest': interest, 'principal': paid_principal,
                         'balance': balance})
        return rows
