#!/usr/bin/env python3
"""
k530gui - Pixel-Perfect Redragon K530 Draconic Control Center for Linux
Exact native Linux recreation of the official Redragon K530 RGB Windows software
using the original graphics, fonts, coordinates, and HID protocol.
"""

import sys
import os
import re
import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from typing import Dict, List, Tuple, Optional

# Dodaj katalog narzędzi do ścieżki
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS_DIR)
from k530ctl import RedragonK530Controller, MODES

REPO_ROOT = os.path.dirname(TOOLS_DIR)
ASSETS_DIR = os.path.join(REPO_ROOT, "drivers", "k530_software", "png_assets")
if not os.path.exists(ASSETS_DIR):
    ASSETS_DIR = "/home/user1/test/drivers/k530_software/png_assets"

MAIN_INI_PATH = os.path.join(REPO_ROOT, "drivers", "k530_software", "Main.ini")
if not os.path.exists(MAIN_INI_PATH):
    MAIN_INI_PATH = "/home/user1/test/drivers/k530_software/Main.ini"

# 8 preset colors extracted from Color1..Color8 assets
PALETTE_COLORS = [
    ("#ec631f", 236, 99, 31),   # Orange
    ("#fe0000", 254, 0, 0),     # Red
    ("#017eff", 1, 126, 255),   # Blue
    ("#5aff02", 90, 255, 2),    # Green
    ("#eaff00", 234, 255, 0),   # Yellow
    ("#ffc001", 255, 192, 1),   # Amber
    ("#ff00b4", 255, 0, 180),   # Magenta
    ("#af00ff", 175, 0, 255),   # Purple
]

# Official lighting mode names mapped to mode IDs
OFFICIAL_MODES = [
    ("Go with the stream", 0x02, True),
    ("Clouds fly", 0x02, True),
    ("Winding paths", 0x03, True),
    ("The trial of light", 0x04, True),
    ("Breathing", 0x01, False),
    ("Normally on (Static)", 0x06, False),
    ("Pass without trace", 0x07, True),
    ("Ripple graff", 0x08, True),
    ("Fast run without trace", 0x09, True),
    ("Snow winter jasmine", 0x0A, True),
    ("Flowers blooming", 0x0B, True),
    ("Swift action", 0x0C, True),
    ("Hurricane", 0x0D, True),
    ("Accumulate", 0x0E, True),
    ("Digital Times", 0x0F, True),
    ("Both ways (Visor)", 0x10, True),
    ("Surmount", 0x11, True),
    ("Fast and the Furious", 0x12, True),
    ("Coastal (Custom)", 0x14, False),
]


def load_key_coordinates() -> List[Tuple[str, int, int, int, int, str]]:
    keys = []
    if not os.path.exists(MAIN_INI_PATH):
        return keys
    try:
        with open(MAIN_INI_PATH, "rb") as f:
            text = f.read().decode("utf-16le")
        for line in text.splitlines():
            m = re.match(r"^\s*(KEY_[A-Za-z0-9_]+)\s*=\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*\"([^\"]*)\"", line)
            if m:
                name, x, y, w, h, label = m.groups()
                keys.append((name, int(x), int(y), int(w), int(h), label))
    except Exception as e:
        print(f"[!] Warning reading Main.ini: {e}", file=sys.stderr)
    return keys


