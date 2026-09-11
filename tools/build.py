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
import json
import os
import re
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = datetime.date.today().isoformat()

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import content  # noqa: E402  (guide and page copy)


# ---------------------------------------------------------------- config

def read_config():
    src = open(os.path.join(ROOT, 'assets', 'site-config.js')).read()

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
    }


CFG = read_config()
DOMAIN = CFG['domain']
BRAND = 'PlainSheet'
TEMPLATES = json.load(open(os.path.join(ROOT, 'tools', 'data', 'templates.json')))
BY_ID = {t['tid']: t for t in TEMPLATES}


# ---------------------------------------------------------------- helpers

def up(depth):
    return '../' * depth


def esc(text):
    return (text.replace('&', '&amp;').replace('<', '&lt;')
                .replace('>', '&gt;').replace('"', '&quot;'))


def head(title, description, path, depth, extra_ld=None, image='assets/og.png',
         published=None, modified=None, kind='website', noindex=False):
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

    parts = [
        '<!DOCTYPE html>',
        '<html lang="en">',
        '<head>',
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<title>%s</title>' % esc(title),
        '<meta name="description" content="%s">' % esc(description),
        '<link rel="canonical" href="%s">' % url,
    ]
    if noindex:
        parts.append('<meta name="robots" content="noindex, follow">')
    parts += [
        '<meta name="theme-color" content="#1F5F5B">',
        '',
        '<meta property="og:type" content="%s">' % ('article' if kind == 'article' else 'website'),
        '<meta property="og:site_name" content="%s">' % BRAND,
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
              '<a class="skip" href="#main">Skip to content</a>']
    return '\n'.join(parts)


NAV = [
    ('templates.html', 'Templates'),
    ('guides/index.html', 'Guides'),
    ('about.html', 'About'),
]


