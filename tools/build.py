#!/usr/bin/env python3
"""Render every page of the site.

The site is plain HTML and is served exactly as it sits in this folder.
This script exists only so that thirty-odd pages can share one header,
one footer and one set of meta tags. Edit the content here or in
tools/content.py, run the script, commit the HTML it writes.

    python3 tools/build.py

Domain and operator details are read from assets/site-config.js, so that
file stays the single place you edit before going live.
"""
import io
import json
import os
import re
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def lies(pfad):
    """Jede Datei hier ist UTF-8.

    Ohne diese Angabe nimmt Python die Kodierung des Betriebssystems — unter
    deutschem Windows cp1252 — und bricht beim ersten typografischen
    Anführungszeichen ab. Auf einem Linux-Rechner fällt das nie auf, und
    genau deshalb steht es hier und nicht im Kopf jeder einzelnen Zeile.
    """
    return io.open(pfad, encoding='utf-8').read()
TODAY = datetime.date.today().isoformat()

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import content  # noqa: E402  (guide and page copy)
import icons  # noqa: E402  (the icon set, one source for site and editor)


# ---------------------------------------------------------------- config

def read_config():
    src = lies(os.path.join(ROOT, 'assets', 'site-config.js'))

    def field(name, block=''):
        pattern = r"%s\s*:\s*'([^']*)'" % name
        if block:
            section = re.search(r'%s\s*:\s*\{(.*?)\n  \}' % block, src, re.S)
            src_part = section.group(1) if section else ''
        else:
            src_part = src
        hit = re.search(pattern, src_part)
        return hit.group(1) if hit else ''

    return {
        'domain': field('domain').rstrip('/'),
        'operator': field('name', 'operator'),
        'email': field('email', 'operator'),
        'adsense': field('client', 'ads'),
        'ki': field('endpunkt', 'ki'),
        'ki_anbieter': field('anbieter', 'ki') or 'an einen KI-Dienst',
    }


CFG = read_config()
DOMAIN = CFG['domain']
BRAND = 'PlainSheet'
TEMPLATES = json.loads(lies(os.path.join(ROOT, 'tools', 'data', 'templates.json')))
BY_ID = {t['tid']: t for t in TEMPLATES}

_de = content.for_lang('de')
TEMPLATE_COPY = {
    'en': {t['tid']: t for t in TEMPLATES},
    'de': {tid: dict(copy,
                     specs=[(_de.SPEC_KEYS.get(k, k), _de.SPEC_VALUES.get(v, v))
                            for k, v in BY_ID[tid]['specs']],
                     svg=BY_ID[tid]['svg'], slug=BY_ID[tid]['slug'], tid=tid)
           for tid, copy in _de.TEMPLATES.items()},
}


# ---------------------------------------------------------------- helpers

def up(depth):
    return '../' * depth


def esc(text):
    return (text.replace('&', '&amp;').replace('<', '&lt;')
                .replace('>', '&gt;').replace('"', '&quot;'))


def head(title, description, path, depth, extra_ld=None, image='assets/og.png',
         published=None, modified=None, kind='website', noindex=False,
         lang='en', alternate=None):
    """The <head> every page shares. `path` is relative to the site root."""
    u = up(depth)
    url = '%s/%s' % (DOMAIN, path)
    ld = [{
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        'name': BRAND,
        'url': DOMAIN + '/',
        'description': 'A free resume builder that runs entirely in the browser.',
    }] if path == 'index.html' else []
    if extra_ld:
        ld.extend(extra_ld)

    # data-root tells the scripts how deep the page sits, which beats guessing
    # from the URL and survives being served from a subdirectory.
    parts = [
        '<!DOCTYPE html>',
        '<html lang="%s" data-root="%s">' % (lang, u or './'),
        '<head>',
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<title>%s</title>' % esc(title),
        '<meta name="description" content="%s">' % esc(description),
        '<link rel="canonical" href="%s">' % url,
    ]
    if alternate:
        # Both directions plus x-default, which is what Google asks for.
        pairs = dict(alternate)
        pairs.setdefault(lang, path)
        for code in sorted(pairs):
            parts.append('<link rel="alternate" hreflang="%s" href="%s/%s">'
                         % (code, DOMAIN, pairs[code]))
        parts.append('<link rel="alternate" hreflang="x-default" href="%s/%s">'
                     % (DOMAIN, pairs.get('en', path)))
    if noindex:
        parts.append('<meta name="robots" content="noindex, follow">')
    parts += [
        '<meta name="theme-color" content="#1F5F5B">',
        '',
        '<meta property="og:type" content="%s">' % ('article' if kind == 'article' else 'website'),
        '<meta property="og:site_name" content="%s">' % BRAND,
        '<meta property="og:locale" content="%s">' % ('de_DE' if lang == 'de' else 'en_GB'),
        '<meta property="og:title" content="%s">' % esc(title),
        '<meta property="og:description" content="%s">' % esc(description),
        '<meta property="og:url" content="%s">' % url,
        '<meta property="og:image" content="%s/%s">' % (DOMAIN, image),
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta name="twitter:card" content="summary_large_image">',
        '',
        '<link rel="icon" href="%sassets/favicon.svg" type="image/svg+xml">' % u,
        '<link rel="alternate icon" href="%sassets/favicon.png" sizes="32x32">' % u,
        '<link rel="apple-touch-icon" href="%sassets/apple-touch-icon.png">' % u,
        '<link rel="manifest" href="%ssite.webmanifest">' % u,
        '',
        '<link rel="preload" as="font" type="font/woff2" crossorigin '
        'href="%sassets/fonts/newsreader-400600-latin.woff2">' % u,
        '<link rel="preload" as="font" type="font/woff2" crossorigin '
        'href="%sassets/fonts/ibmplexsans-400600-latin.woff2">' % u,
        '<link rel="stylesheet" href="%sassets/fonts-site.css">' % u,
        '<link rel="stylesheet" href="%sassets/site.css">' % u,
        '<link rel="stylesheet" href="%sassets/icons.css">' % u,
        '',
        '<script src="%sassets/site-config.js"></script>' % u,
        '<script src="%sassets/consent.js"></script>' % u,
        '<script src="%sassets/ads.js" defer></script>' % u,
    ]
    if published:
        parts.append('<meta property="article:published_time" content="%s">' % published)
    if modified:
        parts.append('<meta property="article:modified_time" content="%s">' % modified)
    for block in ld:
        parts.append('<script type="application/ld+json">%s</script>'
                     % json.dumps(block, separators=(',', ':')))
    parts += ['</head>', '<body>',
              '<a class="skip" href="#main">%s</a>' % LANGS[lang]['skip']]
    return '\n'.join(parts)


# Every path below is relative to the site root; up(depth) turns it into a
# link. The German tree lives under de/ with German slugs, because a URL is
# read by the person deciding whether to click it.
LANGS = {
    'en': {
        'code': 'en',
        'name': 'English',
        'other': 'de',
        'home': 'index.html',
        'editor': 'editor.html',
        'templates': 'templates.html',
        'template_dir': 'templates/',
        'guides': 'guides/index.html',
        'guide_dir': 'guides/',
        'examples': 'examples/index.html',
        'example_dir': 'examples/',
        'about': 'about.html',
        'privacy': 'privacy.html',
        'imprint': 'imprint.html',
        'nav': [('templates', 'Templates'), ('examples', 'Examples'),
                ('guides', 'Guides'), ('about', 'About')],
        'cta': 'Open the editor',
        'switch': 'Deutsch',
        'crumb_home': 'Home',
        'crumb_guides': 'Guides',
        'crumb_examples': 'Examples',
        'crumb_templates': 'Templates',
        'min_read': '%d min read',
        'updated': 'Updated %s',
        'written_by': 'Written by the %s team',
        'read_next': 'Read next',
        'another_example': 'Another example',
        'more_guides': 'More guides',
        'every_guide': 'Every guide',
        'every_example': 'Every example',
        'all_examples': 'All eight examples',
        'faq_heading': 'Common questions',
        'start_here': 'Start here',
        'skip': 'Skip to content',
        'menu': 'Menu',
        'foot_templates': 'Templates',
        'foot_examples': 'Examples',
        'foot_guides': 'Guides',
        'foot_site': 'Site',
        'foot_all_templates': 'All sixteen',
        'foot_editor': 'Editor',
        'foot_about': 'About',
        'foot_privacy': 'Privacy and cookies',
        'foot_imprint': 'Imprint and contact',
        'foot_cookies': 'Cookie settings',
        'foot_blurb': ('A resume editor that runs entirely in your browser. Nothing you '
                       'type is uploaded, stored or sold. The PDF export is free and '
                       'always will be.'),
        'foot_legal': ('© %s %s. Operated by %s. This site is paid for by advertising; '
                       'the editor itself carries none.'),
        'date_fmt': '%d %B %Y',
        'cta_head': 'Now put it on a page',
        'cta_text': ('The editor opens with a filled-in example. Replace the text, pick a '
                     'layout, print to PDF. Nothing is uploaded and nothing costs anything.'),
        'resume_word': 'resume',
    },
    'de': {
        'code': 'de',
        'name': 'Deutsch',
        'other': 'en',
        'home': 'de/index.html',
        'editor': 'editor.html?lang=de',
        'templates': 'de/lebenslauf-vorlagen.html',
        'template_dir': 'de/vorlagen/',
        'guides': 'de/ratgeber/index.html',
        'guide_dir': 'de/ratgeber/',
        'examples': 'de/muster/index.html',
        'example_dir': 'de/muster/',
        'about': 'de/ueber-uns.html',
        'privacy': 'de/datenschutz.html',
        'imprint': 'de/impressum.html',
        'nav': [('templates', 'Vorlagen'), ('examples', 'Muster'),
                ('guides', 'Ratgeber'), ('about', 'Über uns')],
        'cta': 'Editor öffnen',
        'switch': 'English',
        'crumb_home': 'Start',
        'crumb_guides': 'Ratgeber',
        'crumb_examples': 'Muster',
        'crumb_templates': 'Vorlagen',
        'min_read': '%d Minuten Lesezeit',
        'updated': 'Aktualisiert %s',
        'written_by': 'Von der %s-Redaktion',
        'read_next': 'Weiterlesen',
        'another_example': 'Noch ein Muster',
        'more_guides': 'Mehr Ratgeber',
        'every_guide': 'Alle Ratgeber',
        'every_example': 'Alle Muster',
        'all_examples': 'Alle Muster ansehen',
        'faq_heading': 'Häufige Fragen',
        'start_here': 'Hier anfangen',
        'skip': 'Zum Inhalt springen',
        'menu': 'Menü',
        'foot_templates': 'Vorlagen',
        'foot_examples': 'Muster',
        'foot_guides': 'Ratgeber',
        'foot_site': 'Seite',
        'foot_all_templates': 'Alle sechzehn',
        'foot_editor': 'Editor',
        'foot_about': 'Über uns',
        'foot_privacy': 'Datenschutz',
        'foot_imprint': 'Impressum und Kontakt',
        'foot_cookies': 'Cookie-Einstellungen',
        'foot_blurb': ('Ein Lebenslauf-Editor, der vollständig im Browser läuft. Nichts, '
                       'was Sie eintippen, wird hochgeladen, gespeichert oder verkauft. '
                       'Der PDF-Export ist kostenlos und bleibt es.'),
        'foot_legal': ('© %s %s. Betrieben von %s. Diese Seite finanziert sich über '
                       'Werbung; der Editor selbst enthält keine.'),
        'date_fmt': '%d. %B %Y',
        'cta_head': 'Jetzt auf die Seite bringen',
        'cta_text': ('Der Editor startet mit einem ausgefüllten Beispiel. Text ersetzen, '
                     'Layout wählen, als PDF drucken. Nichts wird hochgeladen, nichts '
                     'kostet etwas.'),
        'resume_word': 'Lebenslauf',
    },
}

MONTHS_DE = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli',
             'August', 'September', 'Oktober', 'November', 'Dezember']


def pretty_date(iso, lang):
    d = datetime.date.fromisoformat(iso)
    if lang == 'de':
        return '%d. %s %d' % (d.day, MONTHS_DE[d.month - 1], d.year)
    return d.strftime('%d %B %Y').lstrip('0')


def topbar(active, depth, lang='en'):
    u = up(depth)
    L = LANGS[lang]
    other = LANGS[L['other']]
    links = []
    for key, label in L['nav']:
        current = ' aria-current="page"' if key == active else ''
        links.append('      <a href="%s%s"%s>%s</a>' % (u, L[key], current, label))
    links.append('      <a class="lang" href="%s%s" hreflang="%s" lang="%s">%s</a>'
                 % (u, other['home'], other['code'], other['code'], L['switch']))
    return '\n'.join([
        '<header class="topbar">',
        '  <div class="wrap">',
        '    <a class="wordmark" href="%s%s">Plain<b>Sheet</b></a>' % (u, L['home']),
        '    <button class="navtoggle" type="button" aria-expanded="false" '
        'aria-controls="nav" aria-label="%s" onclick="var n=document.getElementById(\'nav\');'
        'n.classList.toggle(\'open\');this.setAttribute(\'aria-expanded\',n.classList.contains(\'open\'))">'
        % L['menu'],
        '      <svg viewBox="0 0 18 14" aria-hidden="true"><path d="M0 1h18M0 7h18M0 13h18" '
        'stroke="currentColor" stroke-width="1.6"/></svg>',
        '    </button>',
        '    <nav class="topnav" id="nav">',
        '\n'.join(links),
        '      <a class="btn" href="%s%s">%s</a>' % (u, L['editor'], L['cta']),
        '    </nav>',
        '  </div>',
        '</header>',
    ])


