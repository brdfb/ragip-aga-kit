"""
ragip_temizle.sh — Fonksiyonel Testler

Script mantigi: 90 gun+ eski dosyalari sil, toplam > 200 ise en eskilerden sil.
--dry-run: listeleme yapar, silme yapmaz.

Test stratejisi: Gecici git reposu olustur, ciktilar/ altinda dosyalar yarat,
script'i calistir, sonucu dogrula.
"""
import os
import subprocess
import time
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "scripts" / "ragip_temizle.sh"
GUN_SANIYE = 24 * 3600


def _git_init(d: Path) -> None:
    """Temp dizini gecici git reposuna donustur."""
    subprocess.run(["git", "init", str(d)], capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=d, capture_output=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=d, capture_output=True)


def _md(d: Path, isim: str, yas_gun: float = 0) -> Path:
    """Belirtilen yaslanma suresiyle .md dosyasi olustur."""
    f = d / isim
    f.write_text(f"# {isim}\n", encoding="utf-8")
    if yas_gun > 0:
        gecmis = time.time() - yas_gun * GUN_SANIYE
        os.utime(str(f), (gecmis, gecmis))
    return f


def _calistir(repo: Path, *args) -> subprocess.CompletedProcess:
    """ragip_temizle.sh'yi verilen repo dizininde calistir."""
    return subprocess.run(
        ["bash", str(SCRIPT)] + list(args),
        capture_output=True,
        text=True,
        cwd=str(repo),
    )


@pytest.fixture
def repo(tmp_path):
    """Git init + ciktilar/ dizini hazir repo."""
    _git_init(tmp_path)
    ciktilar = tmp_path / "data" / "RAGIP_AGA" / "ciktilar"
    ciktilar.mkdir(parents=True)
    return tmp_path


# --- Script saglik kontrolleri ---


class TestScriptSaglik:
    def test_script_mevcuttur(self):
        assert SCRIPT.exists(), "ragip_temizle.sh bulunamadi"

    def test_script_calistirilabilir(self):
        assert os.access(SCRIPT, os.X_OK), "ragip_temizle.sh calistirilabilir olmali"

    def test_ciktilar_yok_graceful(self, tmp_path):
        """ciktilar/ dizini yoksa sifir cikisla devam etmeli."""
        _git_init(tmp_path)
        r = _calistir(tmp_path)
        assert r.returncode == 0
        assert "bulunamadi" in r.stdout

    def test_bos_ciktilar_ok(self, repo):
        """Bos ciktilar/ dizininde sifir cikisla tamamlanmali."""
        r = _calistir(repo)
        assert r.returncode == 0
        assert "Kalan: 0 dosya" in r.stdout


# --- Yas bazli temizlik ---


class TestYasBazliTemizlik:
    def test_eski_dosyalar_silinir(self, repo):
        """91 gundan eski dosyalar silinmeli."""
        ciktilar = repo / "data" / "RAGIP_AGA" / "ciktilar"
        eski = _md(ciktilar, "eski.md", yas_gun=91)
        yeni = _md(ciktilar, "yeni.md", yas_gun=1)

        r = _calistir(repo)
        assert r.returncode == 0
        assert not eski.exists(), "91 gunluk dosya silinmeli"
        assert yeni.exists(), "1 gunluk dosya korunmali"

    def test_tam_sinirda_dosya_korunur(self, repo):
        """89 gunluk dosya (sinir altinda) silinmemeli."""
        ciktilar = repo / "data" / "RAGIP_AGA" / "ciktilar"
        sinir_alti = _md(ciktilar, "sinir_alti.md", yas_gun=89)

        r = _calistir(repo)
        assert r.returncode == 0
        assert sinir_alti.exists(), "89 gunluk dosya korunmali (sinir 90 gun)"

    def test_birden_fazla_eski_silinir(self, repo):
        """Birden fazla eski dosya hepsi silinmeli."""
        ciktilar = repo / "data" / "RAGIP_AGA" / "ciktilar"
        eskiler = [_md(ciktilar, f"eski_{i}.md", yas_gun=91 + i) for i in range(5)]
        yeniler = [_md(ciktilar, f"yeni_{i}.md", yas_gun=1) for i in range(3)]

        r = _calistir(repo)
        assert r.returncode == 0
        assert all(not f.exists() for f in eskiler), "Tum eski dosyalar silinmeli"
        assert all(f.exists() for f in yeniler), "Yeni dosyalar korunmali"

    def test_yas_cikti_mesaji(self, repo):
        """Yas bazli silme gerceklesince mesaj yazdirmali."""
        ciktilar = repo / "data" / "RAGIP_AGA" / "ciktilar"
        _md(ciktilar, "eski.md", yas_gun=95)

        r = _calistir(repo)
        assert "90 gundan eski" in r.stdout


# --- Limit bazli temizlik ---


