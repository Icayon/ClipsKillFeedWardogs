import os
import re
from tkinter import filedialog
import customtkinter as ctk
from ..theme import (
    BG_MAIN, CARD_BORDER, INNER_BG, HOVER_BG, ACCENT_CYAN, 
    ACCENT_BLUE, ACCENT_BLUE_H, ACCENT_PURPLE, ACCENT_PURPLE_H, 
    ACCENT_GREEN, ACCENT_GREEN_H, TEXT_WHITE, TEXT_LIGHT
)

class SingleCutModal(ctk.CTkToplevel):
    def __init__(self, parent, record, default_out_dir, translator, on_execute):
        super().__init__(parent)
        self.record = record
        self.t = translator
        self.default_out_dir = default_out_dir
        self.on_execute = on_execute
        
        self.title(self.t("single_modal_title"))
        self.geometry("520x350")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color=BG_MAIN)
        
        self._build_ui()
        
    def _build_ui(self):
        vname_clean = os.path.splitext(self.record.video_name)[0]
        ts_clean = self.record.timestamp.replace(':', '-')
        victim_clean = re.sub(r'[^a-zA-Z0-9]', '', self.record.victim)
        dist_clean = self.record.distance.replace('[','').replace(']','')
        self.default_clip_name = f"{vname_clean}_Baja_{ts_clean}_{victim_clean}_{dist_clean}"
        
        ctk.CTkLabel(
            self, 
            text=self.t("single_modal_title"), 
            font=ctk.CTkFont(size=14, weight="bold"), 
            text_color=ACCENT_CYAN
        ).pack(anchor="w", padx=24, pady=(20, 2))
        
        ctk.CTkLabel(
            self, 
            text=f"Jugada: {self.record.timestamp} ({self.record.distance}) — {self.record.victim}", 
            font=ctk.CTkFont(size=11), 
            text_color=TEXT_LIGHT
        ).pack(anchor="w", padx=24, pady=(0, 14))
        
        # 1. Nombre
        ctk.CTkLabel(self, text=self.t("single_clip_name"), font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_WHITE).pack(anchor="w", padx=24, pady=(0, 2))
        self.ent_clip_name = ctk.CTkEntry(self, height=34, font=ctk.CTkFont(size=12), fg_color=INNER_BG, border_color=CARD_BORDER)
        self.ent_clip_name.insert(0, self.default_clip_name)
        self.ent_clip_name.pack(fill="x", padx=24, pady=(0, 12))
        
        # 2. Carpeta
        ctk.CTkLabel(self, text=self.t("single_dest_folder"), font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_WHITE).pack(anchor="w", padx=24, pady=(0, 2))
        path_box = ctk.CTkFrame(self, fg_color="transparent")
        path_box.pack(fill="x", padx=24, pady=(0, 16))
        
        self.ent_dest = ctk.CTkEntry(path_box, height=32, font=ctk.CTkFont(size=11), fg_color=INNER_BG, border_color=CARD_BORDER)
        self.ent_dest.insert(0, self.default_out_dir)
        self.ent_dest.pack(side="left", fill="x", expand=True, padx=(0, 6))
        
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
            command=self._browse
        )
        btn_br.pack(side="right")
        
        # 3. Botones de formato
        btn_grid = ctk.CTkFrame(self, fg_color="transparent")
        btn_grid.pack(fill="x", padx=24, pady=(0, 10))
        
        ctk.CTkButton(
            btn_grid, 
            text=self.t("btn_h169"), 
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=ACCENT_BLUE, 
            hover_color=ACCENT_BLUE_H,
            height=36,
            command=lambda: self._execute("16x9")
        ).pack(side="left", fill="x", expand=True, padx=(0, 4))
        
        ctk.CTkButton(
            btn_grid, 
            text=self.t("btn_v916"), 
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=ACCENT_PURPLE, 
            hover_color=ACCENT_PURPLE_H,
            height=36,
            command=lambda: self._execute("9x16")
        ).pack(side="left", fill="x", expand=True, padx=(0, 4))
        
        ctk.CTkButton(
            btn_grid, 
            text=self.t("btn_both"), 
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=ACCENT_GREEN, 
            hover_color=ACCENT_GREEN_H,
            height=36,
            command=lambda: self._execute("both")
        ).pack(side="left", fill="x", expand=True)

    def _browse(self):
        d = filedialog.askdirectory(initialdir=self.ent_dest.get().strip() or r"E:\Videos OBS")
        if d:
            self.ent_dest.delete(0, "end")
            self.ent_dest.insert(0, os.path.abspath(d))

    def _execute(self, format_choice):
        target_folder = os.path.abspath(self.ent_dest.get().strip())
        custom_name = self.ent_clip_name.get().strip() or self.default_clip_name
        self.destroy()
        if self.on_execute:
            self.on_execute(self.record, format_choice, target_folder, custom_name)