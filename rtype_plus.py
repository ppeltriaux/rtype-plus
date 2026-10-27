#!/usr/bin/env python3
"""R-Type Plus: patch your own arcade R-Type ROMs (MAME's "rtype" set, World) into the game
with a two-player co-op mode, a stage select, an Armour mode and a Boss Rush.

  python3 rtype_plus.py <your rtype.zip, or a folder of its files> [--set rtype|rtypeu] [-o DIR]

Your ROMs are found by their contents (SHA1), whatever their names, in a zip or a folder (a
merged set with the clones in it is fine). The patch holds no 3 bytes in a row of the original:
the program gets the hack's own bytes, and any 3 bytes or more in a row your program already has
(the instructions each hook moves aside, short sequences the new code shares with the original)
are copied from where they are in yours; the new graphics and player 2's palettes are made from
your ROMs by the code below; every file written is checked against the SHA1 it must have. Writes DIR/rtype.zip (or DIR/rtypeu.zip with --set rtypeu: the same game as
MAME's R-Type (US) clone, to sit beside an original rtype.zip), DIR being ./rtype-plus unless
-o says otherwise. Your files are only read. Standard library only (Python 3.8 or later).
"""
import argparse
import base64
import hashlib
import json
import os
import sys
import zipfile
import zlib

VERSION = '2026-10-28 (d357ca5)'
PATCH = """
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
hbP56g==
"""
# --- the new tiles and player 2's palettes, made from your ROMs ---
import colorsys
import math

# the program ROMs: (even-byte ROM, odd-byte ROM, CPU address); the fg and sprite ROMs' planes,
# plane 0 first (each sprite plane a 64K + 32K pair)
PROGRAM = [("rt_r-l0-b.3b", "rt_r-h0-b.1b", 0x00000), ("rt_r-l1-b.3c", "rt_r-h1-b.1c", 0x20000)]
FG_PLANES = [("rt_b-a0.3c",), ("rt_b-a1.3d",), ("rt_b-a2.3a",), ("rt_b-a3.3e",)]
SPRITE_PLANES = [("rt_r-00.1h", "rt_r-01.1j"), ("rt_r-10.1k", "rt_r-11.1l"),
                 ("rt_r-20.3h", "rt_r-21.3j"), ("rt_r-30.3k", "rt_r-31.3l")]

PAL_BASE = 0x3B000               # ROM palettes (3B00:0000): 16 colours x (R, G, B), 0-31 each
P2_PALETTES = {2: 176, 86: 177}  # player 2's copies of the R-9's and the Force's palettes, in
                                 # zero-filled entries no code reads (108-191: an invulnerable
                                 # run through all eight stages read none); src/v30/coop.asm MapPal
# Co-op: player 2's colours (the Neo Geo port's too). Per ROM sprite
# palette, its colour groups: the R-9's (palette 2, also its shots and wave cannon) canopy / nose /
# flame, red stripe, gold markings; the Force's (86) fire. A scheme gives each group a hue
# (saturation and value kept, so fades still work); groups it leaves out keep their colours.
# Player 2's sprites show these palettes in place of their slot's. Previewed schemes, P2_SCHEME
# picks one:
P2_GROUPS = {2: {"canopy": (3, 4, 5), "stripe": (6, 7), "marks": (11, 12, 13)},
             86: {"fire": (10, 11, 12, 13, 14)}}
P2_SCHEMES = {"crimson": dict(canopy=352, stripe=45, marks=45, fire=330),
              "emerald": dict(canopy=140, stripe=45, marks=45, fire=125),
              "violet": dict(canopy=275, stripe=320, marks=45, fire=285),
              "sunset": dict(canopy=22, stripe=205, marks=50, fire=200),
              "ice": dict(canopy=205, stripe=190, marks=190, fire=195)}
P2_SCHEME = "crimson"
# Player 2's HUD text in crimson: copies of the original's HUD glyphs drawing with the HUD
# palette's (slot 15, ROM palette $1F) red pens instead (11 red, 12 dark red)
P2_PENS = {2: 11, 3: 12, 6: 12, 7: 11, 8: 11}
# The arcade hack's new fg tiles go on blank codes the game never writes (an invulnerable run
# through all eight stages wrote none of them), from the top down; the 1P / 2P tags on two blank
# sprite tiles outside every sprite that run drew (each sprite's tiles: code + 8 x + y over its size)
P2_GLYPHS = [0x30 + d for d in range(10)] + [0x011, 0x065, 0x066, 0x063, 0x064, 0x06A] + \
    [ord(c) for c in "PRESTA"]   # digits, the score's blank, "2P-", the ship icon, PRESS START
