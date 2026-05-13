Necesito implementar o ajustar el MÓDULO 1 de la aplicación existente: “1- Base Resoluciones F.E”.

La aplicación ya existe y está separada por módulos. No reconstruyas la app desde cero. No dañes los demás módulos existentes.

Contexto general:
La app se llama “ONOFF | Automatizador BI - Resoluciones FE”.
Ya tiene pestañas o botones superiores:

1- Base Resoluciones F.E
2- Cuenta F.E sin emitir
3- Error F.E
4- Plataformas que presentan error F.E
5- Cartera

Este prompt corresponde únicamente al módulo:

1- Base Resoluciones F.E

==================================================
OBJETIVO DEL MÓDULO 1
==================================================

Procesar el archivo descargado del correo “Reporte seguimiento FE TryTiendas” o “Reporte de consecutivos FE TryTiendas” y generar un Excel resultado listo para copiar y pegar manualmente en el archivo oficial de la empresa:

BASE RESOLUCIONES F.E

Este módulo NO debe conectarse a SharePoint.
Este módulo NO debe modificar el archivo oficial de BI.
Solo debe recibir un archivo de entrada y generar un archivo Excel nuevo de salida.

El resultado debe tener dos hojas:

1. RESOLUCIONES FE
2. ALERTA

==================================================
ARCHIVO DE ENTRADA
==================================================

El usuario seleccionará manualmente el archivo descargado del correo.

Formatos permitidos:
- .csv
- .txt
- .xlsx
- .xlsm

El archivo puede venir separado por:
- punto y coma ;
- coma ,
- tabulación

También puede pasar que el archivo venga con toda la información en una sola columna. En ese caso, la app debe intentar separarlo automáticamente.

El archivo puede tener más de 100.000 filas, por lo tanto debe estar optimizado para archivos grandes.

==================================================
INTERFAZ DEL MÓDULO 1
==================================================

Mantener el estilo visual actual de la aplicación.

Título del módulo:
Automatizador BI - Resoluciones FE

Descripción:
Carga el reporte, procesa automáticamente las hojas RESOLUCIONES FE y ALERTA, y descarga el resultado final.

Botones requeridos:

1. Seleccionar archivo
2. Procesar archivo
3. Abrir resultado en Excel

Debe mostrar en pantalla:

- Archivo seleccionado
- Estado del procesamiento
- Resumen final

Si el usuario selecciona archivo correctamente, mostrar:

Archivo seleccionado:
<ruta del archivo>

Estado:
Archivo cargado correctamente.

Si el usuario presiona “Procesar archivo” sin seleccionar archivo, mostrar:

Primero debes seleccionar el archivo del reporte.

==================================================
LÓGICA GENERAL DEL MÓDULO
==================================================

El proceso manual actual hace lo siguiente:

1. Descarga el reporte del correo.
2. Corrige separadores.
3. Separa columnas.
4. Limpia la plataforma.
5. Clasifica el tipo de documento.
6. Genera la tabla RESOLUCIONES FE.
7. Filtra registros con VENCIMIENTO.
8. Genera la hoja ALERTA.
9. En ALERTA, la última columna debe llamarse exactamente ALERTA.

La app debe automatizar todo ese proceso.

==================================================
LECTURA DEL ARCHIVO
==================================================

La app debe leer archivos CSV, TXT o Excel.

Para CSV o TXT:
- Detectar automáticamente el separador:
  - ;
  - ,
  - tabulación
- Si todo viene en una sola columna, intentar dividirla usando el separador correcto.
- Manejar archivos con comillas.
- Manejar textos largos.
- Manejar columnas vacías sin fallar.

Para Excel:
- Leer la primera hoja por defecto, salvo que exista una hoja claramente relacionada con el reporte.
- Si hay más de una hoja, usar la primera hoja con datos.
- No depender de formatos visuales.

==================================================
COLUMNAS ESPERADAS DEL REPORTE
==================================================

El archivo puede traer columnas parecidas a estas:

- TypeRes
- idPartner
- idDpnDianAuthorization
- idDpnPrefix
- idroute
- idDpnEndConsecutive
- idDpnCurrentConsecutive
- Diferencia
- result

Pero los nombres pueden variar.

No asumir nombres exactos. Crear o reutilizar una función que normalice nombres de columnas ignorando:

- mayúsculas
- minúsculas
- espacios
- guiones bajos
- tildes
- puntos
- dobles espacios

==================================================
EQUIVALENCIAS DE COLUMNAS
==================================================

