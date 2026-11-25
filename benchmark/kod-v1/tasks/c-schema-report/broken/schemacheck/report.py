"""Plain-text reporting of validation issues."""

from .schema import Issue


def format_path(path):
    text = "$"
    for segment in path:
        if isinstance(segment, int):
            text += "[%d]" % segment
        else:
            text += "." + segment
    return text


def _segment_key(segment):
    if isinstance(segment, int):
        return (0, segment, "")
    return (1, 0, segment)


def _sort_key(issue):
    return (format_path(issue.path), issue.code)


def ordered(issues):
    distinct = [Issue(tuple(issue.path), issue.code) for issue in issues]
    return sorted(distinct, key=_sort_key)


def counts(issues):
    tally = {}
    for issue in ordered(issues):
        tally[issue.code] = tally.get(issue.code, 0) + 1
    return dict(sorted(tally.items()))


def render(issues):
    items = ordered(issues)
    if not items:
        return "ok\n"
    lines = ["%s: %s" % (format_path(issue.path), issue.code) for issue in items]
    lines.append("-- %d issue%s" % (len(items), "" if len(items) == 1 else "s"))
    return "\n".join(lines) + "\n"
