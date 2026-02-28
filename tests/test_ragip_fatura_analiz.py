"""Fatura analiz motorlari testleri — ADR-0007 semasina dayali hesaplamalar."""
import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from ragip_aga import FinansalHesap


# ─── Yardimci ─────────────────────────────────────────────────────────────────

def _gun_once(n: int) -> str:
    return str(datetime.date.today() - datetime.timedelta(days=n))


# ─── Ortak Fixture ────────────────────────────────────────────────────────────
# Tarihler bugun bazli offset — DSO/DPO zaman penceresine uyumlu.
# Aging testleri bugun=datetime.date.today() ile cagrilir.

FATURALAR = [
    # F-001: alacak, acik, vade 15 gun gecikmi -> 0-30 bucket
    {
        "id": 1, "fatura_no": "F-001", "firma_id": 10,
        "yon": "alacak", "tutar": 10000.0, "kdv_tutar": 2000.0, "toplam": 12000.0,
        "fatura_tarihi": _gun_once(25), "vade_tarihi": _gun_once(15),
        "odeme_tarihi": None, "odeme_tutari": None, "durum": "acik",
    },
    # F-002: alacak, kismi, vade 45 gun gecikmi -> 31-60 bucket, kalan=16000
    {
        "id": 2, "fatura_no": "F-002", "firma_id": 20,
        "yon": "alacak", "tutar": 20000.0, "kdv_tutar": 4000.0, "toplam": 24000.0,
        "fatura_tarihi": _gun_once(60), "vade_tarihi": _gun_once(45),
        "odeme_tarihi": _gun_once(30), "odeme_tutari": 8000.0, "durum": "kismi",
    },
    # F-003: alacak, odendi — aging'de yok ama gelir/tahsilat'ta var
    {
        "id": 3, "fatura_no": "F-003", "firma_id": 10,
        "yon": "alacak", "tutar": 15000.0, "kdv_tutar": 3000.0, "toplam": 18000.0,
        "fatura_tarihi": _gun_once(50), "vade_tarihi": _gun_once(20),
        "odeme_tarihi": _gun_once(15), "odeme_tutari": 18000.0, "durum": "odendi",
    },
    # F-004: alacak, iptal — hicbir metrikte yok
    {
        "id": 4, "fatura_no": "F-004", "firma_id": 30,
        "yon": "alacak", "tutar": 5000.0, "kdv_tutar": 1000.0, "toplam": 6000.0,
        "fatura_tarihi": _gun_once(40), "vade_tarihi": _gun_once(10),
        "odeme_tarihi": None, "odeme_tutari": None, "durum": "iptal",
    },
    # F-005: borc, acik — DPO + KDV icin
    {
        "id": 5, "fatura_no": "F-005", "firma_id": 50,
        "yon": "borc", "tutar": 8000.0, "kdv_tutar": 1600.0, "toplam": 9600.0,
        "fatura_tarihi": _gun_once(30), "vade_tarihi": _gun_once(20),
        "odeme_tarihi": None, "odeme_tutari": None, "durum": "acik",
    },
    # F-006: alacak, acik, vade 100 gun gecikmi -> 90+ bucket
    {
        "id": 6, "fatura_no": "F-006", "firma_id": 10,
        "yon": "alacak", "tutar": 30000.0, "kdv_tutar": 6000.0, "toplam": 36000.0,
        "fatura_tarihi": _gun_once(85), "vade_tarihi": _gun_once(100),
        "odeme_tarihi": None, "odeme_tutari": None, "durum": "acik",
    },
]


# ─── Gelir trendi icin sabit tarihli fixture ──────────────────────────────────

