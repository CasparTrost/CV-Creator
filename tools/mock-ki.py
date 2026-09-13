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
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer


def lebenslauf_aus(text):
    zeilen = [z.strip() for z in text.splitlines() if z.strip()]
    return {
        'sprache': 'de',
        'kopf': {
            'name': zeilen[0] if zeilen else 'Ohne Namen',
            'rolle': zeilen[1] if len(zeilen) > 1 else '',
            'profil': ' '.join(zeilen[2:5]),
        },
        'kontakt': [{'art': 'mail', 'wert': 'max.mustermann@example.de'},
                    {'art': 'tel', 'wert': '+49 170 123 45 67'}],
        'berufserfahrung': [{
            'titel': 'Projektmanager', 'firma': 'Beispiel GmbH', 'ort': 'Nürnberg',
            'von': '03/2021', 'bis': 'heute',
            'punkte': ['Steuerung externer Dienstleister', 'Aufnahme von Anforderungen'],
        }],
        'ausbildung': [{'abschluss': 'Master of Science', 'fach': 'Wirtschaftsinformatik',
                        'einrichtung': 'Universität Musterstadt', 'von': '2015', 'bis': '2017',
                        'punkte': []}],
        'kenntnisse': ['Projektsteuerung', 'Anforderungsanalyse', 'Jira'],
        'sprachen': [{'sprache': 'Deutsch', 'niveau': 'Muttersprache'},
                     {'sprache': 'Englisch', 'niveau': 'C1'}],
        'weiterbildung': [{'titel': 'Professional Scrum Master I', 'anbieter': 'Scrum.org',
                           'jahr': '2022'}],
        'weitere': [],
        # Nur für die Prüfung im Test: wie viele Zeichen kamen an?
        'zeichenErhalten': len(text),
    }


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
