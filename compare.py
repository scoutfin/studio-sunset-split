#!/usr/bin/env python3
"""Compare my computed times against USNO's, day by day, and PRINT THE EXPOSURE.

Agreement with a reference is uninformative without a count of inputs that could
have differed. So this reports the number of days, how much the reference value
MOVES across them, and the distribution of disagreements in minutes, not a
pass/fail.
"""
import collections
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from solar import events, local

LAT, LON, TZ = 41.8781, -87.6298, -6


def mins(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


rows = [l.rstrip("\n").split("\t") for l in open(sys.argv[1]) if l.strip()]
diffs = collections.Counter()
spread = {"Rise": [], "Upper Transit": [], "Set": []}
worst = []
for date, rise, noon, set_, _dst in rows:
    y, m, d = (int(x) for x in date.split("-"))
    r, n, s = events(y, m, d, LAT, LON)
    mine = {"Rise": local(r, TZ), "Upper Transit": local(n, TZ), "Set": local(s, TZ)}
    ref = {"Rise": mins(rise), "Upper Transit": mins(noon), "Set": mins(set_)}
    for k in ref:
        spread[k].append(ref[k])
        delta = int(round(mine[k])) - ref[k]
        diffs[(k, delta)] += 1
        if delta:
            worst.append((date, k, f"mine {mine[k]/60:.4f}h", f"usno {ref[k]}m", delta))

n_days = len(rows)
print(f"  {n_days} days, {n_days*3} compared values, {dt.date.fromisoformat(rows[0][0])} to "
      f"{dt.date.fromisoformat(rows[-1][0])}")
for k in ("Rise", "Upper Transit", "Set"):
    v = spread[k]
    print(f"    {k:<14} USNO value ranges over {max(v)-min(v)} minutes across the window "
          f"(so the comparison is not a constant)")
print()
for k in ("Rise", "Upper Transit", "Set"):
    sub = {d: c for (kk, d), c in diffs.items() if kk == k}
    tot = sum(sub.values())
    agree = sub.get(0, 0)
    print(f"    {k:<14} {agree}/{tot} to the minute; deltas {dict(sorted(sub.items()))}")
if worst:
    print("\n  every disagreement:")
    for w in worst:
        print("   ", w)