Detectar las siguientes columnas aunque vengan con nombres similares:

TIPO ORIGINAL:
- TypeRes
- Type Res
- Tipo
- TipoRes
- tipo registro
- Documento

PLATAFORMA:
- idPartner
- id Partner
- ID_PARTNER
- Plataforma
- PLATAFORMA
- TC

AUTORIZACION:
- idDpnDianAuthorization
- id Dpn Dian Authorization
- DianAuthorization
- Autorizacion
- Autorización
- AUTORIZACION
- Resolucion
- Resolución

PREFIJO:
- idDpnPrefix
- id Dpn Prefix
- Prefix
- Prefijo
- PREFIJO

UNIDAD:
- idroute
- id route
- ruta
- unidad
- UNIDAD

TOTAL:
- idDpnEndConsecutive
- EndConsecutive
- Consecutivo Final
- Total
- TOTAL

CONSUMO:
- idDpnCurrentConsecutive
- CurrentConsecutive
- Consecutivo Actual
- Consumo
- CONSUMO

DISPONIBLE:
- Diferencia
- Disponible
- DISPONIBLE
- Difference

NOTIFICACION:
- result
- Resultado
- Notificacion
- Notificación
- NOTIFICACION
- ALERTA

==================================================
VALIDACIONES DE ENTRADA
==================================================

Antes de procesar, validar que existan las columnas mínimas necesarias:

- PLATAFORMA
- AUTORIZACION
- PREFIJO
- UNIDAD
- TOTAL
- CONSUMO
- DISPONIBLE
- NOTIFICACION
- TIPO ORIGINAL

Si falta una columna, mostrar un mensaje claro.

Ejemplo:

No se pudo encontrar la columna AUTORIZACION. Revisa que el archivo corresponda al reporte de seguimiento FE TryTiendas.

No mostrar errores técnicos largos al usuario final.
Los errores técnicos deben ir al log.

==================================================
TRANSFORMACIÓN DE DATOS
==================================================

Generar una tabla final llamada RESOLUCIONES FE con estas columnas en este orden exacto:

PLATAFORMA
AUTORIZACION
PREFIJO
UNIDAD
TOTAL
CONSUMO
DISPONIBLE
TIPO DOC
NOTIFICACION

==================================================
REGLAS DE TRANSFORMACIÓN
==================================================

1. PLATAFORMA

Viene de idPartner o columna equivalente.

Limpiar así:
- Quitar espacios.
- Si viene como c5011, dejar 5011.
- Si viene como C5011, dejar 5011.
- Si viene como 5011.0, dejar 5011.
- Evitar notación científica.
- Mantener como texto limpio para evitar errores.

Ejemplos:
c5011 -> 5011
C5370 -> 5370
5058.0 -> 5058
" 6978 " -> 6978

2. AUTORIZACION

Viene de idDpnDianAuthorization o equivalente.

Reglas:
- Puede ser número largo.
- No debe quedar en notación científica.
- No debe perder dígitos.
- Si viene vacío, conservar vacío.
- Tratar preferiblemente como texto limpio.

3. PREFIJO

Viene de idDpnPrefix o equivalente.

Reglas:
- Puede contener letras, números o combinaciones.
- No convertir a número si tiene letras.
- Quitar espacios al inicio y final.
- Conservar valores como FE, TC, FEC, etc.

4. UNIDAD

Viene de idroute o equivalente.

Reglas:
- Limpiar espacios.
- Si viene como 1.0, dejar 1 si aplica.
- Mantener valor legible.

5. TOTAL

Viene de idDpnEndConsecutive o equivalente.

Reglas:
- Debe quedar numérico si es posible.
- Si viene con decimales innecesarios, quitar .0.
- Si viene vacío, dejar vacío.

6. CONSUMO

Viene de idDpnCurrentConsecutive o equivalente.

Reglas:
- Debe quedar numérico si es posible.
- Si viene con decimales innecesarios, quitar .0.
- Si viene vacío, dejar vacío.

7. DISPONIBLE

Viene de Diferencia o equivalente.

Reglas:
- Debe quedar numérico si es posible.
- Puede ser cero o negativo si el reporte lo trae.
- No fallar con valores vacíos.

8. TIPO DOC

Esta columna se calcula a partir de la columna original TypeRes o equivalente.

Reglas:

Si el valor original es:
- Documento POS
- DOCUMENTO POS
- documento pos

Entonces TIPO DOC debe quedar:
RESOLUCION DIAN

Si el valor original es:
- Resolución FE
- Resolucion FE
- RESOLUCION FE
- resolución fe

