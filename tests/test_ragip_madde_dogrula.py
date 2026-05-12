"""ragip_madde_dogrula.py testleri — yasal madde referans dogrulama."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

KIT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT_ROOT / "scripts"))

from ragip_madde_dogrula import (  # noqa: E402
    DEFAULT_KANUN_JSON,
    dogrula_metin,
    madde_var_mi,
    referanslari_cikar,
    _normalize_kanun_kod,
)


@pytest.fixture(scope="module")
def kanunlar():
    with open(DEFAULT_KANUN_JSON, encoding="utf-8") as f:
        return json.load(f)["kanunlar"]


class TestKanunMaddeleriJson:
    def test_dosya_var(self):
        assert DEFAULT_KANUN_JSON.exists()

    def test_json_gecerli(self):
        with open(DEFAULT_KANUN_JSON, encoding="utf-8") as f:
            data = json.load(f)
        assert "kanunlar" in data
        assert isinstance(data["kanunlar"], dict)

    def test_temel_kanunlar_var(self, kanunlar):
        for kod in ("TBK", "TTK", "IIK", "KVKK", "HMK"):
            assert kod in kanunlar, f"{kod} JSON'da eksik"

    def test_skilllerden_referans_alinan_maddeler(self, kanunlar):
        # SKILL.md dosyalarinda referans verilen maddeler JSON'da olmali
        beklenen = [
            ("TBK", "117"), ("TBK", "118"), ("TBK", "119"), ("TBK", "120"),
            ("TBK", "146"), ("TBK", "147"), ("TBK", "207"), ("TBK", "475"),
            ("TBK", "112"), ("TBK", "49"),
            ("TTK", "21"), ("TTK", "23"), ("TTK", "1530"),
            ("IIK", "58"), ("IIK", "68"), ("IIK", "167"),
            ("KVKK", "5"), ("KVKK", "11"), ("KVKK", "13"), ("KVKK", "14"),
            ("HMK", "199"), ("HMK", "200"),
        ]
        for kanun, madde in beklenen:
            assert madde in kanunlar[kanun]["maddeler"], f"{kanun} m.{madde} JSON'da eksik"


class TestNormalize:
    def test_iik_turkish_to_latin(self):
        assert _normalize_kanun_kod("İİK") == "IIK"

    def test_zaten_latin(self):
        assert _normalize_kanun_kod("TBK") == "TBK"

    def test_kucuk_harfle_buyutme(self):
        assert _normalize_kanun_kod("tbk") == "TBK"


class TestMaddeVarMi:
    def test_var(self, kanunlar):
        assert madde_var_mi("TBK", "117", kanunlar) is True
        assert madde_var_mi("TTK", "21", kanunlar) is True
        assert madde_var_mi("KVKK", "5", kanunlar) is True

    def test_yok(self, kanunlar):
        assert madde_var_mi("TBK", "999", kanunlar) is False
        assert madde_var_mi("TBK", "888", kanunlar) is False

    def test_bilinmeyen_kanun(self, kanunlar):
        assert madde_var_mi("TCK", "207", kanunlar) is False
        assert madde_var_mi("UYDURMA", "1", kanunlar) is False

    def test_iik_normalize(self, kanunlar):
        # İİK girişi de IIK'e normalize edilmeli
        assert madde_var_mi("İİK", "58", kanunlar) is True


class TestReferanslariCikar:
    def test_tek_madde(self):
        r = referanslari_cikar("TBK m.117 uyarinca temerrut.")
        assert len(r) == 1
        assert r[0]["kanun"] == "TBK"
        assert r[0]["madde"] == "117"
        assert r[0]["fikra"] is None
        assert r[0]["range"] is False

    def test_fikra(self):
        r = referanslari_cikar("TTK m.21/2 fatura itirazi.")
        assert len(r) == 1
        assert r[0]["kanun"] == "TTK"
        assert r[0]["madde"] == "21"
        assert r[0]["fikra"] == "2"

    def test_fikra_ve_bent(self):
        r = referanslari_cikar("TTK m.23/1-c ticari satis.")
        assert len(r) == 1
        assert r[0]["fikra"] == "1"
        assert r[0]["bent"] == "c"

    def test_madde_kelimesi(self):
        r = referanslari_cikar("TBK madde 117 uyarinca.")
        assert len(r) == 1
        assert r[0]["madde"] == "117"

    def test_range_genisletilir(self):
        r = referanslari_cikar("TBK m.117-120 temerrut hukumleri.")
        assert len(r) == 4
        maddeler = [x["madde"] for x in r]
        assert maddeler == ["117", "118", "119", "120"]
        assert all(x["range"] is True for x in r)

    def test_range_bozuk_tek_madde_olur(self):
        # m.999-1 (bitis<baslangic): tek madde olarak
        r = referanslari_cikar("TBK m.999-1 hatali.")
        assert len(r) == 1
        assert r[0]["madde"] == "999"
        assert r[0]["range"] is False

    def test_coklu_referans(self):
        r = referanslari_cikar("TBK m.117, TTK m.21, IIK m.58 cesitli.")
        assert len(r) == 3
        kanunlar = [x["kanun"] for x in r]
        assert "TBK" in kanunlar and "TTK" in kanunlar and "IIK" in kanunlar

    def test_iik_turkish_karakter(self):
        r = referanslari_cikar("İİK m.58 takip.")
        assert len(r) == 1
        assert r[0]["kanun"] == "IIK"
        assert r[0]["madde"] == "58"

    def test_referans_yok(self):
        r = referanslari_cikar("Bu metinde hicbir madde yok.")
        assert r == []

    def test_bos_metin(self):
        assert referanslari_cikar("") == []


class TestDogrulaMetin:
    def test_temiz_metin(self):
        s = dogrula_metin("TBK m.117 uyarinca temerrut hukumleri.")
        assert s["dogrulanan"] == 1
        assert s["uydurma_sanigi"] == 0
        assert s["bilinmeyen_kanun"] == 0

    def test_uydurma_madde(self):
        s = dogrula_metin("TBK m.999 (uydurma) ile karari ver.")
        assert s["uydurma_sanigi"] == 1
        assert s["uydurma_sanigi_detay"][0]["madde"] == "999"

    def test_bilinmeyen_kanun(self):
        s = dogrula_metin("TCK m.207 scope disi.")
        assert s["bilinmeyen_kanun"] == 1
        assert s["dogrulanan"] == 0
        assert s["uydurma_sanigi"] == 0

    def test_karisik(self):
        metin = """
        TBK m.117 (gercek) + TTK m.21/2 (gercek) + TBK m.999 (uydurma)
        + TCK m.207 (scope disi).
        """
        s = dogrula_metin(metin)
        assert s["dogrulanan"] == 2
        assert s["uydurma_sanigi"] == 1
        assert s["bilinmeyen_kanun"] == 1

    def test_range_tum_maddeler_dogrulanir(self):
        s = dogrula_metin("TBK m.117-120 temerrut hukumleri.")
        assert s["dogrulanan"] == 4
        assert s["uydurma_sanigi"] == 0

    def test_referans_yok_temiz(self):
        s = dogrula_metin("Bu metinde hicbir referans yok.")
        assert s["toplam_referans"] == 0
        assert s["dogrulanan"] == 0


class TestCli:
    def test_cli_dosya_okur_temiz(self, tmp_path):
        f = tmp_path / "rapor.md"
        f.write_text("TBK m.117 ile temerrut.", encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(KIT_ROOT / "scripts" / "ragip_madde_dogrula.py"), str(f)],
            capture_output=True, text=True,
        )
        assert r.returncode == 0
        assert "Dogrulanan:         1" in r.stdout

    def test_cli_uydurma_exit_2(self, tmp_path):
        f = tmp_path / "rapor.md"
        f.write_text("TBK m.999 uydurma madde.", encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(KIT_ROOT / "scripts" / "ragip_madde_dogrula.py"), str(f)],
            capture_output=True, text=True,
        )
        assert r.returncode == 2
        assert "UYDURMA SANIGI" in r.stdout

    def test_cli_stdin(self):
        r = subprocess.run(
            [sys.executable, str(KIT_ROOT / "scripts" / "ragip_madde_dogrula.py"), "-"],
            input="TBK m.117 temerrut.",
            capture_output=True, text=True,
        )
        assert r.returncode == 0

    def test_cli_json_format(self, tmp_path):
        f = tmp_path / "rapor.md"
        f.write_text("TBK m.117 ile.", encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(KIT_ROOT / "scripts" / "ragip_madde_dogrula.py"), "--json", str(f)],
            capture_output=True, text=True,
        )
        assert r.returncode == 0
        out = json.loads(r.stdout)
        assert out["dogrulanan"] == 1

    def test_cli_eksik_dosya_exit_1(self, tmp_path):
        r = subprocess.run(
            [sys.executable, str(KIT_ROOT / "scripts" / "ragip_madde_dogrula.py"), str(tmp_path / "yok.md")],
            capture_output=True, text=True,
        )
        assert r.returncode == 1


class TestBashWrapper:
    def test_bash_wrapper_calisir(self, tmp_path):
        f = tmp_path / "rapor.md"
        f.write_text("TBK m.117 temerrut.", encoding="utf-8")
        r = subprocess.run(
            ["bash", str(KIT_ROOT / "scripts" / "ragip_madde_dogrula.sh"), str(f)],
            capture_output=True, text=True,
        )
        assert r.returncode == 0
        assert "Dogrulanan:         1" in r.stdout


class TestPortability:
    def test_kit_root_dogru_cozulur(self):
        # ragip_madde_dogrula.py kit root'u dogru cozmeli (DEFAULT_KANUN_JSON erisilebilir)
        assert DEFAULT_KANUN_JSON.is_file()
        assert DEFAULT_KANUN_JSON.name == "kanun_maddeleri.json"
