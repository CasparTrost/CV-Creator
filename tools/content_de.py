# -*- coding: utf-8 -*-
"""Deutsche Fassung der Seiteninhalte.

Keine Übersetzung der englischen Texte, sondern eine eigene Fassung: eine
Bewerbung in Deutschland, Österreich und der Schweiz folgt anderen Regeln
als eine amerikanische, und die Themen, die hier gesucht werden — Foto,
Anschreiben, Arbeitszeugnis, Lücken im Lebenslauf — kommen im englischen
Teil gar nicht vor.
"""

UPDATED = '2026-09-11'

GUIDES = []
EXAMPLES = []


def guide(**kw):
    kw.setdefault('updated', UPDATED)
    GUIDES.append(kw)


def example(**kw):
    kw.setdefault('updated', UPDATED)
    EXAMPLES.append(kw)


# ====================================================================
# Vorlagen: Name bleibt, alles andere auf Deutsch.
# ====================================================================

SPEC_KEYS = {
    'Structure': 'Aufbau',
    'Photo': 'Foto',
    'Header treatment': 'Kopfbereich',
    'Pages': 'Seiten',
    'Export': 'Export',
}

SPEC_VALUES = {
    'Two columns': 'Zweispaltig',
    'Single column': 'Einspaltig',
    'Yes': 'Ja',
    'No': 'Nein',
    'None': 'keiner',
    'Two, second one optional': 'Zwei, die zweite optional',
    'PDF and Word, free': 'PDF und Word, kostenlos',
    'Diagonal colour band': 'Diagonales Farbband',
    'Mirrored diagonal band': 'Gespiegeltes Diagonalband',
    'Diagonal band': 'Diagonalband',
    'Dark diagonal band': 'Dunkles Diagonalband',
    'Dark header block': 'Dunkler Kopfblock',
    'Flat colour band': 'Glattes Farbband',
    'Full-width band': 'Band über die volle Breite',
    'Coloured sidebar': 'Farbige Seitenleiste',
    'Accent rule only': 'Nur eine Akzentlinie',
    'Single rule': 'Eine Linie',
    'Hairlines only': 'Nur Haarlinien',
    'Timeline with markers': 'Zeitstrahl mit Punkten',
    'Ruled frame': 'Linienrahmen',
    'Edge bar': 'Balken am Seitenrand',
}

TEMPLATES = {
    't1': dict(
        name='Aster', tagline='Seitenleiste mit diagonalem Kopf',
        title='Aster — Lebenslauf-Vorlage mit Seitenleiste und diagonalem Kopf',
        description='Aster: Seitenleiste mit diagonalem Kopfbereich. Im Browser ausfüllen '
                    'und kostenlos als PDF herunterladen.',
        body='Eine getönte Spalte links trägt Kontaktdaten und Ausbildung, ein diagonales '
             'Band über dem Kopf Ihren Namen und ein kurzes Profil. Die Diagonale ist der '
             'einzige Schmuck; alles darunter bleibt ruhig.',
        fits=['Sie wollen auffallen, ohne verspielt zu wirken',
              'Ihre Berufserfahrung braucht die volle Seitenbreite',
              'Sie bewerben sich außerhalb streng konservativer Branchen']),
    't2': dict(
        name='Verso', tagline='Seitenleiste rechts',
        title='Verso — Lebenslauf-Vorlage mit Seitenleiste rechts',
        description='Verso: Seitenleiste auf der rechten Seite. Im Browser ausfüllen und '
                    'kostenlos als PDF herunterladen.',
        body='Dieselbe Struktur wie Aster, nur gespiegelt. Der Blick fällt zuerst auf Ihren '
             'Namen und die Berufserfahrung, die Nebenangaben stehen rechts.',
        fits=['Ihre Berufserfahrung soll zuerst gelesen werden',
              'Sie mögen die Seitenleiste, aber nicht links',
              'Das Foto darf oben rechts stehen']),
    't3': dict(
        name='Halden', tagline='Durchgehendes Kopfband',
        title='Halden — Lebenslauf-Vorlage mit durchgehendem Kopfband',
        description='Halden: glattes Kopfband ohne Diagonale, mit Seitenleiste. Kostenlos '
                    'als PDF.',
        body='Ein glattes Farbband über die volle Breite, darunter eine Seitenleiste. Ohne '
             'Diagonale wirkt die Seite sachlicher — die naheliegende Wahl, wenn Sie sich '
             'bei einer Behörde oder einem Konzern bewerben.',
        fits=['Sie wollen Farbe, aber keine Schrägen',
              'Die Bewerbung geht in eine eher konservative Branche',
              'Kenntnisse und Sprachen sollen in die Seitenleiste']),
    't4': dict(
        name='Quill', tagline='Ruhiger Kopf auf Weiß',
        title='Quill — schlichte Lebenslauf-Vorlage auf Weiß',
        description='Quill: ruhiger Kopfbereich auf Weiß, Seitenleiste getönt. Kostenlos '
                    'als PDF.',
        body='Kein Farbband, nur Ihr Name in der Akzentfarbe und eine getönte Seitenleiste. '
             'Die zurückhaltendste der zweispaltigen Vorlagen.',
        fits=['Sie wollen Struktur, aber keine Fläche Farbe',
              'Die Branche liest formale Dokumente',
              'Der Text soll die Arbeit machen']),
    't5': dict(
        name='Onyx', tagline='Dunkler Kopf, diagonal geschnitten',
        title='Onyx — Lebenslauf-Vorlage mit dunklem Kopfbereich',
        description='Onyx: dunkler Kopfbereich mit diagonalem Schnitt. Kostenlos als PDF.',
        body='Wie Aster, aber der Kopfbereich ist tiefdunkel statt farbig. Wirkt auf dem '
             'Bildschirm sehr klar; achten Sie beim Druck darauf, Hintergrundgrafiken '
             'einzuschalten, sonst verschwindet die Fläche.',
        fits=['Sie wollen einen kräftigen ersten Eindruck',
              'Die Bewerbung wird vor allem am Bildschirm gelesen',
              'Ihr Foto steht gut auf dunklem Grund']),
    't6': dict(
        name='Cobalt', tagline='Seitenleiste in der Akzentfarbe',
        title='Cobalt — Lebenslauf-Vorlage mit farbiger Seitenleiste',
        description='Cobalt: durchgehend farbige Seitenleiste, weißer Hauptteil. Kostenlos '
                    'als PDF.',
        body='Die Seitenleiste läuft in der Akzentfarbe über die ganze Höhe, der Kopfbereich '
             'bleibt weiß. Kontaktdaten und Kenntnisse stehen dadurch deutlich abgesetzt.',
        fits=['Ihre Kenntnisse sollen ins Auge fallen',
              'Sie wollen Farbe, aber nicht im Kopfbereich',
              'Sie mögen klare Flächen']),
    't7': dict(
        name='Linden', tagline='Einspaltig mit Farbband',
        title='Linden — einspaltige Lebenslauf-Vorlage mit Farbband',
        description='Linden: eine Spalte, ein Farbband im Kopf. Gut lesbar für '
                    'Bewerbungsportale. Kostenlos als PDF.',
        body='Alles in einer Spalte, oben ein Farbband mit Name und Profil. Weil es nur eine '
             'Leserichtung gibt, kommen automatische Bewerbungssysteme damit am besten '
             'zurecht.',
        fits=['Sie laden über ein Bewerbungsportal hoch',
              'Sie wollen den sichersten Aufbau für automatische Auswertung',
              'Ihr Text ist lang genug für die volle Breite']),
    't8': dict(
        name='Ledger', tagline='Datumsspalte links',
        title='Ledger — tabellarische Lebenslauf-Vorlage mit Datumsspalte',
        description='Ledger: Zeiträume in einer eigenen linken Spalte — die klassische '
                    'tabellarische Form. Kostenlos als PDF.',
        body='Die Zeiträume stehen in einer schmalen Spalte links, die Stationen rechts '
             'daneben. Das ist die Form, die im deutschsprachigen Raum mit „tabellarischer '
             'Lebenslauf“ gemeint ist.',
        fits=['Sie bewerben sich in Deutschland, Österreich oder der Schweiz',
              'Ihr Werdegang hat viele klar datierte Stationen',
              'Die Zeiträume sollen auf einen Blick lesbar sein']),
    't9': dict(
        name='Milestone', tagline='Zeitstrahl über die Seite',
        title='Milestone — Lebenslauf-Vorlage mit Zeitstrahl',
        description='Milestone: Zeitstrahl mit Punkten an jeder Station. Kostenlos als PDF.',
        body='Eine Linie läuft über die Seite, jede Station bekommt einen Punkt. Zeigt einen '
             'geradlinigen Werdegang gut — und einen sprunghaften ebenso deutlich.',
        fits=['Ihr Werdegang baut sichtbar aufeinander auf',
              'Sie wollen die zeitliche Abfolge betonen',
              'Sie haben keine großen Lücken zu erklären']),
    't10': dict(
        name='Slate', tagline='Kräftiger Kopfblock',
        title='Slate — Lebenslauf-Vorlage mit kräftigem Kopfblock',
        description='Slate: großer Kopfblock für Name und Kurzprofil, darunter eine Spalte. '
                    'Kostenlos als PDF.',
        body='Ein großzügiger Kopfblock trägt Namen und Kurzprofil, der Rest läuft einspaltig '
             'darunter. Passend, wenn die ersten drei Zeilen Ihr stärkstes Argument sind.',
        fits=['Ihr Kurzprofil ist das Beste auf der Seite',
              'Sie wollen einspaltig bleiben',
              'Der Lebenslauf darf etwas kürzer sein']),
    't11': dict(
        name='Vesper', tagline='Zentriert, rundes Foto',
        title='Vesper — zentrierte Lebenslauf-Vorlage mit rundem Foto',
        description='Vesper: mittig gesetzter Kopf mit rundem Foto. Kostenlos als PDF.',
        body='Kopfbereich mittig, das Foto rund. Trägt einen kürzeren Lebenslauf besser als '
             'die dichten zweispaltigen Vorlagen, weil die Seite von sich aus Luft hat.',
        fits=['Sie haben noch wenig Berufserfahrung',
              'Sie wollen ein Foto, aber nicht eckig',
              'Die Branche ist offen für eine freundlichere Gestaltung']),
    't12': dict(
        name='Hairline', tagline='Zwei Spalten ohne Flächen',
        title='Hairline — zweispaltige Lebenslauf-Vorlage ohne Farbflächen',
        description='Hairline: zwei Spalten, nur Haarlinien, keine Farbflächen. Kostenlos '
                    'als PDF.',
        body='Zwei Spalten, aber keine einzige gefüllte Fläche — nur feine Linien trennen '
             'die Bereiche. Druckt sauber, auch auf einem schlechten Bürodrucker.',
        fits=['Sie wollen zwei Spalten ohne Farbe',
              'Eine lange Liste an Kenntnissen soll nicht die Erfahrung verdrängen',
              'Die Bewerbung wird ausgedruckt']),
    't13': dict(
        name='Plainfield', tagline='Ohne Foto, ohne Farbflächen',
        title='Plainfield — schlichte Lebenslauf-Vorlage ohne Foto',
        description='Plainfield: einspaltig, kein Foto, keine Farbflächen — der sicherste '
                    'Aufbau für Bewerbungsportale. Kostenlos als PDF.',
        body='Reiner Text in einer Spalte, kein Foto, keine Farbe. Die Vorlage für '
             'anonymisierte Bewerbungen und für alles, was durch ein großes Bewerbungsportal '
             'läuft.',
        fits=['Die Bewerbung läuft über ein Portal, das Sie nicht kennen',
              'Sie bewerben sich international, wo Fotos unüblich sind',
              'Sie wollen jede Fehlerquelle beim Einlesen ausschließen']),
    't14': dict(
        name='Frame', tagline='Kopf im Linienrahmen',
        title='Frame — Lebenslauf-Vorlage mit Linienrahmen im Kopf',
        description='Frame: Kopfbereich in einem Linienrahmen, ruhig und formal. Kostenlos '
                    'als PDF.',
        body='Der Kopfbereich steht in einem gezeichneten Rahmen, der Rest bleibt schlicht. '
             'Wirkt formal, ohne steif zu sein.',
        fits=['Sie bewerben sich im öffentlichen Dienst oder an einer Schule',
              'Sie wollen Form ohne Farbe',
              'Der Lebenslauf soll gedruckt gut aussehen']),
    't15': dict(
        name='Broadsheet', tagline='Breite Seitenleiste',
        title='Broadsheet — Lebenslauf-Vorlage mit breiter Seitenleiste',
        description='Broadsheet: breitere Seitenleiste für lange Listen an Kenntnissen. '
                    'Kostenlos als PDF.',
        body='Die Seitenleiste ist deutlich breiter als üblich und nimmt lange Listen auf, '
             'ohne dass die Zeilen umbrechen. Gut, wenn Sie viele Zertifikate und Sprachen '
             'unterzubringen haben.',
        fits=['Sie haben viele Zertifikate oder Sprachen',
              'Die Seitenleiste soll mehr als Kontaktdaten tragen',
              'Ihre Berufserfahrung ist kompakt beschreibbar']),
    't16': dict(
        name='Margin', tagline='Akzentbalken am Seitenrand',
        title='Margin — Lebenslauf-Vorlage mit Akzentbalken am Rand',
        description='Margin: schmaler Farbbalken am Seitenrand, sonst einspaltig. Kostenlos '
                    'als PDF.',
        body='Ein schmaler Balken in der Akzentfarbe läuft am Rand entlang, der Text bleibt '
             'einspaltig. Die kleinste mögliche Geste, wenn eine reine Textseite Ihnen zu '
             'nackt ist.',
        fits=['Sie wollen einspaltig bleiben, aber nicht ganz schmucklos',
              'Die Bewerbung läuft über ein Portal',
              'Ihr Text soll über die volle Breite laufen']),
}


