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
```

| Tecla | Acción |
|---|---|
| F1 | Crear — abre VS Code en la carpeta de trabajo |
| F2 | Linker — compilación directa de prueba |
| F3 | CMake — **solo genera** el `CMakeLists.txt` |
| F5 | Build — compila con CMake, binario en `bin/` |
| F6 | Compile — compilación directa sin CMake |
| F7 | Debug — compila con `-g` y abre GDB |
| F8 | Run — ejecuta con consola interactiva (stdin incluido) |

## Los dos compiladores

**Compile (F6)** — para programas simples (los "hola mundo"): compila el
archivo abierto directamente con `g++`/`gcc` (`-O2 -g -Wall`), detecta las
librerías por los `#include` y deja el binario en `bin/`. Sin CMake.

**CMake (F3) + Build (F5)** — para proyectos: F3 *solo genera* el
`CMakeLists.txt` (escanea fuentes, detecta C vs C++, mapea headers a
`find_package`, detecta Vulkan por 3 vías y GLAD local). F5 configura
(`cmake -S . -B build`) y compila (`cmake --build`), binario en `bin/`.

## Convención de ejecutables

IDEC utiliza la carpeta `bin/` en la raíz del proyecto para los
ejecutables generados:

- La compilación directa (F6) escribe en `bin/`.
- Los `CMakeLists.txt` generados configuran `CMAKE_RUNTIME_OUTPUT_DIRECTORY`
  para usar `bin/`.
- La acción Build (F5) busca el ejecutable esperado en `bin/`.
- La ejecución normal, Weston y BGFX usan la misma convención.

El `CMakeLists.txt` permanece en la raíz del proyecto.

## Gráficos: Weston y BGFX

- **Weston**: lanza el compositor Weston, espera el socket Wayland y ejecuta
  el binario con `WAYLAND_DISPLAY` configurado.
- **BGFX**: ejecuta binarios BGFX bajo Weston/Wayland.
- **GLAD**: genera `glad/` (OpenGL 3.3 Core) dentro del proyecto.
