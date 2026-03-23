"""ragip_output.py testleri — cikti yonetimi, firma klasor, manifest, meta block."""
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from ragip_output import (
    _slug, _frontmatter, _parmak_izi, _ayni_cikti_var_mi,
    kaydet, son_cikti, veri_tazeligi, tazelik_ozeti,
)


class TestSlug:
    """Firma adi → dosya sistemi slug donusumu."""

    def test_basit(self):
        assert _slug("Geneks Kimya") == "geneks_kimya"

    def test_turkce_karakter(self):
        assert _slug("GÜVEN PRES DÖKÜM") == "guven_pres_dokum"

    def test_uzun_unvan_kisaltma(self):
        slug = _slug("HEKİMOĞLU DÖKÜM SANAYİ NAKLİYAT VE TİCARET A.Ş")
        assert "hekimoglu" in slug
        assert "dokum" in slug
        assert slug.endswith("nakliyat") or slug.endswith("dokum")
        # san, ve, tic, as gibi ekler kesilmeli
        assert "tic" not in slug.split("_")
        assert "as" not in slug.split("_")

    def test_bosluk_temizleme(self):
        assert _slug("  Plastay   Kimya  ") == "plastay_kimya"

    def test_ozel_karakter(self):
        slug = _slug("ABC & Partners Ltd. Şti.")
        assert "&" not in slug
        assert "." not in slug

    def test_kisa_isim(self):
        assert _slug("AB") == "ab"

    def test_innova(self):
        slug = _slug("INNOVA BİLİŞİM ÇÖZÜMLERİ A.Ş.")
        assert "innova" in slug
        assert "bilisim" in slug


class TestFrontmatter:
    """YAML frontmatter olusturma."""

    def test_temel_alanlar(self):
        fm = _frontmatter("hesap", "rapor", "Geneks Kimya")
        assert "---" in fm
        assert "agent: hesap" in fm
        assert "skill: rapor" in fm
        assert "firma: Geneks Kimya" in fm
        assert "tarih:" in fm

    def test_firma_id(self):
        fm = _frontmatter("hukuk", "degerlendirme", "Test", firma_id="abc-123")
        assert "firma_id: abc-123" in fm

    def test_ekstra_meta(self):
        fm = _frontmatter("aga", "analiz", "Test", ekstra={"versiyon": "2.8.12"})
        assert "versiyon: 2.8.12" in fm


class TestKaydet:
    """Cikti kaydetme — dosya, klasor, manifest."""

    def test_dosya_olusur(self, tmp_path, monkeypatch):
        monkeypatch.setattr("ragip_output.get_root", lambda: str(tmp_path))

        yol = kaydet("hesap", "rapor", "Geneks Kimya", "# Test Raporu\n\nIcerik.")
        dosya = tmp_path / yol
        assert dosya.exists()
        icerik = dosya.read_text("utf-8")
        assert "---" in icerik
        assert "agent: hesap" in icerik
        assert "# Test Raporu" in icerik

    def test_firma_klasor_yapisi(self, tmp_path, monkeypatch):
        monkeypatch.setattr("ragip_output.get_root", lambda: str(tmp_path))

        yol = kaydet("arastirma", "dis-veri", "GÜVEN PRES DÖKÜM SAN.", "icerik")
        # Firma slug klasoru olusturulmali
        assert "guven_pres_dokum" in yol
        # Ay klasoru olusturulmali
        ay = datetime.now().strftime("%Y-%m")
        assert ay in yol

    def test_dosya_adi_formati(self, tmp_path, monkeypatch):
        monkeypatch.setattr("ragip_output.get_root", lambda: str(tmp_path))

        yol = kaydet("hukuk", "degerlendirme", "Test Firma", "icerik")
        dosya_adi = Path(yol).name
        # YYYYMMDD_HHMMSS-agent-skill-firma.md
        assert "-hukuk-degerlendirme-test_firma.md" in dosya_adi

    def test_manifest_guncellenir(self, tmp_path, monkeypatch):
        monkeypatch.setattr("ragip_output.get_root", lambda: str(tmp_path))

        kaydet("hesap", "rapor", "Firma A", "icerik1")
        kaydet("hukuk", "degerlendirme", "Firma B", "icerik2")

        manifest = tmp_path / "data" / "RAGIP_AGA" / ".ciktilar_manifest.jsonl"
        assert manifest.exists()
        satirlar = manifest.read_text("utf-8").strip().split("\n")
        assert len(satirlar) == 2

        k1 = json.loads(satirlar[0])
        assert k1["agent"] == "hesap"
        assert k1["firma"] == "Firma A"
        assert "dosya" in k1
        assert "tarih" in k1

    def test_frontmatter_eklenir(self, tmp_path, monkeypatch):
        monkeypatch.setattr("ragip_output.get_root", lambda: str(tmp_path))

        yol = kaydet("aga", "analiz", "Test", "# Baslik\n\nParagraf.",
                      firma_id="abc-def", ekstra_meta={"kaynak": "D365"})
        dosya = tmp_path / yol
        icerik = dosya.read_text("utf-8")
        assert icerik.startswith("---\n")
        assert "firma_id: abc-def" in icerik
        assert "kaynak: D365" in icerik
        assert "# Baslik" in icerik


