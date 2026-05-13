# Prompt adaptado - Modulo 5 (Cartera)

Trabaja unicamente en el modulo 5 de la aplicacion existente `ONOFF | Automatizador BI - Resoluciones FE`.

No reconstruyas la app desde cero. No rompas los modulos ya implementados:
- `1- Base Resoluciones F.E`
- `2- Cuenta F.E sin emitir`
- `3- Error F.E`
- `4- Plataformas que presentan error F.E`

## Contexto real del proyecto
- Proyecto: `Automatizar BI/automatizador_bi`
- Entrada: `main.py`
- UI: `ui.py`
- Procesamiento: `processor.py`
- Tests actuales:
  - `tests/test_processor.py` (modulo 1)
  - `tests/test_processor_module2.py` (modulo 2)
  - `tests/test_processor_module3.py` (modulo 3)
  - `tests/test_processor_module4.py` (modulo 4)
- Carpeta de salida: `output/`
- Carpeta de logs: `logs/`

La app ya usa:
- `ModuleConfig` por modulo en UI
- procesamiento en hilo (`threading.Thread`) para no bloquear interfaz
- `ProcessSummary`, `ProcessingError`, `MissingColumnError`
- lectura de `.csv`, `.txt`, `.xlsx`, `.xlsm`

## Objetivo del modulo 5
Procesar el archivo de Cartera descargado (principalmente hoja `FACTURACION`) y generar un archivo resultado con dos hojas:
1. `CARTERA`
2. `PAGO PENDIENTE`

Sin conectarse a SharePoint y sin modificar el archivo oficial de BI.

## Alcance funcional en UI
Activar el modulo `5- Cartera` (ya no en gris).

Botones requeridos:
1. `Seleccionar archivo de Cartera`
2. `Procesar archivo`
3. `Abrir resultado en Excel`

Mostrar en pantalla:
- Archivo de Cartera seleccionado
- Estado del procesamiento
- Resumen final

Mensajes:
- al seleccionar archivo: `Archivo de Cartera cargado correctamente.`
- si falta archivo al procesar: `Primero debes seleccionar el archivo de Cartera.`

## Cambios esperados en `processor.py`
Agregar funciones nuevas siguiendo patron de modulos anteriores:
- `process_file_cartera(...)`
- `read_cartera_input(...)` (si se requiere lectura especializada de hoja)
- `transform_cartera_dataframe(...)`
- `build_pago_pendiente_sheet(...)`
- `write_cartera_output_excel(...)`

## Lectura del archivo de entrada
- Soportar `.xlsx`, `.xlsm`, `.csv`, `.txt`.
- Si es Excel:
  - buscar hoja `FACTURACION` o equivalente (`FACTURACION`, `Facturacion`, `FACTURACION`, `facturacion`)
  - si no existe, lanzar error de usuario:
    `No se encontro la hoja FACTURACION. Revisa que el archivo seleccionado sea el archivo de Cartera correcto.`
- Si es CSV/TXT:
  - leer con detector de separador ya existente
  - tratar la tabla como origen de CARTERA

## Reglas de transformacion para hoja CARTERA
1. Tomar datos con encabezados en fila 1.
2. Eliminar filas completamente vacias.
3. Tomar columnas A hasta AE (31 columnas maximo) cuando existan.
4. Excluir columnas Y y AD usando posiciones originales de Excel:
   - Y = 25
   - AD = 30
5. Si hay menos de 31 columnas:
   - usar las disponibles
   - registrar advertencia en log
6. Mantener encabezados finales de las columnas restantes.
7. Mantener valores sin forzar conversiones destructivas (fechas, montos, textos).

## Deteccion de columnas para PAGO PENDIENTE
Detectar en CARTERA (o en el recorte equivalente) columnas:
- `PLATAFORMA`
- `ESTADO_DE_PAGO`

Permitir aliases (normalizacion ya existente):
- PLATAFORMA: `PLATAFORMA`, `Plataforma`, `TC`, `Tienda`, `idPartner`, `ID_PARTNER`, `ID PARTNER`, `NUMERO PLATAFORMA`
- ESTADO_DE_PAGO: `ESTADO_DE_PAGO`, `ESTADO DE PAGO`, `estado_pago`, `Estado_Pago`, `ESTADO PAGO`

Si falta PLATAFORMA:
`No se pudo encontrar la columna PLATAFORMA. Revisa que el archivo tenga los encabezados correctos.`

