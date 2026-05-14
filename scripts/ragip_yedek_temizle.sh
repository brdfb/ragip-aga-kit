#!/usr/bin/env bash
set -euo pipefail

# Ragip Aga - Yedek temizleme yardimcisi (v2.17.1)
#
# update.sh manifest tutarsizligi sonucu olusan SAHTE yedek dosyalarini ayikla.
# Sahte yedek = `.kullanici-yedek-YYYYMMDD` formatli, ICERIGI kit'in herhangi bir
# kayitli versiyonuyla ayni (yani gercek kullanici ozellestirmesi DEGIL).
#
# Gercek kullanici ozellestirmesi olan yedekler KORUNUR — silinmez.
#
# Kullanim:
#   bash scripts/ragip_yedek_temizle.sh             # Dry-run (default — sadece raporlar)
#   bash scripts/ragip_yedek_temizle.sh --apply     # Gercekten sil
#   bash scripts/ragip_yedek_temizle.sh --source PATH  # Kit kaynak dizini

# --- Renk tanimlari ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()  { echo -e "${GREEN}[+]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
error() { echo -e "${RED}[X]${NC} $*"; exit 1; }
note()  { echo -e "${BLUE}[i]${NC} $*"; }

# --- Arguman parse ---
KIT_SOURCE=""
APPLY=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --source)
            KIT_SOURCE="$2"
            shift 2
            ;;
        --apply)
            APPLY=true
            shift
            ;;
        --help|-h)
            grep '^#' "$0" | sed 's/^# \?//' | head -20
            exit 0
            ;;
        *)
            error "Bilinmeyen parametre: $1 (yardim: --help)"
            ;;
    esac
done

# --- Hedef repo ---
HEDEF=$(git rev-parse --show-toplevel 2>/dev/null) || error "Bu dizin bir git reposu degil."

if [ ! -f "$HEDEF/config/.ragip_manifest.json" ]; then
    error "Manifest yok: $HEDEF/config/.ragip_manifest.json
  Bu repoda Ragip Aga kurulu degil."
fi

# --- Kit kaynagini bul ---
if [ -z "$KIT_SOURCE" ]; then
    # Manifest'ten kit_source bilgisi al, yoksa script'in bulundugu kit'i kullan
    KIT_SOURCE=$(python3 -c "import json; print(json.load(open('$HEDEF/config/.ragip_manifest.json')).get('kit_source',''))" 2>/dev/null)
    if [ -z "$KIT_SOURCE" ] || [ ! -d "$KIT_SOURCE" ]; then
        KIT_SOURCE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    fi
fi

if [ ! -f "$KIT_SOURCE/VERSION" ]; then
    error "Kit kaynagi gecersiz: $KIT_SOURCE (VERSION dosyasi yok). --source ile belirt."
fi

echo "================================================"
info "RAGIP AGA YEDEK TEMIZLE — hedef: $HEDEF"
info "Kit kaynagi: $KIT_SOURCE"
echo "================================================"
echo

if [ "$APPLY" = false ]; then
    note "Dry-run modu (varsayilan). Gercek silme icin --apply ekle."
    echo
fi

# --- Yedek dosyalarini tara ---
# Python ile yedek dosyalari bul, her birinin disk icerigini kit dosyasi (kayitli surum)
# ile karsilastir. Kit'te ayni icerige sahip varsa SAHTE yedek say.

python3 - "$HEDEF" "$KIT_SOURCE" "$APPLY" <<'PYEOF'
import os
import sys
import hashlib
import json
from pathlib import Path
import subprocess

hedef = Path(sys.argv[1])
kit_source = Path(sys.argv[2])
apply = sys.argv[3] == "true"

