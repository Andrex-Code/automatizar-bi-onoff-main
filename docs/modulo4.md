# Prompt adaptado - Modulo 4 (Plataformas que presentan error F.E)

Trabaja unicamente en el modulo 4 de la aplicacion existente `ONOFF | Automatizador BI - Resoluciones FE`.

No reconstruyas la app desde cero. No rompas los modulos ya implementados:
- `1- Base Resoluciones F.E`
- `2- Cuenta F.E sin emitir`
- `3- Error F.E`

## Contexto real del proyecto
- Proyecto: `Automatizar BI/automatizador_bi`
- Entrada: `main.py`
- UI: `ui.py`
- Procesamiento: `processor.py`
- Tests actuales:
  - `tests/test_processor.py` (modulo 1)
  - `tests/test_processor_module2.py` (modulo 2)
  - `tests/test_processor_module3.py` (modulo 3)
- Carpetas estandar: `output/` y `logs/`

La app ya usa:
- `ModuleConfig` por modulo en UI
- procesamiento en hilo (`threading.Thread`) para no congelar interfaz
- `ProcessSummary` y `ProcessingError` en `processor.py`
- lectura de `.csv`, `.txt`, `.xlsx`, `.xlsm` con `read_input_file(...)`

## Objetivo del modulo 4
Generar una lista unica de plataformas que presentan error F.E cruzando dos entradas:
1. `CUENTA F.E SIN EMITIR` (manual o tomado del modulo 2)
2. `TOTAL PLATAFORMAS F.E` (manual)

Sin conectarse a SharePoint y sin modificar archivos oficiales.

## Alcance funcional en UI
Agregar el modulo `4- Plataformas que presentan error F.E` como modulo activo (ya no en gris).

Debe tener:
1. Boton `Tomar reporte modulo 2`
2. Boton `Seleccionar Cuenta F.E sin emitir`
3. Boton `Seleccionar Total Plataformas F.E`
4. Boton `Procesar archivo`
5. Boton `Abrir resultado en Excel`

Debe mostrar:
- Archivo Cuenta F.E seleccionado
- Origen Cuenta F.E (`Tomado automaticamente del modulo 2` o `Seleccionado manualmente`)
- Archivo Total Plataformas F.E seleccionado
- Estado del procesamiento
- Resumen final

## Comportamiento clave de UI
### Tomar reporte modulo 2
Buscar en `output/` el ultimo archivo `RESULTADO_CUENTA_FE_SIN_EMITIR_*.xlsx` por fecha de modificacion.

Si existe:
- asignarlo como archivo Cuenta F.E
- origen: `Tomado automaticamente del modulo 2`
- estado: `Reporte del modulo 2 cargado correctamente.`

Si no existe:
- mostrar mensaje claro:
  `No se encontro un resultado del modulo 2. Genera primero el modulo 2 o selecciona el archivo manualmente.`

### Seleccionar Cuenta F.E sin emitir
Permitir `.xlsx`, `.xlsm`, `.csv`, `.txt`.

Al seleccionar:
- guardar ruta
- origen: `Seleccionado manualmente`
- estado: `Archivo Cuenta F.E sin emitir cargado correctamente.`

### Seleccionar Total Plataformas F.E
Permitir `.xlsx`, `.xlsm`, `.csv`, `.txt`.

Al seleccionar:
- guardar ruta
- estado: `Archivo Total Plataformas F.E cargado correctamente.`

### Procesar archivo
Validar antes:
- existe archivo Cuenta F.E
- existe archivo Total Plataformas

Mensajes:
- falta Cuenta F.E:
  `Primero debes tomar el reporte del modulo 2 o seleccionar el archivo CUENTA F.E SIN EMITIR.`
- falta Total Plataformas:
  `Primero debes seleccionar el archivo TOTAL PLATAFORMAS F.E.`

## Cambios esperados en `processor.py`
Agregar funciones nuevas para modulo 4 siguiendo patron de modulos anteriores:
- `process_file_plataformas_error_fe(...)`
- `transform_plataformas_error_fe(...)` (o equivalente)
- `write_plataformas_error_fe_output_excel(...)`
- resolver columnas requeridas por aliases para ambos archivos

### Entradas del proceso
- archivo A: Cuenta F.E sin emitir
- archivo B: Total Plataformas F.E
- `output_dir`, `logs_dir`, `status_callback`
- origen de Cuenta F.E (para log y resumen)

