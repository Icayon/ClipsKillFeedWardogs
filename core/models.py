from dataclasses import dataclass, field
from typing import Optional, List, Any

@dataclass
class KillRecord:
    video_path: str
    video_name: str
    time_sec: int
    timestamp: str
    killer: str
    distance: str
    victim: str
    play_type: str = "🎯 Baja"
    hype: str = "⭐⭐⭐"
    frame_rgb: Optional[Any] = None

    def to_dict(self):
        return {
            "video_path": self.video_path,
            "video_name": self.video_name,
            "time_sec": self.time_sec,
            "timestamp": self.timestamp,
            "killer": self.killer,
            "distance": self.distance,
            "victim": self.victim,
            "play_type": self.play_type,
            "hype": self.hype,
            "frame_rgb": self.frame_rgb
        }