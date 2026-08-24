import os
import sys
import json
import time
import shutil
import zipfile
import subprocess
import urllib.request
import urllib.error
from utils.paths import get_binary_path, NO_WINDOW_FLAGS

REPO_API_URL = "https://api.github.com/repos/Icayon/ClipsKillFeedWardogs/releases"
CURRENT_VERSION = "v0.2.0"


def parse_version_tuple(v_str: str) -> tuple:
    """Convierte cadenas como 'v1.2.0', '1.2.0-beta', 'v0.2' en tupla numérica de comparación."""
    clean = v_str.strip().lstrip('vV')
    parts = []
    for part in clean.split('.'):
        digits = []
        for ch in part:
            if ch.isdigit():
                digits.append(ch)
            else:
                break
        if digits:
            parts.append(int("".join(digits)))
        else:
            parts.append(0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)


def is_newer_version(latest_tag: str, current_tag: str = CURRENT_VERSION) -> bool:
    """Devuelve True si latest_tag es mayor que current_tag."""
    return parse_version_tuple(latest_tag) > parse_version_tuple(current_tag)


def check_github_release(current_version: str = CURRENT_VERSION) -> dict:
    """
    Consulta la API pública de GitHub Releases para comprobar si existe una versión más reciente.
    Retorna un diccionario con los detalles de la actualización.
    """
    result = {
        "has_update": False,
        "latest_tag": current_version,
        "release_notes": "",
        "download_url": "",
        "published_at": "",
        "error": None
    }
    try:
        req = urllib.request.Request(
            REPO_API_URL,
            headers={
                "User-Agent": "ClipsKillFeedWardogs-App",
                "Accept": "application/vnd.github.v3+json"
            }
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            if resp.status == 200:
                raw_data = json.loads(resp.read().decode('utf-8'))
                data = raw_data[0] if isinstance(raw_data, list) and raw_data else raw_data
                
                tag_name = data.get("tag_name", "")
                body = data.get("body", "Sin notas de versión disponibles.")
                published = data.get("published_at", "")[:10]
                
                # Buscar enlace de descarga (.zip o .exe)
                download_url = ""
                assets = data.get("assets", [])
                for asset in assets:
                    name = asset.get("name", "").lower()
                    if name.endswith(".zip") or name.endswith(".exe"):
                        download_url = asset.get("browser_download_url", "")
                        break
                if not download_url:
                    download_url = data.get("html_url", "")

                result["latest_tag"] = tag_name
                result["release_notes"] = body
                result["download_url"] = download_url
                result["published_at"] = published
                result["has_update"] = is_newer_version(tag_name, current_version)
    except urllib.error.URLError as e:
        result["error"] = f"Error de conexión: {e.reason}"
    except Exception as e:
        result["error"] = str(e)

    return result


def launch_updater_script(downloaded_file: str, target_dir: str):
    """
    Crea y ejecuta un script PowerShell/Batch desvinculado que:
    1. Espera a que el proceso actual de la app finalice (vía PID).
    2. Si es ZIP, lo descomprime reemplazando los archivos en target_dir.
    3. Si es EXE, reemplaza el ejecutable en target_dir.
    4. Reinicia la aplicación.
    """
    current_pid = os.getpid()
    exe_name = "Clips KillFeed Wardogs.exe"
    target_exe = os.path.join(target_dir, exe_name)
    
    temp_dir = os.path.dirname(downloaded_file)
    script_path = os.path.join(temp_dir, "run_update.ps1")

    is_zip = downloaded_file.lower().endswith(".zip")
    
    if is_zip:
        extract_folder = os.path.join(temp_dir, "extracted_update")
        ps_script = f"""
# Esperar a que cierre el proceso principal
Wait-Process -Id {current_pid} -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Descomprimir actualización
Expand-Archive -Path "{downloaded_file}" -DestinationPath "{extract_folder}" -Force

# Copiar archivos sobre la carpeta destino
$sourcePath = "{extract_folder}"
if (Test-Path "$extract_folder\\Clips.KillFeed.Wardogs.Portable") {{
    $sourcePath = "$extract_folder\\Clips.KillFeed.Wardogs.Portable"
}} elseif (Test-Path "$extract_folder\\Clips KillFeed Wardogs") {{
    $sourcePath = "$extract_folder\\Clips KillFeed Wardogs"
}}

Copy-Item -Path "$sourcePath\\*" -Destination "{target_dir}" -Recurse -Force

# Reiniciar la aplicación
Start-Process -FilePath "{target_exe}"
"""
    else:
        ps_script = f"""
Wait-Process -Id {current_pid} -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Copy-Item -Path "{downloaded_file}" -Destination "{target_exe}" -Force
Start-Process -FilePath "{target_exe}"
"""

    with open(script_path, "w", encoding="utf-8") as f:
        f.write(ps_script)

    # Lanzar PowerShell en segundo plano independiente
    cmd = [
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File", script_path
    ]
    subprocess.Popen(cmd, creationflags=NO_WINDOW_FLAGS | subprocess.CREATE_NEW_PROCESS_GROUP)
    
    # Cerrar proceso de la app inmediatamente para permitir el reemplazo
    sys.exit(0)
