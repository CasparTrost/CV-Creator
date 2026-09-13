#!/usr/bin/env python3
"""Generate the favicon, the touch icons and the social sharing image.

    python3 tools/make-images.py

Writes assets/favicon.svg, assets/favicon.png, assets/apple-touch-icon.png,
assets/icon-512.png and assets/og.png. Run it again if the wordmark or the
accent colour changes.
"""
import io
import io
import os
import re
import urllib.request

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, 'assets')

INK = (22, 32, 43)
PAPER = (255, 255, 255)
WASH = (237, 239, 242)
ACCENT = (31, 95, 91)
MUTED = (90, 103, 115)
RULE = (213, 219, 225)

# The old CSS endpoint still answers with TrueType for an old user agent,
# which is what Pillow can draw with. Cached outside the repository.
CACHE = os.path.join(os.environ.get('TMPDIR', '/tmp'), 'plainsheet-fonts')
OLD_UA = 'Mozilla/5.0 (Windows NT 6.1)'   # old enough that the API answers TrueType


def ttf(family, weight):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, '%s-%s.ttf' % (family.replace(' ', ''), weight))
    if not os.path.exists(path):
        url = 'https://fonts.googleapis.com/css?family=%s:%s' % (
            family.replace(' ', '+'), weight)
        css = urllib.request.urlopen(
            urllib.request.Request(url, headers={'User-Agent': OLD_UA}), timeout=60).read().decode()
        src = re.search(r'url\((https://[^)]+)\)', css).group(1)
        with open(path, 'wb') as fh:
            fh.write(urllib.request.urlopen(src, timeout=60).read())
    return path


def font(family, weight, size):
    return ImageFont.truetype(ttf(family, weight), size)


# ---------------------------------------------------------------- favicon

FAVICON_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="10" fill="#16202B"/>
  <rect x="16" y="11" width="32" height="42" rx="2" fill="#FFFFFF"/>
  <rect x="16" y="11" width="32" height="11" fill="#1F5F5B"/>
  <rect x="21" y="28" width="13" height="3" rx="1.5" fill="#1F5F5B"/>
  <rect x="21" y="35" width="22" height="2" rx="1" fill="#D5DBE1"/>
  <rect x="21" y="40" width="22" height="2" rx="1" fill="#D5DBE1"/>
  <rect x="21" y="45" width="15" height="2" rx="1" fill="#D5DBE1"/>
</svg>
'''


def sheet_icon(size):
    """The favicon drawn as a bitmap, at whatever size is asked for."""
    s = size * 4
    img = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    u = s / 64.0
    d.rounded_rectangle([0, 0, s, s], radius=10 * u, fill=INK)
    d.rounded_rectangle([16 * u, 11 * u, 48 * u, 53 * u], radius=2 * u, fill=PAPER)
    d.rectangle([16 * u, 11 * u, 48 * u, 22 * u], fill=ACCENT)
    d.rounded_rectangle([21 * u, 28 * u, 34 * u, 31 * u], radius=1.5 * u, fill=ACCENT)
    for y in (35, 40):
        d.rounded_rectangle([21 * u, y * u, 43 * u, (y + 2) * u], radius=u, fill=RULE)
    d.rounded_rectangle([21 * u, 45 * u, 36 * u, 47 * u], radius=u, fill=RULE)
    return img.resize((size, size), Image.LANCZOS)


# ---------------------------------------------------------------- og image

def og_image():
    W, H = 1200, 630
    img = Image.new('RGB', (W, H), WASH)
    d = ImageDraw.Draw(img)

    # Faint grid, the same one the hero section uses.
    for x in range(0, W, 28):
        d.line([(x, 0), (x, H)], fill=(228, 232, 236), width=1)
    for y in range(0, H, 28):
        d.line([(0, y), (W, y)], fill=(228, 232, 236), width=1)

    serif_l = font('Newsreader', 500, 64)
    serif_m = font('Newsreader', 500, 34)
    sans = font('IBM Plex Sans', 400, 25)
    sans_b = font('IBM Plex Sans', 600, 22)

    d.text((72, 64), 'Plain', font=serif_m, fill=INK)
    w = d.textlength('Plain', font=serif_m)
    d.text((72 + w, 64), 'Sheet', font=font('Newsreader', 600, 34), fill=INK)

    d.text((72, 176), 'Write it, see it,', font=serif_l, fill=INK)
    d.text((72, 250), 'download it.', font=serif_l, fill=INK)

    d.text((72, 352), 'A resume editor with a live A4 page in front of', font=sans, fill=MUTED)
    d.text((72, 388), 'you. Free PDF, no account, nothing uploaded.', font=sans, fill=MUTED)

    d.rounded_rectangle([72, 462, 332, 522], radius=4, fill=ACCENT)
    label = 'Sixteen free layouts'
    lw = d.textlength(label, font=sans_b)
    d.text((72 + (260 - lw) / 2, 481), label, font=sans_b, fill=PAPER)

    # A sheet of paper, drawn the way the template previews are.
    sx, sy, sw = 742, 96, 330
    sh = int(sw * 297 / 210.0)
    d.rectangle([sx + 8, sy + 12, sx + sw + 8, sy + sh + 12], fill=(214, 218, 223))
    d.rectangle([sx, sy, sx + sw, sy + sh], fill=PAPER)
    u = sw / 210.0
    d.rectangle([sx, sy, sx + 71 * u, sy + sh], fill=(230, 236, 234))
    d.polygon([(sx, sy), (sx + sw, sy), (sx + sw, sy + 77 * u), (sx + 77 * u, sy + 77 * u)],
              fill=ACCENT)
    d.rounded_rectangle([sx + 15 * u, sy + 18 * u, sx + 59 * u, sy + 64 * u],
                        radius=2 * u, fill=(210, 203, 199))
    d.rounded_rectangle([sx + 88 * u, sy + 22 * u, sx + 158 * u, sy + 28 * u],
                        radius=u, fill=(255, 255, 255))
    for y in (35, 43, 51):
        d.rectangle([sx + 88 * u, sy + y * u, sx + 192 * u, sy + (y + 2) * u],
                    fill=(180, 208, 205))
    for col, top, width in ((14, 96, 45), (88, 96, 108)):
        d.rounded_rectangle([sx + col * u, sy + top * u,
                             sx + (col + width * 0.55) * u, sy + (top + 4.5) * u],
                            radius=u, fill=ACCENT)
        for i in range(6):
            y = top + 11 + i * 9
            d.rectangle([sx + col * u, sy + y * u, sx + (col + width) * u, sy + (y + 2) * u],
                        fill=RULE)
    return img


def main():
    with io.open(os.path.join(ASSETS, 'favicon.svg'), 'w',
                 encoding='utf-8', newline='\n') as fh:
        fh.write(FAVICON_SVG)
    sheet_icon(32).save(os.path.join(ASSETS, 'favicon.png'))
    sheet_icon(180).save(os.path.join(ASSETS, 'apple-touch-icon.png'))
    sheet_icon(512).save(os.path.join(ASSETS, 'icon-512.png'))

    ico = os.path.join(ASSETS, 'favicon.ico')
    sheet_icon(64).save(ico, sizes=[(16, 16), (32, 32), (48, 48)])

    og = og_image()
    og.save(os.path.join(ASSETS, 'og.png'), optimize=True)
    print('icons and og.png written')


if __name__ == '__main__':
    main()
