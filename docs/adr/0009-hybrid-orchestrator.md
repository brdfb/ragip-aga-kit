# ADR-0009: Hybrid Orchestrator Mimarisi
Tarih: 2026-03-19
Durum: Guncellendi — 2026-03-19 (framework kısıtları netleşti)

## Bagiam

ragip-aga.md, orchestrator + 4 sub-agent dispatch pattern'i ile tasarlandi (ADR-0001).
Ilk gercek dunya testinde dispatch akisi basarisiz oldu. Kok neden analizi yapildi.

## Bulgular

### 1. Nested Agent Spawn — Mimari Olarak Desteklenmiyor

Test sonuclari:

| Senaryo | Nesting | Sonuc |
|---------|---------|-------|
| Ben → ragip-aga → ragip-arastirma | 2 seviye | Basarisiz |
| Ben → ragip-arastirma | 1 seviye | Basarili |

Claude Code resmi dokumantasyonu:
> "Subagents cannot spawn other subagents. If your workflow requires nested
> delegation, use Skills or chain subagents from the main conversation."

Bu bir "guvenilmez" davranis degil, **mimari kısıt**. Prompt ile asilmasi mumkun degil.

### 2. Auto-Delegation Guvenilmez — Bilinen Framework Siniri

Model sub-agent dispatch etmek yerine gorevi kendisi yapmayı tercih ediyor.
Claude Code dokumantasyonu:
> "Claude uses each subagent's description to decide when to delegate tasks."

Bu karari model veriyor; prompt talimatlari override edemiyor. Tasarim siniri.

GitHub Issue #18352 (kapali, "Not Planned"):
- Kullanicılar forced delegation mekanizmasi istedi
- Anthropic planlamada degil olarak kapattı
- Ayni sorunun duplicate'leri: #7475, #16373, #5915

### 3. "Task tool" Adi Hatasi (Duzeltildi)

ragip-aga.md sub-agent spawn icin "Task tool" yaziyordu.
Dogru ad: Agent tool. v2.8.8'de duzeltildi.

### 4. @mention Sadece Interaktif UI'da Calisir

@mention (ornegin `@ragip-hesap gorevi yap`) yalnizca interaktif terminal UI'da
gecerli — CLI `-p` flag'inde veya programatik kullanimi calismiyor.

### 5. subagent_type Parametresi

Agent tool'un `subagent_type` parametresi string tipinde, enum kisiti yok.
Custom agent adlari (ragip-hesap, ragip-arastirma, vb.) gecerli deger olmali.
Kesin dogrulama: Senaryo A ile ilk basarili dispatch'ten sonra yapilacak.

---

## Karar: Senaryo B Birincil Yol

### Senaryo B — Ana Session Dispatch (ONAYLANMIS, GUVENILIR)

```
[Normal Claude Code session — Opus veya Sonnet]
```

Ana session dogrudan sub-agent spawn eder (Level 0 → Level 1).
ragip-aga devreye girmez, dispatch kurallari `.claude/rules/ragip_dispatch.md`'den okunur.

Test edildi, calistiği dogrulandi. Auto-delegation sorunu yok — kullanici
hangi sub-agent'ı istedigini belirtir, ana session direkt spawn eder.

**Tum aktif kullanim senaryolari icin Senaryo B onerilir.**

### Senaryo A — Dedicated Session (SINIRLI, DENEYSEL)

```
claude --agent ragip-aga
```

ragip-aga Level 0 olarak calisir, Agent tool ile sub-agent spawn eder (Level 1).
Nested spawn sorunu ortadan kalkar ama auto-delegation guvenilirlik sorunu devam eder:
Sonnet gorevi kendisi yapabiliyorsa dispatch etmeyebilir.

**Senaryo A yalnizca explicit dispatch gerektiren oturumlarda denenebilir;
uretim icin Senaryo B kullanilmali.**

### Cakisma yok

Iki senaryo birbirini dislamaz. Sub-agent'lar degismez calisir.

---

## Uygulanan Degisiklikler (v2.8.8)

- `agents/ragip-aga.md`: "Task tool" → "Agent tool" (8 occurrence)
- `agents/ragip-aga.md`: subagent_type invocation formati duzeltildi
- `.claude/rules/architecture.md`: Dispatch Kurallari bolumu eklendi
- `config/ragip_dispatch.md`: Hedef repo'ya kurulan routing dosyasi (YENi)
- `install.sh`: `.claude/rules/ragip_dispatch.md` kurulumu eklendi

---

## Sonuc

Senaryo B tek guvenilir yol olarak onaylandı.
Senaryo A deneysel kalir — auto-delegation framework siniri nedeniyle.
Nested spawn Claude Code'da mimari olarak desteklenmiyor; Skills veya
ana session zinciri alternatiftir.

**UYARI:** ragip-aga.md'deki dispatch talimatlari (subagent_type: "ragip-X")
Senaryo A icin yazilmistir. Senaryo B'de bu talimatlar kullanilmaz —
ana session dispatch kurallari ragip_dispatch.md'den okur.
