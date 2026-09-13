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
 *   /tailor  {lebenslauf, stelle}                -> {vorschlaege, passung, luecken}
 *   /stelle  {url}                               -> {text, titel}
 *   /status                                      -> Selbstauskunft, ohne Geheimnisse
 */
import { PARSE, GLIEDERUNG, ABSCHNITT, TAILOR, PRUEFER, ANALYSE } from './prompts.js';
import { textStellen, textSetzen, REIHENFOLGE } from './texte.js';
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

    /* „405 Method Not Allowed“ ist als erste Begegnung mit dem eigenen
       Dienst keine gute Auskunft. */
    if (anfrage.method === 'GET') {
      return new Response(
        'PlainSheet KI-Dienst\n\n' +
        (umgebung.COMETAPI_KEY ? 'Schlüssel ist hinterlegt.' : 'Es fehlt der Schlüssel (COMETAPI_KEY).') +
        '\nModell: ' + modell(umgebung) +
        '\n\nDiese Adresse wird vom Editor benutzt, nicht vom Browser.' +
        '\nSelbstauskunft als JSON: ' + new URL('/api/status', anfrage.url).toString() + '\n',
        { status: 200, headers: { ...kopf, 'Content-Type': 'text/plain; charset=utf-8' } });
    }
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
  /* Beim Entwickeln heißt derselbe Rechner mal localhost, mal 127.0.0.1
     und mal [::1] — je nachdem, was der Browser zuerst auflöst. */
  const daheim = /^https?:\/\/(localhost|127\.0\.0\.1|\[::1\])(:\d+)?$/.test(woher);
  const passt = erlaubt.length === 0 ? '*'
    : (erlaubt.includes(woher) || daheim ? woher : erlaubt[0]);
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

const ARTEN = ['kontakt', 'profil', 'beruf', 'ausbildung', 'weiterbildung',
               'sprachen', 'liste', 'text'];

/* Modelle nennen die Arten gern anders, als man sie ihnen genannt hat. Was
   sich zuordnen lässt, wird zugeordnet — und was übrig bleibt, gilt als
   Fließtext, nicht als Liste. Ein Absatz, den man als Liste behandelt, wird
   in Stücke geschnitten; eine Liste, die man als Absatz behandelt, bleibt
   heil. Der Zweifel gehört auf die Seite, die nichts kaputt macht. */
const ARTNAMEN = [
  [/kontakt|contact|adress|persoenlich|persönlich|datos|personal (data|details|information)/i, 'kontakt'],
  [/profil|summary|about|ueber mich|über mich|perfil/i, 'profil'],
  [/beruf|erfahrung|experience|werdegang|employment|praxis|station/i, 'beruf'],
  /* Das Genauere vor dem Allgemeineren: „Weiterbildung“ enthält „bildung“
     und ist trotzdem keine Ausbildung. */
  [/weiterbild|fortbild|zertifik|training|certific|kurs/i, 'weiterbildung'],
  [/ausbildung|bildung|studium|schul|education|academic|formaci|qualifikation|qualification/i, 'ausbildung'],
  [/sprach|language|idioma/i, 'sprachen'],
  [/liste|list|kenntnis|skill|kompetenz|competenc/i, 'liste'],
];

function artVon(wert) {
  const roh = String(wert || '').trim().toLowerCase();
  if (ARTEN.indexOf(roh) >= 0) return roh;
  for (const [muster, art] of ARTNAMEN) if (muster.test(roh)) return art;
  return 'text';
}

async function lesen(daten, umgebung) {
  let text = (daten.text || '').trim();

  if (!text && daten.datei && daten.datei.daten) {
    const roh = base64Aus(daten.datei.daten);
    const name = (daten.datei.name || '').toLowerCase();
    if (name.endsWith('.pdf') || (daten.datei.typ || '').includes('pdf')) {
      text = await pdfText(roh);
      if (!brauchbar(text)) {
        /* Gescannt oder mit eingebetteten Schriften ohne Zuordnung: dann
           bekommt das Modell die Datei selbst zu sehen. Eine Gliederung nach
           Zeilennummern gibt es dann nicht — die Zeilen kennt nur das
           Modell. Also der Weg am Stück. */
        return await lesenAusDatei(daten.datei, umgebung);
      }
    } else {
      throw fehler('Dieses Dateiformat kann ich nicht lesen. Bitte PDF, DOCX oder Text.', 415);
    }
  }

  if (!text) throw fehler('Es war kein Text in der Datei.', 400);
  return await nachGliederung(text.slice(0, GRENZEN.text), umgebung);
}

/* --------------------------------------------------------- in zwei Stufen

   Erst die Gliederung, dann jeder Abschnitt für sich. Warum, steht bei den
   Systemprompts; hier steht, was danach noch geprüft wird. */

