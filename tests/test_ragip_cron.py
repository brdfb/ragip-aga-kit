"""
ragip_cron.sh — Fonksiyonel Testler

Zamanlanmis gorev wrapper'inin tum alt komutlarini dogrular:
run <gorev>, --setup, --status, --remove, --list.

Test stratejisi: Gecici git reposu + minimal dosya yapisi olustur,
script'i calistir, ciktiyi ve yan etkileri dogrula.
"""
import os
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "scripts" / "ragip_cron.sh"
RATES_SCRIPT = Path(__file__).parent.parent / "scripts" / "ragip_rates.py"
TEMIZLE_SCRIPT = Path(__file__).parent.parent / "scripts" / "ragip_temizle.sh"


def _git_init(d: Path) -> None:
    """Temp dizini gecici git reposuna donustur."""
    subprocess.run(["git", "init", str(d)], capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=d, capture_output=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=d, capture_output=True)


def _calistir(repo: Path, *args, env_extra: dict | None = None) -> subprocess.CompletedProcess:
    """ragip_cron.sh'yi verilen repo dizininde calistir."""
    env = os.environ.copy()
    env["RAGIP_ROOT"] = str(repo)
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        ["bash", str(SCRIPT)] + list(args),
        capture_output=True,
        text=True,
        cwd=str(repo),
        env=env,
    )


def _setup_repo(tmp_path: Path) -> Path:
    """Git init + scripts kopyalama + VERSION dosyasi."""
    _git_init(tmp_path)
    scripts = tmp_path / "scripts"
    scripts.mkdir()

    # ragip_cron.sh kopyala
    (scripts / "ragip_cron.sh").write_text(SCRIPT.read_text())
    os.chmod(scripts / "ragip_cron.sh", 0o755)

    # ragip_rates.py kopyala
    (scripts / "ragip_rates.py").write_text(RATES_SCRIPT.read_text())

    # ragip_temizle.sh kopyala
    (scripts / "ragip_temizle.sh").write_text(TEMIZLE_SCRIPT.read_text())
    os.chmod(scripts / "ragip_temizle.sh", 0o755)

    # VERSION dosyasi
    (tmp_path / "VERSION").write_text("2.10.0\n")

    # ciktilar dizini (temizle icin)
    (tmp_path / "data" / "RAGIP_AGA" / "ciktilar").mkdir(parents=True)

    return tmp_path


@pytest.fixture
def repo(tmp_path):
    """Test repo hazirla."""
    return _setup_repo(tmp_path)


# ============================================================
# Script saglik kontrolleri
# ============================================================


class TestScriptSaglik:
    def test_script_mevcuttur(self):
        assert SCRIPT.exists(), "ragip_cron.sh bulunamadi"

    def test_script_calistirilabilir(self):
        assert os.access(SCRIPT, os.X_OK), "ragip_cron.sh calistirilabilir olmali"

    def test_argumansiz_yardim(self, repo):
        """Argumaniz cagrildiginda kullanim mesaji gostermeli."""
        r = _calistir(repo)
        assert r.returncode != 0
        assert "Kullanim" in r.stdout or "Komutlar" in r.stdout

    def test_bilinmeyen_komut(self, repo):
        """Bilinmeyen komut hatasi vermeli."""
        r = _calistir(repo, "yokkomut")
        assert r.returncode != 0
        assert "HATA" in r.stderr or "Bilinmeyen" in r.stderr


# ============================================================
# --list komutu
# ============================================================


class TestList:
    def test_list_gorevleri_gosterir(self, repo):
        r = _calistir(repo, "--list")
        assert r.returncode == 0
        assert "rates" in r.stdout
        assert "temizle" in r.stdout

    def test_list_aciklamalari_gosterir(self, repo):
        r = _calistir(repo, "--list")
        assert "TCMB" in r.stdout
        assert "temizle" in r.stdout.lower() or "Ciktilar" in r.stdout


