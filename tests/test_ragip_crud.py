"""
ragip_crud.py — Paylaşımlı CRUD yardımcı fonksiyonları unit testleri.
"""
import json
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from ragip_crud import (parse_kv, load_jsonl, save_jsonl, load_json, save_json,
                        next_id, today, validate_fatura, validate_faturalar)


class TestParseKv:
    def test_basic(self):
        assert parse_kv("a=1 b=2") == {"a": "1", "b": "2"}

    def test_empty(self):
        assert parse_kv("") == {}

    def test_equals_in_value(self):
        result = parse_kv("url=http://a=b")
        assert result == {"url": "http://a=b"}

    def test_no_equals(self):
        """Eşittir işareti olmayan parçalar atlanır."""
        assert parse_kv("hello world") == {}

    def test_mixed(self):
        result = parse_kv("firma ABC oran=3.5 vade=60")
        assert result == {"oran": "3.5", "vade": "60"}


class TestJsonl:
    def test_load_save_roundtrip(self, tmp_path):
        dosya = tmp_path / "test.jsonl"
        records = [
            {"id": "1", "ad": "ABC"},
            {"id": "2", "ad": "DEF"},
            {"id": "3", "ad": "GHI"},
        ]
        save_jsonl(dosya, records)
        loaded = load_jsonl(dosya)
        assert loaded == records

    def test_save_atomic(self, tmp_path):
        """Yazma sırasında .tmp dosya kullanılır, sonuçta kalmaz."""
        dosya = tmp_path / "test.jsonl"
        save_jsonl(dosya, [{"id": "1"}])
        tmp_file = dosya.with_suffix(".tmp")
        assert not tmp_file.exists(), ".tmp dosya kalmamalı"
        assert dosya.exists()

    def test_load_missing_file(self, tmp_path):
        dosya = tmp_path / "nonexistent.jsonl"
        assert load_jsonl(dosya) == []

    def test_load_empty_file(self, tmp_path):
        dosya = tmp_path / "empty.jsonl"
        dosya.write_text("", "utf-8")
        assert load_jsonl(dosya) == []

    def test_turkish_chars(self, tmp_path):
        dosya = tmp_path / "turkish.jsonl"
        records = [{"ad": "Öğüş Dağıtım", "not": "çok güzel"}]
        save_jsonl(dosya, records)
        loaded = load_jsonl(dosya)
        assert loaded[0]["ad"] == "Öğüş Dağıtım"


class TestJson:
    def test_load_save_roundtrip(self, tmp_path):
        dosya = tmp_path / "test.json"
        data = {"firma_adi": "Test A.Ş.", "sektor": "teknoloji"}
        save_json(dosya, data)
        loaded = load_json(dosya)
        assert loaded == data

    def test_load_missing(self, tmp_path):
        dosya = tmp_path / "nonexistent.json"
        assert load_json(dosya) is None

    def test_save_atomic(self, tmp_path):
        dosya = tmp_path / "test.json"
        save_json(dosya, {"a": 1})
        tmp_file = dosya.with_suffix(".tmp")
        assert not tmp_file.exists()
        assert dosya.exists()


class TestNextId:
    def test_basic(self):
        records = [{"id": "1"}, {"id": "3"}]
        assert next_id(records) == 4

    def test_empty(self):
        assert next_id([]) == 1

    def test_string_ids(self):
        records = [{"id": "5"}, {"id": "2"}, {"id": "10"}]
        assert next_id(records) == 11


class TestToday:
    def test_format(self):
        result = today()
        # YYYY-MM-DD format
        assert len(result) == 10
        assert result[4] == "-"
        assert result[7] == "-"


# --- Fatura Validasyon Testleri (ADR-0007) ---

