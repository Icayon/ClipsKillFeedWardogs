import os
import glob
from tkinter import filedialog, messagebox
import customtkinter as ctk
from ..theme import (
    CARD_BG, CARD_BORDER, INNER_BG, HOVER_BG, TEXT_WHITE, 
    TEXT_MUTED, ACCENT_BLUE, ACCENT_BLUE_H, ACCENT_GREEN, 
    ACCENT_GREEN_H, ACCENT_RED, ACCENT_RED_H
)

class QueuePanel(ctk.CTkFrame):
    def __init__(self, parent, translator, on_start, on_stop, on_help_gamertag):
        super().__init__(parent, fg_color=CARD_BG, corner_radius=8, width=320, border_width=1, border_color=CARD_BORDER)
        self.pack(side="left", fill="y", padx=(18, 10), pady=16)
        self.pack_propagate(False)
        self.t = translator
        self.on_start = on_start
        self.on_stop = on_stop
        self.on_help_gamertag = on_help_gamertag
        self.video_list = []
        self._build_ui()
        
    def _build_ui(self):
        # Cabecera
        q_hdr = ctk.CTkFrame(self, fg_color="transparent")
        q_hdr.pack(fill="x", padx=16, pady=(16, 8))
        
        self.lbl_queue_hdr = ctk.CTkLabel(
            q_hdr, text=self.t("queue_title"), 
            font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_WHITE
        )
        self.lbl_queue_hdr.pack(side="left")
        
        btn_clear = ctk.CTkButton(
            q_hdr, text=self.t("clear_queue"), width=60, height=26,
            fg_color=INNER_BG, hover_color=HOVER_BG, text_color=TEXT_MUTED,
            border_width=1, border_color=CARD_BORDER, font=ctk.CTkFont(size=10),
            command=self.clear_videos
        )
        btn_clear.pack(side="right")
        
        # Botones añadir
        btn_box = ctk.CTkFrame(self, fg_color="transparent")
        btn_box.pack(fill="x", padx=16, pady=(0, 10))
        
        self.btn_add_files = ctk.CTkButton(
            btn_box, text=self.t("add_files"), height=30,
            fg_color=INNER_BG, hover_color=HOVER_BG, border_width=1, border_color=CARD_BORDER,
            text_color=TEXT_WHITE, font=ctk.CTkFont(size=11),
            command=self.add_files
        )
        self.btn_add_files.pack(side="left", fill="x", expand=True, padx=(0, 4))
        
        self.btn_add_folder = ctk.CTkButton(
            btn_box, text=self.t("add_folder"), height=30,
            fg_color=INNER_BG, hover_color=HOVER_BG, border_width=1, border_color=CARD_BORDER,
            text_color=TEXT_WHITE, font=ctk.CTkFont(size=11),
            command=self.add_folder
        )
        self.btn_add_folder.pack(side="left", fill="x", expand=True)
        
        # Scroll vídeos
        self.scroll_videos = ctk.CTkScrollableFrame(self, fg_color=INNER_BG, corner_radius=6, border_width=1, border_color=CARD_BORDER)
        self.scroll_videos.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        
        # Gamertag & Opciones
        conf_box = ctk.CTkFrame(self, fg_color="transparent")
        conf_box.pack(fill="x", padx=16, pady=(0, 12))
        
        tag_lbl_row = ctk.CTkFrame(conf_box, fg_color="transparent")
        tag_lbl_row.pack(fill="x", pady=(0, 4))
        
        self.lbl_tracking = ctk.CTkLabel(tag_lbl_row, text=self.t("tracking_label"), font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_WHITE)
        self.lbl_tracking.pack(side="left")
        
        ctk.CTkButton(
            tag_lbl_row, text="?", width=20, height=20,
            fg_color=INNER_BG, hover_color=HOVER_BG, border_width=1, border_color=CARD_BORDER,
            text_color="#38bdf8", font=ctk.CTkFont(size=11, weight="bold"), corner_radius=10,
            command=self.on_help_gamertag
        ).pack(side="left", padx=6)
        
        self.ent_gamertags = ctk.CTkEntry(conf_box, placeholder_text="ej: ICayon, [ESP] ICayon", height=32, font=ctk.CTkFont(size=11), fg_color=INNER_BG, border_color=CARD_BORDER)
        self.ent_gamertags.insert(0, "ICayon, [ESP] ICayon, ICayonh")
        self.ent_gamertags.pack(fill="x", pady=(0, 8))
        
        self.chk_detect_audio = ctk.CTkCheckBox(conf_box, text=self.t("audio_hype"), font=ctk.CTkFont(size=11), text_color=TEXT_WHITE, fg_color=ACCENT_BLUE)
        self.chk_detect_audio.select()
        self.chk_detect_audio.pack(anchor="w", pady=2)
        
        self.chk_filter_beta = ctk.CTkCheckBox(conf_box, text=self.t("filter_beta"), font=ctk.CTkFont(size=11), text_color=TEXT_WHITE, fg_color=ACCENT_BLUE)
        self.chk_filter_beta.select()
        self.chk_filter_beta.pack(anchor="w", pady=2)
        
        # Botones acción
        act_box = ctk.CTkFrame(self, fg_color="transparent")
        act_box.pack(fill="x", padx=16, pady=(0, 16))
        
        self.btn_start = ctk.CTkButton(
            act_box, text=self.t("btn_start"), height=36, font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=ACCENT_GREEN, hover_color=ACCENT_GREEN_H, text_color="#ffffff",
            command=self.on_start
        )
        self.btn_start.pack(side="left", fill="x", expand=True, padx=(0, 4))
        
        self.btn_stop = ctk.CTkButton(
            act_box, text=self.t("btn_stop"), height=36, font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=ACCENT_RED, hover_color=ACCENT_RED_H, text_color="#ffffff", state="disabled",
            command=self.on_stop
        )
        self.btn_stop.pack(side="left", fill="x", expand=True)
        
        self.refresh_video_list()

    def add_folder(self):
        folder = filedialog.askdirectory(initialdir=r"E:\Videos OBS")
        if folder:
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
        
    def remove_video(self, vpath):
        if vpath in self.video_list:
            self.video_list.remove(vpath)
            self.refresh_video_list()
            
    def refresh_video_list(self):
        for widget in self.scroll_videos.winfo_children():
            widget.destroy()
            
        if not self.video_list:
            ctk.CTkLabel(
                self.scroll_videos, text=self.t("empty_queue"), 
                font=ctk.CTkFont(size=11), text_color=TEXT_MUTED
            ).pack(pady=40)
            return
            
        for vpath in self.video_list:
            vname = os.path.basename(vpath)
            size_mb = os.path.getsize(vpath) / (1024 * 1024)
            row = ctk.CTkFrame(self.scroll_videos, fg_color=CARD_BG, corner_radius=4, border_width=1, border_color=CARD_BORDER)
            row.pack(fill="x", pady=2, padx=2)
            
            ctk.CTkLabel(row, text=f"🎬  {vname} ({size_mb:.1f} MB)", font=ctk.CTkFont(size=11), anchor="w", text_color=TEXT_WHITE).pack(side="left", padx=8, pady=4)
            
            ctk.CTkButton(
                row, text="✕", width=22, height=22, fg_color=INNER_BG, hover_color=ACCENT_RED,
                text_color=TEXT_MUTED, corner_radius=3, command=lambda p=vpath: self.remove_video(p)
            ).pack(side="right", padx=6)
            
    def refresh_texts(self):
        self.lbl_queue_hdr.configure(text=self.t("queue_title"))
        self.btn_add_files.configure(text=self.t("add_files"))
        self.btn_add_folder.configure(text=self.t("add_folder"))
        self.lbl_tracking.configure(text=self.t("tracking_label"))
        self.chk_detect_audio.configure(text=self.t("audio_hype"))
        self.chk_filter_beta.configure(text=self.t("filter_beta"))
        self.btn_start.configure(text=self.t("btn_start"))
        self.btn_stop.configure(text=self.t("btn_stop"))
        self.refresh_video_list()