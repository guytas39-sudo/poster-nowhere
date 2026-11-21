#!/usr/bin/env python3
"""VELMARA — travel poster for a place that isn't there.

Draws a 1024x1024 travel poster for Velmara, an island where the tide
comes in twice a day and the lighthouse keeps the hours: one tall
lighthouse on a rocky point, two moons in a dusk sky, a lantern boat
crossing the light-path. Pure stdlib + PIL, no network, deterministic.
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

CREAM = (248, 238, 214)
INK = (24, 30, 54)
APRICOT = (242, 166, 90)
ROSE = (214, 120, 110)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def sky_gradient(draw):
    """Dusk sky: deep indigo at the top, apricot glow at the horizon."""
    stops = [
        (0.00, (22, 28, 58)),
        (0.35, (52, 52, 96)),
        (0.55, (104, 78, 116)),
        (0.68, (186, 112, 108)),
        (0.78, (242, 166, 90)),
        (1.00, (246, 178, 104)),
    ]
    horizon = 640
    for y in range(horizon + 1):
        t = y / horizon
        for i in range(len(stops) - 1):
            t0, c0 = stops[i]
            t1, c1 = stops[i + 1]
            if t0 <= t <= t1:
                f = 0 if t1 == t0 else (t - t0) / (t1 - t0)
                draw.line([(0, y), (W, y)], fill=lerp(c0, c1, f))
                break


def sea_gradient(draw):
    """Sea: deep teal darkening toward the bottom."""
    top = (44, 74, 96)
    bottom = (14, 30, 48)
    for y in range(640, H):
        t = (y - 640) / (H - 640)
        draw.line([(0, y), (W, y)], fill=lerp(top, bottom, t))


def stars(draw, rng):
    for _ in range(110):
        x = rng.randint(30, W - 30)
        y = rng.randint(30, 560)
        r = rng.choice([1, 1, 1, 2])
        a = rng.randint(90, 210)
        draw.ellipse([x - r, y - r, x + r, y + r],
                     fill=(255, 244, 214, a))


def moon(draw, cx, cy, r, colour, glow):
    """A full moon with a soft halo."""
    for k in range(4, 0, -1):
        draw.ellipse([cx - r - k * 9, cy - r - k * 9,
                      cx + r + k * 9, cy + r + k * 9],
                     fill=glow + (26,))
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=colour)
    # faint craters
    for dx, dy, cr in [(-r // 3, -r // 5, r // 6), (r // 4, r // 3, r // 8),
                       (0, -r // 2, r // 10)]:
        draw.ellipse([cx + dx - cr, cy + dy - cr, cx + dx + cr, cy + dy + cr],
                     fill=(colour[0] - 18, colour[1] - 18, colour[2] - 26))


def crescent(img, cx, cy, r, colour):
    """A small rose crescent moon low over the headland.

    Built as a mask (disc minus an offset disc) so the bite shows the
    real sky through it — a true crescent, not a disc with a cover.
    """
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    md.ellipse([cx - r + 16, cy - r - 8, cx + r + 16, cy + r - 8], fill=0)
    solid = Image.new("RGB", (W, H), colour)
    img.paste(solid, (0, 0), mask)


def gull(draw, x, y, s):
    draw.arc([x - s, y - s // 2, x, y + s // 2], 200, 340, fill=INK, width=2)
    draw.arc([x, y - s // 2, x + s, y + s // 2], 200, 340, fill=INK, width=2)


def lighthouse(img):
    """The landmark: tall banded lighthouse on a rocky point, lamp lit."""
    draw = ImageDraw.Draw(img, "RGBA")
    # beam sweeping right across the dusk: sliced quads whose alpha fades
    # along the beam, so it dissolves instead of ending in a hard edge
    x0, y_top0, y_bot0 = 196, 352, 392
    x1, y_top1, y_bot1 = 720, 478, 556
    steps = 10
    for i in range(steps):
        f0 = i / steps
        f1 = (i + 1) / steps
        ax = x0 + (x1 - x0) * f0
        bx = x0 + (x1 - x0) * f1
        quad = [(ax, y_top0 + (y_top1 - y_top0) * f0),
                (bx, y_top0 + (y_top1 - y_top0) * f1),
                (bx, y_bot0 + (y_bot1 - y_bot0) * f1),
                (ax, y_bot0 + (y_bot1 - y_bot0) * f0)]
        alpha = int(52 * (1 - f0))
        draw.polygon(quad, fill=(255, 214, 130, alpha))
    # rocky point
    draw.polygon([(60, 700), (150, 600), (210, 590), (300, 660),
                  (320, 700)], fill=(30, 38, 58))
    draw.polygon([(120, 700), (170, 640), (230, 640), (280, 700)],
                 fill=(44, 54, 78))
    # tower, tapered, cream with two terracotta bands
    draw.polygon([(150, 660), (164, 372), (216, 372), (230, 660)],
                 fill=(244, 232, 204))
    draw.polygon([(157, 560), (162, 512), (218, 512), (223, 560)],
                 fill=(178, 84, 66))
    draw.polygon([(160, 452), (164, 412), (216, 412), (220, 452)],
                 fill=(178, 84, 66))
    # gallery and lamp room
    draw.rectangle([156, 356, 224, 372], fill=(30, 38, 58))
    draw.rectangle([166, 322, 214, 356], fill=(30, 38, 58))
    draw.rectangle([172, 330, 208, 350], fill=(255, 214, 130))
    for k in range(3, 0, -1):
        draw.ellipse([190 - 14 - k * 10, 340 - 14 - k * 10,
                      190 + 14 + k * 10, 340 + 14 + k * 10],
                     fill=(255, 214, 130, 30))
    draw.polygon([(160, 322), (190, 300), (220, 322)], fill=(30, 38, 58))
    # tower shading on the right edge
    draw.polygon([(206, 372), (216, 372), (230, 660), (214, 660)],
                 fill=(214, 198, 168))


def headland(draw):
    """Dark headland silhouette on the right, under the low moon."""
    draw.polygon([(880, 640), (930, 560), (980, 585), (1024, 545),
                  (1024, 640)], fill=(26, 34, 56))
    draw.polygon([(940, 640), (980, 600), (1024, 615), (1024, 640)],
                 fill=(38, 48, 74))


def light_path(draw, rng):
    """Shimmering dashes of moonlight and lamplight on the water."""
    for _ in range(46):
        x = rng.randint(240, 860)
        y = rng.randint(660, 960)
        w = rng.randint(24, 90)
        a = rng.randint(28, 90)
        draw.line([(x, y), (x + w, y)], fill=(255, 200, 120, a), width=2)
    for _ in range(30):
        x = rng.randint(60, 980)
        y = rng.randint(680, 980)
        w = rng.randint(40, 140)
        draw.line([(x, y), (x + w, y)], fill=(120, 160, 190, 26), width=2)


def boat(draw):
    """A small rowing boat with a lantern, crossing the light-path."""
    bx, by = 560, 800
    draw.polygon([(bx - 70, by), (bx + 70, by), (bx + 48, by + 26),
                  (bx - 48, by + 26)], fill=(28, 36, 58))
    draw.line([(bx - 70, by), (bx + 70, by)], fill=(244, 232, 204), width=3)
    # seated figure, rowing
    draw.ellipse([bx - 8, by - 34, bx + 8, by - 18], fill=(20, 26, 46))
    draw.polygon([(bx - 10, by - 18), (bx + 10, by - 18), (bx + 6, by),
                  (bx - 6, by)], fill=(20, 26, 46))
    draw.line([(bx + 4, by - 14), (bx + 34, by + 12)], fill=(20, 26, 46),
              width=3)
    draw.line([(bx - 4, by - 14), (bx - 34, by + 12)], fill=(20, 26, 46),
              width=3)
    # lantern on a short mast
    draw.line([(bx + 52, by), (bx + 52, by - 44)], fill=(20, 26, 46),
              width=3)
    for k in range(3, 0, -1):
        draw.ellipse([bx + 52 - 6 - k * 5, by - 52 - 6 - k * 5,
                      bx + 52 + 6 + k * 5, by - 52 + 6 + k * 5],
                     fill=(255, 200, 110, 34))
    draw.ellipse([bx + 46, by - 58, bx + 58, by - 46],
                 fill=(255, 200, 110))
    # reflection
    draw.line([(bx - 40, by + 34), (bx + 40, by + 34)],
              fill=(255, 200, 110, 70), width=2)
    draw.line([(bx - 24, by + 48), (bx + 24, by + 48)],
              fill=(255, 200, 110, 44), width=2)


def letter_spaced(draw, cx, y, text, font, fill, spacing):
    """Draw text centred, with extra tracking between letters."""
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += w + spacing


def poster():
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img, "RGBA")
    rng = random.Random(7)

    sky_gradient(draw)
    stars(draw, rng)
    moon(draw, 815, 290, 58, (250, 226, 170), (250, 226, 170))
    crescent(img, 872, 520, 26, ROSE)
    for gx, gy, gs in [(330, 250, 16), (420, 300, 12), (700, 210, 14),
                       (620, 260, 10), (520, 200, 11)]:
        gull(draw, gx, gy, gs)
    sea_gradient(draw)
    light_path(draw, rng)
    headland(draw)
    boat(draw)
    lighthouse(img)

    # --- type: the place name, big and calm, with one short line ---
    draw = ImageDraw.Draw(img, "RGBA")
    name_font = ImageFont.truetype(SERIF_BOLD, 118)
    letter_spaced(draw, W // 2, 52, "VELMARA", name_font, CREAM, 26)
    tag_font = ImageFont.truetype(SANS, 27)
    tagline = "WHERE THE TIDE COMES IN TWICE"
    letter_spaced(draw, W // 2, 196, tagline,
                  tag_font, (250, 226, 170), 9)
    # small diamonds just outside the tagline's ends (measured, not guessed)
    tag_w = (sum(draw.textlength(ch, font=tag_font) for ch in tagline)
             + 9 * (len(tagline) - 1))
    for dx in (-1, 1):
        cx = W // 2 + dx * (tag_w / 2 + 30)
        cy = 210
        draw.polygon([(cx, cy - 7), (cx + 7, cy), (cx, cy + 7),
                      (cx - 7, cy)], fill=(250, 226, 170))

    # double frame
    draw.rectangle([22, 22, W - 23, H - 23], outline=CREAM, width=3)
    draw.rectangle([34, 34, W - 35, H - 35], outline=(248, 238, 214, 120),
                   width=1)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    img = poster()
    path = os.path.join(out_dir, "entry.png")
    img.save(path, format="PNG")
    print("wrote", path)


if __name__ == "__main__":
    main()