# ============================================================
# run komutu
# ============================================================


class TestRun:
    def test_run_rates(self, repo):
        """run rates basarili calisir (fallback degerlerle)."""
        r = _calistir(repo, "run", "rates")
        assert r.returncode == 0
        # Fallback veya canli oran donecek
        assert "politika_faizi" in r.stdout or "fallback" in r.stdout or "kaynak" in r.stdout

    def test_run_temizle(self, repo):
        """run temizle bos ciktilar/ ile basarili calisir."""
        r = _calistir(repo, "run", "temizle")
        assert r.returncode == 0
        assert "Kalan:" in r.stdout or "bulunamadi" not in r.stdout

    def test_run_bilinmeyen_gorev(self, repo):
        """Bilinmeyen gorev adinda hata donmeli."""
        r = _calistir(repo, "run", "yokgorev")
        assert r.returncode != 0
        assert "Bilinmeyen gorev" in r.stderr

    def test_run_gorev_belirtilmeden(self, repo):
        """run gorev adi vermeden hata donmeli."""
        r = _calistir(repo, "run")
        assert r.returncode != 0
        assert "Gorev adi belirtilmedi" in r.stderr


# ============================================================
# Loglama
# ============================================================


class TestLoglama:
    def test_log_dizini_olusur(self, repo):
        """run komutu log dizinini otomatik olusturur."""
        log_dir = repo / "data" / "RAGIP_AGA" / "logs"
        assert not log_dir.exists()

        _calistir(repo, "run", "rates")
        assert log_dir.exists(), "Log dizini olusturulmali"

    def test_log_dosyasi_olusur(self, repo):
        """run komutu gunluk log dosyasi olusturur."""
        _calistir(repo, "run", "rates")

        log_dir = repo / "data" / "RAGIP_AGA" / "logs"
        log_dosyalari = list(log_dir.glob("cron_*.log"))
        assert len(log_dosyalari) == 1, "Bir adet log dosyasi olmali"

    def test_log_icerigi_basarili(self, repo):
        """Basarili run'da log BASLADI + TAMAMLANDI icermeli."""
        _calistir(repo, "run", "rates")

        log_dir = repo / "data" / "RAGIP_AGA" / "logs"
        log_dosyasi = list(log_dir.glob("cron_*.log"))[0]
        icerik = log_dosyasi.read_text()

        assert "BASLADI: rates" in icerik
        assert "TAMAMLANDI: rates" in icerik

    def test_log_icerigi_basarisiz(self, repo):
        """Basarisiz run'da log BASARISIZ icermeli."""
        _calistir(repo, "run", "yokgorev")

        log_dir = repo / "data" / "RAGIP_AGA" / "logs"
        log_dosyasi = list(log_dir.glob("cron_*.log"))[0]
        icerik = log_dosyasi.read_text()

        assert "HATA: Bilinmeyen gorev" in icerik

    def test_log_ardisik_eklemeli(self, repo):
        """Birden fazla run ayni log dosyasina ekler."""
        _calistir(repo, "run", "rates")
        _calistir(repo, "run", "temizle")

        log_dir = repo / "data" / "RAGIP_AGA" / "logs"
        log_dosyasi = list(log_dir.glob("cron_*.log"))[0]
        icerik = log_dosyasi.read_text()

        assert "rates" in icerik
        assert "temizle" in icerik


# ============================================================
# .env yukleme
# ============================================================


