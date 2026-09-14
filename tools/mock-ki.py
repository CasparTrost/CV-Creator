#!/usr/bin/env python3
"""
Ein Ersatz für den KI-Worker, damit sich die Oberfläche ohne Schlüssel und
ohne Kosten ausprobieren lässt.

    python3 tools/mock-ki.py 8768

Meistens braucht es das gar nicht: tools/serve.py beantwortet dieselben Wege
schon selbst, und der Editor findet sie auf localhost von allein. Dieser
Server hier ist für den Fall, dass die Seite woanders liegt.

Er denkt sich nichts aus: Er gibt zurück, was er bekommen hat, in der Form,
die der Editor erwartet. Damit lässt sich prüfen, ob Dateien richtig gelesen,
Dialoge richtig geführt und Ergebnisse richtig eingesetzt werden — nur eben
ohne Modell dahinter.
"""
import json
import re
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer


# Die Reihenfolge ist die Prüfreihenfolge, und sie ist der ganze Trick:
# „Sprachkenntnisse“ enthält „kenntnis“ und ist trotzdem keine Rubrik
# „Kenntnisse“. Das Genauere steht deshalb vor dem Allgemeineren.
RUBRIKEN = [
    ('profil', r'profil|[üu]ber mich|kurzprofil|zusammenfassung|summary|about me|perfil'),
    ('sprachen', r'sprach|languages|idiomas'),
    ('weiterbildung', r'weiterbildung|fortbildung|zertifikat|training|certificat'),
    ('ausbildung', r'ausbildung|bildungsweg|studium|schul|qualifikation|education|academic|formaci'),
    ('berufserfahrung', r'berufserfahrung|berufliche|werdegang|praxis|experience|employment|experiencia'),
    ('kenntnisse', r'kenntnis|kompetenz|f[äa]higkeit|skills|edv|it-|competenc|tools'),
    ('kontakt', r'pers[öo]nliche daten|kontakt|personal (data|details|information)|contact|datos'),
    ('weitere', r'ehrenamt|engagement|interess|hobby|publikation|referenz|auszeichnung|volunteer|award'),
]


def ist_fliesstext(zeile):
    """Ein Satz ist keine Aufzählung. „Erfahrener Professional mit über 16
    Jahren Berufserfahrung, davon vier Jahre …“ an den Kommas zu zerlegen
    ergibt fünf unsinnige Kenntnisse."""
    if len(zeile) < 60 or ZEITRAUM.search(zeile):
        return False
    return zeile.endswith('.') or '. ' in zeile or len(zeile.split()) > 12
ZEITRAUM = re.compile(
    r'(\d{1,2}[./]\d{4}|\d{4})\s*(?:–|-|bis|to|—)\s*(\d{1,2}[./]\d{4}|\d{4}|heute|jetzt|present|now)',
    re.I)
FIRMA = re.compile(r'\b(GmbH|AG|KG|mbH|e\.?\s?V\.?|SE|Ltd|Inc|Klinikum|Institut|Praxis|'
                   r'Kanzlei|Stiftung|Akademie)\b|\w*(schule|universit[äa]t|hochschule|college|'
                   r'university)\b', re.I)


def rubrik_von(zeile):
    """Ist diese Zeile eine Überschrift?

    „Hochschule Beispielstadt“ enthält „schul“ und ist trotzdem keine
    Rubrik — deshalb zählt nur, was kurz ist, aus wenigen Wörtern besteht
    und nicht wie eine Einrichtung aussieht. Versalien gelten immer.
    """
    # „Deutsch: Muttersprache“ enthält „sprach“ und ist eine Angabe, keine
    # Überschrift. Ein Doppelpunkt mit Text dahinter schließt das aus.
    if len(zeile) > 45 or FIRMA.search(zeile) or re.search(r':\s*\S', zeile):
        return None
    versal = zeile == zeile.upper() and len(zeile) > 3
    if not versal and len(zeile.split()) > 3:
        return None
    for name, muster in RUBRIKEN:
        if re.search(muster, zeile, re.I):
            return name
    return None


