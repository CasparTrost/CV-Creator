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

export async function pdfText(bytes) {
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

  const seitenLaeufe = [];
  for (const seite of seiten) {
    const laeufe = await laeufeAus(roh, bytes, objekte,
      inhaltsNummern(seite.koerper, roh, objekte), seite.koerper, 0, new Set());
    if (laeufe.length) seitenLaeufe.push(laeufe);
  }
  const teile = seitenLaeufe.map(l => seiteTeile(l));
  grabenUebernehmen(seitenLaeufe, teile);
  return saeubern(seitenZusammen(teile).join('\n'));
}

/* Ein Raster gilt für das ganze Dokument.
 *
 * Auf der zweiten Seite hört die Seitenleiste oft nach einem Viertel auf.
 * Darunter steht links nichts mehr, der freie Streifen reicht bis an den
 * Seitenrand, und die Messung findet keinen Graben: Sie sieht eine Seite, die
 * fast nur aus einer Spalte besteht. Gelesen wird sie danach zeilenweise quer
 * über beide hinweg — und die letzten Kenntnisse stehen mitten in einer
 * Stationsbeschreibung, eine Zeile um die andere abwechselnd.
 *
 * Was auf einer Seite gemessen wurde, gilt deshalb auch für die übrigen. Aber
 * nur, wenn es dort aufgeht: Beide Seiten brauchen Text, es muss Höhen geben,
 * auf denen beide etwas haben, und keine Zeile darf über den Graben
 * hinweglaufen. Sonst bleibt die Seite, wie sie ist — eine falsch geteilte
 * wäre schlimmer als eine ungeteilte. */
function grabenUebernehmen(seitenLaeufe, teile) {
  const gefunden = teile.map(t => t.graben).filter(g => g !== null).sort((a, b) => a - b);
  if (!gefunden.length) return;
  const graben = gefunden[Math.floor(gefunden.length / 2)];
  teile.forEach((t, i) => {
    if (t.graben !== null) return;
    const neu = seiteTeile(seitenLaeufe[i], graben);
    if (neu.graben !== null) teile[i] = neu;
  });
}

/* Läuft Text über den Graben hinweg, ist es keiner — jedenfalls nicht auf
   dieser Seite. Eine einzelne Überschrift über die volle Breite darf das,
   ein Zwanzigstel der Zeilen nicht. */
function kreuztGraben(laeufe, graben) {
  const proZeichen = zeilenabstandVon(laeufe) * 0.22;
  const quer = laeufe.filter(l => l.x < graben
    && l.x + Math.min(l.text.length, 70) * proZeichen > graben + 4).length;
  return quer > Math.max(1, laeufe.length * 0.05);
}

function zeilenabstandVon(laeufe) {
  const abstaende = [];
  for (let i = 1; i < laeufe.length; i++) {
    const d = Math.abs(laeufe[i].y - laeufe[i - 1].y);
    if (d > 1 && d < 60) abstaende.push(d);
  }
  abstaende.sort((a, b) => a - b);
  return abstaende.length ? abstaende[Math.floor(abstaende.length / 2)] : 12;
}

/* Eine Spalte hört am Seitenende nicht auf.
 *
 * Eine Seitenleiste, die über zwei Seiten läuft, ist ein Text, kein zwei.
 * Wer Seite für Seite liest, schiebt die zweite Hälfte der Leiste mitten in
 * die breite Spalte der ersten Seite — „Sprachen: Deutsch, Muttersprache“
 * steht dann als Aufgabe unter der zuletzt genannten Stelle. Genau das hat
 * ein echter Lebenslauf gezeigt.
 *
 * Zusammengefasst wird deshalb über Seiten hinweg, aber nur, solange die
 * Seiten wirklich dasselbe Raster haben: unmittelbar aufeinanderfolgend und
 * mit einem Graben an fast derselben Stelle. Wechselt das Raster, beginnt ein
 * neuer Lauf, und was danach kommt, bleibt an seinem Platz. Eine einzelne
 * zweispaltige Seite zwischen einspaltigen wird nicht angefasst.
 *
 * Innerhalb eines Laufs steht zuerst alles über die volle Breite (in
 * Seitenfolge), dann die linken Spalten, dann die rechten. Die Zeilen selbst
 * werden weiter je Seite und je Spalte gebildet: Nur dort stimmt die
 * Geometrie, mit der entschieden wird, ob zwei Läufe eine Zeile sind. */
