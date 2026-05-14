# ADR-0015: Citation Source Whitelist (Tier 2C)

**Tarih:** 2026-05-13
**Durum:** Kabul edildi
**Karar vericiler:** Kit gelistirici
**Iliski:** ADR-0010 (Savunma Katmanlari), ADR-0013 (CoVe + madde_dogrula)

## Baglam

ADR-0013 ile uc katmanli hallucination defense kuruldu:

- **Tier 1 (Barnum filtresi)** — prompt-tabanli generic-bulgu eliminasyonu
- **Tier 2A (`ragip_madde_dogrula`)** — deterministik kanun maddesi dogrulamasi
- **Tier 2B (CoVe)** — yapisal verification akisi

Ama bir bosluk kaldi: **citation source authority**. Kanun maddesi numarasi `kanun_maddeleri.json`'da olsa bile, model "Yargıtay 11. HD 2024/X karar" gibi mahkeme karari, doktrin alintilari veya hukukforum.com bloglarindan turetilmis "guncel ictihat" cumlelerini uydurabilir. madde_dogrula bu turleri tanimiyor (sadece kanun maddesi pattern'i).

Citation hallucination'in arastirma sonuclari:
- arXiv 2510.24476 (2025): adversarial setting'de citation fabrication %94'e cikabilir
- Hukuki domain'de "uydurma karar" gercek karara gore daha tehlikeli — kullanici dogrulayamadan yasal pozisyon kurgular
- Tier 2A yetersiz: kanun maddesinin gercek oldugu dogrulansa bile alintilanan karar/yorum uydurma olabilir

gibibyte-cfo-agent v0.2 (Nisan 2026) settings.json'da bu pattern'i uygulamis: vergi mevzuati sorgularinda WebFetch SADECE gib.gov.tr, mevzuat.gov.tr, resmigazete.gov.tr, turmob.org.tr domainlerine yonelik. Kit icin ayni mantik hukuki citation'a uygulanmali.

## Karar

**Tier 2C — Resmi kaynak domain whitelist**, ragip-hukuk altinda WebSearch/WebFetch kullanan skill'lerde prompt-level zorunluluk.

### Whitelist (hukuki kaynak otoritesi)

| Domain | Ne icin |
|--------|---------|
| `mevzuat.gov.tr` | Kanun/yonetmelik resmi metni |
| `resmigazete.gov.tr` | Yayin asli, tarih ve sayi |
| `yargitay.gov.tr` | Yargitay karar bilgi sistemi |
| `karararama.yargitay.gov.tr` | Yargitay karar arama (alternatif) |
| `danistay.gov.tr` | Danistay |
| `anayasa.gov.tr` | Anayasa Mahkemesi |
| `adalet.gov.tr` | Adalet Bakanligi resmi |
| `hsk.gov.tr` | Hakimler ve Savcilar Kurulu |

### Davranis kurali

WebSearch sonucu:
- **Whitelist domaininden** → WebFetch ile teyit zorunlu, citation kabul.
- **Whitelist disindan** → citation reddet, "Resmi kaynaktan teyit edilemedi — alintilanmadi" notu dus.
- **Hicbir whitelist sonucu yoksa** → "Guncel resmi mevzuat degisikligi tespit edilemedi" yaz, varsayilan TBK/TTK degerlerini kullan.

WebSearch sorgusu `site:mevzuat.gov.tr` veya `site:resmigazete.gov.tr` filtresiyle baslamali — gurultuyu kaynaginda kes.

### Tetik kosulu (reactive, v2.17.0 netlestirmesi)

Tier 2C **reaktiftir**: WebSearch cagrildiginda whitelist devreye girer. Skill kendiliginden mevzuat sorgusu acmaz — tetik kullanicidan veya skill prosedurunden gelir:

