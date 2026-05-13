# Prompt adaptado - Modulo 2 (Cuenta F.E sin emitir)

Trabaja unicamente en el modulo 2 de la aplicacion existente `ONOFF | Automatizador BI - Resoluciones FE`.

## Objetivo
Implementar el flujo del boton:
`2- Cuenta F.E sin emitir`

Sin reconstruir la app y sin afectar el modulo 1 (`Base Resoluciones F.E`).

## Alcance funcional
1. Permitir seleccionar archivo de entrada (`.csv`, `.txt`, `.xlsx`, `.xlsm`).
2. Procesar en segundo plano (UI no bloqueada).
3. Generar archivo Excel de salida en `output/`.
4. Mostrar resumen:
   - Total de registros procesados
   - Ruta del archivo generado
   - Ruta del log
5. Abrir el resultado en Excel.

## Restricciones
- No conectar a SharePoint.
- No modificar archivos oficiales.
- Soportar archivos grandes (+100.000 filas) con operaciones vectorizadas.
- Evitar ciclos fila por fila.

## Entrada esperada
Columnas esperadas (con variaciones de nombre permitidas):
- Plataforma
- Unidad
- id_Venta
- Consecutivo_FE
- Fecha_Venta
- Cod_error
- Error_details

El archivo puede venir con separador `;`, `,` o tab.
Si llega en una sola columna, intentar separarlo automaticamente.

## Salida esperada
Generar `RESULTADO_CUENTA_FE_SIN_EMITIR_YYYYMMDD_HHMMSS.xlsx` con una sola hoja:
`CUENTA F.E SIN EMITIR`

Columnas finales (orden exacto):
1. PLATAFORMA
2. UNIDAD
3. ID_VENTA
4. CONSECUTIVO_FE
5. FECHA_VENTA
6. COD_ERROR
7. DETALLE DEL ERROR
8. COD_ERROR_TEXTO

Regla clave:
`COD_ERROR_TEXTO` debe ser copia exacta de `COD_ERROR` como texto.

## Limpieza de datos
- `PLATAFORMA`: quitar espacios y sufijo `.0` cuando aplique.
- `ID_VENTA` y `CONSECUTIVO_FE`: mantener legibles, sin notacion cientifica.
- `FECHA_VENTA`: conservar valor legible.
- `COD_ERROR`: conservar como texto.
- `DETALLE DEL ERROR`: conservar texto completo.

## Validaciones
Si falta una columna requerida, mostrar mensaje claro para usuario final:
`No se pudo encontrar la columna <NOMBRE>. Revisa que el archivo corresponda al reporte CUENTA F.E SIN EMITIR.`

Errores tecnicos detallados deben quedar en log.

## Logging
Registrar:
- Fecha/hora
- Modulo ejecutado
- Archivo de entrada
- Archivo generado
- Total filas leidas
- Total filas procesadas
- Errores (si aplica)

## Interfaz
- El modulo 2 debe tener titulo y descripcion propios.
- Botones:
  - Seleccionar archivo
  - Procesar archivo
  - Abrir resultado en Excel
- Mantener modulos 3, 4 y 5 en gris con mensaje `AUTOMATIZANDO`.
