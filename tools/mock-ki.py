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


RUBRIKEN = [
    ('berufserfahrung', r'berufserfahrung|berufliche|werdegang|praxis|experience|employment|experiencia'),
    ('ausbildung', r'ausbildung|bildungsweg|studium|schul|education|academic|formaci'),
    ('weiterbildung', r'weiterbildung|fortbildung|zertifikat|training|certificat'),
    ('kenntnisse', r'kenntnis|kompetenz|f[äa]higkeit|skills|edv|it-|competenc'),
    ('sprachen', r'^sprachen|languages|idiomas'),
    ('kontakt', r'pers[öo]nliche daten|kontakt|personal details|contact|datos'),
]
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
    if len(zeile) > 45 or FIRMA.search(zeile):
        return None
    versal = zeile == zeile.upper() and len(zeile) > 3
    if not versal and len(zeile.split()) > 3:
        return None
    for name, muster in RUBRIKEN:
        if re.search(muster, zeile, re.I):
            return name
    return None


def lebenslauf_aus(text):
    """Baut aus dem gelieferten Text einen Lebenslauf — mit einfachen Regeln,
    nicht mit einem Modell.

    Das ist ausdrücklich kein Ersatz für die KI: Es ordnet nur, was schon
    dasteht. Der Sinn ist, im Testbetrieb den *eigenen* Lebenslauf im Layout
    zu sehen statt einer erfundenen Musterperson — und zu erkennen, ob das
    Auslesen der Datei überhaupt etwas gebracht hat.
    """
    zeilen = [z.strip() for z in (text or '').splitlines() if z.strip()]
    aus = {'sprache': 'de', 'kopf': {'name': '', 'rolle': '', 'profil': ''}, 'kontakt': [],
           'berufserfahrung': [], 'ausbildung': [], 'kenntnisse': [], 'sprachen': [],
           'weiterbildung': [], 'weitere': [], 'zeichenErhalten': len(text or '')}

    # Kopf: die erste Zeile, die wie ein Name aussieht, danach die Rolle.
    for i, z in enumerate(zeilen[:6]):
        if rubrik_von(z):
            break            # ab der ersten Überschrift ist der Kopf vorbei
        if not aus['kopf']['name'] and re.match(r"^[^\d@]{4,45}$", z) and 1 <= z.count(' ') <= 3:
            aus['kopf']['name'] = z
            if i + 1 < len(zeilen) and not rubrik_von(zeilen[i + 1]):
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
            if rubrik_von(zeilen[j]):
                return False        # dazwischen fängt eine neue Rubrik an
            if ZEITRAUM.search(zeilen[j]):
                return True
        return False

    for i, z in enumerate(zeilen):
        neue = rubrik_von(z)
        if neue:
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

        if rubrik == 'kenntnisse':
            for teil in re.split(r'\s*[,;|]\s*', z):
                if teil.strip():
                    aus['kenntnisse'].append(teil.strip().lstrip('•-–· '))
            continue
        if rubrik == 'sprachen':
            teile = re.split(r'\s*[:–-]\s*', z, 1)
            aus['sprachen'].append({'sprache': teile[0].lstrip('•-–· '),
                                    'niveau': teile[1] if len(teile) > 1 else ''})
            continue
        if rubrik is None and len(z) > 90 and not aus['kopf']['profil']:
            aus['kopf']['profil'] = z
            continue
        if rubrik is None and len(zeilen) > 3:
            continue

    # Ist gar nichts erkannt worden, bleibt wenigstens der Rohtext sichtbar.
    if not (aus['berufserfahrung'] or aus['ausbildung'] or aus['kenntnisse']):
        aus['weitere'].append({'titel': 'Aus der Datei',
                               'punkte': [z for z in zeilen[:25]]})
    return aus


def antwort_fuer(weg, daten):
    """Die Antwort auf einen der KI-Wege. Wird von diesem Server und von
    tools/serve.py benutzt — eine Quelle, zwei Betriebsarten."""
    weg = weg.replace('/api', '')

    if weg == '/parse':
        text = daten.get('text') or ''
        if daten.get('datei'):
            text = ('Aus Datei: ' + (daten['datei'].get('name') or '') + '\nProjektmanager\n'
                    + 'Base64-Länge ' + str(len(daten['datei'].get('daten') or '')))
        return 200, {'lebenslauf': lebenslauf_aus(text)}

    if weg == '/tailor':
        alt = daten.get('lebenslauf') or {}
        neu = json.loads(json.dumps(alt))
        if neu.get('berufserfahrung'):
            erste = neu['berufserfahrung'][0]
            erste['punkte'] = (['Steuerung von sieben externen Dienstleistern']
                               + list(erste.get('punkte') or [])[1:])
        return 200, {
            'lebenslauf': neu,
            'passung': PASSUNG,
            'aenderungen': [{'wo': 'Berufserfahrung 1, Punkt 1',
                             'vorher': 'Steuerung externer Dienstleister',
                             'nachher': 'Steuerung von sieben externen Dienstleistern',
                             'warum': 'Die Anzeige nennt Lieferantensteuerung zuerst'}],
            'luecken': ['SAP S/4HANA', 'Erfahrung im Anlagenbau'],
            'beanstandet': [{'nachher': 'Steuerung von sieben externen Dienstleistern',
                             'grund': 'Das Original nennt keine Anzahl'}],
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
