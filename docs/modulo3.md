# Prompt adaptado - Modulo 3 (Error F.E)

Trabaja unicamente en el modulo 3 de la aplicacion existente `ONOFF | Automatizador BI - Resoluciones FE`.

No reconstruyas la app desde cero. No rompas modulo 1 (`Base Resoluciones F.E`) ni modulo 2 (`Cuenta F.E sin emitir`).

## Contexto real del codigo actual
- Proyecto: `Automatizar BI/automatizador_bi`
- UI principal: `ui.py`
- Procesamiento: `processor.py`
- Entrada app: `main.py`
- Pruebas: `tests/test_processor.py` y `tests/test_processor_module2.py`
- Arquitectura UI actual:
  - `ModuleConfig` en `ui.py` con `process_fn` por modulo.
  - Procesamiento en segundo plano con `threading.Thread`.
  - Resumen final y apertura de archivo con `os.startfile`.
- Arquitectura de procesamiento actual:
  - Funciones `process_file(...)` (modulo 1) y `process_file_cuenta_fe_sin_emitir(...)` (modulo 2).
  - `read_input_file(...)` reutilizable para CSV/TXT/XLSX/XLSM.
  - Logging por ejecucion en `logs/`.

## Objetivo del modulo 3
Agregar el flujo completo de `3- Error F.E` para generar un archivo nuevo con base en el resultado del modulo 2, sin conectarse a SharePoint ni modificar archivos oficiales.

## Alcance funcional
1. Agregar modulo 3 real en la UI (dejar de ser tab gris con `AUTOMATIZANDO`).
2. Permitir dos formas de entrada:
   - Boton `Tomar reporte modulo 2` (busca ultimo `RESULTADO_CUENTA_FE_SIN_EMITIR_*.xlsx` en `output/`).
   - Boton `Seleccionar archivo` manual (`.xlsx`, `.xlsm`, `.csv`, `.txt`).
3. Boton `Procesar archivo` usando el archivo activo.
4. Boton `Abrir resultado en Excel` para el ultimo resultado del modulo 3.
5. Mostrar en UI:
   - Archivo seleccionado
   - Origen del archivo (`Tomado automaticamente del modulo 2` / `Seleccionado manualmente`)
   - Estado
   - Resumen final
6. Procesar en segundo plano, sin bloquear UI.

## Cambios esperados en `processor.py`
Implementar funciones nuevas para modulo 3 siguiendo el patron de modulo 1 y 2:
- `process_file_error_fe(...)`
- `transform_error_fe_dataframe(...)`
- `write_error_fe_output_excel(...)`
- Resolver columnas requeridas con aliases dedicados (estilo `_resolve_module2_required_columns`).

Usar `ProcessSummary` existente (sin romper compatibilidad). Si hace falta origen del archivo, manejarlo desde UI o extender con compatibilidad hacia atras.

## Entrada esperada (modulo 3)
El archivo fuente normalmente es la salida de modulo 2 y trae columnas equivalentes a:
- `PLATAFORMA`
- `UNIDAD`
- `ID_VENTA`
- `CONSECUTIVO_FE`
- `FECHA_VENTA`
- `COD_ERROR`
- `DETALLE DEL ERROR`
- `COD_ERROR_TEXTO` (ignorar en salida final)

## Salida esperada (modulo 3)
Generar archivo:
`RESULTADO_ERROR_FE_YYYYMMDD_HHMMSS.xlsx`

En carpeta `output/`, con una sola hoja:
`ERROR F.E`

Columnas finales (orden exacto):
1. PLATAFORMA
2. UNIDAD
3. ID_VENTA
4. CONSECUTIVO
5. FECHA DE VENTA
6. COD_ERROR
7. DETALLE DEL ERROR

## Reglas de transformacion
- `CONSECUTIVO = CONSECUTIVO_FE`
- `FECHA DE VENTA = FECHA_VENTA`
- Excluir `COD_ERROR_TEXTO`

