#!/usr/bin/env python3
"""Split the extracted line mask into per-element layers.

Each connected stroke is labelled, then assigned to the named region that
contains the majority of its pixels. Strokes that don't sit mostly inside any
named region (the long circuit traces, the flowing lines) fall to "circuit".
Small round components become "stars".
"""
from collections import deque
import numpy as np
from PIL import Image

SRC = "lines_medium.png"  # black-on-white extraction

# Named regions as fractions of (width, height): x0, y0, x1, y1.
# Checked in this order; first containing box wins (specific elements before
# the catch-all "circuit"). Pixels are cut by geography so the connecting
# flow-lines don't drag every element into one component.
REGIONS = {
    "mic":          (0.08, 0.31, 0.21, 0.66),
    "constellation":(0.40, 0.10, 0.65, 0.68),
    "profile":      (0.75, 0.40, 0.90, 0.66),
    "book":         (0.55, 0.66, 0.89, 1.00),
    "waves":        (0.00, 0.74, 0.33, 1.00),
}
LAYER_COLORS = {
    "mic":          (255, 180, 84),
    "constellation":(127, 245, 224),
    "profile":      (255, 130, 190),
    "book":         (255, 214, 140),
    "waves":        (120, 230, 210),
    "circuit":      (183, 173, 202),
    "stars":        (255, 255, 255),
}
STAR_MAX_AREA = 80
STAR_MAX_SPAN = 16


def components(mask):
    """Yield (pixels list, (y0,x0,y1,x1)) for each 8-connected component."""
    h, w = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    ys, xs = np.nonzero(mask)
    for sy, sx in zip(ys, xs):
        if seen[sy, sx]:
            continue
        px = []
        dq = deque([(sy, sx)])
        seen[sy, sx] = True
        y0 = y1 = sy
        x0 = x1 = sx
        while dq:
            y, x = dq.popleft()
            px.append((y, x))
            y0, y1 = min(y0, y), max(y1, y)
            x0, x1 = min(x0, x), max(x1, x)
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        dq.append((ny, nx))
        yield px, (y0, x0, y1, x1)


def main():
    img = Image.open(SRC).convert("L")
    arr = np.asarray(img)
    mask = arr < 128
    h, w = mask.shape

    layers = {name: np.zeros((h, w), dtype=bool) for name in LAYER_COLORS}

    # 1) Small round components -> stars (so scattered dots aren't chopped).
    star = np.zeros((h, w), dtype=bool)
    for px, (by0, bx0, by1, bx1) in components(mask):
        if len(px) <= STAR_MAX_AREA and max(by1 - by0, bx1 - bx0) <= STAR_MAX_SPAN:
            for (y, x) in px:
                star[y, x] = True
    layers["stars"] = star
    lines = mask & ~star

    # 2) Everything else is assigned per-pixel by region (geography), so the
    #    connecting flow-lines don't drag whole elements together. First region
    #    to claim a pixel wins; the remainder is "circuit".
    claimed = np.zeros((h, w), dtype=bool)
    for name, (x0, y0, x1, y1) in REGIONS.items():
        box = np.zeros((h, w), dtype=bool)
        box[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)] = True
        m = lines & box & ~claimed
        layers[name] = m
        claimed |= m
    layers["circuit"] = lines & ~claimed

    combined = np.zeros((h, w, 3), dtype=np.uint8)
    combined[:] = (11, 7, 22)
    for name, m in layers.items():
        count = int(m.sum())
        print(f"{name:14s}: {count:>7d} px")
        # black-on-white layer for tracing
        bw = np.where(m, 0, 255).astype(np.uint8)
        Image.fromarray(bw).save(f"layer_{name}.png")
        combined[m] = LAYER_COLORS[name]
    Image.fromarray(combined).save("layers_combined.png")


if __name__ == "__main__":
    main()