async function nachGliederung(text, umgebung) {
  const zeilen = text.split(/\r?\n/).map(z => z.trim()).filter(Boolean).slice(0, 400);
  if (zeilen.length < 3) throw fehler('Das sieht nicht nach einem Lebenslauf aus.', 422);

  let plan = null;
  try {
    plan = await fragen(umgebung, GLIEDERUNG,
      zeilen.map((z, i) => (i + 1) + ': ' + z).join('\n'), 0);
  } catch (e) {
    console.log('Gliederung fehlgeschlagen:', e && e.message);
  }
  if (plan && plan.fehler) throw fehler('Das sieht nicht nach einem Lebenslauf aus.', 422);

  const bereiche = bereicheOrdnen(plan && plan.abschnitte, zeilen);
  /* Ohne brauchbare Gliederung lieber der alte Weg als gar keiner. */
  if (!bereiche.length) return await amStueck(text, umgebung);

  const kopf = {
    name: sauberText(plan.kopf && plan.kopf.name, 120),
    rolle: sauberText(plan.kopf && plan.kopf.rolle, 200),
    profil: '',
  };

  /* Eine Berufsbezeichnung ist ein Titel, kein Satz. Steht dort ein Satz, hat
     das Modell den Anfang des Kurzprofils erwischt — und der Rest steht dann
     als eigener Abschnitt darunter, mit unsichtbarer Naht. Also zurück in den
     Text damit. */
  const rolleRoh = kopf.rolle;          /* für den Vergleich weiter unten */
  const ausRolle = [];
  if (istFliesstext(kopf.rolle)) { ausRolle.push(kopf.rolle); kopf.rolle = ''; }

  /* Was über dem ersten Abschnitt steht und weder Name noch Rolle ist, darf
     nicht zwischen Kopf und erstem Abschnitt verschwinden. Kontaktzeilen
     werden ein Kontaktabschnitt, Fließtext wird Kurzprofil. */
  const stapel = bereiche.map(b => ({ ...b, zeilen: zeilen.slice(b.von - 1, b.bis) }));
  /* Verglichen wird mit dem, was oben stand, bevor die Rolle in den Text
     zurückgegeben wurde — sonst stünde dieselbe Zeile zweimal da. */
  const vorspann = uebrigerVorspann(zeilen.slice(0, bereiche[0].anfang - 1),
                                    { name: kopf.name, rolle: rolleRoh });
  const vorText = ohneDoppel(ausRolle.concat(vorspann.filter(z => !istKontaktZeile(z))));
  const vorDaten = vorspann.filter(istKontaktZeile);
  if (vorDaten.length) stapel.unshift({ titel: '', art: 'kontakt', zeilen: vorDaten });
  if (vorText.length) stapel.unshift({ titel: '', art: 'profil', zeilen: vorText });

  const gelesen = await Promise.all(stapel.map(b => abschnittLesen(b, umgebung)));

  const abschnitte = [];
  let nachgetragen = 0;
  gelesen.forEach(a => {
    nachgetragen += a.nachgetragen;
    if (!a.eintraege.length) return;
    /* Ein kurzes Kurzprofil gehört in den Kopf — aber nur dorthin. Beides
       zu setzen war der Grund, warum es zweimal auf dem Blatt stand. */
    /* Dieselbe Überschrift zweimal heißt nicht, dass der Lebenslauf sie
       zweimal hat — es heißt, dass das Modell einen Abschnitt zerschnitten
       hat. Auf dem Blatt standen sonst zwei „PERSONAL DATA“: eines in der
       Leiste mit der Anschrift, eines in der breiten Spalte mit dem
       Geburtsdatum. */
    const gleicher = a.titel && abschnitte.find(x => x.art === a.art && gleicheWorte(x.titel, a.titel));
    if (gleicher) { gleicher.eintraege = gleicher.eintraege.concat(a.eintraege); return; }
    if (a.art === 'profil') {
      /* Ein Kurzprofil gibt es einmal. Findet das Modell es in zwei Stücken —
         etwa weil es über einer Überschrift anfängt —, werden sie eines. */
      const schon = abschnitte.find(x => x.art === 'profil');
      if (schon){ schon.eintraege = schon.eintraege.concat(a.eintraege); return; }
    }
    abschnitte.push({ titel: a.titel, art: a.art, eintraege: a.eintraege });
  });

  /* Jetzt, wo alle Stücke beisammen sind: Das Kurzprofil gehört in den Kopf,
     unter den Namen — dort sucht es jeder, und die Vorlagen halten den Platz
     dafür frei. Wie viel dort hineinpasst, weiß der Editor: Er misst das
     Kopfband und legt das Profil erst dann als eigenen Abschnitt an, wenn es
     wirklich nicht mehr passt. Eine Zeichenzahl hier wäre geraten.
     Nur was gar kein Kurzprofil mehr sein kann, bleibt ein Abschnitt. */
  const profil = abschnitte.find(a => a.art === 'profil');
  if (profil) {
    const ganz = profil.eintraege.join(' ').replace(/\s+/g, ' ').trim();
    if (ganz.length <= 1400) {
      kopf.profil = ganz;
      abschnitte.splice(abschnitte.indexOf(profil), 1);
    }
  }
  if (!abschnitte.length && !kopf.profil) return await amStueck(text, umgebung);

  const lebenslauf = { sprache: spracheVon(plan), kopf, abschnitte };
  /* Das letzte Netz: Was trotz allem nirgends angekommen ist, steht am Ende
     des Blattes statt nirgends. Die Überschriften selbst zählen nicht mit —
     sie stehen in keinem Eintrag, ohne dass etwas fehlt. */
  const bekannt = abschnitte.map(a => a.titel).filter(Boolean);
  const offen = fehlendeZeilen(text, lebenslauf).filter(z => !bekannt.some(t => gleicheWorte(z, t)));
  if (offen.length) {
    abschnitte.push({ titel: RESTTITEL[lebenslauf.sprache] || RESTTITEL.de,
                      art: 'liste', eintraege: offen.slice(0, 40) });
  }
  return { lebenslauf, nachgetragen, offen: offen.length, deckung: deckungVon(text, lebenslauf) };
}

function spracheVon(plan) {
  const s = plan && typeof plan.sprache === 'string' ? plan.sprache.slice(0, 2).toLowerCase() : '';
  return ['de', 'en', 'es'].indexOf(s) >= 0 ? s : 'de';
}

/* Gekürzt wird nur als Notbremse gegen ein Modell, das Unsinn ausgibt — und
   dann an einer Wortgrenze. Ein Satz, der mitten im Wort abbricht, sieht aus
   wie ein Fehler des Bewerbers. */
function sauberText(wert, hoechstens) {
  const text = String(wert === undefined || wert === null ? '' : wert)
    .replace(/\s+/g, ' ').trim();
  const grenze = hoechstens || 400;
  if (text.length <= grenze) return text;
  const kurz = text.slice(0, grenze);
  const luecke = kurz.lastIndexOf(' ');
  return (luecke > grenze * 0.6 ? kurz.slice(0, luecke) : kurz).trim();
}

/* Die Bereiche des Modells sind Vorschläge, keine Zusicherung: Sie
   überlappen sich, lassen Löcher, zeigen ins Leere. Hier werden sie zu einer
   lückenlosen Folge — jede Zeile in genau einem Abschnitt. */
