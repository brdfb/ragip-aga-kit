# ADR-0019: Skill ↔ Agent Koordinasyon Disiplini

**Tarih:** 2026-05-14
**Durum:** Kabul edildi
**Karar vericiler:** Kit gelistirici (audit-driven)
**Iliski:** ADR-0016 (Tier 3 cikti disiplini), ADR-0017 (Orchestrator PRD), ADR-0018 (Tier 4 tutarlilik)

## Baglam

### Gozlemlenmis sorun (14 Mayis 2026 Yontem 2B regresyon)

Uc ardisik kit versiyonu (v2.16.0 / v2.17.0 / v2.18.0) Tier 3 ve Tier 4 cikti disiplinlerini skill'lere ekledi:

- v2.16.0: Tier 3 — `TESPIT/POZISYON/GEREKCE` 3-satir blok (ADR-0016)
- v2.17.0: Tier 4 — `Tutarlilik denetimi` notu zorunlu (ADR-0018) + Kesinlik kalibi
- v2.18.0: Tier 3 zenginlestirme — Lead With Insight + Quantify Impact 4-bilesen + Action 5-bilesen + Etiket netligi

Her versiyonda 3 LLM skill (`ragip-degerlendirme`, `ragip-analiz`, `ragip-strateji`) SKILL.md dosyalari guncellendi. Davranissal test (Yontem 2B — `claude --agent ragip-hukuk` ile gercek senaryo):

| Versiyon | Yapisal eslesme (13 isaret) | Niyet eslesmesi (9 isaret) |
|---|---:|---:|
| v2.16.0 (14 May 09:18) | **0/13** | 3/9 |
| v2.17.0 (14 May 20:08) | **0/13** | 4/9 |
| v2.18.0 (14 May 22:23, kullanici 22:35, ext 22:42) | **0/13** | 6/9 |

