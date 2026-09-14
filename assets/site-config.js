/* ==================================================================
   PlainSheet — the one file you edit before going live.
   Everything that differs between "my copy" and "the public site"
   lives here. No other file needs a publisher ID or a domain.
   ================================================================== */
window.PLAINSHEET = {

  /* Canonical origin, no trailing slash. Used by the consent notice and
     by tools/build.py, which stamps it into the HTML head of every
     page, robots.txt and sitemap.xml. */
  domain: 'https://caspartrost.github.io/CV-Creator',

  /* Soll diese Fassung in Suchmaschinen auftauchen? Eine Probefassung unter
     einer vorläufigen Adresse gehört nicht in den Index: Was Google dort
     aufnimmt, konkurriert später mit der richtigen Domain, und weg ist es
     nicht an einem Tag. Auf false setzt build.py auf jeder Seite
     „noindex, follow“ und in robots.txt ein Disallow.
     Auf true stellen, sobald die endgültige Adresse steht. */
  indexierung: false,

  /* Who runs the site. Shown on the imprint and contact pages. */
  operator: {
    name: '[Your name or company]',
    email: '[you@example.com]'
  },

  ads: {
    /* Master switch. false keeps every slot empty and the site clean,
       which is what you want while AdSense is still reviewing you. */
    enabled: true,

    /* Your AdSense publisher ID.
       This is a placeholder so that the ad slots are visible in the
       layout: they render as labelled, empty units exactly where real
       ads will sit. Google serves nothing against it, and no cookie is
       set until a visitor accepts. Replace it with your own ID once
       AdSense has approved the site — or set it back to '' to hide the
       slots and show a single house promo instead. */
    client: '',

    /* Ad unit IDs from AdSense, one per placement. A placement with an
       empty ID falls back to the house promo. If you use Auto ads you
       can leave these empty and let Google place the units itself. */
    slots: {
      'home-mid': '',
      'templates-foot': '',
      'template-mid': '',
      'guides-mid': '',
      'examples-mid': '',
      'example-top': '',
      'example-mid': '',
      'example-foot': '',
      'guide-top': '',
      'guide-mid': '',
      'guide-foot': ''
    },

    /* Ads are requested only once a visitor accepts them. Leave this
       false: AdSense sets cookies even for non-personalised ads, so
       serving them after a "reject" is not something we do. */
    serveAfterReject: false,

    /* Slots fill when they come within this many pixels of the viewport.
       Keeps ads off screens nobody scrolls to, which lifts viewability. */
    lazyMargin: 500
  },

  /* Die beiden KI-Funktionen im Editor: einen vorhandenen Lebenslauf
     einlesen und einen Lebenslauf auf eine Stellenanzeige zuschneiden.
     Sie brauchen den Worker aus api/ — ohne Adresse bleiben die Knöpfe
     weg, und der Editor ist wie zuvor eine Seite ohne Server.
     Adresse eintragen, die wrangler deploy ausgegeben hat, mit /api am Ende. */
  ki: {
    endpunkt: '',
    anbieter: 'CometAPI',      /* steht so im Hinweis vor dem ersten Senden */
  },

  analytics: {
    /* 'none' | 'plausible' | 'ga4'
       plausible is cookieless and loads immediately.
       ga4 waits for consent to the measurement category. */
    provider: 'none',
    /* Plausible: your domain. GA4: the G-XXXXXXX measurement ID. */
    id: ''
  },

  consent: {
    /* Re-ask after this many days. */
    remember: 180,
    /* Bump this when the wording or the categories change; every stored
       decision made under an older version is asked again. */
    version: 1
  }
};
