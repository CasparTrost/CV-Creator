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
  indexierung: true,

  /* Wer die Seite betreibt. Steht im Impressum, in der
     Datenschutzerklärung und im Fuß jeder Seite — hier einmal, dort
     überall. § 5 DDG verlangt Name, Anschrift und eine Möglichkeit zur
     unmittelbaren Kontaktaufnahme; bei einer Personengesellschaft dazu
     die Vertretungsberechtigten.

     `zusatz` ist die Zeile zwischen Name und Straße (c/o, Postfachnummer
     eines Dienstleisters). `verantwortlich` ist die natürliche Person nach
     § 18 Abs. 2 MStV: Ratgebertexte sind journalistisch-redaktionelle
     Inhalte, und die verlangen einen Menschen mit Namen, keine Firma.

     Eine Telefonnummer ist nicht eingetragen und auch nicht verlangt — der
     EuGH hat entschieden, dass eine E-Mail-Adresse genügt, solange sie
     wirklich gelesen wird (C-298/07). Eine USt-IdNr. steht nur da, wenn es
     eine gibt; sonst bleibt das Feld leer und der Abschnitt fällt weg. */
  operator: {
    name: 'Caspar Trost & Tim Josse GbR – Brozilla',
    vertreter: 'Caspar Trost, Tim Josse',
    verantwortlich: 'Caspar Trost',
    zusatz: 'c/o Autorenglück #73812',
    strasse: 'Albert-Einstein-Straße 47',
    ort: '02977 Hoyerswerda',
    land: 'Deutschland',
    landEn: 'Germany',
    ustid: '',
    register: '',
    telefon: '',
    email: 'info@brozillattv.de'
  },

  /* Wer die Seiten ausliefert. Steht in der Datenschutzerklärung beim
     Abschnitt über Server-Logfiles und muss mitwandern, wenn die Seite
     einmal woanders liegt. */
  hoster: {
    name: 'GitHub, Inc.',
    dienst: 'GitHub Pages',
    anschrift: '88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, USA'
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
      'guide-foot': '',
      /* Die Fläche im Editor-Fenster. */
      'editor-arbeit': ''
    },

    /* Ads are requested only once a visitor accepts them. Leave this
       false: AdSense sets cookies even for non-personalised ads, so
       serving them after a "reject" is not something we do. */
    serveAfterReject: false,

    /* Slots fill when they come within this many pixels of the viewport.
       Keeps ads off screens nobody scrolls to, which lifts viewability. */
    lazyMargin: 500,

    /* Das Fenster im Editor: Es zeigt, dass gearbeitet wird, und daneben
       steht eine Anzeige. Es schließt sich von selbst, sobald die Arbeit
       fertig und die Mindestzeit um ist.

       Wer es wegklickt, bekommt das Ergebnis nicht — kein eingesetzter
       Lebenslauf, kein Zuschnitt, kein PDF. Das steht auch im Fenster, bevor
       jemand klickt; eine Bedingung, die man erst hinterher erfährt, ist ein
       Hinterhalt.

       Schließen geht jederzeit. Das ist kein Zugeständnis, sondern die
       Bedingung: AdSense untersagt Anzeigen, die sich nicht sofort schließen
       lassen. Gesperrt ist die Funktion, nie die Anzeige.

       `wartezeit` sind die Sekunden, die das Fenster mindestens steht, auch
       wenn die Arbeit früher fertig ist. Sie gilt für alle gleich — auch für
       den, der Werbung abgelehnt hat. Wer Ablehnung mit Wartezeit bestraft,
       macht aus der Einwilligung eine Gebühr, und das hält vor keinem
       deutschen Gericht.

       Auch bei eingeschalteter Werbung gilt: Ist der Editor der einzige Ort,
       den jemand besucht, hat er noch keine Einwilligung gegeben. Dann steht
       im Fenster der Eigenhinweis statt einer Anzeige — nie Werbecode ohne
       Zustimmung. */
    zwischenspiel: {
      aktiv: true,
      wartezeit: 5,
    }
  },

  /* Die beiden KI-Funktionen im Editor: einen vorhandenen Lebenslauf
     einlesen und einen Lebenslauf auf eine Stellenanzeige zuschneiden.
     Sie brauchen den Worker aus api/ — ohne Adresse bleiben die Knöpfe
     weg, und der Editor ist wie zuvor eine Seite ohne Server.
     Adresse eintragen, die wrangler deploy ausgegeben hat, mit /api am Ende. */
  ki: {
    endpunkt: 'https://plainsheet-ki.plainsheet.workers.dev/api',
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
