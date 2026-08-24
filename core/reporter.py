import os
import re
import subprocess
import webbrowser
from utils.paths import NO_WINDOW_FLAGS

class HtmlReporter:
    @staticmethod
    def get_unique_filepath(target_dir: str, base_name: str, ext: str = ".html") -> str:
        os.makedirs(target_dir, exist_ok=True)
        candidate = os.path.join(target_dir, f"{base_name}{ext}")
        if not os.path.exists(candidate):
            return candidate
        counter = 1
        while True:
            candidate = os.path.join(target_dir, f"{base_name}_{counter}{ext}")
            if not os.path.exists(candidate):
                return candidate
            counter += 1

    @classmethod
    def generate_report(cls, kills_data: list, out_dir: str = None) -> str:
        if not kills_data:
            return ""

        if not out_dir or not os.path.exists(out_dir):
            out_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            os.makedirs(out_dir, exist_ok=True)

        out_file = cls.get_unique_filepath(out_dir, "reporte_bajas_Wardogs")

        multikills = len([
            k for k in kills_data 
            if any(w in getattr(k, "play_type", "").upper() for w in ["DOBLE", "TRIPLE", "RACHA", "KILL", "MULTI"])
        ])
        hype_moments = len([
            k for k in kills_data 
            if getattr(k, "hype", "") in ["Alto", "Máximo", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"]
        ])

        rows = ""
        for k in kills_data:
            vname = getattr(k, "video_name", "")
            ts = getattr(k, "timestamp", "")
            killer = getattr(k, "killer", "")
            dist = getattr(k, "distance", "")
            victim = getattr(k, "victim", "")
            play = getattr(k, "play_type", "Baja")
            hype = getattr(k, "hype", "Normal")

            rows += f"""<tr>
<td>{vname}</td>
<td><strong style="color: #38bdf8;">{ts}</strong></td>
<td>{killer}</td>
<td>{dist}</td>
<td>{victim}</td>
<td><span class="tag">{play}</span></td>
<td>{hype}</td>
</tr>"""

        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Clips KillFeed Wardogs — Informe de Bajas</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d1117; color: #f0f6fc; margin: 0; padding: 35px; }}
.header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #30363d; padding-bottom: 15px; margin-bottom: 25px; }}
h1 {{ color: #38bdf8; font-size: 22px; margin: 0; }}
.byline {{ color: #8b949e; font-size: 13px; margin-top: 4px; }}
.stats {{ display: flex; gap: 15px; margin-bottom: 25px; }}
.card {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 15px 20px; flex: 1; }}
.card-val {{ font-size: 24px; font-weight: bold; color: #38bdf8; }}
.card-lbl {{ font-size: 11px; color: #8b949e; text-transform: uppercase; margin-top: 4px; }}
table {{ width: 100%; border-collapse: collapse; background: #161b22; border-radius: 8px; overflow: hidden; border: 1px solid #30363d; }}
th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid #30363d; font-size: 13px; }}
th {{ background: #21262d; color: #f0f6fc; font-weight: bold; font-size: 12px; }}
tr:hover {{ background: #1f242c; }}
.tag {{ padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; background: #1f6feb; color: white; }}
</style>
</head>
<body>
<div class="header">
    <div>
        <h1>Clips KillFeed Wardogs</h1>
        <div class="byline">Informe de bajas generado automáticamente</div>
    </div>
</div>
<div class="stats">
    <div class="card">
        <div class="card-val">{len(kills_data)}</div>
        <div class="card-lbl">Total Bajas Detectadas</div>
    </div>
    <div class="card">
        <div class="card-val">{multikills}</div>
        <div class="card-lbl">Multikills / Rachas</div>
    </div>
    <div class="card">
        <div class="card-val">{hype_moments}</div>
        <div class="card-lbl">Momentos de Hype</div>
    </div>
</div>
<table>
<thead>
<tr>
<th>Vídeo</th>
<th>Marca de Tiempo</th>
<th>Asesino (Tú)</th>
<th>Distancia</th>
<th>Víctima</th>
<th>Tipo de Jugada</th>
<th>Hype de Voz</th>
</tr>
</thead>
<tbody>
{rows}
</tbody></table></body></html>"""

        with open(out_file, "w", encoding="utf-8") as f:
            f.write(html)

        return os.path.abspath(out_file)

    @classmethod
    def generate_and_open(cls, kills_data: list, out_dir: str = None) -> bool:
        report_path = cls.generate_report(kills_data, out_dir)
        if not report_path or not os.path.exists(report_path):
            return False

        try:
            webbrowser.open(f"file:///{report_path.replace(chr(92), '/')}")
            return True
        except Exception:
            try:
                os.startfile(report_path)
                return True
            except Exception:
                return False