def crumbs(trail, depth):
    """trail: list of (href_or_None, label). The last item is the current page."""
    u = up(depth)
    items, ld = [], []
    for i, (href, label) in enumerate(trail):
        if href:
            items.append('<li><a href="%s%s">%s</a></li>' % (u, href, esc(label)))
        else:
            items.append('<li>%s</li>' % esc(label))
        entry = {'@type': 'ListItem', 'position': i + 1, 'name': label}
        if href:
            entry['item'] = '%s/%s' % (DOMAIN, href)
        ld.append(entry)
    schema = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': ld}
    return ('<nav class="crumbs" aria-label="Breadcrumb"><div class="wrap"><ol>%s</ol></div></nav>'
            '\n<script type="application/ld+json">%s</script>'
            % (''.join(items), json.dumps(schema, separators=(',', ':'))))


def ad(slot, wrapped=True):
    box = ('  <div class="ad" data-slot="%s">\n'
           '    <!-- Filled by assets/ads.js. The wrapper reserves its height so the\n'
           '         page does not jump when an ad arrives. -->\n'
           '  </div>' % slot)
    if not wrapped:
        return box
    return '<div class="wrap">\n%s\n</div>' % box


def cta(depth, heading=None, text=None, label=None, href=None, lang='en'):
    L = LANGS[lang]
    return ('<div class="cta">\n  <div>\n    <h3>%s</h3>\n    <p>%s</p>\n  </div>\n'
            '  <a class="btn" href="%s%s">%s</a>\n</div>'
            % (heading or L['cta_head'], text or L['cta_text'],
               up(depth), href or L['editor'], label or L['cta']))


def footer(depth, lang='en'):
    u = up(depth)
    L = LANGS[lang]
    guides = content.for_lang(lang).GUIDES
    examples = content.for_lang(lang).EXAMPLES
    names = TEMPLATE_COPY[lang]

    def li(href, label):
        return '<li><a href="%s%s">%s</a></li>' % (u, href, esc(label))

    return '\n'.join([
        '<footer>',
        '  <div class="wrap">',
        '    <div class="cols five">',
        '      <div>',
        '        <a class="wordmark" href="%s%s">Plain<b>Sheet</b></a>' % (u, L['home']),
        '        <p class="fine">%s</p>' % L['foot_blurb'],
        '      </div>',
        '      <div>',
        '        <h3>%s</h3>' % L['foot_templates'],
        '        <ul>%s%s</ul>' % (
            ''.join(li(L['template_dir'] + t['slug'] + '.html', names[t['tid']]['name'])
                    for t in TEMPLATES[:6]),
            li(L['templates'], L['foot_all_templates'])),
        '      </div>',
        '      <div>',
        '        <h3>%s</h3>' % L['foot_examples'],
        '        <ul>%s%s</ul>' % (
            ''.join(li(L['example_dir'] + e['slug'] + '.html', e['role'])
                    for e in examples[:5]),
            li(L['examples'], L['every_example'])),
        '      </div>',
        '      <div>',
        '        <h3>%s</h3>' % L['foot_guides'],
        '        <ul>%s%s</ul>' % (
            ''.join(li(L['guide_dir'] + g['slug'] + '.html', g['short'])
                    for g in guides[:6]),
            li(L['guides'], L['every_guide'])),
        '      </div>',
        '      <div>',
        '        <h3>%s</h3>' % L['foot_site'],
        '        <ul>',
        '          ' + li(L['editor'], L['foot_editor']),
        '          ' + li(L['about'], L['foot_about']),
        '          ' + li(L['privacy'], L['foot_privacy']),
        '          ' + li(L['imprint'], L['foot_imprint']),
        '          <li><button type="button" class="lnk" data-consent-settings>%s</button></li>'
        % L['foot_cookies'],
        '        </ul>',
        '      </div>',
        '    </div>',
        '    <p class="fine">%s</p>'
        % (L['foot_legal'] % (datetime.date.today().year, BRAND,
                              esc(CFG['operator'] or '[your name]'))),
        '  </div>',
        '</footer>',
        '</body>',
        '</html>',
    ])


def write(path, html):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with io.open(full, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(html.rstrip() + '\n')
    return path


# ---------------------------------------------------------------- pieces

def toc(body, lang='en'):
    """Build a table of contents from the h2 landmarks in an article."""
    heads = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body, re.S)
    if len(heads) < 3:
        return ''
    items = ''.join('<li><a href="#%s">%s</a></li>' % (i, re.sub(r'<[^>]+>', '', t))
                    for i, t in heads)
    label = 'Auf dieser Seite' if lang == 'de' else 'On this page'
    return ('<aside class="toc"><strong>%s</strong><ol>%s</ol></aside>' % (label, items))


def inject_mid_ad(body, slot):
    """Put an ad before whichever h2 sits nearest the middle of the article."""
    positions = [m.start() for m in re.finditer(r'<h2 id=', body)]
    if len(positions) < 4:
        return body
    middle = len(body) / 2
    cut = min(positions[1:-1], key=lambda p: abs(p - middle))
    return body[:cut] + ad('guide-' + slot, wrapped=False) + '\n\n' + body[cut:]


# Welches Symbol zu welcher Seite gehört. Ein Ratgeber über Anschreiben bekommt
# den Umschlag, ein Muster für die Pflege das Stethoskop — das Symbol sagt schon
# im Kartenraster, worum es geht, bevor man die Überschrift gelesen hat.
GUIDE_ICON = {
    # Englische Ratgeber
    'how-to-write-a-resume': 'klemmbrett',
    'resume-summary': 'person',
    'resume-skills-section': 'zahnrad',
    'resume-bullet-points': 'stern',
    'resume-length': 'blatt',
    'resume-file-format': 'drucker',
    'ats-friendly-resume': 'lupe',
    'resume-mistakes': 'schild',
    'cover-letter': 'umschlag',
    'career-change-resume': 'aktentasche',
    'first-resume-no-experience': 'hut',
    'lebenslauf-german-resume': 'globus',
    # Deutsche Ratgeber
    'lebenslauf-schreiben': 'klemmbrett',
    'anschreiben': 'umschlag',
    'bewerbungsfoto': 'kamera',
    'arbeitszeugnis': 'urkunde',
    'lebenslauf-luecken': 'kalender',
    'quereinstieg': 'aktentasche',
    'bewerbung-per-email': 'blatt',
    'bewerbung-usa-uk': 'globus',
}

EXAMPLE_ICON = {
    'nurse': 'stethoskop',
    'software-developer': 'code',
    'project-manager': 'klemmbrett',
    'teacher': 'buch',
    'accountant': 'rechner',
    'sales-representative': 'handschlag',
    'warehouse-logistics': 'karton',
    'administrative-assistant': 'aktentasche',
    'pflegefachkraft': 'stethoskop',
    'softwareentwickler': 'code',
    'lagerlogistik': 'karton',
    'bueromanagement': 'aktentasche',
}


def ic(name, extra=''):
    """One icon. aria-hidden, because it repeats what the heading already says."""
    return '<span class="sym sym-%s%s" aria-hidden="true"></span>' % (
        name, (' ' + extra) if extra else '')


def guide_card(g, depth, lang='en', sideways=False):
    """sideways=True when the card already sits in the guides folder."""
    href = ('%s.html' % g['slug']) if sideways else (
        up(depth) + LANGS[lang]['guide_dir'] + g['slug'] + '.html')
    return ('<a class="card" href="%s">'
            '%s'
            '<span class="tag">%s</span>'
            '<h3>%s</h3>'
            '<p>%s</p>'
            '<span class="mins">%s</span></a>'
            % (href, ic(GUIDE_ICON.get(g['slug'], 'buch')), esc(g['tag']), esc(g['h1']),
               esc(g['dek'].split('.')[0] + '.'), LANGS[lang]['min_read'] % g['minutes']))


def template_tile(t, depth, lang='en'):
    copy = TEMPLATE_COPY[lang][t['tid']]
    return ('<a class="tile" href="%s%s%s.html"><div class="sheet">%s</div>'
            '<h3>%s</h3><span>%s</span></a>'
            % (up(depth), LANGS[lang]['template_dir'], t['slug'], t['svg'],
               esc(copy['name']), esc(copy['tagline'])))


def faq_block(pairs):
    if not pairs:
        return '', None
    rows = ''.join('<div><h3>%s</h3><p>%s</p></div>' % (esc(q), a) for q, a in pairs)
    ld = {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        'mainEntity': [{
            '@type': 'Question',
            'name': q,
            'acceptedAnswer': {'@type': 'Answer', 'text': re.sub(r'<[^>]+>', '', a)},
        } for q, a in pairs],
    }
    return '<div class="faq">%s</div>' % rows, ld


# ---------------------------------------------------------------- pages

def page_index():
    """The landing page. It has one job: say what this is and show it."""
    depth = 0
    faq, faq_ld = faq_block([
        ('Is it really free?',
         'Yes. The export is your browser printing to PDF, so there is nothing for us to '
         'charge for and no watermark to remove. Advertising on the pages around the editor '
         'pays for the site.'),
        ('Do I need an account?',
         'No. There is no sign-up because there is no server storing anything. Use Save file '
         'to keep a copy on your own machine and open it again later.'),
        ('Will it get through an applicant tracking system?',
         'Single-column layouts such as Plainfield and Linden parse most reliably. Sidebar '
         'layouts look better to a human but can confuse parsers that read across columns.'),
        ('Where is my data?',
         'In your browser, on your device. The editor keeps a working draft locally so a '
         'closed tab does not lose your work, and that draft never leaves the machine.'),
        ('Can I get a Word file?',
         'Yes, though Word receives a simplified table version. Diagonals and round photos '
         'are beyond what Word draws reliably.'),
    ])
    software_ld = {
        '@context': 'https://schema.org',
        '@type': 'SoftwareApplication',
        'name': BRAND,
        'applicationCategory': 'BusinessApplication',
        'operatingSystem': 'Any browser',
        'url': DOMAIN + '/editor.html',
        'description': 'A free resume builder that runs entirely in the browser, with '
                       'sixteen A4 layouts and a free PDF export.',
        'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'EUR'},
    }

    return '\n'.join([
        head('Free resume builder — no account, no watermark | %s' % BRAND,
             'Write your resume in the browser and download the PDF free. Sixteen layouts, '
             'no sign-up, no watermark, and nothing you type is uploaded.',
             'index.html', depth, extra_ld=[software_ld, faq_ld],
             alternate={'de': 'de/index.html'}),
        topbar(None, depth),
        '',
        '<main id="main">',
        '<section class="hero">',
        '  <div class="wrap">',
        '    <h1>Build your resume in your browser. Free.</h1>',
        '    <p class="lead">Type into a live A4 page, pick one of sixteen layouts, and save '
        'the PDF. No account, no watermark, and nothing you write is uploaded anywhere.</p>',
        '    <div class="actions">',
        '      <a class="btn" href="editor.html">Start writing</a>',
        '      <a class="btn ghost" href="templates.html">See the layouts</a>',
        '    </div>',
        '    <p class="under"><b>Free</b> · no sign-up · works on any browser</p>',
        '    <div class="shot">',
        '      <img src="assets/hero-en.png" width="1500" height="827" alt="The editor: '
        'controls on the left, a live A4 page on the right." loading="eager">',
        '    </div>',
        '  </div>',
        '</section>',
        '',
        '<section class="facts">',
        '  <div class="wrap">',
        '    <div>' + ic('blatt') + '<strong>Nothing to pay</strong><p>The PDF is free at the end, not after a '
        'trial. There is no download button to put a price behind.</p></div>',
        '    <div>' + ic('schild') + '<strong>Nothing uploaded</strong><p>The editor is one page of code running '
        'on your machine. No server sees your employment history'
        + (', unless you ask the AI features to read or tailor it.' if CFG['ki'] else '.')
        + '</p></div>',
        '    <div>' + ic('raster') + '<strong>Sixteen layouts, one text</strong><p>Switch the design whenever you '
        'like. What you wrote stays where it is.</p></div>',
        '  </div>',
        '</section>',
        '',
        '<section class="band">',
        '  <div class="wrap">',
        '    <div class="band-head">',
        '      <h2>Pick a layout</h2>',
        '      <p>Each one is a finished A4 document. Single column parses most reliably '
        'through employer portals; a sidebar reads better when a person opens the PDF.</p>',
        '    </div>',
        '    <div class="grid">%s</div>' % ''.join(
            template_tile(t, depth) for t in TEMPLATES[:8]),
        '    <p style="margin-top:30px"><a href="templates.html">All sixteen layouts</a></p>',
        '  </div>',
        '</section>',
        '',
        ad('home-mid'),
        '',
        '<section class="band tight">',
        '  <div class="wrap">',
        '    <div class="band-head">',
        '      <h2>See a finished one</h2>',
        '      <p>A worked resume for eight occupations, with the reasoning: what the person '
        'hiring checks first, and which lines are worth their space.</p>',
        '    </div>',
        '    <div class="cards">%s</div>' % ''.join(
            example_card(e, depth) for e in content.EXAMPLES[:3]),
        '    <p style="margin-top:26px"><a href="examples/index.html">All eight examples</a></p>',
        '  </div>',
        '</section>',
        '',
        '<section class="band tight">',
        '  <div class="wrap">',
        '    <div class="band-head">',
        '      <h2>What to write on it</h2>',
        '      <p>The editor handles the layout. These handle the words, which is the part '
        'that decides whether anyone calls you.</p>',
        '    </div>',
        '    <div class="cards">%s</div>' % ''.join(
            guide_card(g, depth) for g in content.GUIDES[:3]),
        '    <p style="margin-top:26px"><a href="guides/index.html">All twelve guides</a></p>',
        '  </div>',
        '</section>',
        '',
        '<section class="band tight">',
        '  <div class="wrap">',
        '    <div class="band-head"><h2>Questions</h2></div>',
        '    ' + faq,
        '    ' + cta(depth),
        '  </div>',
        '</section>',
        '</main>',
        footer(depth),
    ])


