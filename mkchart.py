#!/usr/bin/env python3
"""Inline SVG of the earliest-sunset offset against latitude.

currentColor throughout so it reads on both the light and the dark theme.
"""
import os

rows = []
for line in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "curve.tsv")):
    lat, date, off = line.rstrip("\n").split("\t")
    rows.append((float(lat), date, int(off)))

W, H = 980, 470
L, R, T, B = 62, 150, 30, 48
PW, PH = W - L - R, H - T - B
XMAX, YMAX = 70.0, 50.0


def x(lat):
    return L + PW * lat / XMAX


def y(days):
    return T + PH * (1 - days / YMAX)


p = []
a = p.append

# y gridlines: days before the solstice
for d in (0, 10, 20, 30, 40, 50):
    a(f'<line x1="{L}" y1="{y(d):.1f}" x2="{L+PW:.1f}" y2="{y(d):.1f}" '
      f'stroke="currentColor" stroke-width="1" opacity=".13"/>')
    a(f'<text x="{L-8}" y="{y(d)+4:.1f}" font-size="11.5" text-anchor="end" '
      f'fill="currentColor" opacity=".55">{d}</text>')
# x gridlines: latitude
for lat in (0, 10, 20, 30, 40, 50, 60, 70):
    a(f'<line x1="{x(lat):.1f}" y1="{T}" x2="{x(lat):.1f}" y2="{T+PH:.1f}" '
      f'stroke="currentColor" stroke-width="1" opacity=".08"/>')
    a(f'<text x="{x(lat):.1f}" y="{T+PH+18:.1f}" font-size="11.5" text-anchor="middle" '
      f'fill="currentColor" opacity=".55">{lat}°</text>')

# the refraction margin: beyond the geometric Arctic Circle but still getting a sunrise
ARCTIC = 66.564
a(f'<rect x="{x(ARCTIC):.1f}" y="{T}" width="{x(67.4)-x(ARCTIC):.1f}" height="{PH:.1f}" '
  f'fill="currentColor" opacity=".09"/>')
a(f'<line x1="{x(ARCTIC):.1f}" y1="{T}" x2="{x(ARCTIC):.1f}" y2="{T+PH:.1f}" '
  f'stroke="currentColor" stroke-width="1" opacity=".35" stroke-dasharray="3 3"/>')

# the curve
pts = " ".join(f"{x(lat):.1f},{y(off):.1f}" for lat, _d, off in rows)
a(f'<polyline points="{pts}" fill="none" stroke="currentColor" stroke-width="2.4" '
  f'opacity=".82" stroke-linejoin="round"/>')

# city markers
CITIES = [("Quito", 0.18, "0.2°S"), ("Singapore", 1.35, "1.4°N"),
          ("Chicago", 41.88, "41.9°N"), ("Anchorage", 61.22, "61.2°N"),
          ("Reykjavík", 64.15, "64.1°N")]
by_lat = {round(lat, 1): off for lat, _d, off in rows}


def offset_at(lat):
    best = min(rows, key=lambda r: abs(r[0] - lat))
    return best[2], best[1]


for i, (name, lat, label) in enumerate(CITIES):
    off, date = offset_at(lat)
    cx, cy = x(lat), y(off)
    a(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4.6" fill="currentColor" opacity=".92"/>')
    dx, anchor = (12, "start")
    if name == "Quito":
        ty = cy + 4
    elif name == "Singapore":
        ty = cy + 22
    elif name == "Chicago":
        ty = cy - 10
    elif name == "Anchorage":
        ty = cy - 10
    else:
        ty = cy + 20
        dx, anchor = (-12, "end")
    a(f'<text x="{cx+dx:.1f}" y="{ty:.1f}" font-size="12.5" text-anchor="{anchor}" '
      f'fill="currentColor" opacity=".9" font-weight="600">{name}</text>')
    a(f'<text x="{cx+dx:.1f}" y="{ty+14:.1f}" font-size="11" text-anchor="{anchor}" '
      f'fill="currentColor" opacity=".6" '
      f'font-family="ui-monospace,SFMono-Regular,Menlo,monospace">{label} · '
      f'{date[5:]} · {off}d</text>')

# axis titles and the margin label
a(f'<text x="{L}" y="{T-12}" font-size="12.5" fill="currentColor" opacity=".62">'
  f'days the earliest sunset falls BEFORE the December solstice</text>')
a(f'<text x="{L+PW/2:.1f}" y="{H-8}" font-size="12.5" text-anchor="middle" '
  f'fill="currentColor" opacity=".62">latitude</text>')
a(f'<text x="{x(67.0):.1f}" y="{T+PH-10:.1f}" font-size="11" text-anchor="end" '
  f'fill="currentColor" opacity=".62">Arctic Circle 66.56°</text>')
a(f'<text x="{x(67.0):.1f}" y="{T+PH+4:.1f}" font-size="11" text-anchor="end" '
  f'fill="currentColor" opacity=".48" '
  f'font-family="ui-monospace,SFMono-Regular,Menlo,monospace">refraction margin</text>')

alt = ("A curve showing how many days before the December solstice the earliest sunset "
       "falls, against latitude. At the equator it is 49 days, in early November. The "
       "curve falls steeply and then flattens, passing Chicago at 13 days and reaching "
       "1 day near 67 degrees north, where a shaded band marks the latitudes beyond the "
       "geometric Arctic Circle that still get a sunrise because the atmosphere bends light.")

svg = (f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" '
       f'xmlns="http://www.w3.org/2000/svg" aria-label="{alt}">' + "".join(p) + "</svg>")
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "chart.svg"), "w").write(svg)
print("wrote chart.svg", len(svg), "bytes")
