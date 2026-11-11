#!/usr/bin/env python3
"""Sunrise/sunset/solar-noon from first principles (Meeus, as in the NOAA
solar calculator), at SECOND resolution rather than minute resolution.

Minute resolution is the whole problem with the question being asked here:
around the December extremum the sunset time changes by only a few seconds a
day, so a table rounded to the minute shows a PLATEAU of tied days and cannot
say which one is earliest. Everything below keeps seconds and only rounds for
display.

Convention: longitude positive EAST. Altitude of the sun's upper limb at
rise/set taken as -0.8333 deg (34' refraction + 16' semidiameter), which is
what USNO and NOAA both use for a sea-level observer.
"""
import math

RAD = math.pi / 180.0
ZENITH = 90.0 + 0.8333          # 90.8333 deg


def jd_from_ymd(y, m, d):
    """Julian day at 00:00 UT of the given civil date (Gregorian)."""
    if m <= 2:
        y -= 1
        m += 12
    a = y // 100
    b = 2 - a + a // 4
    return (math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1))
            + d + b - 1524.5)


def _sun(jc):
    """Return (apparent longitude deg, obliquity deg, eqtime minutes) at Julian century jc."""
    l0 = (280.46646 + jc * (36000.76983 + jc * 0.0003032)) % 360.0
    m = 357.52911 + jc * (35999.05029 - 0.0001537 * jc)
    e = 0.016708634 - jc * (0.000042037 + 0.0000001267 * jc)
    c = (math.sin(m * RAD) * (1.914602 - jc * (0.004817 + 0.000014 * jc))
         + math.sin(2 * m * RAD) * (0.019993 - 0.000101 * jc)
         + math.sin(3 * m * RAD) * 0.000289)
    true_long = l0 + c
    omega = 125.04 - 1934.136 * jc
    app_long = true_long - 0.00569 - 0.00478 * math.sin(omega * RAD)
    seconds = 21.448 - jc * (46.8150 + jc * (0.00059 - jc * 0.001813))
    e0 = 23.0 + (26.0 + seconds / 60.0) / 60.0
    eps = e0 + 0.00256 * math.cos(omega * RAD)

    y = math.tan(eps / 2 * RAD) ** 2
    eqtime = 4 / RAD * (
        y * math.sin(2 * l0 * RAD)
        - 2 * e * math.sin(m * RAD)
        + 4 * e * y * math.sin(m * RAD) * math.cos(2 * l0 * RAD)
        - 0.5 * y * y * math.sin(4 * l0 * RAD)
        - 1.25 * e * e * math.sin(2 * m * RAD)
    )
    return app_long, eps, eqtime


def declination(jd):
    jc = (jd - 2451545.0) / 36525.0
    app_long, eps, _ = _sun(jc)
    return math.degrees(math.asin(math.sin(eps * RAD) * math.sin(app_long * RAD)))


def eq_of_time(jd):
    return _sun((jd - 2451545.0) / 36525.0)[2]


def events(y, m, d, lat, lon):
    """(sunrise, solar_noon, sunset) as minutes after 00:00 UT, float.

    Two passes: the first uses the sun at 00:00 UT, the second re-evaluates the
    sun's position AT the estimated event time, which is what gets this to a few
    seconds instead of a minute or so. One refinement is enough; a third pass
    moves the answer by well under a second at these latitudes.
    """
    jd0 = jd_from_ymd(y, m, d)

    def pass_(jd_rise, jd_set, jd_noon):
        out = []
        for jd, kind in ((jd_noon, "noon"), (jd_rise, "rise"), (jd_set, "set")):
            _, _, eqtime = _sun((jd - 2451545.0) / 36525.0)
            dec = declination(jd)
            noon = 720.0 - 4.0 * lon - eqtime
            if kind == "noon":
                out.append(noon)
                continue
            cos_h = (math.cos(ZENITH * RAD)
                     / (math.cos(lat * RAD) * math.cos(dec * RAD))
                     - math.tan(lat * RAD) * math.tan(dec * RAD))
            if cos_h > 1.0:
                out.append(None)      # sun never rises
                continue
            if cos_h < -1.0:
                out.append(None)      # sun never sets
                continue
            h = math.degrees(math.acos(cos_h))
            out.append(noon - 4.0 * h if kind == "rise" else noon + 4.0 * h)
        noon_v, rise_v, set_v = out
        return rise_v, noon_v, set_v

    r, n, s = pass_(jd0, jd0, jd0)
    if r is None or s is None:
        return r, n, s
    r2, n2, s2 = pass_(jd0 + r / 1440.0, jd0 + s / 1440.0, jd0 + n / 1440.0)
    return r2, n2, s2


def local_unwrapped(minutes_ut, tz_hours):
    """UT minutes -> local minutes, NOT wrapped. Use this for comparisons.

    2026-11-11: the wrapped version below silently broke the one question this
    file exists to answer. At Reykjavik in late June the sun sets after local
    midnight, so `% 1440` turned a 00:00:17 sunset into the SMALLEST value of
    the year and "earliest sunset" came back as 2026-06-28. A clock that wraps
    at midnight destroys the ordering of the quantity being extremised, and the
    broken answer looked like a plausible date with a plausible time next to it.
    Compare unwrapped; wrap only to print.
    """
    if minutes_ut is None:
        return None
    return minutes_ut + tz_hours * 60.0


def local(minutes_ut, tz_hours):
    """UT minutes -> local clock minutes, wrapped into [0, 1440). DISPLAY ONLY."""
    if minutes_ut is None:
        return None
    return (minutes_ut + tz_hours * 60.0) % 1440.0


def hhmmss(minutes):
    if minutes is None:
        return "    --   "
    t = round(minutes * 60.0)
    return f"{t // 3600:02d}:{t % 3600 // 60:02d}:{t % 60:02d}"


def hhmm_round(minutes):
    """Minute-rounded, the way an almanac prints it."""
    if minutes is None:
        return "  --  "
    t = int(round(minutes))
    return f"{t // 60 % 24:02d}:{t % 60:02d}"
