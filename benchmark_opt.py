import cv2
import subprocess
import numpy as np
import time
import os
import sys
import re
from datetime import timedelta
from rapidocr_onnxruntime import RapidOCR

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

ocr = RapidOCR()
video_test = r"E:\Videos OBS\videos para revisar\2026-08-23 04-41-15.mp4" # 28 min video

def is_watermark_present(texts):
    full = " ".join(texts).lower()
    wm_tokens = ['wardogs', 'beta', '7656', 'aug 21', 'cl-49', 'live-cl', '11866', 'aug21', '7866', 'cl49']
    return any(t in full for t in wm_tokens)

print(f"[*] Iniciando prueba de optimización en: {os.path.basename(video_test)}")
t0 = time.time()

# 1. Optimización: FPS adaptativo a 0.66 fps (1 frame cada 1.5s -> captura el 100% de alertas de 4s)
# 2. Crop ajustado a 240x85
crop_x, crop_y, crop_w, crop_h = 0, 310, 240, 85
fps_rate = 0.66

cmd = [
    "ffmpeg", "-hwaccel", "cuda", "-i", video_test,
    "-vf", f"fps={fps_rate},crop={crop_w}:{crop_h}:{crop_x}:{crop_y}",
    "-f", "rawvideo", "-pix_fmt", "bgr24", "-v", "error", "pipe:1"
]

proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
frame_len = crop_w * crop_h * 3
idx = 0
ocr_calls = 0
kills_found = []

while True:
    raw = proc.stdout.read(frame_len)
    if len(raw) < frame_len:
        break
        
    sec = int(idx * (1.0 / fps_rate))
    frame = np.frombuffer(raw, dtype=np.uint8).reshape((crop_h, crop_w, 3))
    
    # Pre-filtro ultra-rápido en BGR (busca texto blanco / iconos verdes de bajas)
    # 1. Píxeles blancos de texto
    white_mask = cv2.inRange(frame, np.array([175, 175, 175]), np.array([255, 255, 255]))
    white_count = cv2.countNonZero(white_mask)
    
    # Solo si hay suficiente texto blanco visible (>45 px)
    if white_count > 45:
        ocr_calls += 1
        res, _ = ocr(frame)
        if res:
            all_texts = [r[1] for r in res]
            if not is_watermark_present(all_texts):
                for item in res:
                    box, txt, score = item
                    clean = re.sub(r'[^a-zA-Z0-9]', '', txt.lower())
                    if 'cayon' in clean:
                        center_x = (box[0][0] + box[1][0]) / 2.0
                        if center_x < 120:
                            ts = str(timedelta(seconds=sec))
                            feed = " | ".join(all_texts)
                            print(f"  🎯 [BAJA ENCONTRADA] {ts} -> \"{feed}\"")
                            kills_found.append((sec, ts, feed))
    idx += 1

proc.stdout.close()
proc.wait()

elapsed = time.time() - t0
print(f"\n[✓] Completado en SOLO {elapsed:.2f} segundos!")
print(f"    - Frames analizados: {idx}")
print(f"    - Llamadas OCR realizadas: {ocr_calls} (se descartó el {((idx - ocr_calls)/idx)*100:.1f}% de frames vacíos)")
print(f"    - Bajas encontradas: {len(kills_found)}")