function bereicheOrdnen(liste, zeilen) {
  const anzahl = zeilen.length;
  const roh = (Array.isArray(liste) ? liste : [])
    .map(a => ({
      titel: sauberText(a && a.titel, 80),
      art: artVon(a && a.art),
      von: Math.min(anzahl, Math.max(1, parseInt(a && a.von, 10) || 0)),
      bis: Math.min(anzahl, Math.max(1, parseInt(a && a.bis, 10) || 0)),
    }))
    .filter(a => a.von && a.bis >= a.von)
    .sort((a, b) => a.von - b.von || a.bis - b.bis)
    .slice(0, 14);

  const aus = [];
  roh.forEach(a => {
    const vor = aus[aus.length - 1];
    if (vor) {
      /* Ein Abschnitt, den sein Vorgänger ganz verschluckt, verschwände hier
         samt seiner Überschrift — und mit ihm der Grund, warum er da war.
         Also bekommt der Vorgänger seine Grenze zurück. */
      if (a.bis <= vor.bis && a.von > vor.von) vor.bis = a.von - 1;
      if (a.von <= vor.bis) a.von = vor.bis + 1;      /* Überlappung abschneiden */
      else if (a.von > vor.bis + 1) vor.bis = a.von - 1;  /* Loch an den Vorgänger */
      if (a.bis < a.von) a.bis = a.von;
    }
    if (a.bis >= a.von) aus.push(a);
  });
  if (aus.length) aus[aus.length - 1].bis = anzahl;   /* bis zur letzten Zeile */

  /* Eine Überschrift nennt eine Rubrik, keine Station.
     „Sachbearbeiterin 02/2011 – 07/2016“ ist keine Rubrik, sondern die
     Station selbst: Das Modell hat mitten in der Berufserfahrung einen neuen
     Abschnitt aufgemacht. Auf dem Blatt steht dann jede Stelle als eigener
     Abschnitt mit eigener Überschrift — und weil ein Abschnitt seinen Titel
     nicht zweimal setzt, bleibt die halbe Seite darunter leer. */
  const zusammen = [];
  aus.forEach(a => {
    const vor = zusammen[zusammen.length - 1];
    const stationsHaft = vor && (vor.art === a.art
      || (a.art === 'text' && (vor.art === 'beruf' || vor.art === 'ausbildung')));
    if (stationsHaft && istStationsTitel(a.titel)) {
      vor.bis = a.bis;
      return;
    }
    zusammen.push(a);
  });

  /* Überschriften gehören niemandem — weder dem Abschnitt davor noch dem
     Inhalt danach. Sonst endet das Kurzprofil auf „… und reisebereit.
     KONTAKT“, und aus einer zweizeiligen Überschrift werden zwei
     Stichpunkte („ZUSÄTZLICHE“, „QUALIFIKATIONEN“) unter der ersten
     Ausbildung. Beides stand so auf dem Blatt. */
  /* Eine Aufzählung hat keine Zeiträume.
     Steht in einem Abschnitt mehrmals „09/2011 – 08/2014“, ist er keine
     Liste, sondern eine Folge von Stationen — und muss auch so gelesen
     werden. Sonst steht jede Zeile einzeln als Stichpunkt auf dem Blatt:
     Fach, Hochschule und Zeitraum gleichberechtigt untereinander, und von
     der Zuordnung ist nichts mehr übrig. Umgetauft wird nur, wenn die
     Überschrift sagt, wohin: „Zusätzliche Qualifikationen“ ist eine
     Ausbildung, „Publikationen“ bleibt eine Liste. */
  zusammen.forEach(a => {
    if (a.art !== 'liste' && a.art !== 'text') return;
    let mit = 0;
    for (let nr = a.von; nr <= a.bis; nr++) if (ZEITRAUM_ZEILE.test(zeilen[nr - 1] || '')) mit++;
    if (mit < 2) return;
    const nach = artVon(a.titel);
    if (nach === 'beruf' || nach === 'ausbildung' || nach === 'weiterbildung') a.art = nach;
  });

  zusammen.forEach(a => { if (!a.titel) titelNachholen(a, zeilen); });
  zusammen.forEach((a, i) => {
    const naechster = zusammen[i + 1];
    if (naechster) a.bis -= schlussZeilen(zeilen, a.bis, a.von, naechster.titel);
    /* „anfang“ ist der Anfang samt Überschrift. Was davor steht, ist der
       Vorspann des Dokuments — die Überschrift selbst gehört nicht dazu. */
    a.anfang = a.von;
    ueberschriftFassen(a, zeilen);
    if (a.bis < a.von) a.bis = a.von;
  });
  return zusammen;
}

const ZEITRAUM_ZEILE = /\d{1,2}\/\d{4}|\b(19|20)\d{2}\s*[\u2013\u2014-]\s*((19|20)\d{2}|heute|today|present|now)\b/i;

function istStationsTitel(titel) {
  const t = String(titel || '').trim();
  if (!t) return false;
  return /\d{1,2}\/\d{2,4}|\b(19|20)\d{2}\b/.test(t) || t.length > 55;
}

/* Wie viele Zeilen am Ende eines Bereichs gehören schon zur nächsten
   Überschrift? Höchstens drei, und nur solange jede Zeile aus Wörtern dieser
   Überschrift besteht — oder die ganze Überschrift enthält und kaum mehr. */
function schlussZeilen(zeilen, bis, von, titel) {
  const teil = new Set(worte(titel));
  if (!teil.size) return 0;
  let weg = 0;
  while (weg < 3 && bis - weg > von) {
    const w = worte(zeilen[bis - weg - 1]);
    if (!w.length || w.length > 4) break;
    const drin = w.every(x => teil.has(x));
    const umgekehrt = w.length <= teil.size + 1 && [...teil].every(x => w.includes(x));
    if (!drin && !umgekehrt) break;
    weg++;
  }
  return weg;
}

/* Die Überschrift steht im Dokument, und dort wird sie geholt.
 *
 * Sie kann über zwei Zeilen gehen („ZUSÄTZLICHE“ / „QUALIFIKATIONEN“), das
 * Modell kann sie halb mitgeschickt haben („PERSONAL“ statt „PERSONAL DATA“)
 * oder gar nicht. In allen drei Fällen sind die überschriftartigen Zeilen am
 * Anfang des Abschnitts die Überschrift: Sie werden abgeschnitten, und wenn
 * sie mehr hergeben als der gelieferte Titel, wird das der Titel.
 *
 * Überschriftartig heißt: kurz, ohne Zahl, ohne Trenner, ohne
 * Aufzählungszeichen davor — und entweder in Versalien oder aus Wörtern, die
 * schon im Titel stehen. Alles andere ist eine Angabe und bleibt stehen;
 * „Realschule – Nürnberg“ als Titel zu nehmen hieße, sie zu streichen. */
function ueberschriftFassen(bereich, zeilen) {
  const teil = new Set(worte(bereich.titel));
  const gesammelt = [];
  for (let nr = bereich.von; nr <= bereich.bis && gesammelt.length < 3; nr++) {
    const zeile = String(zeilen[nr - 1] || '').trim();
    if (!istUeberschrift(zeile) || MARKE_VORN.test(zeile)) break;
    const w = worte(zeile);
    if (!(w.length && w.every(x => teil.has(x))) && !istVersal(zeile)) break;
    gesammelt.push(zeile);
  }
  if (!gesammelt.length) return;
  bereich.von += gesammelt.length;
  const neu = gesammelt.join(' ');
  if (worte(neu).length >= teil.size) bereich.titel = sauberText(neu, 80);
}

const MARKE_VORN = /^[\u2022\u00b7\u25cf\u25e6\u25aa\u2043*]/;

/* Ein Abschnitt ohne Titel, dessen Überschrift im Dokument sehr wohl steht.
   Dann ist sie sein Titel und gehört aufs Blatt — nicht unser Ersatzwort, und
   erst recht nicht als Angabe mitten im Abschnitt: „PERSONAL DATA“ stand so
   als fünfte Kontaktzeile unter dem Geburtsdatum.

   Gesucht wird auch eine Zeile über dem Anfang: Beim Abschneiden der
   Überlappungen rutscht der Anfang schon mal einen Schritt weiter, und dann
   steht die Überschrift beim Abschnitt davor. Erkannt wird sie daran, dass
   sie kurz ist, keine Zahl enthält und dieselbe Rubrik nennt wie der
   Abschnitt — „Nürnberg“ wird so nie zur Überschrift. */
