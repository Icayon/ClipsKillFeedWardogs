import customtkinter as ctk
from ..theme import (
    BG_MAIN, CARD_BG, CARD_BORDER, INNER_BG, HOVER_BG, 
    ACCENT_CYAN, ACCENT_BLUE, ACCENT_BLUE_H, TEXT_LIGHT
)

class InfoModal(ctk.CTkToplevel):
    def __init__(self, parent, title_text, message_text, btn_text="Entendido"):
        super().__init__(parent)
        self.title(title_text)
        self.geometry("500x300")
        self.minsize(460, 260)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color=BG_MAIN)
        
        self._build_ui(title_text, message_text, btn_text)
        
    def _build_ui(self, title_text, message_text, btn_text):
        top_hdr = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=0, height=48, border_width=1, border_color=CARD_BORDER)
        top_hdr.pack(fill="x", side="top")
        
        ctk.CTkLabel(
            top_hdr, 
            text=title_text, 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), 
            text_color=ACCENT_CYAN
        ).pack(side="left", padx=20, pady=10)
        
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=12)
        
        card = ctk.CTkFrame(body, fg_color=CARD_BG, corner_radius=8, border_width=1, border_color=CARD_BORDER)
        card.pack(fill="both", expand=True)
        
        lbl_msg = ctk.CTkLabel(
            card,
            text=message_text,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_LIGHT,
            justify="left",
            wraplength=420
        )
        lbl_msg.pack(anchor="nw", padx=16, pady=14)
        
        btn_close = ctk.CTkButton(
            self,
            text=btn_text,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=ACCENT_BLUE,
            hover_color=ACCENT_BLUE_H,
            text_color="#ffffff",
            height=34,
            corner_radius=6,
            command=self.destroy
        )
        btn_close.pack(fill="x", padx=20, pady=(0, 16))