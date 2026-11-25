"""Aggregate completed login sessions."""


def durations(events):
    if type(events) not in (list, tuple):
        raise TypeError('events must be a list or tuple')
    checked = []
    users = set()
    for record in events:
        if type(record) not in (list, tuple):
            raise TypeError('event must be a list or tuple')
        if len(record) != 3:
            raise ValueError('event must have three fields')
        user, action, timestamp = record
        if type(user) is not str or type(action) is not str or type(timestamp) is not int:
            raise TypeError('invalid field type')
        if not user or action not in ('login', 'logout'):
            raise ValueError('invalid user or action')
        checked.append((user, action, timestamp))
        users.add(user)
    totals = dict.fromkeys(sorted(users), 0)
    active = {}
    for user, action, timestamp in sorted(checked, key=lambda event: event[2]):
        if action == 'login':
            if user not in active:
                active[user] = timestamp
        elif user in active:
            totals[user] += timestamp - active.pop(user)
    return totals
