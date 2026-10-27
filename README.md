# R-Type Plus 2026-10-28 (d357ca5)

A patch for the 1987 arcade R-Type (Irem, M72 board) that adds four things the original never
had, on the original board's own program (and a PLUS, in the logo's own colours, under the title):

- **Two players at once.** A 2P start begins co-op; either player can join a game later with a coin
  and their start button. Player 2 flies a crimson R-9 with a Force of its own, the beam gauge splits
  while both play, and a lost ship flies in again where the game is while the partner plays.
- **A stage select.** On the start screen, left and right pick the stage (`STAGE n` on the credit line).
- **Armour.** Up and down on the start screen pick CLASSIC, ARMOUR or BOSS RUSH. In Armour an enemy's
  hit with ships to spare costs a ship and a laser level, and the game goes on where it is (a wall
  still destroys the ship).
- **Boss Rush.** The seven bosses back to back (stage 3's, the whole battleship, is left out), every
  ship fully armed (the Force, the blue laser, two bits, missiles, a speed-up), against a run timer,
  with a ranking table of its own (kept until power-off, like the game's).

It runs in MAME, and on anything that runs MAME's `rtype` set. MAME warns that the ROMs' checksums
are wrong: they are changed, that is expected.

## What you need

- **Your own copy of the game:** MAME's `rtype` set (R-Type, World), as a zip or a folder. The files
  are found by their contents, whatever their names; a merged set with the clones in it is fine.
  These 22 files (the three PALs MAME lists are not needed):

| File | Bytes | SHA1 |
|---|---|---|
| `m72_a-8l-.ic66` | 256 | `00e20cf754b6fd5138ee4d2f6ec28dff9e292fe6` |
| `m72_a-9l-.ic75` | 256 | `f13b0a4b52dcc6704063b676f09d83dcba170133` |
| `rt_b-a0.3c` | 32768 | `687061ecade2ebd0bd1343c9c4a831791853f79c` |
| `rt_b-a1.3d` | 32768 | `130bf6af521f13247a739a95eab4bdaa24b2ac10` |
| `rt_b-a2.3a` | 32768 | `95c3b64f50e6f673b2bf9b40642c152da5009d25` |
| `rt_b-a3.3e` | 32768 | `9529ecdedd30e2a0400fb1083117992cc18b5158` |
| `rt_b-b0.3j` | 32768 | `5b390770e56ba2d35e108534d7eda8dca996fdf7` |
| `rt_b-b1.3k` | 32768 | `700905a3e9661e0874939f54da2909e1396ce596` |
| `rt_b-b2.3h` | 32768 | `14222eaa3e67e5a7f80eafcf22bac4eb2d485a9a` |
| `rt_b-b3.3f` | 32768 | `e2683d0e7415f3abd147e518bf6c87e44744cd4f` |
| `rt_r-00.1h` | 65536 | `1e3bc498861946278a0b1fe24259f5d224e265d7` |
| `rt_r-01.1j` | 32768 | `6741eb7f2d9d985b5a89eefc73ea44c3e38de6f7` |
| `rt_r-10.1k` | 65536 | `d2873d05aa3b257e7699c188880ac3daad672fa5` |
| `rt_r-11.1l` | 32768 | `5239a97222212ac9c019177771cb2b5096b7bc17` |
| `rt_r-20.3h` | 65536 | `01cf0a60f47fa5e2ed430a3f075e69e6cb762a48` |
| `rt_r-21.3j` | 32768 | `7e55a9a11fcd989db39bce6be48821b747c7d97f` |
| `rt_r-30.3k` | 65536 | `60a394ab53afdcbbf9e88083b8dbe8c897170d77` |
| `rt_r-31.3l` | 32768 | `b5467d1f22f6e5f90c5d8a8ac2d55974f287d589` |
| `rt_r-h0-b.1b` | 65536 | `0b9d5474bc5963224923126cf84d74a39b8270cc` |
| `rt_r-h1-b.1c` | 65536 | `008d1dc289df2ae2ba8f93d319c2b2c108cb9b89` |
| `rt_r-l0-b.3b` | 65536 | `3001c1b87cd1d441ba1226fb5b9dd6268458c0e8` |
| `rt_r-l1-b.3c` | 65536 | `0144c846fd0bdb3e4d790f6cb7bb64829e931b76` |

- **Python 3.8 or later** (macOS, Linux or Windows; nothing else to install).

## How to use it

```
python3 rtype_plus.py path/to/rtype.zip
```

(on Windows: `py rtype_plus.py path\to\rtype.zip`). It writes `rtype-plus/rtype.zip`; your files are
only read. Put that zip where MAME looks for ROMs in place of the original (keep the original
elsewhere) and run `rtype`.

With `--set rtypeu` it writes `rtype-plus/rtypeu.zip` instead: the same game as MAME's
R-Type (US) clone, which sits beside an untouched `rtype.zip` (front-ends list it as
"R-Type (US)"). `-o FOLDER` picks the output folder. Every file written is checked against the
SHA1 it must have, so a wrong or damaged input stops with the files it could not find.

Tested with MAME 0.289 and MAME 0.258.

## What is in the patch

None of the original game. The program gets 7836 bytes of the hack's own (its code and data in
the program's free space, the jumps where it hooks in and the small stubs they lead to, and the
boot test's checksum word). Any 3 bytes or more in a row that your program already has anywhere,
3420 bytes in all (the instructions each hook moves aside into its stub, and short sequences the
new code happens to share with the original), are copied from your own program at patch time, so
the patch holds no 3 bytes in a row of the original's. The new graphics (player 2's crimson HUD
glyphs, its mirrored beam gauge, the Armour cells, the timer's colon, the 1P / 2P tags) and player
2's two palettes are made from your own ROMs by the script's code, as recoloured or rearranged
copies of the game's; the title's PLUS is drawn by the script's code too (its own art, in the
pens of the logo's palette). Every file written is checked against the SHA1 it must have.

## Legal

This is an unofficial, free fan project, not affiliated with or endorsed by Irem or any rights
holder. R-Type and its program, graphics and sound are Irem's, and R-Type is their trademark,
named here only to say which game the patch is for. The patch is not the game and cannot run
without it: it holds none of the game's program, graphics or sound (see above), and you need your
own lawfully obtained copy of the original ROMs. None are included here, none are linked to, and
none are sent on request: please do not ask. The patcher and the patch's own code are under the
MIT licence (LICENSE), which grants nothing for Irem's work. If you hold rights in R-Type and
object to this patch, write to dev@rtypeneo.com and it will be taken down.

## Contact

dev@rtypeneo.com, or an issue on this repository. More about how the patch was made, with videos
and screenshots: https://rtypeplus.com/
