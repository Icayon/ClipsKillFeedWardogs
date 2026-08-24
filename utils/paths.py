import os
import sys
import subprocess

NO_WINDOW_FLAGS = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0

def init_windows_app_id():
    """Configura el AppUserModelID para que Windows muestre el icono en la barra de tareas"""
    if sys.platform == "win32":
        try:
            import ctypes
            myappid = 'icayon.clips.killfeed.wardogs.1.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

def get_binary_path(binary_name):
    """Busca los ejecutables de ffmpeg o ffplay empaquetados o en el sistema"""
    ext = ".exe" if sys.platform == "win32" and not binary_name.endswith((".exe", ".ico", ".png")) else ""
    full_name = f"{binary_name}{ext}" if ext else binary_name
    
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
        for sub in ["", "Archivos", "_internal", "assets"]:
            candidate = os.path.join(base_dir, sub, full_name) if sub else os.path.join(base_dir, full_name)
            if os.path.exists(candidate):
                return candidate
        meipass = getattr(sys, '_MEIPASS', base_dir)
        candidate_meipass = os.path.join(meipass, full_name)
        if os.path.exists(candidate_meipass):
            return candidate_meipass
            
    base_src = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for sub in ["", "Archivos", "assets"]:
        candidate = os.path.join(base_src, sub, full_name) if sub else os.path.join(base_src, full_name)
        if os.path.exists(candidate):
            return candidate
            
    return binary_name