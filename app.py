import os
import time
import glob
import socket
import urllib.parse
from typing import Dict
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.gzip import GZipMiddleware
from starlette.concurrency import run_in_threadpool
from pydantic import BaseModel
import uvicorn

from services.downloader import get_video_info, download_media, cancel_download, search_youtube_videos

def clean_orphan_files():
    """Elimina automáticamente archivos temporales huérfanos con más de 30 minutos."""
    now = time.time()
    try:
        for filepath in glob.glob(os.path.join(DOWNLOADS_DIR, "*")):
            if os.path.isfile(filepath):
                if now - os.path.getmtime(filepath) > 1800:
                    try:
                        os.remove(filepath)
                    except Exception:
                        pass
    except Exception as e:
        print(f"Limpieza de archivos huérfanos: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejador de ciclo de vida moderno de FastAPI (reemplaza a @app.on_event)."""
    clean_orphan_files()
    yield

app = FastAPI(title="PRICVYT - YouTube Downloader", version="1.0.0", lifespan=lifespan)

# Habilitar compresión GZip para activos estáticos y respuestas API
app.add_middleware(GZipMiddleware, minimum_size=500)

DOWNLOAD_PROGRESS: Dict[str, dict] = {}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
DOWNLOADS_DIR = os.path.join(BASE_DIR, "downloads")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

class InfoRequest(BaseModel):
    url: str

def get_local_ip() -> str:
    """Obtiene la dirección IP local de la computadora en la red Wi-Fi / LAN."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def update_progress_callback(download_id: str, data: dict):
    DOWNLOAD_PROGRESS[download_id] = data

def remove_file(filepath: str, download_id: str = None):
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
        if download_id and download_id in DOWNLOAD_PROGRESS:
            del DOWNLOAD_PROGRESS[download_id]
    except Exception as e:
        print(f"Error borrando archivo temporal {filepath}: {e}")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/manifest.json")
async def get_manifest():
    manifest_path = os.path.join(STATIC_DIR, "manifest.json")
    if os.path.exists(manifest_path):
        return FileResponse(manifest_path, media_type="application/json")
    raise HTTPException(status_code=404, detail="Manifiesto no encontrado.")

@app.get("/sw.js")
async def get_sw():
    sw_path = os.path.join(STATIC_DIR, "sw.js")
    if os.path.exists(sw_path):
        return FileResponse(sw_path, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="Service Worker no encontrado.")

@app.get("/api/search")
async def search_videos(q: str = "", limit: int = 15):
    query = q.strip()
    if not query:
        return JSONResponse(content={"status": "success", "results": []})
    
    try:
        results = await run_in_threadpool(search_youtube_videos, query, limit)
        return JSONResponse(content={"status": "success", "results": results})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/api/info")
async def fetch_info(payload: InfoRequest):
    url = payload.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="Por favor ingresa una URL válida de YouTube.")
    
    try:
        info = await run_in_threadpool(get_video_info, url)
        return JSONResponse(content={"status": "success", "data": info})
    except Exception as e:
        error_msg = str(e)
        if "Unsupported URL" in error_msg:
            error_msg = "La URL proporcionada no es soportada o no es un enlace válido de YouTube."
        elif "Private video" in error_msg:
            error_msg = "El video es privado o ha sido eliminado."
        return JSONResponse(status_code=400, content={"status": "error", "message": error_msg})

@app.get("/api/progress/{download_id}")
async def get_progress(download_id: str):
    progress = DOWNLOAD_PROGRESS.get(download_id, {
        "status": "starting",
        "percent": 0.0,
        "downloaded_str": "0 B",
        "total_str": "Calculando...",
        "speed_str": "",
        "eta_str": ""
    })
    return JSONResponse(content=progress)

@app.post("/api/cancel/{download_id}")
async def cancel_download_route(download_id: str):
    cancel_download(download_id)
    DOWNLOAD_PROGRESS[download_id] = {
        "status": "cancelled",
        "percent": 0,
        "downloaded_str": "Cancelado",
        "total_str": "",
        "speed_str": "",
        "eta_str": ""
    }
    return JSONResponse(content={"status": "success", "message": "Descarga cancelada."})

@app.post("/api/download")
async def download_file(
    background_tasks: BackgroundTasks,
    url: str = Form(...),
    format_id: str = Form(...),
    is_audio: str = Form("false"),
    download_id: str = Form(None)
):
    try:
        is_audio_bool = str(is_audio).lower() in ['true', '1', 'on', 'yes']
        
        if download_id:
            DOWNLOAD_PROGRESS[download_id] = {
                "status": "starting",
                "percent": 0.0,
                "downloaded_str": "Conectando",
                "total_str": "Iniciando multihilo",
                "speed_str": "",
                "eta_str": ""
            }

        filepath = await run_in_threadpool(
            download_media, 
            url, 
            format_id, 
            is_audio_bool, 
            DOWNLOADS_DIR,
            download_id,
            update_progress_callback
        )
        
        if not os.path.exists(filepath):
            raise HTTPException(status_code=500, detail="No se pudo procesar la descarga del archivo.")
            
        filename = os.path.basename(filepath)
        
        background_tasks.add_task(remove_file, filepath, download_id)

        safe_filename = urllib.parse.quote(filename)

        return FileResponse(
            path=filepath,
            filename=filename,
            media_type='application/octet-stream',
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{safe_filename}"
            }
        )
    except Exception as e:
        error_msg = str(e)
        if download_id and download_id in DOWNLOAD_PROGRESS:
            DOWNLOAD_PROGRESS[download_id] = {"status": "error", "percent": 0, "message": error_msg}
        return JSONResponse(status_code=400 if "cancelada" in error_msg else 500, content={"status": "error", "message": error_msg})

if __name__ == "__main__":
    local_ip = get_local_ip()
    print("\n" + "=" * 60)
    print(" 🚀 PRICVYT - YouTube Downloader Web App (Ultra Fast Multithreaded)")
    print(f" 🏠 Acceso Local (esta PC):           http://localhost:8080")
    print(f" 📱 Acceso Red Wi-Fi (Celular/Otros): http://{local_ip}:8080")
    print("=" * 60 + "\n")
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
