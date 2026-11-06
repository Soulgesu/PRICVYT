@echo off
title PRICVYT - Servidor Local
echo ========================================================
echo       Iniciando PRICVYT (YouTube Downloader M3)
echo ========================================================
echo.

cd /d "%~dp0"

IF NOT EXIST "venv" (
    echo [!] No se encontro el entorno virtual 'venv'. Creandolo...
    python -m venv venv
    IF ERRORLEVEL 1 (
        echo [ERROR] No se pudo crear el entorno virtual. Asegurate de tener Python instalado y en el PATH.
        pause
        exit /b 1
    )
    echo [*] Instalando dependencias necesarias...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) ELSE (
    call venv\Scripts\activate.bat
)

echo [*] Iniciando servidor FastAPI / Uvicorn...
python app.py

if ERRORLEVEL 1 (
    echo.
    echo [ERROR] El servidor se detuvo con errores.
    pause
)