function titelNachholen(bereich, zeilen) {
  for (let nr = bereich.von; nr >= Math.max(1, bereich.von - 2); nr--) {
    const zeile = String(zeilen[nr - 1] || '').trim();
    if (!istUeberschrift(zeile) || MARKE_VORN.test(zeile)) continue;
    /* Ein Rubrikname allein ist eine Überschrift, zwei Wörter mit einem
       Rubriknamen darin sind es nicht: „Annähernd muttersprachliche“ enthält
       „sprach“ und ist trotzdem eine Angabe. Sie zum Titel zu machen hieße,
       sie vom Blatt zu nehmen — in Versalien dagegen ist die Sache klar. */
    const rubrik = artVon(zeile) === bereich.art && worte(zeile).length === 1;
    if (!rubrik && !istVersal(zeile)) continue;
    bereich.titel = sauberText(zeile, 80);
    return;
  }
}

/* Eine Überschrift ist kurz, trägt keine Zahl und keinen Trenner. „Realschule
   – Nürnberg“ ist eine Angabe, keine Rubrik; sie zum Titel zu machen hieße,
   sie vom Blatt zu streichen — und genau das ist passiert. */
function istUeberschrift(zeile) {
  if (!zeile || /\d/.test(zeile)) return false;
  if (/[|\u2013\u2014,;:]/.test(zeile)) return false;
  return worte(zeile).length >= 1 && zeile.split(/\s+/).length <= 4;
}

/* Versalien sind das verlässlichste Zeichen für eine Überschrift — und das
   einzige, das auch bei „INTERESSEN“ noch trägt, wo kein Rubrikname passt. */
function istVersal(zeile) {
  return !/\p{Ll}/u.test(zeile) && /\p{Lu}/u.test(zeile);
}

/* Satz oder Angabe? Ein Kurzprofil besteht aus Sätzen, eine Kontaktzeile aus
   einer Adresse, einer Nummer, einem Datum. Entschieden wird an der Länge und
   daran, ob mehrere Wörter aufeinanderfolgen — nicht am Inhalt. */
function istFliesstext(zeile) {
  const text = String(zeile || '').trim();
  if (text.length < 60) return false;
  if (/@|^\+?[\d\s()/-]{7,}$/.test(text)) return false;
  return text.split(/\s+/).length >= 9;
}

/* Gehört die Zeile in den Kontaktblock?
 *
 * Gefragt wird nach dem, was dort steht — Anschrift, Telefon, Mail,
 * Geburtsdatum, Adresse im Netz —, nicht nach der Länge. Vorher entschied
 * das die Frage „ist das Fließtext?“, und die hängt an neun Wörtern: Eine
 * umbrochene Zeile mitten aus dem Kurzprofil hat oft acht und stand deshalb
 * als Kontaktangabe unter dem Geburtsdatum. */
const KONTAKTMUSTER = [
  /@[\w.-]+\.\w{2,}/,                          /* Mail */
  /^\+?[\d\s()/.-]{7,}$/,                      /* Telefon */
  /^\d{1,2}[./]\d{1,2}[./]\d{2,4}$/,           /* Geburtsdatum */
  /https?:\/\/|www\.|linkedin|xing|github/i,   /* Netz */
  /\b\d{5}\b/,                                 /* Postleitzahl */
];

function istKontaktZeile(zeile) {
  const t = String(zeile || '').trim();
  if (!t) return false;
  if (KONTAKTMUSTER.some(m => m.test(t))) return true;
  /* Und was kurz ist und nicht wie ein Satz endet: „Nürnberg“, „ledig“. */
  return t.split(/\s+/).length <= 3 && !/[.!?]$/.test(t);
}

function ohneDoppel(zeilen) {
  const gesehen = new Set();
  return zeilen.filter(z => {
    const schluessel = worte(z).join(' ');
    if (!schluessel || gesehen.has(schluessel)) return false;
    gesehen.add(schluessel);
    return true;
  });
}

function uebrigerVorspann(zeilen, kopf) {
  const bekannt = new Set(worte(kopf.name + ' ' + kopf.rolle));
  return zeilen.filter(z => {
    const w = worte(z);
    if (!w.length) return false;
    return w.filter(x => bekannt.has(x)).length / w.length < 0.6;
  });
}

/* Ein Abschnitt, seine Zeilen, und danach die Frage, ob wirklich jede davon
   angekommen ist. Der Abschnitt ist klein genug, dass sich das beantworten
   lässt — beim ganzen Dokument war es Raten. */
async function abschnittLesen(bereich, umgebung) {
  /* Fließtext wird nicht gefragt, sondern genommen.

     Ein Kurzprofil ist der Text, den jemand über sich geschrieben hat. Daran
     gibt es nichts zu ordnen — es gibt nur die Möglichkeit, dass ein Modell
     ihn „strafft“, und genau das ist passiert: Aus vierzehn Zeilen wurden
     sechs, und niemand hatte darum gebeten. Hier werden die Zeilen des
     Abschnitts deshalb einfach zusammengesetzt. Wort für Wort, ohne Umweg. */
  if (bereich.art === 'profil' || bereich.art === 'text') {
    return { titel: bereich.titel, art: bereich.art, nachgetragen: 0,
             eintraege: fliesstextAus(bereich) };
  }

  /* Eine Aufzählung genauso: Sie hat keine Struktur, die zu erkennen wäre.
     „Generative AI“, „LLM“, „Prompt Engineering“ — das sind die Einträge, und
     zwar genau so viele, wie Zeilen dastehen. Ein Modell hat aus neun
     Kompetenzen einen Eintrag gemacht und aus einem anderen Lebenslauf drei
     stillschweigend gestrichen. Beides kann hier nicht mehr passieren. */
  if (bereich.art === 'liste') {
    return { titel: bereich.titel, art: bereich.art, nachgetragen: 0,
             eintraege: listeAus(bereich) };
  }

  let eintraege = [];
  try {
    const antwort = await fragen(umgebung, ABSCHNITT,
      'ART\n---\n' + bereich.art +
      '\n\nÜBERSCHRIFT\n---\n' + (bereich.titel || '(ohne Überschrift)') +
      '\n\nZEILEN\n---\n' + bereich.zeilen.join('\n'), 0);
    eintraege = Array.isArray(antwort.eintraege) ? antwort.eintraege : [];
  } catch (e) {
    console.log('Abschnitt „' + bereich.titel + '“:', e && e.message);
  }
  eintraege = eintraegeSaeubern(bereich.art, eintraege);

  /* Die Überschrift selbst steht in keinem Eintrag — sie fehlt also nicht. */
  const pruefen = bereich.zeilen.filter(z => !gleicheWorte(z, bereich.titel));
  const fehlt = fehlendeZeilen(pruefen.join('\n'), eintraege);
  nachtragVerteilen(bereich.art, eintraege, pruefen, fehlt.slice(0, 40));
  if (bereich.art === 'ausbildung') eintraege.forEach(notenRuecken);
  return { titel: bereich.titel, art: bereich.art, eintraege, nachgetragen: fehlt.length };
}