function seitenZusammen(teile) {
  const stuecke = [];
  for (let i = 0; i < teile.length; ) {
    let j = i;
    if (teile[i].graben !== null) {
      while (j + 1 < teile.length && gleicherGraben(teile[i], teile[j + 1])) j++;
    }
    const lauf = teile.slice(i, j + 1);
    const zeilen = [];
    for (const t of lauf) zeilen.push(...t.voll);
    for (const t of lauf) zeilen.push(...t.links);
    for (const t of lauf) zeilen.push(...t.rechts);
    if (zeilen.length) stuecke.push(zeilen.join('\n'));
    i = j + 1;
  }
  return stuecke;
}

function gleicherGraben(a, b) {
  if (a.graben === null || b.graben === null) return false;
  const breite = Math.max(a.breite, b.breite);
  return breite > 0 && Math.abs(a.graben - b.graben) <= breite * 0.08;
}

/* Die Textläufe einer Seite — auch die, die in Formularen stecken.
 *
 * Der Inhalt einer Seite kann auf viele Ströme verteilt sein; manche Erzeuger
 * schreiben je Textblock einen. Und manche — Foxit, Word über „Drucken als
 * PDF“ — legen den gesamten Seiteninhalt in ein Form-XObject und rufen es mit
 * einem einzigen „Do“ auf. Im Seitenstrom steht dann kein einziges Zeichen,
 * und wer nur ihn liest, hält ein ganz normales PDF für einen Scan und
 * schickt die Datei an ein Sprachmodell, statt sie zu lesen.
 *
 * Gemessen wird trotzdem die ganze Seite auf einmal, sonst sieht man die
 * Spalten nicht. */
