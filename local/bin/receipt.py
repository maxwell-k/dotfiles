#!/usr/bin/env -S uv run
"""Scan a receipt, process it, save a PDF."""

# /// script
# dependencies = [
#   "numpy",
#   "opencv-python",
# ]
# requires-python = ">=3.13"
# ///

from os import environ
from pathlib import Path
from subprocess import run

import cv2
import numpy as np

SCANIMAGE = "/usr/bin/scanimage"
TRAILER_THRESHOLD = 250
ENVRC = {"SANE_CONFIG_DIR": str(Path("~/.config/adf").expanduser())}
CMD = (
    SCANIMAGE,
    "--format=pnm",
    "--resolution=300",
    "--mode=True Gray",
    "--source=Automatic Document Feeder(center aligned)",
)


def _largest(img: np.ndarray) -> np.ndarray:
    blur = cv2.GaussianBlur(img, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 200, 255, cv2.THRESH_BINARY)
    kernel = np.ones((5, 5), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return sorted(contours, key=cv2.contourArea, reverse=True)[0]


def _main() -> int:
    env = environ.copy()
    env.update(ENVRC)

    result = run((SCANIMAGE, "-L"), capture_output=True, check=True, env=env)
    if b"brother5" not in result.stdout:
        msg = "brother5 scanner not found"
        raise RuntimeError(msg)

    cache = Path("cache.pnm")
    if cache.is_file():
        scan = cache.read_bytes()
    else:
        result = run(CMD, capture_output=True, check=True, env=env)
        scan = result.stdout
        cache.write_bytes(scan)

    img = cv2.imdecode(np.frombuffer(scan, np.uint8), cv2.IMREAD_GRAYSCALE)
    if img is None:
        msg = "Failed to read image from standard input."
        raise RuntimeError(msg)

    # crop trailer
    keep = ~(np.all(img >= TRAILER_THRESHOLD, axis=1))
    img = img[keep, :]

    # deskew
    rect = cv2.minAreaRect(_largest(img))
    rotation = cv2.getRotationMatrix2D(rect[0], rect[-1] + 90.0, 1.0)
    size = (img.shape[1], img.shape[0])
    img = cv2.warpAffine(img, rotation, size, flags=cv2.INTER_CUBIC)

    # crop the sides
    (centre, _), (_, width), _ = rect
    left = int(centre - width / 2)
    right = int(left + width)
    img = img[:, left:right]

    cv2.imwrite("output.png", img)

    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
