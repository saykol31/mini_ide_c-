#include <iostream>
#include <vector>
#include <string>
#include <map>
#include <cstdlib>
#include <fstream>

// Colores ANSI
const std::string GREEN  = "\033[1;32m";
const std::string RED    = "\033[1;31m";
const std::string YELLOW = "\033[1;33m";
const std::string RESET  = "\033[0m";

struct Libreria {
    std::string nombre;
    std::string paquete;       
    std::string pkgconfig;     
    std::vector<std::string> headers;
    bool es_comando = false;       // true si es herramienta CLI
    std::string ejecutable = "";   // nombre del ejecutable para comprobar
};

// Detección de distro simple
enum Distro { DEBIAN, ARCH, FEDORA, UNKNOWN };

Distro detectar_distro() {
    if (system("test -f /etc/debian_version") == 0) return DEBIAN;
    if (system("test -f /etc/arch-release") == 0) return ARCH;
    if (system("test -f /etc/fedora-release") == 0) return FEDORA;
    return UNKNOWN;
}

// Comando de instalación según distro
std::string comando_instalar(Distro d, const std::string &paquete) {
    switch (d) {
        case DEBIAN: return "sudo apt install -y " + paquete;
        case ARCH:   return "sudo pacman -S --noconfirm " + paquete;
        case FEDORA: return "sudo dnf install -y " + paquete;
        default: return "";
    }
}

// Comando de actualización según distro
std::string comando_actualizar(Distro d) {
    switch (d) {
        case DEBIAN: return "sudo apt update && sudo apt upgrade -y";
        case ARCH:   return "sudo pacman -Syu --noconfirm";
        case FEDORA: return "sudo dnf upgrade -y";
        default: return "";
    }
}

// Comprobar si la librería o herramienta está instalada
bool esta_instalada(const Libreria &lib) {
    if (lib.es_comando && !lib.ejecutable.empty()) {
        std::string cmd = "which " + lib.ejecutable + " > /dev/null 2>&1";
        return system(cmd.c_str()) == 0;
    }
    if (!lib.pkgconfig.empty()) {
        std::string cmd = "pkg-config --exists " + lib.pkgconfig + " > /dev/null 2>&1";
        if (system(cmd.c_str()) == 0) return true;
    }
    for (auto &header : lib.headers) {
        std::string cmd = "test -f /usr/include/" + header;
        if (system(cmd.c_str()) == 0) return true;
    }
    return false;
}

// Instalar librerías y generar reporte
void instalar_librerias(const std::map<std::string, std::vector<Libreria>> &categorias, Distro d) {
    std::ofstream reporte("reporte_cpp_librerias.txt");
    reporte << "Reporte de librerías y herramientas C++ instaladas/no instaladas\n\n";

    // Actualizar todo primero
    std::string cmd_actualizar = comando_actualizar(d);
    if (!cmd_actualizar.empty()) {
        std::cout << YELLOW << "🔄 Actualizando sistema..." << RESET << "\n";
        system(cmd_actualizar.c_str());
    }

    for (auto &[categoria, libs] : categorias) {
        std::cout << GREEN << "📂 Revisando categoría: " << categoria << RESET << "\n";
        for (auto &lib : libs) {
            bool instalado = esta_instalada(lib);
            if (!instalado) {
                std::cout << RED << "❌ Instalando: " << lib.nombre << RESET << "\n";
                std::string cmd = comando_instalar(d, lib.paquete);
                if (!cmd.empty()) system(cmd.c_str());
                instalado = esta_instalada(lib); // verificar después de instalar
            } else {
                std::cout << GREEN << "✅ Ya instalado: " << lib.nombre << RESET << "\n";
            }
            reporte << lib.nombre << ": " << (instalado ? "INSTALADO" : "NO INSTALADO") << "\n";
        }
        reporte << "----------------------------------------\n";
    }
    reporte.close();
    std::cout << GREEN << "✅ Proceso completado. Reporte generado en 'reporte_cpp_librerias.txt'\n" << RESET;
}

