@echo off
chcp 65001 >nul
title Wochenteller
cd /d "%~dp0"

set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY (
  python --version >nul 2>nul && set "PY=python"
)
if not defined PY (
  echo.
  echo   Python wurde nicht gefunden.
  echo   Bitte Python 3 von https://www.python.org/downloads/ installieren
  echo   und beim Installieren "Add python.exe to PATH" anhaken.
  echo.
  pause
  exit /b 1
)

%PY% server.py
pause