TRENDI_FATURALAR = [
    {
        "id": 101, "fatura_no": "T-001", "firma_id": 10,
        "yon": "alacak", "tutar": 8000.0, "kdv_tutar": 1600.0, "toplam": 9600.0,
        "fatura_tarihi": "2026-01-10", "vade_tarihi": "2026-02-10",
        "odeme_tarihi": "2026-02-05", "odeme_tutari": 9600.0, "durum": "odendi",
    },
    {
        "id": 102, "fatura_no": "T-002", "firma_id": 20,
        "yon": "alacak", "tutar": 12000.0, "kdv_tutar": 2400.0, "toplam": 14400.0,
        "fatura_tarihi": "2026-01-25", "vade_tarihi": "2026-02-25",
        "odeme_tarihi": None, "odeme_tutari": None, "durum": "acik",
    },
    {
        "id": 103, "fatura_no": "T-003", "firma_id": 10,
        "yon": "alacak", "tutar": 25000.0, "kdv_tutar": 5000.0, "toplam": 30000.0,
        "fatura_tarihi": "2026-02-15", "vade_tarihi": "2026-03-15",
        "odeme_tarihi": None, "odeme_tutari": None, "durum": "acik",
    },
    # iptal — dahil edilmemeli
    {
        "id": 104, "fatura_no": "T-004", "firma_id": 30,
        "yon": "alacak", "tutar": 5000.0, "kdv_tutar": 1000.0, "toplam": 6000.0,
        "fatura_tarihi": "2026-02-20", "vade_tarihi": "2026-03-20",
        "odeme_tarihi": None, "odeme_tutari": None, "durum": "iptal",
    },
]


# ─── KDV fixture (alacak + borc ayni donemde) ────────────────────────────────

KDV_FATURALAR = [
    {
        "id": 201, "fatura_no": "K-001", "firma_id": 10,
        "yon": "alacak", "tutar": 10000.0, "kdv_tutar": 2000.0, "toplam": 12000.0,
        "fatura_tarihi": "2026-01-15", "vade_tarihi": "2026-02-15",
        "odeme_tarihi": None, "odeme_tutari": None, "durum": "acik",
    },
    {
        "id": 202, "fatura_no": "K-002", "firma_id": 50,
        "yon": "borc", "tutar": 6000.0, "kdv_tutar": 1200.0, "toplam": 7200.0,
        "fatura_tarihi": "2026-01-20", "vade_tarihi": "2026-02-20",
        "odeme_tarihi": None, "odeme_tutari": None, "durum": "acik",
    },
    {
        "id": 203, "fatura_no": "K-003", "firma_id": 20,
        "yon": "alacak", "tutar": 15000.0, "kdv_tutar": 3000.0, "toplam": 18000.0,
        "fatura_tarihi": "2026-02-10", "vade_tarihi": "2026-03-10",
        "odeme_tarihi": None, "odeme_tutari": None, "durum": "acik",
    },
    # iptal — dahil edilmemeli
    {
        "id": 204, "fatura_no": "K-004", "firma_id": 10,
        "yon": "alacak", "tutar": 4000.0, "kdv_tutar": 800.0, "toplam": 4800.0,
        "fatura_tarihi": "2026-02-25", "vade_tarihi": "2026-03-25",
        "odeme_tarihi": None, "odeme_tutari": None, "durum": "iptal",
    },
]


# ═══════════════════════════════════════════════════════════════════════════════
# Test Siniflari
# ═══════════════════════════════════════════════════════════════════════════════


class TestAgingRaporu:
    def test_bucket_dagitimi(self):
        """F-001→0-30, F-002→31-60, F-006→90+"""
        sonuc = FinansalHesap.aging_raporu(FATURALAR)
        assert sonuc["b_0_30"]["adet"] == 1
        assert sonuc["b_31_60"]["adet"] == 1
        assert sonuc["b_61_90"]["adet"] == 0
        assert sonuc["b_90_plus"]["adet"] == 1

    def test_kalan_tutar_kismi(self):
        """Kismi odeme: toplam=24000 - odeme=8000 = kalan=16000"""
        sonuc = FinansalHesap.aging_raporu(FATURALAR)
        assert sonuc["b_31_60"]["tutar_tl"] == 16000.0

    def test_toplam_acik_alacak(self):
        """Toplam = F-001(12000) + F-002(16000) + F-006(36000) = 64000"""
        sonuc = FinansalHesap.aging_raporu(FATURALAR)
        assert sonuc["toplam_acik_alacak_tl"] == 64000.0
        assert sonuc["fatura_adedi"] == 3

    def test_odenmis_ve_iptal_haric(self):
        """Odenmis (F-003) ve iptal (F-004) dahil edilmez"""
        filtreli = [f for f in FATURALAR if f["durum"] in ("odendi", "iptal")]
        sonuc = FinansalHesap.aging_raporu(filtreli)
        assert sonuc["fatura_adedi"] == 0
        assert sonuc["toplam_acik_alacak_tl"] == 0.0

    def test_bos_liste(self):
        """Bos liste → sifir + yorum 'Veri yok'"""
        sonuc = FinansalHesap.aging_raporu([])
        assert sonuc["fatura_adedi"] == 0
        assert sonuc["toplam_acik_alacak_tl"] == 0.0
        assert "Veri yok" in sonuc["yorum"]

    def test_bugun_str_parametre(self):
        """bugun string olarak da kabul edilmeli"""
        bugun_str = str(datetime.date.today())
        sonuc = FinansalHesap.aging_raporu(FATURALAR, bugun=bugun_str)
        assert sonuc["bugun"] == bugun_str
        assert sonuc["fatura_adedi"] == 3

    def test_firma_id_filtresi(self):
        """firma_id=10: F-001(acik,12000) + F-006(acik,36000) = 2 fatura, 48000 TL"""
        sonuc = FinansalHesap.aging_raporu(FATURALAR, firma_id=10)
        assert sonuc["firma_id"] == 10
        assert sonuc["fatura_adedi"] == 2
        assert sonuc["toplam_acik_alacak_tl"] == 48000.0


