# Mimari

Orchestrator + sub-agent pattern:
- ragip-aga (sonnet): Orchestrator, skill yok, dispatch only
- ragip-hesap (haiku): ragip-vade-farki, ragip-arbitraj, ragip-rapor
- ragip-arastirma (sonnet): ragip-analiz, ragip-dis-veri, ragip-strateji
- ragip-veri (haiku): ragip-firma, ragip-gorev, ragip-import, ragip-ozet, ragip-profil
- ragip-hukuk (sonnet): ragip-degerlendirme, ragip-zamanasimi, ragip-delil, ragip-ihtar

Kurallar:
- Skill'ler sub-agent'lara dagitilir, cakisma yok (test: TestSkillDagilimi)
- CRUD/prosedurel skill'ler disable-model-invocation: true
- LLM skill'leri (analiz, dis-veri, strateji, vade-farki, arbitraj, degerlendirme, delil, ihtar) model cagirir
- Sub-agent'lar ciktilari data/RAGIP_AGA/ciktilar/ altina yazar
- Format: YYYYMMDD_HHMMSS-{agent}-{skill}-{konu}.md

Tool kisitlama (Principle of Least Privilege):
- ragip-aga, ragip-hesap, ragip-veri: disallowedTools frontmatter ile WebSearch+WebFetch engellendi (mimari seviye)
- ragip-arastirma, ragip-hukuk: WebSearch bazi skill'lerde gerekli (dis-veri, degerlendirme) — prompt kisitlamasi devam eder
- Test: TestOrchestrator.test_no_websearch, TestSubAgentHesap.test_no_websearch, TestSubAgentVeri.test_no_websearch

## Dispatch Kurallari

| Kullanici istegi | Sub-agent |
|-----------------|-----------|
| Hesaplama, vade farki, TVM, arbitraj, rapor | ragip-hesap |
| Sozlesme/fatura analizi, arastirma, strateji | ragip-arastirma |
| Hukuki degerlendirme, zamanasimi, delil, ihtar | ragip-hukuk |
| Firma CRUD, gorev, import, ozet, profil | ragip-veri |

Cagri formati (Agent tool):
  subagent_type: "ragip-X"
  prompt: [gorev aciklamasi + varsa firma profili]

Senaryo A (cok adimli is): `claude --agent ragip-aga` — ragip-aga Level 0 olarak 4 sub-agent'i dispatch eder.
Senaryo B (hizli/gelistirme): Ana session dogrudan sub-agent spawn eder — ayni routing tablosu gecerli.
Not: ragip-aga sub-agent olarak spawn edilirse (Level 1), Agent tool ile baska sub-agent spawn etmesi guvenilmez (ADR-0009).
