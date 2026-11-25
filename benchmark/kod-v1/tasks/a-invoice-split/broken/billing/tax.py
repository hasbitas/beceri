"""Tax arithmetic; rates are expressed in basis points (1/100 of a percent)."""

from billing.money import round_div


def line_tax(taxable, rate_bp):
    return round_div(taxable * rate_bp, 10000)


def tax_by_rate(taxes, rates):
    totals = {}
    for tax, rate in zip(taxes, rates):
        totals[rate] = totals.get(rate, 0) + tax
    return {rate: totals[rate] for rate in sorted(totals)}
