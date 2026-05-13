Quiero construir una aplicación de escritorio semiautomática para Windows que procese archivos grandes de Excel/CSV relacionados con la actualización de BI de “BASE RESOLUCIONES FE”.

La aplicación debe ser sencilla para el usuario, no técnica. Debe permitir seleccionar un archivo descargado del correo “Reporte seguimiento FE TryTiendas” y generar un archivo Excel resultado listo para copiar y pegar manualmente en el archivo oficial de SharePoint.

IMPORTANTE:
El archivo de entrada puede tener más de 100.000 filas, por lo tanto la aplicación debe estar optimizada para archivos grandes. Evitar cargar datos innecesarios en memoria si no es necesario. Usar librerías eficientes para lectura, transformación y escritura de archivos grandes.

Objetivo principal:
Crear una aplicación de escritorio que:
1. Pida al usuario seleccionar el archivo de entrada.
2. Procese automáticamente la información.
3. Genere un archivo Excel resultado con dos hojas:
   - RESOLUCIONES FE
   - ALERTA
4. No debe conectarse a SharePoint.
5. No debe modificar el archivo oficial.
6. Solo debe generar un archivo nuevo de salida.

Contexto del proceso manual actual:
Actualmente el usuario descarga un archivo del correo. Ese archivo puede venir en formato CSV o texto separado por punto y coma “;” o por comas “,”. Hoy se abre manualmente con Bloc de notas y luego Excel para separar columnas, limpiar información y preparar dos hojas: RESOLUCIONES FE y ALERTA.

La app debe reemplazar ese proceso manual.

Tecnología sugerida:
Construir una aplicación de escritorio en Python usando:
- customtkinter o tkinter para la interfaz gráfica.
- pandas o polars para procesamiento de datos.
- openpyxl o xlsxwriter para generar el Excel resultado.

Priorizar rendimiento para más de 100.000 filas. Si pandas puede manejarlo bien, usar pandas. Si se considera mejor para rendimiento, usar polars. Explicar en comentarios la decisión.

Interfaz requerida:
La app debe tener una ventana simple con:
- Título: “Automatizador BI - Resoluciones FE”
- Botón: “Seleccionar archivo”
- Texto que muestre la ruta del archivo seleccionado
- Botón: “Procesar archivo”
- Barra de progreso o mensaje de estado
- Área de resumen final con:
  - Total de registros procesados
  - Total de alertas encontradas
  - Ruta del archivo generado
- Botón opcional: “Abrir carpeta del resultado”

Flujo esperado:
1. El usuario abre la aplicación.
2. Selecciona el archivo descargado.
3. Presiona “Procesar archivo”.
4. La app procesa el archivo.
5. La app genera un Excel nuevo en una carpeta de salida.
6. La app muestra un mensaje de éxito.

El archivo generado debe llamarse así:
RESULTADO_BASE_RESOLUCIONES_FE_YYYYMMDD_HHMMSS.xlsx

El archivo resultado debe tener estas hojas:

HOJA 1: RESOLUCIONES FE
Debe contener la información final organizada y lista para copiar y pegar en el archivo oficial.

HOJA 2: ALERTA
Debe contener únicamente los registros donde la columna de notificación o resultado contenga la palabra “VENCIMIENTO”.
En esta hoja, la columna I debe llamarse exactamente:
ALERTA

Reglas de procesamiento:

1. Lectura del archivo
La app debe aceptar archivos:
- .csv
- .txt
- .xlsx
- .xlsm si es posible

Debe detectar automáticamente el separador cuando sea CSV o TXT:
- Punto y coma ;
- Coma ,
- Tabulación

Si el archivo trae todos los datos en una sola columna, la app debe intentar separarlos automáticamente.

2. Limpieza de nombres de columnas
Los nombres pueden venir con variaciones. La app debe intentar normalizarlos:
- Quitar espacios al inicio y final
- Convertir nombres a mayúsculas internamente para detectar columnas
- Mantener nombres finales claros en el archivo resultado

Columnas esperadas aproximadas en el reporte:
- TypeRes o tipo de registro
- idPartner o plataforma
- idDpnDianAuthorization o autorización/resolución
- idDpnPrefix o prefijo
- idroute o unidad
- idDpnEndConsecutive o total
- idDpnCurrentConsecutive o consumo
- Diferencia o disponible
- result o notificación

No asumir que los nombres vienen exactamente iguales. Crear una función que busque columnas por nombres posibles.

3. Limpieza de plataforma
Si la columna de plataforma viene con valores como:
c5011
c5370
C5058

La app debe quitar la letra “c” o “C” y dejar solo el número:
5011
5370
5058

La plataforma debe quedar como número o texto numérico limpio, sin decimales.

4. Manejo de tipo de documento
El archivo original puede traer una columna inicial con valores como:
- Documento POS
- Resolución FE
- Resolucion FE
- RESOLUCION FE

Pero en el resultado final debe generarse una columna llamada:
TIPO DOC

Reglas:
- Si el registro original dice “Documento POS”, en la columna TIPO DOC debe quedar:
  RESOLUCION DIAN

- Si el registro original dice “Resolución FE” o “Resolucion FE”, en la columna TIPO DOC debe quedar:
  RESOLUCION POS