class TestDso:
    def test_dso_hesap(self):
        """DSO = (acik_alacak / donem_geliri) x donem_gun"""
        sonuc = FinansalHesap.dso(FATURALAR, donem_gun=90)
        # F-001(25g), F-002(60g), F-003(50g), F-006(85g) hepsi son 90 gun icinde
        # Donem geliri = 12000 + 24000 + 18000 + 36000 = 90000
        # Acik alacak = 12000 + 16000 + 36000 = 64000 (F-003 odendi → haric)
        assert sonuc["donem_geliri_tl"] == 90000.0
        assert sonuc["acik_alacak_tl"] == 64000.0
        beklenen = (64000.0 / 90000.0) * 90
        assert abs(sonuc["dso_gun"] - round(beklenen, 1)) < 0.1

    def test_sadece_alacak(self):
        """Borc faturalar DSO'ya dahil edilmez"""
        sadece_borc = [f for f in FATURALAR if f["yon"] == "borc"]
        sonuc = FinansalHesap.dso(sadece_borc, donem_gun=90)
        assert sonuc["donem_geliri_tl"] == 0.0
        assert sonuc["dso_gun"] == 0.0

    def test_donem_gun_parametresi(self):
        """Kisa pencere farkli sonuc verir"""
        sonuc_30 = FinansalHesap.dso(FATURALAR, donem_gun=30)
        sonuc_90 = FinansalHesap.dso(FATURALAR, donem_gun=90)
        # 30 gunluk pencere daha az faturayi kapsar
        assert sonuc_30["donem_geliri_tl"] <= sonuc_90["donem_geliri_tl"]

    def test_bos_liste(self):
        """Bos liste → sifir"""
        sonuc = FinansalHesap.dso([], donem_gun=90)
        assert sonuc["dso_gun"] == 0.0
        assert "Veri yok" in sonuc["yorum"]

    def test_bugun_str_parametre(self):
        """bugun parametresi str olarak kabul edilmeli"""
        bugun_str = str(datetime.date.today())
        sonuc = FinansalHesap.dso(FATURALAR, donem_gun=90, bugun=bugun_str)
        assert sonuc["dso_gun"] >= 0

    def test_bugun_date_parametre(self):
        """bugun parametresi date olarak kabul edilmeli"""
        sonuc = FinansalHesap.dso(FATURALAR, donem_gun=90, bugun=datetime.date.today())
        assert sonuc["dso_gun"] >= 0

    def test_firma_id_filtresi(self):
        """firma_id=10: F-001(12000) + F-003(18000) + F-006(36000) = 66000 gelir"""
        sonuc = FinansalHesap.dso(FATURALAR, donem_gun=90, firma_id=10)
        assert sonuc["firma_id"] == 10
        assert sonuc["donem_geliri_tl"] == 66000.0
        # Acik: F-001(12000) + F-006(36000) = 48000
        assert sonuc["acik_alacak_tl"] == 48000.0