3 versiyon, 5 ayri kosum (iki user + iki kit), hicbirinde Tier 3/4 yapisal blok formati cikti dosyasinda gozlemlenmedi. Niyet eslesmesi artiyor (disiplinin RUHU model'e gecmis), yapisal eslesme sabit sifir (HARFI gecmemis).

### Yapisal kok sebep (audit, /tmp/ragip_audit_v218_structural.md)

QA musaviri structural audit (neutral observer, `claude -p`, agent'siz, self-introspection yasak):

1. **Agent system prompt'larinda Tier 3/4 referansi: 0 esleme** (grep ile teyit).
2. **Agent prompt'larinin `## YANIT FORMATIN` bolumleri Tier 3/4 ile celisen narrative format dayatiyor:**
   - `agents/ragip-hukuk.md:182-192` — 6-bolum narrative (HUKUKI DEGERLENDIRME / MEVZUAT / USUL / DELIL / SONUC / RISK)
   - `agents/ragip-arastirma.md:168-178` — 6-bolum narrative (DURUM ANALIZI / HESAPLAMALAR / KOZLAR / STRATEJI / SOMUT ADIMLAR / RISK)
3. **Model agent system prompt'unu birincil otorite, skill SKILL.md'yi ikincil rehber olarak okuyor.** Skill'de "ZORUNLU" yazsa bile, agent format ile celisirse agent kazaniyor.
4. **Skill icinde Tier 3 spec'i %42-%68 araliginda — Liu et al. 2024 "Lost in the Middle" bolgesinde.**
5. **Tier 4 spec'i skill'in %65-82 arkasinda, cikti yazma adimindan sonra** — model "bitti" dedikten sonra Tier 4 atlatiliyor.
6. **Few-shot WRONG/CORRECT ornekleri spesifik gercek firma adlari iciyor** ("Guven Pres", "Zeren") — model "bu ornek bu firmaya ozgu" yorumlayip format kuralı olarak almiyor.

### Mekanizma propagation hesabi

Skill spec'i degisiyor (5 versiyon), agent prompt sabit. Asimetri **%0** propagation — agent spec'i skill spec'ini override ediyor.

## Karar

**Skill ↔ Agent Koordinasyon Disiplini:** Skill SKILL.md'ye yeni **cikti formati disiplini** eklendiginde, **ilgili agent dosyasinin `## YANIT FORMATIN` bolumu de paralel olarak guncellenmelidir.**

### Kural

| Skill degisikligi | Agent guncellemesi zorunlu mu | Kapsam |
|---|---|---|
| Cikti format spec'i (TESPIT blok, Tier 3 zenginlestirme) | **EVET** | Tum ilgili agent'lar |
| Cikti template ekleme (TUTARLILIK DENETIMI bolumu) | **EVET** | Tum ilgili agent'lar |
| Kontrol kategorileri ([SAYI]/[ETIKET]/...) | Hayir (skill icerigi) | - |
| Akis adimi (DRAFT/CoVe verification) | Hayir (skill icerigi) | - |
| Few-shot ornek ekleme/degistirme | Hayir | - |

**Skill → Agent eslemesi (mevcut):**

| Skill | Birincil Agent |
|---|---|
| ragip-degerlendirme | ragip-hukuk |
| ragip-analiz | ragip-arastirma |
| ragip-strateji | ragip-arastirma |
| ragip-delil | ragip-hukuk |
| ragip-ihtar | ragip-hukuk |
| ragip-zamanasimi | ragip-hukuk (deterministik) |
| ragip-dis-veri | ragip-arastirma |

### Yapisal kurallar

1. **Skill basinda Tier 3/4 ozeti zorunlu** — model'in ilk dikkat hattinda spec'in oldugundan emin ol. Skill'in line 8-30 araliginda `## CIKTI FORMATI (Tier 3/4 ZORUNLU — ILK OKU)` bolumu.
2. **Agent `YANIT FORMATIN` bolumu skill spec ozeti icermeli** — narrative bolumler + format zorunlu bolum (Tier 3 blok) + denetim zorunlu bolum (Tier 4).
3. **Persona vs format ayrimi acikca yazilmali** — "Evladim, duz konusursun" persona narrative bolumlerde, TESPIT: format zorunlu bolumlerde. Celismez.
4. **Few-shot ornek notr firma adi kullanilmali** — "Demo Sanayi A.S.", "Demo IT Hizmetleri" gibi. Gercek musteri adi few-shot'ta = model "bu firmaya ozgu" yorumlar.
5. **Tier 4 bolumu cikti template'inde sondan-once zorunlu kapanis olmali** — Akis adimi olarak skill'in arkasinda DEGIL. Template'e gomulu.

### Test edilebilirlik

Bu disiplin **yapisal testle dogrulanabilir** (pytest), davranissal dogrulama manuel:

- **Yapisal:** Agent dosyalarinda Tier 3 referansi (`TESPIT/POZISYON/GEREKCE`) ve Tier 4 referansi (`Tutarlilik denetimi`) grep ile dogrulanir. Test: `tests/test_ragip_skill_agent_koordinasyon.py` (gelecek).
- **Davranissal:** Yontem 2B regresyonu (manuel haftalik) — eslesme orani 8+/13 hedef. 0/13 hala duruyorsa v2.19.0'da B1 (c) structured output mekanizmasi.

## Gerekce

| Alternatif | Red nedeni |
|---|---|
| Skill spec'i tek otorite | Audit gosterdi: model agent prompt'unu birincil otorite olarak okuyor. Skill spec'i ikincil. |
| Agent prompt tek otorite | Skill modulerligi kaybolur. Her agent'in tum disiplinleri tasimasi kit-size'i sisirir. |
| Output schema (JSON-style) zorlama | (c) — B1 fallback, daha buyuk degisiklik. Once (a) skill-agent koordinasyon dene. |
| Post-process Python (blok insert) | (b) — brittle. Model "Evladim, dosyayi kaydettim" diyince blok'a cevirme anlamsal. |
| Regenerate cycle | (d) — 2x token, son care. (a)+(c) yetmezse. |
| Hicbir sey (mevcut) | %0 propagation 3 versiyon. Yeni disiplinin bilesim kayip. |

**Secilen yaklasim (a) skill-agent koordinasyon:**

- Minimum invasive — sadece YANIT FORMATIN bolumleri guncellenir
- Lost-in-the-middle fix — skill basina ozet eklenir
- Few-shot block confusion fix — notr firma adi
- Tier 4 atlatma fix — cikti template'e gomulu
- Test edilebilir — grep ile agent referansi dogrulanir

**(a) yeterli mi 8+/13 davranissal eslesme?** Manuel test gerekli (v2.18.1 release sonrasi 3 kosum). Yetmezse (c) structured output.

## Konsekvanslar

### Pozitif

- Mekanizma propagation = %0 sorunu yapisal cozulur
- Kit gelistirme disiplini netlesir — yeni Tier ekleme = skill + agent paralel guncelleme
- ADR-0016/0018 motivasyon dolar (yoksa "yazdim ama davranisa yansimadi" kayip)
- Persona ile format celisme acikca ele alindi
- Tier 4 cikti template'e gomulerek atlatma riski azalir

### Negatif

- Agent dosyalari sismeye baslar (her Tier yeni satirlar getirir). 5 agent x ortalama 20 satir = 100 satir ekstra.
- Skill ↔ agent koordinasyon karmasikligi gelistiriciye yuk olur (yeni disiplin ekleme = iki yer guncelleme).
- Audit yapilmadan disiplinin propagation'i otomatik garantilemez — manuel pytest test ile dogrulanir.

### Riskler

- Agent dosyalarinda spec ozeti **eskirse** (skill update edilince agent unutulursa) ayni sorun tekrarlanir. Mitigation: yapisal test ekle (`test_skill_agent_referans_eslesme`).
- Persona vs format ayrimi modeller arasi inconsistent yorumlanabilir (Haiku vs Sonnet). Mitigation: kit kullanim agent'lari Sonnet kapsaminda kalir (orchestrator agent'lari).

### Gelecek calisma

- **`tests/test_ragip_skill_agent_koordinasyon.py`** — yapisal test: skill'de Tier 3 referansi varsa, ilgili agent'ta da `TESPIT/POZISYON/GEREKCE` grep eslesmesi olmali.
- **v2.18.1 sonrasi 3 davranissal kosum** — yapisal eslesme oranini olc, %0 hala duruyorsa B1 (c) structured output.
- **LLM-judge altyapisi (B2)** — skill ↔ agent koordinasyon disiplinini meta-test eder. Sonnet judge, manuel haftalik.

## Iliski

- **Onceki:** ADR-0016 (Tier 3 cikti disiplini), ADR-0017 (PRD), ADR-0018 (Tier 4)
- **Tetikleyici:** 14 Mayis Yontem 2B regresyon (3 versiyon, 5 kosum, 0/13 eslesme) + structural audit raporu
- **Sonraki:** v2.18.1 fix release (bu ADR'in implementasyonu), B2 LLM-judge altyapisi (v2.19.0 candidate), B1 (c) structured output (fallback)

## Kaynaklar

- `/tmp/ragip_audit_v218_structural.md` — structural audit raporu (line-no kanitlari ile)
- `/tmp/ragip_v2.18.0_yontem2b_bulgu.md` — Yontem 2B regresyon FAIL raporu
- `/tmp/ragip_v2.17.0_patch_listesi.md` — onceki versiyon patch listesi
- `docs/FEATURE_IDEAS.md` #19 — Davranissal QA altyapisi (B1+B2+B3)
- Liu et al. 2024 — "Lost in the Middle" (uzun prompt'larda dikkat agirligi)
- Anthropic 2026 eval guidance — Skill design disiplinleri

---

*Bu ADR cherry-pick degil — kit-spesifik bir koordinasyon disiplini. Skill modulerligi kaybetmeden agent override sorununu cozer.*
