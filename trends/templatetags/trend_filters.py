from django import template

register = template.Library()


@register.filter
def format_views(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return '—'
    if value == 0:
        return '—'
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f}B"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return str(value)


@register.filter
def score_width(score, max_score):
    try:
        result = (float(score) / float(max_score)) * 100
        return round(min(100, max(0, result)), 1)
    except (TypeError, ValueError, ZeroDivisionError):
        return 0