class TestTahsilatOrani:
    def test_kismi_odeme(self):
        """F-001(0) + F-002(8000) + F-003(18000) = 26000 / 54000"""
        sonuc = FinansalHesap.tahsilat_orani(FATURALAR)
        # Alacak, iptal haric: F-001(12000,0), F-002(24000,8000), F-003(18000,18000), F-006(36000,0)
        # toplam_fatura = 90000, toplam_odeme = 26000
        assert sonuc["toplam_fatura_tl"] == 90000.0
        assert sonuc["toplam_odeme_tl"] == 26000.0
        beklenen = (26000.0 / 90000.0) * 100
        assert abs(sonuc["tahsilat_orani_pct"] - round(beklenen, 2)) < 0.01

    def test_tam_odeme(self):
        """Tum faturalar odenmis → %100"""
        tam = [
            {"id": 1, "fatura_no": "X", "firma_id": 1, "yon": "alacak",
             "tutar": 1000.0, "toplam": 1200.0, "fatura_tarihi": "2026-01-01",
             "vade_tarihi": "2026-02-01", "odeme_tutari": 1200.0, "durum": "odendi"},
        ]
        sonuc = FinansalHesap.tahsilat_orani(tam)
        assert sonuc["tahsilat_orani_pct"] == 100.0

    def test_tarih_filtresi(self):
        """baslangic/bitis ile donem sinirla"""
        sonuc = FinansalHesap.tahsilat_orani(
            TRENDI_FATURALAR,
            baslangic="2026-02-01",
            bitis="2026-02-28",
        )
        # Sadece T-003 (2026-02-15) kalir, T-004 iptal
        assert sonuc["fatura_adedi"] == 1
        assert sonuc["toplam_fatura_tl"] == 30000.0

    def test_bos_liste(self):
        """Bos liste → sifir"""
        sonuc = FinansalHesap.tahsilat_orani([])
        assert sonuc["tahsilat_orani_pct"] == 0.0
        assert "Veri yok" in sonuc["yorum"]

    def test_firma_id_filtresi(self):
        """firma_id=10: F-001(12000,0) + F-003(18000,18000) + F-006(36000,0)"""
        sonuc = FinansalHesap.tahsilat_orani(FATURALAR, firma_id=10)
        assert sonuc["firma_id"] == 10
        assert sonuc["fatura_adedi"] == 3
        assert sonuc["toplam_fatura_tl"] == 66000.0
        assert sonuc["toplam_odeme_tl"] == 18000.0


class TestGelirTrendi:
    def test_aylar_sirali(self):
        """Aylar kronolojik sirali"""
        sonuc = FinansalHesap.gelir_trendi(TRENDI_FATURALAR)
        aylar = [a["ay"] for a in sonuc["aylar"]]
        assert aylar == sorted(aylar)

    def test_ay_sayisi(self):
        """2 farkli ay var (iptal haric): 2026-01, 2026-02"""
        sonuc = FinansalHesap.gelir_trendi(TRENDI_FATURALAR)
        assert sonuc["ay_sayisi"] == 2

    def test_aylik_toplam(self):
        """Ocak: T-001(9600) + T-002(14400) = 24000. Subat: T-003(30000)"""
        sonuc = FinansalHesap.gelir_trendi(TRENDI_FATURALAR)
        assert sonuc["aylar"][0]["toplam_tl"] == 24000.0
        assert sonuc["aylar"][1]["toplam_tl"] == 30000.0

    def test_degisim_pct(self):
        """Ilk ay None, ikinci ay = (30000-24000)/24000 * 100 = 25%"""
        sonuc = FinansalHesap.gelir_trendi(TRENDI_FATURALAR)
        assert sonuc["aylar"][0]["degisim_pct"] is None
        assert sonuc["aylar"][1]["degisim_pct"] == 25.0

    def test_iptal_haric(self):
        """T-004 (iptal) dahil edilmez — Subat toplami sadece T-003"""
        sonuc = FinansalHesap.gelir_trendi(TRENDI_FATURALAR)
        subat = [a for a in sonuc["aylar"] if a["ay"] == "2026-02"][0]
        assert subat["toplam_tl"] == 30000.0

    def test_bos_liste(self):
        """Bos liste → bos aylar"""
        sonuc = FinansalHesap.gelir_trendi([])
        assert sonuc["ay_sayisi"] == 0
        assert sonuc["aylar"] == []
        assert "Veri yok" in sonuc["yorum"]

    def test_firma_id_filtresi(self):
        """firma_id=10: T-001(9600, 2026-01) + T-003(30000, 2026-02) = 2 ay"""
        sonuc = FinansalHesap.gelir_trendi(TRENDI_FATURALAR, firma_id=10)
        assert sonuc["firma_id"] == 10
        assert sonuc["ay_sayisi"] == 2
        assert sonuc["aylar"][0]["toplam_tl"] == 9600.0
        assert sonuc["aylar"][1]["toplam_tl"] == 30000.0


