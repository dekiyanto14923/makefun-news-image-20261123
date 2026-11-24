#!/usr/bin/env python3
"""Render the front page of THE WORLD for Monday 23 November 2026.

Draws a 1024x1024 newspaper front page with Pillow: a masthead, a hero
story with a small markets chart, seven story tiles, an ALSO strip and a
sources line. Writes entry.png next to this file.

Deterministic by design: no clock, no randomness, no network, fixed fonts.
Run twice and the two files are byte-identical.
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (253, 252, 247)
INK = (17, 17, 17)
RED = (163, 18, 18)
GREY = (105, 105, 105)
FAINT = (214, 212, 203)

FONT_DIR = "/usr/share/fonts/truetype/liberation/"
SERIF_B = FONT_DIR + "LiberationSerif-Bold.ttf"
SERIF = FONT_DIR + "LiberationSerif-Regular.ttf"
SERIF_I = FONT_DIR + "LiberationSerif-Italic.ttf"
SANS_B = FONT_DIR + "LiberationSans-Bold.ttf"
SANS = FONT_DIR + "LiberationSans-Regular.ttf"


def load(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, text, font):
    return draw.textlength(text, font=font)


def wrap(draw, text, font, width):
    """Greedy word wrap; returns a list of lines that fit `width` pixels."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if text_w(draw, trial, font) <= width:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def fit_lines(draw, text, font_path, start_size, width, max_lines, min_size=14):
    """Largest size (from start_size down) whose wrap fits in max_lines."""
    size = start_size
    while size > min_size:
        fnt = load(font_path, size)
        lines = wrap(draw, text, fnt, width)
        if len(lines) <= max_lines and all(
            text_w(draw, line, fnt) <= width for line in lines
        ):
            return fnt, lines
        size -= 1
    fnt = load(font_path, min_size)
    return fnt, wrap(draw, text, fnt, width)


def draw_centered(draw, y, text, font, fill=INK):
    x = (W - text_w(draw, text, font)) / 2
    draw.text((x, y), text, font=font, fill=fill)
    return y + font.size


def draw_rule(draw, y, weight=1, x0=36, x1=988, fill=INK):
    draw.rectangle([x0, y, x1, y + weight - 1], fill=fill)


# ---------------------------------------------------------------- stories

HERO_KICKER = "MARKETS  ·  TECHNOLOGY"
HERO_HEAD = "HUANG IS BACK"
HERO_DECK = (
    "Eleven days after resigning in scandal, Jensen Huang is Nvidia's chief "
    "again \u2014 and Wall Street roars. Shares jump 31%, the Nasdaq gains "
    "6.5% and the S&P 500 4.7%. Trump says: \u2018I made the deal.\u2019"
)

# (kicker, headline, body) — row 1 has three tiles, row 2 has four.
ROW1 = [
    (
        "UKRAINE",
        "WAR REACHES LIBYA",
        "Ukrainian drones strike a Russian warship at a Libyan port, Kyiv "
        "confirms \u2014 the first blow of its kind beyond the Black Sea.",
    ),
    (
        "TRADE",
        "US BLACKLISTS MEGASPEED",
        "Washington puts Nvidia's Asia-Pacific partner on its trade "
        "blacklist, accusing it of funnelling AI chips to China.",
    ),
    (
        "POLITICS",
        "HOUSE WIN BIGGEST SINCE 1992",
        "A North Carolina flip hands Democrats their largest House majority "
        "since the early 1990s.",
    ),
]
ROW2 = [
    (
        "SPAIN",
        "PUIGDEMONT FREE TO COME HOME",
        "Spain's top court shelves the case against the exiled Catalan "
        "leader, clearing his return after nearly a decade.",
    ),
    (
        "ASIA",
        "INDIA PLEDGES $1.6BN TO NEPAL",
        "New Delhi offers a $1.62bn economic package as Nepal's PM visits, "
        "in a reset of ties between the neighbours.",
    ),
    (
        "AFRICA",
        "BOAT DISASTER IN BAYELSA",
        "At least 29 people die as an overcrowded boat capsizes in "
        "Nigeria's Bayelsa state; rescuers hunt for survivors.",
    ),
    (
        "EUROPE",
        "STRIKE GROUNDS 429 FLIGHTS",
        "A cost-of-living strike cancels 429 flights at Brussels Airport, "
        "stranding 59,000 passengers.",
    ),
]

ALSO = (
    "CrowdStrike buys Zscaler in a $44bn deal  \u2022  Trump halts Iowa "
    "explosives blast  \u2022  US to train Syrian soldiers  \u2022  UK "
    "sanctions Myanmar generals  \u2022  Alcaraz wins the ATP Finals  "
    "\u2022  UK to host the 2035 Women's World Cup"
)

SOURCES = (
    "Sources: Reuters \u00b7 AP \u00b7 BBC \u00b7 AFP \u00b7 Al Jazeera  "
    "\u2014  All stories from Monday 23 November 2026"
)


# ---------------------------------------------------------------- drawing

def draw_tile(draw, x, y, width, height, kicker, headline, body):
    f_kick = load(SANS_B, 15)
    draw.text((x, y), kicker, font=f_kick, fill=RED)
    y += 22
    f_head, head_lines = fit_lines(draw, headline, SERIF_B, 26, width, 2)
    for line in head_lines:
        draw.text((x, y), line, font=f_head, fill=INK)
        y += 30
    y += 4
    f_body = load(SERIF, 16)
    body_lines = wrap(draw, body, f_body, width)
    clipped = False
    for line in body_lines[:4]:
        draw.text((x, y), line, font=f_body, fill=INK)
        y += 21
    if len(body_lines) > 4:
        clipped = True
    return clipped


