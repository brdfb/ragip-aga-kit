"""Katman 3 Integration Test — Gerçek D365 veri yapısına dayalı FinansalHesap doğrulaması.

Bu testler gerçek Güven Pres / Plastay / AR Tarım verisiyle keşfedilen edge case'leri kapsar:
- GUID firma_id (36 char)
- %94 USD fatura, %6 TRL
- Kısmi ödeme (3 fatura)
- vade == fatura tarihi (S5 uyarısı)
- Parasüt kur kaynağı
- dto_to_faturalar benzeri yapı → validate → FinansalHesap zinciri
"""
import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from ragip_aga import FinansalHesap
from ragip_crud import validate_fatura, validate_faturalar


# ── Gerçek D365 Yapısını Yansıtan Fixture ────────────────────────────────────
# GUID firma_id, USD/TRL karışık, Parasüt kuru, kısmi ödeme, vade==fatura

BUGUN = datetime.date(2026, 3, 20)

FIRMA_GP = "a31b6428-8fec-f011-8544-6045bde0b04e"  # Güven Pres
FIRMA_PL = "c043527a-8fec-f011-8406-000d3a68a4c0"  # Plastay
FIRMA_AT = "7bfa0ece-8fec-f011-8544-6045bde0b04e"  # AR Tarım

D365_FATURALAR = [
    # Güven Pres — USD, vade==fatura, kısmi ödeme
    {
        "id": 1, "fatura_no": "GT02024000000029", "firma_id": FIRMA_GP,
        "yon": "alacak", "tutar": 7932.0, "kdv_tutar": 1586.4, "toplam": 9518.4,
        "fatura_tarihi": "2024-02-07", "vade_tarihi": "2024-02-07",
        "odeme_tarihi": "2024-03-15", "odeme_tutari": 9285.63, "durum": "kismi",
        "para_birimi": "USD", "fatura_kuru": 30.6,
    },
    # Güven Pres — USD, açık, vade==fatura
    {
        "id": 2, "fatura_no": "GT02025000000200", "firma_id": FIRMA_GP,
        "yon": "alacak", "tutar": 10707.22, "kdv_tutar": 2141.44, "toplam": 12848.66,
        "fatura_tarihi": "2025-10-06", "vade_tarihi": "2025-10-06",
        "odeme_tarihi": None, "odeme_tutari": None, "durum": "acik",
        "para_birimi": "USD", "fatura_kuru": 41.1816,
    },
    # Güven Pres — USD, ödenmiş
    {
        "id": 3, "fatura_no": "GT02022000000129", "firma_id": FIRMA_GP,
        "yon": "alacak", "tutar": 4835.27, "kdv_tutar": 870.35, "toplam": 5705.62,
        "fatura_tarihi": "2022-11-04", "vade_tarihi": "2022-11-04",
        "odeme_tarihi": "2022-11-28", "odeme_tutari": 5705.62, "durum": "odendi",
        "para_birimi": "USD", "fatura_kuru": 18.5972,
    },
    # Plastay — USD, açık, vade != fatura (3 gün)
    {
        "id": 4, "fatura_no": "GT02026000000003", "firma_id": FIRMA_PL,
        "yon": "alacak", "tutar": 101397.86, "kdv_tutar": 20279.57, "toplam": 121677.43,
        "fatura_tarihi": "2026-01-08", "vade_tarihi": "2026-01-11",
        "odeme_tarihi": "2026-02-10", "odeme_tutari": 59173.89, "durum": "kismi",
        "para_birimi": "USD", "fatura_kuru": 35.42,
    },
    # Plastay — USD, ödenmiş
    {
        "id": 5, "fatura_no": "GT02025000000176", "firma_id": FIRMA_PL,
        "yon": "alacak", "tutar": 104580.93, "kdv_tutar": 20916.19, "toplam": 125497.12,
        "fatura_tarihi": "2025-09-09", "vade_tarihi": "2025-09-12",
        "odeme_tarihi": "2025-10-08", "odeme_tutari": 125497.12, "durum": "odendi",
        "para_birimi": "USD", "fatura_kuru": 34.18,
    },
    # AR Tarım — TRL, ödenmiş, kur=1.0
    {
        "id": 6, "fatura_no": "GB02022000000023", "firma_id": FIRMA_AT,
        "yon": "alacak", "tutar": 4873.33, "kdv_tutar": 974.67, "toplam": 5848.0,
        "fatura_tarihi": "2022-04-25", "vade_tarihi": "2022-04-25",
        "odeme_tarihi": "2022-05-20", "odeme_tutari": 5848.0, "durum": "odendi",
        "para_birimi": "TRY", "fatura_kuru": 1.0,
    },
    # AR Tarım — TRL, ödenmiş
    {
        "id": 7, "fatura_no": "GB02022000000034", "firma_id": FIRMA_AT,
        "yon": "alacak", "tutar": 3505.67, "kdv_tutar": 701.13, "toplam": 4206.8,
        "fatura_tarihi": "2022-05-25", "vade_tarihi": "2022-05-25",
        "odeme_tarihi": "2022-06-30", "odeme_tutari": 4206.8, "durum": "odendi",
        "para_birimi": "TRY", "fatura_kuru": 1.0,
    },
]


