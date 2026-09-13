#!/usr/bin/env python3
"""Serve the site locally, the way a real host would.

    python3 tools/serve.py            # http://localhost:8000
    python3 tools/serve.py 8080       # another port

Three things this does that `python3 -m http.server` does not:

  * a missing path gets 404.html (or de/404.html under de/), so the
    not-found page can actually be looked at;
  * nothing is cached, so a reload after tools/build.py shows the new
    page instead of the old one;
  * /api/… is answered with the canned replies from tools/mock-ki.py, so
    the three AI functions in the editor can be clicked through without a
    key, without a deployment and without a cent. The editor looks for
    them here by itself when it is served from localhost and no endpoint
    is configured — and says "Testbetrieb" while it does.

Stop it with Ctrl+C.
"""
import functools
import http.server
import importlib.util
import json
import os
import socketserver
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _testbetrieb():
    """tools/mock-ki.py laden — der Bindestrich verbietet den normalen Weg."""
    pfad = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock-ki.py')
    spec = importlib.util.spec_from_file_location('mock_ki', pfad)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


TESTBETRIEB = _testbetrieb()


class Handler(http.server.SimpleHTTPRequestHandler):

    # ---- der Testbetrieb für die KI-Funktionen ----------------------------
    def _json(self, daten, status=200):
        koerper = json.dumps(daten, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Length', str(len(koerper)))
        self.end_headers()
        self.wfile.write(koerper)

    def do_POST(self):
        if not self.path.startswith('/api/'):
            self.send_error(501, 'Unsupported method (POST)')
            return
        laenge = int(self.headers.get('Content-Length') or 0)
        try:
            daten = json.loads(self.rfile.read(laenge) or b'{}')
        except ValueError:
            self._json({'fehler': 'Ungültige Anfrage.'}, 400)
            return
        status, antwort = TESTBETRIEB.antwort_fuer(self.path, daten)
        self._json(antwort, status)

    def do_OPTIONS(self):
        self._json({}, 204)

    def do_GET(self):
        if self.path.startswith('/api/'):
            status, antwort = TESTBETRIEB.antwort_fuer('/status', {})
            self._json(antwort, status)
            return
        super().do_GET()

    def end_headers(self):
        # A cached page after a rebuild is the most confusing thing that
        # can happen while looking at a change.
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def send_error(self, code, message=None, explain=None):
        if code == 404:
            page = 'de/404.html' if self.path.startswith('/de/') else '404.html'
            full = os.path.join(ROOT, page)
            if os.path.exists(full):
                body = open(full, 'rb').read()
                self.send_response(404)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(body)))
                self.send_header('Cache-Control', 'no-store')
                self.end_headers()
                self.wfile.write(body)
                return
        super().send_error(code, message, explain)

    def log_message(self, fmt, *args):
        # One line per request, without the date noise.
        sys.stderr.write('  %s\n' % (fmt % args))


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    handler = functools.partial(Handler, directory=ROOT)
    try:
        with Server(('', port), handler) as httpd:
            print('PlainSheet on http://localhost:%d' % port)
            print('  English  http://localhost:%d/' % port)
            print('  Deutsch  http://localhost:%d/de/' % port)
            print('  Editor   http://localhost:%d/editor.html' % port)
            print('  KI       Testbetrieb unter /api — erfundene Antworten, keine Kosten')
            print('Ctrl+C to stop.\n')
            httpd.serve_forever()
    except OSError as err:
        print('Could not listen on port %d: %s' % (port, err))
        print('Something else is probably using it. Try: python3 tools/serve.py 8080')
        return 1
    except KeyboardInterrupt:
        print('\nStopped.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
