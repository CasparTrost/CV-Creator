@echo off
REM ======================================================================
REM  Neueste Fassung holen.
REM
REM  Warum es dieses Skript gibt: assets\pdf-text.js und die gebauten
REM  Seiten sind erzeugte Dateien. Sobald hier einmal "py tools\build.py"
REM  gelaufen ist, koennen sie sich von der Fassung im Git unterscheiden,
REM  und "git pull" bricht dann ab ("local changes would be overwritten").
REM  Diese Aenderungen sind nichts wert -- sie entstehen beim naechsten
REM  Bauen wieder. Also: wegwerfen, holen, fertig.
REM ======================================================================
setlocal
cd /d "%~dp0.."

git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 goto keingit

git status --porcelain > "%TEMP%\ps-stand.txt"
for %%A in ("%TEMP%\ps-stand.txt") do if %%~zA EQU 0 goto holen

echo Diese Dateien sind hier geaendert:
echo.
type "%TEMP%\ps-stand.txt"
echo.
echo Sie werden verworfen. Eigene Aenderungen waeren danach weg.
set /p JA=Weiter? (j = ja, alles andere bricht ab): 
if /i not "%JA%"=="j" goto abbruch
git checkout -- .

:holen
echo.
git pull
if errorlevel 1 goto schief
echo.
echo Fertig. Im Browser bitte einmal Strg+F5 druecken.
goto ende

:schief
echo.
echo Das Holen hat nicht geklappt. Bitte die Meldung oben lesen.
goto ende

:keingit
echo Dieser Ordner ist kein Git-Arbeitsordner.
goto ende

:abbruch
echo Abgebrochen. Es wurde nichts geaendert.

:ende
del "%TEMP%\ps-stand.txt" >nul 2>&1
echo.
pause