def page_templates():
    depth = 0
    two_col = [t for t in TEMPLATES if t['specs'][0][1].lower().startswith('two')]
    one_col = [t for t in TEMPLATES if t not in two_col]
    ld = {
        '@context': 'https://schema.org',
        '@type': 'ItemList',
        'name': 'Resume templates',
        'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': t['name'],
             'url': '%s/templates/%s.html' % (DOMAIN, t['slug'])}
            for i, t in enumerate(TEMPLATES)],
    }
    return '\n'.join([
        head('Sixteen free resume templates — %s' % BRAND,
             'Sixteen A4 resume layouts: sidebar, single column, timeline, date column and '
             'more. Free PDF download, no account.',
             'templates.html', depth, extra_ld=[ld],
             alternate={'de': 'de/lebenslauf-vorlagen.html'}),
        topbar('templates', depth),
        crumbs([('index.html', 'Home'), (None, 'Templates')], depth),
        '<main id="main">',
        '<section class="band">',
        '  <div class="wrap">',
        '    <div class="band-head">',
        '      <h1 style="font-size:clamp(2rem,4vw,2.9rem)">Sixteen layouts</h1>',
        '      <p>Eight put your details in a sidebar, eight run in a single column. '
        'Single-column layouts are the safer choice when you upload through an employer '
        'portal; sidebar layouts read better when a person opens the PDF. Every one of them '
        'holds the same text, so switching later costs nothing.</p>',
        '    </div>',
        '    <h2 style="margin-bottom:22px">Two columns</h2>',
        '    <div class="grid">%s</div>' % ''.join(template_tile(t, depth) for t in two_col),
        '    <h2 style="margin:52px 0 22px">Single column</h2>',
        '    <div class="grid">%s</div>' % ''.join(template_tile(t, depth) for t in one_col),
        '  </div>',
        '</section>',
        ad('templates-foot'),
        '<section class="band tight">',
        '  <div class="wrap">',
        '    <div class="band-head"><h2>Which one should you pick?</h2></div>',
        '    <div class="cards">',
        '      <div class="card"><span class="tag">Employer portals</span>'
        '<h3>Single column, no graphics</h3><p>Plainfield, Linden and Hairline put everything '
        'in one reading order, which is what a parser handles best.</p>'
        '<span class="mins"><a href="guides/ats-friendly-resume.html">Why this matters</a>'
        '</span></div>',
        '      <div class="card"><span class="tag">A human reader</span>'
        '<h3>Sidebar layouts</h3><p>Aster, Verso and Broadsheet put contact details and skills '
        'where the eye rests, and leave the full width for your experience.</p>'
        '<span class="mins"><a href="guides/how-to-write-a-resume.html">What goes where</a>'
        '</span></div>',
        '      <div class="card"><span class="tag">DACH applications</span>'
        '<h3>A date column</h3><p>Ledger and Milestone follow the tabellarisch convention, '
        'with dates in their own column and room for a photo.</p>'
        '<span class="mins"><a href="guides/lebenslauf-german-resume.html">The Lebenslauf</a>'
        '</span></div>',
        '    </div>',
        '  </div>',
        '</section>',
        '</main>',
        footer(depth),
    ])


def page_template(t, lang='en'):
    depth = 2 if lang == 'de' else 1
    L = LANGS[lang]
    copy = TEMPLATE_COPY[lang][t['tid']]
    others = [x for x in TEMPLATES if x['slug'] != t['slug']][:4]
    path = L['template_dir'] + t['slug'] + '.html'
    ld = {
        '@context': 'https://schema.org',
        '@type': 'CreativeWork',
        'name': '%s %s template' % (copy['name'], L['resume_word']),
        'about': copy['tagline'],
        'url': '%s/%s' % (DOMAIN, path),
        'isAccessibleForFree': True,
        'inLanguage': lang,
        'creator': {'@type': 'Organization', 'name': BRAND},
    }
    specs = ''.join('<li><span>%s</span><span>%s</span></li>' % (esc(a), esc(b))
                    for a, b in copy['specs'])
    fits = ''.join('<li>%s</li>' % esc(f) for f in copy['fits'])
    other = LANGS[L['other']]
    alt = {lang: path,
           other['code']: other['template_dir'] + t['slug'] + '.html'}
    use = ('%s verwenden' % copy['name']) if lang == 'de' else ('Use %s' % copy['name'])
    kicker = 'Lebenslauf-Vorlage' if lang == 'de' else 'Resume template'
    more = 'Andere Layouts' if lang == 'de' else 'Other layouts'

    return '\n'.join([
        head(copy['title'], copy['description'], path, depth, extra_ld=[ld],
             lang=lang, alternate=alt),
        topbar('templates', depth, lang),
        crumbs([(L['home'], L['crumb_home']), (L['templates'], L['crumb_templates']),
                (None, copy['name'])], depth),
        '<main id="main">',
        '<section class="detail">',
        '  <div class="wrap">',
        '    <div class="sheet">%s</div>' % t['svg'],
        '    <div>',
        '      <p class="kicker">%s</p>' % kicker,
        '      <h1 style="font-size:clamp(2rem,4vw,2.8rem)">%s</h1>' % esc(copy['name']),
        '      <p class="lead">%s</p>' % esc(copy['tagline']),
        '      <p>%s</p>' % copy['body'],
        '      <h3 style="margin-top:26px">%s</h3>'
        % ('Passend, wenn' if lang == 'de' else 'Pick this one if'),
        '      <ul class="fits">%s</ul>' % fits,
        '      <a class="btn" href="%s%s%st=%s">%s</a>'
        % (up(depth), L['editor'], '&' if '?' in L['editor'] else '?', t['tid'], esc(use)),
        '      <ul class="specs">%s</ul>' % specs,
        '    </div>',
        '  </div>',
        '</section>',
        ad('template-mid'),
        '<section class="band tight">',
        '  <div class="wrap">',
        '    <div class="band-head"><h2>%s</h2></div>' % more,
        '    <div class="grid">%s</div>' % ''.join(
            template_tile(x, depth, lang) for x in others),
        '    <p style="margin-top:26px"><a href="%s%s">%s</a></p>'
        % (up(depth), L['templates'], L['foot_all_templates']),
        '  </div>',
        '</section>',
        '</main>',
        footer(depth, lang),
    ])


def page_guides_index(lang='en'):
    depth = 2 if lang == 'de' else 1
    L = LANGS[lang]
    guides = content.for_lang(lang).GUIDES
    tags = []
    for g in guides:
        if g['tag'] not in tags:
            tags.append(g['tag'])
    ld = {
        '@context': 'https://schema.org',
        '@type': 'ItemList',
        'name': 'Ratgeber' if lang == 'de' else 'Resume guides',
        'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': g['h1'],
             'url': '%s/%s%s.html' % (DOMAIN, L['guide_dir'], g['slug'])}
            for i, g in enumerate(guides)],
    }
    lead = guides[0]
    body = ['    <a class="feature" href="%s.html">'
            '<div>%s<span class="tag">%s</span><h3>%s</h3><p>%s</p></div>'
            '<span class="mins">%s</span></a>'
            % (lead['slug'], ic(GUIDE_ICON.get(lead['slug'], 'buch')), L['start_here'],
               esc(lead['h1']), esc(lead['dek']), L['min_read'] % lead['minutes'])]
    first = True
    for tag in tags:
        members = [g for g in guides if g['tag'] == tag and g is not lead]
        if not members:
            continue
        body.append('    <h2 style="margin:%s 0 20px">%s</h2>'
                    % ('0' if first else '54px', esc(tag)))
        body.append('    <div class="cards">%s</div>'
                    % ''.join(guide_card(g, depth, lang, sideways=True) for g in members))
        if not first and 'guides-mid' not in '\n'.join(body):
            body.append(ad('guides-mid', wrapped=False))
        first = False

    if lang == 'de':
        title = 'Ratgeber zur Bewerbung — %s' % BRAND
        desc = ('Acht Ratgeber zur Bewerbung im deutschsprachigen Raum: Lebenslauf, '
                'Anschreiben, Bewerbungsfoto, Arbeitszeugnis, Lücken und Quereinstieg.')
        h1 = 'Ratgeber'
        intro = ('Der Editor übernimmt das Layout. Hier geht es um den schwierigeren Teil: '
                 'was auf die Seite gehört, in welcher Reihenfolge, und woran eine Bewerbung '
                 'nach neun Sekunden scheitert. Ohne Anmeldung, ohne Kurs, ohne Verkauf am '
                 'Ende.')
    else:
        title = 'Resume guides — %s' % BRAND
        desc = ('Twelve plain guides to writing a resume: bullet points, skills, length, '
                'applicant tracking systems, cover letters and the German Lebenslauf.')
        h1 = 'Guides'
        intro = ('The editor takes care of the layout. These are about the harder part: what '
                 'to write on the page, in what order, and what gets a file put down after '
                 'nine seconds. No sign-up, no course, no upsell at the end.')

    return '\n'.join([
        head(title, desc, L['guides'], depth, extra_ld=[ld], lang=lang,
             alternate={'en': LANGS['en']['guides'], 'de': LANGS['de']['guides']}),
        topbar('guides', depth, lang),
        crumbs([(L['home'], L['crumb_home']), (None, L['crumb_guides'])], depth),
        '<main id="main">',
        '<section class="band">',
        '  <div class="wrap">',
        '    <div class="band-head">',
        '      <h1 style="font-size:clamp(2rem,4vw,2.9rem)">%s</h1>' % h1,
        '      <p>%s</p>' % intro,
        '    </div>',
        '\n'.join(body),
        '  </div>',
        '</section>',
        '<section class="band tight">',
        '  <div class="wrap">',
        cta(depth, lang=lang),
        '  </div>',
        '</section>',
        '</main>',
        footer(depth, lang),
    ])


def page_guide(g, lang='en'):
    depth = 2 if lang == 'de' else 1
    L = LANGS[lang]
    body = inject_mid_ad(g['body'].strip(), 'mid')
    faq, faq_ld = faq_block(g.get('faq'))
    path = L['guide_dir'] + g['slug'] + '.html'
    article_ld = {
        '@context': 'https://schema.org',
        '@type': 'Article',
        'headline': g['h1'],
        'description': g['description'],
        'datePublished': g['updated'],
        'dateModified': g['updated'],
        'inLanguage': lang,
        'mainEntityOfPage': '%s/%s' % (DOMAIN, path),
        'image': '%s/assets/og.png' % DOMAIN,
        'author': {'@type': 'Organization', 'name': BRAND,
                   'url': '%s/%s' % (DOMAIN, L['about'])},
        'publisher': {'@type': 'Organization', 'name': BRAND, 'url': DOMAIN + '/'},
    }
    others = content.for_lang(lang).GUIDES
    related = [x for x in others if x['slug'] in g.get('related', [])]

    return '\n'.join([
        head('%s — %s' % (g['title'], BRAND), g['description'], path, depth, kind='article',
             published=g['updated'], modified=g['updated'], lang=lang,
             extra_ld=[article_ld] + ([faq_ld] if faq_ld else [])),
        topbar('guides', depth, lang),
        crumbs([(L['home'], L['crumb_home']), (L['guides'], L['crumb_guides']),
                (None, g['short'])], depth),
        '<main id="main">',
        '<article class="article">',
        '  <div class="wrap">',
        '    <div class="article-head">',
        '      <p class="kicker">%s%s</p>' % (ic(GUIDE_ICON.get(g['slug'], 'buch')),
                                              esc(g['tag'])),
        '      <h1>%s</h1>' % esc(g['h1']),
        '      <p class="lead">%s</p>' % esc(g['dek']),
        '      <p class="article-meta"><span>%s</span><span>%s</span><span>%s</span></p>'
        % (L['min_read'] % g['minutes'], L['updated'] % pretty_date(g['updated'], lang),
           L['written_by'] % BRAND),
        '    </div>',
        ad('guide-top', wrapped=False),
        '    <div class="article-cols">',
        '      <div class="article-body">',
        body,
        cta(depth, lang=lang),
        ad('guide-foot', wrapped=False),
        ('        <h2 id="faq">%s</h2>\n' % L['faq_heading'] + faq) if faq else '',
        '        <div class="nextprev">%s</div>' % ''.join(
            '<a href="%s.html"><span>%s</span><strong>%s</strong></a>'
            % (x['slug'], L['read_next'], esc(x['h1'])) for x in related[:2]),
        '      </div>',
        toc(g['body'], lang),
        '    </div>',
        '  </div>',
        '</article>',
        '<section class="band tight">',
        '  <div class="wrap">',
        '    <div class="band-head"><h2>%s</h2></div>' % L['more_guides'],
        '    <div class="cards">%s</div>' % ''.join(
            guide_card(x, depth, lang, sideways=True) for x in related),
        '    <p style="margin-top:26px"><a href="index.html">%s</a></p>' % L['every_guide'],
        '  </div>',
        '</section>',
        '</main>',
        footer(depth, lang),
    ])