## Limpieza de datos (vectorizada)
- `PLATAFORMA`: trim, remover sufijo `.0` cuando aplique, mantener legible.
- `UNIDAD`: trim.
- `ID_VENTA`: conservar como identificador (evitar notacion cientifica).
- `CONSECUTIVO`: conservar como identificador (evitar notacion cientifica).
- `FECHA DE VENTA`: conservar valor legible sin truncar.
- `COD_ERROR`: conservar como texto.
- `DETALLE DEL ERROR`: conservar texto completo sin recortar.

Reutilizar helpers existentes cuando sea posible (`_clean_text_column`, `_clean_identifier_column`, normalizacion de columnas, etc.).

## Normalizacion y validaciones
No asumir nombres exactos. Permitir variantes por mayusculas/minusculas, espacios, guiones bajos, tildes y puntuacion.

Si falta una columna requerida, lanzar `MissingColumnError` con mensaje claro para usuario, por ejemplo:
`No se pudo encontrar la columna CONSECUTIVO_FE. Revisa que el archivo corresponda al reporte CUENTA F.E SIN EMITIR.`

Si no hay estructura compatible:
`El archivo seleccionado no parece corresponder al resultado del modulo 2.`

Errores tecnicos detallados solo en log.

## Cambios esperados en `ui.py`
1. Agregar `module_3` a `module_configs`:
   - tab: `3- Error F.E`
   - titulo: `Automatizador BI - Error F.E`
   - descripcion: acorde al proceso
   - `process_fn`: nueva funcion `process_file_error_fe`
2. Ajustar construccion de tabs:
   - modulo 1, 2 y 3 activos
   - 4 y 5 siguen en gris (`AUTOMATIZANDO`)
3. Agregar boton `Tomar reporte modulo 2` visible cuando modulo activo sea 3.
4. Gestionar estado/origen de archivo para resumen final.
5. Mensajes esperados:
   - Si no hay archivo y presiona procesar:
     `Primero debes tomar el reporte del modulo 2 o seleccionar un archivo.`
   - Si `Tomar reporte modulo 2` no encuentra archivo:
     `No se encontro un resultado del modulo 2. Genera primero el modulo 2 o selecciona el archivo manualmente.`
   - Si encuentra archivo:
     estado `Reporte del modulo 2 cargado correctamente.`

## Logging modulo 3
Archivo sugerido:
`procesamiento_error_fe_YYYYMMDD_HHMMSS.log`

Registrar:
- Modulo ejecutado: `ERROR F.E`
- Origen del archivo
- Archivo entrada
- Archivo salida
- Filas leidas/procesadas
- Columnas detectadas
- Errores (si aplica)

## Rendimiento
- Soportar +100.000 filas.
- Evitar ciclos fila por fila.
- Priorizar transformaciones vectorizadas.
- Mantener procesamiento en hilo secundario.
- Escritura eficiente con `xlsxwriter` (como modulos actuales).

## Pruebas minimas a agregar
Crear `tests/test_processor_module3.py` con al menos:
1. Caso feliz: genera `ERROR F.E` con columnas exactas y orden correcto.
2. Exclusion de `COD_ERROR_TEXTO`.
3. Limpieza basica de `PLATAFORMA` e identificadores.
4. Falla clara por columna faltante (`MissingColumnError`).

No eliminar ni romper pruebas existentes de modulo 1 y 2.

## Criterios de aceptacion
1. Modulo 3 funcional en UI (no tab gris).
2. Boton `Tomar reporte modulo 2` funcional con busqueda del ultimo archivo.
3. Seleccion manual de archivo funcional.
4. Procesamiento sin bloqueo de interfaz.
5. Excel `RESULTADO_ERROR_FE_*.xlsx` con hoja `ERROR F.E`.
6. Columnas finales exactas y en orden requerido.
7. Resumen final con filas, origen, ruta de salida y ruta de log.
8. Boton `Abrir resultado en Excel` funcional.
9. Logs generados.
10. Modulo 1 y 2 siguen funcionando.
