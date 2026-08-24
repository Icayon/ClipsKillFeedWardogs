import os
import re
from tkinter import filedialog, messagebox
import customtkinter as ctk
from .info_modal import InfoModal
from ..theme import (
    BG_MAIN, CARD_BG, CARD_BORDER, INNER_BG, HOVER_BG, 
    ACCENT_CYAN, ACCENT_BLUE, ACCENT_BLUE_H, ACCENT_GREEN, 
    ACCENT_GREEN_H, TEXT_WHITE, TEXT_MUTED, TEXT_LIGHT
)

class SettingsModal(ctk.CTkToplevel):
    def __init__(self, parent, current_out_dir, current_gpu_mode, current_sec_before, 
                 current_sec_after, current_multikill_window, current_group_multikills,
                 current_auto_open, translator, on_save):
        super().__init__(parent)
        self.t = translator
        self.current_out_dir = current_out_dir
        self.current_gpu_mode = current_gpu_mode
        self.current_sec_before = current_sec_before
        self.current_sec_after = current_sec_after
        self.current_multikill_window = current_multikill_window
        self.current_group_multikills = current_group_multikills
        self.current_auto_open = current_auto_open
        self.on_save = on_save
        
        self.title(self.t("settings_title"))
        self.geometry("630x700")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color=BG_MAIN)
        
        self._build_ui()
        
    def _create_help_btn(self, parent, title_key, desc_key):
        return ctk.CTkButton(
            parent, text="?", width=18, height=18,
            fg_color=INNER_BG, hover_color=HOVER_BG, border_width=1, border_color=CARD_BORDER,
            text_color="#38bdf8", font=ctk.CTkFont(size=11, weight="bold"), corner_radius=9,
            command=lambda: InfoModal(self, self.t(title_key), self.t(desc_key))
        )
        
    def _build_ui(self):
        top_hdr = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=0, height=54, border_width=1, border_color=CARD_BORDER)
        top_hdr.pack(fill="x", side="top")
        
        ctk.CTkLabel(
            top_hdr, 
            text=self.t("settings_title"), 
            font=ctk.CTkFont(size=14, weight="bold"), 
            text_color=ACCENT_CYAN
        ).pack(side="left", padx=24, pady=12)
        
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=12)
        
        # 1. Carpeta de Guardado
        card_dir = ctk.CTkFrame(scroll, fg_color=CARD_BG, corner_radius=8, border_width=1, border_color=CARD_BORDER)
        card_dir.pack(fill="x", pady=6)
        
        row_dir_hdr = ctk.CTkFrame(card_dir, fg_color="transparent")
        row_dir_hdr.pack(fill="x", padx=16, pady=(12, 2))
        ctk.CTkLabel(row_dir_hdr, text=self.t("settings_folder_title"), font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_WHITE).pack(side="left")
        self._create_help_btn(row_dir_hdr, "help_folder_title", "help_folder_desc").pack(side="left", padx=6)
        
        ctk.CTkLabel(card_dir, text=self.t("settings_folder_desc"), font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).pack(anchor="w", padx=16, pady=(0, 8))
        
        path_box = ctk.CTkFrame(card_dir, fg_color="transparent")
        path_box.pack(fill="x", padx=16, pady=(0, 14))
        
        self.ent_dir = ctk.CTkEntry(path_box, height=34, font=ctk.CTkFont(size=11), fg_color=INNER_BG, border_color=CARD_BORDER)
        self.ent_dir.insert(0, self.current_out_dir)
        self.ent_dir.pack(side="left", fill="x", expand=True, padx=(0, 6))
        
        ctk.CTkButton(
            path_box, text=self.t("btn_browse"), width=85, height=34,
            fg_color=INNER_BG, hover_color=HOVER_BG, border_width=1, border_color=CARD_BORDER,
            text_color=TEXT_WHITE, font=ctk.CTkFont(size=11),
            command=self._browse_dir
        ).pack(side="right")
        
        # 2. Hardware / GPU
        card_hw = ctk.CTkFrame(scroll, fg_color=CARD_BG, corner_radius=8, border_width=1, border_color=CARD_BORDER)
        card_hw.pack(fill="x", pady=6)
        
        row_hw_hdr = ctk.CTkFrame(card_hw, fg_color="transparent")
        row_hw_hdr.pack(fill="x", padx=16, pady=(12, 4))
        ctk.CTkLabel(row_hw_hdr, text=self.t("settings_hardware_title"), font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_WHITE).pack(side="left")
        self._create_help_btn(row_hw_hdr, "help_gpu_title", "help_gpu_desc").pack(side="left", padx=6)
        
        self.gpu_var = ctk.BooleanVar(value=self.current_gpu_mode)
        chk_gpu = ctk.CTkCheckBox(
            card_hw, text=self.t("settings_gpu"), variable=self.gpu_var,
            font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_WHITE, fg_color=ACCENT_BLUE
        )
        chk_gpu.pack(anchor="w", padx=16, pady=(0, 2))
        
        ctk.CTkLabel(card_hw, text=self.t("settings_gpu_desc"), font=ctk.CTkFont(size=10), text_color=TEXT_MUTED).pack(anchor="w", padx=44, pady=(0, 14))
        
        # 3. Tiempos de Clips y Bajas Juntas
        card_clips = ctk.CTkFrame(scroll, fg_color=CARD_BG, corner_radius=8, border_width=1, border_color=CARD_BORDER)
        card_clips.pack(fill="x", pady=6)
        
        ctk.CTkLabel(card_clips, text=self.t("settings_clips_title"), font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_WHITE).pack(anchor="w", padx=16, pady=(12, 8))
        
        # Segundos antes
        t_row1 = ctk.CTkFrame(card_clips, fg_color="transparent")
        t_row1.pack(fill="x", padx=16, pady=4)
        ctk.CTkLabel(t_row1, text=self.t("settings_before"), font=ctk.CTkFont(size=11), text_color=TEXT_LIGHT).pack(side="left")
        self._create_help_btn(t_row1, "help_before_title", "help_before_desc").pack(side="left", padx=6)
        self.ent_before = ctk.CTkEntry(t_row1, width=70, height=30, font=ctk.CTkFont(size=11), fg_color=INNER_BG, border_color=CARD_BORDER, justify="center")
        self.ent_before.insert(0, str(self.current_sec_before))
        self.ent_before.pack(side="right")
        
        # Segundos después
        t_row2 = ctk.CTkFrame(card_clips, fg_color="transparent")
        t_row2.pack(fill="x", padx=16, pady=4)
        ctk.CTkLabel(t_row2, text=self.t("settings_after"), font=ctk.CTkFont(size=11), text_color=TEXT_LIGHT).pack(side="left")
        self._create_help_btn(t_row2, "help_after_title", "help_after_desc").pack(side="left", padx=6)
        self.ent_after = ctk.CTkEntry(t_row2, width=70, height=30, font=ctk.CTkFont(size=11), fg_color=INNER_BG, border_color=CARD_BORDER, justify="center")
        self.ent_after.insert(0, str(self.current_sec_after))
        self.ent_after.pack(side="right")
        
        # Ventana de Multikill
        t_row3 = ctk.CTkFrame(card_clips, fg_color="transparent")
        t_row3.pack(fill="x", padx=16, pady=4)
        ctk.CTkLabel(t_row3, text=self.t("settings_multi_window"), font=ctk.CTkFont(size=11), text_color=TEXT_LIGHT).pack(side="left")
        self._create_help_btn(t_row3, "help_multi_title", "help_multi_desc").pack(side="left", padx=6)
        self.ent_multi = ctk.CTkEntry(t_row3, width=70, height=30, font=ctk.CTkFont(size=11), fg_color=INNER_BG, border_color=CARD_BORDER, justify="center")
        self.ent_multi.insert(0, str(self.current_multikill_window))
        self.ent_multi.pack(side="right")
        
        # Modo de Agrupación de Clips en Multikills
        t_row4 = ctk.CTkFrame(card_clips, fg_color="transparent")
        t_row4.pack(fill="x", padx=16, pady=(10, 4))
        ctk.CTkLabel(t_row4, text=self.t("settings_group_title"), font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_WHITE).pack(side="left")
        self._create_help_btn(t_row4, "help_group_title", "help_group_desc").pack(side="left", padx=6)
        
        self.group_seg = ctk.CTkSegmentedButton(
            card_clips,
            values=[self.t("settings_group_cluster"), self.t("settings_group_indiv")],
            height=30,
            fg_color=INNER_BG,
            selected_color=ACCENT_BLUE,
            selected_hover_color=ACCENT_BLUE_H
        )
        if self.current_group_multikills:
            self.group_seg.set(self.t("settings_group_cluster"))
        else:
            self.group_seg.set(self.t("settings_group_indiv"))
        self.group_seg.pack(fill="x", padx=16, pady=(2, 10))
        
        # Abrir carpeta automáticamente
        row_open = ctk.CTkFrame(card_clips, fg_color="transparent")
        row_open.pack(fill="x", padx=16, pady=(4, 14))
        
        self.auto_open_var = ctk.BooleanVar(value=self.current_auto_open)
        chk_open = ctk.CTkCheckBox(
            row_open, text=self.t("settings_auto_open"), variable=self.auto_open_var,
            font=ctk.CTkFont(size=11), text_color=TEXT_WHITE, fg_color=ACCENT_BLUE
        )
        chk_open.pack(side="left")
        self._create_help_btn(row_open, "help_auto_open_title", "help_auto_open_desc").pack(side="left", padx=6)
        
        # Botón Guardar
        ctk.CTkButton(
            self, text=self.t("settings_save"), height=38,
            fg_color=ACCENT_GREEN, hover_color=ACCENT_GREEN_H, text_color="#ffffff",
            font=ctk.CTkFont(size=12, weight="bold"), corner_radius=6,
            command=self._save_and_close
        ).pack(fill="x", padx=20, pady=(0, 16))
        
    def _browse_dir(self):
        d = filedialog.askdirectory(initialdir=self.ent_dir.get().strip() or os.path.join(os.path.expanduser("~"), "Downloads"))
        if d:
            self.ent_dir.delete(0, "end")
            self.ent_dir.insert(0, os.path.abspath(d))
            
    def _save_and_close(self):
        new_dir = os.path.abspath(self.ent_dir.get().strip() or self.current_out_dir)
        new_gpu = self.gpu_var.get()
        
        try:
            val_b = re.sub(r'[^0-9]', '', self.ent_before.get())
            new_before = max(1, min(60, int(val_b))) if val_b else 7
        except Exception:
            new_before = 7
            
        try:
            val_a = re.sub(r'[^0-9]', '', self.ent_after.get())
            new_after = max(1, min(60, int(val_a))) if val_a else 7
        except Exception:
            new_after = 7
            
        try:
            val_m = re.sub(r'[^0-9]', '', self.ent_multi.get())
            new_multi = max(2, min(120, int(val_m))) if val_m else 15
        except Exception:
            new_multi = 15
            
        new_group_multikills = (self.group_seg.get() == self.t("settings_group_cluster"))
        new_auto_open = self.auto_open_var.get()
        
        self.destroy()
        if self.on_save:
            self.on_save(new_dir, new_gpu, new_before, new_after, new_multi, new_group_multikills, new_auto_open)
