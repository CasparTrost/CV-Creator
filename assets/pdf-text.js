/* Erzeugt aus api/pdf.js — nicht von Hand ändern. */
(function(){
/*
 * Text aus einem PDF holen, ohne Bibliothek.
 *
 * Warum selbst und nicht pdf.js: Der Worker soll klein bleiben, und die
 * Alternative wäre, jede hochgeladene Datei an ein teureres Modell zu
 * schicken, das Bilder lesen kann. Für am Rechner erzeugte Lebensläufe —
 * also fast alle — reicht der Weg hier.
 *
 * Der Ablauf ist der, den ein PDF vorgibt:
 *   Seite -> /Resources -> /Font -> /ToUnicode -> Zeichentabelle
 *   Seite -> /Contents -> Textströme -> Zeichenketten -> Tabelle anwenden
 *
 * Zwei Fallen, die einen einfachen Ansatz scheitern lassen:
 *   - „endstream“ enthält „stream“. Wer danach sucht, fängt mitten im Ende
 *     des vorigen Stroms wieder an.
 *   - TextDecoder('latin1') ist nach der Norm windows-1252 und macht aus
 *     dem Byte 0x9C ein 'œ'. Gesucht wird deshalb im Text, geschnitten in
 *     den Bytes.
 *   - Word, Acrobat und InDesign legen die meisten Objekte in gepackte
 *     Objektströme. Wer nur den Klartext durchsucht, findet dort weder
 *     Seiten noch Schrifttabellen — und bekommt Zeichensalat statt Text.
 */

const WIN1252_SONDER = {
  0x80: '€', 0x82: '‚', 0x83: 'ƒ', 0x84: '„', 0x85: '…', 0x86: '†', 0x87: '‡',
  0x88: 'ˆ', 0x89: '‰', 0x8a: 'Š', 0x8b: '‹', 0x8c: 'Œ', 0x8e: 'Ž', 0x91: '‘',
  0x92: '’', 0x93: '“', 0x94: '”', 0x95: '•', 0x96: '–', 0x97: '—', 0x98: '˜',
  0x99: '™', 0x9a: 'š', 0x9b: '›', 0x9c: 'œ', 0x9e: 'ž', 0x9f: 'Ÿ',
};

async function pdfText(bytes) {
  const roh = new TextDecoder('windows-1252').decode(bytes);   /* nur zum Suchen */
  const objekte = objektIndex(roh);
  await objektStroemeOeffnen(roh, bytes, objekte);
  const seiten = [];

  for (const [nummer, eintrag] of objekte) {
    const koerper = koerperVon(roh, eintrag);
    if (!/\/Type\s*\/Page(?![a-zA-Z])/.test(koerper)) continue;
    seiten.push({ nummer, koerper });
  }
  /* Kein /Type /Page gefunden (verschachtelte Objektströme): dann wird jeder
     Strom einzeln versucht, ohne Schriftzuordnung. */
  if (!seiten.length) return await ohneSeiten(roh, bytes, objekte);

  const stuecke = [];
  for (const seite of seiten) {
    const schriften = await schriftTabellen(roh, bytes, objekte, seite.koerper);
    /* Der Inhalt einer Seite kann auf viele Ströme verteilt sein — manche
       Erzeuger schreiben je Textblock einen. Gemessen wird trotzdem die
       ganze Seite, sonst sieht man die Spalten nicht. */
    let laeufe = [];
    for (const nummer of inhaltsNummern(seite.koerper)) {
      const text = await stromText(roh, bytes, objekte, nummer);
      if (text) laeufe = laeufe.concat(zeichenketten(text, schriften));
    }
    if (laeufe.length) stuecke.push(seiteZuText(laeufe).join('\n'));
  }
  return saeubern(stuecke.join('\n'));
}

/* -------------------------------------------------------------- Objekte */

function objektIndex(roh) {
  const index = new Map();
  const marke = /(?:^|[^0-9])(\d+)\s+0\s+obj\b/g;
  let treffer;
  while ((treffer = marke.exec(roh)) !== null) {
    index.set(parseInt(treffer[1], 10),
              { stelle: treffer.index + treffer[0].indexOf(treffer[1]) });
  }
  return index;
}

/* Ein Objektstrom enthält weitere Objekte, gepackt. Sein Anfang ist eine
   Liste aus Nummer und Versatz, danach kommen ab /First die Körper. Ohne
   diesen Schritt bleiben bei Word- und Acrobat-Dateien Seiten, Schriften
   und Zeichentabellen unsichtbar — das Ergebnis ist dann Zeichensalat. */
async function objektStroemeOeffnen(roh, bytes, objekte) {
  const stroeme = [...objekte.entries()]
    .filter(([, e]) => e.stelle !== undefined &&
                       /\/Type\s*\/ObjStm/.test(koerperVon(roh, e)));
  for (const [nummer] of stroeme) {
    const inhalt = await stromText(roh, bytes, objekte, nummer);
    if (!inhalt) continue;
    const koerper = koerperVon(roh, objekte.get(nummer));
    const anzahl = zahlAus(koerper, 'N');
    const erstes = zahlAus(koerper, 'First');
    if (!anzahl || erstes === null) continue;
    const kopf = inhalt.slice(0, erstes).trim().split(/\s+/).map(Number);
    for (let i = 0; i < anzahl; i++) {
      const num = kopf[i * 2], versatz = kopf[i * 2 + 1];
      if (!isFinite(num) || !isFinite(versatz)) continue;
      const bis = i + 1 < anzahl && isFinite(kopf[i * 2 + 3])
        ? erstes + kopf[i * 2 + 3] : inhalt.length;
      if (objekte.has(num) && objekte.get(num).stelle !== undefined) continue;
      objekte.set(num, { text: inhalt.slice(erstes + versatz, bis) });
    }
  }
}

function zahlAus(koerper, name) {
  const t = new RegExp('/' + name + '\\s+(\\d+)').exec(koerper);
  return t ? parseInt(t[1], 10) : null;
}

function koerperVon(roh, eintrag) {
  if (!eintrag) return '';
  if (eintrag.text !== undefined) return eintrag.text;
  const ende = roh.indexOf('endobj', eintrag.stelle);
  return roh.slice(eintrag.stelle, ende < 0 ? eintrag.stelle + 4000 : ende);
}

function verweis(koerper, name) {
  const t = new RegExp('/' + name + '\\s+(\\d+)\\s+0\\s+R').exec(koerper);
  return t ? parseInt(t[1], 10) : null;
}

function inhaltsNummern(seite) {
  const einzeln = verweis(seite, 'Contents');
  if (einzeln !== null) return [einzeln];
  const feld = /\/Contents\s*\[([^\]]*)\]/.exec(seite);
  if (!feld) return [];
  return [...feld[1].matchAll(/(\d+)\s+0\s+R/g)].map(t => parseInt(t[1], 10));
}

/* --------------------------------------------------------------- Ströme */

/* Wo hört ein Strom auf?
 *
 * Die ehrliche Antwort steht im Wörterbuch: /Length. Wer stattdessen bis zum
 * nächsten „endstream“ liest, muss raten, ob die letzten Bytes davor zum
 * Strom gehören oder nur das Zeilenende sind, das der Erzeuger eingefügt hat.
 * Rät man falsch, ist der gepackte Strom um ein Byte zu kurz und damit ganz
 * unlesbar — und auf der Seite fehlt wortlos ein Absatz. Genau so
 * verschwanden einzelne Zeilen aus hochgeladenen Lebensläufen: Ein Strom, der
 * zufällig auf 0x0A oder 0x0D endet, wurde abgeschnitten.
 *
 * Deshalb: /Length zuerst, und danach beide Lesarten der Grenze als
 * Rückfall — der erste Versuch, der sich entpacken lässt, gewinnt.
 */
function laengeVon(roh, objekte, koerper) {
  const verweis = /\/Length\s+(\d+)\s+\d+\s+R/.exec(koerper);
  if (verweis) {
    const ziel = koerperVon(roh, objekte.get(parseInt(verweis[1], 10)));
    const zahl = /\bobj\b\s*(\d+)/.exec(ziel || '');
    return zahl ? parseInt(zahl[1], 10) : null;
  }
  const direkt = /\/Length\s+(\d+)(?!\s+\d+\s+R)/.exec(koerper);
  return direkt ? parseInt(direkt[1], 10) : null;
}

async function stromBytes(roh, bytes, objekte, nummer) {
  const eintrag = objekte.get(nummer);
  if (!eintrag || eintrag.stelle === undefined) return null;   /* im Objektstrom: nie ein Strom */
  const koerper = koerperVon(roh, eintrag);
  const marke = /(?:^|[^A-Za-z])stream\r?\n/.exec(koerper);
  if (!marke) return null;
  const von = eintrag.stelle + marke.index + marke[0].length;

  const enden = [];
  const laenge = laengeVon(roh, objekte, koerper);
  if (laenge !== null && laenge > 0 && von + laenge <= bytes.length) enden.push(von + laenge);
  const roheGrenze = roh.indexOf('endstream', von);
  if (roheGrenze > von) {
    let getrimmt = roheGrenze;
    while (getrimmt > von && (roh[getrimmt - 1] === '\n' || roh[getrimmt - 1] === '\r')) getrimmt--;
    enden.push(getrimmt, roheGrenze);
  }
  if (!enden.length) return null;
  const felder = [...new Set(enden)].map(ende => bytes.subarray(von, ende));
  return { felder, feld: felder[0], gepackt: /\/FlateDecode/.test(koerper) };
}

async function entpacken(feld) {
  for (const art of ['deflate', 'deflate-raw']) {
    try {
      const packe = new Blob([feld]).stream().pipeThrough(new DecompressionStream(art));
      return new Uint8Array(await new Response(packe).arrayBuffer());
    } catch (e) { /* nächster Versuch */ }
  }
  return null;
}

async function stromText(roh, bytes, objekte, nummer) {
  const strom = await stromBytes(roh, bytes, objekte, nummer);
  if (!strom) return null;
  const lesen = feld => new TextDecoder('windows-1252').decode(feld);
  if (!strom.gepackt) return lesen(strom.feld);
  for (const feld of strom.felder) {
    const offen = await entpacken(feld);
    if (offen) return lesen(offen);
  }
  return null;
}

/* ------------------------------------------------------------- Schriften */

/* Name im Text ("F1") -> Tabelle Zeichencode -> Zeichen. */
async function schriftTabellen(roh, bytes, objekte, seite) {
  const tabellen = new Map();
  let quelle = seite;
  const ressourcen = verweis(seite, 'Resources');
  if (ressourcen !== null && objekte.has(ressourcen)) quelle = koerperVon(roh, objekte.get(ressourcen));

  const block = /\/Font\s*<<([\s\S]*?)>>/.exec(quelle);
  if (!block) return tabellen;

  for (const t of block[1].matchAll(/\/([^\s/]+)\s+(\d+)\s+0\s+R/g)) {
    const name = t[1], nummer = parseInt(t[2], 10);
    if (!objekte.has(nummer)) continue;
    const schrift = koerperVon(roh, objekte.get(nummer));
    const zuUnicode = verweis(schrift, 'ToUnicode');
    if (zuUnicode !== null) {
      const cmap = await stromText(roh, bytes, objekte, zuUnicode);
      if (cmap) { tabellen.set(name, cmapLesen(cmap)); continue; }
    }
    /* Ohne ToUnicode: die üblichen Ein-Byte-Kodierungen sind nah genug an
       windows-1252, um den Text lesbar zu machen. */
    tabellen.set(name, null);
  }
  return tabellen;
}

/* beginbfchar / beginbfrange aus einer ToUnicode-CMap. */
function cmapLesen(cmap) {
  const tabelle = new Map();
  for (const block of cmap.matchAll(/beginbfchar([\s\S]*?)endbfchar/g)) {
    for (const zeile of block[1].matchAll(/<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>/g)) {
      tabelle.set(parseInt(zeile[1], 16), ausUtf16(zeile[2]));
    }
  }
  for (const block of cmap.matchAll(/beginbfrange([\s\S]*?)endbfrange/g)) {
    /* <von> <bis> <ziel>   und   <von> <bis> [<z1> <z2> …] */
    for (const zeile of block[1].matchAll(/<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*(?:<([0-9A-Fa-f]+)>|\[([\s\S]*?)\])/g)) {
      const von = parseInt(zeile[1], 16), bis = parseInt(zeile[2], 16);
      if (zeile[3]) {
        const start = parseInt(zeile[3], 16);
        for (let i = 0; i <= bis - von && i < 65536; i++) {
          tabelle.set(von + i, String.fromCodePoint(start + i));
        }
      } else if (zeile[4]) {
        const liste = [...zeile[4].matchAll(/<([0-9A-Fa-f]+)>/g)];
        liste.forEach((t, i) => tabelle.set(von + i, ausUtf16(t[1])));
      }
    }
  }
  return tabelle;
}

function ausUtf16(hex) {
  let aus = '';
  for (let i = 0; i + 3 < hex.length + 1; i += 4) {
    const wert = parseInt(hex.slice(i, i + 4), 16);
    if (isFinite(wert) && wert) aus += String.fromCharCode(wert);
  }
  return aus;
}

/* --------------------------------------------------------- Textoperatoren */

function zeichenketten(inhalt, schriften) {
  /* Chrome setzt jede Silbe einzeln und schiebt den Cursor dazwischen. Ein
     Zeilenumbruch bei jedem Vorschub ergäbe ein Wort je Zeile — umgebrochen
     wird deshalb nur, wenn sich die Höhe ändert. */
  const laeufe = [];                     /* {x, y, text} je Textlauf */
  let zeile = '', tabelle = null, letzteHoehe = null, x = 0, y = 0, zeileX = 0, zeileY = 0;

  const anweisung = new RegExp([
    '\\/([^\\s/]+)\\s+[\\d.]+\\s+Tf',                    /* 1 Schrift */
    '\\[((?:[^\\[\\]\\\\]|\\\\.)*)\\]\\s*TJ',    /* 2 Feld */
    '\\(((?:[^()\\\\]|\\\\.)*)\\)\\s*(?:Tj|\')',    /* 3 Kette */
    '<([0-9A-Fa-f\\s]*)>\\s*Tj',                               /* 4 Hex */
    '(-?[\\d.]+)\\s+(-?[\\d.]+)\\s+(?:Td|TD)',             /* 5,6 Vorschub */
    '(?:-?[\\d.]+\\s+){4}(-?[\\d.]+)\\s+(-?[\\d.]+)\\s+Tm',  /* 7,8 Matrix */
    '(T\\*|ET|BT)',                                              /* 9 Zeile/Block */
  ].join('|'), 'g');

  const umbruch = () => {
    if (zeile.trim()) laeufe.push({ x: zeileX, y: zeileY, text: zeile.trim() });
    zeile = '';
  };
  /* Jeder Textlauf beginnt mit einer Matrix, die seine Höhe nennt. Gleiche
     Höhe heißt gleiche Zeile — dort gehört ein Leerzeichen dazwischen, etwa
     zwischen einer Position und ihrem Zeitraum am rechten Rand. */
  const hoehe = (wertX, wertY) => {
    const neuY = parseFloat(wertY), neuX = parseFloat(wertX);
    if (!isFinite(neuY)) return;
    if (letzteHoehe === null || Math.abs(neuY - letzteHoehe) > 0.4) umbruch();
    else if (zeile && !/\s$/.test(zeile)) zeile += ' ';
    if (!zeile) { zeileX = isFinite(neuX) ? neuX : 0; zeileY = neuY; }
    x = isFinite(neuX) ? neuX : x;
    y = neuY;
    letzteHoehe = neuY;
  };

  let treffer;
  while ((treffer = anweisung.exec(inhalt)) !== null) {
    if (treffer[1] !== undefined) {
      tabelle = schriften.has(treffer[1]) ? schriften.get(treffer[1]) : null;
    } else if (treffer[2] !== undefined) {
      for (const stueck of treffer[2].matchAll(/\((?:[^()\\]|\\.)*\)|<[0-9A-Fa-f\s]*>|-?[\d.]+/g)) {
        const s = stueck[0];
        if (s[0] === '(') zeile += entziffern(entklammern(s.slice(1, -1)), tabelle);
        else if (s[0] === '<') zeile += hexZuText(s.slice(1, -1), tabelle);
        else if (parseFloat(s) < -180) zeile += ' ';      /* großer Vorschub = Leerzeichen */
      }
    } else if (treffer[3] !== undefined) {
      zeile += entziffern(entklammern(treffer[3]), tabelle);
    } else if (treffer[4] !== undefined) {
      zeile += hexZuText(treffer[4], tabelle);
    } else if (treffer[6] !== undefined) {
      /* Td/TD ist hier der Vorschub von Zeichen zu Zeichen. Aus einem
         waagerechten Vorschub ein Leerzeichen zu machen wäre falsch: die
         Wortzwischenräume stehen als eigenes Zeichen im Text. Nur ein
         Sprung in der Höhe ist eine neue Zeile. */
      if (Math.abs(parseFloat(treffer[6])) > 0.4) umbruch();
    } else if (treffer[8] !== undefined) {
      hoehe(treffer[7], treffer[8]);
    } else if (treffer[9] !== undefined) {
      if (treffer[9] === 'T*') umbruch();
    }
  }
  umbruch();
  return laeufe;
}

/* ------------------------------------------------------ Spalten erkennen */

/* Ein Lebenslauf ist selten durchgehend ein- oder zweispaltig. Meistens ist
   er beides: ein Kopf über die ganze Breite, darunter zwei Spalten, unten
   vielleicht eine Unterschrift quer. Manche Erzeuger schreiben so etwas
   zeilenweise quer über beide Spalten — „KONTAKT   ERFAHRUNG“ —, und das
   kann niemand mehr entwirren, auch kein Modell.

   Deshalb wird nicht nach einer Vorlage gesucht, sondern gemessen:
     1. Gibt es einen senkrechten Graben ohne Text?
     2. Auf welchen Höhen steht links UND rechts davon etwas? Das ist der
        zweispaltige Bereich.
     3. Alles darüber und darunter läuft über die ganze Breite und bleibt
        in seiner Reihenfolge; der Bereich dazwischen wird Spalte für
        Spalte gelesen.
   Findet sich kein sauberer Graben, bleibt alles, wie es gesetzt wurde.
   Eine falsch geteilte Seite wäre schlimmer als eine ungeteilte. */
function seiteZuText(roheLaeufe) {
  if (roheLaeufe.length < 8) return zeilenAus(roheLaeufe);
  const laeufe = nachUntenGedreht(roheLaeufe);
  const graben = grabenFinden(laeufe);
  if (graben === null) return zeilenAus(laeufe);

  const links = laeufe.filter(l => l.x < graben);
  const rechts = laeufe.filter(l => l.x >= graben);
  if (links.length < 4 || rechts.length < 4) return zeilenAus(laeufe);

  /* Höhen, auf denen beide Seiten Text haben. */
  const band = (l) => Math.round(l.y / 6);
  const rechteBaender = new Set(rechts.map(band));
  const gemeinsam = links.filter(l => rechteBaender.has(band(l))).map(l => l.y);
  if (gemeinsam.length < 3) return zeilenAus(laeufe);

  /* Ab der ersten gemeinsamen Höhe ist die Seite zweispaltig — bis unten.
     Eine Spalte, die länger ist als die andere, gehört noch zu ihr; sie
     hinten anzuhängen, hat „Englisch: B2“ hinter die Ausbildung gesetzt. */
  const oben = Math.min(...gemeinsam) - 3;
  const davor = laeufe.filter(l => l.y < oben).sort(nachOrt);
  const drin = (l) => l.y >= oben;

  return zeilenAus(davor)
    .concat(zeilenAus(links.filter(drin).sort(nachOrt)))
    .concat(zeilenAus(rechts.filter(drin).sort(nachOrt)));
}

/* Im PDF wächst y nach oben, im Browser nach unten, und die Erzeuger
   verbiegen das Koordinatensystem unterschiedlich. Statt zu raten, wird
   gezählt: Läuft y in der Reihenfolge des Schreibens meistens abwärts, war
   oben oben. Danach heißt „größeres y“ immer „weiter unten“. */
function nachUntenGedreht(laeufe) {
  let steigt = 0, faellt = 0;
  for (let i = 1; i < laeufe.length; i++) {
    if (laeufe[i].y > laeufe[i - 1].y) steigt++;
    else if (laeufe[i].y < laeufe[i - 1].y) faellt++;
  }
  if (steigt >= faellt) return laeufe;
  return laeufe.map(l => ({ x: l.x, y: -l.y, text: l.text }));
}

/* Die breiteste senkrechte Lücke im mittleren Teil der Seite. */
function grabenFinden(laeufe) {
  const xs = [...new Set(laeufe.map(l => Math.round(l.x)))].sort((a, b) => a - b);
  const breite = xs[xs.length - 1] - xs[0];
  if (breite < 100) return null;
  let stelle = null, luecke = 0;
  for (let i = 1; i < xs.length; i++) {
    const mitte = (xs[i] + xs[i - 1]) / 2;
    if (mitte < xs[0] + breite * 0.2 || mitte > xs[0] + breite * 0.8) continue;
    if (xs[i] - xs[i - 1] > luecke) { luecke = xs[i] - xs[i - 1]; stelle = mitte; }
  }
  return luecke >= breite * 0.12 ? stelle : null;
}

function nachOrt(a, b) { return a.y - b.y || a.x - b.x; }

/* Aus Läufen werden Zeilen — und aus einer offensichtlich umbrochenen Zeile
   wieder ein Stück des Absatzes, zu dem sie gehört.

   „Offensichtlich“ heißt hier: die nächste Zeile beginnt klein, oder die
   vorige endet auf ein Wort, nach dem kein Satz enden kann — und beide stehen
   eine Zeile auseinander, nicht zwei. Weiter geht die Geometrie nicht.

   Es wäre verlockend, jede Zeile, die bis an den rechten Rand reicht, als
   umbrochen zu lesen. Das trifft aber genauso auf einen langen
   Aufzählungspunkt zu, und der wird dann mit dem nächsten verschmolzen: Aus
   fünf Stationsaufgaben wird eine. Was an einem Zeilenende wirklich passiert,
   entscheidet die Sprache, nicht der Satzspiegel — und die liest das Modell,
   das den Abschnitt ohnehin in die Hand bekommt. Es weiß dann auch, ob es
   eine Liste vor sich hat oder einen Absatz. */
function zeilenAus(laeufe) {
  if (laeufe.length < 2) return laeufe.map(l => l.text);
  const abstaende = [];
  for (let i = 1; i < laeufe.length; i++) {
    const d = laeufe[i].y - laeufe[i - 1].y;
    if (d > 0.5 && d < 60) abstaende.push(d);
  }
  abstaende.sort((a, b) => a - b);
  const zeilenabstand = abstaende.length ? abstaende[Math.floor(abstaende.length / 2)] : 0;

  const aus = [];
  let letzte = null, letzteY = 0;
  for (const lauf of laeufe) {
    if (letzte && gehoertDazu(letzte, letzteY, lauf, zeilenabstand)) {
      letzte.text = /[\u2010-\u2014-]$/.test(letzte.text)
        ? letzte.text.slice(0, -1) + lauf.text
        : letzte.text + ' ' + lauf.text;
      letzteY = lauf.y;
      continue;
    }
    letzte = { x: lauf.x, y: lauf.y, text: lauf.text };
    letzteY = lauf.y;
    aus.push(letzte);
  }
  return aus.map(l => l.text);
}

const HAENGEND = /(^|\s)(und|oder|sowie|mit|f\u00fcr|in|im|am|zur|zum|von|bis|der|die|das|den|des|ein|eine|einer|and|or|with|for|of|the|to|a|an|y|o|con|para|de)$/i;

function gehoertDazu(oben, obenY, unten, zeilenabstand) {
  const abstand = unten.y - obenY;
  /* Eine Zeile weiter, nicht zwei — und nicht über das Luftholen hinweg, das
     eine Liste zwischen ihren Punkten lässt. */
  if (!(abstand > 0.5 && zeilenabstand > 0 && abstand <= zeilenabstand + 1.5)) return false;
  if (Math.abs(unten.x - oben.x) > 3) return false;      /* andere Spalte, andere Einrückung */
  if (oben.text.length <= 20) return false;
  if (/[.;:!?)\]]$/.test(oben.text)) return false;
  if (/^[\u2022\u00b7\u25cf\u2013\u2014-]\s/.test(unten.text)) return false;
  if (/^\d/.test(unten.text)) return false;
  return /^[a-z\u00e4\u00f6\u00fc\u00df(]/.test(unten.text) || HAENGEND.test(oben.text);
}