/* Die Zeilen eines Fließtext-Abschnitts, ohne seine Überschrift und ohne
   Seitenzahlen — zusammengesetzt zu Absätzen. Ein Kurzprofil ist einer; bei
   einem sonstigen Textabschnitt beginnt nach einem Satzende ein neuer, weil
   dort wirklich mehrere stehen können. */
function fliesstextAus(bereich) {
  const zeilen = bereich.zeilen
    .map(z => z.trim())
    .filter(z => z && !NEBENSACHE.test(z) && !gleicheWorte(z, bereich.titel));
  if (!zeilen.length) return [];
  if (bereich.art === 'profil') return [zeilen.join(' ').replace(/\s+/g, ' ').trim()];

  const absaetze = [];
  zeilen.forEach(z => {
    const vor = absaetze[absaetze.length - 1];
    if (vor && !/[.!?]["'\u201c\u201d)]?$/.test(vor)) absaetze[absaetze.length - 1] = vor + ' ' + z;
    else absaetze.push(z);
  });
  return absaetze;
}

/* Die Einträge einer Aufzählung, Zeile für Zeile.
 *
 * Zwei Dinge muss sie können, die eine reine Zeilenliste nicht kann. Erstens:
 * Ein Punkt, der über zwei Zeilen lief („Deutsch & Englisch“ /
 * „(verhandlungssicher)“), ist einer. Erkennbar ist das daran, dass vor der
 * zweiten Zeile kein Aufzählungszeichen steht, wo die meisten anderen eines
 * haben. Zweitens: Ohne Aufzählungszeichen schreiben viele ihre Kenntnisse in
 * eine Reihe — „Python, SQL, Docker“. Getrennt wird dabei nur, wenn lauter
 * kurze Stücke herauskommen; ein Satz mit Kommas bleibt ein Satz.
 */
const MARKE = /^[\u2022\u00b7\u25cf\u25e6\u25aa\u2043*\u2013\u2014-]\s*/;

function listeAus(bereich) {
  const zeilen = bereich.zeilen
    .map(z => z.trim())
    .filter(z => z && !NEBENSACHE.test(z) && !gleicheWorte(z, bereich.titel));
  const mitMarke = zeilen.filter(z => MARKE.test(z)).length;

  const punkte = [];
  zeilen.forEach(z => {
    const marke = MARKE.test(z);
    const text = z.replace(MARKE, '').trim();
    if (!text) return;
    if (!marke && punkte.length && mitMarke >= zeilen.length / 2) {
      punkte[punkte.length - 1] += ' ' + text;
      return;
    }
    punkte.push(text);
  });
  if (mitMarke) return punkte.slice(0, 60);

  const aus = [];
  punkte.forEach(p => {
    const teile = p.split(/\s*[,;|]\s*/).map(t => t.trim()).filter(Boolean);
    const kurz = teile.every(t => t.length <= 40 && t.split(/\s+/).length <= 5);
    if (teile.length >= 2 && p.length <= 140 && kurz) aus.push(...teile);
    else aus.push(p);
  });
  return aus.slice(0, 60);
}

const PUNKTFELDER = ['punkte', 'aufgaben', 'taetigkeiten', 'tätigkeiten',
                     'beschreibung', 'details', 'bullets', 'points', 'items'];

const EINTRAG_FELDER = {
  kontakt: ['art', 'wert'],
  beruf: ['titel', 'firma', 'ort', 'von', 'bis', 'punkte'],
  ausbildung: ['abschluss', 'fach', 'einrichtung', 'von', 'bis', 'punkte'],
  weiterbildung: ['titel', 'anbieter', 'jahr'],
  sprachen: ['sprache', 'niveau'],
};

const KONTAKTARTEN = ['ort', 'tel', 'mail', 'datum', 'web', 'sonst'];

/* Was vom Modell kommt, wird nicht durchgereicht: Nur die Felder, die es zu
   dieser Art gibt, und nur als Text. Der Editor setzt das später in HTML — was
   hier durchrutscht, steht dort auf dem Blatt. */
function eintraegeSaeubern(art, eintraege) {
  const liste = eintraege.slice(0, 60);
  if (art === 'liste' || art === 'profil' || art === 'text') {
    return liste
      .map(e => sauberText(typeof e === 'string' ? e : (e && (e.wert || e.text || e.titel)), 3000))
      .filter(Boolean);
  }
  const felder = EINTRAG_FELDER[art] || EINTRAG_FELDER.weiterbildung;
  return liste.map(e => {
    if (!e || typeof e !== 'object') {
      const text = sauberText(e, 300);
      return text ? ersatzEintrag(art, text) : null;
    }
    const aus = {};
    felder.forEach(f => {
      if (f === 'punkte') {
        /* „punkte“ heißt bei einem Modell auch mal „aufgaben“ oder
           „beschreibung“. Die Liste dann zu verwerfen hieße: Station ohne
           Inhalt, und niemand sieht, dass etwas fehlte. */
        const roh = PUNKTFELDER.map(f2 => e[f2]).find(x => Array.isArray(x) && x.length)
          || (typeof e.beschreibung === 'string' && e.beschreibung ? [e.beschreibung] : []);
        aus.punkte = roh
          .map(p => sauberText(typeof p === 'string' ? p : (p && (p.text || p.punkt)), 1200))
          .filter(Boolean).slice(0, 40);
      } else {
        aus[f] = sauberText(e[f], 200);
      }
    });
    if (art === 'kontakt' && KONTAKTARTEN.indexOf(aus.art) < 0) aus.art = 'sonst';
    const inhalt = felder.some(f => f !== 'punkte' && aus[f]) || (aus.punkte || []).length;
    return inhalt ? aus : null;
  }).filter(Boolean);
}

/* „Abschluss“ heißt im Lebenslauf zweierlei: der Grad und die Note. Steht
   eine Zahl in dem Feld, war der Grad gemeint und die Note gefunden — dann
   lieber kein Grad als ein falscher.
   Wohin mit der Zahl: Die Zeile, aus der sie stammt, steht zu diesem
   Zeitpunkt meist schon als Punkt dabei, denn die Vollständigkeitsprüfung
   hat sie nachgetragen — „Abschluss: 1,5“, also mit dem Wort davor und
   damit besser als die nackte Zahl. Nur wenn sie fehlt, kommt die Zahl
   dazu. Sonst stand die Note zweimal untereinander. */
function notenRuecken(eintrag) {
  if (!eintrag || !istNote(eintrag.abschluss)) return;
  const note = eintrag.abschluss;
  const zahl = (note.match(/\d[\d.,]*/) || [''])[0];
  eintrag.abschluss = '';
  eintrag.punkte = eintrag.punkte || [];
  if (!zahl || !eintrag.punkte.some(p => String(p).includes(zahl))) eintrag.punkte.unshift(note);
}

/* Eine Note ist eine Zahl, mit oder ohne das Wort davor. Ein Jahr nicht:
   „2018“ bleibt stehen, wo es steht. */
function istNote(wert) {
  const t = String(wert || '').trim();
  if (!t || /^(19|20)\d{2}$/.test(t)) return false;
  return /^(abschluss|note|notendurchschnitt|durchschnitt|grade|gpa)?\s*[:\-\u2013]?\s*\d[\d.,]*\s*(\/\s*\d[\d.,]*)?$/i.test(t);
}

function ersatzEintrag(art, text) {
  if (art === 'kontakt') return { art: 'sonst', wert: text };
  if (art === 'sprachen') {
    const teile = text.split(/\s*[:–-]\s*/);
    return { sprache: teile[0] || text, niveau: teile[1] || '' };
  }
  if (art === 'beruf') return { titel: text, firma: '', ort: '', von: '', bis: '', punkte: [] };
  if (art === 'ausbildung') return { abschluss: text, fach: '', einrichtung: '', von: '', bis: '', punkte: [] };
  return { titel: text, anbieter: '', jahr: '' };
}

/* Übersehene Zeilen kommen an den Eintrag, unter dem sie im Dokument
   standen — nicht alle an den letzten. Dafür werden die Zeilen des
   Abschnitts noch einmal durchgegangen: Wo eine Zeile den Titel oder den
   Arbeitgeber eines Eintrags nennt, beginnt dieser Eintrag; was danach fehlt,
   gehört zu ihm. */
function nachtragVerteilen(art, eintraege, zeilen, fehlt) {
  if (!fehlt.length) return;
  if ((art !== 'beruf' && art !== 'ausbildung') || !eintraege.length) {
    fehlt.forEach(z => eintragNachtragen(art, eintraege, z));
    return;
  }
  const fehlend = new Set(fehlt);
  let aktuell = eintraege[0];
  zeilen.forEach(zeile => {
    const treffer = eintraege.find(e => nenntEintrag(e, zeile));
    if (treffer) { aktuell = treffer; return; }
    if (!fehlend.has(zeile)) return;
    if (!Array.isArray(aktuell.punkte)) aktuell.punkte = [];
    punktEinfuegen(aktuell.punkte, zeile);
  });
}

/* Eine nachgetragene Zeile ersetzt, was schon in ihr steckt.
 *
 * Das Modell hatte „1,5“ als Punkt notiert — die Note ohne das Wort davor.
 * Die Vollständigkeitsprüfung sieht die Zeile „Abschluss: 1,5“ und hält sie
 * für verloren, weil das Wort fehlt. Beides nebeneinander, und die Note steht
 * zweimal auf dem Blatt. Die längere Fassung ist die vollständigere: Sie
 * tritt an die Stelle der kürzeren, statt sich danebenzustellen. */
function punktEinfuegen(punkte, zeile) {
  const neu = stuecke(zeile);
  if (!neu.length) return;
  const stelle = punkte.findIndex(p => {
    const alt = stuecke(p);
    return alt.length && alt.length < neu.length && folgeDrin(alt, neu);
  });
  if (stelle >= 0) { punkte[stelle] = zeile; return; }
  /* Steht die Zeile schon irgendwo, kommt sie nicht noch einmal dazu. Ein
     einzelnes Wort beweist das aber nicht: „Nürnberg“ steht bei jeder Station
     und wäre sonst nirgends mehr aufgetaucht. */
  if (neu.length >= 2 && punkte.some(p => folgeDrin(neu, stuecke(p)))) return;
  punkte.push(zeile);
}

/* Wie „worte“, aber ohne Mindestlänge: Zahlen und Kürzel zählen mit. Für den
   Vergleich zweier Stichpunkte sind gerade sie das Unterscheidende — „1,5“
   ist die ganze Aussage. */
function stuecke(text) {
  return String(text || '').toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, ' ').split(' ').filter(Boolean);
}

/* Steht die Wortfolge a zusammenhängend in b? */
function folgeDrin(a, b) {
  if (!a.length || a.length > b.length) return false;
  for (let i = 0; i + a.length <= b.length; i++)
    if (a.every((w, k) => w === b[i + k])) return true;
  return false;
}

/* Nennt diese Zeile den Eintrag — seinen Titel, seinen Arbeitgeber, seine
   Einrichtung? Dann fängt hier sein Abschnitt an. */
function nenntEintrag(eintrag, zeile) {
  const w = worte(zeile);
  if (!w.length) return false;
  const kennung = worte([eintrag.titel, eintrag.abschluss, eintrag.fach,
                         eintrag.firma, eintrag.einrichtung].filter(Boolean).join(' '));
  if (!kennung.length) return false;
  return w.filter(x => kennung.indexOf(x) >= 0).length / w.length >= 0.6;
}

/* Eine Zeile, die sich nirgends einordnen ließ, kommt dorthin, wo sie am
   wenigsten Schaden anrichtet: an den Eintrag darüber. Sichtbar an der
   falschen Stelle ist besser als unsichtbar an gar keiner. */
function eintragNachtragen(art, eintraege, zeile) {
  if (art === 'liste' || art === 'profil' || art === 'text') { eintraege.push(zeile); return; }
  const letzter = eintraege[eintraege.length - 1];
  if ((art === 'beruf' || art === 'ausbildung') && letzter) {
    if (!Array.isArray(letzter.punkte)) letzter.punkte = [];
    punktEinfuegen(letzter.punkte, zeile);
    return;
  }
  eintraege.push(ersatzEintrag(art, zeile));
}

/* ---------------------------------------------------------- Vollständigkeit

   Ein Modell, das abschreibt, lässt gelegentlich etwas aus — und sagt es
   nicht. Deshalb wird nicht geglaubt, sondern nachgezählt: Welche Zeile
   findet sich im Ergebnis nicht wieder? */

/* Seitenzahlen und Deckblattwörter. Die Ziffernfolge ist auf drei Stellen
   begrenzt: „017623771264“ ist keine Seitenzahl, sondern eine Telefonnummer,
   und sie fiel hier still aus dem Kontaktabschnitt heraus. */
const NEBENSACHE = /^(lebenslauf|curriculum vitae|cv|resume|résumé|seite \d+|\d{1,3}\s*\/\s*\d{1,3}|\d{1,3})$/i;

function worte(text) {
  return String(text || '').toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, ' ')
    .split(' ')
    .filter(w => w.length >= 4);
}

