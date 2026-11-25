"""Billing periods that repeat every `step` months from an anchor date."""

import fractions

from .months import add_months, ensure_date, ensure_int, whole_months_between


def _check_step(step):
    ensure_int(step, "step")
    if step < 1:
        raise ValueError("step must be at least 1")


def billing_periods(anchor, count, step=1):
    ensure_date(anchor, "anchor")
    ensure_int(count, "count")
    _check_step(step)
    if count < 0:
        raise ValueError("count must not be negative")
    periods = []
    start = anchor
    for _ in range(count):
        end = add_months(start, step)
        periods.append((start, end))
        start = end
    return periods


def period_of(anchor, step, day):
    ensure_date(anchor, "anchor")
    ensure_date(day, "day")
    _check_step(step)
    if day < anchor:
        raise ValueError("day is before the anchor")
    index = whole_months_between(anchor, day) // step
    return index, (add_months(anchor, index * step), add_months(anchor, (index + 1) * step))


def next_due(anchor, step, today):
    ensure_date(anchor, "anchor")
    ensure_date(today, "today")
    _check_step(step)
    if today <= anchor:
        return anchor
    return period_of(anchor, step, today)[1][1]


def prorate(anchor, step, day):
    index, (start, end) = period_of(anchor, step, day)
    return fractions.Fraction((end - day).days, (end - start).days)
