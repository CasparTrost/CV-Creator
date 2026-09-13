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
  icons.css             The icon set, generated from tools/icons.py
api/                    The only server: a Cloudflare Worker for the AI features
  prompts.js            The system prompts. The part that decides whether the
                        AI features are useful or dangerous.
  pdf.js                Text out of a PDF, without a library
tools/                  Generators. Not served, not needed to run the site.
  icons.py              The 32 icons, as SVG. One source for site and editor.
  mock-ki.py            The canned AI replies. tools/serve.py serves them
                        itself, so the features can be clicked through
                        without a key, a deployment or a cent.
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
| `python3 tools/serve.py [port]` | Serves the site locally: 404 handling, no caching, and the AI test mode under `/api` |
| `tools\serve.cmd [port]` | The same, for Windows |
| `tools\ki-start.cmd` | Starts the AI worker on this machine (asks for the key once, then `wrangler dev`) |
| `tools\holen.cmd` | Pulls the newest version on Windows, discarding generated files first |

Python 3.8 or newer is the only requirement, and only for the tools — the
site itself is plain HTML and needs nothing.

`assets/pdf-text.js` and the rendered pages are generated: running
`build.py` rewrites them, and a `git pull` then refuses to overwrite what
looks like local work. It is not local work — throw it away
(`git checkout -- assets/pdf-text.js`) and pull again, or let
`tools\holen.cmd` do both. Whoever changes `api/pdf.js` runs `build.py`
before committing, or everyone else inherits exactly that conflict.

Page copy lives in `tools/content.py` and `tools/content_de.py` (`GUIDES` and
`EXAMPLES`) and in the `page_*` functions of `tools/build.py` (everything else). Template descriptions are in
`tools/data/templates.json`.

## How the editor is built

The window is split in two: the **whole left side is the control panel**, the
**whole right side is the sheet**. The panel takes 40vw (with a 430px floor
and a 700px ceiling so it neither collapses on a laptop nor sprawls on a
28-inch screen) and the stage takes what is left. 40/60 rather than 50/50
because the panel is a grid of small controls that fits comfortably in the
narrower half, while the sheet is a fixed-aspect A4 page that turns every
extra millimetre into legibility.

The point of the split is that nothing is hidden behind a scroll. The panel
is a two-column grid of cards: the sixteen layouts sit at the top as a strip
of page-shaped tiles (eight per row, named in their tooltip and in the panel
header), then text, then colours beside typeface and photo beside view, then
the export row. At 1600×1000 and at 1440×900 the panel needs no scrolling at
all.

The sheet fits itself to whatever the stage has left: `zoomAnpassen()` divides
the available width by 793.7px (210mm at 96dpi) and snaps the result to the
nearest 5%. It steps aside permanently the moment the zoom slider is touched,
because an automatic value that overrides a deliberate one is a bug. Below
1150px the two panes stack instead, panel first.

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

- Each column ends in a visible slot, and clicking it adds a section in
  **that** column — the sidebar slot fills the sidebar, the main slot fills
  the main column. Dragging a section by its handle drops it into either.
  A slot is only drawn where it can actually be clicked: it may reach into
  the sheet's bottom margin (it never prints), it becomes shallower when
  space is tight, and on a column that is full to the edge it is left out
  rather than drawn half off the page. Because a full column can therefore
  have no slot, the panel carries both `+ Section` and `+ in sidebar`, so
  every column stays reachable however full the page is.
- Single-column layouts are the same grid with one track: the main column
  first, the sidebar's sections below it, and the contact block lifted to the
  front so the address is under the header rather than behind the job history.
- The slots are interface, not document: `.platz` is hidden in print. Every
  measurement of what still fits runs inside `inDruckmass()`, which hides the
  slots **and sets the zoom back to 100%**. Both matter. Measured at the
  visitor's zoom, a line wraps differently at 90% than at 110%, and whether
  the last section still fitted on page one came down to the zoom slider —
  two people with the same resume got different PDFs. Measuring at print
  scale is the only way the screen and the PDF can be the same document.
- **The sheet follows the content.** Adding or removing a section changes how
  much room the document needs, so the geometry is derived, never fixed:
  a page whose sidebar holds no sections drops its tinted panel — an empty
  block of colour reads as a fault, not as design — and if no page uses the
  sidebar at all, the sheet becomes single-column with the main column at
  full width and the sidebar's slot waiting underneath, labelled, so it can
  be brought back. Page two is the same idea: it appears by itself when
  page one overflows and disappears when nothing is left on it, which is why
  the manual "page 2 on/off" switch is gone — and why a one-page resume no
  longer prints a blank second sheet. `neuOrdnen()` is the single pass that
  does all of it (header height, areas, page two, distribution, slots,
  overflow warning) and every structural change calls it. Typing does not:
  moving a section out from under the caret mid-sentence is worse than a
  late re-flow, so text edits only re-colour and re-check, and `Rearrange`
  in the panel forces a full pass.
- A draft in `localStorage` carries the structure it was saved with, so a
  visitor who used an earlier version would get that structure back and see
  something other than the current layout. `strukturReparieren()` lifts the
  sections out of whatever shape it finds — today's columns, the row grid
  that briefly existed, or the original absolute columns — and puts them into
  the current one. The draft is never discarded: it is the visitor's work.

