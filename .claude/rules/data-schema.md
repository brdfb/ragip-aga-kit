# Veri Yapilari

## Firma (data/RAGIP_AGA/firmalar.jsonl)
- tip: tedarikci | musteri | distributor | diger (varsayilan: diger)
- Nakit akisi yonu: tedarikciye "gec ode", musteriye "erken tahsil et"
- Geriye uyumlu: .get('tip', 'diger')

## Paylasimli Moduller
- scripts/ragip_get_rates.sh — TCMB oran helper (fallback: API -> cache -> FALLBACK_RATES)
- scripts/ragip_crud.py — CRUD helper (load/save jsonl/json, parse_kv, atomic_write, next_id)

## Ortam Degiskenleri
- TCMB_API_KEY: EVDS3 API anahtari (yoksa fallback degerler)
- RAGIP_CACHE_DIR: Cache dizini (varsayilan: scripts/.ragip_cache/)
- COLLECTAPI_KEY: Banka mevduat/kredi oranlari
