# -*- coding: utf-8 -*-
"""
The icon set, in one place.

Every icon is the inside of a 24x24 SVG drawn with strokes only: no fills, no
colour, uniform 2px lines with round caps. They are used as CSS masks, which is
why the colour never appears here — the mask takes the colour of whatever it
sits on, so a heading in the accent colour gets an accent-coloured icon and the
white text in a dark sidebar gets a white one.

`tools/build.py` turns this table into `assets/icons.css` for the site pages and
into the variable block inside `editor.html` for the resume itself. Edit an icon
here and both follow.
"""

# --- Kontaktzeilen im Lebenslauf -------------------------------------------
ICONS = {
'ort': """
<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0116 0z"/><circle cx="12" cy="10" r="3"/>
""",
'tel': """
<path d="M22 16.9v3a2 2 0 01-2.2 2 19.8 19.8 0 01-8.6-3.1 19.5 19.5 0 01-6-6A19.8 19.8 0 012.1 4.2
 2 2 0 014.1 2h3a2 2 0 012 1.7c.1 1 .4 1.9.7 2.8a2 2 0 01-.4 2.1L8.1 9.9a16 16 0 006 6l1.3-1.3a2 2
 0 012.1-.5c.9.4 1.8.6 2.8.8a2 2 0 011.7 2z"/>
""",
'mail': """
<rect x="2" y="4" width="20" height="16" rx="2"/><path d="M2.5 6.5l9.5 7 9.5-7"/>
""",
'datum': """
<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>
""",

# --- Reihe 1 des Blattes: Rubriken des Lebenslaufs -------------------------
'aktentasche': """
<rect x="2.5" y="7" width="19" height="13.5" rx="2"/>
<path d="M8 7V5.2A2.2 2.2 0 0110.2 3h3.6A2.2 2.2 0 0116 5.2V7"/>
<path d="M2.5 13h7.2m4.6 0h7.2"/>
<rect x="9.7" y="11.2" width="4.6" height="3.6" rx="1"/>
""",
'hut': """
<path d="M2.5 8.6 12 4.2l9.5 4.4L12 13z"/>
<path d="M6.2 10.3v4.4c0 1.7 2.6 3.1 5.8 3.1s5.8-1.4 5.8-3.1v-4.4"/>
<path d="M20.4 9.7v5.6"/>
""",
'zahnrad': """
<circle cx="12" cy="12" r="3"/>
<path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 01-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33
 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2
 0 01-2.83-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0
 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06a1.65 1.65 0 001.82.33H9a1.65
 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0
 012.83 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65
 0 00-1.51 1z"/>
""",
'sprechblasen': """
<path d="M13.2 3.5H4.6A2.1 2.1 0 002.5 5.6v5.3a2.1 2.1 0 002.1 2.1h.7v3.1l3.4-3.1h4.5a2.1 2.1 0
 002.1-2.1V5.6a2.1 2.1 0 00-2.1-2.1z"/>
<path d="M17.2 8.6h2.2a2.1 2.1 0 012.1 2.1v4.6a2.1 2.1 0 01-2.1 2.1h-.6v3l-3.3-3h-3.3"/>
""",
'urkunde': """
<path d="M19 13.4V5A2 2 0 0017 3H7a2 2 0 00-2 2v14a2 2 0 002 2h5"/>
<path d="M8.4 7.6h7.2M8.4 10.8h7.2M8.4 14h3.4"/>
<circle cx="16.8" cy="16.6" r="2.9"/>
<path d="M14.7 18.7 14 23l2.8-1.6L19.6 23l-.7-4.3"/>
""",
'person': """
<circle cx="12" cy="12" r="9.4"/><circle cx="12" cy="9.8" r="3.1"/>
<path d="M5.7 18.8a7.1 7.1 0 0112.6 0"/>
""",

# --- Reihe 2: Lebenslauf-Extras und Seiten-Symbole ------------------------
'stern': """
<path d="m12 3.2 2.9 5.9 6.5.9-4.7 4.6 1.1 6.5L12 18l-5.8 3.1 1.1-6.5-4.7-4.6 6.5-.9z"/>
""",
'lenkrad': """
<circle cx="12" cy="12" r="9.3"/>
<circle cx="12" cy="12" r="3.1"/>
<path d="M12 8.9V2.7M9.4 13.6 5.2 17.8M14.6 13.6 18.8 17.8"/>
""",
'globus': """
<circle cx="12" cy="12" r="9.4"/><path d="M2.6 12h18.8"/>
<path d="M12 2.6c2.6 2.6 4.1 5.9 4.1 9.4S14.6 18.8 12 21.4C9.4 18.8 7.9 15.5 7.9 12S9.4 5.2 12 2.6z"/>
<path d="M4.7 6.4c2 1.2 4.6 1.9 7.3 1.9s5.3-.7 7.3-1.9M4.7 17.6c2-1.2 4.6-1.9 7.3-1.9s5.3.7 7.3 1.9"/>
""",
'schild': """
<path d="M12 2.7 4.6 5.3v6.2c0 4.6 3 8.1 7.4 9.8 4.4-1.7 7.4-5.2 7.4-9.8V5.3z"/>
<path d="m8.7 12.1 2.5 2.5 4.2-4.6"/>
""",
'blatt': """
<path d="M14.2 3H7.4A2 2 0 005.4 5v14a2 2 0 002 2h9.2a2 2 0 002-2V7.5z"/>
<path d="M14.2 3v4.5h4.4"/>
<path d="M12 10.6v6.2M9.1 14l2.9 2.9 2.9-2.9"/>
""",
'drucker': """
<path d="M7 8.4V3.6h10v4.8"/>
<path d="M7 16.4H4.6a2 2 0 01-2-2v-4a2 2 0 012-2h14.8a2 2 0 012 2v4a2 2 0 01-2 2H17"/>
<rect x="7" y="13.4" width="10" height="7" rx="1"/>
<path d="M9.6 16.2h4.8M9.6 18.2h4.8"/>
<circle cx="18.1" cy="11" r=".9" fill="#000" stroke="none"/>
""",

# --- Reihe 3: Rubriken der Website ----------------------------------------
'raster': """
<rect x="3.4" y="3.4" width="7.2" height="7.2" rx="1.6"/>
<rect x="13.4" y="3.4" width="7.2" height="7.2" rx="1.6"/>
<rect x="3.4" y="13.4" width="7.2" height="7.2" rx="1.6"/>
<rect x="13.4" y="13.4" width="7.2" height="7.2" rx="1.6"/>
""",
'buch': """
<path d="M12 6.6C10.2 5.2 7.6 4.5 4.2 4.5v12.2c3.4 0 6 .7 7.8 2.1 1.8-1.4 4.4-2.1 7.8-2.1V4.5
 c-3.4 0-6 .7-7.8 2.1z"/>
<path d="M12 6.6v12.2"/>
""",
'lupe': """
<path d="M18.6 10.6V7.5L14.2 3H7.4a2 2 0 00-2 2v14a2 2 0 002 2h3.4"/>
<path d="M14.2 3v4.5h4.4"/><path d="M8.6 8.4h3.6M8.6 11.4h5.4"/>
<circle cx="15.9" cy="15.9" r="3.5"/><path d="m18.6 18.6 2.8 2.8"/>
""",
'umschlag': """
<path d="M2.9 10.9v8.3a1.9 1.9 0 001.9 1.9h14.4a1.9 1.9 0 001.9-1.9v-8.3"/>
<path d="M2.9 10.9 7.9 7.3M21.1 10.9 16.1 7.3"/>
<path d="M7.9 13.7V5.6a1 1 0 011-1h6.2a1 1 0 011 1v8.1"/>
<path d="M10.4 8h3.2M10.4 10.6h3.2"/>
<path d="m2.9 10.9 7.7 6.2h2.8l7.7-6.2"/>
""",
'kamera': """
<path d="M4.6 8.4h2.9l1.7-2.6h5.6l1.7 2.6h2.9a2 2 0 012 2v8a2 2 0 01-2 2H4.6a2 2 0 01-2-2v-8a2 2 0
 012-2z"/>
<circle cx="12" cy="14.4" r="3.5"/>
<circle cx="17.7" cy="11" r=".9" fill="#000" stroke="none"/>
""",
'kalender': """
<rect x="3.4" y="5.6" width="17.2" height="15" rx="2"/>
<path d="M3.4 10.2h17.2M8.2 3.4v4.4M15.8 3.4v4.4"/>
<rect x="9.9" y="13" width="4.6" height="4.2" rx=".8"/>
""",

# --- Reihe 4: Berufe ------------------------------------------------------
'stethoskop': """
<path d="M5.6 3.4v5.4a5 5 0 004.4 5"/>
<path d="M14.4 3.4v5.4a5 5 0 01-4.4 5"/>
<path d="M3.8 3.4h3.6M12.6 3.4h3.6"/>
<path d="M10 13.8v2.4a3.6 3.6 0 007.2 0v-2.2"/>
<circle cx="17.2" cy="11.4" r="2.2"/>
""",
'code': """
<rect x="2.8" y="4" width="18.4" height="16" rx="2"/><path d="M2.8 8.6h18.4"/>
<circle cx="6" cy="6.3" r=".8" fill="#000" stroke="none"/>
<circle cx="8.6" cy="6.3" r=".8" fill="#000" stroke="none"/>
<circle cx="11.2" cy="6.3" r=".8" fill="#000" stroke="none"/>
<path d="m9.4 12.4-2.4 2.4 2.4 2.4M14.6 12.4l2.4 2.4-2.4 2.4M13 11.8l-2 6"/>
""",
'klemmbrett': """
<path d="M9.2 4.6H7.4a2 2 0 00-2 2V19a2 2 0 002 2h9.2a2 2 0 002-2V6.6a2 2 0 00-2-2h-1.8"/>
<rect x="9.2" y="2.8" width="5.6" height="3.6" rx="1.3"/>
<path d="m8.8 13.4 2.5 2.5 4.2-4.6"/>
""",
'karton': """
<path d="M20.6 7.6v8.8L12 20.8 3.4 16.4V7.6L12 3.2z"/>
<path d="M3.4 7.6 12 12l8.6-4.4M12 12v8.8"/>
<path d="M16.3 18.9v-4.3M14.5 16.2l1.8-1.8 1.8 1.8"/>
""",
'rechner': """
<rect x="5" y="2.8" width="14" height="18.4" rx="2"/>
<rect x="7.8" y="5.6" width="8.4" height="3.4" rx=".8"/>
<circle cx="8.7" cy="12.4" r=".95" fill="#000" stroke="none"/>
<circle cx="12" cy="12.4" r=".95" fill="#000" stroke="none"/>
<circle cx="15.3" cy="12.4" r=".95" fill="#000" stroke="none"/>
<circle cx="8.7" cy="15.4" r=".95" fill="#000" stroke="none"/>
<circle cx="12" cy="15.4" r=".95" fill="#000" stroke="none"/>
<circle cx="15.3" cy="15.4" r=".95" fill="#000" stroke="none"/>
<circle cx="8.7" cy="18.4" r=".95" fill="#000" stroke="none"/>
<circle cx="12" cy="18.4" r=".95" fill="#000" stroke="none"/>
<circle cx="15.3" cy="18.4" r=".95" fill="#000" stroke="none"/>
""",
'handschlag': """
<path d="m11 17 2 2a1.4 1.4 0 002-2"/>
<path d="m14 14 2.5 2.5a1.4 1.4 0 002-2l-3.9-3.9a3 3 0 00-4.2 0l-.9.9a1.4 1.4 0 01-2-2l2.8-2.8a5.8
 5.8 0 017 -.9l.5.3a2 2 0 001.4.2L21 4"/>
<path d="m21 3 1 11h-2"/>
<path d="M3 3 2 14l6.5 6.5a1.4 1.4 0 002-2"/>
<path d="M3 4h8"/>
""",
}

WRAPPER = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' "
           "stroke='#000' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>"
           "%s</svg>")


def svg(name):
    """The finished SVG for one icon."""
    return WRAPPER % ' '.join(ICONS[name].split())


def data_uri(name):
    """The same SVG, packed into a CSS url() that works in every browser."""
    s = svg(name).replace('"', "'").replace('#', '%23')
    s = s.replace('<', '%3C').replace('>', '%3E')
    return 'url("data:image/svg+xml;utf8,%s")' % s


def css_variables(indent='  '):
    return '\n'.join('%s--i-%s:%s;' % (indent, n, data_uri(n)) for n in ICONS)