async function laeufeAus(roh, bytes, objekte, nummern, ressourcen, tiefe, gesehen) {
  if (tiefe > 4) return [];
  const schriften = await schriftTabellen(roh, bytes, objekte, ressourcen);
  const formMatrix = matrixAus(ressourcen);
  let aus = [];
  for (const nummer of nummern) {
    if (gesehen.has(nummer)) continue;          /* ein Formular, das sich selbst ruft */
    gesehen.add(nummer);
    const text = await stromText(roh, bytes, objekte, nummer);
    if (!text) continue;
    aus = aus.concat(zeichenketten(text, schriften, formMatrix));
    for (const name of [...text.matchAll(/\/([A-Za-z0-9.#+-]+)\s+Do\b/g)].map(t => t[1])) {
      const form = xobjektNummer(ressourcen, name);
      if (form === null) continue;
      const koerper = koerperVon(roh, objekte.get(form));
      if (!/\/Subtype\s*\/Form/.test(koerper || '')) continue;   /* ein Bild, kein Text */
      aus = aus.concat(await laeufeAus(roh, bytes, objekte, [form], koerper, tiefe + 1, gesehen));
    }
  }
  return aus;
}

/* Ein Formular bringt seine eigene Matrix mit — in ihr stehen seine
   Koordinaten. */
function matrixAus(koerper) {
  const t = /\/Matrix\s*\[\s*(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)/.exec(koerper || '');
  if (!t) return null;
  const m = t.slice(1).map(parseFloat);
  return m.every(isFinite) ? m : null;
}

function xobjektNummer(ressourcen, name) {
  const feld = /\/XObject\s*<<([\s\S]*?)>>/.exec(ressourcen || '');
  if (!feld) return null;
  const treffer = new RegExp('\\/' + name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
                             + '\\s+(\\d+)\\s+0\\s+R').exec(feld[1]);
  return treffer ? parseInt(treffer[1], 10) : null;
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

function nummernAus(text) {
  return [...String(text).matchAll(/(\d+)\s+0\s+R/g)].map(t => parseInt(t[1], 10));
}

/* Welche Ströme bilden den Inhalt dieser Seite?
 *
 * Drei Schreibweisen kommen vor: das Feld steht direkt im Seitenwörterbuch,
 * der Verweis zeigt auf einen einzelnen Strom — oder er zeigt auf ein Objekt,
 * das selbst nur ein Feld von Strömen ist. Den dritten Fall schreiben unter
 * anderem Foxit und Word; wer ihn nicht kennt, hält die Seite für leer und
 * schickt am Ende die ganze Datei an ein Sprachmodell, statt sie zu lesen. */
function inhaltsNummern(seite, roh, objekte) {
  const feld = /\/Contents\s*\[([^\]]*)\]/.exec(seite);
  if (feld) return nummernAus(feld[1]);

  const einzeln = verweis(seite, 'Contents');
  if (einzeln === null) return [];
  const koerper = koerperVon(roh, objekte && objekte.get(einzeln));
  const alsFeld = /^\s*\d+\s+\d+\s+obj\s*\[([^\]]*)\]/.exec(koerper || '');
  if (alsFeld) {
    const nummern = nummernAus(alsFeld[1]);
    if (nummern.length) return nummern;
  }
  return [einzeln];
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

/* Zwei Matrizen hintereinander ausgeführt. */
function malnehmen(m, n) {
  return [
    m[0] * n[0] + m[1] * n[2],          m[0] * n[1] + m[1] * n[3],
    m[2] * n[0] + m[3] * n[2],          m[2] * n[1] + m[3] * n[3],
    m[4] * n[0] + m[5] * n[2] + n[4],   m[4] * n[1] + m[5] * n[3] + n[5],
  ];
}

function verwandeln(px, py, m) {
  return [m[0] * px + m[2] * py + m[4], m[1] * px + m[3] * py + m[5]];
}

function zeichenketten(inhalt, schriften, anfang) {
  /* Chrome setzt jede Silbe einzeln und schiebt den Cursor dazwischen. Ein
     Zeilenumbruch bei jedem Vorschub ergäbe ein Wort je Zeile — umgebrochen
     wird deshalb nur, wenn sich die Höhe ändert. */
  const laeufe = [];                     /* {x, y, text} je Textlauf */
  let zeile = '', tabelle = null, letzteHoehe = null, x = 0, y = 0, zeileX = 0, zeileY = 0;
  /* Die Fläche, in die gerade gezeichnet wird. Ein Erzeuger setzt jeden Block
     mit einer eigenen Matrix — wer sie übergeht, vergleicht Koordinaten aus
     verschiedenen Welten und findet keine Spalte mehr. */
  let flaeche = (anfang && anfang.length === 6) ? anfang.slice() : [1, 0, 0, 1, 0, 0];
  const stapel = [];

  const anweisung = new RegExp([
    '\\/([^\\s/]+)\\s+[\\d.]+\\s+Tf',                    /* 1 Schrift */
    '\\[((?:[^\\[\\]\\\\]|\\\\.)*)\\]\\s*TJ',    /* 2 Feld */
    '\\(((?:[^()\\\\]|\\\\.)*)\\)\\s*(?:Tj|\')',    /* 3 Kette */
    '<([0-9A-Fa-f\\s]*)>\\s*Tj',                               /* 4 Hex */
    '(-?[\\d.]+)\\s+(-?[\\d.]+)\\s+(?:Td|TD)',             /* 5,6 Vorschub */
    '(?:-?[\\d.]+\\s+){4}(-?[\\d.]+)\\s+(-?[\\d.]+)\\s+Tm',  /* 7,8 Matrix */
    '(T\\*|ET|BT)',                                              /* 9 Zeile/Block */
    '(-?[\\d.]+)\\s+(-?[\\d.]+)\\s+(-?[\\d.]+)\\s+(-?[\\d.]+)\\s+(-?[\\d.]+)\\s+(-?[\\d.]+)\\s+cm',
                                                                   /* 10-15 Fläche */
    '(?:^|[^A-Za-z])(q|Q)(?![A-Za-z])',                            /* 16 Stapel */
  ].join('|'), 'g');

  const umbruch = () => {
    if (zeile.trim()) laeufe.push({ x: zeileX, y: zeileY, text: zeile.trim() });
    zeile = '';
  };
  /* Jeder Textlauf beginnt mit einer Matrix, die seine Höhe nennt. Gleiche
     Höhe heißt gleiche Zeile — dort gehört ein Leerzeichen dazwischen, etwa
     zwischen einer Position und ihrem Zeitraum am rechten Rand. */
  const hoehe = (wertX, wertY) => {
    const ort = verwandeln(parseFloat(wertX), parseFloat(wertY), flaeche);
    const neuX = ort[0], neuY = ort[1];
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
    } else if (treffer[10] !== undefined) {
      const neu = [10, 11, 12, 13, 14, 15].map(i => parseFloat(treffer[i]));
      if (neu.every(isFinite)) flaeche = malnehmen(neu, flaeche);
    } else if (treffer[16] !== undefined) {
      if (treffer[16] === 'q') stapel.push(flaeche.slice());
      else if (stapel.length) flaeche = stapel.pop();
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
function seiteTeile(roheLaeufe, vorgabe) {
  const einteilig = (zeilen) => ({ graben: null, breite: 0, voll: zeilen, links: [], rechts: [] });
  if (roheLaeufe.length < 8) return einteilig(zeilenAus(roheLaeufe));
  const laeufe = nachUntenGedreht(roheLaeufe);
  const graben = vorgabe === undefined ? grabenFinden(laeufe)
               : (kreuztGraben(laeufe, vorgabe) ? null : vorgabe);
  /* Kein Graben: eine Spalte. Gelesen wird dann von oben nach unten — nicht
     in der Reihenfolge, in der die Zeichen im Strom stehen. Manche Erzeuger
     schreiben erst alle Überschriften und dann alle Aufzählungen; wer das
     so übernimmt, reicht dem Modell einen Lebenslauf, in dem keine Aufgabe
     mehr bei ihrer Station steht. */
  if (graben === null) return einteilig(zeilenAus(inLesereihenfolge(laeufe)));

  const links = laeufe.filter(l => l.x < graben);
  const rechts = laeufe.filter(l => l.x >= graben);
  if (links.length < 4 || rechts.length < 4) return einteilig(zeilenAus(laeufe));

  /* Höhen, auf denen beide Seiten Text haben. */
  const band = (l) => Math.round(l.y / 6);
  const rechteBaender = new Set(rechts.map(band));
  const gemeinsam = links.filter(l => rechteBaender.has(band(l))).map(l => l.y);
  if (gemeinsam.length < 3) return einteilig(zeilenAus(laeufe));

  /* Ab der ersten gemeinsamen Höhe ist die Seite zweispaltig — bis unten.
     Eine Spalte, die länger ist als die andere, gehört noch zu ihr; sie
     hinten anzuhängen, hat „Englisch: B2“ hinter die Ausbildung gesetzt. */
  const oben = Math.min(...gemeinsam) - 3;
  const davor = inLesereihenfolge(laeufe.filter(l => l.y < oben));
  const drin = (l) => l.y >= oben;
  const xe = laeufe.map(l => l.x);

  return {
    graben,
    breite: Math.max(...xe) - Math.min(...xe),
    voll: zeilenAus(davor),
    links: zeilenAus(inLesereihenfolge(links.filter(drin))),
    rechts: zeilenAus(inLesereihenfolge(rechts.filter(drin))),
  };
}

/* Eine einzelne Seite als Text — für die Notfälle, in denen es gar keine
   Seiten gibt und jeder Strom für sich gelesen wird. */
function seiteZuText(roheLaeufe) {
  const t = seiteTeile(roheLaeufe);
  return t.voll.concat(t.links, t.rechts);
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
/* Ein Graben ist eine senkrechte Bahn, die über fast die ganze Höhe frei
 * bleibt.
 *
 * „Fast“ ist hier das entscheidende Wort. Eine Überschrift oder ein
 * Kurzprofil läuft über beide Spalten — wer verlangt, dass keine einzige
 * Zeile die Bahn kreuzt, findet in solchen Lebensläufen nie eine. Gezählt
 * wird deshalb reihenweise: In wie vielen Zeilen des Blattes ist diese Bahn
 * frei? Ab vier Fünfteln ist es ein Graben.
 *
 * Gebraucht wird dafür das rechte Ende jeder Zeile. Es steht nirgends, aber
 * es lässt sich schätzen: Der Zeilenabstand verrät den Schriftgrad, der
 * Schriftgrad die Breite eines Zeichens.
 *
 * Bleiben mehrere Bahnen, gewinnt die rechte. Die breite Spalte eines
 * Lebenslaufs steht rechts; was links davon noch Lücken hat, ist meist das
 * Innenleben der Seitenleiste und darf nicht auseinandergerissen werden.
 */
function grabenFinden(laeufe) {
  const abstaende = [];
  for (let i = 1; i < laeufe.length; i++) {
    const d = Math.abs(laeufe[i].y - laeufe[i - 1].y);
    if (d > 1 && d < 60) abstaende.push(d);
  }
  abstaende.sort((a, b) => a - b);
  const zeilenabstand = abstaende.length ? abstaende[Math.floor(abstaende.length / 2)] : 12;
  /* Ein Zeichen ist im Mittel gut ein Fünftel so breit wie der Zeilenabstand
     hoch. Knapp geschätzt: Überschätzt man, gilt jede Bahn als überquert. */
  const proZeichen = zeilenabstand * 0.22;

  const spannen = laeufe.map(l => [l.x, l.x + Math.min(l.text.length, 70) * proZeichen]);
  const links = Math.min(...spannen.map(s => s[0]));
  const rechts = Math.max(...spannen.map(s => s[1]));
  const breite = rechts - links;
  if (breite < 100) return null;

  /* Die Zeilen des Blattes, jede mit den Spannen, die in ihr liegen. */
  const reihen = new Map();
  spannen.forEach((spanne, i) => {
    const schluessel = Math.round(laeufe[i].y / Math.max(4, zeilenabstand));
    if (!reihen.has(schluessel)) reihen.set(schluessel, []);
    reihen.get(schluessel).push(spanne);
  });
  const alle = [...reihen.values()];
  if (alle.length < 6) return null;

  const schritt = Math.max(1, breite / 240);
  const mindestens = Math.max(6, breite * 0.03);
  let stelle = null, bandVon = null, letzteFrei = false;
  const pruefen = (bis) => {
    if (bandVon === null) return;
    /* Getrennt wird am rechten Rand der freien Bahn, nicht in ihrer Mitte:
       Die Bahn ist oft breiter als der Zwischenraum — links von ihr endet
       die Leiste schon früher, rechts von ihr beginnt die Spalte sofort. */
    const mitte = bis - (bis - bandVon) * 0.15;
    if (bis - bandVon >= mindestens
        && mitte > links + breite * 0.15 && mitte < links + breite * 0.85) {
      const anteil = laeufe.filter(l => l.x >= mitte).length / laeufe.length;
      if (anteil >= 0.25 && anteil <= 0.8) stelle = mitte;
    }
    bandVon = null;
  };
  for (let x = links; x <= rechts; x += schritt) {
    const frei = alle.filter(r => !r.some(([von, bis]) => von < x && bis > x)).length / alle.length;
    if (frei >= 0.8) { if (!letzteFrei) bandVon = x; }
    else pruefen(x);
    letzteFrei = frei >= 0.8;
  }
  pruefen(rechts);
  return stelle;
}

function nachOrt(a, b) { return a.y - b.y || a.x - b.x; }

/* Läufe in Lesereihenfolge: erst zeilenweise von oben nach unten, innerhalb
 * einer Zeile von links nach rechts.
 *
 * Warum das nicht dasselbe ist wie „nach y sortieren“: Ein
 * Aufzählungszeichen steht nicht auf der Grundlinie seines Textes, sondern
 * eine Winzigkeit daneben — und ob darüber oder darunter, entscheidet der
 * Erzeuger. Bei der einen Datei landet der Punkt vor seinem Text, bei der
 * nächsten dahinter. Dann steht er vor der zweiten Zeile des vorigen
 * Stichpunktes, „KOMPETENZEN“ bekommt einen Punkt vorgesetzt und ist keine
 * Überschrift mehr, und das Modell sieht einen Lebenslauf ohne Gliederung.
 *
 * Was eine Zeile ist, sagt der Zeilenabstand: Läufe, die weniger als ein
 * Drittel davon auseinanderliegen, stehen nebeneinander, nicht untereinander.
 * Gemessen wird er über die Abstände, die größer sind als so ein Versatz. */
function inLesereihenfolge(laeufe) {
  const sortiert = [...laeufe].sort(nachOrt);
  const abstaende = [];
  for (let i = 1; i < sortiert.length; i++) {
    const d = sortiert[i].y - sortiert[i - 1].y;
    if (d > 2 && d < 60) abstaende.push(d);
  }
  abstaende.sort((a, b) => a - b);
  const zeilenabstand = abstaende.length ? abstaende[Math.floor(abstaende.length / 2)] : 12;
  const spielraum = Math.max(1.5, zeilenabstand * 0.4);

  const zeilen = [];
  for (const lauf of sortiert) {
    const letzte = zeilen[zeilen.length - 1];
    if (letzte && lauf.y - letzte.y <= spielraum) letzte.teile.push(lauf);
    else zeilen.push({ y: lauf.y, teile: [lauf] });
  }
  const aus = [];
  zeilen.forEach(z => {
    z.teile.sort((a, b) => a.x - b.x);
    aus.push(...z.teile);
  });
  return aus;
}

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

  /* Wo eine Spalte ihren rechten Rand hat, steht nirgends geschrieben — aber
     wo mehrere Zeilen an derselben Stelle aufhören, ist er. Und eine Zeile,
     die ihn erreicht, ist nicht zu Ende: Sie ist umbrochen, und was folgt,
     gehört dazu, auch wenn es groß anfängt. Ohne das wurde aus einem
     dreizeiligen Stichpunkt einer mit zwei Zeilen und ein zweiter, der mit
     „Orchestrator- und …“ anfing und niemandem gehörte.
     Zwischen zwei Stichpunkten steht das Aufzählungszeichen als eigener Lauf
     und eine Einrückung weiter links — daran scheitert dieser Weg, und genau
     deshalb zieht er nicht zwei Stichpunkte zusammen. */
  const proZeichen = (zeilenabstand || 12) * 0.22;
  const ende = (l) => l.x + Math.min(l.text.length, 200) * proZeichen;

  /* Die Regel gilt nur für Stichpunkte, und nur für solche mit einem
     geschriebenen Aufzählungszeichen. Denn dort — und nur dort — fängt ein
     neuer Punkt mit seinem eigenen Zeichen an, das eine Einrückung weiter
     links steht: Die Kette reißt von selbst, und „bis an den Rand“ kann gar
     nichts anderes heißen als „umbrochen“. Wer die Punkte malt statt sie zu
     schreiben — unsere eigenen PDFs tun das —, gibt diese Sicherheit nicht
     her; dann bliebe von zwei kurzen Stichpunkten hintereinander einer.

     Und gemessen wird der Rand je Einrückung, nicht über die ganze Spalte:
     Rechtsbündige Datumsangaben stehen weiter außen, als der Fließtext je
     reicht. Mit ihnen als Maßstab erreichte keine Zeile mehr den Rand. */
  const einrueckungen = [];
  laeufe.forEach(g => {
    if (!MARKE_ALLEIN.test(g.text)) return;
    const rechts = laeufe.find(l => l !== g && Math.abs(l.y - g.y) <= 2 && l.x > g.x);
    if (rechts && !einrueckungen.some(x => Math.abs(x - rechts.x) <= 3)) einrueckungen.push(rechts.x);
  });
  const raender = einrueckungen.map(px => {
    const eigene = laeufe.filter(l => Math.abs(l.x - px) <= 3).map(ende);
    return { px, rand: eigene.length >= 3 ? Math.max(...eigene) * 0.9 : Infinity };
  });
  const amRand = (l, e) => raender.some(r => Math.abs(l.x - r.px) <= 3 && e >= r.rand);

  const aus = [];
  let letzte = null, letzteY = 0, letztesEnde = 0;
  for (const lauf of laeufe) {
    const randErreicht = !!letzte && amRand(letzte, letztesEnde);
    if (letzte && gehoertDazu(letzte, letzteY, lauf, zeilenabstand, randErreicht)) {
      letzte.text = verbinden(letzte.text, lauf.text);
      letzteY = lauf.y;
      letztesEnde = ende(lauf);
      continue;
    }
    letztesEnde = ende(lauf);
    /* Luft zwischen zwei Zeilen ist eine Aussage: Hier endet etwas. Sie wird
       als Leerzeile festgehalten, damit der spätere Durchgang ohne Geometrie
       sie nicht überschreibt — er hat sonst die Zeile mit dem nächsten
       Arbeitgeber an den letzten Stichpunkt der vorigen Station gehängt,
       weil der Firmenname klein anfing. */
    if (letzte && zeilenabstand > 0 && lauf.y - letzteY > zeilenabstand * 1.6) aus.push(ABSATZ);
    letzte = { x: lauf.x, y: lauf.y, text: lauf.text };
    letzteY = lauf.y;
    aus.push(letzte);
  }
  return aus.map(l => (l === ABSATZ ? '' : l.text));
}

/* Nur eine Marke, kein Text: „hier war Luft“. */
const ABSATZ = { text: '' };

/* Eine Zeile, die auf einem Datum endet, ist eine Kopfzeile und kein halber
   Satz — der Zeitraum steht rechts außen, und was darunter kommt, ist die
   nächste Angabe. Ohne das hing der Arbeitgeber am Ende der vorigen Zeile,
   sobald sein Name klein anfängt — und es gibt genug Firmen, die das tun. */
const ZEITRAUM = /(\d{1,2}\/\d{2,4}|\b(19|20)\d{2}|heute|today|present|now)\s*$/i;

/* Ein Aufzählungszeichen, das allein auf einer Zeile steht. */
const MARKE_ALLEIN = /^[\u2022\u00b7\u25cf\u25e6\u25aa\u2043*]$/;

const HAENGEND = /(^|\s)(und|oder|sowie|mit|f\u00fcr|in|im|am|zur|zum|von|bis|der|die|das|den|des|ein|eine|einer|and|or|with|for|of|the|to|a|an|y|o|con|para|de)$/i;

/* Eine Zeile, die auf einen Bindestrich endet, hört nicht auf — sie wartet. */
const OFFEN = /[\wÀ-ÿ][\u2010-\u2014-]$/;
/* Was nach einem Ergänzungsstrich kommt: „Vertrags- und Buchhaltungswesen“. */
const ANHANG = /^(und|oder|bzw\.?|sowie|beziehungsweise|and|or|y|o)\b/i;

/* Zwei Zeilen werden eine. Wie sie zusammenkommen, verrät das Ende der oberen:
 *
 *   „Ver-“      + „änderung“       -> „Veränderung“        getrenntes Wort
 *   „KI-“       + „gestützter“     -> „KI-gestützter“      Abkürzung, der Strich gehört dazu
 *   „Software-“ + „Entwicklung“    -> „Software-Entwicklung“  zusammengesetztes Wort
 *   „Vertrags-“ + „und Buch…“      -> „Vertrags- und Buch…“   Ergänzungsstrich
 *   „…/i“       + „n/muster…“      -> „…/in/muster…“       Adresse, kein Raum darin
 *
 * Die Unterscheidung trägt weit, weil im Deutschen der zweite Teil eines
 * zusammengesetzten Wortes groß anfängt und eine Worttrennung klein. Bleibt
 * die Abkürzung: „KI-“, „RAG-“, „LLM-“ — dort steht der Strich fest, egal was
 * folgt. Alles andere bekommt ein Leerzeichen. */
function verbinden(oben, unten) {
  if (OFFEN.test(oben)) {
    if (ANHANG.test(unten)) return oben + ' ' + unten;
    const wort = (oben.slice(0, -1).match(/[\wÀ-ÿ]+$/) || [''])[0];
    const fest = /^[A-ZÀ-Þ0-9]{2,}$/.test(wort) || /^[A-ZÀ-Þ]/.test(unten);
    return fest ? oben + unten : oben.slice(0, -1) + unten;
  }
  /* Eine Adresse bricht mitten im Pfad um; ein Leerzeichen macht sie kaputt. */
  if (/(https?:\/\/|www\.)\S*$/.test(oben) && !/[.,;:!?]$/.test(oben)) return oben + unten;
  return oben + ' ' + unten;
}

function gehoertDazu(oben, obenY, unten, zeilenabstand, amRand) {
  const abstand = unten.y - obenY;
  /* Eine Zeile weiter, nicht zwei — und nicht über das Luftholen hinweg, das
     eine Liste zwischen ihren Punkten lässt. */
  if (!(abstand > 0.5 && zeilenabstand > 0 && abstand <= zeilenabstand + 1.5)) return false;
  if (Math.abs(unten.x - oben.x) > 3) return false;      /* andere Spalte, andere Einrückung */
  if (oben.text.length <= 20) return false;
  /* „…(Mendix)“ ist kein Satzende — eine Klammer schließt eine Einfügung,
     nicht den Gedanken. Nur echte Satzzeichen halten hier an. */
  if (/[.;:!?]$/.test(oben.text)) return false;
  if (/^[\u2022\u00b7\u25cf\u2013\u2014-]\s/.test(unten.text)) return false;
  if (/^\d/.test(unten.text)) return false;
  if (ZEITRAUM.test(oben.text)) return false;
  return /^[a-z\u00e4\u00f6\u00fc\u00df(]/.test(unten.text)
      || HAENGEND.test(oben.text) || OFFEN.test(oben.text) || amRand === true;
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
export function textTaugt(text, mindestens) {
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
  /* Die Leerzeilen bleiben bis hierher stehen — sie sind das einzige, was der
     Durchgang ohne Geometrie noch von den Abständen der Seite weiß. */
  const zeilen = text.replace(/[ \t]+/g, ' ').split('\n').map(z => z.trim());
  return zusammenfuegen(zeilen).join('\n').replace(/\n{2,}/g, '\n').trim();
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
  let marke = '';
  for (const roh of zeilen) {
    /* Ein Aufzählungszeichen steht im PDF oft als eigener Lauf — es wird an
       einer anderen Stelle gesetzt als der Text dahinter. Allein ist es keine
       Zeile, sondern der Anfang der nächsten. */
    if (MARKE_ALLEIN.test(roh)) { marke = '• '; continue; }
    if (!roh) { aus.push(''); continue; }          /* Luft trennt, sie steht nicht */
    const zeile = marke + roh;
    marke = '';
    const oben = aus.length ? aus[aus.length - 1] : null;
    const haengend = HAENGEND.test(oben || '');
    const passt = oben && oben.length > 20 &&
      !/[.;:!?]$/.test(oben) &&
      !/^[\u2022\u00b7\u25cf\u2013\u2014-]\s/.test(zeile) &&
      !/^\d/.test(zeile) && !ZEITRAUM.test(oben) &&
      (/^[a-z\u00e4\u00f6\u00fc\u00df(]/.test(zeile) || haengend || OFFEN.test(oben));
    if (!passt) { aus.push(zeile); continue; }
    aus[aus.length - 1] = verbinden(oben, zeile);
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
export async function pdfBilder(bytes, hoechstens) {
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
