#!/usr/bin/env python3
"""Join centerline-trace fragments that are naturally one stroke.

Two path endpoints are welded when they nearly coincide AND the strokes
continue smoothly through the join (outgoing tangents roughly antiparallel).
This joins the through-line at a T/X junction while leaving the branch alone.
"""
import re
import sys
import numpy as np
from svgpathtools import svg2paths, Path

SRC = "lines_tight.svg"
OUT = "lines_tight_joined.svg"
GAP_TOL = 34.0       # bridges the tracer's dash gaps
ANGLE_DOT = -0.55    # outward tangents must be at least this antiparallel
CORNER_STEP = 4.0    # arclength between samples when hunting corners
CORNER_COS = 0.70    # per-step turn beyond ~45 deg => a corner to split at
HEAD_DOT = 0.55      # tuned
SPAN = 18.0          # chord length for tangent estimate (ignores endpoint kinks)
VIEWBOX = "0 0 2816 1536"
STYLE = ('.cls-1{fill:none;stroke:#000;stroke-linecap:round;'
         'stroke-linejoin:round;stroke-width:2px;}')


def outward(path, at_end):
    """Unit vector pointing away from the path body at one endpoint, measured as
    a chord over SPAN units inward — robust to a kink right at the tip."""
    total = path.length()
    span = min(SPAN, total * 0.45)
    try:
        if at_end:
            tip, inner = path.point(1.0), path.point(path.ilength(total - span))
        else:
            tip, inner = path.point(0.0), path.point(path.ilength(span))
        d = tip - inner                 # points outward, away from the body
        if abs(d) > 1e-6:
            return d / abs(d)
    except Exception:
        pass
    # fallback: instantaneous tangent
    try:
        t = path.unit_tangent(1.0 if at_end else 0.0)
        return t if at_end else -t
    except Exception:
        seg = path[-1] if at_end else path[0]
        d = seg.end - seg.start
        return d / abs(d) if abs(d) else 0j


def split_at_corners(path):
    """Break a traced fragment at any sharp internal corner so every piece is
    smooth. Gentle (rounded) turns are left intact — only true corners split."""
    total = path.length()
    if total < 3 * CORNER_STEP:
        return [path]
    ts, s = [], 0.0
    while s < total:
        try:
            ts.append(path.ilength(s))
        except Exception:
            pass
        s += CORNER_STEP
    ts.append(1.0)
    ts = sorted(t for t in set(ts) if 0.0 <= t <= 1.0)
    pts = [path.point(t) for t in ts]
    dirs = []
    for a, b in zip(pts, pts[1:]):
        d = b - a
        dirs.append(d / abs(d) if abs(d) > 1e-9 else None)
    cut_ts = []
    for k in range(1, len(dirs)):
        a, b = dirs[k - 1], dirs[k]
        if a and b and (a.real * b.real + a.imag * b.imag) < CORNER_COS:
            cut_ts.append(ts[k])
    if not cut_ts:
        return [path]
    bounds = [0.0] + cut_ts + [1.0]
    pieces = []
    for t0, t1 in zip(bounds, bounds[1:]):
        if t1 - t0 > 1e-4:
            try:
                pieces.append(path.cropped(t0, t1))
            except Exception:
                pass
    return pieces or [path]


def main():
    raw, _ = svg2paths(SRC)
    paths = []
    for p in raw:
        if len(p) and p.length() > 0.5:
            paths.extend(split_at_corners(p))
    paths = [p for p in paths if p.length() > 0.5]
    n = len(paths)
    print(f"input paths: {len(raw)} -> {n} after corner-splitting")

    # ports: 2 per path -> (path_index, side) with point + outward tangent
    pts = np.array([[p.start, p.end] for p in paths])            # n x 2 complex
    outs = np.array([[outward(p, False), outward(p, True)] for p in paths])

    # candidate welds between ports of different paths
    cands = []
    for i in range(n):
        for si in (0, 1):
            pi, ti = pts[i, si], outs[i, si]
            for j in range(i + 1, n):
                for sj in (0, 1):
                    pj, tj = pts[j, sj], outs[j, sj]
                    gap = abs(pi - pj)
                    if gap > GAP_TOL:
                        continue
                    dot = ti.real * tj.real + ti.imag * tj.imag
                    if dot > ANGLE_DOT:            # tangents not antiparallel enough
                        continue
                    if gap > 2.0:                 # gap must open the way each heads
                        v = pj - pi
                        vhat = v / abs(v)
                        head_i = ti.real * vhat.real + ti.imag * vhat.imag
                        head_j = tj.real * -vhat.real + tj.imag * -vhat.imag
                        if head_i < HEAD_DOT or head_j < HEAD_DOT:
                            continue
                    cands.append((gap + 40 * (dot + 1), i, si, j, sj))
    cands.sort()

    link = {}                                       # (i,side) -> (j,side)
    used = set()
    for _, i, si, j, sj in cands:
        a, b = (i, si), (j, sj)
        if a in used or b in used:
            continue
        link[a] = b
        link[b] = a
        used.add(a)
        used.add(b)
    print(f"welds: {len(link) // 2}")

    # walk chains
    ds = [p.d() for p in paths]
    visited = [False] * n
    merged = []

    def emit_chain(start_i, start_side):
        """start_side is the FREE side we begin at; traverse inward."""
        parts = []
        i, entry = start_i, start_side
        while True:
            visited[i] = True
            reversed_ = (entry == 1)                # entered at end -> go backward
            parts.append(paths[i].reversed().d() if reversed_ else ds[i])
            exit_side = 1 - entry
            nxt = link.get((i, exit_side))
            if nxt is None or visited[nxt[0]]:
                break
            i, entry = nxt
        return parts

    # chains that have a free end first
    for i in range(n):
        if visited[i]:
            continue
        for side in (0, 1):
            if (i, side) not in link:               # free endpoint -> chain start
                merged.append(emit_chain(i, side))
                break
    # leftover closed loops
    for i in range(n):
        if not visited[i]:
            merged.append(emit_chain(i, 0))

    # weld each chain's d-strings into one continuous subpath (drop inner M's)
    strip_m = re.compile(r'^\s*M\s*-?[\d.eE]+[,\s]+-?[\d.eE]+\s*')
    out_paths = []
    for parts in merged:
        d = parts[0].strip()
        for extra in parts[1:]:
            d += " " + strip_m.sub("", extra.strip(), count=1)
        out_paths.append(d)
    print(f"output paths: {len(out_paths)}")

    body = "".join(f'<path class="cls-1" d="{d}"/>' for d in out_paths)
    svg = (f'<?xml version="1.0" encoding="UTF-8"?>'
           f'<svg id="Layer_1" xmlns="http://www.w3.org/2000/svg" viewBox="{VIEWBOX}">'
           f'<defs><style>{STYLE}</style></defs>{body}</svg>')
    with open(OUT, "w") as f:
        f.write(svg)


if __name__ == "__main__":
    main()
