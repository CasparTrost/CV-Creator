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
  const seiten = [];

  for (const [nummer, stelle] of objekte) {
    const koerper = objektKoerper(roh, stelle);
    if (!/\/Type\s*\/Page[^s]/.test(koerper)) continue;
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
    index.set(parseInt(treffer[1], 10), treffer.index + treffer[0].indexOf(treffer[1]));
  }
  return index;
}

function objektKoerper(roh, stelle) {
  const ende = roh.indexOf('endobj', stelle);
  return roh.slice(stelle, ende < 0 ? stelle + 4000 : ende);
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
  const stelle = objekte.get(nummer);
  if (stelle === undefined) return null;
  const koerper = objektKoerper(roh, stelle);
  const marke = /(?:^|[^A-Za-z])stream\r?\n/.exec(koerper);
  if (!marke) return null;
  const von = stelle + marke.index + marke[0].length;
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
  if (ressourcen !== null && objekte.has(ressourcen)) quelle = objektKoerper(roh, objekte.get(ressourcen));

  const block = /\/Font\s*<<([\s\S]*?)>>/.exec(quelle);
  if (!block) return tabellen;

  for (const t of block[1].matchAll(/\/([^\s/]+)\s+(\d+)\s+0\s+R/g)) {
    const name = t[1], nummer = parseInt(t[2], 10);
    if (!objekte.has(nummer)) continue;
    const schrift = objektKoerper(roh, objekte.get(nummer));
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

function saeubern(text) {
  return text.replace(/[ \t]+/g, ' ')
             .split('\n').map(z => z.trim()).filter(Boolean)
             .join('\n').replace(/\n{3,}/g, '\n\n').trim();
}