# ── Sema Doğrulama Testleri ──────────────────────────────────────────────────

class TestD365SemaUyumu:
    """D365 kaynaklı gerçek veri yapısının ADR-0007 şemasına uyumunu doğrular."""

    def test_tum_faturalar_gecerli(self):
        gecerli, hatali = validate_faturalar(D365_FATURALAR)
        assert len(hatali) == 0, f"Hatali faturalar: {hatali}"
        assert len(gecerli) == 7

    def test_guid_firma_id_kabul(self):
        """GUID firma_id (36 char string) geçerli olmalı."""
        for f in D365_FATURALAR:
            hatalar = validate_fatura(f)
            assert not any("firma_id" in h for h in hatalar), \
                f"{f['fatura_no']}: {hatalar}"

    def test_doviz_alanlari_gecerli(self):
        """USD ve TRL döviz kodları geçerli (3 char ISO 4217)."""
        for f in D365_FATURALAR:
            hatalar = validate_fatura(f)
            assert not any("para_birimi" in h for h in hatalar)

    def test_kismi_odeme_tutarliligi(self):
        """Kısmi ödemelerde odeme_tutari < toplam."""
        kismi = [f for f in D365_FATURALAR if f["durum"] == "kismi"]
        assert len(kismi) == 2
        for f in kismi:
            assert f["odeme_tutari"] < f["toplam"], \
                f"{f['fatura_no']}: odeme={f['odeme_tutari']} >= toplam={f['toplam']}"


# ── Aging Testleri (D365 Verisi) ─────────────────────────────────────────────

class TestD365Aging:
    """Gerçek D365 veri yapısıyla aging raporu doğrulaması."""

    def test_acik_faturalar_aging(self):
        aging = FinansalHesap.aging_raporu(D365_FATURALAR, BUGUN)
        # 2 açık + 2 kısmi = 4 fatura aging'de (kalan > 0)
        assert aging["fatura_adedi"] >= 2
        assert aging["toplam_acik_alacak_tl"] > 0

    def test_90_plus_bucket(self):
        """GT02025000000200: vade 2025-10-06, bugün 2026-03-20 = 165 gün → 90+ bucket."""
        aging = FinansalHesap.aging_raporu(D365_FATURALAR, BUGUN)
        assert aging["b_90_plus"]["adet"] >= 1
        assert aging["b_90_plus"]["tutar_tl"] > 0

    def test_odenmis_aging_disinda(self):
        """Ödenmiş faturalar aging'de sayılmamalı."""
        sadece_odenmis = [f for f in D365_FATURALAR if f["durum"] == "odendi"]
        aging = FinansalHesap.aging_raporu(sadece_odenmis, BUGUN)
        assert aging["fatura_adedi"] == 0
        assert aging["toplam_acik_alacak_tl"] == 0

    def test_kismi_odeme_kalan(self):
        """Kısmi ödeme: sadece kalan tutar aging'e girmeli."""
        kismi = [f for f in D365_FATURALAR if f["fatura_no"] == "GT02024000000029"]
        aging = FinansalHesap.aging_raporu(kismi, BUGUN)
        # toplam=9518.4, odeme=9285.63, kalan=232.77
        assert aging["toplam_acik_alacak_tl"] < 9518.4


