/*
 * Der Vermittler zwischen Browser und Sprachmodell.
 *
 * Warum es ihn gibt: Ein API-Schlüssel im Browser ist ein veröffentlichter
 * Schlüssel. Jede Seite, die das anders macht, bezahlt fremde Rechnungen.
 * Dieser Worker hält den Schlüssel, begrenzt, was durchgeht, und ist das
 * einzige Stück Server, das die Seite hat.
 *
 * Er läuft auf Cloudflare Workers (kostenloses Kontingent reicht weit).
 * Einrichtung: api/README.md.
 *
 * Endpunkte, alle POST mit JSON, außer /status:
 *   /parse   {text} | {datei:{name,typ,daten}}   -> {lebenslauf}
 *   /tailor  {lebenslauf, stelle}                -> {lebenslauf, aenderungen, luecken}
 *   /stelle  {url}                               -> {text, titel}
 *   /status                                      -> Selbstauskunft, ohne Geheimnisse
 */
import { PARSE, TAILOR, PRUEFER, ANALYSE } from './prompts.js';
import { pdfText, textTaugt } from './pdf.js';

const GRENZEN = {
  koerper: 6 * 1024 * 1024,   /* Anfrage insgesamt */
  text: 60000,                /* Zeichen Lebenslauftext */
  stelle: 20000,              /* Zeichen Stellenanzeige */
  proTagUndIP: 20,            /* nur mit KV-Bindung LIMITS */
};

export default {
  async fetch(anfrage, umgebung) {
    const url = new URL(anfrage.url);
    const weg = url.pathname.replace(/^\/api/, '') || '/';
    const kopf = corsKopf(anfrage, umgebung);

    if (anfrage.method === 'OPTIONS') return new Response(null, { status: 204, headers: kopf });
    if (weg === '/status') return antwort({
      bereit: !!umgebung.COMETAPI_KEY,
      modell: modell(umgebung),
      grenze: umgebung.LIMITS ? GRENZEN.proTagUndIP + ' Anfragen pro Tag und IP' : 'ohne KV-Bindung ungebremst',
    }, 200, kopf);

    if (anfrage.method !== 'POST') return antwort({ fehler: 'nur POST' }, 405, kopf);
    if (!umgebung.COMETAPI_KEY) return antwort({ fehler: 'Der Dienst ist nicht eingerichtet.' }, 503, kopf);

    const zuviel = await bremse(anfrage, umgebung);
    if (zuviel) return antwort({ fehler: zuviel }, 429, kopf);

    let daten;
    try {
      const roh = await anfrage.text();
      if (roh.length > GRENZEN.koerper) return antwort({ fehler: 'Die Datei ist zu groß.' }, 413, kopf);
      daten = JSON.parse(roh);
    } catch (e) {
      return antwort({ fehler: 'Ungültige Anfrage.' }, 400, kopf);
    }

    try {
      if (weg === '/parse') return antwort(await lesen(daten, umgebung), 200, kopf);
      if (weg === '/tailor') return antwort(await zuschneiden(daten, umgebung), 200, kopf);
      if (weg === '/analyse') return antwort(await ansehen(daten, umgebung), 200, kopf);
      if (weg === '/stelle') return antwort(await stelleHolen(daten), 200, kopf);
      return antwort({ fehler: 'Unbekannter Endpunkt.' }, 404, kopf);
    } catch (e) {
      /* Die Meldung des Anbieters kann Interna enthalten — nach außen geht
         nur, was dem Benutzer weiterhilft. */
      console.log('Fehler:', e && e.stack || e);
      return antwort({ fehler: (e && e.freundlich) || 'Das hat nicht geklappt. Bitte später noch einmal.' },
                     (e && e.status) || 502, kopf);
    }
  },
};

/* ------------------------------------------------------------- Bausteine */

function modell(umgebung){ return umgebung.MODELL || 'gemini-3.5-flash'; }
function basis(umgebung){ return (umgebung.BASIS || 'https://api.cometapi.com/v1').replace(/\/$/, ''); }

function corsKopf(anfrage, umgebung) {
  const erlaubt = (umgebung.HERKUNFT || '').split(',').map(s => s.trim()).filter(Boolean);
  const woher = anfrage.headers.get('Origin') || '';
  const passt = erlaubt.length === 0 ? '*'
    : (erlaubt.includes(woher) || /^https?:\/\/localhost(:\d+)?$/.test(woher) ? woher : erlaubt[0]);
  return {
    'Access-Control-Allow-Origin': passt,
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Max-Age': '86400',
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'no-store',
  };
}

