#!/usr/bin/env python3
"""
Ein Ersatz für den KI-Worker, damit sich die Oberfläche ohne Schlüssel und
ohne Kosten ausprobieren lässt.

    python3 tools/mock-ki.py 8768

Dann in assets/site-config.js eintragen:

    ki: { endpunkt: 'http://localhost:8768/api', anbieter: 'Testbetrieb' }

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
        self._senden({'bereit': True, 'modell': 'testbetrieb', 'grenze': 'keine'})

    def do_POST(self):
        laenge = int(self.headers.get('Content-Length') or 0)
        daten = json.loads(self.rfile.read(laenge) or b'{}')
        weg = self.path.replace('/api', '')

        if weg == '/parse':
            text = daten.get('text') or ''
            if daten.get('datei'):
                text = 'Aus Datei: ' + (daten['datei'].get('name') or '') + '\nProjektmanager\n' \
                     + 'Base64-Länge ' + str(len(daten['datei'].get('daten') or ''))
            return self._senden({'lebenslauf': lebenslauf_aus(text)})

        if weg == '/tailor':
            alt = daten.get('lebenslauf') or {}
            neu = json.loads(json.dumps(alt))
            if neu.get('berufserfahrung'):
                erste = neu['berufserfahrung'][0]
                erste['punkte'] = ['Steuerung von sieben externen Dienstleistern'] + \
                                  list(erste.get('punkte') or [])[1:]
            return self._senden({
                'lebenslauf': neu,
                'aenderungen': [{'wo': 'Berufserfahrung 1, Punkt 1',
                                 'vorher': 'Steuerung externer Dienstleister',
                                 'nachher': 'Steuerung von sieben externen Dienstleistern',
                                 'warum': 'Die Anzeige nennt Lieferantensteuerung zuerst'}],
                'luecken': ['SAP S/4HANA', 'Erfahrung im Anlagenbau'],
                'beanstandet': [{'nachher': 'Steuerung von sieben externen Dienstleistern',
                                 'grund': 'Das Original nennt keine Anzahl'}],
            })

        if weg == '/stelle':
            return self._senden({'text': 'Wir suchen eine Projektleitung. ' * 20,
                                 'titel': 'Projektleitung (m/w/d)', 'quelle': 'firma.example'})

        self._senden({'fehler': 'Unbekannter Endpunkt'}, 404)

    def log_message(self, *args):
        pass


if __name__ == '__main__':
    tor = int(sys.argv[1]) if len(sys.argv) > 1 else 8768
    print('Testbetrieb auf http://localhost:%d/api' % tor)
    HTTPServer(('127.0.0.1', tor), Griff).serve_forever()