# ==================================================================== 1
guide(
    slug='lebenslauf-schreiben',
    short='Lebenslauf schreiben',
    h1='Lebenslauf schreiben',
    title='Lebenslauf schreiben: Aufbau, Inhalt und Beispiele',
    description='Was in einen tabellarischen Lebenslauf gehört, in welcher Reihenfolge, '
                'und wie man die Zeilen schreibt, die tatsächlich gelesen werden.',
    dek='Die meisten Ratgeber zum Lebenslauf sind eine Liste von Adjektiven oder eine '
        'Verkaufsseite. Hier steht die ganze Arbeit: was auf die Seite gehört, in welcher '
        'Reihenfolge, und wie man die Zeilen formuliert, an denen entschieden wird.',
    tag='Grundlagen',
    minutes=11,
    related=['lebenslauf-luecken', 'anschreiben', 'bewerbungsfoto'],
    faq=[
        ('Wie lang darf ein Lebenslauf sein?',
         'Eine Seite bis etwa zehn Berufsjahre, danach zwei. Drei Seiten nur in der '
         'Wissenschaft, wo ohnehin andere Regeln gelten. Anderthalb Seiten sind die einzige '
         'Länge, die man vermeiden sollte.'),
        ('Muss ich den Lebenslauf unterschreiben?',
         'Pflicht ist es nicht. Üblich ist es weiterhin, besonders im öffentlichen Dienst und '
         'in traditionellen Unternehmen. Ort, Datum und Unterschrift unten kosten nichts und '
         'fallen negativ auf, wenn sie in einer solchen Branche fehlen.'),
        ('Reicht ein Lebenslauf ohne Anschreiben?',
         'Nur wenn die Stellenanzeige es ausdrücklich so sagt. In Deutschland gehört das '
         'Anschreiben zur vollständigen Bewerbung; es wegzulassen wirkt wie eine '
         'unvollständige Unterlage.'),
    ],
    body='''
<p>Ein Lebenslauf hat eine einzige Aufgabe: dafür zu sorgen, dass ein fremder Mensch neunzig
Sekunden mit Ihnen verbringt statt dreißig. Alles, was dazu nicht beiträgt, belegt Platz, den
eine bessere Zeile gebrauchen könnte.</p>

<h2 id="aufbau">Die Reihenfolge der Seite</h2>
<p>Es gibt eine übliche Reihenfolge, und davon abzuweichen kostet mehr, als es einbringt. Von
oben nach unten:</p>
<ol>
  <li><strong>Persönliche Daten.</strong> Name, Anschrift, Telefonnummer, E-Mail. Geburtsdatum
  und -ort sind optional, Familienstand und Konfession gehören seit dem AGG nicht mehr dazu.</li>
  <li><strong>Kurzprofil,</strong> zwei bis drei Zeilen. Optional, aber nützlich, wenn Ihre
  Berufsbezeichnung nicht offensichtlich zur ausgeschriebenen Stelle passt.</li>
  <li><strong>Berufserfahrung,</strong> die aktuellste Station zuerst.</li>
  <li><strong>Ausbildung,</strong> ebenfalls rückwärts. Nach oben rutscht sie nur, wenn Sie
  gerade fertig geworden sind.</li>
  <li><strong>Kenntnisse:</strong> Sprachen mit Niveau, Software, Zertifikate, Führerschein,
  wenn er zur Stelle gehört.</li>
  <li><strong>Weiterbildung, Ehrenamt, Interessen,</strong> sofern sie etwas aussagen.</li>
  <li><strong>Ort, Datum, Unterschrift.</strong></li>
</ol>
<p>Abschnitte, die ein Leser an der erwarteten Stelle findet, werden gelesen. Abschnitte an
ungewöhnlicher Stelle werden übersprungen, und ein ungewöhnlicher Aufbau wirkt nicht kreativ,
sondern nach Arbeit.</p>

<h2 id="daten">Die persönlichen Daten</h2>
<p>Name, Anschrift, eine Telefonnummer, unter der Sie erreichbar sind, und eine
E-Mail-Adresse, die Ihr Name ist. Eine Adresse aus der Schulzeit muss jemand abtippen, der
sie danach in einem System stehen lässt, in dem andere sie sehen.</p>
<p>Geburtsdatum und Geburtsort sind freiwillig. Viele geben sie weiterhin an, weil ihr Fehlen
in konservativen Häusern als Lücke gelesen wird — Sie dürfen aber darauf verzichten, und
niemand darf danach fragen, um daraufhin auszusortieren. Staatsangehörigkeit nur, wenn sie
für die Arbeitserlaubnis eine Rolle spielt.</p>

<div class="callout">
<strong>Arbeitserlaubnis</strong>
<p>Wenn Ihre Staatsangehörigkeit eine Arbeitserlaubnis voraussetzt oder Sie eine bereits
haben, schreiben Sie eine kurze Zeile dazu zu den persönlichen Daten. Personaler filtern
danach, und wer sie raten lässt, wird aussortiert.</p>
</div>

<h2 id="erfahrung">Berufserfahrung, der Teil, auf den es ankommt</h2>
<p>Jede Station bekommt eine Kopfzeile und zwei bis sechs Stichpunkte. In die Kopfzeile
gehören Zeitraum, Position, Arbeitgeber und Ort. Zeiträume in <strong>Monat/Jahr</strong>,
nicht nur in Jahren — im deutschsprachigen Raum wird eine Lücke eher nachgefragt als
übersehen, und wer nur Jahre angibt, erzeugt genau diese Nachfrage.</p>
<p>Dann die Stichpunkte. Ein Stichpunkt ist keine Aufgabenbeschreibung. Ihre Aufgaben ergeben
sich aus der Position. Ein Stichpunkt ist der Beleg, dass Sie die Arbeit gut gemacht haben,
und dafür braucht er ein Ergebnis.</p>

<div class="compare">
  <div class="bad">
    <h4>Aufgabe</h4>
    <p>Zuständig für den monatlichen Newsletter und die Social-Media-Kanäle.</p>
    <p>Bearbeitung von Kundenbeschwerden und Eskalationen.</p>
  </div>
  <div class="good">
    <h4>Beleg</h4>
    <p>Newsletter von sechs Themen auf eine Geschichte pro Ausgabe umgestellt; Öffnungsrate
    innerhalb von vier Ausgaben von 18 % auf 31 % gestiegen.</p>
    <p>Die zwanzig häufigsten Beschwerden mit Standardantworten hinterlegt und die erste
    Reaktionszeit von zwei Tagen auf vier Stunden gesenkt.</p>
  </div>
</div>

<p>Das Muster dahinter lautet: <em>was Sie getan haben, wie, und was sich dadurch geändert
hat.</em> Zahlen machen die Veränderung sichtbar, sind aber keine Pflicht. „…womit die
Buchhaltung ihre alte Excel-Liste ersetzt hat“ ist ein Ergebnis. „…womit der Freitagstermin
nicht mehr gerissen wurde“ ebenso.</p>
<p>Die zwei stärksten Stichpunkte Ihrer aktuellen Station gehören nach oben. Das ist der
Teil der Seite, der am sichersten gelesen wird.</p>

<h2 id="ausbildung">Ausbildung</h2>
<p>Abschluss, Einrichtung, Zeitraum. Noten werden in Deutschland anders als in Großbritannien
oder den USA erwartet — geben Sie die Abschlussnote an, wenn sie gut ist, und bei der
Abiturnote gilt: solange sie Ihr jüngster Abschluss ist, gehört sie hin, danach nicht mehr.</p>
<p>Wer noch studiert oder gerade fertig ist, rückt diesen Abschnitt über die Berufserfahrung
und darf etwas mehr hineinschreiben: Thema der Abschlussarbeit, relevante Schwerpunkte, ein
Stipendium. Alles andere bleibt draußen.</p>

<h2 id="kenntnisse">Kenntnisse</h2>
<p>Nur nachprüfbare Substantive. Software, Maschinen, Sprachen, Zertifikate, Führerscheine.
Keine Adjektive über sich selbst: teamfähig behauptet jeder, geglaubt wird es niemandem, weil
die Behauptung nichts kostet.</p>
<p>Sprachen mit GER-Niveau angeben (A1 bis C2) statt mit „verhandlungssicher“, das jeder
anders auslegt. Und löschen Sie die Bewertungsbalken: vier von fünf Punkten neben „Excel“
sagen niemandem etwas, weil Ihre vier Punkte und seine vier Punkte nicht dieselben sind.
Schreiben Sie „Excel bis Pivot-Tabellen und Power Query“, und die Zeile enthält eine Aussage.</p>

<h2 id="kurzprofil">Das Kurzprofil oben</h2>
<p>Drei Zeilen, zuletzt geschrieben, auf diese Stelle gerichtet: was Sie sind, wie lange
schon, und wohin Sie wollen.</p>
<p class="pull">„Teamleiter Lager, sechs Jahre, aktuell verantwortlich für eine Nachtschicht
von vierzehn Leuten in einem regionalen Verteilzentrum. Möchte in die Disposition wechseln,
die ich seit zwei Quartalen vertretungsweise mitmache.“</p>
<p>Das ist den Platz wert. „Dynamische, ergebnisorientierte Persönlichkeit mit Leidenschaft
für Exzellenz“ ist es nicht.</p>

<h2 id="form">Form und Länge</h2>
<p>Eine Seite bis etwa zehn Berufsjahre, danach zwei. Schriftgröße 10 oder 11 Punkt, Ränder
mindestens 15 mm, und lassen Sie den Weißraum in Ruhe — er arbeitet. Eine bis an die Ränder
vollgeschriebene Seite sagt, dass Sie sich nicht entscheiden konnten.</p>
<p>Eine Schrift, höchstens zwei. Farbe in kleinen Mengen ist in Ordnung: eine Linie, eine
Überschrift, eine getönte Seitenleiste. Farbe als Dekoration nicht.</p>

<h2 id="anpassen">Anpassen, ohne neu zu schreiben</h2>
<p>Lesen Sie die Stellenanzeige zweimal. Die ersten drei oder vier genannten Anforderungen
sind das, worauf es der Führungskraft wirklich ankommt; der Rest ist die Wunschliste der
Abteilung. Sorgen Sie dafür, dass diese drei oder vier Punkte auf Ihrer ersten Seite
auftauchen — in den Worten der Anzeige.</p>
<p>Wenn dort „Stakeholdermanagement“ steht und bei Ihnen „Zusammenarbeit mit anderen
Abteilungen“, ändern Sie Ihre Zeile. Nicht wegen einer Software, die nach dem Begriff sucht —
diese Geschichte wird überschätzt —, sondern weil der Mensch, der liest, die Anzeige daneben
liegen hat und Zeile für Zeile abgleicht.</p>

<h2 id="letzter-blick">Der letzte Durchgang</h2>
<ul class="checklist">
  <li>Laut lesen. Jeder Satz, über den Sie stolpern, lässt auch einen Fremden stolpern.</li>
  <li>Prüfen, ob die Zeiträume aufgehen und kein Firmenname falsch geschrieben ist — vor allem
  nicht der des Unternehmens, bei dem Sie sich bewerben.</li>
  <li>Die eigene Telefonnummer einmal anrufen.</li>
  <li>Als PDF speichern und <em>Vorname-Nachname-Lebenslauf.pdf</em> nennen, nicht
  <em>lebenslauf_final_v4.pdf</em>.</li>
  <li>Das PDF auf dem Handy öffnen. Ein großer Teil der ersten Blicke passiert dort.</li>
  <li>Jemandem geben, der Ihren Beruf nicht kennt, und fragen, was Sie tun. Wenn die Antwort
  ausbleibt, ist die Seite noch nicht fertig.</li>
</ul>
''',
)