def topbar(active, depth):
    u = up(depth)
    links = []
    for href, label in NAV:
        current = ' aria-current="page"' if href == active else ''
        links.append('      <a href="%s%s"%s>%s</a>' % (u, href, current, label))
    return '\n'.join([
        '<header class="topbar">',
        '  <div class="wrap">',
        '    <a class="wordmark" href="%sindex.html">Plain<b>Sheet</b></a>' % u,
        '    <button class="navtoggle" type="button" aria-expanded="false" '
        'aria-controls="nav" aria-label="Menu" onclick="var n=document.getElementById(\'nav\');'
        'n.classList.toggle(\'open\');this.setAttribute(\'aria-expanded\',n.classList.contains(\'open\'))">',
        '      <svg viewBox="0 0 18 14" aria-hidden="true"><path d="M0 1h18M0 7h18M0 13h18" '
        'stroke="currentColor" stroke-width="1.6"/></svg>',
        '    </button>',
        '    <nav class="topnav" id="nav">',
        '\n'.join(links),
        '      <a class="btn" href="%seditor.html">Open the editor</a>' % u,
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


def cta(depth, heading='Now put it on a page',
        text='The editor opens with a filled-in example. Replace the text, pick a layout, '
             'print to PDF. Nothing is uploaded and nothing costs anything.',
        label='Open the editor', href='editor.html'):
    return ('<div class="cta">\n  <div>\n    <h3>%s</h3>\n    <p>%s</p>\n  </div>\n'
            '  <a class="btn" href="%s%s">%s</a>\n</div>'
            % (heading, text, up(depth), href, label))


def footer(depth):
    u = up(depth)
    tiles = ''.join(
        '<li><a href="%stemplates/%s.html">%s</a></li>' % (u, t['slug'], t['name'])
        for t in TEMPLATES[:6])
    guides = ''.join(
        '<li><a href="%sguides/%s.html">%s</a></li>' % (u, g['slug'], g['short'])
        for g in content.GUIDES[:6])
    return '\n'.join([
        '<footer>',
        '  <div class="wrap">',
        '    <div class="cols">',
        '      <div>',
        '        <a class="wordmark" href="%sindex.html">Plain<b>Sheet</b></a>' % u,
        '        <p class="fine">A resume editor that runs entirely in your browser. Nothing you',
        '        type is uploaded, stored or sold. The PDF export is free and always will be.</p>',
        '      </div>',
        '      <div>',
        '        <h3>Templates</h3>',
        '        <ul>%s<li><a href="%stemplates.html">All sixteen</a></li></ul>' % (tiles, u),
        '      </div>',
        '      <div>',
        '        <h3>Guides</h3>',
        '        <ul>%s<li><a href="%sguides/index.html">Every guide</a></li></ul>' % (guides, u),
        '      </div>',
        '      <div>',
        '        <h3>Site</h3>',
        '        <ul>',
        '          <li><a href="%seditor.html">Editor</a></li>' % u,
        '          <li><a href="%sabout.html">About</a></li>' % u,
        '          <li><a href="%sprivacy.html">Privacy and cookies</a></li>' % u,
        '          <li><a href="%simprint.html">Imprint and contact</a></li>' % u,
        '          <li><button type="button" class="lnk" data-consent-settings>Cookie settings</button></li>',
        '        </ul>',
        '      </div>',
        '    </div>',
        '    <p class="fine">© %s %s. Operated by %s. '
        'This site is paid for by advertising; the editor itself carries none.</p>'
        % (datetime.date.today().year, BRAND, esc(CFG['operator'] or '[your name]')),
        '  </div>',
        '</footer>',
        '</body>',
        '</html>',
    ])


def write(path, html):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w') as fh:
        fh.write(html.rstrip() + '\n')
    return path


# ---------------------------------------------------------------- pieces

def toc(body):
    """Build a table of contents from the h2 landmarks in an article."""
    heads = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body, re.S)
    if len(heads) < 3:
        return ''
    items = ''.join('<li><a href="#%s">%s</a></li>' % (i, re.sub(r'<[^>]+>', '', t))
                    for i, t in heads)
    return ('<aside class="toc"><strong>On this page</strong><ol>%s</ol></aside>' % items)


def inject_mid_ad(body, slot):
    """Put an ad before whichever h2 sits nearest the middle of the article."""
    positions = [m.start() for m in re.finditer(r'<h2 id=', body)]
    if len(positions) < 4:
        return body
    middle = len(body) / 2
    cut = min(positions[1:-1], key=lambda p: abs(p - middle))
    return body[:cut] + ad('guide-' + slot, wrapped=False) + '\n\n' + body[cut:]


def guide_card(g, depth, prefix='guides/'):
    """prefix='' means the card sits in guides/ already and links sideways."""
    href = ('%s%s%s.html' % (up(depth), prefix, g['slug'])) if prefix else '%s.html' % g['slug']
    return ('<a class="card" href="%s">'
            '<span class="tag">%s</span>'
            '<h3>%s</h3>'
            '<p>%s</p>'
            '<span class="mins">%d min read</span></a>'
            % (href, esc(g['tag']), esc(g['h1']),
               esc(g['dek'].split('.')[0] + '.'), g['minutes']))


def template_tile(t, depth, prefix='templates/'):
    return ('<a class="tile" href="%s%s%s.html"><div class="sheet">%s</div>'
            '<h3>%s</h3><span>%s</span></a>'
            % (up(depth), prefix, t['slug'], t['svg'], esc(t['name']), esc(t['tagline'])))


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
    depth = 0
    faq, faq_ld = faq_block([
        ('Is the download really free?',
         'Yes. The export is a browser print to PDF, so there is nothing for us to charge for '
         'and no watermark to remove. The site is paid for by advertising on the pages around '
         'the editor, not by the editor.'),
        ('Do I need an account?',
         'No. There is no sign-up because there is no server storing anything. Use Save file '
         'to keep a copy on your own machine, and open that file again to carry on.'),
        ('Will it pass an applicant tracking system?',
         'Single-column layouts such as Linden and Plainfield parse most reliably. Sidebar '
         'layouts look better to a human but can confuse parsers that read across columns. '
         'The guide on applicant tracking systems explains what actually breaks.'),
        ('Where is my data stored?',
         'In your browser, on your device. The editor keeps a working draft locally so a '
         'closed tab does not lose your work, and that draft never leaves the machine. '
         'Clearing your browser data removes it.'),
        ('Can I get it as a Word document?',
         'Yes, though Word receives a simplified table version. Diagonals and round photos '
         'are beyond what Word can draw reliably.'),
    ])
    software_ld = {
        '@context': 'https://schema.org',
        '@type': 'SoftwareApplication',
        'name': BRAND,
        'applicationCategory': 'BusinessApplication',
        'operatingSystem': 'Any browser',
        'url': DOMAIN + '/editor.html',
        'description': 'A resume builder that runs entirely in the browser, with sixteen '
                       'A4 layouts and a free PDF export.',
        'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'EUR'},
    }
    hero_svg = BY_ID['t1']['svg']

    return '\n'.join([
        head('Free resume builder with a real PDF export — %s' % BRAND,
             'Build a resume in your browser and download the PDF for free. Sixteen layouts, '
             'no account, no watermark, nothing uploaded to a server.',
             'index.html', depth, extra_ld=[software_ld, faq_ld]),
        topbar(None, depth),
        '',
        '<main id="main">',
        '<section class="hero">',
        '  <div class="wrap">',
        '    <div>',
        '      <p class="eyebrow">Free, no account, nothing uploaded</p>',
        '      <h1>Write it, see it, download it.</h1>',
        '      <p class="lead">A resume editor with a live A4 page in front of you. What you see '
        'is exactly what comes out of the PDF, down to the millimetre.</p>',
        '      <div class="actions">',
        '        <a class="btn" href="editor.html">Open the editor</a>',
        '        <a class="btn ghost" href="templates.html">Browse sixteen layouts</a>',
        '      </div>',
        '      <p class="aside-note">Everything runs inside your browser. Your resume is never '
        'sent anywhere, which also means there is no account to create and nothing to delete '
        'afterwards.</p>',
        '    </div>',
        '    <div class="sheet">%s</div>' % hero_svg,
        '  </div>',
        '</section>',
        '',
        '<section class="claims">',
        '  <div class="wrap">',
        '    <div><strong>The PDF is free</strong><p>No trial, no card, no watermark stamped '
        'across the page you worked on.</p></div>',
        '    <div><strong>Nothing leaves your machine</strong><p>The editor is a single page of '
        'code. There is no server holding your employment history.</p></div>',
        '    <div><strong>Sixteen layouts, one text</strong><p>Switch the design whenever you '
        'like. Your content stays where it is.</p></div>',
        '  </div>',
        '</section>',
        '',
        '<section class="band">',
        '  <div class="wrap">',
        '    <div class="band-head">',
        '      <h2>Start from a layout</h2>',
        '      <p>Each one is a finished A4 document, not a mood board. Pick the structure that '
        'fits how much you have to say.</p>',
        '    </div>',
        '    <div class="grid">%s</div>' % ''.join(
            template_tile(t, depth) for t in TEMPLATES[:8]),
        '    <p style="margin-top:30px"><a href="templates.html">See all sixteen layouts</a></p>',
        '  </div>',
        '</section>',
        '',
        ad('home-mid'),
        '',
        '<section class="band tight">',
        '  <div class="wrap">',
        '    <div class="band-head"><h2>How it works</h2></div>',
        '    <ol class="steps">',
        '      <li><h3>Replace the sample text</h3><p>The editor opens with a filled-in example. '
        'Click into any line and type over it.</p></li>',
        '      <li><h3>Move sections where you want them</h3><p>Drag a section by its handle into '
        'the other column or onto the second page.</p></li>',
        '      <li><h3>Save the PDF</h3><p>Print to PDF with margins set to none and background '
        'graphics switched on.</p></li>',
        '    </ol>',
        '  </div>',
        '</section>',
        '',
        '<section class="band tight">',
        '  <div class="wrap">',
        '    <div class="band-head">',
        '      <h2>Read this before you start</h2>',
        '      <p>The editor handles the layout. These handle the words, which is the part that '
        'decides whether anyone calls you.</p>',
        '    </div>',
        '    <div class="cards">%s</div>' % ''.join(
            guide_card(g, depth) for g in content.GUIDES[:3]),
        '    <p style="margin-top:26px"><a href="guides/index.html">All twelve guides</a></p>',
        '  </div>',
        '</section>',
        '',
        '<section class="band tight">',
        '  <div class="wrap">',
        '    <div class="band-head"><h2>Questions people ask</h2></div>',
        '    ' + faq,
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
             'templates.html', depth, extra_ld=[ld]),
        topbar('templates.html', depth),
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


def page_template(t):
    depth = 1
    others = [x for x in TEMPLATES if x['slug'] != t['slug']][:4]
    ld = {
        '@context': 'https://schema.org',
        '@type': 'CreativeWork',
        'name': '%s resume template' % t['name'],
        'about': t['tagline'],
        'url': '%s/templates/%s.html' % (DOMAIN, t['slug']),
        'isAccessibleForFree': True,
        'creator': {'@type': 'Organization', 'name': BRAND},
    }
    specs = ''.join('<li><span>%s</span><span>%s</span></li>' % (esc(a), esc(b))
                    for a, b in t['specs'])
    fits = ''.join('<li>%s</li>' % esc(f) for f in t['fits'])
    return '\n'.join([
        head(t['title'], t['description'], 'templates/%s.html' % t['slug'], depth,
             extra_ld=[ld]),
        topbar('templates.html', depth),
        crumbs([('index.html', 'Home'), ('templates.html', 'Templates'), (None, t['name'])],
               depth),
        '<main id="main">',
        '<section class="detail">',
        '  <div class="wrap">',
        '    <div class="sheet">%s</div>' % t['svg'],
        '    <div>',
        '      <p class="kicker">Resume template</p>',
        '      <h1 style="font-size:clamp(2rem,4vw,2.8rem)">%s</h1>' % esc(t['name']),
        '      <p class="lead">%s</p>' % esc(t['tagline']),
        '      <p>%s</p>' % t['body'],
        '      <h3 style="margin-top:26px">Pick this one if</h3>',
        '      <ul class="fits">%s</ul>' % fits,
        '      <a class="btn" href="../editor.html?t=%s">Use %s</a>' % (t['tid'], esc(t['name'])),
        '      <ul class="specs">%s</ul>' % specs,
        '    </div>',
        '  </div>',
        '</section>',
        ad('template-mid'),
        '<section class="band tight">',
        '  <div class="wrap">',
        '    <div class="band-head"><h2>Other layouts</h2></div>',
        '    <div class="grid">%s</div>' % ''.join(template_tile(x, depth) for x in others),
        '    <p style="margin-top:26px"><a href="../templates.html">All sixteen</a></p>',
        '  </div>',
        '</section>',
        '</main>',
        footer(depth),
    ])


def page_guides_index():
    depth = 1
    groups = []
    for tag in ['Starting out', 'Writing it', 'Getting read', 'Sending it', 'Special cases']:
        members = [g for g in content.GUIDES if g['tag'] == tag]
        if members:
            groups.append((tag, members))
    ld = {
        '@context': 'https://schema.org',
        '@type': 'ItemList',
        'name': 'Resume guides',
        'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': g['h1'],
             'url': '%s/guides/%s.html' % (DOMAIN, g['slug'])}
            for i, g in enumerate(content.GUIDES)],
    }
    # The pillar guide leads on its own; a lone card in a three-column grid
    # looks like a mistake rather than a starting point.
    lead = content.GUIDES[0]
    body = ['    <a class="feature" href="%s.html">'
            '<div><span class="tag">Start here</span><h3>%s</h3><p>%s</p></div>'
            '<span class="mins">%d min read</span></a>'
            % (lead['slug'], esc(lead['h1']), esc(lead['dek']), lead['minutes'])]
    first = True
    for tag, members in groups:
        members = [g for g in members if g is not lead]
        if not members:
            continue
        body.append('    <h2 style="margin:%s 0 20px">%s</h2>'
                    % ('0' if first else '54px', esc(tag)))
        body.append('    <div class="cards">%s</div>'
                    % ''.join(guide_card(g, depth, prefix='') for g in members))
        if not first and 'guides-mid' not in '\n'.join(body):
            body.append(ad('guides-mid', wrapped=False))
        first = False
    return '\n'.join([
        head('Resume guides — %s' % BRAND,
             'Twelve plain guides to writing a resume: bullet points, skills, length, '
             'applicant tracking systems, cover letters and the German Lebenslauf.',
             'guides/index.html', depth, extra_ld=[ld]),
        topbar('guides/index.html', depth),
        crumbs([('index.html', 'Home'), (None, 'Guides')], depth),
        '<main id="main">',
        '<section class="band">',
        '  <div class="wrap">',
        '    <div class="band-head">',
        '      <h1 style="font-size:clamp(2rem,4vw,2.9rem)">Guides</h1>',
        '      <p>The editor takes care of the layout. These are about the harder part: what '
        'to write on the page, in what order, and what gets a file put down after nine '
        'seconds. No sign-up, no course, no upsell at the end.</p>',
        '    </div>',
        '\n'.join(body),
        '  </div>',
        '</section>',
        '<section class="band tight">',
        '  <div class="wrap">',
        cta(depth),
        '  </div>',
        '</section>',
        '</main>',
        footer(depth),
    ])


