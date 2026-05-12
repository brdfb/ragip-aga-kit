# ADR-0013: Chain-of-Verification (CoVe) ve Citation Validation

**Tarih:** 2026-05-12
**Durum:** Kabul edildi
**Karar vericiler:** Kit gelistirici

## Baglam

ragip-degerlendirme, ragip-analiz ve ragip-strateji skill ciktilarinda iki halusinasyon riski vardir:

1. **Generic bulgu (Barnum etkisi):** "vade farkini takip edin", "sozlesmeyi dikkatli okuyun" gibi firma adi degistirilse hala gecerli ifadeler. Kullanici icin bilgi degeri sifir.
2. **Hallucinated citation:** LLM'in yasal madde numarasi uydurmasi. Adversarial testing'de citation fabrication orani %94'e cikabilir (arXiv 2510.24476, 2025). Sahte "TBK m.999" referansi hem kullaniciyi yaniltir hem hukuki risk yaratir.

v2.11.0'da **Tier 1 savunma** olarak prompt-tabanli **Barnum filtresi** eklendi: "Firma adini degistirsem cumle hala gecerli mi?" testi. Bu production'da "specificity rubric in-prompt" pattern'i.

**Tier 1 sinirlamasi:** Prompt-based self-check **sycophantic reflection** tuzagina dusebilir — model kendi ciktisini kendi onaylar. "Do LLMs Know What They Don't Know" (arXiv 2512.16030, 2025) calismasi TUM frontier modellerde sistematik overconfidence tespit etti. Yani prompt'a "emin misin?" yazmak yetmez.