# ==================================================================== 2
guide(
    slug='bewerbungsfoto',
    short='Das Bewerbungsfoto',
    h1='Das Bewerbungsfoto: Pflicht, Kür oder Risiko',
    title='Bewerbungsfoto: Muss es sein, und wie muss es aussehen?',
    description='Ob ein Foto in den Lebenslauf gehört, was das AGG daran ändert, wie ein '
                'brauchbares Bewerbungsfoto aussieht und wann Sie besser darauf verzichten.',
    dek='Kein Unternehmen darf ein Foto verlangen, und die meisten erwarten trotzdem eines. '
        'Wie man mit diesem Widerspruch umgeht, hängt von der Branche ab — und vom Land.',
    tag='DACH-Besonderheiten',
    minutes=7,
    related=['lebenslauf-schreiben', 'bewerbung-usa-uk', 'lebenslauf-luecken'],
    faq=[
        ('Ist ein Bewerbungsfoto Pflicht?',
         'Nein. Seit dem Allgemeinen Gleichbehandlungsgesetz darf kein Arbeitgeber ein Foto '
         'verlangen, und das Fehlen darf kein Ablehnungsgrund sein. Üblich ist es im '
         'deutschsprachigen Raum trotzdem, und die meisten Bewerbungen enthalten eines.'),
        ('Was kostet ein professionelles Bewerbungsfoto?',
         'Zwischen 60 und 200 Euro, je nach Stadt und Umfang. Für eine Bewerbung, die über '
         'ein Gehalt entscheidet, ist das eine der günstigeren Investitionen — vorausgesetzt, '
         'der Fotograf macht regelmäßig Bewerbungsfotos und keine Hochzeiten.'),
        ('Wo im Lebenslauf steht das Foto?',
         'Oben rechts im Kopfbereich, oder auf einem Deckblatt. Beides ist üblich; beides '
         'zusammen ist zu viel.'),
    ],
    body='''
<p>Zwei Dinge sind gleichzeitig wahr. Erstens: Seit 2006 darf kein Arbeitgeber in Deutschland
ein Foto verlangen, und wer wegen eines fehlenden Fotos aussortiert, handelt angreifbar.
Zweitens: In der Praxis enthält die große Mehrheit der Bewerbungen im deutschsprachigen Raum
ein Foto, und Personaler sind daran gewöhnt.</p>
<p>Daraus folgt keine allgemeine Regel, sondern eine Entscheidung, die Sie pro Bewerbung
treffen.</p>

<h2 id="wann">Wann ein Foto sinnvoll ist</h2>
<ul>
  <li>Mittelständische und traditionelle Unternehmen, Handwerk, öffentlicher Dienst.</li>
  <li>Berufe mit Kundenkontakt, in denen ohnehin jeder weiß, wie Sie aussehen.</li>
  <li>Wenn die Stellenanzeige eine „vollständige Bewerbung“ verlangt — gemeint ist das
  gewohnte Paket.</li>
</ul>

<h2 id="wann-nicht">Wann Sie besser verzichten</h2>
<ul>
  <li><strong>Jede Bewerbung ins englischsprachige Ausland.</strong> In den USA, in
  Großbritannien, Irland, Kanada und Australien wird ein Foto teils sofort aussortiert —
  manche Arbeitgeber sehen sich Bewerbungen mit Foto aus Haftungsgründen gar nicht erst an.</li>
  <li><strong>Anonymisierte Bewerbungsverfahren,</strong> die einige Konzerne und Behörden
  inzwischen führen. Dort ist das Foto nicht neutral, sondern ein Formfehler.</li>
  <li><strong>Wenn Sie kein gutes haben.</strong> Ein zugeschnittenes Urlaubsfoto ist
  schlechter als gar keines, und das ist keine Geschmacksfrage.</li>
</ul>

<div class="callout warn">
<strong>Zwei Fassungen, nicht eine</strong>
<p>Wer sich sowohl in München als auch in London bewirbt, braucht zwei Exportstände: einen
mit Foto und Monatsangaben, einen ohne Foto und ohne Geburtsdatum. Im Editor heißt das
schlicht zwei gesicherte Dateien.</p>
</div>

<h2 id="wie">Wie ein brauchbares Foto aussieht</h2>
<p>Es gibt keine Passbild-Vorschrift, und ein Passbild ist auch nicht gemeint. Was zählt:</p>
<ul>
  <li><strong>Aktuell.</strong> Nicht älter als zwei Jahre, und Sie sollten im Vorstellungs­gespräch
  erkennbar dieselbe Person sein.</li>
  <li><strong>Ruhiger Hintergrund.</strong> Einfarbig oder unscharf, nichts, was ablenkt.</li>
  <li><strong>Kleidung wie im Beruf, eine Stufe besser.</strong> Was in Ihrer Branche am
  ersten Arbeitstag angemessen wäre.</li>
  <li><strong>Blick in die Kamera,</strong> freundlich, kein erzwungenes Lächeln. Ein
  Gesichtsausdruck, den Sie tatsächlich haben.</li>
  <li><strong>Ausschnitt von der Brust aufwärts,</strong> Hochformat, genug Auflösung für den
  Druck — mindestens 1.000 Pixel in der Höhe.</li>
</ul>
<p>Selbst gemacht geht, wenn jemand anders auslöst, das Licht vom Fenster kommt und der
Hintergrund ruhig ist. Eine Handy-Selfie-Perspektive dagegen erkennt jeder sofort.</p>

<h2 id="rechtlich">Was rechtlich noch dazugehört</h2>
<p>Das Urheberrecht am Foto liegt beim Fotografen. Lassen Sie sich die Nutzung für
Bewerbungsunterlagen und berufliche Netzwerke schriftlich einräumen — bei
Bewerbungsfotografen ist das der Normalfall, aber es steht nicht immer von selbst im
Vertrag.</p>
<p>Und: Bewerbungsunterlagen mit Foto sind personenbezogene Daten. Unternehmen müssen sie
nach dem Verfahren löschen, üblicherweise nach sechs Monaten. Sie dürfen danach fragen.</p>

<h2 id="deckblatt">Deckblatt: braucht das jemand?</h2>
<p>Ein Deckblatt mit Foto, Name und Stellenbezeichnung war lange üblich und ist es heute nur
noch selten. Es kostet eine Seite und bringt keine Information, die nicht auch in den
Lebenslauf passt. Wenn Sie eines verwenden, dann statt des Fotos im Lebenslauf, nicht
zusätzlich.</p>
''',
)

# ==================================================================== 3
guide(
    slug='anschreiben',
    short='Das Anschreiben',
    h1='Das Anschreiben, in fünf Absätzen',
    title='Anschreiben schreiben: Aufbau, Formulierungen, Beispiel',
    description='Wie ein Anschreiben aufgebaut ist, das gelesen wird: fünf Absätze, ein '
                'Beispiel, und die Einleitungssätze, die Sie streichen sollten.',
    dek='Das Anschreiben ist im deutschsprachigen Raum keine Zugabe, sondern Teil der '
        'Bewerbung. Die meisten sind eine Prosafassung des Lebenslaufs — und werden deshalb '
        'nicht gelesen.',
    tag='Grundlagen',
    minutes=9,
    related=['lebenslauf-schreiben', 'lebenslauf-luecken', 'quereinstieg'],
    faq=[
        ('Wie lang darf ein Anschreiben sein?',
         'Eine Seite, 250 bis 400 Wörter, mit Briefkopf. Kürzer wirkt lustlos, länger wird '
         'nicht gelesen.'),
        ('Was schreibe ich, wenn kein Ansprechpartner genannt ist?',
         '„Sehr geehrte Damen und Herren“ ist korrekt. Besser ist ein Anruf in der '
         'Personalabteilung und ein Name — das dauert fünf Minuten und verändert den ersten '
         'Satz.'),
        ('Gehören Gehaltsvorstellung und Eintrittstermin hinein?',
         'Nur wenn danach gefragt wird. Dann aber beides, im vorletzten Absatz, mit einer '
         'konkreten Zahl statt einer Spanne von zwanzigtausend Euro.'),
    ],
    body='''
<p>Der Lebenslauf sagt, was Sie getan haben. Das Anschreiben beantwortet eine Frage, die er
strukturell nicht beantworten kann: <em>warum diese Stelle, bei diesem Unternehmen,
jetzt?</em> Wenn Ihr Anschreiben das nicht beantwortet, ist es eine schlechtere Fassung eines
Dokuments, das der Leser bereits hat.</p>

<h2 id="form">Die Form</h2>
<p>Ein Geschäftsbrief: Ihre Adresse, die des Unternehmens, Ort und Datum, eine Betreffzeile
ohne das Wort „Betreff“, Anrede, Text, Grußformel, Unterschrift. Dieselbe Schrift und
derselbe Briefkopf wie im Lebenslauf, damit beide als eine Bewerbung erkennbar sind.</p>
<p>Die Betreffzeile nennt die Stelle und, falls vorhanden, die Kennziffer aus der Anzeige.
Sie ist die einzige Zeile, die garantiert gelesen wird.</p>

<h2 id="aufbau">Die fünf Absätze</h2>
<ol>
  <li><strong>Worauf Sie sich bewerben und der eine Grund, warum es passt.</strong> Kein
  Räuspern, kein „hiermit bewerbe ich mich“. Der erste Satz trägt die Passung.</li>
  <li><strong>Ihr bester Beleg,</strong> als kurze Geschichte mit Ergebnis — ein Absatz, kein
  Stichpunkt. Nehmen Sie den, der dem Hauptproblem der Stelle am nächsten kommt.</li>
  <li><strong>Der zweite Beleg,</strong> zu einer anderen Anforderung aus der Anzeige.</li>
  <li><strong>Warum dieses Unternehmen.</strong> Etwas Konkretes und Nachprüfbares: das
  Produkt, der Markt, eine angekündigte Veränderung. Das ist der Absatz, der sich nicht
  wiederverwenden lässt — und der, dessen Fehlen auffällt.</li>
  <li><strong>Ein schlichter Schluss.</strong> Verfügbar ab wann, gerne im Gespräch, danke.
  Eine Zeile. Kein Konjunktiv: „Ich freue mich auf das Gespräch“ statt „würde mich freuen“.</li>
</ol>

<div class="compare">
  <div class="bad">
    <h4>Einleitung, die den Absatz verschenkt</h4>
    <p>Hiermit bewerbe ich mich auf die von Ihnen ausgeschriebene Stelle als
    Einkaufssachbearbeiter. Ich bin überzeugt, dass mein Profil und meine Erfahrung eine
    ideale Ergänzung für Ihr Team darstellen.</p>
  </div>
  <div class="good">
    <h4>Einleitung, die den nächsten Absatz verdient</h4>
    <p>Seit vier Jahren verhandle ich Rahmenverträge für Zukaufteile in einem Werk mit
    2.000 Positionen — Ihre Ausschreibung beschreibt im Wesentlichen diese Arbeit, nur mit
    einem besseren ERP. Zwei Punkte daraus sind mir aufgefallen.</p>
  </div>
</div>

<h2 id="mitte">Ein ausgearbeiteter Mittelteil</h2>
<p class="pull">„In der Anzeige steht die Senkung der Fehlmengen. Als ich die Nachtschicht
übernommen habe, lagen wir bei etwa 4 %. Der größte Teil davon kam aus der Übergabe: Die
Tagschicht hinterließ Notizen auf Papier, und die Hälfte davon las nie jemand. Ich habe die
Übergabe auf eine fünfminütige Kurzbesprechung mit einem Einseiter umgestellt; nach zwei
Monaten lagen wir unter 1,5 % und sind seitdem dort geblieben.“</p>
<p>Dieser Absatz leistet, wofür sonst sechs Stichpunkte nötig wären, weil er ein Problem, eine
Diagnose und ein Ergebnis enthält. Einer davon pro Anschreiben genügt, zwei sind das Maximum.</p>

<h2 id="weglassen">Was Sie weglassen</h2>
<ul>
  <li>Den Lebenslauf in Sätzen. Der Leser hat ihn.</li>
  <li>„Ich bin motiviert, teamfähig und belastbar“ — drei Behauptungen ohne Beleg.</li>
  <li>Dem Unternehmen erklären, was das Unternehmen tut.</li>
  <li>Entschuldigungen für das, was Ihnen fehlt. Eine echte Lücke in einem selbstbewussten
  Nebensatz ansprechen oder gar nicht.</li>
  <li>Was die Stelle für Ihre Entwicklung täte. Das Anschreiben handelt davon, was Sie
  mitbringen.</li>
</ul>

<div class="callout">
<strong>Versand</strong>
<p>Als eigenes PDF, wenn ein Mensch liest; als Teil des Gesamt-PDFs, wenn ein Portal nur eine
Datei nimmt — dann als erstes Dokument, vor dem Lebenslauf. Bei einer E-Mail darf das
Anschreiben im Text stehen, gehört aber trotzdem zusätzlich als Anhang: der Mailtext
überlebt das Weiterleiten ins Bewerbersystem nicht.</p>
</div>
''',
)

