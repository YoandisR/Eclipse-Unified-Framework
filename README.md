# Eclipse Unified Framework

![Eclipse](https://img.shields.io/badge/Eclipse-v13.2_PRO-green) ![Python](https://img.shields.io/badge/Python-3.7%2B-blue) ![Android](https://img.shields.io/badge/Android-7.0%2B-brightgreen) ![Termux](https://img.shields.io/badge/Termux-Required-orange)

---

## 🌟 Descripción
**Eclipse Unified Framework** es una potente herramienta de gestión para dispositivos Android diseñada específicamente para **Termux**.
Con una interfaz estilo *hacker* y capacidades avanzadas de administración del sistema, Eclipse te permite tomar el control completo de tu dispositivo Android directamente desde la terminal.

---

## 🚀 Características Principales
- **Gestión Avanzada de Aplicaciones**: Instalación, desinstalación y manejo completo de apps del sistema
- **Monitorización en Tiempo Real**: Procesos, uso de CPU, memoria y batería  
- **Captura de Pantalla Avanzada**: Capturas con retardo y vigilancia visual del sistema
- **Control Total del Dispositivo**: Apagado, reinicio y acceso a modos de recuperación
- **Interfaz Estilo Hacker**: Visuales con efectos de terminal y colores tipo matriz
- **Soporte Shizuku**: Funcionalidades elevadas con servicio Shizuku integrado
- **Gestión de Procesos**: Monitorización y gestión avanzada de procesos del sistema
- **22 Módulos Cargados**: Herramientas especializadas para administración completa

---

## 📦 Instalación Rápida

1. Instala **Termux** desde [F-Droid](https://f-droid.org)
2. Ejecuta en Termux:

```bash
pkg update && pkg upgrade -y
pkg install git python -y
git clone https://github.com/YoandisR/Eclipse-Unified-Framework.git
cd Eclipse-Unified-Framework
python3 eclipse.py --help
```

Las dependencias se instalan automáticamente. ✅

---

## 🎯 Uso Básico

### Modo Línea de Comandos

```bash
# Información del sistema
python3 eclipse.py run sysinfo

# Gestión de aplicaciones
python3 eclipse.py run appmanager list
python3 eclipse.py run appmanager uninstall com.example.app

# Captura de pantalla con retardo
python3 eclipse.py run screenshot --delay 3

# Abrir aplicaciones y realizar capturas
python3 eclipse.py run open whatsapp
python3 eclipse.py run screenshot --delay 3

# Gestión de procesos y caché
python3 eclipse.py run process
python3 eclipse.py run cache

# Gestión del servicio Shizuku
python3 eclipse.py run shizuku
```

### Modo Interactivo

```bash
python3 eclipse.py interactive
```

### Interfaz Web

```bash
python3 eclipse.py ui
```

---

## 🔧 Módulos Disponibles

| Módulo          | Comando                | Descripción                                    |
|-----------------|------------------------|------------------------------------------------|
| App Manager     | `appmanager`           | Gestión avanzada de aplicaciones del sistema  |
| Cache Manager   | `cache`                | Gestión de caché del sistema                   |
| Device Control  | `device`               | Control del dispositivo (apagar, reiniciar)   |
| History Manager | `history`              | Gestión del historial de comandos             |
| App Launcher    | `open`                 | Lanza aplicaciones (targets)                  |
| Package Manager | `pm`                   | Gestor de paquetes avanzado                    |
| Process Manager | `process`              | Monitorización y gestión avanzada de procesos |
| Screenshot      | `screenshot`           | Captura de pantalla y vigilancia visual       |
| Shizuku Manager | `shizuku`              | Gestión del servicio Shizuku                  |
| System Info     | `sysinfo`              | Muestra información del sistema                |

---

## 📋 Requisitos del Sistema

- Android **7.0 o superior** (API 24+)
- Termux instalado desde **F-Droid**
- Python **3.7+**
- Conexión a Internet (para dependencias)
- **Servicio Shizuku** para funciones avanzadas (22 módulos disponibles)

---

## 🔐 Método de Privilegios

Eclipse utiliza **Shizuku** como método principal para obtener permisos elevados:

### Configuración de Shizuku:
1. Instala la app **Shizuku** desde Play Store o F-Droid
2. Activa las opciones de desarrollador en Android
3. Habilita la depuración USB
4. Ejecuta Shizuku y sigue las instrucciones para activarlo
5. Eclipse detectará automáticamente el servicio Shizuku

---

## 🖥️ Interfaz Web

Eclipse incluye una interfaz web moderna con:

- Información detallada del dispositivo
- Guías visuales de instalación
- Tablas y módulos interactivos
- Ejemplos de comandos
- Diseño responsive con efectos visuales

Acceso:

```bash
python3 eclipse.py ui
```

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas!

1. Haz un **fork**
2. Crea tu rama (`git checkout -b feature/NuevaFeature`)
3. Haz commit (`git commit -m 'Add NuevaFeature'`)
4. Push (`git push origin feature/NuevaFeature`)
5. Abre un **Pull Request** 🚀

---

## 📝 Licencia

Este proyecto está bajo licencia **MIT**.
Ver el archivo [LICENSE](LICENSE) para más detalles.

---

## 👨‍💻 Autor

**Yoandis Rodríguez**
- [GitHub](https://github.com/YoandisR)
- Contacto: curvadigital0@gmail.com


---

## ⚠️ Disclaimer

Este software está diseñado para la administración y gestión de tu propio dispositivo Android. Eclipse funciona únicamente en el dispositivo donde está instalado y requiere los permisos apropiados del usuario. Úsalo de manera responsable y respeta los términos de servicio de las aplicaciones instaladas en tu dispositivo.

---

⭐ Si te gusta este proyecto, ¡dale una estrella en GitHub!
