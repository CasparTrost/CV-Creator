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

async function pdfLesen(bytes) {
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
  return saeubern(seitenZusammen(teile));
}

/* Der Text allein — für alle, die mit der Gliederung nichts anfangen. */
async function pdfText(bytes) {
  return (await pdfLesen(bytes)).text;
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
    if (zeilen.length) stuecke.push(...zeilen);
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

/* Wie stark die Fläche den Text vergrößert. Ein Erzeuger setzt die Schrift
   auf 1 und skaliert die Fläche auf 12 — ohne das wäre jede Zeile gleich
   groß. Gemessen wird die Fläche der Einheitsmasche. */
function skalierung(m) {
  const wert = Math.sqrt(Math.abs(m[0] * m[3] - m[1] * m[2]));
  return isFinite(wert) && wert > 0 ? wert : 1;
}

function zeichenketten(inhalt, schriften, anfang) {
  /* Chrome setzt jede Silbe einzeln und schiebt den Cursor dazwischen. Ein
     Zeilenumbruch bei jedem Vorschub ergäbe ein Wort je Zeile — umgebrochen
     wird deshalb nur, wenn sich die Höhe ändert. */
  const laeufe = [];                     /* {x, y, text} je Textlauf */
  let zeile = '', tabelle = null, letzteHoehe = null, x = 0, y = 0, zeileX = 0, zeileY = 0;
  /* Schrift und Grad des gerade gesetzten Textes, und der größte Grad, der in
     der laufenden Zeile vorkam: Eine Überschrift ist größer gesetzt als ihr
     Abschnitt, und das steht hier so im Dokument. */
  let schrift = '', grad = 0, zeileGrad = 0, zeileSchrift = '';
  /* Der Grad, wie Tf ihn nennt, und der Maßstab der Textmatrix — die Größe
     auf dem Blatt ist das Produkt aus beidem (mal der Fläche). */
  let tfGrad = 0, tmMassstab = 1;
  /* Die Fläche, in die gerade gezeichnet wird. Ein Erzeuger setzt jeden Block
     mit einer eigenen Matrix — wer sie übergeht, vergleicht Koordinaten aus
     verschiedenen Welten und findet keine Spalte mehr. */
  let flaeche = (anfang && anfang.length === 6) ? anfang.slice() : [1, 0, 0, 1, 0, 0];
  const stapel = [];

  const anweisung = new RegExp([
    '\\/([^\\s/]+)\\s+([\\d.]+)\\s+Tf',                  /* 1 Schrift, 2 Grad */
    '\\[((?:[^\\[\\]\\\\]|\\\\.)*)\\]\\s*TJ',    /* 3 Feld */
    '\\(((?:[^()\\\\]|\\\\.)*)\\)\\s*(?:Tj|\')',    /* 4 Kette */
    '<([0-9A-Fa-f\\s]*)>\\s*Tj',                               /* 5 Hex */
    '(-?[\\d.]+)\\s+(-?[\\d.]+)\\s+(?:Td|TD)',             /* 6,7 Vorschub */
    '(?:-?[\\d.]+\\s+){4}(-?[\\d.]+)\\s+(-?[\\d.]+)\\s+Tm',  /* 8,9 Matrix */
    '(T\\*|ET|BT)',                                              /* 10 Zeile/Block */
    '(-?[\\d.]+)\\s+(-?[\\d.]+)\\s+(-?[\\d.]+)\\s+(-?[\\d.]+)\\s+(-?[\\d.]+)\\s+(-?[\\d.]+)\\s+cm',
                                                                   /* 11-16 Fläche */
    '(?:^|[^A-Za-z])(q|Q)(?![A-Za-z])',                            /* 17 Stapel */
  ].join('|'), 'g');

  /* Gemerkt wird der Grad erst, wenn wirklich Text kommt: „/F7 28 Tf“ steht
     im Strom vor dem Namen, aber nach der letzten Zeile des Kurzprofils — wer
     ihn sofort verbucht, schreibt die Größe der Überschrift der Zeile davor
     zu und verschiebt die ganze Erkennung um eine Zeile. */
  const nimmGrad = () => {
    if (grad > zeileGrad) { zeileGrad = grad; zeileSchrift = schrift; }
  };

  const umbruch = () => {
    if (zeile.trim()) laeufe.push({ x: zeileX, y: zeileY, text: zeile.trim(),
                                    grad: zeileGrad, schrift: zeileSchrift });
    zeile = ''; zeileGrad = 0; zeileSchrift = '';
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
      /* Der Schriftgrad ist das, woran man eine Überschrift erkennt — und er
         steht hier, im Textstrom, eine Anweisung vor dem Text selbst. */
      schrift = treffer[1];
      tfGrad = parseFloat(treffer[2]);
      grad = tfGrad * tmMassstab * skalierung(flaeche);
    } else if (treffer[3] !== undefined) {
      for (const stueck of treffer[3].matchAll(/\((?:[^()\\]|\\.)*\)|<[0-9A-Fa-f\s]*>|-?[\d.]+/g)) {
        const s = stueck[0];
        if (s[0] === '(') { nimmGrad(); zeile += entziffern(entklammern(s.slice(1, -1)), tabelle); }
        else if (s[0] === '<') { nimmGrad(); zeile += hexZuText(s.slice(1, -1), tabelle); }
        else if (parseFloat(s) < -180) zeile += ' ';      /* großer Vorschub = Leerzeichen */
      }
    } else if (treffer[4] !== undefined) {
      nimmGrad(); zeile += entziffern(entklammern(treffer[4]), tabelle);
    } else if (treffer[5] !== undefined) {
      nimmGrad(); zeile += hexZuText(treffer[5], tabelle);
    } else if (treffer[7] !== undefined) {
      /* Td/TD ist hier der Vorschub von Zeichen zu Zeichen. Aus einem
         waagerechten Vorschub ein Leerzeichen zu machen wäre falsch: die
         Wortzwischenräume stehen als eigenes Zeichen im Text. Nur ein
         Sprung in der Höhe ist eine neue Zeile. */
      if (Math.abs(parseFloat(treffer[7])) > 0.4) umbruch();
    } else if (treffer[9] !== undefined) {
      /* Die Textmatrix trägt nicht nur den Ort, sondern auch den Maßstab.
         Viele Erzeuger schreiben „/F1 1 Tf“ und setzen die Größe erst hier:
         „14 0 0 14 x y Tm“. Wer nur Tf liest, misst dann für jede Zeile
         denselben Grad — und die Abschnittserkennung, die genau vom
         Größenunterschied lebt, fällt ersatzlos aus. Der Text kam dabei
         vollständig an, es fehlte nur die Gliederung, und das sieht man
         einer Datei nicht an.
         Gelesen wird aus dem Treffer selbst, nicht über weitere Gruppen:
         Eine zusätzliche Klammer verschiebt die Nummern jeder späteren
         Anweisung, und genau daran ist hier schon einmal alles gerissen. */
      const m = treffer[0].trim().split(/\s+/).slice(0, 6).map(parseFloat);
      const massstab = skalierung(m);
      if (isFinite(massstab) && massstab > 0) {
        tmMassstab = massstab;
        grad = tfGrad * tmMassstab * skalierung(flaeche);
      }
      hoehe(treffer[8], treffer[9]);
    } else if (treffer[10] !== undefined) {
      if (treffer[10] === 'T*') umbruch();
      /* BT setzt die Textmatrix auf die Einheitsmatrix zurück. */
      if (treffer[10] === 'BT') { tmMassstab = 1; grad = tfGrad * skalierung(flaeche); }
    } else if (treffer[11] !== undefined) {
      const neu = [11, 12, 13, 14, 15, 16].map(i => parseFloat(treffer[i]));
      if (neu.every(isFinite)) flaeche = malnehmen(neu, flaeche);
    } else if (treffer[17] !== undefined) {
      if (treffer[17] === 'q') stapel.push(flaeche.slice());
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

  /* Höhen, auf denen beide Seiten Text haben.
     Verglichen wird mit Spielraum, nicht in festen Fächern: Zwei Spalten
     haben selten dieselbe Grundlinie — eine andere Zeilenhöhe verschiebt
     sie um ein paar Punkte. In Sechser-Fächern landen sie dann nebenan,
     die Zeile gilt nicht als gemeinsam, und der zweispaltige Bereich
     beginnt erst darunter. Die Zeile darüber wird über den Graben hinweg
     gelesen: „BERUFSERFAHRUNG SCHEINE“ — zwei Überschriften, eine Zeile. */
  const abstaende = [];
  const sortiertY = laeufe.map(l => l.y).sort((a, b) => a - b);
  for (let i = 1; i < sortiertY.length; i++) {
    const d = sortiertY[i] - sortiertY[i - 1];
    if (d > 1 && d < 60) abstaende.push(d);
  }
  const zeilenhoehe = abstaende.length
    ? abstaende.sort((a, b) => a - b)[Math.floor(abstaende.length / 2)] : 12;
  const spielraum = Math.max(6, zeilenhoehe * 0.8);
  const rechteY = rechts.map(l => l.y);
  const gemeinsam = links
    .filter(l => rechteY.some(y => Math.abs(y - l.y) <= spielraum))
    .map(l => l.y);
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
  return laeufe.map(l => ({ x: l.x, y: -l.y, text: l.text, grad: l.grad }));
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
    /* Getrennt wird dort, wo die rechte Spalte wirklich beginnt: am
       kleinsten x rechts vom Anfang der freien Bahn.
       Vorher stand hier eine Quote — 85 % der Bahnbreite —, weil die Bahn
       meist breiter ist als der Zwischenraum. Die Quote trifft aber nicht,
       sobald die Spalte eine eingerückte Aufzählung enthält: Dann bildet
       deren Rand die Bahn, die Überschrift darüber steht vierzehn Einheiten
       weiter links, und die Trennstelle schneidet sie ab. „SCHEINE“ fiel so
       in die linke Spalte und stand hinter „BERUFSERFAHRUNG“ in derselben
       Zeile. Der kleinste x-Wert ist keine Schätzung, sondern der Rand. */
    const mitte = spaltenRand(laeufe, spannen, bandVon, bis);
    if (bis - bandVon >= mindestens
        && mitte > links + breite * 0.15 && mitte < links + breite * 0.85) {
      if (spalteTraegt(laeufe.filter(l => l.x < mitte), laeufe)
          && spalteTraegt(laeufe.filter(l => l.x >= mitte), laeufe)) stelle = mitte;
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

/* Wo beginnt die Spalte rechts der freien Bahn?
 *
 * Nicht bei einer festen Quote der Bahnbreite: Enthält die Spalte eine
 * eingerückte Aufzählung, bildet deren Rand die Bahn, die Überschrift
 * darüber steht weiter links, und die Trennstelle schneidet sie ab — so
 * stand „SCHEINE“ hinter „BERUFSERFAHRUNG“ in einer Zeile.
 *
 * Aber auch nicht beim kleinsten x rechts der Bahn: Das greift jeden
 * Ausreißer, der zufällig ein Stück weiter links beginnt, und zieht die
 * Trennstelle über den halben Zwischenraum. Bei einem echten Lebenslauf
 * wanderte damit eine ganze Rubrik in die falsche Spalte.
 *
 * Ein Spaltenrand ist die Stelle, an der VIELE Zeilen anfangen. Gesucht
 * wird deshalb der kleinste x-Wert, den mindestens drei Läufe teilen. */
function spaltenRand(laeufe, spannen, bandVon, bis) {
  const kandidaten = [];
  for (let i = 0; i < laeufe.length; i++) {
    /* Beginnt in der Bahn und endet rechts von ihr: gehört nach rechts.
       Beginnt in der Bahn und endet darin: ein Ausreißer der linken Spalte,
       und genau so einer hat die Trennstelle einmal über den halben
       Zwischenraum gezogen. */
    if (laeufe[i].x > bandVon && spannen[i][1] > bis) kandidaten.push(laeufe[i].x);
  }
  return kandidaten.length ? Math.min(...kandidaten) - 1
                           : bis - (bis - bandVon) * 0.15;
}

/* Trägt diese Seite des Grabens eine eigene Spalte?
 *
 * Vorher wurde gefragt, welcher Anteil des Textes rechts vom Graben steht,
 * und alles unter einem Viertel verworfen. Das trifft den falschen Fall:
 * Eine schmale Leiste mit zwei kurzen Listen — Scheine, Sprachen — kommt
 * nie auf ein Viertel, obwohl der Graben sauber ist. Die Seite wurde dann
 * zeilenweise über ihn hinweg gelesen, und aus zwei Überschriften wurde
 * „BERUFSERFAHRUNG SCHEINE“.
 *
 * Gefragt wird stattdessen nach dem, was eine Spalte ausmacht: mehrere
 * Zeilen, die sich über einen nennenswerten Teil der Texthöhe verteilen.
 * Das unterscheidet eine echte Leiste von einer Seitenzahl in der Ecke,
 * und genau dafür war die Anteilsgrenze gedacht. */
function spalteTraegt(teil, alle) {
  if (teil.length < 4) return false;
  const spanne = (l) => Math.max(...l.map(x => x.y)) - Math.min(...l.map(x => x.y));
  const ganz = spanne(alle);
  if (ganz <= 0) return false;
  const reihen = new Set(teil.map(l => Math.round(l.y / 6))).size;
  return reihen >= 3 && spanne(teil) >= ganz * 0.25;
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
    /* Erst ab zwei Einheiten ist es der Abstand zweier Zeilen. Was darunter
       liegt, ist der Versatz eines Aufzählungszeichens gegen seinen Text. */
    if (d > 2 && d < 60) abstaende.push(d);
  }
  abstaende.sort((a, b) => a - b);
  const zeilenabstand = abstaende.length ? abstaende[Math.floor(abstaende.length / 2)] : 0;
  const gleicheZeile = Math.max(1.5, zeilenabstand * 0.4);

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
    /* Zwei Läufe auf derselben Höhe sind eine Zeile — auch wenn die halbe
       Spalte zwischen ihnen liegt. „Maschinenbau“ links und „09/2011 –
       08/2014“ rechtsbündig stehen im Dokument nebeneinander; untereinander
       geschrieben weiß niemand mehr, ob der Zeitraum zum Fach darüber oder
       zur Hochschule darunter gehört, und das Modell rät. Auf dem Blatt
       standen dann Fach und Einrichtung über Kreuz. */
    if (letzte && Math.abs(lauf.y - letzteY) <= gleicheZeile) {
      const nurMarke = MARKE_ALLEIN.test(letzte.text.trim());
      letzte.text += ' ' + lauf.text;
      letzte.grad = Math.max(letzte.grad || 0, lauf.grad || 0);
      /* Das Aufzählungszeichen ist nicht der Anfang der Zeile, sondern was
         dahinter steht — sonst zeigt die Einrückung an die falsche Stelle. */
      if (nurMarke) letzte.x = lauf.x;
      letzteY = lauf.y;
      letztesEnde = ende(lauf);
      continue;
    }
    const randErreicht = !!letzte && amRand(letzte, letztesEnde);
    if (letzte && gehoertDazu(letzte, letzteY, lauf, zeilenabstand, randErreicht)) {
      letzte.text = verbinden(letzte.text, lauf.text);
      letzte.grad = Math.max(letzte.grad || 0, lauf.grad || 0);
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
    letzte = { x: lauf.x, y: lauf.y, text: lauf.text, grad: lauf.grad || 0 };
    letzteY = lauf.y;
    aus.push(letzte);
  }
  return aus.map(l => (l === ABSATZ ? { text: '', grad: 0 }
                                    : { text: l.text, grad: l.grad || 0 }));
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
      stuecke.push(...seiteZuText(zeichenketten(text, new Map())));
    }
  }
  return saeubern(stuecke);
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

/* Aus den Zeilen wird der Text — und die Gliederung.
 *
 * Welche Zeile eine Überschrift ist, muss niemand raten: Sie steht größer da
 * als der Abschnitt, den sie überschreibt. Das ist keine Feinheit des
 * Layouts, sondern der Grund, warum ein Mensch den Lebenslauf auf einen Blick
 * gliedern kann — und es steht im Dokument, Anweisung für Anweisung
 * („/F5 14 Tf“ gegen „/F4 10 Tf“).
 *
 * Der Körpergrad ist der, in dem die meisten Zeichen gesetzt sind. Alles, was
 * deutlich größer ist, ist eine Überschrift; zwei gleich große Zeilen
 * hintereinander sind eine („ZUSÄTZLICHE“ / „QUALIFIKATIONEN“). Der Name
 * ganz oben ist meist noch größer und wird nicht zur Rubrik erklärt — wo er
 * steht, weiß der Kopf des Dokuments ohnehin.
 */
function saeubern(zeilen) {
  const sauber = zeilen.map(z => ({
    text: String(z.text || '').replace(/[ \t]+/g, ' ').trim(),
    grad: z.grad || 0,
  }));
  /* Die Leerzeilen bleiben bis hierher stehen — sie sind das einzige, was der
     Durchgang ohne Geometrie noch von den Abständen der Seite weiß. */
  const fertig = zusammenfuegen(sauber).filter(z => z.text);
  return { text: fertig.map(z => z.text).join('\n'), ueberschriften: ueberschriftenAus(fertig) };
}

function ueberschriftenAus(zeilen) {
  const gewicht = new Map();
  zeilen.forEach(z => {
    const g = Math.round(z.grad * 2) / 2;
    if (g > 0) gewicht.set(g, (gewicht.get(g) || 0) + z.text.length);
  });
  if (!gewicht.size) return [];
  const koerper = [...gewicht.entries()].sort((a, b) => b[1] - a[1])[0][0];
  /* „Deutlich größer“ heißt: ein Zehntel über dem Körpergrad und mindestens
     einen halben Punkt. Eine fette Zeile in derselben Größe zählt nicht —
     Firmennamen sind auch fett. */
  const schwelle = Math.max(koerper * 1.1, koerper + 0.5);

  const aus = [];
  zeilen.forEach((z, i) => {
    if (z.grad < schwelle) return;
    const vor = aus[aus.length - 1];
    /* Zwei gleich große Zeilen unmittelbar hintereinander sind eine
       Überschrift, die umbrochen wurde. */
    if (vor && vor.bis === i - 1 && Math.abs(zeilen[i - 1].grad - z.grad) < 0.1) {
      vor.bis = i; vor.titel += ' ' + z.text;
      return;
    }
    aus.push({ von: i + 1, bis: i, titel: z.text, grad: z.grad });
  });
  return aus.map(u => ({ von: u.von, bis: u.bis + 1, titel: u.titel, grad: u.grad }));
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
  for (const stueck of zeilen) {
    const roh = stueck.text;
    /* Ein Aufzählungszeichen steht im PDF oft als eigener Lauf — es wird an
       einer anderen Stelle gesetzt als der Text dahinter. Allein ist es keine
       Zeile, sondern der Anfang der nächsten. */
    if (MARKE_ALLEIN.test(roh)) { marke = '• '; continue; }
    if (!roh) { aus.push({ text: '', grad: 0 }); continue; }   /* Luft trennt */
    const zeile = marke + roh;
    marke = '';
    const letzte = aus.length ? aus[aus.length - 1] : null;
    const oben = letzte ? letzte.text : null;
    const haengend = HAENGEND.test(oben || '');
    const passt = oben && oben.length > 20 &&
      !/[.;:!?]$/.test(oben) &&
      !/^[\u2022\u00b7\u25cf\u2013\u2014-]\s/.test(zeile) &&
      !/^\d/.test(zeile) && !ZEITRAUM.test(oben) &&
      (/^[a-z\u00e4\u00f6\u00fc\u00df(]/.test(zeile) || haengend || OFFEN.test(oben));
    if (!passt) { aus.push({ text: zeile, grad: stueck.grad }); continue; }
    letzte.text = verbinden(oben, zeile);
    letzte.grad = Math.max(letzte.grad, stueck.grad);
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
window.pdfLesen = pdfLesen;
window.textTaugt = textTaugt;
window.pdfBilder = pdfBilder;
})();