# ==================================================================== 4
guide(
    slug='arbeitszeugnis',
    short='Das Arbeitszeugnis',
    h1='Arbeitszeugnis lesen: der Code und was er bedeutet',
    title='Arbeitszeugnis: Geheimcode entschlüsseln und Note bestimmen',
    description='Wie die Formulierungen im qualifizierten Arbeitszeugnis zu lesen sind, '
                'welche Note dahintersteckt und was Sie tun können, wenn sie zu schlecht ist.',
    dek='Ein Arbeitszeugnis muss wohlwollend und wahr zugleich sein. Aus diesem Widerspruch '
        'ist eine Geheimsprache entstanden, die jeder Personaler liest und die kaum ein '
        'Arbeitnehmer geprüft hat.',
    tag='DACH-Besonderheiten',
    minutes=10,
    related=['lebenslauf-schreiben', 'lebenslauf-luecken', 'anschreiben'],
    faq=[
        ('Habe ich Anspruch auf ein qualifiziertes Arbeitszeugnis?',
         'Ja. Nach § 109 Gewerbeordnung können Sie ein Zeugnis verlangen, das sich auf '
         'Leistung und Verhalten erstreckt. Ein einfaches Zeugnis nennt nur Art und Dauer der '
         'Tätigkeit — verlangen Sie ausdrücklich das qualifizierte.'),
        ('Wie lange kann ich ein Zeugnis nachfordern?',
         'Der Anspruch verjährt regelmäßig nach drei Jahren zum Jahresende, kann aber durch '
         'Fristen im Arbeits- oder Tarifvertrag deutlich früher verfallen. Wer es braucht, '
         'sollte es beim Ausscheiden verlangen, nicht Jahre später.'),
        ('Darf ich mein Zeugnis selbst schreiben?',
         'Formal nicht, praktisch häufig: viele Vorgesetzte bitten darum, einen Entwurf zu '
         'bekommen. Das ist Ihre Gelegenheit und keine Zumutung.'),
    ],
    body='''
<p>Ein Arbeitszeugnis darf Ihr berufliches Fortkommen nicht behindern und muss trotzdem der
Wahrheit entsprechen. Weil sich beides oft widerspricht, hat sich eine Sprache herausgebildet,
in der das Negative durch Auslassung gesagt wird. Wer sie nicht kennt, hält ein schlechtes
Zeugnis für ein freundliches.</p>

<h2 id="note">Die Leistungsbeurteilung: der eine Satz, auf den es ankommt</h2>
<p>Am Ende der Leistungsbeschreibung steht die zusammenfassende Beurteilung. Sie enthält eine
Note, verschlüsselt in drei Größen: der Zufriedenheitsgrad, das Zeitwort und ob die
Zufriedenheit „stets“ war.</p>
<div class="scroll-x">
<table class="plain">
  <tr><th>Formulierung</th><th>Note</th></tr>
  <tr><td>…hat die ihm übertragenen Aufgaben <strong>stets zu unserer vollsten
  Zufriedenheit</strong> erledigt</td><td>sehr gut</td></tr>
  <tr><td>…<strong>stets zu unserer vollen Zufriedenheit</strong></td><td>gut</td></tr>
  <tr><td>…<strong>zu unserer vollsten Zufriedenheit</strong> (ohne „stets“)</td><td>gut bis
  befriedigend</td></tr>
  <tr><td>…<strong>zu unserer vollen Zufriedenheit</strong></td><td>befriedigend</td></tr>
  <tr><td>…<strong>zu unserer Zufriedenheit</strong></td><td>ausreichend</td></tr>
  <tr><td>…<strong>im Großen und Ganzen zu unserer Zufriedenheit</strong></td><td>mangelhaft</td></tr>
  <tr><td>…<strong>hat sich bemüht</strong>, die Aufgaben zu erfüllen</td><td>ungenügend</td></tr>
</table>
</div>
<p>„Bemüht“ ist das schärfste Wort der Branche. Es bedeutet: hat es nicht geschafft.</p>

<h2 id="verhalten">Die Verhaltensbeurteilung und die Reihenfolge</h2>
<p>Der zweite Satz betrifft das Verhalten, und hier liegt die Information in der
<em>Reihenfolge</em>. Genannt werden üblicherweise Vorgesetzte, Kollegen und Kunden. Wer
zuerst steht, zu dem war das Verhältnis am besten.</p>
<p>„Sein Verhalten gegenüber Kollegen und Vorgesetzten war stets einwandfrei“ — die
Vorgesetzten an zweiter Stelle — wird als Hinweis auf Reibung mit der Führung gelesen. Fehlen
die Vorgesetzten ganz, ist das eine deutliche Aussage.</p>

<div class="callout warn">
<strong>Was fehlen darf und was nicht</strong>
<p>Ein vollständiges Zeugnis enthält: Einleitung mit Aufgabenbeschreibung, Leistungs­beurteilung,
Verhaltensbeurteilung, Beendigungsgrund und eine Schlussformel mit Dank und Zukunftswünschen.
<strong>Fehlt die Schlussformel,</strong> ist das ein starkes negatives Zeichen — sie ist zwar
nicht einklagbar, aber ihr Fehlen fällt jedem Personaler auf.</p>
</div>

<h2 id="codes">Weitere Formulierungen, die anders gemeint sind</h2>
<div class="scroll-x">
<table class="plain">
  <tr><th>Steht da</th><th>Gemeint ist</th></tr>
  <tr><td>…war gesellig und trug zur Verbesserung des Betriebsklimas bei</td>
      <td>Alkohol, oder zumindest mehr Feiern als Arbeiten</td></tr>
  <tr><td>…zeigte für seine Arbeit Verständnis</td><td>hat nichts zustande gebracht</td></tr>
  <tr><td>…war stets pünktlich</td>
      <td>mehr fiel nicht ein; Pünktlichkeit ist eine Selbstverständlichkeit</td></tr>
  <tr><td>…erledigte alle Aufgaben mit großem Fleiß und Interesse</td>
      <td>Fleiß ohne Erfolg</td></tr>
  <tr><td>…trat engagiert für die Interessen der Belegschaft ein</td>
      <td>war im Betriebsrat aktiv und eckte an</td></tr>
  <tr><td>…verließ uns auf eigenen Wunsch</td>
      <td>neutral — solange nicht „im gegenseitigen Einvernehmen“ dasteht</td></tr>
</table>
</div>
<p>Vorsicht mit Listen dieser Art, im Internet und auch mit dieser: Manche Formulierungen
werden inzwischen unbeabsichtigt verwendet, weil die Verfasser sie selbst aus Vorlagen haben.
Ein einzelner verdächtiger Satz ist ein Hinweis, kein Urteil. Die Gesamtnote und die
Reihenfolge in der Verhaltensbeurteilung sind die verlässlicheren Größen.</p>

<h2 id="korrektur">Wenn das Zeugnis zu schlecht ist</h2>
<p>Sie haben Anspruch auf ein wohlwollendes Zeugnis. Im Streit gilt eine Beweislastverteilung,
die Sie kennen sollten: Bis zur Note „befriedigend“ muss <em>der Arbeitgeber</em> eine
schlechtere Beurteilung beweisen. Wollen Sie dagegen besser als befriedigend beurteilt werden,
müssen <em>Sie</em> die bessere Leistung belegen.</p>
<p>Der praktische Weg ist selten der Anwalt:</p>
<ol>
  <li>Freundlich um Korrektur bitten, mit konkretem Formulierungsvorschlag. Die meisten
  Personalabteilungen ändern, ohne zu diskutieren.</li>
  <li>Einen vollständigen Entwurf mitliefern, wenn die Vorgesetzte ohnehin fragt, was
  hineinsoll. Das ist der Normalfall und Ihre beste Gelegenheit.</li>
  <li>Fristen beachten: Je länger Sie warten, desto schwieriger wird die Änderung praktisch
  und rechtlich.</li>
</ol>

<h2 id="bewerbung">Was davon in die Bewerbung gehört</h2>
<p>Alle Arbeitszeugnisse, eingescannt, hinter den Lebenslauf, chronologisch mit dem jüngsten
zuerst. Dazu Abschlusszeugnisse und relevante Weiterbildungen. Das gesamte Paket als ein PDF
— Anschreiben, Lebenslauf, Zeugnisse — und möglichst unter 5 MB, weil viele
Bewerbungsportale dort abriegeln.</p>
<p>Fehlt ein Zeugnis noch, schreiben Sie „Zwischenzeugnis liegt vor, Endzeugnis folgt“ in die
Bewerbung, statt es kommentarlos wegzulassen.</p>
''',
)