# ── Tahsilat Testleri ────────────────────────────────────────────────────────

class TestD365Tahsilat:

    def test_tahsilat_orani(self):
        tah = FinansalHesap.tahsilat_orani(D365_FATURALAR)
        # 3 ödenmiş + 2 kısmi ödeme var, 2 açık
        assert tah["tahsilat_orani_pct"] > 0
        assert tah["toplam_fatura_tl"] > 0
        assert tah["toplam_odeme_tl"] > 0

    def test_tahsilat_iptal_haric(self):
        """İptal fatura yoksa toplam fatura tüm kayıtları kapsar."""
        tah = FinansalHesap.tahsilat_orani(D365_FATURALAR)
        assert tah["fatura_adedi"] == 7  # iptal yok


# ── DSO / DPO Testleri ──────────────────────────────────────────────────────

class TestD365DsoDpo:

    def test_dso_hesaplanir(self):
        dso = FinansalHesap.dso(D365_FATURALAR, bugun=BUGUN)
        assert "dso_gun" in dso
        assert isinstance(dso["dso_gun"], (int, float))

    def test_dpo_sifir(self):
        """Sadece alacak faturası var → DPO = 0."""
        dpo = FinansalHesap.dpo(D365_FATURALAR, bugun=BUGUN)
        assert dpo["dpo_gun"] == 0.0


# ── Gelir Trendi ─────────────────────────────────────────────────────────────

class TestD365GelirTrendi:

    def test_donem_sayisi(self):
        trend = FinansalHesap.gelir_trendi(D365_FATURALAR)
        aylar = trend.get("aylar", [])
        # 2022-2026 arası faturalar → birden fazla dönem
        assert len(aylar) >= 3

    def test_iptal_haric(self):
        """İptal fatura gelir trendinde sayılmamalı."""
        iptal_eklenmis = D365_FATURALAR + [{
            "id": 99, "fatura_no": "IPTAL-001", "firma_id": FIRMA_GP,
            "yon": "alacak", "tutar": 999999, "kdv_tutar": 0, "toplam": 999999,
            "fatura_tarihi": "2026-03-01", "vade_tarihi": "2026-03-01",
            "odeme_tarihi": None, "odeme_tutari": None, "durum": "iptal",
        }]
        trend_ile = FinansalHesap.gelir_trendi(iptal_eklenmis)
        trend_siz = FinansalHesap.gelir_trendi(D365_FATURALAR)
        # İptal eklenmesi gelir toplamını değiştirmemeli
        assert trend_ile.get("aylar", [{}])[-1].get("toplam_tl") == \
               trend_siz.get("aylar", [{}])[-1].get("toplam_tl") if trend_siz.get("aylar") else True


# ── Müşteri Konsantrasyon ────────────────────────────────────────────────────

class TestD365Konsantrasyon:

    def test_uc_firma(self):
        kon = FinansalHesap.musteri_konsantrasyonu(D365_FATURALAR)
        assert kon["firma_adedi"] == 3

    def test_tek_firma_raporu(self):
        tek_firma = [f for f in D365_FATURALAR if f["firma_id"] == FIRMA_GP]
        kon = FinansalHesap.musteri_konsantrasyonu(tek_firma, tek_firma_raporu=True)
        assert kon["firma_adedi"] == 1

    def test_guid_firma_id_gruplama(self):
        """GUID firma_id ile gruplama doğru çalışmalı."""
        kon = FinansalHesap.musteri_konsantrasyonu(D365_FATURALAR)
        top3 = kon.get("top3", [])
        firma_idler = {t["firma_id"] for t in top3}
        # Her firma bir kez görünmeli
        assert len(firma_idler) == len(top3)


