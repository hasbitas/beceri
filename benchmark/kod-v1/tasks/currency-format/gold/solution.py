def format_try(cents):
    sign = '-' if cents < 0 else ''
    lira, kurus = divmod(abs(cents), 100)
    groups = []
    while lira >= 1000:
        lira, group = divmod(lira, 1000)
        groups.append(f'{group:03d}')
    groups.append(str(lira))
    return sign + '.'.join(reversed(groups)) + f',{kurus:02d} TL'
