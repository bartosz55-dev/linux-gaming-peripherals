# Linux Gaming Peripherals Suite

> Natywny pakiet sterowników, aplikacji GUI oraz narzędzi wiersza poleceń dla urządzeń peryferyjnych na systemy Linux (Arch Linux, Fedora, Ubuntu/Debian).

Obsługiwane urządzenia:
- ⌨ **Redragon K530 Draconic** (Klawiatura mechaniczna 60% RGB, USB ID `0c45:5004`)
- 🖱 **SteelSeries Aerox 3 Wireless & Wired** (Mysz ultralekka RGB z sensorem TrueMove Air, USB ID `1038:1838` / `1038:183a`)

---

## 🌟 Główne Funkcjonalności

### 1. Klawiatura: Redragon K530 Draconic
- **Oryginalny interfejs GUI (`k530gui.py`)**:
  - Wierne odwzorowanie oficjalnego oprogramowania Windows w skali 1:1 (1000 × 640 px).
  - Oryginalne skórki graficzne, współrzędne 62 klawiszy z pliku `Main.ini` oraz 8 fabrycznych barw.
  - Pełna obsługa 19 fabrycznych trybów podświetlenia (Wave, Breathing, Static, Ripple itp.), regulacji jasności i prędkości.
- **Narzędzie CLI (`k530ctl.py`)**:
  - Sterowanie RGB i trybami bezpośrednio z terminala przez protokół USB HID (`libhidapi-hidraw.so`).

### 2. Myszka: SteelSeries Aerox 3 Wireless
- **Nowoczesne GUI w stylu SteelSeries GG (`aeroxgui.py`)**:
  - Elegancki, ciemny motyw (`#121316`) z akcentem **SteelSeries Orange** (`#FF5200`).
  - Podgląd baterii na żywo w procentach wraz z detekcją stanu ładowania (⚡).
  - Interaktywny model z obudową o strukturze plastra miodu (*honeycomb mesh*).
  - Niezależne sterowanie 3 strefami podświetlenia Prism RGB (Góra, Środek, Dół), tryb Rainbow Wave oraz oświetlenie reaktywne na kliknięcia.
  - 5 konfigurowalnych progów czułości CPI/DPI (100 – 18 000 CPI) dla sensora TrueMove Air.
  - Wybór częstotliwości próbkowania USB (125, 250, 500, 1000 Hz) oraz zarządzanie zasilaniem (Sleep / Dim timers).
  - Zapisywanie konfiguracji w pamięci flash myszy (*Onboard Memory*).
- **Narzędzie CLI (`aeroxctl.py`)**:
  - Odczyt baterii, zmiana DPI i kolorów jednym poleceniem.

### 3. Skille dla Agentów AI (Antigravity Skills)
- Wbudowane skille w katalogu `.agents/skills/`:
  - `redragon-k530-keyboard`
  - `steelseries-aerox-mouse`
  - `esp32-*`

---

## 🚀 Szybki Start

### 1. Wymagania systemowe
Pakiet korzysta ze standardowej biblioteki Pythona (Tkinter) oraz systemowej biblioteki `hidapi`:
```bash
# Arch Linux:
sudo pacman -S --needed python tk hidapi

# Ubuntu / Debian:
sudo apt install python3 python3-tk libhidapi-hidraw0

# Fedora:
sudo dnf install python3 python3-tkinter hidapi
```

### 2. Uprawnienia USB (udev)
Aby zarządzać urządzeniami bez konieczności uruchamiania programów jako root:
```bash
# Uprawnienia dla myszki SteelSeries Aerox 3:
sudo ./setup_aerox_permissions.sh

# Uprawnienia dla klawiatury Redragon K530:
sudo ./setup_k530_permissions.sh
```

### 3. Uruchamianie aplikacji

#### Graficzne Panele (GUI):
```bash
# Panel myszki Aerox 3:
python3 tools/aeroxgui.py

# Panel klawiatury K530:
python3 tools/k530gui.py
```

#### Narzędzia Wiersza Poleceń (CLI):
```bash
# Status i stan baterii myszki:
python3 tools/aeroxctl.py --status
python3 tools/aeroxctl.py --battery

# Ustawienie DPI myszy:
python3 tools/aeroxctl.py --dpi 400 800 1200 2400 3200 --preset 1 --save

# Status klawiatury:
python3 tools/k530ctl.py --status

# Ustawienie fali RGB na klawiaturze:
python3 tools/k530ctl.py --mode wave --speed 3
```

---

## 🛠 Struktura Projektu

```
├── tools/
│   ├── aeroxctl.py            # CLI dla myszki SteelSeries Aerox 3
│   ├── aeroxgui.py            # GUI dla myszki SteelSeries Aerox 3
│   ├── aerox_icon.svg         # Wektorowa ikona myszy
│   ├── k530ctl.py             # CLI dla klawiatury Redragon K530
│   ├── k530gui.py             # GUI 1:1 dla klawiatury Redragon K530
│   └── fix_discover.sh        # Skrypt naprawczy dla KDE Discover
├── drivers/
│   └── k530_software/         # Wyodrębnione zasoby graficzne i layout K530
├── setup_aerox_permissions.sh # Konfigurator udev dla Aerox 3
├── setup_k530_permissions.sh  # Konfigurator udev dla K530
├── .agents/skills/            # Skille Antigravity
└── README.md
```

---

## 📄 Licencja
Projekt stworzony do użytku otwartego dla społeczności graczy korzystających z systemów Linux.
Wszystkie znaki towarowe należą do ich odpowiednich właścicieli (Redragon, SteelSeries).