function antwort(daten, status, kopf) {
  return new Response(JSON.stringify(daten), { status, headers: kopf });
}

function fehler(text, status) {
  const e = new Error(text); e.freundlich = text; e.status = status || 502; return e;
}

/* Eine grobe Bremse pro IP und Tag, damit eine fremde Schleife nicht das
   Guthaben leerräumt. Ohne KV-Bindung läuft der Worker ungebremst — das steht
   so in /status und in der README. */
async function bremse(anfrage, umgebung) {
  if (!umgebung.LIMITS) return null;
  const ip = anfrage.headers.get('CF-Connecting-IP') || 'unbekannt';
  const tag = new Date().toISOString().slice(0, 10);
  const schluessel = `${tag}:${ip}`;
  const stand = parseInt(await umgebung.LIMITS.get(schluessel) || '0', 10);
  if (stand >= GRENZEN.proTagUndIP) return 'Für heute ist das Kontingent aufgebraucht.';
  await umgebung.LIMITS.put(schluessel, String(stand + 1), { expirationTtl: 60 * 60 * 30 });
  return null;
}

/* ---------------------------------------------------------- Modellaufruf */

async function fragen(umgebung, system, inhalt, temperatur) {
  const antwortModell = await fetch(basis(umgebung) + '/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ' + umgebung.COMETAPI_KEY,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: modell(umgebung),
      temperature: temperatur === undefined ? 0.2 : temperatur,
      response_format: { type: 'json_object' },
      messages: [
        { role: 'system', content: system },
        { role: 'user', content: inhalt },
      ],
    }),
  });

  if (!antwortModell.ok) {
    const text = (await antwortModell.text()).slice(0, 400);
    console.log('Anbieter', antwortModell.status, text);
    if (antwortModell.status === 401) throw fehler('Der Schlüssel wird nicht angenommen.', 502);
    if (antwortModell.status === 429) throw fehler('Der Dienst ist gerade ausgelastet. Bitte kurz warten.', 429);
    throw fehler('Der Dienst antwortet nicht wie erwartet.', 502);
  }
  const daten = await antwortModell.json();
  const text = daten && daten.choices && daten.choices[0] &&
               daten.choices[0].message && daten.choices[0].message.content;
  if (!text) throw fehler('Leere Antwort vom Dienst.', 502);
  return jsonAus(text);
}

/* Manche Modelle legen trotz response_format einen Zaun aus ```json. */
function jsonAus(text) {
  const sauber = String(text).trim().replace(/^```(?:json)?/i, '').replace(/```$/, '').trim();
  try { return JSON.parse(sauber); } catch (e) { /* weiter unten */ }
  const von = sauber.indexOf('{'), bis = sauber.lastIndexOf('}');
  if (von >= 0 && bis > von) {
    try { return JSON.parse(sauber.slice(von, bis + 1)); } catch (e) { /* nichts */ }
  }
  throw fehler('Die Antwort war nicht lesbar.', 502);
}

/* ------------------------------------------------------------------ lesen */

async function lesen(daten, umgebung) {
  let text = (daten.text || '').trim();

  if (!text && daten.datei && daten.datei.daten) {
    const roh = base64Aus(daten.datei.daten);
    const name = (daten.datei.name || '').toLowerCase();
    if (name.endsWith('.pdf') || (daten.datei.typ || '').includes('pdf')) {
      text = await pdfText(roh);
      if (!brauchbar(text)) {
        /* Gescannt oder mit eingebetteten Schriften ohne Zuordnung: dann
           bekommt das Modell die Datei selbst zu sehen. */
        return await lesenAusDatei(daten.datei, umgebung);
      }
    } else {
      throw fehler('Dieses Dateiformat kann ich nicht lesen. Bitte PDF, DOCX oder Text.', 415);
    }
  }

  if (!text) throw fehler('Es war kein Text in der Datei.', 400);
  text = text.slice(0, GRENZEN.text);
  const ergebnis = await fragen(umgebung, PARSE,
    'Hier ist der Text eines Lebenslaufs. Gib das JSON zurück.\n\n---\n' + text, 0.1);
  if (ergebnis && ergebnis.fehler) throw fehler('Das sieht nicht nach einem Lebenslauf aus.', 422);
  return { lebenslauf: ergebnis };
}