# ==================================================================== 5
guide(
    slug='lebenslauf-luecken',
    short='Lücken im Lebenslauf',
    h1='Lücken im Lebenslauf',
    title='Lücken im Lebenslauf erklären, ohne sich zu verstecken',
    description='Wie man Lücken im Lebenslauf benennt: welche Formulierungen tragen, ab wann '
                'eine Lücke überhaupt eine ist, und warum Verschweigen teurer wird.',
    dek='Eine Lücke ist eine Tatsache. Eine unerklärte Lücke ist eine Frage — und Fragen '
        'beantwortet der Leser sich selbst, meist zu Ihren Ungunsten.',
    tag='Besondere Fälle',
    minutes=7,
    related=['lebenslauf-schreiben', 'quereinstieg', 'anschreiben'],
    faq=[
        ('Ab wann gilt eine Zeit als Lücke?',
         'Ab etwa zwei bis drei Monaten. Kürzere Übergänge zwischen zwei Stellen erklärt '
         'jeder Personaler sich selbst und fragt nicht nach.'),
        ('Darf ich eine Lücke einfach weglassen?',
         'Lücken verschweigen dürfen Sie, falsche Angaben machen nicht. Ein erfundener '
         'Arbeitgeber oder ein gestreckter Zeitraum ist arbeitsrechtlich eine Täuschung und '
         'kann auch Jahre später zur Anfechtung des Arbeitsvertrags führen.'),
        ('Wie gehe ich mit Arbeitslosigkeit um?',
         'Benennen und füllen: „Berufliche Neuorientierung“ mit dem, was Sie in der Zeit '
         'tatsächlich getan haben — Weiterbildung, Zertifikat, Ehrenamt, Pflege eines '
         'Angehörigen.'),
    ],
    body='''
<p>Im deutschsprachigen Raum wird der Lebenslauf monatsgenau gelesen. Wer aus einer
amerikanischen Vorlage nur Jahreszahlen übernimmt, macht damit keine Lücke unsichtbar,
sondern erzeugt den Eindruck, etwas verbergen zu wollen — und der ist teurer als jede Lücke.</p>

<h2 id="wann">Wann eine Lücke eine Lücke ist</h2>
<p>Zwei Monate zwischen zwei Stellen sind eine Kündigungsfrist, keine Lücke. Ab etwa drei
Monaten entsteht eine Frage, ab sechs eine deutliche. Alles darüber hinaus braucht eine
eigene Zeile im Lebenslauf, nicht bloß eine Erklärung im Gespräch.</p>

<h2 id="benennen">Die Zeile, die eine Lücke schließt</h2>
<p>Sie bekommt dieselbe Form wie jede andere Station: Zeitraum links, Bezeichnung rechts, ein
oder zwei Stichpunkte darunter.</p>
<div class="scroll-x">
<table class="plain">
  <tr><th>Situation</th><th>Bezeichnung im Lebenslauf</th></tr>
  <tr><td>Arbeitssuche</td><td>Berufliche Neuorientierung</td></tr>
  <tr><td>Elternzeit</td><td>Elternzeit</td></tr>
  <tr><td>Pflege eines Angehörigen</td><td>Familiäre Pflegezeit</td></tr>
  <tr><td>Längere Krankheit</td><td>Gesundheitsbedingte Auszeit, inzwischen abgeschlossen</td></tr>
  <tr><td>Weiterbildung, Umschulung</td><td>Weiterbildung: [Titel], [Anbieter]</td></tr>
  <tr><td>Auslandsaufenthalt</td><td>Auslandsaufenthalt [Land], Sprachkurs [Niveau]</td></tr>
  <tr><td>Selbstständigkeit ohne Erfolg</td><td>Selbstständige Tätigkeit als [Beruf]</td></tr>
  <tr><td>Sabbatical</td><td>Berufliche Auszeit</td></tr>
</table>
</div>
<p>Bei Krankheit gilt eine Besonderheit: Sie müssen nichts über Ihre Gesundheit offenlegen,
und eine Diagnose gehört nirgendwohin. „Gesundheitsbedingte Auszeit, vollständig
wiederhergestellt“ ist ausreichend — und der Zusatz ist wichtig, weil die offene Frage sonst
die Absage schreibt.</p>

<div class="callout">
<strong>Füllen schlägt erklären</strong>
<p>Eine Lücke, in der etwas passiert ist, ist keine Lücke mehr. Ein Zertifikat, ein
Sprachkurs, ein Ehrenamt mit echter Verantwortung, ein Projekt, das jemand nutzt: ein
einziger datierter Eintrag verwandelt zwölf leere Monate in eine Station. Das gilt auch
rückwirkend — was Sie damals gemacht haben, dürfen Sie heute aufschreiben.</p>
</div>

<h2 id="ehrlich">Wo die Grenze verläuft</h2>
<p>Sie sind nicht verpflichtet, Ihre Lücken zu kommentieren. Sie dürfen kurze Stationen
weglassen, Sie dürfen die Reihenfolge nach Relevanz gewichten, und Sie dürfen eine neutrale
Bezeichnung wählen. Was Sie nicht dürfen: Zeiträume verlängern, Arbeitgeber erfinden oder
Abschlüsse behaupten. Das ist keine Kosmetik mehr, sondern ein Anfechtungsgrund, der noch
Jahre nach der Einstellung wirkt.</p>
<p>Als Faustregel: Jede Zeile Ihres Lebenslaufs sollte eine sein, über die Sie im Gespräch
fünf Minuten ruhig sprechen können.</p>

<h2 id="gespraech">Im Vorstellungsgespräch</h2>
<p>Die Frage kommt, und sie kommt früh. Drei Sätze reichen: was war, was Sie in der Zeit getan
haben, warum es vorbei ist. Dann weitergehen.</p>
<p class="pull">„Nach der Insolvenz meines Arbeitgebers habe ich acht Monate gesucht und in der
Zeit den Staplerschein und die Ausbildereignung gemacht. Seit Januar bin ich wieder in einer
festen Stelle und suche jetzt etwas mit mehr Verantwortung.“</p>
<p>Was nicht funktioniert: Rechtfertigen, den alten Arbeitgeber schlechtmachen, oder die Zeit
kleinreden. Eine sachlich benannte Lücke ist in fünfzehn Sekunden erledigt.</p>
''',
)

# ==================================================================== 6
guide(
    slug='quereinstieg',
    short='Quereinstieg',
    h1='Lebenslauf für den Quereinstieg',
    title='Quereinstieg: Lebenslauf für den Branchenwechsel schreiben',
    description='Wie ein Lebenslauf aussieht, wenn Sie die Branche wechseln: übersetzen '
                'statt weglassen, und warum der funktionale Lebenslauf eine Falle ist.',
    dek='Das Problem beim Quereinstieg ist nicht, dass Ihre Erfahrung nicht passt. Es ist, '
        'dass die Passung Ihnen offensichtlich erscheint und dem Leser unsichtbar bleibt.',
    tag='Besondere Fälle',
    minutes=8,
    related=['lebenslauf-schreiben', 'anschreiben', 'lebenslauf-luecken'],
    faq=[
        ('Soll ich einen funktionalen Lebenslauf verwenden?',
         'Nein. Personaler erkennen die Form sofort und lesen sie als Versuch, etwas zu '
         'verbergen. Außerdem nimmt sie die Zeiträume weg, an denen sich der Leser '
         'orientiert.'),
        ('Muss ich im Lebenslauf begründen, warum ich wechsle?',
         'Eine Zeile im Kurzprofil genügt. Die Begründung gehört ins Anschreiben, wo Platz '
         'dafür ist.'),
        ('Ist ein Quereinstieg mit Gehaltseinbußen verbunden?',
         'Meistens ja, oft eine Stufe. Wer so tut, als gälte das nicht, bewirbt sich auf '
         'Stellen, bei denen niemand zurückruft und niemand erklärt, warum.'),
    ],
    body='''
<p>Sie wissen, warum acht Jahre Gastronomie auf eine Stelle in der Disposition vorbereiten.
Die Person, die liest, hat vierzig Bewerbungen und zwanzig Minuten und wird diese Übersetzung
nicht für Sie leisten. Ein Lebenslauf für den Quereinstieg besteht darin, sie auf der Seite
zu leisten, in den Worten der Zielbranche.</p>

<h2 id="funktional">Zuerst: kein funktionaler Lebenslauf</h2>
<p>Der Rat, die Chronologie aufzugeben und alles nach Fähigkeiten zu gruppieren, ist
verbreitet und falsch. Personaler erkennen die Form in zwei Sekunden, und was sie signalisiert,
ist: <em>hier wird eine Lücke, ein Abstieg oder eine kurze Beschäftigung versteckt.</em>
Danach wird gesucht statt gelesen. Außerdem verschwinden die Zeiträume, an denen sich ein
Leser in den ersten zehn Sekunden orientiert.</p>
<p>Bleiben Sie beim gewohnten tabellarischen, rückwärts geordneten Aufbau. Die Arbeit
passiert woanders.</p>

<h2 id="uebersetzen">Übersetzen, nicht streichen</h2>
<p>In jeder Ihrer bisherigen Stationen steckt Arbeit, die es in der Zielbranche unter einem
anderen Namen gibt. Finden Sie diese Teile und schreiben Sie sie in deren Sprache.</p>
<div class="scroll-x">
<table class="plain">
  <tr><th>Was es war</th><th>Wie es dort heißt</th></tr>
  <tr><td>Schichtleitung in der Gastronomie</td>
      <td>Operatives Tagesgeschäft unter Zeitdruck, Personaleinsatzplanung, Warenwirtschaft</td></tr>
  <tr><td>Unterricht vor dreißig Schülern</td>
      <td>Schulungskonzeption und -durchführung, Wissensvermittlung, Gruppenmoderation</td></tr>
  <tr><td>Pflegedokumentation</td>
      <td>Dokumentation nach regulatorischem Standard, Übergabeprozesse</td></tr>
  <tr><td>Logistik bei der Bundeswehr</td>
      <td>Materialdisposition, Bestandsführung, Berichterstattung an die Leitungsebene</td></tr>
  <tr><td>Filialleitung im Einzelhandel</td>
      <td>Ergebnisverantwortung, Personalgewinnung und Dienstplan, Inventurdifferenzen</td></tr>
</table>
</div>
<p>Das ist keine Schönfärberei, solange die Tatsachen stimmen. „Personaleinsatzplanung“ ist
eine zutreffende Beschreibung dafür, den Dienstplan zu schreiben. Geändert hat sich nur,
welche zutreffende Beschreibung Sie gewählt haben.</p>

<div class="callout warn">
<strong>Wo Übersetzung zur Erfindung wird</strong>
<p>Den Dienstplan „Personaleinsatzplanung“ zu nennen, ist in Ordnung. Sich selbst
„Personalreferent“ zu nennen, nicht. Beschreiben Sie die Arbeit in deren Sprache; verleihen
Sie sich nicht deren Berufsbezeichnung.</p>
</div>

<h2 id="oben">Oben die Brücke bauen</h2>
<p>Das obere Drittel muss die Passung herstellen, bevor die Berufsbezeichnungen dagegen
sprechen. Drei Elemente in dieser Reihenfolge:</p>
<ol>
  <li><strong>Ein Kurzprofil,</strong> das den Wechsel ausdrücklich benennt. Nicht
  entschuldigend, sondern sachlich: „Restaurantleiter, wechselt in die Disposition“ sagt dem
  Leser, wie er alles Folgende lesen soll.</li>
  <li><strong>Ein Kenntnisblock direkt darunter,</strong> gewichtet auf die Zielbranche: die
  Software, das Zertifikat, die Weiterbildung vom letzten Frühjahr.</li>
  <li><strong>Dann die Berufserfahrung</strong> wie gewohnt, mit den übersetzten
  Stichpunkten.</li>
</ol>

<h2 id="beleg">Ein aktueller Beleg schließt die Lücke</h2>
<p>Das Stärkste auf einem Quereinsteiger-Lebenslauf ist meist ein Nachweis aus der neuen
Branche mit <em>diesjährigem Datum</em>: ein Zertifikat, eine IHK-Weiterbildung, ein Kurs mit
Prüfung, ein Projekt, das jemand benutzt. Ein einziger konkreter Punkt schlägt jede Menge
erklärter Begeisterung, weil er zeigt, dass die Entscheidung schon läuft.</p>
<p>Geben Sie ihm Platz: ein kurzer Abschnitt <em>Weiterbildung</em> oder <em>Relevante
Projekte</em> über der Berufserfahrung ist mehr wert als der fünfte Stichpunkt einer Stelle,
die Sie verlassen.</p>

<h2 id="alt">Die alte Laufbahn kürzen, ohne sie zu verstecken</h2>
<p>Alle Stationen bleiben, alle Zeiträume bleiben, aber das Gewicht verschiebt sich. Die
letzte Station der alten Branche bekommt zwei bis drei übersetzte Stichpunkte. Ältere
Stationen bekommen eine Zeile: Position, Arbeitgeber, Zeitraum. Was mehr als zehn Jahre
zurückliegt, fasst eine gemeinsame Zeile zusammen.</p>
<p>Sie verbergen nichts. Sie verwenden Ihre Seite auf den Teil, der für die nächste Stelle
spricht.</p>
''',
)

