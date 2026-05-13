from __future__ import annotations

import os
import sys
import threading
import time
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any, Callable


def _process_module_1(**kwargs: Any) -> Any:
    from processor import process_file

    return process_file(**kwargs)


def _process_module_2(**kwargs: Any) -> Any:
    from processor import process_file_cuenta_fe_sin_emitir

    return process_file_cuenta_fe_sin_emitir(**kwargs)


def _process_module_3(**kwargs: Any) -> Any:
    from processor import process_file_error_fe

    return process_file_error_fe(**kwargs)


def _process_module_4(**kwargs: Any) -> Any:
    from processor import process_file_plataformas_error_fe

    return process_file_plataformas_error_fe(**kwargs)


def _process_module_5(**kwargs: Any) -> Any:
    from processor import process_file_cartera

    return process_file_cartera(**kwargs)


ProcessFunction = Callable[..., Any]


@dataclass(frozen=True)
class ModuleConfig:
    key: str
    tab_text: str
    header_title: str
    header_description: str
    process_fn: ProcessFunction
    include_alerts_in_summary: bool
    success_message: str


class AutomatizadorBIApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("ONOFF | Automatizador BI - Resoluciones FE")
        self.root.geometry("1060x650")
        self.root.minsize(960, 590)
        self.root.configure(bg="#000000")

        self.bg_color = "#000000"
        self.bg_alt = "#0B1A12"
        self.card_bg = "#101C16"
        self.border_color = "#263A2E"
        self.brand_primary = "#5DAA2F"
        self.brand_primary_hover = "#6DBE45"
        self.brand_highlight = "#8FD65A"
        self.text_primary = "#FFFFFF"
        self.text_muted = "#C8D6CE"
        self.status_default = "#C8D6CE"
        self.status_success = "#22C55E"
        self.status_warning = "#F59E0B"
        self.status_error = "#EF4444"

        self.base_dir = Path(__file__).resolve().parent
        self.runtime_dir = self._resolve_runtime_dir()
        self.resource_dir = self._resolve_resource_dir()
        self.output_dir = self.runtime_dir / "Resultados"
        self.logs_dir = self.runtime_dir / "logs"
        self.assets_dir = self.resource_dir / "assets"
        self._icon_photo: tk.PhotoImage | None = None

        self.selected_file: Path | None = None
        self.selected_file_origin = "No definido"
        self.selected_total_file: Path | None = None
        self.last_output_file: Path | None = None

        self.module_configs: dict[str, ModuleConfig] = {
            "module_1": ModuleConfig(
                key="module_1",
                tab_text="1- Base Resoluciones F.E",
                header_title="Automatizador BI - Base Resoluciones F.E",
                header_description=(
                    "Carga el reporte, procesa automaticamente las hojas RESOLUCIONES FE "
                    "y ALERTA, y descarga el resultado final."
                ),
                process_fn=_process_module_1,
                include_alerts_in_summary=True,
                success_message=(
                    "Archivo generado correctamente.\n\n"
                    "Ya puedes abrir el archivo resultado, copiar la hoja RESOLUCIONES FE "
                    "y luego la hoja ALERTA en el archivo oficial."
                ),
            ),
            "module_2": ModuleConfig(
                key="module_2",
                tab_text="2- Cuenta F.E sin emitir",
                header_title="Automatizador BI - Cuenta F.E sin emitir",
                header_description=(
                    "Carga el reporte de Cuenta F.E sin emitir, procesa automaticamente "
                    "las columnas necesarias y descarga el resultado final."
                ),
                process_fn=_process_module_2,
                include_alerts_in_summary=False,
                success_message=(
                    "Archivo generado correctamente.\n\n"
                    "Ya puedes abrir el archivo resultado, copiar los datos desde la fila 2 "
                    "y pegarlos en el archivo oficial CUENTA F.E SIN EMITIR."
                ),
            ),
            "module_3": ModuleConfig(
                key="module_3",
                tab_text="3- Error F.E",
                header_title="Automatizador BI - Error F.E",
                header_description=(
                    "Carga el resultado de CUENTA F.E SIN EMITIR, prepara la tabla "
                    "ERROR F.E y descarga el resultado final."
                ),
                process_fn=_process_module_3,
                include_alerts_in_summary=False,
                success_message=(
                    "Archivo generado correctamente.\n\n"
                    "Ya puedes abrir el archivo resultado, copiar los datos desde la fila 2 "
                    "y pegarlos en el archivo oficial ERROR F.E."
                ),
            ),
            "module_4": ModuleConfig(
                key="module_4",
                tab_text="4- Plataformas que presentan error F.E",
                header_title="Automatizador BI - Plataformas que presentan error F.E",
                header_description=(
                    "Cruza CUENTA F.E SIN EMITIR con TOTAL PLATAFORMAS F.E para generar "
                    "la lista de plataformas con error F.E."
                ),
                process_fn=_process_module_4,
                include_alerts_in_summary=False,
                success_message=(
                    "Archivo generado correctamente.\n\n"
                    "Ya puedes abrir el archivo resultado, copiar la lista desde la fila 2 "
                    "y pegarla en el archivo oficial PLATAFORMAS QUE PRESENTAN ERROR F.E."
                ),
            ),
            "module_5": ModuleConfig(
                key="module_5",
                tab_text="5- Cartera",
                header_title="Automatizador BI - Cartera",
                header_description=(
                    "Carga el archivo de Cartera, prepara la hoja CARTERA y genera "
                    "la hoja PAGO PENDIENTE."
                ),
                process_fn=_process_module_5,
                include_alerts_in_summary=False,
                success_message=(
                    "Archivo generado correctamente.\n\n"
                    "Ya puedes abrir el archivo resultado, copiar la hoja CARTERA y la hoja "
                    "PAGO PENDIENTE en el archivo oficial de Cartera."
                ),
            ),
        }
        self.current_module_key = "module_1"

        self.file_label_var = tk.StringVar(value="Archivo seleccionado")
        self.file_path_var = tk.StringVar(value="No hay archivo seleccionado")
        self.total_file_path_var = tk.StringVar(value="No hay archivo seleccionado")
        self.origin_label_var = tk.StringVar(value="Origen del archivo")
        self.file_origin_var = tk.StringVar(value="No definido")
        self.status_var = tk.StringVar(value="Esperando archivo")
        self.module_title_var = tk.StringVar()
        self.module_description_var = tk.StringVar()

        self.module_buttons: dict[str, ttk.Button] = {}
        self._is_transitioning = False

        self._configure_window_icon()
        self._configure_styles()
        self._build_widgets()
        self._activate_module("module_1", reset_state=False, animate=False)
        self._update_status_visual(self.status_var.get())

    def _resolve_runtime_dir(self) -> Path:
        if getattr(sys, "frozen", False):
            return Path(sys.executable).resolve().parent
        return self.base_dir

    def _resolve_resource_dir(self) -> Path:
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return Path(meipass)
        return self.base_dir

    def _configure_window_icon(self) -> None:
        self._set_windows_app_id()

        ico_path = self.assets_dir / "onoff_icon_app.ico"
        png_path = self.assets_dir / "onoff_icon_app.png"

        # Windows usually prefers .ico for the title bar icon.
        if ico_path.exists():
            try:
                self.root.iconbitmap(str(ico_path))
            except Exception:
                pass

        # Keep a PhotoImage reference for broader Tk compatibility.
        if png_path.exists():
            try:
                self._icon_photo = tk.PhotoImage(file=str(png_path))
                self.root.iconphoto(True, self._icon_photo)
            except Exception:
                self._icon_photo = None

    def _set_windows_app_id(self) -> None:
        if os.name != "nt":
            return
        try:
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ONOFF.AutomatizadorBI.1")
        except Exception:
            pass

    def _configure_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("App.TFrame", background=self.bg_color)
        style.configure("Card.TFrame", background=self.card_bg)

        style.configure(
            "App.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(14, 8),
            background=self.bg_alt,
            foreground="#FFFFFF",
            borderwidth=1,
            bordercolor=self.border_color,
        )
        style.map(
            "App.TButton",
            background=[("active", "#13241C"), ("disabled", "#142017")],
            foreground=[("disabled", "#7E9286")],
        )
        style.configure(
            "TabActive.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(16, 8),
            background=self.brand_primary,
            foreground="#FFFFFF",
            borderwidth=0,
        )
        style.map(
            "TabActive.TButton",
            background=[("active", self.brand_primary_hover)],
        )
        style.configure(
            "TabAvailable.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(16, 8),
            background=self.bg_alt,
            foreground="#FFFFFF",
            borderwidth=1,
            bordercolor=self.border_color,
        )
        style.map(
            "TabAvailable.TButton",
            background=[("active", "#13241C")],
        )
        style.configure(
            "TabPending.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(16, 8),
            background="#18241D",
            foreground="#7F9487",
            borderwidth=0,
        )
        style.map(
            "TabPending.TButton",
            background=[("active", "#1F2D24")],
            foreground=[("active", "#97AA9F")],
        )

        style.configure(
            "Primary.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(14, 8),
            background=self.brand_primary,
            foreground="#FFFFFF",
            borderwidth=0,
        )
        style.map(
            "Primary.TButton",
            background=[("active", self.brand_primary_hover), ("disabled", "#3F4E45")],
            foreground=[("disabled", "#90A297")],
        )

        style.configure(
            "Secondary.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(14, 8),
            background=self.bg_alt,
            foreground="#FFFFFF",
            borderwidth=1,
            bordercolor=self.border_color,
        )
        style.map(
            "Secondary.TButton",
            background=[("active", "#13241C"), ("disabled", "#142017")],
            foreground=[("disabled", "#7E9286")],
        )

        style.configure(
            "OnOff.Horizontal.TProgressbar",
            troughcolor=self.bg_alt,
            background=self.brand_primary,
            bordercolor=self.border_color,
            lightcolor=self.brand_primary_hover,
            darkcolor=self.brand_primary,
            thickness=9,
        )

    def _build_widgets(self) -> None:
        container = ttk.Frame(self.root, style="App.TFrame", padding=18)
        container.pack(fill="both", expand=True)

        tabs_frame = ttk.Frame(container, style="App.TFrame")
        tabs_frame.pack(fill="x", pady=(0, 10))

        for module_key in ("module_1", "module_2", "module_3", "module_4", "module_5"):
            module = self.module_configs[module_key]
            button = ttk.Button(
                tabs_frame,
                text=module.tab_text,
                style="TabAvailable.TButton",
                command=lambda key=module_key: self._activate_module(key, reset_state=True, animate=True),
            )
            button.pack(side="left", padx=(0 if module_key == "module_1" else 8, 0))
            self.module_buttons[module_key] = button

        hero = tk.Frame(container, bg=self.bg_color, bd=0, highlightthickness=0)
        hero.pack(fill="x", pady=(0, 14))

        hero_top = tk.Frame(hero, bg=self.bg_color)
        hero_top.pack(fill="x", padx=20, pady=(16, 6))

        tk.Label(
            hero_top,
            text="ONOFF",
            font=("Segoe UI", 10, "bold"),
            fg="#FFFFFF",
            bg=self.brand_primary,
            padx=12,
            pady=4,
        ).pack(side="left")

        tk.Label(
            hero_top,
            text="Automatizacion y control de archivos Excel",
            font=("Segoe UI", 10),
            fg=self.text_muted,
            bg=self.bg_color,
        ).pack(side="left", padx=(12, 0))

        self.hero_title_label = tk.Label(
            hero,
            textvariable=self.module_title_var,
            font=("Segoe UI", 21, "bold"),
            fg="#FFFFFF",
            bg=self.bg_color,
        )
        self.hero_title_label.pack(anchor="w", padx=20)

        self.hero_description_label = tk.Label(
            hero,
            textvariable=self.module_description_var,
            font=("Segoe UI", 10),
            fg=self.text_muted,
            bg=self.bg_color,
            wraplength=980,
            justify="left",
        )
        self.hero_description_label.pack(anchor="w", padx=20, pady=(8, 18))

        tk.Frame(hero, bg=self.brand_primary, height=2).pack(fill="x", padx=18, pady=(0, 6))
        content_shell = tk.Frame(
            container,
            bg=self.card_bg,
            bd=0,
            highlightthickness=1,
            highlightbackground=self.border_color,
            relief="flat",
        )
        content_shell.pack(fill="both", expand=True)

        content_card = ttk.Frame(content_shell, style="Card.TFrame", padding=18)
        content_card.pack(fill="both", expand=True)

        action_frame = ttk.Frame(content_card, style="Card.TFrame")
        action_frame.pack(fill="x", pady=(0, 12))

        self.take_module2_button = ttk.Button(
            action_frame,
            text="Tomar reporte modulo 2",
            command=self._take_module2_report,
            style="Secondary.TButton",
        )
        self.take_module2_button.pack(side="left")
        self.take_module2_button.pack_forget()

        self.select_button = ttk.Button(
            action_frame,
            text="Seleccionar archivo",
            command=self._select_file,
            style="App.TButton",
        )
        self.select_button.pack(side="left")

        self.select_total_button = ttk.Button(
            action_frame,
            text="Seleccionar Total Plataformas F.E",
            command=self._select_total_file,
            style="App.TButton",
        )
        self.select_total_button.pack(side="left", padx=(10, 0))
        self.select_total_button.pack_forget()

        self.process_button = ttk.Button(
            action_frame,
            text="Procesar archivo",
            command=self._process_file,
            state="disabled",
            style="Primary.TButton",
        )
        self.process_button.pack(side="left", padx=(10, 0))

        self.open_result_button = ttk.Button(
            action_frame,
            text="Abrir resultado en Excel",
            command=self._open_output_file,
            state="disabled",
            style="Secondary.TButton",
        )
        self.open_result_button.pack(side="left", padx=(10, 0))

        file_label = tk.Label(
            content_card,
            textvariable=self.file_label_var,
            font=("Segoe UI", 10, "bold"),
            fg=self.text_primary,
            bg=self.card_bg,
        )
        file_label.pack(anchor="w", pady=(8, 4))

        file_value = tk.Label(
            content_card,
            textvariable=self.file_path_var,
            wraplength=940,
            justify="left",
            font=("Segoe UI", 10),
            fg=self.text_muted,
            bg=self.card_bg,
        )
        file_value.pack(anchor="w", fill="x")

        origin_label = tk.Label(
            content_card,
            textvariable=self.origin_label_var,
            font=("Segoe UI", 10, "bold"),
            fg=self.text_primary,
            bg=self.card_bg,
        )
        origin_label.pack(anchor="w", pady=(8, 4))

        origin_value = tk.Label(
            content_card,
            textvariable=self.file_origin_var,
            wraplength=940,
            justify="left",
            font=("Segoe UI", 10),
            fg=self.text_muted,
            bg=self.card_bg,
        )
        origin_value.pack(anchor="w", fill="x")

        self.total_file_label = tk.Label(
            content_card,
            text="Archivo Total Plataformas F.E",
            font=("Segoe UI", 10, "bold"),
            fg=self.text_primary,
            bg=self.card_bg,
        )
        self.total_file_label.pack(anchor="w", pady=(8, 4))
        self.total_file_label.pack_forget()

        self.total_file_value = tk.Label(
            content_card,
            textvariable=self.total_file_path_var,
            wraplength=940,
            justify="left",
            font=("Segoe UI", 10),
            fg=self.text_muted,
            bg=self.card_bg,
        )
        self.total_file_value.pack(anchor="w", fill="x")
        self.total_file_value.pack_forget()

        status_label = tk.Label(
            content_card,
            text="Estado del procesamiento",
            font=("Segoe UI", 10, "bold"),
            fg=self.text_primary,
            bg=self.card_bg,
        )
        status_label.pack(anchor="w", pady=(14, 4))

        status_value = tk.Label(
            content_card,
            textvariable=self.status_var,
            font=("Segoe UI", 10, "bold"),
            fg="#FFFFFF",
            bg=self.bg_alt,
            padx=10,
            pady=5,
        )
        status_value.pack(anchor="w")
        self.status_value_label = status_value

        self.progressbar = ttk.Progressbar(
            content_card,
            orient="horizontal",
            mode="indeterminate",
            style="OnOff.Horizontal.TProgressbar",
        )
        self.progressbar.pack(fill="x", pady=(8, 2))

        summary_label = tk.Label(
            content_card,
            text="Resumen",
            font=("Segoe UI", 10, "bold"),
            fg=self.text_primary,
            bg=self.card_bg,
        )
        summary_label.pack(anchor="w", pady=(18, 4))

        self.summary_text = tk.Text(
            content_card,
            height=12,
            wrap="word",
            font=("Consolas", 10),
            bg=self.bg_alt,
            fg=self.text_primary,
            relief="solid",
            borderwidth=1,
            padx=12,
            pady=10,
            insertbackground=self.text_primary,
            highlightthickness=1,
            highlightbackground=self.border_color,
        )
        self.summary_text.pack(fill="both", expand=True)
        self.summary_text.configure(state="disabled")

        footer = tk.Frame(container, bg=self.bg_color)
        footer.pack(fill="x", pady=(10, 2))
        tk.Label(
            footer,
            text="Hecho por Andrex Valencia ·",
            font=("Segoe UI", 9),
            fg=self.text_muted,
            bg=self.bg_color,
        ).pack(side="right")
        tk.Label(
            footer,
            text="VibeCoder",
            font=("Segoe UI", 9, "bold"),
            fg=self.brand_primary,
            bg=self.bg_color,
            padx=6,
        ).pack(side="right")

    def _hex_to_rgb(self, color: str) -> tuple[int, int, int]:
        value = color.lstrip("#")
        return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)

    def _rgb_to_hex(self, red: int, green: int, blue: int) -> str:
        return f"#{red:02X}{green:02X}{blue:02X}"

    def _blend_colors(self, start: str, end: str, ratio: float) -> str:
        ratio = max(0.0, min(1.0, ratio))
        sr, sg, sb = self._hex_to_rgb(start)
        er, eg, eb = self._hex_to_rgb(end)
        return self._rgb_to_hex(
            int(sr + (er - sr) * ratio),
            int(sg + (eg - sg) * ratio),
            int(sb + (eb - sb) * ratio),
        )

    def _set_hero_tone(self, title_color: str, description_color: str) -> None:
        self.hero_title_label.configure(fg=title_color)
        self.hero_description_label.configure(fg=description_color)

    def _animate_module_switch(self, on_midpoint: Callable[[], None]) -> None:
        if self._is_transitioning:
            return

        self._is_transitioning = True
        dim_title = self._blend_colors(self.text_primary, self.bg_color, 0.55)
        dim_description = self._blend_colors(self.text_muted, self.bg_color, 0.55)
        fade_steps = [0.0, 0.4, 0.75, 1.0]
        step_delay_ms = 22

        def run_steps(
            steps: list[float],
            start_title: str,
            end_title: str,
            start_desc: str,
            end_desc: str,
            on_done: Callable[[], None],
        ) -> None:
            if not steps:
                on_done()
                return

            ratio = steps[0]
            self._set_hero_tone(
                self._blend_colors(start_title, end_title, ratio),
                self._blend_colors(start_desc, end_desc, ratio),
            )
            self.root.after(
                step_delay_ms,
                lambda: run_steps(steps[1:], start_title, end_title, start_desc, end_desc, on_done),
            )

        def finish() -> None:
            self._set_hero_tone(self.text_primary, self.text_muted)
            self._is_transitioning = False

        def apply_changes() -> None:
            on_midpoint()
            run_steps(
                fade_steps,
                dim_title,
                self.text_primary,
                dim_description,
                self.text_muted,
                finish,
            )

        run_steps(
            fade_steps,
            self.text_primary,
            dim_title,
            self.text_muted,
            dim_description,
            apply_changes,
        )

    def _activate_module(
        self,
        module_key: str,
        reset_state: bool,
        animate: bool = False,
        _from_transition: bool = False,
    ) -> None:
        if self._is_transitioning and not _from_transition:
            return

        if animate and not _from_transition:
            self._animate_module_switch(
                lambda: self._activate_module(
                    module_key,
                    reset_state=reset_state,
                    animate=False,
                    _from_transition=True,
                )
            )
            return

        module = self.module_configs[module_key]
        self.current_module_key = module_key

        self.root.title(f"ONOFF | {module.header_title}")
        self.module_title_var.set(module.header_title)
        self.module_description_var.set(module.header_description)

        for key, button in self.module_buttons.items():
            button.configure(style="TabActive.TButton" if key == module_key else "TabAvailable.TButton")

        if reset_state:
            self.selected_file = None
            self.selected_file_origin = "No definido"
            self.selected_total_file = None
            self.last_output_file = None
            self.file_path_var.set("No hay archivo seleccionado")
            self.total_file_path_var.set("No hay archivo seleccionado")
            self.file_origin_var.set("No definido")
            self._update_status_visual("Esperando archivo")
            self._write_summary("")
            self.open_result_button.configure(state="disabled")

        if module_key in {"module_3", "module_4"}:
            self.take_module2_button.pack(side="left", before=self.select_button)
        else:
            self.take_module2_button.pack_forget()

        if module_key == "module_4":
            self.select_button.configure(text="Seleccionar Cuenta F.E sin emitir")
            self.select_total_button.pack(side="left", padx=(10, 0), before=self.process_button)
            self.file_label_var.set("Archivo Cuenta F.E sin emitir")
            self.origin_label_var.set("Origen Cuenta F.E")
            self.total_file_label.pack(anchor="w", pady=(8, 4))
            self.total_file_value.pack(anchor="w", fill="x")
        elif module_key == "module_5":
            self.select_button.configure(text="Seleccionar archivo de Cartera")
            self.select_total_button.pack_forget()
            self.total_file_label.pack_forget()
            self.total_file_value.pack_forget()
            self.file_label_var.set("Archivo de Cartera")
            self.origin_label_var.set("Origen del archivo")
        else:
            self.select_button.configure(text="Seleccionar archivo")
            self.select_total_button.pack_forget()
            self.total_file_label.pack_forget()
            self.total_file_value.pack_forget()
            self.file_label_var.set("Archivo seleccionado")
            self.origin_label_var.set("Origen del archivo")

        self._refresh_process_button_state()

    def _select_file(self) -> None:
        title = "Selecciona el archivo de entrada"
        if self.current_module_key == "module_4":
            title = "Selecciona el archivo CUENTA F.E SIN EMITIR"
        elif self.current_module_key == "module_5":
            title = "Selecciona el archivo de Cartera"

        file_path = filedialog.askopenfilename(
            title=title,
            filetypes=[
                ("Archivos soportados", "*.csv *.txt *.xlsx *.xlsm"),
                ("CSV", "*.csv"),
                ("TXT", "*.txt"),
                ("Excel", "*.xlsx *.xlsm"),
                ("Todos", "*.*"),
            ],
        )

        if not file_path:
            return

        self.selected_file = Path(file_path)
        self.selected_file_origin = "Seleccionado manualmente"
        self.file_path_var.set(str(self.selected_file))
        self.file_origin_var.set(self.selected_file_origin)
        if self.current_module_key == "module_4":
            self._update_status_visual("Archivo Cuenta F.E sin emitir cargado correctamente.")
        elif self.current_module_key == "module_5":
            self._update_status_visual("Archivo de Cartera cargado correctamente.")
        else:
            self._update_status_visual("Archivo cargado correctamente.")
        self._refresh_process_button_state()

    def _select_total_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Selecciona el archivo TOTAL PLATAFORMAS F.E",
            filetypes=[
                ("Archivos soportados", "*.csv *.txt *.xlsx *.xlsm"),
                ("CSV", "*.csv"),
                ("TXT", "*.txt"),
                ("Excel", "*.xlsx *.xlsm"),
                ("Todos", "*.*"),
            ],
        )

        if not file_path:
            return

        self.selected_total_file = Path(file_path)
        self.total_file_path_var.set(str(self.selected_total_file))
        self._update_status_visual("Archivo Total Plataformas F.E cargado correctamente.")
        self._refresh_process_button_state()

    def _take_module2_report(self) -> None:
        candidates: dict[Path, float] = {}
        for pattern in ("2-RESULTADO_CUENTA_FE_SIN_EMITIR_*.xlsx", "RESULTADO_CUENTA_FE_SIN_EMITIR_*.xlsx"):
            for path in self.output_dir.rglob(pattern):
                try:
                    candidates[path] = path.stat().st_mtime
                except OSError:
                    continue

        candidate_files = [path for path, _ in sorted(candidates.items(), key=lambda item: item[1], reverse=True)]

        if not candidate_files:
            messagebox.showwarning(
                "Sin reporte de modulo 2",
                "No se encontro un resultado del modulo 2. Genera primero el modulo 2 o selecciona el archivo manualmente.",
            )
            return

        self.selected_file = candidate_files[0]
        self.selected_file_origin = "Tomado automaticamente del modulo 2"
        self.file_path_var.set(str(self.selected_file))
        self.file_origin_var.set(self.selected_file_origin)
        self._update_status_visual("Reporte del modulo 2 cargado correctamente.")
        self._refresh_process_button_state()

    def _process_file(self) -> None:
        if self.current_module_key == "module_4":
            if not self.selected_file:
                messagebox.showwarning(
                    "Falta archivo",
                    "Primero debes tomar el reporte del modulo 2 o seleccionar el archivo CUENTA F.E SIN EMITIR.",
                )
                return
            if not self.selected_total_file:
                messagebox.showwarning(
                    "Falta archivo",
                    "Primero debes seleccionar el archivo TOTAL PLATAFORMAS F.E.",
                )
                return

        if not self.selected_file:
            if self.current_module_key == "module_3":
                messagebox.showwarning(
                    "Falta archivo",
                    "Primero debes tomar el reporte del modulo 2 o seleccionar un archivo.",
                )
            elif self.current_module_key == "module_5":
                messagebox.showwarning("Falta archivo", "Primero debes seleccionar el archivo de Cartera.")
            else:
                messagebox.showwarning("Falta archivo", "Selecciona un archivo antes de procesar.")
            return

        self._set_controls_during_processing(False)
        self._set_status("Procesando...")
        self._write_summary("")

        worker = threading.Thread(target=self._run_processing_worker, daemon=True)
        worker.start()

    def _run_processing_worker(self) -> None:
        assert self.selected_file is not None
        current_module = self.module_configs[self.current_module_key]
        start_time = time.perf_counter()

        try:
            if self.current_module_key == "module_4":
                assert self.selected_total_file is not None
                summary = current_module.process_fn(
                    cuenta_input_path=self.selected_file,
                    total_input_path=self.selected_total_file,
                    output_dir=self.output_dir,
                    logs_dir=self.logs_dir,
                    status_callback=self._set_status,
                    source_origin=self.selected_file_origin,
                )
            else:
                summary = current_module.process_fn(
                    input_path=self.selected_file,
                    output_dir=self.output_dir,
                    logs_dir=self.logs_dir,
                    status_callback=self._set_status,
                    source_origin=self.selected_file_origin,
                )
            elapsed_seconds = time.perf_counter() - start_time
            self.root.after(0, lambda: self._handle_success(summary, current_module, elapsed_seconds))
        except Exception as exc:
            message = str(exc).strip() or "Ocurrio un error inesperado durante el proceso."
            self.root.after(0, lambda: self._handle_error(message))
        finally:
            self.root.after(0, lambda: self._set_controls_during_processing(True))

    def _handle_success(self, summary: Any, module: ModuleConfig, elapsed_seconds: float) -> None:
        self.last_output_file = summary.output_path
        self.open_result_button.configure(state="normal")
        duration_line = f"Tiempo de procesamiento: {self._format_duration(elapsed_seconds)}"

        if self.current_module_key == "module_4" and summary.extra_metrics:
            summary_lines = [
                f"Total plataformas en Cuenta F.E sin emitir: {summary.extra_metrics['cuenta_rows']}",
                f"Total plataformas unicas en Cuenta F.E sin emitir: {summary.extra_metrics['cuenta_unique']}",
                f"Total plataformas en Total Plataformas F.E: {summary.extra_metrics['total_rows']}",
                f"Total plataformas con error encontradas: {summary.extra_metrics['matched_unique']}",
                f"Origen Cuenta F.E: {self.selected_file_origin}",
                duration_line,
                f"Ruta del archivo generado: {summary.output_path}",
                f"Ruta del log: {summary.log_path}",
            ]
        elif self.current_module_key == "module_5" and summary.extra_metrics:
            summary_lines = [
                f"Total registros en CARTERA: {summary.extra_metrics['cartera_rows']}",
                f"Total plataformas con pago pendiente: {summary.extra_metrics['pending_rows']}",
                duration_line,
                f"Ruta del archivo generado: {summary.output_path}",
                f"Ruta del log: {summary.log_path}",
            ]
            if summary.extra_metrics["pending_rows"] == 0:
                summary_lines.append(
                    "No se encontraron registros con ESTADO_DE_PAGO igual a PENDIENTE. "
                    "Se genero la hoja PAGO PENDIENTE solo con encabezados."
                )
        else:
            summary_lines = [
                f"Total de registros procesados: {summary.rows_output}",
                f"Origen del archivo usado: {self.selected_file_origin}",
                duration_line,
                f"Ruta del archivo generado: {summary.output_path}",
                f"Ruta del log: {summary.log_path}",
            ]
            if module.include_alerts_in_summary:
                summary_lines.insert(1, f"Total de alertas encontradas: {summary.alerts_count}")

        self._write_summary("\n".join(summary_lines))
        self._set_status("Archivo generado correctamente")

        try:
            os.startfile(str(summary.output_path))
        except OSError:
            messagebox.showwarning(
                "Apertura automatica no disponible",
                "El archivo fue generado, pero no se pudo abrir automaticamente en Excel.",
            )

        messagebox.showinfo("Proceso finalizado", module.success_message)

    def _handle_error(self, message: str) -> None:
        self._set_status("No se pudo completar el proceso")
        self._write_summary(message)
        messagebox.showerror("Error", message)

    def _open_output_file(self) -> None:
        if not self.last_output_file:
            if self.current_module_key == "module_5":
                messagebox.showwarning(
                    "Sin resultado",
                    "Primero debes procesar el archivo de Cartera para generar el resultado.",
                )
            else:
                messagebox.showwarning("Sin resultado", "Primero procesa un archivo para generar el resultado.")
            return
        try:
            os.startfile(str(self.last_output_file))
        except OSError:
            messagebox.showerror("Error", "No se pudo abrir el archivo resultado en Excel.")

    def _show_automating_message(self, module_name: str) -> None:
        messagebox.showinfo(module_name, "AUTOMATIZANDO")

    def _set_controls_during_processing(self, enabled: bool) -> None:
        self.select_button.configure(state="normal" if enabled else "disabled")
        if self.current_module_key in {"module_3", "module_4"}:
            self.take_module2_button.configure(state="normal" if enabled else "disabled")
        else:
            self.take_module2_button.configure(state="disabled")
        if self.current_module_key == "module_4":
            self.select_total_button.configure(state="normal" if enabled else "disabled")
        else:
            self.select_total_button.configure(state="disabled")
        self.open_result_button.configure(state="normal" if enabled and self.last_output_file else "disabled")
        if enabled:
            self.progressbar.stop()
            self._refresh_process_button_state()
        else:
            self.progressbar.start(10)
            self.process_button.configure(state="disabled")

    def _set_status(self, message: str) -> None:
        self.root.after(0, lambda: self._update_status_visual(message))

    def _write_summary(self, message: str) -> None:
        self.summary_text.configure(state="normal")
        self.summary_text.delete("1.0", "end")
        if message:
            self.summary_text.insert("1.0", message)
        self.summary_text.configure(state="disabled")

    def _refresh_process_button_state(self) -> None:
        if self.current_module_key == "module_4":
            can_process = self.selected_file is not None and self.selected_total_file is not None
        else:
            can_process = self.selected_file is not None
        self.process_button.configure(state="normal" if can_process else "disabled")

    def _format_duration(self, elapsed_seconds: float) -> str:
        elapsed_seconds = max(0.0, elapsed_seconds)
        minutes = int(elapsed_seconds // 60)
        seconds = elapsed_seconds - (minutes * 60)
        if minutes > 0:
            return f"{minutes} min {seconds:05.2f} s"
        return f"{seconds:.2f} s"

    def _update_status_visual(self, message: str) -> None:
        self.status_var.set(message)
        tone_bg = self.bg_alt
        tone_fg = "#FFFFFF"
        normalized = message.strip().upper()

        if "ERROR" in normalized or "NO SE PUDO" in normalized:
            tone_bg = self.status_error
        elif "ADVERTENCIA" in normalized or "NO SE ENCONTR" in normalized:
            tone_bg = self.status_warning
        elif "PROCESANDO" in normalized:
            tone_bg = self.brand_primary
        elif "VALIDANDO" in normalized:
            tone_bg = self.brand_highlight
            tone_fg = "#0B1A12"
        elif "CORRECTAMENTE" in normalized or "COMPLETADO" in normalized or "CARGADO" in normalized:
            tone_bg = self.status_success

        self.status_value_label.configure(bg=tone_bg, fg=tone_fg)