Iki tamamlayici Tier 2 savunma gerekli:
- **Deterministik** citation dogrulama (LLM dahil edilmez)
- **Fresh-context** verification (sub-agent draft'i gormeden cevaplar)

## Karar

Iki katmanli Tier 2 savunma:

### Katman A: `ragip_madde_dogrula` deterministik kontrol

Yeni bilesenler:
- `config/kanun_maddeleri.json` — bilinen Turk mevzuat maddelerinin manuel curated listesi (TBK, TTK, IIK, KVKK, HMK; ~25 madde baslangic).
- `scripts/ragip_madde_dogrula.py` — regex ile metin icindeki madde referanslarini cikar, JSON'a karsi dogrula.
- `scripts/ragip_madde_dogrula.sh` — skill'lerden cagrilan bash wrapper.

Davranis:
- Cikti dosyasi yazildiktan SONRA cagrilir.
- Exit 0 = referanslar dogrulandi.
- Exit 2 = uydurma sanigi var → skill raporu duzeltmeli.
- LLM dahil DEGIL — ragip_get_rates.sh tarzi deterministik yardimci.

Integrasyon:
- `ragip-degerlendirme/SKILL.md` Adim 7: zorunlu dogrulama.
- `ragip-analiz/SKILL.md` Adim 8: madde referansi varsa zorunlu.
- `ragip-strateji/SKILL.md` Adim 3: yasal yola atif varsa zorunlu.

### Katman B: Chain-of-Verification (CoVe) pattern

Yuksek-stake ciktilarda (ragip-degerlendirme) 4-adim akis:
1. **Draft** — LLM ilk degerlendirmeyi yazar.
2. **Verification sorulari uret** — Draft uzerinde "zamanasimi suresi dogru mu?", "TBK m.117 gercekten temerrutu duzenliyor mu?" gibi sorulari LLM uretir.
3. **Fresh-context cevap** — Bu sorular orchestrator'dan **YENI** sub-agent context'inde cevaplanir. Sub-agent draft'i GORMEZ. Bu adim self-sycophancy'yi azaltir.
4. **Sentez** — Soru cevaplari + draft'tan final cikti.

CoVe katmani SADECE ragip-degerlendirme'ye zorunlu (hukuki tavsiye = yuksek risk). ragip-analiz ve ragip-strateji icin opsiyonel (Barnum + madde_dogrula yeterli kabul edilir).

## Gerekce

| Alternatif | Red nedeni |
|---|---|
| Sadece prompt-based self-check | Sycophantic reflection — model kendi ciktisini onaylar (kanitlanmis bias) |
| UQLM Python paketi (production confidence scorer) | Domain kucuk, compute maliyeti deger yok, dependency artar |
| Multi-Agent Reflexion (MAR, arXiv 2512.20845) | Persona debate cok karmasik, kit'in sade yapisina uymaz |
| Process Reward Models | Akademik, training-time, runtime cozum degil |
| LATS (yuksek-stakes tree search) | Bizim domain icin overkill, latency artar |
| Online madde API (mevzuat.gov.tr scraping) | Kirilgan, offline calismaz, kit'in standalone ilkesini bozar |

**Secilen yaklasimin avantajlari:**

- **Defense-in-depth:** Tier 1 (Barnum) + Tier 2A (madde_dogrula) + Tier 2B (CoVe) — birbirini destekleyen katmanlar.
- **Deterministik temel:** madde_dogrula LLM-bagimsiz, ragip_get_rates.sh tarzi.
- **Genisletilebilir:** Kullanici `kanun_maddeleri.json`'a ekleyebilir.
- **Konservatif:** Bilinmeyen madde "uydurma sanigi" olarak isaretlenir (kullanici uyarilir), bilinmeyen kanun ayri kategori ("scope disi" — TCK, vb.).
- **Test edilebilir:** 34 test (CLI, regex, range, fikra/bent, Turkce karakter, edge cases).

## Tasarim

### Regex pattern

```
([A-ZİĞÜŞÖÇ]{2,6})\s*m(?:adde)?\.?\s*(\d+)(?:/(\d+))?(?:[-]([a-zA-ZçğıöşüİĞÜŞÖÇ]))?
```

Yakaladiklari:
- `TBK m.117` (basit)
- `TBK madde 117` ("madde" kelimesi)
- `TTK m.21/2` (fikra)
- `TTK m.23/1-c` (fikra + bent)
- `İİK m.58` (Turkce karakter — normalize edilir)
- `TBK m.117-120` (range — 4 ayri referansa genisletilir)
- `TCK m.207` (bilinmeyen kanun — flagged)

### Konservatif eslesme

Base madde numarasi JSON'da varsa → dogrulandi (fikra/bent detayi gerekli degil). Bu false-positive riskini dusuk tutar (fikra-level data toplama maliyeti yuksek).

### CoVe akisi (skill icinde implementasyon notu)

```
ragip-degerlendirme:
  1. Draft uret (LLM, mevcut akis)
  2. Verification soru listesi uret:
     - "Hangi yasal sureyi belirttin?"
     - "Bu sure hangi kanun maddesine dayaniyor?"
     - "Madde gercek mi? (madde_dogrula ile dogrulanacak)"
     - "Hesap kabul edilen formule uyuyor mu?"
  3. Orchestrator: Sub-agent spawn et (fresh context).
     Sub-agent SADECE sorulari ve gerekli verileri alir.
  4. Cevaplari + draft'i birlestir → final cikti
  5. madde_dogrula calistir
```

Bu adim Anthropic'in "writer/reviewer" pattern'inin daha yapisal versiyonu.

## Konsekvanslar

### Pozitif

- Sahte madde citation riski deterministik olarak engellenir.
- Tier 1 + Tier 2A immediate value (Tier 2B opsiyonel, sonra implemente edilir).
- Kullanici JSON'i editleyerek kapsami genisletebilir.
- Test guvencesi (34 test) — regresyon koruma.

### Negatif

- `kanun_maddeleri.json` manuel bakim gerekir — yeni madde eklendiginde guncellenmeli.
- False positive olabilir: kullanicinin bilincli olarak scope disi madde refernsi kullanmak istemesi durumunda (nadir).
- CoVe akisi 2x token maliyeti (sadece ragip-degerlendirme'de).

### Gelecek calisma

- Periyodik kanun_maddeleri.json zenginlestirme (kullanici talebine gore yeni madde ekle).
- Mevzuat.gov.tr scraper (opsiyonel, online madde dogrulama icin — ama standalone ilkesini bozar).
- CoVe verification soru template'lerini ayri skill icinde sabitle.

## Kaynaklar

- "Citation Fabrication in Modern LLMs" — arXiv 2510.24476, 2025
- "Do LLMs Know What They Don't Know" — arXiv 2512.16030, 2025
- "Chain-of-Verification Reduces Hallucination in Large Language Models" — Meta, ACL 2024
- Anthropic "Building Effective Agents" — writer/reviewer pattern
- HaluGate (vLLM blog, Dec 2025) — NLI-based grounding
- UQLM (cvs-health/uqlm, JMLR 2025) — production confidence scorer (referans, kullanilmadi)

## Iliski

- **Onceki:** ADR-0010 Savunma Katmanlari (Tier 1 Barnum filtresinin altyapi karari)
- **Tamamlayici:** ragip-zamanasimi (zamanasimi hesabi icin ayri deterministik tool)
