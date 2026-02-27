# Ragip Aga Kit — Feature Ideas

Canli deneyim, sohbetler ve mimari degerlendirmelerden derlenen fikirler.
Oncelik yok, siralama yok — acip bakip "simdi hangisi mantikli" diye degerlendirilecek liste.

Tarih: 2026-02-27

---

## 1. Agent Tool Kisitlama (Yapisal)

**Sorun:** Agent, hedef repoda MCP tool gorunde system prompt talimatini atlayip dogrudan MCP'ye yoneliyor. Ayni veri CLI'dan dogru, agent uzerinden yanlis sonuc.

**Cozum:** Claude Code frontmatter'da `tools:` (allowlist) veya `disallowedTools:` (denylist) destekliyor. Ornek:
```yaml
# ragip-aga.md
tools: Bash, Task, Read
```
MCP tool'lari gorünmez olur. Simdi prompt sertlestirme ile cozuldu (v3) ama yapisal enforcement daha guvenilir.

**Effort:** Kucuk — tek satir frontmatter degisikligi + test
**Risk:** Dusuk — geriye uyumlu, MCP olmayan ortamlarda etkisiz
**Oncelik:** MCP entegrasyonu cogaldikca artar

---

## 2. Merkezi Cikti Sema Referansi

**Sorun:** Her skill kendi cikti formatini tanimliyor. Ornegin aging raporu baska format, degerlendirme baska, ihtar baska. Tutarlilik yok.

