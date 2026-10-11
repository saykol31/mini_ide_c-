# mini_ide_c++


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
