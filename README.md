# PlainSheet

A resume builder that runs entirely in the browser. No server, no database,
no build step. Every file in this repository is served as-is.

## Contents

| Path | What it is |
| --- | --- |
| `index.html` | Landing page |
| `templates.html` | Gallery of all sixteen layouts |
| `templates/*.html` | One page per layout, sixteen in total |
| `editor.html` | The editor itself; accepts `?t=t1` … `?t=t16` |
| `privacy.html` | Privacy notice, **contains placeholders** |
| `assets/site.css` | Stylesheet for the site pages |
| `ads.txt` | Ad network authorisation, **contains a placeholder** |
| `robots.txt`, `sitemap.xml` | **Contain a placeholder domain** |

## Publishing with GitHub Pages

1. Push this repository to GitHub.
2. Settings → Pages → Source: *Deploy from a branch*, branch `main`, folder `/ (root)`.
3. Wait a minute, then open `https://<user>.github.io/<repo>/`.

Cloudflare Pages and Netlify work the same way: connect the repository,
leave the build command empty, set the output directory to `/`.

## Before going live

1. Replace `https://YOUR-DOMAIN.example` in `sitemap.xml`, `robots.txt` and the
   `<link rel="canonical">` of every page with the real domain.
2. Fill in the bracketed placeholders in `privacy.html` and the imprint line in
   every footer.
3. Put the line your ad network gives you into `ads.txt`.
4. Install a Google-certified consent tool in the `<head>` of every page,
   before any ad code. Ads must not load until consent is given.
5. Paste ad units inside the `<div class="ad">` wrappers. Keep the wrapper so
   the slot reserves its height and the page does not jump on load.

## Ad slots

| Page | `data-slot` |
| --- | --- |
| `index.html` | `home-mid` |
| `templates.html` | `templates-foot` |
| `templates/*.html` | `template-mid` |
| `editor.html` | none, deliberately |

The editor carries no advertising. A visitor spends twenty minutes there and
produces a single page view, so ads earn almost nothing while making the tool
worse. The content pages are what earn.

## Not done yet

Guides and profession-specific examples. Those generate several page views per
visit where the editor generates one, and ad networks frequently reject sites
that are a tool with no written content.
