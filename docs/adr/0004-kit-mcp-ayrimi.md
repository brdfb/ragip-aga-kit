# ADR-0004: Kit vs MCP Ayrimi
Tarih: 2025-02-22
Durum: Guncellendi — 2026-03-19 (MCP katmani netlesti)

## Baglam
Kit, Parasut (ERP) ve Dynamics 365 Sales (CRM) kullanan bir ortamda calisacak. Soru: veri erisimi kit'in icinde mi olmali, disinda mi?

## Karar
Uc katmanli ayrim:
- **Kit (bu repo) = zeka + validasyon katmani.** Hesaplama, strateji, analiz skill'leri + ADR-0007 sema validasyonu. Veri kaynagi bilmez, ama veri kalitesini dogrular.
- **MCP server'lar = veri + ERP-aware normalizasyon katmani.** Kit'in parcasi degil. Ayri repo'larda gelistirilir.
  - D365 Sales MCP: Custom FastMCP server (ragip_dataverse_mcp.py)
  - Parasut MCP: Gerekirse ayri repo olarak yazilacak
  - **DTO katmani:** ERP-specific normalizasyon (brut/net duzeltme, doviz cevrimi, kismi odeme, durum mapping) MCP repo'sunda yasaR, kit'te degil.
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

## Sonuc
- Kit bagimsiz kalir, herhangi bir veri kaynagi ile calisabilir
- MCP server'lar bagimsiz gelistirilir/test edilir
- Kit'e MCP kodu girmez, skill'ler veri kaynagini bilmez
- Kit sema validasyonu yapar (validate_fatura) — MCP'den gelen verinin ADR-0007'ye uygunlugunu dogrular
- DTO normalizasyonu (brut/net, doviz, durum mapping) MCP repo'sunda kalir
- Trade-off: Entegrasyon testi hedef repoda yapilmali (kit'te yapilmaz)
- Trade-off: DTO katmani her yeni ERP icin yazilmali — kit dokunulmaz, ama MCP+DTO eforu var