**Fikir:** `docs/output-standards.md` — tum cikti turleri icin:
- Standart header yapisi (baslik, tarih, agent, skill, parametreler)
- Rapor tiplerine gore sablon (hesaplama, analiz, hukuki, veri)
- Ragip Aga ses rehberi (do/don't)

**Effort:** Orta — mevcut skill'lerden pattern cikarip dokumante etmek
**Risk:** Over-engineering tehlikesi — 15 skill icin erken olabilir
**Oncelik:** Kit 20+ skill'e cikarsa veya 3. parti kullanici gelirse

---

## 3. Cikti Dosyalarinda Meta Block

**Sorun:** `ciktilar/` altindaki dosyalarda sadece icerik var. Hangi kit versiyonu, hangi parametrelerle, hangi veri kaynagiyla uretildigi belli degil.

**Fikir:** Her cikti dosyasinin basina YAML frontmatter:
```yaml
---
kit_version: 2.7.0
agent: ragip-hesap
skill: ragip-rapor
parametreler: {tur: aging, donem_gun: 90}
tarih: 2026-02-27T14:30:22
veri_kaynagi: faturalar.jsonl (42 kayit)
---
```

**Effort:** Kucuk-orta — cikti kaydetme bloklarini guncellemek
**Risk:** Dusuk — mevcut dosyalara dokunmaz
**Oncelik:** Izlenebilirlik/audit gereksinimi olursa

---

## 4. Markdown Rapor Template'leri

**Sorun:** ragip-rapor skill'inde rapor formatlama inline Python'da. Yeni rapor turu eklenince ayni formatlama kodu tekrar yaziliyor.

**Fikir:** `templates/` dizini veya `scripts/ragip_templates.py`:
- Tablo olusturucu (dict -> markdown tablo)
- Rapor wrapper (baslik + meta + icerik + yorum)
- Ragip Aga imza blogu

**Effort:** Orta — mevcut formatlama kodunu refactor etmek
**Risk:** Erken soyutlama — 7 rapor icin yeterli mi?
**Oncelik:** 10+ rapor turue cikarsa

---

## 5. Nakit Cevrim Dongusu Dashboard

**Sorun:** DSO, DPO ayri ayri hesaplaniyor. Nakit cevrim dongusu (CCC = DSO + DIO - DPO) tek rapor olarak yok.

**Fikir:** `FinansalHesap.nakit_cevrim_dashboard()`:
- DSO + DPO + tahsilat orani + aging tek cagri
- Trend karsilastirmasi (bu ay vs gecen ay)
- Stok varsa DIO dahil (profil'den `stok.var` kontrolu)

**Effort:** Kucuk — mevcut metotlari birlestirmek
**Risk:** Dusuk — yeni metot, mevcut koda dokunmaz
**Oncelik:** Orta — gercek kullanim senaryosunda faydali

---

## 6. Fatura Uyari Sistemi

**Sorun:** Faturalar.jsonl'de vade gecmis faturalar var ama kit bunu sadece sorulunca soyluyor. Proaktif degil.

**Fikir:** `ragip-ozet` skill'ine veya yeni bir `ragip-uyari` skill'ine:
- Vade gecmis faturalar (bugun > vade_tarihi, durum=acik)
- Yaklasan vadeler (7 gun icinde)
- Yogunlasan risk (tek firmadan cok fatura)
- TTK m.21/2 fatura itirazi 8 gun suresi yaklasanlar

**Effort:** Orta — yeni metot + skill prompt
**Risk:** Dusuk
**Oncelik:** Yuksek — gercek kullanim degeri yuksek

---

## 7. Firma Bazli Rapor

**Sorun:** Tum raporlar (aging, DSO, DPO) tum faturalar uzerinden calisiyor. "ABC Dagitim icin aging raporu" yapilamiyor.

**Fikir:** Mevcut metotlara `firma_id` filtresi:
```python
FinansalHesap.aging_raporu(faturalar, firma_id=10)
FinansalHesap.dso(faturalar, firma_id=10)
```

**Effort:** Kucuk — her metota 3-4 satir filtre eklemek
**Risk:** Dusuk
**Oncelik:** Yuksek — en dogal kullanim senaryosu

---

## 8. Odeme Plani Takibi

**Sorun:** Kit vade farki hesapliyor, strateji olusturuyor ama onerilen odeme planinin takibi yok. "Su firmaya 3 taksit onerdik, 1. taksit odendi mi?" sorusuna yanit yok.

**Fikir:** `data/RAGIP_AGA/odeme_planlari.jsonl`:
- firma_id, plan_tarihi, taksitler (tarih, tutar, durum)
- ragip-gorev ile entegre — taksit yaklasinca gorev olustur

**Effort:** Orta-buyuk — yeni veri yapisi + CRUD + skill
**Risk:** Orta — scope creep riski
**Oncelik:** Dusuk — once temel raporlama olgunlasmali

---

## 9. E-Fatura / E-Arsiv Entegrasyonu Hazirlik

**Sorun:** Turkiye'de e-fatura zorunlu. Kit fatura semasinda `kaynak` alani var ama e-fatura XML (UBL-TR) parse etme yok.

**Fikir:** `scripts/ragip_efatura_parser.py`:
- UBL-TR XML -> ADR-0007 fatura semasi donusumu
- Standalone, stdlib + xml.etree (sifir bagimlilik)
- MCP tarafinda degil, kit tarafinda — cunku sema donusumu kit'in isi

**Effort:** Orta — UBL-TR spec okumak + parser yazmak
**Risk:** Orta — UBL-TR spec karmasik
**Oncelik:** e-fatura entegrasyonu gundemdeyse

---

## 10. Coklu Para Birimi Destegi

**Sorun:** Tum hesaplamalar TRY bazli. `para_birimi` alani ADR-0007'de var ama metotlar bunu kullanmiyor. USD/EUR fatura gelince yanlis hesap.

**Fikir:** Fatura analiz metotlarinda `para_birimi` filtresi veya TCMB kuru ile TRY'ye cevirme:
- Ayni para birimindeki faturalari grupla
- Veya TCMB kuru ile normalize et
- Raporda para birimi bazinda ayrim goster

**Effort:** Orta — her metota doviz mantigi eklemek
**Risk:** Orta — kur hangi tarihin kuru? Spot mu, fatura tarihindeki mi?
**Oncelik:** Doviz faturasi olan firmalar icin yuksek

---

## Degerlendirme Notu

Bu liste "yapilacaklar" degil, "dusunulecekler". Her madde icin soru:
1. Gercek kullanici bunu istedi mi / ihtiyac duydu mu?
2. Mevcut cozum (prompt, manuel islem) yeterli mi?
3. Implement edince test edilebilir mi?

Cevaplarin ucUu de "evet" ise yapmaya deger.