def page_guide(g):
    depth = 1
    body = inject_mid_ad(g['body'].strip(), 'mid')
    faq, faq_ld = faq_block(g.get('faq'))
    article_ld = {
        '@context': 'https://schema.org',
        '@type': 'Article',
        'headline': g['h1'],
        'description': g['description'],
        'datePublished': g['updated'],
        'dateModified': g['updated'],
        'mainEntityOfPage': '%s/guides/%s.html' % (DOMAIN, g['slug']),
        'image': '%s/assets/og.png' % DOMAIN,
        'author': {'@type': 'Organization', 'name': BRAND, 'url': DOMAIN + '/about.html'},
        'publisher': {'@type': 'Organization', 'name': BRAND, 'url': DOMAIN + '/'},
    }
    related = [x for x in content.GUIDES if x['slug'] in g.get('related', [])]
    pretty = datetime.date.fromisoformat(g['updated']).strftime('%d %B %Y').lstrip('0')

    return '\n'.join([
        head('%s — %s' % (g['title'], BRAND), g['description'],
             'guides/%s.html' % g['slug'], depth, kind='article',
             published=g['updated'], modified=g['updated'],
             extra_ld=[article_ld] + ([faq_ld] if faq_ld else [])),
        topbar('guides/index.html', depth),
        crumbs([('index.html', 'Home'), ('guides/index.html', 'Guides'), (None, g['short'])],
               depth),
        '<main id="main">',
        '<article class="article">',
        '  <div class="wrap">',
        '    <div class="article-head">',
        '      <p class="kicker">%s</p>' % esc(g['tag']),
        '      <h1>%s</h1>' % esc(g['h1']),
        '      <p class="lead">%s</p>' % esc(g['dek']),
        '      <p class="article-meta"><span>%d min read</span><span>Updated %s</span>'
        '<span>Written by the %s team</span></p>' % (g['minutes'], pretty, BRAND),
        '    </div>',
        ad('guide-top', wrapped=False),
        '    <div class="article-cols">',
        '      <div class="article-body">',
        body,
        cta(depth),
        ad('guide-foot', wrapped=False),
        ('        <h2 id="faq">Common questions</h2>\n' + faq) if faq else '',
        '        <div class="nextprev">%s</div>' % ''.join(
            '<a href="%s.html"><span>Read next</span><strong>%s</strong></a>'
            % (x['slug'], esc(x['h1'])) for x in related[:2]),
        '      </div>',
        toc(g['body']),
        '    </div>',
        '  </div>',
        '</article>',
        '<section class="band tight">',
        '  <div class="wrap">',
        '    <div class="band-head"><h2>More guides</h2></div>',
        '    <div class="cards">%s</div>' % ''.join(
            guide_card(x, depth, prefix='') for x in related),
        '    <p style="margin-top:26px"><a href="index.html">Every guide</a></p>',
        '  </div>',
        '</section>',
        '</main>',
        footer(depth),
    ])


