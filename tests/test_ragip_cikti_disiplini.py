"""Tier 3 cikti disiplini testleri — 3-satir blok formati + VARSAYIM damgasi (ADR-0016)."""
from __future__ import annotations

from pathlib import Path

import pytest

KIT_ROOT = Path(__file__).resolve().parents[1]

# Disiplinin uygulandigi LLM skill'leri
# (ragip-rapor deterministik FinansalHesap ciktisi, ragip-vade-farki/arbitraj deterministik hesap)
LLM_SKILLS_KAPSAM = ["ragip-analiz", "ragip-strateji", "ragip-degerlendirme"]

# Disiplinin uygulanmadigi skill'ler — VARSAYIM/3-satir gereksiz
DETERMINISTIK_SKILLS = ["ragip-vade-farki", "ragip-arbitraj", "ragip-zamanasimi"]


def _skills_dir() -> Path:
    src = KIT_ROOT / "skills"
    if src.exists():
        return src
    return KIT_ROOT / ".claude" / "skills"


@pytest.fixture(scope="module")
def skill_metinleri() -> dict[str, str]:
    out = {}
    for s in LLM_SKILLS_KAPSAM:
        out[s] = (_skills_dir() / s / "SKILL.md").read_text(encoding="utf-8")
    return out


class TestUcSatirBlokFormati:
    @pytest.mark.parametrize("skill", LLM_SKILLS_KAPSAM)
    def test_tespit_pozisyon_gerekce_uclu_var(self, skill_metinleri, skill):
        metin = skill_metinleri[skill]
        # Uc anahtar pattern beraber yer almali (skill icinde tek block tanimi)
        assert "TESPIT" in metin, f"{skill}: TESPIT eksik"
        assert "POZISYON" in metin, f"{skill}: POZISYON eksik"
        assert "GEREKCE" in metin, f"{skill}: GEREKCE eksik"

    @pytest.mark.parametrize("skill", LLM_SKILLS_KAPSAM)
    def test_3_satir_blok_terimi(self, skill_metinleri, skill):
        # "3-satir" pattern'i acikca gecmeli
        metin = skill_metinleri[skill].lower()
        assert "3-satir" in metin or "3-satir blok" in metin or "uc satir" in metin, (
            f"{skill}: '3-satir blok formati' referansi eksik"
        )


class TestVarsayimDamgasi:
    @pytest.mark.parametrize("skill", LLM_SKILLS_KAPSAM)
    def test_varsayim_kelimesi_geciyor(self, skill_metinleri, skill):
        assert "VARSAYIM" in skill_metinleri[skill], f"{skill}: VARSAYIM damgasi tanimi eksik"

    @pytest.mark.parametrize("skill", LLM_SKILLS_KAPSAM)
    def test_aralik_tek_nokta_yasak(self, skill_metinleri, skill):
        metin = skill_metinleri[skill].lower()
        # "tek nokta yasak" veya "aralik" geciyor olmali — VARSAYIM disiplini
        assert "tek nokta" in metin or "aralik" in metin, (
            f"{skill}: VARSAYIM aralik kurali eksik"
        )

    @pytest.mark.parametrize("skill", LLM_SKILLS_KAPSAM)
    def test_kesinlesmek_icin_dil(self, skill_metinleri, skill):
        # "kesinlesmek icin [X] gerekli" disiplini
        metin = skill_metinleri[skill].lower()
        assert "kesinlesmek" in metin or "kesinleşmek" in metin, (
            f"{skill}: 'kesinlesmek icin ... gerekli' VARSAYIM kuyrugu eksik"
        )


class TestSesKorundu:
    @pytest.mark.parametrize("skill", LLM_SKILLS_KAPSAM)
    def test_anlatim_serbest_kurali(self, skill_metinleri, skill):
        # "Anlatim ... serbest" veya "SADECE kritik bulgu" gibi sınirlayici ifade
        metin = skill_metinleri[skill].lower()
        assert "anlatim" in metin or "sadece" in metin or "serbest" in metin, (
            f"{skill}: 'anlatim sesi serbest' kurali eksik — X5 reddine uyumlu olmali"
        )


