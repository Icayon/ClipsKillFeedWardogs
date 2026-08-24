import os
import sys
import threading
import urllib.request
import customtkinter as ctk

from ..theme import (
    BG_MAIN, CARD_BG, CARD_BORDER, INNER_BG, HOVER_BG,
    ACCENT_CYAN, ACCENT_BLUE, ACCENT_BLUE_H, ACCENT_GREEN, ACCENT_GREEN_H,
    TEXT_LIGHT, TEXT_MUTED, TEXT_WHITE
)
from utils.updater import launch_updater_script


class UpdateModal(ctk.CTkToplevel):
    """
    Modal de actualización con las 3 opciones requeridas:
    1. Actualizar ahora (Descarga en segundo plano + reinicio automático)
    2. Recordar más tarde (Preguntará la próxima vez)
    3. No volver a avisar (Desactiva la búsqueda automática)
    """

    def __init__(self, parent, latest_tag: str, release_notes: str, download_url: str,
                 on_later=None, on_never=None):
        super().__init__(parent)
        self.parent = parent
        self.latest_tag = latest_tag
        self.release_notes = release_notes
        self.download_url = download_url
        self.on_later_cb = on_later
        self.on_never_cb = on_never

        self.title(f"Actualización disponible — {latest_tag}")
        self.geometry("540x440")
        self.minsize(500, 400)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color=BG_MAIN)

        self._is_downloading = False
        self._build_ui()

    def _build_ui(self):
        # Header superior
        top_hdr = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=0, height=52, border_width=1, border_color=CARD_BORDER)
        top_hdr.pack(fill="x", side="top")
        top_hdr.pack_propagate(False)

        ctk.CTkLabel(
            top_hdr,
            text=f"🚀 Nueva actualización disponible ({self.latest_tag})",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=ACCENT_CYAN
        ).pack(side="left", padx=20, pady=12)

        # Cuerpo principal
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=12)

        # Contenedor para las notas del parche
        lbl_notes_hdr = ctk.CTkLabel(
            body,
            text="Novedades y cambios de esta versión:",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=TEXT_WHITE,
            anchor="w"
        )
        lbl_notes_hdr.pack(anchor="w", pady=(0, 6))

        notes_box = ctk.CTkTextbox(
            body,
            fg_color=INNER_BG,
            border_width=1,
            border_color=CARD_BORDER,
            text_color=TEXT_LIGHT,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            corner_radius=6
        )
        notes_box.pack(fill="both", expand=True, pady=(0, 8))
        notes_box.insert("1.0", self.release_notes if self.release_notes.strip() else "Sin notas de versión especificadas.")
        notes_box.configure(state="disabled")

        # Recordatorio informativo
        self.lbl_hint = ctk.CTkLabel(
            body,
            text="💡 Podrás actualizar más adelante en Ajustes en cualquier momento.",
            font=ctk.CTkFont(family="Segoe UI", size=10, slant="italic"),
            text_color=TEXT_MUTED,
            anchor="w"
        )
        self.lbl_hint.pack(anchor="w", pady=(0, 8))

        # Sección de progreso de descarga (oculta inicialmente)
        self.dl_frame = ctk.CTkFrame(body, fg_color="transparent")
        
        self.lbl_dl_status = ctk.CTkLabel(
            self.dl_frame,
            text="Preparando descarga...",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=ACCENT_CYAN,
            anchor="w"
        )
        self.lbl_dl_status.pack(fill="x", pady=(0, 4))

        self.progress_bar = ctk.CTkProgressBar(self.dl_frame, height=8, fg_color=INNER_BG, progress_color=ACCENT_GREEN)
        self.progress_bar.set(0.0)
        self.progress_bar.pack(fill="x", pady=(0, 4))

        # Botones de acción
        self.btn_box = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_box.pack(fill="x", padx=20, pady=(0, 16))

        # Botón 1: Actualizar ahora
        self.btn_update = ctk.CTkButton(
            self.btn_box,
            text="⚡ Actualizar ahora",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=ACCENT_GREEN,
            hover_color=ACCENT_GREEN_H,
            text_color="#ffffff",
            height=34,
            corner_radius=6,
            command=self._start_download
        )
        self.btn_update.pack(side="left", fill="x", expand=True, padx=(0, 4))

        # Botón 2: Recordar más tarde
        self.btn_later = ctk.CTkButton(
            self.btn_box,
            text="Recordar luego",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color=INNER_BG,
            hover_color=HOVER_BG,
            text_color=TEXT_WHITE,
            border_width=1,
            border_color=CARD_BORDER,
            height=34,
            corner_radius=6,
            command=self._on_later
        )
        self.btn_later.pack(side="left", fill="x", expand=True, padx=4)

        # Botón 3: No volver a avisar
        self.btn_never = ctk.CTkButton(
            self.btn_box,
            text="No avisar más",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color=INNER_BG,
            hover_color=HOVER_BG,
            text_color=TEXT_MUTED,
            border_width=1,
            border_color=CARD_BORDER,
            height=34,
            corner_radius=6,
            command=self._on_never
        )
        self.btn_never.pack(side="left", fill="x", expand=True, padx=(4, 0))

    def _on_later(self):
        if self._is_downloading:
            return
        if self.on_later_cb:
            self.on_later_cb()
        self.destroy()

    def _on_never(self):
        if self._is_downloading:
            return
        if self.on_never_cb:
            self.on_never_cb()
        self.destroy()

    def _start_download(self):
        if self._is_downloading:
            return
        self._is_downloading = True

        # Deshabilitar botones
        self.btn_update.configure(state="disabled")
        self.btn_later.configure(state="disabled")
        self.btn_never.configure(state="disabled")

        # Mostrar barra de descarga
        self.dl_frame.pack(fill="x", pady=(4, 8))

        threading.Thread(target=self._download_worker, daemon=True).start()

    def _download_worker(self):
        try:
            temp_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp", "ClipSkillFeedWardogs_Update")
            os.makedirs(temp_dir, exist_ok=True)

            ext = ".zip" if ".zip" in self.download_url.lower() else ".exe"
            save_file = os.path.join(temp_dir, f"update_{self.latest_tag}{ext}")

            req = urllib.request.Request(self.download_url, headers={"User-Agent": "ClipsKillFeedWardogs-App"})

            with urllib.request.urlopen(req, timeout=30) as resp:
                total_size = int(resp.headers.get('Content-Length', 0))
                downloaded = 0
                block_size = 65536

                with open(save_file, "wb") as f:
                    while True:
                        buffer = resp.read(block_size)
                        if not buffer:
                            break
                        downloaded += len(buffer)
                        f.write(buffer)

                        if total_size > 0:
                            pct = downloaded / float(total_size)
                            pct_int = int(pct * 100)
                            self.after(0, lambda p=pct, pi=pct_int: self._update_progress(p, f"Descargando actualización... {pi}%"))

            self.after(0, lambda: self._update_progress(1.0, "Descarga completada. Aplicando e iniciando..."))

            # Determinar carpeta de destino de la aplicación
            if getattr(sys, 'frozen', False):
                target_dir = os.path.dirname(sys.executable)
            else:
                target_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

            # Lanzar script desvinculado que cierra esta app, reemplaza y reinicia
            self.after(1000, lambda: launch_updater_script(save_file, target_dir))

        except Exception as e:
            self._is_downloading = False
            error_msg = str(e)
            self.after(0, lambda: self._on_download_error(error_msg))

    def _update_progress(self, pct: float, status_text: str):
        self.progress_bar.set(pct)
        self.lbl_dl_status.configure(text=status_text)

    def _on_download_error(self, err: str):
        self.dl_frame.pack_forget()
        self.btn_update.configure(state="normal")
        self.btn_later.configure(state="normal")
        self.btn_never.configure(state="normal")

        from .error_modal import show_error
        show_error(self.parent, "ERR-006", f"Error durante la descarga:\n{err}")
        self.destroy()
