"""Draws the app icon (dark tile, usage gauge, spark) with no dependencies.

Writes icon.png (256 px), icon.ico (16-256 px) and icon_mac.png (512 px, padded)
next to this file, and the macOS app icon to Claude Usage.app/Contents/Resources/icon.icns.
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


def render(size, samples=4, pad=0.0):
    """pad: empty margin on each side as a fraction of the size (macOS icons leave ~10%)."""
    scale = 256 / size / (1 - 2 * pad)
    shift = 256 * pad * scale * size / 256
    rows = []
    for py in range(size):
        row = bytearray()
        for px in range(size):
            r = g = b = a = 0
            for sy in range(samples):
                for sx in range(samples):
                    c = colour_at((px + (sx + 0.5) / samples) * scale - shift,
                                  (py + (sy + 0.5) / samples) * scale - shift)
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


ICNS_TYPES = [(b"icp4", 16), (b"icp5", 32), (b"icp6", 64), (b"ic07", 128), (b"ic08", 256),
              (b"ic09", 512), (b"ic10", 1024), (b"ic11", 32), (b"ic12", 64), (b"ic13", 256),
              (b"ic14", 512)]


def icns(pngs):
    """pngs: {size: png bytes}; a macOS .icns built from PNG entries."""
    body = b"".join(kind + struct.pack(">I", 8 + len(pngs[s])) + pngs[s] for kind, s in ICNS_TYPES)
    return b"icns" + struct.pack(">I", 8 + len(body)) + body


if __name__ == "__main__":
    here = Path(__file__).parent
    images = [(s, png(s, render(s))) for s in (16, 24, 32, 48, 64, 128, 256)]
    (here / "icon.png").write_bytes(images[-1][1])
    (here / "icon.ico").write_bytes(ico(images))
    # macOS: padded artwork; big sizes need fewer samples to stay fast
    mac = {s: png(s, render(s, samples=4 if s <= 256 else 2, pad=0.1))
           for s in {s for _, s in ICNS_TYPES}}
    (here / "icon_mac.png").write_bytes(mac[512])
    app_res = here.parent / "Claude Usage.app" / "Contents" / "Resources"
    app_res.mkdir(parents=True, exist_ok=True)
    (app_res / "icon.icns").write_bytes(icns(mac))
    print("icon.png, icon.ico, icon_mac.png, Claude Usage.app/Contents/Resources/icon.icns written")