Entonces TIPO DOC debe quedar:
RESOLUCION POS

La comparación debe ignorar:
- mayúsculas
- minúsculas
- tildes
- espacios sobrantes

Si viene otro valor desconocido, conservarlo normalizado o dejarlo registrado en el log como advertencia.

9. NOTIFICACION

Viene de result o columna equivalente.

Reglas:
- Conservar el texto completo.
- No recortar.
- Quitar espacios extremos.
- Puede contener textos como:
  - VIGENTE Quedan mas de 100 Consecutivos
  - VENCIMIENTO Quedan menos de 100 Consecutivos
  - VENCIMIENTO
  - otros textos similares

==================================================
HOJA RESOLUCIONES FE
==================================================

Crear una hoja llamada:

RESOLUCIONES FE

Debe contener las columnas finales en este orden exacto:

PLATAFORMA
AUTORIZACION
PREFIJO
UNIDAD
TOTAL
CONSUMO
DISPONIBLE
TIPO DOC
NOTIFICACION

Encabezados en fila 1.
Datos desde fila 2.

==================================================
HOJA ALERTA
==================================================

Crear una segunda hoja llamada:

ALERTA

Debe contener únicamente los registros de RESOLUCIONES FE donde la columna NOTIFICACION contenga la palabra:

VENCIMIENTO

La búsqueda debe:
- Ignorar mayúsculas y minúsculas.
- Detectar VENCIMIENTO aunque venga dentro de una frase.
- No exigir coincidencia exacta.

Ejemplos válidos:
- VENCIMIENTO Quedan menos de 100 Consecutivos
- vencimiento quedan menos de 100 consecutivos
- VENCIMIENTO

La hoja ALERTA debe tener las mismas columnas que RESOLUCIONES FE, pero la última columna debe llamarse exactamente:

ALERTA

Por lo tanto, las columnas de ALERTA deben quedar en este orden exacto:

PLATAFORMA
AUTORIZACION
PREFIJO
UNIDAD
TOTAL
CONSUMO
DISPONIBLE
TIPO DOC
ALERTA

El contenido de ALERTA debe ser el mismo texto que estaba en NOTIFICACION.

IMPORTANTE:
La columna I de la hoja ALERTA debe llamarse exactamente ALERTA.

==================================================
ARCHIVO DE SALIDA
==================================================

Guardar el resultado en la carpeta output del proyecto.

Nombre del archivo:

RESULTADO_BASE_RESOLUCIONES_FE_YYYYMMDD_HHMMSS.xlsx

Ejemplo:

RESULTADO_BASE_RESOLUCIONES_FE_20260512_130933.xlsx

El archivo generado debe tener dos hojas:

1. RESOLUCIONES FE
2. ALERTA

==================================================
FORMATO DEL EXCEL
==================================================

Formato simple:
- Encabezados en fila 1.
- Datos desde fila 2.
- Congelar fila superior si ya se usa en otros módulos.
- Ajustar ancho de columnas solo si no afecta el rendimiento.
- No usar fórmulas.
- El resultado debe ser solo valores.
- Para archivos grandes, priorizar rendimiento sobre diseño visual.

==================================================
RESUMEN FINAL
==================================================

Al finalizar correctamente, mostrar algo como:

Archivo generado correctamente.

Total de registros procesados: 125000
Total de alertas encontradas: 850
Ruta del archivo generado: C:\...\output\RESULTADO_BASE_RESOLUCIONES_FE_20260512_130933.xlsx
Ruta del log: C:\...\logs\procesamiento_base_resoluciones_fe_20260512_130933.log

Mensaje final:
Ya puedes abrir el archivo resultado, copiar la hoja RESOLUCIONES FE y la hoja ALERTA en el archivo oficial BASE RESOLUCIONES F.E.

==================================================
LOG
==================================================

Crear un log del proceso igual que los demás módulos.

El log debe incluir:

- Fecha y hora
- Módulo ejecutado: BASE RESOLUCIONES F.E
- Archivo de entrada usado
- Archivo generado
- Total filas leídas
- Total registros procesados
- Total alertas encontradas
- Columnas originales detectadas
- Mapeo de columnas usado
- Valores desconocidos encontrados en TIPO DOC, si aplica
- Errores si aplica

Si ya existe una función común de logging en el proyecto, reutilizarla.

==================================================
VALIDACIONES
==================================================

Antes de generar el archivo, validar:

1. Que exista archivo seleccionado.
2. Que se pueda leer el archivo.
3. Que existan datos.
4. Que se detecten las columnas necesarias.
5. Que se pueda generar RESOLUCIONES FE.
6. Que se pueda generar ALERTA.

Mensajes claros:

Si falta archivo:
Primero debes seleccionar el archivo del reporte.

Si no se puede leer:
No se pudo leer el archivo seleccionado. Revisa que no esté abierto o dañado.

Si faltan columnas:
No se pudo encontrar la columna <NOMBRE>. Revisa que el archivo corresponda al reporte de seguimiento FE TryTiendas.

Si no hay alertas:
No se encontraron registros con VENCIMIENTO. Se generará la hoja ALERTA solo con encabezados.

No mostrar errores técnicos largos al usuario final.
Los errores técnicos deben quedar registrados en el log.

==================================================
BOTÓN: ABRIR RESULTADO EN EXCEL
==================================================

El botón “Abrir resultado en Excel” debe abrir el último archivo generado por el módulo 1.

Si todavía no se ha generado un archivo, mostrar:

Primero debes procesar un archivo para generar el resultado.

==================================================
RENDIMIENTO
==================================================

El archivo puede superar las 100.000 filas.

Requisitos:
- No usar ciclos fila por fila.
- Usar operaciones vectorizadas.
- No congelar la interfaz.
- Usar procesamiento en segundo plano igual que los demás módulos.
- Mantener uso de memoria razonable.
- Leer y escribir archivos de forma eficiente.
- Evitar copias innecesarias de DataFrames.
- La hoja ALERTA debe generarse filtrando desde RESOLUCIONES FE de forma eficiente.

==================================================
COMPATIBILIDAD CON EL PROYECTO ACTUAL
==================================================

Antes de implementar:

- Revisa cómo está implementada la interfaz actual.
- Revisa cómo están estructurados los módulos existentes.
- Reutiliza funciones comunes si existen:
  - lectura de archivos
  - detección de separadores
  - normalización de columnas
  - escritura de Excel
  - logging
  - apertura de archivo en Excel
  - ejecución en segundo plano
- Reutiliza estilos visuales actuales.
- Reutiliza estructura de carpetas actual:
  - output
  - logs
- No modificar comportamiento de otros módulos salvo que sea estrictamente necesario.

==================================================
CRITERIOS DE ACEPTACIÓN
==================================================

El módulo 1 estará correcto si:

1. No rompe los demás módulos.
2. Tiene botón “Seleccionar archivo”.
3. Tiene botón “Procesar archivo”.
4. Tiene botón “Abrir resultado en Excel”.
5. Permite seleccionar archivos .csv, .txt, .xlsx o .xlsm.
6. Detecta separadores ; , o tabulación.
7. Si el archivo viene en una sola columna, intenta separarlo automáticamente.
8. Detecta las columnas necesarias aunque tengan variaciones de nombre.
9. Limpia correctamente PLATAFORMA.
10. Conserva AUTORIZACION sin notación científica.
11. Calcula TIPO DOC correctamente:
    - Documento POS -> RESOLUCION DIAN
    - Resolución FE -> RESOLUCION POS
12. Genera un Excel llamado RESULTADO_BASE_RESOLUCIONES_FE_YYYYMMDD_HHMMSS.xlsx.
13. El Excel tiene hoja RESOLUCIONES FE.
14. El Excel tiene hoja ALERTA.
15. La hoja RESOLUCIONES FE tiene columnas en este orden exacto:
    PLATAFORMA
    AUTORIZACION
    PREFIJO
    UNIDAD
    TOTAL
    CONSUMO
    DISPONIBLE
    TIPO DOC
    NOTIFICACION
16. La hoja ALERTA tiene columnas en este orden exacto:
    PLATAFORMA
    AUTORIZACION
    PREFIJO
    UNIDAD
    TOTAL
    CONSUMO
    DISPONIBLE
    TIPO DOC
    ALERTA
17. La columna I de ALERTA se llama exactamente ALERTA.
18. ALERTA solo contiene registros donde NOTIFICACION contiene VENCIMIENTO.
19. Soporta archivos de más de 100.000 filas.
20. Muestra resumen final con total de registros, total de alertas, ruta del archivo generado y ruta del log.
21. Genera log.
22. El botón “Abrir resultado en Excel” abre el archivo generado.
23. Los errores mostrados al usuario son claros y no técnicos.
24. Los errores técnicos quedan registrados en el log.

Por favor implementa o ajusta este módulo completo respetando la arquitectura actual del proyecto.