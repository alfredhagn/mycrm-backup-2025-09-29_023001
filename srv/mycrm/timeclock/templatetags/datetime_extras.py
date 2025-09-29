from django import template
from django.utils import timezone, dateformat
from django.utils.dateparse import parse_datetime
from datetime import datetime

register = template.Library()

@register.filter
def iso_to_local(value, fmt="d.m.Y H:i"):
    """
    Nimmt ISO-Strings wie '2025-09-02T07:28:43Z' oder bereits Datetime,
    liefert formatierten String in der lokalen TZ (settings.TIME_ZONE).
    """
    if not value:
        return ""
    # schon ein datetime?
    if isinstance(value, datetime):
        dt = value
    else:
        s = str(value).strip().replace("Z", "+00:00")
        dt = parse_datetime(s)
        if dt is None:
            # Fallback: gib Original aus
            return str(value)

    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.utc)
    dt_local = dt.astimezone(timezone.get_current_timezone())
    return dateformat.format(dt_local, fmt)