class TestMusteriKonsantrasyonu:
    def test_top3_sirali(self):
        """En yuksek pay ilk sirada"""
        sonuc = FinansalHesap.musteri_konsantrasyonu(FATURALAR)
        assert len(sonuc["top3"]) > 0
        if len(sonuc["top3"]) > 1:
            assert sonuc["top3"][0]["tutar_tl"] >= sonuc["top3"][1]["tutar_tl"]

    def test_firma_10_en_buyuk(self):
        """Firma 10: F-001(12000) + F-003(18000) + F-006(36000) = 66000"""
        sonuc = FinansalHesap.musteri_konsantrasyonu(FATURALAR)
        firma_10 = [t for t in sonuc["top3"] if t["firma_id"] == 10]
        assert len(firma_10) == 1
        assert firma_10[0]["tutar_tl"] == 66000.0

    def test_hhi_tek_firma(self):
        """Tek firma = HHI 10000 (monopol)"""
        tek = [
            {"id": 1, "fatura_no": "X", "firma_id": 1, "yon": "alacak",
             "tutar": 1000.0, "toplam": 1200.0, "fatura_tarihi": "2026-01-01",
             "vade_tarihi": "2026-02-01", "durum": "acik"},
        ]
        sonuc = FinansalHesap.musteri_konsantrasyonu(tek)
        assert sonuc["hhi"] == 10000.0
        assert "yuksek" in sonuc["yorum"]

    def test_iptal_haric(self):
        """F-004 (iptal) dahil edilmez"""
        sonuc = FinansalHesap.musteri_konsantrasyonu(FATURALAR)
        # Toplam gelir iptal haric: F-001(12000) + F-002(24000) + F-003(18000) + F-006(36000) = 90000
        assert sonuc["toplam_gelir_tl"] == 90000.0

    def test_bos_liste(self):
        """Bos liste → sifir"""
        sonuc = FinansalHesap.musteri_konsantrasyonu([])
        assert sonuc["firma_adedi"] == 0
        assert sonuc["hhi"] == 0.0
        assert "Veri yok" in sonuc["yorum"]


class TestKdvDonemOzeti:
    def test_net_hesap(self):
        """Ocak: hesaplanan=2000, indirilecek=1200, net=800"""
        sonuc = FinansalHesap.kdv_donem_ozeti(KDV_FATURALAR)
        ocak = [d for d in sonuc["donemler"] if d["ay"] == "2026-01"][0]
        assert ocak["hesaplanan_kdv_tl"] == 2000.0
        assert ocak["indirilecek_kdv_tl"] == 1200.0
        assert ocak["net_kdv_tl"] == 800.0

    def test_yon_ayirimi(self):
        """Alacak = hesaplanan, borc = indirilecek"""
        sonuc = FinansalHesap.kdv_donem_ozeti(KDV_FATURALAR)
        # Subat: sadece K-003 (alacak, kdv=3000), K-004 iptal
        subat = [d for d in sonuc["donemler"] if d["ay"] == "2026-02"][0]
        assert subat["hesaplanan_kdv_tl"] == 3000.0
        assert subat["indirilecek_kdv_tl"] == 0.0

    def test_toplam(self):
        """Toplam hesaplanan = 2000+3000 = 5000, indirilecek = 1200"""
        sonuc = FinansalHesap.kdv_donem_ozeti(KDV_FATURALAR)
        assert sonuc["toplam_hesaplanan_tl"] == 5000.0
        assert sonuc["toplam_indirilecek_tl"] == 1200.0
        assert sonuc["toplam_net_tl"] == 3800.0

    def test_iptal_haric(self):
        """K-004 (iptal, kdv=800) dahil edilmez"""
        sonuc = FinansalHesap.kdv_donem_ozeti(KDV_FATURALAR)
        # Subat: sadece K-003 hesaplanan = 3000 (K-004 iptal)
        subat = [d for d in sonuc["donemler"] if d["ay"] == "2026-02"][0]
        assert subat["hesaplanan_kdv_tl"] == 3000.0

    def test_bos_liste(self):
        """Bos liste → sifir"""
        sonuc = FinansalHesap.kdv_donem_ozeti([])
        assert sonuc["ay_sayisi"] == 0
        assert "Veri yok" in sonuc["yorum"]

    def test_firma_id_filtresi(self):
        """firma_id=10: K-001(alacak, kdv=2000) — K-004 iptal, haric"""
        sonuc = FinansalHesap.kdv_donem_ozeti(KDV_FATURALAR, firma_id=10)
        assert sonuc["firma_id"] == 10
        assert sonuc["ay_sayisi"] == 1
        assert sonuc["toplam_hesaplanan_tl"] == 2000.0
        assert sonuc["toplam_indirilecek_tl"] == 0.0
        assert sonuc["toplam_net_tl"] == 2000.0