int main() {
    Distro distro = detectar_distro();
    if (distro == UNKNOWN) {
        std::cerr << RED << "⚠️ Distribución no reconocida. Abortando." << RESET << "\n";
        return 1;
    }

    // Categorías y librerías
    std::map<std::string, std::vector<Libreria>> categorias = {
        {"Gráficas / Multimedia", {
            {"SDL2", "libsdl2-dev", "sdl2", {"SDL2/SDL.h"}},
            {"SFML", "libsfml-dev", "sfml-graphics", {"SFML/Graphics.hpp"}},
            {"OpenGL/GLUT", "freeglut3-dev mesa-common-dev", "glut", {"GL/gl.h", "GL/glut.h"}},
            {"GLFW/GLEW", "libglfw3-dev libglew-dev", "glfw3", {"GL/glew.h", "GLFW/glfw3.h"}},
            {"Allegro", "liballegro5-dev", "allegro-5.0", {"allegro5/allegro.h"}}
        }},
        {"GUI", {
            {"Qt5Widgets", "qtbase5-dev libqt5widgets5", "Qt5Widgets", {"QApplication"}},
            {"GTKmm", "libgtkmm-4.0-dev", "gtkmm-4.0", {"gtkmm.h"}},
            {"wxWidgets", "libwxgtk3.0-dev", "wx-config", {"wx/wx.h"}},
            {"ImGui", "libimgui-dev", "", {"imgui.h"}}
        }},
        {"Redes / Sockets", {
            {"Boost.Asio", "libboost-all-dev", "", {"boost/asio.hpp"}},
            {"POCO C++", "libpoco-dev", "", {"Poco/Net/HTTPClientSession.h"}},
            {"cpp-httplib", "libhttplib-dev", "", {"httplib.h"}},
            {"libcurl", "libcurl4-openssl-dev", "libcurl", {"curl/curl.h"}}
        }},
        {"Utilidades", {
            {"Boost", "libboost-all-dev", "", {"boost/algorithm/string.hpp"}},
            {"fmt", "libfmt-dev", "fmt", {"fmt/core.h"}},
            {"spdlog", "libspdlog-dev", "spdlog", {"spdlog/spdlog.h"}},
            {"nlohmann/json", "nlohmann-json3-dev", "", {"nlohmann/json.hpp"}},
            {"yaml-cpp", "libyaml-cpp-dev", "yaml-cpp", {"yaml-cpp/yaml.h"}}
        }},
        {"Matemáticas / Ciencia", {
            {"Eigen", "libeigen3-dev", "eigen3", {"Eigen/Dense"}},
            {"Armadillo", "libarmadillo-dev", "", {"armadillo"}},
            {"BLAS/LAPACK", "libblas-dev liblapack-dev", "", {"cblas.h"}},
            {"CGAL", "libcgal-dev", "", {"CGAL/Exact_predicates_inexact_constructions_kernel.h"}}
        }},
        {"IA / ML", {
            {"TensorFlow C++ API", "tensorflow-cpp-dev", "", {"tensorflow/core/public/session.h"}},
            {"LibTorch", "libtorch-dev", "", {"torch/torch.h"}},
            {"Dlib", "libdlib-dev", "", {"dlib/dnn.h"}},
            {"OpenCV", "libopencv-dev", "opencv4", {"opencv2/opencv.hpp"}}
        }},
        {"Multimedia / Audio / Video", {
            {"PortAudio", "portaudio19-dev", "", {"portaudio.h"}},
            {"OpenAL", "libopenal-dev", "", {"AL/al.h"}},
            {"FMOD", "libfmod-dev", "", {"fmod.h"}},
            {"libsndfile", "libsndfile1-dev", "", {"sndfile.h"}},
            {"FFmpeg", "ffmpeg libavcodec-dev libavformat-dev", "", {"libavcodec/avcodec.h"}}
        }},
        {"Juegos / Motores", {
            {"Box2D", "libbox2d-dev", "", {"box2d/box2d.h"}},
            {"Bullet", "libbullet-dev", "", {"btBulletDynamicsCommon.h"}},
            {"Ogre3D", "libogre-1.9-dev", "", {"Ogre.h"}},
            {"Godot C++ bindings", "godot-cpp-dev", "", {"Godot.hpp"}}
        }},
        {"Seguridad / Criptografía", {
            {"OpenSSL", "libssl-dev", "openssl", {"openssl/ssl.h"}},
            {"libsodium", "libsodium-dev", "sodium", {"sodium.h"}},
            {"Crypto++", "libcrypto++-dev", "", {"cryptlib.h"}}
        }},
        {"Herramientas Esenciales", {
            {"GCC/G++", "g++ build-essential", "", {}, true, "g++"},
            {"Clang", "clang", "", {}, true, "clang"},
            {"GDB", "gdb", "", {}, true, "gdb"},
            {"CMake", "cmake", "", {}, true, "cmake"},
            {"Make", "make", "", {}, true, "make"},
            {"Ninja", "ninja-build", "", {}, true, "ninja"}
        }}
    };

    instalar_librerias(categorias, distro);
    return 0;
}

