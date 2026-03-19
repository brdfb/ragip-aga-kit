# ADR-0004: Kit vs MCP Ayrimi
Tarih: 2025-02-22
Durum: Guncellendi — 2026-03-20 (semantic tool zorunlulugu + MCP katmani netlesti)

## Baglam
Kit, Parasut (ERP) ve Dynamics 365 Sales (CRM) kullanan bir ortamda calisacak. Soru: veri erisimi kit'in icinde mi olmali, disinda mi?

## Karar
Uc katmanli ayrim:
- **Kit (bu repo) = zeka + validasyon katmani.** Hesaplama, strateji, analiz skill'leri + ADR-0007 sema validasyonu. Veri kaynagi bilmez, ama veri kalitesini dogrular.
- **MCP server'lar = veri + ERP-aware normalizasyon katmani.** Kit'in parcasi degil. Ayri repo'larda gelistirilir.
  - D365 Sales MCP: Custom FastMCP server (ragip_dataverse_mcp.py)
  - Parasut MCP: Gerekirse ayri repo olarak yazilacak
  - **DTO katmani:** ERP-specific normalizasyon (brut/net duzeltme, doviz cevrimi, kismi odeme, durum mapping) MCP repo'sunda yasar, kit'te degil.
- **Hedef repo = bulusma noktasi.** install.sh ile kit kurulur, MCP config eklenir.

Akis: ERP/CRM -> MCP server (ham veri) -> DTO (normalizasyon) -> faturalar.jsonl (ADR-0007) -> validate_fatura() (kit) -> FinansalHesap (kit) -> sonuc

### Guncelleme: "MCP = veri" yetersiz

Ilk versiyonda "MCP = saf veri katmani" tanimlandi. Gercek uygulama (D365 MCP) gosterdi ki MCP katmani onemli is mantigi tasiyor:

| Katman | Sorumluluk | Ornek |
|--------|-----------|-------|
| MCP server | ERP API erisimi, auth, pagination | MSAL token, OData query |
| DTO | ERP-aware normalizasyon | Brut/net duzeltme, doviz→TL cevrimi, InvoiceDTO→ADR-0007 |
| Kit validate | Sema dogrulama | validate_fatura() — zorunlu alan, tip, enum, tutarlilik |
| Kit hesaplama | Finansal analiz | FinansalHesap — aging, DSO, vade farki |

**DTO katmani kit'e alinmaz.** Her ERP'nin normalizasyon kurallari farkli — bu is mantigi ERP'ye ozgu. Kit yalnizca ADR-0007 semasini dogrular ve hesaplar.

### Guncelleme: Semantic Tool Zorunlulugu (2026-03-20)

Gercek uygulama (D365 MCP) gosterdi ki agent'lar ham MCP tool'larina (query_records, fatura_listele) dogrudan eristiginde normalize edilmemis veriyi yanlis yorumluyor. Ornekte ham tool 24 acik fatura / $124K raporlarken, normalize semantic tool 2 acik fatura / $20K (gercek) sonuc uretti.

**Karar:** Her MCP adaptorunde semantic tool (orn: `firma_raporu`) ZORUNLU. Ham tool'lar TUM agent'larda `disallowedTools` ile bloke edilmeli — sadece orchestrator'da degil.

**Neden prompt kisitlamasi yetmez:** Agent MCP tool gorunde system prompt talimatini atlayip dogrudan ham tool'u cagiriyor. `disallowedTools` frontmatter ile runtime'da engellenir.

Detay: MCP_ENTEGRASYON_REHBERI.md Adim 3 (Semantic Tool) ve Adim 5 (disallowedTools).

## Sonuc
- Kit bagimsiz kalir, herhangi bir veri kaynagi ile calisabilir
- MCP server'lar bagimsiz gelistirilir/test edilir
- Kit'e MCP kodu girmez, skill'ler veri kaynagini bilmez
- Kit sema validasyonu yapar (validate_fatura) — MCP'den gelen verinin ADR-0007'ye uygunlugunu dogrular
- DTO normalizasyonu (brut/net, doviz, durum mapping) MCP repo'sunda kalir
- Semantic tool zorunlu — agent'lar ham MCP tool'larina erismemeli
- Ham MCP tool'lari tum agent'larda disallowedTools ile bloke edilmeli
- Trade-off: Entegrasyon testi hedef repoda yapilmali (kit'te yapilmaz)
- Trade-off: DTO katmani her yeni ERP icin yazilmali — kit dokunulmaz, ama MCP+DTO eforu var
