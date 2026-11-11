#!/usr/bin/env python3
"""Bound my systematic offset from USNO using ONLY minute-rounded reference data.

The five disagreements are not noise and they are not truncation (truncation
scores 64/126 against round-to-nearest's 121/126, so that hypothesis is dead).
They are a rounding BOUNDARY effect, and a boundary is a high-gain comparator:
a reference rounded to the minute still resolves seconds, at the handful of
inputs that happen to land next to a boundary.

Model: USNO_true = mine - b, with b a small positive offset in seconds, and
USNO rounding to nearest. Then the two printed minutes differ exactly when
frac(mine_minutes) lies in [0.5, 0.5 + b/60).

  every DISAGREEING value with frac f gives   b >= 60*(f - 0.5)
  every AGREEING  value with frac f >= 0.5 gives b <= 60*(f - 0.5)

Two one-sided bounds from 126 coarse values.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from solar import events, local

LAT, LON, TZ = 41.8781, -87.6298, -6


def mins(h):
    a, b = h.split(":")
    return int(a) * 60 + int(b)


lo, hi = 0.0, 60.0
lo_at = hi_at = None
n_near = 0
for line in open("usno-chicago.tsv"):
    if not line.strip():
        continue
    date, rise, noon, set_, _ = line.rstrip("\n").split("\t")
    y, m, d = (int(x) for x in date.split("-"))
    r, n, s = events(y, m, d, LAT, LON)
    for k, mine_v, ref in (("Rise", local(r, TZ), mins(rise)),
                           ("Transit", local(n, TZ), mins(noon)),
                           ("Set", local(s, TZ), mins(set_))):
        f = mine_v - math.floor(mine_v)
        if f < 0.5:
            continue              # carries no information about b
        n_near += 1
        disagrees = int(round(mine_v)) != ref
        b_edge = 60.0 * (f - 0.5)
        if disagrees and b_edge > lo:
            lo, lo_at = b_edge, (date, k, round(f, 4))
        if not disagrees and b_edge < hi:
            hi, hi_at = b_edge, (date, k, round(f, 4))

print(f"  126 compared values; {n_near} of them sit in the informative half "
      f"(frac >= 0.5), the rest say nothing about a sub-minute offset")
print(f"  lower bound  b > {lo:.2f} s   from the disagreeing value nearest the boundary {lo_at}")
print(f"  upper bound  b < {hi:.2f} s   from the agreeing value nearest the boundary {hi_at}")
print(f"\n  => my times run {lo:.2f}-{hi:.2f} s LATE of USNO's, bounded by minute-rounded data alone")
if lo >= hi:
    print("  !! bounds crossed: the one-offset model does not fit, so the residual is "
          "not a constant bias")
