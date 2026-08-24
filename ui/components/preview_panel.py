import customtkinter as ctk
from ..theme import (
    CARD_BG, CARD_BORDER, INNER_BG, HOVER_BG, TEXT_WHITE, 
    TEXT_MUTED, TEXT_LIGHT, ACCENT_BLUE, ACCENT_BLUE_H, 
    ACCENT_PURPLE, ACCENT_PURPLE_H
)

class PreviewPanel(ctk.CTkFrame):
    def __init__(self, parent, translator, on_cut_single, on_play_seek, on_open_full, on_batch, on_html):
        super().__init__(parent, fg_color=CARD_BG, corner_radius=8, width=320, border_width=1, border_color=CARD_BORDER)
        self.pack(side="right", fill="y", padx=(0, 18), pady=16)
        self.pack_propagate(False)
        self.t = translator
        self.on_cut_single = on_cut_single
        self.on_play_seek = on_play_seek
        self.on_open_full = on_open_full
        self.on_batch = on_batch
        self.on_html = on_html
        self.preview_image_ref = None
        self._build_ui()
        
    def _build_ui(self):
        p_hdr = ctk.CTkFrame(self, fg_color="transparent")
        p_hdr.pack(fill="x", padx=16, pady=(16, 8))
        
        self.lbl_preview_hdr = ctk.CTkLabel(p_hdr, text=self.t("preview_title"), font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_WHITE)
        self.lbl_preview_hdr.pack(side="left")
        
        # Frame preview
        self.prev_img_box = ctk.CTkFrame(self, fg_color=INNER_BG, corner_radius=6, height=110, border_width=1, border_color=CARD_BORDER)
        self.prev_img_box.pack(fill="x", padx=16, pady=(0, 10))
        self.prev_img_box.pack_propagate(False)
        
        self.lbl_preview_img = ctk.CTkLabel(self.prev_img_box, text=self.t("preview_hint"), font=ctk.CTkFont(size=11), text_color=TEXT_MUTED)
        self.lbl_preview_img.pack(expand=True)
        
        # Metadata
        self.meta_box = ctk.CTkFrame(self, fg_color=INNER_BG, corner_radius=6, border_width=1, border_color=CARD_BORDER)
        self.meta_box.pack(fill="x", padx=16, pady=(0, 12))
        
        self.lbl_preview_details = ctk.CTkLabel(
            self.meta_box, 
            text=f"{self.t('meta_file')} --\n{self.t('meta_time')} --:--:--\n{self.t('meta_play')} --\n{self.t('meta_dist')} --\n{self.t('meta_target')} --\n{self.t('meta_hype')} --",
            font=ctk.CTkFont(size=11), text_color=TEXT_LIGHT, justify="left", anchor="w"
        )
        self.lbl_preview_details.pack(fill="x", padx=12, pady=10)
        
        # Botones acción
        btn_card = ctk.CTkFrame(self, fg_color="transparent")
        btn_card.pack(fill="x", padx=16, pady=(0, 16))
        
        self.btn_cut_this = ctk.CTkButton(
            btn_card, text=self.t("btn_cut_this"), height=36, font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=ACCENT_PURPLE, hover_color=ACCENT_PURPLE_H, text_color="#ffffff",
            command=self.on_cut_single
        )
        self.btn_cut_this.pack(fill="x", pady=3)
        
        self.btn_preview_sec = ctk.CTkButton(
            btn_card, text=self.t("btn_play_seek"), height=32, font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=INNER_BG, hover_color=HOVER_BG, border_width=1, border_color=CARD_BORDER,
            text_color=TEXT_WHITE, command=self.on_play_seek
        )
        self.btn_preview_sec.pack(fill="x", pady=3)
        
        self.btn_open_video = ctk.CTkButton(
            btn_card, text=self.t("btn_open_full"), height=32, font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=INNER_BG, hover_color=HOVER_BG, border_width=1, border_color=CARD_BORDER,
            text_color=TEXT_WHITE, command=self.on_open_full
        )
        self.btn_open_video.pack(fill="x", pady=3)
        
        self.btn_batch = ctk.CTkButton(
            btn_card, text=self.t("btn_batch"), height=34, font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=INNER_BG, hover_color=HOVER_BG, border_width=1, border_color=CARD_BORDER,
            text_color=TEXT_WHITE, command=self.on_batch
        )
        self.btn_batch.pack(fill="x", pady=3)
        
        self.btn_html = ctk.CTkButton(
            btn_card, text=self.t("btn_html"), height=32, font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=INNER_BG, hover_color=HOVER_BG, border_width=1, border_color=CARD_BORDER,
            text_color=TEXT_WHITE, command=self.on_html
        )
        self.btn_html.pack(fill="x", pady=3)

    def refresh_texts(self):
        self.lbl_preview_hdr.configure(text=self.t("preview_title"))
        self.btn_cut_this.configure(text=self.t("btn_cut_this"))
        self.btn_preview_sec.configure(text=self.t("btn_play_seek"))
        self.btn_open_video.configure(text=self.t("btn_open_full"))
        self.btn_batch.configure(text=self.t("btn_batch"))
        self.btn_html.configure(text=self.t("btn_html"))

    def clear(self):
        """Resetea el panel de vista previa al estado vacío inicial."""
        self.lbl_preview_img.configure(image=None, text=self.t("preview_hint"))
        self.preview_image_ref = None
        self.lbl_preview_details.configure(
            text=f"{self.t('meta_file')} --\n{self.t('meta_time')} --:--:--\n{self.t('meta_play')} --\n{self.t('meta_dist')} --\n{self.t('meta_target')} --\n{self.t('meta_hype')} --"
        )