def page_about():
    depth = 0
    return '\n'.join([
        head('About %s' % BRAND, 'Who makes this resume builder, how it is paid for, and '
             'what it does with your data — which is nothing.',
             'about.html', depth, alternate={'de': LANGS['de']['about']}),
        topbar('about', depth),
        crumbs([('index.html', 'Home'), (None, 'About')], depth),
        '<main id="main">',
        '<section class="band">',
        '  <div class="wrap prose">',
        '    <h1 style="font-size:clamp(2rem,4vw,2.8rem)">About this site</h1>',
        '    <p class="lead">A resume editor that runs in your browser, sixteen layouts to '
        'start from, and twelve guides about what to write. Free, and free in the ordinary '
        'sense: no trial, no account, no watermark on the export.</p>',
        '',
        '    <h2>Why it works this way</h2>',
        '    <p>Almost every resume builder online follows the same pattern. You type your '
        'employment history into a form, you watch a preview build, and at the download button '
        'you meet the price. The work is done, the page is finished, and the only way to get '
        'it out is a subscription that renews.</p>',
        '    <p>This one has no download button to put a price behind, because the export is '
        'your browser printing to PDF. There is no server that could hold your document '
        'hostage, because there is no server: the editor is one HTML file, and everything you '
        'type stays in the tab you typed it into.</p>',
        '',
        '    <h2>How it is paid for</h2>',
        '    <p>Advertising, on the pages around the editor — the home page, the template '
        'gallery and the guides. The editor itself carries no advertising and will not. '
        'Someone spends twenty minutes in there and produces a single page view, so ads in '
        'the editor would earn almost nothing while making the tool worse to use.</p>',
        '    <p>Ads load only if you agree to them. If you decline, no advertising script is '
        'requested at all, and the site works exactly as it does otherwise. You can change '
        'that decision from the <button type="button" class="lnk" data-consent-settings '
        'style="background:none;border:0;padding:0;font:inherit;color:var(--accent);'
        'text-decoration:underline;cursor:pointer">cookie settings</button> link in the footer '
        'of any page.</p>',
        '',
        '    <h2>What happens to your resume</h2>',
        '    <p>Nothing. It is not uploaded, not stored on a server, not backed up and not '
        'seen by us. The editor keeps a working draft in your own browser so that closing the '
        'tab by accident does not lose an hour of work, and that draft stays on your device '
        'until you clear it. The <a href="privacy.html">privacy notice</a> sets out the '
        'detail, including what the ad network does if you allow it.</p>',
        '',
        '    <h2>Who writes the guides</h2>',
        '    <p>We do — they are written for this site rather than assembled from elsewhere, '
        'and they say what we would tell a friend rather than what performs well as a list. '
        'Where the advice differs by country, they say so, because most resume advice online '
        'is written for one market and silently applied to all of them.</p>',
        '    <p>If something in a guide is wrong, out of date, or missing the case you are in, '
        'write to us. Corrections get made and the update date on the article changes.</p>',
        '',
        '    <h2>Contact</h2>',
        '    <p>Questions, corrections and bug reports: <a href="imprint.html">see the imprint '
        'and contact page</a>.</p>',
        '  </div>',
        '</section>',
        '</main>',
        footer(depth),
    ])


def page_imprint():
    depth = 0
    return '\n'.join([
        head('Imprint and contact — %s' % BRAND,
             'Who is responsible for this site, and how to get in touch.',
             'imprint.html', depth, alternate={'de': LANGS['de']['imprint']}),
        topbar(None, depth),
        crumbs([('index.html', 'Home'), (None, 'Imprint')], depth),
        '<main id="main">',
        '<section class="band">',
        '  <div class="wrap prose">',
        '    <h1 style="font-size:clamp(2rem,4vw,2.8rem)">Imprint and contact</h1>',
        '    <div class="callout warn"><strong>Fill this in before you publish</strong>',
        '    <p>Germany, Austria and Switzerland require an imprint with a name, a postal '
        'address and a way to contact the operator directly. An email address alone is not '
        'enough, and the requirement applies to a hobby site carrying advertising. The '
        'placeholders below mark what has to be replaced; the operator name and email come '
        'from <code>assets/site-config.js</code>.</p></div>',
        '',
        '    <h2>Responsible for this site</h2>',
        '    <p>%s<br>[Street and number]<br>[Postcode and town]<br>[Country]</p>'
        % esc(CFG['operator'] or '[Name]'),
        '',
        '    <h2>Contact</h2>',
        '    <p>Email: %s<br>Telephone: [number]</p>' % esc(CFG['email'] or '[you@example.com]'),
        '    <p>We read everything sent to that address. Corrections to a guide are welcome '
        'and get made.</p>',
        '',
        '    <h2>VAT and registration</h2>',
        '    <p>[VAT identification number, if you have one]<br>'
        '[Commercial register and number, if the operator is a company]</p>',
        '',
        '    <h2>Responsible for the content</h2>',
        '    <p>[Name and address of the person responsible for editorial content, where your '
        'jurisdiction requires it separately]</p>',
        '',
        '    <h2>Dispute resolution</h2>',
        '    <p>The European Commission provides a platform for online dispute resolution at '
        '<a href="https://ec.europa.eu/consumers/odr" rel="nofollow noopener">'
        'ec.europa.eu/consumers/odr</a>. We are neither obliged nor willing to take part in '
        'dispute resolution proceedings before a consumer arbitration board.</p>',
        '',
        '    <h2>Liability for links</h2>',
        '    <p>This site links to external sites over whose content we have no control. '
        'Responsibility for that content rests with its operators. Links were checked for '
        'obvious legal problems at the time they were added.</p>',
        '  </div>',
        '</section>',
        '</main>',
        footer(depth),
    ])


def page_404():
    depth = 0
    return '\n'.join([
        head('Page not found — %s' % BRAND,
             'That page does not exist. The editor, the templates and the guides are all '
             'one click away.', '404.html', depth, noindex=True),
        topbar(None, depth),
        '<main id="main">',
        '<section class="band mid">',
        '  <div class="wrap">',
        '    <p class="kicker">Error 404</p>',
        '    <h1 style="font-size:clamp(2rem,4vw,3rem)">That page is not here</h1>',
        '    <p class="lead">It may have been renamed, or the link that sent you here may be '
        'older than the site. Everything is still one click away.</p>',
        '    <div class="actions">',
        '      <a class="btn" href="/editor.html">Open the editor</a>',
        '      <a class="btn ghost" href="/templates.html">Browse the layouts</a>',
        '      <a class="btn ghost" href="/guides/index.html">Read the guides</a>',
        '    </div>',
        '  </div>',
        '</section>',
        '</main>',
        footer(depth),
    ])


def example_card(e, depth, lang='en', sideways=False):
    href = ('%s.html' % e['slug']) if sideways else (
        up(depth) + LANGS[lang]['example_dir'] + e['slug'] + '.html')
    return ('<a class="card" href="%s">'
            '%s'
            '<span class="tag">%s</span>'
            '<h3>%s</h3>'
            '<p>%s</p>'
            '<span class="mins">%s</span></a>'
            % (href, ic(EXAMPLE_ICON.get(e['slug'], 'aktentasche')), esc(e['field']),
               esc(e['role']), esc(e['dek'].split('.')[0] + '.'),
               LANGS[lang]['min_read'] % e['minutes']))


SAMPLE_LABELS = {
    'en': ('Summary', 'Experience', 'Skills', 'Education'),
    'de': ('Kurzprofil', 'Berufserfahrung', 'Kenntnisse', 'Ausbildung'),
}


def sample_block(s, lang='en'):
    """The worked resume, marked up so it reads as a document rather than a quote."""
    lbl = SAMPLE_LABELS[lang]
    jobs = []
    for job in s['jobs']:
        jobs.append('<div class="role"><strong>%s</strong><span>%s</span></div>'
                    '<p class="where">%s</p><ul>%s</ul>'
                    % (esc(job['title']), esc(job['dates']), esc(job['employer']),
                       ''.join('<li>%s</li>' % esc(b) for b in job['bullets'])))
    return ('<div class="sample">'
            '<div class="who"><h3>%s</h3><p>%s</p></div>'
            '<h4>%s</h4><p class="line">%s</p>'
            '<h4>%s</h4>%s'
            '<h4>%s</h4><p class="line">%s</p>'
            '<h4>%s</h4><p class="line">%s</p>'
            '</div>'
            % (esc(s['name']), esc(s['headline']),
               lbl[0], esc(s['summary']), lbl[1], ''.join(jobs),
               lbl[2], esc(s['skills']), lbl[3], s['education']))


def page_example(e, lang='en'):
    depth = 2 if lang == 'de' else 1
    L = LANGS[lang]
    de = lang == 'de'
    faq, faq_ld = faq_block(e.get('faq'))
    path = L['example_dir'] + e['slug'] + '.html'
    ld = {
        '@context': 'https://schema.org',
        '@type': 'Article',
        'headline': ('Lebenslauf Muster: %s' if de else '%s resume example') % e['role'],
        'description': e['description'],
        'datePublished': e['updated'],
        'dateModified': e['updated'],
        'inLanguage': lang,
        'mainEntityOfPage': '%s/%s' % (DOMAIN, path),
        'image': '%s/assets/og.png' % DOMAIN,
        'author': {'@type': 'Organization', 'name': BRAND,
                   'url': '%s/%s' % (DOMAIN, L['about'])},
        'publisher': {'@type': 'Organization', 'name': BRAND, 'url': DOMAIN + '/'},
    }
    scans = ''.join('<li>%s</li>' % esc(x) for x in e['scans'])
    weak = 'Sagt wenig' if de else 'Says little'
    strong = 'Dieselbe Aussage, brauchbar' if de else 'Says the same thing, usefully'
    pairs = ''.join(
        '<div class="compare"><div class="bad"><h4>%s</h4><p>%s</p></div>'
        '<div class="good"><h4>%s</h4><p>%s</p></div></div>'
        % (weak, esc(a), strong, esc(b)) for a, b in e['pairs'])
    layouts = ''.join(
        '<li><a href="%s%s%s.html">%s</a> — %s</li>'
        % (up(depth), L['template_dir'], BY_ID[tid]['slug'],
           esc(TEMPLATE_COPY[lang][tid]['name']), esc(why)) for tid, why in e['templates'])
    guides = [g for g in content.for_lang(lang).GUIDES if g['slug'] in e['guides']]
    others = [x for x in content.for_lang(lang).EXAMPLES if x['slug'] != e['slug']][:3]

    heads = [
        ('scans', 'Was zuerst geprüft wird' if de else 'What gets looked at first'),
        ('example', 'Das Muster' if de else 'The example'),
        ('lines', 'Warum diese Zeilen und nicht die üblichen' if de
                  else 'Why those lines and not the usual ones'),
        ('layout', 'Welches Layout dazu passt' if de else 'Which layout suits it'),
        ('faq', L['faq_heading']),
    ]

    return '\n'.join([
        head('%s — %s' % (e['title'], BRAND), e['description'], path, depth, kind='article',
             published=e['updated'], modified=e['updated'], lang=lang,
             extra_ld=[ld] + ([faq_ld] if faq_ld else [])),
        topbar('examples', depth, lang),
        crumbs([(L['home'], L['crumb_home']), (L['examples'], L['crumb_examples']),
                (None, e['role'])], depth),
        '<main id="main">',
        '<article class="article">',
        '  <div class="wrap">',
        '    <div class="article-head">',
        '      <p class="kicker">%s%s · %s</p>'
        % (ic(EXAMPLE_ICON.get(e['slug'], 'aktentasche')), esc(e['field']),
           'Muster-Lebenslauf' if de else 'Resume example'),
        '      <h1>%s</h1>' % esc(e['role']),
        '      <p class="lead">%s</p>' % esc(e['dek']),
        '      <p class="article-meta"><span>%s</span><span>%s</span><span>%s</span></p>'
        % (L['min_read'] % e['minutes'], L['updated'] % pretty_date(e['updated'], lang),
           L['written_by'] % BRAND),
        '    </div>',
        ad('example-top', wrapped=False),
        '    <div class="article-cols">',
        '      <div class="article-body">',
        '<h2 id="scans">%s</h2>' % heads[0][1],
        ('<p>Bevor jemand einen Satz liest, wird geprüft, ob Sie die Hürde überhaupt nehmen. '
         'Für diese Stelle heißt das:</p>' if de else
         '<p>Before anyone reads a sentence, they check whether you clear the bar. For this '
         'role that means:</p>'),
        '<ul>%s</ul>' % scans,
        ('<p>Alles auf der Seite darunter beantwortet einen dieser Punkte — oder es steht '
         'nicht da.</p>' if de else
         '<p>Everything on the page below is there to answer one of those, or it is not '
         'there.</p>'),
        '',
        '<h2 id="example">%s</h2>' % heads[1][1],
        ('<p>Erfunden, aber so gebaut, wie ein gutes aussieht. Einmal für die Form lesen, '
         'dann die Anmerkungen darunter.</p>' if de else
         '<p>Invented, but built the way a good one is. Read it once for the shape, then '
         'read the notes underneath.</p>'),
        sample_block(e['sample'], lang),
        ad('example-mid', wrapped=False),
        '',
        '<h2 id="lines">%s</h2>' % heads[2][1],
        ('<p>Jede schwache Fassung unten ist ein Satz, der tausendfach in Lebensläufen '
         'steht. Für die rechte Spalte wurde nichts erfunden — dieselben Tatsachen sind '
         'nur ausgesprochen.</p>' if de else
         '<p>Every weak version below is a real sentence that appears on thousands of '
         'resumes. Nothing was invented to fix them — the same facts are simply stated.</p>'),
        pairs,
        ('<p>Das Muster ist das aus dem <a href="%s%slebenslauf-schreiben.html">Ratgeber zum '
         'Lebenslauf</a>: was Sie getan haben, wie, und was sich dadurch geändert hat.</p>'
         % (up(depth), L['guide_dir']) if de else
         '<p>The pattern is the one from <a href="%s%sresume-bullet-points.html">the bullet '
         'points guide</a>: what you did, how you did it, and what changed as a result.</p>'
         % (up(depth), L['guide_dir'])),
        '',
        '<h2 id="layout">%s</h2>' % heads[3][1],
        '<ul>%s</ul>' % layouts,
        ('<p>Beide öffnen sich im Editor mit dem Beispieltext, den Sie überschreiben. Nichts '
         'wird hochgeladen, und das PDF kostet nichts.</p>' if de else
         '<p>Either opens in the editor with the sample text in place, which you then type '
         'over. Nothing is uploaded and the PDF costs nothing.</p>'),
        cta(depth, lang=lang,
            heading='Mit diesem Muster anfangen' if de else 'Start from this example',
            text=('Editor öffnen, den Beispieltext durch Ihren ersetzen, als PDF drucken. '
                  'Sechzehn Layouts, keine Anmeldung, nichts verlässt Ihren Browser.') if de
                 else ('Open the editor, replace the sample text with yours, and print to '
                       'PDF. Sixteen layouts, no account, nothing leaves your browser.')),
        ad('example-foot', wrapped=False),
        ('<h2 id="faq">%s</h2>\n' % L['faq_heading'] + faq) if faq else '',
        '        <div class="nextprev">%s</div>' % ''.join(
            '<a href="%s.html"><span>%s</span><strong>%s</strong></a>'
            % (x['slug'], L['another_example'], esc(x['role'])) for x in others[:2]),
        '      </div>',
        toc(''.join('<h2 id="%s">%s</h2>' % (i, t) for i, t in heads), lang),
        '    </div>',
        '  </div>',
        '</article>',
        '<section class="band tight">',
        '  <div class="wrap">',
        '    <div class="band-head"><h2>%s</h2></div>' % L['read_next'],
        '    <div class="cards">%s</div>' % ''.join(
            guide_card(g, depth, lang) for g in guides),
        '  </div>',
        '</section>',
        '</main>',
        footer(depth, lang),
    ])


