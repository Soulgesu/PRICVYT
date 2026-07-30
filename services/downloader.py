import os
import re
import math
import shutil
import glob
import yt_dlp
from typing import Dict, Any, List, Callable, Optional, Set

CANCELLED_DOWNLOADS: Set[str] = set()

# Cargar automáticamente FFmpeg embebido desde imageio_ffmpeg y asegurar ejecutable 'ffmpeg.exe'
FFMPEG_PATH = None
try:
    import imageio_ffmpeg
    bin_path = imageio_ffmpeg.get_ffmpeg_exe()
    if bin_path and os.path.exists(bin_path):
        bin_dir = os.path.dirname(bin_path)
        standard_exe = os.path.join(bin_dir, "ffmpeg.exe")
        if not os.path.exists(standard_exe):
            try:
                shutil.copyfile(bin_path, standard_exe)
            except Exception:
                pass
        
        FFMPEG_PATH = standard_exe if os.path.exists(standard_exe) else bin_path
        if bin_dir not in os.environ.get("PATH", ""):
            os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
except Exception as e:
    print(f"Info: imageio_ffmpeg no disponible: {e}")

if not FFMPEG_PATH:
    sys_ffmpeg = shutil.which('ffmpeg') or shutil.which('ffmpeg.exe')
    if sys_ffmpeg:
        FFMPEG_PATH = sys_ffmpeg

HAS_FFMPEG = bool(FFMPEG_PATH and os.path.exists(FFMPEG_PATH))

DEFAULT_NETWORK_OPTS = {
    'retries': 25,
    'fragment_retries': 25,
    'skip_unavailable_fragments': True,
    'concurrent_fragment_downloads': 4,
    'http_chunk_size': 10485760,
    'buffersize': 1048576,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'nocheckcertificate': True,
    'noplaylist': True,
}

def clean_youtube_url(url: str) -> str:
    """
    Limpia y normaliza enlaces de YouTube (incluyendo Shorts, enlaces móviles y playlists mix)
    para enfocarse en el video individual.
    """
    if not url:
        return url

    url = url.strip()
    match = re.search(r'(?:v=|\/embed\/|\/v\/|youtu\.be\/|\/shorts\/)([a-zA-Z0-9_-]{11})', url)
    if match:
        video_id = match.group(1)
        return f"https://www.youtube.com/watch?v={video_id}"
    
    return url

def cancel_download(download_id: str):
    """Marca un ID de descarga para cancelar inmediatamente."""
    if download_id:
        CANCELLED_DOWNLOADS.add(download_id)

def format_duration(seconds: float) -> str:
    if not seconds:
        return "00:00"
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"

def format_eta(seconds: Optional[float]) -> str:
    """
    Formatea los segundos de estimación de tiempo restante (ETA) en horas, minutos y segundos.
    Ejemplos: '45s restantes', '2m 15s restantes', '1h 04m 20s restantes'
    """
    if seconds is None or seconds < 0:
        return ""
    seconds = int(seconds)
    if seconds == 0:
        return "Un momento..."
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours}h {minutes:02d}m {secs:02d}s restantes"
    elif minutes > 0:
        return f"{minutes}m {secs:02d}s restantes"
    else:
        return f"{secs}s restantes"

def format_bytes(bytes_val: float) -> str:
    if not bytes_val or bytes_val <= 0:
        return "Desconocido"
    sizes = ['B', 'KB', 'MB', 'GB']
    i = int(math.floor(math.log(bytes_val, 1024)))
    p = math.pow(1024, i)
    s = round(bytes_val / p, 2)
    return f"{s} {sizes[i]}"

def search_youtube_videos(query: str, max_results: int = 15) -> List[Dict[str, Any]]:
    """
    Busca videos en YouTube en tiempo real utilizando yt-dlp con extracción plana acelerada.
    """
    if not query or not query.strip():
        return []
    
    clean_query = query.strip()
    search_target = f"ytsearch{max_results}:{clean_query}"
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': 'in_playlist',
        'skip_download': True,
        'default_search': 'ytsearch',
        **DEFAULT_NETWORK_OPTS
    }

    results = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            res = ydl.extract_info(search_target, download=False)
            entries = res.get('entries', []) if res else []
            for entry in entries:
                if not entry:
                    continue
                video_id = entry.get('id')
                if not video_id:
                    continue
                title = entry.get('title') or 'Video sin título'
                uploader = entry.get('uploader') or entry.get('channel') or 'Canal'
                duration = entry.get('duration') or 0
                view_count = entry.get('view_count') or 0
                thumbnails = entry.get('thumbnails') or []
                thumbnail = thumbnails[-1]['url'] if thumbnails else f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
                
                results.append({
                    'id': video_id,
                    'title': title,
                    'uploader': uploader,
                    'duration': duration,
                    'duration_str': format_duration(duration),
                    'view_count': view_count,
                    'view_count_str': f"{view_count:,}" if view_count else "0",
                    'thumbnail': thumbnail,
                    'url': f"https://www.youtube.com/watch?v={video_id}"
                })
    except Exception as e:
        print(f"Error en búsqueda YouTube: {e}")
    
    return results

