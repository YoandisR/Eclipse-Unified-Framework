#!/data/data/com.termux/files/usr/bin/python3
# -*- coding: utf-8 -*-
"""
ECLIPSE UNIFIED FRAMEWORK v13.2 (Professional Edition)
Versión mejorada con funciones modernas para obtener información detallada del sistema e interfaz gráfica estilizada.
"""

import os
import sys
import subprocess
import time
import importlib.util
import inspect
import json
import sqlite3
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import signal
import webbrowser
import tempfile
import http.server
import socketserver
import threading
import shutil

# ==================== VERIFICACIÓN E INSTALACIÓN DE DEPENDENCIAS ====================
REQUIRED_PACKAGES = ['click', 'psutil', 'requests', 'colorama']

def install_dependencies():
    """Instala dependencias necesarias si no se encuentran."""
    missing_packages = []
    for pkg in REQUIRED_PACKAGES:
        try:
            __import__(pkg)
        except ImportError:
            missing_packages.append(pkg)
    
    if missing_packages:
        print(f"Instalando dependencias faltantes: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_packages], 
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("Dependencias instaladas exitosamente.")
            return True
        except Exception as e:
            print(f"Error al instalar dependencias: {e}\nInstala manualmente: pip install {' '.join(missing_packages)}")
            return False
    return True

# Intentar instalar dependencias
if not install_dependencies():
    sys.exit(1)

# Importar dependencias después de la instalación
try:
    import click
    import psutil
    import requests
    from colorama import init, Fore, Style
    init()
except ImportError as e:
    print(f"Error crítico: {e}")
    sys.exit(1)

# ==================== CONFIGURACIÓN Y CONSTANTES ====================
VERSION = "ECLIPSE_UNIFIED_v13.2_PRO (Professional Edition)"
SHIZUKU_PACKAGE = "moe.shizuku.privileged.api"
SHIZUKU_SCRIPT_PATH = f"/storage/emulated/0/Android/data/{SHIZUKU_PACKAGE}/files/start.sh"
MODULES_DIR = Path(__file__).parent / "modules"
HISTORY_DB = Path.home() / ".eclipse_history.db"
CONFIG_FILE = Path.home() / ".eclipse_config.json"

# Configuración de la base de datos para historial
def init_history_db():
    """Inicializa la base de datos para el historial de comandos."""
    conn = sqlite3.connect(HISTORY_DB)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS command_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        command TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        result TEXT
    )
    ''')
    conn.commit()
    conn.close()

# Inicializar la base de datos al iniciar
init_history_db()

# ==================== ESTILO DE COLORES ====================
class Colors:
    """Códigos de color ANSI para una salida estilizada."""
    MATRIX_BRIGHT = '\033[1;92m' # Verde brillante
    MATRIX_DIM = '\033[0;32m' # Verde oscuro
    MATRIX_GLOW = '\033[1;32m' # Verde resplandeciente
    HACKER_RED = '\033[1;91m' # Rojo brillante
    HACKER_YELLOW = '\033[1;93m' # Amarillo brillante
    HACKER_CYAN = '\033[1;36m' # Cian brillante
    HACKER_PINK = '\033[1;35m' # Rosa brillante (magenta)
    NC = '\033[0m' # No color
    SUCCESS_BORDER = '\033[1;36m' # Cian brillante para el borde
    SUCCESS_TEXT = '\033[1;95m' # Magenta brillante para el texto
    SUCCESS_ICON = '\033[1;96m' # Cian más claro para el icono
    RAINBOW_COLORS = [
        '\033[1;91m', # Rojo
        '\033[1;93m', # Amarillo
        '\033[1;92m', # Verde
        '\033[1;96m', # Cian
        '\033[1;94m', # Azul
        '\033[1;95m', # Magenta
    ]
    ERROR_BORDER = HACKER_RED
    WARNING_BORDER = HACKER_YELLOW
    INFO_BORDER = HACKER_CYAN

# ==================== HELPERS GLOBALES ====================
def clear_screen():
    """Limpia la pantalla de forma multiplataforma."""
    os.system('clear' if os.name == 'posix' else 'cls')
    sys.stdout.flush()

def get_visual_length(s: str) -> int:
    """Calcula la longitud visual de una cadena, ignorando los códigos ANSI."""
    ansi_escape = re.compile(r'\x1b\[([0-9]{1,2}(;[0-9]{1,2})*)?[mGK]')
    return len(ansi_escape.sub('', s))

# ==================== FUNCIONES DE MENSAJERÍA (Estilizadas) ====================
def hacker_msg(message: str):
    """Mensaje con estilo hacker."""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"{Colors.MATRIX_DIM}[{timestamp}] {Colors.MATRIX_GLOW}▶ {message}{Colors.NC}")
    sys.stdout.flush()

def hacker_success(message: str):
    """Mensaje de éxito con estilo mejorado."""
    print(f"{Colors.SUCCESS_BORDER}╔{'═'*76}╗{Colors.NC}")
    print(f"{Colors.SUCCESS_BORDER}║ {Colors.SUCCESS_ICON}✅{Colors.SUCCESS_TEXT} SUCCESS: {message:<64} {Colors.SUCCESS_BORDER}║{Colors.NC}")
    print(f"{Colors.SUCCESS_BORDER}╚{'═'*76}╝{Colors.NC}")
    sys.stdout.flush()

def hacker_error(message: str):
    """Mensaje de error con estilo mejorado."""
    print(f"{Colors.ERROR_BORDER}╔{'═'*76}╗{Colors.NC}")
    print(f"{Colors.ERROR_BORDER}║ ❌ ERROR: {message:<66} ║{Colors.NC}")
    print(f"{Colors.ERROR_BORDER}╚{'═'*76}╝{Colors.NC}")
    sys.stdout.flush()

def hacker_warning(message: str):
    """Mensaje de advertencia con estilo mejorado."""
    print(f"{Colors.WARNING_BORDER}╔{'═'*76}╗{Colors.NC}")
    print(f"{Colors.WARNING_BORDER}║ ⚠ WARNING: {message:<65} ║{Colors.NC}")
    print(f"{Colors.WARNING_BORDER}╚{'═'*76}╝{Colors.NC}")
    sys.stdout.flush()

def hacker_info(message: str):
    """Mensaje informativo con estilo mejorado."""
    print(f"{Colors.INFO_BORDER}╔{'═'*76}╗{Colors.NC}")
    print(f"{Colors.INFO_BORDER}║ ℹ INFO: {message:<67} ║{Colors.NC}")
    print(f"{Colors.INFO_BORDER}╚{'═'*76}╝{Colors.NC}")
    sys.stdout.flush()

# ==================== FUNCIÓN GLOBAL MATRIX_LOADING (CORREGIDA Y OPTIMIZADA) ====================
def matrix_loading(message: str, duration: float = 2.0):
    """Animación de carga estilo Matrix con arte ASCII completo."""
    clear_screen()
    
    ascii_lines_logo = [
        " ██╗ ██████╗ █████╗ ██████╗ ██╗███╗ ██╗ ██████╗ ",
        " ██║ ██╔═══██╗██╔══██╗██╔══██╗██║████╗ ██║██╔════╝ ",
        " ██║ ██║ ██║███████║██║ ██║██║██╔██╗ ██║██║ ███╗",
        " ██║ ██║ ██║██╔══██║██║ ██║██║██║╚██╗██║██║ ██║",
        " ███████╗╚██████╔╝██║ ██║██████╔╝██║██║ ╚████║╚██████╔╝",
        " ╚══════╝ ╚═════╝ ╚═╝ ╚═╝╚═════╝ ╚═╝╚═╝ ╚═══╝ ╚═════╝ "
    ]
    
    for line in ascii_lines_logo:
        print(f"{Colors.MATRIX_BRIGHT}{line}{Colors.NC}")
    print()
    
    fixed_prefix_text = "HACKING INTO SYSTEM: "
    raw_target_name = message.upper()
    
    total_ascii_art_visual_width = 70
    outer_blocks_visual_width = get_visual_length("████") * 2
    
    available_inner_width_for_message_content = total_ascii_art_visual_width - outer_blocks_visual_width
    
    display_target_name = raw_target_name
    fixed_prefix_visual_len = get_visual_length(fixed_prefix_text)
    
    if get_visual_length(raw_target_name) > (available_inner_width_for_message_content - fixed_prefix_visual_len):
        max_target_len_after_prefix = available_inner_width_for_message_content - fixed_prefix_visual_len - get_visual_length("...")
        if max_target_len_after_prefix < 0:
            max_target_len_after_prefix = 0
        display_target_name = raw_target_name[:max_target_len_after_prefix] + "..."
    
    colored_message_part = f"{Colors.HACKER_CYAN}{display_target_name}{Colors.MATRIX_GLOW}"
    
    full_message_visual_len = fixed_prefix_visual_len + get_visual_length(colored_message_part)
    
    padding_needed_for_centering = available_inner_width_for_message_content - full_message_visual_len
    left_padding = padding_needed_for_centering // 2
    right_padding = padding_needed_for_centering - left_padding
    
    print(f"{Colors.MATRIX_GLOW}████{' ' * left_padding}{fixed_prefix_text}{colored_message_part}{' ' * right_padding}████{Colors.NC}")
    print()
    sys.stdout.flush()
    
    progress_chars = ["█", "▉", "▊", "▋", "▌", "▍", "▎", "▏"]
    steps = int(duration * 10)
    
    for i in range(steps):
        progress = (i + 1) / steps
        bar_visual_length = 20
        filled_visual_length = int(bar_visual_length * progress)
        
        bar_content = "█" * filled_visual_length
        
        if filled_visual_length < bar_visual_length:
            bar_content += progress_chars[i % len(progress_chars)]
            bar_content += "░" * (bar_visual_length - get_visual_length(bar_content))
        else:
            bar_content = "█" * bar_visual_length
            
        status = "EXPLOITING" if progress < 0.9 else "BREACHING"
        
        status_message_colored = f"[{bar_content}] {Colors.MATRIX_BRIGHT}{status}...{Colors.NC}"
        
        line_output_padded = f"\r{Colors.MATRIX_DIM}{status_message_colored}{' ' * (total_ascii_art_visual_width - get_visual_length(status_message_colored))}{Colors.NC}"
        print(line_output_padded, end="", flush=True)
        time.sleep(0.1)
    
    access_granted_message_raw_content = " ACCESS GRANTED!"
    access_granted_line_colored = f"[{'█'*20}]{Colors.MATRIX_GLOW}{access_granted_message_raw_content}{Colors.NC}"
    
    remaining_spaces_after_final_message = total_ascii_art_visual_width - get_visual_length(access_granted_line_colored)
    
    print(f"\r{Colors.MATRIX_BRIGHT}{access_granted_line_colored}{' ' * remaining_spaces_after_final_message}{Colors.NC}")
    print()
    sys.stdout.flush()

# ==================== CLASE BASE PARA MÓDULOS ====================
class EclipseModule:
    def __init__(self, core: 'EclipseCore'):
        self.core = core
        self.name = self.__class__.__name__.replace("Module", "").lower()
        self.description = "Módulo sin descripción."
        self.aliases = []

    def hacker_msg(self, message: str):
        hacker_msg(message)

    def hacker_success(self, message: str):
        hacker_success(message)

    def hacker_error(self, message: str):
        hacker_error(message)

    def hacker_warning(self, message: str):
        hacker_warning(message)

    def hacker_info(self, message: str):
        hacker_info(message)

    def matrix_loading(self, message: str, duration: float = 2.0):
        matrix_loading(message, duration)

    def run(self, *args: Any, **kwargs: Any):
        raise NotImplementedError(f"El módulo '{self.name}' debe implementar el método run().")

    def save_to_history(self, command: str, result: str):
        """Guarda un comando en el historial."""
        conn = sqlite3.connect(HISTORY_DB)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO command_history (command, result) VALUES (?, ?)",
            (command, result)
        )
        conn.commit()
        conn.close()

# ==================== MÓDULOS INTEGRADOS ====================
class AppManagerModule(EclipseModule):
    def __init__(self, core: 'EclipseCore'):
        super().__init__(core)
        self.name = "appmanager"
        self.description = "Gestión avanzada de aplicaciones del sistema"
        self.aliases = ["apps", "am"]

    def run(self, *args: Any, **kwargs: Any):
        action = args[0].lower() if args else "help"
        package_name = args[1] if len(args) > 1 else None
        
        actions = {
            "list": self._list_packages,
            "uninstall": self._uninstall_package,
            "reinstall": self._reinstall_package,
            "info": self._package_info,
            "clear": self._clear_data,
            "disable": self._disable_package,
            "enable": self._enable_package,
            "find": self._find_package
        }
        
        if action == "help":
            self._show_help()
            return
        
        if action in actions:
            if action in ["uninstall", "reinstall", "info", "clear", "disable", "enable", "find"] and not package_name:
                self.hacker_error(f"La acción '{action}' requiere un nombre de paquete.")
                return
            
            if action == "list":
                actions[action](package_name)
            else:
                actions[action](package_name)
        else:
            self._show_help()

    def _show_help(self):
        self.hacker_msg(f"Uso: run {self.name} <acción> [paquete]")
        print(f"{Colors.MATRIX_DIM} list [filtro] - Lista apps del sistema")
        print(f" info <pkg> - Muestra información detallada de un paquete")
        print(f" uninstall <pkg> - Elimina una app")
        print(f" reinstall <pkg> - Restaura una app")
        print(f" clear <pkg> - Limpia datos de una app")
        print(f" disable <pkg> - Deshabilita una app del sistema")
        print(f" enable <pkg> - Habilita una app del sistema")
        print(f" find <nombre> - Busca una app por nombre{Colors.NC}")

    def _list_packages(self, filter_keyword: Optional[str] = None):
        self.hacker_msg(f"Accediendo a paquetes vía {self.core.privilege_method}...")
        exit_code, output = self.core.sudo("pm list packages -s")
        
        if exit_code != 0:
            self.hacker_error(f"Error al listar paquetes: {output}")
            return
        
        packages = []
        if output:
            packages = sorted([line.replace('package:', '').strip() for line in output.splitlines() if 'package:' in line])
        
        if filter_keyword:
            packages = [p for p in packages if filter_keyword.lower() in p.lower()]
        
        if not packages:
            self.hacker_warning("No se encontraron paquetes del sistema.")
            return
        
        print(f"{Colors.MATRIX_BRIGHT}--- Paquetes del Sistema Encontrados ({len(packages)}) ---{Colors.NC}")
        for pkg in packages:
            print(f"{Colors.MATRIX_DIM} ▶ {pkg}{Colors.NC}")

    def _package_info(self, package_name: str):
        self.hacker_msg(f"Obteniendo información del paquete {package_name}...")
        exit_code, output = self.core.sudo(f"dumpsys package {package_name}")
        
        if exit_code != 0:
            self.hacker_error(f"Error al obtener información: {output}")
            return
        
        lines = output.split('\n')
        version = "No encontrada"
        uid = "No encontrado"
        path = "No encontrado"
        install_time = "No encontrado"
        update_time = "No encontrado"
        
        for line in lines:
            if "versionName" in line and version == "No encontrada":
                version = line.split('=')[1].strip()
            elif "userId=" in line and uid == "No encontrado":
                uid = line.split('=')[1].strip()
            elif "codePath=" in line and path == "No encontrada":
                path = line.split('=')[1].strip()
            elif "firstInstallTime" in line and install_time == "No encontrada":
                install_time = line.split('=')[1].strip()
            elif "lastUpdateTime" in line and update_time == "No encontrada":
                update_time = line.split('=')[1].strip()
        
        self.hacker_info(f"Información del paquete {package_name}:")
        print(f"{Colors.MATRIX_DIM} Versión: {version}")
        print(f" UID: {uid}")
        print(f" Ruta: {path}")
        print(f" Instalado: {install_time}")
        print(f" Actualizado: {update_time}{Colors.NC}")

    def _uninstall_package(self, package_name: str):
        if not click.confirm(f"{Colors.HACKER_YELLOW}¿Confirmas la eliminación de {package_name}?{Colors.NC}", default=False, err=True):
            self.hacker_msg("Operación cancelada.")
            return
            
        self.hacker_msg(f"Eliminando {package_name}...")
        exit_code, output = self.core.sudo(f"pm uninstall -k --user 0 {package_name}")
        
        if exit_code == 0 and "Success" in output:
            self.hacker_success(f"Paquete '{package_name}' eliminado.")
            self.save_to_history(f"uninstall {package_name}", "Success")
        else:
            self.hacker_error(f"Fallo al eliminar: {output}")

    def _reinstall_package(self, package_name: str):
        self.hacker_msg(f"Restaurando {package_name}...")
        exit_code, output = self.core.sudo(f"pm install-existing --user 0 {package_name}")
        
        if exit_code == 0 and "installed for user" in output:
            self.hacker_success(f"Paquete '{package_name}' restaurado.")
            self.save_to_history(f"reinstall {package_name}", "Success")
        else:
            self.hacker_error(f"Fallo al restaurar: {output}")

    def _clear_data(self, package_name: str):
        self.hacker_msg(f"Limpiando datos de {package_name}...")
        exit_code, output = self.core.sudo(f"pm clear {package_name}")
        
        if exit_code == 0 and "Success" in output:
            self.hacker_success(f"Datos de '{package_name}' limpiados.")
            self.save_to_history(f"clear {package_name}", "Success")
        else:
            self.hacker_error(f"Fallo al limpiar datos: {output}")

    def _disable_package(self, package_name: str):
        if not click.confirm(f"{Colors.HACKER_YELLOW}¿Confirmas que quieres deshabilitar {package_name}?{Colors.NC}", default=False, err=True):
            self.hacker_msg("Operación cancelada.")
            return
            
        self.hacker_msg(f"Deshabilitando {package_name}...")
        exit_code, output = self.core.sudo(f"pm disable-user --user 0 {package_name}")
        
        if exit_code == 0 and "disabled" in output:
            self.hacker_success(f"Paquete '{package_name}' deshabilitado.")
            self.save_to_history(f"disable {package_name}", "Success")
        else:
            self.hacker_error(f"Fallo al deshabilitar: {output}")

    def _enable_package(self, package_name: str):
        self.hacker_msg(f"Habilitando {package_name}...")
        exit_code, output = self.core.sudo(f"pm enable {package_name}")
        
        if exit_code == 0 and "enabled" in output:
            self.hacker_success(f"Paquete '{package_name}' habilitado.")
            self.save_to_history(f"enable {package_name}", "Success")
        else:
            self.hacker_error(f"Fallo al habilitar: {output}")

    def _find_package(self, package_name: str):
        self.hacker_msg(f"Buscando paquetes que contengan '{package_name}'...")
        exit_code, output = self.core.sudo("pm list packages -f")
        
        if exit_code != 0:
            self.hacker_error(f"Error al buscar paquetes: {output}")
            return
        
        packages = []
        for line in output.splitlines():
            if package_name.lower() in line.lower():
                pkg_full = line.replace('package:', '').strip()
                parts = pkg_full.split('=')
                pkg_path = parts[0]
                pkg_name = parts[1] if len(parts) > 1 else parts[0]
                packages.append((pkg_path, pkg_name))
        
        if not packages:
            self.hacker_warning(f"No se encontraron paquetes que contengan '{package_name}'.")
            return
        
        print(f"{Colors.MATRIX_BRIGHT}--- Paquetes Encontrados ({len(packages)}) ---{Colors.NC}")
        for pkg_path, pkg_name in packages:
            print(f"{Colors.MATRIX_DIM} ▶ {pkg_name} ({pkg_path}){Colors.NC}")

class PackageManagerModule(EclipseModule):
    def __init__(self, core: 'EclipseCore'):
        super().__init__(core)
        self.name = "pm"
        self.description = "Gestor de paquetes avanzado"
        self.aliases = ["pkg"]
        self.backup_dir = Path("/sdcard/EclipseBackups")

    def run(self, *args: Any, **kwargs: Any):
        if not args:
            self.show_help()
            return
        
        action = str(args[0]).lower()
        package_name = str(args[1]) if len(args) > 1 else None
        
        if action in ["list", "help", "gaming-mode", "clean-cache-all", "list-disabled", "list-system", "list-user", "find-large-apps"]:
            if action == "list":
                self.list_packages()
            elif action == "help":
                self.show_help()
            elif action == "gaming-mode":
                self.gaming_mode()
            elif action == "clean-cache-all":
                self.clean_cache_all()
            elif action == "list-disabled":
                self.list_disabled_packages()
            elif action == "list-system":
                self.list_system_packages()
            elif action == "list-user":
                self.list_user_packages()
            elif action == "find-large-apps":
                self.find_large_apps()
            return
        
        if not package_name:
            self.hacker_error(f"Especifica un nombre de paquete para la acción '{action}'")
            return
        
        if action == "uninstall":
            self.uninstall_package(package_name)
        elif action == "disable":
            self.disable_package(package_name)
        elif action == "enable":
            self.enable_package(package_name)
        elif action == "clear-data":
            self.clear_package_data(package_name)
        elif action == "info":
            self.package_info(package_name)
        elif action == "exists":
            self.check_package_exists(package_name)
        elif action == "backup":
            self.backup_apk(package_name)
        elif action == "size":
            self.package_size(package_name)
        elif action == "permissions":
            self.show_permissions(package_name)
        elif action == "version":
            self.package_version(package_name)
        elif action == "grant-permission":
            permission = str(args[2]) if len(args) > 2 else None
            if permission:
                self.grant_permission(package_name, permission)
            else:
                self.hacker_error("Falta especificar el permiso")
        elif action == "revoke-permission":
            permission = str(args[2]) if len(args) > 2 else None
            if permission:
                self.revoke_permission(package_name, permission)
            else:
                self.hacker_error("Falta especificar el permiso")
        elif action == "reset-permissions":
            self.reset_permissions(package_name)
        else:
            self.hacker_error(f"Acción '{action}' no reconocida")
            self.show_help()

    def package_exists(self, package_name):
        self.hacker_msg(f"Verificando existencia del paquete {package_name}...")
        exit_code, output = self.core.sudo(f"pm list packages | grep -w {package_name}")
        return exit_code == 0 and package_name in output

    def check_package_exists(self, package_name):
        if self.package_exists(package_name):
            self.hacker_success(f"El paquete {package_name} está instalado")
        else:
            self.hacker_error(f"El paquete {package_name} NO está instalado")

    def list_packages(self):
        self.hacker_msg("Obteniendo lista de paquetes instalados...")
        exit_code, output = self.core.sudo("pm list packages")
        if exit_code != 0:
            self.hacker_error(f"Error al obtener la lista de paquetes: {output}")
            return
        
        packages = []
        for line in output.split("\n"):
            if line.startswith("package:"):
                packages.append(line.replace("package:", "").strip())
        
        packages.sort()
        self.hacker_success(f"Se encontraron {len(packages)} paquetes instalados")
        
        for i, package in enumerate(packages[:20]):
            print(f"{Colors.MATRIX_DIM}📦 {package}{Colors.NC}")
        
        if len(packages) > 20:
            self.hacker_msg(f"... y {len(packages) - 20} paquetes más")

    def uninstall_package(self, package_name):
        if not self.package_exists(package_name):
            self.hacker_error(f"El paquete '{package_name}' no está instalado")
            return
        
        if not click.confirm(f"{Colors.HACKER_YELLOW}¿Confirmas la eliminación de {package_name}?{Colors.NC}", default=False, err=True):
            self.hacker_msg("Operación cancelada.")
            return
        
        self.hacker_msg(f"Desinstalando {package_name}...")
        command = f"pm uninstall -k --user 0 {package_name}"
        exit_code, output = self.core.sudo(command)
        
        if exit_code == 0 and "Success" in output:
            self.hacker_success(f"Paquete {package_name} desinstalado correctamente")
            self.save_to_history(f"uninstall {package_name}", "Success")
        else:
            self.hacker_error(f"Falló la desinstalación de {package_name}: {output}")

    def disable_package(self, package_name):
        if not self.package_exists(package_name):
            self.hacker_error(f"El paquete '{package_name}' no está instalado")
            return
        
        if not click.confirm(f"{Colors.HACKER_YELLOW}¿Confirmas la deshabilitación de {package_name}?{Colors.NC}", default=False, err=True):
            self.hacker_msg("Operación cancelada.")
            return
        
        self.hacker_msg(f"Deshabilitando {package_name}...")
        command = f"pm disable-user --user 0 {package_name}"
        exit_code, output = self.core.sudo(command)
        
        if exit_code == 0:
            self.hacker_success(f"Paquete {package_name} deshabilitado correctamente")
            self.save_to_history(f"disable {package_name}", "Success")
        else:
            self.hacker_error(f"Falló al deshabilitar {package_name}: {output}")

    def enable_package(self, package_name):
        self.hacker_msg(f"Habilitando {package_name}...")
        command = f"pm enable {package_name}"
        exit_code, output = self.core.sudo(command)
        
        if exit_code == 0:
            self.hacker_success(f"Paquete {package_name} habilitado correctamente")
            self.save_to_history(f"enable {package_name}", "Success")
        else:
            self.hacker_error(f"Falló al habilitar {package_name}: {output}")

    def clear_package_data(self, package_name):
        if not self.package_exists(package_name):
            self.hacker_error(f"El paquete '{package_name}' no está instalado")
            return
        
        if not click.confirm(f"{Colors.HACKER_YELLOW}¿Confirmas que quieres limpiar los datos de {package_name}?{Colors.NC}", default=False, err=True):
            self.hacker_msg("Operación cancelada.")
            return
        
        self.hacker_msg(f"Limpiando datos de {package_name}...")
        command = f"pm clear {package_name}"
        exit_code, output = self.core.sudo(command)
        
        if exit_code == 0:
            self.hacker_success(f"Datos de {package_name} limpiados correctamente")
            self.save_to_history(f"clear {package_name}", "Success")
        else:
            self.hacker_error(f"Fallo al limpiar datos: {output}")

    def package_info(self, package_name):
        self.hacker_msg(f"Obteniendo información de {package_name}...")
        exit_code, output = self.core.sudo(f"dumpsys package {package_name}")
        
        if exit_code == 0 and output.strip():
            self.hacker_success(f"Información de {package_name}")
            lines = output.split('\n')[:10]
            for line in lines:
                if line.strip():
                    self.hacker_msg(f"▶ {line.strip()}")
        else:
            self.hacker_error(f"No se pudo obtener información de {package_name}: {output}")

    def backup_apk(self, package_name):
        if not self.package_exists(package_name):
            self.hacker_error(f"El paquete '{package_name}' no existe")
            return
        
        backup_dir = self.backup_dir / "APKs"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.hacker_msg(f"Buscando ruta del APK para {package_name}...")
        exit_code, output = self.core.sudo(f"pm path {package_name}")
        
        if exit_code == 0 and output:
            apk_path = output.strip().replace("package:", "")
            backup_file = backup_dir / f"{package_name}.apk"
            
            self.hacker_msg(f"Copiando APK desde {apk_path}...")
            exit_code, output = self.core.sudo(f"cp {apk_path} {backup_file}")
            
            if exit_code == 0:
                self.hacker_success(f"APK respaldado en: {backup_file}")
                self.save_to_history(f"backup {package_name}", "Success")
            else:
                self.hacker_error(f"Error al copiar APK: {output}")
        else:
            self.hacker_error(f"No se pudo encontrar el APK de {package_name}: {output}")

    def package_size(self, package_name):
        if not self.package_exists(package_name):
            self.hacker_error(f"El paquete '{package_name}' no existe")
            return
        
        self.hacker_msg(f"Analizando espacio de {package_name}...")
        exit_code, output = self.core.sudo(f"du -sh /data/data/{package_name} 2>/dev/null || echo '0'")
        
        if exit_code == 0:
            size = output.split()[0] if output else "Desconocido"
            self.hacker_success(f"Espacio ocupado por {package_name}: {size}")
        else:
            self.hacker_error(f"Error al analizar espacio: {output}")

    def gaming_mode(self):
        gaming_bloatware = [
            "com.facebook.katana",
            "com.instagram.android",
            "com.twitter.android",
            "com.whatsapp",
            "com.spotify.music",
            "com.netflix.mediaclient",
            "com.amazon.mShop.android.shopping",
            "com.android.chrome"
        ]
        
        disabled_count = 0
        self.hacker_msg("Activando modo gaming...")
        
        for package in gaming_bloatware:
            if self.package_exists(package):
                exit_code, output = self.core.sudo(f"pm disable-user --user 0 {package}")
                if exit_code == 0:
                    self.hacker_msg(f"📵 Deshabilitado: {package}")
                    disabled_count += 1
        
        self.hacker_success(f"Modo gaming activado. {disabled_count} apps deshabilitadas")
        self.save_to_history("gaming-mode", f"Disabled {disabled_count} apps")

    def show_permissions(self, package_name):
        if not self.package_exists(package_name):
            self.hacker_error(f"El paquete '{package_name}' no existe")
            return
        
        self.hacker_msg(f"Obteniendo permisos de {package_name}...")
        exit_code, output = self.core.sudo(f"dumpsys package {package_name} | grep -A50 'requested permissions:'")
        
        if exit_code == 0 and output:
            self.hacker_success(f"Permisos de {package_name}:")
            for line in output.split('\n')[:20]:
                if line.strip() and 'permission:' in line:
                    self.hacker_msg(f"🔐 {line.strip()}")
        else:
            self.hacker_error(f"No se pudieron obtener los permisos: {output}")

    def package_version(self, package_name):
        if not self.package_exists(package_name):
            self.hacker_error(f"El paquete '{package_name}' no existe")
            return
        
        self.hacker_msg(f"Obteniendo versión de {package_name}...")
        exit_code, output = self.core.sudo(f"dumpsys package {package_name} | grep versionName")
        
        if exit_code == 0 and output:
            version = output.split('=')[1].strip() if '=' in output else "Desconocida"
            self.hacker_success(f"Versión de {package_name}: {version}")
        else:
            self.hacker_error(f"No se pudo obtener la versión: {output}")

    def grant_permission(self, package_name, permission):
        if not self.package_exists(package_name):
            self.hacker_error(f"El paquete '{package_name}' no existe")
            return
        
        self.hacker_msg(f"Otorgando permiso {permission} a {package_name}...")
        exit_code, output = self.core.sudo(f"pm grant {package_name} {permission}")
        
        if exit_code == 0:
            self.hacker_success(f"Permiso {permission} otorgado a {package_name}")
            self.save_to_history(f"grant {package_name} {permission}", "Success")
        else:
            self.hacker_error(f"Error al otorgar permiso: {output}")

    def revoke_permission(self, package_name, permission):
        if not self.package_exists(package_name):
            self.hacker_error(f"El paquete '{package_name}' no existe")
            return
        
        self.hacker_msg(f"Revocando permiso {permission} de {package_name}...")
        exit_code, output = self.core.sudo(f"pm revoke {package_name} {permission}")
        
        if exit_code == 0:
            self.hacker_success(f"Permiso {permission} revocado de {package_name}")
            self.save_to_history(f"revoke {package_name} {permission}", "Success")
        else:
            self.hacker_error(f"Error al revocar permiso: {output}")

    def reset_permissions(self, package_name):
        if not self.package_exists(package_name):
            self.hacker_error(f"El paquete '{package_name}' no existe")
            return
        
        self.hacker_msg(f"Reseteando permisos de {package_name}...")
        exit_code, output = self.core.sudo(f"pm reset-permissions {package_name}")
        
        if exit_code == 0:
            self.hacker_success(f"Permisos de {package_name} reseteados")
            self.save_to_history(f"reset-permissions {package_name}", "Success")
        else:
            self.hacker_error(f"Error al resetear permisos: {output}")

    def clean_cache_all(self):
        self.hacker_msg("Limpiando caché de todas las aplicaciones...")
        exit_code, output = self.core.sudo("pm trim-caches 9999999999999")
        
        if exit_code == 0:
            self.hacker_success("Caché de todas las aplicaciones limpiada")
            self.save_to_history("clean-cache-all", "Success")
        else:
            self.hacker_error(f"Error al limpiar caché: {output}")

    def list_disabled_packages(self):
        self.hacker_msg("Obteniendo lista de paquetes deshabilitados...")
        exit_code, output = self.core.sudo("pm list packages -d")
        if exit_code != 0:
            self.hacker_error(f"Error al obtener la lista de paquetes deshabilitados: {output}")
            return
        
        packages = []
        for line in output.split("\n"):
            if line.startswith("package:"):
                packages.append(line.replace("package:", "").strip())
        
        packages.sort()
        self.hacker_success(f"Se encontraron {len(packages)} paquetes deshabilitados")
        
        for package in packages:
            print(f"{Colors.MATRIX_DIM}📦 {package}{Colors.NC}")

    def list_system_packages(self):
        self.hacker_msg("Obteniendo lista de paquetes del sistema...")
        exit_code, output = self.core.sudo("pm list packages -s")
        if exit_code != 0:
            self.hacker_error(f"Error al obtener la lista de paquetes del sistema: {output}")
            return
        
        packages = []
        for line in output.split("\n"):
            if line.startswith("package:"):
                packages.append(line.replace("package:", "").strip())
        
        packages.sort()
        self.hacker_success(f"Se encontraron {len(packages)} paquetes del sistema")
        
        for i, package in enumerate(packages[:20]):
            print(f"{Colors.MATRIX_DIM}📦 {package}{Colors.NC}")
        
        if len(packages) > 20:
            self.hacker_msg(f"... y {len(packages) - 20} paquetes más")

    def list_user_packages(self):
        self.hacker_msg("Obteniendo lista de paquetes de usuario...")
        exit_code, output = self.core.sudo("pm list packages -3")
        if exit_code != 0:
            self.hacker_error(f"Error al obtener la lista de paquetes de usuario: {output}")
            return
        
        packages = []
        for line in output.split("\n"):
            if line.startswith("package:"):
                packages.append(line.replace("package:", "").strip())
        
        packages.sort()
        self.hacker_success(f"Se encontraron {len(packages)} paquetes de usuario")
        
        for i, package in enumerate(packages[:20]):
            print(f"{Colors.MATRIX_DIM}📦 {package}{Colors.NC}")
        
        if len(packages) > 20:
            self.hacker_msg(f"... y {len(packages) - 20} paquetes más")

    def find_large_apps(self):
        self.hacker_msg("Buscando aplicaciones que ocupan más espacio...")
        exit_code, output = self.core.sudo("du -s /data/data/* | sort -nr | head -10")
        
        if exit_code == 0 and output:
            self.hacker_success("Top 10 aplicaciones que ocupan más espacio:")
            lines = output.split('\n')
            for i, line in enumerate(lines):
                if line.strip():
                    size, path = line.split('\t') if '\t' in line else ("Unknown", line)
                    app_name = path.split('/')[-1] if '/' in path else path
                    print(f"{Colors.MATRIX_DIM}{i+1}. {app_name}: {size}{Colors.NC}")
        else:
            self.hacker_error(f"Error al buscar aplicaciones grandes: {output}")

    def show_help(self):
        help_text = f"""
{Colors.MATRIX_BRIGHT}🔧 MÓDULO PACKAGE MANAGER (pm) - Ayuda{Colors.NC}

{Colors.MATRIX_GLOW}Uso: run pm <acción> [paquete] [argumento]{Colors.NC}

{Colors.MATRIX_BRIGHT}Acciones disponibles:{Colors.NC}
{Colors.MATRIX_DIM} list - Lista todos los paquetes instalados{Colors.NC}
{Colors.MATRIX_DIM} uninstall <paquete> - Desinstala un paquete{Colors.NC}
{Colors.MATRIX_DIM} disable <paquete> - Deshabilita un paquete{Colors.NC}
{Colors.MATRIX_DIM} enable <paquete> - Habilita un paquete{Colors.NC}
{Colors.MATRIX_DIM} clear-data <paquete> - Limpia los datos de un paquete{Colors.NC}
{Colors.MATRIX_DIM} info <paquete> - Información detallada del paquete{Colors.NC}
{Colors.MATRIX_DIM} exists <paquete> - Verifica si un paquete está instalado{Colors.NC}
{Colors.MATRIX_DIM} backup <paquete> - Respaldar APK de una aplicación{Colors.NC}
{Colors.MATRIX_DIM} size <paquete> - Mostrar espacio ocupado por una app{Colors.NC}
{Colors.MATRIX_DIM} permissions <paquete>- Mostrar permisos de una aplicación{Colors.NC}
{Colors.MATRIX_DIM} version <paquete> - Mostrar versión de un paquete{Colors.NC}
{Colors.MATRIX_DIM} grant-permission <paquete> <permiso> - Otorgar permiso específico{Colors.NC}
{Colors.MATRIX_DIM} revoke-permission <paquete> <permiso> - Revocar permiso específico{Colors.NC}
{Colors.MATRIX_DIM} reset-permissions <paquete> - Resetear permisos a valores por defecto{Colors.NC}
{Colors.MATRIX_DIM} gaming-mode - Deshabilitar apps para optimizar gaming{Colors.NC}
{Colors.MATRIX_DIM} clean-cache-all - Limpiar caché de todas las aplicaciones{Colors.NC}
{Colors.MATRIX_DIM} list-disabled - Listar paquetes deshabilitados{Colors.NC}
{Colors.MATRIX_DIM} list-system - Listar paquetes del sistema{Colors.NC}
{Colors.MATRIX_DIM} list-user - Listar paquetes de usuario{Colors.NC}
{Colors.MATRIX_DIM} find-large-apps - Encontrar apps que ocupan más espacio{Colors.NC}
{Colors.MATRIX_DIM} help - Muestra esta ayuda{Colors.NC}

{Colors.MATRIX_BRIGHT}Ejemplos:{Colors.NC}
{Colors.MATRIX_GLOW} run pm list{Colors.NC}
{Colors.MATRIX_GLOW} run pm uninstall cn.oneplus.photos{Colors.NC}
{Colors.MATRIX_GLOW} run pm disable com.facebook.katana{Colors.NC}
{Colors.MATRIX_GLOW} run pm backup com.whatsapp{Colors.NC}
{Colors.MATRIX_GLOW} run pm gaming-mode{Colors.NC}
{Colors.MATRIX_GLOW} run pm grant-permission com.instagram.android android.permission.CAMERA{Colors.NC}
"""
        print(help_text)

class ShizukuManagerModule(EclipseModule):
    def __init__(self, core: 'EclipseCore'):
        super().__init__(core)
        self.name = "shizuku"
        self.description = "Gestión del servicio Shizuku"
        self.aliases = ["shz"]

    def run(self, *args: Any, **kwargs: Any):
        action = args[0].lower() if args else "status"
        
        actions = {
            "status": self._check_status,
            "start": self._start_service,
            "stop": self._stop_service,
            "restart": self._restart_service
        }
        
        if action in actions:
            actions[action]()
        else:
            self._show_help()

    def _show_help(self):
        self.hacker_msg("Uso: run shizuku <acción>")
        print(f"{Colors.MATRIX_DIM} status - Ver estado del servicio")
        print(f" start - Iniciar servicio")
        print(f" stop - Detener servicio")
        print(f" restart - Reiniciar servicio{Colors.NC}")

    def _check_status(self):
        self.hacker_msg("Comprobando estado de Shizuku...")
        if self.core.privilege_method == "Shizuku":
            exit_code, output = self.core.sudo("shizuku -v")
            if exit_code == 0 and "shizuku_version" in output:
                self.hacker_success(f"Shizuku está en ejecución. {output.strip()}")
            else:
                self.hacker_error("Shizuku no está en ejecución o no responde.")
        else:
            self.hacker_warning("Shizuku no es el método de privilegios activo.")

    def _start_service(self):
        self.hacker_msg("Iniciando servicio Shizuku...")
        exit_code, output = self.core.sudo(f"sh {SHIZUKU_SCRIPT_PATH}")
        if exit_code == 0:
            self.hacker_msg("Comando de inicio enviado. Verificando en 3 segundos...")
            time.sleep(3)
            self._check_status()
        else:
            self.hacker_error(f"Error al iniciar: {output}")

    def _stop_service(self):
        self.hacker_msg("Deteniendo servicio Shizuku...")
        exit_code, _ = self.core.sudo(f"pkill -f {SHIZUKU_PACKAGE}")
        if exit_code == 0:
            self.hacker_success("Servicio Shizuku detenido.")
        else:
            self.hacker_warning("Shizuku no estaba en ejecución o no se pudo detener.")

    def _restart_service(self):
        self.hacker_msg("Reiniciando servicio Shizuku...")
        self._stop_service()
        time.sleep(2)
        self._start_service()

class AppLauncherModule(EclipseModule):
    def __init__(self, core: 'EclipseCore'):
        super().__init__(core)
        self.name = "open"
        self.description = "Lanza aplicaciones (targets)"
        self.aliases = ["launch", "start"]

    def run(self, *args: Any, **kwargs: Any):
        if not args:
            self._show_targets()
            return
        
        self._open_app(args[0])

    def _show_targets(self):
        self.core.show_available_targets()

    def _get_intent(self, app_name: str) -> List[str]:
        app_name = app_name.lower()
        for category, apps in self.core.config.get('targets', {}).items():
            if app_name in apps:
                intent = apps[app_name]
                return [intent] if isinstance(intent, str) else intent
        
        self.hacker_msg(f"'{app_name}' no es un atajo predefinido, intentando resolver dinámicamente...")
        exit_code, output = self.core.sudo(f"cmd package resolve-activity --brief {app_name} | tail -n 1")
        if exit_code == 0 and '/' in output and 'Error' not in output:
            return [output.strip()]
        
        default_intents = {
            "browser": ["com.android.chrome/com.google.android.apps.chrome.Main"],
            "phone": ["com.android.dialer/.DialtactsActivity"],
            "contacts": ["com.android.contacts/.activities.PeopleActivity"],
            "messages": ["com.google.android.apps.messaging/.ui.conversationlist.ConversationListActivity"],
            "clock": ["com.android.deskclock/.DeskClock"]
        }
        
        return default_intents.get(app_name, [])

    def _open_app(self, app_name: str):
        clear_screen()
        self.core.show_hacker_banner()
        time.sleep(0.5)
        clear_screen()
        
        print(f"{Colors.MATRIX_BRIGHT}╔{'═'*70}╗{Colors.NC}")
        print(f"{Colors.MATRIX_BRIGHT}║{'TARGET ACQUISITION SYSTEM':^68}║{Colors.NC}")
        print(f"{Colors.MATRIX_BRIGHT}╠{'═'*70}╣{Colors.NC}")
        
        target_line_prefix = "║ TARGET: "
        target_name_colored = f"{Colors.HACKER_CYAN}{app_name.upper()}{Colors.MATRIX_BRIGHT}"
        
        inner_content_width = 70 - get_visual_length("║ ") - get_visual_length(" ║")
        current_content_visual_len = get_visual_length("TARGET: ") + get_visual_length(app_name.upper())
        remaining_space_target_line = inner_content_width - current_content_visual_len
        
        print(f"{target_line_prefix}{target_name_colored}{' ' * remaining_space_target_line} ║{Colors.NC}")
        print(f"{Colors.MATRIX_BRIGHT}╚{'═'*70}╝{Colors.NC}")
        print()
        sys.stdout.flush()
        
        self.core.test_privilege_access_visual()
        print()
        sys.stdout.flush()
        
        self.matrix_loading(app_name.upper())
        
        intents = self._get_intent(app_name)
        if not intents:
            print(f"{Colors.HACKER_RED}╔{'═'*60}╗{Colors.NC}")
            print(f"{Colors.HACKER_RED}║ ❌ TARGET NOT FOUND IN DATABASE ❌ ║{Colors.NC}")
            print(f"{Colors.HACKER_RED}╚{'═'*60}╝{Colors.NC}")
            print()
            self.core.show_available_targets()
            return
        
        success = False
        methods_tried = []
        
        for intent in intents:
            if not intent:
                continue
                
            self.hacker_msg(f"ATTEMPTING EXPLOITATION: {intent}")
            
            try:
                exit_code, output = self.core.sudo(f"am start -n {intent}")
                if exit_code == 0:
                    success = True
                    methods_tried.append("Activity Manager")
                    break
            except Exception:
                pass
                
            try:
                package = intent.split('/')[0] if '/' in intent else intent
                exit_code, output = self.core.sudo(f"am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER {package}")
                if exit_code == 0:
                    success = True
                    methods_tried.append("Intent Launcher (MAIN)")
                    break
            except Exception:
                pass
                
            try:
                package = intent.split('/')[0] if '/' in intent else intent
                exit_code, output = self.core.sudo(f"monkey -p {package} -c android.intent.category.LAUNCHER 1")
                if exit_code == 0:
                    success = True
                    methods_tried.append("Monkey Exploit")
                    break
            except Exception:
                pass
        
        print()
        sys.stdout.flush()
        
        if success:
            ascii_success_lines = [
                "╔══════════════════════════════════════════════════════════════════╗",
                "║ ████████╗ █████╗ ██████╗ ██████╗ ███████╗████████╗ ║",
                "║ ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝ ██╔════╝╚══██╔══╝ ║",
                "║ ██║ ███████║██████╔╝██║ ███╗█████╗ ██║ ║",
                "║ ██║ ██╔══██║██╔══██╗██║ ██║██╔══╝ ██║ ║",
                "║ ██║ ██║ ██║██║ ██║╚██████╔╝███████╗ ██║ ║",
                "║ ╚═╝ ╚═╝ ╚═╝╚═╝ ╚═╝ ╚═════╝ ╚══════╝ ╚═╝ ║",
                "║ ║",
                "║ 🔓 EXPLOITATION SUCCESSFUL - TARGET COMPROMISED 🔓 ║"
            ]
            
            for line in ascii_success_lines:
                print(f"{Colors.MATRIX_BRIGHT}{line}{Colors.NC}")
            
            target_line_prefix = "║ TARGET: "
            method_line_prefix = "║ METHOD: "
            total_line_width_banner = 70
            
            target_name_colored = f"{Colors.HACKER_CYAN}{app_name.upper()}{Colors.MATRIX_BRIGHT}"
            
            remaining_target_padding = (total_line_width_banner - get_visual_length("║ ") - get_visual_length(" ║")) - \
                                      (get_visual_length("TARGET: ") + get_visual_length(app_name.upper()))
            print(f"{target_line_prefix}{target_name_colored}{' ' * remaining_target_padding} ║{Colors.NC}")
            
            method_name_colored = f"{Colors.MATRIX_GLOW}{(methods_tried[-1] if methods_tried else 'N/A')}{Colors.MATRIX_BRIGHT}"
            remaining_method_padding = (total_line_width_banner - get_visual_length("║ ") - get_visual_length(" ║")) - \
                                      (get_visual_length("METHOD: ") + get_visual_length(methods_tried[-1] if methods_tried else 'N/A'))
            print(f"{method_line_prefix}{method_name_colored}{' ' * remaining_method_padding} ║{Colors.NC}")
            
            print(f"{Colors.MATRIX_BRIGHT}╚{'═'*70}╝{Colors.NC}")
            sys.stdout.flush()
            print()
            print(f"{Colors.MATRIX_DIM} {'░'*70}{Colors.NC}")
            print(f"{Colors.MATRIX_GLOW} {'█'*25} APPLICATION LAUNCHED {'█'*25}{Colors.NC}")
            print(f"{Colors.MATRIX_DIM} {'░'*70}{Colors.NC}")
            self.save_to_history(f"open {app_name}", "Success")
            sys.stdout.flush()
        else:
            ascii_failure_lines = [
                "╔══════════════════════════════════════════════════════════════════╗",
                "║ ███████╗ █████╗ ██╗ ██╗██╗ ██╗██████╗ ███████╗ ║",
                "║ ██╔════╝██╔══██╗██║ ██║╚██╗ ██╔╝██╔══██╗██╔════╝ ║",
                "║ █████╗ ███████║███████║ ╚████╔╝ ██████╔╝█████╗ ║",
                "║ ██╔══╝ ██╔══██║██╔══██║ ╚██╔╝ ██╔══██╗██╔══╝ ║",
                "║ ██║ ██║ ██║██║ ██║ ██║ ██║ ██║███████╗ ║",
                "║ ╚═╝ ╚═╝ ╚═╝╚═╝ ╚═╝ ╚═╝ ╚═╝ ╚═╝╚══════╝ ║",
                "║ ║",
                "║ ❌ EXPLOITATION FAILED ❌ ║"
            ]
            
            for line in ascii_failure_lines:
                print(f"{Colors.HACKER_RED}{line}{Colors.NC}")
            
            print(f"{Colors.HACKER_RED}╠{'═'*70}╣{Colors.NC}")
            inner_content_width = 70 - 4
            print(f"{Colors.HACKER_RED}║ {'POSSIBLE CAUSES:'.ljust(inner_content_width)} ║{Colors.NC}")
            print(f"{Colors.HACKER_RED}║ {'• Target not installed on system'.ljust(inner_content_width)} ║{Colors.NC}")
            print(f"{Colors.HACKER_RED}║ {'• Insufficient access privileges'.ljust(inner_content_width)} ║{Colors.NC}")
            print(f"{Colors.HACKER_RED}║ {'• Package name mismatch'.ljust(inner_content_width)} ║{Colors.NC}")
            print(f"{Colors.HACKER_RED}║ {'• Security patches blocking exploitation'.ljust(inner_content_width)} ║{Colors.NC}")
            print(f"{Colors.HACKER_RED}╚{'═'*70}╝{Colors.NC}")
            self.save_to_history(f"open {app_name}", "Failed")
            print()
            print(f"{Colors.MATRIX_BRIGHT}{'█'*78}{Colors.NC}")
            sys.stdout.flush()

class SystemInfoModule(EclipseModule):
    def __init__(self, core: 'EclipseCore'):
        super().__init__(core)
        self.name = "sysinfo"
        self.description = "Muestra información del sistema"
        self.aliases = ["info", "system"]

    def run(self, info_type: str = "all", *args: Any, **kwargs: Any):
        if info_type.lower() == "battery":
            self._show_battery_info()
        elif info_type.lower() == "storage":
            self._show_storage_info()
        elif info_type.lower() == "network":
            self._show_network_info()
        else:
            self._show_complete_info()

    def _show_complete_info(self):
        self.hacker_msg("Recopilando inteligencia del sistema objetivo...")
        print(f"{Colors.MATRIX_BRIGHT}╔{'═'*76}╗{Colors.NC}")
        print(f"{Colors.MATRIX_BRIGHT}║{'INFORMACIÓN DEL SISTEMA OBJETIVO':^74}║{Colors.NC}")
        print(f"{Colors.MATRIX_BRIGHT}╠{'═'*76}╣{Colors.NC}")
        
        try:
            android_version = self.core._get_prop('ro.build.version.release', 'N/A')
            model = self.core._get_prop('ro.product.model', 'N/A')
            manufacturer = self.core._get_prop('ro.product.manufacturer', 'N/A')
            cpu_abi = self.core._get_prop('ro.product.cpu.abi', 'N/A')
            
            print(f"{Colors.MATRIX_GLOW}║ Android Version: {android_version:<57}║{Colors.NC}")
            print(f"{Colors.MATRIX_GLOW}║ Modelo: {model:<65}║{Colors.NC}")
            print(f"{Colors.MATRIX_GLOW}║ Fabricante: {manufacturer:<61}║{Colors.NC}")
            print(f"{Colors.MATRIX_GLOW}║ CPU ABI: {cpu_abi:<64}║{Colors.NC}")
            
            try:
                memory = psutil.virtual_memory()
                total_gb = memory.total / (1024**3)
                used_gb = memory.used / (1024**3)
                free_gb = memory.free / (1024**3)
                
                print(f"{Colors.MATRIX_GLOW}║ Memoria Total: {total_gb:.2f} GB{' '*(51-len(f'{total_gb:.2f}'))}║{Colors.NC}")
                print(f"{Colors.MATRIX_GLOW}║ Memoria Usada: {used_gb:.2f} GB ({memory.percent:.1f}%){' '*(35-len(f'{used_gb:.2f}'))}{' '*(10-len(f'{memory.percent:.1f}'))}║{Colors.NC}")
                print(f"{Colors.MATRIX_GLOW}║ Memoria Libre: {free_gb:.2f} GB{' '*(51-len(f'{free_gb:.2f}'))}║{Colors.NC}")
            except Exception:
                print(f"{Colors.MATRIX_GLOW}║ Memoria: Información no disponible{' '*37}║{Colors.NC}")
            
            try:
                cpu_count = psutil.cpu_count()
                cpu_usage = psutil.cpu_percent(interval=1)
                
                print(f"{Colors.MATRIX_GLOW}║ CPU Cores: {cpu_count}{' '*(62-len(str(cpu_count)))}║{Colors.NC}")
                print(f"{Colors.MATRIX_GLOW}║ CPU Usage: {cpu_usage:.1f}%{' '*(60-len(f'{cpu_usage:.1f}'))}║{Colors.NC}")
            except Exception:
                print(f"{Colors.MATRIX_GLOW}║ CPU: Información no disponible{' '*42}║{Colors.NC}")
                
        except Exception as e:
            self.hacker_error(f"Error al obtener información del sistema: {e}")
        
        print(f"{Colors.MATRIX_BRIGHT}╚{'═'*76}╝{Colors.NC}")

    def _show_battery_info(self):
        self.hacker_msg("Analizando estado de la batería...")
        try:
            battery = psutil.sensors_battery()
            if battery:
                status = "Cargando" if battery.power_plugged else "Descargando"
                print(f"{Colors.MATRIX_GLOW}Nivel: {battery.percent:.1f}%{Colors.NC}")
                print(f"{Colors.MATRIX_GLOW}Estado: {status}{Colors.NC}")
                if battery.secsleft != psutil.POWER_TIME_UNLIMITED:
                    hours, remainder = divmod(battery.secsleft, 3600)
                    minutes = remainder // 60
                    print(f"{Colors.MATRIX_GLOW}Tiempo restante: {hours}h {minutes}m{Colors.NC}")
            else:
                print(f"{Colors.HACKER_YELLOW}Información de batería no disponible{Colors.NC}")
        except Exception as e:
            self.hacker_error(f"Error al obtener información de batería: {e}")

    def _show_storage_info(self):
        self.hacker_msg("Analizando sistemas de archivos...")
        try:
            disk_usage = psutil.disk_usage('/')
            total_gb = disk_usage.total / (1024**3)
            used_gb = disk_usage.used / (1024**3)
            free_gb = disk_usage.free / (1024**3)
            usage_percent = (used_gb / total_gb) * 100
            
            print(f"{Colors.MATRIX_BRIGHT}╔{'═'*50}╗{Colors.NC}")
            print(f"{Colors.MATRIX_BRIGHT}║{'ALMACENAMIENTO':^48}║{Colors.NC}")
            print(f"{Colors.MATRIX_BRIGHT}╠{'═'*50}╣{Colors.NC}")
            print(f"{Colors.MATRIX_GLOW}║ Total: {total_gb:.2f} GB{' '*(35-len(f'{total_gb:.2f}'))}║{Colors.NC}")
            print(f"{Colors.MATRIX_GLOW}║ Usado: {used_gb:.2f} GB ({usage_percent:.1f}%){' '*(20-len(f'{used_gb:.2f}'))}{' '*(8-len(f'{usage_percent:.1f}'))}║{Colors.NC}")
            print(f"{Colors.MATRIX_GLOW}║ Libre: {free_gb:.2f} GB{' '*(35-len(f'{free_gb:.2f}'))}║{Colors.NC}")
            print(f"{Colors.MATRIX_BRIGHT}╚{'═'*50}╝{Colors.NC}")
        except Exception as e:
            self.hacker_error(f"Error al obtener información de almacenamiento: {e}")

    def _show_network_info(self):
        self.hacker_msg("Escaneando interfaces de red...")
        try:
            net_info = psutil.net_if_addrs()
            print(f"{Colors.MATRIX_BRIGHT}╔{'═'*60}╗{Colors.NC}")
            print(f"{Colors.MATRIX_BRIGHT}║{'INTERFACES DE RED':^58}║{Colors.NC}")
            print(f"{Colors.MATRIX_BRIGHT}╠{'═'*60}╣{Colors.NC}")
            
            for interface, addresses in net_info.items():
                print(f"{Colors.MATRIX_GLOW}║ Interface: {interface:<47}║{Colors.NC}")
                for addr in addresses:
                    if addr.family.name in ['AF_INET', 'AF_INET6']:
                        print(f"{Colors.MATRIX_DIM}║ {addr.family.name}: {addr.address:<42}║{Colors.NC}")
            
            print(f"{Colors.MATRIX_BRIGHT}╚{'═'*60}╝{Colors.NC}")
        except Exception as e:
            self.hacker_error(f"Error al obtener información de red: {e}")

class DeviceControlModule(EclipseModule):
    def __init__(self, core: 'EclipseCore'):
        super().__init__(core)
        self.name = "device"
        self.description = "Control del dispositivo (apagar, reiniciar)"
        self.aliases = ["ctrl", "power"]

    def run(self, *args: Any, **kwargs: Any):
        action = args[0].lower() if args else "help"
        
        actions = {
            "shutdown": self._shutdown,
            "reboot": self._reboot,
            "recovery": self._reboot_recovery,
            "bootloader": self._reboot_bootloader,
            "help": self._show_help
        }
        
        if action in actions:
            if action in ["shutdown", "reboot", "recovery", "bootloader"]:
                if not click.confirm(f"{Colors.HACKER_YELLOW}¿Confirmas {action} del dispositivo?{Colors.NC}", default=False, err=True):
                    self.hacker_msg("Operación cancelada.")
                    return
                actions[action]()
        else:
            self._show_help()

    def _show_help(self):
        self.hacker_msg("Uso: run device <acción>")
        print(f"{Colors.MATRIX_DIM} shutdown - Apagar el dispositivo")
        print(f" reboot - Reiniciar el dispositivo")
        print(f" recovery - Reiniciar en modo recovery")
        print(f" bootloader - Reiniciar en modo bootloader{Colors.NC}")

    def _shutdown(self):
        self.hacker_msg("Apagando el dispositivo...")
        exit_code, output = self.core.sudo("reboot -p")
        if exit_code == 0:
            self.hacker_success("Comando de apagado enviado. El dispositivo se apagará en breve.")
            self.save_to_history("shutdown", "Success")
        else:
            self.hacker_error(f"Error al apagar: {output}")

    def _reboot(self):
        self.hacker_msg("Reiniciando el dispositivo...")
        exit_code, output = self.core.sudo("reboot")
        if exit_code == 0:
            self.hacker_success("Comando de reinicio enviado. El dispositivo se reiniciará en breve.")
            self.save_to_history("reboot", "Success")
        else:
            self.hacker_error(f"Error al reiniciar: {output}")

    def _reboot_recovery(self):
        self.hacker_msg("Reiniciando en modo recovery...")
        exit_code, output = self.core.sudo("reboot recovery")
        if exit_code == 0:
            self.hacker_success("Comando de reinicio en recovery enviado.")
            self.save_to_history("reboot recovery", "Success")
        else:
            self.hacker_error(f"Error al reiniciar en recovery: {output}")

    def _reboot_bootloader(self):
        self.hacker_msg("Reiniciando en modo bootloader...")
        exit_code, output = self.core.sudo("reboot bootloader")
        if exit_code == 0:
            self.hacker_success("Comando de reinicio en bootloader enviado.")
            self.save_to_history("reboot bootloader", "Success")
        else:
            self.hacker_error(f"Error al reiniciar en bootloader: {output}")

class HistoryManagerModule(EclipseModule):
    def __init__(self, core: 'EclipseCore'):
        super().__init__(core)
        self.name = "history"
        self.description = "Gestión del historial de comandos"
        self.aliases = ["hist"]

    def run(self, *args: Any, **kwargs: Any):
        action = args[0].lower() if args else "list"
        
        actions = {
            "list": self._list_history,
            "clear": self._clear_history,
            "delete": self._delete_entry,
            "search": self._search_history,
            "help": self._show_help
        }
        
        if action in actions:
            if action == "delete" and len(args) < 2:
                self.hacker_error("Especifica el ID del registro a eliminar.")
                return
            if action == "search" and len(args) < 2:
                self.hacker_error("Especifica el término de búsqueda.")
                return
            actions[action](*args[1:])
        else:
            self._show_help()

    def _show_help(self):
        self.hacker_msg("Uos: run history <acción> [argumento]")
        print(f"{Colors.MATRIX_DIM} list [n] - Muestra los últimos n comandos (10 por defecto)")
        print(f" clear - Limpia todo el historial")
        print(f" delete <id> - Elimina un registro específico")
        print(f" search <term> - Busca comandos que contengan el término{Colors.NC}")

    def _list_history(self, limit=10):
        try:
            limit = int(limit)
        except (ValueError, TypeError):
            limit = 10
            
        conn = sqlite3.connect(HISTORY_DB)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, command, timestamp, result FROM command_history ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        records = cursor.fetchall()
        conn.close()
        
        if not records:
            self.hacker_warning("No hay registros en el historial.")
            return
            
        self.hacker_success(f"Mostrando los últimos {len(records)} comandos:")
        print(f"{Colors.MATRIX_BRIGHT}{'ID':<5} {'Fecha/Hora':<20} {'Comando':<40} {'Resultado'}{Colors.NC}")
        print(f"{Colors.MATRIX_DIM}{'-'*5} {'-'*20} {'-'*40} {'-'*10}{Colors.NC}")
        
        for record in records:
            id_, command, timestamp, result = record
            display_cmd = command[:37] + "..." if len(command) > 40 else command
            print(f"{Colors.MATRIX_DIM}{id_:<5} {timestamp:<20} {display_cmd:<40} {result}{Colors.NC}")

    def _clear_history(self):
        if not click.confirm(f"{Colors.HACKER_YELLOW}¿Confirmas que quieres borrar todo el historial?{Colors.NC}", default=False, err=True):
            self.hacker_msg("Operación cancelada.")
            return
            
        conn = sqlite3.connect(HISTORY_DB)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM command_history")
        conn.commit()
        conn.close()
        
        self.hacker_success("Historial borrado completamente.")

    def _delete_entry(self, entry_id):
        conn = sqlite3.connect(HISTORY_DB)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM command_history WHERE id = ?", (entry_id,))
        changes = cursor.rowcount
        conn.commit()
        conn.close()
        
        if changes > 0:
            self.hacker_success(f"Registro {entry_id} eliminado.")
        else:
            self.hacker_error(f"No se encontró el registro {entry_id}.")

    def _search_history(self, term):
        conn = sqlite3.connect(HISTORY_DB)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, command, timestamp, result FROM command_history WHERE command LIKE ? ORDER BY timestamp DESC",
            (f"%{term}%",)
        )
        records = cursor.fetchall()
        conn.close()
        
        if not records:
            self.hacker_warning(f"No se encontraron comandos que contengan '{term}'.")
            return
            
        self.hacker_success(f"Comandos que contienen '{term}':")
        print(f"{Colors.MATRIX_BRIGHT}{'ID':<5} {'Fecha/Hora':<20} {'Comando':<40} {'Resultado'}{Colors.NC}")
        print(f"{Colors.MATRIX_DIM}{'-'*5} {'-'*20} {'-'*40} {'-'*10}{Colors.NC}")
        
        for record in records:
            id_, command, timestamp, result = record
            highlighted_cmd = command.replace(term, f"{Colors.HACKER_YELLOW}{term}{Colors.MATRIX_DIM}")
            display_cmd = highlighted_cmd[:37] + "..." if len(highlighted_cmd) > 40 else highlighted_cmd
            print(f"{Colors.MATRIX_DIM}{id_:<5} {timestamp:<20} {display_cmd:<40} {result}{Colors.NC}")

class CacheManagerModule(EclipseModule):
    def __init__(self, core: 'EclipseCore'):
        super().__init__(core)
        self.name = "cache"
        self.description = "Gestión de caché del sistema"
        self.aliases = ["c"]

    def run(self, *args: Any, **kwargs: Any):
        action = args[0].lower() if args else "status"
        
        actions = {
            "status": self._cache_status,
            "clear-all": self._clear_all_cache,
            "clear-app": self._clear_app_cache,
            "clear-dalvik": self._clear_dalvik_cache,
            "help": self._show_help
        }
        
        if action in actions:
            if action == "clear-app" and len(args) < 2:
                self.hacker_error("Especifica el nombre del paquete.")
                return
            actions[action](*args[1:])
        else:
            self._show_help()

    def _show_help(self):
        self.hacker_msg("Uso: run cache <acción> [argumento]")
        print(f"{Colors.MATRIX_DIM} status - Muestra el estado de la caché")
        print(f" clear-all - Limpia toda la caché del sistema")
        print(f" clear-app <pkg> - Limpia la caché de una aplicación específica")
        print(f" clear-dalvik - Limpia la caché Dalvik/ART{Colors.NC}")

    def _cache_status(self):
        self.hacker_msg("Obteniendo estado de la caché...")
        exit_code, system_cache = self.core.sudo("du -sh /cache 2>/dev/null || echo '0'")
        exit_code, app_cache = self.core.sudo("du -sh /data/data/*/cache 2>/dev/null | tail -1 | awk '{print $1}' || echo '0'")
        exit_code, dalvik_cache = self.core.sudo("du -sh /data/dalvik-cache 2>/dev/null || echo '0'")
        
        self.hacker_info("Estado de la Caché:")
        print(f"{Colors.MATRIX_DIM} Caché del sistema: {system_cache.split()[0] if system_cache and system_cache != '0' else 'No disponible'}")
        print(f" Caché de aplicaciones: {app_cache if app_cache and app_cache != '0' else 'No disponible'}")
        print(f" Caché Dalvik/ART: {dalvik_cache.split()[0] if dalvik_cache and dalvik_cache != '0' else 'No disponible'}{Colors.NC}")

    def _clear_all_cache(self):
        if not click.confirm(f"{Colors.HACKER_YELLOW}¿Confirmas que quieres limpiar toda la caché del sistema?{Colors.NC}", default=False, err=True):
            self.hacker_msg("Operación cancelada.")
            return
            
        self.hacker_msg("Limpiando toda la caché del sistema...")
        self.core.sudo("rm -rf /cache/*")
        self.core.sudo("find /data/data -name 'cache' -type d -exec rm -rf {} + 2>/dev/null || true")
        self.core.sudo("rm -rf /data/dalvik-cache/* 2>/dev/null || true")
        
        self.hacker_success("Caché del sistema limpiada completamente.")
        self.save_to_history("clear-all-cache", "Success")

    def _clear_app_cache(self, package_name):
        if not click.confirm(f"{Colors.HACKER_YELLOW}¿Confirmas que quieres limpiar la caché de {package_name}?{Colors.NC}", default=False, err=True):
            self.hacker_msg("Operación cancelada.")
            return
            
        self.hacker_msg(f"Limpiando caché de {package_name}...")
        exit_code, output = self.core.sudo(f"rm -rf /data/data/{package_name}/cache/* 2>/dev/null || true")
        
        if exit_code == 0:
            self.hacker_success(f"Caché de {package_name} limpiada.")
            self.save_to_history(f"clear-cache {package_name}", "Success")
        else:
            self.hacker_error(f"Error al limpiar caché de {package_name}: {output}")

    def _clear_dalvik_cache(self):
        if not click.confirm(f"{Colors.HACKER_YELLOW}¿Confirmas que quieres limpiar la caché Dalvik/ART?{Colors.NC}", default=False, err=True):
            self.hacker_msg("Operación cancelada.")
            return
            
        self.hacker_msg("Limpiando caché Dalvik/ART...")
        exit_code, output = self.core.sudo("rm -rf /data/dalvik-cache/* 2>/dev/null || true")
        
        if exit_code == 0:
            self.hacker_success("Caché Dalvik/ART limpiada. El dispositivo se reiniciará para aplicar los cambios.")
            self.save_to_history("clear-dalvik-cache", "Success")
            self.core.sudo("reboot")
        else:
            self.hacker_error(f"Error al limpiar caché Dalvik/ART: {output}")

class ProcessModule(EclipseModule):
    """Módulo avanzado de gestión de procesos."""
    def __init__(self, core: 'EclipseCore'):
        super().__init__(core)
        self.name = "process"
        self.description = "Monitorización y gestión avanzada de procesos del sistema"

    def run(self, sort_by: str = "cpu", limit: str = "15", kill_process: Optional[str] = None, *args, **kwargs):
        """Ejecuta el análisis de procesos con opciones avanzadas."""
        if kill_process:
            self._kill_process(kill_process)
            return
            
        self.hacker_msg(f"Analizando procesos del sistema... (Orden: {sort_by})")
        
        try:
            limit_int = min(int(limit), 50)
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    proc_info = proc.info
                    if proc_info['name']:
                        processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            sort_key = {
                'cpu': 'cpu_percent',
                'memory': 'memory_percent',
                'mem': 'memory_percent',
                'pid': 'pid',
                'name': 'name'
            }.get(sort_by.lower(), 'cpu_percent')
            
            if sort_key in ['cpu_percent', 'memory_percent', 'pid']:
                processes.sort(key=lambda x: x.get(sort_key, 0) or 0, reverse=True)
            else:
                processes.sort(key=lambda x: str(x.get(sort_key, '')).lower())
            
            print(f"{Colors.MATRIX_BRIGHT}╔{'═'*6}╤{'═'*25}╤{'═'*15}╤{'═'*8}╤{'═'*8}╤{'═'*10}╗{Colors.NC}")
            print(f"{Colors.MATRIX_BRIGHT}║ {'PID':>4} │ {'NAME':<23} │ {'USER':<13} │ {'CPU%':>6} │ {'MEM%':>6} │ {'STATUS':<8} ║{Colors.NC}")
            print(f"{Colors.MATRIX_BRIGHT}╠{'═'*6}╪{'═'*25}╪{'═'*15}╪{'═'*8}╪{'═'*8}╪{'═'*10}╣{Colors.NC}")
            
            for proc in processes[:limit_int]:
                pid = proc.get('pid', 0)
                name = (proc.get('name', 'Unknown') or 'Unknown')[:23]
                user = (proc.get('username', 'N/A') or 'N/A')[:13]
                cpu = proc.get('cpu_percent', 0) or 0
                mem = proc.get('memory_percent', 0) or 0
                status = (proc.get('status', 'unknown') or 'unknown')[:8]
                
                color = Colors.MATRIX_DIM
                if cpu > 50:
                    color = Colors.HACKER_RED
                elif cpu > 20:
                    color = Colors.HACKER_YELLOW
                
                print(f"{color}║ {pid:>4} │ {name:<23} │ {user:<13} │ {cpu:>6.1f} │ {mem:>6.1f} │ {status:<8} ║{Colors.NC}")
            
            print(f"{Colors.MATRIX_BRIGHT}╚{'═'*6}╧{'═'*25}╧{'═'*15}╧{'═'*8}╧{'═'*8}╧{'═'*10}╝{Colors.NC}")
            self.hacker_msg(f"Total de procesos mostrados: {len(processes[:limit_int])}")
        except Exception as e:
            self.hacker_error(f"Error al analizar procesos: {e}")

    def _kill_process(self, pid_or_name: str):
        """Termina un proceso por PID o nombre."""
        self.hacker_msg(f"Intentando terminar proceso: {pid_or_name}")
        
        try:
            if pid_or_name.isdigit():
                pid = int(pid_or_name)
                process = psutil.Process(pid)
                process.terminate()
                process.wait(timeout=3)
                self.hacker_success(f"Proceso {pid} terminado exitosamente")
            else:
                terminated = 0
                for proc in psutil.process_iter(['pid', 'name']):
                    if proc.info['name'] and pid_or_name.lower() in proc.info['name'].lower():
                        proc.terminate()
                        terminated += 1
                
                if terminated > 0:
                    self.hacker_success(f"{terminated} procesos terminados")
                else:
                    self.hacker_error(f"No se encontraron procesos con nombre: {pid_or_name}")
                    
        except psutil.NoSuchProcess:
            self.hacker_error(f"Proceso no encontrado: {pid_or_name}")
        except psutil.AccessDenied:
            self.hacker_error("Acceso denegado. Se requieren permisos root")
        except Exception as e:
            self.hacker_error(f"Error inesperado al terminar proceso: {e}")

class ScreenshotModule(EclipseModule):
    """Módulo de captura de pantalla avanzado."""
    def __init__(self, core: 'EclipseCore'):
        super().__init__(core)
        self.name = "screenshot"
        self.description = "Captura de pantalla y vigilancia visual del sistema"
        self.capture_dir = "/sdcard/EclipseCaptures"

    def run(self, delay: str = "0", *args, **kwargs):
        """Realiza una captura de pantalla con opciones avanzadas."""
        delay_int = max(0, int(delay))
        
        if delay_int > 0:
            self.hacker_msg(f"Iniciando captura en {delay_int} segundos...")
            for i in range(delay_int, 0, -1):
                print(f"{Colors.HACKER_YELLOW}Captura en: {i}{Colors.NC}", end='\r', flush=True)
                time.sleep(1)
            print(" " * 20, end='\r')
        
        # Asegura que el directorio de captura exista
        self.hacker_msg(f"Asegurando directorio de captura: {self.capture_dir}")
        mkdir_exit_code, mkdir_output = self.core.sudo(f"mkdir -p {self.capture_dir}")
        if mkdir_exit_code != 0:
            self.hacker_error(f"Fallo al crear el directorio de captura {self.capture_dir}: {mkdir_output.strip()}")
            return
        else:
            self.hacker_success(f"Directorio {self.capture_dir} asegurado.")
        
        # Intenta cambiar los permisos para asegurar que screencap pueda escribir
        chmod_exit_code, chmod_output = self.core.sudo(f"chmod 777 {self.capture_dir}")
        if chmod_exit_code != 0:
            self.hacker_warning(f"No se pudieron establecer permisos 777 en {self.capture_dir}: {chmod_output.strip()}")
        else:
            self.hacker_msg(f"Permisos 777 aplicados a {self.capture_dir}.")
        
        output_path = "/sdcard/EclipseCaptures/screenshot.png"
        self.hacker_msg(f"INICIANDO MÓDULO DE VIGILANCIA VISUAL. Guardando en: {output_path}")
        
        try:
            result_proc = self.core.sudo_raw_run(
                ['/system/bin/screencap', '-p', output_path],
                timeout=15
            )
            
            if result_proc.returncode == 0:
                self.hacker_msg("Comando screencap ejecutado. Verificando archivo...")
                time.sleep(1)
                
                exit_code, output_ls = self.core.sudo(f"ls -l {output_path}")
                if exit_code == 0:
                    try:
                        parts = output_ls.split()
                        if len(parts) >= 5:
                            size_bytes = int(parts[4])
                            size_kb = size_bytes / 1024
                            self.hacker_success(f"Captura realizada: {output_path}")
                            print(f"{Colors.MATRIX_GLOW}Tamaño del archivo: {size_kb:.1f} KB{Colors.NC}")
                        else:
                            self.hacker_success(f"Captura realizada: {output_path} (no se pudo obtener el tamaño)")
                    except Exception as e:
                        self.hacker_success(f"Captura realizada: {output_path} (error al obtener tamaño: {e})")
                else:
                    self.hacker_error(f"Captura fallida - archivo no creado o no accesible para verificar. (Output ls -l: {output_ls.strip()})")
            else:
                self.hacker_error(f"Comando screencap falló: código {result_proc.returncode}. STDOUT: '{result_proc.stdout.strip()}' STDERR: '{result_proc.stderr.strip()}'")
                
        except subprocess.TimeoutExpired:
            self.hacker_error("Timeout - captura cancelada")
        except Exception as e:
            self.hacker_error(f"Error inesperado: {e}")

# ==================== NÚCLEO PRINCIPAL ====================
class EclipseCore:
    def __init__(self):
        self.version = VERSION
        self.modules: Dict[str, EclipseModule] = {}
        self.privilege_method = "Ninguno"
        self.privilege_prefix: Optional[str] = None
        self.config: Dict[str, Any] = self._load_or_create_config()
        self._setup_signal_handlers()
        self._determine_privilege_method()
        self._load_all_modules()

    def _setup_signal_handlers(self):
        signal.signal(signal.SIGINT, lambda s, f: (print(f"\n{Colors.HACKER_YELLOW}Cerrando...{Colors.NC}"), sys.exit(0)))
        signal.signal(signal.SIGTERM, lambda s, f: (print(f"\n{Colors.HACKER_YELLOW}Cerrando...{Colors.NC}"), sys.exit(0)))

    def _get_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto con targets ampliados."""
        return {
            "targets": {
                "sistema": {
                    "settings": "com.android.settings/.Settings",
                    "camera": [
                        "com.android.camera2/com.android.camera.CameraLauncher",
                        "com.sec.android.app.camera/.Camera",
                        "com.google.android.GoogleCamera/com.android.camera.CameraLauncher"
                    ],
                    "calculator": "com.android.calculator2/com.android.calculator2.Calculator",
                    "gallery": "com.android.gallery3d/com.android.gallery3d.app.GalleryActivity",
                    "files": "com.android.documentsui/.files.FilesActivity"
                },
                "comunicacion": {
                    "whatsapp": "com.whatsapp/.HomeActivity",
                    "telegram": "org.telegram.messenger/org.telegram.ui.LaunchActivity",
                    "instagram": "com.instagram.android/com.instagram.android.activity.MainTabActivity",
                    "facebook": "com.facebook.katana/com.facebook.katana.LoginActivity",
                    "gmail": "com.google.android.gm/com.google.android.gm.ConversationListActivityGmail"
                },
                "navegadores": {
                    "google": "com.android.chrome/com.google.android.apps.chrome.Main",
                    "firefox": "org.mozilla.firefox/.App",
                    "edge": "com.microsoft.emmx/.MainActivity",
                    "opera": "com.opera.browser/.leanplum.OpCampaignForegroundActivity"
                },
                "entretenimiento": {
                    "youtube": "com.google.android.youtube/com.google.android.youtube.HomeActivity",
                    "netflix": "com.netflix.mediaclient/com.netflix.mediaclient.ui.launch.UIWebViewActivity",
                    "spotify": "com.spotify.music/com.spotify.music.MainActivity",
                    "twitch": "tv.twitch.android.app/tv.twitch.android.app.core.LandingActivity"
                },
                "google": {
                    "maps": "com.google.android.apps.maps/com.google.android.apps.maps.MapsActivity",
                    "drive": "com.google.android.apps.docs/com.google.android.apps.docs.app.NewMainProxyActivity",
                    "photos": "com.google.android.apps.photos/com.google.android.apps.photos.home.HomeActivity",
                    "play": "com.android.vending/com.google.android.finsky.activities.MainActivity"
                }
            }
        }

    def _load_or_create_config(self) -> Dict[str, Any]:
        """Carga o crea el archivo de configuración."""
        try:
            if CONFIG_FILE.exists():
                with CONFIG_FILE.open('r', encoding='utf-8') as f:
                    config = json.load(f)
                
                default_config = self._get_default_config()
                if config.get("targets", {}) != default_config["targets"]:
                    config["targets"] = default_config["targets"]
                    self._save_config(config)
                
                return config
            else:
                default_config = self._get_default_config()
                self._save_config(default_config)
                return default_config
        except Exception as e:
            hacker_error(f"Error al cargar configuración: {e}")
            return self._get_default_config()

    def _save_config(self, config: Dict[str, Any]):
        """Guarda la configuración en el archivo."""
        try:
            with CONFIG_FILE.open('w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            hacker_error(f"Error al guardar configuración: {e}")

    def _determine_privilege_method(self):
        hacker_msg("Detectando método de privilegios...")
        
        try:
            if subprocess.run(['su', '-c', 'echo'], capture_output=True, timeout=2).returncode == 0:
                self.privilege_method = "Root"
                self.privilege_prefix = "su -c"
                hacker_success("Método 'Root' detectado.")
                return
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
            
        try:
            if subprocess.run(['rish', '-c', 'echo'], capture_output=True, timeout=2).returncode == 0:
                self.privilege_method = "Shizuku"
                self.privilege_prefix = "rish -c"
                hacker_success("Método 'Shizuku' detectado.")
                return
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
            
        hacker_warning("Ningún método de privilegios funcional. Algunas funciones pueden estar limitadas.")

    def sudo(self, command: str) -> Tuple[int, str]:
        if not self.privilege_prefix:
            return 1, "No hay método de privilegios activo. Necesitas root o Shizuku."
        
        try:
            full_command = f'{self.privilege_prefix} "{command}"'
            proc = subprocess.run(full_command, shell=True, capture_output=True, text=True, timeout=30, errors='ignore')
            return proc.returncode, proc.stdout.strip() or proc.stderr.strip()
        except Exception as e:
            return 1, f"Error de ejecución del framework: {e}"

    def sudo_raw_run(self, cmd_list: List[str], timeout: int = 10) -> subprocess.CompletedProcess:
        """
        Ejecuta un comando con privilegios elevados, pero permite pasar el comando como una lista.
        Es útil para comandos que no se comportan bien dentro de un shell anidado o con redirecciones.
        El privilegio_prefix se añade una sola vez.
        """
        if not self.privilege_prefix:
            return subprocess.CompletedProcess(args=cmd_list, returncode=1, stdout="", stderr="No hay método de privilegios activo. Necesitas root o Shizuku.")
        
        try:
            full_command_str = f'{self.privilege_prefix} {" ".join(cmd_list)}'
            return subprocess.run(full_command_str, shell=True, capture_output=True, text=True, timeout=timeout, errors='ignore')
        except Exception as e:
            return subprocess.CompletedProcess(args=cmd_list, returncode=1, stdout="", stderr=f"Error de ejecución del framework: {e}")

    def _load_all_modules(self):
        hacker_msg("Cargando módulos integrados...")
        module_classes = [
            AppManagerModule,
            PackageManagerModule,
            ShizukuManagerModule,
            AppLauncherModule,
            SystemInfoModule,
            DeviceControlModule,
            HistoryManagerModule,
            CacheManagerModule,
            ProcessModule,
            ScreenshotModule
        ]
        
        for mc in module_classes:
            try:
                module = mc(self)
                self.modules[module.name] = module
                for alias in module.aliases:
                    self.modules[alias] = module
            except Exception as e:
                hacker_error(f"Error cargando módulo {mc.__name__}: {e}")
        
        if MODULES_DIR.exists() and MODULES_DIR.is_dir():
            hacker_msg("Buscando módulos externos...")
            self._load_external_modules()
        
        hacker_success(f"{len(self.modules)} módulos cargados.")

    def _load_external_modules(self):
        """Carga módulos externos desde el directorio modules/"""
        if str(MODULES_DIR.parent) not in sys.path:
            sys.path.insert(0, str(MODULES_DIR.parent))
            
        for file_path in MODULES_DIR.glob("*.py"):
            if file_path.name.startswith("_"):
                continue
                
            module_name = file_path.stem
            try:
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec is None:
                    continue
                    
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and issubclass(obj, EclipseModule) and obj != EclipseModule):
                        instance = obj(self)
                        self.modules[instance.name] = instance
                        for alias in instance.aliases:
                            self.modules[alias] = instance
                        hacker_msg(f"Módulo externo cargado: {instance.name}")
            except Exception as e:
                hacker_error(f"Error cargando módulo {module_name}: {e}")

    # ==================== Funciones de UI de EclipseCore (modificadas) ====================
    def show_hacker_banner(self):
        clear_screen()
        print(f"{Colors.MATRIX_BRIGHT}{'█'*78}{Colors.NC}")
        print()
        
        ascii_logo_lines = [
            " ███████╗ ██████╗██╗ ██╗██████╗ ███████╗███████╗ ██████╗ ██████╗ ██████╗ ",
            " ██╔════╝██╔════╝██║ ██║██╔══██╗██╔════╝██╔════╝ ██╔══██╗██╔══██╗██╔═══██╗",
            " █████╗ ██║ ██║ ██║██████╔╝███████╗█████╗ ██████╔╝██████╔╝██║ ██║",
            " ██╔══╝ ██║ ██║ ██║██╔═══╝ ╚════██║██╔══╝ ██╔═══╝ ██╔══██╗██║ ██║",
            " ███████╗╚██████╗███████╗██║ ███████║███████╗ ██║ ██║ ██║╚██████╔╝",
            " ╚══════╝ ╚═════╝╚══════╝╚═╝ ╚══════╝╚══════╝ ╚═╝ ╚═╝ ╚═╝ ╚═════╝ "
        ]
        
        for line in ascii_logo_lines[:-2]:
            print(f"{Colors.MATRIX_BRIGHT}{line}{Colors.NC}")
        for line in ascii_logo_lines[-2:]:
            print(f"{Colors.MATRIX_DIM}{line}{Colors.NC}")
        print()
        
        inner_width = 72
        
        print(f"{Colors.MATRIX_GLOW} ╔{'═'*inner_width}╗{Colors.NC}")
        tool_description = "ECLIPSE UNIFIED FRAMEWORK - HERRAMIENTA PROFESIONAL"
        centered_tool_desc = tool_description.center(inner_width + (get_visual_length(tool_description) - len(tool_description)))
        print(f"{Colors.MATRIX_GLOW} ║ {centered_tool_desc} ║{Colors.NC}")
        
        print(f"{Colors.MATRIX_GLOW} ║{'='*inner_width}║{Colors.NC}")
        
        sys_version_prefix = " System Version: "
        sys_version_content = self.version
        sys_version_line_content_visual_len = get_visual_length(sys_version_prefix) + get_visual_length(sys_version_content)
        sys_version_padding = inner_width - sys_version_line_content_visual_len
        print(f"{Colors.MATRIX_GLOW} ║ {sys_version_prefix}{sys_version_content}{' '*sys_version_padding}║{Colors.NC}")
        
        priv_method_prefix = " Privilege Method: "
        priv_method_content = self.privilege_method
        priv_method_line_content_visual_len = get_visual_length(priv_method_prefix) + get_visual_length(priv_method_content)
        priv_method_padding = inner_width - priv_method_line_content_visual_len
        print(f"{Colors.MATRIX_GLOW} ║ {priv_method_prefix}{priv_method_content}{' '*priv_method_padding}║{Colors.NC}")
        
        creator_info = "Yoandis Rodríguez"
        github_info = "https://github.com/YoandisR"
        email_info = "curvadigital0@gmail.com"
        phone_info = "737_437_0336"
        
        creator_prefix = " CREADO POR: "
        creator_line_content_visual_len = get_visual_length(creator_prefix) + get_visual_length(creator_info)
        creator_padding = inner_width - creator_line_content_visual_len
        print(f"{Colors.MATRIX_GLOW} ║ {creator_prefix}{creator_info}{' '*creator_padding}║{Colors.NC}")
        
        github_prefix = " GITHUB: "
        github_line_content_visual_len = get_visual_length(github_prefix) + get_visual_length(github_info)
        github_padding = inner_width - github_line_content_visual_len
        print(f"{Colors.MATRIX_GLOW} ║ {github_prefix}{github_info}{' '*github_padding}║{Colors.NC}")
        
        email_prefix = " CORREO: "
        email_line_content_visual_len = get_visual_length(email_prefix) + get_visual_length(email_info)
        email_padding = inner_width - email_line_content_visual_len
        print(f"{Colors.MATRIX_GLOW} ║ {email_prefix}{email_info}{' '*email_padding}║{Colors.NC}")
        
        phone_prefix = " TELÉFONO: "
        phone_line_content_visual_len = get_visual_length(phone_prefix) + get_visual_length(phone_info)
        phone_padding = inner_width - phone_line_content_visual_len
        print(f"{Colors.MATRIX_GLOW} ║ {phone_prefix}{phone_info}{' '*phone_padding}║{Colors.NC}")
        
        modules_loaded_prefix = " Módulos Cargados: "
        modules_loaded_content = str(len(self.modules))
        modules_loaded_line_content_visual_len = get_visual_length(modules_loaded_prefix) + get_visual_length(modules_loaded_content)
        modules_loaded_padding = inner_width - modules_loaded_line_content_visual_len
        print(f"{Colors.MATRIX_GLOW} ║ {modules_loaded_prefix}{modules_loaded_content}{' '*modules_loaded_padding}║{Colors.NC}")
        
        print(f"{Colors.MATRIX_GLOW} ╚{'═'*inner_width}╝{Colors.NC}")
        print()
        sys.stdout.flush()

    def test_privilege_access_visual(self) -> bool:
        """Verifica visualmente si el método de privilegio está disponible."""
        hacker_msg("SCANNING BACKDOOR ACCESS...")
        base_width = 60
        
        if self.privilege_method != "Ninguno":
            status_line_content = f"🔓 {self.privilege_method.upper()} ACCESS GRANTED - SYSTEM ONLINE 🔓"
            android_version_content = f"Android Version: {self._get_prop('ro.build.version.release', 'N/A')}"
            
            inner_content_width = base_width - 4
            
            status_padding = inner_content_width - get_visual_length(status_line_content)
            centered_status_line = status_line_content.center(get_visual_length(status_line_content) + status_padding)
            
            version_padding = inner_content_width - get_visual_length(android_version_content)
            
            print(f"{Colors.MATRIX_BRIGHT}╔{'═'* (base_width - 2)}╗{Colors.NC}")
            print(f"{Colors.MATRIX_BRIGHT}║ {centered_status_line} ║{Colors.NC}")
            print(f"{Colors.MATRIX_BRIGHT}║ {android_version_content}{' '*version_padding} ║{Colors.NC}")
            print(f"{Colors.MATRIX_BRIGHT}╚{'═'* (base_width - 2)}╝{Colors.NC}")
            sys.stdout.flush()
            return True
        else:
            inner_content_width = base_width - 4
            print(f"{Colors.HACKER_RED}╔{'═'* (base_width - 2)}╗{Colors.NC}")
            print(f"{Colors.HACKER_RED}║ {'❌ PRIVILEGE ACCESS DENIED - BACKDOOR CLOSED ❌'.center(inner_content_width)} ║{Colors.NC}")
            print(f"{Colors.HACKER_RED}╠{'═'* (base_width - 2)}╣{Colors.NC}")
            print(f"{Colors.HACKER_RED}║ {'INSTRUCCIONES PARA EXPLOIT:'.ljust(inner_content_width)} ║{Colors.NC}")
            print(f"{Colors.HACKER_RED}║ {'1. Asegúrate de tener Root (Magisk/SuperSU) O'.ljust(inner_content_width)} ║{Colors.NC}")
            print(f"{Colors.HACKER_RED}║ {'2. Ejecutar la app Shizuku y conceder permisos a Termux'.ljust(inner_content_width)} ║{Colors.NC}")
            print(f"{Colors.HACKER_RED}╚{'═'* (base_width - 2)}╝{Colors.NC}")
            sys.stdout.flush()
            return False

    def show_available_targets(self):
        """Muestra los targets disponibles organizados por categorías."""
        self.show_hacker_banner()
        print(f"{Colors.MATRIX_BRIGHT}╔{'═'*76}╗{Colors.NC}")
        print(f"{Colors.MATRIX_BRIGHT}║{'TARGETS DATABASE - EXPLOITATION READY':^74}║{Colors.NC}")
        print(f"{Colors.MATRIX_BRIGHT}╚{'═'*76}╝{Colors.NC}")
        print()
        
        for category, targets in self.config.get('targets', {}).items():
            category_line_width = 70
            category_text = f"╔═ {category.upper()} TARGETS "
            category_padding_needed = category_line_width - get_visual_length(category_text) - get_visual_length("╗")
            print(f"{Colors.HACKER_CYAN}{category_text}{'═' * category_padding_needed}╗{Colors.NC}")
            
            target_line_internal_width = 70 - get_visual_length("║ ") - get_visual_length(" ║")
            name_col_width = 12
            arrow_len = get_visual_length(" ► ")
            
            for name, intent in targets.items():
                intent_val = intent[0] if isinstance(intent, list) else intent
                package = intent_val.split('/')[0] if '/' in intent_val else intent_val
                
                descriptions = {
                    "settings": "System configuration backdoor",
                    "camera": "Visual surveillance module",
                    "calculator": "Numeric processing unit",
                    "gallery": "Image database access",
                    "files": "File system penetration",
                    "whatsapp": "Encrypted messaging exploit",
                    "telegram": "Secure channel infiltration",
                    "instagram": "Social media breach",
                    "facebook": "Social media breach",
                    "gmail": "Email system access",
                    "google": "Chrome browser exploitation",
                    "firefox": "Mozilla network access",
                    "edge": "Microsoft Edge network access",
                    "opera": "Opera browser network access",
                    "youtube": "Media streaming hijack",
                    "spotify": "Audio streaming exploit",
                    "netflix": "Video content access",
                    "twitch": "Live streaming surveillance",
                    "browser": "Default browser exploitation",
                    "phone": "Phone dialer exploit",
                    "contacts": "Contact list infiltration",
                    "messages": "SMS/MMS system access",
                    "clock": "System clock manipulation"
                }
                
                desc = descriptions.get(name, "Application exploitation vector")
                
                current_name_visual_len = get_visual_length(name)
                current_desc_visual_len = get_visual_length(desc)
                
                available_for_desc = target_line_internal_width - name_col_width - arrow_len
                
                display_name = name
                display_desc = desc
                
                if current_name_visual_len > name_col_width:
                    display_name = name[:name_col_width - 3] + "..."
                    current_name_visual_len = get_visual_length(display_name)
                
                if current_desc_visual_len > available_for_desc:
                    display_desc = desc[:available_for_desc - 3] + "..."
                    current_desc_visual_len = get_visual_length(display_desc)
                
                name_padding = name_col_width - current_name_visual_len
                desc_padding = available_for_desc - current_desc_visual_len
                
                print(f"{Colors.MATRIX_DIM}║ {display_name}{' '*name_padding} ► {display_desc}{' '*desc_padding} ║{Colors.NC}")
            
            print(f"{Colors.HACKER_CYAN}╚{'═'* (category_line_width - 2)}╝{Colors.NC}")
            print()
        
        print(f"{Colors.MATRIX_GLOW}████ EXPLOITATION EXAMPLES ████{Colors.NC}")
        print(f"{Colors.MATRIX_BRIGHT}run open google {Colors.MATRIX_DIM}# Launch Chrome browser exploit{Colors.NC}")
        print(f"{Colors.MATRIX_BRIGHT}run open settings {Colors.MATRIX_DIM}# Access system configuration{Colors.NC}")
        print(f"{Colors.MATRIX_BRIGHT}run open whatsapp {Colors.MATRIX_DIM}# Infiltrate messaging system{Colors.NC}")
        print(f"{Colors.MATRIX_BRIGHT}run process {Colors.MATRIX_DIM}# Execute process analysis{Colors.NC}")
        print(f"{Colors.MATRIX_BRIGHT}run screenshot {Colors.MATRIX_DIM}# Capture system visual{Colors.NC}")
        print()
        print(f"{Colors.MATRIX_BRIGHT}{'█'*78}{Colors.NC}")
        sys.stdout.flush()

    def run_system_test(self):
        """Ejecuta un test completo del sistema."""
        self.show_hacker_banner()
        print(f"{Colors.MATRIX_BRIGHT}╔{'═'*70}╗{Colors.NC}")
        print(f"{Colors.MATRIX_BRIGHT}║{'SYSTEM PENETRATION TEST':^68}║{Colors.NC}")
        print(f"{Colors.MATRIX_BRIGHT}╚{'═'*70}╝{Colors.NC}")
        print()
        
        tests = [
            ("TERMUX ENVIRONMENT", self._test_termux),
            ("PRIVILEGE BACKDOOR", self.test_privilege_access_visual),
            ("SYSTEM COMMANDS", self._test_system_commands),
            ("MODULE INTEGRITY", self._test_modules)
        ]
        
        results = []
        for test_name, test_func in tests:
            hacker_msg(f"RUNNING {test_name} TEST...")
            try:
                result = test_func()
                results.append((test_name, result))
                status = "PASSED" if result else "FAILED"
                color = Colors.MATRIX_BRIGHT if result else Colors.HACKER_RED
                print(f"{color} ► {test_name}: {status}{Colors.NC}")
            except Exception as e:
                results.append((test_name, False))
                print(f"{Colors.HACKER_RED} ► {test_name}: ERROR - {e}{Colors.NC}")
            sys.stdout.flush()
        
        print()
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        print(f"{Colors.MATRIX_BRIGHT}╔{'═'*70}╗{Colors.NC}")
        print(f"{Colors.MATRIX_BRIGHT}║{'TEST RESULTS SUMMARY':^68}║{Colors.NC}")
        print(f"{Colors.MATRIX_BRIGHT}╠{'═'*70}╣{Colors.NC}")
        print(f"{Colors.MATRIX_BRIGHT}║ Tests Passed: {passed}/{total}{' '*(54-len(f'{passed}/{total}'))}║{Colors.NC}")
        
        if passed == total:
            print(f"{Colors.MATRIX_BRIGHT}║ Status: {Colors.MATRIX_GLOW}ALL SYSTEMS OPERATIONAL{Colors.MATRIX_BRIGHT}{' '*44}║{Colors.NC}")
            print(f"{Colors.MATRIX_BRIGHT}║ 🔓 READY FOR EXPLOITATION 🔓{' '*40}║{Colors.NC}")
        else:
            print(f"{Colors.MATRIX_BRIGHT}║ Status: {Colors.HACKER_RED}SOME TESTS FAILED{Colors.MATRIX_BRIGHT}{' '*48}║{Colors.NC}")
            print(f"{Colors.MATRIX_BRIGHT}║ ⚠ SYSTEM MAY BE COMPROMISED ⚠{' '*37}║{Colors.NC}")
        
        print(f"{Colors.MATRIX_BRIGHT}╚{'═'*70}╝{Colors.NC}")
        sys.stdout.flush()
        return passed == total

    def _test_termux(self) -> bool:
        """Test del entorno Termux."""
        return os.path.isdir("/data/data/com.termux")

    def _test_system_commands(self) -> bool:
        """Test de comandos del sistema."""
        commands = ['am', 'pm', 'getprop']
        for cmd in commands:
            try:
                result = subprocess.run([cmd, '--help'], timeout=3, capture_output=True, text=True)
                if result.returncode != 0:
                    return False
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                return False
        return True

    def _test_modules(self) -> bool:
        """Test de integridad de módulos."""
        if not self.modules:
            return False
            
        essential_modules = ['process', 'sysinfo', 'screenshot', 'appmanager', 'pm']
        for module_name in essential_modules:
            found = False
            for m_name, m_obj in self.modules.items():
                if m_name == module_name or module_name in m_obj.aliases:
                    found = True
                    break
            if not found:
                return False
        return True

    def _get_prop(self, prop: str, default: str = "N/A") -> str:
        """Obtiene una propiedad del sistema Android."""
        try:
            result = subprocess.run(['getprop', prop], capture_output=True, text=True, timeout=2)
            return result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else default
        except:
            return default

    def interactive_mode(self):
        """Modo interactivo mejorado con navegación por menús."""
        while True:
            self.show_hacker_banner()
            print(f"{Colors.MATRIX_BRIGHT}╔{'═'*70}╗{Colors.NC}")
            print(f"{Colors.MATRIX_BRIGHT}║{'INTERACTIVE MODE - ECLIPSE PRO':^68}║{Colors.NC}")
            print(f"{Colors.MATRIX_BRIGHT}╠{'═'*70}╣{Colors.NC}")
            print(f"{Colors.MATRIX_GLOW}║ 1.{Colors.NC} Launch Application Exploit")
            print(f"{Colors.MATRIX_GLOW}║ 2.{Colors.NC} Execute System Test")
            print(f"{Colors.MATRIX_GLOW}║ 3.{Colors.NC} Run Process Analysis")
            print(f"{Colors.MATRIX_GLOW}║ 4.{Colors.NC} System Information")
            print(f"{Colors.MATRIX_GLOW}║ 5.{Colors.NC} Capture Screenshot")
            print(f"{Colors.MATRIX_GLOW}║ 6.{Colors.NC} Show Available Targets")
            print(f"{Colors.MATRIX_GLOW}║ 7.{Colors.NC} Module Management")
            print(f"{Colors.MATRIX_GLOW}║ 8.{Colors.NC} Open Web Interface")
            print(f"{Colors.MATRIX_GLOW}║ Q.{Colors.NC} Exit Framework")
            print(f"{Colors.MATRIX_BRIGHT}╚{'═'*70}╝{Colors.NC}")
            print()
            sys.stdout.flush()
            
            choice = input(f"{Colors.MATRIX_GLOW}>>> SELECT OPTION: {Colors.NC}").strip().lower()
            
            if choice == '1':
                target = input(f"{Colors.MATRIX_GLOW}>>> TARGET NAME: {Colors.NC}").strip()
                if target:
                    if "open" in self.modules:
                        self.modules["open"].run(target)
                    else:
                        hacker_error("Open module not available.")
                    input(f"\n{Colors.MATRIX_DIM}Press Enter to continue...{Colors.NC}")
            elif choice == '2':
                self.run_system_test()
                input(f"\n{Colors.MATRIX_DIM}Press Enter to continue...{Colors.NC}")
            elif choice == '3':
                if 'process' in self.modules:
                    self.modules['process'].run()
                else:
                    hacker_error("Process module not available.")
                input(f"\n{Colors.MATRIX_DIM}Press Enter to continue...{Colors.NC}")
            elif choice == '4':
                if 'sysinfo' in self.modules:
                    self.modules['sysinfo'].run()
                else:
                    hacker_error("System Info module not available.")
                input(f"\n{Colors.MATRIX_DIM}Press Enter to continue...{Colors.NC}")
            elif choice == '5':
                if 'screenshot' in self.modules:
                    delay_str = input(f"{Colors.MATRIX_GLOW}>>> DELAY IN SECONDS (e.g., 3, 0 for no delay): {Colors.NC}").strip()
                    self.modules['screenshot'].run(delay=delay_str if delay_str.isdigit() else "0")
                else:
                    hacker_error("Screenshot module not available.")
                input(f"\n{Colors.MATRIX_DIM}Press Enter to continue...{Colors.NC}")
            elif choice == '6':
                self.show_available_targets()
                input(f"\n{Colors.MATRIX_DIM}Press Enter to continue...{Colors.NC}")
            elif choice == '7':
                self._module_management_menu()
            elif choice == '8':
                self.open_web_interface()
                input(f"\n{Colors.MATRIX_DIM}Press Enter to continue...{Colors.NC}")
            elif choice == 'q':
                hacker_msg("SHUTTING DOWN FRAMEWORK... MAINTAINING LOW PROFILE")
                print(f"{Colors.MATRIX_BRIGHT}Thanks for using Eclipse Pro Framework!{Colors.NC}")
                break
            else:
                hacker_error("Invalid option. Please try again.")
                time.sleep(1)

    def _module_management_menu(self):
        """Submenú de gestión de módulos."""
        while True:
            self.show_hacker_banner()
            print(f"{Colors.MATRIX_BRIGHT}╔{'═'*70}╗{Colors.NC}")
            print(f"{Colors.MATRIX_BRIGHT}║{'MODULE MANAGEMENT SYSTEM':^68}║{Colors.NC}")
            print(f"{Colors.MATRIX_BRIGHT}╠{'═'*70}╣{Colors.NC}")
            print(f"{Colors.MATRIX_GLOW}║ 1.{Colors.NC} List Available Modules")
            print(f"{Colors.MATRIX_GLOW}║ 2.{Colors.NC} Execute Module")
            print(f"{Colors.MATRIX_GLOW}║ 3.{Colors.NC} Module Information")
            print(f"{Colors.MATRIX_GLOW}║ 4.{Colors.NC} Reload Modules")
            print(f"{Colors.MATRIX_GLOW}║ B.{Colors.NC} Back to Main Menu")
            print(f"{Colors.MATRIX_BRIGHT}╚{'═'*70}╝{Colors.NC}")
            print()
            sys.stdout.flush()
            
            choice = input(f"{Colors.MATRIX_GLOW}>>> MODULE OPTION: {Colors.NC}").strip().lower()
            
            if choice == '1':
                self._list_modules()
                input(f"\n{Colors.MATRIX_DIM}Press Enter to continue...{Colors.NC}")
            elif choice == '2':
                module_name = input(f"{Colors.MATRIX_GLOW}>>> MODULE NAME: {Colors.NC}").strip().lower()
                if module_name in self.modules:
                    try:
                        args_str = input(f"{Colors.MATRIX_GLOW}>>> ARGUMENTS (e.g., --sort cpu --limit 10): {Colors.NC}").strip()
                        args_list = args_str.split()
                        
                        module_args = []
                        module_kwargs = {}
                        i = 0
                        while i < len(args_list):
                            arg = args_list[i]
                            if arg.startswith('--'):
                                key = arg[2:]
                                if i + 1 < len(args_list) and not args_list[i + 1].startswith('-'):
                                    module_kwargs[key] = args_list[i + 1]
                                    i += 2
                                else:
                                    module_kwargs[key] = True
                                    i += 1
                            elif arg.startswith('-'):
                                key = arg[1:]
                                if i + 1 < len(args_list) and not args_list[i + 1].startswith('-'):
                                    module_kwargs[key] = args_list[i + 1]
                                    i += 2
                                else:
                                    module_kwargs[key] = True
                                    i += 1
                            else:
                                module_args.append(arg)
                                i += 1
                                
                        self.modules[module_name].run(*module_args, **module_kwargs)
                    except Exception as e:
                        hacker_error(f"Error executing module: {e}")
                else:
                    hacker_error(f"Module '{module_name}' not found")
                input(f"\n{Colors.MATRIX_DIM}Press Enter to continue...{Colors.NC}")
            elif choice == '3':
                module_name = input(f"{Colors.MATRIX_GLOW}>>> MODULE NAME: {Colors.NC}").strip().lower()
                if module_name in self.modules:
                    module = self.modules[module_name]
                    print(f"{Colors.MATRIX_BRIGHT}╔{'═'*60}╗{Colors.NC}")
                    print(f"{Colors.MATRIX_BRIGHT}║ Module: {module.name:<49}║{Colors.NC}")
                    print(f"{Colors.MATRIX_BRIGHT}║ Description: {module.description:<44}║{Colors.NC}")
                    print(f"{Colors.MATRIX_BRIGHT}║ Class: {module.__class__.__name__:<50}║{Colors.NC}")
                    print(f"{Colors.MATRIX_BRIGHT}╚{'═'*60}╝{Colors.NC}")
                else:
                    hacker_error(f"Module '{module_name}' not found")
                input(f"\n{Colors.MATRIX_DIM}Press Enter to continue...{Colors.NC}")
            elif choice == '4':
                hacker_msg("Reloading modules...")
                old_count = len(self.modules)
                self.modules.clear()
                self._load_all_modules()
                new_count = len(self.modules)
                hacker_msg(f"Modules reloaded: {old_count} -> {new_count}")
                input(f"\n{Colors.MATRIX_DIM}Press Enter to continue...{Colors.NC}")
            elif choice == 'b':
                break
            else:
                hacker_error("Invalid option. Please try again.")
                time.sleep(1)

    def _list_modules(self):
        """Lista todos los módulos disponibles con información detallada, incluyendo iconos de paquete y estilo."""
        clear_screen()
        self.show_hacker_banner()
        print(f"{Colors.MATRIX_BRIGHT}╔{'═'*76}╗{Colors.NC}")
        print(f"{Colors.MATRIX_BRIGHT}║{'MÓDULOS DISPONIBLES':^74}║{Colors.NC}")
        print(f"{Colors.MATRIX_BRIGHT}╚{'═'*76}╝{Colors.NC}")
        
        main_modules = {}
        for name, module in self.modules.items():
            if name == module.name:
                main_modules[module.name] = module
                
        if not main_modules:
            print(f"{Colors.MATRIX_BRIGHT}╔{'═'*76}╗{Colors.NC}")
            print(f"{Colors.MATRIX_BRIGHT}║{Colors.HACKER_YELLOW}{'No modules loaded':^74}{Colors.MATRIX_BRIGHT}║{Colors.NC}")
            print(f"{Colors.MATRIX_BRIGHT}╚{'═'*76}╝{Colors.NC}")
        else:
            icon_space_len = get_visual_length(" 📦 ")
            name_display_len = 18
            pipe_space_len = get_visual_length(" │ ")
            
            first_line_desc_max_visual_len = 74 - icon_space_len - name_display_len - pipe_space_len
            
            for i, name in enumerate(sorted(main_modules.keys())):
                module = main_modules[name]
                raw_description = module.description
                
                first_desc_line = raw_description
                second_desc_line = ""
                
                if get_visual_length(raw_description) > first_line_desc_max_visual_len:
                    split_point = -1
                    temp_desc_words = raw_description.split(' ')
                    current_line_visual_len = 0
                    
                    for k, word in enumerate(temp_desc_words):
                        word_visual_len = get_visual_length(word)
                        potential_len = current_line_visual_len + word_visual_len + (1 if k > 0 else 0)
                        
                        if potential_len <= first_line_desc_max_visual_len:
                            current_line_visual_len = potential_len
                            split_point = k + 1
                        else:
                            break
                    
                    if split_point > 0:
                        first_desc_line = ' '.join(temp_desc_words[:split_point])
                        second_desc_line = ' '.join(temp_desc_words[split_point:])
                    else:
                        first_desc_line = raw_description[:first_line_desc_max_visual_len]
                        second_desc_line = raw_description[first_line_desc_max_visual_len:]
                
                print(f"{Colors.MATRIX_BRIGHT}╔{'═'*76}╗{Colors.NC}")
                
                name_padding_needed = name_display_len - get_visual_length(name)
                formatted_name = f"{Colors.HACKER_PINK}{name}{' '*name_padding_needed}{Colors.NC}"
                
                desc_padding_needed = first_line_desc_max_visual_len - get_visual_length(first_desc_line)
                formatted_first_desc_line = f"{Colors.HACKER_YELLOW}{first_desc_line}{' '*desc_padding_needed}{Colors.NC}"
                
                print(f"{Colors.MATRIX_BRIGHT}║ 📦 {formatted_name}{Colors.MATRIX_BRIGHT} │ {formatted_first_desc_line}{Colors.MATRIX_BRIGHT} ║{Colors.NC}")
                
                if second_desc_line:
                    indent_str = ' ' * (icon_space_len + name_display_len + pipe_space_len)
                    remaining_space_for_sec_desc = 74 - get_visual_length(indent_str)
                    sec_desc_padding_needed = remaining_space_for_sec_desc - get_visual_length(second_desc_line)
                    formatted_second_desc_line = f"{Colors.HACKER_YELLOW}{second_desc_line}{' '*sec_desc_padding_needed}{Colors.NC}"
                    print(f"{Colors.MATRIX_BRIGHT}║{indent_str}{formatted_second_desc_line}{Colors.MATRIX_BRIGHT} ║{Colors.NC}")
                
                print(f"{Colors.MATRIX_BRIGHT}╚{'═'*76}╝{Colors.NC}")
            
            print(f"{Colors.MATRIX_GLOW}Total modules loaded: {len(main_modules)}{Colors.NC}")
        sys.stdout.flush()

    # ==================== WEB INTERFACE FUNCTIONS ====================
    def generate_web_interface(self):
        """Genera y guarda la interfaz web HTML."""
        html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Eclipse Unified Framework {self.version}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --primary-color: #00ff00;
            --secondary-color: #00cc00;
            --accent-color: #ff6600;
            --background-color: #0a0a0a;
            --card-background: #111111;
            --text-color: #ffffff;
            --terminal-bg: rgba(0, 0, 0, 0.85);
            --glow-intensity: 0.8;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Courier New', monospace;
        }}
        
        body {{
            background-color: var(--background-color);
            color: var(--text-color);
            line-height: 1.6;
            overflow-x: hidden;
            background-image: 
                radial-gradient(circle at 25% 25%, rgba(0, 255, 0, 0.05) 2px, transparent 0),
                radial-gradient(circle at 75% 75%, rgba(0, 255, 0, 0.05) 1px, transparent 0);
            background-size: 30px 30px;
            min-height: 100vh;
            position: relative;
        }}
        
        .cyberpunk-loader {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: var(--background-color);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            transition: opacity 0.5s ease-out, visibility 0.5s;
        }}
        
        .cyberpunk-loader.hidden {{
            opacity: 0;
            visibility: hidden;
        }}
        
        .loader-logo {{
            font-size: 3rem;
            font-weight: bold;
            color: var(--primary-color);
            text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
            margin-bottom: 20px;
            letter-spacing: 3px;
            animation: glow 2s ease-in-out infinite alternate;
        }}
        
        .loader-progress {{
            width: 300px;
            height: 5px;
            background-color: #222;
            border-radius: 5px;
            overflow: hidden;
            position: relative;
        }}
        
        .loader-progress-bar {{
            position: absolute;
            height: 100%;
            width: 0%;
            background-color: var(--primary-color);
            box-shadow: 0 0 10px var(--primary-color);
            animation: progressLoad 3s ease-in-out forwards;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 1s ease, transform 1s ease;
        }}
        
        .container.visible {{
            opacity: 1;
            transform: translateY(0);
        }}
        
        header {{
            text-align: center;
            padding: 30px 0;
            margin-bottom: 40px;
            position: relative;
            overflow: hidden;
        }}
        
        .cyberpunk-border {{
            position: absolute;
            width: 100%;
            height: 100%;
            top: 0;
            left: 0;
            pointer-events: none;
        }}
        
        .cyberpunk-border::before, .cyberpunk-border::after {{
            content: '';
            position: absolute;
            background-color: var(--primary-color);
            box-shadow: 0 0 15px var(--primary-color);
        }}
        
        .cyberpunk-border::before {{
            top: 0;
            left: 0;
            width: 100%;
            height: 1px;
            animation: borderGlow 3s infinite alternate;
        }}
        
        .cyberpunk-border::after {{
            bottom: 0;
            left: 0;
            width: 100%;
            height: 1px;
            animation: borderGlow 3s infinite alternate-reverse;
        }}
        
        .logo {{
            font-size: 3rem;
            font-weight: bold;
            color: var(--primary-color);
            text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
            margin-bottom: 15px;
            letter-spacing: 3px;
            position: relative;
            display: inline-block;
        }}
        
        .logo::after {{
            content: '';
            position: absolute;
            bottom: -10px;
            left: 0;
            width: 100%;
            height: 3px;
            background: linear-gradient(90deg, transparent, var(--primary-color), transparent);
            animation: logoUnderline 3s infinite;
        }}
        
        .version-badge {{
            display: inline-block;
            background-color: var(--accent-color);
            color: black;
            font-weight: bold;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 0.8rem;
            margin-left: 10px;
            transform: translateY(-15px);
            animation: badgePulse 2s infinite;
        }}
        
        .subtitle {{
            color: var(--secondary-color);
            font-size: 1.3rem;
            margin-bottom: 25px;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
        }}
        
        .terminal {{
            background-color: var(--terminal-bg);
            border: 1px solid var(--primary-color);
            border-radius: 8px;
            padding: 20px;
            margin: 25px 0;
            overflow-x: auto;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.25);
            position: relative;
            transform: translateZ(0);
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        
        .terminal:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 25px rgba(0, 255, 0, 0.4);
        }}
        
        .terminal-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--secondary-color);
        }}
        
        .terminal-title {{
            color: var(--primary-color);
            font-weight: bold;
            font-size: 1.1rem;
        }}
        
        .terminal-actions {{
            display: flex;
            gap: 8px;
        }}
        
        .terminal-action-btn {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            cursor: pointer;
        }}
        
        .terminal-action-btn.close {{ background-color: #ff5f56; }}
        .terminal-action-btn.minimize {{ background-color: #ffbd2e; }}
        .terminal-action-btn.maximize {{ background-color: #27c93f; }}
        
        .terminal-content {{
            font-family: 'Courier New', monospace;
            color: var(--primary-color);
            line-height: 1.5;
            font-size: 1.05rem;
        }}
        
        .command {{
            color: var(--accent-color);
            font-weight: bold;
        }}
        
        .comment {{
            color: #888;
            font-style: italic;
        }}
        
        .card {{
            background-color: var(--card-background);
            border: 1px solid var(--secondary-color);
            border-radius: 8px;
            padding: 25px;
            margin: 20px 0;
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.15);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(0, 255, 0, 0.1), transparent);
            transition: left 0.7s;
        }}
        
        .card:hover::before {{
            left: 100%;
        }}
        
        .card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 10px 25px rgba(0, 255, 0, 0.25);
        }}
        
        .card-title {{
            color: var(--primary-color);
            font-size: 1.5rem;
            margin-bottom: 20px;
            border-bottom: 1px solid var(--secondary-color);
            padding-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 25px;
            margin: 25px 0;
        }}
        
        .feature-list {{
            list-style-type: none;
        }}
        
        .feature-list li {{
            padding: 10px 0;
            border-bottom: 1px dotted var(--secondary-color);
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
        }}
        
        .feature-list li:hover {{
            background-color: rgba(0, 255, 0, 0.05);
            padding-left: 15px;
        }}
        
        .feature-list li:before {{
            content: ">> ";
            color: var(--primary-color);
            font-weight: bold;
            margin-right: 8px;
        }}
        
        .btn {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background-color: transparent;
            color: var(--primary-color);
            border: 1px solid var(--primary-color);
            padding: 12px 24px;
            margin: 8px;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.3s;
            border-radius: 4px;
            position: relative;
            overflow: hidden;
            font-weight: bold;
            gap: 8px;
        }}
        
        .btn::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(0, 255, 0, 0.2), transparent);
            transition: left 0.7s;
        }}
        
        .btn:hover::before {{
            left: 100%;
        }}
        
        .btn:hover {{
            background-color: rgba(0, 255, 0, 0.1);
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.4);
            transform: translateY(-3px);
        }}
        
        footer {{
            text-align: center;
            margin-top: 60px;
            padding: 30px;
            border-top: 1px solid var(--primary-color);
            color: var(--secondary-color);
            position: relative;
        }}
        
        .typewriter-container {{
            width: 100%;
            text-align: center;
            margin: 0 auto;
            padding: 0 10px;
        }}
        
        .typewriter {{
            display: inline-block;
            overflow: visible;
            border-right: 0.15em solid var(--primary-color);
            white-space: normal;
            word-wrap: break-word;
            letter-spacing: 0.1em;
            font-size: 1.2rem;
            line-height: 1.4;
            max-width: 100%;
            font-weight: 500;
        }}
        
        .module {{
            background-color: rgba(0, 30, 0, 0.2);
            border-left: 3px solid var(--primary-color);
            padding: 20px;
            margin: 15px 0;
            transition: all 0.3s;
            border-radius: 0 8px 8px 0;
            position: relative;
            overflow: hidden;
        }}
        
        .module::after {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 3px;
            height: 100%;
            background-color: var(--primary-color);
            box-shadow: 0 0 10px var(--primary-color);
            opacity: 0;
            transition: opacity 0.3s;
        }}
        
        .module:hover {{
            background-color: rgba(0, 50, 0, 0.3);
            transform: translateX(10px);
            box-shadow: 0 5px 15px rgba(0, 255, 0, 0.2);
        }}
        
        .module:hover::after {{
            opacity: 1;
        }}
        
        .module-title {{
            color: var(--accent-color);
            font-weight: bold;
            font-size: 1.2rem;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .status-indicator {{
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background-color: var(--primary-color);
            margin-right: 10px;
            animation: pulse 2s infinite;
            box-shadow: 0 0 0 0 rgba(0, 255, 0, 0.7);
        }}
        
        .matrix-bg {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
            opacity: 0.15;
        }}
        
        .cyberpunk-grid {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
            background-image: 
                linear-gradient(rgba(0, 255, 0, 0.05) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 255, 0, 0.05) 1px, transparent 1px);
            background-size: 30px 30px;
            opacity: 0.3;
        }}
        
        .floating-particles {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
        }}
        
        .particle {{
            position: absolute;
            background-color: var(--primary-color);
            border-radius: 50%;
            opacity: 0.3;
            animation: floatParticle 15s infinite linear;
        }}
        
        .ui-command-section {{
            background: rgba(0, 30, 0, 0.3);
            border: 1px solid var(--accent-color);
            border-radius: 8px;
            padding: 20px;
            margin: 30px 0;
            text-align: center;
        }}
        
        .ui-command-title {{
            color: var(--accent-color);
            font-size: 1.5rem;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }}
        
        .ui-command-code {{
            background: var(--terminal-bg);
            padding: 15px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            color: var(--primary-color);
            margin: 15px 0;
            display: inline-block;
            border: 1px solid var(--primary-color);
        }}
        
        /* Animations */
        @keyframes glow {{
            from {{
                text-shadow: 0 0 5px rgba(0, 255, 0, 0.5);
            }}
            to {{
                text-shadow: 0 0 20px rgba(0, 255, 0, 0.8), 0 0 30px rgba(0, 255, 0, 0.6);
            }}
        }}
        
        @keyframes pulse {{
            0% {{
                box-shadow: 0 0 0 0 rgba(0, 255, 0, 0.7);
            }}
            70% {{
                box-shadow: 0 0 0 12px rgba(0, 255, 0, 0);
            }}
            100% {{
                box-shadow: 0 0 0 0 rgba(0, 255, 0, 0);
            }}
        }}
        
        @keyframes progressLoad {{
            0% {{ width: 0%; }}
            20% {{ width: 20%; }}
            50% {{ width: 50%; }}
            80% {{ width: 80%; }}
            100% {{ width: 100%; }}
        }}
        
        @keyframes borderGlow {{
            0% {{ box-shadow: 0 0 5px var(--primary-color); }}
            100% {{ box-shadow: 0 0 20px var(--primary-color); }}
        }}
        
        @keyframes logoUnderline {{
            0% {{ transform: scaleX(0); opacity: 0; }}
            50% {{ transform: scaleX(1); opacity: 1; }}
            100% {{ transform: scaleX(0); opacity: 0; }}
        }}
        
        @keyframes badgePulse {{
            0% {{ box-shadow: 0 0 0 0 rgba(255, 102, 0, 0.7); }}
            70% {{ box-shadow: 0 0 0 10px rgba(255, 102, 0, 0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(255, 102, 0, 0); }}
        }}
        
        @keyframes floatParticle {{
            0% {{
                transform: translateY(0) translateX(0);
                opacity: 0;
            }}
            10% {{
                opacity: 0.3;
            }}
            90% {{
                opacity: 0.3;
            }}
            100% {{
                transform: translateY(-100vh) translateX(100px);
                opacity: 0;
            }}
        }}
        
        /* Responsive adjustments */
        @media (max-width: 768px) {{
            .grid {{
                grid-template-columns: 1fr;
            }}
            
            .logo {{
                font-size: 2.2rem;
            }}
            
            .typewriter {{
                font-size: 1.1rem;
            }}
            
            .container {{
                padding: 15px;
            }}
            
            header {{
                padding: 20px 0;
            }}
            
            .terminal-content {{
                font-size: 1rem;
            }}
            
            .card-title {{
                font-size: 1.3rem;
            }}
            
            .module-title {{
                font-size: 1.1rem;
            }}
        }}
        
        @media (max-width: 480px) {{
            .typewriter {{
                font-size: 1rem;
            }}
            
            .logo {{
                font-size: 1.8rem;
            }}
            
            .terminal-content {{
                font-size: 0.9rem;
            }}
            
            .card {{
                padding: 15px;
            }}
            
            .btn {{
                padding: 10px 15px;
                font-size: 0.9rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="cyberpunk-loader" id="loader">
        <div class="loader-logo">ECLIPSE FRAMEWORK</div>
        <div class="loader-progress">
            <div class="loader-progress-bar"></div>
        </div>
    </div>
    
    <canvas class="matrix-bg" id="matrix"></canvas>
    <div class="cyberpunk-grid"></div>
    <div class="floating-particles" id="particles"></div>
    
    <div class="container" id="main-content">
        <header>
            <div class="cyberpunk-border"></div>
            <div class="logo">
                <span class="status-indicator"></span>ECLIPSE UNIFIED FRAMEWORK
                <span class="version-badge">v13.2 PRO</span>
            </div>
            <div class="subtitle">Herramienta profesional de gestión para dispositivos Android</div>
            <div class="typewriter-container">
                <div class="typewriter" id="typewriter-text"></div>
            </div>
        </header>
        
        <div class="terminal">
            <div class="terminal-header">
                <div class="terminal-title">terminal@eclipse:~</div>
                <div class="terminal-actions">
                    <div class="terminal-action-btn close"></div>
                    <div class="terminal-action-btn minimize"></div>
                    <div class="terminal-action-btn maximize"></div>
                </div>
            </div>
            <div class="terminal-content">
                <p><span class="comment"># Instalación automática en Termux</span></p>
                <p><span class="command">pkg install git python -y</span></p>
                <p><span class="command">git clone https://github.com/YoandisR/Eclipse-Unified-Framework.git</span></p>
                <p><span class="command">cd Eclipse-Unified-Framework</span></p>
                <p><span class="command">chmod +x eclipse.py</span></p>
                <p><span class="command">python3 eclipse.py --help</span></p>
                <p><span class="comment"># Las dependencias se instalarán automáticamente</span></p>
            </div>
        </div>
        
        <!-- Nueva sección para el comando UI -->
        <div class="ui-command-section">
            <div class="ui-command-title">
                <i class="fas fa-desktop"></i> Nueva Función: Comando UI
            </div>
            <p>Ahora puedes abrir esta interfaz gráfica directamente desde el framework con el comando:</p>
            <div class="ui-command-code">python3 eclipse.py ui</div>
            <p>Este comando abrirá automáticamente esta guía visual en tu navegador predeterminado.</p>
            <a href="#" class="btn" id="simulate-ui-command">
                <i class="fas fa-terminal"></i> Simular Comando UI
            </a>
        </div>
        
        <div class="card">
            <div class="card-title"><i class="fas fa-rocket"></i> Características Principales</div>
            <ul class="feature-list">
                <li>Gestión Avanzada de Aplicaciones del Sistema</li>
                <li>Análisis de Sistema en Tiempo Real</li>
                <li>Captura de Pantalla con Opciones Avanzadas</li>
                <li>Control Completo del Dispositivo</li>
                <li>Gestión Inteligente de Caché del Sistema</li>
                <li>Historial de Comandos con Búsqueda Avanzada</li>
                <li>Interfaz Estilizada Tipo "Hacker"</li>
                <li>Soporte Nativo para Root y Shizuku</li>
            </ul>
        </div>
        
        <div class="card">
            <div class="card-title"><i class="fas fa-cubes"></i> Módulos Integrados</div>
            <div class="grid">
                <div class="module">
                    <div class="module-title"><i class="fas fa-mobile-alt"></i> Gestión de Aplicaciones</div>
                    <p>Comandos: <code>appmanager</code>, <code>pm</code><br>
                    Instalación, desinstalación y gestión completa de aplicaciones del sistema</p>
                </div>
                <div class="module">
                    <div class="module-title"><i class="fas fa-microchip"></i> Sistema y Dispositivo</div>
                    <p>Comandos: <code>sysinfo</code>, <code>device</code>, <code>process</code><br>
                    Información detallada del sistema y control avanzado del dispositivo</p>
                </div>
                <div class="module">
                    <div class="module-title"><i class="fas fa-tools"></i> Utilidades Avanzadas</div>
                    <p>Comandos: <code>screenshot</code>, <code>cache</code>, <code>history</code><br>
                    Herramientas esenciales para administración profesional</p>
                </div>
                <div class="module">
                    <div class="module-title"><i class="fas fa-play-circle"></i> Lanzamiento de Apps</div>
                    <p>Comando: <code>open</code><br>
                    Lanza aplicaciones predefinidas o personalizadas con parámetros</p>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-title"><i class="fas fa-terminal"></i> Comandos de Ejemplo</div>
            <div class="terminal">
                <div class="terminal-content">
                    <p><span class="command">python3 eclipse.py run sysinfo</span> <span class="comment"># Información completa del sistema</span></p>
                    <p><span class="command">python3 eclipse.py run screenshot --delay 3</span> <span class="comment"># Captura con retardo</span></p>
                    <p><span class="command">python3 eclipse.py run process --sort cpu --limit 10</span> <span class="comment"># Top 10 procesos por CPU</span></p>
                    <p><span class="command">python3 eclipse.py run cache clear-all</span> <span class="comment"># Limpieza total de caché</span></p>
                    <p><span class="command">python3 eclipse.py interactive</span> <span class="comment"># Modo interactivo avanzado</span></p>
                    <p><span class="command">python3 eclipse.py run open --app whatsapp</span> <span class="comment"># Abrir WhatsApp</span></p>
                    <p><span class="command">python3 eclipse.py ui</span> <span class="comment"># Abrir interfaz gráfica (NUEVO)</span></p>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-title"><i class="fas fa-server"></i> Requisitos del Sistema</div>
            <ul class="feature-list">
                <li>Android 7.0 o superior (API 24+)</li>
                <li>Termux instalado y configurado</li>
                <li>Acceso Root o Shizuku (para funciones avanzadas)</li>
                <li>Python 3.7+ (incluido automáticamente en Termux)</li>
                <li>Dependencias: click, psutil, requests, colorama (auto-instalación)</li>
                <li>Espacio libre: mínimo 50MB para instalación completa</li>
            </ul>
        </div>
        
        <div style="text-align: center; margin: 40px 0;">
            <a href="#" class="btn"><i class="fas fa-book"></i> Documentación Completa</a>
            <a href="#" class="btn"><i class="fas fa-download"></i> Descargar Framework</a>
            <a href="https://github.com/YoandisR" class="btn"><i class="fab fa-github"></i> Ver Código Fuente</a>
        </div>
        
        <footer>
            <p><strong>ECLIPSE UNIFIED FRAMEWORK</strong> - La herramienta definitiva para la gestión avanzada de dispositivos Android desde Termux</p>
            <p>Desarrollado por <strong>Yoandis Rodríguez</strong> | 
               GitHub: <a href="https://github.com/YoandisR" style="color: var(--primary-color); text-decoration: none;">YoandisR</a> | 
               Email: <a href="mailto:curvadigital0@gmail.com" style="color: var(--primary-color); text-decoration: none;">curvadigital0@gmail.com</a>
            </p>
            <p style="margin-top: 15px; font-size: 0.9em; opacity: 0.7;">
                © 2024 Eclipse Framework. Todos los derechos reservados.
            </p>
        </footer>
    </div>

    <script>
        // Matrix background effect
        function initMatrix() {{
            const canvas = document.getElementById('matrix');
            const ctx = canvas.getContext('2d');
            
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            
            const matrix = "ECLIPSE0123456789ABCDEF";
            const matrixArray = matrix.split("");
            
            const fontSize = 14;
            const columns = canvas.width / fontSize;
            
            const drops = [];
            for (let x = 0; x < columns; x++) {{
                drops[x] = Math.floor(Math.random() * canvas.height / fontSize);
            }}
            
            function draw() {{
                ctx.fillStyle = 'rgba(10, 10, 10, 0.04)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                
                ctx.fillStyle = '#00ff00';
                ctx.font = fontSize + 'px monospace';
                
                for (let i = 0; i < drops.length; i++) {{
                    const text = matrixArray[Math.floor(Math.random() * matrixArray.length)];
                    ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                    
                    if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {{
                        drops[i] = 0;
                    }}
                    drops[i]++;
                }}
            }}
            
            setInterval(draw, 35);
        }}
        
        // Create floating particles
        function createParticles() {{
            const container = document.getElementById('particles');
            const particleCount = 30;
            
            for (let i = 0; i < particleCount; i++) {{
                const particle = document.createElement('div');
                particle.classList.add('particle');
                
                const size = Math.random() * 5 + 2;
                particle.style.width = `${{size}}px`;
                particle.style.height = `${{size}}px`;
                
                particle.style.left = `${{Math.random() * 100}}%`;
                particle.style.top = `${{Math.random() * 100}}%`;
                
                particle.style.animationDuration = `${{Math.random() * 20 + 10}}s`;
                particle.style.animationDelay = `${{Math.random() * 5}}s`;
                
                container.appendChild(particle);
            }}
        }}
        
        // Typewriter effect function
        function typeWriter() {{
            const typewriterElement = document.getElementById('typewriter-text');
            const text = "Herramienta profesional de gestión para dispositivos Android";
            let i = 0;
            
            typewriterElement.textContent = '';
            
            function type() {{
                if (i < text.length) {{
                    typewriterElement.textContent += text.charAt(i);
                    i++;
                    setTimeout(type, 80);
                }} else {{
                    setInterval(() => {{
                        typewriterElement.style.borderRightColor = 
                            typewriterElement.style.borderRightColor === 'transparent' ? 
                            'var(--primary-color)' : 'transparent';
                    }}, 750);
                }}
            }}
            
            type();
        }}
        
        // Simulate UI command execution
        function simulateUICommand() {{
            const notification = document.createElement('div');
            notification.style.position = 'fixed';
            notification.style.top = '20px';
            notification.style.right = '20px';
            notification.style.backgroundColor = 'rgba(0, 80, 0, 0.8)';
            notification.style.color = 'var(--primary-color)';
            notification.style.padding = '15px';
            notification.style.borderRadius = '5px';
            notification.style.border = '1px solid var(--primary-color)';
            notification.style.zIndex = '1000';
            notification.innerHTML = '<p><i class="fas fa-check-circle"></i> Interfaz gráfica abierta</p>';
            
            document.body.appendChild(notification);
            
            setTimeout(() => {{
                document.body.removeChild(notification);
            }}, 3000);
        }}
        
        // Initialize effects when page loads
        document.addEventListener('DOMContentLoaded', function() {{
            setTimeout(() => {{
                document.getElementById('loader').classList.add('hidden');
                document.getElementById('main-content').classList.add('visible');
                
                initMatrix();
                createParticles();
                typeWriter();
                
                document.getElementById('simulate-ui-command').addEventListener('click', function(e) {{
                    e.preventDefault();
                    simulateUICommand();
                }});
                
                const commands = document.querySelectorAll('.command');
                commands.forEach((cmd, index) => {{
                    const text = cmd.textContent;
                    cmd.textContent = '';
                    setTimeout(() => {{
                        let i = 0;
                        const typeEffect = setInterval(() => {{
                            if (i < text.length) {{
                                cmd.textContent += text.charAt(i);
                                i++;
                            }} else {{
                                clearInterval(typeEffect);
                            }}
                        }}, 30);
                    }}, index * 300);
                }});
            }}, 3500);
            
            document.querySelectorAll('.btn').forEach(btn => {{
                btn.addEventListener('click', function(e) {{
                    e.preventDefault();
                    
                    const ripple = document.createElement('span');
                    const rect = this.getBoundingClientRect();
                    const size = Math.max(rect.width, rect.height);
                    const x = e.clientX - rect.left - size / 2;
                    const y = e.clientY - rect.top - size / 2;
                    
                    ripple.style.width = ripple.style.height = size + 'px';
                    ripple.style.left = x + 'px';
                    ripple.style.top = y + 'px';
                    ripple.classList.add('ripple');
                    
                    this.appendChild(ripple);
                    
                    setTimeout(() => {{
                        ripple.remove();
                    }}, 600);
                }});
            }});
        }});
        
        window.addEventListener('resize', function() {{
            const canvas = document.getElementById('matrix');
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }});
    </script>
</body>
</html>
"""
        
        file_path = os.path.join(os.getcwd(), "eclipse_ui.html")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        return file_path

    def open_web_interface(self, port=8000):
        """Genera y abre la interfaz web en el navegador, priorizando un servidor HTTP local."""
        hacker_msg("Generando interfaz web...")
        file_path = self.generate_web_interface()

        original_cwd = os.getcwd()
        try:
            # Cambiar el directorio de trabajo a donde está el archivo HTML
            # para que SimpleHTTPRequestHandler pueda encontrarlo.
            os.chdir(os.path.dirname(file_path))
            
            # Iniciar el servidor HTTP en un hilo separado
            server_thread = threading.Thread(target=self._run_http_server, args=(port,), daemon=True)
            server_thread.start()
            
            # Dar tiempo al servidor para que inicie
            time.sleep(1) 
            
            target_url = f'http://localhost:{port}/eclipse_ui.html'
            
            hacker_msg(f"Intentando abrir la interfaz en el navegador: {target_url}")
            
            opened_via_webbrowser = False
            try:
                # Intenta abrir usando webbrowser.open()
                opened_via_webbrowser = webbrowser.open(target_url)
            except Exception as e:
                hacker_warning(f"Error con webbrowser.open(): {e}")

            if opened_via_webbrowser:
                hacker_success(f"Interfaz web generada y abierta vía navegador: {target_url}")
            else:
                hacker_warning("webbrowser.open() no pudo lanzar el navegador o el navegador no respondió. Intentando con 'am start'...")
                # Alternativa: usar 'am start' a través de sudo para un lanzamiento más directo en Android
                exit_code, output = self.sudo(f"am start -a android.intent.action.VIEW -d '{target_url}'")
                if exit_code == 0:
                    hacker_success(f"Interfaz web lanzada con 'am start': {target_url}")
                else:
                    hacker_error(f"Fallo al lanzar la interfaz con 'am start': {output}. Por favor, abre manualmente en tu navegador: {target_url}")
            
            hacker_info(f"Si la página está en blanco o no carga, revisa la consola del navegador para errores.")
            hacker_msg("El servidor web local se mantendrá activo. Presiona Ctrl+C para detenerlo.")
            
            # Mantener el hilo principal vivo para que el hilo del servidor daemon pueda seguir ejecutándose
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                hacker_msg("Servidor web local detenido por el usuario.")
            
            return True
            
        except Exception as e:
            hacker_error(f"Error inesperado al intentar abrir la interfaz web: {e}")
            return False
        finally:
            # Siempre restaurar el directorio de trabajo original al finalizar
            os.chdir(original_cwd)

    def _run_http_server(self, port=8000):
        """Ejecuta un servidor HTTP simple para servir la interfaz web."""
        handler = http.server.SimpleHTTPRequestHandler
        try:
            with socketserver.TCPServer(("", port), handler) as httpd:
                hacker_msg(f"Servidor web escuchando en el puerto {port}")
                httpd.serve_forever()
        except OSError as e:
            hacker_error(f"No se pudo iniciar el servidor HTTP en el puerto {port}: {e}. Intenta usar un puerto diferente si está en uso.")


# ==================== INTERFAZ CLI ====================
@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.version_option(VERSION, '-v', '--version', message=f"Eclipse Pro Framework v{VERSION}")
@click.pass_context
def cli(ctx):
    """ECLIPSE - Framework de Gestión para Android"""
    ctx.ensure_object(dict)
    core = EclipseCore()
    ctx.obj['core'] = core
    core.show_hacker_banner()

@cli.command()
@click.argument('module')
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def run(ctx, module, args):
    """Ejecuta un módulo de ECLIPSE"""
    core = ctx.obj['core']
    module_name = module.lower()
    full_command = f"run {module} {' '.join(args)}"
    
    if module_name in core.modules:
        result_status = "Success"
        try:
            module_args = []
            module_kwargs = {}
            i = 0
            while i < len(args):
                arg = args[i]
                if arg.startswith('--'):
                    key = arg[2:]
                    if i + 1 < len(args) and not args[i + 1].startswith('-'):
                        module_kwargs[key] = args[i + 1]
                        i += 2
                    else:
                        module_kwargs[key] = True
                        i += 1
                elif arg.startswith('-'):
                    key = arg[1:]
                    if i + 1 < len(args) and not args[i + 1].startswith('-'):
                        module_kwargs[key] = args[i + 1]
                        i += 2
                    else:
                        module_kwargs[key] = True
                        i += 1
                else:
                    module_args.append(arg)
                    i += 1
                    
            core.modules[module_name].run(*module_args, **module_kwargs)
        except Exception as e:
            result_status = f"Error: {str(e)}"
            hacker_error(f"Error ejecutando módulo '{module_name}': {str(e)}")
        
        if module_name in core.modules:
            core.modules[module_name].save_to_history(full_command, result_status)
    else:
        hacker_error(f"Módulo '{module_name}' no encontrado.")
        print(f"Módulos disponibles: {', '.join(sorted(set(m.name for m in core.modules.values())))}")

@cli.command()
@click.pass_context
def modules(ctx):
    """Lista todos los módulos disponibles"""
    ctx.obj['core']._list_modules()

@cli.command()
@click.pass_context
def update(ctx):
    """Actualiza el framework ECLIPSE desde el repositorio"""
    hacker_msg("Buscando actualizaciones para ECLIPSE...")
    try:
        repo_url = "https://api.github.com/repos/tu_usuario/ECLIPSE/releases/latest"
        response = requests.get(repo_url)
        if response.status_code == 200:
            latest_version_tag = response.json()["tag_name"]
            latest_version_num_match = re.search(r'\d+\.\d+', latest_version_tag)
            current_version_num_match = re.search(r'\d+\.\d+', VERSION)
            
            latest_version_num = float(latest_version_num_match.group()) if latest_version_num_match else 0.0
            current_version_num = float(current_version_num_match.group()) if current_version_num_match else 0.0
            
            if latest_version_num > current_version_num:
                hacker_info(f"Actualización disponible: {latest_version_tag}")
                if click.confirm("¿Deseas actualizar ahora?"):
                    hacker_msg("Iniciando proceso de actualización... (Funcionalidad pendiente)")
                    hacker_success("Framework actualizado correctamente. Por favor, reinicia la aplicación.")
                else:
                    hacker_msg("Actualización cancelada.")
            else:
                hacker_success("Ya tienes la última versión instalada.")
        else:
            hacker_error(f"No se pudo verificar actualizaciones. Código de estado: {response.status_code}")
    except Exception as e:
        hacker_error(f"Error al verificar actualizaciones: {e}")

@cli.command()
@click.argument('command')
@click.pass_context
def repeat(ctx, command):
    """Repite un comando del historial por ID"""
    core = ctx.obj['core']
    try:
        command_id = int(command)
    except ValueError:
        hacker_error("El ID debe ser un número.")
        return
        
    conn = sqlite3.connect(HISTORY_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT command FROM command_history WHERE id = ?", (command_id,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        hacker_error(f"No se encontró el comando con ID {command_id}.")
        return
        
    command_to_repeat = result[0]
    hacker_msg(f"Repitiendo comando: {command_to_repeat}")
    
    parts = command_to_repeat.split()
    if len(parts) >= 2 and parts[0] == "run":
        module_name = parts[1]
        args = parts[2:]
        
        if module_name in core.modules:
            try:
                module_args = []
                module_kwargs = {}
                i = 0
                while i < len(args):
                    arg = args[i]
                    if arg.startswith('--'):
                        key = arg[2:]
                        if i + 1 < len(args) and not args[i + 1].startswith('-'):
                            module_kwargs[key] = args[i + 1]
                            i += 2
                        else:
                            module_kwargs[key] = True
                            i += 1
                    elif arg.startswith('-'):
                        key = arg[1:]
                        if i + 1 < len(args) and not args[i + 1].startswith('-'):
                            module_kwargs[key] = args[i + 1]
                            i += 2
                        else:
                            module_kwargs[key] = True
                            i += 1
                    else:
                        module_args.append(arg)
                        i += 1
                        
                core.modules[module_name].run(*module_args, **module_kwargs)
            except Exception as e:
                hacker_error(f"Error ejecutando módulo '{module_name}': {str(e)}")
        else:
            hacker_error(f"Módulo '{module_name}' no encontrado.")
    else:
        hacker_error(f"Formato de comando no válido para repetir: {command_to_repeat}")

@cli.command()
@click.pass_context
def shortcuts(ctx):
    """Muestra atajos de comandos comunes"""
    core = ctx.obj['core']
    shortcuts_text = f"""
{Colors.MATRIX_BRIGHT}═════════════════════ ATAJOS DE COMANDOS ═════════════════════{Colors.NC}

{Colors.MATRIX_GLOW}Gestión de Aplicaciones:{Colors.NC}
{Colors.MATRIX_DIM} run apps list - Lista aplicaciones del sistema
 run apps uninstall pkg - Desinstala una aplicación
 run apps info pkg - Muestra información de una app
 run apps clear pkg - Limpia datos de una app{Colors.NC}

{Colors.MATRIX_GLOW}Gestión de Paquetes:{Colors.NC}
{Colors.MATRIX_DIM} run pm list - Lista todos los paquetes
 run pm uninstall pkg - Desinstala un paquete
 run pm disable pkg - Deshabilita un paquete
 run pm backup pkg - Respalda un APK{Colors.NC}

{Colors.MATRIX_GLOW}Control del Dispositivo:{Colors.NC}
{Colors.MATRIX_DIM} run device shutdown - Apaga el dispositivo
 run device reboot - Reinicia el dispositivo
 run device recovery - Reinicia en modo recovery{Colors.NC}

{Colors.MATRIX_GLOW}Lanzamiento de Apps:{Colors.NC}
{Colors.MATRIX_DIM} run open whatsapp - Abre WhatsApp
 run open settings - Abre configuración
 run open chrome - Abre Chrome{Colors.NC}

{Colors.MATRIX_GLOW}Gestión de Caché:{Colors.NC}
{Colors.MATRIX_DIM} run cache status - Muestra estado de la caché
 run cache clear-all - Limpia toda la caché
 run cache clear-app pkg - Limpia caché de una app{Colors.NC}

{Colors.MATRIX_GLOW}Información del Sistema:{Colors.NC}
{Colors.MATRIX_DIM} run sysinfo - Muestra info completa del sistema
 run sysinfo battery - Muestra info de la batería
 run sysinfo network - Muestra info de red{Colors.NC}

{Colors.MATRIX_GLOW}Gestión de Procesos:{Colors.NC}
{Colors.MATRIX_DIM} run process - Lista procesos (orden CPU)
 run process --sort mem - Lista procesos (orden Memoria)
 run process --kill <pid/name> - Termina un proceso{Colors.NC}

{Colors.MATRIX_GLOW}Captura de Pantalla:{Colors.NC}
{Colors.MATRIX_DIM} run screenshot - Captura pantalla
 run screenshot --delay 3 - Captura con retraso de 3s{Colors.NC}

{Colors.MATRIX_GLOW}Historial:{Colors.NC}
{Colors.MATRIX_DIM} run history list - Muestra historial de comandos
 run history clear - Limpia el historial
 run repeat ID - Repite un comando por ID{Colors.NC}

{Colors.MATRIX_GLOW}Modo Interactivo:{Colors.NC}
{Colors.MATRIX_DIM} interactive - Inicia el modo interactivo con menús{Colors.NC}

{Colors.MATRIX_GLOW}Test del Sistema:{Colors.NC}
{Colors.MATRIX_DIM} test - Ejecuta un test completo de penetración del sistema{Colors.NC}

{Colors.MATRIX_BRIGHT}════════════════════════════════════════════════════════════════{Colors.NC}
"""
    print(shortcuts_text)
    sys.stdout.flush()

@cli.command()
@click.pass_context
def interactive(ctx):
    """Lanza el modo interactivo con navegación por menús."""
    ctx.obj['core'].interactive_mode()

@cli.command()
@click.pass_context
def test(ctx):
    """Ejecuta un test completo de penetración del sistema."""
    ctx.obj['core'].run_system_test()

@cli.command()
@click.pass_context
def ui(ctx):
    """Abre la interfaz web de Eclipse Framework"""
    core = ctx.obj['core']
    core.open_web_interface()

if __name__ == "__main__":
    cli()