# ==================================================================== 7
guide(
    slug='bewerbung-usa-uk',
    short='Bewerbung im Ausland',
    h1='Bewerbung in den USA und Großbritannien: was anders ist',
    title='Resume statt Lebenslauf: Bewerbung in den USA und UK',
    description='Was eine deutsche Bewerbung im englischsprachigen Ausland untauglich macht: '
                'Foto, Geburtsdatum, Anschreiben, Zeugnisse — und was stattdessen zählt.',
    dek='Eine deutsche Bewerbung enthält drei Dinge, die im englischsprachigen Raum von '
        'harmlos bis schädlich reichen — und lässt eines weg, das dort entscheidet.',
    tag='DACH-Besonderheiten',
    minutes=8,
    related=['bewerbungsfoto', 'lebenslauf-schreiben', 'anschreiben'],
    faq=[
        ('Darf ich mein Bewerbungsfoto im Ausland verwenden?',
         'Besser nicht. In den USA, Großbritannien, Irland, Kanada und Australien sortieren '
         'manche Arbeitgeber Bewerbungen mit Foto aus, um Diskriminierungsvorwürfen '
         'vorzubeugen. Das Foto hilft dort nie und schadet manchmal.'),
        ('Was ist der Unterschied zwischen Resume und CV?',
         'In den USA ist ein Resume die ein- bis zweiseitige Bewerbungsunterlage und ein CV '
         'das lange akademische Dokument. In Großbritannien heißt dieselbe zweiseitige '
         'Unterlage CV. Gemeint ist in beiden Fällen dasselbe.'),
        ('Muss ich meine deutschen Zeugnisse übersetzen?',
         'Mitschicken sollten Sie sie gar nicht. Gefragt sind Referenzpersonen, keine '
         'Zeugnisse. Die Abschlussnote können Sie im Lebenslauf umrechnen und in einer '
         'Klammer erklären.'),
    ],
    body='''
<p>Eine gute deutsche Bewerbung ist im englischsprachigen Raum keine schlechte Bewerbung —
sie ist eine fremde. Die Unterschiede sind klein in der Zahl und groß in der Wirkung.</p>

<h2 id="unterschiede">Die Gegenüberstellung</h2>
<div class="scroll-x">
<table class="plain">
  <tr><th></th><th>Deutschland, Österreich, Schweiz</th><th>USA, UK, Irland, Kanada</th></tr>
  <tr><td>Foto</td><td>üblich</td><td>weglassen; kann zum Aussortieren führen</td></tr>
  <tr><td>Geburtsdatum</td><td>häufig</td><td>nie</td></tr>
  <tr><td>Familienstand, Nationalität</td><td>gelegentlich</td><td>nie</td></tr>
  <tr><td>Unterschrift</td><td>üblich</td><td>keine</td></tr>
  <tr><td>Anschreiben</td><td>Pflichtbestandteil</td><td>oft optional, aber nützlich</td></tr>
  <tr><td>Zeugnisse</td><td>eingescannt beigefügt</td><td>keine; stattdessen Referenzpersonen</td></tr>
  <tr><td>Zeiträume</td><td>Monat/Jahr, lückenlos</td><td>Jahre genügen häufig</td></tr>
  <tr><td>Länge</td><td>ein bis zwei Seiten plus Anlagen</td><td>eine Seite unter zehn
  Berufsjahren</td></tr>
  <tr><td>Ergebnisse</td><td>zunehmend erwartet</td><td>zwingend; ohne Zahlen wirkt es leer</td></tr>
</table>
</div>

<h2 id="ergebnisse">Der eigentliche Unterschied: Ergebnisse</h2>
<p>Der deutsche Lebenslauf beschreibt traditionell Zuständigkeiten, der amerikanische Erfolge.
Wer seine Stichpunkte eins zu eins übersetzt, klingt auf Englisch nach jemandem, der anwesend
war.</p>
<div class="compare">
  <div class="bad">
    <h4>Übersetzte Zuständigkeit</h4>
    <p>Responsible for the monthly reporting and the coordination of external service
    providers.</p>
  </div>
  <div class="good">
    <h4>Amerikanisch geschrieben</h4>
    <p>Rebuilt monthly reporting into a single dashboard used by three plant directors;
    cut preparation from two days to two hours.</p>
  </div>
</div>
<p>Das Muster ist dasselbe wie im deutschen Lebenslauf, nur wird es dort strenger erwartet:
Verb, was Sie getan haben, was sich geändert hat.</p>

<h2 id="noten">Noten und Abschlüsse umrechnen</h2>
<p>Eine deutsche 1,7 versteht in Manchester niemand — sie sieht nach einer schlechten Note
aus, weil dort höhere Zahlen besser sind. Schreiben Sie die Note und die Einordnung
zusammen: „Grade 1.7 (German scale, where 1.0 is best; roughly equivalent to a UK 2:1)“.</p>
<p>Bei Abschlüssen den deutschen Titel behalten und erklären: „Ausbildung als
Industriekaufmann (three-year dual vocational training, apprenticeship plus vocational
school)“. Das duale System ist im Ausland unbekannt und wird ohne Erläuterung als „kein
Studium“ gelesen, obwohl es ein Berufsabschluss ist.</p>

<div class="callout">
<strong>Referenzen statt Zeugnisse</strong>
<p>Statt Arbeitszeugnissen erwartet man dort zwei bis drei Personen, die man anrufen kann —
frühere Vorgesetzte, mit Name, Position und Kontakt. Fragen Sie vorher, ob Sie sie nennen
dürfen. Auf den Lebenslauf gehören sie nicht; „References available on request“ ist
überflüssig, weil das ohnehin jeder weiß.</p>
</div>

<h2 id="arbeitserlaubnis">Arbeitserlaubnis: die Frage, die zuerst gestellt wird</h2>
<p>Für ein britisches oder amerikanisches Unternehmen ist die erste Frage bei einer Bewerbung
aus Deutschland, ob es Sie überhaupt einstellen darf. Beantworten Sie sie ungefragt, in einer
Zeile unter Ihren Kontaktdaten: ob Sie ein Visum benötigen, ob Sie eines haben, ob Sie einen
irischen oder anderen EU-Pass besitzen, der in Irland sofort gilt.</p>
<p>Wer das offen lässt, wird aussortiert, ohne es zu erfahren — es ist der billigste Filter,
den eine Personalabteilung hat.</p>

<h2 id="zwei">Zwei Fassungen pflegen</h2>
<p>Es gibt keine Datei, die in beiden Märkten funktioniert. Behalten Sie zwei: eine deutsche
mit Foto, Monatsangaben und Unterschrift, eine englische ohne Foto, ohne Geburtsdatum, mit
Ergebnissen in jedem Stichpunkt. Im Editor sind das zwei gesicherte Dateien mit demselben
Inhalt und unterschiedlicher Bestückung — und die englischen Ratgeber auf dieser Seite sind
für die zweite geschrieben.</p>
''',
)

# ==================================================================== 8
guide(
    slug='bewerbung-per-email',
    short='Bewerbung per E-Mail',
    h1='Die Bewerbung per E-Mail',
    title='Bewerbung per E-Mail: Betreff, Text, Anhang, Dateigröße',
    description='Wie eine Bewerbungs-E-Mail aussieht, die ankommt: Betreffzeile, kurzer '
                'Text, ein PDF unter 5 MB, richtig benannt.',
    dek='Die E-Mail ist der erste Eindruck, nicht der Lebenslauf. Sie entscheidet, ob der '
        'Anhang überhaupt geöffnet wird — und ob er im Spam landet.',
    tag='Grundlagen',
    minutes=6,
    related=['anschreiben', 'lebenslauf-schreiben', 'arbeitszeugnis'],
    faq=[
        ('Gehört das Anschreiben in die E-Mail oder in den Anhang?',
         'In beides. Ein kurzer Text in der Mail, das vollständige Anschreiben im PDF. Der '
         'Mailtext überlebt das Weiterleiten ins Bewerbersystem nicht.'),
        ('Wie groß darf die Bewerbung als Datei sein?',
         'Unter 5 MB, besser unter 3. Viele Mailserver und Bewerbungsportale riegeln dort ab, '
         'und eine abgewiesene Mail bekommen Sie nicht immer zurückgemeldet.'),
        ('Ein PDF oder mehrere?',
         'Ein einziges, in der Reihenfolge Anschreiben, Lebenslauf, Zeugnisse. Wer fünf '
         'Anhänge schickt, überlässt dem Empfänger das Sortieren.'),
    ],
    body='''
<p>Die Bewerbungsmappe aus Papier ist weitgehend verschwunden, das Verfahren dahinter nicht:
Es wird weiterhin ein vollständiges Paket erwartet, nur eben als eine Datei an einer
E-Mail.</p>

<h2 id="betreff">Die Betreffzeile</h2>
<p>Sie ist die einzige Zeile, die garantiert gelesen wird, und sie entscheidet über das
Ablegen in den richtigen Ordner:</p>
<p class="pull">Bewerbung als Industriemechaniker, Kennziffer 2026-114 — Jonas Wieland</p>
<p>Stelle, Kennziffer aus der Anzeige, Ihr Name. Nicht „Bewerbung“ allein, nicht „Meine
Unterlagen“, und auf keinen Fall ein leerer Betreff — der landet zuverlässig im Spam.</p>

<h2 id="text">Der Mailtext</h2>
<p>Fünf bis acht Zeilen. Er ersetzt das Anschreiben nicht, er kündigt es an.</p>
<div class="sample">
<p class="line">Sehr geehrte Frau Kessler,</p>
<p class="line">auf Ihre Ausschreibung als Industriemechaniker (Kennziffer 2026-114) bewerbe
ich mich gerne. Ich arbeite seit fünf Jahren in der Instandhaltung einer Serienfertigung und
habe dort zuletzt die Umstellung auf vorbeugende Wartung mit begleitet.</p>
<p class="line">Anschreiben, Lebenslauf und meine Zeugnisse finden Sie im Anhang. Für
Rückfragen erreichen Sie mich jederzeit unter 0170 1234567.</p>
<p class="line">Mit freundlichen Grüßen<br>Jonas Wieland</p>
</div>
<p>Eine Signatur mit Telefonnummer darunter. Keine Grafiken, keine Zitate, kein bunter
Hintergrund.</p>

<h2 id="anhang">Der Anhang</h2>
<ul class="checklist">
  <li><strong>Ein PDF</strong>, in der Reihenfolge Anschreiben, Lebenslauf, Zeugnisse.</li>
  <li><strong>Unter 5 MB.</strong> Scans in 150 dpi statt 600 reichen völlig; das ist meist
  der ganze Unterschied.</li>
  <li><strong>Sinnvoll benannt:</strong> <code>Bewerbung-Jonas-Wieland-Industriemechaniker.pdf</code>.
  In einem Ordner mit zweihundert Dateien ist das die, die man wiederfindet.</li>
  <li><strong>Kein ZIP</strong>, keine Cloud-Links, keine Word-Datei, sofern nicht ausdrücklich
  verlangt.</li>
  <li><strong>Textbasiert, nicht als Bild.</strong> Öffnen, alles markieren, kopieren, in einen
  Texteditor einfügen: Kommt Ihr Name als Text heraus, kann die Software der Personalabteilung
  ihn lesen.</li>
</ul>

<div class="callout warn">
<strong>Vor dem Senden</strong>
<p>Schicken Sie die fertige Mail einmal an sich selbst und öffnen Sie sie auf dem Handy. Sie
sehen in dreißig Sekunden, ob der Anhang ankommt, wie groß er ist, ob die Signatur zerfällt —
und ob Sie den Firmennamen im Anschreiben ausgetauscht haben.</p>
</div>

<h2 id="absender">Absenderadresse und Zeitpunkt</h2>
<p>Eine Adresse aus Vor- und Nachnamen, bei einem gängigen Anbieter. Spitznamen und
Geburtsjahre aus der Schulzeit sind der billigste vermeidbare Punktabzug, den es gibt.</p>
<p>Der Versandzeitpunkt spielt eine kleinere Rolle, als Ratgeber behaupten — aber eine Mail,
die dienstags um zehn eintrifft, steht oben im Posteingang, und eine von Sonntag drei Uhr
morgens steht unter dreißig anderen.</p>

<h2 id="nachfassen">Nachfassen</h2>
<p>Nach zwei Wochen ohne Antwort ist ein kurzer Anruf oder eine dreizeilige Mail üblich und
gern gesehen, sofern die Anzeige nichts anderes sagt. Einmal, freundlich, mit dem Angebot,
Unterlagen nachzureichen. Ein zweites Nachfassen bringt nichts mehr.</p>
''',
)


