"""ragip_format_dogrula.py testleri — Tier 3/4 format dogrulama (ADR-0019)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

KIT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT_ROOT / "scripts"))

from ragip_format_dogrula import dogrula_metin  # noqa: E402


# Tam format-temiz ornek (Tier 3 + Tier 4 hepsi mevcut)
TEMIZ_RAPOR = """### SONUC VE ONERILER

TESPIT: 14 acik fatura, anapara (kalan) 142.593 USD, gecikme 220-827 gun.
   Etki: 79K USD faiz (TTK m.1530) (%55 anapara ustu) ↑ aylik 3K USD birikim, 30gun ihtar
POZISYON: Noter ihtari gonder. · Sahip: Hukuk · Zaman: 5 is gunu · Beklenen: 30 gun icinde tahsilat
GEREKCE: TTK m.21/2 itiraz suresi gecmis, alacak kesinlesti.

---

Tutarlilik denetimi: temiz.
"""

# Eksik 1: TESPIT yok
EKSIK_TESPIT = """### SONUC

Anapara (kalan) 142K USD, faiz 79K USD. Ihtar gonderilmeli.

Tutarlilik denetimi: temiz.
"""

# Eksik 2: POZISYON 5-bilesen yok
EKSIK_POZ_5BIL = """TESPIT: 14 acik fatura, anapara (kalan) 142K USD.
   Etki: 79K USD faiz (%55) ↑ 30gun
POZISYON: Ihtar gonder.
GEREKCE: TTK m.21/2.

Tutarlilik denetimi: temiz.
"""

# Eksik 3: Anapara etiket yok
EKSIK_ANAPARA_ETIKET = """TESPIT: 14 acik fatura, anapara 142K USD, gecikme 220-827 gun.
   Etki: 79K USD faiz (%55) ↑ 30gun
POZISYON: Ihtar gonder. · Sahip: Hukuk · Zaman: 5 gun · Beklenen: 30 gun tahsilat
GEREKCE: TTK m.21/2.

Tutarlilik denetimi: temiz.
"""

# Eksik 4: Tutarlilik denetimi notu yok
EKSIK_TUTARLILIK = """TESPIT: 14 acik fatura, anapara (kalan) 142K USD.
   Etki: 79K USD faiz (%55) ↑ 30gun
POZISYON: Ihtar gonder. · Sahip: Hukuk · Zaman: 5 gun · Beklenen: 30 gun tahsilat
GEREKCE: TTK m.21/2.
"""

# Hicbir blok yok (eski format — gerçek v2.16/v2.17/v2.18 çıktıları gibi)
TAMAMEN_EKSIK = """### POZISYON: GUCLU

14 fatura belgelenmis, itiraz yok, odeme yok. Temerut otomatik baslamis.

Anapara: 142.592,96 USD
Faiz: 78.038,59 USD
"""

# Anapara hic gecmiyor — etiket gereksiz
ANAPARASIZ_TEMIZ = """TESPIT: 3 sozlesme maddesi ihlal edildi (m.7, m.9, m.12).
   Etki: 0 TL (henuz tutar belirlenmedi) ⇄ kalici risk
POZISYON: Ihtar gonder. · Sahip: Hukuk · Zaman: bu hafta · Beklenen: 10 gun yanit
GEREKCE: TBK m.117 ihtar zorunlulugu.

Tutarlilik denetimi: temiz.
"""

# Multi-line POZISYON (v2.19.1 — LLM dogal yaziminda Sahip/Zaman/Beklenen alt satirda)
# 16 Mayis 2026 5. davranissal kosumda gozlemlenen format — bilgi mevcut, satirlandirma farkli
MULTI_LINE_POZ_TEMIZ = """TESPIT: 14 acik fatura, anapara (kalan) 142.593 USD, gecikme 220-827 gun.
   Etki: 79K USD faiz (TTK m.1530) (%55 anapara ustu) ↑ aylik 3K USD birikim
POZISYON: Noter/KEP ihtarı 14 fatura + faiz + asgari giderim ile gonder
  Sahip: Hukuk | Zaman: 5 is gunu icinde | Beklenen: 30 gun icinde tahsilat veya icra
GEREKCE: TTK m.21/2 itiraz suresi gecmis, alacak kesinlesti.

