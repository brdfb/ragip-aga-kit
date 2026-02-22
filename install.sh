#!/usr/bin/env bash
set -euo pipefail

# Ragip Aga - Installer
# Hedef repoya Ragip Aga agent/skill/script dosyalarini kurar.
#
# Kullanim:
#   cd /path/to/hedef-repo
#   curl -sSL https://raw.githubusercontent.com/USER/ragip-aga-kit/main/install.sh | bash
#
# veya clone edip:
#   git clone https://github.com/USER/ragip-aga-kit.git /tmp/ragip-aga-kit
#   cd /path/to/hedef-repo
#   bash /tmp/ragip-aga-kit/install.sh

# --- Renk tanimlari ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[+]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
error() { echo -e "${RED}[X]${NC} $*"; exit 1; }

# --- Hedef repo kontrolu ---
HEDEF=$(git rev-parse --show-toplevel 2>/dev/null) || error "Bu dizin bir git reposu degil. Once 'git init' yapin."

# .claude dizini kontrolu
if [ ! -d "$HEDEF/.claude" ]; then
    warn ".claude/ dizini bulunamadi, olusturuluyor..."
    mkdir -p "$HEDEF/.claude"
fi

# --- Kaynak dizini bul ---
# install.sh'nin bulundugu dizin = kit koku
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -f "$SCRIPT_DIR/agents/ragip-aga.md" ]; then
    error "Kaynak dosyalar bulunamadi. install.sh'yi ragip-aga-kit dizininden calistirin."
fi

# --- Kurulum ---
info "Ragip Aga kurulumu basliyor..."
info "Hedef repo: $HEDEF"
echo ""

# 1. Agents
info "Agent dosyalari kopyalaniyor (4 dosya)..."
mkdir -p "$HEDEF/.claude/agents"
cp "$SCRIPT_DIR"/agents/ragip-*.md "$HEDEF/.claude/agents/"

# 2. Skills
info "Skill dosyalari kopyalaniyor (11 skill)..."
for skill_dir in "$SCRIPT_DIR"/skills/ragip-*/; do
    skill_name=$(basename "$skill_dir")
    mkdir -p "$HEDEF/.claude/skills/$skill_name"
    cp "$skill_dir/SKILL.md" "$HEDEF/.claude/skills/$skill_name/"
done

# 3. Scripts
info "Script dosyalari kopyalaniyor (2 dosya)..."
mkdir -p "$HEDEF/scripts"
cp "$SCRIPT_DIR"/scripts/ragip_*.py "$HEDEF/scripts/"

# 4. Config
info "Konfigurasyon kopyalaniyor..."
mkdir -p "$HEDEF/config"
cp "$SCRIPT_DIR"/config/ragip_aga.yaml "$HEDEF/config/"

# 5. Tests (opsiyonel)
if [ -d "$SCRIPT_DIR/tests" ]; then
    info "Test dosyalari kopyalaniyor..."
    mkdir -p "$HEDEF/tests/e2e_ragip_scenario"
    cp "$SCRIPT_DIR"/tests/test_ragip_*.py "$HEDEF/tests/" 2>/dev/null || true
    cp "$SCRIPT_DIR"/tests/e2e_ragip_scenario/* "$HEDEF/tests/e2e_ragip_scenario/" 2>/dev/null || true
fi

# 6. Data dizini
info "Data dizini olusturuluyor..."
mkdir -p "$HEDEF/data/RAGIP_AGA/ciktilar"

# 7. Gitignore
if [ -f "$HEDEF/.gitignore" ]; then
    if ! grep -q "data/RAGIP_AGA/" "$HEDEF/.gitignore" 2>/dev/null; then
        echo "" >> "$HEDEF/.gitignore"
        echo "# Ragip Aga runtime data" >> "$HEDEF/.gitignore"
        echo "data/RAGIP_AGA/" >> "$HEDEF/.gitignore"
        info ".gitignore guncellendi (data/RAGIP_AGA/ eklendi)"
    else
        info ".gitignore zaten data/RAGIP_AGA/ iceriyor"
    fi
    if ! grep -q "scripts/.ragip_cache/" "$HEDEF/.gitignore" 2>/dev/null; then
        echo "scripts/.ragip_cache/" >> "$HEDEF/.gitignore"
        info ".gitignore guncellendi (scripts/.ragip_cache/ eklendi)"
    fi
else
    echo "# Ragip Aga runtime data" > "$HEDEF/.gitignore"
    echo "data/RAGIP_AGA/" >> "$HEDEF/.gitignore"
    echo "scripts/.ragip_cache/" >> "$HEDEF/.gitignore"
    info ".gitignore olusturuldu"
fi

# --- Sonuc ---
echo ""
echo "================================================"
info "Ragip Aga basariyla kuruldu!"
echo "================================================"
echo ""
echo "  Agents:  4  (.claude/agents/ragip-*.md)"
echo "  Skills:  11 (.claude/skills/ragip-*/SKILL.md)"
echo "  Scripts: 2  (scripts/ragip_*.py)"
echo "  Config:  1  (config/ragip_aga.yaml)"
echo ""
echo "Kullanim:"
echo "  /ragip-firma listele          — Firma kartlari"
echo "  /ragip-gorev listele          — Gorev takibi"
echo "  /ragip-vade-farki 250000 3 45 — Vade farki hesapla"
echo "  /ragip-arbitraj               — Arbitraj firsatlari"
echo "  /ragip-profil ABC Dagitim     — Firma profili"
echo "  /ragip-ozet                   — Gunluk brifing"
echo ""
echo "Dogrulama:"
echo "  python -m pytest tests/test_ragip_subagents.py -v"
echo ""

# --- Bagimliliik uyarisi ---
MISSING_DEPS=""
python3 -c "import pdfplumber" 2>/dev/null || MISSING_DEPS="$MISSING_DEPS pdfplumber"
python3 -c "import pandas" 2>/dev/null || MISSING_DEPS="$MISSING_DEPS pandas"
python3 -c "import openpyxl" 2>/dev/null || MISSING_DEPS="$MISSING_DEPS openpyxl"
python3 -c "import yaml" 2>/dev/null || MISSING_DEPS="$MISSING_DEPS pyyaml"

if [ -n "$MISSING_DEPS" ]; then
    warn "Eksik Python bagimliliklari:$MISSING_DEPS"
    echo "  pip install$MISSING_DEPS"
    echo ""
fi
