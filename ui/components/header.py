import os
import webbrowser
from PIL import Image, ImageTk
import customtkinter as ctk
from utils.paths import get_binary_path
from ..theme import (
    CARD_BG, CARD_BORDER, TEXT_WHITE, TEXT_MUTED, INNER_BG, 
    HOVER_BG, ACCENT_BLUE, ACCENT_BLUE_H
)

class AppHeader(ctk.CTkFrame):
    def __init__(self, parent, translator, on_lang_change, on_open_tutorial, on_open_settings):
        super().__init__(parent, fg_color=CARD_BG, corner_radius=0, height=60, border_width=1, border_color=CARD_BORDER)
        self.pack(fill="x", side="top")
        self.t = translator
        self.on_lang_change = on_lang_change
        self.on_open_tutorial = on_open_tutorial
        self.on_open_settings = on_open_settings
        self._build_ui()
        
    def _build_ui(self):
        head_left = ctk.CTkFrame(self, fg_color="transparent")
        head_left.pack(side="left", padx=18, pady=8)
        
        # Logo
        try:
            png_logo_path = get_binary_path("app_icon.png")
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
        
        head_right = ctk.CTkFrame(self, fg_color="transparent")
        head_right.pack(side="right", padx=18, pady=8)
        
        # Redes
        ctk.CTkButton(
            head_right, text="𝕏  @ICayonh", width=105, height=32,
            fg_color=INNER_BG, hover_color=HOVER_BG, border_width=1, border_color=CARD_BORDER,
            text_color=TEXT_WHITE, font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: webbrowser.open("https://x.com/ICayonh")
        ).pack(side="left", padx=4)
        
        ctk.CTkButton(
            head_right, text="🟣  Twitch/icayon", width=125, height=32,
            fg_color="#9146FF", hover_color="#772ce8",
            text_color="#ffffff", font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: webbrowser.open("https://www.twitch.tv/icayon")
        ).pack(side="left", padx=4)
        
        # Tutorial
        self.btn_top_help = ctk.CTkButton(
            head_right, text=self.t("btn_help"), width=125, height=32,
            fg_color=ACCENT_BLUE, hover_color=ACCENT_BLUE_H,
            text_color="#ffffff", font=ctk.CTkFont(size=12, weight="bold"),
            command=self.on_open_tutorial
        )
        self.btn_top_help.pack(side="left", padx=4)
        
        # Settings Gear
        self.btn_settings = ctk.CTkButton(
            head_right, text=self.t("btn_settings"), width=105, height=32,
            fg_color=INNER_BG, hover_color=HOVER_BG, border_width=1, border_color=CARD_BORDER,
            text_color=TEXT_WHITE, font=ctk.CTkFont(size=12, weight="bold"),
            command=self.on_open_settings
        )
        self.btn_settings.pack(side="left", padx=4)
        
        # Idioma
        self.lang_var = ctk.StringVar(value="🇪🇸 Español")
        self.cmb_lang = ctk.CTkOptionMenu(
            head_right, values=["🇪🇸 Español", "🇬🇧 English"], variable=self.lang_var,
            width=115, height=32, fg_color=INNER_BG, button_color=INNER_BG,
            button_hover_color=HOVER_BG, text_color=TEXT_WHITE,
            font=ctk.CTkFont(size=11), dropdown_fg_color=CARD_BG,
            command=self.on_lang_change
        )
        self.cmb_lang.pack(side="left", padx=4)
        
    def refresh_texts(self):
        self.btn_top_help.configure(text=self.t("btn_help"))
        self.btn_settings.configure(text=self.t("btn_settings"))