#!/usr/bin/env python3
"""
aeroxctl - SteelSeries Aerox 3 Wireless Controller for Linux
Narzędzie CLI i biblioteka sterująca myszkami SteelSeries Aerox 3 Wireless
(tryb bezprzewodowy 2.4 GHz oraz przewodowy USB).

Obsługiwane urządzenia:
  - SteelSeries Aerox 3 Wireless (Dongle: 1038:1838, Przewód: 1038:183A)
  - SteelSeries Aerox 3 Wireless CS2 Edition (Dongle: 1038:1878, Przewód: 1038:187A)
  - SteelSeries Aerox 3 Wired (1038:1836)

Funkcje:
  - Odczyt poziomu naładowania baterii (%) oraz stanu ładowania
  - Niezależne sterowanie 3 strefami podświetlenia RGB (góra, środek, dół)
  - Tryb Rainbow Effect
  - Konfiguracja czułości DPI (TrueMove Air: 100 - 18000 DPI, do 5 poziomów)
  - Wybór częstotliwości próbkowania USB (125, 250, 500, 1000 Hz)
  - Ustawianie timera uśpienia (Sleep Timer) i przyciemnienia (Dim Timer)
  - Zapisywanie ustawień w pamięci myszy (Onboard Memory)
"""

import os
import sys
import argparse
import ctypes
import time
from typing import Optional, Tuple, Dict, List

# TrueMove Air Sensor DPI Byte Mapping (100 - 18000 DPI, krok 100)
TRUEMOVE_AIR_DPI: Dict[int, int] = {
    100: 0x00, 200: 0x02, 300: 0x03, 400: 0x04, 500: 0x05, 600: 0x06, 700: 0x07, 800: 0x09,
    900: 0x0A, 1000: 0x0B, 1100: 0x0C, 1200: 0x0D, 1300: 0x0E, 1400: 0x10, 1500: 0x11, 1600: 0x12,
    1700: 0x13, 1800: 0x14, 1900: 0x16, 2000: 0x17, 2100: 0x18, 2200: 0x19, 2300: 0x1A, 2400: 0x1B,
    2500: 0x1D, 2600: 0x1E, 2700: 0x1F, 2800: 0x20, 2900: 0x21, 3000: 0x23, 3100: 0x25, 3200: 0x26,
    3300: 0x27, 3400: 0x28, 3500: 0x29, 3600: 0x2A, 3700: 0x2C, 3800: 0x2D, 3900: 0x2E, 4000: 0x2F,
    4100: 0x30, 4200: 0x32, 4300: 0x33, 4400: 0x34, 4500: 0x35, 4600: 0x36, 4700: 0x38, 4800: 0x39,
    4900: 0x3A, 5000: 0x3B, 5100: 0x3C, 5200: 0x3E, 5300: 0x3F, 5400: 0x40, 5500: 0x41, 5600: 0x42,
    5700: 0x44, 5800: 0x45, 5900: 0x46, 6000: 0x47, 6100: 0x48, 6200: 0x4A, 6300: 0x4B, 6400: 0x4C,
    6500: 0x4D, 6600: 0x4E, 6700: 0x50, 6800: 0x51, 6900: 0x52, 7000: 0x53, 7100: 0x54, 7200: 0x56,
    7300: 0x57, 7400: 0x58, 7500: 0x59, 7600: 0x5A, 7700: 0x5C, 7800: 0x5D, 7900: 0x5E, 8000: 0x5F,
    8100: 0x60, 8200: 0x62, 8300: 0x63, 8400: 0x64, 8500: 0x65, 8600: 0x66, 8700: 0x68, 8800: 0x69,
    8900: 0x6A, 9000: 0x6B, 9100: 0x6C, 9200: 0x6E, 9300: 0x6F, 9400: 0x70, 9500: 0x71, 9600: 0x72,
    9700: 0x74, 9800: 0x75, 9900: 0x76, 10000: 0x77, 10100: 0x78, 10200: 0x7A, 10300: 0x7B, 10400: 0x7C,
    10500: 0x7D, 10600: 0x7E, 10700: 0x80, 10800: 0x81, 10900: 0x82, 11000: 0x83, 11100: 0x84, 11200: 0x86,
    11300: 0x87, 11400: 0x88, 11500: 0x89, 11600: 0x8A, 11700: 0x8C, 11800: 0x8D, 11900: 0x8E, 12000: 0x8F,
    12100: 0x90, 12200: 0x92, 12300: 0x93, 12400: 0x94, 12500: 0x95, 12600: 0x96, 12700: 0x98, 12800: 0x99,
    12900: 0x9A, 13000: 0x9B, 13100: 0x9C, 13200: 0x9E, 13300: 0x9F, 13400: 0xA0, 13500: 0xA1, 13600: 0xA2,
    13700: 0xA4, 13800: 0xA5, 13900: 0xA6, 14000: 0xA7, 14100: 0xA8, 14200: 0xAA, 14300: 0xAB, 14400: 0xAC,
    14500: 0xAD, 14600: 0xAE, 14700: 0xB0, 14800: 0xB1, 14900: 0xB2, 15000: 0xB3, 15100: 0xB4, 15200: 0xB5,
    15300: 0xB6, 15400: 0xB7, 15500: 0xB8, 15600: 0xB9, 15700: 0xBA, 15800: 0xBB, 15900: 0xBC, 16000: 0xBD,
    16100: 0xBF, 16200: 0xC0, 16300: 0xC2, 16400: 0xC3, 16500: 0xC4, 16600: 0xC5, 16700: 0xC6, 16800: 0xC7,
    16900: 0xC9, 17000: 0xCA, 17100: 0xCB, 17200: 0xCC, 17300: 0xCD, 17400: 0xCF, 17500: 0xD0, 17600: 0xD1,
    17700: 0xD2, 17800: 0xD3, 17900: 0xD5, 18000: 0xD6
}

