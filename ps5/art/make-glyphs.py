#!/usr/bin/env python3
# Dusklight for the PlayStation 5 - the DualSense's symbols for the game's button prompts.
# SPDX-License-Identifier: MIT
"""Draws ps5/art/glyphs/*.png: replacement textures for the letters on the game's buttons.

The game draws a button as a coloured shape with a white letter over it, each letter a small
texture of its own. Dusklight replaces a texture by a file named after it (Dolphin's scheme:
tex1_<width>x<height>_<hash of its texels>_<format>.png), so each picture here carries the name
of the letter it stands in for, and nothing of the letter itself: a cross for A, a circle for B,
a square for X and a triangle for Y, as Dusklight's default mapping has them (A south, B east,
X west, Y north), and "R1" for Z. The names are the GameCube USA disc's.

Needs Python with Pillow 10.1 or later (its built-in font draws "R1").
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SCALE = 8  # the replacement is this many times the original's size
out = Path(__file__).resolve().parent / "glyphs"
out.mkdir(exist_ok=True)


def canvas(w, h):
    image = Image.new("L", (w * SCALE, h * SCALE), 0)
    return image, ImageDraw.Draw(image)


def save(mask, name):
    white = Image.new("RGBA", mask.size, (255, 255, 255, 0))
    white.putalpha(mask)
    # drawn large and reduced, for smooth edges
    white = white.resize((mask.width // 2, mask.height // 2), Image.LANCZOS)
    white.save(out / (name + ".png"))


def symbol(name, w, h, kind):
    mask, draw = canvas(w, h)
    cx, cy = mask.width / 2, mask.height / 2
    r = min(w, h) * SCALE * 0.40
    t = int(min(w, h) * SCALE * 0.13)
    if kind == "cross":
        draw.line([(cx - r, cy - r), (cx + r, cy + r)], fill=255, width=t)
        draw.line([(cx - r, cy + r), (cx + r, cy - r)], fill=255, width=t)
        for x, y in ((cx - r, cy - r), (cx + r, cy + r), (cx - r, cy + r), (cx + r, cy - r)):
            draw.ellipse([x - t / 2, y - t / 2, x + t / 2, y + t / 2], fill=255)
    elif kind == "circle":
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=255, width=t)
    elif kind == "square":
        draw.rounded_rectangle([cx - r, cy - r, cx + r, cy + r], radius=t / 2, outline=255, width=t)
    elif kind == "triangle":
        top, bottom, half = cy - r * 1.02, cy + r * 0.82, r * 1.08
        points = [(cx, top), (cx + half, bottom), (cx - half, bottom)]
        draw.line(points + [points[0]], fill=255, width=t, joint="curve")
        for x, y in points:
            draw.ellipse([x - t / 2, y - t / 2, x + t / 2, y + t / 2], fill=255)
    save(mask, name)


def text(name, w, h, label):
    mask, draw = canvas(w, h)
    size = 10
    while True:
        font = ImageFont.load_default(size=size + 4)
        box = draw.textbbox((0, 0), label, font=font, stroke_width=SCALE // 2)
        if box[2] - box[0] > mask.width * 0.96 or box[3] - box[1] > mask.height * 0.9:
            break
        size += 4
    font = ImageFont.load_default(size=size)
    box = draw.textbbox((0, 0), label, font=font, stroke_width=SCALE // 2)
    draw.text(((mask.width - (box[2] - box[0])) / 2 - box[0], (mask.height - (box[3] - box[1])) / 2 - box[1]), label,
              font=font, fill=255, stroke_width=SCALE // 2, stroke_fill=255)
    save(mask, name)


symbol("tex1_32x46_683dc853245a0f36_0", 32, 46, "cross")     # A
symbol("tex1_24x40_b191153a917b3b50_0", 24, 40, "circle")    # B
symbol("tex1_32x45_3b03f19ac102dd38_0", 32, 45, "square")    # X
symbol("tex1_32x40_a57e14b2809290fc_0", 32, 40, "triangle")  # Y
text("tex1_24x40_1868b6990a352fae_2", 24, 40, "R1")          # Z
print(sorted(p.name for p in out.glob("*.png")))