Tutarlilik denetimi: temiz.
"""


class TestDogrulaMetin:
    def test_tam_temiz_rapor(self):
        s = dogrula_metin(TEMIZ_RAPOR)
        assert s["temiz"] is True
        assert s["tespit_count"] >= 1
        assert s["etki_count"] >= 1
        assert s["pozisyon_count"] >= 1
        assert s["pozisyon_5bilesen_count"] >= 1
        assert s["tutarlilik_denetimi_count"] == 1
        assert s["eksikler"] == []

    def test_tespit_eksik(self):
        s = dogrula_metin(EKSIK_TESPIT)
        assert s["temiz"] is False
        assert s["tespit_count"] == 0
        assert any("TESPIT" in e for e in s["eksikler"])

    def test_pozisyon_5bilesen_eksik(self):
        s = dogrula_metin(EKSIK_POZ_5BIL)
        # POZISYON: var ama Sahip/Zaman/Beklenen yok
        assert s["pozisyon_count"] >= 1
        assert s["pozisyon_5bilesen_count"] == 0
        assert any("POZISYON 5-bilesen" in e for e in s["eksikler"])
        assert s["temiz"] is False

    def test_anapara_etiket_eksik(self):
        s = dogrula_metin(EKSIK_ANAPARA_ETIKET)
        assert s["anapara_gecti"] is True
        assert s["anapara_etiket_count"] == 0
        assert any("Anapara etiketi" in e for e in s["eksikler"])
        assert s["temiz"] is False

    def test_tutarlilik_denetimi_eksik(self):
        s = dogrula_metin(EKSIK_TUTARLILIK)
        assert s["tutarlilik_denetimi_count"] == 0
        assert any("Tutarlilik denetimi" in e for e in s["eksikler"])
        assert s["temiz"] is False

    def test_tamamen_eksik_tum_sinyaller(self):
        s = dogrula_metin(TAMAMEN_EKSIK)
        # Eski format çıktısı — TUM sinyaller eksik
        assert s["tespit_count"] == 0
        assert s["etki_count"] == 0
        assert s["pozisyon_count"] == 0
        assert s["anapara_etiket_count"] == 0
        assert s["tutarlilik_denetimi_count"] == 0
        assert len(s["eksikler"]) == 5  # 5 zorunlu sinyalin hepsi
        assert s["temiz"] is False

    def test_anaparasiz_metin_temiz(self):
        # Anapara hic gecmiyorsa etiket gereksiz, diger sinyaller mevcut
        s = dogrula_metin(ANAPARASIZ_TEMIZ)
        assert s["anapara_gecti"] is False
        assert s["anapara_etiket_count"] == 0
        # anapara_etiket eksigi olmamali
        assert not any("Anapara etiketi" in e for e in s["eksikler"])
        assert s["temiz"] is True

    def test_multi_line_pozisyon_temiz(self):
        """v2.19.1 fix: LLM POZISYON: + Sahip/Zaman/Beklenen'i 2 satira yazabilir.
        Regex multi-line yakalamali, Exit 0 vermeli (16 Mayis 5. kosum gozlemi).
        """
        s = dogrula_metin(MULTI_LINE_POZ_TEMIZ)
        assert s["pozisyon_count"] >= 1
        assert s["pozisyon_5bilesen_count"] >= 1, (
            "Multi-line POZISYON 5-bilesen yakalanmali"
        )
        assert s["temiz"] is True

    def test_bos_metin(self):
        s = dogrula_metin("")
        assert s["temiz"] is False
        assert len(s["eksikler"]) >= 4  # TESPIT/Etki/POZISYON/Tutarlilik (anapara gecmedigi icin gereksiz)


class TestSinyalSayimlari:
    def test_coklu_tespit_pozisyon(self):
        metin = """TESPIT: A.
   Etki: 1
POZISYON: B. · Sahip: X · Zaman: Y · Beklenen: Z
GEREKCE: C.

TESPIT: D.
   Etki: 2
POZISYON: E. · Sahip: X · Zaman: Y · Beklenen: Z
GEREKCE: F.

Tutarlilik denetimi: temiz.
"""
        s = dogrula_metin(metin)
        assert s["tespit_count"] == 2
        assert s["pozisyon_count"] == 2
        assert s["pozisyon_5bilesen_count"] == 2
        assert s["temiz"] is True

    def test_denge_uyari_tetiklenir(self):
        # 2 TESPIT, 1 POZISYON — uyari beklenir
        metin = """TESPIT: A.
   Etki: 1
TESPIT: B.
   Etki: 2
POZISYON: C. · Sahip: X · Zaman: Y · Beklenen: Z

