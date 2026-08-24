import re
import cv2
import subprocess
import numpy as np
from datetime import timedelta
from rapidocr_onnxruntime import RapidOCR
from utils.paths import get_binary_path, NO_WINDOW_FLAGS
from .models import KillRecord
from .audio import AudioAnalyzer

class KillfeedScanner:
    def __init__(self):
        self.ocr = RapidOCR()
        
    @staticmethod
    def get_video_duration(video_path: str) -> int:
        try:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            cap.release()
            if fps > 0 and frame_count > 0:
                return int(frame_count / fps)
        except Exception:
            pass
        return 0

    @staticmethod
    def is_watermark_present(texts: list, filter_beta: bool) -> bool:
        if not filter_beta:
            return False
        full = " ".join(texts).lower()
        wm_tokens = ['wardogs', 'beta', '7656', 'aug 21', 'cl-49', 'live-cl', '11866', 'aug21', '7866', 'cl49']
        return any(t in full for t in wm_tokens)

    @staticmethod
    def parse_killfeed_line(res_sorted: list, clean_gamertags: list) -> tuple:
        texts = [r[1] for r in res_sorted]
        line_str = " | ".join(texts)
        dist_match = re.search(r'\[?(\d+)\s*m\]?', line_str, re.IGNORECASE)
        distance = f"[{dist_match.group(1)}m]" if dist_match else "Distancia media"
        
        killer = "Tu"
        victim = "Enemigo"
        
        parts = [t.strip() for t in texts if t.strip()]
        if len(parts) >= 2:
            killer = parts[0]
            victim = parts[-1]
            for p in parts[1:-1]:
                p_clean = re.sub(r'[^a-zA-Z0-9]', '', p.lower())
                if any(tag in p_clean for tag in clean_gamertags):
                    killer = p
                    
        return killer, distance, victim

    def scan_video(self, video_path: str, gamertags: list, detect_audio: bool, filter_beta: bool, 
                   use_gpu: bool = True, multi_window: int = 15, on_progress=None, is_running_check=None):
        """
        Escanea el video con normalización universal y discriminación estricta Asesino vs Víctima.
        Si tu nombre aparece a la derecha de la línea significa que has muerto y NO se contabiliza como baja.
        """
        clean_gamertags = []
        for t in gamertags:
            t_str = t.strip().lower()
            if not t_str:
                continue
            clean = re.sub(r'[^a-zA-Z0-9]', '', t_str)
            if clean and clean not in clean_gamertags:
                clean_gamertags.append(clean)
            words = re.findall(r'[a-zA-Z0-9]{2,}', t_str)
            for w in words:
                if w not in clean_gamertags:
                    clean_gamertags.append(w)
                    
        duration_sec = self.get_video_duration(video_path)
        
        audio_energies = []
        if detect_audio:
            audio_energies = AudioAnalyzer.analyze_audio_peaks(video_path)
            
        crop_w, crop_h, crop_x, crop_y = 320, 120, 0, 290
        fps_rate = 0.66
        
        vf_filter = f"fps={fps_rate},scale=1280:720,crop={crop_w}:{crop_h}:{crop_x}:{crop_y}"
        
        if use_gpu:
            cmd = [
                get_binary_path("ffmpeg"), "-hwaccel", "cuda", "-i", video_path,
                "-vf", vf_filter,
                "-f", "rawvideo", "-pix_fmt", "bgr24", "-v", "error", "pipe:1"
            ]
        else:
            cmd = [
                get_binary_path("ffmpeg"), "-i", video_path,
                "-vf", vf_filter,
                "-f", "rawvideo", "-pix_fmt", "bgr24", "-v", "error", "pipe:1"
            ]
        
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, creationflags=NO_WINDOW_FLAGS)
        except Exception:
            if use_gpu:
                cmd.pop(1); cmd.pop(1)
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, creationflags=NO_WINDOW_FLAGS)
            
        frame_len = crop_w * crop_h * 3
        idx = 0
        video_kills = []
        last_kill_sec = -999
        v_name = re.sub(r'^[a-zA-Z]:.*[\\/]', '', video_path)
        
        while is_running_check is None or is_running_check():
            raw = proc.stdout.read(frame_len)
            if len(raw) < frame_len:
                break
                
            sec = int(idx * (1.0 / fps_rate))
            frame = np.frombuffer(raw, dtype=np.uint8).reshape((crop_h, crop_w, 3))
            
            if on_progress and (idx % 2 == 0 or (duration_sec > 0 and sec >= duration_sec)):
                on_progress(sec, duration_sec, len(video_kills))
                
            white_mask = cv2.inRange(frame, np.array([160, 160, 160]), np.array([255, 255, 255]))
            if cv2.countNonZero(white_mask) > 35:
                res, _ = self.ocr(frame)
                if res:
                    all_texts = [r[1] for r in res]
                    if not self.is_watermark_present(all_texts, filter_beta):
                        # Ordenar cajas de texto de izquierda a derecha
                        res_sorted = sorted(res, key=lambda r: min(p[0] for p in r[0]))
                        
                        # Buscar si eres el atacante (lado izquierdo) y NO la víctima (lado derecho)
                        is_my_kill = False
                        matched_killer_text = None
                        
                        for r_idx, item in enumerate(res_sorted):
                            box, txt, score = item
                            clean_txt = re.sub(r'[^a-zA-Z0-9]', '', txt.lower())
                            
                            is_matched = any(gt in clean_txt for gt in clean_gamertags if len(gt) >= 2)
                            if is_matched:
                                min_x = min(p[0] for p in box)
                                center_x = (box[0][0] + box[1][0]) / 2.0
                                
                                # Si tu nombre está en la primera posición a la izquierda (< 115px) es una baja tuya
                                if r_idx == 0 and center_x < 120:
                                    is_my_kill = True
                                    matched_killer_text = txt
                                    break
                                elif r_idx == 1 and min_x < 90:
                                    # Caso donde el primer token sea un clan tag [TAG]
                                    prev_txt = res_sorted[0][1].strip()
                                    if prev_txt.startswith('[') or len(prev_txt) <= 5:
                                        is_my_kill = True
                                        matched_killer_text = txt
                                        break
                                # Si tu nombre aparece a la derecha de otro jugador (r_idx > 1 o center_x >= 120), significa que tú has muerto
                                # por lo que se ignora explícitamente.
                                
                        if is_my_kill:
                            if sec - last_kill_sec >= 3.0:
                                last_kill_sec = sec
                                ts_str = str(timedelta(seconds=sec))
                                killer, dist, victim = self.parse_killfeed_line(res_sorted, clean_gamertags)
                                
                                rec = KillRecord(
                                    video_path=video_path,
                                    video_name=v_name,
                                    time_sec=sec,
                                    timestamp=ts_str,
                                    killer=killer,
                                    distance=dist,
                                    victim=victim,
                                    frame_rgb=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                                )
                                video_kills.append(rec)
            idx += 1
            
        try:
            proc.terminate()
            proc.wait()
        except Exception:
            pass
            
        # Post-procesar multikills usando la ventana configurable
        for i, k in enumerate(video_kills):
            streak = 1
            for j in range(i - 1, -1, -1):
                if k.time_sec - video_kills[j].time_sec <= multi_window:
                    streak += 1
                else:
                    break
                    
            if streak == 2: k.play_type = "Doble Baja"
            elif streak == 3: k.play_type = "Triple Baja"
            elif streak >= 4: k.play_type = f"Racha x{streak}"
            else: k.play_type = "Baja"
            
            k.hype = AudioAnalyzer.get_hype_score(k.time_sec, audio_energies, streak > 1)
            
        return video_kills