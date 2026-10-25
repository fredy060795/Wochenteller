@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Wochenteller
py -3 -m wochenteller %*
if errorlevel 1 pause
