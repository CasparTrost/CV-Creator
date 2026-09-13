# Der KI-Teil

Drei Funktionen im Editor brauchen ein Sprachmodell: einen vorhandenen
Lebenslauf einlesen, ihn auf eine Stellenanzeige zuschneiden und ihn prüfen
lassen (Auffälligkeiten, Gesprächsfragen, Passung). Alle drei laufen über
diesen Worker.

## Warum überhaupt ein Server

Der API-Schlüssel darf nicht in den Browser. Wer ihn dort hinlegt, hat ihn
veröffentlicht — er steht dann in jedem „Quelltext anzeigen", und die Rechnung
schreibt jemand anderes. Der Worker hält den Schlüssel, begrenzt die Menge und
ist das einzige Stück Server, das diese Seite hat. Der Editor selbst bleibt,
was er war: eine Seite, die im Browser läuft.

## Einrichten

```sh
cd api
npx wrangler login
npx wrangler secret put COMETAPI_KEY      # der Schlüssel von cometapi.com
npx wrangler deploy
```

**Der kürzeste Weg zum echten Modell** führt nicht über das Deployment:
`tools\ki-start.cmd` (Windows) fragt einmal nach dem Schlüssel, legt ihn in
`api/.dev.vars` ab und startet `npx wrangler dev`. Der Editor findet den
Dienst auf `localhost:8787` von selbst und schaltet den Testbetrieb ab — ohne
Cloudflare-Konto, ohne Veröffentlichung, ohne dass irgendwo etwas einzutragen
wäre. Auf anderen Systemen ist es `cd api && npx wrangler dev`.

**Zum bloßen Anschauen braucht es auch das nicht:** `python3 tools/serve.py`
beantwortet dieselben Wege selbst mit erfundenen Antworten, und der Editor
findet sie auf localhost von allein — erkennbar am Vermerk „Testbetrieb“ in
der Leiste. Erst wenn echte Antworten kommen sollen, gilt das hier.

Zum Ausprobieren auf dem eigenen Rechner liest `wrangler dev` den Schlüssel
aus `api/.dev.vars`. Diese Datei steht in `.gitignore` und darf dort bleiben —
ein Schlüssel im Repository ist ein veröffentlichter Schlüssel. Für den
Betrieb zählt nur das Secret oben.

`wrangler deploy` nennt am Ende die Adresse, etwa
`https://plainsheet-ki.<konto>.workers.dev`. Diese Adresse gehört in
`assets/site-config.js`:

```js
ki: { endpunkt: 'https://plainsheet-ki.<konto>.workers.dev/api', aktiv: true }
```

Danach `python3 tools/build.py` laufen lassen und beides hochladen.

In `wrangler.toml` gehört `HERKUNFT` auf die eigene Domain, sonst darf jede
fremde Seite den Worker benutzen — und damit das Guthaben.

**Die Bremse anschalten.** Ohne KV-Bindung ist der Worker ungebremst:

```sh
npx wrangler kv namespace create LIMITS
```

Die ausgegebene ID in `wrangler.toml` eintragen, den Block einkommentieren,
neu deployen. Danach gilt eine Obergrenze pro IP und Tag (siehe `GRENZEN` in
`worker.js`). `GET /api/status` sagt, ob sie greift.

## Was kostet das

Ein Lebenslauf sind grob 1.500 bis 4.000 Token Eingabe und 1.000 bis 2.000
Token Ausgabe. Das Zuschneiden ruft das Modell zweimal (einmal schreiben,
einmal die eigene Arbeit prüfen). Bei einem günstigen Modell liegt ein
Durchgang im Bereich weniger Zehntelcent — aber rechne mit dem aktuellen
Preis des Modells, das du einträgst, und setze in deinem Konto ein
Ausgabenlimit. Die Bremse oben ersetzt das nicht.

## Endpunkte

