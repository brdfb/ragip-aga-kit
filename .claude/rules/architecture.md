# Mimari

Orchestrator + sub-agent pattern:
- ragip-aga (sonnet): Orchestrator, skill yok, dispatch only
- ragip-hesap (haiku): ragip-vade-farki, ragip-arbitraj
- ragip-arastirma (sonnet): ragip-analiz, ragip-dis-veri, ragip-strateji
- ragip-veri (haiku): ragip-firma, ragip-gorev, ragip-import, ragip-ozet, ragip-profil
- ragip-hukuk (sonnet): ragip-degerlendirme, ragip-zamanasimi, ragip-delil, ragip-ihtar

Kurallar:
- Skill'ler sub-agent'lara dagitilir, cakisma yok (test: TestSkillDagilimi)
- CRUD/prosedurel skill'ler disable-model-invocation: true
- LLM skill'leri (analiz, dis-veri, strateji, vade-farki, arbitraj, degerlendirme, delil) model cagirir
- Sub-agent'lar ciktilari data/RAGIP_AGA/ciktilar/ altina yazar
- Format: YYYYMMDD_HHMMSS-{agent}-{skill}-{konu}.md