def get_video_info(url: str) -> Dict[str, Any]:
    """
    Extrae la información básica y los formatos de máxima calidad disponibles de un video de YouTube.
    """
    clean_url = clean_youtube_url(url)
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        **DEFAULT_NETWORK_OPTS
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(clean_url, download=False)
        
        if '_type' in info and info['_type'] == 'playlist':
            info = info['entries'][0]

        video_id = info.get('id', '')
        title = info.get('title', 'Video sin título')
        uploader = info.get('uploader') or info.get('channel') or 'Canal Desconocido'
        duration = info.get('duration', 0)
        view_count = info.get('view_count', 0)
        thumbnail = info.get('thumbnail') or f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"
        
        raw_formats = info.get('formats', [])
        
        video_formats_dict = {}
        audio_options = []

        # Encontrar tamaño del mejor flujo de audio para calcular peso total combinado (video + audio)
        best_audio_size = 0
        for fmt in raw_formats:
            if fmt.get('vcodec') == 'none' and fmt.get('acodec') != 'none':
                a_size = fmt.get('filesize') or fmt.get('filesize_approx') or 0
                if a_size > best_audio_size:
                    best_audio_size = a_size

        if HAS_FFMPEG:
            audio_options.append({
                'format_id': 'best_mp3_320',
                'ext': 'mp3',
                'resolution': 'Audio MP3 (Alta Calidad 320kbps)',
                'quality_label': 'MP3 320 kbps',
                'filesize_str': f"~{format_bytes(best_audio_size)}" if best_audio_size else "Variable",
                'is_audio': True
            })
            audio_options.append({
                'format_id': 'best_mp3_192',
                'ext': 'mp3',
                'resolution': 'Audio MP3 (Estándar 192kbps)',
                'quality_label': 'MP3 192 kbps',
                'filesize_str': f"~{format_bytes(best_audio_size * 0.6)}" if best_audio_size else "Variable",
                'is_audio': True
            })
        
        audio_options.append({
            'format_id': 'best_m4a',
            'ext': 'm4a',
            'resolution': 'Audio M4A / AAC Original (Sin Pérdida)',
            'quality_label': 'M4A Directo',
            'filesize_str': f"~{format_bytes(best_audio_size)}" if best_audio_size else "Variable",
            'is_audio': True
        })

        for fmt in raw_formats:
            height = fmt.get('height')
            vcodec = fmt.get('vcodec', 'none')

            if height and vcodec != 'none':
                res_key = f"{height}p"
                fps = fmt.get('fps', '')
                fps_str = f" {int(fps)}fps" if fps and fps > 30 else ""
                label = f"{res_key}{fps_str}"
                
                v_size = fmt.get('filesize') or fmt.get('filesize_approx') or 0
                total_size = (v_size + best_audio_size) if v_size else 0
                tbr = fmt.get('tbr') or 0
                
                # Seleccionar la pista de mejor bitrate (AV1 / VP9 / H264)
                if res_key not in video_formats_dict or tbr > video_formats_dict[res_key].get('raw_tbr', 0):
                    video_formats_dict[res_key] = {
                        'format_id': res_key,
                        'ext': 'mp4',
                        'height': height,
                        'resolution': label,
                        'quality_label': label,
                        'filesize_str': f"~{format_bytes(total_size)}" if total_size else "Variable (HD)",
                        'raw_size': total_size,
                        'raw_tbr': tbr,
                        'is_audio': False
                    }

        sorted_video_formats = sorted(
            video_formats_dict.values(),
            key=lambda x: x['height'],
            reverse=True
        )

        if not sorted_video_formats:
            sorted_video_formats.append({
                'format_id': '1080p',
                'ext': 'mp4',
                'height': 1080,
                'resolution': 'Máxima Calidad HD (1080p / 4K)',
                'quality_label': 'Máxima Calidad HD',
                'filesize_str': 'Variable',
                'is_audio': False
            })

        return {
            'id': video_id,
            'title': title,
            'uploader': uploader,
            'duration_str': format_duration(duration),
            'duration': duration,
            'view_count_str': f"{view_count:,}" if view_count else "0",
            'thumbnail': thumbnail,
            'video_formats': sorted_video_formats,
            'audio_formats': audio_options,
            'url': clean_url,
            'has_ffmpeg': HAS_FFMPEG
        }

