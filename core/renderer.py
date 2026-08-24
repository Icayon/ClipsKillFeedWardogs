import os
import re
import subprocess
from utils.paths import get_binary_path, NO_WINDOW_FLAGS

class ClipRenderer:
    @staticmethod
    def get_unique_filepath(target_dir: str, base_name: str, ext: str = ".mp4") -> str:
        base_clean = re.sub(r'\.mp4$', '', base_name, flags=re.IGNORECASE)
        candidate = os.path.join(target_dir, f"{base_clean}{ext}")
        counter = 1
        while os.path.exists(candidate):
            try:
                with open(candidate, "a"): pass
                return candidate
            except Exception:
                candidate = os.path.join(target_dir, f"{base_clean}_{counter}{ext}")
                counter += 1
        return candidate

    @classmethod
    def render_clip(cls, video_path: str, start_t: int, duration: int, out_filepath: str, 
                    is_vertical: bool = False, use_gpu: bool = True) -> bool:
        """Renderiza el clip conservando la calidad y resolución 100% original del vídeo subido"""
        out_filepath = os.path.abspath(out_filepath)
        os.makedirs(os.path.dirname(out_filepath), exist_ok=True)
        ffmpeg_bin = get_binary_path("ffmpeg")
        
        if use_gpu:
            if is_vertical:
                filter_v = "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5[bg];[0:v]scale=1080:608[fg];[bg][fg]overlay=0:656"
                cmd = [
                    ffmpeg_bin, "-y", "-ss", str(start_t), "-i", video_path,
                    "-t", str(duration),
                    "-filter_complex", filter_v,
                    "-c:v", "h264_nvenc", "-preset", "p6", "-cq", "17", "-b:v", "0",
                    "-c:a", "aac", "-b:a", "320k", out_filepath
                ]
            else:
                # 16:9 con GPU en calidad visual sin pérdidas y resolución original
                cmd = [
                    ffmpeg_bin, "-y", "-ss", str(start_t), "-i", video_path,
                    "-t", str(duration),
                    "-c:v", "h264_nvenc", "-preset", "p6", "-cq", "17", "-b:v", "0",
                    "-c:a", "aac", "-b:a", "320k", out_filepath
                ]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=NO_WINDOW_FLAGS)
        
        # Fallback o modo CPU (libx264 en máxima calidad CRF 17)
        if not os.path.exists(out_filepath) or os.path.getsize(out_filepath) < 1000:
            if is_vertical:
                filter_v = "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5[bg];[0:v]scale=1080:608[fg];[bg][fg]overlay=0:656"
                cmd_cpu = [
                    ffmpeg_bin, "-y", "-ss", str(start_t), "-i", video_path,
                    "-t", str(duration),
                    "-filter_complex", filter_v,
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "17",
                    "-c:a", "aac", "-b:a", "320k", out_filepath
                ]
            else:
                cmd_cpu = [
                    ffmpeg_bin, "-y", "-ss", str(start_t), "-i", video_path,
                    "-t", str(duration),
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "17",
                    "-c:a", "aac", "-b:a", "320k", out_filepath
                ]
            subprocess.run(cmd_cpu, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=NO_WINDOW_FLAGS)
            
        return os.path.exists(out_filepath) and os.path.getsize(out_filepath) > 1000

    @classmethod
    def concatenate_clips(cls, clip_paths: list, out_filepath: str) -> bool:
        """Une múltiples clips en un Supercut Montage mediante el filtro concat sin pérdida"""
        if not clip_paths:
            return False
        out_dir = os.path.dirname(os.path.abspath(out_filepath))
        concat_list = os.path.join(out_dir, "temp_concat.txt")
        try:
            with open(concat_list, "w", encoding="utf-8") as f:
                for cp in clip_paths:
                    f.write(f"file '{os.path.abspath(cp)}'\n")
                    
            cmd = [get_binary_path("ffmpeg"), "-y", "-f", "concat", "-safe", "0", "-i", concat_list, "-c", "copy", out_filepath]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=NO_WINDOW_FLAGS)
            try: os.remove(concat_list)
            except Exception: pass
            return os.path.exists(out_filepath) and os.path.getsize(out_filepath) > 1000
        except Exception:
            return False