function gleicheWorte(a, b) {
  const x = worte(a), y = worte(b);
  return x.length > 0 && x.join(' ') === y.join(' ');
}

function alleTexte(objekt) {
  const aus = [];
  const gehen = x => {
    if (typeof x === 'string') aus.push(x);
    else if (Array.isArray(x)) x.forEach(gehen);
    else if (x && typeof x === 'object') Object.values(x).forEach(gehen);
  };
  gehen(objekt);
  return aus.join(' \n ');
}

/* Eine Zeile gilt als übernommen, wenn ihre tragenden Wörter im Ergebnis
   vorkommen. Wortweise, weil ein zweispaltiges PDF Zeilen zerlegt und wieder
   zusammensetzt — ein Vergleich auf Gleichheit fände fast nichts wieder. */
/* Steht diese Zeile im Ergebnis?
 *
 * Die Frage nach einzelnen Wörtern beantwortet sich in einem Lebenslauf zu
 * leicht mit ja: Das Kurzprofil nennt dieselben Begriffe wie die Stationen
 * darunter. Ein ganzer Abschnitt konnte so verschwinden und trotzdem als
 * „angekommen“ gelten, weil seine Wörter anderswo vorkamen.
 *
 * Gefragt wird deshalb nach einer Wortfolge: Drei Wörter hintereinander,
 * irgendwo im Ergebnis. Das steht kaum je zufällig da. Und weil eine zu
 * streng beantwortete Frage die Zeile ein zweites Mal aufs Blatt brächte,
 * gilt sie auch dann als vorhanden, wenn fast alle ihre Wörter da sind.
 */
