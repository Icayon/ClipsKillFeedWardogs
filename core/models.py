from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class KillRecord:
    video_path: str
    video_name: str
    time_sec: int
    timestamp: str
    killer: str
    distance: str
    victim: str
    play_type: str = "Baja"
    hype: str = "Normal"
    frame_rgb: Optional[Any] = None