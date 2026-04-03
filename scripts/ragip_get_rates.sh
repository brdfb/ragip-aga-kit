#!/bin/bash
# Tek kaynak: TCMB oranlarini JSON olarak dondurur.
# Fallback zinciri: canli API → cache → FALLBACK_RATES → hata
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo ".")
# .env'den TCMB_API_KEY yukle (ragip_rates.py stdlib-only, dotenv kullanmaz)
if [ -f "$ROOT/.env" ] && [ -z "$TCMB_API_KEY" ]; then
    TCMB_API_KEY=$(grep -E '^TCMB_API_KEY=' "$ROOT/.env" | cut -d'=' -f2 | tr -d '"' | tr -d "'")
    export TCMB_API_KEY
fi
RATES=$(python3 "$ROOT/scripts/ragip_rates.py" 2>/dev/null)
if [ -z "$RATES" ] || ! echo "$RATES" | python3 -c "import sys,json;json.load(sys.stdin)" 2>/dev/null; then
    RATES=$(python3 -c "
import sys,json
sys.path.insert(0,'$ROOT/scripts')
from ragip_rates import FALLBACK_RATES
print(json.dumps(FALLBACK_RATES))
" 2>/dev/null)
fi
echo "$RATES"
