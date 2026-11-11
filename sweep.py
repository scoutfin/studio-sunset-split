#!/usr/bin/env python3
"""How far before the December solstice does the earliest sunset fall, as a
function of latitude?

Longitude and timezone cancel out of this question entirely: both shift every
sunset on every day by the same constant, so they cannot move which day is
earliest. Run at longitude 0, UTC, so nothing is hidden in an offset.
"""
import datetime as dt
import sys

sys.path.insert(0, "/home/scout/studio/sunset-split")
from solar import events, local_unwrapped

SOLSTICE = dt.date(2026, 12, 21)        # verified against USNO; see the post


def earliest_sunset(lat):
    """(date, days_before_solstice, note). Returns a note instead of a number
    whenever the answer would not be an answer.

    Two refusals, both found by running it rather than by reasoning about it:

    * EDGE. An extremum sitting on the first or last day of the search window is
      the window, not an extremum. Caught when a Nov-1 window start reported
      Quito's earliest sunset as Nov 2.
    * GAP. Above the Arctic Circle the sun does not rise at all for part of this
      window, and skipping those days leaves a series with a hole exactly where
      the minimum belongs. The surviving minimum then looks perfectly healthy:
      at 68 deg N the first version returned Dec 8, which is simply the edge of
      the hole. A dropped day is not a day with no extremum.
    """
    rows, skipped = [], 0
    d0 = dt.date(2026, 9, 1)
    n_days = 170                        # Sep 1 -> Feb 17, solstice well inside
    for i in range(n_days):
        day = d0 + dt.timedelta(days=i)
        r, n, s = events(day.year, day.month, day.day, lat, 0.0)
        if s is None or r is None:
            skipped += 1
            continue
        rows.append((day, local_unwrapped(s, 0)))
    if skipped:
        return None, None, f"{skipped} day(s) with no sunrise/sunset in the window"
    best = min(rows, key=lambda x: x[1])
    i = rows.index(best)
    if i < 5 or i >= len(rows) - 5:
        return None, None, f"minimum {min(i, len(rows)-1-i)} day(s) from the window edge"
    return best[0], (SOLSTICE - best[0]).days, f"{len(rows)} contiguous days"


if __name__ == "__main__":
    print("  lat\tearliest sunset\tdays before solstice\tusable days")
    for lat10 in range(0, 681, 20):     # 0.0 to 68.0 in 2-degree steps
        lat = lat10 / 10.0
        d, off, note = earliest_sunset(lat)
        if d is None:
            print(f"  {lat:5.1f}\tNO ANSWER      \t --\t{note}")
        else:
            print(f"  {lat:5.1f}\t{d}\t{off:>3d}\t{note}")
