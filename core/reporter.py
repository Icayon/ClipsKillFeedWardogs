import os
import subprocess
import webbrowser
from utils.paths import NO_WINDOW_FLAGS

class HtmlReporter:
    @staticmethod
    def generate_and_open(kills_data: list):
        if not kills_data:
            return False
            
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.exists(downloads_folder):
            downloads_folder = os.path.abspath(".")
            
        out_file = os.path.join(downloads_folder, "reporte_bajas_Wardogs_ICayon.html")
        
        multikills = len([k for k in kills_data if "BAJA" in getattr(k, "play_type", "") or "KILL" in getattr(k, "play_type", "") or "RACHA" in getattr(k, "play_type", "")])
        hype_moments = len([k for k in kills_data if "⭐⭐⭐⭐" in getattr(k, "hype", "")])
        
        rows = ""
        for k in kills_data:
            vname = getattr(k, "video_name", "")
            ts = getattr(k, "timestamp", "")
            killer = getattr(k, "killer", "")
            dist = getattr(k, "distance", "")
            victim = getattr(k, "victim", "")
            play = getattr(k, "play_type", "🎯 Baja")
            hype = getattr(k, "hype", "⭐⭐⭐")
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
<title>Clips KillFeed Wardogs by ICayon — Informe de Bajas</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d1117; color: #f0f6fc; margin: 0; padding: 35px; }}
.header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #30363d; padding-bottom: 15px; margin-bottom: 25px; }}
h1 {{ color: #38bdf8; font-size: 22px; margin: 0; }}
.byline {{ color: #8b949e; font-size: 13px; margin-top: 4px; }}
.socials a {{ color: #58a6ff; text-decoration: none; font-weight: bold; margin-left: 15px; font-size: 13px; }}
.stats {{ display: flex; gap: 15px; margin-bottom: 25px; }}
.card {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 15px 20px; flex: 1; }}
.card-val {{ font-size: 24px; font-weight: bold; color: #238636; }}
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
        <h1>🎯 Clips KillFeed Wardogs</h1>
        <div class="byline">Creado por <strong>ICayon</strong> • Informe generado automáticamente</div>
    </div>
    <div class="socials">
        <a href="https://x.com/ICayonh" target="_blank">𝕏 @ICayonh</a>
        <a href="https://www.twitch.tv/icayon" target="_blank">🟣 Twitch/icayon</a>
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
        <div class="card-lbl">Momentos con Hype de Voz</div>
    </div>
</div>
<table>
<thead>
<tr>
<th>Vídeo</th>
<th>Minuto</th>
<th>Asesino (Tú)</th>
<th>Distancia</th>
<th>Víctima</th>
<th>Tipo de Jugada</th>
<th>Hype Voz</th>
</tr>
</thead>
<tbody>
{rows}
</tbody></table></body></html>"""
        
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(html)
            
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        if os.path.exists(chrome_path):
            try:
                subprocess.Popen([chrome_path, out_file], creationflags=NO_WINDOW_FLAGS)
                return True
            except Exception:
                pass
        webbrowser.open(f"file:///{os.path.abspath(out_file).replace(chr(92), '/')}")
        return True