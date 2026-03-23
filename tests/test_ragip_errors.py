"""ragip_errors.py testleri — yapilandirilmis hata siniflandirmasi."""
import sys
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from ragip_errors import HataTuru, RagipHata, siniflandir, tekrar_denenebilir


class TestHataTuru:
    """Enum degerleri."""

    def test_gecici(self):
        assert HataTuru.GECICI.value == "gecici"

    def test_kalici(self):
        assert HataTuru.KALICI.value == "kalici"

    def test_politika(self):
        assert HataTuru.POLITIKA.value == "politika"

    def test_uc_kategori(self):
        assert len(HataTuru) == 3


class TestRagipHata:
    """RagipHata exception sinifi."""

    def test_exception_subclass(self):
        assert issubclass(RagipHata, Exception)

    def test_varsayilan_tur_kalici(self):
        h = RagipHata("test")
        assert h.tur == HataTuru.KALICI

    def test_tur_atamasi(self):
        h = RagipHata("ag hatasi", tur=HataTuru.GECICI)
        assert h.tur == HataTuru.GECICI

    def test_kaynak(self):
        h = RagipHata("hata", kaynak="rates")
        assert h.kaynak == "rates"

    def test_orijinal_exception(self):
        orijinal = ValueError("gecersiz deger")
        h = RagipHata("sarmalama", orijinal=orijinal)
        assert h.orijinal is orijinal

    def test_mesaj(self):
        h = RagipHata("test mesaji")
        assert str(h) == "test mesaji"

    def test_raise_catch(self):
        try:
            raise RagipHata("test", tur=HataTuru.POLITIKA, kaynak="crud")
        except RagipHata as e:
            assert e.tur == HataTuru.POLITIKA
            assert e.kaynak == "crud"
        except Exception:
            assert False, "RagipHata Exception olarak yakalanmali"

    def test_catch_as_exception(self):
        """RagipHata genel Exception catch ile de yakalanir."""
        try:
            raise RagipHata("test")
        except Exception as e:
            assert isinstance(e, RagipHata)


class TestSiniflandir:
    """siniflandir() — exception → HataTuru esleme."""

    def test_value_error_kalici(self):
        assert siniflandir(ValueError("x")) == HataTuru.KALICI

    def test_key_error_kalici(self):
        assert siniflandir(KeyError("x")) == HataTuru.KALICI

    def test_type_error_kalici(self):
        assert siniflandir(TypeError("x")) == HataTuru.KALICI

    def test_connection_error_gecici(self):
        assert siniflandir(ConnectionError("x")) == HataTuru.GECICI

    def test_timeout_error_gecici(self):
        assert siniflandir(TimeoutError("x")) == HataTuru.GECICI

    def test_os_error_gecici(self):
        assert siniflandir(OSError("disk")) == HataTuru.GECICI

    def test_url_error_gecici(self):
        assert siniflandir(urllib.error.URLError("ag")) == HataTuru.GECICI

    def test_ragip_hata_passthrough(self):
        h = RagipHata("test", tur=HataTuru.POLITIKA)
        assert siniflandir(h) == HataTuru.POLITIKA

    def test_ragip_hata_gecici(self):
        h = RagipHata("test", tur=HataTuru.GECICI)
        assert siniflandir(h) == HataTuru.GECICI

    def test_bilinmeyen_varsayilan_kalici(self):
        """Tanimlanmamis exception tipi → KALICI."""
        assert siniflandir(RuntimeError("x")) == HataTuru.KALICI

    def test_attribute_error_kalici(self):
        assert siniflandir(AttributeError("x")) == HataTuru.KALICI


class TestTekrarDenenebilir:
    """tekrar_denenebilir() — retry karari."""

    def test_gecici_true(self):
        assert tekrar_denenebilir(ConnectionError("x")) is True

    def test_timeout_true(self):
        assert tekrar_denenebilir(TimeoutError("x")) is True

    def test_url_error_true(self):
        assert tekrar_denenebilir(urllib.error.URLError("x")) is True

    def test_os_error_true(self):
        assert tekrar_denenebilir(OSError("disk")) is True

    def test_kalici_false(self):
        assert tekrar_denenebilir(ValueError("x")) is False

    def test_politika_false(self):
        h = RagipHata("schema", tur=HataTuru.POLITIKA)
        assert tekrar_denenebilir(h) is False

    def test_kalici_ragip_hata_false(self):
        h = RagipHata("veri", tur=HataTuru.KALICI)
        assert tekrar_denenebilir(h) is False

    def test_gecici_ragip_hata_true(self):
        h = RagipHata("ag", tur=HataTuru.GECICI)
        assert tekrar_denenebilir(h) is True
