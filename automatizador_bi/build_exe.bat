@echo off
setlocal

set "PYTHON_CMD="

if exist "%~dp0.venv\Scripts\python.exe" (
  set "PYTHON_CMD=%~dp0.venv\Scripts\python.exe"
)
if not defined PYTHON_CMD (
  py -3 -c "import sys" >nul 2>&1
  if not errorlevel 1 set "PYTHON_CMD=py -3"
)
if not defined PYTHON_CMD (
  python -c "import sys" >nul 2>&1
  if not errorlevel 1 set "PYTHON_CMD=python"
)

if not defined PYTHON_CMD (
  echo Error: no se encontro un interprete Python valido.
  echo Crea un .venv o instala Python con el launcher "py".
  exit /b 1
)

cd /d "%~dp0"

echo Comando Python: %PYTHON_CMD%
%PYTHON_CMD% -c "import sys; print('Python exe:', sys.executable)"
%PYTHON_CMD% -c "import _socket, _ssl, _multiprocessing; print('OK runtime modules:', _socket.__file__)"
if errorlevel 1 (
  echo Error: este Python no tiene modulos binarios stdlib completos.
  exit /b 1
)

%PYTHON_CMD% -m PyInstaller --noconfirm --clean "ONOFF_Automatizador_BI_Fast.spec"
if errorlevel 1 (
  echo Error: fallo la construccion del ejecutable.
  exit /b 1
)

set ROOT_DIR=%~dp0..
set DIST_DIR=%~dp0dist\ONOFF_Automatizador_BI_Fast
set SOCKET_PYD=%DIST_DIR%\_internal\_socket.pyd
if not exist "%SOCKET_PYD%" (
  echo Error: build invalido, no se genero _socket.pyd en _internal.
  exit /b 1
)

copy /Y "%DIST_DIR%\ONOFF_Automatizador_BI_Fast.exe" "%ROOT_DIR%\ONOFF_Automatizador_BI_Fast.exe" >nul
if exist "%ROOT_DIR%\_internal" rmdir /S /Q "%ROOT_DIR%\_internal"
robocopy "%DIST_DIR%\_internal" "%ROOT_DIR%\_internal" /E /R:1 /W:1 /NFL /NDL >nul
if errorlevel 8 (
  echo Error: fallo la copia de la carpeta _internal.
  exit /b 1
)

echo.
echo Build finalizado.
echo Ejecutable rapido: %ROOT_DIR%\ONOFF_Automatizador_BI_Fast.exe
endlocal