# ── KDV Dönem Özeti ──────────────────────────────────────────────────────────

class TestD365KDV:

    def test_donem_olusur(self):
        kdv = FinansalHesap.kdv_donem_ozeti(D365_FATURALAR)
        donemler = kdv.get("donemler", [])
        assert len(donemler) >= 1

    def test_kdv_tutarlari_pozitif(self):
        """Alacak faturalarında hesaplanan KDV pozitif olmalı."""
        kdv = FinansalHesap.kdv_donem_ozeti(D365_FATURALAR)
        for d in kdv.get("donemler", []):
            assert d.get("hesaplanan_kdv_tl", 0) >= 0


# ── Fatura Uyarıları ─────────────────────────────────────────────────────────

class TestD365Uyarilar:

    def test_vade_gecmis_tespiti(self):
        """GT02025000000200: vade 2025-10-06, bugün 2026-03-20 → vadesi geçmiş."""
        uyarilar = FinansalHesap.fatura_uyarilari(D365_FATURALAR, BUGUN)
        vade_gecmis = uyarilar.get("vade_gecmis", [])
        # En az 1 vadesi geçmiş fatura olmalı
        assert len(vade_gecmis) >= 1

    def test_vade_gecmis_gun_hesabi(self):
        """Gecikme gün sayısı doğru hesaplanmalı."""
        uyarilar = FinansalHesap.fatura_uyarilari(D365_FATURALAR, BUGUN)
        for vg in uyarilar.get("vade_gecmis", []):
            if vg.get("fatura_no") == "GT02025000000200":
                # 2025-10-06 → 2026-03-20 = 165 gün
                assert vg["gecikme_gun"] == 165
                break


# ── CCC Dashboard ────────────────────────────────────────────────────────────

class TestD365CCC:

    def test_ccc_hesaplanir(self):
        ccc = FinansalHesap.ccc_dashboard(D365_FATURALAR, bugun=BUGUN)
        assert "dso_gun" in ccc
        assert "dpo_gun" in ccc
        assert "tahsilat_orani_pct" in ccc
        assert "aging" in ccc
        assert "ccc_gun" in ccc

    def test_ccc_sadece_alacak(self):
        """Sadece alacak fatura → DPO=0, CCC=DSO."""
        sadece_alacak = [f for f in D365_FATURALAR if f["yon"] == "alacak"]
        ccc = FinansalHesap.ccc_dashboard(sadece_alacak, bugun=BUGUN)
        assert ccc["dpo_gun"] == 0.0


# ── Çoklu Döviz Senaryosu ───────────────────────────────────────────────────

