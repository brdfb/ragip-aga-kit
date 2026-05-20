#!/usr/bin/env bash
# Ragip Aga Kit LLM-judge — Tier 3/4 Spirit (anlamsal) olcumu.
# Tier 5 (format_dogrula.sh) yapisal HARF'i olcer, bu wrapper RUH'u olcer.
#
# Kullanim:
#   bash scripts/ragip_judge.sh <cikti.md>
#   bash scripts/ragip_judge.sh --json <cikti.md>
#   bash scripts/ragip_judge.sh --max-budget-usd 1.0 <cikti.md>
#
# Exit kodlari:
#   0 = judge pass (spirit_score >= 5)
#   2 = judge fail/partial
#   1 = hata (cost limit, ANTHROPIC_API_KEY, parse vb.)
#
# Onkosul: ANTHROPIC_API_KEY env'de tanimli olmali (workspace .env).

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

# .env'den ANTHROPIC_API_KEY otomatik yukle (var ise)
ENV_FILE=""
if [ -f "$KIT_ROOT/.env" ]; then
    ENV_FILE="$KIT_ROOT/.env"
elif [ -f "$(git rev-parse --show-toplevel 2>/dev/null)/.env" ]; then
    ENV_FILE="$(git rev-parse --show-toplevel)/.env"
fi
if [ -n "$ENV_FILE" ] && [ -z "${ANTHROPIC_API_KEY:-}" ]; then
    export ANTHROPIC_API_KEY="$(grep -E '^ANTHROPIC_API_KEY=' "$ENV_FILE" | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'")"
fi

exec "$PY" "$KIT_ROOT/scripts/ragip_judge.py" "$@"
