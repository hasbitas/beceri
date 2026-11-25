def format_try(cents):
    sign = '-' if cents < 0 else ''
    amount = abs(cents) / 100
    formatted = f'{amount:,.2f}'
    formatted = formatted.replace(',', '_').replace('.', ',').replace('_', '.')
    return sign + formatted + ' TL'