/* Eine Kette aus ( ) ist bei einer Schrift mit Tabelle ebenfalls kodiert. */
function entziffern(s, tabelle) {
  if (!tabelle) return s;
  let aus = '';
  for (const zeichen of s) {
    const abbild = tabelle.get(zeichen.charCodeAt(0));
    aus += abbild !== undefined ? abbild : zeichen;
  }
  return aus;
}

function hexZuText(hex, tabelle) {
  const sauber = hex.replace(/\s+/g, '');
  if (!sauber) return '';
  let aus = '';
  if (tabelle) {
    /* Identity-H und die üblichen Untermengen zählen in zwei Bytes. */
    for (let i = 0; i + 1 < sauber.length; i += 4) {
      const code = parseInt(sauber.slice(i, i + 4), 16);
      const abbild = tabelle.get(code);
      aus += abbild !== undefined ? abbild : '';
    }
    if (aus) return aus;
  }
  for (let i = 0; i + 1 < sauber.length; i += 2) {
    aus += einByte(parseInt(sauber.slice(i, i + 2), 16));
  }
  return aus;
}

function einByte(code) {
  if (WIN1252_SONDER[code]) return WIN1252_SONDER[code];
  return code >= 32 ? String.fromCharCode(code) : '';
}

function entklammern(s) {
  return s.replace(/\\([nrtbf()\\]|[0-7]{1,3})/g, (ganz, was) => {
    const tabelle = { n: '\n', r: '\n', t: ' ', b: '', f: '', '(': '(', ')': ')', '\\': '\\' };
    if (tabelle[was] !== undefined) return tabelle[was];
    return String.fromCharCode(parseInt(was, 8));
  });
}

