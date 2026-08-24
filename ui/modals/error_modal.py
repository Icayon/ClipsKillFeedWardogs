import customtkinter as ctk
from ..theme import (
    BG_MAIN, CARD_BG, CARD_BORDER, INNER_BG, HOVER_BG,
    ACCENT_BLUE, ACCENT_BLUE_H, TEXT_LIGHT, TEXT_MUTED
)

# ─────────────────────────────────────────────────────────────────────────────
# Catálogo de códigos de error
# ─────────────────────────────────────────────────────────────────────────────
ERROR_CODES = {
    "ERR-001": "Cola de vídeos vacía. Añade al menos un vídeo antes de iniciar el escaneo.",
    "ERR-002": "Gamertag no especificado. Introduce tu nick en el campo correspondiente.",
    "ERR-003": "FFmpeg no encontrado. Asegúrate de que ffmpeg.exe está en la carpeta Archivos.",
    "ERR-004": "El escaneo fue interrumpido de forma inesperada. El vídeo puede estar corrupto o en un formato no compatible.",
    "ERR-005": "Fallo de aceleración GPU (CUDA). El programa ha cambiado automáticamente a CPU.",
    "ERR-006": "Error al exportar el clip. Comprueba que tienes espacio en disco y permisos de escritura en la carpeta destino.",
    "ERR-007": "Archivo de vídeo no encontrado o inaccesible. Puede haber sido movido o eliminado.",
    "ERR-008": "Error al analizar la pista de audio del vídeo. El análisis de hype será omitido.",
    "ERR-009": "Error al generar la vista previa del fotograma. La baja ha sido registrada igualmente.",
    "ERR-010": "Error inesperado. Si persiste, reinicia la aplicación.",
    "ERR-011": "Ruta de exportación inválida o sin permisos de escritura.",
    "ERR-012": "Error al concatenar clips para el montaje final.",
}


class ErrorModal(ctk.CTkToplevel):
    """
    Ventana de error con código de bug, descripción y detalle técnico opcional.
    Estilo oscuro coherente con el resto de la aplicación.
    """
    ACCENT_RED  = "#ef4444"
    ACCENT_RED_H = "#dc2626"

    def __init__(self, parent, error_code: str, detail: str = ""):
        super().__init__(parent)
        description = ERROR_CODES.get(error_code, "Error desconocido.")
        self.title(f"Error — {error_code}")
        self.geometry("520x320")
        self.minsize(480, 280)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color=BG_MAIN)
        self._build_ui(error_code, description, detail)

    def _build_ui(self, code: str, description: str, detail: str):
        # Header rojo
        hdr = ctk.CTkFrame(self, fg_color=self.ACCENT_RED, corner_radius=0, height=48)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)

        hdr_inner = ctk.CTkFrame(hdr, fg_color="transparent")
        hdr_inner.pack(fill="both", expand=True, padx=18, pady=8)

        ctk.CTkLabel(
            hdr_inner,
            text="  Error del sistema",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#ffffff"
        ).pack(side="left")

        ctk.CTkLabel(
            hdr_inner,
            text=code,
            font=ctk.CTkFont(family="Segoe UI Mono", size=12, weight="bold"),
            text_color="#ffffff"
        ).pack(side="right")

        # Cuerpo
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=18, pady=12)

        # Descripción principal
        card = ctk.CTkFrame(body, fg_color=CARD_BG, corner_radius=8, border_width=1, border_color=CARD_BORDER)
        card.pack(fill="x")

        ctk.CTkLabel(
            card,
            text=description,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_LIGHT,
            justify="left",
            wraplength=440,
            anchor="w"
        ).pack(anchor="w", padx=14, pady=12)

        # Detalle técnico (si lo hay)
        if detail:
            detail_card = ctk.CTkFrame(body, fg_color=INNER_BG, corner_radius=6, border_width=1, border_color=CARD_BORDER)
            detail_card.pack(fill="x", pady=(8, 0))

            ctk.CTkLabel(
                detail_card,
                text="Detalle técnico:",
                font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                text_color=TEXT_MUTED,
                anchor="w"
            ).pack(anchor="w", padx=12, pady=(8, 2))

            ctk.CTkLabel(
                detail_card,
                text=str(detail)[:280],
                font=ctk.CTkFont(family="Segoe UI Mono", size=10),
                text_color=TEXT_MUTED,
                justify="left",
                wraplength=440,
                anchor="w"
            ).pack(anchor="w", padx=12, pady=(0, 10))

        # Botón cerrar
        ctk.CTkButton(
            self,
            text="Entendido",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=self.ACCENT_RED,
            hover_color=self.ACCENT_RED_H,
            text_color="#ffffff",
            height=34,
            corner_radius=6,
            command=self.destroy
        ).pack(fill="x", padx=18, pady=(0, 16))


def show_error(parent, error_code: str, detail: str = ""):
    """Función de conveniencia para mostrar el modal de error."""
    try:
        ErrorModal(parent, error_code, detail)
    except Exception:
        # Fallback a messagebox si el modal falla
        from tkinter import messagebox
        desc = ERROR_CODES.get(error_code, "Error desconocido.")
        messagebox.showerror(f"Error — {error_code}", f"{desc}\n\n{detail}")
