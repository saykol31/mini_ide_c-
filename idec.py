# Importaciones estándar
import os
from pathlib import Path
import re
import shlex
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import glob
import time

# Importaciones de terceros
from PIL import Image, ImageTk


# --- RUTAS PORTABLES ---
BASE_DIR = Path(__file__).resolve().parent

# Recursos que viajan dentro del repositorio
CARPETA_ICONOS = BASE_DIR / "Icons"
CARPETA_MANT = BASE_DIR / "MANTENIMIENTO"
UPDATER = CARPETA_MANT / "UPDATER_ENTORNO.cpp"

# Carpeta de trabajo predeterminada del usuario
CARPETA_C = Path.home() / "C"

ultimo_archivo = None

# --- COLORES ---
COLOR_ROSA       = "#FF69B4"
COLOR_DORADO_OSC = "#DAA520"
COLOR_NARANJA    = "#FFA500"
COLOR_VERDE_LIMA = "#32CD32"
COLOR_AZUL_DODGE = "#1E90FF"
COLOR_PURPURA    = "#8A2BE2"
COLOR_TURQUESA   = "#00CED1"
COLOR_DORADO     = "#FFD700"
COLOR_ROJO       = "#FF0000"

# -------Definir Variables

# ---------------- VENTANA ---------------- #
root = tk.Tk()
frame_consola = tk.Frame(root)
root.title("Mini IDE para C/C++")
root.geometry("900x850")
root.config(bg="#E6E6FA")

# ---------------- FUNCIONES ---------------- #

################### FUNCION LISTAR  ####### BOTON OPEN ################

def listar():
    global ultimo_archivo
    archivo = filedialog.askopenfilename(
        initialdir=CARPETA_C,
        filetypes=[("Archivos C y C++", "*.c *.cpp *.h")],
        title="Abrir archivo"
    )
    if archivo:
        with open(archivo, "r") as f:
            contenido = f.read()
        editor.delete("1.0", tk.END)
        editor.insert(tk.END, contenido)
        editor.edit_modified(False)
        ultimo_archivo = archivo
        resaltar()

def auto_indent(event):
    line = editor.get("insert linestart", "insert")
    indent = ""
    for c in line:
        if c in (" ", "\t"):
            indent += c
        else:
            break
    editor.insert("insert", "\n" + indent)
    return "break"


###################  GUARDAR  #######################

