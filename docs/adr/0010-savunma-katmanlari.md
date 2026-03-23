# ADR-0010: Yapilandirilmis Hata Siniflandirmasi ve Savunma Katmanlari

Tarih: 2026-03-23
Durum: Kabul

## Baglam

Kit'in mevcut hata yonetimi ad-hoc: ValueError, bare except, sessiz fallback.
gibibyte-agent'ta (v0.9.0) kanitlanmis 3 savunma katmani var:
1. Failure classification (TRANSIENT/PERMANENT/POLICY)
2. Idempotency fingerprint (SHA-256 dedup)
3. PII scrubbing (maskeleme + hash'leme)

Bu pattern'ler jenerik — her KOBi kurulumunda fayda saglar.

## Karar

Kit'e 3 yeni savunma katmani eklenir:

### 1. Hata Siniflandirmasi (`scripts/ragip_errors.py`)
- `HataTuru` enum: GECICI (retry), KALICI (no retry), POLITIKA (veri duzelt)
- `RagipHata(Exception)`: yapilandirilmis exception, tur/kaynak/orijinal attribute'lari
- `siniflandir(exc)`: exception → HataTuru esleme
- `tekrar_denenebilir(exc)`: retry karari

### 2. Idempotency / Parmak Izi (`scripts/ragip_output.py`)
- `_parmak_izi(agent, skill, icerik)`: SHA-256 fingerprint
- `_ayni_cikti_var_mi(parmak_izi, saat=24)`: 24h dedup penceresi
- `kaydet()` fonksiyonuna `dedup=True` parametresi eklendi
- Manifest entry'lere `parmak_izi` alani eklendi

### 3. PII Temizleyici (`scripts/ragip_pii.py`)
- Yuksek risk (email, tel, TCKN, IBAN): regex ile maskeleme
- Orta risk (firma, musteri, yetkili): SHA-256 hash
- `kaydet()` fonksiyonuna `pii_temizle=False` parametresi eklendi

### 4. TCMB Protocol Pattern (`scripts/ragip_rates.py`)
- `OranSaglayici` Protocol: swap edilebilir oran saglayici arayuzu
- `StubSaglayici`: test icin, API cagrisi yapmaz
- `EVDSSaglayici`: gercek TCMB EVDS3
- `saglayici_olustur()`: factory fonksiyonu

## Gerekce

- gibibyte-agent'ta 8 faz boyunca test edilmis, olgunlasmis pattern'ler
- Jenerik: her KOBi kurulumunda faydali (PII multi-tenant icin, dedup maliyet icin)
- Incremental: her pattern bagimsiz, mevcut davranisi bozmaz
- stdlib only: ek bagimlilik yok (typing.Protocol 3.8+, hashlib, re stdlib)

## Sonuclar

- 2 yeni script: `ragip_errors.py`, `ragip_pii.py`
- 2 degisiklik: `ragip_output.py` (fingerprint + pii), `ragip_rates.py` (protocol)
- 2 yeni test dosyasi, 2 test dosyasina ekleme (~57 yeni test)
- install.sh guncelleme: script sayisi 5 → 7
- Geriye uyumlu: mevcut testler degistirilmez, mevcut API'ler korunur
