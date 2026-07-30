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
  - PWA instalable como aplicación nativa en la pantalla de inicio.
  - Integración `share_target`: Comparte cualquier video desde la app oficial de YouTube hacia PRICVYT en un toque.
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
└── downloads/              # Carpeta de salida de descargas temporales (ignorada en git)
```

---

## 🛠️ Requisitos Previos

- **Python 3.9+**
- **FFmpeg** (Instalado en el sistema o gestionado por `imageio-ffmpeg`)
- Navegador moderno en dispositivo móvil Android (Google Chrome, Edge, Brave, etc.)

---

## 🚀 Instalación y Uso

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/PRICVYT.git
cd PRICVYT
```

### 2. Crear entorno virtual e instalar dependencias

```bash
# En Windows:
python -m venv venv
venv\Scripts\activate

# Instalar librerías requeridas:
pip install -r requirements.txt
```

### 3. Iniciar el servidor

```bash
python app.py
```

Al ejecutar la aplicación, verás en consola las direcciones de acceso:

- 🏠 **Acceso Local (esta PC):** `http://localhost:8080`
- 📱 **Acceso Red Wi-Fi (Celular Android):** `http://<IP_LOCAL>:8080`

> 💡 **Tip:** Abre la dirección IP local desde tu teléfono Android conectado a la misma red Wi-Fi para usar la interfaz táctil adaptada y añadir la app a la pantalla de inicio como PWA.

---

## 📜 Licencia

Este proyecto está distribuido bajo la licencia MIT.
