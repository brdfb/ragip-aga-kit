#!/usr/bin/env bash
# Ragip Aga citation validation helper — skill'lerden cagrilir.
# Cikti dosyasindaki yasal madde referanslarini dogrula.
#
# Kullanim:
#   bash scripts/ragip_madde_dogrula.sh <cikti.md>
#   bash scripts/ragip_madde_dogrula.sh --json <cikti.md>
#
# Exit kodlari:
#   0 = tum referanslar dogrulandi (veya hic referans yok)
#   2 = uydurma sanigi madde bulundu
#   1 = hata (dosya yok vs.)

set -euo pipefail

# Kit root cozumlemesi (git rev-parse veya script dirname'den)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KIT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Python tercih: kit .venv > sistem python3
if [ -x "$KIT_ROOT/.venv/bin/python3" ]; then
    PY="$KIT_ROOT/.venv/bin/python3"
elif [ -x "$KIT_ROOT/.venv/bin/python" ]; then
    PY="$KIT_ROOT/.venv/bin/python"
else
    PY="$(command -v python3 || command -v python)"
fi

if [ -z "$PY" ]; then
    echo "HATA: python3 bulunamadi" >&2
    exit 1
fi

exec "$PY" "$KIT_ROOT/scripts/ragip_madde_dogrula.py" "$@"
