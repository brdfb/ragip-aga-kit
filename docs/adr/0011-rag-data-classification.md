# ADR-0011: RAG Veri Siniflandirma Politikasi

**Tarih:** 2026-03-26
**Durum:** Kabul Edildi

## Baglan

Kit hedef repoya kuruldugunda RAG bilgi tabani ile birlikte kullanilabilir.
Musteri/fiyat/portfoy verisi RAG'a konmamali — bu veriler ERP/CRM'de tutulur.

## Karar

4 katmanli veri siniflandirma sistemi uygulanir:

| Katman | Etiket | RAG'da mi? | Ornekler |
|--------|--------|------------|----------|
| 1 | public | Evet | Urun dokumanlar, genel proseduler |
| 2 | internal | Evet (varsayilan) | SOP, playbook, marka rehberi |
| 3 | confidential | HAYIR | Musteri faturasi, fiyat, anlasma |
| 4 | restricted | ASLA | PII, credential, hukuki veri |

### Temel kural

```
RAG = nasil yapilir (prosedur, standart, rehber)
ERP/CRM = kimin neyi var (musteri, fiyat, lisans, anlasma)
```

### Uygulama noktalari (hedef repoda)

1. **Frontmatter classification**: Her knowledge dosyasinda `classification: public|internal`
2. **Indexleme engeli**: confidential/restricted dosyalar indexlenmez
3. **PII taramasi**: Indexleme oncesi ragip_pii.metin_temizle() ile maskeleme
4. **Retrieval filtresi**: Varsayilan max_classification=internal
5. **Cikti maskeleme**: Arama sonuclarina metin_temizle() uygulanir
6. **Ekleme validasyonu**: PII iceren icerik reddedilir

## Alternatifler

1. **Tek katman (hepsini indexle)**: Reddedildi — veri sizintisi riski
2. **Ayri collection'lar**: Gereksiz karmasiklik — metadata filtresi yeterli

## Sonuclar

- Agent prompt'larinda VERI GUVENLIK KURALLARI bolumu zorunlu
- Musteri/fiyat/anlasma verisi ASLA RAG'a konmaz
- Kit PII modulu (ragip_pii.py) RAG pipeline'ina entegre edilebilir
