# Ragip Aga — Dispatch Kurallari

Ana session'dan (Level 0) dogrudan sub-agent dispatch:

| Kullanici istegi | Sub-agent |
|-----------------|-----------|
| Hesaplama, vade farki, TVM, arbitraj, rapor | ragip-hesap |
| Sozlesme/fatura analizi, arastirma, strateji | ragip-arastirma |
| Hukuki degerlendirme, zamanasimi, delil, ihtar | ragip-hukuk |
| Firma CRUD, gorev, import, ozet, profil | ragip-veri |

## Cagri Formati

Agent tool ile:
- subagent_type: "ragip-hesap" | "ragip-arastirma" | "ragip-hukuk" | "ragip-veri"
- prompt: [gorev aciklamasi]

## Senaryo A vs B

**Senaryo A** — Cok adimli / cok sub-agent is:
`claude --agent ragip-aga` ile dedicated session ac.
ragip-aga Level 0 olarak 4 sub-agent'i dispatch eder.

**Senaryo B** — Hizli sorgu / gelistirme session'i (su anki gibi):
Ana session dogrudan sub-agent spawn eder.
Bu dispatch tablosu gecerlidir — ragip-aga.md okumak gerekmez.

## Onemli Not

ragip-aga sub-agent olarak spawn edilirse (Level 1), Agent tool ile
baska sub-agent spawn etmesi guvenilmez. Detay: docs/adr/0009-hybrid-orchestrator.md
