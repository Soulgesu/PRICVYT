# 📱 PRICVYT - YouTube Downloader para Dispositivos Móviles (Android 13+)

<p align="center">
  <img src="static/icons/icon-192.png" width="120" alt="PRICVYT Logo" style="border-radius: 24px;">
</p>

<p align="center">
  <b>Aplicación Web y PWA de descarga directa de videos de YouTube optimizada para dispositivos móviles Android 13+ (API 33+) con interfaz Material Design 3 (Material You).</b>
</p>

---

## 🌟 Características Principales

- 📱 **Optimizada para Android > 12 (Android 13, 14, 15, 16+)**:
  - PWA instalable como aplicación nativa en la pantalla de inicio de tu celular.
  - Integración `share_target`: Comparte cualquier video desde la app oficial de YouTube hacia PRICVYT en un solo toque.
  - Soporte para áreas seguras (`safe-area-inset-top`, `safe-area-inset-bottom`) y navegación por gestos de Android.

- 🎨 **Interfaz Material Design 3 (Material You / M3)**:
  - Paleta dinámica Slate Violet Dark Mode.
  - **M3 Top App Bar**, **M3 Search Bar** con chips interactivos y **M3 Bottom Navigation Bar**.

- 🔍 **Buscador Interno de YouTube (API Backend)**:
  - Busca cualquier video o tema directamente en la app en tiempo real sin necesidad de salir.
  - Chips de filtrado rápido (*Tendencias, Música, Podcasts, Gaming, Shorts, Tutoriales*).
  - **Sin reproductor de video obligatorio**: Al pulsar en un resultado o botón de descarga, se abre un **M3 Bottom Sheet** para descargar inmediatamente.

- ⚡ **Descargas Multihilo en Máxima Calidad**:
  - Video MP4 en **4K (2160p), 2K (1440p), 1080p Full HD y 720p HD** con fusión de flujos por FFmpeg sin pérdida de calidad.
  - Audio MP3 de alta calidad (**320 kbps, 192 kbps**) o M4A original.
  - Control de descargas: barra de progreso en vivo con porcentaje, velocidad, tiempo restante (ETA) y botón de cancelación instantánea.

---

## 📁 Estructura del Proyecto

```text
PRICVYT/
├── app.py                  # Servidor principal FastAPI y endpoints REST / API Search
├── requirements.txt        # Dependencias Python
├── iniciar.bat             # Lanzador rápido para Windows (un clic)
├── .gitignore              # Archivo para ignorar temporales y descargas en Git
├── README.md               # Documentación del repositorio
├── services/
│   └── downloader.py       # Motor de búsqueda y descargas aceleradas con yt-dlp / FFmpeg
├── static/
│   ├── css/
│   │   └── style.css       # Sistema de diseño Material UI 3 para móviles
│   ├── js/
│   │   └── main.js         # Lógica frontend M3, PWA Service Worker y búsqueda
│   ├── icons/              # Iconos de la aplicación para PWA Android
│   ├── manifest.json       # Manifiesto PWA para Android 13+
│   └── sw.js               # Service Worker para almacenamiento en caché
├── templates/
│   └── index.html          # Estructura principal HTML5 con componentes M3
└── downloads/              # Carpeta de salida de descargas temporales (limpieza automática)
```

---

## 🛠️ Requisitos Previos

- **Python 3.9 o superior** (marcar la casilla *"Add Python to PATH"* durante la instalación).
- **FFmpeg** (gestionado automáticamente por `imageio-ffmpeg` o instalado en el sistema).
- Navegador web moderno (Google Chrome, Microsoft Edge, Brave, etc.).

---

## 🚀 Instalación y Puesta en Marcha

### 1. Clonar el repositorio

```bash
git clone https://github.com/Soulgesu/PRICVYT.git
cd PRICVYT
```

---

### Opción A: Inicio Rápido en Windows (Recomendado) ⚡

Simplemente haz **doble clic en el archivo `iniciar.bat`** (o ejecútalo desde la consola):

```cmd
iniciar.bat
```