`tools/` has no test runner, but the checks used while building this are worth
knowing about: render all sixteen layouts, measure where each column starts
and ends, and compare those numbers against the previous commit. That is how
a 4.5mm gutter that had quietly vanished from seven layouts was found. Two
more are worth repeating after any change to the editor: click every visible
slot and assert the section appears in that slot's own column, and print the
same resume from two different window widths and diff the PDFs — they must
be byte-for-byte the same story.

## The three AI features

The editor can read an existing CV into a layout, tailor a CV to one job
advert, and review a finished CV. Both are off until `assets/site-config.js` has the address of
the worker in `api/` — without it the buttons are not rendered at all, and the
editor is exactly what it was: a page with no server.

**Why there is a server at all.** An API key in the browser is a published
key. The worker holds it, limits what goes through, and is the only
server-side code in this repository. Setup, cost and the rate limit are in
[`api/README.md`](api/README.md).

**The rule the prompts enforce.** The model may rephrase, reorder and
re-emphasise. It may never add a fact. Every employer, title, date, figure and
language level is copied character for character; "supported" may not become
"led"; a vague statement may not be made specific. What the advert asks for
and the CV does not show is listed back to the applicant as a gap — never
written into the CV. That is the honest half of the answer and often the
useful one.

Three things check the result, because one is not enough:

1. The prompt states the rule and gives the test to apply to every sentence:
   *could this be answered in an interview from what the original says?*
2. A second, cheap model call compares the rewrite against the original and
   reports sentences that claim more than the original supports.
3. The browser itself, independent of any model, collects every number, year
   and acronym in the new text and flags any that appears nowhere in the old
   one. A model that invents usually invents exactly there.

Whatever survives all three is still shown as a diff — what was there before,
what it says now, and why — and the dialog says plainly that the applicant is
the one signing it.

**The review.** *Lebenslauf prüfen* returns three things and no filler: what
carries the application, what stands out (ranked, most serious first, each
with the spot in the document and one concrete instruction), and the questions
this CV invites in an interview — each with the entry that provokes it and a
line of argument built only from what the CV already says. With a job advert
pasted in, it adds a fit score: the share of the advert's requirements the CV
actually evidences, musts weighted double, rounded to five, with every
requirement listed as met or open. The same score appears after a tailoring
run.

Gaps, overlaps, four-month stints and missing end dates are **computed in the
browser** from the dates and handed to the model as given facts. Date
arithmetic is the one job a language model reliably gets wrong and code never
does; judgement is the one it is for. And the advice on a gap is never to
conceal it — name it in a line and move on.

**Uploads.** Everything is read **in the browser**: DOCX, ODT and XLSX are ZIP
archives that `DecompressionStream` unpacks without a library, and PDFs go
through the same reader the worker uses — page objects, font resources,
`ToUnicode` maps — generated into `assets/pdf-text.js` from `api/pdf.js` so
there is one source. Only the extracted text is sent, which is faster,
cheaper and gives less away; the whole file goes out only when the text comes
back unusable, as it does for a scan. The dialog shows how many characters
were recognised and the first lines of them **before** anything is sent, so a
failed read is visible rather than silent. During development the dev
server answers `/api/…` itself with canned replies, and the editor finds them
on localhost without anything being configured — labelled *Testbetrieb* in the
panel, because a test mode mistaken for the real thing is worse than none.

A real worker running next to it wins that competition automatically: the
editor asks `localhost:8787` once at startup, and if something answers, it
uses that and drops the badge. So `tools\ki-start.cmd` (or `npx wrangler dev`
in `api/`) is the whole step from canned replies to a real model — nothing to
edit, nothing to undo afterwards.

**Switching it on changes the site's own claims.** The build reads the config:
with an AI endpoint set, the privacy pages gain a section on what is sent
where and on what legal basis, and the "nothing is uploaded" promise on both
home pages gains its exception. Both revert if the endpoint is emptied. A
privacy notice that omits a feature is worse than none.

## The icon set

Thirty-two line icons live in `tools/icons.py`, each one the inside of a
24x24 SVG drawn with 2px strokes and nothing else. `python3 tools/build.py`
turns that table into two things: `assets/icons.css` for the site pages, and
the variable block between the two marks in `editor.html` for the resume
itself. Edit an icon in the table and both follow; edit them anywhere else and
the next build overwrites you.

They are **masks, not images**. The shape is cut out of a colour the page
already has, so one definition covers every situation: a section heading takes
the accent colour, the same icon in a dark sidebar takes the white of the text
around it, and nothing needs a second file for a dark background. It is also
why they cost about 400 bytes each and stay sharp at any zoom, which a
generated PNG sheet of the same 28 icons would not.

In the resume, **the heading decides its own icon.** `rubrikSymbole()` matches
the text against a list of patterns, so renaming *Kompetenzen* to
*IT-Kenntnisse* swaps the gear for the code window, in German, English or
Spanish, and a heading nobody recognises simply has no icon rather than a
wrong one. The contact block is deliberately left out: every line there
already carries its own. `Symbole ein / aus` in the panel switches the lot off
for anyone who wants the plain sheet, and because the class sits on the page it
survives a reload with the draft.

On the site the mapping is by slug — `GUIDE_ICON` and `EXAMPLE_ICON` in
`tools/build.py` — so the guide about cover letters gets the envelope and the
nursing example gets the stethoscope. The class is `.sym`, not `.ic`: the house
promo has used `.ic` for its colour block since the first version, and a mask
rule on that name turned it into a solid square.

## The landing page

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