def guardar():
    global ultimo_archivo

    # ============================================================
    # OBTENER CONTENIDO DEL EDITOR
    # ============================================================

    contenido = editor.get("1.0", tk.END)

    # ============================================================
    # SI YA EXISTE UN ARCHIVO ABIERTO
    # ============================================================

    if ultimo_archivo:

        try:
            with open(
                ultimo_archivo,
                "w",
                encoding="utf-8"
            ) as f:
                f.write(contenido)

            editor.edit_modified(False)

            ruta_carpeta = os.path.dirname(
                ultimo_archivo
            )

            messagebox.showinfo(
                "Guardado",
                f"Archivo guardado:\n\n{ultimo_archivo}"
            )

        except Exception as e:

            messagebox.showerror(
                "Error al guardar",
                f"No se pudo guardar el archivo:\n\n{e}"
            )

            return

    # ============================================================
    # ARCHIVO NUEVO -> GUARDAR COMO
    # ============================================================

    else:

        archivo = filedialog.asksaveasfilename(

            initialdir=CARPETA_C,

            # ----------------------------------------------------
            # IMPORTANTE:
            # C++ es ahora el lenguaje predeterminado
            # ----------------------------------------------------

            defaultextension=".cpp",

            filetypes=[
                (
                    "Archivos C++",
                    "*.cpp"
                ),
                (
                    "Archivos C",
                    "*.c"
                ),
                (
                    "Archivos C++",
                    "*.cc"
                ),
                (
                    "Archivos C++",
                    "*.cxx"
                ),
                (
                    "Archivos C y C++",
                    "*.c *.cpp *.cc *.cxx"
                ),
                (
                    "Todos los archivos",
                    "*.*"
                )
            ],

            title="Guardar como..."
        )

        # --------------------------------------------------------
        # Canceló el diálogo
        # --------------------------------------------------------

        if not archivo:
            return

        # ========================================================
        # ASEGURAR EXTENSIÓN C++
        # ========================================================

        nombre_archivo = os.path.basename(
            archivo
        )

        nombre_base, extension = os.path.splitext(
            nombre_archivo
        )

        extension = extension.lower()

        # --------------------------------------------------------
        # Si NO escribió ninguna extensión:
        #
        #       oxigen
        #
        # se convierte en:
        #
        #       oxigen.cpp
        # --------------------------------------------------------

        if extension == "":
            archivo += ".cpp"

            nombre_archivo = os.path.basename(
                archivo
            )

        # --------------------------------------------------------
        # Si escribió .c, se respeta:
        #
        #       programa.c
        #
        # --------------------------------------------------------

        elif extension == ".c":
            pass

        # --------------------------------------------------------
        # Si escribió .cpp, se respeta:
        #
        #       programa.cpp
        #
        # --------------------------------------------------------

        elif extension in (
            ".cpp",
            ".cc",
            ".cxx"
        ):
            pass

        # --------------------------------------------------------
        # Otras extensiones:
        #
        # No las modificamos.
        # --------------------------------------------------------

        else:
            pass

        # ========================================================
        # CREAR CARPETA DEL PROYECTO
        # ========================================================

        nombre_carpeta = os.path.splitext(
            os.path.basename(archivo)
        )[0]

        ruta_carpeta = os.path.join(
            os.path.dirname(archivo),
            nombre_carpeta
        )

        try:

            # Crear carpeta del proyecto
            os.makedirs(
                ruta_carpeta,
                exist_ok=True
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"No se pudo crear la carpeta:\n\n"
                f"{ruta_carpeta}\n\n"
                f"{e}"
            )

            return

        # ========================================================
        # RUTA FINAL DEL ARCHIVO
        # ========================================================

        ruta_archivo = os.path.join(
            ruta_carpeta,
            os.path.basename(archivo)
        )

        # ========================================================
        # GUARDAR
        # ========================================================

        try:

            with open(
                ruta_archivo,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(
                    contenido
                )

        except Exception as e:

            messagebox.showerror(
                "Error al guardar",
                f"No se pudo guardar el archivo:\n\n"
                f"{ruta_archivo}\n\n"
                f"{e}"
            )

            return

        # ========================================================
        # ACTUALIZAR ARCHIVO ACTUAL
        # ========================================================

        ultimo_archivo = ruta_archivo

        editor.edit_modified(False)

        # ========================================================
        # MENSAJE
        # ========================================================

        messagebox.showinfo(
            "Guardado",
            f"Archivo guardado:\n\n"
            f"{ultimo_archivo}"
        )

    # ============================================================
    # LIMPIAR CONSOLA
    # ============================================================

    try:

        consola.config(
            state="normal"
        )

        consola.delete(
            "1.0",
            tk.END
        )

        consola.config(
            state="disabled"
        )

    except Exception:
        pass

    # ============================================================
    # MOSTRAR EN CONSOLA
    # ============================================================

    if 'print_consola' in globals():

        print_consola(
            "\033[1;32m"
            f"✅ Guardado en carpeta: {ruta_carpeta}"
            "\033[0m"
        )

        print_consola(
            "\033[1;36m"
            f"📄 Archivo: {ultimo_archivo}"
            "\033[0m"
        )

        # --------------------------------------------------------
        # Mostrar lenguaje detectado
        # --------------------------------------------------------

        extension_final = os.path.splitext(
            ultimo_archivo
        )[1].lower()

        if extension_final == ".c":

            print_consola(
                "\033[1;33m"
                "🔧 Lenguaje: C"
                "\033[0m"
            )

        elif extension_final in (
            ".cpp",
            ".cc",
            ".cxx"
        ):

            print_consola(
                "\033[1;35m"
                "🔧 Lenguaje: C++"
                "\033[0m"
            )
###################  SELECCIONAR  #######################

def seleccionar_todo():
    """Selecciona todo el contenido del editor."""
    editor.tag_add("sel", "1.0", "end")
    editor.mark_set("insert", "1.0")  # opcional: colocar cursor al inicio
    editor.see("1.0")


###################  COPIAR  #######################

def copiar():
    editor.event_generate("<<Copy>>")

# Limpiar consola
    consola.config(state="normal")
    consola.delete("1.0", tk.END)
    consola.config(state="disabled")


###################  PEGAR  #######################

def pegar():
    editor.event_generate("<<Paste>>")
    editor.after_idle(resaltar)

# Limpiar consola
    consola.config(state="normal")
    consola.delete("1.0", tk.END)
    consola.config(state="disabled")


###################  LIMPIAR  #######################

def limpiar_area():
    global ultimo_archivo
    if editor.edit_modified():
        if not messagebox.askyesno("Confirmar", "Tienes cambios sin guardar. ¿Deseas continuar?"):
            return

         # Limpiar editor
    editor.delete("1.0", tk.END)
    editor.edit_modified(False)

     # Limpiar consola integrada
    consola.config(state="normal")
    consola.delete("1.0", tk.END)
    consola.config(state="disabled")

    # Limpiar barra de números de línea
    lineas.config(state="normal")
    lineas.delete("1.0", tk.END)
    lineas.config(state="disabled")

    ultimo_archivo = None
    messagebox.showinfo("Limpiar", "Área de edición vacía.")



##################  UPDATER  ########################


def ejecutar_updater():
    if not UPDATER.is_file():
        messagebox.showerror(
            "Error",
            f"No se encontró el archivo: {UPDATER}"
        )
        return

    bin_updater = CARPETA_MANT / "UPDATER_ENTORNO"
    archivo_errores = CARPETA_MANT / "error.log"

    bash_cmd = f"""
    g++ {shlex.quote(str(UPDATER))} -o {shlex.quote(str(bin_updater))} 2>{shlex.quote(str(archivo_errores))}
    if [ $? -eq 0 ]; then
        echo -e "\\033[1;32m✅ Compilación exitosa. Ejecutando updater...\\033[0m"
        {shlex.quote(str(bin_updater))}
    else
        echo -e "\\033[1;31m❌ Error de compilación:\\033[0m"
        cat {shlex.quote(str(archivo_errores))}
    fi
    read -p "Presiona ENTER para cerrar..."
    """

    subprocess.Popen(
        ["konsole", "--noclose", "-e", "bash", "-c", bash_cmd],
        cwd=str(CARPETA_MANT)
    )

###################  CREAR  #######################

def crear_externo():
    # Abrir VS Code en la carpeta CARPETA_C
    try:
        subprocess.Popen(["code", str(CARPETA_C)])
        # Limpiar consola integrada
        consola.config(state="normal")
        consola.delete("1.0", tk.END)
        consola.config(state="disabled")
        print_consola(f"✅ VS Code abierto en: {CARPETA_C}", "amarillo")
    except Exception as e:
        print_consola(f"❌ Error al abrir VS Code: {e}", "rojo")



###################  CMAKE / MAKE  #######################

def _carpeta_proyecto():
    """
    Obtiene la carpeta real del proyecto.

    Prioridad:
        1. Archivo actualmente abierto.
        2. CARPETA_C.
    """

    if 'ultimo_archivo' in globals() and ultimo_archivo:
        return os.path.dirname(
            os.path.abspath(ultimo_archivo)
        )

    return os.path.abspath(
        CARPETA_C
    )


def generar_cmakelists(
    ruta_proyecto=None,
    nombre_proyecto=None
):
    """
    Genera un CMakeLists.txt profesional para el proyecto actual.

    Detecta:

        C / C++
        SDL2
        SDL2_image
        SFML
        GLFW
        GLEW
        OpenGL
        GLU
        GLUT
        FreeGLUT
        Vulkan
        GTK3
        GLAD local

    GLAD moderno:

        glad/
        ├── include/
        │   ├── glad/
        │   │   └── gl.h
        │   └── KHR/
        │       └── khrplatform.h
        │
        └── src/
            └── gl.c

    Cuando GLAD existe dentro del proyecto:

        - añade glad/src/gl.c
        - añade glad/include
        - habilita lenguaje C
        - mantiene C++
    """

    import os
    import re
    from tkinter import messagebox

    # ========================================================
    # ESTRUCTURAS
    # ========================================================

    find_packages = set()

    include_dirs = set()

    target_libs = []

    fuentes = []

    fuentes_c = []

    fuentes_cpp = []

    headers_detectados = set()

    paquetes_detectados = set()

    # ========================================================
    # RUTA DEL PROYECTO
    # ========================================================

    ruta = os.path.abspath(
        ruta_proyecto or _carpeta_proyecto()
    )

    nombre = (
        nombre_proyecto
        or os.path.basename(ruta)
        or "MiPrograma"
    )

    # ========================================================
    # ESTÁNDAR C++
    # ========================================================

    std_num = "17"

    try:

        if (
            'CPP_STD' in globals()
            and isinstance(CPP_STD, str)
            and CPP_STD.startswith("c++")
        ):
            std_num = CPP_STD.replace(
                "c++",
                ""
            )

    except Exception:
        std_num = "17"

    # ========================================================
    # COMPROBAR CARPETA
    # ========================================================

    if not os.path.isdir(ruta):

        messagebox.showerror(
            "Error",
            "La carpeta del proyecto no existe:\n\n"
            f"{ruta}"
        )

        return False

    # ========================================================
    # DETECTAR FUENTES DEL PROYECTO
    # ========================================================

    extensiones_cpp = (
        ".cpp",
        ".cc",
        ".cxx",
        ".c++"
    )

    extensiones_c = (
        ".c",
    )

    # --------------------------------------------------------
    # Buscar fuentes solamente dentro del proyecto.
    #
    # Se excluyen:
    #
    #     build/
    #     bin/
    #     .git/
    #
    # pero NO se excluye glad/
    # porque glad/src/gl.c es una dependencia local.
    # --------------------------------------------------------

    directorios_excluidos = {
        "build",
        "bin",
        ".git",
        ".svn",
        ".hg"
    }

    for root, dirs, files in os.walk(ruta):

        dirs[:] = [
            d for d in dirs
            if d not in directorios_excluidos
        ]

        for archivo in files:

            extension = os.path.splitext(
                archivo
            )[1].lower()

            ruta_fuente = os.path.join(
                root,
                archivo
            )

            # ------------------------------------------------
            # C++
            # ------------------------------------------------

            if extension in extensiones_cpp:

                rel = os.path.relpath(
                    ruta_fuente,
                    ruta
                )

                fuentes_cpp.append(
                    rel
                )

            # ------------------------------------------------
            # C
            # ------------------------------------------------

            elif extension in extensiones_c:

                rel = os.path.relpath(
                    ruta_fuente,
                    ruta
                )

                fuentes_c.append(
                    rel
                )

    # ========================================================
    # SI NO EXISTE NINGUNA FUENTE
    # ========================================================

    if not fuentes_cpp and not fuentes_c:

        messagebox.showwarning(
            "Advertencia",
            "No se encontraron archivos C/C++ en:\n\n"
            f"{ruta}"
        )

        if 'print_consola' in globals():

            print_consola(
                "\033[1;33m"
                "⚠️ No se encontraron archivos C/C++."
                "\033[0m"
            )

        return False

    # ========================================================
    # ORDENAR FUENTES
    # ========================================================

    fuentes_cpp.sort()
    fuentes_c.sort()

    fuentes.extend(
        fuentes_cpp
    )

    fuentes.extend(
        fuentes_c
    )

    # ========================================================
    # MAPA DE HEADERS
    # ========================================================

    header_map = {

        # ----------------------------------------------------
        # SDL2
        # ----------------------------------------------------

        "SDL2/SDL.h": {
            "package": "SDL2 REQUIRED",
            "include": "${SDL2_INCLUDE_DIRS}",
            "libs": "${SDL2_LIBRARIES}"
        },

        "SDL2/SDL_image.h": {
            "package": "SDL2_image REQUIRED",
            "include": "",
            "libs": "SDL2_image::SDL2_image"
        },

        # ----------------------------------------------------
        # SFML
        # ----------------------------------------------------

        "SFML/Graphics.hpp": {
            "package":
                "SFML COMPONENTS system window graphics",
            "include": "",
            "libs":
                "sfml-graphics sfml-window sfml-system"
        },

        "SFML/Audio.hpp": {
            "package":
                "SFML COMPONENTS system window graphics audio",
            "include": "",
            "libs":
                "sfml-graphics sfml-window sfml-system sfml-audio"
        },

        "SFML/Window.hpp": {
            "package":
                "SFML COMPONENTS system window graphics",
            "include": "",
            "libs":
                "sfml-graphics sfml-window sfml-system"
        },

        "SFML/System.hpp": {
            "package":
                "SFML COMPONENTS system window graphics",
            "include": "",
            "libs":
                "sfml-graphics sfml-window sfml-system"
        },

        # ----------------------------------------------------
        # GLFW
        # ----------------------------------------------------

        "GLFW/glfw3.h": {
            "package": "glfw3 REQUIRED",
            "include": "",
            "libs": "glfw"
        },

        # ----------------------------------------------------
        # GLEW
        # ----------------------------------------------------

        "GL/glew.h": {
            "package": "GLEW REQUIRED",
            "include": "${GLEW_INCLUDE_DIRS}",
            "libs": "GLEW::GLEW"
        },

        # ----------------------------------------------------
        # OpenGL
        # ----------------------------------------------------

        "GL/gl.h": {
            "package": "OpenGL REQUIRED",
            "include": "${OPENGL_INCLUDE_DIR}",
            "libs": "OpenGL::GL"
        },

        "GL/glu.h": {
            "package": "OpenGL REQUIRED",
            "include": "${OPENGL_INCLUDE_DIR}",
            "libs": "OpenGL::GLU"
        },

        # ----------------------------------------------------
        # GLUT
        # ----------------------------------------------------

        "GL/glut.h": {
            "package": "GLUT REQUIRED",
            "include": "${GLUT_INCLUDE_DIRS}",
            "libs": "${GLUT_LIBRARIES}"
        },

        # ----------------------------------------------------
        # Vulkan
        # ----------------------------------------------------

        "vulkan/vulkan.h": {
            "package": "Vulkan REQUIRED",
            "include": "",
            "libs": "Vulkan::Vulkan",
            "is_vulkan": True
        },

        # ----------------------------------------------------
        # GTK3
        # ----------------------------------------------------

        "gtk/gtk.h": {
            "package": "GTK3",
            "include": "${GTK3_INCLUDE_DIRS}",
            "libs": "${GTK3_LIBRARIES}",
            "is_pkgconfig": True
        },

        # ----------------------------------------------------
        # GLAD MODERNO
        #
        # NO es find_package().
        #
        # Es código local.
        # ----------------------------------------------------

        "glad/gl.h": {
            "local": True
        }
    }

    # ========================================================
    # ESCANEAR HEADERS
    # ========================================================

    archivos_para_escanear = []

    for root, dirs, files in os.walk(ruta):

        dirs[:] = [
            d for d in dirs
            if d not in directorios_excluidos
        ]

        for archivo in files:

            extension = os.path.splitext(
                archivo
            )[1].lower()

            if extension not in (
                ".cpp",
                ".cc",
                ".cxx",
                ".c++",
                ".c",
                ".h",
                ".hpp"
            ):
                continue

            archivos_para_escanear.append(
                os.path.join(
                    root,
                    archivo
                )
            )

    # ========================================================
    # ANALIZAR #include
    # ========================================================

    patron_include = re.compile(
        r'^\s*#\s*include\s*[<"]([^>"]+)[>"]'
    )

    for archivo in archivos_para_escanear:

        try:

            with open(
                archivo,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as f:

                for linea in f:

                    match = patron_include.match(
                        linea
                    )

                    if not match:
                        continue

                    header = match.group(
                        1
                    ).strip()

                    headers_detectados.add(
                        header
                    )

        except Exception:
            continue

        # ========================================================
    # DETECTAR VULKAN
    #
    # Vulkan puede utilizarse de varias formas:
    #
    #   1. #include <vulkan/vulkan.h>
    #
    #   2. #define GLFW_INCLUDE_VULKAN
    #      #include <GLFW/glfw3.h>
    #
    #   3. Uso directo de tipos/API Vulkan.
    #
    # Esto evita que un proyecto GLFW + Vulkan sea detectado
    # únicamente como GLFW.
    # ========================================================

    vulkan_detectado = False

    # --------------------------------------------------------
    # Caso 1:
    # include directo
    # --------------------------------------------------------

    if "vulkan/vulkan.h" in headers_detectados:

        vulkan_detectado = True

    # --------------------------------------------------------
    # Analizar contenido fuente para detectar Vulkan
    # --------------------------------------------------------

    simbolos_vulkan = (
        "VkInstance",
        "VkPhysicalDevice",
        "VkDevice",
        "VkQueue",
        "VkSurfaceKHR",
        "VkSwapchainKHR",
        "VkCommandBuffer",
        "VkImage",
        "VkImageView",
        "VkBuffer",
        "VkShaderModule",

        "vkCreateInstance",
        "vkEnumeratePhysicalDevices",
        "vkCreateDevice",
        "vkGetDeviceQueue",
        "vkCreateSwapchainKHR",
        "vkGetSwapchainImagesKHR",
        "vkAcquireNextImageKHR",
        "vkQueuePresentKHR",
        "vkQueueSubmit",
        "vkDeviceWaitIdle",
        "vkDestroyInstance",
        "vkDestroyDevice",

        "VK_KHR_surface",
        "VK_KHR_swapchain",
        "VK_API_VERSION_1_0",
        "VK_API_VERSION_1_1",
        "VK_API_VERSION_1_2",
        "VK_API_VERSION_1_3",
        "VK_API_VERSION_1_4"
    )

    # --------------------------------------------------------
    # GLFW_INCLUDE_VULKAN
    # --------------------------------------------------------

    glfw_vulkan_detectado = False

    # --------------------------------------------------------
    # Leer archivos C/C++
    # --------------------------------------------------------

    for archivo in archivos_para_escanear:

        try:

            with open(
                archivo,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as f:

                contenido_archivo = f.read()

        except Exception:

            continue

        # ----------------------------------------------------
        # GLFW_INCLUDE_VULKAN
        # ----------------------------------------------------

        if "GLFW_INCLUDE_VULKAN" in contenido_archivo:

            glfw_vulkan_detectado = True
            vulkan_detectado = True

        # ----------------------------------------------------
        # API Vulkan
        # ----------------------------------------------------

        if not vulkan_detectado:

            for simbolo in simbolos_vulkan:

                if simbolo in contenido_archivo:

                    vulkan_detectado = True
                    break

    # --------------------------------------------------------
    # Registrar Vulkan como dependencia
    # --------------------------------------------------------

    if vulkan_detectado:

        headers_detectados.add(
            "vulkan/vulkan.h"
        )

    # ========================================================
    # DETECTAR GLAD LOCAL
    # ========================================================

    glad_header = os.path.join(
        ruta,
        "glad",
        "include",
        "glad",
        "gl.h"
    )

    glad_source = os.path.join(
        ruta,
        "glad",
        "src",
        "gl.c"
    )

    glad_include = os.path.join(
        ruta,
        "glad",
        "include"
    )

    glad_detectado = (

        "glad/gl.h" in headers_detectados
        and
        os.path.isfile(glad_header)
        and
        os.path.isfile(glad_source)
    )

    # ========================================================
    # PROCESAR HEADERS
    # ========================================================

    for header in headers_detectados:

        data = header_map.get(
            header
        )

        if not data:
            continue

        # ----------------------------------------------------
        # GLAD LOCAL
        # ----------------------------------------------------

        if data.get("local"):

            continue

        # ----------------------------------------------------
        # PKGCONFIG
        # ----------------------------------------------------

        if data.get("is_pkgconfig"):

            find_packages.add(
                "find_package(PkgConfig REQUIRED)"
            )

            find_packages.add(
                "pkg_check_modules("
                "GTK3 REQUIRED gtk+-3.0)"
            )

            paquetes_detectados.add(
                "GTK3"
            )

        else:

            paquete = data["package"]

            # ------------------------------------------------
            # SFML puede aparecer repetido.
            # ------------------------------------------------

            if paquete.startswith(
                "SFML COMPONENTS"
            ):

                find_packages.add(
                    "find_package("
                    f"{paquete}"
                    ")"
                )

            else:

                find_packages.add(
                    f"find_package({paquete})"
                )

            paquetes_detectados.add(
                paquete
            )

        # ----------------------------------------------------
        # INCLUDE
        # ----------------------------------------------------

        include = data.get(
            "include"
        )

        if include:

            include_dirs.add(
                include
            )

    # ========================================================
    # AÑADIR GLAD
    # ========================================================

    if glad_detectado:

        # ----------------------------------------------------
        # Include local
        # ----------------------------------------------------

        include_dirs.add(
            "${PROJECT_SOURCE_DIR}/glad/include"
        )

        # ----------------------------------------------------
        # gl.c
        # ----------------------------------------------------

        glad_source_rel = os.path.relpath(
            glad_source,
            ruta
        )

        glad_source_rel = glad_source_rel.replace(
            os.sep,
            "/"
        )

        if glad_source_rel not in fuentes:

            fuentes.append(
                glad_source_rel
            )

        if glad_source_rel not in fuentes_c:

            fuentes_c.append(
                glad_source_rel
            )

        # ----------------------------------------------------
        # GLAD necesita C
        # ----------------------------------------------------

        paquetes_detectados.add(
            "GLAD local"
        )

    # ========================================================
    # LIBRERÍAS
    # ========================================================

    lib_priority = [

        "SDL2/SDL.h",

        "SDL2/SDL_image.h",

        "SFML/Graphics.hpp",

        "SFML/Audio.hpp",

        "GLFW/glfw3.h",

        "GL/glew.h",

        "GL/gl.h",

        "GL/glu.h",

        "GL/glut.h",

        "vulkan/vulkan.h"
    ]

    # ========================================================
    # AGREGAR LIBRERÍAS EN ORDEN
    # ========================================================

    for header in lib_priority:

        if header not in headers_detectados:
            continue

        data = header_map.get(
            header
        )

        if not data:
            continue

        lib = data.get(
            "libs"
        )

        if not lib:
            continue

        if lib not in target_libs:

            target_libs.append(
                lib
            )

    # ========================================================
    # OPENGL AUTOMÁTICO PARA GLFW + GLAD
    # ========================================================

    if glad_detectado:

        if "OpenGL REQUIRED" not in paquetes_detectados:

            find_packages.add(
                "find_package(OpenGL REQUIRED)"
            )

        if "OpenGL::GL" not in target_libs:

            target_libs.append(
                "OpenGL::GL"
            )

        paquetes_detectados.add(
            "OpenGL REQUIRED"
        )

    # ========================================================
    # OPENGL PARA GLEW
    # ========================================================

    if "GL/glew.h" in headers_detectados:

        find_packages.add(
            "find_package(OpenGL REQUIRED)"
        )

        if "OpenGL::GL" not in target_libs:

            target_libs.append(
                "OpenGL::GL"
            )

    # ========================================================
    # OPENGL PARA GL
    # ========================================================

    if "GL/gl.h" in headers_detectados:

        find_packages.add(
            "find_package(OpenGL REQUIRED)"
        )

    # ========================================================
    # GLU
    # ========================================================

    if "GL/glu.h" in headers_detectados:

        find_packages.add(
            "find_package(OpenGL REQUIRED)"
        )

        if "OpenGL::GLU" not in target_libs:

            target_libs.append(
                "OpenGL::GLU"
            )

    # ========================================================
    # DETERMINAR LENGUAJES
    # ========================================================

    usa_c = bool(
        fuentes_c
    )

    usa_cpp = bool(
        fuentes_cpp
    )

    if usa_c and usa_cpp:

        cmake_languages = (
            "LANGUAGES C CXX"
        )

    elif usa_c:

        cmake_languages = (
            "LANGUAGES C"
        )

    else:

        cmake_languages = (
            "LANGUAGES CXX"
        )

    # ========================================================
    # ELIMINAR DUPLICADOS DE FUENTES
    # ========================================================

    fuentes_finales = []

    for fuente in fuentes:

        fuente = fuente.replace(
            os.sep,
            "/"
        )

        if fuente not in fuentes_finales:

            fuentes_finales.append(
                fuente
            )

    # ========================================================
    # CONSTRUIR CMAKE
    # ========================================================

    cmake = []

    cmake.append(
        "cmake_minimum_required(VERSION 3.15)"
    )

    cmake.append("")

    cmake.append(
        f"project({nombre}"
    )

    cmake.append(
        "    VERSION 1.0"
    )

    cmake.append(
        f"    {cmake_languages}"
    )

    cmake.append(
        ")"
    )

    cmake.append("")

    # ========================================================
    # CONFIGURACIÓN
    # ========================================================

    cmake.append(
        "# ============================================================"
    )

    cmake.append(
        "# CONFIGURACIÓN DEL COMPILADOR"
    )

    cmake.append(
        "# ============================================================"
    )

    cmake.append("")

    cmake.append(
        f"set(CMAKE_CXX_STANDARD {std_num})"
    )

    cmake.append(
        "set(CMAKE_CXX_STANDARD_REQUIRED ON)"
    )

    cmake.append(
        "set(CMAKE_CXX_EXTENSIONS OFF)"
    )

    cmake.append("")

    # ========================================================
    # BIN
    # ========================================================

    cmake.append(
        "# ============================================================"
    )

    cmake.append(
        "# DIRECTORIO DEL EJECUTABLE"
    )

    cmake.append(
        "# ============================================================"
    )

    cmake.append("")

    cmake.append(
        "set(CMAKE_RUNTIME_OUTPUT_DIRECTORY"
    )

    cmake.append(
        "    ${PROJECT_SOURCE_DIR}/bin"
    )

    cmake.append(
        ")"
    )

    cmake.append("")

    # ========================================================
    # FUENTES
    # ========================================================

    cmake.append(
        "# ============================================================"
    )

    cmake.append(
        "# FUENTES"
    )

    cmake.append(
        "# ============================================================"
    )

    cmake.append("")

    cmake.append(
        "set(SOURCES"
    )

    for fuente in fuentes_finales:

        cmake.append(
            f"    {fuente}"
        )

    cmake.append(
        ")"
    )

    cmake.append("")

    # ========================================================
    # DEPENDENCIAS
    # ========================================================

    if find_packages:

        cmake.append(
            "# ============================================================"
        )

        cmake.append(
            "# DEPENDENCIAS"
        )

        cmake.append(
            "# ============================================================"
        )

        cmake.append("")

        for paquete in sorted(
            find_packages
        ):

            cmake.append(
                paquete
            )

        cmake.append("")

    # ========================================================
    # EJECUTABLE
    # ========================================================

    cmake.append(
        "# ============================================================"
    )

    cmake.append(
        "# EJECUTABLE"
    )

    cmake.append(
        "# ============================================================"
    )

    cmake.append("")

    cmake.append(
        "add_executable("
        "${PROJECT_NAME}"
    )

    cmake.append(
        "    ${SOURCES}"
    )

    cmake.append(
        ")"
    )

    cmake.append("")

    # ========================================================
    # INCLUDES
    # ========================================================

    if include_dirs:

        cmake.append(
            "# ============================================================"
        )

        cmake.append(
            "# DIRECTORIOS DE INCLUSIÓN"
        )

        cmake.append(
            "# ============================================================"
        )

        cmake.append("")

        cmake.append(
            "target_include_directories("
            "${PROJECT_NAME}"
        )

        cmake.append(
            "    PRIVATE"
        )

        for include in sorted(
            include_dirs
        ):

            cmake.append(
                f"        {include}"
            )

        cmake.append(
            ")"
        )

        cmake.append("")

    # ========================================================
    # LIBRERÍAS
    # ========================================================

    if target_libs:

        cmake.append(
            "# ============================================================"
        )

        cmake.append(
            "# LIBRERÍAS"
        )

        cmake.append(
            "# ============================================================"
        )

        cmake.append("")

        cmake.append(
            "target_link_libraries("
            "${PROJECT_NAME}"
        )

        cmake.append(
            "    PRIVATE"
        )

        for lib in target_libs:

            cmake.append(
                f"        {lib}"
            )

        cmake.append(
            ")"
        )

        cmake.append("")

    # ========================================================
    # COMPILADOR
    # ========================================================

    cmake.append(
        "# ============================================================"
    )

    cmake.append(
        "# OPCIONES DEL COMPILADOR"
    )

    cmake.append(
        "# ============================================================"
    )

    cmake.append("")

    cmake.append(
        'if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")'
    )

    cmake.append(
        "    target_compile_options("
        "${PROJECT_NAME}"
    )

    cmake.append(
        "        PRIVATE"
    )

    cmake.append(
        "            -Wall"
    )

    cmake.append(
        "            -Wextra"
    )

    cmake.append(
        "            -Wpedantic"
    )

    cmake.append(
        "            -O2"
    )

    cmake.append(
        "    )"
    )

    cmake.append(
        "endif()"
    )

    cmake.append("")

    # ========================================================
    # INFORMACIÓN
    # ========================================================

    cmake.append(
        "# ============================================================"
    )

    cmake.append(
        "# INFORMACIÓN"
    )

    cmake.append(
        "# ============================================================"
    )

    cmake.append("")

    cmake.append(
        'message(STATUS "==========================================")'
    )

    cmake.append(
        f'message(STATUS " Proyecto: {nombre}")'
    )

    cmake.append(
        f'message(STATUS " C++:      {std_num}")'
    )

    if glad_detectado:

        cmake.append(
            'message(STATUS " GLAD:     proyecto local")'
        )

        cmake.append(
            'message(STATUS " GLAD:     glad/src/gl.c")'
        )

    if "GLFW/glfw3.h" in headers_detectados:

        cmake.append(
            'message(STATUS " GLFW:     encontrado")'
        )

    if "SDL2/SDL.h" in headers_detectados:

        cmake.append(
            'message(STATUS " SDL2:     encontrado")'
        )

    if "SFML/Graphics.hpp" in headers_detectados:

        cmake.append(
            'message(STATUS " SFML:     encontrado")'
        )

    cmake.append(
        'message(STATUS "==========================================")'
    )

    cmake.append("")

    cmake_content = "\n".join(
        cmake
    )

    # ========================================================
    # GUARDAR
    # ========================================================

    cmake_path = os.path.join(
        ruta,
        "CMakeLists.txt"
    )

    try:

        with open(
            cmake_path,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                cmake_content
            )

    except Exception as e:

        messagebox.showerror(
            "Error",
            "No se pudo escribir:\n\n"
            f"{cmake_path}\n\n"
            f"{e}"
        )

        if 'print_consola' in globals():

            print_consola(
                "\033[1;31m"
                f"❌ Error escribiendo CMakeLists.txt: {e}"
                "\033[0m"
            )

        return False

    # ========================================================
    # CONSOLA IDE
    # ========================================================

    if 'print_consola' in globals():

        print_consola(
            "\033[1;32m"
            f"✅ CMakeLists.txt generado en: "
            f"{cmake_path}"
            "\033[0m"
        )

        print_consola(
            "\033[1;34m"
            "🔎 Fuentes detectadas: "
            f"{', '.join(fuentes_finales)}"
            "\033[0m"
        )

        if headers_detectados:

            print_consola(
                "\033[1;35m"
                "📦 Headers detectados: "
                f"{', '.join(sorted(headers_detectados))}"
                "\033[0m"
            )

        if glad_detectado:

            print_consola(
                "\033[1;32m"
                "🧩 GLAD local detectado:"
                "\033[0m"
            )

            print_consola(
                "\033[1;36m"
                "   📁 glad/include"
                "\033[0m"
            )

            print_consola(
                "\033[1;36m"
                "   📄 glad/src/gl.c"
                "\033[0m"
            )

        if target_libs:

            libs_str = ", ".join(
                target_libs
            )

            print_consola(
                "\033[1;36m"
                f"🔧 Librerías detectadas: {libs_str}"
                "\033[0m"
            )

        if find_packages:

            print_consola(
                "\033[1;33m"
                "🔎 Paquetes CMake: "
                f"{', '.join(sorted(find_packages))}"
                "\033[0m"
            )

    messagebox.showinfo(
        "CMake",
        "CMakeLists.txt generado correctamente:\n\n"
        f"{cmake_path}"
    )

    return True


# ============================================================
# BOTÓN CMAKE
# ============================================================

def make():
    """
    Callback del botón CMake (F3).
    """

    return generar_cmakelists()
###################  BUILD  #######################

def _nombre_proyecto(ruta):
    return os.path.basename(os.path.abspath(ruta)) or "MiPrograma"


def _nombre_objetivo_cmake(contenido, predeterminado):
    """Obtiene el nombre del primer objetivo ejecutable de CMake."""

    proyecto = re.search(
        r"(?im)^\s*project\s*\(\s*([A-Za-z_][A-Za-z0-9_.+-]*)",
        contenido,
    )

    nombre_proyecto = proyecto.group(1) if proyecto else predeterminado

    objetivo = re.search(
        r"(?is)\badd_executable\s*\(\s*([^\s()]+)",
        contenido,
    )

    if not objetivo:
        return nombre_proyecto

    nombre = objetivo.group(1).strip()

    if nombre.upper() == "${PROJECT_NAME}":
        return nombre_proyecto

    if nombre.startswith("${"):
        return nombre_proyecto

    return nombre


def build():

    """
    Genera la carpeta build/, configura y compila con CMake.
    - Detecta si es un proyecto BGFX (busca CMakeLists.txt con include bgfx)
    - Para BGFX, binario se genera en 'bin/'
    - Los ejecutables se esperan en bin/
    - Muestra salida línea por línea en consola integrada
    """
    ruta = os.path.abspath(_carpeta_proyecto())
    nombre_proyecto = _nombre_proyecto(ruta)
    build_dir = os.path.join(ruta, "build")
    os.makedirs(build_dir, exist_ok=True)

    def _run():
        try:
            cmakelists_path = os.path.join(ruta, "CMakeLists.txt")
            es_bgfx = False

            if not os.path.exists(cmakelists_path):
                if 'print_consola' in globals():
                    print_consola("\033[1;33m⚠️ No existe CMakeLists.txt, generando...\033[0m")
                ok = generar_cmakelists(ruta_proyecto=ruta, nombre_proyecto=nombre_proyecto)
                if not ok:
                    messagebox.showerror("Error", "No se pudo generar CMakeLists.txt.")
                    return

            # Detectar si es un proyecto BGFX buscando "include/bgfx" en CMakeLists
            with open(cmakelists_path, "r") as f:
                contenido = f.read()
                if "bgfx" in contenido.lower():
                    es_bgfx = True

            # Configurar CMake
            cmd_configure = f"cmake -S {shlex.quote(ruta)} -B {shlex.quote(build_dir)}"
            print_consola(f"\033[1;34m▶ {cmd_configure}\033[0m")
            p1 = subprocess.Popen(cmd_configure, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=ruta)
            for line in p1.stdout:
                print_consola(line.rstrip())
            for line in p1.stderr:
                print_consola(line.rstrip())
            p1.wait()
            if p1.returncode != 0:
                print_consola("\033[1;31m❌ Error en configuración CMake.\033[0m")
                messagebox.showerror("Build", "❌ Error en configuración CMake")
                return

            # Compilar con CMake
            cmd_build = f"cmake --build {shlex.quote(build_dir)} --parallel"
            print_consola(f"\033[1;34m▶ {cmd_build}\033[0m")
            p2 = subprocess.Popen(cmd_build, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=ruta)
            for line in p2.stdout:
                print_consola(line.rstrip())
            for line in p2.stderr:
                print_consola(line.rstrip())
            p2.wait()
            if p2.returncode != 0:
                print_consola("\033[1;31m❌ Error en compilación.\033[0m")
                messagebox.showerror("Build", "❌ Error en compilación")
                return

            # Todos los ejecutables de IDEC deben estar en bin/.
            bin_dir = os.path.join(ruta, "bin")
            nombre_objetivo = _nombre_objetivo_cmake(
                contenido, nombre_proyecto
            )
            bin_path = os.path.join(bin_dir, nombre_objetivo)

            if os.path.isfile(bin_path):
                print_consola(f"\033[1;32m✅ Build completado. Binario: {bin_path}\033[0m")
                messagebox.showinfo("Build", f"✅ Build completado.\nBinario:\n{bin_path}")
            else:
                print_consola("\033[1;33m⚠️ Build completado, pero no se encontró el binario esperado.\033[0m")
                messagebox.showwarning("Build", "⚠️ Build completado, pero no se encontró el binario esperado.")

        except Exception as e:
            print_consola(f"\033[1;31m❌ Excepción en build: {e}\033[0m")
            messagebox.showerror("Build", f"❌ Excepción en build:\n{e}")

    threading.Thread(target=_run, daemon=True).start()



###################  COMPILAR  #######################

import os
import shlex
import subprocess
import threading
import re
import tkinter as tk
from tkinter import messagebox


# ============================================================
# CONFIGURACIÓN
# ============================================================

CPP_STD = "c++17"

# CARPETA_C se define una sola vez al inicio del archivo



# ============================================================
# UTILIDADES
# ============================================================

def _pkg_config(paquetes):
    """
    Ejecuta pkg-config y devuelve:
        --cflags --libs

    paquetes:
        str
        o
        lista de paquetes

    Ejemplo:

        _pkg_config(
            ["sfml-graphics", "sfml-window", "sfml-system"]
        )
    """

    if isinstance(paquetes, str):
        paquetes = [paquetes]

    try:
        resultado = subprocess.run(
            ["pkg-config", "--cflags", "--libs", *paquetes],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        return resultado.stdout.strip()

    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def _pkg_config_disponible(paquetes):
    """
    Comprueba si un paquete/pkg-config existe.
    """

    if isinstance(paquetes, str):
        paquetes = [paquetes]

    try:
        resultado = subprocess.run(
            ["pkg-config", "--exists", *paquetes],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        return resultado.returncode == 0

    except FileNotFoundError:
        return False


# ============================================================
# DETECCIÓN DE LIBRERÍAS
# ============================================================

def _detectar_libs(contenido: str) -> str:
    """
    Detecta automáticamente las bibliotecas necesarias
    observando los #include del archivo C/C++.

    IMPORTANTE:

    SFML:
        Se utiliza pkg-config.

    OpenGL:
        Solo se agregan las bibliotecas si el código
        realmente incluye OpenGL.

    No se agrega GLEW automáticamente a SFML.

    Esto evita errores como:

        cannot find -lGLEW
        cannot find -lGLU
    """

    libs_ordered = []
    libs_set = set()

    def agregar(lib):
        if not lib:
            return

        if lib not in libs_set:
            libs_set.add(lib)
            libs_ordered.append(lib)


    # ========================================================
    # DETECCIÓN SFML
    # ========================================================

    sfml_detected = (
        "#include <SFML/" in contenido
    )


    sfml_audio = (
        "#include <SFML/Audio.hpp>" in contenido
    )


    sfml_network = (
        "#include <SFML/Network.hpp>" in contenido
    )


    if sfml_detected:

        paquetes_sfml = [
            "sfml-graphics",
            "sfml-window",
            "sfml-system"
        ]

        if sfml_audio:
            paquetes_sfml.append("sfml-audio")

        if sfml_network:
            paquetes_sfml.append("sfml-network")


        flags_sfml = _pkg_config(
            paquetes_sfml
        )


        if flags_sfml:

            for elemento in shlex.split(flags_sfml):
                agregar(elemento)

        else:

            # ------------------------------------------------
            # FALLBACK
            # ------------------------------------------------
            #
            # Si pkg-config no está disponible, utilizamos
            # las bibliotecas tradicionales.
            #

            agregar("-lsfml-graphics")
            agregar("-lsfml-window")
            agregar("-lsfml-system")

            if sfml_audio:
                agregar("-lsfml-audio")

            if sfml_network:
                agregar("-lsfml-network")


    # ========================================================
    # SDL2
    # ========================================================

    if "#include <SDL2/" in contenido:

        flags_sdl = _pkg_config("sdl2")

        if flags_sdl:

            for elemento in shlex.split(flags_sdl):
                agregar(elemento)

        else:

            agregar("-lSDL2")


    if "#include <SDL2/SDL_image.h>" in contenido:
        agregar("-lSDL2_image")


    if "#include <SDL2/SDL_ttf.h>" in contenido:
        agregar("-lSDL2_ttf")


    if "#include <SDL2/SDL_mixer.h>" in contenido:
        agregar("-lSDL2_mixer")


    # ========================================================
    # GLUT / OPENGL
    # ========================================================

    glut_detected = (
        "#include <GL/glut.h>" in contenido
    )

    glew_detected = (
        "#include <GL/glew.h>" in contenido
    )

    opengl_detected = (
        "#include <GL/gl.h>" in contenido
        or
        glut_detected
        or
        glew_detected
    )


    # --------------------------------------------------------
    # OpenGL puro
    # --------------------------------------------------------

    if opengl_detected:

        agregar("-lGL")


    # --------------------------------------------------------
    # GLU
    #
    # SOLO si el código realmente utiliza GLU.
    # --------------------------------------------------------

    if (
        "#include <GL/glu.h>" in contenido
        or
        glut_detected
    ):
        agregar("-lGLU")


    # --------------------------------------------------------
    # GLEW
    #
    # SOLO si el usuario incluye explícitamente:
    #
    # #include <GL/glew.h>
    # --------------------------------------------------------

    if glew_detected:

        if _pkg_config_disponible("glew"):

            flags_glew = _pkg_config("glew")

            for elemento in shlex.split(flags_glew):
                agregar(elemento)

        else:

            agregar("-lGLEW")


    # --------------------------------------------------------
    # GLUT
    # --------------------------------------------------------

    if glut_detected:

        agregar("-lglut")


    # ========================================================
    # GLFW
    # ========================================================

    if "#include <GLFW/glfw3.h>" in contenido:

        flags_glfw = _pkg_config("glfw3")

        if flags_glfw:

            for elemento in shlex.split(flags_glfw):
                agregar(elemento)

        else:

            agregar("-lglfw")
            agregar("-lGL")


    # ========================================================
    # FLTK
    # ========================================================

    if "#include <FL/" in contenido:

        agregar("-lfltk")
        agregar("-lX11")


    # ========================================================
    # VULKAN
    # ========================================================

    if "#include <vulkan/vulkan.h>" in contenido:

        flags_vulkan = _pkg_config("vulkan")

        if flags_vulkan:

            for elemento in shlex.split(flags_vulkan):
                agregar(elemento)

        else:

            agregar("-lvulkan")
            agregar("-lglfw")
            agregar("-lxcb")
            agregar("-lxcb-keysyms")
            agregar("-lxcb-image")
            agregar("-lxcb-shm")
            agregar("-lxcb-icccm")
            agregar("-lxcb-ewmh")
            agregar("-lxcb-randr")


    # ========================================================
    # XCB
    # ========================================================

    if "#include <xcb/" in contenido:

        agregar("-lxcb")
        agregar("-lxcb-keysyms")
        agregar("-lxcb-image")
        agregar("-lxcb-shm")
        agregar("-lxcb-icccm")
        agregar("-lxcb-ewmh")
        agregar("-lxcb-randr")


    # ========================================================
    # ALLEGRO
    # ========================================================

    if "#include <allegro5/allegro.h>" in contenido:

        agregar("-lallegro")
        agregar("-lallegro_main")
        agregar("-lallegro_primitives")


    # ========================================================
    # RAYLIB
    # ========================================================

    if "#include <raylib.h>" in contenido:

        flags_raylib = _pkg_config("raylib")

        if flags_raylib:

            for elemento in shlex.split(flags_raylib):
                agregar(elemento)

        else:

            agregar("-lraylib")


    # ========================================================
    # QT5
    # ========================================================

    if "#include <QApplication>" in contenido:

        flags_qt = _pkg_config(
            "Qt5Widgets"
        )

        if flags_qt:

            for elemento in shlex.split(flags_qt):
                agregar(elemento)


    # ========================================================
    # GTK3
    # ========================================================

    if "#include <gtk/gtk.h>" in contenido:

        flags_gtk = _pkg_config(
            "gtk+-3.0"
        )

        if flags_gtk:

            for elemento in shlex.split(flags_gtk):
                agregar(elemento)


    # ========================================================
    # GTKMM 4
    # ========================================================

    if "#include <gtkmm.h>" in contenido:

        flags_gtkmm = _pkg_config(
            "gtkmm-4.0"
        )

        if flags_gtkmm:

            for elemento in shlex.split(flags_gtkmm):
                agregar(elemento)


    # ========================================================
    # OPENCV
    # ========================================================

    if "#include <opencv2/" in contenido:

        flags_opencv = _pkg_config(
            "opencv4"
        )

        if flags_opencv:

            for elemento in shlex.split(flags_opencv):
                agregar(elemento)


    # ========================================================
    # FFMPEG
    # ========================================================

    ffmpeg_headers = (
        "#include <libavcodec/" in contenido
        or
        "#include <libavformat/" in contenido
        or
        "#include <libavutil/" in contenido
    )


    if ffmpeg_headers:

        flags_ffmpeg = _pkg_config(
            [
                "libavcodec",
                "libavformat",
                "libavutil"
            ]
        )

        if flags_ffmpeg:

            for elemento in shlex.split(flags_ffmpeg):
                agregar(elemento)


    # ========================================================
    # GSTREAMER
    # ========================================================

    if "#include <gst/gst.h>" in contenido:

        flags_gstreamer = _pkg_config(
            "gstreamer-1.0"
        )

        if flags_gstreamer:

            for elemento in shlex.split(flags_gstreamer):
                agregar(elemento)


    # ========================================================
    # OGRE
    # ========================================================

    if "#include <Ogre.h>" in contenido:

        flags_ogre = _pkg_config("OGRE")

        if flags_ogre:

            for elemento in shlex.split(flags_ogre):
                agregar(elemento)


    # ========================================================
    # IRRLICHT
    # ========================================================

    if "#include <irrlicht.h>" in contenido:

        agregar("-lIrrlicht")


    # ========================================================
    # MAGNUM
    # ========================================================

    if "#include <Magnum/" in contenido:

        flags_magnum = _pkg_config("Magnum")

        if flags_magnum:

            for elemento in shlex.split(flags_magnum):
                agregar(elemento)


    # ========================================================
    # DIRECT3D
    # ========================================================

    if "#include <d3d11.h>" in contenido:

        agregar("-ld3d11")
        agregar("-ldxgi")
        agregar("-ld3dcompiler")


    # ========================================================
    # METAL
    # ========================================================

    if "#include <Metal/Metal.h>" in contenido:

        agregar("-framework")
        agregar("Metal")

        agregar("-framework")
        agregar("QuartzCore")


    # ========================================================
    # RESULTADO
    # ========================================================

    return " ".join(libs_ordered)


# ============================================================
# QT
# ============================================================

def obtener_flags_qt():

    try:

        cflags = subprocess.check_output(
            [
                "pkg-config",
                "--cflags",
                "Qt5Widgets"
            ],
            text=True
        ).strip()


        libs = subprocess.check_output(
            [
                "pkg-config",
                "--libs",
                "Qt5Widgets"
            ],
            text=True
        ).strip()


        return f"{cflags} {libs}"


    except (
        subprocess.CalledProcessError,
        FileNotFoundError
    ):

        return ""


# ============================================================
# FUNCIÓN COMPILAR
# ============================================================

def compilar():

    global ultimo_archivo


    # --------------------------------------------------------
    # COMPROBAR ARCHIVO
    # --------------------------------------------------------

    if not ultimo_archivo:

        messagebox.showwarning(
            "Error",
            "Primero guarda o abre un archivo"
        )

        return


    # --------------------------------------------------------
    # CARPETA DEL PROYECTO
    # --------------------------------------------------------

    ruta_proyecto = os.path.dirname(
        os.path.abspath(
            ultimo_archivo
        )
    )


    # --------------------------------------------------------
    # NOMBRE DEL EJECUTABLE
    # --------------------------------------------------------

    nombre_salida = os.path.splitext(
        os.path.basename(
            ultimo_archivo
        )
    )[0]


    # --------------------------------------------------------
    # CARPETA BIN
    # --------------------------------------------------------

    ruta_bin = os.path.join(
        ruta_proyecto,
        "bin"
    )


    os.makedirs(
        ruta_bin,
        exist_ok=True
    )


    # --------------------------------------------------------
    # EJECUTABLE
    # --------------------------------------------------------

    salida = os.path.join(
        ruta_bin,
        nombre_salida
    )


    # --------------------------------------------------------
    # COMPILADOR
    # --------------------------------------------------------

    extension = (
        os.path.splitext(
            ultimo_archivo
        )[1].lower()
    )


    if extension == ".c":

        compilador = "gcc"

        flags = "-O2 -g -Wall"


    elif extension in (".cpp", ".cc", ".cxx"):

        compilador = "g++"

        flags = (
            f"-std={CPP_STD} "
            "-O2 "
            "-g "
            "-Wall"
        )


    else:

        messagebox.showerror(
            "Error",
            "Archivo no reconocido.\n\n"
            "Extensiones soportadas:\n"
            ".c\n"
            ".cpp\n"
            ".cc\n"
            ".cxx"
        )

        return


    # --------------------------------------------------------
    # LEER CÓDIGO
    # --------------------------------------------------------

    try:

        with open(
            ultimo_archivo,
            "r",
            encoding="utf-8"
        ) as f:

            contenido = f.read()


    except Exception as e:

        messagebox.showerror(
            "Error",
            f"No se pudo leer el archivo:\n\n{e}"
        )

        return


    # --------------------------------------------------------
    # DETECTAR LIBRERÍAS
    # --------------------------------------------------------

    libs = _detectar_libs(
        contenido
    )


    # --------------------------------------------------------
    # QT
    # --------------------------------------------------------

    if "#include <QApplication>" in contenido:

        flags += " -fPIC"

        libs_qt = obtener_flags_qt()

        if libs_qt:

            libs = libs_qt


    # --------------------------------------------------------
    # COMANDO FINAL
    # --------------------------------------------------------

    partes_cmd = [
        compilador,
        shlex.quote(ultimo_archivo),
        "-o",
        shlex.quote(salida),
        flags
    ]


    if libs:

        partes_cmd.append(
            libs
        )


    cmd = " ".join(
        partes_cmd
    )


    # ========================================================
    # HILO DE COMPILACIÓN
    # ========================================================

    def run_compile():

        print_consola(
            f"\033[1;34m"
            f"Compilando:\n{cmd}"
            f"\033[0m"
        )


        try:

            proceso = subprocess.Popen(

                cmd,

                shell=True,

                stdout=subprocess.PIPE,

                stderr=subprocess.PIPE,

                cwd=ruta_proyecto,

                text=True,

                bufsize=1

            )


            # ------------------------------------------------
            # STDOUT
            # ------------------------------------------------

            for linea in proceso.stdout:

                print_consola(
                    linea.rstrip()
                )


            # ------------------------------------------------
            # STDERR
            # ------------------------------------------------

            for linea in proceso.stderr:

                print_consola(
                    linea.rstrip()
                )


            proceso.wait()


            # ------------------------------------------------
            # RESULTADO
            # ------------------------------------------------

            if proceso.returncode == 0:

                print_consola(
                    "\033[1;32m"
                    "================================================\n"
                    "✅ COMPILACIÓN EXITOSA\n"
                    f"📦 Binario: {salida}\n"
                    "================================================"
                    "\033[0m"
                )


            else:

                print_consola(
                    "\033[1;31m"
                    "================================================\n"
                    "❌ ERROR DE COMPILACIÓN\n"
                    "================================================"
                    "\033[0m"
                )


        except Exception as e:

            print_consola(
                "\033[1;31m"
                f"❌ Error ejecutando compilador: {e}"
                "\033[0m"
            )


    # --------------------------------------------------------
    # LANZAR HILO
    # --------------------------------------------------------

    threading.Thread(
        target=run_compile,
        daemon=True
    ).start()
##################  DEPURAR  ########################
def depurar():
    global ultimo_archivo
    if not ultimo_archivo:
        messagebox.showwarning("Error", "Primero guarda o abre un archivo")
        return

    ruta_proyecto = os.path.dirname(os.path.abspath(ultimo_archivo))
    nombre_salida = os.path.splitext(os.path.basename(ultimo_archivo))[0]
    ruta_bin = os.path.join(ruta_proyecto, "bin")
    os.makedirs(ruta_bin, exist_ok=True)
    salida = os.path.join(ruta_bin, nombre_salida)

    # Detectar compilador
    if ultimo_archivo.endswith(".c"):
        compilador = "gcc"
    elif ultimo_archivo.endswith(".cpp"):
        compilador = "g++"
    else:
        messagebox.showerror("Error", "Archivo no reconocido (solo .c o .cpp)")
        return

    # Leer librerías
    try:
        with open(ultimo_archivo, "r", encoding="utf-8", errors="ignore") as f:
            contenido = f.read()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo leer el archivo:\n{e}")
        return

    libs = _detectar_libs(contenido)

    # Línea de compilación con símbolos de depuración
    cmd_compile = f"{compilador} -g {shlex.quote(ultimo_archivo)} -o {shlex.quote(salida)} {libs}"

    def run_debug():
        print_consola(f"\033[1;34mCompilando para depuración: {cmd_compile}\033[0m")
        proceso = subprocess.Popen(
            cmd_compile,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=ruta_proyecto,
            text=True
        )

        # Mostrar salida de compilación
        for linea in proceso.stdout:
            print_consola(linea.rstrip())
        for linea in proceso.stderr:
            print_consola(linea.rstrip())

        proceso.wait()
        if proceso.returncode != 0:
            print_consola("\033[1;31m❌ Error de compilación para depuración\033[0m")
            return

        # ✅ Compilación exitosa
        print_consola(f"\033[1;32m✅ Compilación exitosa.\033[0m")
        print_consola(f"\033[1;33m⚡ Abriendo GDB en una konsole real...\033[0m")
        print_consola("\033[34m##################  DEPURAR  ########################\033[0m")

        # === Nivel 1: Comandos básicos ===
        print_consola("\033[36m📘 NIVEL 1: COMANDOS BÁSICOS\033[0m")
        print_consola("\033[34m---------------------------------------------------\033[0m")
        print_consola("\033[34mrun (r)\033[0m              \033[32m| Ejecutar el programa desde inicio\033[0m")
        print_consola("\033[34mbreak (b) <n>\033[0m        \033[32m| Poner breakpoint en línea <n>\033[0m")
        print_consola("\033[34mbreak <func>\033[0m         \033[32m| Poner breakpoint en función <func>\033[0m")
        print_consola("\033[34minfo breakpoints\033[0m     \033[32m| Ver breakpoints activos\033[0m")
        print_consola("\033[34mdelete <n>\033[0m           \033[32m| Borrar breakpoint <n>\033[0m")
        print_consola("\033[34mnext (n)\033[0m             \033[32m| Ejecutar línea (sin entrar en funciones)\033[0m")
        print_consola("\033[34mstep (s)\033[0m             \033[32m| Entrar en la función\033[0m")
        print_consola("\033[34mcontinue (c)\033[0m         \033[32m| Continuar hasta el próximo breakpoint\033[0m")
        print_consola("\033[34mprint (p) <var>\033[0m      \033[32m| Mostrar valor de variable\033[0m")
        print_consola("\033[34mlist (l)\033[0m             \033[32m| Ver código fuente cercano\033[0m")
        print_consola("\033[34mbacktrace (bt)\033[0m       \033[32m| Ver pila de llamadas\033[0m")
        print_consola("\033[34mquit (q)\033[0m             \033[32m| Salir de GDB\033[0m")
        print_consola("\033[34m---------------------------------------------------\033[0m")

        # === Nivel 2: Comandos intermedios ===
        print_consola("\033[33m📗 NIVEL 2: COMANDOS INTERMEDIOS\033[0m")
        print_consola("\033[34m---------------------------------------------------\033[0m")
        print_consola("\033[34mwatch <var>\033[0m          \033[32m| Vigilar variable y detener si cambia\033[0m")
        print_consola("\033[34mdisplay <expr>\033[0m       \033[32m| Mostrar expresión en cada paso\033[0m")
        print_consola("\033[34mundisplay <n>\033[0m        \033[32m| Quitar visualización automática\033[0m")
        print_consola("\033[34mdisable <bp#>\033[0m        \033[32m| Desactivar breakpoint sin borrarlo\033[0m")
        print_consola("\033[34menable <bp#>\033[0m         \033[32m| Reactivar breakpoint\033[0m")
        print_consola("\033[34minfo locals\033[0m          \033[32m| Variables locales de la función actual\033[0m")
        print_consola("\033[34minfo args\033[0m            \033[32m| Argumentos de la función actual\033[0m")
        print_consola("\033[34minfo registers\033[0m       \033[32m| Ver registros CPU\033[0m")
        print_consola("\033[34mset var x=valor\033[0m      \033[32m| Cambiar el valor de una variable\033[0m")
        print_consola("\033[34mx/<fmt> <addr>\033[0m       \033[32m| Examinar memoria (ej: x/16xb ptr)\033[0m")
        print_consola("\033[34mdisassemble\033[0m          \033[32m| Ver el código ensamblador\033[0m")
        print_consola("\033[34mthread <id>\033[0m          \033[32m| Cambiar a hilo específico\033[0m")
        print_consola("\033[34minfo threads\033[0m         \033[32m| Listar hilos activos\033[0m")
        print_consola("\033[34m---------------------------------------------------\033[0m")

        # === Nivel 3: Comandos expertos ===
        print_consola("\033[31m📙 NIVEL 3: COMANDOS EXPERTOS\033[0m")  # 31 = rojo (aprox. naranja)
        print_consola("\033[34m---------------------------------------------------\033[0m")
        print_consola("\033[34mattach <pid>\033[0m         \033[32m| Adjuntar GDB a un proceso en ejecución\033[0m")
        print_consola("\033[34mdetach\033[0m               \033[32m| Soltar proceso adjuntado\033[0m")
        print_consola("\033[34mcore <archivo>\033[0m       \033[32m| Analizar un volcado core\033[0m")
        print_consola("\033[34minfo sharedlibrary\033[0m   \033[32m| Ver librerías dinámicas cargadas\033[0m")
        print_consola("\033[34minfo functions\033[0m       \033[32m| Listar todas las funciones disponibles\033[0m")
        print_consola("\033[34minfo variables\033[0m       \033[32m| Listar todas las variables globales\033[0m")
        print_consola("\033[34mcatch <evento>\033[0m       \033[32m| Detenerse en eventos (ej: throw, exec)\033[0m")
        print_consola("\033[34mhandle <señal> act\033[0m   \033[32m| Controlar señales (ej: SIGSEGV, SIGINT)\033[0m")
        print_consola("\033[34mtui enable\033[0m           \033[32m| Activar interfaz visual (split código/estado)\033[0m")
        print_consola("\033[34mlayout asm/src\033[0m       \033[32m| Cambiar vista en TUI (asm, src, regs)\033[0m")
        print_consola("\033[34msave gdb <archivo>\033[0m   \033[32m| Guardar sesión y breakpoints\033[0m")
        print_consola("\033[34msource <archivo>\033[0m     \033[32m| Cargar script de comandos GDB\033[0m")
        print_consola("\033[34mdefine <cmd>\033[0m         \033[32m| Crear macro/comando personalizado\033[0m")
        print_consola("\033[34mshell <cmd>\033[0m          \033[32m| Ejecutar comandos de sistema dentro de GDB\033[0m")
        print_consola("\033[34mrecord\033[0m               \033[32m| Grabar la ejecución paso a paso (replay)\033[0m")
        print_consola("\033[34mreverse-step (rs)\033[0m    \033[32m| Ir hacia atrás en el debug (requiere record)\033[0m")
        print_consola("\033[34mreverse-continue (rc)\033[0m\033[32m| Continuar hacia atrás en el tiempo\033[0m")
        print_consola("\033[34m---------------------------------------------------\033[0m")

        print_consola("\033[34m⚡ Usa NIVEL 1 para empezar, NIVEL 2 para diagnóstico, y NIVEL 3 cuando quieras control quirúrgico total.\033[0m")

        # Lanzar konsole real con GDB
        bash_cmd = f"gdb {shlex.quote(salida)}"
        subprocess.Popen(
            ["konsole", "--noclose", "-e", "bash", "-c", bash_cmd],
            cwd=ruta_proyecto
        )

    threading.Thread(target=run_debug, daemon=True).start()

    # Limpiar consola integrada
    consola.config(state="normal")
    consola.delete("1.0", tk.END)
    consola.config(state="disabled")



#################    EJECUTAR  ####################



proceso_ejecucion = None

def ejecutar():
    global ultimo_archivo, proceso_ejecucion
    if not ultimo_archivo:
        messagebox.showwarning("Error", "Primero guarda o abre un archivo")
        return

    # Ruta del binario (misma carpeta que el archivo fuente)
    ruta_proyecto = os.path.dirname(os.path.abspath(ultimo_archivo))

    # Nombre del binario (igual que el archivo fuente pero sin extensión)
    nombre_salida = os.path.splitext(os.path.basename(ultimo_archivo))[0]

    # Ruta del ejecutable dentro de 'bin/
    salida = os.path.join(ruta_proyecto,"bin", nombre_salida)

    if not os.path.exists(salida):
        messagebox.showwarning("Error", "Primero compila el archivo")
        return

    # Limpiar consola integrada
    consola.config(state="normal")
    consola.delete("1.0", tk.END)
    consola.config(state="disabled")

    # Ejecutar binario con pipes para capturar salida
    proceso_ejecucion = subprocess.Popen(
        [salida],
        cwd=ruta_proyecto,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1  # línea por línea
    )

    # Hilo para leer stdout en tiempo real
    threading.Thread(target=_leer_salida, args=(proceso_ejecucion.stdout,), daemon=True).start()
    # Hilo para leer stderr en tiempo real
    threading.Thread(target=_leer_salida, args=(proceso_ejecucion.stderr,), daemon=True).start()

def _leer_salida(pipe):
    """Lee stdout/stderr en tiempo real y lo muestra en la consola integrada"""
    for linea in iter(pipe.readline, ''):
        if linea:
            consola.after(0, print_consola, linea.rstrip())
    pipe.close()

# Entrada de consola para enviar datos al proceso
entrada_consola = tk.Entry(frame_consola, bg="black", fg="white",
                           font=("Courier", 12), insertbackground="white")
entrada_consola.pack(fill="x")

def enviar_a_proceso(event=None):
    """Envía texto de la consola integrada al stdin del proceso"""
    global proceso_ejecucion
    if proceso_ejecucion and proceso_ejecucion.poll() is None:
        texto = entrada_consola.get()
        entrada_consola.delete(0, tk.END)
        proceso_ejecucion.stdin.write(texto + "\n")
        proceso_ejecucion.stdin.flush()
        # eco opcional en la consola
        print_consola("> " + texto)

# Bind Enter para enviar al proceso
entrada_consola.bind("<Return>", enviar_a_proceso)

def detener():
    """Detiene el proceso en ejecución"""
    global proceso_ejecucion
    if proceso_ejecucion and proceso_ejecucion.poll() is None:
        proceso_ejecucion.kill()
        print_consola("\033[1;31mProceso detenido.\033[0m")






###################  GLAD  #######################

def glad():
    """
    Genera GLAD dentro de la carpeta EXACTA del proyecto actual.

    Proyecto:
        /ruta/proyecto/programa.cpp

    Genera:

        /ruta/proyecto/glad/
        ├── include/
        │   ├── glad/
        │   │   └── gl.h
        │   └── KHR/
        │       └── khrplatform.h
        │
        └── src/
            └── gl.c

    Comando:

        glad --api gl:core=3.3 --out-path glad c

    IMPORTANTE:
    El comando se ejecuta con cwd=ruta_proyecto.
    """

    import os
    import shutil
    import subprocess
    from tkinter import messagebox

    # ============================================================
    # VERIFICAR ARCHIVO ACTUAL
    # ============================================================

    global ultimo_archivo

    if not ultimo_archivo:

        messagebox.showwarning(
            "GLAD",
            "No hay ningún proyecto guardado.\n\n"
            "Primero guarda el archivo C/C++ "
            "con el botón Guardar."
        )

        if 'print_consola' in globals():

            print_consola(
                "\033[1;33m"
                "⚠️ GLAD: no existe un archivo de proyecto guardado."
                "\033[0m"
            )

        return False


    # ============================================================
    # VERIFICAR QUE EL ARCHIVO EXISTE
    # ============================================================

    if not os.path.isfile(ultimo_archivo):

        messagebox.showerror(
            "GLAD",
            "El archivo actual no existe:\n\n"
            f"{ultimo_archivo}"
        )

        if 'print_consola' in globals():

            print_consola(
                "\033[1;31m"
                f"❌ Archivo inexistente: {ultimo_archivo}"
                "\033[0m"
            )

        return False


    # ============================================================
    # OBTENER CARPETA EXACTA DEL PROYECTO
    # ============================================================

    ruta_proyecto = os.path.dirname(
        os.path.abspath(
            ultimo_archivo
        )
    )


    # ============================================================
    # NOMBRE DEL PROYECTO
    # ============================================================

    nombre_proyecto = os.path.basename(
        ruta_proyecto
    )


    # ============================================================
    # RUTA GLAD
    # ============================================================

    ruta_glad = os.path.join(
        ruta_proyecto,
        "glad"
    )


    # ============================================================
    # VERIFICAR COMANDO GLAD
    # ============================================================

    glad_executable = shutil.which(
        "glad"
    )

    if not glad_executable:

        messagebox.showerror(
            "GLAD no encontrado",
            "El comando 'glad' no está disponible.\n\n"
            "Comprueba la instalación con:\n\n"
            "glad --help"
        )

        if 'print_consola' in globals():

            print_consola(
                "\033[1;31m"
                "❌ No se encontró el comando 'glad'."
                "\033[0m"
            )

        return False


    # ============================================================
    # LIMPIAR CONSOLA
    # ============================================================

    try:

        consola.config(
            state="normal"
        )

        consola.delete(
            "1.0",
            tk.END
        )

        consola.config(
            state="disabled"
        )

    except Exception:
        pass


    # ============================================================
    # INFORMACIÓN
    # ============================================================

    if 'print_consola' in globals():

        print_consola(
            "\033[1;36m"
            "=============================================="
            "\033[0m"
        )

        print_consola(
            "\033[1;36m"
            "                 GLAD"
            "\033[0m"
        )

        print_consola(
            "\033[1;36m"
            "=============================================="
            "\033[0m"
        )

        print_consola(
            "\033[1;34m"
            f"📁 Proyecto: {ruta_proyecto}"
            "\033[0m"
        )

        print_consola(
            "\033[1;34m"
            f"📄 Archivo: {ultimo_archivo}"
            "\033[0m"
        )

        print_consola(
            "\033[1;34m"
            f"🎯 API: OpenGL 3.3 Core"
            "\033[0m"
        )

        print_consola(
            "\033[1;34m"
            f"📦 Salida: {ruta_glad}"
            "\033[0m"
        )


    # ============================================================
    # COMANDO GLAD
    # ============================================================

    comando = [
        glad_executable,
        "--api",
        "gl:core=3.3",
        "--out-path",
        "glad",
        "c"
    ]


    if 'print_consola' in globals():

        print_consola(
            "\033[1;35m"
            "▶ "
            + " ".join(comando)
            + "\033[0m"
        )

        print_consola(
            "\033[1;35m"
            f"📂 Ejecutando desde: {ruta_proyecto}"
            "\033[0m"
        )


    # ============================================================
    # EJECUTAR GLAD
    # ============================================================

    try:

        proceso = subprocess.Popen(
            comando,
            cwd=ruta_proyecto,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        # --------------------------------------------------------
        # MOSTRAR SALIDA EN TIEMPO REAL
        # --------------------------------------------------------

        for linea in proceso.stdout:

            linea = linea.rstrip()

            if not linea:
                continue

            if 'print_consola' in globals():

                print_consola(
                    linea
                )

        proceso.wait()


    except FileNotFoundError:

        messagebox.showerror(
            "GLAD",
            "No se pudo ejecutar el comando 'glad'."
        )

        if 'print_consola' in globals():

            print_consola(
                "\033[1;31m"
                "❌ No se pudo ejecutar GLAD."
                "\033[0m"
            )

        return False


    except Exception as e:

        messagebox.showerror(
            "Error GLAD",
            f"Error ejecutando GLAD:\n\n{e}"
        )

        if 'print_consola' in globals():

            print_consola(
                "\033[1;31m"
                f"❌ Error ejecutando GLAD: {e}"
                "\033[0m"
            )

        return False


    # ============================================================
    # COMPROBAR RESULTADO
    # ============================================================

    if proceso.returncode != 0:

        messagebox.showerror(
            "GLAD",
            "GLAD terminó con errores.\n\n"
            f"Código de salida: {proceso.returncode}\n\n"
            "Revisa la consola de la IDE."
        )

        if 'print_consola' in globals():

            print_consola(
                "\033[1;31m"
                f"❌ GLAD terminó con código "
                f"{proceso.returncode}"
                "\033[0m"
            )

        return False


    # ============================================================
    # ARCHIVOS GENERADOS POR GLAD MODERNO
    # ============================================================

    archivo_gl = os.path.join(
        ruta_glad,
        "include",
        "glad",
        "gl.h"
    )

    archivo_khr = os.path.join(
        ruta_glad,
        "include",
        "KHR",
        "khrplatform.h"
    )

    archivo_c = os.path.join(
        ruta_glad,
        "src",
        "gl.c"
    )


    archivos_esperados = [
        archivo_gl,
        archivo_khr,
        archivo_c
    ]


    # ============================================================
    # VERIFICAR ARCHIVOS
    # ============================================================

    faltantes = []

    for archivo in archivos_esperados:

        if not os.path.isfile(archivo):

            faltantes.append(
                archivo
            )


    if faltantes:

        if 'print_consola' in globals():

            print_consola(
                "\033[1;31m"
                "❌ GLAD terminó pero faltan archivos:"
                "\033[0m"
            )

            for archivo in faltantes:

                print_consola(
                    "\033[1;31m"
                    f"   ❌ {archivo}"
                    "\033[0m"
                )


        messagebox.showerror(
            "GLAD",
            "GLAD terminó pero no se encontraron "
            "todos los archivos esperados.\n\n"
            + "\n".join(
                faltantes
            )
        )

        return False


    # ============================================================
    # ÉXITO
    # ============================================================

    if 'print_consola' in globals():

        print_consola(
            "\033[1;32m"
            "=============================================="
            "\033[0m"
        )

        print_consola(
            "\033[1;32m"
            "✅ GLAD generado correctamente."
            "\033[0m"
        )

        print_consola(
            "\033[1;32m"
            "=============================================="
            "\033[0m"
        )

        print_consola(
            "\033[1;36m"
            f"📁 Carpeta GLAD: {ruta_glad}"
            "\033[0m"
        )

        print_consola(
            "\033[1;36m"
            f"📄 {os.path.relpath(archivo_gl, ruta_proyecto)}"
            "\033[0m"
        )

        print_consola(
            "\033[1;36m"
            f"📄 {os.path.relpath(archivo_khr, ruta_proyecto)}"
            "\033[0m"
        )

        print_consola(
            "\033[1;36m"
            f"📄 {os.path.relpath(archivo_c, ruta_proyecto)}"
            "\033[0m"
        )


    # ============================================================
    # MENSAJE FINAL
    # ============================================================

    messagebox.showinfo(
        "GLAD",
        "GLAD generado correctamente.\n\n"
        f"Proyecto:\n{ruta_proyecto}\n\n"
        "OpenGL: 3.3 Core\n\n"
        "Archivos:\n"
        "• glad/include/glad/gl.h\n"
        "• glad/include/KHR/khrplatform.h\n"
        "• glad/src/gl.c"
    )


    return True

###################  WESTON + BGFX #######################




weston_proc = None

def abrir_weston_y_bgfx():
    global weston_proc, proceso_ejecucion, ultimo_archivo

    # --- Paso 1: Preparar entorno ---
    env = os.environ.copy()
    xdg_runtime = f"/run/user/{os.getuid()}"
    env.setdefault("XDG_RUNTIME_DIR", xdg_runtime)

    # --- Paso 2: Lanzar Weston si no está activo ---
    if weston_proc is None or weston_proc.poll() is not None:
        try:
            weston_proc = subprocess.Popen(
                ["weston"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )
            print_consola("🚀 Weston compositor iniciado...\n")

            # Esperar hasta que se cree un socket Wayland válido
            socket_path = None
            timeout = 10  # segundos
            for _ in range(timeout * 10):
                sockets = glob.glob(os.path.join(xdg_runtime, "wayland-*"))
                if sockets:
                    socket_path = sockets[0]
                    break
                time.sleep(0.1)

            if socket_path is None:
                print_consola("⚠️ Timeout: Wayland socket no encontrado.\n")
                return
            else:
                wayland_display = os.path.basename(socket_path)
                env["WAYLAND_DISPLAY"] = wayland_display
                print_consola(f"✅ Wayland listo: {wayland_display}\n")
        except Exception as e:
            print_consola(f"❌ Error al iniciar Weston: {e}\n")
            return
    else:
        print_consola("✅ Weston ya estaba en ejecución.\n")
        # Obtener socket existente si Weston ya estaba activo
        sockets = glob.glob(os.path.join(xdg_runtime, "wayland-*"))
        if not sockets:
            print_consola("⚠️ No se encontró ningún socket Wayland existente.\n")
            return
        wayland_display = os.path.basename(sockets[0])
        env["WAYLAND_DISPLAY"] = wayland_display
        print_consola(f"ℹ️ Usando socket Wayland existente: {wayland_display}\n")

    # --- Paso 3: Verificar archivo compilado ---
    if not ultimo_archivo:
        messagebox.showwarning("Error", "Primero guarda o abre un archivo")
        return

    ruta_proyecto = os.path.dirname(os.path.abspath(ultimo_archivo))
    nombre_salida = os.path.splitext(os.path.basename(ultimo_archivo))[0]
    salida = os.path.join(ruta_proyecto, "bin", nombre_salida)

    if not os.path.exists(salida):
        messagebox.showwarning("Error", "Primero compila el archivo")
        return

    # --- Paso 4: Limpiar consola integrada ---
    consola.config(state="normal")
    consola.delete("1.0", tk.END)
    consola.config(state="disabled")

    # --- Paso 5: Ejecutar binario BGFX con Wayland ---
    global proceso_ejecucion
    proceso_ejecucion = subprocess.Popen(
        [salida],
        cwd=ruta_proyecto,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=env
    )

    # --- Paso 6: Hilos para leer salida en tiempo real ---
    threading.Thread(target=_leer_salida, args=(proceso_ejecucion.stdout,), daemon=True).start()
    threading.Thread(target=_leer_salida, args=(proceso_ejecucion.stderr,), daemon=True).start()



###################  BGFX  #######################

# Variables globales
bgfx_proc = None

def ejecutar_bgfx():
    global bgfx_proc, weston_proc, ultimo_archivo

    if not ultimo_archivo:
        messagebox.showwarning("Error", "Primero guarda o abre un archivo")
        return

    ruta_proyecto = os.path.dirname(os.path.abspath(ultimo_archivo))
    nombre_salida = os.path.splitext(os.path.basename(ultimo_archivo))[0]
    salida = os.path.join(ruta_proyecto, "bin", nombre_salida)

    if not os.path.exists(salida):
        messagebox.showwarning("Error", "Primero compila el archivo")
        return

    # Lanzar Weston si no está activo
    if weston_proc is None or weston_proc.poll() is not None:
        try:
            weston_proc = subprocess.Popen(
                ["weston"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print_consola("🚀 Weston compositor iniciado...")
            # Esperar socket Wayland
            import time, os
            wayland_socket = None
            for _ in range(50):  # 5 segundos máximo
                # Buscar sockets existentes: wayland-0, wayland-1, etc.
                for f in os.listdir(f"/run/user/{os.getuid()}"):
                    if f.startswith("wayland-"):
                        wayland_socket = f
                        break
                if wayland_socket:
                    break
                time.sleep(0.1)
            if wayland_socket:
                print_consola(f"✅ Wayland listo: {wayland_socket}")
            else:
                print_consola("⚠️ Timeout: Wayland socket no encontrado.")
                return
        except Exception as e:
            print_consola(f"❌ Error al iniciar Weston: {e}")
            return
    else:
        print_consola("✅ Weston ya estaba en ejecución.")
        # Detectar socket activo
        import os
        wayland_socket = None
        for f in os.listdir(f"/run/user/{os.getuid()}"):
            if f.startswith("wayland-"):
                wayland_socket = f
                break
        if wayland_socket:
            print_consola(f"✅ Wayland activo: {wayland_socket}")
        else:
            print_consola("⚠️ No se detectó socket Wayland activo.")
            return

    # Limpiar consola integrada
    consola.config(state="normal")
    consola.delete("1.0", tk.END)
    consola.config(state="disabled")

    # Ejecutar binario BGFX con WAYLAND_DISPLAY
    env = os.environ.copy()
    env["WAYLAND_DISPLAY"] = wayland_socket

    bgfx_proc = subprocess.Popen(
        [salida],
        cwd=ruta_proyecto,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=env
    )

    # Hilos para leer stdout y stderr
    import threading
    threading.Thread(target=_leer_salida, args=(bgfx_proc.stdout,), daemon=True).start()
    threading.Thread(target=_leer_salida, args=(bgfx_proc.stderr,), daemon=True).start()





###################  BOTONES  #######################


# --------- ICONOS ---------
def cargar_icono(nombre_archivo, tamaño=(48,48)):
    ruta = os.path.join(CARPETA_ICONOS, nombre_archivo)
    if os.path.exists(ruta):
        img = Image.open(ruta).resize(tamaño, Image.LANCZOS)
    else:
        # Crear imagen vacía como placeholder
        img = Image.new("RGBA", tamaño, (200,200,200,0))
    return ImageTk.PhotoImage(img)


iconos = {name: cargar_icono(name+".png") for name in [
    "crear","guardar","select","listar","compilar","ejecutar","debug","limpiar","copiar","cmake","build","paste","actualizar","salir"
]}

refs_imgs = []



# --- Barra superior ---
frame_superior = tk.Frame(root, bg="#E6E6FA")
frame_superior.pack(side="top", fill="x", pady=5)
#  - -  -  -  -  -  -  -("Nombre del boton", enlace a la funcion , color del boton , "nombre del icono"),
botones_superior = [
    ("Open", listar, COLOR_NARANJA, "listar"),
    ("Save", guardar, COLOR_NARANJA, "guardar"),
    ("Select All", seleccionar_todo, COLOR_NARANJA, "select"),
    ("Copy", copiar, COLOR_NARANJA, "copiar"),
    ("Paste", pegar, COLOR_NARANJA, "paste"),
    ("Clear", limpiar_area, COLOR_NARANJA, "limpiar"),
    ("Update", ejecutar_updater, COLOR_NARANJA, "actualizar"),
    ("Exit", root.destroy, COLOR_ROJO, "salir")
]

for texto, comando, color, icono_nombre in botones_superior:
    img = iconos.get(icono_nombre)
    btn = tk.Button(
        frame_superior,
        text=texto,
        command=comando,
        image=img,
        compound="top",
        bg=color,
        fg="black",
        activebackground="#FFD700",  # fondo al presionar
        activeforeground="black",    # texto al presionar
        relief="raised",              # efecto elevado
        bd=4,                         # grosor del borde
        padx=4,
        pady=4,
        highlightthickness=0,
        font=("Arial", 8, "bold"),
    )
    # Ajuste seguro: solo si img existe
    if img is not None:
        btn.config(width=img.width(), height=img.height())
        refs_imgs.append(img)  # mantener referencia para que no se elimine

    btn.pack(side="left", padx=3)




###################   EDITOR  #######################




# --- Area de EDITOR  ---


# Contenedor para barra de línea + editor
frame_editor = tk.Frame(root)
frame_editor.pack(fill="both", expand=True, padx=5, pady=5)

# --- Barra de números de línea ---
lineas = tk.Text(frame_editor, width=4, padx=3, takefocus=0, border=0,
                 background="#DDDDDD", state="disabled", wrap="none")
lineas.pack(side="left", fill="y")



# --- Editor PRINCIPAL  ---

# Scrollbar vertical del editor
scroll_vert = tk.Scrollbar(frame_editor, orient="vertical", command=lambda *args: [editor.yview(*args), lineas.yview(*args)])
scroll_vert.pack(side="right", fill="y")

# Scrollbar horizontal del editor
scroll_hor = tk.Scrollbar(frame_editor, orient="horizontal", command=lambda *args: [editor.xview(*args), lineas.xview(*args)])
scroll_hor.pack(side="bottom", fill="x")

#------AREA DE TRABAJO-----

editor = tk.Text(frame_editor, wrap="none", background="#FFFFFF",yscrollcommand=scroll_vert.set, xscrollcommand=scroll_hor.set, font=("Courier", 12), undo=True)
editor.pack(side="left", fill="both", expand=True)

# --- Scroll sincronizado entre editor y números de línea ---
def sync_scroll(*args):
    editor.yview(*args)
    lineas.yview(*args)
    scroll_vert.set(*args)  # actualiza scrollbar vertical

# Conectar scrollbars con editor y línea
editor.config(yscrollcommand=scroll_vert.set, xscrollcommand=scroll_hor.set)
lineas.config(yscrollcommand=scroll_vert.set)

# --- Función de sincronización para scrollbar vertical ---
scroll_vert.config(command=sync_scroll)
scroll_hor.config(command=editor.xview)

# Función para sincronizar la rueda del ratón
def on_mouse_wheel(event):
    # Windows/Mac usan event.delta, Linux usa Button-4/5
    if event.num == 4:   # Linux scroll up
        editor.yview_scroll(-1, "units")
        lineas.yview_scroll(-1, "units")
    elif event.num == 5: # Linux scroll down
        editor.yview_scroll(1, "units")
        lineas.yview_scroll(1, "units")
    else:
        editor.yview_scroll(int(-1*(event.delta/120)), "units")
        lineas.yview_scroll(int(-1*(event.delta/120)), "units")
    return "break"

# Vincular rueda del ratón
editor.bind("<MouseWheel>", on_mouse_wheel)  # Windows/Mac
editor.bind("<Button-4>", on_mouse_wheel)    # Linux scroll up
editor.bind("<Button-5>", on_mouse_wheel)    # Linux scroll down

# --- Actualizar números de línea ---
def actualizar_lineas(event=None):
    lineas.config(state="normal")
    lineas.delete("1.0", tk.END)
    # obtener número de líneas reales, ignorando línea final extra
    num_lineas = int(editor.index('end-1c').split('.')[0])
    numeros = "\n".join(str(i) for i in range(1, num_lineas+1))
    lineas.insert("1.0", numeros)
    lineas.config(state="disabled")

# --- Auto-indent + actualizar líneas correctamente ---
def on_return(event):
    auto_indent(event)
    root.after(10, actualizar_lineas)  # esperar que el Enter se procese
    root.after(15, resaltar)           # llamar al resaltado después de actualizar líneas
    return "break"

editor.bind("<Return>", on_return)

# Llamar resaltar + actualizar líneas en eventos de edición
editor.bind("<Any-KeyRelease>", lambda e: [actualizar_lineas(), resaltar()])
editor.bind("<Button-1>", lambda e: [actualizar_lineas(), resaltar()])
editor.bind("<MouseWheel>", lambda e: [actualizar_lineas(), resaltar()])


# Inicializar línea 1 al inicio
actualizar_lineas()




# ---------------- RESALTADO AVANZADO ---------------- #
def resaltar(event=None):
    contenido = editor.get("1.0", tk.END)

    # Borrar formatos previos
    for tag in editor.tag_names():
        editor.tag_remove(tag, "1.0", tk.END)

    # --- Palabras clave de C/C++ ---
    palabras_clave = r'\b(' + '|'.join([
        'bool','char','wchar_t','char16_t','char32_t','short','int','long','float','double','void','auto','decltype',
        'signed','unsigned','const','volatile','mutable','static','extern','register','thread_local',
        'if','else','switch','case','default','for','while','do','break','continue','goto','return','co_await','co_yield','co_return',
        'class','struct','union','enum','typename','template','friend','virtual','override','final','explicit','operator','this',
        'namespace','using','new','delete','alignas','alignof','noexcept',
        'try','catch','throw',
        'constexpr','consteval','constinit',
        'nullptr','ref','decltype_auto',
        'static_assert','typeid','sizeof','dynamic_cast','static_cast','reinterpret_cast','const_cast',
        'bitand','bitor','and','and_eq','or','or_eq','xor','xor_eq','compl','not','not_eq',
        'true','false'
    ]) + r')\b'


    # Preprocesadores
    preprocesador = r'^\s*#\s*\w+'

    # Strings (simples y dobles)
    string = r'(\".*?\"|\'.*?\')'

    # Comentarios (// y /* */)
    comentario_linea = r'//.*$'        # termina al final de la línea
    comentario_bloque = r'/\*.*?\*/'   # multilinea

    # Funciones (identificadores seguidos de paréntesis)
    funcion = r'\b([a-zA-Z_]\w*)(?=\s*\()'

    # Números
    numeros = r'\b\d+(\.\d+)?\b'

    # Aplicar resaltado
    patrones = [
        ("comment", comentario_bloque),  # primero los bloques
        ("comment", comentario_linea),   # luego los comentarios de línea
        ("string", string),
        ("keyword", palabras_clave),
        ("preprocessor", preprocesador),
        ("function", funcion),
        ("number", numeros)
    ]


    for tag, pattern in patrones:
        flags = re.MULTILINE
        if tag == "comment" and pattern == comentario_bloque:
            flags |= re.DOTALL  # permite multilinea en /* */
        for match in re.finditer(pattern, contenido, flags):
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            editor.tag_add(tag, start, end)

# --- Configuración de colores y estilos neón ---
editor.tag_config("keyword", foreground="#0000FF", font=("Consolas", 12, ))        # azul intenso
editor.tag_config("preprocessor", foreground="#BF00FF", font=("Consolas", 12, ))   # púrpura neón
editor.tag_config("string", foreground="#C833FF", font=("Consolas", 12, "italic"))       # lila neón
editor.tag_config("comment", foreground="#008000", font=("Consolas", 12, "italic"))      # verde intenso
editor.tag_config("function", foreground="#C833FF", font=("Consolas", 12, "underline"))  #  rosado
editor.tag_config("number", foreground="#FF3131", font=("Consolas", 12, ))         # rojo neón

# --- Opcionales adicionales para resaltado avanzado ---
editor.tag_config("type", foreground="#00FF9F", font=("Consolas", 12, ))           # tipos de datos
editor.tag_config("operator", foreground="#FFFF00", font=("Consolas", 12, ))       # operadores
editor.tag_config("constant", foreground="#FF00FF", font=("Consolas", 12, ))       # constantes
editor.tag_config("boolean", foreground="#00FFFF", font=("Consolas", 12, ))        # true / false
editor.tag_config("namespace", foreground="#FFA500", font=("Consolas", 12, "italic"))    # nombres de espacio
editor.tag_config("macro", foreground="#BF00FF", font=("Consolas", 12, ))          # macros #define
editor.tag_config("todo", foreground="#FF1493", font=("Consolas", 12, ))           # comentarios



# --- Barra inferior ---
frame_inferior = tk.Frame(root, bg="#E6E6FA")
frame_inferior.pack(side="bottom", fill="x", pady=5)

#  - -  -  -  -  -  -  -("Nombre del boton", enlace a la funcion , color del boton , "nombre del icono"),
botones_inferior = [
    ("Crear (F1)", crear_externo, COLOR_NARANJA, "crear"),
    ("CMake (F3)", make, COLOR_NARANJA, "cmake"),
    ("Build (F5)", build, COLOR_NARANJA, "build"),
    ("Compile (F6)", compilar, COLOR_NARANJA, "compilar"),
    ("Debug (F7)", depurar, COLOR_NARANJA, "debug"),
    ("Run (F8)", ejecutar, COLOR_NARANJA, "ejecutar"),
]

for texto, comando, color, icono_nombre in botones_inferior:
    img = iconos.get(icono_nombre)
    btn = tk.Button(
        frame_inferior,
        text=texto,
        command=comando,
        image=img,
        compound="top",
        bg=color,
        fg="black",
        activebackground="#FFD700",  # fondo al presionar
        activeforeground="black",    # texto al presionar
        relief="raised",              # efecto elevado
        bd=4,                         # grosor del borde
        padx=4,
        pady=4,
        highlightthickness=0,
        font=("Arial", 8, "bold"),  # <-- aquí asignas la fuente
    )
    # Ajuste seguro: solo si img existe
    if img is not None:
        btn.config(width=img.width(), height=img.height())
        refs_imgs.append(img)  # mantener referencia para que no se elimine

    btn.pack(side="left", padx=3)


# ============================================================
# BOTONES ESPECIALES
# ============================================================


# ------------------------------------------------------------
# WESTON
# ------------------------------------------------------------


btn_weston = tk.Button(
    frame_inferior,
    text="Weston",
    command=abrir_weston_y_bgfx,
    bg="#4682B4",
    fg="white",
    font=("Arial", 12, "bold"),
    relief="raised",
    padx=10,
    pady=5
)

btn_weston.pack(side="right", padx=5)

# ------------------------------------------------------------
# GLAD
# ------------------------------------------------------------

btn_glad = tk.Button(
    frame_inferior,
    text="GLAD",
    command=glad,
    bg="#4682B4",
    fg="white",
    activebackground="#FFD700",
    activeforeground="black",
    font=("Arial", 10, "bold"),
    relief="raised",
    bd=4,
    padx=10,
    pady=5
)

btn_glad.pack(
    side="right",
    padx=3
)



# ------------------------------------------------------------
# BGFX
# ------------------------------------------------------------

btn_bgfx = tk.Button(
    frame_inferior,
    text="BGFX",
    command=ejecutar_bgfx,
    bg="#4682B4",
    fg="white",
    font=("Arial", 10, "bold"),
    relief="raised",
    padx=5,
    pady=5
)
btn_bgfx.pack(side="right", padx=3)



# --- Area de consola integrada ---

frame_consola.pack(fill="both", side="bottom", padx=5, pady=5, expand=True)

# Text con scroll
consola = tk.Text(frame_consola, height=10, bg="black", fg="white", font=("Courier", 12),
                  state="disabled", wrap="none")
consola.pack(side="left", fill="both", expand=True)

# Scroll vertical
scroll_consola = tk.Scrollbar(frame_consola, command=consola.yview)
scroll_consola.pack(side="right", fill="y")
consola.config(yscrollcommand=scroll_consola.set)

# Tags para colores ANSI
consola.tag_config("verde", foreground="#00FF00")
consola.tag_config("rojo", foreground="#FF0000")
consola.tag_config("amarillo", foreground="#FFFF00")
consola.tag_config("azul", foreground="#00BFFF")
consola.tag_config("magenta", foreground="#FF00FF")

# Función para imprimir en la consola


def print_consola(mensaje):
    consola.config(state="normal")

    ansi_pattern = re.compile(r'\033\[(\d+;?\d*)m')
    last_end = 0
    current_tag = None

    for match in ansi_pattern.finditer(mensaje):
        start, end = match.span()
        if start > last_end:
            consola.insert(tk.END, mensaje[last_end:start], current_tag)
        code = match.group(1)
        if code == "1;32":   current_tag = "verde"
        elif code == "1;31": current_tag = "rojo"
        elif code == "1;33": current_tag = "amarillo"
        elif code == "1;34": current_tag = "azul"
        elif code == "1;35": current_tag = "magenta"
        elif code == "0":    current_tag = None
        last_end = end

    if last_end < len(mensaje):
        consola.insert(tk.END, mensaje[last_end:], current_tag)

    consola.insert(tk.END, "\n")
    consola.see(tk.END)
    consola.config(state="disabled")



# --- TECLAS RAPIDAS ---
root.bind("<F1>", lambda e: root.after_idle(crear_externo))
root.bind("<F3>", lambda e: root.after_idle(make))
root.bind("<F5>", lambda e: root.after_idle(build))
root.bind("<F6>", lambda e: root.after_idle(compilar))
root.bind("<F7>", lambda e: root.after_idle(debug))
root.bind("<F8>", lambda e: root.after_idle(ejecutar))
editor.bind("<Return>", auto_indent)
editor.bind("<KeyRelease>", resaltar)

# --- CENTRAR VENTANA ---
root.update_idletasks()
w = root.winfo_screenwidth()
h = root.winfo_screenheight()
size = tuple(int(_) for _ in root.geometry().split('+')[0].split('x'))
x = w//2 - size[0]//2
y = h//2 - size[1]//2
root.geometry(f"{size[0]}x{size[1]}+{x}+{y}")

root.mainloop()
