import os
import sys
import re
import glob
import time
import webbrowser
import subprocess
import threading
from datetime import timedelta
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import customtkinter as ctk
import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR

# Configuración de apariencia
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

if sys.platform == "win32" and sys.stdout is not None:
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

NO_WINDOW_FLAGS = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0

def get_binary_path(binary_name):
    """Busca los ejecutables de ffmpeg o ffplay empaquetados o en el sistema"""
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
        p1 = os.path.join(base_dir, f"{binary_name}.exe")
        if os.path.exists(p1): return p1
        meipass = getattr(sys, '_MEIPASS', base_dir)
        p2 = os.path.join(meipass, f"{binary_name}.exe")
        if os.path.exists(p2): return p2
    local_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{binary_name}.exe")
    if os.path.exists(local_p): return local_p
    return binary_name

# Paleta Gaming Studio Profesional
BG_MAIN         = "#0d1117"   # Fondo oscuro principal
CARD_BG         = "#161b22"   # Fondo de tarjetas y paneles
CARD_BORDER     = "#30363d"   # Bordes de 1px
INNER_BG        = "#090d13"   # Fondo de campos y tablas
HOVER_BG        = "#21262d"   # Hover
HOVER_LIGHT     = "#30363d"

ACCENT_BLUE     = "#2f81f7"   # Azul Twitch/Gaming
ACCENT_BLUE_H   = "#1f6feb"
ACCENT_GREEN    = "#238636"   # Verde éxito
ACCENT_GREEN_H  = "#2ea043"
ACCENT_PURPLE   = "#8b5cf6"   # Púrpura Shorts/Montaje
ACCENT_PURPLE_H = "#7c3aed"
ACCENT_RED      = "#da3633"   # Rojo detener/eliminar
ACCENT_RED_H    = "#b91c1c"
ACCENT_CYAN     = "#38bdf8"   # Azul claro para títulos

TEXT_WHITE      = "#f0f6fc"
TEXT_MUTED      = "#8b949e"
TEXT_LIGHT      = "#c9d1d9"

# Diccionario Bilingüe Completo (Español / English)
I18N = {
    "es": {
        "title": "Clips KillFeed Wardogs by ICayon",
        "subtitle": "Detector Inteligente de Bajas y Editor de Clips",
        "btn_help": "❓ Guía y Tutorial",
        "lang": "Idioma:",
        "queue_title": "📁 Vídeos a Analizar",
        "add_files": "🎬 Añadir Vídeo(s)...",
        "add_folder": "📂 Añadir Carpeta...",
        "clear_queue": "🗑️ Limpiar",
        "empty_queue": "No hay vídeos en la cola.\nAñade tus grabaciones de OBS para empezar.",
        "files_loaded": "vídeos cargados",
        "tracking_label": "👤 Tu Gamertag / Nombre:",
        "help_tooltip": "Haz clic para ver el tutorial paso a paso",
        "audio_hype": "🎙️ Detectar Picos de Voz y Gritos (Hype)",
        "filter_beta": "🛡️ Ignorar Marca de Agua de la Beta",
        "btn_start": "▶ Iniciar Escaneo",
        "btn_stop": "⏹ Detener",
        "ready": "Listo para Escanear",
        "scanning": "Analizando Vídeos...",
        "scan_finished": "¡Escaneo Completado!",
        "kills_indexed": "bajas detectadas",
        "events_title": "🎯 Catálogo de Bajas y Jugadas",
        "col_time": "Minuto",
        "col_killer": "Asesino (Tú)",
        "col_dist": "Distancia",
        "col_target": "Víctima",
        "col_play": "Tipo de Jugada",
        "col_hype": "Hype Voz",
        "preview_title": "🔍 Vista Previa y Acciones",
        "preview_hint": "Selecciona una baja de la tabla\npara ver el fotograma aquí.",
        "meta_file": "🎬 Vídeo:",
        "meta_time": "⏱️ Minuto:",
        "meta_play": "🎯 Jugada:",
        "meta_dist": "🔫 Distancia:",
        "meta_target": "💀 Víctima:",
        "meta_hype": "🎙️ Hype Voz:",
        "btn_cut_this": "✂️ Recortar Esta Jugada",
        "btn_play_seek": "▶ Ver Jugada (5s Antes)",
        "btn_open_full": "🎬 Abrir Vídeo Completo",
        "btn_batch": "⚡ Recorte Masivo / Montaje...",
        "btn_html": "🌐 Informe HTML en Chrome",
        "single_modal_title": "✂️ Guardar Clip de Jugada",
        "single_clip_name": "📝 Nombre del Clip:",
        "single_dest_folder": "📁 Carpeta de Destino:",
        "btn_browse": "Examinar...",
        "btn_h169": "🖥️ Horizontal 16:9",
        "btn_v916": "📱 Vertical 9:16 (Shorts)",
        "btn_both": "🌟 Ambos Formatos",
        "export_success": "¡Clip guardado correctamente en tu carpeta!",
        "batch_modal_title": "⚡ Exportación Masiva de Clips",
        "batch_mode": "Modo de Exportación:",
        "batch_sep": "Clips Separados",
        "batch_montage": "Montaje Unificado (1 Vídeo)",
        "batch_both": "Ambos (Separados + Montaje)",
        "btn_run_batch": "⚡ Ejecutar Exportación con GPU",
        "tut_title": "Guía Paso a Paso — Clips KillFeed Wardogs",
        "tut_step1_title": "1. Seleccionar Vídeos o Carpetas",
        "tut_step1_desc": "Usa los botones 'Añadir Vídeo(s)' o 'Añadir Carpeta' para cargar tus partidas grabadas con OBS. Puedes añadir múltiples vídeos a la vez.",
        "tut_step2_title": "2. Indicar tu Gamertag / Nombre",
        "tut_step2_desc": "Escribe el nombre exacto que tenías en la partida (ej: ICayon, [ESP] ICayon). Si usas varios tags, sepáralos con comas. El motor OCR inteligente buscará exactamente tus bajas en el Killfeed.",
        "tut_step3_title": "3. Detector de Hype y Picos de Voz",
        "tut_step3_desc": "Al activar esta casilla, la app analiza la pista de audio de tu micrófono. Cuando detecta gritos, celebraciones o euforia, marca la jugada con ⭐⭐⭐⭐⭐ de Hype para que encuentres fácilmente tus mejores momentos.",
        "tut_step4_title": "4. Iniciar el Escaneo por GPU",
        "tut_step4_desc": "Pulsa 'Iniciar Escaneo'. El motor acelerado por hardware analizará cada fotograma a máxima velocidad y rellenará automáticamente la tabla con cada baja detectada.",
        "tut_step5_title": "5. Vista Previa y Recortes",
        "tut_step5_desc": "• Doble Clic en la tabla: Reproduce la jugada instantáneamente 5 segundos antes de la baja.\n• Recortar Esta Jugada: Genera el clip en Horizontal 16:9 o Vertical 9:16 Shorts (con fondo difuminado cinematográfico).\n• Recorte Masivo / Montaje: Genera todos los clips de golpe o crea un Supercut unificado.\n• Informe HTML: Abre un reporte visual con estadísticas en Google Chrome.",
        "tut_btn_close": "Entendido, ¡a recortar!"
    },
    "en": {
        "title": "Clips KillFeed Wardogs by ICayon",
        "subtitle": "Smart Killfeed Detector & Highlight Clip Studio",
        "btn_help": "❓ Guide & Tutorial",
        "lang": "Language:",
        "queue_title": "📁 Videos to Scan",
        "add_files": "🎬 Add Video(s)...",
        "add_folder": "📂 Add Folder...",
        "clear_queue": "🗑️ Clear",
        "empty_queue": "Queue is empty.\nAdd your OBS recordings to begin.",
        "files_loaded": "videos loaded",
        "tracking_label": "👤 In-game Gamertag / Name:",
        "help_tooltip": "Click to view step-by-step tutorial",
        "audio_hype": "🎙️ Detect Voice Peaks & Shouting (Hype)",
        "filter_beta": "🛡️ Suppress Beta Watermark",
        "btn_start": "▶ Start Scan",
        "btn_stop": "⏹ Stop",
        "ready": "Ready to Scan",
        "scanning": "Scanning Videos...",
        "scan_finished": "Scan Completed!",
        "kills_indexed": "kills detected",
        "events_title": "🎯 Detected Kills & Plays",
        "col_time": "Time",
        "col_killer": "Actor (You)",
        "col_dist": "Distance",
        "col_target": "Victim",
        "col_play": "Play Type",
        "col_hype": "Voice Hype",
        "preview_title": "🔍 Preview & Actions",
        "preview_hint": "Select a kill from the table\nto inspect frame capture here.",
        "meta_file": "🎬 Video:",
        "meta_time": "⏱️ Time:",
        "meta_play": "🎯 Play:",
        "meta_dist": "🔫 Distance:",
        "meta_target": "💀 Victim:",
        "meta_hype": "🎙️ Voice Hype:",
        "btn_cut_this": "✂️ Clip This Play",
        "btn_play_seek": "▶ Play Seek (5s Before)",
        "btn_open_full": "🎬 Open Full Video",
        "btn_batch": "⚡ Batch Export / Montage...",
        "btn_html": "🌐 HTML Report in Chrome",
        "single_modal_title": "✂️ Save Highlight Clip",
        "single_clip_name": "📝 Clip File Name:",
        "single_dest_folder": "📁 Destination Folder:",
        "btn_browse": "Browse...",
        "btn_h169": "🖥️ Landscape 16:9",
        "btn_v916": "📱 Portrait 9:16 (Shorts)",
        "btn_both": "🌟 Both Formats",
        "export_success": "Clip successfully exported to your folder!",
        "batch_modal_title": "⚡ Batch Clip Export",
        "batch_mode": "Export Mode:",
        "batch_sep": "Separate Clips",
        "batch_montage": "Unified Supercut Montage",
        "batch_both": "Both (Separate + Montage)",
        "btn_run_batch": "⚡ Execute GPU Batch Export",
        "tut_title": "Step-by-Step Guide — Clips KillFeed Wardogs",
        "tut_step1_title": "1. Select Videos or Folders",
        "tut_step1_desc": "Use 'Add Video(s)' or 'Add Folder' to load your OBS game recordings. You can queue multiple videos at once.",
        "tut_step2_title": "2. Enter your In-Game Gamertag",
        "tut_step2_desc": "Type the exact name you used during the match (e.g., ICayon, [ESP] ICayon). If you use multiple tags, separate them with commas. The smart OCR engine will locate your kills in the Killfeed.",
        "tut_step3_title": "3. Audio Hype & Voice Peak Scoring",
        "tut_step3_desc": "When enabled, the app analyzes your microphone track. Whenever it detects shouting, hype or celebrations, it badges the kill with ⭐⭐⭐⭐⭐ so you can instantly spot your best plays.",
        "tut_step4_title": "4. Launch GPU-Accelerated Scan",
        "tut_step4_desc": "Click 'Start Scan'. The hardware-accelerated engine analyzes each video at high speed and automatically populates the table with every detected kill.",
        "tut_step5_title": "5. Preview & Clip Cutting",
        "tut_step5_desc": "• Double-Click table row: Instantly plays the video 5 seconds before the kill.\n• Clip This Play: Exports the clip in 16:9 Landscape or 9:16 Portrait Shorts (with cinematic blurred background).\n• Batch Export / Montage: Renders all clips at once or creates a single unified Supercut.\n• HTML Report: Opens an interactive visual statistics summary in Google Chrome.",
        "tut_btn_close": "Got it, let's clip!"
    }
}


class AutoClipWardogsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.current_lang = "es"
        
        self.title("Clips KillFeed Wardogs by ICayon")
        self.geometry("1280x870")
        self.minsize(1100, 740)
        self.configure(fg_color=BG_MAIN)
        
        # Icono de Ventana y Barra de Tareas
        try:
            icon_ico = get_binary_path("app_icon.ico")
            if not os.path.exists(icon_ico):
                base_d = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
                p1 = os.path.join(base_d, "Archivos", "app_icon.ico")
                p2 = os.path.join(base_d, "assets", "app_icon.ico")
                icon_ico = p1 if os.path.exists(p1) else p2
            if os.path.exists(icon_ico):
                self.iconbitmap(icon_ico)
        except Exception:
            pass
        
        self.is_running = False
        self.current_process = None
        
        # OCR Local
        self.ocr = RapidOCR()
        
        # Estado
        self.video_list = []
        self.all_kills_data = []
        self.preview_image_ref = None
        self.custom_out_dir = r"E:\Videos OBS\Clips_Generados"
        
        self.setup_ui()
        
    def t(self, key):
        return I18N[self.current_lang].get(key, key)
        
    def setup_ui(self):
        # -------------------------------------------------------------
        # 1. HEADER CON REDES SOCIALES DE ICAYON, TUTORIAL & IDIOMA
        # -------------------------------------------------------------
        header = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=0, height=60, border_width=1, border_color=CARD_BORDER)
        header.pack(fill="x", side="top")
        
        # Izquierda: Título y Firma del Creador
        head_left = ctk.CTkFrame(header, fg_color="transparent")
        head_left.pack(side="left", padx=18, pady=8)
        
        # Logo Perro Wardogs en el Encabezado
        try:
            png_logo_path = get_binary_path("app_icon.png")
            if not os.path.exists(png_logo_path):
                base_d = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
                p1 = os.path.join(base_d, "Archivos", "app_icon.png")
                p2 = os.path.join(base_d, "assets", "app_icon.png")
                png_logo_path = p1 if os.path.exists(p1) else p2
            if os.path.exists(png_logo_path):
                pil_logo = Image.open(png_logo_path).resize((36, 36), Image.Resampling.LANCZOS)
                self.header_logo_img = ImageTk.PhotoImage(pil_logo)
                lbl_logo = ctk.CTkLabel(head_left, image=self.header_logo_img, text="")
                lbl_logo.pack(side="left", padx=(0, 10))
        except Exception:
            pass
            
        title_box = ctk.CTkFrame(head_left, fg_color="transparent")
        title_box.pack(side="left")
        
        self.lbl_main_title = ctk.CTkLabel(
            title_box, 
            text="Clips KillFeed Wardogs", 
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
            text_color=TEXT_WHITE
        )
        self.lbl_main_title.pack(side="left")
        
        lbl_by = ctk.CTkLabel(
            title_box, 
            text="by ICayon", 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#38bdf8",
            fg_color="#0c2d48",
            corner_radius=6,
            padx=8,
            pady=2
        )
        lbl_by.pack(side="left", padx=(10, 0))
        
        # Derecha: Redes Sociales, Botón de Tutorial y Selector de Idioma
        head_right = ctk.CTkFrame(header, fg_color="transparent")
        head_right.pack(side="right", padx=18, pady=8)
        
        # Botón Guía / Tutorial
        self.btn_top_help = ctk.CTkButton(
            head_right, 
            text=self.t("btn_help"), 
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=INNER_BG,
            hover_color=HOVER_BG,
            border_width=1,
            border_color=CARD_BORDER,
            text_color=ACCENT_CYAN,
            height=32,
            corner_radius=6,
            command=self.open_tutorial_modal
        )
        self.btn_top_help.pack(side="left", padx=(0, 10))
        
        # Botón Twitter / X de ICayon
        btn_twitter = ctk.CTkButton(
            head_right, 
            text="𝕏 @ICayonh", 
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#181c24",
            hover_color="#000000",
            border_width=1,
            border_color="#38444d",
            text_color="#ffffff",
            width=100,
            height=32,
            corner_radius=6,
            command=lambda: webbrowser.open("https://x.com/ICayonh")
        )
        btn_twitter.pack(side="left", padx=(0, 8))
        
        # Botón Twitch de ICayon
        btn_twitch = ctk.CTkButton(
            head_right, 
            text="🟣 Twitch/icayon", 
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#6441a5",
            hover_color="#7d5bbe",
            text_color="#ffffff",
            width=125,
            height=32,
            corner_radius=6,
            command=lambda: webbrowser.open("https://www.twitch.tv/icayon")
        )
        btn_twitch.pack(side="left", padx=(0, 14))
        
        # Selector de Idioma (Español / English)
        self.lang_switch = ctk.CTkSegmentedButton(
            head_right, 
            values=["🇪🇸 Español", "🇬🇧 English"],
            height=32,
            fg_color=INNER_BG,
            selected_color=ACCENT_BLUE,
            selected_hover_color=ACCENT_BLUE_H,
            command=self.change_language
        )
        self.lang_switch.set("🇪🇸 Español")
        self.lang_switch.pack(side="left")

        # -------------------------------------------------------------
        # 2. CUERPO PRINCIPAL DIVIDIDO (3 PANELES INTUITIVOS)
        # -------------------------------------------------------------
        main_body = ctk.CTkFrame(self, fg_color="transparent")
        main_body.pack(fill="both", expand=True, padx=16, pady=12)
        
        main_body.columnconfigure(0, weight=3) # Panel Izquierdo: Cola & Configuración
        main_body.columnconfigure(1, weight=5) # Panel Central: Tabla de Bajas
        main_body.columnconfigure(2, weight=3) # Panel Derecho: Vista Previa & Acciones
        main_body.rowconfigure(0, weight=1)
        
        self.build_left_queue_panel(main_body)
        self.build_center_table_panel(main_body)
        self.build_right_preview_panel(main_body)

    # =================================================================
    # PANEL 1 (IZQUIERDA): VÍDEOS Y CONFIGURACIÓN
    # =================================================================
    def build_left_queue_panel(self, parent):
        box = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=8, border_width=1, border_color=CARD_BORDER)
        box.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        
        self.lbl_queue_hdr = ctk.CTkLabel(
            box, 
            text=self.t("queue_title"), 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=ACCENT_CYAN
        )
        self.lbl_queue_hdr.pack(anchor="w", padx=16, pady=(16, 8))
        
        # Botones de añadir vídeos (Cajas sólidas)
        btn_box = ctk.CTkFrame(box, fg_color="transparent")
        btn_box.pack(fill="x", padx=16, pady=(0, 8))
        
        self.btn_add_files = ctk.CTkButton(
            btn_box, 
            text=self.t("add_files"), 
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=ACCENT_BLUE,
            hover_color=ACCENT_BLUE_H,
            height=34,
            corner_radius=6,
            command=self.add_files
        )
        self.btn_add_files.pack(side="left", fill="x", expand=True, padx=(0, 4))
        
        self.btn_add_folder = ctk.CTkButton(
            btn_box, 
            text=self.t("add_folder"), 
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=INNER_BG,
            hover_color=HOVER_BG,
            border_width=1,
            border_color=CARD_BORDER,
            height=34,
            corner_radius=6,
            command=self.add_folder
        )
        self.btn_add_folder.pack(side="left", fill="x", expand=True)
        
        # Lista de vídeos con scroll
        self.scroll_videos = ctk.CTkScrollableFrame(box, fg_color=INNER_BG, corner_radius=6, border_width=1, border_color=CARD_BORDER)
        self.scroll_videos.pack(fill="both", expand=True, padx=16, pady=(0, 8))
        
        self.lbl_empty_queue = ctk.CTkLabel(
            self.scroll_videos, 
            text=self.t("empty_queue"), 
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED
        )
        self.lbl_empty_queue.pack(pady=40)
        
        # Configuración de Gamertag y opciones
        config_box = ctk.CTkFrame(box, fg_color="transparent")
        config_box.pack(fill="x", padx=16, pady=(0, 10))
        
        # Fila Gamertag con botón (?) explicativo
        gt_header_row = ctk.CTkFrame(config_box, fg_color="transparent")
        gt_header_row.pack(fill="x", pady=(0, 3))
        
        self.lbl_tracking = ctk.CTkLabel(
            gt_header_row, 
            text=self.t("tracking_label"), 
            font=ctk.CTkFont(size=11, weight="bold"), 
            text_color=TEXT_WHITE
        )
        self.lbl_tracking.pack(side="left")
        
        # Botón [ ? ] con caja sólida
        btn_help_gt = ctk.CTkButton(
            gt_header_row, 
            text="?", 
            width=24, 
            height=22, 
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#1e293b",
            hover_color=ACCENT_BLUE,
            border_width=1,
            border_color=CARD_BORDER,
            text_color=ACCENT_CYAN,
            corner_radius=4,
            command=self.open_tutorial_modal
        )
        btn_help_gt.pack(side="right")
        
        self.ent_gamertags = ctk.CTkEntry(
            config_box, 
            height=34, 
            font=ctk.CTkFont(size=12),
            fg_color=INNER_BG,
            border_color=CARD_BORDER,
            border_width=1,
            text_color=TEXT_WHITE
        )
        self.ent_gamertags.insert(0, "ICayon, [ESP] ICayon, [LIVE] ICayon")
        self.ent_gamertags.pack(fill="x", pady=(0, 8))
        
        self.chk_detect_audio = ctk.CTkCheckBox(
            config_box, 
            text=self.t("audio_hype"), 
            font=ctk.CTkFont(size=11),
            text_color=TEXT_LIGHT,
            fg_color=ACCENT_BLUE,
            hover_color=ACCENT_BLUE_H
        )
        self.chk_detect_audio.select()
        self.chk_detect_audio.pack(anchor="w", pady=2)
        
        self.chk_filter_beta = ctk.CTkCheckBox(
            config_box, 
            text=self.t("filter_beta"), 
            font=ctk.CTkFont(size=11),
            text_color=TEXT_LIGHT,
            fg_color=ACCENT_BLUE,
            hover_color=ACCENT_BLUE_H
        )
        self.chk_filter_beta.select()
        self.chk_filter_beta.pack(anchor="w", pady=2)
        
        # Botones de Escaneo (Cajas sólidas y limpias)
        action_row = ctk.CTkFrame(box, fg_color="transparent")
        action_row.pack(fill="x", padx=16, pady=(4, 16))
        
        self.btn_start = ctk.CTkButton(
            action_row, 
            text=self.t("btn_start"), 
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=ACCENT_GREEN, 
            hover_color=ACCENT_GREEN_H,
            text_color="#ffffff",
            height=36,
            corner_radius=6,
            command=self.start_scan
        )
        self.btn_start.pack(side="left", fill="x", expand=True, padx=(0, 6))
        
        self.btn_stop = ctk.CTkButton(
            action_row, 
            text=self.t("btn_stop"), 
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=INNER_BG, 
            hover_color=ACCENT_RED,
            border_width=1,
            border_color=CARD_BORDER,
            text_color=TEXT_MUTED,
            height=36,
            width=85,
            corner_radius=6,
            state="disabled",
            command=self.stop_scan
        )
        self.btn_stop.pack(side="right")

    # =================================================================
    # PANEL 2 (CENTRO): TABLA DE BAJAS Y JUGADAS
    # =================================================================
    def build_center_table_panel(self, parent):
        box = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=8, border_width=1, border_color=CARD_BORDER)
        box.grid(row=0, column=1, sticky="nsew", padx=6)
        
        top_bar = ctk.CTkFrame(box, fg_color="transparent")
        top_bar.pack(fill="x", padx=16, pady=(16, 8))
        
        self.lbl_events_hdr = ctk.CTkLabel(
            top_bar, 
            text=self.t("events_title"), 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=ACCENT_CYAN
        )
        self.lbl_events_hdr.pack(side="left")
        
        self.lbl_status_progress = ctk.CTkLabel(
            top_bar, 
            text=self.t("ready"), 
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED
        )
        self.lbl_status_progress.pack(side="right")
        
        # Tabla de bajas
        table_frame = ctk.CTkFrame(box, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        
        columns = ("time", "killer", "dist", "victim", "play", "hype")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        self.update_table_headers()
        
        self.tree.column("time", width=75, anchor="center")
        self.tree.column("killer", width=105, anchor="w")
        self.tree.column("dist", width=80, anchor="center")
        self.tree.column("victim", width=120, anchor="w")
        self.tree.column("play", width=125, anchor="center")
        self.tree.column("hype", width=80, anchor="center")
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview", 
            background=INNER_BG, 
            foreground=TEXT_WHITE, 
            fieldbackground=INNER_BG, 
            rowheight=26, 
            font=("Segoe UI", 10),
            borderwidth=0
        )
        style.configure(
            "Treeview.Heading", 
            background="#21262d", 
            foreground=TEXT_WHITE, 
            font=("Segoe UI", 10, "bold"),
            borderwidth=0
        )
        style.map("Treeview", background=[('selected', ACCENT_BLUE)], foreground=[('selected', '#ffffff')])
        
        tree_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")
        
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Double-1>", lambda e: self.open_selected_video_at_time())
        
        # Barra de progreso inferior del escaneo con indicador destacado de %
        prog_info_box = ctk.CTkFrame(box, fg_color="transparent")
        prog_info_box.pack(fill="x", padx=16, pady=(0, 4))
        
        self.lbl_progress_detail = ctk.CTkLabel(
            prog_info_box, 
            text="00:00:00 / 00:00:00", 
            font=ctk.CTkFont(size=11), 
            text_color=TEXT_MUTED
        )
        self.lbl_progress_detail.pack(side="left")
        
        self.lbl_progress_pct = ctk.CTkLabel(
            prog_info_box, 
            text="0%", 
            font=ctk.CTkFont(size=13, weight="bold"), 
            text_color=ACCENT_CYAN
        )
        self.lbl_progress_pct.pack(side="right")
        
        self.progress_bar = ctk.CTkProgressBar(box, height=8, progress_color=ACCENT_BLUE, fg_color=INNER_BG, corner_radius=4)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=16, pady=(0, 16))

    # =================================================================
    # PANEL 3 (DERECHA): VISTA PREVIA Y ACCIONES DE CLIP
    # =================================================================
    def build_right_preview_panel(self, parent):
        box = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=8, border_width=1, border_color=CARD_BORDER)
        box.grid(row=0, column=2, sticky="nsew", padx=(6, 0))
        
        self.lbl_preview_hdr = ctk.CTkLabel(
            box, 
            text=self.t("preview_title"), 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=ACCENT_CYAN
        )
        self.lbl_preview_hdr.pack(anchor="w", padx=16, pady=(16, 8))
        
        # Fotograma recortado del Killfeed
        img_box = ctk.CTkFrame(box, fg_color=INNER_BG, corner_radius=6, border_width=1, border_color=CARD_BORDER)
        img_box.pack(fill="x", padx=16, pady=(0, 10))
        
        self.lbl_preview_img = ctk.CTkLabel(
            img_box, 
            text=self.t("preview_hint"), 
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED, 
            height=100
        )
        self.lbl_preview_img.pack(fill="both", expand=True, padx=4, pady=4)
        
        # Metadatos del evento
        self.lbl_preview_details = ctk.CTkLabel(
            box, 
            text=f"{self.t('meta_file')} ---\n{self.t('meta_time')} --:--:--\n{self.t('meta_play')} ---\n{self.t('meta_dist')} ---\n{self.t('meta_target')} ---\n{self.t('meta_hype')} ---",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_LIGHT,
            justify="left"
        )
        self.lbl_preview_details.pack(anchor="w", padx=16, pady=(0, 12))
        
        # Botonera de acciones (TODOS con cajas sólidas bien definidas)
        action_box = ctk.CTkFrame(box, fg_color="transparent")
        action_box.pack(fill="x", padx=16, pady=(0, 16), side="bottom")
        
        # 1. Recortar esta jugada
        self.btn_cut_this = ctk.CTkButton(
            action_box, 
            text=self.t("btn_cut_this"), 
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=ACCENT_GREEN, 
            hover_color=ACCENT_GREEN_H,
            text_color="#ffffff",
            height=34,
            corner_radius=6,
            command=self.open_single_cut_dialog
        )
        self.btn_cut_this.pack(fill="x", pady=(0, 6))
        
        # 2. Reproducir al segundo exacto
        self.btn_preview_sec = ctk.CTkButton(
            action_box, 
            text=self.t("btn_play_seek"), 
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=ACCENT_BLUE, 
            hover_color=ACCENT_BLUE_H,
            text_color="#ffffff",
            height=32,
            corner_radius=6,
            command=self.open_selected_video_at_time
        )
        self.btn_preview_sec.pack(fill="x", pady=(0, 6))
        
        # 3. Recorte Masivo / Montaje
        self.btn_batch = ctk.CTkButton(
            action_box, 
            text=self.t("btn_batch"), 
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=ACCENT_PURPLE, 
            hover_color=ACCENT_PURPLE_H,
            text_color="#ffffff",
            height=32,
            corner_radius=6,
            command=self.open_batch_export_dialog
        )
        self.btn_batch.pack(fill="x", pady=(0, 6))
        
        # 4. Abrir informe en Google Chrome
        self.btn_html = ctk.CTkButton(
            action_box, 
            text=self.t("btn_html"), 
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=INNER_BG, 
            hover_color=HOVER_BG,
            border_width=1,
            border_color=CARD_BORDER,
            text_color=TEXT_WHITE,
            height=30,
            corner_radius=6,
            command=self.export_html_report
        )
        self.btn_html.pack(fill="x", pady=(0, 6))
        
        # 5. Abrir vídeo original completo (Caja sólida definida)
        self.btn_open_video = ctk.CTkButton(
            action_box, 
            text=self.t("btn_open_full"), 
            font=ctk.CTkFont(size=11),
            fg_color=INNER_BG, 
            hover_color=HOVER_BG,
            border_width=1,
            border_color=CARD_BORDER,
            text_color=TEXT_LIGHT,
            height=28,
            corner_radius=6,
            command=self.open_original_video_file
        )
        self.btn_open_video.pack(fill="x")

    # =================================================================
    # MODAL INTERACTIVO: MINI TUTORIAL PASO A PASO
    # =================================================================
    def open_tutorial_modal(self):
        dlg = ctk.CTkToplevel(self)
        dlg.title(self.t("tut_title"))
        dlg.geometry("640x600")
        dlg.resizable(False, False)
        dlg.transient(self)
        dlg.grab_set()
        dlg.configure(fg_color=BG_MAIN)
        
        # Encabezado del Tutorial
        top_hdr = ctk.CTkFrame(dlg, fg_color=CARD_BG, corner_radius=0, height=54, border_width=1, border_color=CARD_BORDER)
        top_hdr.pack(fill="x", side="top")
        
        ctk.CTkLabel(
            top_hdr, 
            text=f"📖  {self.t('tut_title')}", 
            font=ctk.CTkFont(size=14, weight="bold"), 
            text_color=ACCENT_CYAN
        ).pack(side="left", padx=20, pady=12)
        
        # Scroll con los 5 pasos ilustrados
        scroll_tut = ctk.CTkScrollableFrame(dlg, fg_color="transparent")
        scroll_tut.pack(fill="both", expand=True, padx=20, pady=12)
        
        steps = [
            ("🎬", self.t("tut_step1_title"), self.t("tut_step1_desc"), ACCENT_BLUE),
            ("👤", self.t("tut_step2_title"), self.t("tut_step2_desc"), "#38bdf8"),
            ("🎙️", self.t("tut_step3_title"), self.t("tut_step3_desc"), "#f59e0b"),
            ("⚡", self.t("tut_step4_title"), self.t("tut_step4_desc"), ACCENT_GREEN),
            ("✂️", self.t("tut_step5_title"), self.t("tut_step5_desc"), ACCENT_PURPLE)
        ]
        
        for icon, title, desc, color in steps:
            card = ctk.CTkFrame(scroll_tut, fg_color=CARD_BG, corner_radius=8, border_width=1, border_color=CARD_BORDER)
            card.pack(fill="x", pady=6)
            
            c_hdr = ctk.CTkFrame(card, fg_color="transparent")
            c_hdr.pack(fill="x", padx=14, pady=(12, 4))
            
            ctk.CTkLabel(
                c_hdr, 
                text=f"{icon}  {title}", 
                font=ctk.CTkFont(size=12, weight="bold"), 
                text_color=color
            ).pack(side="left")
            
            ctk.CTkLabel(
                card, 
                text=desc, 
                font=ctk.CTkFont(size=11), 
                text_color=TEXT_LIGHT,
                justify="left",
                wraplength=550
            ).pack(anchor="w", padx=14, pady=(0, 12))
            
        # Botón de cerrar
        btn_close = ctk.CTkButton(
            dlg, 
            text=self.t("tut_btn_close"), 
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=ACCENT_GREEN, 
            hover_color=ACCENT_GREEN_H,
            text_color="#ffffff",
            height=36,
            corner_radius=6,
            command=dlg.destroy
        )
        btn_close.pack(fill="x", padx=20, pady=(0, 16))

    # =================================================================
    # CAMBIO DINÁMICO DE IDIOMA
    # =================================================================
    def change_language(self, choice):
        self.current_lang = "es" if "Español" in choice else "en"
        
        self.btn_top_help.configure(text=self.t("btn_help"))
        self.lbl_queue_hdr.configure(text=self.t("queue_title"))
        self.btn_add_files.configure(text=self.t("add_files"))
        self.btn_add_folder.configure(text=self.t("add_folder"))
        self.lbl_tracking.configure(text=self.t("tracking_label"))
        self.chk_detect_audio.configure(text=self.t("audio_hype"))
        self.chk_filter_beta.configure(text=self.t("filter_beta"))
        self.btn_start.configure(text=self.t("btn_start"))
        self.btn_stop.configure(text=self.t("btn_stop"))
        
        self.lbl_events_hdr.configure(text=self.t("events_title"))
        self.lbl_preview_hdr.configure(text=self.t("preview_title"))
        self.btn_cut_this.configure(text=self.t("btn_cut_this"))
        self.btn_preview_sec.configure(text=self.t("btn_play_seek"))
        self.btn_batch.configure(text=self.t("btn_batch"))
        self.btn_html.configure(text=self.t("btn_html"))
        self.btn_open_video.configure(text=self.t("btn_open_full"))
        
        self.update_table_headers()
        self.refresh_video_list()

    def update_table_headers(self):
        self.tree.heading("time", text=self.t("col_time"))
        self.tree.heading("killer", text=self.t("col_killer"))
        self.tree.heading("dist", text=self.t("col_dist"))
        self.tree.heading("victim", text=self.t("col_target"))
        self.tree.heading("play", text=self.t("col_play"))
        self.tree.heading("hype", text=self.t("col_hype"))

    # =================================================================
    # GESTIÓN DE ARCHIVOS
    # =================================================================
    def add_folder(self):
        folder = filedialog.askdirectory(initialdir=r"E:\Videos OBS")
        if folder:
            self.load_videos_from_folder(folder)
            
    def load_videos_from_folder(self, folder):
        files = sorted(glob.glob(os.path.join(folder, "*.mp4")) + glob.glob(os.path.join(folder, "*.mkv")))
        for f in files:
            if f not in self.video_list and os.path.getsize(f) > 5 * 1024 * 1024:
                self.video_list.append(f)
        self.refresh_video_list()
        
    def add_files(self):
        files = filedialog.askopenfilenames(initialdir=r"E:\Videos OBS", filetypes=[("Videos", "*.mp4 *.mkv *.mov *.avi")])
        if files:
            for f in files:
                if f not in self.video_list:
                    self.video_list.append(f)
            self.refresh_video_list()
            
    def clear_videos(self):
        self.video_list = []
        self.refresh_video_list()
        
    def refresh_video_list(self):
        for widget in self.scroll_videos.winfo_children():
            widget.destroy()
            
        if not self.video_list:
            self.lbl_empty_queue = ctk.CTkLabel(
                self.scroll_videos, 
                text=self.t("empty_queue"), 
                font=ctk.CTkFont(size=11),
                text_color=TEXT_MUTED
            )
            self.lbl_empty_queue.pack(pady=40)
            return
            
        for vpath in self.video_list:
            vname = os.path.basename(vpath)
            size_mb = os.path.getsize(vpath) / (1024 * 1024)
            
            row = ctk.CTkFrame(self.scroll_videos, fg_color=CARD_BG, corner_radius=4, border_width=1, border_color=CARD_BORDER)
            row.pack(fill="x", pady=2, padx=2)
            
            lbl = ctk.CTkLabel(row, text=f"🎬  {vname} ({size_mb:.1f} MB)", font=ctk.CTkFont(size=11), anchor="w", text_color=TEXT_WHITE)
            lbl.pack(side="left", padx=8, pady=4)
            
            btn_del = ctk.CTkButton(
                row, text="✕", width=22, height=22, fg_color=INNER_BG, hover_color=ACCENT_RED,
                text_color=TEXT_MUTED, corner_radius=3,
                command=lambda p=vpath: self.remove_video(p)
            )
            btn_del.pack(side="right", padx=6)
            
    def remove_video(self, vpath):
        if vpath in self.video_list:
            self.video_list.remove(vpath)
            self.refresh_video_list()

    def get_output_dir(self):
        out_dir = getattr(self, "custom_out_dir", r"E:\Videos OBS\Clips_Generados")
        out_dir = os.path.abspath(out_dir)
        os.makedirs(out_dir, exist_ok=True)
        return out_dir

    def get_unique_filepath(self, target_dir, base_name, ext=".mp4"):
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

    def get_video_duration(self, video_path):
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

    # =================================================================
    # AUDIO SCORING & HYPE
    # =================================================================
    def analyze_audio_peaks(self, video_path):
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

    def get_hype_score(self, kill_sec, audio_energies, is_multikill):
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

    # =================================================================
    # RENDERIZADO GPU SEGURO
    # =================================================================
    def render_clip_file_safely(self, vpath, start_t, duration, out_filepath, is_vertical=False):
        out_filepath = os.path.abspath(out_filepath)
        os.makedirs(os.path.dirname(out_filepath), exist_ok=True)
        ffmpeg_bin = get_binary_path("ffmpeg")
        
        if is_vertical:
            filter_v = "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5[bg];[0:v]scale=1080:608[fg];[bg][fg]overlay=0:656"
            cmd = [
                ffmpeg_bin, "-y", "-ss", str(start_t), "-i", vpath,
                "-t", str(duration),
                "-filter_complex", filter_v,
                "-c:v", "h264_nvenc", "-preset", "p4", "-b:v", "5M",
                "-c:a", "aac", "-b:a", "192k", out_filepath
            ]
        else:
            cmd = [
                ffmpeg_bin, "-y", "-ss", str(start_t), "-i", vpath,
                "-t", str(duration),
                "-c:v", "h264_nvenc", "-preset", "p4", "-b:v", "6M",
                "-c:a", "aac", "-b:a", "192k", out_filepath
            ]
            
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=NO_WINDOW_FLAGS)
        
        # Fallback de CPU
        if not os.path.exists(out_filepath) or os.path.getsize(out_filepath) < 1000:
            if is_vertical:
                filter_v = "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5[bg];[0:v]scale=1080:608[fg];[bg][fg]overlay=0:656"
                cmd_cpu = [
                    ffmpeg_bin, "-y", "-ss", str(start_t), "-i", vpath,
                    "-t", str(duration),
                    "-filter_complex", filter_v,
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                    "-c:a", "aac", out_filepath
                ]
            else:
                cmd_cpu = [
                    ffmpeg_bin, "-y", "-ss", str(start_t), "-i", vpath,
                    "-t", str(duration),
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                    "-c:a", "aac", out_filepath
                ]
            subprocess.run(cmd_cpu, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=NO_WINDOW_FLAGS)
            
        return os.path.exists(out_filepath) and os.path.getsize(out_filepath) > 1000

    # =================================================================
    # ESCANEO DE KILLFEED
    # =================================================================
    def is_watermark_present(self, texts):
        if not self.chk_filter_beta.get():
            return False
        full = " ".join(texts).lower()
        wm_tokens = ['wardogs', 'beta', '7656', 'aug 21', 'cl-49', 'live-cl', '11866', 'aug21', '7866', 'cl49']
        return any(t in full for t in wm_tokens)

    def parse_killfeed_line(self, texts, user_clean_tags):
        line_str = " | ".join(texts)
        dist_match = re.search(r'\[?(\d+)\s*m\]?', line_str, re.IGNORECASE)
        distance = f"[{dist_match.group(1)}m]" if dist_match else "Distancia media"
        
        killer = "Tú"
        victim = "Enemigo"
        
        parts = [t.strip() for t in texts if t.strip()]
        if len(parts) >= 2:
            killer = parts[0]
            victim = parts[-1]
            for p in parts[1:-1]:
                if any(tag in re.sub(r'[^a-zA-Z0-9]', '', p.lower()) for tag in user_clean_tags):
                    killer = p
                    
        return killer, distance, victim

    def start_scan(self):
        if not self.video_list:
            messagebox.showwarning("Atención", self.t("empty_queue"))
            return
            
        raw_gamertags = self.ent_gamertags.get().strip()
        if not raw_gamertags:
            messagebox.showwarning("Atención", self.t("tracking_label"))
            return
            
        self.is_running = True
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.all_kills_data = []
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        self.lbl_status_progress.configure(text=self.t("scanning"))
        threading.Thread(target=self.scan_thread, daemon=True).start()

    def stop_scan(self):
        self.is_running = False
        if self.current_process:
            try:
                self.current_process.terminate()
            except Exception:
                pass
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        self.lbl_status_progress.configure(text="Detenido")
        self.lbl_progress_detail.configure(text="Detenido por el usuario")

    def scan_thread(self):
        gamertags = [t.strip().lower() for t in self.ent_gamertags.get().split(",") if t.strip()]
        clean_gamertags = [re.sub(r'[^a-zA-Z0-9]', '', t) for t in gamertags]
        
        multi_window = 20
        total_videos = len(self.video_list)
        fps_rate = 0.66
        
        for v_idx, v_path in enumerate(self.video_list):
            if not self.is_running:
                break
                
            v_name = os.path.basename(v_path)
            duration_sec = self.get_video_duration(v_path)
            total_ts_str = str(timedelta(seconds=duration_sec)) if duration_sec > 0 else "--:--:--"
            
            audio_energies = []
            if self.chk_detect_audio.get():
                self.lbl_status_progress.configure(text=f"Analizando audio: {v_name}...")
                audio_energies = self.analyze_audio_peaks(v_path)
                
            crop_x, crop_y, crop_w, crop_h = 0, 310, 240, 85
            cmd = [
                get_binary_path("ffmpeg"), "-hwaccel", "cuda", "-i", v_path,
                "-vf", f"fps={fps_rate},crop={crop_w}:{crop_h}:{crop_x}:{crop_y}",
                "-f", "rawvideo", "-pix_fmt", "bgr24", "-v", "error", "pipe:1"
            ]
            
            try:
                self.current_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=NO_WINDOW_FLAGS)
            except Exception:
                cmd.pop(1); cmd.pop(1)
                self.current_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=NO_WINDOW_FLAGS)
                
            frame_len = crop_w * crop_h * 3
            idx = 0
            video_kills = []
            last_kill_sec = -999
            
            while self.is_running:
                raw = self.current_process.stdout.read(frame_len)
                if len(raw) < frame_len:
                    break
                    
                sec = int(idx * (1.0 / fps_rate))
                frame = np.frombuffer(raw, dtype=np.uint8).reshape((crop_h, crop_w, 3))
                
                if idx % 2 == 0 or (duration_sec > 0 and sec >= duration_sec):
                    cur_ts = str(timedelta(seconds=sec))
                    pct = int((sec / duration_sec) * 100) if duration_sec > 0 else 0
                    global_pct = ((v_idx + (sec / duration_sec if duration_sec > 0 else 0)) / total_videos)
                    self.progress_bar.set(global_pct)
                    self.lbl_progress_pct.configure(text=f"{int(global_pct * 100)}%")
                    self.lbl_progress_detail.configure(text=f"{cur_ts} / {total_ts_str}  [{v_idx+1}/{total_videos}]")
                    self.lbl_status_progress.configure(
                        text=f"Bajas: {len(self.all_kills_data)} | {v_name}"
                    )
                
                white_mask = cv2.inRange(frame, np.array([175, 175, 175]), np.array([255, 255, 255]))
                if cv2.countNonZero(white_mask) > 40:
                    res, _ = self.ocr(frame)
                    if res:
                        all_texts = [r[1] for r in res]
                        if not self.is_watermark_present(all_texts):
                            for item in res:
                                box, txt, score = item
                                clean = re.sub(r'[^a-zA-Z0-9]', '', txt.lower())
                                
                                matched = any(gt in clean for gt in clean_gamertags if len(gt) >= 3)
                                if matched:
                                    center_x = (box[0][0] + box[1][0]) / 2.0
                                    
                                    if center_x < 120:
                                        if sec - last_kill_sec >= 3.0:
                                            last_kill_sec = sec
                                            ts_str = str(timedelta(seconds=sec))
                                            
                                            killer, dist, victim = self.parse_killfeed_line(all_texts, clean_gamertags)
                                            
                                            kill_record = {
                                                "video_path": v_path,
                                                "video_name": v_name,
                                                "time_sec": sec,
                                                "timestamp": ts_str,
                                                "killer": killer,
                                                "distance": dist,
                                                "victim": victim,
                                                "feed_raw": " | ".join(all_texts),
                                                "frame_rgb": cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                                            }
                                            video_kills.append(kill_record)
                                            self.all_kills_data.append(kill_record)
                idx += 1
                
            try:
                self.current_process.stdout.close()
                self.current_process.wait()
            except Exception:
                pass
                
            if video_kills:
                current_streak = [video_kills[0]]
                for k in video_kills[1:]:
                    if k['time_sec'] - current_streak[-1]['time_sec'] <= multi_window:
                        current_streak.append(k)
                    else:
                        is_multi = len(current_streak) >= 2
                        streak_name = self.get_streak_name(len(current_streak))
                        for sk in current_streak:
                            sk['play_type'] = streak_name
                            sk['hype'] = self.get_hype_score(sk['time_sec'], audio_energies, is_multi)
                            self.add_table_row(sk)
                        current_streak = [k]
                        
                is_multi = len(current_streak) >= 2
                streak_name = self.get_streak_name(len(current_streak))
                for sk in current_streak:
                    sk['play_type'] = streak_name
                    sk['hype'] = self.get_hype_score(sk['time_sec'], audio_energies, is_multi)
                    self.add_table_row(sk)
                    
        self.progress_bar.set(1.0)
        self.lbl_progress_pct.configure(text="100%")
        self.lbl_progress_detail.configure(text=f"Total: {len(self.all_kills_data)} bajas")
        self.lbl_status_progress.configure(text=f"{self.t('scan_finished')} ({len(self.all_kills_data)} {self.t('kills_indexed')})")
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")

    def get_streak_name(self, count):
        if self.current_lang == "es":
            if count == 1: return "🎯 Baja Individual"
            elif count == 2: return "🔥 DOBLE BAJA"
            elif count == 3: return "🔥 TRIPLE BAJA"
            elif count == 4: return "💥 CUÁDRUPLE"
            else: return f"👑 RACHA DE {count}"
        else:
            if count == 1: return "🎯 Single Kill"
            elif count == 2: return "🔥 DOUBLE KILL"
            elif count == 3: return "🔥 TRIPLE KILL"
            elif count == 4: return "💥 QUAD KILL"
            else: return f"👑 STREAK ({count})"

    def add_table_row(self, k):
        self.tree.insert("", "end", values=(
            k['timestamp'],
            k['killer'],
            k['distance'],
            k['victim'],
            k.get('play_type', '🎯 Baja Individual'),
            k.get('hype', '⭐⭐⭐')
        ))

    # =================================================================
    # VISTA PREVIA
    # =================================================================
    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
            
        values = self.tree.item(selected[0])['values']
        timestamp = values[0]
        killer = values[1]
        distance = values[2]
        victim = values[3]
        play_type = values[4]
        hype = values[5]
        
        record = next((k for k in self.all_kills_data if k['timestamp'] == timestamp and k['victim'] == victim), None)
        if record:
            if "frame_rgb" in record:
                try:
                    img_arr = record['frame_rgb']
                    img_pil = Image.fromarray(img_arr)
                    img_pil = img_pil.resize((260, 92), Image.Resampling.LANCZOS)
                    
                    self.preview_image_ref = ImageTk.PhotoImage(img_pil)
                    self.lbl_preview_img.configure(image=self.preview_image_ref, text="")
                except Exception:
                    pass
                    
            self.lbl_preview_details.configure(
                text=f"{self.t('meta_file')} {record['video_name']}\n{self.t('meta_time')} {timestamp}\n{self.t('meta_play')} {play_type}\n{self.t('meta_dist')} {distance}\n{self.t('meta_target')} {victim}\n{self.t('meta_hype')} {hype}"
            )

    def get_selected_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Atención", "Selecciona una baja de la tabla para continuar.")
            return None
            
        values = self.tree.item(selected[0])['values']
        timestamp = values[0]
        victim = values[3]
        
        record = next((k for k in self.all_kills_data if k['timestamp'] == timestamp and k['victim'] == victim), None)
        return record

    def open_selected_video_at_time(self):
        record = self.get_selected_record()
        if not record:
            return
            
        vpath = record['video_path']
        start_sec = max(0, record['time_sec'] - 5)
        
        cmd = [get_binary_path("ffplay"), "-ss", str(start_sec), "-autoexit", vpath]
        try:
            subprocess.Popen(cmd, creationflags=NO_WINDOW_FLAGS)
        except Exception:
            os.startfile(vpath)

    def open_original_video_file(self):
        record = self.get_selected_record()
        if not record:
            return
        try:
            os.startfile(record['video_path'])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo: {str(e)}")

    # =================================================================
    # MODAL DE RECORTE INDIVIDUAL
    # =================================================================
    def open_single_cut_dialog(self):
        record = self.get_selected_record()
        if not record:
            return
            
        vname_clean = os.path.splitext(record['video_name'])[0]
        ts_clean = record['timestamp'].replace(':', '-')
        victim_clean = re.sub(r'[^a-zA-Z0-9]', '', record['victim'])
        dist_clean = record['distance'].replace('[','').replace(']','')
        default_clip_name = f"{vname_clean}_Baja_{ts_clean}_{victim_clean}_{dist_clean}"
        
        dlg = ctk.CTkToplevel(self)
        dlg.title(self.t("single_modal_title"))
        dlg.geometry("520x350")
        dlg.resizable(False, False)
        dlg.transient(self)
        dlg.grab_set()
        dlg.configure(fg_color=BG_MAIN)
        
        ctk.CTkLabel(
            dlg, 
            text=self.t("single_modal_title"), 
            font=ctk.CTkFont(size=14, weight="bold"), 
            text_color=ACCENT_CYAN
        ).pack(anchor="w", padx=24, pady=(20, 2))
        
        ctk.CTkLabel(
            dlg, 
            text=f"Jugada: {record['timestamp']} ({record['distance']}) — {record['victim']}", 
            font=ctk.CTkFont(size=11), 
            text_color=TEXT_LIGHT
        ).pack(anchor="w", padx=24, pady=(0, 14))
        
        # 1. Nombre
        ctk.CTkLabel(dlg, text=self.t("single_clip_name"), font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_WHITE).pack(anchor="w", padx=24, pady=(0, 2))
        ent_clip_name = ctk.CTkEntry(dlg, height=34, font=ctk.CTkFont(size=12), fg_color=INNER_BG, border_color=CARD_BORDER)
        ent_clip_name.insert(0, default_clip_name)
        ent_clip_name.pack(fill="x", padx=24, pady=(0, 12))
        
        # 2. Carpeta
        ctk.CTkLabel(dlg, text=self.t("single_dest_folder"), font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_WHITE).pack(anchor="w", padx=24, pady=(0, 2))
        path_box = ctk.CTkFrame(dlg, fg_color="transparent")
        path_box.pack(fill="x", padx=24, pady=(0, 16))
        
        ent_dest = ctk.CTkEntry(path_box, height=32, font=ctk.CTkFont(size=11), fg_color=INNER_BG, border_color=CARD_BORDER)
        ent_dest.insert(0, self.get_output_dir())
        ent_dest.pack(side="left", fill="x", expand=True, padx=(0, 6))
        
        def browse_modal():
            d = filedialog.askdirectory(initialdir=ent_dest.get().strip() or r"E:\Videos OBS")
            if d:
                d = os.path.abspath(d)
                ent_dest.delete(0, "end")
                ent_dest.insert(0, d)
                self.custom_out_dir = d
                
        btn_br = ctk.CTkButton(
            path_box, 
            text=self.t("btn_browse"), 
            width=80, 
            height=32, 
            fg_color=INNER_BG,
            hover_color=HOVER_BG,
            border_width=1,
            border_color=CARD_BORDER,
            text_color=TEXT_WHITE,
            command=browse_modal
        )
        btn_br.pack(side="right")
        
        # 3. Formatos
        btn_grid = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_grid.pack(fill="x", padx=24, pady=(0, 10))
        
        def execute_cut(format_choice):
            target_folder = os.path.abspath(ent_dest.get().strip())
            os.makedirs(target_folder, exist_ok=True)
            self.custom_out_dir = target_folder
            
            custom_name = ent_clip_name.get().strip() or default_clip_name
            dlg.destroy()
            self.perform_single_cut(record, format_choice, target_folder, custom_name)
            
        btn_h = ctk.CTkButton(
            btn_grid, 
            text=self.t("btn_h169"), 
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=ACCENT_BLUE, 
            hover_color=ACCENT_BLUE_H,
            height=36,
            command=lambda: execute_cut("16x9")
        )
        btn_h.pack(side="left", fill="x", expand=True, padx=(0, 4))
        
        btn_v = ctk.CTkButton(
            btn_grid, 
            text=self.t("btn_v916"), 
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=ACCENT_PURPLE, 
            hover_color=ACCENT_PURPLE_H,
            height=36,
            command=lambda: execute_cut("9x16")
        )
        btn_v.pack(side="left", fill="x", expand=True, padx=(0, 4))
        
        btn_both = ctk.CTkButton(
            btn_grid, 
            text=self.t("btn_both"), 
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=ACCENT_GREEN, 
            hover_color=ACCENT_GREEN_H,
            height=36,
            command=lambda: execute_cut("both")
        )
        btn_both.pack(side="left", fill="x", expand=True)

    def perform_single_cut(self, record, format_choice, target_folder, custom_name):
        def thread_task():
            vpath = record['video_path']
            start_t = max(0, record['time_sec'] - 7)
            duration = 14
            last_created = None
            
            if format_choice in ["16x9", "both"]:
                suffix = "_16x9" if format_choice == "both" else ""
                out_h = self.get_unique_filepath(target_folder, f"{custom_name}{suffix}")
                ok = self.render_clip_file_safely(vpath, start_t, duration, out_h, is_vertical=False)
                if ok: last_created = out_h
                    
            if format_choice in ["9x16", "both"]:
                suffix = "_Shorts_9x16" if format_choice == "both" else ""
                out_v = self.get_unique_filepath(target_folder, f"{custom_name}{suffix}")
                ok = self.render_clip_file_safely(vpath, start_t, duration, out_v, is_vertical=True)
                if ok: last_created = out_v
                    
            if last_created and os.path.exists(last_created):
                messagebox.showinfo("AutoClip", f"{self.t('export_success')}\n\n📁 {target_folder}\n🎬 {os.path.basename(last_created)}")
                try:
                    subprocess.Popen(f'explorer /select,"{os.path.abspath(last_created)}"', creationflags=NO_WINDOW_FLAGS)
                except Exception:
                    os.startfile(target_folder)
            else:
                messagebox.showerror("Error", f"No se pudo guardar el clip en:\n{target_folder}")
                    
        threading.Thread(target=thread_task, daemon=True).start()

    # =================================================================
    # MODAL DE RECORTE MASIVO
    # =================================================================
    def open_batch_export_dialog(self):
        if not self.all_kills_data:
            messagebox.showwarning("Atención", "No hay bajas detectadas para exportar.")
            return
            
        dlg = ctk.CTkToplevel(self)
        dlg.title(self.t("batch_modal_title"))
        dlg.geometry("500x300")
        dlg.resizable(False, False)
        dlg.transient(self)
        dlg.grab_set()
        dlg.configure(fg_color=BG_MAIN)
        
        ctk.CTkLabel(
            dlg, 
            text=self.t("batch_modal_title"), 
            font=ctk.CTkFont(size=14, weight="bold"), 
            text_color=ACCENT_CYAN
        ).pack(anchor="w", padx=24, pady=(18, 2))
        
        ctk.CTkLabel(dlg, text=f"{len(self.all_kills_data)} bajas listas para renderizar por GPU", font=ctk.CTkFont(size=11), text_color=TEXT_LIGHT).pack(anchor="w", padx=24, pady=(0, 12))
        
        # Modo
        ctk.CTkLabel(dlg, text=self.t("batch_mode"), font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_WHITE).pack(anchor="w", padx=24, pady=(0, 2))
        mode_seg = ctk.CTkSegmentedButton(
            dlg, 
            values=[self.t("batch_sep"), self.t("batch_montage"), self.t("batch_both")],
            height=32,
            fg_color=INNER_BG,
            selected_color=ACCENT_BLUE,
            selected_hover_color=ACCENT_BLUE_H
        )
        mode_seg.set(self.t("batch_both"))
        mode_seg.pack(fill="x", padx=24, pady=(0, 12))
        
        # Carpeta
        path_box = ctk.CTkFrame(dlg, fg_color="transparent")
        path_box.pack(fill="x", padx=24, pady=(0, 16))
        
        ent_dest = ctk.CTkEntry(path_box, height=32, font=ctk.CTkFont(size=11), fg_color=INNER_BG, border_color=CARD_BORDER)
        ent_dest.insert(0, self.get_output_dir())
        ent_dest.pack(side="left", fill="x", expand=True, padx=(0, 6))
        
        def browse_batch():
            d = filedialog.askdirectory(initialdir=ent_dest.get().strip() or r"E:\Videos OBS")
            if d:
                d = os.path.abspath(d)
                ent_dest.delete(0, "end")
                ent_dest.insert(0, d)
                self.custom_out_dir = d
                
        btn_br = ctk.CTkButton(
            path_box, text=self.t("btn_browse"), width=80, height=32,
            fg_color=INNER_BG, hover_color=HOVER_BG, border_width=1, border_color=CARD_BORDER,
            text_color=TEXT_WHITE, command=browse_batch
        )
        btn_br.pack(side="right")
        
        def start_batch():
            out_dir = os.path.abspath(ent_dest.get().strip())
            mode_choice = mode_seg.get()
            dlg.destroy()
            threading.Thread(target=self.batch_export_thread, args=(out_dir, mode_choice), daemon=True).start()
            
        btn_run = ctk.CTkButton(
            dlg, 
            text=self.t("btn_run_batch"), 
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=ACCENT_GREEN, 
            hover_color=ACCENT_GREEN_H, 
            text_color="#ffffff",
            height=38,
            command=start_batch
        )
        btn_run.pack(fill="x", padx=24, pady=(0, 10))

    def batch_export_thread(self, out_dir, mode_choice):
        os.makedirs(out_dir, exist_ok=True)
        
        do_separate = ("Separados" in mode_choice) or ("Separate" in mode_choice) or ("Ambos" in mode_choice) or ("Both" in mode_choice)
        do_montage = ("Montaje" in mode_choice) or ("Montage" in mode_choice) or ("Ambos" in mode_choice) or ("Both" in mode_choice)
        
        total = len(self.all_kills_data)
        h_clips = []
        
        for idx, k in enumerate(self.all_kills_data):
            vpath = k['video_path']
            vname = os.path.splitext(k['video_name'])[0]
            ts_str = k['timestamp'].replace(":", "-")
            start_t = max(0, k['time_sec'] - 7)
            duration = 14
            
            clean_victim = re.sub(r'[^a-zA-Z0-9]', '', k['victim'])
            clean_dist = k['distance'].replace('[','').replace(']','')
            base_name = f"{vname}_Baja_{ts_str}_{clean_victim}_{clean_dist}"
            
            self.lbl_status_progress.configure(text=f"Exportando [{idx+1}/{total}]: {k['timestamp']}")
            
            out_h = self.get_unique_filepath(out_dir, f"{base_name}_16x9")
            ok = self.render_clip_file_safely(vpath, start_t, duration, out_h, is_vertical=False)
            if ok:
                h_clips.append(out_h)
                
        if do_montage and h_clips:
            self.lbl_status_progress.configure(text="Generando vídeo recopilatorio de Highlights...")
            concat_list = os.path.join(out_dir, "temp_concat.txt")
            with open(concat_list, "w", encoding="utf-8") as f:
                for cp in h_clips:
                    f.write(f"file '{os.path.abspath(cp)}'\n")
                    
            master_montage = self.get_unique_filepath(out_dir, "MONTAJE_HIGHLIGHTS_16x9")
            cmd = [get_binary_path("ffmpeg"), "-y", "-f", "concat", "-safe", "0", "-i", concat_list, "-c", "copy", master_montage]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=NO_WINDOW_FLAGS)
            try: os.remove(concat_list)
            except Exception: pass
            
        self.lbl_status_progress.configure(text=f"¡Exportación finalizada! Guardado en: {out_dir}")
        messagebox.showinfo("AutoClip Studio", f"¡Exportación completada con éxito!\n\nCarpeta:\n{out_dir}")
        try: os.startfile(out_dir)
        except Exception: pass

    # =================================================================
    # REPORTE HTML
    # =================================================================
    def export_html_report(self):
        if not self.all_kills_data:
            messagebox.showwarning("Atención", "No hay datos de bajas para exportar.")
            return
            
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.exists(downloads_folder):
            downloads_folder = r"E:\Videos OBS"
            
        out_file = os.path.join(downloads_folder, "reporte_bajas_Wardogs_ICayon.html")
            
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
        <div class="card-val">{len(self.all_kills_data)}</div>
        <div class="card-lbl">Total Bajas Detectadas</div>
    </div>
    <div class="card">
        <div class="card-val">{len([k for k in self.all_kills_data if "BAJA" in k.get("play_type", "") or "KILL" in k.get("play_type", "")])}</div>
        <div class="card-lbl">Multikills / Rachas</div>
    </div>
    <div class="card">
        <div class="card-val">{len([k for k in self.all_kills_data if "⭐⭐⭐⭐" in k.get("hype", "")])}</div>
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
"""
        for k in self.all_kills_data:
            html += f"""<tr>
<td>{k['video_name']}</td>
<td><strong style="color: #38bdf8;">{k['timestamp']}</strong></td>
<td>{k['killer']}</td>
<td>{k['distance']}</td>
<td>{k['victim']}</td>
<td><span class="tag">{k.get('play_type', '🎯 Baja')}</span></td>
<td>{k.get('hype', '⭐⭐⭐')}</td>
</tr>"""
        html += "</tbody></table></body></html>"
        
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(html)
            
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        if os.path.exists(chrome_path):
            try:
                subprocess.Popen([chrome_path, out_file], creationflags=NO_WINDOW_FLAGS)
            except Exception:
                import webbrowser
                webbrowser.open(f"file:///{os.path.abspath(out_file).replace(chr(92), '/')}")
        else:
            import webbrowser
            webbrowser.open(f"file:///{os.path.abspath(out_file).replace(chr(92), '/')}")


if __name__ == "__main__":
    app = AutoClipWardogsApp()
    app.mainloop()