class TestDpo:
    def test_dpo_hesap(self):
        """DPO = (acik_borc / donem_alimlari) x donem_gun"""
        sonuc = FinansalHesap.dpo(FATURALAR, donem_gun=90)
        # F-005: borc, acik, fatura_tarihi 30 gun once → son 90 gun icinde
        # donem_alimlari = 9600, acik_borc = 9600
        assert sonuc["donem_alimlari_tl"] == 9600.0
        assert sonuc["acik_borc_tl"] == 9600.0
        # DPO = (9600/9600) * 90 = 90
        assert sonuc["dpo_gun"] == 90.0

    def test_sadece_borc_filtresi(self):
        """Alacak faturalar DPO'ya dahil edilmez"""
        sadece_alacak = [f for f in FATURALAR if f["yon"] == "alacak"]
        sonuc = FinansalHesap.dpo(sadece_alacak, donem_gun=90)
        assert sonuc["donem_alimlari_tl"] == 0.0
        assert sonuc["dpo_gun"] == 0.0

    def test_donem_gun_parametresi(self):
        """Kisa pencere: F-005 (30 gun once) son 30 gunde"""
        sonuc = FinansalHesap.dpo(FATURALAR, donem_gun=30)
        assert sonuc["donem_alimlari_tl"] == 9600.0

    def test_bos_liste(self):
        """Bos liste → sifir"""
        sonuc = FinansalHesap.dpo([], donem_gun=90)
        assert sonuc["dpo_gun"] == 0.0
        assert "Veri yok" in sonuc["yorum"]

    def test_bugun_str_parametre(self):
        """bugun parametresi str olarak kabul edilmeli"""
        bugun_str = str(datetime.date.today())
        sonuc = FinansalHesap.dpo(FATURALAR, donem_gun=90, bugun=bugun_str)
        assert sonuc["dpo_gun"] >= 0

    def test_bugun_date_parametre(self):
        """bugun parametresi date olarak kabul edilmeli"""
        sonuc = FinansalHesap.dpo(FATURALAR, donem_gun=90, bugun=datetime.date.today())
        assert sonuc["dpo_gun"] >= 0

    def test_firma_id_filtresi(self):
        """firma_id=50: F-005(borc, acik, 9600) — tek borc fatura"""
        sonuc = FinansalHesap.dpo(FATURALAR, donem_gun=90, firma_id=50)
        assert sonuc["firma_id"] == 50
        assert sonuc["donem_alimlari_tl"] == 9600.0
        assert sonuc["acik_borc_tl"] == 9600.0
        assert sonuc["dpo_gun"] == 90.0


