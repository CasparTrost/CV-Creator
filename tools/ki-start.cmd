@echo off
rem ===================================================================
rem  Startet den KI-Dienst auf diesem Rechner.
rem
rem  Doppelklick genuegt. Das Fenster bleibt offen, solange der Dienst
rem  laeuft — hier stehen auch alle Anfragen und Fehler im Klartext.
rem  Beenden mit Strg+C.
rem ===================================================================
setlocal
cd /d "%~dp0\.."

where node >nul 2>nul
if errorlevel 1 (
  echo.
  echo   Node.js fehlt noch. Das ist ein Programm fuer diesen Rechner,
  echo   kein Teil des Projekts.
  echo.
  echo   Ich oeffne jetzt die Downloadseite. Dort den grossen Knopf
  echo   "LTS" nehmen, die Datei ausfuehren, alles durchklicken —
  echo   und danach dieses Fenster schliessen und neu starten.
  echo.
  pause
  start "" https://nodejs.org/en/download
  exit /b 1
)

if not exist "api\.dev.vars" (
  echo.
  echo   Es fehlt noch der Schluessel von CometAPI.
  echo   Er wird in api\.dev.vars gespeichert und landet nie auf GitHub.
  echo.
  set /p SCHLUESSEL="  Schluessel einfuegen und Enter:  "
  if "%SCHLUESSEL%"=="" (
    echo   Nichts eingegeben — abgebrochen.
    pause
    exit /b 1
  )
  > "api\.dev.vars" echo COMETAPI_KEY=%SCHLUESSEL%
  echo   Gespeichert.
)

echo.
echo   Starte den KI-Dienst. Beim ersten Mal fragt er, ob er "wrangler"
echo   installieren darf — mit y bestaetigen. Das dauert ein, zwei Minuten.
echo.
echo   Wenn "Ready on http://localhost:8787" steht, laeuft er. Dann im
echo   Editor Strg+F5 druecken: der Vermerk "Testbetrieb" verschwindet.
echo.
cd api
call npx wrangler dev
