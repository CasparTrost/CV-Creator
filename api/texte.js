/*
 * Die Stellen eines Lebenslaufs, an denen der Zuschnitt arbeiten darf.
 *
 * Der Zuschnitt schreibt den Lebenslauf nicht neu. Er schlägt einzelne
 * Umformulierungen vor, und jede hat eine Adresse: "beruf.0.punkt.2" ist der
 * dritte Punkt der ersten Station, nichts anderes. Das hat drei Gründe.
 *
 *   1. Was keine Adresse hat, kann nicht geändert werden. Firmennamen, Titel,
 *      Abschlüsse, Einrichtungen und Datumsangaben stehen deshalb gar nicht
 *      erst in dieser Liste. Ein Modell, das sie ändern wollte, hätte keinen
 *      Ort, an den es das schreiben könnte.
 *   2. Jeder Vorschlag lässt sich einzeln prüfen — gegen genau den Satz, der
 *      vorher dort stand, statt gegen ein ganzes Dokument.
 *   3. Der Benutzer sieht Vorher und Nachher nebeneinander und hakt ab, was er
 *      will. Ein neu geschriebener Lebenslauf ließe sich nur ganz annehmen
 *      oder ganz verwerfen.
 *
 * Der Editor kennt dieses Schema nicht und braucht es nicht: Zu jedem
 * Vorschlag steht der bisherige Wortlaut dabei, und danach sucht er auf dem
 * Blatt. So gibt es das Schema nur an einer Stelle — hier.
 */

/* Die Reihenfolge der Kenntnisse ist der einzige Vorschlag, der keinen
   Wortlaut ändert: Er stellt um, was die Anzeige zuerst sehen will. */
export const REIHENFOLGE = 'kenntnisse.reihenfolge';

export function textStellen(lebenslauf) {
  const l = lebenslauf || {};
  const aus = [];
  const nimm = (id, wo, wert) => {
    const text = wert === undefined || wert === null ? '' : String(wert).trim();
    if (text) aus.push({ id, wo, text });
  };

  nimm('kopf.rolle', 'Berufsbezeichnung', l.kopf && l.kopf.rolle);
  nimm('kopf.profil', 'Kurzprofil', l.kopf && l.kopf.profil);

  (l.berufserfahrung || []).forEach((j, i) => {
    const wo = (j.titel || 'Station ' + (i + 1)) + (j.firma ? ', ' + j.firma : '');
    (j.punkte || []).forEach((p, k) => nimm('beruf.' + i + '.punkt.' + k, wo, p));
  });

  (l.ausbildung || []).forEach((a, i) => {
    const wo = a.abschluss || a.fach || 'Ausbildung ' + (i + 1);
    (a.punkte || []).forEach((p, k) => nimm('ausbildung.' + i + '.punkt.' + k, wo, p));
  });

  (l.kenntnisse || []).forEach((k, i) => nimm('kenntnis.' + i, 'Kenntnisse', k));

  (l.weitere || []).forEach((w, i) => {
    const wo = w.titel || 'Weitere Angaben';
    (w.punkte || []).forEach((p, k) => nimm('weitere.' + i + '.punkt.' + k, wo, p));
  });

  return aus;
}

/* Schreibt einen neuen Wortlaut an genau diese Stelle. Gibt zurück, ob die
   Adresse existiert — eine erfundene Adresse ändert nichts. */
export function textSetzen(lebenslauf, id, wert) {
  const l = lebenslauf;
  if (!l || typeof l !== 'object' || typeof id !== 'string') return false;

  if (id === REIHENFOLGE) return kenntnisseStellen(l, wert);

  const text = String(wert === undefined || wert === null ? '' : wert).trim();
  if (!text) return false;

  if (id === 'kopf.rolle' || id === 'kopf.profil') {
    if (!l.kopf || typeof l.kopf !== 'object') return false;
    const feld = id.slice(5);
    if (!l.kopf[feld]) return false;
    l.kopf[feld] = text;
    return true;
  }

  let m = id.match(/^kenntnis\.(\d+)$/);
  if (m) {
    const liste = l.kenntnisse;
    if (!Array.isArray(liste) || !liste[+m[1]]) return false;
    liste[+m[1]] = text;
    return true;
  }

  m = id.match(/^(beruf|ausbildung|weitere)\.(\d+)\.punkt\.(\d+)$/);
  if (m) {
    const liste = m[1] === 'beruf' ? l.berufserfahrung
                : m[1] === 'ausbildung' ? l.ausbildung : l.weitere;
    const eintrag = Array.isArray(liste) ? liste[+m[2]] : null;
    if (!eintrag || !Array.isArray(eintrag.punkte) || !eintrag.punkte[+m[3]]) return false;
    eintrag.punkte[+m[3]] = text;
    return true;
  }
  return false;
}

/* Umstellen heißt umstellen: Dieselben Einträge, andere Reihenfolge. Fehlt
   einer oder kommt einer dazu, wird nichts übernommen. */
function kenntnisseStellen(lebenslauf, neu) {
  const alt = lebenslauf.kenntnisse;
  if (!Array.isArray(alt) || !Array.isArray(neu) || alt.length !== neu.length) return false;
  const zaehlen = liste => {
    const m = new Map();
    liste.forEach(x => {
      const k = String(x).trim().toLowerCase();
      m.set(k, (m.get(k) || 0) + 1);
    });
    return m;
  };
  const a = zaehlen(alt), b = zaehlen(neu);
  if (a.size !== b.size) return false;
  for (const [k, n] of a) if (b.get(k) !== n) return false;
  lebenslauf.kenntnisse = neu.map(x => String(x).trim());
  return true;
}