class TestCccDashboard:
    def test_ccc_hesap(self):
        """CCC = DSO - DPO"""
        sonuc = FinansalHesap.ccc_dashboard(FATURALAR, donem_gun=90)
        # DSO ve DPO ayri metotlarla ayni sonucu vermeli
        dso = FinansalHesap.dso(FATURALAR, donem_gun=90)
        dpo = FinansalHesap.dpo(FATURALAR, donem_gun=90)
        beklenen_ccc = round(dso["dso_gun"] - dpo["dpo_gun"], 1)
        assert sonuc["ccc_gun"] == beklenen_ccc
        assert sonuc["dso_gun"] == dso["dso_gun"]
        assert sonuc["dpo_gun"] == dpo["dpo_gun"]

    def test_firma_id(self):
        """firma_id=10 filtresi tum alt metotlara iletilir"""
        sonuc = FinansalHesap.ccc_dashboard(FATURALAR, donem_gun=90, firma_id=10)
        assert sonuc["firma_id"] == 10
        # Firma 10 icin DSO/DPO kontrol
        dso = FinansalHesap.dso(FATURALAR, donem_gun=90, firma_id=10)
        dpo = FinansalHesap.dpo(FATURALAR, donem_gun=90, firma_id=10)
        assert sonuc["dso_gun"] == dso["dso_gun"]
        assert sonuc["dpo_gun"] == dpo["dpo_gun"]

    def test_bos_liste(self):
        """Bos liste → sifir + 'Veri yok'"""
        sonuc = FinansalHesap.ccc_dashboard([])
        assert sonuc["ccc_gun"] == 0.0
        assert sonuc["dso_gun"] == 0.0
        assert sonuc["dpo_gun"] == 0.0
        assert sonuc["tahsilat_orani_pct"] == 0.0
        assert "Veri yok" in sonuc["yorum"]

    def test_donem_gun(self):
        """Farkli donem penceresi farkli sonuc verebilir"""
        sonuc_30 = FinansalHesap.ccc_dashboard(FATURALAR, donem_gun=30)
        sonuc_90 = FinansalHesap.ccc_dashboard(FATURALAR, donem_gun=90)
        assert sonuc_30["donem_gun"] == 30
        assert sonuc_90["donem_gun"] == 90

    def test_altinda_metotlar(self):
        """dso_gun, dpo_gun, tahsilat, aging alanlari dogru donuyor"""
        sonuc = FinansalHesap.ccc_dashboard(FATURALAR, donem_gun=90)
        # Acik alacak = F-001(12000) + F-002(16000) + F-006(36000) = 64000
        assert sonuc["acik_alacak_tl"] == 64000.0
        # Acik borc = F-005(9600)
        assert sonuc["acik_borc_tl"] == 9600.0
        # Tahsilat orani
        tahsilat = FinansalHesap.tahsilat_orani(FATURALAR)
        assert sonuc["tahsilat_orani_pct"] == tahsilat["tahsilat_orani_pct"]
        # Aging alanlari mevcut
        assert "b_0_30" in sonuc["aging"]
        assert "b_31_60" in sonuc["aging"]
        assert "b_61_90" in sonuc["aging"]
        assert "b_90_plus" in sonuc["aging"]


# ═══════════════════════════════════════════════════════════════════════════════
# Fatura Uyari Sistemi
# ═══════════════════════════════════════════════════════════════════════════════


# Yaklasan vade fixture: alacak, acik, vade 3 gun sonra
YAKLASAN_FATURALAR = [
    {
        "id": 301, "fatura_no": "Y-001", "firma_id": 10,
        "yon": "alacak", "tutar": 5000.0, "kdv_tutar": 1000.0, "toplam": 6000.0,
        "fatura_tarihi": _gun_once(20),
        "vade_tarihi": str(datetime.date.today() + datetime.timedelta(days=3)),
        "odeme_tarihi": None, "odeme_tutari": None, "durum": "acik",
    },
    {
        "id": 302, "fatura_no": "Y-002", "firma_id": 20,
        "yon": "alacak", "tutar": 8000.0, "kdv_tutar": 1600.0, "toplam": 9600.0,
        "fatura_tarihi": _gun_once(15),
        "vade_tarihi": str(datetime.date.today() + datetime.timedelta(days=6)),
        "odeme_tarihi": None, "odeme_tutari": None, "durum": "acik",
    },
    # Vade 10 gun sonra — yaklasan degil (>7)
    {
        "id": 303, "fatura_no": "Y-003", "firma_id": 10,
        "yon": "alacak", "tutar": 3000.0, "kdv_tutar": 600.0, "toplam": 3600.0,
        "fatura_tarihi": _gun_once(10),
        "vade_tarihi": str(datetime.date.today() + datetime.timedelta(days=10)),
        "odeme_tarihi": None, "odeme_tutari": None, "durum": "acik",
    },
]