def draw_chart(draw, x0, y0, x1, y1):
    """Mini bar chart of Monday's market moves, inside a bordered panel."""
    draw.rectangle([x0, y0, x1, y1], outline=INK, width=2)
    f_title = load(SANS_B, 16)
    draw_centered(draw, y0 + 10, "WALL STREET ROARS", f_title)
    f_big = load(SERIF_B, 38)
    big = "NVDA +31%"
    bx = (x0 + x1 - text_w(draw, big, f_big)) / 2
    draw.text((bx, y0 + 38), big, font=f_big, fill=RED)
    # bars: (label, value, scale max 7)
    bars = [("NASDAQ", 6.5), ("S&P 500", 4.7), ("DOW", 3.0)]
    base = y1 - 42
    top = y0 + 108
    span = base - top
    bw = 52
    gap = 26
    total = len(bars) * bw + (len(bars) - 1) * gap
    bx = x0 + (x1 - x0 - total) / 2
    f_val = load(SANS_B, 15)
    f_lab = load(SANS, 13)
    for label, value in bars:
        h = max(6, int(span * value / 7.0))
        draw.rectangle([bx, base - h, bx + bw, base], fill=INK)
        val = "+%.1f%%" % value
        vx = bx + (bw - text_w(draw, val, f_val)) / 2
        draw.text((vx, base - h - 20), val, font=f_val, fill=INK)
        lx = bx + (bw - text_w(draw, label, f_lab)) / 2
        draw.text((lx, base + 6), label, font=f_lab, fill=GREY)
        bx += bw + gap
    draw_rule(draw, base, 1, x0 + 16, x1 - 16)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    clipped = []

    # top strip
    f_small = load(SANS, 15)
    draw.text((36, 18), "EST. 2015  \u00b7  VOL. XII", font=f_small, fill=GREY)
    right = "No. 327  \u2014  $2.50"
    draw.text((988 - text_w(draw, right, f_small), 18), right,
              font=f_small, fill=GREY)
    draw_rule(draw, 42)

    # masthead
    f_mast = load(SERIF_B, 100)
    draw_centered(draw, 52, "THE WORLD", f_mast)
    f_date = load(SANS_B, 21)
    date = "MONDAY, 23 NOVEMBER 2026"
    dw = text_w(draw, date, f_date)
    cx = (W - dw) / 2
    draw.text((cx, 162), date, font=f_date, fill=INK)
    draw.rectangle([36, 171, cx - 18, 172], fill=INK)
    draw.rectangle([cx + dw + 18, 171, 988, 172], fill=INK)
    draw_rule(draw, 196, 3)
    draw_rule(draw, 202, 1)

    # hero
    f_kick = load(SANS_B, 19)
    draw.text((36, 216), HERO_KICKER, font=f_kick, fill=RED)
    f_head, head_lines = fit_lines(draw, HERO_HEAD, SERIF_B, 88, 620, 1)
    hy = 244
    for line in head_lines:
        draw.text((36, hy), line, font=f_head, fill=INK)
        hy += f_head.size + 6
    f_deck = load(SERIF_I, 22)
    deck_lines = wrap(draw, HERO_DECK, f_deck, 620)
    dy = hy + 12
    for line in deck_lines:
        draw.text((36, dy), line, font=f_deck, fill=INK)
        dy += 31

    # chart panel, right of the hero
    draw_chart(draw, 688, 216, 988, 462)

    draw_rule(draw, 478)

    # story grid
    row1_y, row_h = 494, 168
    row2_y = row1_y + row_h + 16
    widths1 = [306, 307, 307]
    xs1 = [36, 358, 681]
    for i, (kick, head, body) in enumerate(ROW1):
        if draw_tile(draw, xs1[i], row1_y, widths1[i], row_h,
                     kick, head, body):
            clipped.append(head)
        if i:
            x = xs1[i] - 8
            draw.rectangle([x, row1_y + 4, x, row1_y + row_h - 4],
                           fill=FAINT)
    widths2 = [227, 228, 227, 228]
    xs2 = [36, 277, 519, 760]
    for i, (kick, head, body) in enumerate(ROW2):
        if draw_tile(draw, xs2[i], row2_y, widths2[i], row_h,
                     kick, head, body):
            clipped.append(head)
        if i:
            x = xs2[i] - 7
            draw.rectangle([x, row2_y + 4, x, row2_y + row_h - 4],
                           fill=FAINT)

    draw_rule(draw, row2_y + row_h + 16)

    # ALSO strip
    ay = row2_y + row_h + 32
    f_also = load(SANS_B, 16)
    draw.text((36, ay), "ALSO", font=f_also, fill=RED)
    f_item = load(SERIF, 17)
    item_lines = wrap(draw, ALSO, f_item, 952 - 62)
    iy = ay - 1
    for line in item_lines:
        draw.text((104, iy), line, font=f_item, fill=INK)
        iy += 23

    # footer
    f_foot = load(SANS, 14)
    draw_centered(draw, 968, SOURCES, f_foot, fill=GREY)
    # frame the page with a thin rule near the bottom edge
    draw_rule(draw, 1006)

    img.save("entry.png")
    print("wrote entry.png")
    if clipped:
        print("WARNING: clipped body text in:", ", ".join(clipped))


if __name__ == "__main__":
    main()