def sha256_path(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

# Yedek dosyalarini bul
yedek_pattern = "*.kullanici-yedek-*"
yedekler = []
for sub in (".claude/agents", ".claude/skills", "scripts", "config", "tests"):
    base = hedef / sub
    if not base.exists():
        continue
    for p in base.rglob(yedek_pattern):
        yedekler.append(p)

if not yedekler:
    print("Yedek dosyasi bulunamadi. Temiz.")
    sys.exit(0)

# Asil dosya yolu (yedek son ekini cikar)
def asil_yol(yedek):
    # foo.md.kullanici-yedek-20260513 → foo.md
    name = yedek.name
    idx = name.rfind(".kullanici-yedek-")
    if idx < 0:
        return None
    return yedek.parent / name[:idx]

# Asil dosyanin kit kaynagindaki karsiligini bul
def kit_yolu(asil):
    rel = asil.relative_to(hedef)
    rel_str = str(rel)
    # .claude/agents/X.md → agents/X.md (kit'te)
    # .claude/skills/X/SKILL.md → skills/X/SKILL.md (kit'te)
    if rel_str.startswith(".claude/"):
        rel_str = rel_str[len(".claude/"):]
    return kit_source / rel_str

sahte = []
gercek = []
soru = []

for yedek in yedekler:
    asil = asil_yol(yedek)
    if asil is None:
        soru.append((yedek, "Yedek format dısı"))
        continue
    kit_dosya = kit_yolu(asil)
    if not kit_dosya.exists():
        soru.append((yedek, f"Kit kaynagi yok: {kit_dosya}"))
        continue
    yedek_hash = sha256_path(yedek)
    kit_hash = sha256_path(kit_dosya)
    # Eski kit versiyonlarinin git history'sinde de var mi check
    git_match = False
    try:
        log = subprocess.run(
            ["git", "-C", str(kit_source), "log", "--all", "--pretty=format:%H",
             "--diff-filter=A", "--", str(kit_dosya.relative_to(kit_source))],
            capture_output=True, text=True, check=False, timeout=5
        )
        # Daha basit yontem: yedek icerigini git'te tum versionlarda ara
        for commit in subprocess.run(
            ["git", "-C", str(kit_source), "log", "--all", "--pretty=format:%H", "--",
             str(kit_dosya.relative_to(kit_source))],
            capture_output=True, text=True, check=False, timeout=5
        ).stdout.split("\n"):
            commit = commit.strip()
            if not commit:
                continue
            blob = subprocess.run(
                ["git", "-C", str(kit_source), "show", f"{commit}:{kit_dosya.relative_to(kit_source)}"],
                capture_output=True, check=False, timeout=3
            )
            if blob.returncode == 0 and hashlib.sha256(blob.stdout).hexdigest() == yedek_hash:
                git_match = True
                break
    except Exception:
        pass

    if yedek_hash == kit_hash or git_match:
        sahte.append((yedek, "Kit history'sinde mevcut" if git_match else "Mevcut kit ile ayni"))
    else:
        gercek.append((yedek, asil))

print(f"\nToplam yedek: {len(yedekler)}")
print(f"  Sahte (silinebilir): {len(sahte)}")
print(f"  Gercek ozellestirme (KORUMA): {len(gercek)}")
print(f"  Belirsiz (manuel inceleme): {len(soru)}")

if sahte:
    print("\n--- SAHTE YEDEKLER (silinecek) ---")
    for y, sebep in sahte:
        rel = y.relative_to(hedef)
        print(f"  [SAHTE] {rel}  ({sebep})")

if gercek:
    print("\n--- GERCEK OZELLESTIRMELER (KORUNACAK) ---")
    for y, asil in gercek:
        rel = y.relative_to(hedef)
        asil_rel = asil.relative_to(hedef)
        print(f"  [KORU]  {rel}")
        print(f"          asil: {asil_rel} (yedek icerigiyle farkli)")

if soru:
    print("\n--- BELIRSIZ (elle bakilmali) ---")
    for y, sebep in soru:
        rel = y.relative_to(hedef)
        print(f"  [?] {rel}  ({sebep})")

if not apply:
    print("\n(Dry-run — silinmedi. Gercekten silmek icin --apply ekle.)")
    sys.exit(0)

if not sahte:
    print("\nSilinecek sahte yedek yok.")
    sys.exit(0)

print("\nSahte yedekler siliniyor...")
for y, _ in sahte:
    y.unlink()
    print(f"  silindi: {y.relative_to(hedef)}")
print(f"\nToplam {len(sahte)} sahte yedek silindi.")
if gercek:
    print(f"{len(gercek)} gercek ozellestirme yedegi KORUNDU.")
PYEOF

echo
echo "================================================"
info "Tamamlandi."
echo "================================================"