/* ------------------------------------------------------------- Rückfall */

async function ohneSeiten(roh, bytes, objekte) {
  const stuecke = [];
  for (const nummer of objekte.keys()) {
    const text = await stromText(roh, bytes, objekte, nummer);
    if (text && /\b(Tj|TJ)\b/.test(text)) {
      stuecke.push(seiteZuText(zeichenketten(text, new Map())).join('\n'));
    }
  }
  return saeubern(stuecke.join('\n'));
}

/* Taugt der gelesene Text, oder ist es Zeichensalat?
 *
 * Der Anteil der Buchstaben allein sagt nichts: Eine Schrift, deren Codes um
 * ein paar Stellen verschoben sind, liefert „&DVSDU%HLVSLHO“ — fast lauter
 * Buchstaben und trotzdem wertlos. Zwei Merkmale trennen das zuverlässig:
 * Echter Text hat Leerzeichen (etwa jedes sechste Zeichen), und seine Wörter
 * haben Vokale. Verschobene Codes haben meist weder das eine noch das andere.
 */
function textTaugt(text, mindestens) {
  if (!text || text.length < (mindestens || 150)) return false;
  const buchstaben = (text.match(/[A-Za-zÀ-ÿ]/g) || []).length;
  if (buchstaben / text.length < 0.5) return false;

  const luecken = (text.match(/[ \n]/g) || []).length;
  if (luecken / text.length < 0.08) return false;

  const woerter = text.split(/[^A-Za-zÀ-ÿ]+/).filter(w => w.length >= 4);
  if (woerter.length < 12) return false;
  const mitVokal = woerter.filter(w => /[aeiouäöüàéèAEIOUÄÖÜ]/.test(w)).length;
  return mitVokal / woerter.length > 0.75;
}