### Logica de cruce
1. Leer ambos archivos con `read_input_file(...)`
2. Detectar columna equivalente a `PLATAFORMA` en ambos
3. Limpiar plataformas en ambos lados con misma regla
4. Eliminar vacios
5. Obtener listas unicas
6. Interseccion entre ambas listas
7. Eliminar duplicados
8. Ordenar ascendente cuando sea posible
9. Generar salida con una sola columna

### Limpieza de plataforma
Aplicar de forma vectorizada (sin loops fila por fila):
- trim espacios
- remover prefijo `c` / `C` al inicio
- remover sufijo decimal `.0` cuando aplique
- preservar como texto
- evitar notacion cientifica
- excluir vacios/NaN

No transformar incorrectamente cadenas tipo `70,355` en numero distinto.

### Aliases de columna esperados
En ambos archivos permitir equivalentes de `PLATAFORMA`, por ejemplo:
- `PLATAFORMA`, `Plataforma`, `plataforma`
- `idPartner`, `ID_PARTNER`, `id partner`
- para Total Plataformas tambien: `TC`, `Tienda`

Reutilizar `_normalize_column_name(...)` y `_find_matching_column(...)`.

## Salida esperada
Archivo:
`RESULTADO_PLATAFORMAS_ERROR_FE_YYYYMMDD_HHMMSS.xlsx`

Ubicacion:
`output/`

Hoja unica:
`PLATAFORMAS ERROR F.E`

Columna unica (encabezado exacto):
`PLATAFORMAS QUE PRESENTAN ERROR F.E`

Solo valores (sin formulas).

## Resumen final esperado
Mostrar en UI, minimo:
- Total plataformas en Cuenta F.E sin emitir
- Total plataformas unicas en Cuenta F.E sin emitir
- Total plataformas en Total Plataformas F.E
- Total plataformas con error encontradas
- Origen Cuenta F.E
- Ruta del archivo generado
- Ruta del log

Mensaje final:
`Ya puedes abrir el archivo resultado, copiar la lista desde la fila 2 y pegarla en el archivo oficial PLATAFORMAS QUE PRESENTAN ERROR F.E.`

## Logging
Crear log por ejecucion con nombre sugerido:
`procesamiento_plataformas_error_fe_YYYYMMDD_HHMMSS.log`

Incluir:
- modulo ejecutado
- archivo Cuenta F.E
- origen Cuenta F.E
- archivo Total Plataformas
- columnas detectadas en ambos
- filas leidas en ambos
- plataformas unicas en ambos
- total coincidencias finales
- archivo generado
- errores tecnicos

## Validaciones y errores de usuario
Mensajes claros (sin traza tecnica):
- `No se pudo encontrar la columna PLATAFORMA en CUENTA F.E SIN EMITIR.`
- `No se pudo encontrar la columna PLATAFORMA en TOTAL PLATAFORMAS F.E.`
- `No se encontraron plataformas con error que coincidan entre CUENTA F.E SIN EMITIR y TOTAL PLATAFORMAS F.E. Revisa que los archivos correspondan al dia correcto.`

Detalles tecnicos solo en log.

## Rendimiento
- Soportar archivos de mas de 100.000 filas
- usar operaciones vectorizadas
- usar `isin`, `merge` o sets eficientes para interseccion
- sin loops fila por fila
- mantener procesamiento en segundo plano

## Compatibilidad con arquitectura actual
- mantener modulos 1, 2 y 3 sin regresiones
- reutilizar helpers de `processor.py`
- mantener estilo visual y flujo actual de `ui.py`
- no cambiar nombres globales sin necesidad

## Pruebas minimas a agregar
Crear `tests/test_processor_module4.py` con al menos:
1. caso feliz con interseccion correcta
2. deduplicacion de plataformas
3. limpieza de `c70355` / `70355.0` / espacios
4. error por columna faltante en Cuenta
5. error por columna faltante en Total
6. comportamiento cuando no hay coincidencias

No eliminar ni romper pruebas existentes.

## Criterios de aceptacion
1. Modulo 4 activo en UI (no tab gris)
2. Botones requeridos disponibles
3. Carga de Cuenta F.E desde modulo 2 funcional
4. Seleccion manual de ambos archivos funcional
5. Validaciones claras antes de procesar
6. Cruce correcto y sin duplicados
7. Excel de salida con hoja y encabezado exactos
8. Solo valores, sin formulas
9. Resumen final completo
10. Logs generados
11. Boton abrir resultado funcional
12. M1, M2 y M3 siguen funcionando
