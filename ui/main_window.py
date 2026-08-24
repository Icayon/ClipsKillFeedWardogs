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
from utils.config import load_config, save_config
from utils.updater import check_github_release, CURRENT_VERSION
from i18n import Translator
from core import KillRecord, KillfeedScanner, ClipRenderer, HtmlReporter
from .theme import BG_MAIN, CARD_BG, CARD_BORDER, ACCENT_BLUE, ACCENT_CYAN, TEXT_MUTED, TEXT_LIGHT
from .components import AppHeader, QueuePanel, EventsTable, PreviewPanel
from .modals import TutorialModal, SingleCutModal, BatchExportModal, SettingsModal, InfoModal, UpdateModal, show_error

class AutoClipWardogsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        init_windows_app_id()
        
        # Cargar configuración persistente
        self.config = load_config()
        self.lang = self.config.get("language", "es")
        self.translator = Translator(self.lang)
        self.t = self.translator
        
        self.default_out_dir = self.config.get("default_out_dir", os.path.join(os.path.expanduser("~"), "Downloads", "Clips_Wardogs"))
        os.makedirs(self.default_out_dir, exist_ok=True)
        self.use_gpu = self.config.get("use_gpu", True)
        self.sec_before = self.config.get("sec_before", 7)
        self.sec_after = self.config.get("sec_after", 7)
        self.multikill_window = self.config.get("multikill_window", 15)
        self.group_multikills = self.config.get("group_multikills", True)
        self.auto_open = self.config.get("auto_open", True)
        self.auto_check_updates = bool(self.config.get("auto_check_updates", True))
        
        self.title("Clips KillFeed Wardogs by ICayon")
        self.geometry("1280x870")
        self.minsize(1100, 740)
        self.configure(fg_color=BG_MAIN)
        
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
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Comprobar actualizaciones automáticamente tras 1.5s
        self.after(1500, self._check_updates_on_startup)
        
    def _check_updates_on_startup(self):
        if self.auto_check_updates:
            threading.Thread(target=self._check_updates_thread, daemon=True).start()

    def _check_updates_thread(self):
        res = check_github_release()
        if res.get("has_update"):
            ignored = self.config.get("ignored_update_tag", "")
            if res.get("latest_tag") != ignored:
                self.after(0, lambda: self._show_startup_update_modal(res))

    def _show_startup_update_modal(self, res: dict):
        def on_never():
            self.auto_check_updates = False
            self.config["auto_check_updates"] = False
            self.config["ignored_update_tag"] = res.get("latest_tag", "")
            save_config(self.config)

        UpdateModal(
            self,
            latest_tag=res["latest_tag"],
            release_notes=res["release_notes"],
            download_url=res["download_url"],
            on_never=on_never
        )

    def _setup_ui(self):
        # 1. Header
        self.header = AppHeader(
            self, self.t, 
            on_lang_change=self._change_language,
            on_open_tutorial=self._open_tutorial,
            on_open_settings=self._open_settings
        )
        if self.lang == "en":
            self.header.lang_var.set("English")
        else:
            self.header.lang_var.set("Español")
        
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
        
        # Restaurar gamertags guardados
        saved_tags = self.config.get("gamertags", "ICayon")
        self.queue_panel.ent_gamertags.delete(0, "end")
        self.queue_panel.ent_gamertags.insert(0, saved_tags)
        
        # Auto-guardado de Gamertag en tiempo real
        self.queue_panel.ent_gamertags.bind("<KeyRelease>", self._auto_save_gamertags)
        self.queue_panel.ent_gamertags.bind("<FocusOut>", self._auto_save_gamertags)
        
        if not self.config.get("detect_audio", True):
            self.queue_panel.chk_detect_audio.deselect()
        if not self.config.get("filter_beta", True):
            self.queue_panel.chk_filter_beta.deselect()
        
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
        
        self.lbl_status_progress = ctk.CTkLabel(status_box, text=self.t("ready"), font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_MUTED)
        self.lbl_status_progress.pack(side="left")
        
        self.lbl_progress_pct = ctk.CTkLabel(status_box, text="0%", font=ctk.CTkFont(size=11), text_color=TEXT_MUTED)
        self.lbl_progress_pct.pack(side="right")
        
        self.progress_bar = ctk.CTkProgressBar(self.bottom_bar, height=6, corner_radius=3, fg_color=BG_MAIN, progress_color=ACCENT_BLUE)
        self.progress_bar.pack(fill="x", padx=18, pady=(2, 4))
        self.progress_bar.set(0)
        
        self.lbl_progress_detail = ctk.CTkLabel(self.bottom_bar, text="", font=ctk.CTkFont(size=10), text_color=TEXT_MUTED)
        self.lbl_progress_detail.pack(side="left", padx=18, pady=(0, 6))

    def _open_tutorial(self):
        TutorialModal(self, self.t)
        
    def _open_settings(self):
        SettingsModal(
            self, 
            current_out_dir=self.default_out_dir, 
            current_gpu_mode=self.use_gpu, 
            current_sec_before=self.sec_before,
            current_sec_after=self.sec_after,
            current_multikill_window=self.multikill_window,
            current_group_multikills=self.group_multikills,
            current_auto_open=self.auto_open,
            current_auto_check_updates=self.auto_check_updates,
            translator=self.t, 
            on_save=self._save_settings
        )
        
    def _save_settings(self, new_dir, new_gpu, new_before, new_after, new_multi, new_group_multikills, new_auto_open, new_auto_check_updates):
        self.default_out_dir = new_dir
        self.use_gpu = new_gpu
        self.sec_before = new_before
        self.sec_after = new_after
        self.multikill_window = new_multi
        self.group_multikills = new_group_multikills
        self.auto_open = new_auto_open
        self.auto_check_updates = new_auto_check_updates
        
        # Guardar en archivo persistente
        self.config["default_out_dir"] = self.default_out_dir
        self.config["use_gpu"] = self.use_gpu
        self.config["sec_before"] = self.sec_before
        self.config["sec_after"] = self.sec_after
        self.config["multikill_window"] = self.multikill_window
        self.config["group_multikills"] = self.group_multikills
        self.config["auto_open"] = self.auto_open
        self.config["auto_check_updates"] = self.auto_check_updates
        save_config(self.config)

    def _change_language(self, choice):
        code = "en" if "English" in choice else "es"
        self.lang = code
        self.translator.set_language(code)
        self.config["language"] = code
        save_config(self.config)
        self._refresh_all_texts()
        
    def _refresh_all_texts(self):
        self.header.refresh_texts()
        self.queue_panel.refresh_texts()
        self.events_table.refresh_headers()
        self.preview_panel.refresh_texts()
        self.lbl_status_progress.configure(text=self.t("ready"))

    def _auto_save_gamertags(self, event=None):
        tag_val = self.queue_panel.ent_gamertags.get().strip()
        if tag_val:
            self.config["gamertags"] = tag_val
            save_config(self.config)

    def _on_close(self):
        try:
            tag_val = self.queue_panel.ent_gamertags.get().strip()
            if tag_val:
                self.config["gamertags"] = tag_val
            self.config["detect_audio"] = bool(self.queue_panel.chk_detect_audio.get())
            self.config["filter_beta"] = bool(self.queue_panel.chk_filter_beta.get())
            save_config(self.config)
        except Exception:
            pass
        self.destroy()

    def _start_scan(self):
        if not self.queue_panel.video_list:
            messagebox.showwarning("Atención", "Añade al menos un vídeo a la lista para comenzar.")
            return
            
        tags_raw = self.queue_panel.ent_gamertags.get().strip()
        if not tags_raw:
            messagebox.showwarning("Atención", "Introduce tu Gamertag / Nick en el campo correspondiente.")
            return
            
        # Guardar configuración actual
        self.config["gamertags"] = tags_raw
        self.config["detect_audio"] = bool(self.queue_panel.chk_detect_audio.get())
        self.config["filter_beta"] = bool(self.queue_panel.chk_filter_beta.get())
        save_config(self.config)
        
        gamertags = [t.strip() for t in tags_raw.split(',') if t.strip()]
        detect_audio = bool(self.queue_panel.chk_detect_audio.get())
        filter_beta = bool(self.queue_panel.chk_filter_beta.get())
        
        self.is_running = True
        self.queue_panel.btn_start.configure(state="disabled")
        self.queue_panel.btn_stop.configure(state="normal")
        self.all_kills_data = []
        self.events_table.clear()
        self.preview_panel.clear()
        
        self.progress_bar.set(0)
        self.lbl_progress_pct.configure(text="0%")
        self.lbl_status_progress.configure(text=self.t("scanning"))
        
        threading.Thread(
            target=self._scan_worker, 
            args=(list(self.queue_panel.video_list), gamertags, detect_audio, filter_beta), 
            daemon=True
        ).start()

    def _stop_scan(self):
        self.is_running = False
        self.lbl_status_progress.configure(text="Deteniendo escaneo...")

    def _scan_worker(self, video_list, gamertags, detect_audio, filter_beta):
        total_videos = len(video_list)
        for v_idx, vpath in enumerate(video_list):
            if not self.is_running:
                break

            vname = os.path.basename(vpath)

            # ERR-007: archivo inaccesible
            if not os.path.exists(vpath):
                self.after(0, lambda p=vpath: show_error(self, "ERR-007", p))
                continue

            def on_prog(sec, dur, kills_found, _vidx=v_idx, _vname=vname):
                pct = 0.0
                if dur > 0:
                    video_pct = sec / float(dur)
                    pct = (_vidx + video_pct) / float(total_videos)
                else:
                    pct = (_vidx + 0.5) / float(total_videos)

                pct_clamped = min(1.0, max(0.0, pct))

                def update_gui():
                    if not self.is_running:
                        return
                    self.progress_bar.set(pct_clamped)
                    self.lbl_progress_pct.configure(text=f"{int(pct_clamped * 100)}%")
                    total_dur_str = str(timedelta(seconds=dur)) if dur > 0 else "--:--:--"
                    current_sec_str = str(timedelta(seconds=int(sec)))
                    self.lbl_status_progress.configure(
                        text=f"Analizando [{_vidx+1}/{total_videos}]: {_vname} — {current_sec_str} / {total_dur_str}"
                    )
                    self.lbl_progress_detail.configure(
                        text=f"Vídeo {_vidx+1} de {total_videos} | {kills_found} bajas detectadas"
                    )
                self.after(0, update_gui)

            def on_kill_found(rec):
                def insert_kill():
                    self.all_kills_data.append(rec)
                    row_id = f"item_{len(self.all_kills_data)}"
                    self.events_table.add_item(row_id, (rec.timestamp, rec.killer, rec.distance, rec.victim, rec.play_type, rec.hype))
                    self.events_table.update_count(len(self.all_kills_data))
                self.after(0, insert_kill)

            try:
                self.scanner.scan_video(
                    vpath, gamertags, detect_audio, filter_beta,
                    use_gpu=self.use_gpu,
                    multi_window=self.multikill_window,
                    on_progress=on_prog,
                    on_kill_found=on_kill_found,
                    is_running_check=lambda: self.is_running
                )
            except FileNotFoundError as e:
                self.after(0, lambda err=str(e): show_error(self, "ERR-003", err))
            except MemoryError as e:
                self.after(0, lambda err=str(e): show_error(self, "ERR-004", err))
            except Exception as e:
                import traceback
                detail = traceback.format_exc()[-300:]
                self.after(0, lambda err=detail: show_error(self, "ERR-010", err))

        def finish_gui():
            self.is_running = False
            self.queue_panel.btn_start.configure(state="normal")
            self.queue_panel.btn_stop.configure(state="disabled")
            self.progress_bar.set(1.0)
            self.lbl_progress_pct.configure(text="100%")
            self.lbl_status_progress.configure(text=self.t("scan_finished"))
            self.lbl_progress_detail.configure(text=f"Total: {len(self.all_kills_data)} bajas")
            messagebox.showinfo("Clips KillFeed Wardogs", f"{self.t('scan_finished')}\n\nTotal bajas detectadas: {len(self.all_kills_data)}")
        self.after(0, finish_gui)

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
            except Exception as e:
                show_error(self, "ERR-009", str(e))
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
            except Exception as e: show_error(self, "ERR-007", str(e))

    def _open_single_cut(self):
        rec = self._get_selected_record()
        if not rec: return
        SingleCutModal(self, rec, self.default_out_dir, self.t, on_execute=self._execute_single_cut)

    def _execute_single_cut(self, rec, format_choice, target_folder, custom_name):
        self.default_out_dir = target_folder
        self.config["default_out_dir"] = target_folder
        save_config(self.config)

        def task():
            try:
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
                    messagebox.showinfo("Clips KillFeed Wardogs", f"{self.t('export_success')}\n\nCarpeta: {target_folder}\nArchivo: {os.path.basename(last_created)}")
                    if self.auto_open:
                        try: subprocess.Popen(f'explorer /select,"{os.path.abspath(last_created)}"', creationflags=NO_WINDOW_FLAGS)
                        except Exception: os.startfile(target_folder)
                else:
                    self.after(0, lambda: show_error(self, "ERR-006", f"Carpeta destino: {target_folder}"))
            except PermissionError as e:
                self.after(0, lambda err=str(e): show_error(self, "ERR-011", err))
            except Exception as e:
                import traceback
                self.after(0, lambda err=traceback.format_exc()[-300:]: show_error(self, "ERR-006", err))
        threading.Thread(target=task, daemon=True).start()

    def _open_batch(self):
        if not self.all_kills_data:
            messagebox.showwarning("Atención", "No hay bajas detectadas para exportar.")
            return
        BatchExportModal(self, len(self.all_kills_data), self.default_out_dir, self.t, on_start=self._execute_batch)

    def _execute_batch(self, out_dir, mode_choice, group_multikills=True):
        self.default_out_dir = out_dir
        self.config["default_out_dir"] = out_dir
        save_config(self.config)
        
        def task():
            do_separate = ("Separados" in mode_choice) or ("Separate" in mode_choice) or ("Ambos" in mode_choice) or ("Both" in mode_choice)
            do_montage = ("Montaje" in mode_choice) or ("Montage" in mode_choice) or ("Ambos" in mode_choice) or ("Both" in mode_choice)
            h_clips = []
            
            if group_multikills:
                clusters = []
                current_cluster = []
                
                for k in self.all_kills_data:
                    if not current_cluster:
                        current_cluster.append(k)
                    else:
                        prev_k = current_cluster[-1]
                        if k.video_path == prev_k.video_path and (k.time_sec - prev_k.time_sec <= self.multikill_window):
                            current_cluster.append(k)
                        else:
                            clusters.append(current_cluster)
                            current_cluster = [k]
                if current_cluster:
                    clusters.append(current_cluster)
                    
                total = len(clusters)
                for idx, cluster in enumerate(clusters):
                    first_k = cluster[0]
                    last_k = cluster[-1]
                    vname = os.path.splitext(first_k.video_name)[0]
                    ts_str = first_k.timestamp.replace(":", "-")
                    start_t = max(0, first_k.time_sec - self.sec_before)
                    end_t = last_k.time_sec + self.sec_after
                    duration = end_t - start_t
                    
                    streak_count = len(cluster)
                    if streak_count == 1:
                        play_type = "Baja"
                    elif streak_count == 2:
                        play_type = "Doble_Baja"
                    elif streak_count == 3:
                        play_type = "Triple_Baja"
                    else:
                        play_type = f"Racha_x{streak_count}"
                        
                    clean_victims = "_".join([re.sub(r'[^a-zA-Z0-9]', '', x.victim) for x in cluster[:3]])
                    base_name = f"{vname}_{play_type}_{ts_str}_{clean_victims}"
                    
                    self.lbl_status_progress.configure(text=f"Exportando [{idx+1}/{total}]: {play_type} ({first_k.timestamp})")
                    out_h = ClipRenderer.get_unique_filepath(out_dir, f"{base_name}_16x9")
                    if ClipRenderer.render_clip(first_k.video_path, start_t, duration, out_h, is_vertical=False, use_gpu=self.use_gpu):
                        h_clips.append(out_h)
            else:
                total = len(self.all_kills_data)
                duration = self.sec_before + self.sec_after
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
                self.lbl_status_progress.configure(text="Generando vídeo recopilatorio...")
                master_montage = ClipRenderer.get_unique_filepath(out_dir, "MONTAJE_HIGHLIGHTS_16x9")
                ClipRenderer.concatenate_clips(h_clips, master_montage)
                
            self.lbl_status_progress.configure(text=f"Exportación finalizada en: {out_dir}")
            messagebox.showinfo("Clips KillFeed Wardogs", f"Exportación completada con éxito.\n\nCarpeta:\n{out_dir}")
            if self.auto_open:
                try: os.startfile(out_dir)
                except Exception: pass
        threading.Thread(target=task, daemon=True).start()

    def _open_html_report(self):
        if not self.all_kills_data:
            messagebox.showwarning("Atención", "No hay datos de bajas para exportar.")
            return
        try:
            report_path = HtmlReporter.generate_report(self.all_kills_data, self.default_out_dir)
            if report_path and os.path.exists(report_path):
                import webbrowser
                try:
                    webbrowser.open(f"file:///{os.path.abspath(report_path).replace(chr(92), '/')}")
                except Exception:
                    os.startfile(report_path)
            else:
                show_error(self, "ERR-006", "No se pudo generar el archivo del informe HTML.")
        except Exception as e:
            show_error(self, "ERR-010", str(e))