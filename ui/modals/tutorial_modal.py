import customtkinter as ctk
from ..theme import (
    BG_MAIN, CARD_BG, CARD_BORDER, ACCENT_CYAN, ACCENT_BLUE, 
    ACCENT_GREEN, ACCENT_GREEN_H, ACCENT_PURPLE, TEXT_LIGHT
)

class TutorialModal(ctk.CTkToplevel):
    def __init__(self, parent, translator):
        super().__init__(parent)
        self.t = translator
        
        self.title(self.t("tut_title"))
        self.geometry("640x600")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color=BG_MAIN)
        
        self._build_ui()
        
    def _build_ui(self):
        top_hdr = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=0, height=54, border_width=1, border_color=CARD_BORDER)
        top_hdr.pack(fill="x", side="top")
        
        ctk.CTkLabel(
            top_hdr, 
            text=self.t("tut_title"), 
            font=ctk.CTkFont(size=14, weight="bold"), 
            text_color=ACCENT_CYAN
        ).pack(side="left", padx=20, pady=12)
        
        scroll_tut = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_tut.pack(fill="both", expand=True, padx=20, pady=12)
        
        steps = [
            (self.t("tut_step1_title"), self.t("tut_step1_desc"), ACCENT_BLUE),
            (self.t("tut_step2_title"), self.t("tut_step2_desc"), "#38bdf8"),
            (self.t("tut_step3_title"), self.t("tut_step3_desc"), "#f59e0b"),
            (self.t("tut_step4_title"), self.t("tut_step4_desc"), ACCENT_GREEN),
            (self.t("tut_step5_title"), self.t("tut_step5_desc"), ACCENT_PURPLE)
        ]
        
        for title, desc, color in steps:
            card = ctk.CTkFrame(scroll_tut, fg_color=CARD_BG, corner_radius=8, border_width=1, border_color=CARD_BORDER)
            card.pack(fill="x", pady=6)
            
            c_hdr = ctk.CTkFrame(card, fg_color="transparent")
            c_hdr.pack(fill="x", padx=14, pady=(12, 4))
            
            ctk.CTkLabel(
                c_hdr, 
                text=title, 
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
            
        btn_close = ctk.CTkButton(
            self, 
            text=self.t("tut_btn_close"), 
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=ACCENT_GREEN, 
            hover_color=ACCENT_GREEN_H,
            text_color="#ffffff",
            height=36,
            corner_radius=6,
            command=self.destroy
        )
        btn_close.pack(fill="x", padx=20, pady=(0, 16))