class TestD365CokluDoviz:

    def test_trl_ve_usd_karisik(self):
        """TRL ve USD faturalar birlikte çalışmalı."""
        # validate hepsi geçerli
        gecerli, hatali = validate_faturalar(D365_FATURALAR)
        assert len(hatali) == 0

        # aging çalışmalı (TL bazlı raporlama)
        aging = FinansalHesap.aging_raporu(gecerli, BUGUN)
        assert aging["toplam_acik_alacak_tl"] > 0

    def test_kur_1_try(self):
        """TRY faturalarda kur=1.0 olmalı."""
        try_faturalar = [f for f in D365_FATURALAR if f.get("para_birimi") == "TRY"]
        assert len(try_faturalar) >= 1, "Test verisinde TRY fatura olmali"
        for f in try_faturalar:
            assert f.get("fatura_kuru") == 1.0

    def test_fatura_kuru_pozitif(self):
        """Tum fatura kurlari pozitif olmali."""
        for f in D365_FATURALAR:
            kur = f.get("fatura_kuru")
            if kur is not None:
                assert kur > 0, f"{f['fatura_no']}: fatura_kuru={kur} pozitif olmali"

    def test_fatura_kuru_validasyon(self):
        """fatura_kuru=0 veya negatif validate_fatura'da hata vermeli."""
        f = D365_FATURALAR[0].copy()
        f["fatura_kuru"] = 0
        hatalar = validate_fatura(f)
        assert any("fatura_kuru" in h and "pozitif" in h for h in hatalar)

        f["fatura_kuru"] = -5.0
        hatalar = validate_fatura(f)
        assert any("fatura_kuru" in h and "pozitif" in h for h in hatalar)

    def test_odeme_kuru_validasyon(self):
        """odeme_kuru tip ve pozitiflik kontrolu."""
        f = D365_FATURALAR[0].copy()
        # Gecerli odeme_kuru
        f["odeme_kuru"] = 32.5
        hatalar = validate_fatura(f)
        assert not any("odeme_kuru" in h for h in hatalar)

        # Gecersiz: string
        f["odeme_kuru"] = "otuz"
        hatalar = validate_fatura(f)
        assert any("odeme_kuru" in h and "sayisal" in h for h in hatalar)

        # Gecersiz: negatif
        f["odeme_kuru"] = -1.0
        hatalar = validate_fatura(f)
        assert any("odeme_kuru" in h and "pozitif" in h for h in hatalar)

    def test_odeme_kuru_null_gecerli(self):
        """odeme_kuru=null (odenmemis) gecerli olmali."""
        f = D365_FATURALAR[1].copy()  # acik fatura
        f["odeme_kuru"] = None
        hatalar = validate_fatura(f)
        assert not any("odeme_kuru" in h for h in hatalar)

    def test_para_birimi_standart_alan_adi(self):
        """ADR-0007 standart alan adi para_birimi olmali, doviz degil."""
        for f in D365_FATURALAR:
            assert "para_birimi" in f, f"{f['fatura_no']}: para_birimi alani eksik"
            assert "doviz" not in f, f"{f['fatura_no']}: doviz yerine para_birimi kullanilmali"


# ── Vade == Fatura Tarihi Senaryosu ──────────────────────────────────────────

class TestD365VadeEsit:

    def test_vade_esit_hala_gecerli(self):
        """vade == fatura_tarihi olan kayıtlar şema açısından geçerli."""
        esit = [f for f in D365_FATURALAR if f["vade_tarihi"] == f["fatura_tarihi"]]
        assert len(esit) >= 4  # Güven Pres + AR Tarım
        for f in esit:
            hatalar = validate_fatura(f)
            assert len(hatalar) == 0

    def test_aging_vade_esit_ile_calisir(self):
        """vade == fatura olan kayıtlarla aging hata vermemeli."""
        esit = [f for f in D365_FATURALAR
                if f["vade_tarihi"] == f["fatura_tarihi"] and f["durum"] == "acik"]
        aging = FinansalHesap.aging_raporu(esit, BUGUN)
        assert aging["fatura_adedi"] == len(esit)


# ── Nakit Projeksiyon ────────────────────────────────────────────────────────

class TestD365NakitProjeksiyon:

    def test_projeksiyon_olusur(self):
        proj = FinansalHesap.nakit_projeksiyon(D365_FATURALAR, donem_gun=90, bugun=BUGUN)
        assert "haftalik" in proj
        assert "donem_toplam" in proj
        assert "vadesi_gecmis" in proj
        assert "toplam_acik" in proj

    def test_haftalik_kirilim(self):
        proj = FinansalHesap.nakit_projeksiyon(D365_FATURALAR, donem_gun=30, bugun=BUGUN)
        haftalik = proj["haftalik"]
        # 30 gun / 7 = 4-5 hafta
        assert len(haftalik) >= 4

    def test_vadesi_gecmis_faturalar(self):
        """Acik faturalar vadesi gecmis olarak gosterilmeli."""
        proj = FinansalHesap.nakit_projeksiyon(D365_FATURALAR, donem_gun=30, bugun=BUGUN)
        # GT02025000000200 vade 2025-10-06 < BUGUN (2026-03-20) = vadesi gecmis
        assert proj["vadesi_gecmis"]["alacak_tl"] > 0

    def test_firma_filtresi(self):
        proj = FinansalHesap.nakit_projeksiyon(
            D365_FATURALAR, donem_gun=90, bugun=BUGUN, firma_id=FIRMA_GP)
        assert proj["firma_id"] == FIRMA_GP

    def test_odenmis_dahil_degil(self):
        """Odenmiş faturalar projeksiyonda olmamali."""
        sadece_odenmis = [f for f in D365_FATURALAR if f["durum"] == "odendi"]
        proj = FinansalHesap.nakit_projeksiyon(sadece_odenmis, donem_gun=90, bugun=BUGUN)
        assert proj["toplam_acik"]["alacak_tl"] == 0
        assert proj["toplam_acik"]["borc_tl"] == 0

    def test_net_pozisyon(self):
        proj = FinansalHesap.nakit_projeksiyon(D365_FATURALAR, donem_gun=90, bugun=BUGUN)
        net = proj["toplam_acik"]["net_tl"]
        alacak = proj["toplam_acik"]["alacak_tl"]
        borc = proj["toplam_acik"]["borc_tl"]
        assert abs(net - (alacak - borc)) < 0.01


