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

VERSION = '2026-10-28 (04294d3)'
PATCH = """
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
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
