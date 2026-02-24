# Mimari

Orchestrator + sub-agent pattern:
- ragip-aga (sonnet): Orchestrator, skill yok, dispatch only
- ragip-hesap (haiku): ragip-vade-farki, ragip-arbitraj
- ragip-arastirma (sonnet): ragip-analiz, ragip-dis-veri, ragip-strateji, ragip-ihtar
- ragip-veri (haiku): ragip-firma, ragip-gorev, ragip-import, ragip-ozet, ragip-profil

Kurallar:
- 11 skill 3 sub-agent'a dagitilir, cakisma yok (test: TestSkillDagilimi)
- CRUD skill'leri disable-model-invocation: true
- LLM skill'leri (analiz, dis-veri, strateji, vade-farki, arbitraj) model cagirir
- Sub-agent'lar ciktilari data/RAGIP_AGA/ciktilar/ altina yazar
- Format: YYYYMMDD_HHMMSS-{agent}-{skill}-{konu}.md