def page_about():
    depth = 0
    return '\n'.join([
        head('About %s' % BRAND, 'Who makes this resume builder, how it is paid for, and '
             'what it does with your data — which is nothing.',
             'about.html', depth),
        topbar('about.html', depth),
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
             'imprint.html', depth),
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


def page_privacy():
    depth = 0
    return '\n'.join([
        head('Privacy and cookies — %s' % BRAND,
             'What this site collects, what it does not, and exactly what happens when you '
             'accept or decline advertising cookies.',
             'privacy.html', depth),
        topbar(None, depth),
        crumbs([('index.html', 'Home'), (None, 'Privacy')], depth),
        '<main id="main">',
        '<section class="band">',
        '  <div class="wrap prose">',
        '    <h1 style="font-size:clamp(2rem,4vw,2.8rem)">Privacy and cookies</h1>',
        '    <p class="lead">The short version: your resume never leaves your device, the site '
        'sets no cookie until you say yes, and declining costs you nothing but the ads.</p>',
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


def patch_editor():
    """The editor is hand-written, so only its canonical and og: URLs are stamped."""
    path = os.path.join(ROOT, 'editor.html')
    src = open(path).read()
    fixed = re.sub(r'https://[A-Za-z0-9.\-]*YOUR-DOMAIN\.example', DOMAIN, src)
    fixed = re.sub(r'(<link rel="canonical" href=")[^"]*(">)',
                   r'\g<1>%s/editor.html\g<2>' % DOMAIN, fixed)
    fixed = re.sub(r'(<meta property="og:url" content=")[^"]*(">)',
                   r'\g<1>%s/editor.html\g<2>' % DOMAIN, fixed)
    if fixed != src:
        open(path, 'w').write(fixed)
    return 'editor.html'


def main():
    written = []
    written.append(write('index.html', page_index()))
    written.append(write('templates.html', page_templates()))
    for t in TEMPLATES:
        written.append(write('templates/%s.html' % t['slug'], page_template(t)))
    written.append(write('guides/index.html', page_guides_index()))
    for g in content.GUIDES:
        written.append(write('guides/%s.html' % g['slug'], page_guide(g)))
    written.append(write('about.html', page_about()))
    written.append(write('privacy.html', page_privacy()))
    written.append(write('imprint.html', page_imprint()))
    write('404.html', page_404())

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