function saeubern(text) {
  const zeilen = text.replace(/[ \t]+/g, ' ')
                     .split('\n').map(z => z.trim()).filter(Boolean);
  return zusammenfuegen(zeilen).join('\n').replace(/\n{3,}/g, '\n\n').trim();
}

/* Ein PDF kennt keine Sätze, nur Zeilen. „Projektsteuerung nach Scrum und“ /
   „klassisch“ sind zwei Zeilen und ein Gedanke; getrennt ergeben sie zwei
   Stichpunkte, von denen einer Unsinn ist. Zusammengefügt wird nur, wo es
   eindeutig ist: die obere Zeile endet ohne Satzzeichen, die untere beginnt
   klein. Trennstriche am Zeilenende werden dabei aufgelöst. */
/* Der zweite Durchgang, diesmal ohne Geometrie: Er fängt, was über eine
   Seiten- oder Stromgrenze hinweg zusammengehört. Hier fehlt der senkrechte
   Abstand als Merkmal, also bleibt es bei den sicheren Fällen — eine falsch
   zusammengezogene Zeile ist schlimmer als eine zu viel. */
function zusammenfuegen(zeilen) {
  const aus = [];
  for (const zeile of zeilen) {
    const oben = aus.length ? aus[aus.length - 1] : null;
    const haengend = HAENGEND.test(oben || '');
    const passt = oben && oben.length > 20 &&
      !/[.;:!?)\]]$/.test(oben) &&
      !/^[\u2022\u00b7\u25cf\u2013\u2014-]\s/.test(zeile) &&
      !/^\d/.test(zeile) &&
      (/^[a-z\u00e4\u00f6\u00fc\u00df(]/.test(zeile) || haengend);
    if (!passt) { aus.push(zeile); continue; }
    if (/[\u2010-\u2014-]$/.test(oben)) aus[aus.length - 1] = oben.slice(0, -1) + zeile;
    else aus[aus.length - 1] = oben + ' ' + zeile;
  }
  return aus;
}



