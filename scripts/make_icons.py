#!/usr/bin/env python3
"""Generate unified-style toolbar-button icons for the three Finder buttons.

Unified visual language:
  - Same macOS-blue vertical gradient background (with a subtle top highlight)
  - Same rounded-corner square mask (radius 230)
  - Same solid-white foreground glyphs, consistent stroke/scale
Functions differ only by glyph, so the set reads as one family.

No external deps: raw RGBA canvas + zlib PNG encoder.
"""
import struct, zlib, math, os

W = H = 1024

def new_canvas():
    return bytearray(W * H * 4)

def blend(buf, x, y, r, g, b, a):
    if not (0 <= x < W and 0 <= y < H) or a <= 0:
        return
    i = (y * W + x) * 4
    sa = a / 255.0
    da = buf[i + 3] / 255.0
    out_a = sa + da * (1 - sa)
    if out_a <= 0:
        return
    out_r = (r * sa + buf[i]     * da * (1 - sa)) / out_a
    out_g = (g * sa + buf[i + 1] * da * (1 - sa)) / out_a
    out_b = (b * sa + buf[i + 2] * da * (1 - sa)) / out_a
    buf[i]     = max(0, min(255, int(out_r)))
    buf[i + 1] = max(0, min(255, int(out_g)))
    buf[i + 2] = max(0, min(255, int(out_b)))
    buf[i + 3] = max(0, min(255, int(out_a * 255)))

def round_rect(buf, x0, y0, x1, y1, radius, color, alpha=255):
    r, g, b = color
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    radius = min(radius, (x1 - x0) // 2, (y1 - y0) // 2)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            inside = True
            tests = [
                (x < x0 + radius and y < y0 + radius, (x0 + radius, y0 + radius)),
                (x > x1 - radius and y < y0 + radius, (x1 - radius, y0 + radius)),
                (x < x0 + radius and y > y1 - radius, (x0 + radius, y1 - radius)),
                (x > x1 - radius and y > y1 - radius, (x1 - radius, y1 - radius)),
            ]
            for cond, (cx, cy) in tests:
                if cond and (x - cx) ** 2 + (y - cy) ** 2 > radius * radius:
                    inside = False
            if inside:
                blend(buf, x, y, r, g, b, alpha)

def thick_line(buf, x0, y0, x1, y1, width, color, alpha=255):
    r, g, b = color
    dx = x1 - x0; dy = y1 - y0
    length = math.hypot(dx, dy)
    if length == 0:
        return
    hw = width / 2.0
    minx = int(min(x0, x1) - hw) - 1; maxx = int(max(x0, x1) + hw) + 1
    miny = int(min(y0, y1) - hw) - 1; maxy = int(max(y0, y1) + hw) + 1
    for y in range(miny, maxy + 1):
        for x in range(minx, maxx + 1):
            t = ((x - x0) * dx + (y - y0) * dy) / (length * length)
            t = max(0.0, min(1.0, t))
            px = x0 + t * dx; py = y0 + t * dy
            if math.hypot(x - px, y - py) <= hw:
                blend(buf, x, y, r, g, b, alpha)

def fill_triangle(buf, pts, color, alpha=255):
    r, g, b = color
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    minx = int(min(xs)); maxx = int(max(xs)); miny = int(min(ys)); maxy = int(max(ys))
    def sign(ax, ay, bx, by, cx, cy):
        return (ax - cx) * (by - cy) - (bx - cx) * (ay - cy)
    for y in range(miny, maxy + 1):
        for x in range(minx, maxx + 1):
            d1 = sign(x, y, pts[0][0], pts[0][1], pts[1][0], pts[1][1])
            d2 = sign(x, y, pts[1][0], pts[1][1], pts[2][0], pts[2][1])
            d3 = sign(x, y, pts[2][0], pts[2][1], pts[0][0], pts[0][1])
            neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
            pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
            if not (neg and pos):
                blend(buf, x, y, r, g, b, alpha)

def png_encode(buf, path):
    def chunk(typ, body):
        return struct.pack(">I", len(body)) + typ + body + struct.pack(">I", zlib.crc32(typ + body) & 0xffffffff)
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 6, 0, 0, 0)
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += buf[y * W * 4:(y + 1) * W * 4]
    idat = zlib.compress(bytes(raw), 9)
    with open(path, "wb") as f:
        f.write(sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b""))

# ---- shared background: blue gradient + top highlight, rounded mask ----
TOP = (40, 155, 255)     # #289BFF
BOT = (10, 110, 224)     # #0A6EE0
RADIUS = 230

def fill_background(buf):
    for y in range(H):
        t = y / (H - 1)
        cr = int(TOP[0] + (BOT[0] - TOP[0]) * t)
        cg = int(TOP[1] + (BOT[1] - TOP[1]) * t)
        cb = int(TOP[2] + (BOT[2] - TOP[2]) * t)
        hl = 50 * (1 - y / 260) if y < 260 else 0.0   # top gloss
        for x in range(W):
            inside = True
            tests = [
                (x < RADIUS and y < RADIUS, (RADIUS, RADIUS)),
                (x > W - RADIUS and y < RADIUS, (W - RADIUS, RADIUS)),
                (x < RADIUS and y > H - RADIUS, (RADIUS, H - RADIUS)),
                (x > W - RADIUS and y > H - RADIUS, (W - RADIUS, H - RADIUS)),
            ]
            for cond, (cx, cy) in tests:
                if cond and (x - cx) ** 2 + (y - cy) ** 2 > RADIUS * RADIUS:
                    inside = False
            if inside:
                i = (y * W + x) * 4
                buf[i] = cr; buf[i + 1] = cg; buf[i + 2] = cb; buf[i + 3] = 255
                if hl > 0:
                    blend(buf, x, y, 255, 255, 255, hl)

WHITE = (255, 255, 255)

def draw_terminal():
    buf = new_canvas()
    fill_background(buf)
    # prompt chevron ">"  (right-pointing)
    thick_line(buf, 358, 512, 672, 370, 74, WHITE)
    thick_line(buf, 358, 512, 672, 654, 74, WHITE)
    # solid cursor block "_"
    round_rect(buf, 372, 744, 470, 802, 10, WHITE)
    return buf

def draw_copy():
    buf = new_canvas()
    fill_background(buf)
    # back sheet (ghost copy) offset up-right, semi-transparent
    round_rect(buf, 372, 300, 724, 652, 72, WHITE, 150)
    # front sheet
    round_rect(buf, 300, 360, 652, 712, 72, WHITE, 255)
    return buf

def draw_pathbar():
    buf = new_canvas()
    fill_background(buf)
    # three folder blocks, horizontally centered
    bw = 180; gap = 36
    start = (W - (3 * bw + 2 * gap)) // 2
    y0, y1 = 410, 600
    for i in range(3):
        x0 = start + i * (bw + gap)
        round_rect(buf, x0, y0, x0 + bw, y1, 44, WHITE, 255)
    # two chevrons between blocks
    cy = (y0 + y1) // 2
    for i in range(2):
        xc = start + (i + 1) * bw + i * gap + gap // 2
        fill_triangle(buf, [(xc - 16, cy - 40), (xc - 16, cy + 40), (xc + 40, cy)], WHITE, 255)
    return buf

OUT = "/tmp/icicons2"
os.makedirs(OUT, exist_ok=True)
png_encode(draw_terminal(), f"{OUT}/terminal.png")
png_encode(draw_copy(),     f"{OUT}/copy.png")
png_encode(draw_pathbar(),  f"{OUT}/pathbar.png")
print("written:", OUT)