POLLING_RATES: Dict[int, int] = {
    1000: 0x00,
    500:  0x01,
    250:  0x02,
    125:  0x03,
}

NAMED_COLORS: Dict[str, Tuple[int, int, int]] = {
    "red":     (255, 0, 0),
    "green":   (0, 255, 0),
    "blue":    (0, 0, 255),
    "yellow":  (255, 255, 0),
    "cyan":    (0, 255, 255),
    "magenta": (255, 0, 255),
    "white":   (255, 255, 255),
    "orange":  (255, 82, 0),     # SteelSeries Orange
    "purple":  (128, 0, 255),
    "pink":    (255, 105, 180),
    "lime":    (50, 255, 50),
    "off":     (0, 0, 0),
}

# --- CTYPES HIDAPI BINDINGS ---
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
    return None


class AeroxMouse:
    """Klasa sterująca myszką SteelSeries Aerox 3."""

    SUPPORTED_MODELS = {
        0x1838: ("SteelSeries Aerox 3 Wireless (2.4 GHz)", True, 3),
        0x183A: ("SteelSeries Aerox 3 Wireless (Wired)", False, 3),
        0x1878: ("SteelSeries Aerox 3 Wireless CS2 Edition (2.4 GHz)", True, 3),
        0x187A: ("SteelSeries Aerox 3 Wireless CS2 Edition (Wired)", False, 3),
        0x1836: ("SteelSeries Aerox 3 Wired", False, 3),
    }

    def __init__(self):
        self.hid = load_hidapi()
        if not self.hid:
            raise RuntimeError("Nie znaleziono biblioteki hidapi (libhidapi-hidraw.so). Zainstaluj hidapi.")
        self.hid.hid_init()
        self.handle = None
        self.path: Optional[bytes] = None
        self.product_id: Optional[int] = None
        self.model_name: str = "Unknown"
        self.is_wireless: bool = False
        self.interface_num: int = 3

    def find_device(self) -> bool:
        """Wyszukuje i identyfikuje urządzenie SteelSeries Aerox."""
        devs = self.hid.hid_enumerate(0x1038, 0)
        curr = devs
        candidates = []

        while curr:
            info = curr.contents
            pid = info.product_id
            if pid in self.SUPPORTED_MODELS:
                name, wireless, req_iface = self.SUPPORTED_MODELS[pid]
                if info.interface_number == req_iface or (info.usage_page == 0xFFC0 and info.usage == 0x01):
                    candidates.append((info.path, pid, name, wireless, info.interface_number))
            curr = info.next

        self.hid.hid_free_enumeration(devs)

        if not candidates:
            return False

        # Wybierz pierwszy pasujący interfejs sterujący
        self.path, self.product_id, self.model_name, self.is_wireless, self.interface_num = candidates[0]
        return True

    def open(self) -> bool:
        """Otwiera urządzenie HID."""
        if not self.path:
            if not self.find_device():
                return False

        self.handle = self.hid.hid_open_path(self.path)
        if not self.handle:
            err = self.hid.hid_error(None)
            raise PermissionError(f"Brak dostępu do {self.path.decode('utf-8', errors='ignore')}: {err}")
        return True

    def close(self):
        """Zamyka urządzenie HID."""
        if self.handle:
            self.hid.hid_close(self.handle)
            self.handle = None

    def _send_command(self, cmd_bytes: List[int]) -> bool:
        """Wysyła raport wyjściowy do myszki z uwzględnieniem flagi trybu bezprzewodowego."""
        if not self.handle:
            raise RuntimeError("Urządzenie nie jest otwarte.")

        payload = list(cmd_bytes)
        if self.is_wireless:
            payload[0] |= 0x40  # Flaga bezprzewodowa 2.4 GHz

        # Report ID 0x00 + payload
        data = bytearray([0x00] + payload)
        c_buf = (ctypes.c_char * len(data)).from_buffer(data)
        res = self.hid.hid_write(self.handle, c_buf, len(data))
        time.sleep(0.015)  # Odstęp bezpieczeństwa między poleceniami
        return res >= 0

    def _read_response(self, length: int = 64, timeout_ms: int = 250) -> Optional[bytes]:
        """Odczytuje odpowiedź z urządzenia HID."""
        if not self.handle:
            raise RuntimeError("Urządzenie nie jest otwarte.")

        buf = ctypes.create_string_buffer(length)
        res = self.hid.hid_read_timeout(self.handle, buf, length, timeout_ms)
        if res > 0:
            return buf.raw[:res]
        return None

    def get_battery(self) -> Dict[str, Optional[int]]:
        """Odczytuje stan naładowania baterii."""
        # Komenda 0x92 (lub 0xD2 w trybie wireless)
        cmd = [0x92]
        if not self._send_command(cmd):
            return {"level": None, "is_charging": None}

        resp = self._read_response(length=64, timeout_ms=300)
        if not resp or len(resp) < 2:
            return {"level": None, "is_charging": None}

        # Format odpowiedzi:
        # resp[0] = nagłówek / komenda, resp[1] = stan baterii
        # bit 7: flaga ładowania (0x80)
        # bity 0-6: wartość bazowa (poziom = (wartość - 1) * 5)
        status_byte = resp[1]
        is_charging = bool(status_byte & 0x80)
        raw_level = (status_byte & ~0x80)
        if raw_level > 0:
            level = max(0, min(100, (raw_level - 1) * 5))
        else:
            level = 0

        return {"level": level, "is_charging": is_charging}

    def set_zone_color(self, zone: int, r: int, g: int, b: int) -> bool:
        """
        Ustawia kolor pojedynczej strefy:
          zone 0: góra (top / z1)
          zone 1: środek (middle / z2)
          zone 2: dół (bottom / z3)
        """
        zone = max(0, min(2, zone))
        cmd = [0x21, 0x01, zone, r & 0xFF, g & 0xFF, b & 0xFF]
        return self._send_command(cmd)

    def set_all_colors(self, r: int, g: int, b: int) -> bool:
        """Ustawia jednakowy kolor dla wszystkich 3 stref."""
        ok = True
        for z in range(3):
            if not self.set_zone_color(z, r, g, b):
                ok = False
        return ok

    def set_rainbow(self) -> bool:
        """Włącza efekt tęczy (Rainbow Effect)."""
        return self._send_command([0x22, 0xFF])

    def set_reactive_color(self, r: int, g: int, b: int) -> bool:
        """Ustawia kolor reaktywny przy kliknięciu przycisku."""
        if r == 0 and g == 0 and b == 0:
            return self._send_command([0x26, 0x00])
        return self._send_command([0x26, r & 0xFF, g & 0xFF, b & 0xFF])

    def set_dpi(self, presets: List[int], selected_idx: int = 0) -> bool:
        """
        Ustawia profile czułości DPI (od 1 do 5 poziomów, 100 - 18000 DPI).
        selected_idx: indeks aktywnego profilu (0-indexed).
        """
        if not presets:
            raise ValueError("Wymagany jest przynajmniej jeden profil DPI.")
        if len(presets) > 5:
            presets = presets[:5]

        # Zaokrąglij DPI do najbliższej setki
        mapped_bytes = []
        for dpi in presets:
            rounded = int(round(dpi / 100.0) * 100)
            rounded = max(100, min(18000, rounded))
            code = TRUEMOVE_AIR_DPI.get(rounded, 0x04)
            mapped_bytes.append(code)

        count = len(presets)
        selected_idx = max(0, min(count - 1, selected_idx))

        # Komenda 0x2D: [0x2D, count, selected_preset, v0, v1, ...]
        cmd = [0x2D, count, selected_idx] + mapped_bytes
        return self._send_command(cmd)

    def set_polling_rate(self, hz: int) -> bool:
        """Ustawia częstotliwość raportowania USB (125, 250, 500, 1000 Hz)."""
        if hz not in POLLING_RATES:
            raise ValueError(f"Nieobsługiwana częstotliwość {hz} Hz. Wybierz spośród: 125, 250, 500, 1000")
        code = POLLING_RATES[hz]
        return self._send_command([0x2B, code])

    def set_sleep_timer(self, minutes: int) -> bool:
        """Ustawia czas bezczynności przed uśpieniem myszy (0 = wyłączone, max 20 min)."""
        minutes = max(0, min(20, minutes))
        ms = minutes * 60000
        b0 = ms & 0xFF
        b1 = (ms >> 8) & 0xFF
        b2 = (ms >> 16) & 0xFF
        return self._send_command([0x29, b0, b1, b2])

    def set_dim_timer(self, seconds: int) -> bool:
        """Ustawia czas bezczynności przed przyciemnieniem podświetlenia (0 = wyłączone, max 1200 sek)."""
        seconds = max(0, min(1200, seconds))
        ms = seconds * 1000
        b0 = ms & 0xFF
        b1 = (ms >> 8) & 0xFF
        b2 = (ms >> 16) & 0xFF
        return self._send_command([0x23, 0x0F, 0x01, 0x00, 0x00, b0, b1, b2])

    def save(self) -> bool:
        """Zapisuje bieżącą konfigurację w pamięci flash myszy (Onboard Memory)."""
        return self._send_command([0x11, 0x00])


