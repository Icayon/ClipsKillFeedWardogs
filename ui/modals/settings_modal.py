import os
from tkinter import filedialog
import customtkinter as ctk
from ..theme import (
    BG_MAIN, CARD_BG, CARD_BORDER, INNER_BG, HOVER_BG, ACCENT_BLUE, 
    ACCENT_GREEN, ACCENT_GREEN_H, ACCENT_CYAN, TEXT_WHITE, 
    TEXT_MUTED, TEXT_LIGHT
)

class SettingsModal(ctk.CTkToplevel):
    def __init__(self, parent, default_folder: str, use_gpu: bool, sec_before: int, sec_after: int, 
                 auto_open: bool, translator, on_save):
        super().__init__(parent)
        self.t = translator
        self.on_save = on_save
        
        self.use_gpu_var = ctk.BooleanVar(value=use_gpu)
        self.auto_open_var = ctk.BooleanVar(value=auto_open)
        self.sec_before_var = ctk.StringVar(value=f"{sec_before}s")
        self.sec_after_var = ctk.StringVar(value=f"{sec_after}s")
        
        self.title(self.t("settings_title"))
        self.geometry("540x510")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color=BG_MAIN)
        
        self._build_ui(default_folder)
        
    def _build_ui(self, default_folder):
        # 1. Header
        top_hdr = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=0, height=54, border_width=1, border_color=CARD_BORDER)
        top_hdr.pack(fill="x", side="top")
        
        ctk.CTkLabel(
            top_hdr, 
            text=self.t("settings_title"), 
            font=ctk.CTkFont(size=14, weight="bold"), 
            text_color=ACCENT_CYAN
        ).pack(side="left", padx=20, pady=12)
        
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=14)
        
        # 2. Carpeta de Descargas / Guardado
        card_dir = ctk.CTkFrame(content, fg_color=CARD_BG, corner_radius=8, border_width=1, border_color=CARD_BORDER)
        card_dir.pack(fill="x", pady=(0, 10))
        
        d_hdr = ctk.CTkFrame(card_dir, fg_color="transparent")
        d_hdr.pack(fill="x", padx=14, pady=(10, 4))
        
        ctk.CTkLabel(d_hdr, text=self.t("settings_folder_title"), font=ctk.CTkFont(size=11, weight="bold"), text_color=ACCENT_CYAN).pack(side="left")
        
        ctk.CTkLabel(card_dir, text=self.t("settings_folder_desc"), font=ctk.CTkFont(size=10), text_color=TEXT_MUTED).pack(anchor="w", padx=14, pady=(0, 6))
        
        path_row = ctk.CTkFrame(card_dir, fg_color="transparent")
        path_row.pack(fill="x", padx=14, pady=(0, 12))
        
        self.ent_folder = ctk.CTkEntry(path_row, height=32, font=ctk.CTkFont(size=11), fg_color=INNER_BG, border_color=CARD_BORDER)
        self.ent_folder.insert(0, default_folder)
        self.ent_folder.pack(side="left", fill="x", expand=True, padx=(0, 6))
        
        ctk.CTkButton(
            path_row, text=self.t("btn_browse"), width=80, height=32,
            fg_color=INNER_BG, hover_color=HOVER_BG, border_width=1, border_color=CARD_BORDER,
            text_color=TEXT_WHITE, font=ctk.CTkFont(size=11), command=self._browse_folder
        ).pack(side="right")
        
        # 3. GPU / Hardware
        card_hw = ctk.CTkFrame(content, fg_color=CARD_BG, corner_radius=8, border_width=1, border_color=CARD_BORDER)
        card_hw.pack(fill="x", pady=(0, 10))
        
        hw_hdr = ctk.CTkFrame(card_hw, fg_color="transparent")
        hw_hdr.pack(fill="x", padx=14, pady=(10, 4))
        ctk.CTkLabel(hw_hdr, text=self.t("settings_hardware_title"), font=ctk.CTkFont(size=11, weight="bold"), text_color=ACCENT_CYAN).pack(side="left")
        
        self.sw_gpu = ctk.CTkSwitch(
            card_hw, text=self.t("settings_gpu"), variable=self.use_gpu_var,
            font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_WHITE, progress_color=ACCENT_GREEN
        )
        self.sw_gpu.pack(anchor="w", padx=14, pady=(0, 4))
        
        ctk.CTkLabel(card_hw, text=self.t("settings_gpu_desc"), font=ctk.CTkFont(size=10), text_color=TEXT_MUTED).pack(anchor="w", padx=14, pady=(0, 12))
        
        # 4. Tiempos de Recorte de Jugadas
        card_time = ctk.CTkFrame(content, fg_color=CARD_BG, corner_radius=8, border_width=1, border_color=CARD_BORDER)
        card_time.pack(fill="x", pady=(0, 10))
        
        t_hdr = ctk.CTkFrame(card_time, fg_color="transparent")
        t_hdr.pack(fill="x", padx=14, pady=(10, 6))
        ctk.CTkLabel(t_hdr, text=self.t("settings_clips_title"), font=ctk.CTkFont(size=11, weight="bold"), text_color=ACCENT_CYAN).pack(side="left")
        
        row_timers = ctk.CTkFrame(card_time, fg_color="transparent")
        row_timers.pack(fill="x", padx=14, pady=(0, 8))
        
        # Antes
        ctk.CTkLabel(row_timers, text=self.t("settings_before"), font=ctk.CTkFont(size=11), text_color=TEXT_LIGHT).pack(side="left", padx=(0, 6))
        self.cmb_before = ctk.CTkOptionMenu(
            row_timers, values=["3s", "5s", "7s", "10s", "15s"], variable=self.sec_before_var,
            width=70, height=28, fg_color=INNER_BG, button_color=INNER_BG, button_hover_color=HOVER_BG,
            text_color=TEXT_WHITE, font=ctk.CTkFont(size=11), dropdown_fg_color=CARD_BG
        )
        self.cmb_before.pack(side="left", padx=(0, 20))
        
        # Después
        ctk.CTkLabel(row_timers, text=self.t("settings_after"), font=ctk.CTkFont(size=11), text_color=TEXT_LIGHT).pack(side="left", padx=(0, 6))
        self.cmb_after = ctk.CTkOptionMenu(
            row_timers, values=["3s", "5s", "7s", "10s"], variable=self.sec_after_var,
            width=70, height=28, fg_color=INNER_BG, button_color=INNER_BG, button_hover_color=HOVER_BG,
            text_color=TEXT_WHITE, font=ctk.CTkFont(size=11), dropdown_fg_color=CARD_BG
        )
        self.cmb_after.pack(side="left")
        
        # Auto-abrir carpeta
        self.chk_auto = ctk.CTkCheckBox(
            card_time, text=self.t("settings_auto_open"), variable=self.auto_open_var,
            font=ctk.CTkFont(size=11), text_color=TEXT_WHITE, fg_color=ACCENT_BLUE
        )
        self.chk_auto.pack(anchor="w", padx=14, pady=(4, 12))
        
        # 5. Botón Guardar
        btn_save = ctk.CTkButton(
            self, text=self.t("settings_save"), font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=ACCENT_GREEN, hover_color=ACCENT_GREEN_H, text_color="#ffffff",
            height=38, corner_radius=6, command=self._save_and_close
        )
        btn_save.pack(fill="x", padx=20, pady=(0, 16))

    def _browse_folder(self):
        d = filedialog.askdirectory(initialdir=self.ent_folder.get().strip() or os.path.join(os.path.expanduser("~"), "Downloads"))
        if d:
            self.ent_folder.delete(0, "end")
            self.ent_folder.insert(0, os.path.abspath(d))

    def _save_and_close(self):
        folder = os.path.abspath(self.ent_folder.get().strip())
        use_gpu = self.use_gpu_var.get()
        sec_before = int(self.sec_before_var.get().replace('s',''))
        sec_after = int(self.sec_after_var.get().replace('s',''))
        auto_open = self.auto_open_var.get()
        
        self.destroy()
        if self.on_save:
            self.on_save(folder, use_gpu, sec_before, sec_after, auto_open)