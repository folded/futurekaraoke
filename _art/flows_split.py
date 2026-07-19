#!/usr/bin/env python3
"""Separate smooth 'flow' lines from angular 'circuit' traces.

Heuristic (from observation): flow lines keep a roughly constant width and make
no sharp turns — they are long, smooth, diagonal curves. Circuit traces are
axis-aligned (long vertical runs) and/or turn sharply (~90deg corners).

Method: skeletonise -> split into arcs at junctions -> for each arc measure its
sharpest local turn and how axis-aligned it is -> classify -> paint the original
thick pixels by nearest skeleton arc.
"""
import numpy as np
from PIL import Image
from skimage.morphology import skeletonize
from scipy import ndimage as ndi

SRC = "layer_circuit.png"      # black-on-white: circuit + flows mixed
SAMPLE = 7                     # px between tangent samples (smooths pixel noise)
SHARP_DEG = 52                 # a local turn above this => a corner => circuit
AXIS_DEG = 20                  # within this of vertical/horizontal => axis-aligned
AXIS_FRAC = 0.58               # arc mostly axis-aligned => circuit
MIN_FLOW_LEN = 45              # px; shorter smooth arcs aren't confidently flows


def order_arc(coords_set, start):
    """Walk a degree<=2 pixel set into an ordered point list from `start`."""
    pts = [start]
    seen = {start}
    cur = start
    while True:
        y, x = cur
        nxt = None
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy == 0 and dx == 0:
                    continue
                c = (y + dy, x + dx)
                if c in coords_set and c not in seen:
                    nxt = c
                    break
            if nxt:
                break
        if nxt is None:
            break
        pts.append(nxt)
        seen.add(nxt)
        cur = nxt
    return pts


def classify(pts, is_loop):
    """Return 'flow' or 'circuit' for an ordered arc."""
    if is_loop:                      # closed loop => terminal dot / ring => circuit
        return "circuit"
    if len(pts) < SAMPLE * 2:
        return "circuit"
    samp = pts[::SAMPLE]
    if len(samp) < 3:
        return "circuit"
    angs = []
    for (y0, x0), (y1, x1) in zip(samp, samp[1:]):
        angs.append(np.degrees(np.arctan2(y1 - y0, x1 - x0)))
    angs = np.array(angs)
    # local turning between consecutive tangent samples
    turn = np.abs((np.diff(angs) + 180) % 360 - 180)
    sharp = turn.max() if len(turn) else 0.0
    # verticality: a long vertical run is the circuit signature (flows are never
    # long-vertical, though they may run flat, so horizontal is NOT a circuit cue)
    m = angs % 180
    vert_frac = float((np.abs(m - 90) < AXIS_DEG).mean())

    if sharp > SHARP_DEG:
        return "circuit"
    if vert_frac > AXIS_FRAC:
        return "circuit"
    if len(pts) >= MIN_FLOW_LEN:
        return "flow"
    return "circuit"


def main():
    mask = np.asarray(Image.open(SRC).convert("L")) < 128
    skel = skeletonize(mask)

    # neighbour count -> junctions (deg>=3)
    k = np.ones((3, 3), int)
    deg = ndi.convolve(skel.astype(int), k, mode="constant") - skel
    junctions = skel & (deg >= 3)
    arcs_mask = skel & ~junctions

    lbl, n = ndi.label(arcs_mask, structure=np.ones((3, 3)))
    print(f"{n} arcs")

    skel_class = np.zeros(skel.shape, np.uint8)  # 1=circuit, 2=flow
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lbl == i)
        coords = set(zip(ys.tolist(), xs.tolist()))
        # start at an endpoint if there is one
        start = None
        for c in coords:
            y, x = c
            nb = sum((y + dy, x + dx) in coords
                     for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                     if not (dy == 0 and dx == 0))
            if nb == 1:
                start = c
                break
        is_loop = start is None      # no endpoint => closed loop
        if start is None:
            start = next(iter(coords))
        pts = order_arc(coords, start)
        cls = classify(pts, is_loop)
        val = 2 if cls == "flow" else 1
        for (y, x) in coords:
            skel_class[y, x] = val

    # paint thick pixels by nearest classified skeleton pixel
    nz = skel_class > 0
    _, (iy, ix) = ndi.distance_transform_edt(~nz, return_indices=True)
    nearest = skel_class[iy, ix]
    flows = mask & (nearest == 2)
    circuit = mask & (nearest == 1)
    print(f"flow px {int(flows.sum())} | circuit px {int(circuit.sum())}")

    for name, m in (("flows", flows), ("circuit2", circuit)):
        Image.fromarray(np.where(m, 0, 255).astype(np.uint8)).save(f"layer_{name}.png")

    h, w = mask.shape
    prev = np.full((h, w, 3), (11, 7, 22), np.uint8)
    prev[circuit] = (150, 140, 180)
    prev[flows] = (255, 150, 70)
    Image.fromarray(prev).save("flows_preview.png")


if __name__ == "__main__":
    main()
