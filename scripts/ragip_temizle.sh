#!/usr/bin/env bash
# ragip_temizle.sh — ciktilar/ dizin temizleme yardimcisi
# Kullanim: bash scripts/ragip_temizle.sh [--dry-run]
#
# Kural 1: 90 gundan eski dosyalari sil
# Kural 2: Toplam 200 dosyayi asarsa en eski dosyalari sil

set -euo pipefail

ROOT=$(git rev-parse --show-toplevel)
CIKTILAR="$ROOT/data/RAGIP_AGA/ciktilar"
MAX_DOSYA=200
YASLANMA_GUN=90
DRY_RUN=false

for arg in "$@"; do
  [[ "$arg" == "--dry-run" ]] && DRY_RUN=true
done

if [[ ! -d "$CIKTILAR" ]]; then
  echo "ciktilar/ dizini bulunamadi: $CIKTILAR"
  exit 0
fi

# --- Kural 1: Yas bazli temizlik ---
eski_sayi=0
while IFS= read -r -d '' f; do
  eski_sayi=$((eski_sayi + 1))
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "[DRY-RUN] Silinecek (yas): $(basename "$f")"
  else
    rm -f "$f"
  fi
done < <(find "$CIKTILAR" -maxdepth 1 -name "*.md" -mtime +$YASLANMA_GUN -print0 2>/dev/null || true)

if [[ $eski_sayi -gt 0 ]]; then
  echo "$YASLANMA_GUN gundan eski: $eski_sayi dosya${DRY_RUN:+ (dry-run)}"
fi

# --- Kural 2: Limit bazli temizlik ---
toplam=$(find "$CIKTILAR" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
if [[ $toplam -gt $MAX_DOSYA ]]; then
  fazla=$((toplam - MAX_DOSYA))
  echo "Dosya limiti asimi: $toplam / $MAX_DOSYA (fazla: $fazla)"
  limit_sayi=0
  while IFS= read -r f && [[ $limit_sayi -lt $fazla ]]; do
    limit_sayi=$((limit_sayi + 1))
    if [[ "$DRY_RUN" == "true" ]]; then
      echo "[DRY-RUN] Silinecek (limit): $(basename "$f")"
    else
      rm -f "$f"
    fi
  done < <(find "$CIKTILAR" -maxdepth 1 -name "*.md" 2>/dev/null | sort)
fi

kalan=$(find "$CIKTILAR" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
echo "Tamamlandi. Kalan: $kalan dosya"