class TestSonCikti:
    """Manifest sorgulama."""

    def test_firma_filtresi(self, tmp_path, monkeypatch):
        monkeypatch.setattr("ragip_output.get_root", lambda: str(tmp_path))

        kaydet("hesap", "rapor", "Geneks Kimya", "a")
        kaydet("hesap", "rapor", "Plastay", "b")
        kaydet("hukuk", "degerlendirme", "Geneks Kimya", "c")

        sonuclar = son_cikti(firma="Geneks")
        assert len(sonuclar) == 2
        assert all("geneks" in s["firma"].lower() for s in sonuclar)

    def test_agent_filtresi(self, tmp_path, monkeypatch):
        monkeypatch.setattr("ragip_output.get_root", lambda: str(tmp_path))

        kaydet("hesap", "rapor", "A", "x")
        kaydet("hukuk", "degerlendirme", "A", "y")

        sonuclar = son_cikti(agent="hukuk")
        assert len(sonuclar) == 1
        assert sonuclar[0]["agent"] == "hukuk"

    def test_limit(self, tmp_path, monkeypatch):
        monkeypatch.setattr("ragip_output.get_root", lambda: str(tmp_path))

        for i in range(10):
            kaydet("hesap", "rapor", f"Firma{i}", f"icerik{i}")

        sonuclar = son_cikti(limit=3)
        assert len(sonuclar) == 3

    def test_bos_manifest(self, tmp_path, monkeypatch):
        monkeypatch.setattr("ragip_output.get_root", lambda: str(tmp_path))
        assert son_cikti() == []


