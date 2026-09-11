@echo off
rem Serve the site locally on Windows, where the command is "py", not "python3".
rem Double-click this file, or run tools\serve.cmd from the repository folder.
rem An optional argument sets the port: tools\serve.cmd 8080

cd /d "%~dp0.."

rem "py --version" can succeed against the Microsoft Store stub without a real
rem interpreter behind it, so actually run something instead.
py -c "import sys" >nul 2>&1
if %errorlevel%==0 (
  py tools\serve.py %*
  goto done
)

python -c "import sys" >nul 2>&1
if %errorlevel%==0 (
  python tools\serve.py %*
  goto done
)

echo.
echo   Python 3 was not found on this machine.
echo.
echo   Install it with either of these:
echo.
echo     winget install Python.Python.3.12
echo     https://www.python.org/downloads/
echo.
echo   During the python.org install, tick "Add python.exe to PATH".
echo   Then close this window, open a new one, and run tools\serve.cmd again.
echo.
pause

:done