def rubriken_gemessen(ueberschriften, anzahl):
    """Die Ueberschriften, wie der Leser sie im Dokument gemessen hat.

    Geliefert wird je Ueberschrift die erste und letzte Zeile und der
    Schriftgrad. Der Name ganz oben ist ebenfalls gross gesetzt und meist noch
    groesser - die Rubriken sind die Gruppe mit den meisten Mitgliedern, alles
    Groessere faellt heraus. Unter zwei Rubriken lohnt es nicht; dann bleibt es
    bei den Mustern.
    """
    roh = []
    for u in (ueberschriften or []):
        try:
            von = int(u.get('von') or 0)
            bis = int(u.get('bis') or von)
            grad = float(u.get('grad') or 0)
        except (TypeError, ValueError):
            continue
        titel = (u.get('titel') or '').strip()
        if titel and 1 <= von <= anzahl and bis >= von:
            roh.append((von, bis, titel, round(grad * 2) / 2))
    if len(roh) < 2:
        return None
    haeufig = {}
    for _, _, _, g in roh:
        haeufig[g] = haeufig.get(g, 0) + 1
    rubrik_grad = sorted(haeufig.items(), key=lambda p: (-p[1], p[0]))[0][0]
    genommen = [r for r in roh if abs(r[3] - rubrik_grad) < 0.1]
    if len(genommen) < 2:
        return None
    aus = {'rubrik': {}, 'titel': {}, 'weiter': set()}
    for von, bis, titel, _ in genommen:
        aus['rubrik'][von] = rubrik_von(titel) or 'weitere'
        aus['titel'][von] = titel
        for nr in range(von + 1, bis + 1):
            aus['weiter'].add(nr)
    return aus


