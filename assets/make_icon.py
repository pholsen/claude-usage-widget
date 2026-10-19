"""Draws the app icon (dark tile, usage gauge, spark) with no dependencies.

Writes icon.png (256 px) and icon.ico (16-256 px) next to this file.
Run: python assets/make_icon.py
"""
import math
import struct
import zlib
from pathlib import Path

BG = (0x1F, 0x1E, 0x1D)
TRACK = (0x3A, 0x38, 0x35)
ACCENT = (0xD9, 0x77, 0x57)
SPARK = (0xF5, 0xF4, 0xEF)

# geometry on a 256 x 256 canvas
TILE_R = 56                   # tile corner radius
ARC_R, ARC_W = 82, 20         # gauge radius and stroke width
ARC_START, ARC_SWEEP = 225, 270  # degrees, clockwise from the start, gap at the bottom
ARC_FILL = 0.65               # filled part of the gauge
RAYS = [(a, 48 if a % 60 == 0 else 36, 5) for a in range(0, 180, 30)]  # angle, half length, half width


def in_tile(x, y):
    qx, qy = max(abs(x - 128) - (128 - TILE_R), 0), max(abs(y - 128) - (128 - TILE_R), 0)
    return math.hypot(qx, qy) <= TILE_R


def arc_point(frac):
    a = math.radians(ARC_START - ARC_SWEEP * frac)
    return 128 + ARC_R * math.cos(a), 128 - ARC_R * math.sin(a)


def arc_colour(x, y):
    """Gauge colour at (x, y), or None. Round caps on both ends and at the fill edge."""
    dx, dy = x - 128, 128 - y
    frac = ((ARC_START - math.degrees(math.atan2(dy, dx))) % 360) / ARC_SWEEP
    if frac <= 1 and abs(math.hypot(dx, dy) - ARC_R) <= ARC_W / 2:
        return ACCENT if frac <= ARC_FILL else TRACK
    for f, colour in ((0, ACCENT), (ARC_FILL, ACCENT), (1, TRACK)):
        px, py = arc_point(f)
        if math.hypot(x - px, y - py) <= ARC_W / 2:
            return colour
    return None


def in_spark(x, y):
    dx, dy = x - 128, y - 128
    for angle, length, width in RAYS:
        a = math.radians(angle)
        along = dx * math.cos(a) + dy * math.sin(a)
        across = -dx * math.sin(a) + dy * math.cos(a)
        if abs(along) < length and abs(across) <= width * (1 - abs(along) / length):
            return True
    return False


def colour_at(x, y):
    if not in_tile(x, y):
        return None
    if in_spark(x, y):
        return SPARK
    return arc_colour(x, y) or BG


def render(size, samples=4):
    scale = 256 / size
    rows = []
    for py in range(size):
        row = bytearray()
        for px in range(size):
            r = g = b = a = 0
            for sy in range(samples):
                for sx in range(samples):
                    c = colour_at((px + (sx + 0.5) / samples) * scale,
                                  (py + (sy + 0.5) / samples) * scale)
                    if c:
                        r, g, b, a = r + c[0], g + c[1], b + c[2], a + 1
            n = samples * samples
            row += bytes((r // a, g // a, b // a, 255 * a // n) if a else (0, 0, 0, 0))
        rows.append(bytes(row))
    return rows


def png(size, rows):
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    raw = b"".join(b"\x00" + row for row in rows)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9))
            + chunk(b"IEND", b""))


def ico(images):
    """images: [(size, png bytes)]; an ICO that embeds PNGs (Windows Vista+)."""
    header = struct.pack("<HHH", 0, 1, len(images))
    offset = 6 + 16 * len(images)
    entries, data = b"", b""
    for size, blob in images:
        dim = 0 if size >= 256 else size
        entries += struct.pack("<BBBBHHII", dim, dim, 0, 0, 1, 32, len(blob), offset + len(data))
        data += blob
    return header + entries + data


if __name__ == "__main__":
    here = Path(__file__).parent
    images = [(s, png(s, render(s))) for s in (16, 24, 32, 48, 64, 128, 256)]
    (here / "icon.png").write_bytes(images[-1][1])
    (here / "icon.ico").write_bytes(ico(images))
    print("icon.png, icon.ico written")
