#!/usr/bin/env python3
"""Friday 20 November 2026 - one day of world news, by the numbers.

A single-page broadsheet front page: 48 stories from Friday 20 November
2026, drawn from scratch with PIL. Numbers XL variant: the figures lead -
a strip of six giant numbers under the masthead, and a big figure chip on
every pictured panel. Canvas 1600x1600, saved as entry.png at 1024x1024.
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

W, H = 1600, 1600
M = 48
CW = W - 2 * M

DJ = "/usr/share/fonts/truetype/dejavu/"
LB = "/usr/share/fonts/truetype/liberation/"

INK = (26, 24, 20)
PAPER = (250, 246, 238)
RED = (168, 32, 40)
NAVY = (24, 30, 52)
GREY = (96, 92, 84)
RULE = (178, 170, 154)
DARK = (52, 48, 42)


def _load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        pass
    plain = path.rsplit("/", 1)[-1]
    if plain != path:
        try:
            return ImageFont.truetype(plain, size)
        except OSError:
            pass
    return ImageFont.load_default()


def sans(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return _load_font(DJ + name, size)


def serif(size, bold=False, italic=False):
    if bold:
        path = LB + "LiberationSerif-Bold.ttf"
    elif italic:
        path = LB + "LiberationSerif-Italic.ttf"
    else:
        path = DJ + "DejaVuSerif.ttf"
    return _load_font(path, size)


def wrap_text(d, text, font, width):
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=font) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def block(d, x, y, text, font, w, lh, ink, max_lines=None):
    lines = wrap_text(d, text, font, w)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and d.textlength(lines[-1] + "…", font=font) > w:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1].rstrip() + "…"
    for ln in lines:
        d.text((x, y), ln, font=font, fill=ink)
        y += lh
    return y


def one_line(d, text, font, width):
    if d.textlength(text, font=font) <= width:
        return text
    while text and d.textlength(text + "…", font=font) > width:
        text = text[:-1]
    return text.rstrip() + "…"


def paper_sheet():
    im = Image.new("RGB", (W, H), PAPER)
    px = im.load()
    rng = random.Random(20261120)
    for yy in range(H):
        for xx in range(W):
            if rng.random() < 0.22:
                n = rng.randint(-6, 6)
                r, g, b = px[xx, yy]
                px[xx, yy] = (max(0, min(255, r + n)),
                              max(0, min(255, g + n)),
                              max(0, min(255, b + n)))
    return im


def sky_band(d, x, y, w, h, top, bottom):
    for i in range(h):
        t = i / max(1, h - 1)
        c = tuple(int(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
        d.line([(x, y + i), (x + w - 1, y + i)], fill=c)


def skyline(d, x, y, w, h, base, lit, seed):
    rng = random.Random(seed)
    bx = x
    while bx < x + w:
        bw = rng.randint(18, 46)
        bh = rng.randint(int(h * 0.35), h)
        d.rectangle([bx, y + h - bh, min(bx + bw, x + w), y + h], fill=base)
        for wy in range(y + h - bh + 6, y + h - 4, 12):
            for wx in range(bx + 4, min(bx + bw, x + w) - 4, 10):
                if rng.random() < 0.45:
                    d.rectangle([wx, wy, wx + 4, wy + 6], fill=lit)
        bx += bw + 2


def flagpole(d, x, y, h, stripes):
    d.line([(x, y), (x, y + h)], fill=(70, 66, 60), width=3)
    fw, fh = 34, 22
    n = len(stripes)
    for i, c in enumerate(stripes):
        d.rectangle([x + 2, y + i * (fh // n),
                     x + 2 + fw, y + (i + 1) * (fh // n)], fill=c)


def scene(d, x, y, w, h, kind, seed=7):
    rng = random.Random(seed)
    if kind == "storm":
        sky_band(d, x, y, w, h, (28, 52, 66), (74, 104, 122))
        for _ in range(70):
            rx = rng.randint(x, x + w)
            ry = rng.randint(y, y + h)
            d.line([(rx, ry), (rx - 4, ry + 12)], fill=(200, 215, 225), width=1)
        cx, cy = x + w // 2, y + h // 2 - 8
        for r in (36, 25, 15):
            d.arc([cx - r, cy - r, cx + r, cy + r], 20, 300,
                  fill=(235, 240, 244), width=3)
        for i in range(4):
            yy = y + h - 6 - i * 6
            d.arc([x - 20, yy - 10, x + w + 20, yy + 26], 200, 340,
                  fill=(220, 230, 236), width=2)
    elif kind == "skyline":
        sky_band(d, x, y, w, h, (38, 48, 78), (96, 78, 96))
        skyline(d, x, y + h // 2, w, h // 2, (18, 20, 34),
                (255, 214, 120), seed)
        d.arc([x + 10, y - 10, x + w - 20, y + h], 300, 360,
              fill=(255, 190, 60), width=3)
        bx, by = x + w - 60, y + 26
        for r, c in ((16, (255, 120, 40)), (10, (255, 190, 60)),
                     (5, (255, 240, 160))):
            d.ellipse([bx - r, by - r, bx + r, by + r], fill=c)
    elif kind == "flags":
        sky_band(d, x, y, w, h, (120, 150, 190), (200, 205, 215))
        skyline(d, x, y + h - 46, w, 46, (52, 56, 72), (255, 220, 140), seed)
        flagpole(d, x + 26, y + 18, 62,
                 [(200, 30, 40), (255, 255, 255), (200, 30, 40),
                  (255, 255, 255), (200, 30, 40)])
        d.rectangle([x + 28, y + 18, x + 38, y + 28], fill=(30, 60, 140))
        flagpole(d, x + w // 2 - 10, y + 18, 62,
                 [(222, 30, 30)])
        d.ellipse([x + w // 2 + 2, y + 22, x + w // 2 + 10, y + 30],
                  fill=(255, 220, 60))
        flagpole(d, x + w - 62, y + 18, 62,
                 [(255, 255, 255), (40, 80, 200), (220, 30, 30)])
    elif kind == "bridge":
        sky_band(d, x, y, w, h, (150, 180, 205), (225, 225, 220))
        d.arc([x + 10, y + 18, x + w - 10, y + h + 30], 180, 360,
              fill=(60, 60, 70), width=5)
        d.rectangle([x, y + h - 26, x + w, y + h - 18], fill=(60, 60, 70))
        for px in (x + w // 4, x + w // 2, x + 3 * w // 4):
            d.rectangle([px - 3, y + h - 26, px + 3, y + h], fill=(60, 60, 70))
        d.rectangle([x, y + h - 12, x + w, y + h], fill=(90, 120, 150))
        d.line([(x + 8, y + h - 20), (x + w - 8, y + h - 20)],
               fill=(255, 80, 60), width=2)
    elif kind == "summit":
        sky_band(d, x, y, w, h, (250, 190, 110), (250, 220, 170))
        d.ellipse([x + w - 70, y + 12, x + w - 22, y + 60],
                  fill=(255, 200, 60))
        skyline(d, x, y + h - 52, w, 52, (70, 50, 60), (255, 220, 140), seed)
    elif kind == "climate":
        sky_band(d, x, y, w, h, (40, 130, 140), (160, 210, 200))
        d.ellipse([x + w - 64, y + 10, x + w - 20, y + 54],
                  fill=(255, 210, 80))
        d.line([(x + w // 3, y + h - 14), (x + w // 3, y + h // 2)],
               fill=(90, 70, 50), width=5)
        for a in (-50, -20, 10, 40):
            ex = x + w // 3 + int(34 * math.cos(math.radians(a - 90)))
            ey = y + h // 2 + int(20 * math.sin(math.radians(a - 90))) - 8
            d.line([(x + w // 3, y + h // 2), (ex, ey)],
                   fill=(40, 110, 70), width=3)
        d.rectangle([x, y + h - 14, x + w, y + h], fill=(210, 190, 140))
    elif kind in ("court", "seoul"):
        sky_band(d, x, y, w, h, (215, 220, 228), (240, 240, 235))
        d.polygon([(x + w // 2, y + 12), (x + 14, y + 44),
                   (x + w - 14, y + 44)], fill=(120, 110, 95))
        for i in range(4):
            cx = x + 22 + i * (w - 44) // 3
            d.rectangle([cx - 7, y + 46, cx + 7, y + h - 12],
                        fill=(150, 140, 125))
        d.rectangle([x + 10, y + h - 12, x + w - 10, y + h - 4],
                    fill=(120, 110, 95))
        if kind == "seoul":
            d.ellipse([x + w // 2 - 14, y + 52, x + w // 2 + 14, y + 80],
                      fill=(255, 255, 255), outline=(40, 80, 180), width=2)
            d.arc([x + w // 2 - 14, y + 52, x + w // 2 + 14, y + 80], 90, 270,
                  fill=(200, 40, 40), width=6)
    elif kind == "chart":
        d.rectangle([x, y, x + w, y + h], fill=(248, 246, 242))
        for gy in range(1, 4):
            yy = y + gy * h // 4
            d.line([(x + 6, yy), (x + w - 6, yy)], fill=(220, 216, 208), width=1)
        pts = [(x + 8, y + 18), (x + w // 3, y + 34),
               (x + 2 * w // 3, y + h - 34), (x + w - 10, y + h - 12)]
        d.line(pts, fill=(200, 40, 50), width=4)
        d.polygon([(x + w - 10, y + h - 12), (x + w - 26, y + h - 16),
                   (x + w - 20, y + h - 28)], fill=(200, 40, 50))
        for i, bh in enumerate((26, 40, 18, 34)):
            bx = x + 12 + i * (w - 24) // 4
            d.rectangle([bx, y + h - 10 - bh, bx + 16, y + h - 10],
                        fill=(70, 90, 130))
    elif kind == "neon":
        sky_band(d, x, y, w, h, (24, 16, 54), (70, 30, 90))
        for _ in range(30):
            sx = rng.randint(x, x + w)
            sy = rng.randint(y, y + h // 2)
            d.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 220))
        skyline(d, x, y + h // 2, w, h // 2, (12, 10, 26),
                (255, 120, 200), seed)
        d.rectangle([x + 8, y + h - 24, x + w - 8, y + h - 8],
                    outline=(80, 240, 255), width=2)
        d.text((x + 14, y + h - 22), "GTA VI", font=sans(13, bold=True),
               fill=(80, 240, 255))
    elif kind == "space":
        d.rectangle([x, y, x + w, y + h], fill=(8, 10, 26))
        for _ in range(46):
            sx = rng.randint(x, x + w)
            sy = rng.randint(y, y + h)
            d.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 255))
        px, py = x + w // 2, y + h // 2
        d.ellipse([px - 26, py - 26, px + 26, py + 26], fill=(210, 170, 110))
        d.ellipse([px - 44, py - 6, px + 44, py + 6], outline=(230, 210, 170),
                  width=2)
        d.rectangle([x + w - 40, y + 14, x + w - 26, y + 24], fill=(200, 200, 210))
        d.line([(x + w - 33, y + 14), (x + w - 33, y + 6)],
               fill=(200, 200, 210), width=2)
    elif kind == "drought":
        sky_band(d, x, y, w, h, (245, 220, 170), (240, 200, 150))
        d.ellipse([x + w // 2 - 22, y + 10, x + w // 2 + 22, y + 54],
                  fill=(255, 190, 60))
        d.rectangle([x, y + h - 26, x + w, y + h], fill=(205, 175, 130))
        for i in range(5):
            cx = x + 14 + i * (w - 28) // 4
            d.line([(cx, y + h - 26), (cx + rng.randint(-8, 8), y + h - 8)],
                   fill=(140, 105, 70), width=2)
        d.line([(x + w // 4, y + h - 26), (x + w // 4, y + h // 2)],
               fill=(110, 85, 60), width=4)
        d.line([(x + w // 4, y + h // 2), (x + w // 4 - 16, y + h // 2 - 14)],
               fill=(110, 85, 60), width=3)
        d.line([(x + w // 4, y + h // 2), (x + w // 4 + 16, y + h // 2 - 18)],
               fill=(110, 85, 60), width=3)
    elif kind == "atom":
        d.rectangle([x, y, x + w, y + h], fill=(16, 34, 64))
        cx, cy = x + w // 2, y + h // 2
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(255, 200, 80))
        for (rw, rh) in ((44, 14), (14, 44), (36, 36)):
            d.ellipse([cx - rw, cy - rh, cx + rw, cy + rh],
                      outline=(120, 180, 240), width=2)
        for (ox, oy) in ((-38, -10), (36, 12), (0, -38)):
            d.ellipse([cx + ox - 3, cy + oy - 3, cx + ox + 3, cy + oy + 3],
                      fill=(240, 240, 255))
    elif kind == "handshake":
        sky_band(d, x, y, w, h, (140, 170, 205), (215, 220, 225))
        flagpole(d, x + 20, y + 20, 60,
                 [(255, 220, 60), (30, 60, 160), (220, 30, 30)])
        flagpole(d, x + w - 56, y + 20, 60,
                 [(255, 255, 255), (30, 90, 200), (220, 30, 30)])
        cx, cy = x + w // 2, y + h // 2 + 8
        for r, c in ((20, (255, 200, 60)), (13, (255, 230, 130)),
                     (6, (255, 255, 255))):
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
    elif kind == "tanker":
        sky_band(d, x, y, w, h, (150, 180, 205), (210, 215, 220))
        d.rectangle([x, y + h - 34, x + w, y + h], fill=(70, 110, 150))
        d.rectangle([x + 14, y + h - 62, x + w - 14, y + h - 34],
                    fill=(40, 44, 54))
        for i, c in enumerate(((200, 60, 50), (40, 120, 80), (220, 160, 40))):
            bx = x + 24 + i * 30
            d.rectangle([bx, y + h - 84, bx + 26, y + h - 62], fill=c)
        d.rectangle([x + w - 52, y + h - 96, x + w - 30, y + h - 62],
                    fill=(230, 230, 235))
    elif kind == "cricket":
        d.rectangle([x, y, x + w, y + h], fill=(70, 140, 80))
        d.rectangle([x + w // 2 - 16, y + 8, x + w // 2 + 16, y + h - 8],
                    fill=(220, 200, 150))
        for i in range(3):
            sx = x + w // 2 - 8 + i * 8
            d.line([(sx, y + h - 26), (sx, y + h - 12)],
                   fill=(255, 240, 180), width=2)
        d.ellipse([x + w - 34, y + 16, x + w - 26, y + 24], fill=(200, 40, 40))
        d.line([(x + 16, y + 20), (x + w // 2 - 10, y + h - 30)],
               fill=(220, 200, 150), width=3)
    else:
        sky_band(d, x, y, w, h, (120, 140, 170), (200, 205, 210))


NUMBERS = [
    ("300,000", "people evacuated ahead of Cyclone Akvan"),
    ("$1.84bn", "GTA VI's first-day sales, Sensor Tower estimates"),
    ("-1,084", "points the Dow lost in Friday's slide"),
    ("16bn miles", "Voyager 1 from Earth - one light-day out"),
    ("7.91m", "peak viewers watching GTA VI at once"),
    ("9-6", "the ICJ vote finding Myanmar guilty"),
]

REGIONS = [
    ("EUROPE 11", 11, (31, 78, 121)),
    ("THE AMERICAS 7", 7, (46, 125, 50)),
    ("ASIA-PACIFIC 19", 19, (168, 32, 40)),
    ("MIDEAST 4", 4, (199, 123, 33)),
    ("AFRICA 2", 2, (106, 76, 147)),
    ("OCEANIA 1", 1, (14, 124, 123)),
    ("WORLD 4", 4, (51, 51, 51)),
]

TIMELINE = ("THE DAY IN UTC — OVERNIGHT Crimean Bridge hit a third time · "
            "06:00 APEC leaders meet in Shenzhen · 10:00 Trilateral "
            "declaration issued · 12:00 Akvan makes landfall in Odisha · "
            "14:00 Houthi missile hits Riyadh KAFD · LATE Wall Street "
            "slides; Dow -1,084")

HEROES = [
    (1, "1 · ODISHA · STORM", "Akvan comes ashore on the Odisha coast",
     "Cyclone Akvan crossed the coast near Gopalpur at noon, winds "
     "90-100 km/h gusting to 110. Three hundred thousand people are out "
     "of harm's way, 423 rescue teams deployed, red alerts in 11 districts.",
     "IMD · THE HINDU", "storm", "300,000"),
    (2, "2 · RIYADH · ATTACK", "Houthi missile hits Riyadh's KAFD financial district",
     "A Houthi missile damaged a wealth-fund tower in the financial "
     "district, one of Riyadh's tallest. No casualties are reported, as "
     "air defences answered the strike.",
     "ARAB NEWS · REUTERS", "skyline", "0"),
    (3, "3 · SHENZHEN · DIPLOMACY", "Trump, Xi and Putin issue a joint declaration",
     "No big peace deal from the trilateral's second day. Trump says the "
     "Iran war call waits until 2027, rates the summit '12 out of 10', "
     "and Putin may attend December's G20 in Miami.",
     "REUTERS · AP", "flags", "12/10"),
]

PICTURED = [
    (4, "4 · KERCH STRAIT · WAR", "Crimean Bridge hit a third time this week; rail halted",
     "A Ukrainian naval drone strike disrupted rail traffic on the bridge. "
     "Rail partly resumes; Putin vows retaliation, and Kyiv was hit by drones.",
     "CLAIM · KYIV", "bridge", "3rd"),
    (5, "5 · SHENZHEN · SUMMIT", "APEC leaders meet in Shenzhen",
     "Leaders gather in China for the APEC summit. Xi urges APEC economies "
     "to back open trade and new technology.",
     "AP", "summit", "21"),
    (6, "6 · ANTALYA · CLIMATE", "COP31's final day: fossil fuels cut from the text",
     "A revised draft strips out every fossil-fuel phase-out pledge. "
     "Delegates push back as the final plenary meets today.",
     "UNFCCC · AFP", "climate", "0"),
    (7, "7 · THE HAGUE · LAW", "The world answers the genocide verdict",
     "Britain expels Myanmar's defence attache and seeks an urgent Security "
     "Council meeting. The Gambia hails a 'historic' verdict.",
     "AP · BBC", "court", "9-6"),
    (8, "8 · NEW YORK · MARKETS", "Anthropic's debut can't stop the slide",
     "The Dow fell 1,084 points, the S&P 2.02% and the Nasdaq 2.25%, as the "
     "AI selloff bit a day after Anthropic's record debut.",
     "BLOOMBERG", "chart", "-1,084"),
    (9, "9 · VICE CITY · GAMES", "GTA VI passes The Odyssey's $1.84bn",
     "Launch-day sales top The Odyssey's $1.80bn global run, Sensor Tower "
     "estimates. Reviews land; Rockstar calls it the highest-rated game ever.",
     "SENSOR TOWER", "neon", "$1.84bn"),
    (10, "10 · SPACE · SCIENCE", "NASA confirms Voyager 1's light-day milestone",
     "The probe is now a full light-day from Earth - 16 billion miles out, "
     "the farthest any human-made object has ever travelled.",
     "NASA · JPL", "space", "16bn"),
    (11, "11 · SEOUL · LAW", "South Korea clears ex-PM Han",
     "The Supreme Court overturns former prime minister Han Duck-soo's "
     "conviction, in the case tied to the 2024 martial-law declaration.",
     "KOREA TIMES", "seoul", "2024"),
    (12, "12 · SUVA · CLIMATE", "Fiji declares a national disaster over drought",
     "Fiji declares a national disaster over drought and water shortages. "
     "El Nino leaves water short across the islands.",
     "AFP", "drought", "1"),
    (13, "13 · VIENNA · SECURITY", "North Korea expands uranium enrichment at Yongbyon",
     "The UN watchdog reports growth at the nuclear site, in its latest "
     "assessment of the Yongbyon complex.",
     "IAEA", "atom", "1"),
    (14, "14 · CARACAS · DIPLOMACY", "US and Venezuela restore military cooperation",
     "The two countries sign an agreement to work together again, restoring "
     "a military channel closed for years.",
     "REUTERS", "handshake", "2"),
    (15, "15 · HORMUZ · CONFLICT", "ADNOC vessel attacked in the Strait of Hormuz",
     "One crew member is missing after the strike on the ADNOC vessel in "
     "the strait.",
     "REUTERS", "tanker", "1"),
    (16, "16 · WELLINGTON · CRICKET", "Day two at the Basin: Nicholls' 113 anchors New Zealand",
     "New Zealand build on Henry Nicholls' unbeaten 113 as India hunt early "
     "wickets, in the first Test at the Basin Reserve.",
     "AP", "cricket", "113"),
]

BRIEFS = [
    (17, "BRUSSELS", "EU-UK summit opens"),
    (18, "NEW DELHI", "Modi meets William and Kate"),
    (19, "DHAKA", "Fire at the Yunus home; arson feared"),
    (20, "MUMBAI", "Sensex +1.21%, Nifty +1.14% on the day"),
    (21, "TOKYO", "Hayabusa2 gives up landing; mission rewritten"),
    (22, "BERLIN", "Coalition of the Willing meets in Berlin"),
    (23, "BERLIN", "Merz hosts Qatar's emir in Berlin"),
    (24, "NEW DELHI", "Pakistan minister leads delegation to Delhi for SCO"),
    (25, "MANILA", "Philippines-Chile trade deal signed"),
    (26, "MANILA", "Musk plans Philippines projects"),
    (27, "HONG KONG", "India beats Malaysia, Asian Hockey Trophy opens"),
    (28, "IPOH", "Harimau Shakti exercise opens in Ipoh"),
    (29, "NEW DELHI", "India's electronics exports jump 44%"),
    (30, "NEW DELHI", "ICMR completes 100 tech transfers"),
    (31, "NEW DELHI", "India unveils its first bird-flu vaccine"),
    (32, "GENEVA", "World Children's Day marked worldwide"),
    (33, "EUROPE", "Youth anti-war protests across Europe"),
    (34, "BRUSSELS", "EU delays its methane rules by 24 months"),
    (35, "COLOGNE", "Bayern Munich beat Koln 3-0"),
    (36, "U17 CUP", "Argentina 0-2 Australia at the U17 Cup"),
    (37, "WASHINGTON", "Jobless claims come in at 203,000"),
    (38, "STRASBOURG", "NATO's assembly opens its 72nd session"),
    (39, "HANOI", "Azerbaijan's Aliyev visits Vietnam"),
    (40, "MARKETS", "Crude futures fall over 3%"),
    (41, "KHARTOUM", "Sudan army: two-year El Obeid siege broken"),
    (42, "MOGADISHU", "Somalia gives UAE ambassador 72 hours to leave"),
    (43, "SAN SALVADOR", "Migrant boat capsizes off El Salvador; dozens missing"),
    (44, "PORT-AU-PRINCE", "Haiti approves Salvadoran troop deal vs gangs"),
    (45, "ARABIAN SEA", "Amur falcons cross the Arabian Sea"),
    (46, "NEW YORK", "Al-Saadi appears in a New York court over a UK plot"),
    (47, "KYIV", "Witkoff and Kushner brief Zelenskyy"),
    (48, "BEIJING", "Xi urges APEC to back open trade, new tech"),
]

LAND = [
    (1, 1, 5, 3), (4, 1, 14, 6), (15, 0, 18, 2), (11, 7, 15, 13),
    (22, 1, 27, 4), (22, 5, 29, 12), (28, 1, 45, 6), (30, 6, 33, 8),
    (36, 6, 39, 8), (40, 11, 46, 13),
]

PINS = {
    4: (0.52, 0.18), 5: (0.86, 0.38), 6: (0.50, 0.24), 7: (0.45, 0.13),
    8: (0.20, 0.28), 9: (0.23, 0.40), 10: (0.92, 0.10), 11: (0.90, 0.28),
    12: (0.96, 0.62), 13: (0.49, 0.17), 14: (0.26, 0.46), 15: (0.63, 0.36),
    16: (0.97, 0.74),
}

DATE_CHECK = ("Left out - they broke before Friday: the ICJ genocide ruling "
              "on Myanmar itself (Thursday 19 Nov) - Friday's news is the "
              "world's answer to it - Denmark's Greenland-US pact (19 Nov) - "
              "Anthropic's $81.34bn IPO (19 Nov); its first trading day was "
              "Thursday - Germany's electricity-tax cut (18 Nov) - the "
              "Crimean Bridge span collapse (17-18 Nov). Not yet: the "
              "trilateral's first meeting was 19 Nov; the joint declaration "
              "is Friday's.")


def story_panel(d, x, y, w, item, scene_h, head_size, dek_size,
                  dek_lines=3):
    num, kicker, head, dek, src, kind, big = item
    scene(d, x, y, w, scene_h, kind, seed=num * 13)
    f_big = sans(26 if len(big) < 6 else 20, bold=True)
    tw = d.textlength(big, font=f_big)
    d.rectangle([x + w - tw - 20, y + 8, x + w - 6, y + 42], fill=(255, 255, 255))
    d.rectangle([x + w - tw - 20, y + 8, x + w - 6, y + 42],
                outline=RED, width=2)
    d.text((x + w - tw - 13, y + 12), big, font=f_big, fill=RED)
    ty = y + scene_h + 10
    d.rectangle([x, ty + 2, x + 8, ty + 14], fill=RED)
    d.text((x + 14, ty), kicker, font=sans(13, bold=True), fill=RED)
    sw = d.textlength(src, font=sans(11, bold=True))
    d.text((x + w - sw, ty), src, font=sans(11, bold=True), fill=GREY)
    ty += 24
    head_lh = head_size + 5
    dek_lh = dek_size + 4
    ty = block(d, x, ty, head, serif(head_size, bold=True), w, head_lh,
               INK, max_lines=2)
    ty += 4
    block(d, x, ty, dek, sans(dek_size), w, dek_lh, DARK, max_lines=dek_lines)


def draw_map(d, x, y, w, h):
    cols, rows = 48, 16
    cw, ch = w / cols, h / rows
    for (x0, y0, x1, y1) in LAND:
        for gy in range(y0, y1 + 1):
            for gx in range(x0, x1 + 1):
                if (gx * 5 + gy * 11) % 7 == 0:
                    continue
                cx = x + gx * cw + cw / 2
                cy = y + gy * ch + ch / 2
                d.ellipse([cx - 2.5, cy - 2.5, cx + 2.5, cy + 2.5],
                          fill=(70, 76, 92))
    for num, (fx, fy) in PINS.items():
        px = x + fx * w
        py = y + fy * h
        d.ellipse([px - 10, py - 10, px + 10, py + 10], fill=RED,
                  outline=(255, 255, 255), width=2)
        t = str(num)
        tw = d.textlength(t, font=sans(10, bold=True))
        d.text((px - tw / 2, py - 7), t, font=sans(10, bold=True),
               fill=(255, 255, 255))


def build():
    im = paper_sheet()
    d = ImageDraw.Draw(im)

    # Top line.
    d.text((M, 28), "THE DAY IN WORLD NEWS - BY THE NUMBERS",
           font=sans(16, bold=True), fill=RED)
    right = "48 STORIES - ONE PAGE"
    d.text((M + CW - d.textlength(right, font=sans(16, bold=True)), 28),
           right, font=sans(16, bold=True), fill=INK)
    d.line([(M, 54), (M + CW, 54)], fill=INK, width=2)

    # Masthead on a navy band.
    d.rectangle([M, 58, M + CW, 178], fill=NAVY)
    d.text((M + 10, 78), "Friday 20 November 2026",
           font=serif(88, bold=True), fill=(255, 255, 255))

    # Numbers strip: six giant figures.
    ny = 190
    cell = CW // 6
    for i, (num, cap) in enumerate(NUMBERS):
        cx = M + i * cell
        d.text((cx + 4, ny), num, font=serif(40, bold=True), fill=RED)
        block(d, cx + 4, ny + 52, cap, sans(12), cell - 12, 15, DARK,
              max_lines=2)
        if i:
            d.line([(cx, ny + 4), (cx, ny + 82)], fill=RULE, width=1)
    d.line([(M, ny + 88), (M + CW, ny + 88)], fill=RULE, width=1)

    # Region strip.
    ry = 286
    total = sum(c for _, c, _ in REGIONS)
    rx = M
    for label, count, color in REGIONS:
        seg = int(CW * count / total)
        d.rectangle([rx, ry, rx + seg - 2, ry + 26], fill=color)
        if seg >= 70:
            f = sans(13, bold=True)
            tw = d.textlength(label, font=f)
            d.text((rx + (seg - tw) / 2, ry + 5), label, font=f,
                   fill=(255, 255, 255))
        rx += seg

    # Timeline.
    block(d, M, 322, TIMELINE, sans(15), CW, 19, INK, max_lines=2)
    d.line([(M, 356), (M + CW, 356)], fill=INK, width=2)

    # Heroes.
    hy = 366
    hw = (CW - 24) // 3
    for i, item in enumerate(HEROES):
        story_panel(d, M + i * (hw + 12), hy, hw, item, 118, 28, 16)
    d.line([(M, hy + 292), (M + CW, hy + 292)], fill=INK, width=2)

    # Pictured rows: 5, then 4, then 4.
    rows = [PICTURED[0:5], PICTURED[5:9], PICTURED[9:13]]
    py = 668
    for row in rows:
        pw = (CW - 12 * (len(row) - 1)) // len(row)
        for i, item in enumerate(row):
            story_panel(d, M + i * (pw + 12), py, pw, item, 84, 20, 13,
                        dek_lines=2)
        py += 206

    # Bottom: map on the left, 32 briefs on the right.
    by = 1292
    d.text((M, by), "WHERE IT HAPPENED", font=sans(16, bold=True), fill=RED)
    d.text((M + 560, by), "ALSO ON FRIDAY 20 NOVEMBER - 32 MORE STORIES",
           font=sans(15, bold=True), fill=RED)
    draw_map(d, M, by + 26, 500, 124)
    cols = [BRIEFS[0:11], BRIEFS[11:22], BRIEFS[22:32]]
    for ci, col in enumerate(cols):
        bx = M + 560 + ci * 330
        yy = by + 26
        for num, place, text in col:
            line = "%d %s — %s" % (num, place, text)
            d.text((bx, yy), one_line(d, line, sans(11, bold=True), 318),
                   font=sans(11, bold=True), fill=INK)
            yy += 12

    # Date check box.
    dy = 1472
    d.rectangle([M, dy, M + CW, dy + 62], outline=RED, width=2)
    d.rectangle([M, dy, M + 150, dy + 62], fill=RED)
    d.text((M + 12, dy + 20), "DATE CHECK", font=sans(16, bold=True),
           fill=(255, 255, 255))
    block(d, M + 162, dy + 6, DATE_CHECK, sans(13), CW - 174, 17, INK,
          max_lines=3)

    # Footer.
    fy = 1548
    d.text((M, fy), "Every story here happened, or was first reported, on "
                    "Friday 20 November 2026, in some time zone. Disputed "
                    "claims are attributed, not stated as fact.",
           font=serif(13, italic=True), fill=GREY)
    d.text((M, fy + 20), "Sources: Reuters - AP - AFP - BBC - Bloomberg - "
                         "IMD - NASA - IAEA - The Hindu - Arab News - "
                         "Sensor Tower. Original drawings, drawn for this page.",
           font=serif(13, italic=True), fill=GREY)

    out = im.resize((1024, 1024), Image.LANCZOS)
    candidates = []
    env_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env_dir:
        candidates.append(env_dir)
    candidates.append(".")
    candidates.append(os.path.dirname(os.path.abspath(__file__)))
    last_err = None
    saved = False
    for cand in candidates:
        try:
            out.save(os.path.join(cand, "entry.png"))
            saved = True
            break
        except OSError as exc:
            last_err = exc
    if not saved:
        raise last_err


def main():
    build()


if __name__ == "__main__":
    main()