| Weg | Eingabe | Ausgabe |
| --- | --- | --- |
| `POST /api/parse` | `{text}` oder `{datei:{name,typ,daten}}` (Base64) | `{lebenslauf}` |
| `POST /api/tailor` | `{lebenslauf, stelle}` | `{lebenslauf, aenderungen, luecken, beanstandet}` |
| `POST /api/analyse` | `{lebenslauf, stelle?, hinweise[]}` | `{staerken, auffaelligkeiten, fragen, passung}` |
| `POST /api/stelle` | `{url}` | `{text, titel, quelle}` |
| `GET /api/status` | – | Selbstauskunft, ohne Geheimnisse |

## PDF

`pdf.js` holt den Text selbst heraus: Seiten, Schriftressourcen,
`ToUnicode`-Tabellen, Flate-Ströme, gepackte Objektströme.

Nichts daran ist auf eine Vorlage zugeschnitten, weil es keine zwei gleichen
Lebensläufe gibt. Gemessen wird die Geometrie: Wo ist ein senkrechter Graben
ohne Text? Auf welchen Höhen steht links und rechts davon etwas? In welche
Richtung wächst y bei diesem Erzeuger? Daraus ergibt sich die Lesereihenfolge
— Kopf über die ganze Breite, darunter Spalte für Spalte. Ist der Befund
nicht eindeutig, bleibt die Seite, wie sie gesetzt wurde: eine falsch
geteilte Seite wäre schlimmer als eine ungeteilte. Dieselbe Datei läuft im Browser —
`tools/build.py` erzeugt daraus `assets/pdf-text.js` —, und dort ist sie mehr
wert: Was schon im Browser zu Text wird, muss nicht als ganze Datei den
Rechner verlassen. Der Worker behält seinen eigenen Weg für den Fall, dass
der Browser es nicht kann.

Kommt dabei Zeichensalat heraus (Scan, Schrift ohne Zuordnung), geht die
Datei selbst an das Modell. Klappt auch das nicht, sagt der Editor, dass der
Text eingefügt werden soll — und nicht, dass „etwas schiefgelaufen" ist.

Der Testbetrieb in `tools/mock-ki.py` ordnet den gelieferten Text mit
einfachen Regeln: Überschriften an Schlüsselwörtern, Stationen an
Zeiträumen, Kontaktzeilen an @ und Postleitzahl. Er ersetzt kein Modell und
soll es nicht — er zeigt nur, ob das Auslesen der Datei etwas gebracht hat,
und füllt das Layout mit dem eigenen Lebenslauf statt mit einer erfundenen
Musterperson.

## Stellenanzeigen

`/api/stelle` holt die Seite und schneidet Text heraus. Das geht bei vielen
Firmenseiten gut. Große Jobbörsen sperren fremde Zugriffe oder laden die
Anzeige erst per Skript nach; dann kommt eine klare Meldung zurück, und der
Benutzer fügt den Text ein. Das ist Absicht: Diese Seite umgeht keine Sperren.

## Was die Analyse nicht tut

`/api/analyse` bekommt die Befunde mitgeliefert, die der Browser aus den
Datumsangaben **gerechnet** hat: Lücken auf den Monat genau, Überschneidungen,
sehr kurze Stationen, fehlende Enddaten. Das Modell soll sie beurteilen, nicht
suchen — Datumsarithmetik ist die eine Aufgabe, bei der ein Sprachmodell
zuverlässig danebenliegt und Code nie.

Der Rest ist Urteil, und dafür gilt dieselbe Grundregel wie beim Zuschneiden:
Die Analyse darf keine Tatsache über den Bewerber erfinden und ihm keine
vorschlagen. Bei Lücken heißt das ausdrücklich: nie verdecken, nie zurück-
datieren, nie eine Beschäftigung strecken. Der Rat ist, die Lücke in einer
Zeile zu benennen — und dass im deutschsprachigen Raum niemand einem
Arbeitgeber die Einzelheiten einer Krankheit oder einer Trennung schuldet.

## Die Systemprompts

Stehen in `prompts.js` und sind der eigentliche Kern. Wer dort etwas ändert,
ändert, wie ehrlich das Ergebnis ist. Die Grundregel: Das Modell darf
umformulieren, umstellen und gewichten — nie ergänzen. Was der Lebenslauf
nicht hergibt, landet in `luecken` und wird dem Benutzer gezeigt, statt
erfunden zu werden.
