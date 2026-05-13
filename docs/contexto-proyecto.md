# Contexto del proyecto - Automatizador BI

## Resumen
- Nombre de la app: `ONOFF | Automatizador BI - Resoluciones FE`
- Tipo: app de escritorio Python con `tkinter` + `pandas`
- Objetivo: transformar reportes operativos y generar Excels listos para pegar manualmente en archivos oficiales
- Regla de negocio global: no conectar a SharePoint y no modificar archivos oficiales

## Ruta real del codigo
- Proyecto principal: `Automatizar BI/automatizador_bi`
- Entrada: `main.py`
- UI: `ui.py`
- Procesamiento: `processor.py`
- Pruebas: `tests/`
- Carpetas de salida: `output/` y `logs/`

## Estado actual de modulos (12 mayo 2026)
- Modulo 1 implementado: `Base Resoluciones F.E`
- Modulo 2 implementado: `Cuenta F.E sin emitir`
- Modulo 3 implementado: `Error F.E`
- Modulo 4 implementado: `Plataformas que presentan error F.E`
- Modulo 5 implementado: `Cartera`

## Arquitectura de UI (`ui.py`)
- Clase principal: `AutomatizadorBIApp`
- Configuracion por modulo con dataclass `ModuleConfig`:
  - `tab_text`
  - `header_title`
  - `header_description`
  - `process_fn`
  - `include_alerts_in_summary`
  - `success_message`
- Flujo:
  1. usuario selecciona archivo
  2. pulsa procesar
  3. se lanza `threading.Thread` (no bloquea UI)
  4. resultado o error se comunica con `root.after(...)`
- Botones transversales actuales:
  - `Seleccionar archivo`
  - `Procesar archivo`
  - `Abrir resultado en Excel`

## Arquitectura de procesamiento (`processor.py`)
- Excepciones de usuario:
  - `ProcessingError`
  - `MissingColumnError`
- Resultado estandar:
  - dataclass `ProcessSummary` con `input_path`, `output_path`, `log_path`, `rows_read`, `rows_output`, `alerts_count`
- Funciones de proceso vigentes:
  - `process_file(...)` para modulo 1
  - `process_file_cuenta_fe_sin_emitir(...)` para modulo 2
- Utilidades reutilizables clave:
  - `read_input_file(...)`
  - `_read_delimited_file(...)`
  - `_detect_delimiter(...)`
  - `_normalize_column_name(...)`
  - `_clean_text_column(...)`
  - `_clean_identifier_column(...)`
  - `_build_logger(...)`

## Convenciones de datos
- Lectura soportada: `.csv`, `.txt`, `.xlsx`, `.xlsm`
- Prioridad: operaciones vectorizadas (`pandas`) para >100.000 filas
- Evitar loops fila por fila
- Mantener identificadores largos como texto para no perder informacion en notacion cientifica

## Convenciones de salida
- Modulo 1:
  - `RESULTADO_BASE_RESOLUCIONES_FE_YYYYMMDD_HHMMSS.xlsx`
  - Hojas: `RESOLUCIONES FE` y `ALERTA`
- Modulo 2:
  - `RESULTADO_CUENTA_FE_SIN_EMITIR_YYYYMMDD_HHMMSS.xlsx`
  - Hoja: `CUENTA F.E SIN EMITIR`
- Logs por ejecucion en `logs/` con timestamp

## Convenciones de pruebas
- Framework: `pytest`
- Tests actuales:
  - `tests/test_processor.py` (modulo 1)
  - `tests/test_processor_module2.py` (modulo 2)
  - `tests/test_processor_module3.py` (modulo 3)
  - `tests/test_processor_module4.py` (modulo 4)
  - `tests/test_processor_module5.py` (modulo 5)
- Patron recomendado para nuevos modulos:
  - test de caso feliz
  - test de columnas faltantes con `MissingColumnError`
  - validacion de nombres/orden de columnas de salida

## Guia rapida para futuras solicitudes
1. Mantener arquitectura por modulo (UI + processor).
2. Reutilizar helpers existentes antes de crear nuevos.
3. No romper firmas existentes salvo necesidad fuerte.
4. Si se agrega modulo nuevo, actualizar:
   - `module_configs` en UI
   - proceso dedicado en `processor.py`
   - pruebas dedicadas en `tests/`
5. Conservar mensajes claros para usuario y errores tecnicos en logs.

## Archivos de referencia rapida
- `Automatizar BI/automatizador_bi/ui.py`
- `Automatizar BI/automatizador_bi/processor.py`
- `Automatizar BI/automatizador_bi/tests/test_processor.py`
- `Automatizar BI/automatizador_bi/tests/test_processor_module2.py`
- `Automatizar BI/modulo2.md`
- `Automatizar BI/modulo3.md`