def download_media(
    url: str, 
    format_id: str, 
    is_audio: bool, 
    output_dir: str,
    download_id: Optional[str] = None,
    progress_callback: Optional[Callable[[str, dict], None]] = None
) -> str:
    """
    Descarga el video o audio especificado en la resolución seleccionada (1080p, 1440p 2K, 2160p 4K, 720p)
    utilizando FFmpeg para fusionar las pistas de mayor tasa de bits sin pérdida.
    """
    clean_url = clean_youtube_url(url)
    os.makedirs(output_dir, exist_ok=True)
    out_tmpl = os.path.join(output_dir, '%(title).50s_%(id)s.%(ext)s')

    hooks = []
    if download_id:
        CANCELLED_DOWNLOADS.discard(download_id)

    def hook(d):
        if download_id and download_id in CANCELLED_DOWNLOADS:
            raise Exception("CANCELLED_BY_USER")

        if progress_callback and d.get('status') == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded = d.get('downloaded_bytes') or 0
            percent = (downloaded / total * 100) if total > 0 else 0
            
            speed = d.get('speed') or 0
            speed_str = f"{format_bytes(speed)}/s" if speed else ""
            
            eta = d.get('eta')
            eta_str = format_eta(eta)
            
            progress_callback(download_id, {
                'status': 'downloading',
                'percent': round(min(percent, 99.0), 1),
                'downloaded_str': format_bytes(downloaded),
                'total_str': format_bytes(total) if total else "Calculando...",
                'speed_str': speed_str,
                'eta_str': eta_str
            })
        elif progress_callback and d.get('status') == 'finished':
            progress_callback(download_id, {
                'status': 'processing',
                'percent': 99.0,
                'downloaded_str': 'Finalizando HD',
                'total_str': 'Combinando pistas de máxima tasa de bits con FFmpeg',
                'speed_str': '',
                'eta_str': ''
            })

    hooks.append(hook)

    if is_audio:
        if HAS_FFMPEG and format_id in ['best_mp3_320', 'best_mp3_192']:
            quality = '320' if format_id == 'best_mp3_320' else '192'
            ydl_opts = {
                'format': 'bestaudio/best',
                'ffmpeg_location': FFMPEG_PATH,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': quality,
                }],
                'outtmpl': out_tmpl,
                'progress_hooks': hooks,
                'quiet': True,
                'no_warnings': True,
                **DEFAULT_NETWORK_OPTS
            }
        else:
            ydl_opts = {
                'format': 'bestaudio[ext=m4a]/bestaudio/best',
                'outtmpl': out_tmpl,
                'progress_hooks': hooks,
                'quiet': True,
                'no_warnings': True,
                **DEFAULT_NETWORK_OPTS
            }
            if FFMPEG_PATH:
                ydl_opts['ffmpeg_location'] = FFMPEG_PATH
    else:
        height = None
        if format_id:
            match = re.search(r'(\d+)', str(format_id))
            if match:
                height = match.group(1)

        if HAS_FFMPEG:
            if height:
                format_spec = f"bestvideo[height<={height}]+bestaudio/bestvideo+bestaudio/best"
            else:
                format_spec = "bestvideo+bestaudio/best"

            ydl_opts = {
                'format': format_spec,
                'ffmpeg_location': FFMPEG_PATH,
                'outtmpl': out_tmpl,
                'merge_output_format': 'mp4',
                'progress_hooks': hooks,
                'quiet': True,
                'no_warnings': True,
                **DEFAULT_NETWORK_OPTS
            }
        else:
            if height:
                format_spec = f"best[height<={height}]/best"
            else:
                format_spec = "best"

            ydl_opts = {
                'format': format_spec,
                'outtmpl': out_tmpl,
                'progress_hooks': hooks,
                'quiet': True,
                'no_warnings': True,
                **DEFAULT_NETWORK_OPTS
            }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=True)
            filename = ydl.prepare_filename(info)
            
            if is_audio and HAS_FFMPEG and 'mp3' in format_id:
                filename = os.path.splitext(filename)[0] + '.mp3'
            
            if not os.path.exists(filename):
                video_id = info.get('id', '')
                for f in os.listdir(output_dir):
                    if video_id in f:
                        filename = os.path.join(output_dir, f)
                        break

            if download_id and progress_callback:
                progress_callback(download_id, {
                    'status': 'completed',
                    'percent': 100.0,
                    'downloaded_str': 'Completado',
                    'total_str': '',
                    'speed_str': '',
                    'eta_str': ''
                })

            return filename

    except Exception as err:
        if "CANCELLED_BY_USER" in str(err) or (download_id and download_id in CANCELLED_DOWNLOADS):
            CANCELLED_DOWNLOADS.discard(download_id)
            for temp_file in glob.glob(os.path.join(output_dir, "*.part")) + glob.glob(os.path.join(output_dir, "*.ytdl")):
                try:
                    os.remove(temp_file)
                except Exception:
                    pass
            
            if download_id and progress_callback:
                progress_callback(download_id, {
                    'status': 'cancelled',
                    'percent': 0,
                    'downloaded_str': 'Cancelado por el usuario',
                    'total_str': '',
                    'speed_str': '',
                    'eta_str': ''
                })

            raise ValueError("Descarga cancelada por el usuario.")
        raise err