class RedragonK530OfficialUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Redragon K530RGB Keyboard")
        self.geometry("1000x640")
        self.resizable(False, False)

        # Usunięcie domyślnego paska okna dla 100% wierności z oryginałem lub obsługa przesuwania
        self.configure(bg="#121212")

        # Stan aplikacji
        self.current_r = 254
        self.current_g = 0
        self.current_b = 0
        self.current_hex = "#fe0000"
        self.current_mode_id = 0x06  # Static by default
        self.brightness = 4
        self.speed = 2
        self.direction = 0
        self.random_color = False
        self.selected_profile = 1
        self.selected_key: Optional[str] = None
        self.per_key_colors: Dict[str, Tuple[int, int, int]] = {}

        # Referencje do obrazów PhotoImage (aby GC ich nie usunął)
        self.images: Dict[str, tk.PhotoImage] = {}

        # Wczytanie zasobów graficznych
        self._load_assets()

        # Budowa interfejsu Canvas
        self._build_canvas_ui()

        # Inicjalizacja sterownika
        self.ctrl = RedragonK530Controller()
        self._update_connection_status()

    def _load_assets(self):
        def get_img(name: str) -> Optional[tk.PhotoImage]:
            p = os.path.join(ASSETS_DIR, name)
            if os.path.exists(p):
                img = tk.PhotoImage(file=p)
                self.images[name] = img
                return img
            return None

        self.bg_img = get_img("main_normal.png")
        self.left_arr = get_img("leftup.png")
        self.right_arr = get_img("rightup.png")
        self.add_img = get_img("add.png")
        self.sub_img = get_img("sub.png")
        self.deng_img = get_img("dengup.png")
        self.sjs_up = get_img("sjsup.png")
        self.sjs_down = get_img("sjsdown.png")

        self.color_imgs = []
        for i in range(1, 9):
            img = get_img(f"Color{i}.png")
            if img:
                self.color_imgs.append(img)

    def _build_canvas_ui(self):
        self.canvas = tk.Canvas(self, width=1000, height=640, highlightthickness=0, bd=0, bg="#121212")
        self.canvas.pack(fill="both", expand=True)

        # 1. Rysowanie tła (Oryginalny skin Redragon 1000x640)
        if self.bg_img:
            self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw")

        # Obsługa przesuwania okna (Drag window by top bar)
        self.canvas.bind("<ButtonPress-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._do_drag)

        # 2. Pasek tytułowy i przyciski okna (Top Right)
        # Minimize (903, 33, 19, 19)
        self._create_hover_btn(903, 33, 19, 19, "—", self.iconify, bg="#2a2a2a", fg="#aaaaaa")
        # Close (924, 33, 20, 19)
        self._create_hover_btn(924, 33, 20, 19, "✕", self.destroy, bg="#c62828", fg="#ffffff")

        # Wskaźnik połączenia USB (Top Center/Right)
        self.status_item = self.canvas.create_text(
            780, 42, text="● WYKRYWANIE...", fill="#ffaa00", font=("Segoe UI", 9, "bold"), anchor="w"
        )

        # 3. Przyciski boczne (Profile i nawigacja po lewej)
        # FUNC_PROFILE1: 69, 184, 151, 29
        # FUNC_PROFILE2: 69, 218, 151, 29
        # FUNC_PROFILE3: 69, 252, 151, 29
        # FUNC_MACRO: 69, 321, 151, 29
        # FUNC_MAGICFN: 69, 355, 151, 29
        # FUNC_DEFAULT: 69, 563, 151, 29
        self.profile_btns = []
        for p_idx, y_pos in enumerate([184, 218, 252], start=1):
            btn = self._create_side_btn(69, y_pos, 151, 29, f"Profile {p_idx}", lambda idx=p_idx: self._select_profile(idx))
            self.profile_btns.append(btn)

        self._create_side_btn(69, 321, 151, 29, "Macro Setting", self._show_macro_info)
        self._create_side_btn(69, 355, 151, 29, "Magic FN", self._show_magic_fn_info)
        self._create_side_btn(69, 563, 151, 29, "Restore Default", self._restore_default)

        # 4. Klawisze klawiatury 60% (Interaktywna siatka 62 klawiszy)
        self.key_items = {}
        key_list = load_key_coordinates()
        for name, x, y, w, h, label in key_list:
            # Rysowanie przezroczystej nakładki na klawisz
            rect_id = self.canvas.create_rectangle(
                x, y, x + w, y + h,
                outline="", fill="", tags=("key", name)
            )
            text_id = self.canvas.create_text(
                x + w / 2, y + h / 2,
                text=label, fill="#d0d0d0", font=("Segoe UI", 8, "bold"),
                tags=("key", name)
            )
            self.key_items[name] = (rect_id, text_id, x, y, w, h, label)

            # Zdarzenia hover i click na klawiszach
            self.canvas.tag_bind(name, "<Enter>", lambda e, n=name: self._on_key_enter(n))
            self.canvas.tag_bind(name, "<Leave>", lambda e, n=name: self._on_key_leave(n))
            self.canvas.tag_bind(name, "<Button-1>", lambda e, n=name: self._on_key_click(n))

        # 5. Dolny panel kontrolny (Lighting Controls)
        # Etykieta Trybu (303, 360)
        self.canvas.create_text(340, 368, text="Light:", fill="#ffffff", font=("Segoe UI", 10, "bold"), anchor="w")

        # Rozwijana lista trybów (CONTROL_XGcombox: 380, 355, 175, 25)
        self.mode_var = tk.StringVar(value=OFFICIAL_MODES[5][0])  # Static domyślnie
        self.mode_combo = ttk.Combobox(
            self, textvariable=self.mode_var, values=[m[0] for m in OFFICIAL_MODES],
            state="readonly", width=22, font=("Segoe UI", 9)
        )
        self.mode_combo.bind("<<ComboboxSelected>>", self._on_mode_change)
        self.canvas.create_window(385, 355, window=self.mode_combo, anchor="nw")

        # Brightness (Jasność): 303, 400
        self.canvas.create_text(340, 412, text="Light:", fill="#c0c0c0", font=("Segoe UI", 9, "bold"), anchor="w")
        
        # Przycisk minus (365, 412)
        btn_sub_br = tk.Button(self, text="−", bg="#2a2a35", fg="#ffffff", bd=0, font=("Segoe UI", 9, "bold"),
                               width=2, height=1, cursor="hand2", command=lambda: self._adj_brightness(-1))
        self.canvas.create_window(370, 403, window=btn_sub_br, anchor="nw")

        self.br_var = tk.IntVar(value=4)
        self.br_scale = tk.Scale(
            self, from_=0, to=4, orient="horizontal", variable=self.br_var,
            bg="#2a2a35", fg="#ffffff", highlightthickness=0, troughcolor="#1a1a24",
            activebackground="#e53935", length=110, showvalue=False, command=self._on_slider_change
        )
        self.canvas.create_window(395, 405, window=self.br_scale, anchor="nw")

        btn_add_br = tk.Button(self, text="+", bg="#2a2a35", fg="#ffffff", bd=0, font=("Segoe UI", 9, "bold"),
                               width=2, height=1, cursor="hand2", command=lambda: self._adj_brightness(1))
        self.canvas.create_window(512, 403, window=btn_add_br, anchor="nw")

        self.br_val_text = self.canvas.create_text(545, 414, text="4", fill="#ffffff", font=("Segoe UI", 9, "bold"))

        # Speed (Prędkość): 303, 450
        self.canvas.create_text(340, 462, text="Speed:", fill="#c0c0c0", font=("Segoe UI", 9, "bold"), anchor="w")

        btn_sub_sp = tk.Button(self, text="−", bg="#2a2a35", fg="#ffffff", bd=0, font=("Segoe UI", 9, "bold"),
                               width=2, height=1, cursor="hand2", command=lambda: self._adj_speed(1))  # w K530 10 to najwolniej
        self.canvas.create_window(370, 453, window=btn_sub_sp, anchor="nw")

        self.speed_var = tk.IntVar(value=2)
        self.speed_scale = tk.Scale(
            self, from_=0, to=10, orient="horizontal", variable=self.speed_var,
            bg="#2a2a35", fg="#ffffff", highlightthickness=0, troughcolor="#1a1a24",
            activebackground="#e53935", length=110, showvalue=False, command=self._on_slider_change
        )
        self.canvas.create_window(395, 455, window=self.speed_scale, anchor="nw")

        btn_add_sp = tk.Button(self, text="+", bg="#2a2a35", fg="#ffffff", bd=0, font=("Segoe UI", 9, "bold"),
                               width=2, height=1, cursor="hand2", command=lambda: self._adj_speed(-1))
        self.canvas.create_window(512, 453, window=btn_add_sp, anchor="nw")

        self.sp_val_text = self.canvas.create_text(545, 464, text="2", fill="#ffffff", font=("Segoe UI", 9, "bold"))

        # Prawa strona dolnego panelu: Color & Presets & Direction
        # Color Label (640, 365)
        self.canvas.create_text(640, 365, text="Color:", fill="#ffffff", font=("Segoe UI", 9, "bold"), anchor="w")

        # Color Preview Swatch (700, 354, 45, 24)
        self.swatch_btn = tk.Button(
            self, bg=self.current_hex, activebackground=self.current_hex,
            bd=1, relief="ridge", width=4, height=1, cursor="hand2", command=self._pick_custom_color
        )
        self.canvas.create_window(695, 353, window=self.swatch_btn, anchor="nw")

        # Colourful / Rainbow checkbox (760, 356)
        self.rand_var = tk.BooleanVar(value=False)
        self.rand_check = tk.Checkbutton(
            self, text="Colourful", variable=self.rand_var, bg="#202026", fg="#ffffff",
            selectcolor="#30303c", activebackground="#202026", activeforeground="#ffffff",
            font=("Segoe UI", 9), command=self._on_rand_toggle
        )
        self.canvas.create_window(760, 353, window=self.rand_check, anchor="nw")

        # 8 Przycisków Palety Kolorów (Color1..Color8): 640, 395
        for idx, (c_hex, cr, cg, cb) in enumerate(PALETTE_COLORS):
            x_pos = 640 + idx * 28
            img = self.color_imgs[idx] if idx < len(self.color_imgs) else None
            if img:
                b = tk.Button(self, image=img, bd=0, bg="#202026", activebackground="#202026",
                              cursor="hand2", command=lambda h=c_hex, r=cr, g=cg, b=cb: self._set_palette_color(h, r, g, b))
            else:
                b = tk.Button(self, bg=c_hex, width=2, height=1, bd=1, cursor="hand2",
                              command=lambda h=c_hex, r=cr, g=cg, b=cb: self._set_palette_color(h, r, g, b))
            self.canvas.create_window(x_pos, 395, window=b, anchor="nw")

        # Direction (Kierunek): 640, 440
        self.canvas.create_text(640, 442, text="Direction:", fill="#c0c0c0", font=("Segoe UI", 9, "bold"), anchor="w")
        
        btn_dir_l = tk.Button(self, text="◄", bg="#2a2a35", fg="#ffffff", bd=0, font=("Segoe UI", 9),
                              width=3, cursor="hand2", command=lambda: self._set_direction(0))
        self.canvas.create_window(715, 432, window=btn_dir_l, anchor="nw")

        btn_dir_r = tk.Button(self, text="►", bg="#2a2a35", fg="#ffffff", bd=0, font=("Segoe UI", 9),
                              width=3, cursor="hand2", command=lambda: self._set_direction(1))
        self.canvas.create_window(755, 432, window=btn_dir_r, anchor="nw")

        # 6. Przyciski Akcji (Na dole: OK, Cancel, Apply)
        # CONTROL_OK: 439, 563, 75, 29
        # CONTROL_CANCEL: 518, 563, 75, 29
        # CONTROL2_APPLY: 596, 563, 75, 29
        self._create_bottom_action_btn(439, 563, 75, 29, "OK", self._on_apply_and_close)
        self._create_bottom_action_btn(518, 563, 75, 29, "Off", self._turn_off_lighting)
        self._create_bottom_action_btn(596, 563, 75, 29, "Apply", self.apply_current_lighting, primary=True)

        # Status text na dole (700, 577)
        self.log_text = self.canvas.create_text(
            700, 577, text="Ready", fill="#888899", font=("Segoe UI", 9), anchor="w"
        )

        # Zaznacz pierwszy profil
        self._highlight_active_profile(1)

    def _create_side_btn(self, x, y, w, h, text, cmd):
        btn = tk.Button(
            self, text=text, bg="#26262e", fg="#e0e0e0", activebackground="#e53935",
            activeforeground="#ffffff", font=("Segoe UI", 9, "bold"), bd=1, relief="ridge",
            cursor="hand2", command=cmd
        )
        self.canvas.create_window(x, y, window=btn, width=w, height=h, anchor="nw")
        return btn

    def _create_bottom_action_btn(self, x, y, w, h, text, cmd, primary=False):
        bg_col = "#e53935" if primary else "#32323e"
        btn = tk.Button(
            self, text=text, bg=bg_col, fg="#ffffff", activebackground="#d32f2f" if primary else "#454556",
            activeforeground="#ffffff", font=("Segoe UI", 9, "bold"), bd=1, relief="ridge",
            cursor="hand2", command=cmd
        )
        self.canvas.create_window(x, y, window=btn, width=w, height=h, anchor="nw")
        return btn

    def _create_hover_btn(self, x, y, w, h, text, cmd, bg="#2a2a2a", fg="#ffffff"):
        btn = tk.Button(
            self, text=text, bg=bg, fg=fg, bd=0, font=("Segoe UI", 8, "bold"),
            cursor="hand2", command=cmd
        )
        self.canvas.create_window(x, y, window=btn, width=w, height=h, anchor="nw")
        return btn

    # Drag window handlers
    def _start_drag(self, event):
        if event.y < 50 and event.x < 890:
            self._drag_x = event.x
            self._drag_y = event.y
        else:
            self._drag_x = None

    def _do_drag(self, event):
        if getattr(self, "_drag_x", None) is not None:
            dx = event.x - self._drag_x
            dy = event.y - self._drag_y
            x = self.winfo_x() + dx
            y = self.winfo_y() + dy
            self.geometry(f"+{x}+{y}")

    # Key events
    def _on_key_enter(self, key_name):
        rect_id, text_id, x, y, w, h, label = self.key_items[key_name]
        self.canvas.itemconfig(rect_id, fill=self.current_hex, outline="#ffffff")
        self.canvas.itemconfig(text_id, fill="#ffffff")

    def _on_key_leave(self, key_name):
        if self.selected_key == key_name:
            return
        rect_id, text_id, x, y, w, h, label = self.key_items[key_name]
        col = self.per_key_colors.get(key_name)
        if col:
            hex_col = f"#{col[0]:02x}{col[1]:02x}{col[2]:02x}"
            self.canvas.itemconfig(rect_id, fill=hex_col, outline="")
        else:
            self.canvas.itemconfig(rect_id, fill="", outline="")
        self.canvas.itemconfig(text_id, fill="#d0d0d0")

    def _on_key_click(self, key_name):
        self.selected_key = key_name
        self.per_key_colors[key_name] = (self.current_r, self.current_g, self.current_b)
        rect_id, text_id, x, y, w, h, label = self.key_items[key_name]
        self.canvas.itemconfig(rect_id, fill=self.current_hex, outline="#ffffff")
        self.canvas.itemconfig(self.log_text, text=f"Key: {label} [{key_name}] set to {self.current_hex}", fill="#4caf50")

    def _update_connection_status(self):
        try:
            info = self.ctrl.get_device_info()
            if info:
                self.canvas.itemconfig(self.status_item, text="● CONNECTED (0C45:5004)", fill="#4caf50")
            else:
                self.canvas.itemconfig(self.status_item, text="● NOT DETECTED", fill="#f44336")
        except Exception:
            self.canvas.itemconfig(self.status_item, text="● PERMISSION ERROR", fill="#ff9800")

    def _highlight_active_profile(self, p_num: int):
        self.selected_profile = p_num
        for idx, btn in enumerate(self.profile_btns, start=1):
            if idx == p_num:
                btn.config(bg="#e53935", fg="#ffffff")
            else:
                btn.config(bg="#26262e", fg="#e0e0e0")

    def _select_profile(self, p_num: int):
        self._highlight_active_profile(p_num)
        self.canvas.itemconfig(self.log_text, text=f"Profile {p_num} selected", fill="#4caf50")

    def _show_macro_info(self):
        messagebox.showinfo("Macro Setting", "Konfiguracja makr K530: Wciśnij FN2 + 7 na klawiaturze, aby rozpocząć nagrywanie w locie.")

    def _show_magic_fn_info(self):
        messagebox.showinfo("Magic FN", "Magic FN: Klawisz CapsLock działa domyślnie jako FN1 w trybie tap/hold.")

    def _restore_default(self):
        if messagebox.askyesno("Restore Default", "Przywrócić fabryczne ustawienia podświetlenia K530?"):
            try:
                with self.ctrl:
                    self.ctrl.set_lighting(mode_id=0x02, brightness=4, speed=2, random_color=True)
                self.mode_combo.current(0)
                self.br_var.set(4)
                self.speed_var.set(2)
                self.rand_var.set(True)
                self._update_sliders_display()
                self.canvas.itemconfig(self.log_text, text="Factory defaults restored", fill="#4caf50")
            except Exception as e:
                messagebox.showerror("Error", f"Błąd: {e}")

    def _adj_brightness(self, delta):
        nv = max(0, min(4, self.br_var.get() + delta))
        self.br_var.set(nv)
        self._update_sliders_display()

    def _adj_speed(self, delta):
        nv = max(0, min(10, self.speed_var.get() + delta))
        self.speed_var.set(nv)
        self._update_sliders_display()

    def _on_slider_change(self, val):
        self._update_sliders_display()

    def _update_sliders_display(self):
        self.canvas.itemconfig(self.br_val_text, text=str(self.br_var.get()))
        self.canvas.itemconfig(self.sp_val_text, text=str(self.speed_var.get()))

    def _on_mode_change(self, event=None):
        idx = self.mode_combo.current()
        if 0 <= idx < len(OFFICIAL_MODES):
            name, mid, has_rand = OFFICIAL_MODES[idx]
            self.current_mode_id = mid
            if has_rand:
                self.rand_var.set(True)
            self.canvas.itemconfig(self.log_text, text=f"Mode: {name}", fill="#e0e0e0")

    def _on_rand_toggle(self):
        self.random_color = self.rand_var.get()

    def _set_direction(self, dir_val):
        self.direction = dir_val
        dir_name = "Left" if dir_val == 0 else "Right"
        self.canvas.itemconfig(self.log_text, text=f"Direction: {dir_name}", fill="#e0e0e0")

    def _set_palette_color(self, hex_val, r, g, b):
        self.current_hex = hex_val
        self.current_r = r
        self.current_g = g
        self.current_b = b
        self.swatch_btn.config(bg=hex_val, activebackground=hex_val)
        self.rand_var.set(False)
        self.canvas.itemconfig(self.log_text, text=f"Color: RGB({r},{g},{b})", fill="#4caf50")

    def _pick_custom_color(self):
        col = colorchooser.askcolor(color=self.current_hex, parent=self)
        if col and col[0]:
            r, g, b = int(col[0][0]), int(col[0][1]), int(col[0][2])
            self._set_palette_color(col[1], r, g, b)

    def apply_current_lighting(self):
        idx = self.mode_combo.current()
        if 0 <= idx < len(OFFICIAL_MODES):
            self.current_mode_id = OFFICIAL_MODES[idx][1]

        try:
            with self.ctrl:
                self.ctrl.set_lighting(
                    mode_id=self.current_mode_id,
                    brightness=self.br_var.get(),
                    speed=self.speed_var.get(),
                    direction=self.direction,
                    random_color=self.rand_var.get(),
                    r=self.current_r,
                    g=self.current_g,
                    b=self.current_b
                )
            self.canvas.itemconfig(self.log_text, text="Settings Applied Successfully!", fill="#4caf50")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send to keyboard:\n{e}")
            self.canvas.itemconfig(self.log_text, text=f"Error: {e}", fill="#f44336")

    def _turn_off_lighting(self):
        try:
            with self.ctrl:
                self.ctrl.set_lighting(mode_id=0x06, brightness=0, r=0, g=0, b=0)
            self.canvas.itemconfig(self.log_text, text="Lighting turned off", fill="#ffaa00")
        except Exception as e:
            messagebox.showerror("Error", f"Błąd: {e}")

    def _on_apply_and_close(self):
        self.apply_current_lighting()
        self.after(300, self.destroy)


def main():
    app = RedragonK530OfficialUI()
    app.mainloop()


if __name__ == "__main__":
    main()
