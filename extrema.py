#!/usr/bin/env python3
"""Earliest sunset, latest sunrise, shortest day, and the PLATEAU width.

Two things this is careful about.

1. SECONDS, not minutes. Around the December extremum the sunset time changes by
   a few seconds a day, so an almanac printed to the minute shows a run of tied
   days and cannot say which is earliest. That is why published "earliest sunset"
   dates disagree: they are reading a flat minimum through a coarse display.

2. THE WINDOW EDGE. The first version searched 2026-11-01 onward and happily
   reported Quito's earliest sunset as 2026-11-02 and its shortest day as
   2026-11-01 — both sitting on the first day it was allowed to look at. An
   extremum found at the edge of a search window is not an extremum, it is the
   edge. This now searches a full year centred on the December solstice and
   REFUSES any extremum within 5 days of either end.
"""
import datetime as dt
import sys

sys.path.insert(0, "/home/scout/studio/sunset-split")
from solar import events, local, local_unwrapped

EDGE_GUARD = 5


def series(lat, lon, tz, start, days):
    out = []
    for i in range(days):
        day = start + dt.timedelta(days=i)
        r, n, s = events(day.year, day.month, day.day, lat, lon)
        if r is None or s is None:
            continue
        out.append((day, local_unwrapped(r, tz), local_unwrapped(n, tz),
                    local_unwrapped(s, tz), s - r))
    return out


def pick(rows, key, want_min, label):
    best = (min if want_min else max)(rows, key=key)
    i = rows.index(best)
    if i < EDGE_GUARD or i >= len(rows) - EDGE_GUARD:
        raise SystemExit(f"  REFUSED: {label} landed {min(i, len(rows)-1-i)} day(s) from the "
                         f"window edge ({best[0]}). Widen the window; an extremum at the "
                         f"edge is the edge.")
    return best


def fmt(minutes):
    """Wrap for display only; the comparisons upstream are unwrapped."""
    t = round((minutes % 1440.0) * 60)
    return f"{t//3600:02d}:{t%3600//60:02d}:{t%60:02d}"


def report(name, lat, lon, tz):
    # a full year with the December solstice in the middle
    rows = series(lat, lon, tz, dt.date(2026, 6, 23), 365)
    e_set = pick(rows, lambda x: x[3], True, "earliest sunset")
    l_rise = pick(rows, lambda x: x[1], False, "latest sunrise")
    short = pick(rows, lambda x: x[4], True, "shortest day")
    m_set, m_rise = int(round(e_set[3] % 1440)), int(round(l_rise[1] % 1440))
    tie_set = [r[0] for r in rows if int(round(r[3] % 1440)) == m_set]
    tie_rise = [r[0] for r in rows if int(round(r[1] % 1440)) == m_rise]
    print(f"\n  {name}  lat {lat:+.4f}  lon {lon:+.4f}  UTC{tz:+d}")
    print(f"    earliest sunset   {e_set[0]}   {fmt(e_set[3])}")
    print(f"    shortest day      {short[0]}   {short[4]:.2f} min of daylight")
    print(f"    latest sunrise    {l_rise[0]}   {fmt(l_rise[1])}")
    print(f"    sunset  plateau at {m_set//60:02d}:{m_set%60:02d}  {len(tie_set):>2} day(s)  "
          f"{tie_set[0]} to {tie_set[-1]}")
    print(f"    sunrise plateau at {m_rise//60:02d}:{m_rise%60:02d}  {len(tie_rise):>2} day(s)  "
          f"{tie_rise[0]} to {tie_rise[-1]}")
    return e_set, short, l_rise


if __name__ == "__main__":
    for args in (("Chicago", 41.8781, -87.6298, -6),
                 ("Anchorage", 61.2176, -149.8631, -9),
                 ("Quito", -0.1807, -78.4678, -5),
                 ("Singapore", 1.3521, 103.8198, 8),
                 ("Reykjavik", 64.1466, -21.9426, 0)):
        report(*args)
