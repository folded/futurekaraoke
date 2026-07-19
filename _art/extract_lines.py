#!/usr/bin/env python3
"""Extract the line-art strokes from the background illustration into a clean
black-on-white bitmap suitable for centerline tracing.

Approach: the strokes are thin and locally brighter than their surroundings,
while the clouds / vignette / gradients are broad and smooth. A high-pass
(unsharp) filter — grayscale minus a blurred copy — keeps the thin strokes and
dissolves the smooth regions. Threshold, despeckle, done.
"""
import sys
import numpy as np
from PIL import Image, ImageFilter

SRC = "/Users/tjs/repo/futurekaraoke/images/space-background.webp"


def extract(blur_radius=7.0, thresh=12.0, min_component=6):
    img = Image.open(SRC).convert("RGB")
    # Luminance, but weight blue up a touch since the strokes are lavender.
    r, g, b = [np.asarray(c, dtype=np.float32) for c in img.split()]
    gray = 0.30 * r + 0.40 * g + 0.45 * b  # slightly blue-biased
    gray_img = Image.fromarray(np.clip(gray, 0, 255).astype(np.uint8))

    blurred = np.asarray(
        gray_img.filter(ImageFilter.GaussianBlur(blur_radius)), dtype=np.float32
    )
    highpass = gray - blurred            # positive where locally bright (strokes)
    mask = highpass > thresh             # boolean line mask

    mask = despeckle(mask, min_component)
    return mask


def despeckle(mask, min_size):
    """Drop connected components smaller than min_size px (removes trace noise)
    while keeping intentional star dots. Simple iterative flood fill in numpy."""
    if min_size <= 1:
        return mask
    visited = np.zeros_like(mask, dtype=bool)
    out = mask.copy()
    h, w = mask.shape
    ys, xs = np.nonzero(mask)
    from collections import deque
    for y0, x0 in zip(ys, xs):
        if visited[y0, x0]:
            continue
        comp = []
        dq = deque([(y0, x0)])
        visited[y0, x0] = True
        while dq:
            y, x = dq.popleft()
            comp.append((y, x))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not visited[ny, nx]:
                        visited[ny, nx] = True
                        dq.append((ny, nx))
        if len(comp) < min_size:
            for (y, x) in comp:
                out[y, x] = False
    return out


def save(mask, tag):
    # Black lines on white (trace-ready)
    bw = np.where(mask, 0, 255).astype(np.uint8)
    Image.fromarray(bw).convert("1").save(f"lines_{tag}.bmp")
    Image.fromarray(bw).save(f"lines_{tag}.png")
    # Cyan-on-dark preview to judge quality
    h, w = mask.shape
    prev = np.zeros((h, w, 3), dtype=np.uint8)
    prev[:] = (11, 7, 22)
    prev[mask] = (127, 245, 224)
    Image.fromarray(prev).save(f"preview_{tag}.png")
    print(f"{tag}: {int(mask.sum())} stroke px")


if __name__ == "__main__":
    for tag, (br, th, mc) in {
        "tight": (7.0, 16.0, 8),
        "medium": (8.0, 11.0, 6),
        "loose": (10.0, 7.0, 5),
    }.items():
        save(extract(br, th, mc), tag)