def page_examples_index(lang='en'):
    depth = 2 if lang == 'de' else 1
    L = LANGS[lang]
    de = lang == 'de'
    examples = content.for_lang(lang).EXAMPLES
    ld = {
        '@context': 'https://schema.org',
        '@type': 'ItemList',
        'name': 'Muster-Lebensläufe nach Beruf' if de else 'Resume examples by occupation',
        'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1,
             'name': ('Lebenslauf Muster: %s' if de else '%s resume example') % e['role'],
             'url': '%s/%s%s.html' % (DOMAIN, L['example_dir'], e['slug'])}
            for i, e in enumerate(examples)],
    }
    fields = []
    for e in examples:
        if e['field'] not in fields:
            fields.append(e['field'])
    body = []
    for i, field in enumerate(fields):
        members = [e for e in examples if e['field'] == field]
        body.append('    <h2 style="margin:%s 0 20px">%s</h2>'
                    % ('0' if i == 0 else '54px', esc(field)))
        body.append('    <div class="cards">%s</div>'
                    % ''.join(example_card(e, depth, lang, sideways=True) for e in members))
        if i == 1:
            body.append(ad('examples-mid', wrapped=False))

    if de:
        title = 'Muster-Lebensläufe nach Beruf — %s' % BRAND
        desc = ('Fertige Muster-Lebensläufe für vier Berufe, jeweils mit der Begründung: '
                'was zuerst geprüft wird und welche Zeilen ihren Platz verdienen.')
        h1 = 'Muster'
        intro = ('Ein fertiger Lebenslauf für mehrere Berufe, mit der Begründung daneben: '
                 'was die einstellende Person prüft, bevor sie einen Satz liest, welche '
                 'Zeilen Gewicht haben, und welche üblichen Formulierungen sie ersetzen. '
                 'Erfundene Personen, echter Aufbau.')
    else:
        title = 'Resume examples by occupation — %s' % BRAND
        desc = ('Worked resume examples for eight occupations, each with the reasoning: what '
                'gets scanned for first and which lines earn their space.')
        h1 = 'Examples'
        intro = ('A finished resume for eight occupations, with the reasoning written out: '
                 'what the person hiring checks before reading a sentence, which lines carry '
                 'weight, and the usual phrasing they replace. Invented people, real '
                 'structure.')

    return '\n'.join([
        head(title, desc, L['examples'], depth, extra_ld=[ld], lang=lang,
             alternate={'en': LANGS['en']['examples'], 'de': LANGS['de']['examples']}),
        topbar('examples', depth, lang),
        crumbs([(L['home'], L['crumb_home']), (None, L['crumb_examples'])], depth),
        '<main id="main">',
        '<section class="band">',
        '  <div class="wrap">',
        '    <div class="band-head">',
        '      <h1 style="font-size:clamp(2rem,4vw,2.9rem)">%s</h1>' % h1,
        '      <p>%s</p>' % intro,
        '    </div>',
        '\n'.join(body),
        '  </div>',
        '</section>',
        '<section class="band tight">',
        '  <div class="wrap">',
        cta(depth, lang=lang),
        '  </div>',
        '</section>',
        '</main>',
        footer(depth, lang),
    ])


def page_index_de():
    depth = 1
    L = LANGS['de']
    faq, faq_ld = faq_block([
        ('Ist es wirklich kostenlos?',
         'Ja. Der Export ist der Druck-nach-PDF Ihres Browsers — es gibt nichts, wofür wir '
         'etwas verlangen könnten, und kein Wasserzeichen zu entfernen. Bezahlt wird die '
         'Seite über Werbung auf den Seiten um den Editor herum.'),
        ('Brauche ich ein Konto?',
         'Nein. Es gibt keine Anmeldung, weil kein Server etwas speichert. Mit „Sichern“ '
         'legen Sie eine Datei auf Ihrem Rechner ab und arbeiten später daran weiter.'),
        ('Kommt der Lebenslauf durch ein Bewerbungssystem?',
         'Einspaltige Layouts wie Plainfield und Linden werden am zuverlässigsten '
         'eingelesen. Layouts mit Seitenleiste gefallen einem Menschen besser, können aber '
         'Programme verwirren, die quer über die Spalten lesen.'),
        ('Wo liegen meine Daten?',
         'In Ihrem Browser, auf Ihrem Gerät. Der Editor behält einen Arbeitsstand lokal, '
         'damit ein geschlossener Tab keine Stunde kostet, und dieser Stand verlässt das '
         'Gerät nie.'),
        ('Mit Foto oder ohne?',
         'Im deutschsprachigen Raum ist ein Foto weiterhin üblich, in den USA und '
         'Großbritannien ein Risiko. Jedes Layout funktioniert mit und ohne.'),
    ])
    software_ld = {
        '@context': 'https://schema.org',
        '@type': 'SoftwareApplication',
        'name': BRAND,
        'applicationCategory': 'BusinessApplication',
        'operatingSystem': 'Jeder Browser',
        'inLanguage': 'de',
        'url': '%s/%s' % (DOMAIN, L['editor']),
        'description': 'Ein kostenloser Lebenslauf-Editor, der vollständig im Browser läuft, '
                       'mit sechzehn A4-Layouts und kostenlosem PDF-Export.',
        'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'EUR'},
    }
    guides = content.for_lang('de').GUIDES
    examples = content.for_lang('de').EXAMPLES

    return '\n'.join([
        head('Lebenslauf erstellen — kostenlos, ohne Anmeldung | %s' % BRAND,
             'Lebenslauf im Browser schreiben und kostenlos als PDF herunterladen. Sechzehn '
             'Vorlagen, keine Anmeldung, kein Wasserzeichen, nichts wird hochgeladen.',
             'de/index.html', depth, extra_ld=[software_ld, faq_ld], lang='de',
             alternate={'en': 'index.html'}),
        topbar(None, depth, 'de'),
        '',
        '<main id="main">',
        '<section class="hero">',
        '  <div class="wrap">',
        '    <h1>Lebenslauf im Browser schreiben. Kostenlos.</h1>',
        '    <p class="lead">Direkt in eine echte A4-Seite tippen, eines von sechzehn Layouts '
        'wählen, PDF speichern. Ohne Anmeldung, ohne Wasserzeichen, und nichts von dem, was '
        'Sie schreiben, wird hochgeladen.</p>',
        '    <div class="actions">',
        '      <a class="btn" href="%s%s">Jetzt schreiben</a>' % (up(depth), L['editor']),
        '      <a class="btn ghost" href="%s%s">Vorlagen ansehen</a>'
        % (up(depth), L['templates']),
        '    </div>',
        '    <p class="under"><b>Kostenlos</b> · keine Anmeldung · läuft in jedem Browser</p>',
        '    <div class="shot">',
        '      <img src="../assets/hero-de.png" width="1500" height="827" alt="Der Editor: '
        'links die Bedienung, rechts die A4-Seite." loading="eager">',
        '    </div>',
        '  </div>',
        '</section>',
        '',
        '<section class="facts">',
        '  <div class="wrap">',
        '    <div>' + ic('blatt') + '<strong>Nichts zu bezahlen</strong><p>Das PDF ist am Ende kostenlos, nicht '
        'nach einer Testphase. Es gibt keinen Download-Knopf, hinter den ein Preis passt.</p>'
        '</div>',
        '    <div>' + ic('schild') + '<strong>Nichts wird hochgeladen</strong><p>Der Editor ist eine Seite Code, '
        'die auf Ihrem Gerät läuft. Kein Server sieht Ihren Werdegang'
        + (' – außer Sie lassen ihn von der KI einlesen oder zuschneiden.' if CFG['ki'] else '.')
        + '</p></div>',
        '    <div>' + ic('raster') + '<strong>Sechzehn Layouts, ein Text</strong><p>Wechseln Sie das Design, wann '
        'Sie wollen. Was Sie geschrieben haben, bleibt stehen.</p></div>',
        '  </div>',
        '</section>',
        '',
        '<section class="band">',
        '  <div class="wrap">',
        '    <div class="band-head">',
        '      <h2>Vorlage wählen</h2>',
        '      <p>Jede ist ein fertiges A4-Dokument. Die tabellarischen mit Datumsspalte '
        'entsprechen der hier üblichen Form; einspaltige werden von Bewerbungsportalen am '
        'zuverlässigsten eingelesen.</p>',
        '    </div>',
        '    <div class="grid">%s</div>' % ''.join(
            template_tile(BY_ID[t], depth, 'de')
            for t in ['t8', 't9', 't1', 't7', 't3', 't13', 't4', 't11']),
        '    <p style="margin-top:30px"><a href="%s%s">Alle sechzehn Vorlagen</a></p>'
        % (up(depth), L['templates']),
        '  </div>',
        '</section>',
        '',
        ad('home-mid'),
        '',
        '<section class="band tight">',
        '  <div class="wrap">',
        '    <div class="band-head">',
        '      <h2>Ein fertiges Muster ansehen</h2>',
        '      <p>Ein vollständiger Lebenslauf für mehrere Berufe, mit der Begründung '
        'daneben: was zuerst geprüft wird und welche Zeilen zählen.</p>',
        '    </div>',
        '    <div class="cards">%s</div>' % ''.join(
            example_card(e, depth, 'de') for e in examples[:3]),
        '    <p style="margin-top:26px"><a href="%s%s">Alle Muster</a></p>'
        % (up(depth), L['examples']),
        '  </div>',
        '</section>',
        '',
        '<section class="band tight">',
        '  <div class="wrap">',
        '    <div class="band-head">',
        '      <h2>Was hineingehört</h2>',
        '      <p>Das Layout übernimmt der Editor. Diese Texte behandeln die Worte — den '
        'Teil, an dem entschieden wird, ob jemand anruft.</p>',
        '    </div>',
        '    <div class="cards">%s</div>' % ''.join(
            guide_card(g, depth, 'de') for g in [guides[0], guides[2], guides[3]]),
        '    <p style="margin-top:26px"><a href="%s%s">Alle acht Ratgeber</a></p>'
        % (up(depth), L['guides']),
        '  </div>',
        '</section>',
        '',
        '<section class="band tight">',
        '  <div class="wrap">',
        '    <div class="band-head"><h2>Fragen</h2></div>',
        '    ' + faq,
        '    ' + cta(depth, lang='de'),
        '  </div>',
        '</section>',
        '</main>',
        footer(depth, 'de'),
    ])


