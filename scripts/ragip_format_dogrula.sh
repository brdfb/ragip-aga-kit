#!/usr/bin/env bash
# Ragip Aga Tier 3/4 format validation — skill'lerden cagrilir.
# Cikti dosyasinda zenginlestirilmis blok formati (TESPIT/Etki/POZISYON/GEREKCE)
# ve Tier 4 tutarlilik denetimi notunu dogrula.
#
# Kullanim:
#   bash scripts/ragip_format_dogrula.sh <cikti.md>
#   bash scripts/ragip_format_dogrula.sh --json <cikti.md>
#
# Exit kodlari:
#   0 = format temiz (tum zorunlu sinyaller mevcut)
#   2 = format eksik (en az 1 zorunlu sinyal yok)
#   1 = hata (dosya yok vs.)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KIT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ -x "$KIT_ROOT/.venv/bin/python3" ]; then
    PY="$KIT_ROOT/.venv/bin/python3"
elif [ -x "$KIT_ROOT/.venv/bin/python" ]; then
    PY="$KIT_ROOT/.venv/bin/python"
elif [ -x "$KIT_ROOT/.ragip-venv/bin/python3" ]; then
    PY="$KIT_ROOT/.ragip-venv/bin/python3"
elif [ -x "$KIT_ROOT/.ragip-venv/bin/python" ]; then
    PY="$KIT_ROOT/.ragip-venv/bin/python"
else
    PY="$(command -v python3 || command -v python)"
fi

if [ -z "$PY" ]; then
    echo "HATA: python3 bulunamadi" >&2
    exit 1
fi

exec "$PY" "$KIT_ROOT/scripts/ragip_format_dogrula.py" "$@"
