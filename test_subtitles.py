import os
import subprocess
import time
from faster_whisper import WhisperModel

print("[*] Probando generador de subtitulos Twitch/TikTok...")
model = WhisperModel('tiny', device='cuda', compute_type='float16')

# Generar un archivo SRT de prueba
srt_content = """1
00:00:01,000 --> 00:00:03,500
¡TOMA! ¡BUENA BAJA!

2
00:00:04,000 --> 00:00:06,800
¡DOBLE BAJA CONFIRMADA!
"""

srt_path = r"E:\Videos OBS\AutoClip_AI\test_sub.srt"
with open(srt_path, "w", encoding="utf-8") as f:
    f.write(srt_content)
    
print(f"[✓] Archivo SRT guardado en: {srt_path}")
