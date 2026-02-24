# ADR-0005: DRY Helpers
Tarih: 2025-02-18
Durum: Kabul edildi

## Baglam
v2.4.0'da 6 skill ayni TCMB oran cekme kodunu tekrarliyordu. 5 CRUD skill'i benzer dosya IO, JSON parse, atomic write kodunu iceriyordu (~%60 ortak boilerplate).

## Karar
Iki paylasimli helper olusturuldu:
- **scripts/ragip_get_rates.sh**: TCMB oran cekme tek kaynak. Fallback zinciri: canli API -> cache -> FALLBACK_RATES. 6 tekrar -> 1 helper.
- **scripts/ragip_crud.py**: CRUD skill'leri icin paylasimli modul. get_root, load/save jsonl/json, parse_kv, atomic_write, next_id. ~%60 boilerplate azaltma.

Her iki helper da standalone calisabilir ve testleri var.

## Sonuc
- Skill dosyalari kisaldi, bakimi kolaylasti
- Bir degisiklik (ornegin cache TTL) tek yerde yapilir
- Yeni CRUD skill eklemek kolaylasti (ragip_crud.py import et)
- Trade-off: Helper degisirse tum bagli skill'ler etkilenir (ama testler yakalar)
