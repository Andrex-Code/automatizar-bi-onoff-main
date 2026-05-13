# ONOFF Automatizador BI

Este repositorio queda en formato dual:

1. Ejecutable portable listo para usar (sin instalar Python).
2. Codigo fuente completo para seguir editando.

## Ejecutar en cualquier PC

1. Descarga la carpeta del repo (ZIP o `git clone`).
2. En la raiz, ejecuta `ABRIR_APP_ONOFF.bat`.
3. Ese lanzador abre `ONOFF_Automatizador_BI_Fast.exe` usando la carpeta `_internal`.

## Editar el proyecto

- El codigo fuente esta en `automatizador_bi/`.
- Punto de entrada para desarrollo: `automatizador_bi/main.py`.
- Build del ejecutable: `automatizador_bi/build_exe.bat`.

## Estructura clave

- `ONOFF_Automatizador_BI_Fast.exe`: ejecutable portable.
- `_internal/`: librerias necesarias del ejecutable.
- `ABRIR_APP_ONOFF.bat`: acceso rapido para abrir la app.
- `automatizador_bi/`: codigo fuente y pruebas.
- `docs/`: prompts, contexto y documentacion de modulos.
