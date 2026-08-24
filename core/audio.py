import subprocess
import numpy as np
from utils.paths import get_binary_path, NO_WINDOW_FLAGS

class AudioAnalyzer:
    @staticmethod
    def analyze_audio_peaks(video_path: str) -> list:
        """Extrae la pista de audio en crudo a 8kHz mono y calcula el RMS por segundo"""
        try:
            cmd = [
                get_binary_path("ffmpeg"), "-i", video_path, "-vn",
                "-ac", "1", "-ar", "8000", "-f", "s16le", "-v", "error", "pipe:1"
            ]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=NO_WINDOW_FLAGS)
            raw = proc.stdout.read()
            proc.stdout.close()
            proc.wait()
            
            if not raw:
                return []
                
            samples = np.frombuffer(raw, dtype=np.int16)
            chunk_size = 8000
            num_chunks = len(samples) // chunk_size
            if num_chunks == 0:
                return []
                
            energies = []
            for i in range(num_chunks):
                chunk = samples[i * chunk_size : (i + 1) * chunk_size].astype(np.float32)
                rms = np.sqrt(np.mean(chunk**2) + 1e-6)
                energies.append(rms)
                
            return energies
        except Exception:
            return []

    @staticmethod
    def get_hype_score(kill_sec: int, audio_energies: list, is_multikill: bool) -> str:
        """Puntúa de 3 a 5 estrellas según la energía vocal detectada en el micrófono"""
        if not audio_energies or kill_sec >= len(audio_energies):
            return "⭐⭐⭐" if not is_multikill else "⭐⭐⭐⭐"
            
        start_sec = max(0, kill_sec - 2)
        end_sec = min(len(audio_energies), kill_sec + 5)
        window = audio_energies[start_sec:end_sec]
        
        avg_energy = np.mean(audio_energies)
        max_in_window = np.max(window) if len(window) > 0 else 0
        
        has_voice_hype = (max_in_window > avg_energy * 2.2) and (max_in_window > 800)
        
        if is_multikill and has_voice_hype:
            return "⭐⭐⭐⭐⭐"
        elif is_multikill or has_voice_hype:
            return "⭐⭐⭐⭐"
        else:
            return "⭐⭐⭐"