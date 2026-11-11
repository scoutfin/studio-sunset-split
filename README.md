# sunset-split

The earliest sunset is not the shortest day, and the size of the gap is a curve.
This is the working behind
[the post](https://scoutfin.net/posts/2026-11-11-the-day-slides/).

## What is here

| file | what it does |
|---|---|
| `solar.py` | sunrise, solar noon, sunset and the equation of time from Meeus, kept at second resolution |
| `fetch_usno.py` | pulls USNO's published rise/transit/set for a date range, paced and cached on disk |
| `compare.py` | my values against USNO's, 126 of them, with the exposure printed next to the agreement |
| `bias.py` | bounds my sub-4-second offset from USNO using only their minute-rounded output |
| `extrema.py` | earliest sunset, latest sunrise, shortest day, and the width of the minute-rounded plateau |
| `sweep.py` | the offset against latitude, which is the curve in the post |
| `mkchart.py` | the inline SVG |

`python3 compare.py usno-chicago.tsv` reproduces the cross-check from the cached
USNO responses without touching the network.

## Three bugs, all found by running it rather than by reading it

**The window edge.** The first version searched from 2026-11-01 and reported
Quito's earliest sunset as 2026-11-02 and its shortest day as 2026-11-01, both
sitting on the first day it was allowed to look at. An extremum on the edge of a
search window is the window. `extrema.py` now refuses any extremum within five
days of either end.

**The midnight wrap.** Sunset times were wrapped into `[0, 1440)` for display and
then compared in that form. At Reykjavík in late June the sun sets after local
midnight, so `% 1440` turned a 00:00:17 sunset into the smallest value of the
year and the earliest sunset came back as 2026-06-28. A clock that wraps at
midnight destroys the ordering of the quantity being extremised, and the wrong
answer arrives as a plausible date with a plausible time beside it. Compare
unwrapped, wrap only to print.

**The silent gap.** Above the Arctic Circle the sun does not rise for part of the
search window. Skipping those days left a series with a hole exactly where the
minimum belongs, and the surviving minimum looked perfectly healthy: at 68°N it
returned 2026-12-08, which is simply the edge of the hole. `sweep.py` now refuses
a latitude where any day in the window had no sunrise, because a dropped day is
not a day with no extremum.

## Two hypotheses that died

The five minute-level disagreements with USNO all had my value 30 to 33 seconds
past the minute, which looked exactly like USNO truncating where I round. Scored
against the alternative, truncation gets 64 of 126 values and round-to-nearest
gets 121, so that story is dead. The residual is a sub-four-second offset, and
treating rounding boundaries as a comparator bounds it: see `bias.py`.

The first model there assumed one offset for all three phenomena and its two
bounds crossed, which is the model saying it does not fit. Split by phenomenon it
fits, with three different offsets.

## Sources

- USNO Astronomical Applications rise/transit/set API, `aa.usno.navy.mil/api/rstt/oneday`
- USNO Earth's Seasons API, `aa.usno.navy.mil/api/seasons`
- Jean Meeus, *Astronomical Algorithms*, via the NOAA solar calculator's formulation
