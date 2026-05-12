"""Tier 2C kaynak domain whitelist testleri — ragip-hukuk citation authority."""
from __future__ import annotations

from pathlib import Path

import pytest

KIT_ROOT = Path(__file__).resolve().parents[1]

# Tier 2C whitelist — resmi hukuki kaynak domainleri (ADR-0015)
WHITELIST_DOMAINS = [
    "mevzuat.gov.tr",
    "resmigazete.gov.tr",
    "yargitay.gov.tr",
    "karararama.yargitay.gov.tr",
    "danistay.gov.tr",
    "anayasa.gov.tr",
    "adalet.gov.tr",
    "hsk.gov.tr",
]


def _agents_dir() -> Path:
    """Kit kaynak veya kurulu repo agent dizinini bul."""
    src = KIT_ROOT / "agents"
    if src.exists():
        return src
    installed = KIT_ROOT / ".claude" / "agents"
    return installed


def _skills_dir() -> Path:
    src = KIT_ROOT / "skills"
    if src.exists():
        return src
    return KIT_ROOT / ".claude" / "skills"


@pytest.fixture(scope="module")
def ragip_hukuk_md() -> str:
    return (_agents_dir() / "ragip-hukuk.md").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def ragip_degerlendirme_md() -> str:
    return (_skills_dir() / "ragip-degerlendirme" / "SKILL.md").read_text(encoding="utf-8")


class TestRagipHukukAgent:
    def test_tier_2c_bolumu_mevcut(self, ragip_hukuk_md):
        assert "TIER 2C" in ragip_hukuk_md
        assert "WHITELIST" in ragip_hukuk_md.upper() or "whitelist" in ragip_hukuk_md

    def test_tum_whitelist_domainleri_listelenmis(self, ragip_hukuk_md):
        for domain in WHITELIST_DOMAINS:
            assert domain in ragip_hukuk_md, f"{domain} ragip-hukuk.md'de eksik"

    def test_adr_referansi(self, ragip_hukuk_md):
        assert "ADR-0015" in ragip_hukuk_md

    def test_tier_katmanlari_zincirinde(self, ragip_hukuk_md):
        # Tier 1 Barnum + Tier 2A madde_dogrula + Tier 2B CoVe + Tier 2C whitelist
        for marker in ("Barnum", "madde_dogrula", "CoVe"):
            assert marker in ragip_hukuk_md, f"{marker} zinciri ragip-hukuk.md'de eksik"


class TestRagipDegerlendirmeSkill:
    def test_webfetch_eklenmis(self, ragip_degerlendirme_md):
        # Tier 2C teyit icin WebFetch gerekli (whitelist domain'inde dogrulama)
        ilk_satirlar = ragip_degerlendirme_md.split("---", 2)
        assert len(ilk_satirlar) >= 3
        frontmatter = ilk_satirlar[1]
        assert "WebFetch" in frontmatter, "ragip-degerlendirme allowed-tools'a WebFetch eklenmemis"

    def test_tier_2c_bolumu_mevcut(self, ragip_degerlendirme_md):
        assert "TIER 2C" in ragip_degerlendirme_md

    def test_whitelist_domainleri_skillde_de_var(self, ragip_degerlendirme_md):
        for domain in WHITELIST_DOMAINS:
            assert domain in ragip_degerlendirme_md, f"{domain} ragip-degerlendirme/SKILL.md'de eksik"

    def test_site_filtreli_arama_ornegi(self, ragip_degerlendirme_md):
        # WebSearch sorgusu site: filtresi onerisi icermeli
        assert "site:mevzuat.gov.tr" in ragip_degerlendirme_md or "site:resmigazete.gov.tr" in ragip_degerlendirme_md

    def test_whitelist_disi_davranis_tanimli(self, ragip_degerlendirme_md):
        # Whitelist disi sonuc icin acik politika
        assert "teyit edilemedi" in ragip_degerlendirme_md.lower() or "alintilanmadi" in ragip_degerlendirme_md.lower()


class TestWhitelistTutarliligi:
    def test_agent_skill_domain_listesi_ayni(self, ragip_hukuk_md, ragip_degerlendirme_md):
        # Agent ve skill ayni domain listesini referans almali
        for domain in WHITELIST_DOMAINS:
            in_agent = domain in ragip_hukuk_md
            in_skill = domain in ragip_degerlendirme_md
            assert in_agent == in_skill, (
                f"{domain} tutarsiz: agent={in_agent}, skill={in_skill}"
            )

    def test_diger_hukuk_skilllerinde_websearch_yok(self):
        # ragip-zamanasimi, ragip-delil, ragip-ihtar WebSearch kullanmamali
        # (whitelist sadece WebSearch kullanan skill icin gerekli)
        for skill in ("ragip-zamanasimi", "ragip-delil", "ragip-ihtar"):
            metin = (_skills_dir() / skill / "SKILL.md").read_text(encoding="utf-8")
            frontmatter = metin.split("---", 2)[1]
            assert "WebSearch" not in frontmatter, (
                f"{skill} WebSearch kullaniyor — Tier 2C whitelist eklenmesi gerekir"
            )


class TestAdr0015Mevcut:
    def test_adr_dosyasi_var(self):
        adr = KIT_ROOT / "docs" / "adr" / "0015-citation-source-whitelist.md"
        assert adr.exists(), "ADR-0015 dosyasi eksik"

    def test_adr_whitelist_iceriyor(self):
        adr = KIT_ROOT / "docs" / "adr" / "0015-citation-source-whitelist.md"
        metin = adr.read_text(encoding="utf-8")
        for domain in WHITELIST_DOMAINS:
            assert domain in metin, f"{domain} ADR-0015'te eksik"
