# ADR-0021: Gibibyte-spesifik skill'ler workspace'te (kural takviyesi)

**Tarih:** 2026-07-06
**Durum:** Kabul edildi
**İlgili:** ADR-0004 (Kit vs MCP Ayrımı), ADR-0007 (Standart Fatura Şeması — ERP-agnostik)

## Bağlam

ADR-0004 kit'in **domain-genel KOBi finans/hukuk danışmanı** olmasını, workspace/hedef repo'nun **Gibibyte'a özgü** yapılandırmayı içermesini kararlaştırmıştı. Ancak 4 Nisan 2026'da commit `a968919` ile 4 skill kit'e "acil müşteri ihtiyacı" (Zeren UAT) altında **doğrudan** eklendi:

- `ragip-teklif` — Ingram maliyet + MCI teşvik + mevduat float + 3 senaryolu fiyat modeli (Gibibyte satış ekibi)
- `ragip-maliyet` — Ingram YA vs YM, NCE prim hesabı (Gibibyte satış)
- `ragip-yenileme` — Lisans yenileme kit list değişim (Gibibyte satış)
- `ragip-esles` — Satış-alış fatura çapraz doğrulama, kaçak kontrolü (Gibibyte iç kontrol)

Bu skill'ler:
- **38, 16, 7, 1 kez Gibibyte-spesifik terim** içeriyordu (Ingram, MCI, NCE, Noventiq, Makronet)
- ADR-0004 sınırını **fiilen ihlal ediyordu** — başka bir MSP hedef repo'ya install.sh çalıştırıldığında bu skill'ler işe yaramaz (rakip distributor, farklı program)
- Kit-workspace ayrımını bozuyordu: workspace'te de aynı skill'ler mevcut, install.sh her seferinde kit'in kopyasını workspace'in üzerine yazıyordu (`for skill_dir in "$SCRIPT_DIR"/skills/ragip-*/`) — silent duplicate/override
- CHANGELOG'a eklenmemişti (governance ihlali)
- Test dosyası yoktu (ADR-0008 test stratejisi ihlali)

Bu 3 aylık "unutulmuş kısa yol" 5 Temmuz 2026 v2.20.2 doc cleanup Faz B sonrası kit özet kontrolünde fark edildi ("emin misin, dikkatlice baktın mı?" sorusuyla).

## Karar

1. **4 skill kit'ten silinir** (v2.20.3). Workspace tarafında zaten identik kopya var — bilgi kaybı yok.
2. **Kural formal olarak yeniden ilan edilir:** Skill'in içeriği bir müşterinin/tedarikçinin **kimliğine** bağlıysa (marka adı, program adı, spesifik ürün SKU'ları, hesap manager ilişkisi), o skill **workspace'e** aittir — kit'e değil.
3. **Sınav testi (yazarken kendine sor):** "Bu skill Gibibyte olmayan bir MSP repo'ya install edilse işe yarar mı?"
   - Evet → kit
   - Hayır → workspace
4. **Acil müşteri ihtiyacı** kit-workspace ayrımını atlamak için gerekçe değildir. Workspace'e ekle, gerçekten kit-genel olabilecek soyutlamayı ADR-0007 tarzı standart şema olarak kite ayrı çıkar.
5. **install.sh üzerinden gelecek kaymalar** için: mevcut `skills/ragip-*/` glob pattern korunur ama yeni skill eklenirken PR'da "Domain-genel mi?" sorusu commit-checklist'e eklenmelidir (bkz. `.claude/rules/commit-checklist.md`).

## Sonuçlar

**Olumlu:**
- Kit yalın kalır, ADR-0004 fiilen uygulanır
- Başka MSP hedef repo'ya install kit'e Gibibyte kirlenmesi bulaştırmaz
- Workspace'in single source of truth durumu geri gelir — 4 skill'in tek gerçek konumu workspace
- Governance eksikleri kapatılır (bu ADR + CHANGELOG entry + test güncellemeleri)

**Olumsuz:**
- Kit'te 19 skill → 15 skill (README + install.sh tabloları güncel)
- Gelecek fikirlerdeki bağlı skill referansları (FEATURE_IDEAS.md) "workspace-side" notu ile işaretlendi
- Kit-side 3 test güncellemesi (`test_ragip_subagents.py`) — skill dağılım set'leri
- Kit-side 2 sub-agent frontmatter güncellemesi (`ragip-hesap`, `ragip-veri`) — `skills:` listelerinden kaldırıldı

## Alternatifler değerlendirildi

**Alternatif A: Kit'te bırak, "opsiyonel skill" işaretle.** Reddedildi — install.sh glob'u zorunlu kılıyor, "opsiyonel" ayrımı için mekanizma yok, karmaşıklık.

**Alternatif B: Skill'leri jenerikleştir.** Reddedildi — "Ingram" terminolojisi 38 kez geçtiği bir skill'i "distributor-genel" yapmak effektif olarak yeniden yazmak; workspace'te zaten var.

**Alternatif C: Kit ve workspace'te iki farklı sürüm tut.** Reddedildi — divergence problemi, install.sh her seferinde workspace'i ezerdi.

## Etki alanı

- `agents/ragip-hesap.md` — `skills:` listesinden 3 satır çıkarıldı
- `agents/ragip-veri.md` — `skills:` listesinden 1 satır çıkarıldı
- `skills/ragip-teklif/`, `skills/ragip-maliyet/`, `skills/ragip-yenileme/`, `skills/ragip-esles/` — silindi
- `README.md` — skill listesi ve mimari tablo güncel
- `install.sh` — hardcoded skill sayısı 19 → 15
- `docs/FEATURE_IDEAS.md` — `ragip-teklif` referansına "workspace-side" notu
- `tests/test_ragip_subagents.py` — 3 set güncellemesi