# TTK m.21/2 fixture: borc fatura, fatura_tarihi 6 gun once (itiraz suresi 2 gun kaldi)
TTK_FATURALAR = [
    {
        "id": 401, "fatura_no": "B-001", "firma_id": 50,
        "yon": "borc", "tutar": 7000.0, "kdv_tutar": 1400.0, "toplam": 8400.0,
        "fatura_tarihi": _gun_once(6),
        "vade_tarihi": str(datetime.date.today() + datetime.timedelta(days=24)),
        "odeme_tarihi": None, "odeme_tutari": None, "durum": "acik",
    },
    # fatura_tarihi 3 gun once — itiraz suresi 5 gun kaldi (>3, dahil degil)
    {
        "id": 402, "fatura_no": "B-002", "firma_id": 50,
        "yon": "borc", "tutar": 4000.0, "kdv_tutar": 800.0, "toplam": 4800.0,
        "fatura_tarihi": _gun_once(3),
        "vade_tarihi": str(datetime.date.today() + datetime.timedelta(days=27)),
        "odeme_tarihi": None, "odeme_tutari": None, "durum": "acik",
    },
    # fatura_tarihi 10 gun once — itiraz suresi gecmis (<=0, dahil degil)
    {
        "id": 403, "fatura_no": "B-003", "firma_id": 60,
        "yon": "borc", "tutar": 2000.0, "kdv_tutar": 400.0, "toplam": 2400.0,
        "fatura_tarihi": _gun_once(10),
        "vade_tarihi": str(datetime.date.today() + datetime.timedelta(days=20)),
        "odeme_tarihi": None, "odeme_tutari": None, "durum": "acik",
    },
]


class TestFaturaUyarilari:
    def test_vade_gecmis(self):
        """F-001(15g), F-002(45g, kismi), F-006(100g) vade gecmis"""
        sonuc = FinansalHesap.fatura_uyarilari(FATURALAR)
        assert sonuc["ozet"]["vade_gecmis_adet"] == 3
        # En kritik (100g) basta
        assert sonuc["vade_gecmis"][0]["fatura_no"] == "F-006"
        assert sonuc["vade_gecmis"][0]["gecikme_gun"] == 100
        # Kismi odeme: kalan = 24000 - 8000 = 16000
        f002 = [v for v in sonuc["vade_gecmis"] if v["fatura_no"] == "F-002"]
        assert len(f002) == 1
        assert f002[0]["kalan"] == 16000.0

    def test_yaklasan_vade(self):
        """Y-001(3g) + Y-002(6g) yaklasan, Y-003(10g) degil"""
        sonuc = FinansalHesap.fatura_uyarilari(YAKLASAN_FATURALAR)
        assert sonuc["ozet"]["yaklasan_adet"] == 2
        assert sonuc["ozet"]["vade_gecmis_adet"] == 0
        # En yakin basta
        assert sonuc["yaklasan_vade"][0]["fatura_no"] == "Y-001"
        assert sonuc["yaklasan_vade"][0]["kalan_gun"] == 3

    def test_ttk_itiraz_suresi(self):
        """B-001(2g kaldi) dahil, B-002(5g) ve B-003(gecmis) haric"""
        sonuc = FinansalHesap.fatura_uyarilari(TTK_FATURALAR)
        assert sonuc["ozet"]["ttk_adet"] == 1
        assert sonuc["ttk_itiraz"][0]["fatura_no"] == "B-001"
        assert sonuc["ttk_itiraz"][0]["kalan_gun"] == 2

    def test_firma_id_filtresi(self):
        """firma_id=10: FATURALAR'dan sadece firma 10'un uyarilari"""
        sonuc = FinansalHesap.fatura_uyarilari(FATURALAR, firma_id=10)
        assert sonuc["firma_id"] == 10
        # Firma 10: F-001(acik, 15g gecikti) + F-006(acik, 100g gecikti)
        assert sonuc["ozet"]["vade_gecmis_adet"] == 2
        for v in sonuc["vade_gecmis"]:
            assert v["firma_id"] == 10

    def test_bos_liste(self):
        """Bos liste → sifir uyari + 'Veri yok'"""
        sonuc = FinansalHesap.fatura_uyarilari([])
        assert sonuc["ozet"]["vade_gecmis_adet"] == 0
        assert sonuc["ozet"]["yaklasan_adet"] == 0
        assert sonuc["ozet"]["ttk_adet"] == 0
        assert "Veri yok" in sonuc["yorum"]

    def test_iptal_haric(self):
        """F-004 (iptal, alacak) dahil edilmez"""
        iptal = [f for f in FATURALAR if f["fatura_no"] == "F-004"]
        sonuc = FinansalHesap.fatura_uyarilari(iptal)
        assert sonuc["ozet"]["vade_gecmis_adet"] == 0

    def test_odenmis_haric(self):
        """F-003 (odenmis, alacak) dahil edilmez"""
        odenmis = [f for f in FATURALAR if f["fatura_no"] == "F-003"]
        sonuc = FinansalHesap.fatura_uyarilari(odenmis)
        assert sonuc["ozet"]["vade_gecmis_adet"] == 0
        assert "Uyari yok" in sonuc["yorum"]