class TestLimitBazliTemizlik:
    def test_200_altinda_silme_yok(self, repo):
        """200 dosya varsa silme gerceklesmemeli."""
        ciktilar = repo / "data" / "RAGIP_AGA" / "ciktilar"
        for i in range(200):
            _md(ciktilar, f"dosya_{i:04d}.md")

        r = _calistir(repo)
        assert r.returncode == 0
        kalan = len(list(ciktilar.glob("*.md")))
        assert kalan == 200

    def test_201_dosyada_en_eski_silinir(self, repo):
        """201 dosyada en eski 1 dosya silinmeli."""
        ciktilar = repo / "data" / "RAGIP_AGA" / "ciktilar"
        # Siralama: sort alfabetik, en kucuk isim en eski sayilir
        en_eski = _md(ciktilar, "aaaa_en_eski.md")
        for i in range(200):
            _md(ciktilar, f"dosya_{i:04d}.md")

        r = _calistir(repo)
        assert r.returncode == 0
        assert not en_eski.exists(), "En eski dosya silinmeli"
        kalan = len(list(ciktilar.glob("*.md")))
        assert kalan == 200

    def test_205_dosyada_5_silinir(self, repo):
        """205 dosyada 5 dosya silinerek 200'e indirilmeli."""
        ciktilar = repo / "data" / "RAGIP_AGA" / "ciktilar"
        fazlalar = [_md(ciktilar, f"aaa_{i:04d}.md") for i in range(5)]
        for i in range(200):
            _md(ciktilar, f"dosya_{i:04d}.md")

        r = _calistir(repo)
        assert r.returncode == 0
        kalan = len(list(ciktilar.glob("*.md")))
        assert kalan == 200
        assert "Dosya limiti asimi" in r.stdout

    def test_limit_mesaji_icerigi(self, repo):
        """Limit asiminda toplam ve fazla sayisi mesajda gozukmeli."""
        ciktilar = repo / "data" / "RAGIP_AGA" / "ciktilar"
        for i in range(203):
            _md(ciktilar, f"dosya_{i:04d}.md")

        r = _calistir(repo)
        assert "203" in r.stdout
        assert "200" in r.stdout


# --- Dry-run modu ---


class TestDryRun:
    def test_dry_run_silmez_eski(self, repo):
        """--dry-run eski dosyalari silmemeli."""
        ciktilar = repo / "data" / "RAGIP_AGA" / "ciktilar"
        eski = _md(ciktilar, "eski.md", yas_gun=91)

        r = _calistir(repo, "--dry-run")
        assert r.returncode == 0
        assert eski.exists(), "--dry-run eski dosyayi silmemeli"

    def test_dry_run_silmez_limit(self, repo):
        """--dry-run limit asiminda da silmemeli."""
        ciktilar = repo / "data" / "RAGIP_AGA" / "ciktilar"
        for i in range(205):
            _md(ciktilar, f"dosya_{i:04d}.md")

        r = _calistir(repo, "--dry-run")
        assert r.returncode == 0
        kalan = len(list(ciktilar.glob("*.md")))
        assert kalan == 205, "--dry-run hicbir dosyayi silmemeli"

    def test_dry_run_cikti_iceriyor(self, repo):
        """--dry-run silinecekleri listeleyen mesaj yazdirmali."""
        ciktilar = repo / "data" / "RAGIP_AGA" / "ciktilar"
        _md(ciktilar, "eski.md", yas_gun=91)

        r = _calistir(repo, "--dry-run")
        assert "[DRY-RUN]" in r.stdout

    def test_dry_run_bos_ciktilar(self, repo):
        """--dry-run bos dizinde de basarisiz olmamali."""
        r = _calistir(repo, "--dry-run")
        assert r.returncode == 0
        assert "Kalan: 0 dosya" in r.stdout


# --- Sadece .md dosyalari ---


class TestDosyaFiltresi:
    def test_md_olmayan_dosyalar_korunur(self, repo):
        """Script sadece .md dosyalarini silmeli, diger tipler korunmali."""
        ciktilar = repo / "data" / "RAGIP_AGA" / "ciktilar"
        eski_md = _md(ciktilar, "eski.md", yas_gun=91)
        txt_dosya = ciktilar / "veri.txt"
        txt_dosya.write_text("veri")
        gecmis = time.time() - 100 * GUN_SANIYE
        os.utime(str(txt_dosya), (gecmis, gecmis))

        r = _calistir(repo)
        assert r.returncode == 0
        assert not eski_md.exists(), "Eski .md silinmeli"
        assert txt_dosya.exists(), ".txt dosyasi korunmali"

    def test_alt_dizin_dosyalari_korunur(self, repo):
        """ciktilar/ altindaki alt dizinlerin icindeki dosyalar etkilenmemeli."""
        ciktilar = repo / "data" / "RAGIP_AGA" / "ciktilar"
        alt_dizin = ciktilar / "arsiv"
        alt_dizin.mkdir()
        alt_dosya = alt_dizin / "eski.md"
        alt_dosya.write_text("arsiv")
        gecmis = time.time() - 100 * GUN_SANIYE
        os.utime(str(alt_dosya), (gecmis, gecmis))

        r = _calistir(repo)
        assert r.returncode == 0
        assert alt_dosya.exists(), "Alt dizindeki dosya etkilenmemeli (maxdepth 1)"


# --- Tamamlandi mesaji ---


class TestCiktiMesaji:
    def test_tamamlandi_mesaji_her_zaman_var(self, repo):
        """Her kosulda 'Tamamlandi. Kalan:' mesaji olmali."""
        ciktilar = repo / "data" / "RAGIP_AGA" / "ciktilar"
        _md(ciktilar, "dosya.md")

        r = _calistir(repo)
        assert "Tamamlandi. Kalan:" in r.stdout

    def test_kalan_sayisi_dogrulugu(self, repo):
        """Kalan dosya sayisi gercekle uyusmali."""
        ciktilar = repo / "data" / "RAGIP_AGA" / "ciktilar"
        for i in range(5):
            _md(ciktilar, f"dosya_{i}.md")

        r = _calistir(repo)
        assert "Kalan: 5 dosya" in r.stdout
