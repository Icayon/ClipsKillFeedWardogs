import os
import json
import sys

DEFAULT_CONFIG = {
    "gamertags": "ICayon",
    "default_out_dir": os.path.join(os.path.expanduser("~"), "Downloads", "Clips_Wardogs"),
    "use_gpu": True,
    "sec_before": 7,
    "sec_after": 7,
    "multikill_window": 15,
    "group_multikills": True,
    "auto_open": True,
    "detect_audio": True,
    "filter_beta": True,
    "language": "es"
}

def get_config_path():
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    cfg_dir = os.path.join(base_dir, "config")
    try:
        os.makedirs(cfg_dir, exist_ok=True)
        return os.path.join(cfg_dir, "settings.json")
    except Exception:
        fallback_dir = os.path.join(os.path.expanduser("~"), ".clipskillfeedwardogs")
        os.makedirs(fallback_dir, exist_ok=True)
        return os.path.join(fallback_dir, "settings.json")

def load_config():
    cfg = DEFAULT_CONFIG.copy()
    p = get_config_path()
    if os.path.exists(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
                cfg.update(data)
        except Exception:
            pass
    return cfg

def save_config(cfg):
    p = get_config_path()
    try:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)
    except Exception:
        pass