# ====================================================================
# Muster nach Beruf
# ====================================================================

example(
    slug='pflegefachkraft',
    role='Pflegefachkraft',
    field='Gesundheit',
    title='Lebenslauf Muster: Pflegefachkraft',
    description='Muster-Lebenslauf für Pflegefachkräfte, mit der Begründung: was die '
                'Pflegedienstleitung zuerst prüft und welche Zeilen zählen.',
    dek='Ein Pflege-Lebenslauf wird auf Fakten gelesen, bevor er auf Formulierungen gelesen '
        'wird: Anerkennung, Fachbereich, Versorgungsschlüssel, Weiterbildungen.',
    minutes=6,
    scans=[
        'Die Berufsanerkennung und, bei ausländischem Abschluss, deren Status.',
        'Der Fachbereich: Intensiv, Innere, Chirurgie, ambulant, stationäre Altenpflege. '
        'Das sind verschiedene Berufe.',
        'Betreuungsschlüssel und Stationsgröße — sie sagen mehr über Ihre Woche als jedes '
        'Adjektiv.',
        'Aktuelle Pflichtfortbildungen und Fachweiterbildungen mit Jahr.',
        'Ob Sie schon angeleitet, eingearbeitet oder eine Schicht geführt haben.',
    ],
    sample={
        'name': 'Marie Schuster',
        'headline': 'Pflegefachkraft · 90402 Nürnberg · m.schuster@example.de · '
                    '0170 1234567',
        'summary': 'Pflegefachkraft, sieben Jahre, Innere Medizin und Pneumologie. Derzeit '
                   'Schichtleitung auf einer Station mit 28 Betten, Praxisanleiterin seit '
                   '2023. Suche eine Stelle mit Leitungsanteil im Raum Nürnberg.',
        'jobs': [
            {'title': 'Pflegefachkraft, Schichtleitung', 'employer': 'Klinikum Nordstadt, '
                                                                     'Nürnberg',
             'dates': '09/2021 – heute',
             'bullets': [
                 'Station Pneumologie, 28 Betten, Betreuungsschlüssel 1:7 im Frühdienst, '
                 'einschließlich NIV und Trachealkanülenversorgung.',
                 'Schichtleitung zwei- bis dreimal wöchentlich: Einteilung, Eskalation, '
                 'Ansprechpartnerin für den ärztlichen Dienst.',
                 'Praxisanleiterin für zwei Auszubildende pro Kurs, beide Jahrgänge '
                 'vollständig durch die praktische Prüfung gebracht.',
                 'Entlassungscheckliste gemeinsam mit der Apotheke überarbeitet, nachdem '
                 'Entlassungen regelmäßig an der Medikation hingen; Entlasszeitpunkt von '
                 'nachmittags auf vormittags verschoben.',
                 'Hygienebeauftragte der Station, monatliche Begehungen und Rückmeldung in '
                 'der Teamsitzung.',
             ]},
            {'title': 'Gesundheits- und Krankenpflegerin', 'employer': 'Sana Klinik Fürth',
             'dates': '08/2019 – 08/2021',
             'bullets': [
                 'Innere Medizin, Aufnahmestation, Patienten aus Notaufnahme und '
                 'Einweisung.',
                 'Zusatzqualifikationen Blutentnahme und periphere Venenverweilkanüle '
                 'erworben.',
             ]},
        ],
        'skills': 'NIV, Trachealkanülenmanagement, Portversorgung, Schmerzpumpen. '
                  'Praxisanleitung (2023), Basale Stimulation (2022), aktuelle '
                  'Pflichtfortbildungen. Dokumentation: ORBIS, Medico. '
                  'Deutsch (Muttersprache), Englisch (B2).',
        'education': 'Examen Gesundheits- und Krankenpflege, Berufsfachschule am Klinikum '
                     'Nürnberg, 2019',
    },
    pairs=[
        ('Betreuung und Versorgung von Patienten auf einer internistischen Station.',
         'Station Pneumologie, 28 Betten, Betreuungsschlüssel 1:7 im Frühdienst, '
         'einschließlich NIV und Trachealkanülenversorgung.'),
        ('Mitwirkung an der Verbesserung von Stationsabläufen.',
         'Entlassungscheckliste gemeinsam mit der Apotheke überarbeitet; Entlasszeitpunkt '
         'von nachmittags auf vormittags verschoben.'),
    ],
    templates=[('t8', 'Ledger stellt die Zeiträume in eine eigene Spalte — die tabellarische '
                      'Form, die in Kliniken erwartet wird.'),
               ('t7', 'Linden bleibt einspaltig und hat Platz für die lange Liste an '
                      'Fortbildungen.')],
    guides=['lebenslauf-schreiben', 'arbeitszeugnis', 'lebenslauf-luecken'],
    faq=[
        ('Wohin mit der Berufsanerkennung bei ausländischem Abschluss?',
         'Direkt zu den persönlichen Daten, mit Status und Datum: „Anerkennung als '
         'Pflegefachkraft, Regierung von Mittelfranken, 03/2024“. Das ist die erste Frage '
         'der Pflegedienstleitung, und eine offene Frage kostet den Termin.'),
        ('Soll ich alle Pflichtfortbildungen einzeln aufführen?',
         'Nur die aktuellen, in einer Zeile zusammengefasst. Die vollständige Übersicht '
         'gehört in die Mappe fürs Gespräch, nicht auf die Seite.'),
    ],
)

example(
    slug='bueromanagement',
    role='Kauffrau für Büromanagement',
    field='Büro',
    title='Lebenslauf Muster: Kauffrau für Büromanagement',
    description='Muster-Lebenslauf für Büromanagement und Assistenz, mit der Begründung: '
                'welche Systeme zählen und wie man unsichtbare Arbeit sichtbar macht.',
    dek='Verwaltungsarbeit wird daran gemessen, was aufgehört hat schiefzugehen — die Art '
        'von Erfolg, die am schwersten aufzuschreiben ist.',
    minutes=6,
    scans=[
        'Welche Systeme, und wie tief. Outlook und Word werden vorausgesetzt, das ERP und '
        'die Buchhaltungssoftware nicht.',
        'Wen Sie unterstützt haben und wie viele.',
        'Ob Sie ein Budget verantwortet haben, und sei es ein kleines.',
        'Wie komplex Termine und Reisen waren: wie viele Kalender, wie viele Länder.',
        'Verschwiegenheit, gezeigt an dem, was man Ihnen anvertraut hat.',
    ],
    sample={
        'name': 'Nadine Bergmann',
        'headline': 'Kauffrau für Büromanagement · 04109 Leipzig · '
                    'n.bergmann@example.de · 0151 9876543',
        'summary': 'Kauffrau für Büromanagement, sechs Jahre, zuletzt Büroleitung für einen '
                   'Standort mit 45 Mitarbeitenden und Assistenz der Geschäftsführung. '
                   'Verantwortlich für Lieferantenbudget und Dienstleisterverträge. Suche '
                   'eine Assistenz- oder Office-Management-Stelle.',
        'jobs': [
            {'title': 'Büroleitung und Assistenz der Geschäftsführung',
             'employer': 'Nordvik Consulting GmbH, Leipzig', 'dates': '04/2022 – heute',
             'bullets': [
                 'Büroorganisation für 45 Mitarbeitende: Gebäude, Dienstleister, Onboarding, '
                 'Arbeitssicherheit und ein Sachkostenbudget von 90.000 € im Jahr.',
                 'Assistenz für drei Geschäftsführer — Termine, Auslandsreisen, '
                 'Sitzungsunterlagen und die Reisekostenabrechnungen, die ohne zweimaliges '
                 'Nachfragen nicht eingehen.',
                 'Reinigungs-, Kaffee- und Druckverträge zur Verlängerung neu verhandelt, '
                 '14.000 € im Jahr gespart bei gleicher Leistung.',
                 'Einarbeitung als Wochenplan mit IT und Personalabteilung neu aufgesetzt; '
                 'neue Kolleginnen haben seither am ersten Tag Zugänge und Ausstattung.',
                 'Alleinige Betreuung der Dokumentation für die ISO-9001-Audits 2024 und '
                 '2025, beide ohne Abweichung bestanden.',
             ]},
            {'title': 'Teamassistentin', 'employer': 'Bergmann & Co KG, Halle',
             'dates': '08/2019 – 03/2022',
             'bullets': [
                 'Assistenz für zwölf Beraterinnen und Berater: Termine, Reisen, '
                 'Rechnungsstellung, Korrespondenz.',
                 'Rechnungsstellung nach dem Weggang der Buchhaltungskraft fünf Monate '
                 'allein weitergeführt.',
             ]},
        ],
        'skills': 'Microsoft 365 inklusive Excel bis Pivot und Power Query, SharePoint, '
                  'DATEV, Lexware, Concur. ISO-9001-Dokumentation. '
                  'Deutsch (Muttersprache), Englisch (C1), Französisch (A2).',
        'education': 'Ausbildung zur Kauffrau für Büromanagement, IHK Leipzig, 2019',
    },
    pairs=[
        ('Unterstützung der Geschäftsführung und des Teams im Tagesgeschäft.',
         'Assistenz für drei Geschäftsführer — Termine, Auslandsreisen, Sitzungsunterlagen '
         'und die Reisekostenabrechnungen, die ohne zweimaliges Nachfragen nicht eingehen.'),
        ('Zuständig für Bestellwesen und Lieferantenbetreuung.',
         'Reinigungs-, Kaffee- und Druckverträge zur Verlängerung neu verhandelt, 14.000 € '
         'im Jahr gespart bei gleicher Leistung.'),
    ],
    templates=[('t4', 'Quill wirkt aufgeräumt und lässt der Seitenleiste Platz für Systeme '
                      'und Sprachen.'),
               ('t13', 'Plainfield, wenn die Bewerbung über ein großes Portal läuft.')],
    guides=['lebenslauf-schreiben', 'bewerbung-per-email', 'anschreiben'],
    faq=[
        ('Meine Arbeit fällt nur auf, wenn sie schiefgeht. Wie schreibe ich das?',
         'Schreiben Sie die Folge auf. „Neue Kolleginnen haben seither am ersten Tag Zugänge '
         'und Ausstattung“ beschreibt Arbeit, die niemand bemerkt, so, dass jeder sie '
         'versteht.'),
        ('Gehört „MS Office“ in die Kenntnisse?',
         'Nur mit Substanz dahinter. „Excel bis Pivot-Tabellen und Power Query“ ist eine '
         'Aussage; „MS Office“ allein legt nahe, dass es erwähnenswert war.'),
    ],
)

