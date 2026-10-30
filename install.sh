#!/usr/bin/env bash
# install.sh — Instalador de idec para Debian
#
# Instala el mínimo que idec necesita para abrirse en una Debian limpia.
# Lista verificada en una Debian 13 recién instalada (2026-10-29):
# la base no traía ni python3; cada paquete de esta lista salió de un
# error real al intentar abrir el IDE.
#
# Uso:
#   chmod +x install.sh
#   ./install.sh

set -e

# --- Paquetes -------------------------------------------------------------
# Para que la ventana abra: python3 + Tkinter + Pillow.
# En Debian, ImageTk viene en su propio paquete (python3-pil.imagetk).
MINIMOS="python3 python3-tk python3-pil python3-pil.imagetk"
# Para que el IDE haga su trabajo completo: compilar C++ desde adentro.
# (La ventana no lo necesita; si solo quieres que abra, borra este paso.)
COMPILADOR="build-essential"

echo "==> Instalador de idec para Debian"

# --- Debe ser un sistema con apt (Debian y derivados) ----------------------
if ! command -v apt >/dev/null 2>&1; then
    echo "ERROR: este instalador es para sistemas con apt (Debian y derivados)." >&2
    exit 1
fi

# --- sudo si no somos root --------------------------------------------------
if [ "$(id -u)" -ne 0 ]; then
    SUDO="sudo"
else
    SUDO=""
fi

echo "==> Actualizando la lista de paquetes..."
$SUDO apt update

echo "==> Instalando el mínimo para que idec abra: $MINIMOS"
$SUDO apt install -y $MINIMOS

echo "==> Instalando el compilador de C++: $COMPILADOR"
$SUDO apt install -y $COMPILADOR

# --- Verificación -----------------------------------------------------------
# Los mismos imports que idec.py hace al arrancar. Si esto pasa sin abrir
# la ventana, el IDE puede abrir.
echo "==> Verificando los módulos que idec importa al arrancar..."
python3 -c "import tkinter; from PIL import Image, ImageTk; print('OK: tkinter y Pillow responden.')"

echo ""
echo "Listo. Para abrir idec:"
echo "  python3 idec.py"