/* ------------------------------------------------------------------ Bilder
 *
 * Wer seinen Lebenslauf hochlädt, hat sein Foto schon ausgesucht — es noch
 * einmal zu verlangen, wäre eine überflüssige Frage. Gesucht wird deshalb im
 * PDF nach einem Bild, das ein Bewerbungsfoto sein kann.
 *
 * Woran man es erkennt: hochkant bis quadratisch, groß genug zum Drucken,
 * aber kein gescanntes Blatt. Gescannte Seiten haben das Seitenverhältnis von
 * A4 (1:1.414) und Millionen von Bildpunkten; ein Foto hat ungefähr 3:4. Was
 * dazwischenliegt, bleibt liegen: lieber kein Foto als das Firmenlogo.
 */
async function pdfBilder(bytes, hoechstens) {
  const roh = new TextDecoder('windows-1252').decode(bytes);
  const objekte = objektIndex(roh);
  const gefunden = [];

  for (const [nummer, eintrag] of objekte) {
    if (gefunden.length >= (hoechstens || 4)) break;
    if (!eintrag || eintrag.stelle === undefined) continue;
    const koerper = koerperVon(roh, eintrag);
    if (!/\/Subtype\s*\/Image/.test(koerper)) continue;

    const breite = zahlAus(koerper, 'Width'), hoehe = zahlAus(koerper, 'Height');
    if (!breite || !hoehe) continue;
    if (!fotoMass(breite, hoehe)) continue;
    if (/\/ImageMask\s+true/.test(koerper)) continue;

    const strom = await stromBytes(roh, bytes, objekte, nummer);
    if (!strom) continue;
    const bild = /\/DCTDecode/.test(koerper)
      ? { typ: 'image/jpeg', feld: strom.feld }
      : await ausRohbild(koerper, strom);
    if (!bild) continue;
    gefunden.push({ breite, hoehe, typ: bild.typ, feld: bild.feld, daten: bild.daten });
  }
  /* Das plausibelste zuerst: nah an 3:4 und lieber groß als klein. */
  gefunden.sort((a, b) =>
    Math.abs(a.breite / a.hoehe - 0.75) - Math.abs(b.breite / b.hoehe - 0.75)
    || b.breite * b.hoehe - a.breite * a.hoehe);
  return gefunden;
}

