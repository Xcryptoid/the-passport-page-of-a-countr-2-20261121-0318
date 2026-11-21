#!/usr/bin/env python3
"""Draw the passport spread of the Republic of Caldara (invented country).

One open passport spread, 1024x1024: data page (left) with portrait and
machine-readable zone, visa/stamp page (right) with two consistent voyages.
Run: python3 draw.py  ->  entry.png
"""
import hashlib
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = "/usr/share/fonts/truetype/dejavu"

W, H = 1024, 1024

# --- palette ---------------------------------------------------------------
PAPER_L = (248, 244, 233)
PAPER_R = (246, 242, 231)
NAVY = (27, 42, 74)
INK = (31, 42, 68)
GOLD = (176, 141, 46)
GOLD_LT = (201, 170, 80)
RULE = (120, 130, 150)
FAINT = (196, 202, 214)
STAMP_BLUE = (31, 78, 121)
STAMP_RED = (140, 47, 47)
STAMP_GREEN = (46, 107, 79)
SKIN = (233, 190, 150)
SKIN_DK = (214, 168, 128)
HAIR = (74, 50, 38)
JACKET = (31, 42, 68)

# --- fonts -----------------------------------------------------------------


def F(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def sans(size, bold=False):
    return F("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)


def serif(size, bold=False, italic=False):
    if italic:
        return ImageFont.truetype(
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
            size)
    return F("DejaVuSerif-Bold.ttf" if bold else "DejaVuSerif.ttf", size)


def mono(size, bold=False):
    return F("DejaVuSansMono-Bold.ttf" if bold else "DejaVuSansMono.ttf", size)


# --- helpers ---------------------------------------------------------------

def spaced(draw, xy, text, font, fill, tracking=2):
    """Draw text with extra letter spacing."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking
    return x


def mrz_check(s):
    vals = {}
    for i in range(10):
        vals[str(i)] = i
    for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        vals[c] = 10 + i
    vals["<"] = 0
    total = 0
    for i, ch in enumerate(s):
        total += vals[ch] * (7, 3, 1)[i % 3]
    return str(total % 10)


def mrz_lines():
    line1 = "P<CDRVOSS<<ELENA<MARIS"
    line1 = line1 + "<" * (44 - len(line1))
    num = "CD0048217"
    dob = "940314"
    exp = "360602"
    pers = "PC940314000000"
    body = (
        num + mrz_check(num)
        + "CDR"
        + dob + mrz_check(dob)
        + "F"
        + exp + mrz_check(exp)
        + pers + mrz_check(pers)
    )
    line2 = body + mrz_check(body)
    assert len(line1) == 44 and len(line2) == 44, (len(line1), len(line2))
    return line1, line2


def guilloche(draw, x0, y0, x1, y1, color, step=9, amp=3):
    """Faint wavy horizontal rules across a page."""
    for y in range(y0, y1, step):
        pts = []
        for x in range(x0, x1 + 1, 8):
            pts.append((x, y + amp * math.sin((x - x0) / 47.0 + y / 31.0)))
        draw.line(pts, fill=color, width=1)


def coat_of_arms(draw, cx, cy, s, ink=NAVY, gold=GOLD):
    """Shield: star above a volcano, three waves below."""
    # shield outline
    pts = [
        (cx - s * 0.52, cy - s * 0.55),
        (cx + s * 0.52, cy - s * 0.55),
        (cx + s * 0.52, cy + s * 0.05),
        (cx, cy + s * 0.62),
        (cx - s * 0.52, cy + s * 0.05),
    ]
    draw.polygon(pts, outline=ink, width=max(2, int(s * 0.05)))
    # star
    sx, sy, r = cx, cy - s * 0.30, s * 0.13
    star = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        star.append((sx + rr * math.cos(ang), sy + rr * math.sin(ang)))
    draw.polygon(star, fill=gold)
    # volcano
    draw.polygon(
        [(cx - s * 0.34, cy + s * 0.28), (cx, cy - s * 0.12),
         (cx + s * 0.34, cy + s * 0.28)],
        fill=ink,
    )
    draw.polygon(
        [(cx - s * 0.10, cy + s * 0.02), (cx, cy - s * 0.12),
         (cx + s * 0.10, cy + s * 0.02)],
        fill=(232, 226, 208),
    )
    # waves
    for k, wy in enumerate((0.32, 0.42)):
        y = cy + s * wy
        pts = []
        for x in range(int(cx - s * 0.42), int(cx + s * 0.42) + 1, 4):
            pts.append((x, y + s * 0.03 * math.sin((x - cx) / (s * 0.09))))
        draw.line(pts, fill=ink, width=max(2, int(s * 0.035)))


def draw_portrait(box):
    """Flat-illustration passport portrait, returns an RGBA image."""
    w, h = box
    img = Image.new("RGBA", box, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # backdrop: soft vertical gradient bands
    for i in range(h):
        t = i / h
        c = tuple(int(199 + (226 - 199) * t) if j == 0 else
                  int(210 + (228 - 210) * t) if j == 1 else
                  int(220 + (232 - 220) * t) for j in range(3))
        d.line([(0, i), (w, i)], fill=c + (255,))
    # faint backdrop circle
    d.ellipse([w * 0.14, h * 0.06, w * 0.86, h * 0.72],
              outline=(255, 255, 255, 90), width=2)
    cx = w // 2
    # shoulders / jacket
    d.polygon([(w * 0.10, h), (w * 0.30, h * 0.74), (w * 0.70, h * 0.74),
               (w * 0.90, h)], fill=JACKET + (255,))
    # shirt V
    d.polygon([(cx - 13, h * 0.76), (cx + 13, h * 0.76), (cx, h * 0.94)],
              fill=(245, 244, 240, 255))
    # lapels
    d.polygon([(cx - 13, h * 0.76), (cx - 34, h * 0.86), (cx - 6, h)],
              fill=(24, 36, 62, 255))
    d.polygon([(cx + 13, h * 0.76), (cx + 34, h * 0.86), (cx + 6, h)],
              fill=(24, 36, 62, 255))
    # neck
    d.rectangle([cx - 9, h * 0.60, cx + 9, h * 0.75], fill=SKIN_DK + (255,))
    # back hair (bob)
    d.rounded_rectangle([cx - 34, h * 0.10, cx + 34, h * 0.52], radius=30,
                        fill=HAIR + (255,))
    # face
    d.ellipse([cx - 27, h * 0.13, cx + 27, h * 0.55], fill=SKIN + (255,))
    # hair fringe over forehead (soft arc, not a straight band)
    d.pieslice([cx - 28, h * 0.08, cx + 28, h * 0.32], 180, 360,
               fill=HAIR + (255,))
    d.ellipse([cx - 28, h * 0.16, cx - 8, h * 0.30], fill=HAIR + (255,))
    d.ellipse([cx + 8, h * 0.16, cx + 28, h * 0.30], fill=HAIR + (255,))
    # side locks
    d.rounded_rectangle([cx - 34, h * 0.22, cx - 22, h * 0.50], radius=6,
                        fill=HAIR + (255,))
    d.rounded_rectangle([cx + 22, h * 0.22, cx + 34, h * 0.50], radius=6,
                        fill=HAIR + (255,))
    # brows
    d.arc([cx - 20, h * 0.335, cx - 6, h * 0.375], 200, 340,
          fill=(58, 40, 30, 255), width=2)
    d.arc([cx + 6, h * 0.335, cx + 20, h * 0.375], 200, 340,
          fill=(58, 40, 30, 255), width=2)
    # eyes
    for ex in (cx - 13, cx + 13):
        d.ellipse([ex - 5, h * 0.39, ex + 5, h * 0.41],
                  fill=(255, 255, 255, 255))
        d.ellipse([ex - 2, h * 0.39, ex + 2, h * 0.41],
                  fill=(40, 32, 26, 255))
        d.line([(ex - 6, h * 0.385), (ex + 6, h * 0.385)],
               fill=(40, 32, 26, 255), width=2)
    # nose
    d.line([(cx, h * 0.42), (cx - 2, h * 0.475), (cx + 2, h * 0.475)],
           fill=(190, 140, 105, 255), width=2)
    # lips
    d.arc([cx - 8, h * 0.495, cx + 8, h * 0.525], 10, 170,
          fill=(150, 80, 70, 255), width=2)
    # cheeks
    d.ellipse([cx - 24, h * 0.45, cx - 12, h * 0.48],
              fill=(226, 150, 130, 70))
    d.ellipse([cx + 12, h * 0.45, cx + 24, h * 0.48],
              fill=(226, 150, 130, 70))
    return img


def stamp_layer(w, h, lines, color, shape="oval", font_size=15):
    """One ink stamp on its own transparent layer."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = 6
    if shape == "oval":
        d.ellipse([pad, pad, w - pad, h - pad], outline=color + (255,),
                  width=3)
        d.ellipse([pad + 5, pad + 5, w - pad - 5, h - pad - 5],
                  outline=color + (255,), width=1)
    else:
        d.rounded_rectangle([pad, pad, w - pad, h - pad], radius=8,
                            outline=color + (255,), width=3)
        d.rounded_rectangle([pad + 5, pad + 5, w - pad - 5, h - pad - 5],
                            radius=6, outline=color + (255,), width=1)
    f_big = sans(font_size + 2, bold=True)
    f = sans(font_size, bold=True)
    f_sm = sans(font_size - 2)
    y = pad + 12
    for i, (txt, kind) in enumerate(lines):
        ft = f_big if kind == "big" else (f if kind == "mid" else f_sm)
        tw = d.textlength(txt, font=ft)
        d.text(((w - tw) / 2, y), txt, font=ft, fill=color + (255,))
        y += ft.size + 5
    return img


def paste_rotated(base, layer, cx, cy, angle):
    rot = layer.rotate(angle, resample=Image.BICUBIC, expand=False)
    base.alpha_composite(rot, (int(cx - rot.width / 2), int(cy - rot.height / 2)))


def field(draw, x, y, label, value, label_w=118, vsize=19):
    draw.text((x, y), label, font=sans(10, bold=True), fill=(90, 100, 120))
    draw.text((x + label_w, y - 3), value, font=sans(vsize, bold=True),
              fill=INK)
    return y + 30


# --- build -----------------------------------------------------------------

img = Image.new("RGBA", (W, H), (255, 255, 255, 255))
d = ImageDraw.Draw(img)

# page backgrounds
d.rectangle([0, 0, 511, H], fill=PAPER_L + (255,))
d.rectangle([512, 0, W, H], fill=PAPER_R + (255,))
# outer frame
d.rectangle([6, 6, W - 7, H - 7], outline=NAVY + (255,), width=3)
d.rectangle([12, 12, W - 13, H - 13], outline=GOLD + (255,), width=1)
# spine
d.line([(511, 12), (511, H - 13)], fill=(150, 140, 110, 255), width=2)
d.line([(513, 12), (513, H - 13)], fill=(220, 212, 190, 255), width=1)

# faint guilloche on both pages
guilloche(d, 16, 130, 505, 1010, (214, 219, 228, 255), step=12)
guilloche(d, 518, 90, 1008, 1010, (214, 219, 228, 255), step=12)

# ================= LEFT PAGE : DATA PAGE =================
# header
coat_of_arms(d, 78, 66, 78)
spaced(d, (128, 34), "REPUBLIC OF CALDARA", serif(25, bold=True), NAVY, 1)
spaced(d, (128, 70), "P A S S P O R T", sans(15, bold=True), NAVY, 2)
d.text((128, 96), "Passeport  ·  République de Caldara",
       font=serif(11, italic=True), fill=(90, 100, 120))
d.line([(24, 122), (498, 122)], fill=RULE + (255,), width=1)
d.text((24, 128), "DATA PAGE  /  PAGE DES DONNÉES",
       font=sans(9, bold=True), fill=(110, 118, 135))

# portrait box
d.rectangle([24, 152, 178, 356], outline=NAVY + (255,), width=2)
d.rectangle([28, 156, 174, 352], outline=GOLD + (255,), width=1)
portrait = draw_portrait((142, 192))
img.alpha_composite(portrait, (30, 158))
d.text((30, 360), "PHOTOGRAPH  ·  PHOTO", font=sans(8, bold=True),
       fill=(110, 118, 135))

# data fields, right of portrait
x0 = 196
y = 152
y = field(d, x0, y, "TYPE", "P", label_w=52)
y = field(d, x0 + 190, 152, "CODE", "CDR", label_w=52)
y = 186
y = field(d, x0, y, "PASSPORT No.", "CD 0048217")
y = field(d, x0, y, "SURNAME", "VOSS")
y = field(d, x0, y, "GIVEN NAMES", "ELENA MARIS")
y = field(d, x0, y, "NATIONALITY", "CALDARAN")
y = field(d, x0, y, "DATE OF BIRTH", "14 MAR 1994")
y = field(d, x0, y, "PLACE OF BIRTH", "PORT CALDARA")

# lower block: authority, issue, expiry, sex
d.line([(24, 392), (498, 392)], fill=RULE + (255,), width=1)
y = 404
y = field(d, 24, y, "SEX", "F", label_w=52)
y = field(d, 196, 404, "DATE OF ISSUE", "03 JUN 2026")
y = field(d, 196, 434, "DATE OF EXPIRY", "02 JUN 2036")
y = 470
y = field(d, 24, y, "AUTHORITY", "MINISTRY OF THE INTERIOR",
          label_w=118, vsize=17)
y = field(d, 24, y, "PLACE OF ISSUE", "PORT CALDARA", label_w=118,
          vsize=17)

# signature
d.line([(24, 556), (300, 556)], fill=INK + (255,), width=1)
d.text((30, 524), "Elena Maris Voss", font=serif(24, italic=True), fill=INK)
d.text((24, 560), "HOLDER'S SIGNATURE  ·  SIGNATURE DU TITULAIRE",
       font=sans(8, bold=True), fill=(110, 118, 135))

# bilingual note: the telling paperwork detail on the data page
d.rounded_rectangle([24, 596, 498, 684], radius=4,
                    outline=(140, 120, 60, 255), width=1)
d.text((34, 604), "ENDORSEMENT  ·  MENTION",
       font=sans(9, bold=True), fill=(120, 100, 40))
d.text((34, 622),
       "Holder is a registered seafarer of the Caldaran",
       font=sans(12), fill=INK)
d.text((34, 640),
       "Merchant Marine. Shore employment ashore",
       font=sans(12), fill=INK)
d.text((34, 658),
       "requires a work permit.",
       font=sans(12), fill=INK)

# second-language column (Caldaran / English)
d.text((24, 690), "Issued in Caldaran and English.  ·  Délivré en caldaran et en anglais.",
       font=serif(11, italic=True), fill=(90, 100, 120))
d.text((24, 712), "Nom  ·  Prénom  ·  Né(e) le  ·  Lieu de naissance  ·  Sexe",
       font=sans(9), fill=(110, 118, 135))

# fingerprint + emergency contact fill the lower gap
d.rectangle([24, 736, 168, 848], outline=NAVY + (255,), width=2)
d.rectangle([28, 740, 164, 844], outline=GOLD + (255,), width=1)
for k in range(5):
    r = 12 + k * 9
    d.arc([96 - r, 792 - r, 96 + r, 792 + r], 200, 340,
          fill=(90, 100, 120, 255), width=2)
    d.arc([96 - r, 792 - r, 96 + r, 792 + r], 20, 160,
          fill=(90, 100, 120, 255), width=2)
d.text((36, 742), "RIGHT INDEX", font=sans(8, bold=True),
       fill=(110, 118, 135))
d.text((186, 742), "IN CASE OF EMERGENCY, NOTIFY",
       font=sans(9, bold=True), fill=(110, 118, 135))
d.text((186, 764), "MARA VOSS", font=sans(15, bold=True), fill=INK)
d.text((186, 788), "Harbour Office, Quay 3", font=sans(12), fill=INK)
d.text((186, 808), "Port Caldara, Caldara", font=sans(12), fill=INK)

# MRZ
l1, l2 = mrz_lines()
mf = mono(17)
d.rectangle([22, 856, 500, 916], fill=(238, 234, 220, 255))
d.rectangle([22, 856, 500, 916], outline=(180, 175, 155, 255), width=1)
d.text((30, 862), l1, font=mf, fill=INK)
d.text((30, 888), l2, font=mf, fill=INK)
d.text((24, 928), "2", font=sans(11, bold=True), fill=(110, 118, 135))

# ================= RIGHT PAGE : VISA / STAMPS =================
d.text((536, 30), "VISAS", font=serif(22, bold=True), fill=NAVY)
d.text((640, 38), "VISAS  ·  VISA", font=sans(10, bold=True),
       fill=(110, 118, 135))
d.line([(536, 62), (1000, 62)], fill=RULE + (255,), width=1)

# visa sticker (own layer, rotated)
visa = Image.new("RGBA", (470, 190), (0, 0, 0, 0))
vd = ImageDraw.Draw(visa)
vd.rounded_rectangle([4, 4, 465, 185], radius=10,
                     fill=(226, 238, 226, 255),
                     outline=STAMP_GREEN + (255,), width=3)
vd.rounded_rectangle([10, 10, 459, 179], radius=8,
                     outline=STAMP_GREEN + (255,), width=1)
vd.text((22, 16), "SOVARA", font=sans(24, bold=True),
        fill=STAMP_GREEN + (255,))
vd.text((330, 22), "VISA", font=sans(22, bold=True),
        fill=STAMP_GREEN + (255,))
vd.line([(22, 52), (448, 52)], fill=STAMP_GREEN + (255,), width=2)
vd.text((22, 62), "SINGLE ENTRY  ·  No. SV-22140", font=sans(15, bold=True),
        fill=(30, 60, 40, 255))
vd.text((22, 88), "Valid  18 JUL 2026  —  02 AUG 2026", font=sans(15),
        fill=(30, 60, 40, 255))
vd.text((22, 114), "CONDITION: SHIP'S CREW ONLY", font=sans(15, bold=True),
        fill=(140, 47, 47, 255))
vd.text((22, 142), "Issued at Port Caldara  ·  10 JUL 2026",
        font=sans(13), fill=(30, 60, 40, 255))
paste_rotated(img, visa, 768, 168, -2)

# stamps: 2 columns x 4 rows
stamps = [
    ("EXIT", "PORT CALDARA", "18 JUL 2026", STAMP_BLUE, -4),
    ("ENTRY", "SOVARA", "18 JUL 2026", STAMP_BLUE, 3),
    ("EXIT", "SOVARA", "02 AUG 2026", STAMP_BLUE, -2),
    ("ENTRY", "PORT CALDARA", "02 AUG 2026", STAMP_BLUE, 5),
    ("EXIT", "PORT CALDARA", "12 SEP 2026", STAMP_RED, -3),
    ("ENTRY", "TARNOVIA", "12 SEP 2026", STAMP_RED, 4),
    ("EXIT", "TARNOVIA", "28 SEP 2026", STAMP_RED, 2),
    ("ENTRY", "PORT CALDARA", "28 SEP 2026", STAMP_RED, -5),
]
sx = [640, 896]
sy = [330, 450, 570, 690]
for i, (kind, place, date, color, ang) in enumerate(stamps):
    cx = sx[i % 2]
    cy = sy[i // 2]
    layer = stamp_layer(216, 104,
                        [(kind, "big"), (place, "mid"), (date, "mid")],
                        color, shape="oval", font_size=15)
    paste_rotated(img, layer, cx, cy, ang)

# fee stamp, bottom
fee = stamp_layer(300, 92,
                  [("PORT TAX  ·  25 CALDRA", "mid"), ("PAID", "big"),
                   ("HARBOUR MASTER, PORT CALDARA", "sm")],
                  STAMP_RED, shape="rect", font_size=14)
paste_rotated(img, fee, 768, 800, -1)

# faint watermark arms on visa page
wm = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
wd = ImageDraw.Draw(wm)
coat_of_arms(wd, 150, 150, 240, ink=(27, 42, 74, 28),
             gold=(176, 141, 46, 28))
img.alpha_composite(wm, (620, 830))
d.text((988, 928), "3", font=sans(11, bold=True), fill=(110, 118, 135))

# save
out = os.path.join(HERE, "entry.png")
img.convert("RGB").save(out, "PNG")
size = os.path.getsize(out)
sha = hashlib.sha256(open(out, "rb").read()).hexdigest()
print(f"entry.png: {size} bytes, sha256 {sha[:16]}...")
print(f"MRZ L1: {l1}")
print(f"MRZ L2: {l2}")
assert size <= 1048576, "over 1 MiB"