Usar normalización para ignorar tildes, mayúsculas y minúsculas.

5. Columnas finales de la hoja RESOLUCIONES FE
La hoja RESOLUCIONES FE debe quedar con estas columnas, en este orden exacto:

PLATAFORMA
AUTORIZACION
PREFIJO
UNIDAD
TOTAL
CONSUMO
DISPONIBLE
TIPO DOC
NOTIFICACION

Notas:
- PLATAFORMA viene de idPartner, limpiando la letra c si existe.
- AUTORIZACION viene de idDpnDianAuthorization.
- PREFIJO viene de idDpnPrefix.
- UNIDAD viene de idroute.
- TOTAL viene de idDpnEndConsecutive.
- CONSUMO viene de idDpnCurrentConsecutive.
- DISPONIBLE viene de Diferencia.
- TIPO DOC se calcula según la regla anterior.
- NOTIFICACION viene de result.

6. Hoja ALERTA
Crear una segunda hoja llamada ALERTA.

Debe filtrar los registros de RESOLUCIONES FE donde NOTIFICACION contenga la palabra:
VENCIMIENTO

La búsqueda debe ser sin importar mayúsculas o minúsculas.

La hoja ALERTA debe tener las mismas columnas que RESOLUCIONES FE, pero la última columna debe llamarse exactamente:
ALERTA

Por lo tanto las columnas de ALERTA deben ser:

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

7. Tipos de datos
Evitar que Excel convierta valores largos en notación científica cuando no convenga.
Especialmente:
- AUTORIZACION puede ser un número largo y debe conservarse correctamente.
- PREFIJO puede contener letras y números.
- PLATAFORMA debe quedar limpia.
- TOTAL, CONSUMO y DISPONIBLE pueden ser numéricos.

Si hay valores vacíos, no debe fallar.

8. Validaciones
Antes de generar el resultado, la app debe validar:
- Que se pudo leer el archivo.
- Que se encontraron las columnas mínimas necesarias.
- Que se pudo crear RESOLUCIONES FE.
- Que se pudo crear ALERTA.

Si falta alguna columna importante, mostrar un mensaje claro al usuario:
“No se pudo encontrar la columna AUTORIZACION. Revisa que el archivo corresponda al reporte de seguimiento FE TryTiendas.”

No mostrar errores técnicos largos al usuario final, pero sí guardar un archivo log para diagnóstico.

9. Archivo log
Crear un archivo de log junto al resultado o en una carpeta logs.
Debe registrar:
- Fecha y hora del proceso
- Archivo procesado
- Número de filas leídas
- Número de filas resultantes
- Número de alertas
- Errores si ocurren

10. Rendimiento
Como el archivo puede superar las 100.000 filas:
- Evitar ciclos fila por fila si se puede hacer vectorizado.
- No usar operaciones lentas innecesarias.
- Mostrar estado de “Procesando...” para que el usuario sepa que la app no está congelada.
- Ejecutar el procesamiento en un hilo separado para que la interfaz no se bloquee.
- Manejar archivos grandes de forma estable.

11. Experiencia de usuario
La app debe ser sencilla:
- Mensajes claros.
- Botones grandes.
- Nada de términos técnicos.
- Al finalizar, mostrar:
  “Archivo generado correctamente.”
  “Ya puedes abrir el archivo resultado, copiar la hoja RESOLUCIONES FE y luego la hoja ALERTA en el archivo oficial.”

12. Estructura del proyecto
Crear una estructura ordenada:

/automatizador_bi
  main.py
  processor.py
  ui.py
  requirements.txt
  README.md
  /logs
  /output

main.py:
- Punto de entrada de la app.

ui.py:
- Interfaz gráfica.
- Selección de archivo.
- Botones.
- Mensajes de estado.
- Llamada al procesamiento en segundo plano.

processor.py:
- Lectura del archivo.
- Detección de separador.
- Normalización de columnas.
- Transformación de datos.
- Creación del Excel resultado.
- Creación del log.

requirements.txt:
Incluir las librerías necesarias.

README.md:
Explicar cómo instalar y ejecutar:
- Crear entorno virtual
- Instalar dependencias
- Ejecutar la app

13. Entregables esperados
Genera todo el código necesario para que pueda correr la aplicación desde Visual Studio Code.

También incluye instrucciones para empaquetarla luego como .exe usando PyInstaller, pero no es necesario empaquetarla todavía.

Comando esperado para ejecutar en desarrollo:
python main.py

Comando sugerido para crear exe:
pyinstaller --onefile --windowed main.py

14. Criterios de aceptación
La app se considera correcta si:
- Permite seleccionar un archivo.
- Procesa un archivo con más de 100.000 filas sin bloquear la interfaz.
- Genera un Excel con dos hojas: RESOLUCIONES FE y ALERTA.
- La hoja RESOLUCIONES FE tiene las columnas correctas y en el orden correcto.
- La hoja ALERTA filtra solo registros con VENCIMIENTO.
- La columna I de ALERTA se llama exactamente ALERTA.
- La app muestra un resumen final.
- Los errores son claros para el usuario.
- Se genera un log del proceso.

Por favor, construye la aplicación completa con código limpio, comentarios útiles y separando correctamente interfaz y procesamiento.