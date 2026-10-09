#!/usr/bin/env python3
"""
k530ctl - Redragon K530 Draconic Keyboard Controller for Linux
Native driver and CLI utility for controlling RGB lighting, modes, and parameters
via USB HID without requiring Windows or vendor software.

Hardware Target:
  Vendor ID:  0x0C45 (Microdia / SONiX)
  Product ID: 0x5004 (SONiX Draconic / Redragon Mitra/Draconic)
  MCU:        Sonix SN32F248B / EVision VS11K09A-1
  Interface:  HID Interface 1 (Usage Page: 0xFF1C, Usage: 0x0092)
"""

import sys
import os
import argparse
import ctypes
import time
from typing import Optional, Tuple, Dict, List

# Standard lighting modes supported by Redragon K530 firmware
MODES: Dict[str, Tuple[int, str]] = {
    "breathing":        (0x01, "Breathing (Oddychanie)"),
    "wave":             (0x02, "Color Wave (Fala kolorów)"),
    "winding":          (0x03, "Winding Paths (Kręte ścieżki)"),
    "trial":            (0x04, "The Trial of Light (Próba światła)"),
    "breathing2":       (0x05, "Alternating Breathing (Alternatywne oddychanie)"),
    "static":           (0x06, "Static / Normally On (Stałe podświetlenie)"),
    "pass":             (0x07, "Pass Without Trace (Przejście bez śladu)"),
    "ripple":           (0x08, "Ripple (Rozchodzące się fale)"),
    "fast_run":         (0x09, "Fast Run (Szybki bieg)"),
    "snow":             (0x0A, "Snow Winter Jasmine (Zimowy jaśmin)"),
    "flowers":          (0x0B, "Flowers Blooming (Kwitnące kwiaty / Spectrum)"),
    "swift":            (0x0C, "Swift Action (Szybka akcja)"),
    "hurricane":        (0x0D, "Hurricane (Huragan)"),
    "accumulate":       (0x0E, "Accumulate (Akumulacja)"),
    "digital":          (0x0F, "Digital Times (Cyfrowy czas)"),
    "both_ways":        (0x10, "Both Ways / Visor (W obie strony)"),
    "surmount":         (0x11, "Surmount (Pokonywanie barier)"),
    "furious":          (0x12, "Fast and the Furious (Szybcy i wściekli)"),
    "coastal":          (0x14, "Coastal / Custom (Wybrzeże / Własne)"),
}

NAMED_COLORS: Dict[str, Tuple[int, int, int]] = {
    "red":     (255, 0, 0),
    "green":   (0, 255, 0),
    "blue":    (0, 0, 255),
    "yellow":  (255, 255, 0),
    "cyan":    (0, 255, 255),
    "magenta": (255, 0, 255),
    "white":   (255, 255, 255),
    "orange":  (255, 128, 0),
    "purple":  (128, 0, 255),
    "pink":    (255, 105, 180),
    "off":     (0, 0, 0),
}

# --- CTYPES HIDAPI DEFINITIONS ---
class hid_device_info(ctypes.Structure):
    pass

hid_device_info._fields_ = [
    ("path", ctypes.c_char_p),
    ("vendor_id", ctypes.c_ushort),
    ("product_id", ctypes.c_ushort),
    ("serial_number", ctypes.c_wchar_p),
    ("release_number", ctypes.c_ushort),
    ("manufacturer_string", ctypes.c_wchar_p),
    ("product_string", ctypes.c_wchar_p),
    ("usage_page", ctypes.c_ushort),
    ("usage", ctypes.c_ushort),
    ("interface_number", ctypes.c_int),
    ("next", ctypes.POINTER(hid_device_info)),
]


