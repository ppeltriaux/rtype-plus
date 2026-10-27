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

VERSION = '2026-10-28 (bfe81f7)'
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
