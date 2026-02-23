#!/usr/bin/env bash
set -euo pipefail

# Ragip Aga - Updater
# Mevcut kurulumu guvenli bir sekilde gunceller.
# Kullanici degisiklikleri korunur, cakismalar yedeklenir.
#
# Kullanim:
#   cd /path/to/hedef-repo
#   bash /path/to/ragip-aga-kit/update.sh
#
# Flagler:
#   --source PATH   Kit kaynak dizini (varsayilan: update.sh'nin bulundugu dizin)
#   --force         Ayni versiyon olsa bile guncelle
#   --dry-run       Degisiklikleri goster ama uygulama

# --- Renk tanimlari ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[+]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
error() { echo -e "${RED}[X]${NC} $*"; exit 1; }

# --- Arguman parse ---
KIT_SOURCE=""
FORCE=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --source)
            KIT_SOURCE="$2"
            shift 2
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            error "Bilinmeyen parametre: $1"
            ;;
    esac
done

# --- Hedef repo kontrolu ---
HEDEF=$(git rev-parse --show-toplevel 2>/dev/null) || error "Bu dizin bir git reposu degil."

# --- Manifest kontrolu ---
MANIFEST_FILE="$HEDEF/config/.ragip_manifest.json"
if [ ! -f "$MANIFEST_FILE" ]; then
    error "Manifest bulunamadi: $MANIFEST_FILE
  Bu repo Ragip Aga kurulumu icermiyor veya eski bir surum.
  Once install.sh ile kurun: bash /path/to/ragip-aga-kit/install.sh"
fi

# --- Kit kaynagini bul ---
if [ -z "$KIT_SOURCE" ]; then
    KIT_SOURCE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

if [ ! -f "$KIT_SOURCE/VERSION" ] || [ ! -f "$KIT_SOURCE/agents/ragip-aga.md" ]; then
    error "Kit kaynak dizini gecersiz: $KIT_SOURCE
  VERSION veya agents/ragip-aga.md bulunamadi.
  Dogru dizini --source ile belirtin: bash update.sh --source /path/to/ragip-aga-kit"
fi

# --- Versiyon karsilastirma ---
NEW_VERSION=$(cat "$KIT_SOURCE/VERSION")
INSTALLED_VERSION=$(python3 -c "import json; print(json.load(open('$MANIFEST_FILE'))['kit_version'])" 2>/dev/null) || error "Manifest okunamadi."

if [ "$INSTALLED_VERSION" = "$NEW_VERSION" ] && [ "$FORCE" = false ]; then
    info "Ragip Aga zaten v$INSTALLED_VERSION surumunde."
    echo "  Zorla guncellemek icin: bash $0 --force"
    exit 0
fi

echo ""
echo "================================================"
info "RAGIP AGA GUNCELLEME: v$INSTALLED_VERSION → v$NEW_VERSION"
echo "================================================"
echo ""

# --- Degiskenleri python'a aktar ---
export _HEDEF="$HEDEF"
export _KIT_SOURCE="$KIT_SOURCE"
export _NEW_VERSION="$NEW_VERSION"
export _DRY_RUN="$( [ "$DRY_RUN" = true ] && echo "true" || echo "false" )"
export _MANIFEST_FILE="$MANIFEST_FILE"

# --- Dosya karsilastirma ve guncelleme ---
python3 << 'UPDATE_CORE'
import json, hashlib, datetime, shutil, sys, os
from pathlib import Path

hedef = os.environ["_HEDEF"]
kit_source = os.environ["_KIT_SOURCE"]
new_version = os.environ["_NEW_VERSION"]
dry_run = os.environ["_DRY_RUN"] == "true"
manifest_file = os.environ["_MANIFEST_FILE"]

# Renk kodlari
G = "\033[0;32m"
Y = "\033[1;33m"
R = "\033[0;31m"
B = "\033[0;34m"
N = "\033[0m"


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def kit_to_installed(kit_rel_path):
    """Kit kaynak yolunu hedef kurulum yoluna donustur."""
    if kit_rel_path.startswith("agents/"):
        return ".claude/" + kit_rel_path
    elif kit_rel_path.startswith("skills/"):
        return ".claude/" + kit_rel_path
    return kit_rel_path


# Manifest oku
manifest = json.loads(Path(manifest_file).read_text(encoding="utf-8"))
old_files = manifest.get("files", {})

# Kit dosyalari tara
kit_files = {}
kit_root = Path(kit_source)

for f in sorted(kit_root.glob("agents/ragip-*.md")):
    rel = kit_to_installed(str(f.relative_to(kit_root)))
    kit_files[rel] = {"kit_path": str(f), "new_hash": sha256_file(f)}

for f in sorted(kit_root.glob("skills/ragip-*/SKILL.md")):
    rel = kit_to_installed(str(f.relative_to(kit_root)))
    kit_files[rel] = {"kit_path": str(f), "new_hash": sha256_file(f)}

