# Ekosistem Repo Haritasi

> Son guncelleme: 2026-03-27

## Repolar

| # | Repo | Path | Rol | GitHub |
|---|------|------|-----|--------|
| 1 | ragip-aga-kit | ~/projects/ragip-aga-kit | Kit (kaynak), install.sh ile dagitilir | brdfb (github.com) |
| 2 | ragip-workspace | ~/projects/ragip-workspace | Kit kurulumu + D365 MCP | — |
| 3 | gb_ragipaga | ~/projects/gb_ragipaga | Emekli, referans | — |
| 4 | dyn365hunterv3 | ~/projects/dyn365hunterv3 | Lead intelligence, Azure VM, production | brdfb (github.com) |
| 5 | PRST | ~/projects/PRST | Parasut→D365 sync, ayri ekip | brdfbai (github-brdfbai) |
| 6 | gibibyte-knowledge-source | ~/projects/gibibyte-knowledge-source | RAG knowledge base, 65 dokuman, v0.7.0 | brdfbai |
| 7 | gibibyte-agent | ~/projects/gibibyte-agent | RAG agent, 20 skill, Qdrant, v0.9.0 | brdfbai |
| 8 | gibibyte-continuity-hub | ~/projects/gibibyte-continuity-hub | Website (gibibyte.com.tr), React+Vercel, Lead Engine | brdfbai |

## D365 Ortak Instance

- **Hunter** → lead olusturur (hnt_* alanlari) — satis oncesi
- **PRST** → fatura/odeme sync (prst_* alanlari) — satis sonrasi
- **Ragip MCP** → okur, analiz eder — operasyon

## SSH Erisim

- `brdfb` (kisisel) → github.com → ragip-aga-kit, dyn365hunterv3
- `brdfbai` (organizasyon) → github-brdfbai → PRST, gibibyte-*