class TestKapsamDisi:
    @pytest.mark.parametrize("skill", DETERMINISTIK_SKILLS)
    def test_deterministik_skiller_kapsamda_degil(self, skill):
        # ragip-vade-farki, ragip-arbitraj, ragip-zamanasimi deterministik — VARSAYIM gereksiz
        # Bu test "yanlislikla zorunluluk eklenirse" uyari amaciyla; mevcut state'i kayit altina alir.
        metin = (_skills_dir() / skill / "SKILL.md").read_text(encoding="utf-8")
        # Bu skill'lerde VARSAYIM disiplini ZORUNLULUK olarak eklenmemeli
        # (kelime gecebilir ama "ZORUNLU" beraberinde olmamali)
        zorunlu_varsayim = "VARSAYIM" in metin and (
            "VARSAYIM damgasi" in metin and "zorunlu" in metin.lower()
        )
        assert not zorunlu_varsayim, (
            f"{skill}: deterministik skill'e VARSAYIM zorunlulugu eklenmis — uygunsuz"
        )


class TestAdr0016Mevcut:
    def test_adr_dosyasi_var(self):
        adr = KIT_ROOT / "docs" / "adr" / "0016-cikti-disiplini-tier-3.md"
        assert adr.exists(), "ADR-0016 dosyasi eksik"

    def test_adr_kapsami(self):
        metin = (KIT_ROOT / "docs" / "adr" / "0016-cikti-disiplini-tier-3.md").read_text(encoding="utf-8")
        for kavram in ("TESPIT", "POZISYON", "GEREKCE", "VARSAYIM", "X5"):
            assert kavram in metin, f"ADR-0016: {kavram} kavrami eksik"


class TestKesinlikKalibi:
    """A5 — Tier 1 Barnum guclendirme: 'Do not fabricate certainty' tum LLM skill'lerinde."""

    @pytest.mark.parametrize("skill", LLM_SKILLS_KAPSAM)
    def test_kesinlik_kalibi_kurali_var(self, skill_metinleri, skill):
        metin = skill_metinleri[skill]
        # Yeni alt-kural "Kesinlik kalibi" baslikla geciyor olmali
        assert "Kesinlik kalibi" in metin, (
            f"{skill}: 'Kesinlik kalibi' alt-kurali eksik"
        )

    @pytest.mark.parametrize("skill", LLM_SKILLS_KAPSAM)
    def test_do_not_fabricate_certainty(self, skill_metinleri, skill):
        metin = skill_metinleri[skill]
        assert "Do not fabricate certainty" in metin, (
            f"{skill}: 'Do not fabricate certainty' ifadesi eksik (Data Quality Rule)"
        )

    @pytest.mark.parametrize("skill", LLM_SKILLS_KAPSAM)
    def test_belirsizlik_gizleme_uyarisi(self, skill_metinleri, skill):
        metin = skill_metinleri[skill]
        # Mutlak ifade yasagi acikca gecmeli — model "kesin/muhakkak/kesinlikle" yasagini gormeli
        mutlak_kelimeler = ["kesin", "muhakkak", "kesinlikle"]
        eslesme = sum(1 for k in mutlak_kelimeler if k in metin)
        assert eslesme >= 2, (
            f"{skill}: mutlak ifade yasagi yeterince acik degil "
            f"(beklenen >= 2 ornek kelime, bulundu: {eslesme})"
        )

    @pytest.mark.parametrize("skill", LLM_SKILLS_KAPSAM)
    def test_pozitif_olasilik_dili(self, skill_metinleri, skill):
        """v2.17.1: pozitif yonlendirme — olasilik kelimeleri prompt'ta gosterilmeli."""
        metin = skill_metinleri[skill]
        olasilik_kelimeleri = ["olası", "muhtemel", "tahmin", "belirsiz"]
        eslesme = sum(1 for k in olasilik_kelimeleri if k in metin)
        assert eslesme >= 3, (
            f"{skill}: pozitif olasilik dili yeterince acik degil "
            f"(beklenen >= 3 ornek kelime, bulundu: {eslesme}). "
            f"v2.17.1 pozitif yonlendirme kuralı."
        )

    @pytest.mark.parametrize("skill", LLM_SKILLS_KAPSAM)
    def test_veri_yok_kosullu_yasak(self, skill_metinleri, skill):
        """v2.17.1: mutlak ifade yasagi kosullu olmali — 'veri yok' / 'veri eksik' tetik ile."""
        metin = skill_metinleri[skill]
        # Yasagin kosulu (veri-yok durumu) acikca belirtilmeli
        kosullar = ["veri yok", "veri eksik", "veri-yok"]
        eslesme = sum(1 for k in kosullar if k.lower() in metin.lower())
        assert eslesme >= 1, (
            f"{skill}: mutlak ifade yasagi kosullu olarak belirtilmeli "
            f"(veri-yok durumu tetik). Yoksa Turkce legitimate kullanim "
            f"(orn: 'hukum kesinlesti') yakalanir."
        )
