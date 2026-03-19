# ADR-0008: Test Stratejisi — Structural Oncelikli, Behavioral Out-of-Scope
Tarih: 2026-03-19
Durum: Kabul edildi

## Baglam

Kit'te 290 test var (v2.8.9). Bu sayi guvenilir bir test altyapisi izlenimi verebilir. Ancak testlerin buyuk cogunlugu structural dogrulama yapiyor:

- Frontmatter alanlari dogru mu? (name, model, maxTurns, skills, disallowedTools)
- Dosyalar dogru yerde mi?
- Skill dagilimi cakisiyor mu?
- Path'ler hardcoded mi?
- Versiyon tutarli mi?

Test edilmeyen alanlar:

- Ragip Aga kullanicinin istegini dogru sub-agent'a yonlendiriyor mu?
- ragip-hesap'in hesaplamalari matematiksel olarak dogru mu (gercek fatura verisiyle)?
- Sub-agent ciktilari kullanilabilir formatta mi?
- Skill'ler beklenen aksiyonu uretiyor mu?

Bu belge kit'in test stratejisi icin bilinçli bir karar kaydeder.

## Karar

**Structural testler (Katman 1) birincil test katmani olmaya devam eder.**

Davranissal / e2e testler (Katman 3-4) MCP veri akisi baslayana kadar out-of-scope.

### Test katmanlari

| Katman | Tip | Durum | Araç |
|--------|-----|-------|------|
| 1 | Structural — frontmatter, dosya, port., versiyon | Mevcut (290 test) | pytest |
| 2 | Unit — FinansalHesap, CRUD, rates | Mevcut (~80 test) | pytest |
| 3 | Integration — gercek fatura akisi ile hesaplama dogrulugu | **Eksik — MCP sonrasi** | pytest + fixture |
| 4 | E2E — LLM routing, skill ciktisi kalitesi | **Kapsam disi** | — |

### Neden Katman 3 simdi yapilmiyor

Katman 3 integration testleri gercek fatura verisi gerektirir. Kit'te su an sifir gercek fatura var — `faturalar.jsonl` bos. MCP adaptoru (Parasut veya D365) gelmeden anlamli bir integration fixture olusturulamaz. El ile yazilan sentetik fixture FinansalHesap'in gercek veriyle calisip calismadigi sorusunu cevaplamaz.

MCP veri akisi basladiginda Katman 3 ilk yapilacak istir (FEATURE_IDEAS #17 ile baglantili).

### Neden Katman 4 kapsam disi

LLM davranisi non-deterministic: ayni girdi farkli turde farkli cikti uretebilir. E2E test her calistirmada farkli sonuc verebilir, bu da testin guvenilirligi yoktur. Ayrica her LLM cagrisinin maliyeti var. Bu iki sebepten Katman 4 sistematik test icin uygun degil.

Pratik alternatif: Bir senaryo seti elle calistirilip sonuclar incelenir (golden path review), otomasyon degil.

### Mevcut durumun sonucu

"290 test geciyor" ifadesi dogruydu: **structural butunluk saglamlidir.** Ama "kit dogru cevap veriyor mu?" sorusu test edilmemistir ve bu bilerek kabul edilmis bir trade-off.

## Alternativler

**Alternatif A: Simdi sentetik fixture yaz**
Elle olusturulmus sahte fatura verisiyle FinansalHesap calistir. Avantaj: beklemeden test katmani eklenir. Dezavantaj: Sahte veri gercek uretim verisiyle farkli dagilim gosterir — agirlikli yanlis guven saglar. Reddedildi.

**Alternatif C: Sentetik fatura verisiyle FinansalHesap regresyon testi**
Bilerek basitlestirilmis, el ile dogrulanmis sentetik veriyle temel hesaplama dogruluğu testi. Avantaj: MCP'ye bagimli degil, regresyon yakalar. Dezavantaj: Gercek veri dagilimini yansitmaz. **Degerlendiriliyor** — Katman 3'un ilk adimi olabilir.

**Alternatif B: E2E test framework kur (LangSmith, Braintrust)**
LLM ciktilarini degerlendirecek bir framework entegre et. Avantaj: Katman 4 test edilir. Dezavantaj: Kit'in dis bagimlilik politikasini bozar (ADR-0005), maliyetli, tek kullanici icin overengineering. Reddedildi.

## Sonuc

- Structural + unit testler saglam ve yeterli mevcut asama icin.
- Katman 3 integration testleri MCP veri akisi basladiginda eklenir — bu bir gecerli hedef.
- Katman 4 e2e LLM testleri bilinçli olarak kapsam disi birakiliyor.
- "Test sayisi cok = guvenilir" cikarimina karsı: sayida degil kapsam kalitesinde guclu olmak hedef.
