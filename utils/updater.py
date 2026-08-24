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
CURRENT_VERSION = "v1.0.1"


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
    Crea y ejecuta un script PowerShell desvinculado que:
    1. Espera a que el proceso actual (PID) se cierre por completo.
    2. Descomprime y copia los nuevos archivos a target_dir con bucle de reintentos.
    3. Reinicia la aplicación.
    """
    current_pid = os.getpid()
    exe_name = "Clips KillFeed Wardogs.exe"
    target_exe = os.path.join(target_dir, exe_name)
    
    temp_dir = os.path.dirname(downloaded_file)
    script_path = os.path.join(temp_dir, "run_update.ps1")

    is_zip = downloaded_file.lower().endswith(".zip")
    extract_folder = os.path.join(temp_dir, "extracted_update")

    ps_script = f"""$ErrorActionPreference = "Stop"
$logFile = "$env:TEMP\\clip_updater.log"
"Iniciando actualización: $(Get-Date)" | Out-File $logFile -Encoding utf-8

try {{
    # 1. Esperar a que el proceso principal cierre completamente (máximo 15s)
    $targetPid = {current_pid}
    "Esperando cierre del proceso PID: $targetPid" | Out-File $logFile -Append
    for ($i = 0; $i -lt 15; $i++) {{
        $p = Get-Process -Id $targetPid -ErrorAction SilentlyContinue
        if (-not $p) {{ break }}
        Start-Sleep -Seconds 1
    }}
    Start-Sleep -Seconds 2

    # 2. Descomprimir si es un archivo ZIP
    $src = "{downloaded_file}"
    if ("{str(is_zip).lower()}" -eq "true") {{
        "Descomprimiendo {downloaded_file}..." | Out-File $logFile -Append
        if (Test-Path "{extract_folder}") {{ Remove-Item "{extract_folder}" -Recurse -Force -ErrorAction SilentlyContinue }}
        Expand-Archive -Path "{downloaded_file}" -DestinationPath "{extract_folder}" -Force

        $src = "{extract_folder}"
        if (Test-Path "{extract_folder}\\Clips.KillFeed.Wardogs.Portable") {{
            $src = "{extract_folder}\\Clips.KillFeed.Wardogs.Portable"
        }} elseif (Test-Path "{extract_folder}\\Clips KillFeed Wardogs") {{
            $src = "{extract_folder}\\Clips KillFeed Wardogs"
        }}
    }}

    "Carpeta origen: $src" | Out-File $logFile -Append
    "Carpeta destino: {target_dir}" | Out-File $logFile -Append

    # 3. Copiar archivos a la carpeta de destino con bucle de reintentos
    $copied = $false
    for ($attempt = 1; $attempt -le 10; $attempt++) {{
        try {{
            if ("{str(is_zip).lower()}" -eq "true") {{
                Copy-Item -Path "$src\\*" -Destination "{target_dir}" -Recurse -Force -ErrorAction Stop
            }} else {{
                Copy-Item -Path "$src" -Destination "{target_exe}" -Force -ErrorAction Stop
            }}
            $copied = $true
            "Reemplazo correcto en intento $attempt" | Out-File $logFile -Append
            break
        }} catch {{
            "Intento $attempt fallido (archivo bloqueado): $_" | Out-File $logFile -Append
            Start-Sleep -Seconds 1
        }}
    }}

    # 4. Reiniciar la aplicación
    Start-Sleep -Seconds 1
    "Iniciando ejecutable: {target_exe}" | Out-File $logFile -Append
    Start-Process -FilePath "{target_exe}"
}} catch {{
    "ERROR CRITICO DE ACTUALIZACION: $_" | Out-File $logFile -Append
}}
"""

    with open(script_path, "w", encoding="utf-8") as f:
        f.write(ps_script)

    cmd = [
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File", script_path
    ]
    subprocess.Popen(cmd, creationflags=NO_WINDOW_FLAGS | subprocess.CREATE_NEW_PROCESS_GROUP)
    sys.exit(0)
