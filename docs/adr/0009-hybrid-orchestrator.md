# ADR-0009: Hybrid Orchestrator Mimarisi
Tarih: 2026-03-19
Durum: Kabul edildi

## Bagiam

ragip-aga.md, orchestrator + 4 sub-agent dispatch pattern'i ile tasarlandi (ADR-0001).
Ilk gercek dunya testinde dispatch akisi basarisiz oldu. Kok neden analizi yapildi.

## Bulgular

### Nested Agent Spawn Sorunu

Test sonuclari:

| Senaryo | Nesting | Sonuc |
|---------|---------|-------|
| Ben → ragip-aga → ragip-arastirma | 2 seviye | Basarisiz |
| Ben → ragip-arastirma | 1 seviye | Basarili |

Claude Code'da sub-agent (Level 1), Agent tool ile baska sub-agent (Level 2) spawn etmeyi guvenilir sekilde yapamiyor. Framework-level sinir, prompt ile asilmiyor.

### "Task tool" Adi Hatasi

ragip-aga.md, sub-agent spawn icin "Task tool" olarak referans veriyordu.
Claude Code'daki dogru arac adi: **"Agent tool"**.
Araç adi ilk committe yanlis yazildi, hic test edilmeden production'a alindi.
`ciktilar/` dizininin bos olmasi dispatch'in hic calismadigini dogruluyor.

### subagent_type Parametresi

Agent tool'un `subagent_type` parametresi string tipinde, enum kisiti yok.
Custom agent adlari (ragip-hesap, ragip-arastirma, vb.) gecerli deger olmali.
Kesin dogrulama: Senaryo A ile ilk basarili dispatch'ten sonra.

## Karar: Hybrid Mimari

### Senaryo A — Dedicated Session (Cok Adimli Is)

```
claude --agent ragip-aga
```

ragip-aga **Level 0** olarak calisir. Agent tool ile 4 sub-agent'i spawn eder (Level 1).
1-seviye nesting: destekleniyor.

Kullanim: Tam firma degerlendirmesi, paralel sub-agent dispatch, cok adimli analiz.

### Senaryo B — Ana Session Dispatch (Hizli / Gelistirme)

```
[Normal Claude Code session]
```

Ana session dogrudan sub-agent spawn eder (Level 0 → Level 1).
ragip-aga devreye girmez, dispatch kurallari `.claude/rules/ragip_dispatch.md`'den okunur.

Kullanim: Tek skill gerektiren isler, hizli sorgular, gelistirme + analiz karisik session'lar.

### Cakisma yok

Iki senaryo birbirini dislamaz. Sub-agent'lar (ragip-hesap, ragip-arastirma, ragip-veri, ragip-hukuk) her iki senaryoda da degismez calisir.

## Uygulanan Degisiklikler

- `agents/ragip-aga.md`: "Task tool" → "Agent tool" (8 occurrence)
- `agents/ragip-aga.md`: subagent_type invocation formati duzeltildi
- `.claude/rules/architecture.md`: Dispatch Kurallari bolumu eklendi
- `config/ragip_dispatch.md`: Hedef repo'ya kurulan routing dosyasi (YENi)
- `install.sh`: `.claude/rules/ragip_dispatch.md` kurulumu eklendi

## Sonuc

ragip-aga Level 0'da calistiginda dispatch guvenilir olmali (subagent_type fix + dogru arac adi).
Senaryo B her zaman calisir (zaten dogrulanmis).
Hybrid yaklasim her iki kullanim senaryosunu karsilar.