def _gecerli_fatura(**overrides):
    """Geçerli bir fatura kaydı oluşturur, overrides ile alan değiştirilebilir."""
    base = {
        "id": 1, "fatura_no": "FT-001", "firma_id": 10,
        "yon": "alacak", "tutar": 1000.0, "toplam": 1200.0,
        "fatura_tarihi": "2026-01-15", "vade_tarihi": "2026-02-15",
        "durum": "acik"
    }
    base.update(overrides)
    return base


class TestValidateFatura:
    """validate_fatura() — ADR-0007 şema doğrulaması."""

    def test_gecerli_kayit(self):
        assert validate_fatura(_gecerli_fatura()) == []

    def test_gecerli_tum_alanlar(self):
        """Tüm opsiyonel alanlar dahil geçerli kayıt."""
        f = _gecerli_fatura(
            kdv_oran_pct=20.0, kdv_tutar=200.0, para_birimi="TRY",
            odeme_tarihi="2026-02-10", odeme_tutari=1200.0,
            durum="odendi", kategori="hizmet", kaynak="parasut",
            aciklama="Test faturası"
        )
        assert validate_fatura(f) == []

    def test_zorunlu_alan_eksik(self):
        f = _gecerli_fatura()
        del f["firma_id"]
        hatalar = validate_fatura(f)
        assert any("firma_id" in h for h in hatalar)

    def test_birden_fazla_zorunlu_alan_eksik(self):
        f = _gecerli_fatura()
        del f["yon"]
        del f["durum"]
        hatalar = validate_fatura(f)
        assert len(hatalar) >= 2

    def test_gecersiz_yon(self):
        hatalar = validate_fatura(_gecerli_fatura(yon="gelir"))
        assert any("yon" in h for h in hatalar)

    def test_gecersiz_durum(self):
        hatalar = validate_fatura(_gecerli_fatura(durum="beklemede"))
        assert any("durum" in h for h in hatalar)

    def test_tutar_string_hatasi(self):
        hatalar = validate_fatura(_gecerli_fatura(tutar="1000"))
        assert any("tutar" in h and "sayisal" in h for h in hatalar)

    def test_toplam_string_hatasi(self):
        hatalar = validate_fatura(_gecerli_fatura(toplam="1200"))
        assert any("toplam" in h and "sayisal" in h for h in hatalar)

    def test_tarih_format_hatasi(self):
        hatalar = validate_fatura(_gecerli_fatura(fatura_tarihi="15/01/2026"))
        assert any("fatura_tarihi" in h for h in hatalar)

    def test_vade_tarihi_format_hatasi(self):
        hatalar = validate_fatura(_gecerli_fatura(vade_tarihi="2026-1-5"))
        assert any("vade_tarihi" in h for h in hatalar)

    def test_odeme_tutari_string_hatasi(self):
        hatalar = validate_fatura(_gecerli_fatura(odeme_tutari="500"))
        assert any("odeme_tutari" in h for h in hatalar)

    def test_odeme_tarihi_format_hatasi(self):
        hatalar = validate_fatura(_gecerli_fatura(odeme_tarihi="2026/02/10"))
        assert any("odeme_tarihi" in h for h in hatalar)

    def test_para_birimi_gecersiz(self):
        hatalar = validate_fatura(_gecerli_fatura(para_birimi="TRYY"))
        assert any("para_birimi" in h for h in hatalar)

    # --- Doviz kuru validasyonu (ADR-0007 guncelleme 2026-03-22) ---

    def test_fatura_kuru_gecerli(self):
        """Pozitif fatura_kuru gecerli olmali."""
        assert validate_fatura(_gecerli_fatura(fatura_kuru=30.6)) == []

    def test_fatura_kuru_null_gecerli(self):
        """fatura_kuru=null (TRY fatura) gecerli olmali."""
        assert validate_fatura(_gecerli_fatura(fatura_kuru=None)) == []

    def test_fatura_kuru_sifir_hatasi(self):
        """fatura_kuru=0 hata vermeli."""
        hatalar = validate_fatura(_gecerli_fatura(fatura_kuru=0))
        assert any("fatura_kuru" in h and "pozitif" in h for h in hatalar)

    def test_fatura_kuru_negatif_hatasi(self):
        """fatura_kuru negatif hata vermeli."""
        hatalar = validate_fatura(_gecerli_fatura(fatura_kuru=-10.5))
        assert any("fatura_kuru" in h and "pozitif" in h for h in hatalar)

    def test_fatura_kuru_string_hatasi(self):
        """fatura_kuru string hata vermeli."""
        hatalar = validate_fatura(_gecerli_fatura(fatura_kuru="30.6"))
        assert any("fatura_kuru" in h and "sayisal" in h for h in hatalar)

    def test_odeme_kuru_gecerli(self):
        """Pozitif odeme_kuru gecerli olmali."""
        assert validate_fatura(_gecerli_fatura(odeme_kuru=32.1)) == []

    def test_odeme_kuru_null_gecerli(self):
        """odeme_kuru=null gecerli olmali."""
        assert validate_fatura(_gecerli_fatura(odeme_kuru=None)) == []

    def test_odeme_kuru_negatif_hatasi(self):
        """odeme_kuru negatif hata vermeli."""
        hatalar = validate_fatura(_gecerli_fatura(odeme_kuru=-1.0))
        assert any("odeme_kuru" in h and "pozitif" in h for h in hatalar)

    def test_kismi_odeme_tutari_eksik(self):
        hatalar = validate_fatura(_gecerli_fatura(durum="kismi"))
        assert any("kismi" in h and "odeme_tutari" in h for h in hatalar)

    def test_kismi_odeme_tutari_buyuk(self):
        hatalar = validate_fatura(_gecerli_fatura(durum="kismi", odeme_tutari=1500.0))
        assert any("kismi" in h and "odeme_tutari" in h for h in hatalar)

    def test_kismi_odeme_dogru(self):
        f = _gecerli_fatura(durum="kismi", odeme_tutari=600.0)
        assert validate_fatura(f) == []

    def test_int_tutar_gecerli(self):
        """int tipi de kabul edilmeli (1000 vs 1000.0)."""
        assert validate_fatura(_gecerli_fatura(tutar=1000, toplam=1200)) == []

    def test_firma_id_int_gecerli(self):
        """firma_id int kabul edilmeli."""
        assert validate_fatura(_gecerli_fatura(firma_id=10)) == []

    def test_firma_id_str_gecerli(self):
        """firma_id string (GUID) kabul edilmeli — D365 gibi ERP'lerden gelir."""
        assert validate_fatura(_gecerli_fatura(firma_id="a1b2c3d4-e5f6-7890")) == []

    def test_firma_id_gecersiz_tip(self):
        """firma_id ne int ne str ise hata vermeli."""
        hatalar = validate_fatura(_gecerli_fatura(firma_id=[10]))
        assert any("firma_id" in h for h in hatalar)


class TestValidateFaturalar:
    """validate_faturalar() — toplu doğrulama."""

    def test_tumu_gecerli(self):
        kayitlar = [_gecerli_fatura(id=i) for i in range(1, 4)]
        gecerli, hatali = validate_faturalar(kayitlar)
        assert len(gecerli) == 3
        assert len(hatali) == 0

    def test_karisik(self):
        kayitlar = [
            _gecerli_fatura(id=1),
            _gecerli_fatura(id=2, yon="YANLIS"),
            _gecerli_fatura(id=3),
        ]
        gecerli, hatali = validate_faturalar(kayitlar)
        assert len(gecerli) == 2
        assert len(hatali) == 1
        assert "_hatalar" in hatali[0]

    def test_bos_liste(self):
        gecerli, hatali = validate_faturalar([])
        assert gecerli == []
        assert hatali == []

    def test_orijinal_degismez(self):
        """Orijinal kayıt mutate edilmemeli."""
        kayit = _gecerli_fatura(yon="HATALI")
        validate_faturalar([kayit])
        assert "_hatalar" not in kayit