function fotoMass(breite, hoehe) {
  if (breite < 100 || hoehe < 120) return false;
  if (breite * hoehe > 4000000) return false;          /* das ist eine Seite, kein Foto */
  const verhaeltnis = breite / hoehe;
  if (verhaeltnis < 0.45 || verhaeltnis > 1.2) return false;
  if (Math.abs(verhaeltnis - 1 / Math.SQRT2) < 0.02) return false;   /* DIN-Format: ein Blatt */
  return true;
}

/* Ein unkomprimiertes oder Flate-gepacktes Bild ist eine Folge von Bytes ohne
   Dateikopf. Im Browser wird daraus über die Zeichenfläche ein PNG; im Worker
   gibt es keine, und dort braucht auch niemand ein Foto. */
async function ausRohbild(koerper, strom) {
  if (typeof document === 'undefined') return null;
  /* Alles außer roh und Flate — JPX, CCITT, JBIG2 — ist ein eigener Decoder.
     Den gibt es hier nicht, und ein falsch gedeutetes Bild ist schlimmer als
     keines. */
  const filter = (koerper.match(/\/Filter\s*(\/[A-Za-z0-9]+|\[[^\]]*\])/) || [, ''])[1];
  if (filter && !/FlateDecode/.test(filter)) return null;
  const kanaele = /\/DeviceRGB/.test(koerper) ? 3 : (/\/DeviceGray/.test(koerper) ? 1 : 0);
  if (!kanaele) return null;
  if ((zahlAus(koerper, 'BitsPerComponent') || 8) !== 8) return null;

  let feld = strom.feld;
  if (strom.gepackt) {
    feld = null;
    for (const kandidat of strom.felder) {
      feld = await entpacken(kandidat);
      if (feld) break;
    }
    if (!feld) return null;
  }
  const breite = zahlAus(koerper, 'Width'), hoehe = zahlAus(koerper, 'Height');
  if (feld.length < breite * hoehe * kanaele) return null;

  const flaeche = document.createElement('canvas');
  flaeche.width = breite; flaeche.height = hoehe;
  const stift = flaeche.getContext('2d');
  const punkte = stift.createImageData(breite, hoehe);
  for (let i = 0, q = 0, z = 0; i < breite * hoehe; i++, q += kanaele, z += 4) {
    punkte.data[z] = feld[q];
    punkte.data[z + 1] = kanaele === 3 ? feld[q + 1] : feld[q];
    punkte.data[z + 2] = kanaele === 3 ? feld[q + 2] : feld[q];
    punkte.data[z + 3] = 255;
  }
  stift.putImageData(punkte, 0, 0);
  return { typ: 'image/png', daten: flaeche.toDataURL('image/png') };
}

window.pdfText = pdfText;
window.textTaugt = textTaugt;
window.pdfBilder = pdfBilder;
})();
