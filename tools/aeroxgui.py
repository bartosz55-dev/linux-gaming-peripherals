#!/usr/bin/env python3
"""
aeroxgui - SteelSeries Aerox 3 Wireless Control Center for Linux
Nowoczesny, natywny panel kontrolny w stylu SteelSeries GG / Engine
dla myszek SteelSeries Aerox 3 Wireless i Wired.

Funkcjonalności:
  - Odczyt poziomu baterii z animowanym wskaźnikiem i wykrywaniem ładowania
  - Wizualny podgląd myszy Aerox 3 (plaster miodu / honeycomb mesh)
  - Niezależne sterowanie 3 strefami RGB (góra, środek, dół)
  - Efekt Rainbow Wave i podświetlenie reaktywne
  - 5 konfigurowalnych poziomów czułości CPI/DPI (TrueMove Air: 100-18000 DPI)
  - Zmiana częstotliwości próbkowania USB (125, 250, 500, 1000 Hz)
  - Ustawienia oszczędzania energii: Sleep Timer i Dim Timer
  - Bezpośredni zapis do wbudowanej pamięci myszy (Onboard Memory)
  - Odporność na brak uprawnień z automatycznym asystentem udev
"""

import os
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from typing import Dict, List, Tuple, Optional

# Dołącz lokalną bibliotekę aeroxctl
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS_DIR)
from aeroxctl import AeroxMouse, NAMED_COLORS, TRUEMOVE_AIR_DPI, POLLING_RATES

# --- MOTYW STEELSERIES DARK / ORANGE ---
THEME = {
    "bg_main":       "#121316",  # Głęboki ciemny grafit
    "bg_card":       "#1C1D24",  # Karty paneli
    "bg_card_dark":  "#16171D",  # Pola wewnętrzne kart
    "border":        "#2A2C37",  # Subtelna ramka
    "accent":        "#FF5200",  # Legendarny SteelSeries Orange
    "accent_hover":  "#FF6E26",  # Jaśniejszy pomarańcz
    "accent_dim":    "#9E3300",  # Przyciemniony akcent
    "text_primary":  "#F0F1F5",  # Czysta biel
    "text_muted":    "#8E92A4",  # Przygaszony szary
    "text_dim":      "#5E6272",  # Ciemny szary
    "success":       "#00E676",  # Zielony wskaźnik
    "warning":       "#FFD600",  # Żółty
    "danger":        "#FF1744",  # Czerwony
    "mesh_hole":     "#0D0E11",  # Otwory w obudowie
}

# Paleta szybkich kolorów RGB
QUICK_COLORS = [
    ("#FF5200", "SteelSeries Orange"),
    ("#00E5FF", "Cyber Cyan"),
    ("#FF1744", "Neon Red"),
    ("#00E676", "Neon Lime"),
    ("#7C4DFF", "Electric Violet"),
    ("#FFEA00", "Bright Yellow"),
    ("#FFFFFF", "Pure White"),
    ("#000000", "LED Off"),
]


class AeroxGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SteelSeries Aerox 3 Control Center")
        self.geometry("1060x720")
        self.minsize(1000, 680)
        self.configure(bg=THEME["bg_main"])

        # Inicjalizacja sterownika myszy
        self.mouse: Optional[AeroxMouse] = None
        self.mouse_connected = False
        self.mouse_wireless = False
        self.battery_level = 0
        self.is_charging = False
        self.perm_error = False

        # Stan konfiguracji myszy
        self.zone_colors = [
            "#FF5200",  # Z1 Góra
            "#FF5200",  # Z2 Środek
            "#FF5200",  # Z3 Dół
        ]
        self.selected_zone = 0  # 0: Wszystkie, 1: Z1, 2: Z2, 3: Z3
        self.is_rainbow = False
        self.is_reactive = False

        self.dpi_presets = [400, 800, 1200, 2400, 3200]
        self.active_dpi_idx = tk.IntVar(value=1)  # Domyślnie profil 2 (800 DPI)
        self.dpi_vars = [tk.IntVar(value=dpi) for dpi in self.dpi_presets]

        self.polling_rate_var = tk.IntVar(value=1000)
        self.sleep_timer_var = tk.IntVar(value=5)
        self.dim_timer_var = tk.IntVar(value=30)

        # Inicjalizacja komponentów GUI
        self._setup_styles()
        self._build_header()
        self._build_main_content()
        self._build_footer()

        # Pierwsze połączenie z myszką
        self._connect_mouse()

        # Automatyczne odświeżanie baterii w tle co 30 sekund
        self._schedule_battery_refresh()

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        # Styl suwaków
        style.configure("Horizontal.TScale",
                        background=THEME["bg_card"],
                        troughcolor=THEME["bg_card_dark"],
                        sliderthickness=14,
                        sliderrelief="flat")
        style.map("Horizontal.TScale",
                  background=[("active", THEME["accent"])])

        # Styl radiobuttonów
        style.configure("TRadiobutton",
                        background=THEME["bg_card"],
                        foreground=THEME["text_primary"],
                        font=("Segoe UI", 9, "bold"))
        style.map("TRadiobutton",
                  background=[("active", THEME["bg_card"])],
                  foreground=[("active", THEME["accent"])])

    # =========================================================================
    # GŁÓWNY NAGŁÓWEK (HEADER)
    # =========================================================================
    def _build_header(self):
        header_frame = tk.Frame(self, bg=THEME["bg_card"], height=64, padx=20)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)

        # Ramka dolna nagłówka
        tk.Frame(self, bg=THEME["border"], height=1).pack(fill="x", side="top")

        # Lewo: Stylizowane logo i nazwa
        left_box = tk.Frame(header_frame, bg=THEME["bg_card"])
        left_box.pack(side="left", fill="y", pady=12)

        # Ikonka tarczy SteelSeries (rysujemy na minicanvasie)
        logo_cv = tk.Canvas(left_box, width=28, height=28, bg=THEME["bg_card"], highlightthickness=0)
        logo_cv.pack(side="left", padx=(0, 10))
        # Okrąg zewnętrzny i wewnętrzny
        logo_cv.create_oval(2, 2, 26, 26, outline=THEME["accent"], width=3)
        logo_cv.create_oval(8, 8, 20, 20, fill=THEME["accent"], outline="")

        title_lbl = tk.Label(left_box, text="STEELSERIES", font=("Segoe UI", 12, "bold"),
                             fg=THEME["text_primary"], bg=THEME["bg_card"])
        title_lbl.pack(side="left")

        subtitle_lbl = tk.Label(left_box, text=" AEROX 3 WIRELESS", font=("Segoe UI", 12, "bold"),
                                fg=THEME["accent"], bg=THEME["bg_card"])
        subtitle_lbl.pack(side="left")

        # Środek: Plakietka połączenia
        self.conn_pill = tk.Label(header_frame, text="SPRAWDZANIE...",
                                  font=("Segoe UI", 8, "bold"),
                                  fg=THEME["text_muted"], bg=THEME["bg_card_dark"],
                                  padx=12, pady=4, relief="flat")
        self.conn_pill.pack(side="left", padx=30, pady=16)

        # Prawo: Bateria i przycisk odświeżenia
        right_box = tk.Frame(header_frame, bg=THEME["bg_card"])
        right_box.pack(side="right", fill="y", pady=12)

        # Wizualny wskaźnik baterii
        self.battery_canvas = tk.Canvas(right_box, width=44, height=20, bg=THEME["bg_card"], highlightthickness=0)
        self.battery_canvas.pack(side="left", padx=(0, 8))
        self._draw_battery_icon(0, False)

        self.battery_lbl = tk.Label(right_box, text="-- %", font=("Segoe UI", 10, "bold"),
                                    fg=THEME["text_primary"], bg=THEME["bg_card"])
        self.battery_lbl.pack(side="left", padx=(0, 12))

        refresh_btn = tk.Button(right_box, text="⟳ Odśwież", font=("Segoe UI", 9),
                                bg=THEME["bg_card_dark"], fg=THEME["text_primary"],
                                activebackground=THEME["border"], activeforeground=THEME["text_primary"],
                                relief="flat", padx=10, pady=3, cursor="hand2",
                                command=self._on_refresh_status)
        refresh_btn.pack(side="left")

    def _draw_battery_icon(self, level: int, is_charging: bool):
        cv = self.battery_canvas
        cv.delete("all")

        # Obrys baterii
        cv.create_rectangle(2, 3, 38, 17, outline=THEME["text_muted"], width=1)
        # Biegun baterii
        cv.create_rectangle(38, 6, 41, 14, fill=THEME["text_muted"], outline="")

        if level > 0:
            fill_width = int((level / 100.0) * 32)
            color = THEME["success"] if level > 25 else (THEME["warning"] if level > 10 else THEME["danger"])
            cv.create_rectangle(4, 5, 4 + fill_width, 15, fill=color, outline="")

        if is_charging:
            # Błyskawica ładowania
            cv.create_polygon(20, 4, 15, 11, 19, 11, 17, 16, 24, 9, 20, 9,
                               fill="#FFFFFF", outline="")

    # =========================================================================
    # GŁÓWNA ZAWARTOŚĆ (DWIE KOLUMNY)
    # =========================================================================
    def _build_main_content(self):
        container = tk.Frame(self, bg=THEME["bg_main"], padx=20, pady=15)
        container.pack(fill="both", expand=True)

        # Lewa kolumna: RGB i Mysz (szerokość 420px)
        left_col = tk.Frame(container, bg=THEME["bg_card"], width=420)
        left_col.pack(side="left", fill="both", padx=(0, 12))
        left_col.pack_propagate(False)
        self._build_rgb_panel(left_col)

        # Prawa kolumna: Wydajność (DPI, Polling, Zasilanie)
        right_col = tk.Frame(container, bg=THEME["bg_main"])
        right_col.pack(side="right", fill="both", expand=True)
        self._build_performance_panel(right_col)

    # -------------------------------------------------------------------------
    # PANEL LEWY: PRISM RGB & WIZUALIZACJA MYSZY
    # -------------------------------------------------------------------------
    def _build_rgb_panel(self, parent):
        p = tk.Frame(parent, bg=THEME["bg_card"], padx=16, pady=16)
        p.pack(fill="both", expand=True)

        header = tk.Label(p, text="PODŚWIETLENIE PRISM RGB", font=("Segoe UI", 11, "bold"),
                          fg=THEME["text_primary"], bg=THEME["bg_card"])
        header.pack(anchor="w", pady=(0, 10))

        # Canvas z podglądem myszy Aerox 3
        self.mouse_cv = tk.Canvas(p, width=380, height=270, bg=THEME["bg_card_dark"],
                                  highlightthickness=1, highlightbackground=THEME["border"])
        self.mouse_cv.pack(fill="x", pady=(0, 12))
        self.mouse_cv.bind("<Button-1>", self._on_canvas_click)

        self._draw_aerox_mouse()

        # Przełączniki stref
        zones_frame = tk.Frame(p, bg=THEME["bg_card"])
        zones_frame.pack(fill="x", pady=(0, 10))

        self.zone_btns = []
        zone_titles = ["Wszystkie Strefy", "Góra (Z1)", "Środek (Z2)", "Dół (Z3)"]
        for idx, title in enumerate(zone_titles):
            b = tk.Button(zones_frame, text=title, font=("Segoe UI", 8, "bold"),
                          bg=THEME["accent"] if idx == 0 else THEME["bg_card_dark"],
                          fg=THEME["text_primary"], relief="flat", padx=6, pady=4, cursor="hand2",
                          command=lambda i=idx: self._select_zone(i))
            b.pack(side="left", expand=True, fill="x", padx=1)
            self.zone_btns.append(b)

        # Paleta kolorów
        pal_frame = tk.Frame(p, bg=THEME["bg_card"])
        pal_frame.pack(fill="x", pady=(0, 12))

        tk.Label(pal_frame, text="Szybki wybór barwy:", font=("Segoe UI", 9),
                 fg=THEME["text_muted"], bg=THEME["bg_card"]).pack(anchor="w", pady=(0, 6))

        swatches_row = tk.Frame(pal_frame, bg=THEME["bg_card"])
        swatches_row.pack(fill="x")

        for color_hex, name in QUICK_COLORS:
            btn = tk.Button(swatches_row, bg=color_hex, width=3, height=1, relief="flat",
                            activebackground=color_hex, cursor="hand2",
                            highlightthickness=1, highlightbackground=THEME["border"],
                            command=lambda c=color_hex: self._apply_color(c))
            btn.pack(side="left", padx=2, expand=True)

        # Własny kolor (Color Picker)
        custom_row = tk.Frame(p, bg=THEME["bg_card"])
        custom_row.pack(fill="x", pady=(0, 12))

        custom_btn = tk.Button(custom_row, text="🎨 Własny Kolor (Paleta)...", font=("Segoe UI", 9, "bold"),
                               bg=THEME["bg_card_dark"], fg=THEME["text_primary"], relief="flat",
                               padx=10, pady=5, cursor="hand2", command=self._pick_custom_color)
        custom_btn.pack(fill="x")

        # Przełączniki efektów specjalnych (Rainbow & Reaktywne)
        effects_box = tk.Frame(p, bg=THEME["bg_card_dark"], padx=10, pady=10)
        effects_box.pack(fill="x")

        self.rainbow_btn = tk.Button(effects_box, text="🌈 Efekt Tęczy (Rainbow Wave): WYŁ.",
                                     font=("Segoe UI", 9, "bold"),
                                     bg=THEME["bg_card"], fg=THEME["text_muted"], relief="flat",
                                     padx=10, pady=5, cursor="hand2", command=self._toggle_rainbow)
        self.rainbow_btn.pack(fill="x", pady=(0, 6))

        self.reactive_btn = tk.Button(effects_box, text="⚡ Podświetlenie Reaktywne: WYŁ.",
                                      font=("Segoe UI", 9, "bold"),
                                      bg=THEME["bg_card"], fg=THEME["text_muted"], relief="flat",
                                      padx=10, pady=5, cursor="hand2", command=self._toggle_reactive)
        self.reactive_btn.pack(fill="x")

    def _draw_aerox_mouse(self):
        cv = self.mouse_cv
        cv.delete("all")
        cx, cy = 190, 135

        # Kolory aktualnych stref
        c_top = self.zone_colors[0] if not self.is_rainbow else "#00E5FF"
        c_mid = self.zone_colors[1] if not self.is_rainbow else "#FF5200"
        c_bot = self.zone_colors[2] if not self.is_rainbow else "#7C4DFF"

        # Tło blasku pod myszką (Dolna strefa Z3)
        cv.create_oval(cx - 75, cy + 50, cx + 75, cy + 115, fill=c_bot, outline="", tags="z3_glow", stipple="gray50")

        # Zarys sylwetki myszy Aerox 3
        mouse_body = [
            cx - 50, cy - 90,
            cx - 55, cy - 40,
            cx - 58, cy + 20,
            cx - 52, cy + 80,
            cx - 30, cy + 105,
            cx + 30, cy + 105,
            cx + 52, cy + 80,
            cx + 58, cy + 20,
            cx + 55, cy - 40,
            cx + 50, cy - 90,
            cx + 25, cy - 100,
            cx - 25, cy - 100,
        ]
        cv.create_polygon(mouse_body, fill="#1C1E24", outline=THEME["border"], width=2, smooth=True)

        # Wewnętrzne strefy RGB (Glow)
        # Z1: Górna strefa (pod rolką)
        cv.create_oval(cx - 20, cy - 85, cx + 20, cy - 35, fill=c_top, outline="", tags=("zone0", "zone_item"))

        # Z2: Środkowa strefa (wnętrze korpusu)
        cv.create_oval(cx - 35, cy - 25, cx + 35, cy + 45, fill=c_mid, outline="", tags=("zone1", "zone_item"))

        # Z3: Dolna listwa (dyfuzor na dole korpusu)
        cv.create_arc(cx - 45, cy + 40, cx + 45, cy + 102, start=200, extent=140,
                      outline=c_bot, width=6, style="arc", tags=("zone2", "zone_item"))

        # Ażurowa perforacja "Plaster Miodu" (Aerox Honeycomb Holes)
        for row in range(-2, 4):
            for col in range(-2, 3):
                hx = cx + col * 16 + (8 if row % 2 else 0)
                hy = cy + row * 15
                # Ograniczenie siatki do wnętrza korpusu
                if abs(col) <= 1 or (row in (-1, 0, 1) and abs(col) <= 2):
                    cv.create_polygon(
                        hx, hy - 4,
                        hx + 4, hy - 2,
                        hx + 4, hy + 2,
                        hx, hy + 4,
                        hx - 4, hy + 2,
                        hx - 4, hy - 2,
                        fill=THEME["mesh_hole"], outline="#2D303E", width=1
                    )

        # Przyciski główne i rolka
        # Podziałka przycisków lewy/prawy
        cv.create_line(cx, cy - 100, cx, cy - 40, fill="#2A2C37", width=2)

        # Rolka przewijania (Scroll Wheel)
        cv.create_rectangle(cx - 6, cy - 85, cx + 6, cy - 50, fill="#121316", outline=c_top, width=2)
        # Prążki na rolce
        for ry in range(cy - 80, cy - 50, 7):
            cv.create_line(cx - 5, ry, cx + 5, ry, fill=THEME["text_muted"])

        # Przycisk zmiany DPI za rolką
        cv.create_rectangle(cx - 4, cy - 42, cx + 4, cy - 32, fill="#2A2C37", outline="#404456", width=1)

        # Etykiety informacyjne stref
        cv.create_text(cx - 95, cy - 70, text="Strefa 1 (Góra)", fill=THEME["text_muted"], font=("Segoe UI", 8), anchor="e")
        cv.create_line(cx - 90, cy - 70, cx - 22, cy - 70, fill=THEME["border"], dash=(2, 2))

        cv.create_text(cx + 95, cy + 10, text="Strefa 2 (Środek)", fill=THEME["text_muted"], font=("Segoe UI", 8), anchor="w")
        cv.create_line(cx + 90, cy + 10, cx + 38, cy + 10, fill=THEME["border"], dash=(2, 2))

        cv.create_text(cx - 95, cy + 85, text="Strefa 3 (Dół)", fill=THEME["text_muted"], font=("Segoe UI", 8), anchor="e")
        cv.create_line(cx - 90, cy + 85, cx - 40, cy + 85, fill=THEME["border"], dash=(2, 2))

    def _on_canvas_click(self, event):
        # Kliknięcie w canvas pozwala szybko wybrać odpowiednią strefę
        y = event.y
        if y < 100:
            self._select_zone(1)
        elif y < 180:
            self._select_zone(2)
        else:
            self._select_zone(3)

    def _select_zone(self, idx: int):
        self.selected_zone = idx
        for i, btn in enumerate(self.zone_btns):
            if i == idx:
                btn.configure(bg=THEME["accent"], fg=THEME["text_primary"])
            else:
                btn.configure(bg=THEME["bg_card_dark"], fg=THEME["text_muted"])

    def _apply_color(self, hex_color: str):
        self.is_rainbow = False
        self.rainbow_btn.configure(text="🌈 Efekt Tęczy: WYŁ.", bg=THEME["bg_card"], fg=THEME["text_muted"])

        if self.selected_zone == 0:
            # Wszystkie strefy
            for i in range(3):
                self.zone_colors[i] = hex_color
            if self.mouse_connected and self.mouse:
                r, g, b = self._hex_to_rgb(hex_color)
                self.mouse.set_all_colors(r, g, b)
        else:
            zone_idx = self.selected_zone - 1
            self.zone_colors[zone_idx] = hex_color
            if self.mouse_connected and self.mouse:
                r, g, b = self._hex_to_rgb(hex_color)
                self.mouse.set_zone_color(zone_idx, r, g, b)

        self._draw_aerox_mouse()
        self._set_status(f"Zastosowano kolor {hex_color} dla strefy: {self.zone_btns[self.selected_zone].cget('text')}")

    def _pick_custom_color(self):
        curr = self.zone_colors[max(0, self.selected_zone - 1)]
        color = colorchooser.askcolor(initialcolor=curr, title="Wybierz kolor podświetlenia Aerox 3")
        if color and color[1]:
            self._apply_color(color[1].upper())

    def _toggle_rainbow(self):
        self.is_rainbow = not self.is_rainbow
        if self.is_rainbow:
            self.rainbow_btn.configure(text="🌈 Efekt Tęczy: WŁĄCZONY", bg=THEME["accent"], fg=THEME["text_primary"])
            if self.mouse_connected and self.mouse:
                self.mouse.set_rainbow()
            self._set_status("Włączono efekt wielokolorowej tęczy (Rainbow Wave)")
        else:
            self.rainbow_btn.configure(text="🌈 Efekt Tęczy: WYŁ.", bg=THEME["bg_card"], fg=THEME["text_muted"])
            # Przywróć poprzednie barwy stref
            for z in range(3):
                r, g, b = self._hex_to_rgb(self.zone_colors[z])
                if self.mouse_connected and self.mouse:
                    self.mouse.set_zone_color(z, r, g, b)
        self._draw_aerox_mouse()

    def _toggle_reactive(self):
        self.is_reactive = not self.is_reactive
        if self.is_reactive:
            self.reactive_btn.configure(text="⚡ Podświetlenie Reaktywne: WŁĄCZONE", bg=THEME["accent"], fg=THEME["text_primary"])
            if self.mouse_connected and self.mouse:
                r, g, b = self._hex_to_rgb(self.zone_colors[0])
                self.mouse.set_reactive_color(r, g, b)
            self._set_status("Włączono oświetlenie reaktywne na kliknięcia.")
        else:
            self.reactive_btn.configure(text="⚡ Podświetlenie Reaktywne: WYŁ.", bg=THEME["bg_card"], fg=THEME["text_muted"])
            if self.mouse_connected and self.mouse:
                self.mouse.set_reactive_color(0, 0, 0)
            self._set_status("Wyłączono podświetlenie reaktywne.")

    # -------------------------------------------------------------------------
    # PANEL PRAWY: WYDAJNOŚĆ (DPI, POLLING, ZASILANIE)
    # -------------------------------------------------------------------------
    def _build_performance_panel(self, parent):
        # Karta 1: Czułość sensora TrueMove Air (DPI)
        dpi_card = tk.Frame(parent, bg=THEME["bg_card"], padx=18, pady=16)
        dpi_card.pack(fill="x", pady=(0, 12))

        dpi_header = tk.Frame(dpi_card, bg=THEME["bg_card"])
        dpi_header.pack(fill="x", pady=(0, 10))

        tk.Label(dpi_header, text="CZUŁOŚĆ SENSORA TRUEMOVE AIR (CPI / DPI)",
                 font=("Segoe UI", 11, "bold"), fg=THEME["text_primary"], bg=THEME["bg_card"]).pack(side="left")

        # Szybkie presety
        preset_frame = tk.Frame(dpi_header, bg=THEME["bg_card"])
        preset_frame.pack(side="right")

        tk.Button(preset_frame, text="Esport (400-3200)", font=("Segoe UI", 8),
                  bg=THEME["bg_card_dark"], fg=THEME["text_muted"], relief="flat", cursor="hand2",
                  command=lambda: self._load_dpi_preset([400, 800, 1200, 1600, 3200])).pack(side="left", padx=2)
        tk.Button(preset_frame, text="High (800-6400)", font=("Segoe UI", 8),
                  bg=THEME["bg_card_dark"], fg=THEME["text_muted"], relief="flat", cursor="hand2",
                  command=lambda: self._load_dpi_preset([800, 1600, 2400, 3200, 6400])).pack(side="left", padx=2)

        # 5 Suwaków progów DPI
        self.dpi_labels = []
        for i in range(5):
            row = tk.Frame(dpi_card, bg=THEME["bg_card"])
            row.pack(fill="x", pady=2)

            rb = tk.Radiobutton(row, text=f"Poziom {i+1}:", variable=self.active_dpi_idx, value=i,
                                bg=THEME["bg_card"], fg=THEME["text_primary"],
                                selectcolor=THEME["bg_card_dark"], activebackground=THEME["bg_card"],
                                activeforeground=THEME["accent"], font=("Segoe UI", 9, "bold"),
                                width=10, anchor="w",
                                command=self._on_dpi_stage_changed)
            rb.pack(side="left")

            scale = ttk.Scale(row, from_=100, to=18000, variable=self.dpi_vars[i],
                              command=lambda val, idx=i: self._on_dpi_slider_moved(idx, val))
            scale.pack(side="left", fill="x", expand=True, padx=8)

            lbl = tk.Label(row, text=f"{self.dpi_vars[i].get()} CPI", font=("Segoe UI", 9, "bold"),
                           fg=THEME["accent"] if i == self.active_dpi_idx.get() else THEME["text_muted"],
                           bg=THEME["bg_card"], width=10, anchor="e")
            lbl.pack(side="right")
            self.dpi_labels.append(lbl)

        # Karta 2: Częstotliwość próbkowania USB (Polling Rate)
        polling_card = tk.Frame(parent, bg=THEME["bg_card"], padx=18, pady=14)
        polling_card.pack(fill="x", pady=(0, 12))

        tk.Label(polling_card, text="CZĘSTOTLIWOŚĆ PRÓBKOWANIA USB (POLLING RATE)",
                 font=("Segoe UI", 11, "bold"), fg=THEME["text_primary"], bg=THEME["bg_card"]).pack(anchor="w", pady=(0, 8))

        poll_btn_box = tk.Frame(polling_card, bg=THEME["bg_card"])
        poll_btn_box.pack(fill="x")

        self.poll_btns = {}
        rates = [(1000, "1000 Hz / 1ms (Zalecane)"),
                 (500,  "500 Hz / 2ms"),
                 (250,  "250 Hz / 4ms"),
                 (125,  "125 Hz / 8ms (Oszczędne)")]

        for hz, title in rates:
            b = tk.Button(poll_btn_box, text=title, font=("Segoe UI", 8, "bold"),
                          bg=THEME["accent"] if hz == self.polling_rate_var.get() else THEME["bg_card_dark"],
                          fg=THEME["text_primary"], relief="flat", padx=8, pady=6, cursor="hand2",
                          command=lambda h=hz: self._set_polling_rate(h))
            b.pack(side="left", expand=True, fill="x", padx=2)
            self.poll_btns[hz] = b

        # Karta 3: Oszczędzanie energii (Sleep & Dim)
        power_card = tk.Frame(parent, bg=THEME["bg_card"], padx=18, pady=14)
        power_card.pack(fill="x")

        tk.Label(power_card, text="ZARZĄDZANIE ENERGIĄ (HIGH-EFFICIENCY)",
                 font=("Segoe UI", 11, "bold"), fg=THEME["text_primary"], bg=THEME["bg_card"]).pack(anchor="w", pady=(0, 8))

        # Sleep Timer
        sleep_row = tk.Frame(power_card, bg=THEME["bg_card"])
        sleep_row.pack(fill="x", pady=3)

        tk.Label(sleep_row, text="Uśpienie bezczynności (Sleep):", font=("Segoe UI", 9),
                 fg=THEME["text_primary"], bg=THEME["bg_card"], width=26, anchor="w").pack(side="left")

        self.sleep_lbl = tk.Label(sleep_row, text=f"{self.sleep_timer_var.get()} min", font=("Segoe UI", 9, "bold"),
                                  fg=THEME["accent"], bg=THEME["bg_card"], width=8, anchor="e")
        self.sleep_lbl.pack(side="right")

        ttk.Scale(sleep_row, from_=0, to=20, variable=self.sleep_timer_var,
                  command=self._on_sleep_slider_moved).pack(side="left", fill="x", expand=True, padx=8)

        # Dim Timer
        dim_row = tk.Frame(power_card, bg=THEME["bg_card"])
        dim_row.pack(fill="x", pady=3)

        tk.Label(dim_row, text="Przyciemnienie LED (Dim):", font=("Segoe UI", 9),
                 fg=THEME["text_primary"], bg=THEME["bg_card"], width=26, anchor="w").pack(side="left")

        self.dim_lbl = tk.Label(dim_row, text=f"{self.dim_timer_var.get()} sek", font=("Segoe UI", 9, "bold"),
                                fg=THEME["accent"], bg=THEME["bg_card"], width=8, anchor="e")
        self.dim_lbl.pack(side="right")

        ttk.Scale(dim_row, from_=0, to=1200, variable=self.dim_timer_var,
                  command=self._on_dim_slider_moved).pack(side="left", fill="x", expand=True, padx=8)

    def _load_dpi_preset(self, values: List[int]):
        for i, val in enumerate(values):
            if i < len(self.dpi_vars):
                self.dpi_vars[i].set(val)
                self.dpi_labels[i].configure(text=f"{val} CPI")
        self._apply_dpi_to_device()

    def _on_dpi_slider_moved(self, idx: int, raw_val: str):
        val = int(float(raw_val))
        rounded = int(round(val / 100.0) * 100)
        rounded = max(100, min(18000, rounded))
        self.dpi_vars[idx].set(rounded)
        self.dpi_labels[idx].configure(text=f"{rounded} CPI")

    def _on_dpi_stage_changed(self):
        active = self.active_dpi_idx.get()
        for i, lbl in enumerate(self.dpi_labels):
            lbl.configure(fg=THEME["accent"] if i == active else THEME["text_muted"])
        self._apply_dpi_to_device()

    def _apply_dpi_to_device(self):
        if self.mouse_connected and self.mouse:
            presets = [v.get() for v in self.dpi_vars]
            active = self.active_dpi_idx.get()
            self.mouse.set_dpi(presets, selected_idx=active)
            self._set_status(f"Zaktualizowano czułość: aktywny profil {active+1} ({presets[active]} CPI)")

    def _set_polling_rate(self, hz: int):
        self.polling_rate_var.set(hz)
        for h, btn in self.poll_btns.items():
            if h == hz:
                btn.configure(bg=THEME["accent"], fg=THEME["text_primary"])
            else:
                btn.configure(bg=THEME["bg_card_dark"], fg=THEME["text_muted"])

        if self.mouse_connected and self.mouse:
            self.mouse.set_polling_rate(hz)
            self._set_status(f"Ustawiono częstotliwość raportowania: {hz} Hz")

    def _on_sleep_slider_moved(self, val):
        m = int(float(val))
        self.sleep_timer_var.set(m)
        self.sleep_lbl.configure(text=f"{m} min" if m > 0 else "Wyłączone")

    def _on_dim_slider_moved(self, val):
        s = int(float(val))
        self.dim_timer_var.set(s)
        self.dim_lbl.configure(text=f"{s} sek" if s > 0 else "Wyłączone")

    # =========================================================================
    # DOLNY PASEK AKCJI (FOOTER)
    # =========================================================================
    def _build_footer(self):
        tk.Frame(self, bg=THEME["border"], height=1).pack(fill="x", side="bottom")

        footer = tk.Frame(self, bg=THEME["bg_card"], height=52, padx=20)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        # Status text
        self.status_lbl = tk.Label(footer, text="Inicjalizacja...", font=("Segoe UI", 9),
                                   fg=THEME["text_muted"], bg=THEME["bg_card"])
        self.status_lbl.pack(side="left", pady=14)

        # Przyciski akcji
        btn_box = tk.Frame(footer, bg=THEME["bg_card"])
        btn_box.pack(side="right", pady=8)

        # Przycisk uprawnień udev
        udev_btn = tk.Button(btn_box, text="⚙ Uprawnienia Udev", font=("Segoe UI", 9),
                             bg=THEME["bg_card_dark"], fg=THEME["text_muted"], relief="flat",
                             padx=12, pady=5, cursor="hand2", command=self._show_udev_help)
        udev_btn.pack(side="left", padx=4)

        # Zastosuj na żywo
        apply_btn = tk.Button(btn_box, text="✔ Zastosuj Wszystko", font=("Segoe UI", 9, "bold"),
                              bg=THEME["bg_card_dark"], fg=THEME["text_primary"], relief="flat",
                              padx=14, pady=5, cursor="hand2", command=self._apply_all_live)
        apply_btn.pack(side="left", padx=4)

        # Zapisz w pamięci myszy
        save_btn = tk.Button(btn_box, text="💾 Zapisz w Pamięci Myszy", font=("Segoe UI", 9, "bold"),
                             bg=THEME["accent"], fg=THEME["text_primary"], relief="flat",
                             activebackground=THEME["accent_hover"], activeforeground=THEME["text_primary"],
                             padx=16, pady=5, cursor="hand2", command=self._save_onboard)
        save_btn.pack(side="left", padx=4)

    # =========================================================================
    # KOMUNIKACJA Z MYSZKĄ I ZDARZENIA W TLE
    # =========================================================================
    def _connect_mouse(self):
        try:
            self.mouse = AeroxMouse()
            if not self.mouse.find_device():
                self.mouse_connected = False
                self.conn_pill.configure(text="● BRAK URZĄDZENIA", fg=THEME["danger"], bg=THEME["bg_card_dark"])
                self._set_status("Nie wykryto myszy SteelSeries Aerox 3. Podłącz odbiornik USB lub kabel.")
                return

            self.mouse.open()
            self.mouse_connected = True
            self.mouse_wireless = self.mouse.is_wireless

            mode_str = "● BEZPRZEWODOWY 2.4 GHz" if self.mouse_wireless else "● PRZEWODOWY USB"
            self.conn_pill.configure(text=mode_str, fg=THEME["success"], bg=THEME["bg_card_dark"])
            self._set_status(f"Pomyślnie połączono z {self.mouse.model_name}")

            # Pobierz stan baterii
            self._update_battery_status()

        except PermissionError:
            self.mouse_connected = False
            self.perm_error = True
            self.conn_pill.configure(text="● BRAK UPRAWNIEŃ ROOT/UDEV", fg=THEME["danger"], bg=THEME["bg_card_dark"])
            self._set_status("Wymagane uprawnienia udev! Kliknij '⚙ Uprawnienia Udev' poniżej.")
        except Exception as e:
            self.mouse_connected = False
            self.conn_pill.configure(text="● BŁĄD POŁĄCZENIA", fg=THEME["danger"], bg=THEME["bg_card_dark"])
            self._set_status(f"Błąd inicjalizacji: {e}")

    def _update_battery_status(self):
        if not self.mouse_connected or not self.mouse:
            return

        def task():
            try:
                bat = self.mouse.get_battery()
                lvl = bat.get("level")
                charging = bat.get("is_charging", False)
                self.after(0, lambda: self._apply_battery_ui(lvl, charging))
            except Exception:
                pass

        threading.Thread(target=task, daemon=True).start()

    def _apply_battery_ui(self, level: Optional[int], is_charging: bool):
        if level is not None:
            self.battery_level = level
            self.is_charging = is_charging
            ch_str = " (Ładowanie ⚡)" if is_charging else ""
            self.battery_lbl.configure(text=f"{level}%{ch_str}")
            self._draw_battery_icon(level, is_charging)
        else:
            self.battery_lbl.configure(text="-- %")
            self._draw_battery_icon(0, False)

    def _schedule_battery_refresh(self):
        self._update_battery_status()
        self.after(30000, self._schedule_battery_refresh)

    def _on_refresh_status(self):
        self._connect_mouse()
        self._update_battery_status()
        self._set_status("Odświeżono status urządzenia.")

    def _apply_all_live(self):
        if not self.mouse_connected or not self.mouse:
            self._show_device_missing_error()
            return

        try:
            # 1. RGB
            if self.is_rainbow:
                self.mouse.set_rainbow()
            else:
                for z in range(3):
                    r, g, b = self._hex_to_rgb(self.zone_colors[z])
                    self.mouse.set_zone_color(z, r, g, b)

            # 2. DPI
            presets = [v.get() for v in self.dpi_vars]
            active = self.active_dpi_idx.get()
            self.mouse.set_dpi(presets, selected_idx=active)

            # 3. Polling rate
            self.mouse.set_polling_rate(self.polling_rate_var.get())

            # 4. Timery
            self.mouse.set_sleep_timer(self.sleep_timer_var.get())
            self.mouse.set_dim_timer(self.dim_timer_var.get())

            self._set_status("Wszystkie parametry zostały pomyślnie wysłane do myszy.")
        except Exception as e:
            self._set_status(f"Błąd podczas aplikowania ustawień: {e}")

    def _save_onboard(self):
        if not self.mouse_connected or not self.mouse:
            self._show_device_missing_error()
            return

        try:
            self._apply_all_live()
            self.mouse.save()
            messagebox.showinfo("Zapisano Ustawienia",
                                "Twoja konfiguracja została trwale zapisana w pamięci myszy (Onboard Memory).\n"
                                "Będzie ona zachowana nawet po odłączeniu od komputera!")
            self._set_status("Zapisano konfigurację w pamięci flash myszy.")
        except Exception as e:
            messagebox.showerror("Błąd Zapisu", f"Nie udało się zapisać ustawień w pamięci: {e}")

    def _show_udev_help(self):
        msg = ("Aby uzyskać pełny dostęp do parametrów myszy SteelSeries Aerox 3 bez uprawnień roota, "
               "uruchom w terminalu przygotowany skrypt reguł udev:\n\n"
               "    sudo /home/user1/test/setup_aerox_permissions.sh\n\n"
               "Skrypt automatycznie skonfiguruje reguły udev i uprawnienia dla portu USB HID.")
        messagebox.showinfo("Konfiguracja Uprawnień Udev", msg)

    def _show_device_missing_error(self):
        if self.perm_error:
            self._show_udev_help()
        else:
            messagebox.showwarning("Brak Urządzenia",
                                   "Mysz SteelSeries Aerox 3 nie została wykryta.\n"
                                   "Sprawdź czy odbiornik USB jest podłączony do komputera.")

    def _set_status(self, text: str):
        self.status_lbl.configure(text=f"● {text}")

    @staticmethod
    def _hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
        clean = hex_code.lstrip("#")
        return int(clean[0:2], 16), int(clean[2:4], 16), int(clean[4:6], 16)


if __name__ == "__main__":
    app = AeroxGUI()
    app.mainloop()
