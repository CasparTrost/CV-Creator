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
    for (const nummer of inhaltsNummern(seite.koerper)) {
      const text = await stromText(roh, bytes, objekte, nummer);
      if (text) stuecke.push(zeichenketten(text, schriften));
    }
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

async function stromBytes(roh, bytes, objekte, nummer) {
  const eintrag = objekte.get(nummer);
  if (!eintrag || eintrag.stelle === undefined) return null;   /* im Objektstrom: nie ein Strom */
  const koerper = koerperVon(roh, eintrag);
  const marke = /(?:^|[^A-Za-z])stream\r?\n/.exec(koerper);
  if (!marke) return null;
  const von = eintrag.stelle + marke.index + marke[0].length;
  const bis = roh.indexOf('endstream', von);
  if (bis < 0) return null;
  let ende = bis;
  while (ende > von && (roh[ende - 1] === '\n' || roh[ende - 1] === '\r')) ende--;
  return { feld: bytes.subarray(von, ende), gepackt: /\/FlateDecode/.test(koerper) };
}

async function stromText(roh, bytes, objekte, nummer) {
  const strom = await stromBytes(roh, bytes, objekte, nummer);
  if (!strom) return null;
  if (!strom.gepackt) return new TextDecoder('windows-1252').decode(strom.feld);
  for (const art of ['deflate', 'deflate-raw']) {
    try {
      const packe = new Blob([strom.feld]).stream().pipeThrough(new DecompressionStream(art));
      return new TextDecoder('windows-1252').decode(await new Response(packe).arrayBuffer());
    } catch (e) { /* nächster Versuch */ }
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
  const zeilen = [];
  let zeile = '', tabelle = null, letzteHoehe = null;

  const anweisung = new RegExp([
    '\\/([^\\s/]+)\\s+[\\d.]+\\s+Tf',                    /* 1 Schrift */
    '\\[((?:[^\\[\\]\\\\]|\\\\.)*)\\]\\s*TJ',    /* 2 Feld */
    '\\(((?:[^()\\\\]|\\\\.)*)\\)\\s*(?:Tj|\')',    /* 3 Kette */
    '<([0-9A-Fa-f\\s]*)>\\s*Tj',                               /* 4 Hex */
    '(-?[\\d.]+)\\s+(-?[\\d.]+)\\s+(?:Td|TD)',             /* 5,6 Vorschub */
    '(?:-?[\\d.]+\\s+){4}(-?[\\d.]+)\\s+(-?[\\d.]+)\\s+Tm',  /* 7,8 Matrix */
    '(T\\*|ET|BT)',                                              /* 9 Zeile/Block */
  ].join('|'), 'g');

  const umbruch = () => { if (zeile.trim()) zeilen.push(zeile.trim()); zeile = ''; };
  /* Jeder Textlauf beginnt mit einer Matrix, die seine Höhe nennt. Gleiche
     Höhe heißt gleiche Zeile — dort gehört ein Leerzeichen dazwischen, etwa
     zwischen einer Position und ihrem Zeitraum am rechten Rand. */
  const hoehe = (wert) => {
    const y = parseFloat(wert);
    if (!isFinite(y)) return;
    if (letzteHoehe === null || Math.abs(y - letzteHoehe) > 0.4) umbruch();
    else if (zeile && !/\s$/.test(zeile)) zeile += ' ';
    letzteHoehe = y;
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
      hoehe(treffer[8]);
    } else if (treffer[9] !== undefined) {
      if (treffer[9] === 'T*') umbruch();
    }
  }
  umbruch();
  return zeilen.join('\n');
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
    if (text && /\b(Tj|TJ)\b/.test(text)) stuecke.push(zeichenketten(text, new Map()));
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
function zusammenfuegen(zeilen) {
  const aus = [];
  for (const zeile of zeilen) {
    const oben = aus.length ? aus[aus.length - 1] : null;
    /* Zwei sichere Fälle: die untere Zeile beginnt klein, oder die obere
       endet auf ein Wort, nach dem kein Satz enden kann. Alles andere bleibt
       getrennt — eine falsch zusammengezogene Zeile ist schlimmer als eine
       zu viel, und ein Sprachmodell bringt beides in Ordnung. */
    const haengend = /(^|\s)(und|oder|sowie|mit|f\u00fcr|in|im|am|zur|zum|von|bis|der|die|das|den|des|ein|eine|einer|and|or|with|for|of|the|to|a|an|y|o|con|para|de)$/i.test(oben || '');
    const passt = oben && oben.length > 20 &&
      !/[.;:!?)\]]$/.test(oben) &&
      !/^\d/.test(zeile) &&
      (/^[a-z\u00e4\u00f6\u00fc\u00df(]/.test(zeile) || haengend);
    if (!passt) { aus.push(zeile); continue; }
    if (/[\u2010-\u2014-]$/.test(oben)) aus[aus.length - 1] = oben.slice(0, -1) + zeile;
    else aus[aus.length - 1] = oben + ' ' + zeile;
  }
  return aus;
}

window.pdfText = pdfText;
window.textTaugt = textTaugt;
})();