class TestVeriTazeligi:
    """t-factor — veri yaslanma kontrolu."""

    def test_taze_veri(self, tmp_path, monkeypatch):
        monkeypatch.setattr("ragip_output.get_root", lambda: str(tmp_path))
        kaydet("hesap", "rapor", "Firma A", "icerik")

        sonuclar = veri_tazeligi(firma="Firma A")
        assert len(sonuclar) == 1
        assert sonuclar[0]["durum"] == "taze"
        assert sonuclar[0]["uyari"] is None

    def test_bayat_veri(self, tmp_path, monkeypatch):
        """Manifest'e eski tarihli kayit ekleyerek bayat veri simule et."""
        monkeypatch.setattr("ragip_output.get_root", lambda: str(tmp_path))

        # Once normal kaydet (manifest olusur)
        kaydet("hesap", "rapor", "Firma B", "icerik")

        # Manifest'e eski tarihli kayit elle ekle
        import json
        from ragip_output import _manifest_path
        manifest = _manifest_path()
        eski_kayit = {
            "firma": "Firma B",
            "firma_slug": "firma_b",
            "agent": "hesap",
            "skill": "rapor",
            "dosya": "eski.md",
            "tarih": "2025-01-01T00:00:00",
            "boyut": 100,
        }
        with open(manifest, "a", encoding="utf-8") as f:
            f.write(json.dumps(eski_kayit) + "\n")

        sonuclar = veri_tazeligi(firma="Firma B")
        bayat = [s for s in sonuclar if s["durum"] == "bayat"]
        assert len(bayat) >= 1
        assert bayat[0]["uyari"] is not None
        assert "gun once" in bayat[0]["uyari"]

    def test_agent_bazli_esikler(self, tmp_path, monkeypatch):
        """Hukuk verileri daha yavas yaslanir."""
        monkeypatch.setattr("ragip_output.get_root", lambda: str(tmp_path))

        import json
        from ragip_output import _manifest_path

        # 40 gunluk hesap verisi → orta (esik: 7 gun taze, 30 gun orta)
        # 40 gunluk hukuk verisi → taze (esik: 30 gun taze, 90 gun orta)
        manifest = _manifest_path()
        manifest.parent.mkdir(parents=True, exist_ok=True)

        from datetime import timedelta
        eski = (datetime.now() - timedelta(days=40)).isoformat()

        for agent in ["hesap", "hukuk"]:
            with open(manifest, "a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "firma": "Test", "firma_slug": "test",
                    "agent": agent, "skill": "rapor",
                    "dosya": f"{agent}.md", "tarih": eski, "boyut": 50,
                }) + "\n")

        sonuclar = veri_tazeligi(firma="Test")
        hesap = [s for s in sonuclar if s["agent"] == "hesap"][0]
        hukuk = [s for s in sonuclar if s["agent"] == "hukuk"][0]

        # hesap 40 gun = bayat (taze=7, orta=30, 40 > 30 = bayat)
        assert hesap["durum"] == "bayat"
        # hukuk 40 gun = orta (taze=30, orta=90, 30 < 40 < 90 = orta)
        assert hukuk["durum"] == "orta"

    def test_tazelik_ozeti_formati(self, tmp_path, monkeypatch):
        monkeypatch.setattr("ragip_output.get_root", lambda: str(tmp_path))
        kaydet("hesap", "rapor", "Test", "icerik")

        ozet = tazelik_ozeti(firma="Test")
        assert "Veri Tazeligi" in ozet
        assert "[OK]" in ozet

    def test_bos_firma(self, tmp_path, monkeypatch):
        monkeypatch.setattr("ragip_output.get_root", lambda: str(tmp_path))
        ozet = tazelik_ozeti(firma="Olmayan Firma")
        assert "ilk analiz" in ozet


class TestParmakIzi:
    """Fingerprint hesaplama."""

    def test_deterministik(self):
        h1 = _parmak_izi("hesap", "rapor", "icerik A")
        h2 = _parmak_izi("hesap", "rapor", "icerik A")
        assert h1 == h2

    def test_farkli_icerik_farkli_hash(self):
        h1 = _parmak_izi("hesap", "rapor", "icerik A")
        h2 = _parmak_izi("hesap", "rapor", "icerik B")
        assert h1 != h2

    def test_farkli_agent_farkli_hash(self):
        h1 = _parmak_izi("hesap", "rapor", "x")
        h2 = _parmak_izi("hukuk", "rapor", "x")
        assert h1 != h2

    def test_farkli_skill_farkli_hash(self):
        h1 = _parmak_izi("hesap", "rapor", "x")
        h2 = _parmak_izi("hesap", "analiz", "x")
        assert h1 != h2

    def test_format(self):
        h = _parmak_izi("a", "b", "c")
        assert h.startswith("sha256:")
        assert len(h) == 7 + 64  # "sha256:" + 64 hex


