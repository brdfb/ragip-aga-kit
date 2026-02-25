# ADR-0006: Hukuk Sub-Agent
Tarih: 2026-02-25
Durum: Kabul edildi

## Baglam
Kit'te hukuki analiz eksikti. ragip-ihtar sablon uretiyor, ragip-strateji maliyet hesapliyor, ragip-analiz madde tespit ediyor — ama hicbiri "hakli miyiz?" sorusunu yanitlayamiyordu. KOBi uyusmazliklarinda mevzuata dayali degerlendirme, zamanasimi takibi ve delil stratejisi gerekiyordu.

## Karar
4. sub-agent olarak ragip-hukuk (sonnet) eklendi. 3 yeni skill + ragip-ihtar tasimasi:

- **ragip-degerlendirme** (LLM): Hukuki haklilik analizi, madde bazli yorum, GUCLU/ORTA/ZAYIF verdikt
- **ragip-zamanasimi** (prosedurel): Yasal sure hesaplayici (fatura itirazi, zamanasimi, KVKK)
- **ragip-delil** (LLM): Delil gucu puanlama, eksik delil tespiti, avukata dosya hazirligi
- **ragip-ihtar** (tasindi): ragip-arastirma'dan ragip-hukuk'a. Icerik ayni, semantik yerlesim daha dogru.

ragip-ihtar tasima karari: Ihtar hukuki belge uretir, analiz/strateji degil. Ayni agent'ta degerlendirme -> delil -> ihtar akisi mumkun.

## Sonuc
- Kit artik "hakli miyiz?" sorusuna mevzuat cercevesinde yanit verebilir
- Zamanasimi takibi ile yasal sure kaybi riski azalir
- Delil stratejisi avukata gitme oncesi hazirligi kolaylastirir
- ragip-arastirma 4->3 skill ile daha odakli (analiz, arastirma, strateji)
- Trade-off: Dispatch overhead artti (4 sub-agent), ihtar tasimasi breaking change (test guncelleme gerekti)
