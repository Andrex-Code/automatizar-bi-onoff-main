@echo off
cd /d "%~dp0"

if exist "ONOFF_Automatizador_BI_Fast.exe" (
  start "" "ONOFF_Automatizador_BI_Fast.exe"
  exit /b
)

echo No se encontro el ejecutable rapido de ONOFF en la raiz.
pause
