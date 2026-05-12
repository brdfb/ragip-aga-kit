# ADR-0017: Orchestrator PRD Disiplini

**Tarih:** 2026-05-13
**Durum:** Kabul edildi
**Karar vericiler:** Kit gelistirici
**Iliski:** ADR-0001 (Sub-agent mimarisi), ADR-0009 (Hybrid orchestrator), I8 (Senaryo A guvenilirligi)

## Baglam

ragip-aga orchestrator karmasik isler icin (sozlesme analizi + strateji + ihtar dosyasi) Agent tool ile dogrudan dispatch yapiyor. Kullanici plan goremiyor — sonucu gorunce yanlis yonlendirildigini anliyor. Geri donus pahali:

- Karmasik dispatch: 4-6 alt-ajan turn'u, ~3-5 dakika sure
- Yanlis dispatch → yeniden plan + yeniden dispatch → toplam ~8-10 dakika
- Kullanici frustrationu: "Ben bunu istemedim, neden direkt yaptin?"

Mevcut savunma katmanlari:
- ADR-0001: Sub-agent mimarisi (5 sub-agent, 19 skill dagilimi)
- ADR-0009: Hybrid orchestrator (Senaryo A vs B)
- I8: Senaryo A interaktif modda ragip-aga ilk mesajda dispatch yapmiyor — auto-delegation sinirli

Bu sinirlamalar **disiplin bosluk** birakti: ragip-aga'nin ne yapacagini onceden soylemesi yapisal degil, esnek (model tercihine bagli).

### Cherry-pick kaynagi

gibibyte-cfo-agent v0.2 (Nisan 2026) bu sorunu **K4: Her gorevde PRD onyemli** ilkesiyle cozdu:

> K4 — Her gorevde PRD onyemli. Ise baslamadan: gorev ozeti + yaklasim maddeleri + Bered onayi. PRD onaysiz ana is yok.

CFO konseptindeki bilgi:
- PRD = Plan / Recap / Direction (üç adım: ne, nasıl, onay)
- Trivial işler (basit liste, tek hesaplama) bypass
- Karmaşık işler için zorunlu

## Karar

**Karmasik isler icin PRD zorunlu, trivial isler icin bypass.**

### PRD formati

```
"Sunu yapacagim: <X gorevi> → ragip-Y sub-agent'i → <Z ciktisi uretecek>. Devam edeyim mi?"
```

1-2 satir. Detayli plan degil, ne yapilacagin ozeti + onay sorusu.

### Tetikleyici anahtar kelimeler (PRD zorunlu)

| Kategori | Anahtar kelimeler |
|----------|-------------------|
| Analiz | "tam analiz", "stratejik degerlendirme", "firma degerlendirmesi" |
| Strateji | "strateji olustur", "3 senaryo", "muzakere plani" |
| Hukuki | "ihtar hazirla", "ihtar taslagi" |
| Rapor | "tum raporlar", "rapor + analiz", coklu rapor |
| Dosya | "dosya hazirla", "avukata dosya" |
| Mimari | Birden fazla alt-ajan gerektiren her is |

### Trivial bypass (PRD'siz dogrudan dispatch)

| Tipi | Ornek | Hedef |
|------|-------|-------|
| Hesaplama | "100K vade farki %3 45 gun" | ragip-hesap direkt |
| Listele | "tum firmalari listele", "gorevleri goster" | ragip-veri direkt |
| Ozet | "ABC Dagitim hakkinda" | ragip-veri direkt |
| Kavramsal | "vade farki nedir?" | Kendin cevapla |
| Tek skill | Tek aksiyon, tek cikti | Direkt dispatch |

### Onay akisi

```
PRD sun
  ↓
Kullanici tepkisi
  ├── "evet", "devam", "yap", "ok" → dispatch
  ├── "hayir", "dur", "duzelt" → plani revize, tekrar PRD
  └── Ek ayrinti istegi → planı detaylandir, tekrar PRD
```

## Gerekce