Tutarlilik denetimi: temiz.
"""
        s = dogrula_metin(metin)
        assert s["denge_uyari"] is not None
        assert "TESPIT count (2)" in s["denge_uyari"]


class TestTutarlilikDenetimiNotu:
    def test_temiz_notu(self):
        s = dogrula_metin("TESPIT: a\n   Etki: 1\nPOZISYON: b. · Sahip: X · Zaman: Y · Beklenen: Z\n\nTutarlilik denetimi: temiz.")
        assert s["tutarlilik_denetimi_count"] == 1

    def test_celiski_notu(self):
        s = dogrula_metin("TESPIT: a\n   Etki: 1\nPOZISYON: b. · Sahip: X · Zaman: Y · Beklenen: Z\n\nTutarlilik denetimi: 2 celiski bulundu, duzeltildi.")
        assert s["tutarlilik_denetimi_count"] == 1

    def test_bold_kapsami(self):
        # **Tutarlilik denetimi: temiz.** gibi markdown bold sarmalaması
        s = dogrula_metin("TESPIT: a\n   Etki: 1\nPOZISYON: b. · Sahip: X · Zaman: Y · Beklenen: Z\n\n**Tutarlilik denetimi: temiz.**")
        assert s["tutarlilik_denetimi_count"] == 1

    def test_buyuk_kucuk_harf(self):
        s = dogrula_metin("TUTARLILIK DENETIMI: temiz.")
        assert s["tutarlilik_denetimi_count"] == 1


class TestCli:
    def test_cli_temiz_metin_exit_0(self, tmp_path):
        f = tmp_path / "rapor.md"
        f.write_text(TEMIZ_RAPOR, encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(KIT_ROOT / "scripts" / "ragip_format_dogrula.py"), str(f)],
            capture_output=True, text=True,
        )
        assert r.returncode == 0
        assert "[TEMIZ]" in r.stdout

    def test_cli_eksik_metin_exit_2(self, tmp_path):
        f = tmp_path / "rapor.md"
        f.write_text(TAMAMEN_EKSIK, encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(KIT_ROOT / "scripts" / "ragip_format_dogrula.py"), str(f)],
            capture_output=True, text=True,
        )
        assert r.returncode == 2
        assert "EKSIK SINYAL" in r.stdout

    def test_cli_stdin(self):
        r = subprocess.run(
            [sys.executable, str(KIT_ROOT / "scripts" / "ragip_format_dogrula.py"), "-"],
            input=TEMIZ_RAPOR,
            capture_output=True, text=True,
        )
        assert r.returncode == 0

    def test_cli_json_format(self, tmp_path):
        f = tmp_path / "rapor.md"
        f.write_text(TEMIZ_RAPOR, encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(KIT_ROOT / "scripts" / "ragip_format_dogrula.py"), "--json", str(f)],
            capture_output=True, text=True,
        )
        assert r.returncode == 0
        out = json.loads(r.stdout)
        assert out["temiz"] is True
        assert out["tespit_count"] >= 1

    def test_cli_eksik_dosya_exit_1(self, tmp_path):
        r = subprocess.run(
            [sys.executable, str(KIT_ROOT / "scripts" / "ragip_format_dogrula.py"), str(tmp_path / "yok.md")],
            capture_output=True, text=True,
        )
        assert r.returncode == 1


class TestBashWrapper:
    def test_bash_temiz_metin(self, tmp_path):
        f = tmp_path / "rapor.md"
        f.write_text(TEMIZ_RAPOR, encoding="utf-8")
        r = subprocess.run(
            ["bash", str(KIT_ROOT / "scripts" / "ragip_format_dogrula.sh"), str(f)],
            capture_output=True, text=True,
        )
        assert r.returncode == 0
        assert "[TEMIZ]" in r.stdout

    def test_bash_eksik_metin(self, tmp_path):
        f = tmp_path / "rapor.md"
        f.write_text(TAMAMEN_EKSIK, encoding="utf-8")
        r = subprocess.run(
            ["bash", str(KIT_ROOT / "scripts" / "ragip_format_dogrula.sh"), str(f)],
            capture_output=True, text=True,
        )
        assert r.returncode == 2


class TestGercekCiktilarRegression:
    """Audit'in bulgu noktasi — 3 yazili kosumda 5/5 eksik olmali."""

    @pytest.mark.parametrize("cikti_yolu", [
        "data/RAGIP_AGA/ciktilar/guven_pres_dokum/2026-05/20260514_091852-hukuk-degerlendirme-guven_pres_dokum.md",
    ])
    def test_v216_eski_kosum_format_eksik(self, cikti_yolu):
        dosya = KIT_ROOT / cikti_yolu
        if not dosya.exists():
            pytest.skip(f"Test fixture yok: {cikti_yolu}")
        s = dogrula_metin(dosya.read_text(encoding="utf-8"))
        # v2.16.0 koşumu Tier 3 blok format kullanmiyor — Exit 2 beklenir
        assert s["temiz"] is False
        assert s["tespit_count"] == 0
        assert s["pozisyon_count"] == 0