def lebenslauf_aus(text, ueberschriften=None):
    """Baut aus dem gelieferten Text einen Lebenslauf — mit einfachen Regeln,
    nicht mit einem Modell.

    Das ist ausdrücklich kein Ersatz für die KI: Es ordnet nur, was schon
    dasteht. Der Sinn ist, im Testbetrieb den *eigenen* Lebenslauf im Layout
    zu sehen statt einer erfundenen Musterperson — und zu erkennen, ob das
    Auslesen der Datei überhaupt etwas gebracht hat.
    """
    zeilen = [z.strip() for z in (text or '').splitlines() if z.strip()]
    # Was das Dokument selbst als Ueberschrift setzt, schlaegt jedes Muster.
    gemessen = rubriken_gemessen(ueberschriften, len(zeilen))
    aus = {'sprache': 'de', 'kopf': {'name': '', 'rolle': '', 'profil': ''}, 'kontakt': [],
           'berufserfahrung': [], 'ausbildung': [], 'kenntnisse': [], 'sprachen': [],
           'weiterbildung': [], 'weitere': [], 'ueberschriften': {},
           'zeichenErhalten': len(text or '')}

    # Kopf: die erste Zeile, die wie ein Name aussieht, danach die Rolle.
    ist_rubrik = (lambda nr, z: (nr + 1) in gemessen['rubrik']) if gemessen is not None \
                 else (lambda nr, z: bool(rubrik_von(z)))
    for i, z in enumerate(zeilen[:6]):
        if ist_rubrik(i, z):
            break            # ab der ersten Überschrift ist der Kopf vorbei
        if not aus['kopf']['name'] and re.match(r"^[^\d@]{4,45}$", z) and 1 <= z.count(' ') <= 3:
            aus['kopf']['name'] = z
            if i + 1 < len(zeilen) and not ist_rubrik(i + 1, zeilen[i + 1]):
                aus['kopf']['rolle'] = zeilen[i + 1][:70]
            break

    rubrik = None
    eintrag = None
    wartend = []          # Zeilen vor einem Zeitraum: Abschluss, Fach, Einrichtung

    datum_allein = [False]      # Stand der Zeitraum in einer eigenen Zeile?

    def zeitraum_folgt(i, weite=3):
        """Kommt gleich ein Zeitraum? Dann gehört diese Zeile zum nächsten
        Eintrag und nicht als Stichpunkt zum laufenden."""
        for j in range(i + 1, min(i + 1 + weite, len(zeilen))):
            if ist_rubrik(j, zeilen[j]):
                return False        # dazwischen fängt eine neue Rubrik an
            if ZEITRAUM.search(zeilen[j]):
                return True
        return False

    for i, z in enumerate(zeilen):
        if gemessen is not None and (i + 1) in gemessen.get('weiter', ()):
            continue                      # zweite Zeile einer Ueberschrift
        neue = gemessen['rubrik'].get(i + 1) if gemessen is not None else rubrik_von(z)
        if gemessen is not None and neue:
            z = gemessen['titel'].get(i + 1, z)
        if neue == 'weitere':
            aus['weitere'].append({'titel': z.strip(' :'), 'punkte': []})
            rubrik, eintrag, wartend = 'weitere', None, []
            continue
        if neue:
            # Die Ueberschrift des Dokuments merken: Wer seinen Abschnitt
            # "Kontakt" nennt, soll ihn auf dem Blatt "Kontakt" nennen duerfen.
            aus['ueberschriften'].setdefault(neue, z.strip(' :'))
            rubrik, eintrag, wartend = neue, None, []
            continue
        if z in (aus['kopf']['name'], aus['kopf']['rolle']):
            continue

        if '@' in z and len(z) < 60:
            aus['kontakt'].append({'art': 'mail', 'wert': z}); continue
        if re.match(r'^[+\d][\d\s()/-]{7,}$', z):
            aus['kontakt'].append({'art': 'tel', 'wert': z}); continue
        if re.match(r'^\d{1,2}\.\d{1,2}\.\d{4}$', z):
            aus['kontakt'].append({'art': 'datum', 'wert': z}); continue
        if re.search(r'\b\d{5}\b', z) and len(z) < 70:
            aus['kontakt'].append({'art': 'ort', 'wert': z}); continue

        zeit = ZEITRAUM.search(z)
        if rubrik in ('berufserfahrung', 'ausbildung', 'weiterbildung'):
            if zeit:
                # Steht der Zeitraum in einer eigenen Zeile, gehören Abschluss
                # und Einrichtung zu den Zeilen davor — nicht zu denen danach.
                rest = ZEITRAUM.sub('', z).strip(' ,;·|–-')
                datum_allein[0] = not rest
                kopf = [t for t in wartend if t]
                if not rest and kopf:
                    rest, kopf = kopf[0], kopf[1:]
                einrichtung = next((t for t in kopf if FIRMA.search(t)), '')
                fach = next((t for t in kopf if t != einrichtung), '')
                wartend = []
                if rubrik == 'ausbildung':
                    eintrag = {'abschluss': rest or '—', 'fach': fach,
                               'einrichtung': einrichtung,
                               'von': zeit.group(1), 'bis': zeit.group(2), 'punkte': []}
                elif rubrik == 'weiterbildung':
                    eintrag = {'titel': rest or fach or '—', 'anbieter': einrichtung,
                               'jahr': zeit.group(2)}
                else:
                    eintrag = {'titel': rest or '—', 'firma': einrichtung, 'ort': '',
                               'von': zeit.group(1), 'bis': zeit.group(2), 'punkte': []}
                aus[rubrik].append(eintrag)
                continue
            if eintrag is None or (datum_allein[0] and zeitraum_folgt(i)):
                wartend = (wartend + [z])[-3:]
                continue
            if eintrag is not None:
                if FIRMA.search(z) and not eintrag.get('firma') and not eintrag.get('einrichtung'):
                    if rubrik == 'ausbildung':
                        eintrag['einrichtung'] = z
                    elif rubrik == 'weiterbildung':
                        eintrag['anbieter'] = z
                    else:
                        eintrag['firma'] = z
                elif 'punkte' in eintrag:
                    eintrag['punkte'].append(z.lstrip('•-–· '))
                continue

        if rubrik == 'profil' or (rubrik is None and ist_fliesstext(z)):
            aus['kopf']['profil'] = (aus['kopf']['profil'] + ' ' + z).strip()
            continue

        if rubrik == 'kenntnisse':
            if ist_fliesstext(z):
                aus['kopf']['profil'] = (aus['kopf']['profil'] + ' ' + z).strip()
                continue
            for teil in re.split(r'\s*[,;|]\s*', z):
                if teil.strip():
                    aus['kenntnisse'].append(teil.strip().lstrip('•-–· '))
            continue

        if rubrik == 'sprachen':
            if ist_fliesstext(z):
                aus['kopf']['profil'] = (aus['kopf']['profil'] + ' ' + z).strip()
                continue
            for teil in re.split(r'\s{2,}|\s*[,;|]\s*', z):
                teil = teil.strip().lstrip('•-–· ')
                if not teil:
                    continue
                stufe = re.split(r'\s*[:–—-]\s*|\s+\(', teil, 1)
                aus['sprachen'].append({'sprache': stufe[0].strip(),
                                        'niveau': stufe[1].strip(' )') if len(stufe) > 1 else ''})
            continue

        if rubrik == 'weitere' and aus['weitere']:
            aus['weitere'][-1]['punkte'].append(z.lstrip('•-–· '))
            continue

        if rubrik is None and len(zeilen) > 3:
            continue

    # Ist gar nichts erkannt worden, bleibt wenigstens der Rohtext sichtbar.
    if not (aus['berufserfahrung'] or aus['ausbildung'] or aus['kenntnisse']):
        aus['weitere'].append({'titel': 'Aus der Datei',
                               'punkte': [z for z in zeilen[:25]]})
    return aus