def parse_color_str(color_str: str) -> Tuple[int, int, int]:
    """Konwertuje nazwę koloru lub kod HEX (#RRGGBB / RRGGBB) na trójkę (R, G, B)."""
    clean = color_str.strip().lower()
    if clean in NAMED_COLORS:
        return NAMED_COLORS[clean]
    if clean.startswith("#"):
        clean = clean[1:]
    if len(clean) == 6:
        try:
            return int(clean[0:2], 16), int(clean[2:4], 16), int(clean[4:6], 16)
        except ValueError:
            pass
    raise ValueError(f"Nieznany format koloru: '{color_str}'. Użyj nazwy lub formatu hex np. #FF5200")


def print_banner():
    print("=" * 64)
    print("  SteelSeries Aerox 3 Linux Controller (aeroxctl)")
    print("=" * 64)


def main():
    parser = argparse.ArgumentParser(
        description="Natywny kontroler myszy SteelSeries Aerox 3 Wireless dla Linux",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--status", action="store_true", help="Wyświetl status urządzenia, baterię i parametry")
    parser.add_argument("--battery", action="store_true", help="Pobierz aktualny poziom naładowania baterii (%%)")
    parser.add_argument("-c", "--color", help="Ustaw kolor dla wszystkich 3 stref (np. #FF5200 lub orange, red, off)")
    parser.add_argument("--top", help="Ustaw kolor strefy górnej (Z1)")
    parser.add_argument("--middle", help="Ustaw kolor strefy środkowej (Z2)")
    parser.add_argument("--bottom", help="Ustaw kolor strefy dolnej (Z3)")
    parser.add_argument("--rainbow", action="store_true", help="Włącz efekt wielokolorowej fali (Rainbow Effect)")
    parser.add_argument("--reactive", help="Ustaw kolor reakcji na kliknięcie lub 'off'")
    parser.add_argument("-s", "--dpi", nargs="+", type=int, help="Ustaw progi DPI (1 do 5 wartości np. --dpi 400 800 1200 2400)")
    parser.add_argument("--preset", type=int, default=0, help="Indeks aktywnego progu DPI (0-4, domyślnie 0)")
    parser.add_argument("-p", "--polling-rate", type=int, choices=[125, 250, 500, 1000], help="Częstotliwość próbkowania USB w Hz")
    parser.add_argument("-t", "--sleep-timer", type=int, help="Czas bezczynności do uśpienia (0-20 min)")
    parser.add_argument("-T", "--dim-timer", type=int, help="Czas bezczynności do przyciemnienia (0-1200 sek)")
    parser.add_argument("--save", action="store_true", help="Zapisz ustawienia na stałe w pamięci wewnętrznej myszy")

    args = parser.parse_args()

    # Jeśli brak argumentów, pokaż pomoc
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    mouse = AeroxMouse()

    try:
        if not mouse.find_device():
            print("[!] Nie wykryto podłączonej myszy SteelSeries Aerox 3.")
            print("    Upewnij się, że odbiornik USB 2.4 GHz lub przewód jest wpięty.")
            sys.exit(1)

        try:
            mouse.open()
        except PermissionError as pe:
            print(f"[!] Błąd uprawnień: {pe}")
            print("\n    Aby nadać uprawnienia do portu HID bez roota, wykonaj jednorazowo:")
            print("    sudo /home/user1/test/setup_aerox_permissions.sh\n")
            sys.exit(2)

        # Obsługa zapytań
        if args.status:
            print_banner()
            print(f"  Model:       {mouse.model_name}")
            print(f"  ID:          0x1038:0x{mouse.product_id:04X}")
            print(f"  Tryb:        {'Bezprzewodowy 2.4 GHz' if mouse.is_wireless else 'Przewodowy USB'}")
            print(f"  Węzeł HID:   {mouse.path.decode('utf-8', errors='ignore')}")

            bat = mouse.get_battery()
            if bat["level"] is not None:
                charging_str = " (Ładowanie...)" if bat["is_charging"] else ""
                print(f"  Bateria:     {bat['level']}%{charging_str}")
            else:
                print("  Bateria:     Brak danych / Mysz w stanie uśpienia")
            print("=" * 64)

        if args.battery:
            bat = mouse.get_battery()
            if bat["level"] is not None:
                charging_str = " [Ładowanie]" if bat["is_charging"] else ""
                print(f"Bateria: {bat['level']}%{charging_str}")
            else:
                print("Brak odpowiedzi baterii (mysz może być uśpiona).")

        # Ustawienia kolorów
        if args.color:
            r, g, b = parse_color_str(args.color)
            mouse.set_all_colors(r, g, b)
            print(f"[OK] Ustawiono kolor podświetlenia dla wszystkich stref: RGB({r}, {g}, {b})")

        if args.top:
            r, g, b = parse_color_str(args.top)
            mouse.set_zone_color(0, r, g, b)
            print(f"[OK] Ustawiono strefę górną (Z1): RGB({r}, {g}, {b})")

        if args.middle:
            r, g, b = parse_color_str(args.middle)
            mouse.set_zone_color(1, r, g, b)
            print(f"[OK] Ustawiono strefę środkową (Z2): RGB({r}, {g}, {b})")

        if args.bottom:
            r, g, b = parse_color_str(args.bottom)
            mouse.set_zone_color(2, r, g, b)
            print(f"[OK] Ustawiono strefę dolną (Z3): RGB({r}, {g}, {b})")

        if args.rainbow:
            mouse.set_rainbow()
            print("[OK] Włączono efekt tęczy (Rainbow Effect)")

        if args.reactive:
            if args.reactive.lower() == "off":
                mouse.set_reactive_color(0, 0, 0)
                print("[OK] Wyłączono kolor reaktywny.")
            else:
                r, g, b = parse_color_str(args.reactive)
                mouse.set_reactive_color(r, g, b)
                print(f"[OK] Ustawiono kolor reaktywny: RGB({r}, {g}, {b})")

        # Czułość DPI
        if args.dpi:
            mouse.set_dpi(args.dpi, selected_idx=args.preset)
            print(f"[OK] Ustawiono progi DPI: {args.dpi} (aktywny profil: {args.preset})")

        # Polling rate
        if args.polling_rate:
            mouse.set_polling_rate(args.polling_rate)
            print(f"[OK] Ustawiono częstotliwość próbkowania: {args.polling_rate} Hz")

        # Timery
        if args.sleep_timer is not None:
            mouse.set_sleep_timer(args.sleep_timer)
            print(f"[OK] Ustawiono Sleep Timer: {args.sleep_timer} min.")

        if args.dim_timer is not None:
            mouse.set_dim_timer(args.dim_timer)
            print(f"[OK] Ustawiono Dim Timer: {args.dim_timer} sek.")

        # Zapis
        if args.save:
            mouse.save()
            print("[OK] Zapisano konfigurację w pamięci stałej myszy (Onboard Memory).")

    finally:
        mouse.close()


if __name__ == "__main__":
    main()