GAUGE_TILES = list(range(0x6AD, 0x6C0))     # the beam gauge's caps and cells
FG_SPARE = range(0xF63, 0xF00, -2)  # blank codes never written: the odd ones $F63-$F01 (the
                                     # even blank ones there are written: a stage's empty cells)
ARMOUR_PENS = {14: 8, 15: 12}   # the Armour cells' green / yellow (3+ ships, 2): the HUD's tile
                                # palette has neither and no pen to spare (stage tiles drawn with
                                # it use its black pens 14 / 15), so its light blue and amber
TAG_TILES = (0x97C, 0x97D)      # the 2P and 1P tags (sprite tiles)
# The title's PLUS (src/v30/plus.asm) under the R-TYPE logo, in the logo's palette (ROM palette
# $5E: its teal chrome): extruded letters lit from the upper left as the logo's are, the faces
# towards the light white (lavender rims on top faces, pink low down on left ones), the others
# teal, dark at the stroke's middle to bright at its rim. Its tiles go on blank sprite codes no
# sprite showed in a survey (2026-10-28: attract mode, stages 1-8 played invulnerable, co-op
# stages 3 and 6, Boss Rush through its 8 bosses, the ending, continue, game over, rankings)
PLUS_SPARE = [0x8CA, 0x8CB, 0x8D2, 0x8D9, 0x8DA, 0x8DD, 0x8DE, 0x8E1, 0x8E2, 0x8E5, 0x8E6, 0x8E9,
              0x8EA, 0x8ED, 0x8EE, 0x901, 0x902, 0x90D, 0x90E, 0x911, 0x912, 0x91D, 0x91E, 0x921,
              0x922, 0x928, 0x92B, 0x92D, 0x92E, 0x930, 0x933, 0x934, 0x937, 0x940, 0x943, 0x944]
PLUS_H = 22                     # letter height (the gap between the logo and the (c) line: 32)
PLUS_R = 3.0                    # stroke radius
PLUS_CORNER = 4.0               # corner radius (of the strokes' middle lines)
PLUS_W = 16                     # letter width (L: 2 less)
PLUS_GAP = 5                    # between letters
PLUS_SLANT = 0.2                # its lean to the right: pixels across a line up
PLUS_RIGHT, PLUS_Y = 361, 196   # the art's right edge on screen (the logo's), its top
PLUS_GRID = (266, 191, 7, 2)    # its sprites' grid: left, top, columns, rows (a column either side
                                # of the art for the glint's mask, room above it for the twinkle)
PLUS_BAND = [0xB, 0xF, 7, 7, 0xF, 0xB]  # the glint's band across, leaning right 1 in 2
PLUS_STEP = 3                   # pixels the glint moves a frame
PLUS_STARS = [1, 2, 4, 5]       # twinkle arm lengths (a tile each)


def read_program(roms):
    """the program as the CPU sees it (256 KB) from the program ROMs ({board name: contents})"""
    data = bytearray(0x40000)
    for lo, hi, base in PROGRAM:
        data[base:base + 2 * len(roms[lo]):2] = roms[lo]
        data[base + 1:base + 2 * len(roms[hi]):2] = roms[hi]
    return data


def split_program(data):
    """{board name: contents} of the program ROMs holding data"""
    out = {}
    for lo, hi, base in PROGRAM:
        out[lo] = bytes(data[base:base + 0x20000:2])
        out[hi] = bytes(data[base + 1:base + 0x20000:2])
    return out


