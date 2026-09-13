@echo off
rem ===================================================================
rem  Startet den KI-Dienst auf diesem Rechner.
rem
rem  Doppelklick genuegt. Das Fenster bleibt offen, solange der Dienst
rem  laeuft - hier stehen auch alle Anfragen und Fehler im Klartext.
rem  Beenden mit Strg+C.
rem
rem  Zwei Fallen stecken in dieser Datei, beide schon einmal getreten:
rem    * Ohne "enabledelayedexpansion" ersetzt Windows %VARIABLE% beim
rem      Einlesen eines Klammerblocks, also bevor "set /p" ueberhaupt
rem      gelaufen ist. Die Eingabe ist dann immer leer. Darum hier
rem      Sprungmarken statt Klammern und !VARIABLE! statt %VARIABLE%.
rem    * Keine Umlaute, keine Gedankenstriche: die Konsole zeigt sonst
rem      Zeichensalat statt der Sonderzeichen.
rem ===================================================================
setlocal enabledelayedexpansion
cd /d "%~dp0\.."

where node >nul 2>nul
if errorlevel 1 goto keinnode

if not exist "api\.dev.vars" goto schluessel
findstr /b /c:"COMETAPI_KEY=" "api\.dev.vars" >nul 2>nul
if errorlevel 1 goto schluessel
goto starten

:keinnode
echo.
echo   Node.js fehlt noch. Das ist ein Programm fuer diesen Rechner,
echo   kein Teil des Projekts.
echo.
echo   Ich oeffne jetzt die Downloadseite. Dort den grossen Knopf "LTS"
echo   nehmen, die Datei ausfuehren, alles durchklicken - und danach
echo   dieses Fenster schliessen und neu starten.
echo.
pause
start "" https://nodejs.org/en/download
exit /b 1

:schluessel
echo.
echo   Es fehlt noch der Schluessel von CometAPI.
echo   Er wird in api\.dev.vars gespeichert und landet nie auf GitHub.
echo.
set "SCHLUESSEL="
set /p "SCHLUESSEL=  Schluessel einfuegen und Enter:  "
if not defined SCHLUESSEL goto leer
> "api\.dev.vars" echo COMETAPI_KEY=!SCHLUESSEL!
echo   Gespeichert in api\.dev.vars
goto starten

:leer
echo.
echo   Es kam nichts an. Einfuegen geht in der Eingabeaufforderung mit
echo   Rechtsklick oder Strg+V, nicht ueber das Kontextmenue "Einfuegen"
echo   in aelteren Fenstern.
echo.
pause
exit /b 1

:starten
echo.
echo   Starte den KI-Dienst. Beim ersten Mal fragt er, ob er "wrangler"
echo   installieren darf - mit y bestaetigen. Das dauert ein, zwei Minuten.
echo.
echo   Wenn "Ready on http://localhost:8787" steht, laeuft er. Dann im
echo   Editor Strg+F5 druecken: der Vermerk "Testbetrieb" verschwindet.
echo.
cd api
call npx wrangler dev
echo.
echo   Der Dienst ist beendet.
pause
