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
#   git clone https://github.com/brdfb/ragip-aga-kit.git /tmp/ragip-aga-kit
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

# --- Kit versiyonu ---
KIT_VERSION=$(cat "$SCRIPT_DIR/VERSION" 2>/dev/null) || error "VERSION dosyasi bulunamadi."

# --- Mevcut kurulum kontrolu ---
if [ -f "$HEDEF/config/.ragip_manifest.json" ]; then
    INSTALLED_VERSION=$(python3 -c "import json; print(json.load(open('$HEDEF/config/.ragip_manifest.json'))['kit_version'])" 2>/dev/null || echo "")
    if [ -n "$INSTALLED_VERSION" ]; then
        warn "Mevcut Ragip Aga kurulumu tespit edildi (v$INSTALLED_VERSION)."
        warn "Guncelleme icin update.sh kullanin: bash $SCRIPT_DIR/update.sh"
        if [ -t 0 ]; then
            read -p "[?] Yine de sifirdan kurmak istiyor musunuz? Mevcut kit dosyalari uzerine yazilacak. (y/N) " OVERWRITE
            [ "$OVERWRITE" != "y" ] && [ "$OVERWRITE" != "Y" ] && exit 0
        fi
    fi
fi

# --- Kurulum ---
info "Ragip Aga v$KIT_VERSION kurulumu basliyor..."
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
info "Script dosyalari kopyalaniyor (4 dosya)..."
mkdir -p "$HEDEF/scripts"
cp "$SCRIPT_DIR"/scripts/ragip_*.py "$HEDEF/scripts/"
cp "$SCRIPT_DIR"/scripts/ragip_get_rates.sh "$HEDEF/scripts/"
chmod +x "$HEDEF/scripts/ragip_get_rates.sh"

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

# 7. Manifest olustur
info "Kurulum manifesti olusturuluyor..."
python3 << MANIFEST_EOF
import json, hashlib, datetime
from pathlib import Path

hedef = "$HEDEF"
version = "$KIT_VERSION"
source = "$SCRIPT_DIR"

files = {}

# Agents
for f in sorted(Path(hedef, ".claude/agents").glob("ragip-*.md")):
    rel = str(f.relative_to(hedef))
    sha = hashlib.sha256(f.read_bytes()).hexdigest()
    files[rel] = "sha256:" + sha

# Skills
for f in sorted(Path(hedef, ".claude/skills").glob("ragip-*/SKILL.md")):
    rel = str(f.relative_to(hedef))
    sha = hashlib.sha256(f.read_bytes()).hexdigest()
    files[rel] = "sha256:" + sha

# Scripts
for name in ["ragip_aga.py", "ragip_rates.py", "ragip_crud.py", "ragip_get_rates.sh"]:
    f = Path(hedef, "scripts", name)
    if f.exists():
        rel = str(f.relative_to(hedef))
        sha = hashlib.sha256(f.read_bytes()).hexdigest()
        files[rel] = "sha256:" + sha

# Config
f = Path(hedef, "config/ragip_aga.yaml")
if f.exists():
    rel = str(f.relative_to(hedef))
    sha = hashlib.sha256(f.read_bytes()).hexdigest()
    files[rel] = "sha256:" + sha

# Tests
for f in sorted(Path(hedef, "tests").glob("test_ragip_*.py")):
    rel = str(f.relative_to(hedef))
    sha = hashlib.sha256(f.read_bytes()).hexdigest()
    files[rel] = "sha256:" + sha

now = datetime.datetime.now().isoformat(timespec="seconds")
manifest = {
    "kit_version": version,
    "installed_at": now,
    "updated_at": now,
    "kit_source": source,
    "files": files,
}

Path(hedef, "config/.ragip_manifest.json").write_text(
    json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)
print(f"  {len(files)} dosya manifeste kaydedildi")
MANIFEST_EOF

# 8. Gitignore
# Yedek dosyalari gitignore'a ekle
if [ -f "$HEDEF/.gitignore" ]; then
    if ! grep -q "*.kullanici-yedek*" "$HEDEF/.gitignore" 2>/dev/null; then
        echo "*.kullanici-yedek*" >> "$HEDEF/.gitignore"
    fi
fi
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

# 9. Opsiyonel venv + pip install
if [ -t 0 ]; then
    read -p "[?] Python venv olusturup bagimliliklari kurayim mi? (y/N) " INSTALL_DEPS
    if [ "$INSTALL_DEPS" = "y" ] || [ "$INSTALL_DEPS" = "Y" ]; then
        python3 -m venv "$HEDEF/.ragip-venv"
        "$HEDEF/.ragip-venv/bin/pip" install -q -r "$SCRIPT_DIR/requirements.txt"
        info "Venv olusturuldu: $HEDEF/.ragip-venv/"
    fi
fi

# 10. Opsiyonel shell alias
if [ -t 0 ]; then
    read -p "[?] 'ragip' shell alias tanimlayayim mi? (y/N) " SETUP_ALIAS
    if [ "$SETUP_ALIAS" = "y" ] || [ "$SETUP_ALIAS" = "Y" ]; then
        SHELL_RC="$HOME/.bashrc"
        [ -n "$ZSH_VERSION" ] && SHELL_RC="$HOME/.zshrc"
        VENV_PYTHON="$HEDEF/.ragip-venv/bin/python"
        [ ! -f "$VENV_PYTHON" ] && VENV_PYTHON="python3"
        echo "" >> "$SHELL_RC"
        echo "# Ragip Aga CLI" >> "$SHELL_RC"
        echo "alias ragip='$VENV_PYTHON $HEDEF/scripts/ragip_aga.py'" >> "$SHELL_RC"
        info "Alias eklendi: $SHELL_RC"
        info "Aktif etmek icin: source $SHELL_RC"
    fi
fi

# --- Sonuc ---
echo ""
echo "================================================"
info "Ragip Aga v$KIT_VERSION basariyla kuruldu!"
echo "================================================"
echo ""
echo "  Agents:  4  (.claude/agents/ragip-*.md)"
echo "  Skills:  11 (.claude/skills/ragip-*/SKILL.md)"
echo "  Scripts: 4  (scripts/ragip_*.py + ragip_get_rates.sh)"
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
