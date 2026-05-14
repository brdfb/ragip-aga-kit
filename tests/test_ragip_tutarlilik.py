"""Tier 4 — Dokuman tutarlilik kontrolu (ADR-0018, v2.17.0)."""
from __future__ import annotations

from pathlib import Path

import pytest

KIT_ROOT = Path(__file__).resolve().parents[1]

# Tier 4 uygulanan skill'ler (ADR-0018 kapsam tablosu)
LLM_SKILLS_TIER4 = ["ragip-analiz", "ragip-strateji", "ragip-degerlendirme"]


def _skills_dir() -> Path:
    src = KIT_ROOT / "skills"
    if src.exists():
        return src
    return KIT_ROOT / ".claude" / "skills"


@pytest.fixture(scope="module")
def skill_metinleri() -> dict[str, str]:
    out = {}
    for s in LLM_SKILLS_TIER4:
        out[s] = (_skills_dir() / s / "SKILL.md").read_text(encoding="utf-8")
    return out


class TestTier4PromptlardaMevcut:
    @pytest.mark.parametrize("skill", LLM_SKILLS_TIER4)
    def test_tutarlilik_denetimi_terimi(self, skill_metinleri, skill):
        metin = skill_metinleri[skill]
        assert "Tutarlilik denetimi" in metin, (
            f"{skill}: 'Tutarlilik denetimi' notu eksik (Tier 4)"
        )

    @pytest.mark.parametrize("skill", LLM_SKILLS_TIER4)
    def test_tier4_referansi(self, skill_metinleri, skill):
        metin = skill_metinleri[skill]
        assert "Tier 4" in metin and "ADR-0018" in metin, (
            f"{skill}: Tier 4 + ADR-0018 referansi eksik"
        )

    @pytest.mark.parametrize("skill", LLM_SKILLS_TIER4)
    def test_dort_kontrol_kategorisi(self, skill_metinleri, skill):
        """Tier 4 prompt 4 ana kontrol kategorisini gostermeli (SAYI/ETIKET/MANTIK/SENARYO veya esdeger)."""
        metin = skill_metinleri[skill]
        kategoriler = ["[SAYI]", "[ETIKET]", "[MANTIK]"]
        eslesme = sum(1 for k in kategoriler if k in metin)
        assert eslesme >= 3, (
            f"{skill}: Tier 4 kontrol kategorileri eksik "
            f"(beklenen en az 3: SAYI/ETIKET/MANTIK, bulundu: {eslesme})"
        )

    @pytest.mark.parametrize("skill", LLM_SKILLS_TIER4)
    def test_denetim_notu_formati(self, skill_metinleri, skill):
        metin = skill_metinleri[skill]
        # Iki olasi cikti formati prompt'ta gosterilmeli
        assert "celiski bulundu" in metin.lower() or "duzeltildi" in metin.lower(), (
            f"{skill}: 'celiski bulundu/duzeltildi' formati eksik"
        )
        assert "temiz" in metin.lower(), (
            f"{skill}: 'temiz' notu formati eksik"
        )


class TestKapsamDisi:
    """Tier 4 deterministik skill'lere uygulanmamali."""

    @pytest.mark.parametrize("skill", ["ragip-vade-farki", "ragip-arbitraj", "ragip-zamanasimi"])
    def test_deterministik_skill_kapsam_disi(self, skill):
        metin = (_skills_dir() / skill / "SKILL.md").read_text(encoding="utf-8")
        # ZORUNLU Tier 4 enforcement deterministik skillere eklenmemeli
        zorunlu_tier4 = (
            "Tier 4" in metin and "ZORUNLU" in metin and "Tutarlilik denetimi" in metin
        )
        assert not zorunlu_tier4, (
            f"{skill}: deterministik skill'e Tier 4 ZORUNLU eklenmis — uygunsuz"
        )


class TestAdr0018Mevcut:
    def test_adr_dosyasi_var(self):
        adr = KIT_ROOT / "docs" / "adr" / "0018-tier-4-dokuman-tutarlilik.md"
        assert adr.exists(), "ADR-0018 dosyasi eksik"

    def test_adr_kapsami(self):
        metin = (KIT_ROOT / "docs" / "adr" / "0018-tier-4-dokuman-tutarlilik.md").read_text(encoding="utf-8")
        for kavram in ("Tier 4", "Tutarlilik", "K3", "ADR-0010", "ADR-0016"):
            assert kavram in metin, f"ADR-0018: '{kavram}' kavrami eksik"

    def test_adr_cherry_pick_kaynagi(self):
        metin = (KIT_ROOT / "docs" / "adr" / "0018-tier-4-dokuman-tutarlilik.md").read_text(encoding="utf-8")
        # CFO agent K3 cherry-pick referansi olmali
        assert "gibibyte-cfo-agent" in metin and "K3" in metin, (
            "ADR-0018 cherry-pick kaynagi (CFO K3) belgelemeli"
        )
