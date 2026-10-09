#!/usr/bin/env bash
# ==============================================================================
# Automatyczny skrypt tworzenia repozytorium i wypychania na GitHub
# ==============================================================================

set -euo pipefail

REPO_DIR="/home/user1/test"
cd "$REPO_DIR"

echo "==> 1. Sprawdzanie stanu autoryzacji w GitHub CLI (gh)..."
if ! gh auth status >/dev/null 2>&1; then
    echo ""
    echo "[!] Nie jesteś jeszcze zalogowany do GitHuba."
    echo "    Zalogujmy się teraz przez przeglądarkę..."
    echo ""
    gh auth login -h github.com -p https -w
fi

echo ""
echo "==> [OK] Zalogowano pomyślnie!"
gh auth status

REPO_NAME="${1:-linux-gaming-peripherals}"
VISIBILITY="${2:---public}"

echo ""
echo "==> 2. Tworzenie repozytorium '${REPO_NAME}' na Twoim koncie GitHub (${VISIBILITY})..."

# Jeśli origin już istnieje, po prostu wypchnij
if git remote get-url origin >/dev/null 2>&1; then
    echo "    [i] Remote 'origin' już istnieje: $(git remote get-url origin)"
    git push -u origin main
else
    gh repo create "$REPO_NAME" "$VISIBILITY" --source=. --remote=origin --push
fi

echo ""
echo "=============================================================================="
echo "Sukces! Cały projekt został pomyślnie wypchnięty na Twój GitHub:"
gh repo view --web || true
echo "=============================================================================="
