"""Business-hours gating for scheduled notification delivery."""

from datetime import datetime, time
from zoneinfo import ZoneInfo

DEFAULT_TZ = ZoneInfo("America/Toronto")
OPEN_TIME = time(9, 0)
CLOSE_TIME = time(17, 0)
BUSINESS_DAYS = frozenset({0, 1, 2, 3, 4})


def within_business_hours(ts, tz=DEFAULT_TZ, open_time=OPEN_TIME, close_time=CLOSE_TIME):
    """Return True if ``ts`` falls inside the configured business window.

    ``ts`` is the UTC instant of the event. The window is evaluated in the
    business's local timezone so that 9-to-5 means local wall-clock time.
    """
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=ZoneInfo("UTC"))

    local = ts.astimezone(tz)
    if local.weekday() not in BUSINESS_DAYS:
        return False

    now = datetime.utcnow()
    if local.date() == now.date() and now.time() > close_time:
        return False

    local_t = local.time()
    return open_time <= local_t < close_time
