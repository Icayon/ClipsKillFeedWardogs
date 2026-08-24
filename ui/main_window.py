import os
import re
import sys
import threading
import subprocess
from datetime import timedelta
from tkinter import messagebox
from PIL import Image, ImageTk
import customtkinter as ctk

from utils.paths import get_binary_path, NO_WINDOW_FLAGS, init_windows_app_id
from i18n import Translator
from core import KillRecord, KillfeedScanner, ClipRenderer, HtmlReporter
from .theme import BG_MAIN, CARD_BG, CARD_BORDER, ACCENT_BLUE, ACCENT_CYAN, TEXT_MUTED, TEXT_LIGHT
from .components import AppHeader, QueuePanel, EventsTable, PreviewPanel
from .modals import TutorialModal, SingleCutModal, BatchExportModal, SettingsModal

class AutoClipWardogsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        init_windows_app_id()
        
        self.translator = Translator("es")
        self.t = self.translator
        
        # Configuración del usuario
        self.default_out_dir = os.path.join(os.path.expanduser("~"), "Downloads", "Clips_Wardogs")
        os.makedirs(self.default_out_dir, exist_ok=True)
        self.use_gpu = True
        self.sec_before = 7
        self.sec_after = 7
        self.auto_open = True
        
        self.title("Clips KillFeed Wardogs by ICayon")
        self.geometry("1280x870")
        self.minsize(1100, 740)
        self.configure(fg_color=BG_MAIN)
        
        # Icono ventana
        try:
            icon_ico = get_binary_path("app_icon.ico")
            if os.path.exists(icon_ico):
                self.iconbitmap(icon_ico)
        except Exception:
            pass
            
        self.is_running = False
        self.scanner = KillfeedScanner()
        self.all_kills_data = []
        
        self._setup_ui()
        
    def _setup_ui(self):
        # 1. Header
        self.header = AppHeader(
            self, self.t, 
            on_lang_change=self._change_language,
            on_open_tutorial=self._open_tutorial,
            on_open_settings=self._open_settings
        )
        
        # 2. Main Area
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.pack(fill="both", expand=True)
        
        # Left Panel (Queue)
        self.queue_panel = QueuePanel(
            main_content, self.t,
            on_start=self._start_scan,
            on_stop=self._stop_scan,
            on_help_gamertag=self._open_tutorial
        )
        
        # Center Table
        self.events_table = EventsTable(
            main_content, self.t,
            on_select=self._on_table_select,
            on_double_click=self._on_table_double_click
        )
        
        # Right Panel (Preview)
        self.preview_panel = PreviewPanel(
            main_content, self.t,
            on_cut_single=self._open_single_cut,
            on_play_seek=self._play_seek,
            on_open_full=self._open_full_video,
            on_batch=self._open_batch,
            on_html=self._open_html_report
        )
        
        # 3. Bottom Progress Bar
        self._setup_bottom_bar()

    def _setup_bottom_bar(self):
        self.bottom_bar = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=0, height=52, border_width=1, border_color=CARD_BORDER)
        self.bottom_bar.pack(fill="x", side="bottom")
        
        status_box = ctk.CTkFrame(self.bottom_bar, fg_color="transparent")
        status_box.pack(fill="x", padx=18, pady=(8, 2))
        
        self.lbl_status_progress = ctk.CTkLabel(status_box, text=self.t("ready"), font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_LIGHT)
        self.lbl_status_progress.pack(side="left")
        
        self.lbl_progress_pct = ctk.CTkLabel(status_box, text="0%", font=ctk.CTkFont(size=12, weight="bold"), text_color=ACCENT_CYAN)
        self.lbl_progress_pct.pack(side="left", padx=12)
        
        self.lbl_progress_detail = ctk.CTkLabel(status_box, text="--:--:-- / --:--:--", font=ctk.CTkFont(size=11), text_color=TEXT_MUTED)
        self.lbl_progress_detail.pack(side="right")
        
        self.progress_bar = ctk.CTkProgressBar(self.bottom_bar, height=6, corner_radius=3, fg_color=BG_MAIN, progress_color=ACCENT_BLUE)
        self.progress_bar.set(0.0)
        self.progress_bar.pack(fill="x", padx=18, pady=(0, 8))

    def _change_language(self, choice):
        lang = "es" if "Español" in choice else "en"
        self.translator.set_language(lang)
        self.header.refresh_texts()
        self.queue_panel.refresh_texts()
        self.events_table.refresh_headers()
        self.preview_panel.refresh_texts()
        self.lbl_status_progress.configure(text=self.t("ready"))
        
    def _open_tutorial(self):
        TutorialModal(self, self.t)
        
    def _open_settings(self):
        SettingsModal(
            self, 
            default_folder=self.default_out_dir, 
            use_gpu=self.use_gpu, 
            sec_before=self.sec_before, 
            sec_after=self.sec_after, 
            auto_open=self.auto_open, 
            translator=self.t, 
            on_save=self._apply_settings
        )
        
    def _apply_settings(self, folder: str, use_gpu: bool, sec_before: int, sec_after: int, auto_open: bool):
        self.default_out_dir = folder
        self.use_gpu = use_gpu
        self.sec_before = sec_before
        self.sec_after = sec_after
        self.auto_open = auto_open
        os.makedirs(self.default_out_dir, exist_ok=True)
        messagebox.showinfo("AutoClip", "Configuración guardada correctamente.")

    def _start_scan(self):
        if not self.queue_panel.video_list:
            messagebox.showwarning("Atención", self.t("empty_queue"))
            return
            
        raw_gamertags = self.queue_panel.ent_gamertags.get().strip()
        if not raw_gamertags:
            messagebox.showwarning("Atención", self.t("tracking_label"))
            return
            
        self.is_running = True
        self.queue_panel.btn_start.configure(state="disabled")
        self.queue_panel.btn_stop.configure(state="normal")
        self.all_kills_data = []
        self.events_table.clear()
        self.lbl_status_progress.configure(text=self.t("scanning"))
        
        threading.Thread(target=self._scan_worker, daemon=True).start()

    def _stop_scan(self):
        self.is_running = False
        self.queue_panel.btn_start.configure(state="normal")
        self.queue_panel.btn_stop.configure(state="disabled")
        self.lbl_status_progress.configure(text="Detenido")
        self.lbl_progress_detail.configure(text="Detenido por el usuario")

    def _scan_worker(self):
        videos = self.queue_panel.video_list
        total_videos = len(videos)
        gamertags = [t.strip() for t in self.queue_panel.ent_gamertags.get().split(",") if t.strip()]
        detect_audio = self.queue_panel.chk_detect_audio.get()
        filter_beta = self.queue_panel.chk_filter_beta.get()
        
        for v_idx, v_path in enumerate(videos):
            if not self.is_running:
                break
                
            v_name = os.path.basename(v_path)
            duration_sec = self.scanner.get_video_duration(v_path)
            total_ts_str = str(timedelta(seconds=duration_sec)) if duration_sec > 0 else "--:--:--"
            
            def on_prog(sec, total_sec, count_v):
                global_pct = ((v_idx + (sec / total_sec if total_sec > 0 else 0)) / total_videos)
                self.progress_bar.set(global_pct)
                self.lbl_progress_pct.configure(text=f"{int(global_pct * 100)}%")
                self.lbl_progress_detail.configure(text=f"{str(timedelta(seconds=sec))} / {total_ts_str}  [{v_idx+1}/{total_videos}]")
                self.lbl_status_progress.configure(text=f"Bajas: {len(self.all_kills_data)} | {v_name}")
                
            kills = self.scanner.scan_video(
                v_path, gamertags, detect_audio, filter_beta,
                use_gpu=self.use_gpu,
                on_progress=on_prog, is_running_check=lambda: self.is_running
            )
            
            for k in kills:
                self.all_kills_data.append(k)
                row_id = f"item_{len(self.all_kills_data)}"
                self.events_table.add_item(row_id, (k.timestamp, k.killer, k.distance, k.victim, k.play_type, k.hype))
                self.events_table.update_count(len(self.all_kills_data))
                
        self.is_running = False
        self.queue_panel.btn_start.configure(state="normal")
        self.queue_panel.btn_stop.configure(state="disabled")
        self.progress_bar.set(1.0)
        self.lbl_progress_pct.configure(text="100%")
        self.lbl_status_progress.configure(text=self.t("scan_finished"))
        self.lbl_progress_detail.configure(text=f"Total: {len(self.all_kills_data)} bajas")
        messagebox.showinfo("AutoClip", f"{self.t('scan_finished')}\n\nTotal bajas: {len(self.all_kills_data)}")

    def _get_selected_record(self):
        selected = self.events_table.tree.selection()
        if not selected:
            messagebox.showinfo("Atención", "Selecciona una baja de la tabla para continuar.")
            return None
        values = self.events_table.tree.item(selected[0])['values']
        ts, victim = values[0], values[3]
        return next((k for k in self.all_kills_data if k.timestamp == ts and k.victim == victim), None)

    def _on_table_select(self, event):
        rec = self._get_selected_record()
        if not rec:
            return
        if rec.frame_rgb is not None:
            try:
                img_pil = Image.fromarray(rec.frame_rgb).resize((260, 92), Image.Resampling.LANCZOS)
                self.preview_image_ref = ImageTk.PhotoImage(img_pil)
                self.preview_panel.lbl_preview_img.configure(image=self.preview_image_ref, text="")
            except Exception:
                pass
        self.preview_panel.lbl_preview_details.configure(
            text=f"{self.t('meta_file')} {rec.video_name}\n{self.t('meta_time')} {rec.timestamp}\n{self.t('meta_play')} {rec.play_type}\n{self.t('meta_dist')} {rec.distance}\n{self.t('meta_target')} {rec.victim}\n{self.t('meta_hype')} {rec.hype}"
        )

    def _on_table_double_click(self, event):
        self._play_seek()

    def _play_seek(self):
        rec = self._get_selected_record()
        if not rec: return
        start_sec = max(0, rec.time_sec - 5)
        cmd = [get_binary_path("ffplay"), "-ss", str(start_sec), "-autoexit", rec.video_path]
        try: subprocess.Popen(cmd, creationflags=NO_WINDOW_FLAGS)
        except Exception: os.startfile(rec.video_path)

    def _open_full_video(self):
        rec = self._get_selected_record()
        if rec:
            try: os.startfile(rec.video_path)
            except Exception as e: messagebox.showerror("Error", str(e))

    def _open_single_cut(self):
        rec = self._get_selected_record()
        if not rec: return
        SingleCutModal(self, rec, self.default_out_dir, self.t, on_execute=self._execute_single_cut)

    def _execute_single_cut(self, rec, format_choice, target_folder, custom_name):
        self.default_out_dir = target_folder
        def task():
            start_t = max(0, rec.time_sec - self.sec_before)
            duration = self.sec_before + self.sec_after
            last_created = None
            if format_choice in ["16x9", "both"]:
                suffix = "_16x9" if format_choice == "both" else ""
                out_h = ClipRenderer.get_unique_filepath(target_folder, f"{custom_name}{suffix}")
                if ClipRenderer.render_clip(rec.video_path, start_t, duration, out_h, is_vertical=False, use_gpu=self.use_gpu):
                    last_created = out_h
            if format_choice in ["9x16", "both"]:
                suffix = "_Shorts_9x16" if format_choice == "both" else ""
                out_v = ClipRenderer.get_unique_filepath(target_folder, f"{custom_name}{suffix}")
                if ClipRenderer.render_clip(rec.video_path, start_t, duration, out_v, is_vertical=True, use_gpu=self.use_gpu):
                    last_created = out_v
                    
            if last_created and os.path.exists(last_created):
                messagebox.showinfo("AutoClip", f"{self.t('export_success')}\n\n📁 {target_folder}\n🎬 {os.path.basename(last_created)}")
                if self.auto_open:
                    try: subprocess.Popen(f'explorer /select,"{os.path.abspath(last_created)}"', creationflags=NO_WINDOW_FLAGS)
                    except Exception: os.startfile(target_folder)
            else:
                messagebox.showerror("Error", f"No se pudo guardar el clip en:\n{target_folder}")
        threading.Thread(target=task, daemon=True).start()

    def _open_batch(self):
        if not self.all_kills_data:
            messagebox.showwarning("Atención", "No hay bajas detectadas para exportar.")
            return
        BatchExportModal(self, len(self.all_kills_data), self.default_out_dir, self.t, on_start=self._execute_batch)

    def _execute_batch(self, out_dir, mode_choice):
        self.default_out_dir = out_dir
        def task():
            do_separate = ("Separados" in mode_choice) or ("Separate" in mode_choice) or ("Ambos" in mode_choice) or ("Both" in mode_choice)
            do_montage = ("Montaje" in mode_choice) or ("Montage" in mode_choice) or ("Ambos" in mode_choice) or ("Both" in mode_choice)
            total = len(self.all_kills_data)
            duration = self.sec_before + self.sec_after
            h_clips = []
            
            for idx, k in enumerate(self.all_kills_data):
                vname = os.path.splitext(k.video_name)[0]
                ts_str = k.timestamp.replace(":", "-")
                start_t = max(0, k.time_sec - self.sec_before)
                clean_victim = re.sub(r'[^a-zA-Z0-9]', '', k.victim)
                clean_dist = k.distance.replace('[','').replace(']','')
                base_name = f"{vname}_Baja_{ts_str}_{clean_victim}_{clean_dist}"
                
                self.lbl_status_progress.configure(text=f"Exportando [{idx+1}/{total}]: {k.timestamp}")
                out_h = ClipRenderer.get_unique_filepath(out_dir, f"{base_name}_16x9")
                if ClipRenderer.render_clip(k.video_path, start_t, duration, out_h, is_vertical=False, use_gpu=self.use_gpu):
                    h_clips.append(out_h)
                    
            if do_montage and h_clips:
                self.lbl_status_progress.configure(text="Generando vídeo recopilatorio de Highlights...")
                master_montage = ClipRenderer.get_unique_filepath(out_dir, "MONTAJE_HIGHLIGHTS_16x9")
                ClipRenderer.concatenate_clips(h_clips, master_montage)
                
            self.lbl_status_progress.configure(text=f"¡Exportación finalizada! Guardado en: {out_dir}")
            messagebox.showinfo("AutoClip", f"¡Exportación completada con éxito!\n\nCarpeta:\n{out_dir}")
            if self.auto_open:
                try: os.startfile(out_dir)
                except Exception: pass
        threading.Thread(target=task, daemon=True).start()

    def _open_html_report(self):
        if not self.all_kills_data:
            messagebox.showwarning("Atención", "No hay datos de bajas para exportar.")
            return
        HtmlReporter.generate_and_open(self.all_kills_data)