# ── Ödeme Trend Analizi ─────────────────────────────────────────────────────

class TestD365OdemeTrend:

    def test_trend_olusur(self):
        trend = FinansalHesap.odeme_trend_analizi(D365_FATURALAR, bugun=BUGUN)
        assert "firmalar" in trend
        assert "firma_adedi" in trend

    def test_firma_bazli(self):
        trend = FinansalHesap.odeme_trend_analizi(
            D365_FATURALAR, bugun=BUGUN, firma_id=FIRMA_GP)
        # Sadece GP firması
        assert trend["firma_adedi"] <= 1

    def test_gecikme_hesabi(self):
        trend = FinansalHesap.odeme_trend_analizi(D365_FATURALAR, bugun=BUGUN)
        for f in trend["firmalar"]:
            # Ortalama gecikme sayisal olmali
            assert isinstance(f["ortalama_gecikme_gun"], (int, float))
            assert f["max_gecikme_gun"] >= f["min_gecikme_gun"]

    def test_trend_degerleri(self):
        trend = FinansalHesap.odeme_trend_analizi(D365_FATURALAR, bugun=BUGUN)
        for f in trend["firmalar"]:
            assert f["trend"] in ("iyilesiyor", "kotulesiyor", "stabil", "yetersiz_veri")

    def test_uc_firma(self):
        trend = FinansalHesap.odeme_trend_analizi(D365_FATURALAR, bugun=BUGUN)
        # 3 firma var, en az birinde gecikme olmali
        assert trend["firma_adedi"] >= 1


# ── Kur Farkı Hesaplama ──────────────────────────────────────────────────────