async function lesenAusDatei(datei, umgebung) {
  const antwortModell = await fetch(basis(umgebung) + '/chat/completions', {
    method: 'POST',
    headers: { 'Authorization': 'Bearer ' + umgebung.COMETAPI_KEY, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: modell(umgebung),
      temperature: 0.1,
      response_format: { type: 'json_object' },
      messages: [
        { role: 'system', content: PARSE },
        { role: 'user', content: [
          { type: 'text', text: 'Hier ist ein Lebenslauf als Datei. Gib das JSON zurück.' },
          { type: 'file', file: { filename: datei.name || 'lebenslauf.pdf',
                                  file_data: 'data:application/pdf;base64,' + datei.daten } },
        ] },
      ],
    }),
  });
  if (!antwortModell.ok) {
    console.log('Datei-Weg', antwortModell.status, (await antwortModell.text()).slice(0, 300));
    throw fehler('Aus diesem PDF lässt sich kein Text lesen — vermutlich ein Scan. '
               + 'Bitte den Text einfügen oder eine DOCX-Datei nehmen.', 422);
  }
  const daten = await antwortModell.json();
  const inhalt = daten.choices && daten.choices[0] && daten.choices[0].message.content;
  return { lebenslauf: jsonAus(inhalt) };
}

/* ------------------------------------------------------------ zuschneiden */

async function zuschneiden(daten, umgebung) {
  const lebenslauf = daten.lebenslauf;
  const stelle = String(daten.stelle || '').trim().slice(0, GRENZEN.stelle);
  if (!lebenslauf || typeof lebenslauf !== 'object') throw fehler('Kein Lebenslauf übergeben.', 400);
  if (stelle.length < 80) throw fehler('Die Stellenbeschreibung ist zu kurz.', 400);

  const ergebnis = await fragen(umgebung, TAILOR,
    'STELLENANZEIGE\n---\n' + stelle +
    '\n\nLEBENSLAUF (JSON)\n---\n' + JSON.stringify(lebenslauf), 0.3);

  /* Der zweite Blick: dasselbe Modell prüft das Ergebnis gegen das Original.
     Zwei kleine Aufrufe sind billiger als eine erfundene Zahl im Lebenslauf. */
  let beanstandet = [];
  try {
    const pruefung = await fragen(umgebung, PRUEFER,
      'ORIGINAL\n---\n' + JSON.stringify(lebenslauf) +
      '\n\nNEU\n---\n' + JSON.stringify(ergebnis.lebenslauf || {}), 0);
    beanstandet = Array.isArray(pruefung.beanstandet) ? pruefung.beanstandet : [];
  } catch (e) {
    console.log('Prüfung fehlgeschlagen:', e && e.message);
  }

  return {
    lebenslauf: ergebnis.lebenslauf || lebenslauf,
    passung: ergebnis.passung || null,
    aenderungen: Array.isArray(ergebnis.aenderungen) ? ergebnis.aenderungen : [],
    luecken: Array.isArray(ergebnis.luecken) ? ergebnis.luecken : [],
    beanstandet,
  };
}

/* ---------------------------------------------------------------- ansehen */

async function ansehen(daten, umgebung) {
  const lebenslauf = daten.lebenslauf;
  if (!lebenslauf || typeof lebenslauf !== 'object') throw fehler('Kein Lebenslauf übergeben.', 400);
  const stelle = String(daten.stelle || '').trim().slice(0, GRENZEN.stelle);
  /* Die Hinweise sind im Browser aus den Datumsangaben gerechnet, nicht
     geraten. Das Modell soll sie beurteilen, nicht noch einmal suchen. */
  const hinweise = Array.isArray(daten.hinweise) ? daten.hinweise.slice(0, 20) : [];

  const eingabe =
    'LEBENSLAUF (JSON)\n---\n' + JSON.stringify(lebenslauf) +
    (hinweise.length ? '\n\nBERECHNETE BEFUNDE (gegeben, nicht zu prüfen)\n---\n'
                       + hinweise.map(h => '- ' + h).join('\n') : '') +
    (stelle ? '\n\nSTELLENANZEIGE\n---\n' + stelle : '\n\n(keine Stellenanzeige)');

  const ergebnis = await fragen(umgebung, ANALYSE, eingabe, 0.4);
  const liste = (feld, grenze) => Array.isArray(ergebnis[feld]) ? ergebnis[feld].slice(0, grenze) : [];
  return {
    staerken: liste('staerken', 3),
    auffaelligkeiten: liste('auffaelligkeiten', 6),
    fragen: liste('fragen', 8),
    passung: stelle ? (ergebnis.passung || null) : null,
  };
}

/* -------------------------------------------------------- Stellenanzeige */