def p2_palettes(prog):
    """Player 2's palettes: the R-9's (2) and the Force's (86) with their colour groups turned to
    the scheme (hue set, saturation and value kept), written to their P2_PALETTES entries."""
    scheme = P2_SCHEMES[P2_SCHEME]
    for n, dest in P2_PALETTES.items():
        src = PAL_BASE + 48 * n
        pal = [list(prog[src + 3 * i:src + 3 * i + 3]) for i in range(16)]
        for g, idx in P2_GROUPS[n].items():
            if g not in scheme:
                continue
            for i in idx:
                h, sat, v = colorsys.rgb_to_hsv(*(c / 31 for c in pal[i]))
                if g == "fire":
                    sat = max(0.25, sat)
                pal[i] = [round(c * 31) for c in colorsys.hsv_to_rgb(scheme[g] / 360, sat, v)]
        at = PAL_BASE + 48 * dest
        if any(prog[at:at + 48]):
            raise ValueError("palette %d is not free" % dest)
        prog[at:at + 48] = bytes(c for col in pal for c in col)


def fg_tiles(roms):
    """The fg ROM as 4096 8x8 tiles of pens (rows of 8)."""
    pl = [roms[f[0]] for f in FG_PLANES]
    tiles = []
    for c in range(len(pl[0]) // 8):
        tiles.append([[sum(((pl[p][c * 8 + y] >> (7 - x)) & 1) << p for p in range(4))
                       for x in range(8)] for y in range(8)])
    return tiles


def put_fg(roms, code, tile):
    for p, f in enumerate(FG_PLANES):
        data = bytearray(roms[f[0]])
        for y in range(8):
            data[code * 8 + y] = sum(((tile[y][x] >> p) & 1) << (7 - x) for x in range(8))
        roms[f[0]] = bytes(data)


def put_sprite(roms, code, tile):
    """A 16x16 sprite tile (rows of 16 pens) at code: each plane is a 64K + 32K ROM pair, 32
    bytes a tile, a row's left 8 pixels at + y, its right 8 at + 16 + y."""
    for p, (lo, hi) in enumerate(SPRITE_PLANES):
        data = bytearray(roms[lo] + roms[hi])
        for y in range(16):
            for half in range(2):
                data[code * 32 + half * 16 + y] = sum(((tile[y][half * 8 + x] >> p) & 1) << (7 - x)
                                                      for x in range(8))
        roms[lo], roms[hi] = bytes(data[:len(roms[lo])]), bytes(data[len(roms[lo]):])


def armour_tiles(fg):
    """Armour's ship gauge in the beam gauge's style, 6 tiles: a cell green, yellow, red, empty;
    the left cap; the right cap. A cell is the gauge's body ($6BA full, $6AE empty) with a light
    line (pen 4, the frame's) down each side in the fill rows, so cells meet in a 2-pixel
    separator like the walls; the fill is flat: pen 14 (green) or 15 (yellow) (the Neo Geo's
    HUD palette's unused pens; the arcade maps them, ARMOUR_PENS), or 11 (the HUD's red). The caps
    are the original's ($6AD, $6BF) with their nub and wall moved against the cells (shifted 4
    pixels inwards, the 4 pixels of box inside them gone) so a cap does not read as half a cell."""
    def cell(src, pen):
        t = [list(row) for row in src]
        for y in range(2, 7):
            for x in range(1, 7):
                if pen:
                    t[y][x] = pen
            t[y][0] = t[y][7] = 4
        return t
    left = [[9] * 4 + row[:4] for row in fg[0x6AD]]
    right = [row[4:] + [9] * 4 for row in fg[0x6BF]]
    return [cell(fg[0x6BA], 14), cell(fg[0x6BA], 15), cell(fg[0x6BA], 11), cell(fg[0x6AE], 0), left, right]


def colon_tile(fg):
    """Boss Rush's timer: a colon (the font has none), the full stop's dot and a copy 4 lines up
    (the font's background is pen 1, its glyphs pens 2 and 3)."""
    dot = fg[0x2E]
    return [[dot[y + 4][x] if y + 4 < 8 and dot[y + 4][x] > 1 else dot[y][x] for x in range(8)]
            for y in range(8)]


def hud_tiles(roms):
    """Player 2's crimson glyphs and mirrored gauge, Armour's cells, the tags, Boss Rush's colon,
    the title's PLUS, written into roms ({board name: contents}); -> their codes: glyphs [(the
    original's code, its copy's)], gauge [codes], armour [codes], colon code, PLUS's (plus_tiles)."""
    fg = fg_tiles(roms)
    spare = [c for c in FG_SPARE if not any(any(r) for r in fg[c])]
    if len(spare) < len(P2_GLYPHS) + len(GAUGE_TILES) + 7:
        raise ValueError("not enough spare fg codes")
    glyphs, gauge, armour = [], [], []
    for c in P2_GLYPHS:
        code = spare.pop(0)
        put_fg(roms, code, [[P2_PENS.get(v, v) for v in row] for row in fg[c]])
        glyphs.append((c, code))
    for c in GAUGE_TILES:
        code = spare.pop(0)
        put_fg(roms, code, [[P2_PENS.get(v, v) for v in row[::-1]] for row in fg[c]])
        gauge.append(code)
    for t in armour_tiles(fg):
        code = spare.pop(0)
        put_fg(roms, code, [[ARMOUR_PENS.get(v, v) for v in row] for row in t])
        armour.append(code)
    colon = spare.pop(0)
    put_fg(roms, colon, colon_tile(fg))
    for tile, digit in zip(TAG_TILES, (0x32, 0x31)):
        # the HUD font's digit and P (fg, 8x8 each) on 16 x 16, in ship palette pens: outline
        # black (1) only around the glyph, the light pen the canopy's brightest (5), the
        # shadow its darkest (3); the rest transparent
        tag = [[0] * 16 for _ in range(16)]
        for k, c in enumerate((digit, 0x50)):
            for y in range(8):
                for x in range(8):
                    tag[4 + y][k * 8 + x] = {1: 1, 2: 5, 3: 3}.get(fg[c][y][x], 0)
        lit = {(y, x) for y in range(16) for x in range(16) if tag[y][x] in (5, 3)}
        for y in range(16):
            for x in range(16):
                if tag[y][x] == 1 and not any((y + dy, x + dx) in lit for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
                    tag[y][x] = 0
        put_sprite(roms, tile, tag)
    return glyphs, gauge, armour, colon, plus_tiles(roms)


def plus_art():
    """PLUS as {(x, y): pen} (the logo palette's pens), x 0 at its left, y 0 at its top; its width"""
    r, h, c = PLUS_R, PLUS_H, PLUS_CORNER

    def path(pts):                          # a polyline, its corners rounded: segments
        out = [pts[0]]
        for a, b, e in zip(pts, pts[1:], pts[2:]):
            u = [a[k] - b[k] for k in (0, 1)]
            v = [e[k] - b[k] for k in (0, 1)]
            lu, lv = math.hypot(*u), math.hypot(*v)
            p0 = [b[k] + u[k] / lu * c for k in (0, 1)]
            p1 = [b[k] + v[k] / lv * c for k in (0, 1)]
            for n in range(7):              # a quadratic curve through the corner
                t = n / 6
                out.append(tuple((1 - t) ** 2 * p0[k] + 2 * t * (1 - t) * b[k] + t * t * p1[k] for k in (0, 1)))
        out.append(pts[-1])
        return list(zip(out, out[1:]))

    x0, y0, y1, ym = r, r, h - r, h * 0.52
    art, left = {}, 0
    for letter, w in (("P", PLUS_W), ("L", PLUS_W - 2), ("U", PLUS_W), ("S", PLUS_W)):
        x1 = w - r
        segs = path({"P": [(x0, y1), (x0, y0), (x1, y0), (x1, ym), (x0, ym)],
                     "L": [(x0, y0), (x0, y1), (x1, y1)],
                     "U": [(x0, y0), (x0, y1), (x1, y1), (x1, y0)],
                     "S": [(x1, y0), (x0, y0), (x0, ym), (x1, ym), (x1, y1), (x0, y1)]}[letter])
        for y in range(h):
            for x in range(-1, w + 1 + math.ceil(PLUS_SLANT * h)):
                hits = []                   # 4 x 4 samples: their offsets from the middle line
                for sy in range(4):
                    for sx in range(4):
                        py = y + (sy + 0.5) / 4
                        px = x + (sx + 0.5) / 4 - PLUS_SLANT * (h - py)     # (upright)
                        best = None
                        for (ax, ay), (bx, by) in segs:
                            dx, dy = bx - ax, by - ay
                            t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy or 1)))
                            v = (px - ax - t * dx, py - ay - t * dy)
                            if best is None or v[0] ** 2 + v[1] ** 2 < best[0] ** 2 + best[1] ** 2:
                                best = v
                        if best[0] ** 2 + best[1] ** 2 <= r * r:
                            hits.append(best)
                if len(hits) < 8:
                    continue
                nx = sum(v[0] for v in hits) / len(hits) / r
                ny = sum(v[1] for v in hits) / len(hits) / r
                rim = math.hypot(nx, ny)                        # 0 the middle, 1 the rim
                if -nx - 1.2 * ny > 0.08:                       # towards the light
                    if ny < nx:                                 # a top face
                        pen = 0xE if rim > 0.85 else 0xF if rim > 0.65 else 7
                    else:                                       # a left face
                        pen = 7 if y < 0.45 * (h - 1) else 8 if y < 0.75 * (h - 1) else 9
                else:
                    pen = [2, 3, 4, 5, 6, 0xB][min(5, int(rim * 5.99))]
                art[(left + x, y)] = pen
        left += w + PLUS_GAP
    return art, left - PLUS_GAP + math.ceil(PLUS_SLANT * h)


