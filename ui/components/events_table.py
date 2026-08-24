from tkinter import ttk
import customtkinter as ctk
from ..theme import (
    CARD_BG, CARD_BORDER, INNER_BG, TEXT_WHITE, 
    TEXT_MUTED, ACCENT_BLUE, ACCENT_CYAN
)

class EventsTable(ctk.CTkFrame):
    def __init__(self, parent, translator, on_select, on_double_click):
        super().__init__(parent, fg_color=CARD_BG, corner_radius=8, border_width=1, border_color=CARD_BORDER)
        self.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=16)
        self.t = translator
        self.on_select = on_select
        self.on_double_click = on_double_click
        self._setup_treeview_dark_style()
        self._build_ui()
        
    def _setup_treeview_dark_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
            
        style.configure(
            "DarkTable.Treeview",
            background="#090d13",
            foreground="#f0f6fc",
            fieldbackground="#090d13",
            borderwidth=0,
            rowheight=26,
            font=("Segoe UI", 10)
        )
        style.configure(
            "DarkTable.Treeview.Heading",
            background="#161b22",
            foreground="#f0f6fc",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            borderwidth=1,
            bordercolor="#30363d"
        )
        style.map(
            "DarkTable.Treeview",
            background=[('selected', '#1f6feb')],
            foreground=[('selected', '#ffffff')]
        )
        style.map(
            "DarkTable.Treeview.Heading",
            background=[('active', '#21262d'), ('pressed', '#30363d')]
        )

    def _build_ui(self):
        t_hdr = ctk.CTkFrame(self, fg_color="transparent")
        t_hdr.pack(fill="x", padx=16, pady=(16, 8))
        
        self.lbl_events_hdr = ctk.CTkLabel(t_hdr, text=self.t("events_title"), font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_WHITE)
        self.lbl_events_hdr.pack(side="left")
        
        self.lbl_count = ctk.CTkLabel(t_hdr, text="0 bajas", font=ctk.CTkFont(size=11), text_color=TEXT_MUTED)
        self.lbl_count.pack(side="right")
        
        tbl_container = ctk.CTkFrame(self, fg_color=INNER_BG, corner_radius=6, border_width=1, border_color=CARD_BORDER)
        tbl_container.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        
        cols = ("time", "killer", "dist", "victim", "play", "hype")
        self.tree = ttk.Treeview(tbl_container, columns=cols, show='headings', selectmode='browse', style="DarkTable.Treeview")
        
        self.tree.column("time", width=75, anchor="center")
        self.tree.column("killer", width=120, anchor="w")
        self.tree.column("dist", width=95, anchor="center")
        self.tree.column("victim", width=130, anchor="w")
        self.tree.column("play", width=120, anchor="center")
        self.tree.column("hype", width=90, anchor="center")
        
        self.refresh_headers()
        
        scrollbar = ttk.Scrollbar(tbl_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=1, pady=1)
        scrollbar.pack(side="right", fill="y", padx=(0, 1), pady=1)
        
        self.tree.bind("<<TreeviewSelect>>", lambda e: self.on_select(e))
        self.tree.bind("<Double-1>", lambda e: self.on_double_click(e))
        
    def refresh_headers(self):
        self.tree.heading("time", text=self.t("col_time"))
        self.tree.heading("killer", text=self.t("col_killer"))
        self.tree.heading("dist", text=self.t("col_dist"))
        self.tree.heading("victim", text=self.t("col_target"))
        self.tree.heading("play", text=self.t("col_play"))
        self.tree.heading("hype", text=self.t("col_hype"))
        self.lbl_events_hdr.configure(text=self.t("events_title"))
        
    def clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.lbl_count.configure(text="0 bajas")
        
    def add_item(self, item_id, values, tag=None):
        if tag:
            self.tree.insert('', 'end', iid=item_id, values=values, tags=(tag,))
        else:
            self.tree.insert('', 'end', iid=item_id, values=values)
            
    def update_count(self, count):
        self.lbl_count.configure(text=f"{count} {self.t('kills_indexed')}")