class TestKurFarkiHesapla:
    """ADR-0007 kur farki hesaplama testleri."""

    def _fatura_kur(self, fatura_kuru, odeme_kuru, tutar=1000.0, pb="USD", durum="odendi"):
        """Kur farki testi icin minimal fatura."""
        return {
            "id": 99, "fatura_no": "KF-TEST", "firma_id": "test-firma",
            "yon": "alacak", "tutar": tutar, "toplam": tutar * 1.2,
            "fatura_tarihi": "2025-06-01", "vade_tarihi": "2025-07-01",
            "odeme_tarihi": "2025-07-15", "odeme_tutari": tutar * 1.2,
            "durum": durum, "para_birimi": pb,
            "fatura_kuru": fatura_kuru, "odeme_kuru": odeme_kuru,
        }

    def test_kur_kaybi(self):
        """TRY zayifladi — kur farki pozitif (kayip)."""
        f = self._fatura_kur(fatura_kuru=30.0, odeme_kuru=35.0, tutar=1000.0)
        sonuc = FinansalHesap.kur_farki_hesapla([f])
        # (35 - 30) × 1000 = 5000 TL kayip
        assert sonuc["toplam_kur_farki_tl"] == 5000.0
        assert sonuc["toplam_kayip_tl"] == 5000.0
        assert sonuc["toplam_kazanc_tl"] == 0.0
        assert sonuc["islenen_fatura"] == 1

    def test_kur_kazanci(self):
        """TRY guclendi — kur farki negatif (kazanc)."""
        f = self._fatura_kur(fatura_kuru=35.0, odeme_kuru=30.0, tutar=1000.0)
        sonuc = FinansalHesap.kur_farki_hesapla([f])
        # (30 - 35) × 1000 = -5000 TL kazanc
        assert sonuc["toplam_kur_farki_tl"] == -5000.0
        assert sonuc["toplam_kazanc_tl"] == 5000.0
        assert sonuc["toplam_kayip_tl"] == 0.0

    def test_try_fatura_atlanir(self):
        """TRY faturalar kur farki hesabina girmemeli."""
        f = self._fatura_kur(fatura_kuru=1.0, odeme_kuru=1.0, pb="TRY")
        sonuc = FinansalHesap.kur_farki_hesapla([f])
        assert sonuc["islenen_fatura"] == 0

    def test_eksik_odeme_kuru(self):
        """odeme_kuru=None → eksik_kur sayaci artmali."""
        f = self._fatura_kur(fatura_kuru=30.0, odeme_kuru=None)
        sonuc = FinansalHesap.kur_farki_hesapla([f])
        assert sonuc["eksik_kur_fatura"] == 1
        assert sonuc["islenen_fatura"] == 0

    def test_eksik_fatura_kuru(self):
        """fatura_kuru=None → eksik_kur sayaci artmali."""
        f = self._fatura_kur(fatura_kuru=None, odeme_kuru=35.0)
        sonuc = FinansalHesap.kur_farki_hesapla([f])
        assert sonuc["eksik_kur_fatura"] == 1

    def test_iptal_atlanir(self):
        """iptal faturalar hesaba girmemeli."""
        f = self._fatura_kur(fatura_kuru=30.0, odeme_kuru=35.0, durum="iptal")
        sonuc = FinansalHesap.kur_farki_hesapla([f])
        assert sonuc["islenen_fatura"] == 0

    def test_karisik_faturalar(self):
        """Kayip + kazanc karisik — net sonuc doğru olmali."""
        kayip = self._fatura_kur(fatura_kuru=30.0, odeme_kuru=35.0, tutar=1000.0)
        kazanc = self._fatura_kur(fatura_kuru=35.0, odeme_kuru=32.0, tutar=500.0)
        kazanc["fatura_no"] = "KF-TEST-2"
        sonuc = FinansalHesap.kur_farki_hesapla([kayip, kazanc])
        # kayip: (35-30)*1000 = 5000, kazanc: (32-35)*500 = -1500
        assert sonuc["toplam_kur_farki_tl"] == 3500.0
        assert sonuc["toplam_kayip_tl"] == 5000.0
        assert sonuc["toplam_kazanc_tl"] == 1500.0
        assert sonuc["islenen_fatura"] == 2

    def test_firma_filtresi(self):
        """firma_id filtresi calismali."""
        f1 = self._fatura_kur(fatura_kuru=30.0, odeme_kuru=35.0)
        f1["firma_id"] = "firma-A"
        f2 = self._fatura_kur(fatura_kuru=30.0, odeme_kuru=35.0)
        f2["firma_id"] = "firma-B"
        f2["fatura_no"] = "KF-TEST-B"
        sonuc = FinansalHesap.kur_farki_hesapla([f1, f2], firma_id="firma-A")
        assert sonuc["islenen_fatura"] == 1

    def test_d365_verisi_eksik_kur(self):
        """D365 verisinde odeme_kuru null — tum faturalar eksik_kur'a dusmeli."""
        sonuc = FinansalHesap.kur_farki_hesapla(D365_FATURALAR)
        # D365 test verisinde odeme_kuru yok — hepsi eksik
        usd = [f for f in D365_FATURALAR if f.get("para_birimi") == "USD"]
        assert sonuc["eksik_kur_fatura"] == len(usd)
        assert sonuc["islenen_fatura"] == 0