WORTTAUSCH = [
    ('Steuerung', 'Koordination'),
    ('Koordination', 'Steuerung'),
    ('Erstellung', 'Aufbau'),
    ('Analyse', 'Auswertung'),
    ('Betreuung', 'Begleitung'),
    ('Digitalisierung', 'digitale Transformation'),
    (' und ', ' sowie '),
]


STANDARDTITEL = {'kontakt': 'Kontakt', 'beruf': 'Berufserfahrung',
                 'ausbildung': 'Ausbildung', 'liste': 'Kenntnisse',
                 'sprachen': 'Sprachen', 'weiterbildung': 'Weiterbildung'}

# Von welchem Feld des flachen Formulars zu welcher Art - dieselbe Zuordnung
# wie im Worker, damit der Testbetrieb denselben Weg geht.
FLACH_ZU_ART = [
    ('kontakt', 'kontakt', 'kontakt'),
    ('berufserfahrung', 'beruf', 'berufserfahrung'),
    ('ausbildung', 'ausbildung', 'ausbildung'),
    ('kenntnisse', 'liste', 'kenntnisse'),
    ('sprachen', 'sprachen', 'sprachen'),
    ('weiterbildung', 'weiterbildung', 'weiterbildung'),
]


def abschnitte_aus_flach(flach):
    """Das flache Formular in die Folge von Abschnitten bringen, die der
    Editor heute erwartet - mit den Ueberschriften des Dokuments, wo sie
    bekannt sind."""
    ueber = flach.get('ueberschriften') or {}
    abschnitte = []
    for feld, art, schluessel in FLACH_ZU_ART:
        eintraege = flach.get(feld) or []
        if eintraege:
            abschnitte.append({'titel': ueber.get(schluessel) or STANDARDTITEL[art],
                               'art': art, 'eintraege': eintraege})
    for w in flach.get('weitere') or []:
        if w.get('punkte'):
            abschnitte.append({'titel': w.get('titel') or 'Weitere Angaben',
                               'art': 'liste', 'eintraege': w['punkte']})
    return {'sprache': flach.get('sprache') or 'de',
            'kopf': flach.get('kopf') or {},
            'abschnitte': abschnitte}


def stellen_aus(lebenslauf):
    """Dasselbe Adressschema wie api/texte.js - nur die Stellen, an denen
    umformuliert werden darf. Der Zuschnitt bekommt den Lebenslauf vom Blatt,
    und das ist weiterhin das flache Formular."""
    aus = []
    kopf = lebenslauf.get('kopf') or {}
    if kopf.get('rolle'):
        aus.append(('kopf.rolle', 'Berufsbezeichnung', kopf['rolle']))
    if kopf.get('profil'):
        aus.append(('kopf.profil', 'Kurzprofil', kopf['profil']))
    for i, job in enumerate(lebenslauf.get('berufserfahrung') or []):
        for k, punkt in enumerate(job.get('punkte') or []):
            aus.append(('beruf.%d.punkt.%d' % (i, k), job.get('titel') or 'Station', punkt))
    for i, weg in enumerate(lebenslauf.get('ausbildung') or []):
        for k, punkt in enumerate(weg.get('punkte') or []):
            aus.append(('ausbildung.%d.punkt.%d' % (i, k),
                        weg.get('abschluss') or 'Ausbildung', punkt))
    for i, kenntnis in enumerate(lebenslauf.get('kenntnisse') or []):
        aus.append(('kenntnis.%d' % i, 'Kenntnisse', kenntnis))
    return [(a, b, c) for a, b, c in aus if (c or '').strip()]


def umformuliert(text):
    """Eine Umformulierung ohne neue Behauptung - mehr braucht der
    Testbetrieb nicht, und weniger waere unehrlich. Faellt kein Wort ein,
    gibt es keinen Vorschlag: ein Vorschlag, der nichts aendert, kostet den
    Leser Zeit und bringt ihm nichts."""
    for wort, ersatz in WORTTAUSCH:
        if wort in text:
            return text.replace(wort, ersatz, 1)
    return None