Si falta ESTADO_DE_PAGO:
`No se pudo encontrar la columna ESTADO_DE_PAGO. Revisa que el archivo tenga los encabezados correctos.`

## Hoja PAGO PENDIENTE
Construir hoja `PAGO PENDIENTE` con columnas exactas:
1. `PLATAFORMA`
2. `ESTADO_DE_PAGO`

Filtro:
- usar registros donde `ESTADO_DE_PAGO`, despues de `strip` + uppercase, sea exactamente `PENDIENTE`
- no incluir variantes como `PENDIENTE-EXCEPCION`, `PENDIENTE-PRIMERA CUOTA`, `PENDIENTE-RETIRO`

Valor de salida:
- `ESTADO_DE_PAGO` debe quedar exactamente `PENDIENTE` en todos los registros filtrados

Si no hay registros pendientes:
- no fallar
- generar hoja con solo encabezados
- registrar advertencia/log

## Limpieza de datos
Para `PLATAFORMA` (en PAGO PENDIENTE):
- trim
- remover sufijo `.0` cuando aplique
- conservar texto
- evitar notacion cientifica
- no perder ceros iniciales

Para `ESTADO_DE_PAGO`:
- normalizar solo para filtrar
- en salida escribir `PENDIENTE`

No aplicar limpiezas agresivas al resto de CARTERA.

## Salida esperada
Archivo:
`RESULTADO_CARTERA_YYYYMMDD_HHMMSS.xlsx`

Ubicacion:
`output/`

Hojas:
1. `CARTERA`
2. `PAGO PENDIENTE`

## Formato Excel
- encabezados fila 1
- datos desde fila 2
- congelar fila superior
- evitar formulas
- priorizar rendimiento para archivos grandes

## Resumen final esperado en UI
Minimo mostrar:
- Total registros en CARTERA
- Total plataformas con pago pendiente
- Ruta del archivo generado
- Ruta del log

Mensaje final:
`Ya puedes abrir el archivo resultado, copiar la hoja CARTERA y la hoja PAGO PENDIENTE en el archivo oficial de Cartera.`

## Logging
Archivo sugerido:
`procesamiento_cartera_YYYYMMDD_HHMMSS.log`

Incluir:
- modulo ejecutado
- archivo de entrada
- hoja leida
- filas leidas
- columnas originales
- columnas excluidas (Y y AD cuando apliquen)
- total registros en CARTERA
- columna detectada como PLATAFORMA
- columna detectada como ESTADO_DE_PAGO
- total registros en PAGO PENDIENTE
- advertencias (menos de 31 columnas, sin pendientes)
- errores tecnicos

## Rendimiento
- soportar volumen alto (>100k filas si aplica)
- evitar loops fila por fila
- usar operaciones vectorizadas
- minimizar copias innecesarias
- mantener procesamiento en segundo plano

## Compatibilidad
- no romper modulos 1, 2, 3 y 4
- reutilizar helpers existentes antes de crear duplicados
- conservar estilo visual de UI
- no cambiar contratos publicos sin necesidad

## Pruebas minimas a agregar
Crear `tests/test_processor_module5.py` con al menos:
1. caso feliz: genera `CARTERA` y `PAGO PENDIENTE`
2. aplica exclusion de columnas Y y AD en recorte A:AE
3. detecta PLATAFORMA por alias
4. detecta ESTADO_DE_PAGO por alias
5. filtra solo `PENDIENTE` exacto (normalizado)
6. caso sin pendientes: hoja vacia con encabezados
7. error por hoja FACTURACION faltante en Excel
8. error por columna PLATAFORMA faltante
9. error por columna ESTADO_DE_PAGO faltante

No eliminar ni romper pruebas existentes.

## Criterios de aceptacion
1. Modulo 5 activo en UI
2. Boton `Seleccionar archivo de Cartera` funcional
3. Boton `Procesar archivo` funcional
4. Boton `Abrir resultado en Excel` funcional
5. Lee `FACTURACION` (o equivalente) en Excel
6. Recorta A:AE y excluye Y/AD
7. Genera hoja `CARTERA`
8. Detecta `PLATAFORMA`
9. Detecta `ESTADO_DE_PAGO`
10. Genera `PAGO PENDIENTE` con filtro exacto `PENDIENTE`
11. `PAGO PENDIENTE` con columnas exactas `PLATAFORMA`, `ESTADO_DE_PAGO`
12. Salida `RESULTADO_CARTERA_*.xlsx` en `output/`
13. Logs generados
14. Mensajes claros para usuario
15. M1-M4 siguen funcionando