example(
    slug='softwareentwickler',
    role='Softwareentwickler',
    field='IT',
    title='Lebenslauf Muster: Softwareentwickler',
    description='Muster-Lebenslauf für Softwareentwicklerinnen und -entwickler: Stack, '
                'Produktivbetrieb und Verantwortung statt Technologieliste.',
    dek='Entwickler-Lebensläufe werden von Entwicklern gelesen. Die überfliegen den Stack '
        'und suchen dann den Beleg, dass Sie etwas an echte Nutzer ausgeliefert haben.',
    minutes=6,
    scans=[
        'Der Stack, in den ersten zehn Sekunden: Sprachen, Frameworks, Datenbank.',
        'Ob Sie etwas im Produktivbetrieb betrieben oder nur gebaut haben.',
        'Größenordnung, in der Einheit Ihres Felds: Requests, Nutzer, Datensätze, Deployments.',
        'Was Sie verantwortet haben statt woran Sie beteiligt waren.',
        'Hinweise darauf, dass Sie mit anderen arbeiten können — das ist der größere Teil '
        'der Arbeit.',
    ],
    sample={
        'name': 'Jonas Feldmann',
        'headline': 'Backend-Entwickler · 10115 Berlin · jonas.feldmann@example.de · '
                    'github.com/beispiel',
        'summary': 'Backend-Entwickler, fünf Jahre, überwiegend Java und PostgreSQL in '
                   'Systemen, die Geld bewegen. Verantworte den Zahlungsdienst bei einem '
                   'Logistikunternehmen mit 40 Mitarbeitenden. Suche eine Stelle, in der '
                   'Korrektheit vor Auslieferungsgeschwindigkeit geht.',
        'jobs': [
            {'title': 'Backend-Entwickler', 'employer': 'Cargolane GmbH, Berlin',
             'dates': '03/2022 – heute',
             'bullets': [
                 'Verantworte den Zahlungsdienst: Java 21, Spring Boot, PostgreSQL, rund '
                 '40.000 Transaktionen am Tag in sechs Währungen.',
                 'Abgleich der Auszahlungen nach einem Vorfall mit doppelten Buchungen '
                 'idempotent neu gebaut; seit zwei Jahren kein Wiederholungsfall, und die '
                 'Buchhaltung prüft nicht mehr manuell nach.',
                 'p95-Latenz der Angebotsschnittstelle von 1,9 s auf 220 ms gesenkt, indem '
                 'drei aufeinanderfolgende Aufrufe durch eine materialisierte Sicht ersetzt '
                 'wurden.',
                 'Vertragstests zwischen unserem Dienst und den Speditionsanbindungen '
                 'eingeführt, womit eine ganze Fehlerklasse vom Produktivsystem in die '
                 'Build-Pipeline gewandert ist.',
                 'Zwei Werkstudenten durch ihre erste Rufbereitschaft begleitet.',
             ]},
            {'title': 'Softwareentwickler', 'employer': 'Studio Nord GmbH, Hamburg',
             'dates': '09/2020 – 02/2022',
             'bullets': [
                 'Vier Kundenprojekte von der ersten Zeile bis zur Übergabe, Java und '
                 'Spring.',
                 'Deployments von manuellem SSH auf GitLab CI umgestellt; ein Release dauert '
                 'seither elf Minuten statt eines Nachmittags.',
             ]},
        ],
        'skills': 'Java (Spring Boot), SQL und PostgreSQL inklusive Ausführungsplänen, '
                  'Docker, GitLab CI, AWS (ECS, RDS, S3), Terraform-Grundlagen. '
                  'Lesekenntnisse in Go. Deutsch (Muttersprache), Englisch (C1).',
        'education': 'B.Sc. Informatik, TU Berlin, 2020',
    },
    pairs=[
        ('Mitarbeit am Zahlungssystem mit Java und PostgreSQL.',
         'Verantworte den Zahlungsdienst: Java 21, Spring Boot, PostgreSQL, rund 40.000 '
         'Transaktionen am Tag in sechs Währungen.'),
        ('Verbesserung der Performance der Schnittstelle.',
         'p95-Latenz der Angebotsschnittstelle von 1,9 s auf 220 ms gesenkt, indem drei '
         'aufeinanderfolgende Aufrufe durch eine materialisierte Sicht ersetzt wurden.'),
    ],
    templates=[('t13', 'Plainfield ist einspaltig und schmucklos — genau das, was '
                       'Bewerbungsportale am zuverlässigsten einlesen.'),
               ('t12', 'Hairline gibt zwei Spalten ohne Farbflächen, damit eine lange '
                       'Technologieliste nicht die Berufserfahrung verdrängt.')],
    guides=['lebenslauf-schreiben', 'bewerbung-usa-uk', 'bewerbung-per-email'],
    faq=[
        ('Soll ich jede Technologie aufführen, die ich einmal benutzt habe?',
         'Nein. Aufführen, was Sie im Gespräch verteidigen können. Eine Liste mit vierzig '
         'Einträgen liest sich als Liste von Dingen, die einmal ausprobiert wurden.'),
        ('Gehören private Projekte in den Lebenslauf?',
         'Ein bis zwei, wenn es sie wirklich gibt und der Link funktioniert. Ein verwaistes '
         'Repository ist weniger wert als gar keines, sobald jemand hineinsieht.'),
    ],
)

example(
    slug='lagerlogistik',
    role='Fachkraft für Lagerlogistik',
    field='Gewerblich',
    title='Lebenslauf Muster: Fachkraft für Lagerlogistik',
    description='Muster-Lebenslauf für Lager und Logistik: Scheine mit Gültigkeit, '
                'Lagersystem und Durchsatz — die drei Dinge, die zuerst geprüft werden.',
    dek='Im Lager wird schnell und praktisch eingestellt. Scheine, Systeme und Zahlen '
        'entscheiden; ein Absatz über Belastbarkeit nicht.',
    minutes=5,
    scans=[
        'Scheine und deren Gültigkeit: Gabelstapler, Schubmaststapler, Ameise, Kran, '
        'Führerschein CE.',
        'Das Lagerverwaltungssystem. SAP EWM, Körber, Manhattan, hauseigen — welches?',
        'Durchsatz: Picks pro Stunde, Positionen pro Schicht, Paletten, Versandschluss.',
        'Erfahrung mit Schichtmodellen, einschließlich Nachtschicht.',
        'Ob Sie ein Team geführt haben, und wie groß.',
    ],
    sample={
        'name': 'Ercan Yilmaz',
        'headline': 'Fachkraft für Lagerlogistik · 47059 Duisburg · '
                    'e.yilmaz@example.de · 0160 5554433',
        'summary': 'Fachkraft für Lagerlogistik, sechs Jahre Kontraktlogistik, seit zwei '
                   'Jahren Schichtführer einer Nachtschicht mit vierzehn Personen. Stapler- '
                   'und Schubmastschein, täglich SAP EWM. Suche eine Stelle als '
                   'Schichtleiter.',
        'jobs': [
            {'title': 'Schichtführer Nachtschicht',
             'employer': 'Rhein Fulfilment GmbH, Duisburg', 'dates': '05/2022 – heute',
             'bullets': [
                 'Führung einer Schicht aus vierzehn Kommissionierern und zwei '
                 'Staplerfahrern, 4.000 bis 6.000 Positionen pro Nacht, Versandschluss 05:00 '
                 'Uhr.',
                 'Fehlkommissionierungen innerhalb von zwei Monaten von rund 4 % auf unter '
                 '1,5 % gesenkt, indem die Papierübergabe durch eine fünfminütige '
                 'Kurzbesprechung mit Einseiter ersetzt wurde.',
                 'Personaleinsatz gegen den Wellenplan disponiert und Eskalation an den '
                 'Schichtleiter, wenn die Mengenprognose nicht stimmt — etwa einmal pro '
                 'Woche.',
                 'Neun neue Kolleginnen und Kollegen am System und am Kommissionierprozess '
                 'eingearbeitet; sieben sind weiterhin im Betrieb.',
                 'Drei Jahre ohne meldepflichtigen Unfall in der Schicht; wöchentliche '
                 'Regal- und Gerätekontrolle.',
             ]},
            {'title': 'Staplerfahrer und Kommissionierer',
             'employer': 'Hansa Lager GmbH, Krefeld', 'dates': '02/2019 – 04/2022',
             'bullets': [
                 'Frontstapler und Schubmaststapler, Wareneingang und Einlagerung, rund 120 '
                 'Paletten pro Schicht.',
                 'Vertretung des Wareneingangsleiters während der Urlaubszeiten im letzten '
                 'Jahr.',
             ]},
        ],
        'skills': 'Gabelstapler (gültig bis 2027), Schubmaststapler (bis 2027), '
                  'Mitgängerflurförderzeug. SAP EWM, Zebra-Handscanner. Ausbildereignung '
                  '(2024), Brandschutzhelfer, Ladungssicherung. '
                  'Türkisch (Muttersprache), Deutsch (C1), Englisch (A2).',
        'education': 'Ausbildung zur Fachkraft für Lagerlogistik, IHK Duisburg, 2019',
    },
    pairs=[
        ('Mitarbeit in einem großen Lager im Bereich Kommissionierung und Versand.',
         'Führung einer Schicht aus vierzehn Kommissionierern und zwei Staplerfahrern, '
         '4.000 bis 6.000 Positionen pro Nacht, Versandschluss 05:00 Uhr.'),
        ('Mitwirkung bei der Reduzierung von Fehlern.',
         'Fehlkommissionierungen innerhalb von zwei Monaten von rund 4 % auf unter 1,5 % '
         'gesenkt, indem die Papierübergabe durch eine Kurzbesprechung ersetzt wurde.'),
    ],
    templates=[('t13', 'Plainfield ist reiner Text in einer Spalte — was die meisten '
                       'Bewerbungsportale der Industrie am besten verarbeiten.'),
               ('t7', 'Linden fügt ein einziges Farbband hinzu, falls die Seite Ihnen sonst '
                      'zu nackt ist.')],
    guides=['lebenslauf-schreiben', 'lebenslauf-luecken', 'bewerbung-per-email'],
    faq=[
        ('Muss die Gültigkeit der Scheine dabeistehen?',
         'Ja. Ein abgelaufener Staplerschein ist der Unterschied zwischen Montag anfangen und '
         'in sechs Wochen anfangen, und der Schichtleiter will das vorher wissen.'),
        ('Wie zeige ich mehrere Zeitarbeitseinsätze?',
         'Zusammenfassen: „Einsätze über Randstad und Adecco, 2019 – 2021: drei '
         'Lagerprojekte, längstes 14 Monate bei …“. Sechs kurze Einträge wirken unstet, eine '
         'zusammengefasste Zeile ist ehrlich und liest sich ruhig.'),
    ],
)