def load_hidapi():
    candidates = [
        "libhidapi-hidraw.so.0",
        "libhidapi-hidraw.so",
        "libhidapi-libusb.so.0",
        "libhidapi-libusb.so",
    ]
    for lib in candidates:
        try:
            h = ctypes.cdll.LoadLibrary(lib)
            # Setup function prototypes
            h.hid_init.restype = ctypes.c_int
            h.hid_exit.restype = ctypes.c_int
            h.hid_enumerate.restype = ctypes.POINTER(hid_device_info)
            h.hid_enumerate.argtypes = [ctypes.c_ushort, ctypes.c_ushort]
            h.hid_free_enumeration.argtypes = [ctypes.POINTER(hid_device_info)]
            h.hid_open_path.restype = ctypes.c_void_p
            h.hid_open_path.argtypes = [ctypes.c_char_p]
            h.hid_close.argtypes = [ctypes.c_void_p]
            h.hid_write.restype = ctypes.c_int
            h.hid_write.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t]
            h.hid_read_timeout.restype = ctypes.c_int
            h.hid_read_timeout.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_int]
            h.hid_error.restype = ctypes.c_wchar_p
            h.hid_error.argtypes = [ctypes.c_void_p]
            return h
        except OSError:
            continue
    raise RuntimeError("Nie znaleziono biblioteki libhidapi (zainstaluj pakiet 'hidapi')")


class RedragonK530Controller:
    VID = 0x0C45
    PID = 0x5004
    USAGE_PAGE = 0xFF1C
    USAGE = 0x0092

    CMD_BEGIN = 0x01
    CMD_END = 0x02
    CMD_SET_PARAM = 0x06
    CMD_WRITE_CUSTOM = 0x11

    def __init__(self):
        self.hid = load_hidapi()
        self.hid.hid_init()
        self.dev = None
        self.dev_path = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        self.hid.hid_exit()

    def find_device_path(self) -> Optional[bytes]:
        devs = self.hid.hid_enumerate(self.VID, self.PID)
        cur = devs
        matched_path = None
        fallback_path = None

        while cur:
            d = cur.contents
            # Sprawdzamy czy to właściwy endpoint kontrolny
            if d.usage_page == self.USAGE_PAGE and d.usage == self.USAGE:
                matched_path = d.path
                break
            # Jako fallback, jeśli usage_page nie jest raportowane przez kernel, bierzemy interface 1
            if d.interface_number == 1 and not fallback_path:
                fallback_path = d.path
            cur = d.next

        chosen = matched_path or fallback_path
        res = bytes(chosen) if chosen else None
        self.hid.hid_free_enumeration(devs)
        return res

    def get_device_info(self) -> List[Dict]:
        info_list = []
        devs = self.hid.hid_enumerate(self.VID, self.PID)
        cur = devs
        while cur:
            d = cur.contents
            info_list.append({
                "path": d.path.decode('utf-8', errors='replace'),
                "vid": f"0x{d.vendor_id:04x}",
                "pid": f"0x{d.product_id:04x}",
                "interface": d.interface_number,
                "usage_page": f"0x{d.usage_page:04x}",
                "usage": f"0x{d.usage:04x}",
                "product": d.product_string or "Draconic",
                "manufacturer": d.manufacturer_string or "SONiX",
            })
            cur = d.next
        self.hid.hid_free_enumeration(devs)
        return info_list

    def connect(self):
        path = self.find_device_path()
        if not path:
            raise FileNotFoundError(
                "Nie znaleziono klawiatury Redragon K530 (0c45:5004).\n"
                "Upewnij się, że klawiatura jest podłączona kablem USB lub odbiornikiem 2.4G."
            )

        self.dev_path = path
        self.dev = self.hid.hid_open_path(path)
        if not self.dev:
            err = self.hid.hid_error(None) or "Brak uprawnień do urządzenia"
            path_str = path.decode('utf-8', errors='replace')
            raise PermissionError(
                f"Błąd otwarcia urządzenia {path_str}: {err}\n"
                f"Prawdopodobny brak uprawnień do węzła hidraw.\n"
                f"Rozwiązanie: Uruchom jednorazowo skrypt uprawnień roota:\n"
                f"  sudo /home/user1/test/setup_k530_permissions.sh"
            )

    def disconnect(self):
        if self.dev:
            self.hid.hid_close(self.dev)
            self.dev = None

    @staticmethod
    def _compute_checksum(buf: bytearray):
        # Suma kontrolna liczona od bajtu 0x03 do 0x3F (63)
        chk = sum(buf[3:64]) & 0xFFFF
        buf[1] = chk & 0xFF
        buf[2] = (chk >> 8) & 0xFF

    def _write_packet(self, buf: bytearray, timeout_ms: int = 100) -> bytes:
        if not self.dev:
            raise RuntimeError("Urządzenie nie jest otwarte")
        if len(buf) < 64:
            buf.extend([0] * (64 - len(buf)))

        raw_in = bytes(buf[:64])
        ret = self.hid.hid_write(self.dev, raw_in, 64)
        if ret < 0:
            err = self.hid.hid_error(self.dev) or "Nieznany błąd zapisu HID"
            raise IOError(f"Błąd zapisu do klawiatury: {err}")

        # Odczyt odpowiedzi potwierdzającej
        read_buf = ctypes.create_string_buffer(64)
        self.hid.hid_read_timeout(self.dev, read_buf, 64, timeout_ms)
        return read_buf.raw

    def send_begin(self):
        pkt = bytearray(64)
        pkt[0] = 0x04  # Report ID
        pkt[1] = self.CMD_BEGIN
        pkt[2] = 0x00
        pkt[3] = self.CMD_BEGIN
        self._write_packet(pkt)

    def send_end(self):
        pkt = bytearray(64)
        pkt[0] = 0x04  # Report ID
        pkt[1] = self.CMD_END
        pkt[2] = 0x00
        pkt[3] = self.CMD_END
        self._write_packet(pkt)

    def set_lighting(
        self,
        mode_id: int,
        brightness: int = 4,
        speed: int = 0,
        direction: int = 0,
        random_color: bool = False,
        r: int = 255,
        g: int = 0,
        b: int = 0,
    ):
        """
        Wysyła konfigurację podświetlenia do klawiatury.
        - mode_id: ID trybu (np. 6 dla Static, 1 dla Breathing)
        - brightness: 0 (wył/najniższa) do 4 (maksymalna)
        - speed: 0 (najszybciej) do 10 (najwolniej)
        - direction: 0 (w lewo/domyślny), 1 (w prawo)
        - random_color: True jeśli tryb tęczy / losowy, False dla koloru stałego
        - r, g, b: 0-255 składowe koloru
        """
        brightness = max(0, min(4, brightness))
        speed = max(0, min(10, speed))
        direction = 1 if direction else 0
        rand_flag = 1 if random_color else 0

        self.send_begin()
        time.sleep(0.01)

        pkt = bytearray(64)
        pkt[0] = 0x04                  # Report ID
        pkt[3] = self.CMD_SET_PARAM    # 0x06
        pkt[4] = 0x08                  # Parameter length: 8 bytes
        pkt[5] = 0x00                  # Parameter ID: 0 (Lighting mode config)

        # Dane parametrów (8 bajtów od indeksu 8)
        pkt[8]  = mode_id & 0xFF
        pkt[9]  = brightness & 0xFF
        pkt[10] = speed & 0xFF
        pkt[11] = direction & 0xFF
        pkt[12] = rand_flag & 0xFF
        pkt[13] = r & 0xFF
        pkt[14] = g & 0xFF
        pkt[15] = b & 0xFF

        self._compute_checksum(pkt)
        self._write_packet(pkt)
        time.sleep(0.01)

        self.send_end()


