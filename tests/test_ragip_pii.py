"""ragip_pii.py testleri — PII temizleme (maskeleme + hash'leme)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from ragip_pii import metin_temizle, kayit_temizle, _hash_deger, _ORTA_ALANLAR


class TestMetinTemizle:
    """Yuksek riskli PII maskeleme."""

    def test_email(self):
        assert "***EMAIL***" in metin_temizle("ahmet@firma.com.tr")

    def test_email_metin_icinde(self):
        sonuc = metin_temizle("Gorusme: ali.veli@example.org sonrasi")
        assert "ali.veli@example.org" not in sonuc
        assert "***EMAIL***" in sonuc
        assert "Gorusme:" in sonuc

    def test_telefon_05xx(self):
        assert "***TEL***" in metin_temizle("Tel: 0532 123 45 67")

    def test_telefon_plus90(self):
        assert "***TEL***" in metin_temizle("+90 532 123 45 67")

    def test_telefon_bitisik(self):
        assert "***TEL***" in metin_temizle("05321234567")

    def test_tckn(self):
        assert "***TCKN***" in metin_temizle("TC: 12345678901")

    def test_iban(self):
        assert "***IBAN***" in metin_temizle("TR33 0006 1005 1978 6457 8413 26")

    def test_karisik_metin(self):
        metin = "Ahmet Bey ahmet@firma.com 0532 123 45 67 TC:12345678901"
        sonuc = metin_temizle(metin)
        assert "***EMAIL***" in sonuc
        assert "***TEL***" in sonuc
        assert "***TCKN***" in sonuc
        assert "Ahmet Bey" in sonuc

    def test_pii_olmayan_metin(self):
        metin = "Fatura tutari 15000 TL vade 30 gun"
        assert metin_temizle(metin) == metin

    def test_bos_metin(self):
        assert metin_temizle("") == ""

    def test_none(self):
        assert metin_temizle(None) is None

    def test_sayi_girdi(self):
        assert metin_temizle(12345) == 12345


class TestHashDeger:
    """SHA-256 hash fonksiyonu."""

    def test_deterministik(self):
        assert _hash_deger("Geneks Kimya") == _hash_deger("Geneks Kimya")

    def test_farkli_girdi_farkli_hash(self):
        assert _hash_deger("Firma A") != _hash_deger("Firma B")

    def test_format(self):
        h = _hash_deger("test")
        assert h.startswith("h:")
        assert len(h) == 10  # "h:" + 8 hex karakter

    def test_geri_donusturulemez(self):
        h = _hash_deger("Geneks Kimya")
        assert "Geneks" not in h
        assert "Kimya" not in h


class TestKayitTemizle:
    """Dict kayit temizleme."""

    def test_firma_hashlenir(self):
        kayit = {"firma": "Geneks Kimya", "agent": "hesap"}
        temiz = kayit_temizle(kayit)
        assert temiz["firma"].startswith("h:")
        assert temiz["agent"] == "hesap"  # degismez

    def test_firma_slug_hashlenir(self):
        kayit = {"firma_slug": "geneks_kimya", "skill": "rapor"}
        temiz = kayit_temizle(kayit)
        assert temiz["firma_slug"].startswith("h:")
        assert temiz["skill"] == "rapor"

    def test_email_string_alanlarda_maskelenir(self):
        kayit = {"aciklama": "Ilgili: test@mail.com", "tutar": 5000}
        temiz = kayit_temizle(kayit)
        assert "***EMAIL***" in temiz["aciklama"]
        assert temiz["tutar"] == 5000

    def test_orijinal_degismez(self):
        kayit = {"firma": "Test Firma"}
        kayit_temizle(kayit)
        assert kayit["firma"] == "Test Firma"

    def test_bos_string_hash_olmaz(self):
        kayit = {"firma": "", "agent": "veri"}
        temiz = kayit_temizle(kayit)
        assert temiz["firma"] == ""

    def test_sayi_degeri_gecir(self):
        kayit = {"boyut": 1234, "firma": "X"}
        temiz = kayit_temizle(kayit)
        assert temiz["boyut"] == 1234

    def test_ozel_orta_alanlar(self):
        kayit = {"ozel_alan": "gizli", "normal": "gorunur"}
        temiz = kayit_temizle(kayit, orta_alanlar={"ozel_alan"})
        assert temiz["ozel_alan"].startswith("h:")
        assert temiz["normal"] == "gorunur"

    def test_none_girdi(self):
        assert kayit_temizle(None) is None

    def test_tum_orta_alanlar(self):
        """_ORTA_ALANLAR setindeki tum alanlar hash'lenir."""
        kayit = {alan: f"deger_{alan}" for alan in _ORTA_ALANLAR}
        temiz = kayit_temizle(kayit)
        for alan in _ORTA_ALANLAR:
            assert temiz[alan].startswith("h:"), f"{alan} hash'lenmedi"