| Alternatif | Red nedeni |
|---|---|
| Her dispatch'te PRD (esneksiz) | Trivial isler icin overhead, kullaniciyi sinirlendirir |
| Hicbir zaman PRD (mevcut) | Yanlis dispatch maliyeti yuksek, geri donus pahali |
| Sub-agent icinde PRD | Sub-agent zaten kendi skill'ini calistiriyor — orchestrator seviyesinde anlamli |
| User-confirm config (settings.json) | Kullanici-tercih degil, sistem-disiplin gerekiyor |

**Secilen yaklasimin avantajlari:**

- **Esnek**: Trivial isler bypass, karmasik isler onay — kullanici frustrationsuz.
- **Yapisal**: Anahtar kelime listesi ile tetik ilkeselli, model tercihine bagli degil.
- **Geri alinabilir**: Prompt-level — istenmezse silinir.
- **gibibyte-cfo-agent uyumlu**: K4 disiplini paylasilir, cross-project tutarlilik.
- **I8 sinirlarini destekler**: Senaryo A interaktif modda ilk mesajda dispatch yapmama davranisini YAPISAL hale getirir — "dispatch yapma" yerine "PRD ver" yapisal alternatifi.

**Sinirlamalari:**

- Prompt-level enforcement — model atlayabilir.
- Anahtar kelime listesi statik — yeni kalıp eklendiginde manuel guncelleme gerekir.
- "Karmasik" tanimi yumusak — model yargisina bagli. Tetik listesi kati referans yapar.
- Onay bekleme sub-agent dispatch latency'ye ekleme yapar (1-2 turn).

## Konsekvanslar

### Pozitif

- Yanlis dispatch oranı azalir, kullanici turn maliyeti dusurur.
- Karmasik isler kullaniciyla onceden hizalanir — frustration azalir.
- I8 Senaryo A "ilk mesajda dispatch yapma" davranisi YAPISAL — model neden yapmadigi kullaniciya görünür.
- gibibyte-cfo-agent ile cross-project PRD disiplin tutarliligi.

### Negatif

- Bazi kullanicilar "her seferinde onay sorma" diye sikayet edebilir — trivial bypass bunu azaltir.
- Anahtar kelime listesi bakim gerektirir (yeni intent patterni cikinca eklenir).
- PRD onayi 1 ek turn maliyetidir — karmasik isler icin 3-5dk dispatch zatensiz fark edilmez.

### Gelecek calisma

- Anahtar kelime listesi: gercek kullanim verisinden (interaktif log) sik gorulen patternleri ekle.
- Sessizlik (1 turn yanit yok) → otomatik onay sayma — UX denemesi.
- Custom PRD opsiyonu: kullanici "her zaman onaysiz" tercihi (CLAUDE.md veya settings.json).
- Senaryo A vs B PRD davranis ayrimi: dedicated session'da PRD daha sik, ana session'da daha az.

### Acik soru

- "Karmasik mi trivial mi" sinirini model dogru saptayabilir mi? Anahtar kelime tetigi yardimci, ama tamamlayici "alt-ajan sayisi" heuristic (>=2 → karmasik) eklenebilir.
- Sub-agent dispatch sonrasi yeni soru → her ardisik dispatch icin PRD? Karar: ana sentez tamamlanana kadar tek bir PRD yeterli, ek sorular icin gerek yok.

## Iliski

- **Onceki:** ADR-0001 (sub-agent mimarisi), ADR-0009 (hybrid orchestrator)
- **Iliskili:** I8 Senaryo A guvenilirligi — PRD disiplini bu sinirin yapisal sebebini disipline cevirir.
- **Cherry-pick:** gibibyte-cfo-agent v0.2 K4 (5 Operasyonel Kural pattern), FEATURE_IDEAS #22.

## Kaynaklar

- gibibyte-cfo-agent v0.2 (Nisan 2026) — K4: PRD onyemli disiplini
- FEATURE_IDEAS #22 — Orchestrator PRD disiplini onerisi (12 Mayis 2026)
- I8 Senaryo A guvenilirligi (FEATURE_IDEAS) — auto-delegation sinirlarini destekleyen yapisal disiplin
