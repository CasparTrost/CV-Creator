# PlainSheet

A resume builder and a small publication around it. Everything is static HTML
served exactly as it sits in this repository — no framework, no server, no
database. The editor runs entirely in the visitor's browser; the pages around
it carry the advertising that pays for the hosting.

```
index.html          Landing page
templates.html      Gallery of all sixteen layouts
templates/*.html    One page per layout
guides/*.html       Twelve guides, plus the guides index
examples/*.html     Eight worked resume examples by occupation
editor.html         The editor, accepts ?t=t1 … ?t=t16
about.html          Who runs it and how it is paid for
privacy.html        Privacy notice, contains two placeholders
imprint.html        Imprint and contact, contains placeholders
404.html            Not-found page
assets/             Stylesheet, scripts, self-hosted fonts, icons
tools/              Generators. Not served, not needed to run the site.
```

## Going live

### 1. Fill in `assets/site-config.js`

It is the only file that needs editing. Domain, operator name, contact address,
AdSense publisher ID, ad unit IDs and the analytics choice all live there.

### 2. Run the build

```sh
python3 tools/build.py
```

This renders all 44 pages from `tools/build.py` and `tools/content.py`, stamps the
domain into every canonical URL, every `og:` tag and the editor, and regenerates
`sitemap.xml`, `robots.txt`, `site.webmanifest` and `ads.txt`.

The site is *served* without a build step; the generator exists so that forty-odd
pages can share one header, one footer and one set of meta tags. Commit whatever
it writes.

### 3. Publish

GitHub Pages: Settings → Pages → Deploy from a branch, `main`, folder `/ (root)`.
Cloudflare Pages and Netlify: connect the repository, leave the build command
empty, output directory `/`.

### 4. Finish the legal pages

- `imprint.html` — name, postal address, telephone. In Germany, Austria and
  Switzerland this is required even for a hobby site, and carrying ads makes it
  unambiguous. The bracketed placeholders mark what is missing.
- `privacy.html` — replace `[hosting provider]` with your host, twice.

### 5. Apply to AdSense

The site is built to meet the usual approval conditions: original written
content, an about page, a contact page, a privacy notice that names the ad
partner, working navigation and no dead ends. Approval still takes days to
weeks. Until the publisher ID is filled in, no ad code is requested and each
page shows one house promo in the first slot instead — the layout is already
final, so nothing shifts when real ads arrive.

## How the advertising works

Three files, in this order in every `<head>`:

| File | What it does |
| --- | --- |
| `assets/site-config.js` | The configuration above. No logic. |
| `assets/consent.js` | Declares every Google consent signal as denied, shows the notice, remembers the answer for 180 days, re-opens from any `data-consent-settings` element. |
| `assets/ads.js` | Fills `<div class="ad" data-slot="…">` once the slot approaches the viewport, and only if advertising was accepted. Loads analytics if configured. |

Nothing advertising-related is requested before a visitor answers. Rejecting
means no ad script is loaded at all, which is the conservative reading of the
GDPR and ePrivacy rules: AdSense sets cookies even for non-personalised ads.
`serveAfterReject` in the config exists if you take a different view of that
after taking advice.

Consent Mode v2 signals (`ad_storage`, `ad_user_data`, `ad_personalization`,
`analytics_storage`) are set to denied before any tag runs and updated on the
visitor's answer.

**One caveat worth knowing:** for traffic from the EEA and the UK, Google
requires publishers to use a CMP from its certified list. The notice here does
the technical job correctly — it gates the script and speaks Consent Mode — but
it is not itself on that list. Either register a certified CMP (Google's own
"Privacy & messaging" tool is free and appears in the AdSense interface) and
drop its snippet in place of `consent.js`, or check the current requirement for
your situation. `ads.js` works with either: it only ever asks
`window.Consent.allowsAds()`, so pointing that at another CMP is a few lines.

### Ad slots

| Page | `data-slot` |
| --- | --- |
| `index.html` | `home-mid` |
| `templates.html` | `templates-foot` |
| `templates/*.html` | `template-mid` |
| `guides/index.html` | `guides-mid` |
| `guides/*.html` | `guide-top`, `guide-mid`, `guide-foot` |
| `examples/index.html` | `examples-mid` |
| `examples/*.html` | `example-top`, `example-mid`, `example-foot` |
| `editor.html` | none, deliberately |

The editor carries no advertising. A visitor spends twenty minutes there and
produces a single page view, so ads would earn almost nothing while making the
tool worse. The guides and the examples are what earn: several page views per
visit, search traffic that arrives with intent, and the subject matter
advertisers pay for.

## Privacy decisions baked in

- **Fonts are self-hosted.** `tools/fetch-fonts.py` downloads the latin and
  latin-ext subsets into `assets/fonts/`. No visitor request reaches
  `fonts.gstatic.com`, which settles the Google Fonts question for EU operators
  and removes a render-blocking third-party connection.
- **The editor stores its draft locally.** `localStorage['ps.draft']` holds the
  current sheet so a closed tab does not cost an hour. It never leaves the
  device; "Start over" in the sidebar clears it.
- **A file saved with "Sichern" is self-contained.** It carries
  `data-gesichert` so that opening it later shows its own content rather than
  the browser's draft.

## Tools

| Command | What it does |
| --- | --- |
| `python3 tools/build.py` | Renders every page, the sitemap, robots.txt, the manifest and ads.txt |
| `python3 tools/fetch-fonts.py` | Re-downloads the self-hosted webfonts |
| `python3 tools/make-images.py` | Regenerates the favicons and `assets/og.png` (needs Pillow) |

Page copy lives in `tools/content.py` (`GUIDES` and `EXAMPLES`) and in the
`page_*` functions of `tools/build.py` (everything else). Template descriptions are in
`tools/data/templates.json`.

## Still worth doing

- German translations. The editor already speaks German, Spanish and English;
  the written content does not. A `/de/` tree with `hreflang` would roughly
  double the addressable search traffic for a German operator.
- More occupations. The eight in `examples/` cover the biggest search volumes;
  the structure takes another one in about twenty minutes of writing.
- Once AdSense is approved, compare the fixed slots against Auto ads on a
  fraction of traffic before deciding which earns more.
