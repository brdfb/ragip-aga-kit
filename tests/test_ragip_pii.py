"""ragip_pii.py testleri — PII temizleme (maskeleme + hash'leme + geri donusturulabilir)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from ragip_pii import (metin_temizle, kayit_temizle, _hash_deger, _ORTA_ALANLAR,
                        maskele_geri_donusturulabilir, geri_cevir)


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


# ── Geri donusturulabilir maskeleme ──────────────────────────────────────


class TestMaskeleGeriDonusturulabilir:
    """maskele_geri_donusturulabilir() + geri_cevir() testleri."""

    def test_firma_adlari_maskelenir(self):
        metin = "Gibibyte ile ABC Holding arasinda sozlesme"
        masked, mapping = maskele_geri_donusturulabilir(
            metin, firma_adlari=["Gibibyte", "ABC Holding"]
        )
        assert "Gibibyte" not in masked
        assert "ABC Holding" not in masked
        assert "[FIRMA_1]" in masked
        assert "[FIRMA_2]" in masked
        # En uzun firma adi once maskelenir (greedy match)
        assert mapping["[FIRMA_1]"] == "ABC Holding"
        assert mapping["[FIRMA_2]"] == "Gibibyte"

    def test_geri_cevirme(self):
        metin = "Gibibyte ile ABC Holding arasinda sozlesme"
        masked, mapping = maskele_geri_donusturulabilir(
            metin, firma_adlari=["Gibibyte", "ABC Holding"]
        )
        geri = geri_cevir(masked, mapping)
        assert geri == metin

    def test_email_maskelenir(self):
        metin = "Ilgili kisi: ahmet@gibibyte.com.tr"
        masked, mapping = maskele_geri_donusturulabilir(metin)
        assert "ahmet@gibibyte.com.tr" not in masked
        assert "[EMAIL_1]" in masked
        assert mapping["[EMAIL_1]"] == "ahmet@gibibyte.com.tr"

    def test_telefon_maskelenir(self):
        metin = "Tel: 0532 123 45 67"
        masked, mapping = maskele_geri_donusturulabilir(metin)
        assert "0532" not in masked
        assert "[TEL_1]" in masked

    def test_tckn_maskelenir(self):
        metin = "TC Kimlik: 12345678901"
        masked, mapping = maskele_geri_donusturulabilir(metin)
        assert "12345678901" not in masked
        assert "[TCKN_1]" in masked

    def test_iban_maskelenir(self):
        metin = "IBAN: TR33 0006 1005 1978 6457 8413 26"
        masked, mapping = maskele_geri_donusturulabilir(metin)
        assert "TR33" not in masked
        assert "[IBAN_1]" in masked

    def test_tutar_maskelenir(self):
        metin = "Sozlesme bedeli 500.000 TL olarak belirlenmistir"
        masked, mapping = maskele_geri_donusturulabilir(metin)
        assert "500.000 TL" not in masked
        assert "[TUTAR_1]" in masked

    def test_tarih_maskelenir(self):
        metin = "Baslangic tarihi 27.03.2026 bitis 27.03.2027"
        masked, mapping = maskele_geri_donusturulabilir(metin)
        assert "27.03.2026" not in masked
        assert "[TARIH_1]" in masked
        assert "[TARIH_2]" in masked

    def test_iso_tarih_maskelenir(self):
        metin = "tarih: 2026-03-27"
        masked, mapping = maskele_geri_donusturulabilir(metin)
        assert "2026-03-27" not in masked

    def test_kisi_adlari_maskelenir(self):
        metin = "Yetkili: Ahmet Yilmaz"
        masked, mapping = maskele_geri_donusturulabilir(
            metin, kisi_adlari=["Ahmet Yilmaz"]
        )
        assert "Ahmet Yilmaz" not in masked
        assert "[KISI_1]" in masked

    def test_karisik_metin_tam_dongu(self):
        """Tum PII turleri maskelenip geri cevrilebilir."""
        metin = (
            "Gibibyte Bilisim ile Guven Pres arasinda 15.03.2026 tarihinde "
            "250.000 TL tutarinda hizmet sozlesmesi imzalanmistir. "
            "Ilgili: veli@guven.com Tel: 0532 987 65 43"
        )
        masked, mapping = maskele_geri_donusturulabilir(
            metin,
            firma_adlari=["Gibibyte Bilisim", "Guven Pres"]
        )
        # Hassas bilgiler maskelenmis olmali
        assert "Gibibyte Bilisim" not in masked
        assert "Guven Pres" not in masked
        assert "veli@guven.com" not in masked
        # Geri cevirme calismali
        geri = geri_cevir(masked, mapping)
        assert "Gibibyte Bilisim" in geri
        assert "Guven Pres" in geri
        assert "veli@guven.com" in geri

    def test_bos_metin(self):
        masked, mapping = maskele_geri_donusturulabilir("")
        assert masked == ""
        assert mapping == {}

    def test_none_metin(self):
        masked, mapping = maskele_geri_donusturulabilir(None)
        assert masked is None
        assert mapping == {}

    def test_pii_olmayan_metin(self):
        metin = "Bu sozlesme iki taraf arasinda gecerlidir"
        masked, mapping = maskele_geri_donusturulabilir(metin)
        assert masked == metin
        assert mapping == {}

    def test_mapping_deterministik(self):
        """Ayni girdi ayni mapping uretir."""
        metin = "Gibibyte sozlesmesi"
        m1, map1 = maskele_geri_donusturulabilir(metin, firma_adlari=["Gibibyte"])
        m2, map2 = maskele_geri_donusturulabilir(metin, firma_adlari=["Gibibyte"])
        assert m1 == m2
        assert map1 == map2


class TestGeriCevir:
    """geri_cevir() testleri."""

    def test_basit(self):
        assert geri_cevir("[FIRMA_1] sozlesmesi", {"[FIRMA_1]": "ABC"}) == "ABC sozlesmesi"

    def test_birden_fazla(self):
        mapping = {"[FIRMA_1]": "ABC", "[FIRMA_2]": "XYZ"}
        assert geri_cevir("[FIRMA_1] ve [FIRMA_2]", mapping) == "ABC ve XYZ"

    def test_bos_mapping(self):
        assert geri_cevir("metin", {}) == "metin"

    def test_none_metin(self):
        assert geri_cevir(None, {"[X]": "Y"}) is None

    def test_bos_metin(self):
        assert geri_cevir("", {"[X]": "Y"}) == ""