def parse_color(c_str: str) -> Tuple[int, int, int]:
    c_str = c_str.strip().lower()
    if c_str in NAMED_COLORS:
        return NAMED_COLORS[c_str]

    if c_str.startswith("#"):
        c_str = c_str[1:]
    if len(c_str) == 6:
        try:
            return int(c_str[0:2], 16), int(c_str[2:4], 16), int(c_str[4:6], 16)
        except ValueError:
            pass

    if "," in c_str:
        parts = c_str.split(",")
        if len(parts) == 3:
            try:
                return int(parts[0]), int(parts[1]), int(parts[2])
            except ValueError:
                pass

    raise ValueError(f"Nieprawidłowy format koloru: '{c_str}'. Użyj nazwy (red), formatu HEX (#FF0000) lub RGB (255,0,0).")


def main():
    parser = argparse.ArgumentParser(
        description="k530ctl - Kontroler klawiatury Redragon K530 Draconic dla Linux",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:
  k530ctl --status
  k530ctl --list-modes
  k530ctl --mode static --color red --brightness 4
  k530ctl --mode wave --speed 2 --random
  k530ctl --mode breathing --color "#00FFCC" --brightness 3 --speed 5
  k530ctl --mode static --color "0,255,128"
        """
    )

    parser.add_argument("--status", action="store_true", help="Wyświetl status podłączonej klawiatury i interfejsy HID")
    parser.add_argument("--list-modes", action="store_true", help="Wypisz listę wszystkich dostępnych trybów podświetlenia")
    parser.add_argument("--mode", "-m", type=str, help="Nazwa lub numer trybu podświetlenia (np. static, wave, breathing)")
    parser.add_argument("--color", "-c", type=str, default="red", help="Kolor w formacie: nazwa (red, blue), HEX (#00FFAA) lub RGB (255,0,0)")
    parser.add_argument("--brightness", "-b", type=int, default=4, choices=range(0, 5), help="Poziom jasności (0=wył, 1-4)")
    parser.add_argument("--speed", "-s", type=int, default=0, choices=range(0, 11), help="Prędkość animacji (0=najszybciej, 10=najwolniej)")
    parser.add_argument("--direction", "-d", type=int, default=0, choices=[0, 1], help="Kierunek animacji (0=lewo, 1=prawo)")
    parser.add_argument("--random", "-r", action="store_true", help="Włącz tryb tęczy / wielokolorowy (dla trybów animowanych)")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    if args.list_modes:
        print("\n=== Dostępne tryby podświetlenia Redragon K530 ===")
        print(f"{'Klucz CLI':<16} {'ID':<6} {'Opis'}")
        print("-" * 55)
        for key, (m_id, desc) in MODES.items():
            print(f"{key:<16} 0x{m_id:02x}   {desc}")
        print()
        sys.exit(0)

    try:
        ctrl = RedragonK530Controller()
    except Exception as e:
        print(f"[!] Błąd inicjalizacji biblioteki HID: {e}", file=sys.stderr)
        sys.exit(1)

    if args.status:
        try:
            devices = ctrl.get_device_info()
            if not devices:
                print("[-] Nie wykryto klawiatury Redragon K530 (0c45:5004).")
                sys.exit(1)
            print(f"[+] Znaleziono urządzenie Redragon K530 ({len(devices)} punktów końcowych HID):")
            for idx, dev in enumerate(devices):
                is_ctrl = dev['usage_page'] == '0xff1c' and dev['usage'] == '0x0092'
                flag = " <-- [GŁÓWNY PUNKT STEROWANIA]" if is_ctrl else ""
                print(f"  [{idx}] Węzeł: {dev['path']} | Interfejs: {dev['interface']} | UsagePage: {dev['usage_page']} | Usage: {dev['usage']}{flag}")
            
            # Sprawdzenie dostępności zapisu
            try:
                with ctrl:
                    print("\n[+] Status uprawnień: PEŁEN DOSTĘP (odczyt/zapis HID działa poprawnie)")
            except PermissionError as pe:
                print(f"\n[!] Status uprawnień: OGRANICZONY (wymagana konfiguracja udev)")
                print(f"    {pe}")
        except Exception as e:
            print(f"[!] Błąd sprawdzania statusu: {e}", file=sys.stderr)
            sys.exit(1)
        sys.exit(0)

    if args.mode:
        mode_val = args.mode.lower()
        mode_id = None
        if mode_val in MODES:
            mode_id = MODES[mode_val][0]
        else:
            try:
                mode_id = int(mode_val, 0)
            except ValueError:
                print(f"[!] Nieznany tryb '{args.mode}'. Użyj --list-modes aby zobaczyć dostępne tryby.", file=sys.stderr)
                sys.exit(1)

        try:
            r, g, b = parse_color(args.color)
        except ValueError as ve:
            print(f"[!] {ve}", file=sys.stderr)
            sys.exit(1)

        try:
            with ctrl:
                ctrl.set_lighting(
                    mode_id=mode_id,
                    brightness=args.brightness,
                    speed=args.speed,
                    direction=args.direction,
                    random_color=args.random,
                    r=r,
                    g=g,
                    b=b
                )
            print(f"[OK] Pomyślnie zaktualizowano podświetlenie K530:")
            print(f"     Tryb: ID 0x{mode_id:02x}")
            print(f"     Kolor: RGB({r}, {g}, {b})")
            print(f"     Jasność: {args.brightness}/4, Prędkość: {args.speed}/10, Losowy: {args.random}")
        except PermissionError as pe:
            print(f"\n[!] BŁĄD UPRAWNIEŃ:\n{pe}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"[!] Błąd komunikacji z klawiaturą: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
