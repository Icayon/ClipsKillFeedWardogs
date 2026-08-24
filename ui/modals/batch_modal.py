import os
from tkinter import filedialog
import customtkinter as ctk
from ..theme import (
    BG_MAIN, CARD_BORDER, INNER_BG, HOVER_BG, ACCENT_CYAN, 
    ACCENT_BLUE, ACCENT_BLUE_H, ACCENT_GREEN, ACCENT_GREEN_H, 
    TEXT_WHITE, TEXT_LIGHT
)

class BatchExportModal(ctk.CTkToplevel):
    def __init__(self, parent, total_kills, default_out_dir, translator, on_start):
        super().__init__(parent)
        self.total_kills = total_kills
        self.default_out_dir = default_out_dir
        self.t = translator
        self.on_start = on_start
        
        self.title(self.t("batch_modal_title"))
        self.geometry("500x300")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color=BG_MAIN)
        
        self._build_ui()
        
    def _build_ui(self):
        ctk.CTkLabel(
            self, 
            text=self.t("batch_modal_title"), 
            font=ctk.CTkFont(size=14, weight="bold"), 
            text_color=ACCENT_CYAN
        ).pack(anchor="w", padx=24, pady=(18, 2))
        
        ctk.CTkLabel(
            self, 
            text=f"{self.total_kills} bajas listas para renderizar por GPU", 
            font=ctk.CTkFont(size=11), 
            text_color=TEXT_LIGHT
        ).pack(anchor="w", padx=24, pady=(0, 12))
        
        # Modo
        ctk.CTkLabel(self, text=self.t("batch_mode"), font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_WHITE).pack(anchor="w", padx=24, pady=(0, 2))
        self.mode_seg = ctk.CTkSegmentedButton(
            self, 
            values=[self.t("batch_sep"), self.t("batch_montage"), self.t("batch_both")],
            height=32,
            fg_color=INNER_BG,
            selected_color=ACCENT_BLUE,
            selected_hover_color=ACCENT_BLUE_H
        )
        self.mode_seg.set(self.t("batch_both"))
        self.mode_seg.pack(fill="x", padx=24, pady=(0, 12))
        
        # Carpeta
        path_box = ctk.CTkFrame(self, fg_color="transparent")
        path_box.pack(fill="x", padx=24, pady=(0, 16))
        
        self.ent_dest = ctk.CTkEntry(path_box, height=32, font=ctk.CTkFont(size=11), fg_color=INNER_BG, border_color=CARD_BORDER)
        self.ent_dest.insert(0, self.default_out_dir)
        self.ent_dest.pack(side="left", fill="x", expand=True, padx=(0, 6))
        
        ctk.CTkButton(
            path_box, 
            text=self.t("btn_browse"), 
            width=80, 
            height=32,
            fg_color=INNER_BG, 
            hover_color=HOVER_BG, 
            border_width=1, 
            border_color=CARD_BORDER,
            text_color=TEXT_WHITE, 
            command=self._browse
        ).pack(side="right")
        
        ctk.CTkButton(
            self, 
            text=self.t("btn_run_batch"), 
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=ACCENT_GREEN, 
            hover_color=ACCENT_GREEN_H, 
            text_color="#ffffff",
            height=38,
            command=self._run
        ).pack(fill="x", padx=24, pady=(0, 10))

    def _browse(self):
        d = filedialog.askdirectory(initialdir=self.ent_dest.get().strip() or r"E:\Videos OBS")
        if d:
            self.ent_dest.delete(0, "end")
            self.ent_dest.insert(0, os.path.abspath(d))

    def _run(self):
        out_dir = os.path.abspath(self.ent_dest.get().strip())
        mode_choice = self.mode_seg.get()
        self.destroy()
        if self.on_start:
            self.on_start(out_dir, mode_choice)