async function stelleHolen(daten) {
  let url;
  try { url = new URL(String(daten.url || '')); } catch (e) { throw fehler('Das ist keine gültige Adresse.', 400); }
  if (!/^https?:$/.test(url.protocol)) throw fehler('Nur http und https.', 400);
  if (/^(localhost|127\.|10\.|192\.168\.|169\.254\.|\[?::1)/i.test(url.hostname))
    throw fehler('Diese Adresse ist nicht erreichbar.', 400);

  let seite;
  try {
    seite = await fetch(url.toString(), {
      redirect: 'follow',
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; PlainSheet/1.0; +https://plainsheet.example/bot)',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'de,en;q=0.8',
      },
      cf: { cacheTtl: 300 },
    });
  } catch (e) {
    throw fehler('Die Seite war nicht erreichbar. Bitte den Text der Anzeige einfügen.', 502);
  }
  if (!seite.ok) {
    throw fehler(seite.status === 403 || seite.status === 401
      ? 'Diese Jobbörse lässt sich nicht auslesen. Bitte den Text der Anzeige einfügen.'
      : 'Die Seite antwortet mit Fehler ' + seite.status + '. Bitte den Text einfügen.', 422);
  }
  const html = (await seite.text()).slice(0, 2 * 1024 * 1024);
  const text = textAusHtml(html);
  if (text.length < 200) {
    throw fehler('Auf der Seite stand kein lesbarer Text — viele Jobbörsen laden die Anzeige erst '
               + 'per Skript nach. Bitte den Text der Anzeige einfügen.', 422);
  }
  return { text: text.slice(0, GRENZEN.stelle), titel: titelAus(html), quelle: url.hostname };
}

function titelAus(html) {
  const t = /<title[^>]*>([\s\S]{0,200}?)<\/title>/i.exec(html);
  return t ? entzeichnen(t[1]).trim() : '';
}

function textAusHtml(html) {
  /* Erst die Teile weg, die nie Fließtext sind, dann die Marken. */
  let s = html
    .replace(/<script[\s\S]*?<\/script>/gi, ' ')
    .replace(/<style[\s\S]*?<\/style>/gi, ' ')
    .replace(/<noscript[\s\S]*?<\/noscript>/gi, ' ')
    .replace(/<nav[\s\S]*?<\/nav>/gi, ' ')
    .replace(/<footer[\s\S]*?<\/footer>/gi, ' ')
    .replace(/<header[\s\S]*?<\/header>/gi, ' ')
    .replace(/<!--[\s\S]*?-->/g, ' ');
  /* Blockenden werden zu Zeilenumbrüchen, damit Aufzählungen Aufzählungen bleiben. */
  s = s.replace(/<\/(p|div|li|h[1-6]|tr|section|article|br)\s*>/gi, '\n')
       .replace(/<br\s*\/?>/gi, '\n')
       .replace(/<li[^>]*>/gi, '• ')
       .replace(/<[^>]+>/g, ' ');
  s = entzeichnen(s);
  return s.split('\n').map(z => z.replace(/[ \t ]+/g, ' ').trim())
          .filter((z, i, alle) => z.length > 0 && !(i > 0 && z === alle[i - 1]))
          .join('\n').slice(0, 40000);
}

function entzeichnen(s) {
  const tabelle = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ',
                    auml: 'ä', ouml: 'ö', uuml: 'ü', Auml: 'Ä', Ouml: 'Ö', Uuml: 'Ü',
                    szlig: 'ß', euro: '€', ndash: '–', mdash: '—', hellip: '…' };
  return s.replace(/&(#x?[0-9a-f]+|[a-z]+);/gi, (ganz, name) => {
    if (name[0] === '#') {
      const zahl = name[1] === 'x' || name[1] === 'X'
        ? parseInt(name.slice(2), 16) : parseInt(name.slice(1), 10);
      return isFinite(zahl) ? String.fromCodePoint(zahl) : ganz;
    }
    return tabelle[name] !== undefined ? tabelle[name] : ganz;
  });
}

/* ------------------------------------------------------------------- PDF */

function base64Aus(s) {
  const roh = atob(String(s).replace(/^data:[^,]*,/, ''));
  const feld = new Uint8Array(roh.length);
  for (let i = 0; i < roh.length; i++) feld[i] = roh.charCodeAt(i);
  return feld;
}

/* Taugt der Text? Siehe textTaugt() in api/pdf.js — dort steht, warum der
   Anteil der Buchstaben allein nicht reicht. */
function brauchbar(text) {
  return textTaugt(text, 200);
}
