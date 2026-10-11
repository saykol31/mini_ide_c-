# mini_ide_c++

# mini_ide_c- — Mini IDE para C/C++ en Python

IDE ligera de un solo archivo (`idec.py`, Tkinter) para programar en C/C++
en Linux: editor con resaltado de sintaxis, compilación directa, generación
de CMake, build, ejecución con consola interactiva, depuración con GDB y
herramientas para gráficos (Weston/BGFX, GLAD).

> Proyecto personal: mi debut en Python, después de un simulador de tanque
> procedural en SDL2.

## Requisitos

- **Linux** (no corre en Windows: usa `bash`, `konsole` y rutas POSIX)
- Python 3 + Tkinter (`python3-tk`)
- Pillow (`pip install pillow`) — iconos de la interfaz
- `g++` / `gcc`
- `cmake` + `make` (botones CMake/Build)
- `gdb` (botón Debug)
- `pkg-config` (autodetección de librerías: SDL2, SFML, GLFW, Vulkan...)

Opcionales, solo para sus botones:
- `konsole` — terminal de Update/Debug
- `code` — VS Code, botón Crear
- `glad` — botón GLAD (genera `glad/` con OpenGL 3.3 Core)
- `weston` — botones Weston/BGFX

## Uso

```bash
python3 idec.py

## Convención de ejecutables

IDEC utiliza la carpeta `bin/` situada en la raíz del proyecto
para almacenar los ejecutables generados.

- La compilación directa escribe en `bin/<nombre_del_fuente>`.
- Los proyectos CMake generados por IDEC configuran
  `CMAKE_RUNTIME_OUTPUT_DIRECTORY` para utilizar `bin/`.
- La acción Build comprueba el ejecutable esperado en `bin/`
  sin buscar arbitrariamente en subdirectorios.
- La ejecución normal, Weston y BGFX utilizan la misma
  convención de rutas.

El archivo `CMakeLists.txt` permanece en la raíz del proyecto.