def plus_tiles(roms):
    """PLUS's sprite tiles written into roms; -> where they go: {"fill": [(screen x, y, code)],
    "mask": [...], "band": [(dy, code)] (the glint band's tiles, under each other), "band_y",
    "band_x": (first, last) screen x of the band, "stars": [codes], "star": (x, y) of the
    twinkle's tile}. The fill is the letters; the mask, drawn over the band, is the art's rows
    on the whole grid but the letters, in black (pen 1), so the band shows on the letters only."""
    art, w = plus_art()
    gx, gy, cols, rows = PLUS_GRID
    left = PLUS_RIGHT + 1 - (max(x for x, _ in art) + 1)
    ox, oy = left - gx, PLUS_Y - gy
    planes = [roms[lo] + roms[hi] for lo, hi in SPRITE_PLANES]
    spare = [c for c in PLUS_SPARE if not any(any(p[c * 32:c * 32 + 32]) for p in planes)]
    grid = {(x + ox, y + oy): pen for (x, y), pen in art.items()}
    mask = {(x, y): 1 for y in range(oy, oy + PLUS_H) for x in range(cols * 16) if (x, y) not in grid}
    out = {"fill": [], "mask": [], "band": [], "stars": []}

    def put(pixels, x0, y0):
        code = spare.pop(0)
        put_sprite(roms, code, [[pixels.get((x0 + x, y0 + y), 0) for x in range(16)] for y in range(16)])
        return code

    for name, pixels in (("fill", grid), ("mask", mask)):
        for col in range(cols):
            for row in range(rows):
                if any((col * 16 + x, row * 16 + y) in pixels for x in range(16) for y in range(16)):
                    out[name].append((gx + col * 16, gy + row * 16, put(pixels, col * 16, row * 16)))
    band = {}
    for y in range(PLUS_H):
        for k, pen in enumerate(PLUS_BAND):
            band[((PLUS_H - 1 - y) // 2 + k, oy + y)] = pen
    bw = max(x for x, _ in band) + 1
    for row in range(rows):
        if any(y // 16 == row for _, y in band):
            out["band"].append((row * 16, put(band, 0, row * 16)))
    out["band_y"] = gy
    out["band_x"] = (gx, gx + cols * 16 - bw)
    tx = max(x for (x, y) in art if y < PLUS_H // 3) - 2       # the twinkle: the S's top right
    ty = min(y for (x, y) in art if x >= tx - 2) + 1
    for arm in PLUS_STARS:
        star = {}
        for k in range(-arm, arm + 1):
            pen = 7 if abs(k) < 2 else 0xF if abs(k) < 4 else 0xE
            star[(8 + k, 8)] = star[(8, 8 + k)] = pen
        out["stars"].append(put(star, 0, 0))
    out["star"] = (left + tx - 8, PLUS_Y + ty - 8)
    return out
# --- end of the tiles and palettes ---
MAX_SIZE = 0x20000                 # (the largest ROM in the set: files above it are not looked at)
SETS = ("rtype", "rtypeu")


class PatchError(Exception):
    pass


def sha1(data):
    return hashlib.sha1(data).hexdigest()


def load_inputs(src):
    """{sha1: contents} of every file up to MAX_SIZE in the zip or folder src"""
    found = {}
    if os.path.isdir(src):
        for root, _, names in os.walk(src):
            for n in names:
                path = os.path.join(root, n)
                if os.path.getsize(path) <= MAX_SIZE:
                    with open(path, "rb") as f:
                        data = f.read()
                    found[sha1(data)] = data
    elif zipfile.is_zipfile(src):
        with zipfile.ZipFile(src) as z:
            for info in z.infolist():
                if not info.is_dir() and info.file_size <= MAX_SIZE:
                    data = z.read(info)
                    found[sha1(data)] = data
    else:
        raise PatchError("%s: not a zip file or a folder" % src)
    return found


def decode(text):
    return json.loads(zlib.decompress(base64.b64decode("".join(text.split()))))


def build(patch, inputs, set_name):
    """[(file name, contents)] of the patched set set_name from inputs ({sha1: contents})"""
    missing = sorted((v["name"], v["size"], h) for h, v in patch["inputs"].items() if h not in inputs)
    if missing:
        raise PatchError("not found in your files (by content), so they are not MAME's \"rtype\" (World) set:\n" +
                         "\n".join("  %s  %6d bytes  SHA1 %s" % m for m in missing))
    roms = {v["name"]: inputs[h] for h, v in patch["inputs"].items()}
    orig = bytes(read_program(roms))
    prog = read_program(roms)
    try:
        p2_palettes(prog)                           # (made from your ROMs, as are the tiles)
        files = dict(roms)
        hud_tiles(files)
    except ValueError as e:
        raise PatchError(str(e))
    for op in patch["program"]:                     # ["L", address, our bytes] or
        if op[0] == "L":                            # ["C", address, your program's address, length]
            new = bytes.fromhex(op[2])
            prog[op[1]:op[1] + len(new)] = new
        else:
            prog[op[1]:op[1] + op[3]] = orig[op[2]:op[2] + op[3]]
    files.update(split_program(prog))
    out = []
    for e in patch["sets"][set_name]:
        data = files[e["board"]] if e["board"] else bytes(e["size"])
        if len(data) != e["size"] or sha1(data) != e["sha1"]:
            raise PatchError("%s: the result is not what it must be (SHA1 %s, wanted %s)" % (e["name"], sha1(data), e["sha1"]))
        out.append((e["name"], data))
    return out


def write_zip(files, path):
    tmp = path + ".part"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in files:
            z.writestr(name, data)
    os.replace(tmp, path)


def main(argv=None):
    ap = argparse.ArgumentParser(description="R-Type Plus %s: patch your own arcade R-Type ROMs "
                                 "(MAME's \"rtype\" set)." % (VERSION or "(development)"))
    ap.add_argument("roms", help="your rtype.zip, or a folder with its files")
    ap.add_argument("--set", choices=SETS, default="rtype",
                    help="rtype (default): replaces the World set; rtypeu: as MAME's R-Type (US) clone, beside an original rtype.zip")
    ap.add_argument("-o", "--out", default="rtype-plus", help="the folder to write the zip to (default: ./rtype-plus)")
    args = ap.parse_args(argv)
    if PATCH is None:
        print("this copy of the patcher carries no patch", file=sys.stderr)
        return 2
    path = os.path.join(args.out, args.set + ".zip")
    if os.path.exists(path) and os.path.exists(args.roms) and os.path.samefile(path, args.roms):
        print("%s is your input: pick another output folder (-o), so your original stays as it is" % path, file=sys.stderr)
        return 2
    try:
        patch = decode(PATCH)
        files = build(patch, load_inputs(args.roms), args.set)
    except PatchError as e:
        print("error: %s" % e, file=sys.stderr)
        return 1
    os.makedirs(args.out, exist_ok=True)
    write_zip(files, path)
    ours = sum(len(op[2]) // 2 for op in patch["program"] if op[0] == "L")
    copied = sum(op[3] for op in patch["program"] if op[0] == "C")
    print("wrote %s: %d files; the program: %d bytes of the hack's, %d copied from your own; the graphics\n"
          "and palettes made from yours. Put it where MAME looks for ROMs (it warns that the checksums\n"
          "are wrong: the ROMs are changed) and run \"%s\"." % (path, len(files), ours, copied, args.set))
    return 0


if __name__ == "__main__":
    sys.exit(main())
