# ADR-0007: Standart Fatura Semasi — ERP-Agnostik Veri Sozlesmesi
Tarih: 2026-02-26
Durum: Kabul edildi

## Baglam
Kit 11 temel finansal metrigi (aging, DSO, tahsilat orani, gelir trendi, musteri konsantrasyonu, KDV ozeti vb.) hesaplayabilmeli. Ancak fatura/islem verisi yok — mevcut veri modeli firma karti (firmalar.jsonl) ve gorev takibi (gorevler.jsonl) ile sinirli.

Kit farkli hedef repolara kurulacak. Her repoda farkli ERP/CRM olabilir (Parasut, D365, Logo, Mikro, Netsis...). Kit hesaplama motorlari ERP'den bagimsiz calismali.

ADR-0004 prensibi: kit = zeka, MCP = veri, hedef repo = bulusma noktasi.

## Karar
ERP-agnostik standart fatura semasi tanimlandi. MCP adaptorleri kendi ERP'sinden veriyi ceker ve bu formata normalize eder. Kit hesaplama motorlari yalnizca bu formati tuketir.

### Sema: faturalar.jsonl

Dosya yolu: `data/RAGIP_AGA/faturalar.jsonl`

| Alan | Tip | Zorunlu | Aciklama |
|------|-----|---------|----------|
| id | int | evet | Otomatik artan (next_id) |
| fatura_no | str | evet | Kaynak sistemdeki fatura numarasi |
| firma_id | int | evet | firmalar.jsonl'deki id referansi |
| yon | str | evet | `alacak` \| `borc` |
| tutar | float | evet | KDV haric net tutar |
| kdv_oran_pct | float | hayir | KDV orani (orn: 20.0). Varsayilan: 20 |
| kdv_tutar | float | hayir | KDV tutari. Bos ise tutar × kdv_oran_pct/100 |
| toplam | float | evet | KDV dahil toplam |
| para_birimi | str | hayir | ISO 4217 (TRY, USD, EUR). Varsayilan: TRY |
| fatura_tarihi | str | evet | ISO 8601 (YYYY-MM-DD) |
| vade_tarihi | str | evet | ISO 8601 |
| odeme_tarihi | str\|null | hayir | null = odenmedi |
| odeme_tutari | float\|null | hayir | Kismi odeme destegi. null = odenmedi |
| durum | str | evet | `acik` \| `odendi` \| `kismi` \| `iptal` |
| kategori | str | hayir | Serbest etiket (orn: hizmet, lisans, mal) |
| kaynak | str | hayir | Veriyi yazan MCP/sistem (orn: parasut, d365) |
| aciklama | str | hayir | Serbest metin |

### yon alani mantigi
- `alacak` = musteriye kesilen satis faturasi (bize odeme gelecek)
- `borc` = tedarikciden gelen alis faturasi (biz odeyecegiz)
- Kit'in mevcut nakit akisi yonu ile uyumlu: tedarikciye gec ode, musteriden erken tahsil et

### durum alani gecisleri
```
acik ──→ odendi      (tam odeme)
acik ──→ kismi       (odeme_tutari < toplam)
kismi ──→ odendi     (kalan da odendi)
acik ──→ iptal       (fatura iptal)
```

### Hangi metrik hangi alani kullaniyor

| Metrik | Gereken alanlar |
|--------|----------------|
| Aging raporu | vade_tarihi, toplam, yon=alacak, durum=acik\|kismi |
| DSO | yon=alacak, toplam, odeme_tutari, fatura_tarihi |
| Tahsilat orani | yon=alacak, toplam, odeme_tutari, fatura_tarihi |
| Gelir trendi | yon=alacak, toplam, fatura_tarihi |
| Musteri konsantrasyonu | yon=alacak, firma_id, toplam |
| KDV donem ozeti | kdv_tutar, fatura_tarihi, yon |
| DPO (veri varsa) | yon=borc, fatura_tarihi, odeme_tarihi, toplam |

### Kit sinirinda kalan metrikler (ayri veri gerekir)
- Brut kar: maliyet verisi (ERP)
- DIO: stok verisi (ERP)
- Enflasyon duzeltmesi: TUFE endeksi (TCMB/TUIK)
- Butce vs gerceklesme: butce verisi (ERP/kullanici)

### Tasarim ilkeleri
1. **Kit ERP bilmez.** Hesaplama motorlari sadece bu semayi okur.
2. **MCP adaptorleri kit bilmez.** Sadece bu semaya yazar.
3. **ragip_crud.py kullanilir.** load_jsonl/save_jsonl, next_id, atomic_write — ayni altyapi.
4. **kaynak alani izlenebilirlik saglar.** Hangi MCP'den geldi, belli.
5. **Kismi odeme desteklenir.** odeme_tutari < toplam → durum=kismi.
6. **para_birimi alani coklu doviz destegi saglar.** Hesaplamalar TRY bazli, kur cevrimi gerekirse ragip_rates.py'den alinir.

## Sonuc
- Kit'in hesaplama motorlari tek bir veri sozlesmesine baglanir, ERP bagimliligi sifir
- 7 metrik (aging, DSO, tahsilat, trend, konsantrasyon, KDV, DPO) bu sema ile hesaplanabilir
- Farkli ERP kullanan firmalar ayni kit'i kullanabilir — sadece MCP adaptorleri farkli
- Trade-off: MCP adaptorleri normalize etme yukunu tasir; her yeni ERP icin bir adaptor yazilmali
- Trade-off: Kismi odeme ve coklu doviz destegi semayi biraz karistiriyor, ama gercek hayat boyle