/* Alles zusammengeschrieben, ohne Punkte und Leerzeichen: „B. Eng. :“ wird
   zu „beng“. Das ist grob, aber es ist der einzige Weg, eine Zeile
   wiederzufinden, die aus lauter kurzen Stücken besteht. */
function knapp(text) {
  return String(text || '').toLowerCase().replace(/[^\p{L}\p{N}]+/gu, '');
}

function istDrin(zeile, folge, einzeln, engFolge) {
  const w = worte(zeile);
  /* „M.A. :“, „B. Eng. :“, „B. A. :“ — kein einziges Wort mit vier Buchstaben,
     und damit für den Vergleich unsichtbar. Genau das sind die Abschlüsse:
     Sie verschwanden spurlos, und niemandem fiel etwas auf, weil die
     Vollständigkeitsprüfung sie nie vermisst hat. */
  if (!w.length) {
    const k = knapp(zeile);
    return !k || String(engFolge || '').includes(k);
  }
  const gedeckt = w.filter(x => einzeln.has(x)).length / w.length;
  /* Bei einer langen Zeile reicht eine gefundene Wortfolge nicht: „…von
     KI-Projekten“ steht auch dann da, wenn der Rest des Satzes fehlt. Ein
     gekürzter Stichpunkt ist ein verlorener Stichpunkt. */
  if (w.length >= 6) return gedeckt >= 0.8;
  const n = Math.min(3, w.length);
  for (let i = 0; i + n <= w.length; i++) {
    if (folge.includes(' ' + w.slice(i, i + n).join(' ') + ' ')) return true;
  }
  return gedeckt >= 0.9;
}

export function fehlendeZeilen(text, ergebnis, ohneUeberschriften) {
  const texte = alleTexte(ergebnis);
  const alle = worte(texte);
  const folge = ' ' + alle.join(' ') + ' ';
  const einzeln = new Set(alle);
  const engFolge = knapp(texte);
  const fehlt = [];
  String(text).split(/\r?\n/).forEach(zeile => {
    const roh = zeile.trim();
    if (roh.length < 4 || NEBENSACHE.test(roh)) return;
    /* Beim Weg am Stück sind die Überschriften des Dokuments nicht bekannt.
       Eine kurze Zeile ohne Ziffern ist dort fast immer eine — und eine
       Überschrift steht in keinem Eintrag, ohne dass etwas fehlt. */
    if (ohneUeberschriften && roh.length <= 34 && !/\d/.test(roh)
        && roh.split(/\s+/).length <= 3) return;
    if (!istDrin(roh, folge, einzeln, engFolge)) fehlt.push(roh);
  });
  return fehlt;
}

/* ------------------------------------------------------------- am Stück

   Der Rückfallweg: ein Aufruf, festes Formular. Er springt ein, wenn die
   Gliederung nichts hergibt, und er ist der einzige Weg für eine Datei, die
   nur das Modell selbst lesen kann. Das Ergebnis wird in dieselbe Form
   gebracht, damit der Editor nur eine kennt. */

async function amStueck(text, umgebung) {
  const ergebnis = await fragen(umgebung, PARSE,
    'Hier ist der Text eines Lebenslaufs. Gib das JSON zurück.\n\n---\n' + text, 0.1);
  if (ergebnis && ergebnis.fehler) throw fehler('Das sieht nicht nach einem Lebenslauf aus.', 422);
  const lebenslauf = flachZuAbschnitten(ergebnis);
  const fehlt = fehlendeZeilen(text, lebenslauf, true);
  if (fehlt.length) {
    const rest = { titel: RESTTITEL[lebenslauf.sprache] || RESTTITEL.de, art: 'liste',
                   eintraege: fehlt.slice(0, 40) };
    lebenslauf.abschnitte.push(rest);
  }
  return { lebenslauf, nachgetragen: 0, offen: fehlt.length,
           deckung: deckungVon(text, lebenslauf) };
}

const RESTTITEL = { de: 'Weitere Angaben', en: 'Further details', es: 'Otros datos' };

/* Wie viel von der Datei ist auf dem Blatt wiederzufinden? Die Zahl geht mit
   nach vorn: Wer seinen eigenen Lebenslauf hochlädt, soll nicht erst beim
   dritten Lesen merken, dass ein Drittel fehlt. */
function deckungVon(text, lebenslauf) {
  const zeilen = String(text).split(/\r?\n/)
    .map(z => z.trim())
    .filter(z => z.length >= 8 && !NEBENSACHE.test(z) && worte(z).length);
  const fehlend = fehlendeZeilen(text, lebenslauf).length;
  return { zeilen: zeilen.length, fehlend };
}

const FLACHNAMEN = {
  de: { kontakt: 'Kontakt', beruf: 'Berufserfahrung', ausbildung: 'Ausbildung',
        liste: 'Kenntnisse', sprachen: 'Sprachen', weiterbildung: 'Weiterbildung' },
  en: { kontakt: 'Contact', beruf: 'Work experience', ausbildung: 'Education',
        liste: 'Skills', sprachen: 'Languages', weiterbildung: 'Further training' },
  es: { kontakt: 'Contacto', beruf: 'Experiencia', ausbildung: 'Formación',
        liste: 'Competencias', sprachen: 'Idiomas', weiterbildung: 'Formación continua' },
};