def fehlende_zeilen(text, lebenslauf, ueberschriften=None):
    """Welche Zeile des Quelltextes findet sich im Ergebnis nicht wieder?
    Dieselbe Rechnung wie im Worker, damit der Testbetrieb denselben Weg
    geht wie der Ernstfall."""
    import re as _re
    def worte(s):
        return [w for w in _re.split(r'[^0-9A-Za-zÀ-ÿ]+', s.lower()) if len(w) >= 4]
    da = set(worte(json.dumps(lebenslauf, ensure_ascii=False)))
    kopfzeilen = {' '.join(worte(u)) for u in (ueberschriften or [])}
    fehlt = []
    for zeile in text.split('\n'):
        roh = zeile.strip()
        if len(roh) < 8 or _re.match(r'^(lebenslauf|cv|seite \d+|\d+)$', roh, _re.I):
            continue
        w = worte(roh)
        if not w or ' '.join(w) in kopfzeilen:
            continue
        if sum(1 for x in w if x in da) / len(w) < 0.6:
            fehlt.append(roh)
    return fehlt[:30]


def antwort_fuer(weg, daten):
    """Die Antwort auf einen der KI-Wege. Wird von diesem Server und von
    tools/serve.py benutzt — eine Quelle, zwei Betriebsarten."""
    weg = weg.replace('/api', '')

    if weg == '/parse':
        text = daten.get('text') or ''
        if daten.get('datei'):
            text = ('Aus Datei: ' + (daten['datei'].get('name') or '') + '\nProjektmanager\n'
                    + 'Base64-Laenge ' + str(len(daten['datei'].get('daten') or '')))
        flach = lebenslauf_aus(text, daten.get('ueberschriften'))
        lebenslauf = abschnitte_aus_flach(flach)
        # Derselbe Weg wie im Worker: nachzaehlen, was im Ergebnis fehlt, und
        # es hinten anhaengen, statt es verschwinden zu lassen.
        # Die Ueberschriften stehen in keinem Eintrag - sie fehlen also nicht.
        bekannt = list((flach.get('ueberschriften') or {}).values())
        bekannt += [a['titel'] for a in lebenslauf['abschnitte']]
        fehlt = fehlende_zeilen(text, lebenslauf, bekannt)
        if fehlt:
            lebenslauf['abschnitte'].append(
                {'titel': 'Weitere Angaben', 'art': 'liste', 'eintraege': fehlt})
        return 200, {'lebenslauf': lebenslauf, 'nachgetragen': len(fehlt), 'offen': 0}

    if weg == '/tailor':
        alt = daten.get('lebenslauf') or {}
        stellen = stellen_aus(alt)[:4]
        vorschlaege = []
        for nr, (kennung, wo, text) in enumerate(stellen):
            if nr != 1 and umformuliert(text) is None:
                continue
            # Der zweite ist absichtlich einer, der mehr behauptet als das
            # Original: genau den muss der Benutzer ungehakt vorfinden.
            bedenklich = nr == 1
            vorschlaege.append({
                'id': kennung, 'wo': wo, 'vorher': text,
                'nachher': (text.rstrip('.') + ' für sieben Dienstleister') if bedenklich
                           else umformuliert(text),
                'warum': 'Die Anzeige nennt das zuerst.',
                'bedenken': 'Im Original steht keine Anzahl.' if bedenklich else ''})
        kenntnisse = alt.get('kenntnisse') or []
        reihenfolge = list(reversed(kenntnisse)) if len(kenntnisse) > 1 else None
        return 200, {
            'vorschlaege': vorschlaege,
            'reihenfolge': reihenfolge,
            'verworfen': [{'wo': 'Kurzprofil', 'grund': 'neue Angabe: 40'}],
            'passung': PASSUNG,
            'luecken': ['SAP S/4HANA', 'Erfahrung im Anlagenbau'],
        }

    if weg == '/analyse':
        hinweise = daten.get('hinweise') or []
        return 200, {
            'staerken': ['Acht Jahre ohne Bruch in einer Linie.',
                         'Jede Station mit Zahlen belegt.'],
            'auffaelligkeiten': [
                {'art': 'luecke', 'wo': '02/2020 – 09/2020',
                 'befund': hinweise[0] if hinweise else 'Zwischen zwei Stationen fehlen Monate.',
                 'rat': 'Eine Zeile in den Lebenslauf: „07/2020 – 09/2020 Weiterbildung '
                        'Projektmanagement“. Nicht erklären, nur benennen.',
                 'gewicht': 'hoch'},
                {'art': 'inhalt', 'wo': 'Projektreferent, 2017–2021',
                 'befund': 'Drei von vier Punkten beschreiben Aufgaben, kein Ergebnis.',
                 'rat': 'Aus „Koordination von Terminen“ wird „Koordination von Terminen für '
                        'zwei Systemeinführungen“ — nur wenn das stimmt.',
                 'gewicht': 'mittel'},
                {'art': 'formales', 'wo': 'Kenntnisse',
                 'befund': '„SAP – Grundkenntnisse“ steht neben „Microsoft Office – fortgeschritten“.',
                 'rat': 'Reihenfolge nach Relevanz für die Stelle, nicht nach Können.',
                 'gewicht': 'klein'}],
            'fragen': [
                {'frage': 'Was haben Sie zwischen Februar und September 2020 gemacht?',
                 'warum': 'Die Lücke zwischen Musterfirma AG und der nächsten Station.',
                 'antwort': 'Kurz benennen, was in der Zeit war, und auf die Weiterbildung '
                            'verweisen, die im Lebenslauf schon steht.',
                 'falle': 'Nicht ausweichen und keine Beschäftigung erfinden, die sich prüfen lässt.'},
                {'frage': 'Sie führen „Verantwortung für Budgetziele“ auf — wie hoch war das Budget?',
                 'warum': 'Der Punkt bei Projektmanager Digitalisierung nennt keine Größe.',
                 'antwort': 'Die Zahl nennen, die im Lebenslauf steht (bis 500.000 €), und sagen, '
                            'worauf sich das bezog.'},
                {'frage': 'Warum der Wechsel vom Werkstudenten in die Beratung?',
                 'warum': 'Der Sprung zwischen 2015 und 2017.',
                 'antwort': 'Aus den beiden Stationen erzählen, was inhaltlich zusammengehört.'}],
            'passung': PASSUNG if (daten.get('stelle') or '').strip() else None,
        }

    if weg == '/stelle':
        return 200, {'text': 'Wir suchen eine Projektleitung. ' * 20,
                     'titel': 'Projektleitung (m/w/d)', 'quelle': 'firma.example'}

    if weg == '/status':
        return 200, {'bereit': True, 'modell': 'Testbetrieb', 'grenze': 'keine'}

    return 404, {'fehler': 'Unbekannter Endpunkt'}


