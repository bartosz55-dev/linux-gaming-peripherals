#!/usr/bin/env bash
# ==============================================================================
# Naprawa problemów z aktualizacjami w KDE Discover na Arch Linux
# ==============================================================================

set -euo pipefail

echo "==> 1. Wyłączanie problematycznego trybu aktualizacji offline w discoverrc..."
DISCOVER_RC="${HOME}/.config/discoverrc"
if [ -f "${DISCOVER_RC}" ]; then
    if grep -q "UseOfflineUpdates" "${DISCOVER_RC}"; then
        sed -i 's/UseOfflineUpdates=true/UseOfflineUpdates=false/' "${DISCOVER_RC}"
    else
        echo -e "\n[Software]\nUseOfflineUpdates=false" >> "${DISCOVER_RC}"
    fi
    echo "    [OK] Zaktualizowano ${DISCOVER_RC}: UseOfflineUpdates=false"
fi

echo "==> 2. Czyszczenie pamięci podręcznej Discover i powiadomień..."
rm -rf "${HOME}/.cache/discover"/*
echo "    [OK] Wyczyszczono ~/.cache/discover/"

echo "==> 3. Wymuszanie odświeżenia bazy AppStream..."
if command -v appstreamcli >/dev/null 2>&1; then
    appstreamcli refresh-cache --force 2>/dev/null || true
    echo "    [OK] Pomyślnie odświeżono bazę AppStream"
fi

echo "==> 4. Sprawdzanie brakujących bibliotek backendu Discover (PackageKit, Fwupd)..."
MISSING_PKGS=()
if ! pacman -Q packagekit-qt6 >/dev/null 2>&1; then
    MISSING_PKGS+=("packagekit-qt6")
fi
if ! pacman -Q fwupd >/dev/null 2>&1; then
    MISSING_PKGS+=("fwupd")
fi

if [ ${#MISSING_PKGS[@]} -gt 0 ]; then
    echo "    [!] Wykryto brakujące backendy: ${MISSING_PKGS[*]}"
    echo "    Discover próbuje je ładować przy każdym starcie, co powoduje błędy i spowolnienia."
    if [ "$(id -u)" -eq 0 ]; then
        echo "    Instalowanie brakujących pakietów..."
        pacman -S --noconfirm --needed "${MISSING_PKGS[@]}"
    else
        echo "    Aby całkowicie wyeliminować błędy w Discover i umożliwić aktualizacje pakietów systemowych:"
        echo "    sudo pacman -S --needed ${MISSING_PKGS[*]}"
    fi
else
    echo "    [OK] Wszystkie backendy Discover są zainstalowane."
fi

echo ""
echo "=============================================================================="
echo "Sukces! Konfiguracja Discover została naprawiona."
echo "Aktualizacje Flatpak i aplikacji będą teraz instalowane bezpośrednio na żywo."
echo "=============================================================================="