export function flachZuAbschnitten(flach) {
  const f = flach || {};
  const sprache = ['de', 'en', 'es'].indexOf(f.sprache) >= 0 ? f.sprache : 'de';
  const namen = FLACHNAMEN[sprache];
  const abschnitte = [];
  const nimm = (art, eintraege, titel) => {
    const sauber = eintraegeSaeubern(art, Array.isArray(eintraege) ? eintraege : []);
    if (sauber.length) abschnitte.push({ titel: titel || namen[art] || '', art, eintraege: sauber });
  };
  nimm('kontakt', f.kontakt);
  nimm('beruf', f.berufserfahrung);
  nimm('ausbildung', f.ausbildung);
  nimm('liste', f.kenntnisse);
  nimm('sprachen', f.sprachen);
  nimm('weiterbildung', f.weiterbildung);
  (Array.isArray(f.weitere) ? f.weitere : []).forEach(w => {
    if (w) nimm('liste', w.punkte, sauberText(w.titel, 80));
  });
  return {
    sprache,
    kopf: {
      name: sauberText(f.kopf && f.kopf.name, 120),
      rolle: sauberText(f.kopf && f.kopf.rolle, 120),
      profil: sauberText(f.kopf && f.kopf.profil, 600),
    },
    abschnitte,
  };
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
  /* Auch dieser Weg gibt Abschnitte zurück: Der Editor soll nur eine Form
     kennen, egal wie gelesen wurde. */
  return { lebenslauf: flachZuAbschnitten(jsonAus(inhalt)), nachgetragen: 0, offen: 0 };
}

/* ------------------------------------------------------------ zuschneiden */

/* Was einen Satz zu einer Behauptung macht: Zahlen, Jahreszahlen, Kürzel.
   Genau dort verrutscht einem Modell am ehesten etwas. */
function harteAngaben(text) {
  return (String(text).match(/\d+(?:[.,]\d+)*|\b[A-ZÄÖÜ]{2,}[A-ZÄÖÜ0-9/+-]*\b/g) || [])
    .map(t => t.replace(/[.,]$/, ''));
}

/* Die eigene Kontrolle, vor dem Modell und unabhängig von ihm. Sie kostet
   nichts und fängt den teuersten Fehler: eine Angabe, die vorher nicht
   dastand. */
function vorschlagPruefen(vorher, nachher) {
  const neu = String(nachher || '').trim();
  if (!neu) return { weg: 'leer' };
  if (neu === vorher) return { weg: 'unverändert' };
  if (neu.length > vorher.length * 1.4 + 25) return { weg: 'deutlich länger als das Original' };

  const altAngaben = new Set(harteAngaben(vorher));
  const neuAngaben = harteAngaben(neu);
  const dazu = [...new Set(neuAngaben.filter(x => !altAngaben.has(x)))];
  if (dazu.length) return { weg: 'neue Angabe: ' + dazu.join(', ') };

  const jetzt = new Set(neuAngaben);
  const fehlt = [...altAngaben].filter(x => !jetzt.has(x));
  return fehlt.length ? { bedenken: 'Im Original steht ' + fehlt.join(', ') + ', hier nicht mehr.' } : {};
}

async function zuschneiden(daten, umgebung) {
  const lebenslauf = daten.lebenslauf;
  const stelle = String(daten.stelle || '').trim().slice(0, GRENZEN.stelle);
  if (!lebenslauf || typeof lebenslauf !== 'object') throw fehler('Kein Lebenslauf übergeben.', 400);
  if (stelle.length < 80) throw fehler('Die Stellenbeschreibung ist zu kurz.', 400);

  const stellen = textStellen(lebenslauf);
  if (!stellen.length) throw fehler('In diesem Lebenslauf ist nichts zum Umformulieren.', 400);
  const nachId = new Map(stellen.map(s => [s.id, s]));

  const ergebnis = await fragen(umgebung, TAILOR,
    'STELLENANZEIGE\n---\n' + stelle +
    '\n\nLEBENSLAUF (JSON, nur zur Kenntnis)\n---\n' + JSON.stringify(lebenslauf) +
    '\n\nPLACES (nur diese darfst du ändern)\n---\n' + JSON.stringify(stellen), 0.3);

  /* Erst die eigene Prüfung, dann das Modell noch einmal über das, was
     übrig bleibt. Was hier durchfällt, sieht der Benutzer gar nicht erst. */
  const vorschlaege = [];
  const verworfen = [];
  (Array.isArray(ergebnis.vorschlaege) ? ergebnis.vorschlaege : []).slice(0, 40).forEach(v => {
    const stelle2 = v && nachId.get(v.id);
    if (!stelle2) return;
    if (vorschlaege.some(x => x.id === v.id)) return;
    const urteil = vorschlagPruefen(stelle2.text, v.nachher);
    if (urteil.weg){ verworfen.push({ wo: stelle2.wo, grund: urteil.weg }); return; }
    vorschlaege.push({ id: v.id, wo: stelle2.wo, vorher: stelle2.text,
                       nachher: String(v.nachher).trim(),
                       warum: String(v.warum || '').trim().slice(0, 200),
                       bedenken: urteil.bedenken || '' });
  });

  if (vorschlaege.length) {
    try {
      const pruefung = await fragen(umgebung, PRUEFER,
        JSON.stringify(vorschlaege.map(v => ({ id: v.id, vorher: v.vorher, nachher: v.nachher }))), 0);
      (Array.isArray(pruefung.beanstandet) ? pruefung.beanstandet : []).forEach(b => {
        const treffer = vorschlaege.find(v => v.id === (b && b.id));
        if (treffer && b.grund) treffer.bedenken = String(b.grund).slice(0, 200);
      });
    } catch (e) {
      console.log('Prüfung fehlgeschlagen:', e && e.message);
    }
  }

  /* Umstellen ist der einzige Vorschlag ohne neuen Wortlaut — und nur
     gültig, wenn wirklich dieselben Einträge herauskommen. */
  let reihenfolge = null;
  if (Array.isArray(ergebnis.reihenfolge) && Array.isArray(lebenslauf.kenntnisse)) {
    const probe = { kenntnisse: lebenslauf.kenntnisse.slice() };
    if (textSetzen(probe, REIHENFOLGE, ergebnis.reihenfolge)
        && probe.kenntnisse.join('|') !== lebenslauf.kenntnisse.join('|')) {
      reihenfolge = probe.kenntnisse;
    }
  }

  return {
    vorschlaege,
    reihenfolge,
    verworfen: verworfen.slice(0, 10),
    passung: ergebnis.passung || null,
    luecken: Array.isArray(ergebnis.luecken) ? ergebnis.luecken : [],
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
