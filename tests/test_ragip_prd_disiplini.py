"""Orchestrator PRD disiplini testleri — ragip-aga karmasik is icin onay (ADR-0017)."""
from __future__ import annotations

from pathlib import Path

import pytest

KIT_ROOT = Path(__file__).resolve().parents[1]


def _agents_dir() -> Path:
    src = KIT_ROOT / "agents"
    if src.exists():
        return src
    return KIT_ROOT / ".claude" / "agents"


@pytest.fixture(scope="module")
def ragip_aga_md() -> str:
    return (_agents_dir() / "ragip-aga.md").read_text(encoding="utf-8")


class TestPrdBolumuMevcut:
    def test_prd_section_header(self, ragip_aga_md):
        assert "PRD DISIPLINI" in ragip_aga_md or "PRD Disiplini" in ragip_aga_md

    def test_adr_referansi(self, ragip_aga_md):
        assert "ADR-0017" in ragip_aga_md

    def test_cherry_pick_kaynagi(self, ragip_aga_md):
        # gibibyte-cfo-agent K4 referansi olmali (kaynak kayit)
        assert "gibibyte-cfo-agent" in ragip_aga_md.lower() or "cfo-agent" in ragip_aga_md.lower()


class TestKarmaikIsTetigi:
    @pytest.mark.parametrize("kelime", [
        "tam analiz",
        "strateji",
        "ihtar",
        "dosya hazirla",
        "firma degerlendirmesi",
    ])
    def test_anahtar_kelime_listede(self, ragip_aga_md, kelime):
        assert kelime in ragip_aga_md.lower(), (
            f"'{kelime}' karmasik-is tetik listesinde eksik"
        )


class TestPrdFormati:
    def test_prd_format_ornegi(self, ragip_aga_md):
        # Format: "Sunu yapacagim: ... → ragip-X → ... Devam edeyim mi?"
        assert "Sunu yapacagim" in ragip_aga_md or "Şunu yapacağım" in ragip_aga_md
        assert "Devam edeyim mi" in ragip_aga_md

    def test_onay_kelimeleri(self, ragip_aga_md):
        # Onay alternatifleri
        metin = ragip_aga_md.lower()
        for onay in ("evet", "devam", "yap"):
            assert onay in metin, f"Onay kelimesi '{onay}' tanımlanmamis"

    def test_red_kelimeleri(self, ragip_aga_md):
        # Red/duzeltme alternatifleri
        metin = ragip_aga_md.lower()
        for red in ("hayir", "dur", "duzelt"):
            assert red in metin, f"Red/duzeltme kelimesi '{red}' tanımlanmamis"


class TestTrivialBypass:
    def test_bypass_bolumu_mevcut(self, ragip_aga_md):
        # Trivial isler icin PRD'siz dispatch politikasi
        metin = ragip_aga_md.lower()
        assert "bypass" in metin or "dogrudan dispatch" in metin or "prd'siz" in metin

    @pytest.mark.parametrize("trivial_ornek", [
        "vade farki",       # hesaplama bypass
        "listele",          # liste bypass
        "tek skill",        # tek skill bypass
        "soru-cevap",       # kavramsal cevap bypass
    ])
    def test_trivial_ornekleri(self, ragip_aga_md, trivial_ornek):
        assert trivial_ornek in ragip_aga_md.lower(), (
            f"Trivial bypass ornegi '{trivial_ornek}' eksik"
        )


class TestCalismaAkisiEntegre:
    def test_prd_karari_adimi(self, ragip_aga_md):
        # CALISMA AKISI'nda PRD karari adimi olmali (Adim 2 olarak)
        assert "PRD karari" in ragip_aga_md or "PRD kararı" in ragip_aga_md

    def test_orijinal_adim_korunmus(self, ragip_aga_md):
        # Yonlendir, Sentezle, Kaydet, Persist adimlari hala var
        for adim in ("Yonlendir", "Sentezle", "Kaydet", "Persist"):
            assert adim in ragip_aga_md, f"CALISMA AKISI adimi '{adim}' kayboldu"


class TestAdr0017Mevcut:
    def test_adr_dosyasi_var(self):
        adr = KIT_ROOT / "docs" / "adr" / "0017-orchestrator-prd-disiplini.md"
        assert adr.exists(), "ADR-0017 dosyasi eksik"

    def test_adr_kapsami(self):
        metin = (KIT_ROOT / "docs" / "adr" / "0017-orchestrator-prd-disiplini.md").read_text(encoding="utf-8")
        for kavram in ("PRD", "trivial", "tetik", "onay", "K4"):
            assert kavram in metin, f"ADR-0017: '{kavram}' kavrami eksik"


class TestNonInteractiveFallback:
    """v2.17.0 Patch #1 — PRD non-interactive modda stuck olmamali."""

    def test_agent_promptunda_non_interactive_kelimesi(self, ragip_aga_md):
        # Agent prompt non-interactive senaryoyu acikca ele almali
        assert "non-interactive" in ragip_aga_md.lower() or "-p" in ragip_aga_md, (
            "ragip-aga.md non-interactive PRD fallback'i belirtmeli"
        )

    def test_agent_promptunda_fallback_davranisi(self, ragip_aga_md):
        # Fallback davranisi: PRD ozetini cikti olarak yaz + dispatch
        # En az iki bilesen prompt'ta gecmeli
        kavramlar = ["fallback", "dispatch", "cikti", "stuck", "onay beklemeden", "kullanici yok"]
        eslesme = sum(1 for k in kavramlar if k.lower() in ragip_aga_md.lower())
        assert eslesme >= 2, (
            f"ragip-aga.md non-interactive fallback'i yetersiz tanimliyor "
            f"(en az 2 kavram beklenir, bulundu: {eslesme})"
        )

    def test_adr_non_interactive_kapsami(self):
        adr = KIT_ROOT / "docs" / "adr" / "0017-orchestrator-prd-disiplini.md"
        metin = adr.read_text(encoding="utf-8")
        # ADR Patch #1'i ve fallback kararini belgelemeli
        assert "non-interactive" in metin.lower(), "ADR-0017 non-interactive fallback'i belgelemeli"
        assert "v2.17.0" in metin or "Patch #1" in metin, (
            "ADR-0017 fallback kararinin geldigi versiyonu belgelemeli"
        )

    def test_v2_17_1_acik_sinyal_semantigi(self, ragip_aga_md):
        """v2.17.1 sadelestirme: fallback ancak ACIK kullanici sinyali ile tetiklenir."""
        # Belirsiz sessizlik heuristik'i yasak olmali (yanlis dispatch riski)
        assert "acik" in ragip_aga_md.lower() and "sinyal" in ragip_aga_md.lower(), (
            "PRD fallback 'acik sinyal' kavramini iceriyor olmali"
        )
        # CLI cozumune referans olmali (mevcut prompt-level cozumun sinirli oldugu kabul)
        assert "kit-disi" in ragip_aga_md.lower() or "CLI" in ragip_aga_md, (
            "Asil cozum kit-disi (CLI/harness) oldugu prompt'ta acikca belirtilmeli"
        )