def page_templates_de():
    depth = 1
    L = LANGS['de']
    two_col = [t for t in TEMPLATES if t['specs'][0][1].lower().startswith('two')]
    one_col = [t for t in TEMPLATES if t not in two_col]
    ld = {
        '@context': 'https://schema.org',
        '@type': 'ItemList',
        'name': 'Lebenslauf-Vorlagen',
        'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1,
             'name': TEMPLATE_COPY['de'][t['tid']]['name'],
             'url': '%s/%s%s.html' % (DOMAIN, L['template_dir'], t['slug'])}
            for i, t in enumerate(TEMPLATES)],
    }
    return '\n'.join([
        head('Sechzehn kostenlose Lebenslauf-Vorlagen — %s' % BRAND,
             'Sechzehn Lebenslauf-Vorlagen im A4-Format: tabellarisch mit Datumsspalte, '
             'einspaltig, mit Seitenleiste, mit und ohne Foto. Kostenlos als PDF.',
             L['templates'], depth, extra_ld=[ld], lang='de',
             alternate={'en': 'templates.html'}),
        topbar('templates', depth, 'de'),
        crumbs([(L['home'], L['crumb_home']), (None, L['crumb_templates'])], depth),
        '<main id="main">',
        '<section class="band">',
        '  <div class="wrap">',
        '    <div class="band-head">',
        '      <h1 style="font-size:clamp(2rem,4vw,2.9rem)">Sechzehn Vorlagen</h1>',
        '      <p>Acht setzen Ihre Angaben in eine Seitenleiste, acht laufen einspaltig. '
        'Einspaltig ist die sicherere Wahl, wenn Sie über ein Bewerbungsportal hochladen; '
        'mit Seitenleiste liest es sich besser, wenn ein Mensch das PDF öffnet. '
        'Jede Vorlage trägt denselben Text, ein Wechsel kostet also nichts.</p>',
        '    </div>',
        '    <h2 style="margin-bottom:22px">Zweispaltig</h2>',
        '    <div class="grid">%s</div>' % ''.join(
            template_tile(t, depth, 'de') for t in two_col),
        '    <h2 style="margin:52px 0 22px">Einspaltig</h2>',
        '    <div class="grid">%s</div>' % ''.join(
            template_tile(t, depth, 'de') for t in one_col),
        '  </div>',
        '</section>',
        ad('templates-foot'),
        '<section class="band tight">',
        '  <div class="wrap">',
        '    <div class="band-head"><h2>Welche sollten Sie nehmen?</h2></div>',
        '    <div class="cards">',
        '      <div class="card"><span class="tag">Bewerbung in DACH</span>'
        '<h3>Mit Datumsspalte</h3><p>Ledger und Milestone folgen der tabellarischen Form, '
        'die hier erwartet wird, und haben Platz für ein Foto.</p>'
        '<span class="mins"><a href="%s%slebenslauf-schreiben.html">Wie man ihn aufbaut</a>'
        '</span></div>' % (up(depth), L['guide_dir']),
        '      <div class="card"><span class="tag">Bewerbungsportale</span>'
        '<h3>Einspaltig, ohne Grafik</h3><p>Plainfield, Linden und Hairline haben nur eine '
        'Leserichtung — damit kommen automatische Systeme am besten zurecht.</p>'
        '<span class="mins"><a href="%s%sbewerbung-per-email.html">Worauf es beim Versand '
        'ankommt</a></span></div>' % (up(depth), L['guide_dir']),
        '      <div class="card"><span class="tag">Bewerbung im Ausland</span>'
        '<h3>Ohne Foto</h3><p>Plainfield und Quill funktionieren ohne Bild — in den USA und '
        'Großbritannien ist ein Foto ein Risiko, kein Vorteil.</p>'
        '<span class="mins"><a href="%s%sbewerbung-usa-uk.html">Was dort anders ist</a>'
        '</span></div>' % (up(depth), L['guide_dir']),
        '    </div>',
        '  </div>',
        '</section>',
        '</main>',
        footer(depth, 'de'),
    ])


def ki_abschnitt(lang):
    """Steht nur auf der Seite, wenn die KI-Funktionen eingerichtet sind.

    Eine Datenschutzerklärung, die eine Funktion verschweigt, ist schlimmer
    als keine. Und der Satz „Ihr Lebenslauf verlässt Ihr Gerät nicht“ gilt
    dann nicht mehr ohne Einschränkung — also steht die Einschränkung da.
    """
    if not CFG['ki']:
        return []
    dienst = esc(CFG['ki_anbieter'])
    if lang == 'de':
        return [
            '',
            '    <h2>Die beiden KI-Funktionen</h2>',
            '    <p>Der Editor bietet zwei Funktionen an, bei denen Text Ihr Gerät verlässt: '
            'einen vorhandenen Lebenslauf einlesen und einen Lebenslauf auf eine '
            'Stellenanzeige zuschneiden. Beide laufen nur, wenn Sie sie anklicken, und beim '
            'ersten Mal werden Sie vorher gefragt. Wer sie nicht benutzt, für den bleibt der '
            'Editor eine Seite ohne Server.</p>',
            '    <p><strong>Was gesendet wird:</strong> der Text Ihres Lebenslaufs '
            '(beziehungsweise die hochgeladene Datei) und, beim Zuschneiden, der Text der '
            'Stellenanzeige. <strong>Wohin:</strong> an unseren Vermittlungsdienst und von '
            'dort an %s, der das Sprachmodell betreibt. <strong>Wie lange:</strong> Wir '
            'speichern nichts davon; die Anfrage wird beantwortet und ist damit erledigt. '
            'Welche Speicherfristen beim Modellanbieter gelten, steht in dessen '
            'Datenschutzhinweisen.</p>' % dienst,
            '    <p>Rechtsgrundlage ist Ihre Einwilligung nach Art. 6 Abs. 1 lit. a DSGVO, '
            'die Sie mit dem Bestätigen des Hinweises erteilen. Sie können sie jederzeit '
            'widerrufen, indem Sie die Funktionen nicht mehr benutzen; die Zustimmung selbst '
            'liegt als Merkposten im <em>local storage</em> Ihres Browsers und verschwindet '
            'mit Ihren Browserdaten. Eine Übermittlung in Drittländer ist dabei nicht '
            'ausgeschlossen — prüfen Sie das für den von Ihnen gewählten Anbieter.</p>',
            '    <p>Bitte laden Sie nichts hoch, was nicht in eine Bewerbung gehört. Ein '
            'Lebenslauf enthält personenbezogene Daten; besondere Kategorien nach Art. 9 '
            'DSGVO — etwa Gesundheitsdaten oder die Religionszugehörigkeit — gehören weder in '
            'eine Bewerbung noch in ein Sprachmodell.</p>',
        ]
    return [
        '',
        '    <h2>The two AI features</h2>',
        '    <p>The editor offers two features where text leaves your device: reading in an '
        'existing CV, and tailoring a CV to a job advert. Both run only when you click them, '
        'and the first time you are asked beforehand. If you never use them, the editor stays '
        'a page without a server.</p>',
        '    <p><strong>What is sent:</strong> the text of your CV (or the file you upload) '
        'and, when tailoring, the text of the job advert. <strong>Where to:</strong> our own '
        'relay, and from there to %s, who run the language model. <strong>For how long:</strong> '
        'we store none of it; the request is answered and that is the end of it. The model '
        'provider\'s own retention terms are in their privacy notice.</p>' % dienst,
        '    <p>The legal basis is your consent under Art. 6(1)(a) GDPR, given when you confirm '
        'the notice. You can withdraw it at any time by not using the features; the consent '
        'itself is a marker in your browser\'s local storage and disappears with your browser '
        'data. A transfer outside the EEA is not ruled out — check that for the provider you '
        'choose.</p>',
        '    <p>Please do not upload anything that does not belong in a job application. A CV '
        'contains personal data; special categories under Art. 9 GDPR — health data or '
        'religious affiliation, say — belong neither in an application nor in a language '
        'model.</p>',
    ]


def page_privacy():
    depth = 0
    return '\n'.join([
        head('Privacy and cookies — %s' % BRAND,
             'What this site collects, what it does not, and exactly what happens when you '
             'accept or decline advertising cookies.',
             'privacy.html', depth, alternate={'de': LANGS['de']['privacy']}),
        topbar(None, depth),
        crumbs([('index.html', 'Home'), (None, 'Privacy')], depth),
        '<main id="main">',
        '<section class="band">',
        '  <div class="wrap prose">',
        '    <h1 style="font-size:clamp(2rem,4vw,2.8rem)">Privacy and cookies</h1>',
        '    <p class="lead">The short version: your resume never leaves your device'
        + (' unless you use one of the two AI features, which ask first' if CFG['ki'] else '')
        + ', the site sets no cookie until you say yes, and declining costs you nothing but '
        'the ads.</p>',
        '    <div class="callout warn"><strong>Before you publish this site</strong>',
        '    <p>This is a working draft written for the site as it is built, not legal advice. '
        'Have it checked, and replace the bracketed details — your hosting provider and the '
        'contact address in the imprint.</p></div>',
        '',
        '    <h2>The editor</h2>',
        '    <p>The resume editor runs entirely in your browser. The text you type, the photo '
        'you choose and the design you pick are never transmitted to us: there is no account, '
        'no database, and no copy of your resume on any server.</p>',
        '    <p>The editor does keep a working draft in your browser\'s local storage, so that '
        'closing the tab by accident does not destroy an hour of work. That draft sits on your '
        'own device, is readable only by this site in this browser, and is never sent anywhere. '
        'Clearing your browser data, or using the Clear button in the editor, removes it.</p>',
        ] + ki_abschnitt('en') + [
        '',
        '    <h2>Cookies and local storage on the rest of the site</h2>',
        '    <div class="scroll-x"><table class="plain">',
        '      <tr><th>What</th><th>Where</th><th>Why</th><th>How long</th></tr>',
        '      <tr><td><code>ps.consent</code></td><td>Local storage</td>'
        '<td>Remembers your answer to the cookie question so you are not asked again</td>'
        '<td>180 days</td></tr>',
        '      <tr><td><code>ps.draft</code></td><td>Local storage, editor only</td>'
        '<td>Your unfinished resume, kept on your device</td><td>Until you clear it</td></tr>',
        '      <tr><td>Google advertising cookies</td><td>Set by Google</td>'
        '<td>Ad measurement and personalisation — only if you accept</td>'
        '<td>Set by Google; see their policy</td></tr>',
        '    </table></div>',
        '    <p>Nothing in the first two rows identifies you, is shared, or leaves your '
        'device.</p>',
        '',
        '    <h2>Advertising</h2>',
        '    <p>Pages other than the editor carry advertising, which is what pays for the site. '
        'Our ad partner is Google (AdSense). Before you answer the consent question, no '
        'advertising script is loaded and no advertising cookie exists.</p>',
        '    <p><strong>If you accept:</strong> Google\'s ad script loads, may set cookies and '
        'similar identifiers, and receives your IP address, browser and the page you are on. It '
        'uses that to select ads, to measure them, and to limit how often you see the same one. '
        'Google may combine it with data it holds from other sites. Data may be processed in '
        'the United States under the EU&nbsp;–&nbsp;US Data Privacy Framework. What Google does '
        'with it is set out in the <a href="https://policies.google.com/technologies/partner-sites" '
        'rel="nofollow noopener">Google privacy and terms</a>.</p>',
        '    <p><strong>If you decline:</strong> nothing loads. No ad script is requested, no '
        'identifier is set, and the pages show a link to our own editor in the space instead. '
        'Declining does not limit any part of the site.</p>',
        '    <p>Legal basis: your consent, under Art. 6(1)(a) GDPR and the corresponding '
        'national implementation of the ePrivacy rules (in Germany, § 25 TDDDG). You may '
        'withdraw it at any time through the '
        '<button type="button" class="lnk" data-consent-settings style="background:none;'
        'border:0;padding:0;font:inherit;color:var(--accent);text-decoration:underline;'
        'cursor:pointer">cookie settings</button> link, which appears in the footer of every '
        'page. Withdrawal takes effect immediately and does not affect what was lawful '
        'before.</p>',
        '',
        '    <h2>Hosting and server logs</h2>',
        '    <p>This site is served by [hosting provider], which records standard server log '
        'data: IP address, time of request, the page requested, and the browser identification '
        'your device sends. Those logs exist to keep the site running and to investigate abuse. '
        '[Provider] processes them on our behalf under a data processing agreement. Legal '
        'basis: our legitimate interest in operating the site securely, Art. 6(1)(f) GDPR.</p>',
        '',
        '    <h2>Fonts and other third parties</h2>',
        '    <p>The typefaces are served from this domain, not from Google Fonts, so no request '
        'for a font reaches a third party and no IP address is passed on to one. Apart from the '
        'advertising described above, this site loads nothing from anywhere else: no analytics '
        'by default, no social widgets, no trackers, no content delivery network.</p>',
        '',
        '    <h2>Measurement</h2>',
        '    <p>If page statistics are switched on, they appear as a separate category in the '
        'cookie notice and are off until you allow them. As configured today, this site runs '
        'no analytics at all.</p>',
        '',
        '    <h2>Your rights</h2>',
        '    <p>Under the GDPR you may request access to the personal data we hold about you, '
        'its correction or deletion, a restriction on processing, and a copy in a portable '
        'form; you may object to processing based on legitimate interest; and you may complain '
        'to a supervisory authority in the country where you live. Since the editor stores '
        'nothing and we operate no user accounts, such requests in practice concern server logs '
        'and, where you have consented, advertising identifiers held by Google.</p>',
        '    <p>Write to the address on the <a href="imprint.html">imprint page</a>.</p>',
        '',
        '    <h2>Children</h2>',
        '    <p>This site is not directed at children and we do not knowingly process data '
        'about them.</p>',
        '',
        '    <h2>Changes</h2>',
        '    <p>If the cookie categories or the ad partner change, this page changes with them '
        'and the consent question is asked again rather than assumed.</p>',
        '    <p class="fine">Last updated %s.</p>' % content.UPDATED,
        '  </div>',
        '</section>',
        '</main>',
        footer(depth),
    ])