class TestDedup:
    """Idempotency — ayni ciktiyi tekrar yazmama."""

    def test_ayni_cikti_dedup(self, tmp_path, monkeypatch):
        """Ayni agent+skill+icerik ile 2 kez kaydet → 1 dosya."""
        monkeypatch.setattr("ragip_output.get_root", lambda: str(tmp_path))

        yol1 = kaydet("hesap", "rapor", "Firma A", "ayni icerik")
        yol2 = kaydet("hesap", "rapor", "Firma A", "ayni icerik")
        assert yol1 == yol2

        # Manifest'te sadece 1 kayit olmali
        from ragip_output import _manifest_path
        manifest = _manifest_path()
        satirlar = [l for l in manifest.read_text('utf-8').strip().split('\n') if l.strip()]
        assert len(satirlar) == 1

    def test_farkli_icerik_yeni_dosya(self, tmp_path, monkeypatch):
        monkeypatch.setattr("ragip_output.get_root", lambda: str(tmp_path))

        yol1 = kaydet("hesap", "rapor", "Firma A", "icerik 1")
        yol2 = kaydet("hesap", "rapor", "Firma A", "icerik 2")
        # Farkli icerik → dedup engellemez, dosya yazilir
        # Ayni saniyede olursa dosya adi ayni olabilir, manifest'te 2 kayit olmali
        from ragip_output import _manifest_path
        manifest = _manifest_path()
        satirlar = [l for l in manifest.read_text('utf-8').strip().split('\n') if l.strip()]
        assert len(satirlar) == 2
        k1 = json.loads(satirlar[0])
        k2 = json.loads(satirlar[1])
        assert k1['parmak_izi'] != k2['parmak_izi']

    def test_dedup_devre_disi(self, tmp_path, monkeypatch):
        """dedup=False ile her zaman yeni dosya yazilir."""
        monkeypatch.setattr("ragip_output.get_root", lambda: str(tmp_path))

        yol1 = kaydet("hesap", "rapor", "Firma", "icerik", dedup=False)
        import time; time.sleep(1.1)  # timestamp farki icin
        yol2 = kaydet("hesap", "rapor", "Firma", "icerik", dedup=False)
        assert yol1 != yol2

    def test_manifest_parmak_izi_alani(self, tmp_path, monkeypatch):
        """Manifest entry'de parmak_izi alani bulunur."""
        monkeypatch.setattr("ragip_output.get_root", lambda: str(tmp_path))

        kaydet("hesap", "rapor", "Firma", "icerik")
        from ragip_output import _manifest_path
        manifest = _manifest_path()
        kayit = json.loads(manifest.read_text('utf-8').strip().split('\n')[0])
        assert "parmak_izi" in kayit
        assert kayit["parmak_izi"].startswith("sha256:")

    def test_eski_manifest_uyumlu(self, tmp_path, monkeypatch):
        """Parmak_izi olmayan eski manifest kayitlari hata vermez."""
        monkeypatch.setattr("ragip_output.get_root", lambda: str(tmp_path))

        # Eski format manifest entry (parmak_izi yok)
        from ragip_output import _manifest_path
        manifest = _manifest_path()
        manifest.parent.mkdir(parents=True, exist_ok=True)
        eski = {"firma": "X", "agent": "hesap", "skill": "rapor",
                "dosya": "eski.md", "tarih": datetime.now().isoformat(), "boyut": 10}
        manifest.write_text(json.dumps(eski) + '\n', encoding='utf-8')

        # Yeni kaydet calismali (eski kayitla eslesmez)
        yol = kaydet("hesap", "rapor", "X", "yeni icerik")
        assert yol  # dosya olusturuldu

    def test_dedup_penceresi(self, tmp_path, monkeypatch):
        """24 saat onceki kayit dedup'a takilmaz."""
        monkeypatch.setattr("ragip_output.get_root", lambda: str(tmp_path))

        # Once bir kayit olustur
        kaydet("hesap", "rapor", "F", "icerik X")

        # Manifest'teki tarihi 25 saat oncesine cek
        from ragip_output import _manifest_path
        manifest = _manifest_path()
        from datetime import timedelta
        eski_tarih = (datetime.now() - timedelta(hours=25)).isoformat()
        satir = manifest.read_text('utf-8').strip()
        kayit = json.loads(satir)
        kayit['tarih'] = eski_tarih
        manifest.write_text(json.dumps(kayit, ensure_ascii=False) + '\n', encoding='utf-8')

        # Ayni icerik tekrar yazilmali (24h doldu)
        yol = kaydet("hesap", "rapor", "F", "icerik X")
        satirlar = [l for l in manifest.read_text('utf-8').strip().split('\n') if l.strip()]
        assert len(satirlar) == 2  # 2 kayit (eski + yeni)

    def test_pii_temizle(self, tmp_path, monkeypatch):
        """pii_temizle=True ile manifest'te firma hash'lenir."""
        monkeypatch.setattr("ragip_output.get_root", lambda: str(tmp_path))

        kaydet("hesap", "rapor", "Geneks Kimya", "icerik", pii_temizle=True)
        from ragip_output import _manifest_path
        manifest = _manifest_path()
        kayit = json.loads(manifest.read_text('utf-8').strip().split('\n')[0])
        # Firma alani hash'lenmis olmali
        assert kayit["firma"].startswith("h:")
        # Agent/skill temizlenmemis
        assert kayit["agent"] == "hesap"
