import os
import re
import cv2
import numpy as np
import subprocess
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
            
        try:
            cmd = [get_binary_path("ffmpeg"), "-i", video_path]
            p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, creationflags=NO_WINDOW_FLAGS)
            _, err = p.communicate(timeout=4)
            err_str = err.decode('utf-8', errors='ignore')
            m = re.search(r'Duration:\s*(\d+):(\d+):(\d+\.?\d*)', err_str)
            if m:
                h, mi, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
                return int(h * 3600 + mi * 60 + s)
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
    def parse_killfeed_line(texts: list, clean_gamertags: list) -> tuple:
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
                   use_gpu: bool = True, multi_window: int = 15, on_progress=None, on_kill_found=None, is_running_check=None):
        clean_gamertags = [re.sub(r'[^a-zA-Z0-9]', '', t.lower()) for t in gamertags if t.strip()]
        duration_sec = self.get_video_duration(video_path)
        
        audio_energies = []
        if detect_audio:
            audio_energies = AudioAnalyzer.analyze_audio_peaks(video_path)
            
        crop_x, crop_y, crop_w, crop_h = 0, 310, 240, 85
        fps_rate = 0.66
        vf_filter = f"fps={fps_rate},scale=1280:720,crop={crop_w}:{crop_h}:{crop_x}:{crop_y}"
        
        def start_ffmpeg(enable_gpu):
            if enable_gpu:
                c = [
                    get_binary_path("ffmpeg"), "-hwaccel", "cuda", "-i", video_path,
                    "-vf", vf_filter,
                    "-f", "rawvideo", "-pix_fmt", "bgr24", "-v", "error", "pipe:1"
                ]
            else:
                c = [
                    get_binary_path("ffmpeg"), "-i", video_path,
                    "-vf", vf_filter,
                    "-f", "rawvideo", "-pix_fmt", "bgr24", "-v", "error", "pipe:1"
                ]
            return subprocess.Popen(c, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, creationflags=NO_WINDOW_FLAGS)
        
        proc = start_ffmpeg(use_gpu)
        frame_len = crop_w * crop_h * 3
        
        # Leer primer frame con fallback automático a CPU
        raw = proc.stdout.read(frame_len)
        if len(raw) < frame_len and use_gpu:
            try:
                proc.terminate()
            except Exception:
                pass
            proc = start_ffmpeg(False)
            raw = proc.stdout.read(frame_len)
            
        idx = 0
        video_kills = []
        last_kill_sec = -999
        v_name = os.path.basename(video_path)
        
        while is_running_check is None or is_running_check():
            if len(raw) < frame_len:
                break
                
            sec = int(idx * (1.0 / fps_rate))
            frame = np.frombuffer(raw, dtype=np.uint8).reshape((crop_h, crop_w, 3))
            
            if on_progress:
                on_progress(sec, duration_sec, len(video_kills))
                
            white_mask = cv2.inRange(frame, np.array([170, 170, 170]), np.array([255, 255, 255]))
            if cv2.countNonZero(white_mask) > 30:
                res, _ = self.ocr(frame)
                if res:
                    all_texts = [r[1] for r in res]
                    if not self.is_watermark_present(all_texts, filter_beta):
                        for item in res:
                            box, txt, score = item
                            clean = re.sub(r'[^a-zA-Z0-9]', '', txt.lower())
                            
                            matched = any(gt in clean for gt in clean_gamertags if len(gt) >= 2)
                            if matched:
                                center_x = (box[0][0] + box[1][0]) / 2.0
                                
                                # Si el nombre aparece a la izquierda (center_x < 130), eres tú eliminando al enemigo
                                if center_x < 130:
                                    if sec - last_kill_sec >= 2.5:
                                        last_kill_sec = sec
                                        killer, distance, victim = self.parse_killfeed_line(all_texts, clean_gamertags)
                                        if txt.strip():
                                            killer = txt.strip()
                                            
                                        is_multikill = (len(video_kills) > 0 and (sec - video_kills[-1].time_sec <= multi_window))
                                        
                                        if is_multikill:
                                            if len(video_kills) >= 2 and (sec - video_kills[-2].time_sec <= multi_window):
                                                play_type = "Triple Baja"
                                            else:
                                                play_type = "Doble Baja"
                                        else:
                                            play_type = "Baja"
                                            
                                        hype = AudioAnalyzer.get_hype_score(sec, audio_energies, is_multikill)
                                        
                                        rec = KillRecord(
                                            video_path=video_path,
                                            video_name=v_name,
                                            time_sec=sec,
                                            timestamp=str(timedelta(seconds=sec)),
                                            killer=killer,
                                            distance=distance,
                                            victim=victim,
                                            play_type=play_type,
                                            hype=hype,
                                            frame_rgb=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                                        )
                                        video_kills.append(rec)
                                        
                                        if on_kill_found:
                                            on_kill_found(rec)
                                        break
                                        
            idx += 1
            raw = proc.stdout.read(frame_len)
            
        try:
            proc.terminate()
            proc.stdout.close()
        except Exception:
            pass
            
        return video_kills