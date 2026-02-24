# ADR-0001: Sub-Agent Mimarisi
Tarih: 2025-01-15
Durum: Kabul edildi

## Baglam
v1.x'te tek bir ragip-aga agent'i tum skill'leri dogrudan calistiriyordu. Skill sayisi arttikca prompt uzunlugu ve model maliyeti sorun oldu. Farkli skill turleri farkli model kapasiteleri gerektiriyor: CRUD islemleri icin sonnet gereksiz, analiz icin haiku yetersiz.

## Karar
Orchestrator + 3 sub-agent mimarisine gecildi:
- **ragip-aga** (sonnet): Sadece dispatch, skill yok. Kullanici profilini okuyarak context-aware routing yapar.
- **ragip-hesap** (haiku): Deterministik finansal hesaplamalar. Model maliyeti dusuk.
- **ragip-arastirma** (sonnet): Derin analiz, strateji, hukuki taslak. Reasoning gerektirir.
- **ragip-veri** (haiku): CRUD islemleri. Cogu skill disable-model-invocation: true.

11 skill 3 sub-agent'a dagilir, cakisma yok. Yapisal testler (TestSkillDagilimi) bunu dogrular.

## Sonuc
- Model maliyeti ~%40 azaldi (haiku sub-agent'lar ucuz)
- Her sub-agent kendi kontekstinde calisir, prompt uzunlugu kisaldi
- Yeni skill eklemek icin sadece ilgili sub-agent'a atama yeterli
- Trade-off: Dispatch overhead (orchestrator -> sub-agent arasi Task call)
