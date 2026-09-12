# PlainSheet

A resume builder and a small publication around it. Everything is static HTML
served exactly as it sits in this repository — no framework, no server, no
database. The editor runs entirely in the visitor's browser; the pages around
it carry the advertising that pays for the hosting.

```
index.html              Landing page (English)
templates.html          Gallery of all sixteen layouts
templates/*.html        One page per layout
guides/*.html           Twelve guides, plus the guides index
examples/*.html         Eight worked resume examples by occupation
about.html              Who runs it and how it is paid for
privacy.html            Privacy notice, contains two placeholders
imprint.html            Imprint and contact, contains placeholders
404.html                Not-found page

de/                     The German site, with German slugs
  index.html            Startseite
  lebenslauf-vorlagen.html
  vorlagen/*.html       Sixteen layouts, German copy
  ratgeber/*.html       Eight guides written for the DACH market
  muster/*.html         Four worked examples by occupation
  ueber-uns.html, datenschutz.html, impressum.html

editor.html             The editor. Accepts ?t=t1 … ?t=t16 and ?lang=de
assets/                 Stylesheet, scripts, self-hosted fonts, icons
tools/                  Generators. Not served, not needed to run the site.
```

## Two languages, one codebase

The German tree is not a translation. A DACH application follows different
rules — photo, Anschreiben, Arbeitszeugnis, month-accurate dates — and the
topics people search for there do not exist in the English set. `tools/i18n`
lives in the `LANGS` table at the top of `tools/build.py`; German copy is in
`tools/content_de.py`.

What follows the language automatically: the navigation and footer, the
breadcrumbs, the consent notice (`assets/consent.js` reads
`document.documentElement.lang`), the ad label — *Anzeige* rather than
*advertisement*, which German law expects — the house promos, the editor
interface, and `hreflang` pairs on every page that exists in both.

Pages know their own depth through `data-root` on `<html>`, written by the
generator, so the scripts never guess from the URL.

## Looking at it locally

```sh
git clone https://github.com/CasparTrost/CV-Creator.git
cd CV-Creator
python3 tools/serve.py          # http://localhost:8000
```

On Windows the command is `py`, not `python3`, so either run
`py tools\serve.py` or double-click `tools\serve.cmd`, which finds whichever
Python is installed and says what to install if there is none.

`tools/serve.py` also serves `404.html` for a missing path and sends
`Cache-Control: no-store`, so a reload after `tools/build.py` shows the new
page rather than the old one. `python3 -m http.server` works too and does
neither.

Open the site over `http://localhost`, not by double-clicking a file: over
`file://` Chrome blocks browser storage, so neither the cookie notice nor
the editor's draft behaves correctly.

Worth clicking through: the language switch at the right of the navigation,
a guide, a worked example, the editor (type something, reload the tab, watch
the draft come back), and the cookie notice — accept, then reopen it from the
footer. In the editor, step through all sixteen layouts: each one is expected
to hold the sample on a single page with nothing clipped.

**The ad slots are already visible.** `assets/site-config.js` ships with the
placeholder publisher ID `ca-pub-0000000000000000`, and in that one case each
slot draws its own outline, its label and its name — so you can see exactly
where advertising will sit before AdSense has answered. Google serves nothing
against that ID and no cookie is set until a visitor accepts. Replace it with
your own ID after approval (the outline disappears by itself), or set it back
to `''` to hide the slots entirely.

**To get the cookie notice back**, run `Consent.reset()` in the browser
console, or clear site data for localhost.

## Going live

### 1. Fill in `assets/site-config.js`

It is the only file that needs editing. Domain, operator name, contact address,
AdSense publisher ID, ad unit IDs and the analytics choice all live there.

### 2. Run the build

```sh
python3 tools/build.py
```

This renders all 79 pages from `tools/build.py`, `tools/content.py` and
`tools/content_de.py`, stamps the
domain into every canonical URL, every `og:` tag and the editor, and regenerates
`sitemap.xml`, `robots.txt`, `site.webmanifest` and `ads.txt`.