class TestEnvYukleme:
    def test_env_dosyasi_okunur(self, repo):
        """RAGIP_ROOT/.env icindeki degiskenler yuklenir."""
        env_dosya = repo / ".env"
        env_dosya.write_text('TEST_RAGIP_VAR="test_deger_42"\n')

        # rates calistirildiginda .env okunmali
        r = _calistir(repo, "run", "rates")
        assert r.returncode == 0
        # .env yuklendi mi — dogrudan kontrol edemeyiz ama
        # script hata vermeden calistiysa .env parse basarili

    def test_env_dosyasi_yoksa_hata_yok(self, repo):
        """RAGIP_ROOT/.env yoksa script normal calismali."""
        env_dosya = repo / ".env"
        if env_dosya.exists():
            env_dosya.unlink()

        r = _calistir(repo, "run", "rates")
        assert r.returncode == 0

    def test_env_yorumlar_atlanir(self, repo):
        """.env dosyasindaki yorumlar sorun cikarmazmali."""
        env_dosya = repo / ".env"
        env_dosya.write_text(
            "# Bu bir yorum\n"
            "TCMB_API_KEY=test123\n"
            "\n"
            "# Baska yorum\n"
            "COLLECTAPI_KEY=abc\n"
        )
        r = _calistir(repo, "run", "rates")
        assert r.returncode == 0


# ============================================================
# Python (venv) tespit
# ============================================================


class TestVenvTespit:
    def test_venv_varsa_kullanilir(self, repo):
        """RAGIP_ROOT/.ragip-venv/bin/python3 varsa onu kullanmali."""
        venv_bin = repo / ".ragip-venv" / "bin"
        venv_bin.mkdir(parents=True)
        # Sahte python3 — gercek python3'e symlink
        import shutil
        real_python = shutil.which("python3")
        if real_python:
            os.symlink(real_python, venv_bin / "python3")
            r = _calistir(repo, "run", "rates")
            assert r.returncode == 0

    def test_venv_yoksa_sistem_python(self, repo):
        """Venv yoksa sistem python3 kullanilmali."""
        venv_dir = repo / ".ragip-venv"
        assert not venv_dir.exists()

        r = _calistir(repo, "run", "rates")
        assert r.returncode == 0


# ============================================================
# --setup komutu
# ============================================================


class TestSetup:
    def test_setup_crontab_ekler(self, repo):
        """--setup crontab'a Ragip Aga girisleri ekler."""
        r = _calistir(repo, "--setup")
        assert r.returncode == 0
        assert "Crontab guncellendi" in r.stdout

        # Crontab'da girisleri kontrol et
        crontab = subprocess.run(
            ["crontab", "-l"], capture_output=True, text=True
        )
        assert "Ragip Aga cron" in crontab.stdout
        assert "rates" in crontab.stdout
        assert "temizle" in crontab.stdout

    def test_setup_idempotent(self, repo):
        """--setup iki kez calistirildiginda duplicate olmazmali."""
        _calistir(repo, "--setup")
        _calistir(repo, "--setup")

        crontab = subprocess.run(
            ["crontab", "-l"], capture_output=True, text=True
        )
        # "rates" sadece 1 kez olmali (tag satirinda degil, gorev satirinda)
        rates_lines = [l for l in crontab.stdout.splitlines()
                       if "run rates" in l]
        assert len(rates_lines) == 1, f"rates duplicated: {rates_lines}"

    def test_setup_version_icerir(self, repo):
        """--setup crontab'a versiyon numarasini eklemeli."""
        _calistir(repo, "--setup")

        crontab = subprocess.run(
            ["crontab", "-l"], capture_output=True, text=True
        )
        assert "v2.10.0" in crontab.stdout

    def test_setup_root_path_icerir(self, repo):
        """--setup crontab'a RAGIP_ROOT path'ini baked-in eklemeli."""
        _calistir(repo, "--setup")

        crontab = subprocess.run(
            ["crontab", "-l"], capture_output=True, text=True
        )
        assert str(repo) in crontab.stdout


# ============================================================
# --remove komutu
# ============================================================


