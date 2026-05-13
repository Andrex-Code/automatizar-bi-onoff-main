# Automatizador BI - Resoluciones FE

Aplicacion de escritorio en Python para transformar el reporte de seguimiento FE TryTiendas y generar un Excel de salida con dos hojas:

- `RESOLUCIONES FE`
- `ALERTA`

## Caracteristicas

- Soporta archivos de entrada `.csv`, `.txt`, `.xlsx`, `.xlsm`.
- Detecta separador automaticamente (`;`, `,`, tab).
- Normaliza nombres de columnas con variaciones.
- Procesa archivos grandes usando operaciones vectorizadas de pandas.
- Ejecuta el procesamiento en segundo plano para no bloquear la interfaz.
- Genera log por ejecucion en la carpeta `logs/`.

## Estructura

```text
automatizador_bi/
  main.py
  processor.py
  ui.py
  requirements.txt
  README.md
  logs/
  Resultados/
  tests/
```

## Instalacion

1. Abrir terminal en la carpeta `automatizador_bi`.
2. Crear entorno virtual:

```bash
python -m venv .venv
```

3. Activar entorno virtual (PowerShell):

```bash
.\.venv\Scripts\Activate.ps1
```

4. Instalar dependencias:

```bash
pip install -r requirements.txt
```

## Ejecutar en desarrollo

```bash
python main.py
```

## Ejecutar pruebas

```bash
pytest -q
```

## Salida

Se genera un archivo con nombre:

`RESULTADO_BASE_RESOLUCIONES_FE_YYYYMMDD_HHMMSS.xlsx`

en la carpeta `Resultados/`.

## Empaquetar como EXE (PyInstaller)

Instalar pyinstaller:

```bash
pip install pyinstaller
```

Comando sugerido:

```bash
pyinstaller --onefile --windowed main.py
```

## Nota tecnica de rendimiento

Se uso `pandas` por su buen equilibrio entre rendimiento y simplicidad para operaciones vectorizadas sobre archivos de mas de 100.000 filas. La carga y transformacion se hace por columnas, evitando ciclos fila por fila.