> Este script creará automáticamente el entorno virtual (`venv`), instalará las dependencias si aún no están listas e iniciará el servidor.

---

### Opción B: Inicio Manual por Consola

#### En Windows (CMD o PowerShell):
```cmd
# 1. Crear el entorno virtual (solo la primera vez):
python -m venv venv

# 2. Activar el entorno virtual:
# En CMD:
venv\Scripts\activate
# O en PowerShell:
.\venv\Scripts\Activate.ps1

# 3. Instalar dependencias:
pip install -r requirements.txt

# 4. Iniciar la aplicación:
python app.py
```

#### En Linux o macOS:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

---

## 🌐 ¿Cómo Acceder a la Aplicación?

Al ejecutar `python app.py`, verás en la consola un cuadro como este:

```text
=================================================================
 🚀 PRICVYT - YouTube Downloader Web App
=================================================================
 💻 Abre en tu navegador (esta PC):     http://localhost:8080
 📱 Desde tu celular (misma red Wi-Fi): http://192.168.1.X:8080
-----------------------------------------------------------------
 ⚠️  NOTA: No intentes abrir '0.0.0.0' en tu navegador.
           Usa siempre 'http://localhost:8080'.
=================================================================
```

> [!IMPORTANT]
> ### ⚠️ ¿Por qué NO carga `http://0.0.0.0:8080`?
> Uvicorn muestra internamente el mensaje `Uvicorn running on http://0.0.0.0:8080`.
> En redes, **`0.0.0.0` NO es una dirección web accesible desde tu navegador**. Significa que el servidor está escuchando peticiones en todas las tarjetas de red de tu computadora.
> 
> - **Para usar la app en tu PC:** Abre en tu navegador 👉 **[http://localhost:8080](http://localhost:8080)** o **[http://127.0.0.1:8080](http://127.0.0.1:8080)**
> - **Para usar la app en tu celular:** Abre la dirección IP local de tu PC (por ejemplo `http://192.168.1.2:8080`) asegurándote de que tu celular esté conectado a la **misma red Wi-Fi**.

---

## 📲 Cómo Usar e Instalar en tu Celular Android (PWA)

1. Conecta tu celular a la misma red Wi-Fi que tu PC.
2. Abre Google Chrome en tu celular y entra a la IP local que te dio la consola (ej. `http://192.168.1.2:8080`).
3. Toca el menú de tres puntos de Chrome (⋮) y selecciona **"Agregar a la pantalla principal"** o **"Instalar aplicación"**.
4. ¡Listo! Ahora tendrás PRICVYT como una aplicación nativa en tu teléfono:
   - Podrás compartir videos desde la app oficial de YouTube tocando **Compartir ➔ PRICVYT**.
   - Podrás buscar canciones o videos directamente desde el buscador integrado de la app.

---

## ❓ Preguntas Frecuentes y Solución de Problemas

<details>
<summary><b>1. No me abre desde el celular (la página no responde)</b></summary>
Verifica que el <b>Firewall de Windows</b> no esté bloqueando las conexiones entrantes al puerto 8080:
- Abre la configuración de Windows ➔ Firewall y protección de red.
- Permite la comunicación a través del firewall para <b>Python</b> o para el puerto <b>8080</b> en redes privadas.
- Asegúrate de que el celular no esté usando datos móviles y esté conectado a la misma red Wi-Fi.
</details>

<details>
<summary><b>2. Error "ExecutionPolicy" al activar venv en PowerShell</b></summary>
Si PowerShell bloquea los scripts, ejecuta este comando una sola vez en PowerShell como administrador:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```
O simplemente usa `venv\Scripts\activate.bat` en la consola CMD normal, o ejecuta `iniciar.bat`.
</details>

<details>
<summary><b>3. ¿Dónde se guardan los videos descargados?</b></summary>
Cuando pulsas descargar en la web, el archivo se transfiere y se guarda directamente en la carpeta <b>Descargas</b> de tu navegador (o de tu celular). Los archivos temporales del servidor se limpian automáticamente.
</details>

---

## 📜 Licencia

Este proyecto está distribuido bajo la licencia MIT.