def page_about_de():
    depth = 1
    L = LANGS['de']
    return '\n'.join([
        head('Über uns — %s' % BRAND,
             'Wer diese Seite betreibt, wie sie finanziert wird, und was mit Ihren Daten '
             'passiert — nämlich nichts.',
             L['about'], depth, lang='de', alternate={'en': 'about.html'}),
        topbar('about', depth, 'de'),
        crumbs([(L['home'], L['crumb_home']), (None, 'Über uns')], depth),
        '<main id="main">',
        '<section class="band">',
        '  <div class="wrap prose">',
        '    <h1 style="font-size:clamp(2rem,4vw,2.8rem)">Über diese Seite</h1>',
        '    <p class="lead">Ein Lebenslauf-Editor, der im Browser läuft, sechzehn Vorlagen '
        'zum Anfangen und acht Ratgeber zum Inhalt. Kostenlos, und zwar im gewöhnlichen '
        'Sinn: keine Testphase, kein Konto, kein Wasserzeichen im Export.</p>',
        '',
        '    <h2>Warum es so gebaut ist</h2>',
        '    <p>Fast jeder Lebenslauf-Generator im Netz funktioniert gleich. Sie tippen Ihren '
        'Werdegang in ein Formular, sehen eine Vorschau entstehen, und am Download-Knopf '
        'treffen Sie den Preis. Die Arbeit ist getan, die Seite ist fertig, und der einzige '
        'Weg, sie herauszubekommen, ist ein Abonnement, das sich verlängert.</p>',
        '    <p>Hier gibt es keinen Download-Knopf, hinter den man einen Preis stellen '
        'könnte, weil der Export der Druck-nach-PDF Ihres Browsers ist. Und es gibt keinen '
        'Server, der Ihr Dokument als Pfand behalten könnte, weil es keinen Server gibt: Der '
        'Editor ist eine HTML-Datei, und alles, was Sie eintippen, bleibt in dem Tab, in dem '
        'Sie es eingetippt haben.</p>',
        '',
        '    <h2>Wie die Seite finanziert wird</h2>',
        '    <p>Über Werbung auf den Seiten um den Editor herum — Startseite, Vorlagen, '
        'Muster, Ratgeber. Der Editor selbst enthält keine Werbung und wird keine enthalten. '
        'Wer dort zwanzig Minuten verbringt, erzeugt einen einzigen Seitenaufruf; Werbung im '
        'Editor würde also fast nichts einbringen und das Werkzeug schlechter machen.</p>',
        '    <p>Werbung wird nur geladen, wenn Sie zustimmen. Lehnen Sie ab, wird kein '
        'Werbeskript angefordert, und die Seite funktioniert genauso wie sonst. Ihre '
        'Entscheidung ändern Sie über den Link '
        '<button type="button" class="lnk" data-consent-settings '
        'style="background:none;border:0;padding:0;font:inherit;color:var(--accent);'
        'text-decoration:underline;cursor:pointer">Cookie-Einstellungen</button> im Fuß '
        'jeder Seite.</p>',
        '',
        '    <h2>Was mit Ihrem Lebenslauf passiert</h2>',
        '    <p>Nichts. Er wird nicht hochgeladen, nicht auf einem Server gespeichert, nicht '
        'gesichert und von uns nicht gesehen. Der Editor behält einen Arbeitsstand in Ihrem '
        'eigenen Browser, damit ein versehentlich geschlossener Tab keine Stunde Arbeit '
        'kostet, und dieser Stand bleibt auf Ihrem Gerät, bis Sie ihn löschen. Die '
        '<a href="datenschutz.html">Datenschutzerklärung</a> nennt die Einzelheiten, '
        'einschließlich dessen, was das Werbenetzwerk tut, wenn Sie es zulassen.</p>',
        '',
        '    <h2>Wer die Ratgeber schreibt</h2>',
        '    <p>Wir selbst — sie sind für diese Seite geschrieben und nicht aus anderen '
        'Quellen zusammengetragen. Und sie sind für den deutschsprachigen Raum geschrieben, '
        'nicht aus dem Englischen übersetzt: Foto, Anschreiben, Arbeitszeugnis und '
        'monatsgenaue Zeiträume kommen in amerikanischen Ratgebern gar nicht vor, und '
        'umgekehrt ist ein Foto in London ein Risiko. Wo sich die Empfehlung nach Land '
        'unterscheidet, steht das dort.</p>',
        '    <p>Wenn etwas in einem Ratgeber falsch, veraltet oder für Ihren Fall unpassend '
        'ist, schreiben Sie uns. Korrekturen werden gemacht, und das Änderungsdatum am '
        'Artikel ändert sich mit.</p>',
        '',
        '    <h2>Kontakt</h2>',
        '    <p>Fragen, Korrekturen und Fehlermeldungen: siehe '
        '<a href="impressum.html">Impressum und Kontakt</a>.</p>',
        '  </div>',
        '</section>',
        '</main>',
        footer(depth, 'de'),
    ])


def page_imprint_de():
    depth = 1
    L = LANGS['de']
    return '\n'.join([
        head('Impressum und Kontakt — %s' % BRAND,
             'Anbieterkennzeichnung nach § 5 DDG und Kontaktmöglichkeiten.',
             L['imprint'], depth, lang='de', alternate={'en': 'imprint.html'}),
        topbar(None, depth, 'de'),
        crumbs([(L['home'], L['crumb_home']), (None, 'Impressum')], depth),
        '<main id="main">',
        '<section class="band">',
        '  <div class="wrap prose">',
        '    <h1 style="font-size:clamp(2rem,4vw,2.8rem)">Impressum</h1>',
        '    <div class="callout warn"><strong>Vor der Veröffentlichung ausfüllen</strong>',
        '    <p>§ 5 Digitale-Dienste-Gesetz verlangt Name, Anschrift und eine unmittelbare '
        'Kontaktmöglichkeit. Eine E-Mail-Adresse allein genügt nicht, ein Postfach genügt '
        'nicht, und die Pflicht gilt auch für eine private Seite, sobald sie Werbung trägt — '
        'fehlendes Impressum ist ein häufiger Abmahngrund. Die Angaben in eckigen Klammern '
        'sind zu ersetzen; Name und E-Mail kommen aus '
        '<code>assets/site-config.js</code>.</p></div>',
        '',
        '    <h2>Angaben gemäß § 5 DDG</h2>',
        '    <p>%s<br>[Straße und Hausnummer]<br>[PLZ und Ort]<br>[Land]</p>'
        % esc(CFG['operator'] or '[Name]'),
        '',
        '    <h2>Kontakt</h2>',
        '    <p>Telefon: [Nummer]<br>E-Mail: %s</p>'
        % esc(CFG['email'] or '[ihre@adresse.de]'),
        '',
        '    <h2>Umsatzsteuer-Identifikationsnummer</h2>',
        '    <p>[USt-IdNr. gemäß § 27 a UStG, sofern vorhanden]<br>'
        '[Registergericht und Registernummer, sofern es eine Gesellschaft ist]</p>',
        '',
        '    <h2>Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV</h2>',
        '    <p>[Name]<br>[Anschrift, falls von der obigen abweichend]</p>',
        '',
        '    <h2>Verbraucherstreitbeilegung</h2>',
        '    <p>Wir sind nicht verpflichtet und nicht bereit, an '
        'Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.</p>',
        '',
        '    <h2>Haftung für Inhalte und Links</h2>',
        '    <p>Als Diensteanbieter sind wir für eigene Inhalte auf diesen Seiten nach den '
        'allgemeinen Gesetzen verantwortlich, nicht jedoch verpflichtet, übermittelte oder '
        'gespeicherte fremde Informationen zu überwachen. Diese Seite verweist auf externe '
        'Seiten, auf deren Inhalte wir keinen Einfluss haben; für sie ist der jeweilige '
        'Anbieter verantwortlich. Die verlinkten Seiten waren zum Zeitpunkt der Verlinkung '
        'nicht erkennbar rechtswidrig.</p>',
        '',
        '    <h2>Urheberrecht</h2>',
        '    <p>Die Texte und Gestaltungen dieser Seite unterliegen dem Urheberrecht. Die '
        'Lebenslauf-Vorlagen dürfen Sie für Ihre eigenen Bewerbungen frei verwenden, '
        'einschließlich gewerblicher Bewerbungen, ohne Namensnennung.</p>',
        '',
        '    <h2>Ratgeberinhalte</h2>',
        '    <p>Die Ratgeber auf dieser Seite sind allgemeine Hinweise und keine '
        'Rechtsberatung. Bei arbeitsrechtlichen Fragen — etwa zu einem Arbeitszeugnis — '
        'ersetzt sie kein Gespräch mit einer Fachanwältin oder der Gewerkschaft.</p>',
        '  </div>',
        '</section>',
        '</main>',
        footer(depth, 'de'),
    ])


def page_privacy_de():
    depth = 1
    L = LANGS['de']
    return '\n'.join([
        head('Datenschutzerklärung — %s' % BRAND,
             'Was diese Seite erhebt, was nicht, und was genau passiert, wenn Sie '
             'Werbe-Cookies zustimmen oder ablehnen.',
             L['privacy'], depth, lang='de', alternate={'en': 'privacy.html'}),
        topbar(None, depth, 'de'),
        crumbs([(L['home'], L['crumb_home']), (None, 'Datenschutz')], depth),
        '<main id="main">',
        '<section class="band">',
        '  <div class="wrap prose">',
        '    <h1 style="font-size:clamp(2rem,4vw,2.8rem)">Datenschutzerklärung</h1>',
        '    <p class="lead">Kurz: Ihr Lebenslauf verlässt Ihr Gerät nicht'
        + (' – außer Sie benutzen eine der beiden KI-Funktionen, die vorher fragen' if CFG['ki'] else '')
        + ', die Seite setzt kein Cookie, bevor Sie zustimmen, und eine Ablehnung kostet Sie '
        'nichts außer der Werbung.</p>',
        '    <div class="callout warn"><strong>Vor der Veröffentlichung</strong>',
        '    <p>Dies ist ein Arbeitsentwurf für die Seite, wie sie gebaut ist, und keine '
        'Rechtsberatung. Lassen Sie ihn prüfen und ersetzen Sie die Angaben in eckigen '
        'Klammern — Ihren Hoster und die Anschrift im Impressum.</p></div>',
        '',
        '    <h2>1. Verantwortlicher</h2>',
        '    <p>Verantwortlich im Sinne der DSGVO ist die im '
        '<a href="impressum.html">Impressum</a> genannte Person. Eine '
        'Datenschutzbeauftragte ist nicht bestellt, da die Voraussetzungen des § 38 BDSG '
        'nicht vorliegen.</p>',
        '',
        '    <h2>2. Der Editor</h2>',
        '    <p>Der Lebenslauf-Editor läuft vollständig in Ihrem Browser. Der Text, den Sie '
        'eintippen, das Foto, das Sie wählen, und das Design, das Sie einstellen, werden uns '
        'nie übermittelt: Es gibt kein Konto, keine Datenbank und keine Kopie Ihres '
        'Lebenslaufs auf einem Server.</p>',
        '    <p>Der Editor speichert einen Arbeitsstand im <em>local storage</em> Ihres '
        'Browsers, damit ein versehentlich geschlossener Tab nicht eine Stunde Arbeit '
        'vernichtet. Dieser Stand liegt auf Ihrem Gerät, ist nur von dieser Seite in diesem '
        'Browser lesbar und wird nirgendwohin gesendet. Ihre Browserdaten zu löschen oder im '
        'Editor „Von vorn beginnen“ zu wählen, entfernt ihn.</p>',
        '',
        ] + ki_abschnitt('de') + [
        '',
        '    <h2>3. Cookies und lokaler Speicher</h2>',
        '    <div class="scroll-x"><table class="plain">',
        '      <tr><th>Was</th><th>Wo</th><th>Wozu</th><th>Wie lange</th></tr>',
        '      <tr><td><code>ps.consent</code></td><td>Local Storage</td>'
        '<td>Merkt Ihre Antwort auf die Cookie-Frage, damit Sie nicht erneut gefragt werden'
        '</td><td>180 Tage</td></tr>',
        '      <tr><td><code>ps.draft</code></td><td>Local Storage, nur im Editor</td>'
        '<td>Ihr unfertiger Lebenslauf, auf Ihrem Gerät</td><td>bis Sie ihn löschen</td></tr>',
        '      <tr><td>Werbe-Cookies von Google</td><td>von Google gesetzt</td>'
        '<td>Messung und Personalisierung von Werbung — nur bei Ihrer Einwilligung</td>'
        '<td>von Google festgelegt</td></tr>',
        '    </table></div>',
        '    <p>Die ersten beiden Einträge identifizieren Sie nicht, werden nicht geteilt und '
        'verlassen Ihr Gerät nicht. Rechtsgrundlage für das Speichern der '
        'Einwilligungsentscheidung ist unser berechtigtes Interesse daran, Ihre Entscheidung '
        'zu respektieren (Art. 6 Abs. 1 lit. f DSGVO); das Speichern selbst ist nach § 25 '
        'Abs. 2 Nr. 2 TDDDG einwilligungsfrei, weil es für den von Ihnen gewünschten Dienst '
        'unbedingt erforderlich ist.</p>',
        '',
        '    <h2>4. Werbung</h2>',
        '    <p>Die Seiten außerhalb des Editors enthalten Werbung; sie bezahlt den Betrieb. '
        'Werbepartner ist Google Ireland Limited (Google AdSense). Bevor Sie die '
        'Einwilligungsfrage beantworten, wird kein Werbeskript geladen und kein Werbe-Cookie '
        'gesetzt.</p>',
        '    <p><strong>Wenn Sie zustimmen:</strong> Das Skript von Google wird geladen, kann '
        'Cookies und ähnliche Kennungen setzen und erhält Ihre IP-Adresse, Angaben zu Ihrem '
        'Browser und die aufgerufene Seite. Google verwendet das zur Auswahl und Messung von '
        'Werbung und zur Begrenzung der Häufigkeit und kann es mit Daten aus anderen Quellen '
        'zusammenführen. Eine Übermittlung in die USA ist möglich; Google LLC ist unter dem '
        'EU-US Data Privacy Framework zertifiziert, sodass ein Angemessenheitsbeschluss der '
        'Kommission vorliegt. Einzelheiten unter '
        '<a href="https://policies.google.com/technologies/partner-sites" '
        'rel="nofollow noopener">policies.google.com</a>.</p>',
        '    <p><strong>Wenn Sie ablehnen:</strong> Es wird nichts geladen. Kein Werbeskript, '
        'keine Kennung, und an der Stelle steht ein Hinweis auf unseren eigenen Editor. Die '
        'Ablehnung schränkt keinen Teil der Seite ein.</p>',
        '    <p>Rechtsgrundlage ist Ihre Einwilligung nach Art. 6 Abs. 1 lit. a DSGVO und '
        '§ 25 Abs. 1 TDDDG. Sie können sie jederzeit über den Link '
        '<button type="button" class="lnk" data-consent-settings '
        'style="background:none;border:0;padding:0;font:inherit;color:var(--accent);'
        'text-decoration:underline;cursor:pointer">Cookie-Einstellungen</button> im Fuß '
        'jeder Seite widerrufen. Der Widerruf wirkt sofort und lässt die Rechtmäßigkeit der '
        'bis dahin erfolgten Verarbeitung unberührt.</p>',
        '',
        '    <h2>5. Hosting und Server-Logfiles</h2>',
        '    <p>Diese Seite wird von [Hoster] bereitgestellt. Dabei werden übliche '
        'Server-Logfiles erhoben: IP-Adresse, Zeitpunkt der Anfrage, aufgerufene Seite und '
        'die Browserkennung, die Ihr Gerät übermittelt. Diese Daten dienen dem sicheren '
        'Betrieb und der Aufklärung von Missbrauch. [Hoster] verarbeitet sie für uns als '
        'Auftragsverarbeiter nach Art. 28 DSGVO. Rechtsgrundlage ist unser berechtigtes '
        'Interesse am sicheren Betrieb, Art. 6 Abs. 1 lit. f DSGVO.</p>',
        '',
        '    <h2>6. Schriftarten und weitere Dritte</h2>',
        '    <p>Die Schriftarten werden von dieser Domain ausgeliefert, nicht von Google '
        'Fonts. Es geht also keine Anfrage für eine Schrift an einen Dritten, und es wird '
        'keine IP-Adresse dorthin übermittelt. Abgesehen von der oben beschriebenen Werbung '
        'lädt diese Seite nichts von anderen Servern: keine Analyse, keine Social-Plugins, '
        'keine Tracker, kein Content-Delivery-Network.</p>',
        '',
        '    <h2>7. Reichweitenmessung</h2>',
        '    <p>Sofern eine Statistik eingeschaltet ist, erscheint sie als eigene Kategorie '
        'im Cookie-Hinweis und ist aus, bis Sie zustimmen. In der aktuellen Konfiguration '
        'läuft auf dieser Seite keine Analyse.</p>',
        '',
        '    <h2>8. Ihre Rechte</h2>',
        '    <p>Sie haben das Recht auf Auskunft (Art. 15), Berichtigung (Art. 16), Löschung '
        '(Art. 17), Einschränkung der Verarbeitung (Art. 18), Datenübertragbarkeit (Art. 20) '
        'und Widerspruch gegen eine auf berechtigtem Interesse beruhende Verarbeitung '
        '(Art. 21 DSGVO). Da der Editor nichts speichert und wir keine Nutzerkonten führen, '
        'betreffen solche Anfragen in der Praxis nur Server-Logfiles und — bei erteilter '
        'Einwilligung — die bei Google liegenden Werbekennungen.</p>',
        '    <p>Außerdem können Sie sich bei einer Aufsichtsbehörde beschweren, in der Regel '
        'bei der Landesdatenschutzbehörde Ihres Wohnsitzes. Anfragen richten Sie an die '
        'Adresse im <a href="impressum.html">Impressum</a>.</p>',
        '',
        '    <h2>9. Kinder</h2>',
        '    <p>Diese Seite richtet sich nicht an Kinder, und wir verarbeiten nicht wissentlich '
        'Daten von ihnen.</p>',
        '',
        '    <h2>10. Änderungen</h2>',
        '    <p>Ändern sich die Cookie-Kategorien oder der Werbepartner, ändert sich diese '
        'Seite mit, und die Einwilligungsfrage wird neu gestellt statt unterstellt.</p>',
        '    <p class="fine">Stand: %s.</p>' % pretty_date(content.UPDATED, 'de'),
        '  </div>',
        '</section>',
        '</main>',
        footer(depth, 'de'),
    ])