The site is *served* without a build step; the generator exists so that eighty
pages in two languages can share one header, one footer and one set of meta tags. Commit whatever
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
| `python3 tools/build.py` | Renders every page in both languages, the sitemap, robots.txt, the manifest and ads.txt |
| `python3 tools/fetch-fonts.py` | Re-downloads the self-hosted webfonts |
| `python3 tools/make-images.py` | Regenerates the favicons and `assets/og.png` (needs Pillow) |
| `node tools/make-hero.js` | Re-photographs the editor for the landing pages (needs Playwright and a running server) |
| `python3 tools/serve.py [port]` | Serves the site locally with 404 handling and no caching |
| `tools\serve.cmd [port]` | The same, for Windows |

Python 3.8 or newer is the only requirement, and only for the tools — the
site itself is plain HTML and needs nothing.

Page copy lives in `tools/content.py` and `tools/content_de.py` (`GUIDES` and
`EXAMPLES`) and in the `page_*` functions of `tools/build.py` (everything else). Template descriptions are in
`tools/data/templates.json`.

## How the editor is built

The sheet has two columns, and they are **tracks of a grid** rather than
absolutely positioned boxes. That is what guarantees they begin at the same
height and cannot drift against each other, which is what went wrong before.
Inside a column the sections flow.

They flow rather than sitting in a strict row-by-row grid for a measured
reason. Aligning every section with its neighbour across both columns sounds
tidier, and it was the first thing tried here — but a row is as tall as its
taller side, so the page loses around 90mm of usable height. On this sample
that is the difference between a one-page and a two-page resume, and it
pushed the skills and languages sections off page one entirely. Columns that
start together and then flow independently is the right trade.

- Each column ends in a visible slot. Clicking it adds a section exactly
  there; dragging a section by its handle drops it into either column.
- Single-column layouts are the same grid with one track: the main column
  first, the sidebar's sections below it, and the contact block lifted to the
  front so the address is under the header rather than behind the job history.
- The slots are interface, not document: `.platz` is hidden in print. Because
  of that, every measurement of what still fits on a page runs inside
  `inDruckmass()`, which hides them first — otherwise the editor distributes
  content against a fuller page than the one that prints, and the promise of
  the tool is that the two are identical.
- A draft in `localStorage` carries the structure it was saved with, so a
  visitor who used an earlier version would get that structure back and see
  something other than the current layout. `strukturReparieren()` lifts the
  sections out of whatever shape it finds — today's columns, the row grid
  that briefly existed, or the original absolute columns — and puts them into
  the current one. The draft is never discarded: it is the visitor's work.

`tools/` has no test runner, but the checks used while building this are worth
knowing about: render all sixteen layouts, measure where each column starts
and ends, and compare those numbers against the previous commit. That is how
a 4.5mm gutter that had quietly vanished from seven layouts was found.

## The landing page## The landing page

It answers one question above anything else: *what is this?* Headline, one
sentence, one button, then a photograph of the editor itself — taken by
`tools/make-hero.js`, so it shows the real product rather than an
illustration of it. The step-by-step "how it works" blocks are gone: a tool
that needs instructions on its own landing page has a different problem.

Below that, in order: three facts, the layouts, a worked example, the
guides, and the questions people actually ask.

## Still worth doing

- More German occupations. There are four in `de/muster/` against eight in
  English; Erzieherin, Verkäuferin, Elektroniker and Bürokauffrau are the
  obvious next ones.
- A Spanish tree. The editor already speaks Spanish, so `LANGS` would take an
  `es` entry and the content would need writing.
- Once AdSense is approved, compare the fixed slots against Auto ads on a
  fraction of traffic before deciding which earns more.

## What this will and will not do

The site is built properly, which is a precondition and not a result. Free
resume builders are one of the most contested niches in search: Zety,
resume.io, Novoresume, Canva and Indeed all outrank a new domain on every
English query worth having, and they buy traffic on top. Expect close to
nothing from English organic search for the first six months.

The German tree is the better bet, and the reason it exists: fewer well-made
competitors, and most international ones serve machine-translated pages that
get the DACH conventions wrong. It is still a market with incumbents.

What moves the needle beyond content: a domain that ages, links from places
where people discuss job applications, and the fact that this tool is
genuinely free with no paywall at the download — which is a story worth
telling in the places that would otherwise never link to a resume site.
- Once AdSense is approved, compare the fixed slots against Auto ads on a
  fraction of traffic before deciding which earns more.
