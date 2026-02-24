# ADR-0004: Kit vs MCP Ayrimi
Tarih: 2025-02-22
Durum: Kabul edildi

## Baglam
Kit, Parasut (ERP) ve Dynamics 365 Sales (CRM) kullanan bir ortamda calisacak. Soru: veri erisimi kit'in icinde mi olmali, disinda mi?

## Karar
Uc katmanli ayrim:
- **Kit (bu repo) = saf zeka katmani.** Hesaplama, strateji, analiz skill'leri. Veri kaynagi bilmez.
- **MCP server'lar = veri katmani.** Kit'in parcasi degil. Ayri repo'larda gelistirilir.
  - D365 Sales MCP: Microsoft resmi (preview)
  - Parasut MCP: Gerekirse ayri repo olarak yazilacak
- **Hedef repo = bulusma noktasi.** install.sh ile kit kurulur, .claude/settings.json ile MCP config eklenir.

Akis: ERP/CRM -> MCP server (veri) -> Claude Code -> Ragip Aga skill (zeka) -> sonuc

## Sonuc
- Kit bagimsiz kalir, herhangi bir veri kaynagi ile calisabilir
- MCP server'lar bagimsiz gelistirilir/test edilir
- Kit'e MCP kodu girmez, skill'ler veri kaynagini bilmez
- Trade-off: Entegrasyon testi hedef repoda yapilmali (kit'te yapilmaz)