def page_404_de():
    depth = 1
    L = LANGS['de']
    return '\n'.join([
        head('Seite nicht gefunden — %s' % BRAND,
             'Diese Seite gibt es nicht. Editor, Vorlagen und Ratgeber sind einen Klick '
             'entfernt.', 'de/404.html', depth, noindex=True, lang='de'),
        topbar(None, depth, 'de'),
        '<main id="main">',
        '<section class="band mid">',
        '  <div class="wrap">',
        '    <p class="kicker">Fehler 404</p>',
        '    <h1 style="font-size:clamp(2rem,4vw,3rem)">Diese Seite gibt es nicht</h1>',
        '    <p class="lead">Vielleicht wurde sie umbenannt, vielleicht ist der Link, der '
        'Sie hierher geschickt hat, älter als die Seite. Alles andere ist einen Klick '
        'entfernt.</p>',
        '    <div class="actions">',
        '      <a class="btn" href="/editor.html?lang=de">Editor öffnen</a>',
        '      <a class="btn ghost" href="/de/lebenslauf-vorlagen.html">Vorlagen ansehen</a>',
        '      <a class="btn ghost" href="/de/ratgeber/index.html">Ratgeber lesen</a>',
        '    </div>',
        '  </div>',
        '</section>',
        '</main>',
        footer(depth, 'de'),
    ])


# ---------------------------------------------------------------- site files

def sitemap(paths):
    rows = []
    for path in paths:
        priority = '1.0' if path == 'index.html' else (
            '0.9' if path in ('templates.html', 'guides/index.html', 'editor.html') else '0.7')
        rows.append('  <url><loc>%s/%s</loc><lastmod>%s</lastmod>'
                    '<priority>%s</priority></url>' % (DOMAIN, path, TODAY, priority))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s\n</urlset>'
            % '\n'.join(rows))


def robots():
    return ('User-agent: *\n'
            'Allow: /\n'
            '\n'
            '# Nothing here is private; the editor holds no data to crawl.\n'
            'Sitemap: %s/sitemap.xml\n' % DOMAIN)


def manifest():
    return json.dumps({
        'name': '%s resume builder' % BRAND,
        'short_name': BRAND,
        'description': 'Build a resume in your browser and download the PDF for free.',
        'start_url': '/editor.html',
        'display': 'standalone',
        'background_color': '#EDEFF2',
        'theme_color': '#1F5F5B',
        'icons': [
            {'src': '/assets/favicon.png', 'sizes': '32x32', 'type': 'image/png'},
            {'src': '/assets/apple-touch-icon.png', 'sizes': '180x180', 'type': 'image/png'},
            {'src': '/assets/icon-512.png', 'sizes': '512x512', 'type': 'image/png'},
            {'src': '/assets/favicon.svg', 'sizes': 'any', 'type': 'image/svg+xml'},
        ],
    }, indent=2)


def ads_txt():
    """ads.txt tells ad networks which sellers may sell this site's inventory."""
    client = CFG['adsense']
    if not client:
        return ('# Put the line your ad network gives you here. For AdSense it is\n'
                '# generated from the publisher ID in assets/site-config.js the next\n'
                '# time you run tools/build.py:\n'
                '#\n'
                '#   google.com, pub-0000000000000000, DIRECT, f08c47fec0942fa0\n')
    publisher = client.replace('ca-', '', 1)
    return ('# Generated from assets/site-config.js by tools/build.py.\n'
            'google.com, %s, DIRECT, f08c47fec0942fa0\n' % publisher)


def icons_css():
    """The icon set as one small stylesheet for the site pages.

    Each icon becomes a CSS variable and a class. They are masks, not images:
    the shape is cut out of the current text colour, so an icon in a heading is
    the colour of that heading and needs no second file for a dark background.
    """
    lines = [
        '/* Symbole. Erzeugt aus tools/icons.py — nicht von Hand ändern. */',
        ':root{',
        icons.css_variables(),
        '}',
        '/* .sym, nicht .ic: .ad-house .ic ist seit der ersten Fassung ein',
        '   Farbfeld und würde sonst zu einer vollen Fläche. */',
        '.sym{display:inline-block;width:1em;height:1em;flex:0 0 auto;'
        'background:currentColor;vertical-align:-.14em;',
        '  -webkit-mask:var(--sym) no-repeat center/contain;'
        'mask:var(--sym) no-repeat center/contain}',
    ]
    for name in icons.ICONS:
        lines.append('.sym-%s{--sym:var(--i-%s)}' % (name, name))
    return '\n'.join(lines) + '\n'


def pdf_leser():
    """api/pdf.js noch einmal, aber für den Browser.

    Dieselbe Datei liest im Worker den Text aus einem PDF. Im Browser ist sie
    mehr wert: Was dort schon zu Text geworden ist, muss nicht als ganze Datei
    hochgeladen werden — das ist schneller, billiger und gibt weniger preis.
    Erzeugt wird sie hier, damit es nur eine Quelle gibt.
    """
    quelle = lies(os.path.join(ROOT, 'api', 'pdf.js'))
    quelle = quelle.replace('export async function', 'async function')
    quelle = quelle.replace('export function', 'function')
    return ('/* Erzeugt aus api/pdf.js — nicht von Hand ändern. */\n'
            '(function(){\n' + quelle +
            '\nwindow.pdfText = pdfText;\nwindow.textTaugt = textTaugt;\n})();\n')


def patch_editor_icons(src):
    """Writes the icon variables into the editor, between its two marks."""
    anfang, ende = '/* symbole:anfang */', '/* symbole:ende */'
    i, j = src.index(anfang), src.index(ende)
    return src[:i + len(anfang)] + '\n' + icons.css_variables() + '\n  ' + src[j:]


def patch_editor():
    """The editor is hand-written, so only its canonical and og: URLs are stamped."""
    path = os.path.join(ROOT, 'editor.html')
    src = lies(path)
    fixed = patch_editor_icons(src)
    fixed = re.sub(r'https://[A-Za-z0-9.\-]*YOUR-DOMAIN\.example', DOMAIN, fixed)
    fixed = re.sub(r'(<link rel="canonical" href=")[^"]*(">)',
                   r'\g<1>%s/editor.html\g<2>' % DOMAIN, fixed)
    fixed = re.sub(r'(<meta property="og:url" content=")[^"]*(">)',
                   r'\g<1>%s/editor.html\g<2>' % DOMAIN, fixed)
    if fixed != src:
        io.open(path, 'w', encoding='utf-8', newline='\n').write(fixed)
    return 'editor.html'


def main():
    written = []
    write('assets/icons.css', icons_css())      # Stilblatt, gehört nicht in die Sitemap
    write('assets/pdf-text.js', pdf_leser())    # derselbe Leser, für den Browser

    # ---- English, at the root ----------------------------------------
    written.append(write('index.html', page_index()))
    written.append(write('templates.html', page_templates()))
    for t in TEMPLATES:
        written.append(write('templates/%s.html' % t['slug'], page_template(t)))
    written.append(write('examples/index.html', page_examples_index()))
    for e in content.EXAMPLES:
        written.append(write('examples/%s.html' % e['slug'], page_example(e)))
    written.append(write('guides/index.html', page_guides_index()))
    for g in content.GUIDES:
        written.append(write('guides/%s.html' % g['slug'], page_guide(g)))
    written.append(write('about.html', page_about()))
    written.append(write('privacy.html', page_privacy()))
    written.append(write('imprint.html', page_imprint()))
    write('404.html', page_404())

    # ---- German, under de/ -------------------------------------------
    de = content.for_lang('de')
    L = LANGS['de']
    written.append(write(L['home'], page_index_de()))
    written.append(write(L['templates'], page_templates_de()))
    for t in TEMPLATES:
        written.append(write(L['template_dir'] + t['slug'] + '.html',
                             page_template(t, 'de')))
    written.append(write(L['examples'], page_examples_index('de')))
    for e in de.EXAMPLES:
        written.append(write(L['example_dir'] + e['slug'] + '.html',
                             page_example(e, 'de')))
    written.append(write(L['guides'], page_guides_index('de')))
    for g in de.GUIDES:
        written.append(write(L['guide_dir'] + g['slug'] + '.html', page_guide(g, 'de')))
    written.append(write(L['about'], page_about_de()))
    written.append(write(L['privacy'], page_privacy_de()))
    written.append(write(L['imprint'], page_imprint_de()))
    write('de/404.html', page_404_de())

    indexable = [p for p in written] + ['editor.html']
    indexable.sort(key=lambda p: (p.count('/'), p))
    write('sitemap.xml', sitemap(indexable))
    write('robots.txt', robots())
    write('site.webmanifest', manifest())
    write('ads.txt', ads_txt())
    patch_editor()

    print('%d pages, sitemap with %d urls, domain %s'
          % (len(written) + 1, len(indexable), DOMAIN))
    if 'YOUR-DOMAIN' in DOMAIN:
        print('note: assets/site-config.js still has the placeholder domain')


if __name__ == '__main__':
    main()