for name in ["ragip_aga.py", "ragip_rates.py"]:
    f = kit_root / "scripts" / name
    if f.exists():
        kit_files[f"scripts/{name}"] = {"kit_path": str(f), "new_hash": sha256_file(f)}

f = kit_root / "config" / "ragip_aga.yaml"
if f.exists():
    kit_files["config/ragip_aga.yaml"] = {"kit_path": str(f), "new_hash": sha256_file(f)}

# Uclu checksum karsilastirma
updated = []
skipped_unchanged = []
skipped_user = []
conflicts = []
missing_reinstall = []
new_files = []

all_paths = sorted(set(list(old_files.keys()) + list(kit_files.keys())))

for rel_path in all_paths:
    installed_path = Path(hedef) / rel_path
    in_old = rel_path in old_files
    in_new = rel_path in kit_files

    if in_old and not in_new:
        print(f"  {B}[i]{N} Yeni surumde kaldirildi (korunuyor): {rel_path}")
        continue
    if not in_old and in_new:
        new_files.append(rel_path)
        continue

    manifest_hash = old_files[rel_path].replace("sha256:", "")
    new_hash = kit_files[rel_path]["new_hash"]

    if not installed_path.exists():
        missing_reinstall.append(rel_path)
        continue

    installed_hash = sha256_file(installed_path)

    if installed_hash == manifest_hash and new_hash == manifest_hash:
        skipped_unchanged.append(rel_path)
    elif installed_hash == manifest_hash and new_hash != manifest_hash:
        updated.append(rel_path)
    elif installed_hash != manifest_hash and new_hash == manifest_hash:
        skipped_user.append(rel_path)
    else:
        conflicts.append(rel_path)

# Ozet
total_update = len(updated) + len(missing_reinstall) + len(new_files)
print(f"  {G}[+] Guncellenecek:{N} {total_update} dosya")
for f in updated:
    print(f"      {f}")
for f in missing_reinstall:
    print(f"      {f} (yeniden kurulacak)")
for f in new_files:
    print(f"      {f} (yeni)")
print(f"  {B}[=] Degismedi:{N} {len(skipped_unchanged)} dosya")
print(f"  {Y}[~] Korunan (sizin degisiklikleriniz):{N} {len(skipped_user)} dosya")
for f in skipped_user:
    print(f"      {f}")
print(f"  {R}[!] Cakisma (yedeklenecek):{N} {len(conflicts)} dosya")
for f in conflicts:
    print(f"      {f}")
print("")

if dry_run:
    print(f"  {Y}--dry-run modu: Degisiklik yapilmadi.{N}")
    sys.exit(0)

total_changes = total_update + len(conflicts)
if total_changes == 0:
    print(f"  {G}Guncellenecek dosya yok.{N}")
    sys.exit(0)

# Guncelleme uygula
today = datetime.date.today().strftime("%Y%m%d")


def copy_file(rel_path):
    src = kit_files[rel_path]["kit_path"]
    dst = Path(hedef) / rel_path
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


for rel_path in updated:
    copy_file(rel_path)

for rel_path in conflicts:
    installed_path = Path(hedef) / rel_path
    backup_name = str(installed_path) + f".kullanici-yedek-{today}"
    shutil.copy2(installed_path, backup_name)
    print(f"  {Y}Yedeklendi:{N} {rel_path} → {Path(backup_name).name}")
    copy_file(rel_path)

for rel_path in missing_reinstall:
    copy_file(rel_path)

for rel_path in new_files:
    copy_file(rel_path)

# Yeni manifest
new_manifest_files = {}
for rel_path in sorted(kit_files.keys()):
    installed_path = Path(hedef) / rel_path
    if installed_path.exists():
        new_manifest_files[rel_path] = "sha256:" + sha256_file(installed_path)

for rel_path in skipped_user:
    installed_path = Path(hedef) / rel_path
    if installed_path.exists():
        new_manifest_files[rel_path] = "sha256:" + sha256_file(installed_path)

for rel_path in skipped_unchanged:
    installed_path = Path(hedef) / rel_path
    if installed_path.exists():
        new_manifest_files[rel_path] = "sha256:" + sha256_file(installed_path)

new_manifest = {
    "kit_version": new_version,
    "installed_at": manifest.get("installed_at", datetime.datetime.now().isoformat(timespec="seconds")),
    "updated_at": datetime.datetime.now().isoformat(timespec="seconds"),
    "kit_source": str(kit_root),
    "files": new_manifest_files,
}

Path(manifest_file).write_text(
    json.dumps(new_manifest, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)

print(f"  {G}Manifest guncellendi: v{new_version}{N}")
UPDATE_CORE

echo ""
echo "================================================"
info "Guncelleme tamamlandi!"
echo "================================================"
echo ""