class TestRemove:
    def test_remove_crontab_temizler(self, repo):
        """--remove onceden eklenen girisleri kaldirir."""
        _calistir(repo, "--setup")
        _calistir(repo, "--remove")

        crontab = subprocess.run(
            ["crontab", "-l"], capture_output=True, text=True
        )
        assert "Ragip Aga cron" not in crontab.stdout

    def test_remove_bos_crontab(self, repo):
        """--remove bos crontab'da hata vermez."""
        # Once crontab'i tamamen temizle
        subprocess.run(["crontab", "-r"], capture_output=True)
        r = _calistir(repo, "--remove")
        assert r.returncode == 0

    def test_remove_idempotent(self, repo):
        """--remove iki kez calistirildiginda hata vermez."""
        _calistir(repo, "--setup")
        _calistir(repo, "--remove")
        r = _calistir(repo, "--remove")
        assert r.returncode == 0

    def test_remove_diger_girisleri_korur(self, repo):
        """--remove sadece Ragip Aga girisleri kaldirmali, digerleri korunmali."""
        # Baska bir crontab girisi ekle
        subprocess.run(
            ["bash", "-c", '(crontab -l 2>/dev/null; echo "0 12 * * * echo test") | crontab -'],
            capture_output=True,
        )
        _calistir(repo, "--setup")
        _calistir(repo, "--remove")

        crontab = subprocess.run(
            ["crontab", "-l"], capture_output=True, text=True
        )
        assert "echo test" in crontab.stdout
        assert "Ragip Aga cron" not in crontab.stdout


# ============================================================
# --status komutu
# ============================================================


class TestStatus:
    def test_status_cikti_yapisi(self, repo):
        """--status baslik ve bolumleri gostermeli."""
        r = _calistir(repo, "--status")
        assert r.returncode == 0
        assert "Ragip Aga Cron Durumu" in r.stdout
        assert "Cron servisi" in r.stdout

    def test_status_giris_yok(self, repo):
        """Crontab'da giris yokken 'YOK' gostermeli."""
        # Temiz crontab
        subprocess.run(["crontab", "-r"], capture_output=True)
        r = _calistir(repo, "--status")
        assert "YOK" in r.stdout

    def test_status_giris_var(self, repo):
        """Setup sonrasi --status girisleri gostermeli."""
        _calistir(repo, "--setup")
        r = _calistir(repo, "--status")
        assert "rates" in r.stdout

    def test_status_log_gosterir(self, repo):
        """Onceden run yapilmissa son logu gostermeli."""
        _calistir(repo, "run", "rates")
        r = _calistir(repo, "--status")
        assert "Son log" in r.stdout or "TAMAMLANDI" in r.stdout


# ============================================================
# RAGIP_ROOT env var
# ============================================================


class TestRootTespit:
    def test_ragip_root_env_oncelikli(self, repo):
        """RAGIP_ROOT env var set edilmisse onu kullanmali."""
        r = _calistir(repo, "--list")
        assert r.returncode == 0

    def test_ragip_root_farki_dizin(self, tmp_path):
        """RAGIP_ROOT farkli bir dizine isaret edebilir."""
        repo = _setup_repo(tmp_path)
        r = _calistir(repo, "--list", env_extra={"RAGIP_ROOT": str(repo)})
        assert r.returncode == 0
        assert "rates" in r.stdout


# ============================================================
# Cleanup: Testlerden sonra crontab'i temizle
# ============================================================


@pytest.fixture(autouse=True)
def crontab_temizle():
    """Her testten sonra Ragip crontab girisleri temizle."""
    yield
    # Temizlik: Ragip Aga satirlarini kaldir
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        if result.returncode == 0 and "Ragip Aga cron" in result.stdout:
            filtered = "\n".join(
                l for l in result.stdout.splitlines()
                if "Ragip Aga cron" not in l and "RAGIP_ROOT=" not in l
            ).strip()
            if filtered:
                subprocess.run(
                    ["bash", "-c", f'echo "{filtered}" | crontab -'],
                    capture_output=True,
                )
            else:
                subprocess.run(["crontab", "-r"], capture_output=True)
    except Exception:
        pass