PASSUNG = {
    'wert': 72,
    'urteil': 'Die Projektsteuerung sitzt, die Branchenerfahrung fehlt.',
    'treffer': [{'anforderung': 'Mehrjährige Projektleitung',
                 'beleg': 'Projektmanager Digitalisierung seit 03/2021'},
                {'anforderung': 'Steuerung externer Dienstleister',
                 'beleg': 'Punkt 3 der aktuellen Station'}],
    'offen': [{'anforderung': 'SAP S/4HANA',
               'rat': 'Im Lebenslauf steht nur „SAP – Grundkenntnisse“. Nicht aufwerten.'},
              {'anforderung': 'Erfahrung im Anlagenbau',
               'rat': 'Fehlt. Im Anschreiben auf die Branchenwechsel eingehen.'}],
}


class Griff(BaseHTTPRequestHandler):
    def _senden(self, daten, status=200):
        koerper = json.dumps(daten, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Length', str(len(koerper)))
        self.end_headers()
        self.wfile.write(koerper)

    def do_OPTIONS(self):
        self._senden({}, 204)

    def do_GET(self):
        status, daten = antwort_fuer('/status', {})
        self._senden(daten, status)

    def do_POST(self):
        laenge = int(self.headers.get('Content-Length') or 0)
        daten = json.loads(self.rfile.read(laenge) or b'{}')
        status, antwort = antwort_fuer(self.path, daten)
        self._senden(antwort, status)

    def log_message(self, *args):
        pass


if __name__ == '__main__':
    tor = int(sys.argv[1]) if len(sys.argv) > 1 else 8768
    print('Testbetrieb auf http://localhost:%d/api' % tor)
    HTTPServer(('127.0.0.1', tor), Griff).serve_forever()
