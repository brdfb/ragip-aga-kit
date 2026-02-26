# Veri Yapilari

## Firma (data/RAGIP_AGA/firmalar.jsonl)
- tip: tedarikci | musteri | distributor | diger (varsayilan: diger)
- Nakit akisi yonu: tedarikciye "gec ode", musteriye "erken tahsil et"
- Geriye uyumlu: .get('tip', 'diger')

## Fatura (data/RAGIP_AGA/faturalar.jsonl)
ERP-agnostik standart sema. MCP adaptorleri yazar, kit hesaplama motorlari okur. (ADR-0007)
- yon: alacak | borc (alacak = satis faturasi, borc = alis faturasi)
- durum: acik | odendi | kismi | iptal
- Zorunlu alanlar: id, fatura_no, firma_id, yon, tutar, toplam, fatura_tarihi, vade_tarihi, durum
- Opsiyonel: kdv_oran_pct (vars: 20), kdv_tutar, para_birimi (vars: TRY), odeme_tarihi, odeme_tutari, kategori, kaynak, aciklama
- Kismi odeme: odeme_tutari < toplam → durum=kismi
- firma_id → firmalar.jsonl id referansi
- kaynak alani: veriyi yazan MCP/sistem (orn: parasut, d365)
- Tarihler ISO 8601 (YYYY-MM-DD), para_birimi ISO 4217

## Paylasimli Moduller
- scripts/ragip_get_rates.sh — TCMB oran helper (fallback: API -> cache -> FALLBACK_RATES)
- scripts/ragip_crud.py — CRUD helper (load/save jsonl/json, parse_kv, atomic_write, next_id)

## Ortam Degiskenleri
- TCMB_API_KEY: EVDS3 API anahtari (yoksa fallback degerler)
- RAGIP_CACHE_DIR: Cache dizini (varsayilan: scripts/.ragip_cache/)
- COLLECTAPI_KEY: Banka mevduat/kredi oranlari