- **Kullanici tetigi:** "guncel mevzuat sorgula", "son ictihat var mi", "TTK m.X degisti mi" tipi acik istek.
- **Skill prosedur tetigi:** ragip-degerlendirme adim listesinde "guncel mevzuat degisikligi kontrol et" varsa (skill prompt'una bagli).

Bu yuzden gercek senaryo testinde Tier 2C ancak yukaridakilerden biri tetiklendiginde **gozlemlenir**. Tetik yoksa whitelist davranisi inactive — "bos koruma" izlenimi verir ama tasarim boyle. ragip-degerlendirme skill'inin her cagrida WebSearch yapmasi default davranis DEGIL (overhead + LLM cagri maliyeti).

Tetik tasarim sorusu: Skill her zaman "son 6 ayda mevzuat degisikligi var mi" kontrolu yapmali mi (proactive)? Karar **hayir** — KOBi hukuki danismanlik senaryolarinin cogunda yeterli (deterministik kanun maddesi referansi yeterli, guncel ictihat secimliklidir). Proactive tetik gerekirse skill prompt'unda explicit eklenmeli.

### Kapsam

| Skill | WebSearch kullanir mi | Tier 2C uygulanir mi |
|-------|-----------------------|----------------------|
| ragip-degerlendirme | Evet (mevzuat degisikligi) | **Evet** |
| ragip-zamanasimi | Hayir (deterministik) | Gerekmiyor |
| ragip-delil | Hayir | Gerekmiyor |
| ragip-ihtar | Hayir | Gerekmiyor |
| ragip-dis-veri | Evet (sirket arastirmasi) | **Hayir** — kapsam disi |
| ragip-analiz, ragip-strateji | Hayir (sadece dosya + hesaplama) | Gerekmiyor |

ragip-dis-veri serbest WebSearch (rakip arastirmasi, sektor verisi) yapar — hukuki citation degil, ticari intel. Whitelist bagimliligi gereksiz.

## Gerekce

| Alternatif | Red nedeni |
|---|---|
| `.claude/settings.json` permissions whitelist (kit-level) | ragip-dis-veri'yi de etkiler, ticari intel kapsamini bozar |
| Agent frontmatter `allowedTools: WebFetch(domain:...)` | Per-skill kontrol gerekiyor (sadece degerlendirme), agent-level cok kalin |
| Hooks (PreToolUse URL filtresi) | Mevcut hook altyapisi yok — buyuk yatirim, prompt-level baslamak yeterli |
| Manuel madde-by-madde URL listesi | Olceklenemez, surekli bakim |
| Sadece WebSearch query'sine site: ekle | Sufficient ama enforcement zayif — model query'yi degistirip aramaya devam edebilir |

**Secilen yaklasimin avantajlari:**

- **Defense-in-depth tamamlama**: Tier 1 (Barnum) + Tier 2A (madde_dogrula) + Tier 2B (CoVe) + **Tier 2C (whitelist)** = full citation defense
- **Prompt-level**: Geri alinabilir, dependency yok, infrastructure degisikligi yok
- **Test edilebilir**: Whitelist string'leri agent ve skill metninde regex/grep ile dogrulanir (regression)
- **Belge-bagimli**: Surekli bakim gereksinmiyor (resmi domain listesi nadir degisir)
- **Konservatif**: Whitelist disi → reddet (false negative > false positive — uydurma karari kabul etmektense gecmek daha gvuvenli)

**Sinirlamalari:**

- Prompt-level enforcement → model atlayabilir. Sub-agent yeniden spawn olsa bile whitelist talimati prompt'ta kalir.
- Whitelist eksik olabilir — diger resmi mahkeme/kurum domainleri (orn: il barosu, KGM) bilincli olarak disarida birakildi.
- WebFetch domain restrictions agent frontmatter'da tool-level olarak ENFORCE edilebilir ama kit'in skill-level allowed-tools pattern'iyle catismaktadir. Sonraki iterasyonda degerlendirilebilir.

## Konsekvanslar

### Pozitif

- ragip-degerlendirme citation otoritesi yapisal olarak isaretli.
- Tier 2A (kanun maddesi) + Tier 2C (kaynak otoritesi) birlikte mahkeme karari + doktrin halusinasyonunu kapsar.
- ADR-0013 mimari acigi kapanir.

### Negatif

- Prompt-level enforcement, model kurali atlamadan onceki bir guarantee saglamaz.
- Yeni resmi domain (orn: mevzuat-yeni.gov.tr) cikarsa whitelist guncellenmesi gerekir.
- `site:` operator search engine'e bagli (Google honors, bazi engine'ler yok sayar).

### Gelecek calisma

- Tool-level enforcement: ragip-hukuk agent frontmatter'a `WebFetch(domain:...)` whitelist (Claude Code permissions syntax destek dogrulanirsa).
- Hooks-based PreToolUse URL filtresi: WebFetch URL'i whitelist disindaysa hard block. Buyuk yatirim, sonraki faz.
- Negative whitelist gelisimi: `hukukforum.com`, `*.blogspot.com` gibi sik gorulen citation magnet'leri "kara liste" olarak ek.
- ragip-zamanasimi'na WebSearch eklenirse (mevzuat degisikligi takip), whitelist genisletme.

## Kaynaklar

- gibibyte-cfo-agent v0.2 settings.json (Nisan 2026) — WebFetch whitelist pattern'inin oncusu
- arXiv 2510.24476 (2025) — Citation fabrication in modern LLMs
- ADR-0013 — CoVe + madde_dogrula (Tier 1, 2A, 2B kararlari)
- ADR-0010 — Savunma katmanlari mimari

## Iliski

- **Onceki:** ADR-0013 (Tier 1 + 2A + 2B); bu ADR Tier 2C ekler.
- **Tamamlayici:** ragip-degerlendirme/SKILL.md Adim 3 (WebSearch + Tier 2C whitelist), ragip-hukuk.md agent system prompt.
- **Sonraki:** Tool-level enforcement (potansiyel ADR-XXXX), hooks-based URL filtering.
