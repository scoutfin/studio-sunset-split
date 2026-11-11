#!/usr/bin/env python3
"""Pull USNO rise/transit/set for a date range and cache each day on disk.

Paced at 1.2s between requests and cached, so a re-run costs nothing. USNO is a
public US Navy service; this is a handful of dates, fetched like a person would.
"""
import datetime as dt
import json
import os
import subprocess
import sys
import time

CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "usno-cache")
UA = "scout/1.0 (+https://scoutfin.net/about/)"


def one(date, lat, lon, tz):
    key = f"{date}_{lat}_{lon}_{tz}.json".replace("/", "_")
    path = os.path.join(CACHE, key)
    if os.path.exists(path):
        return json.load(open(path))
    url = (f"https://aa.usno.navy.mil/api/rstt/oneday?date={date}"
           f"&coords={lat},{lon}&tz={tz}")
    r = subprocess.run(["curl", "-sS", "-m", "25", "-A", UA, url],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"curl failed for {date}: {r.stderr[:200]}")
    d = json.loads(r.stdout)
    with open(path, "w") as fh:
        json.dump(d, fh)
    time.sleep(1.2)
    return d


def sun(d):
    out = {}
    for row in d["properties"]["data"].get("sundata") or []:
        out[row["phen"]] = row["time"]
    return out, d["properties"]["data"].get("isdst")


if __name__ == "__main__":
    lat, lon, tz, start, days = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5])
    d0 = dt.date.fromisoformat(start)
    for i in range(days):
        day = d0 + dt.timedelta(days=i)
        s, isdst = sun(one(day.isoformat(), lat, lon, tz))
        print(f"{day}\t{s.get('Rise','--')}\t{s.get('Upper Transit','--')}\t{s.get('Set','--')}\tdst={isdst}")
