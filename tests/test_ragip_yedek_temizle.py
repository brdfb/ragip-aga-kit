"""Yedek temizleme scripti testleri (v2.17.1)."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

KIT_DIR = Path(__file__).resolve().parents[1]
SCRIPT = KIT_DIR / "scripts" / "ragip_yedek_temizle.sh"


def _init_repo(path: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", "init"], cwd=path, check=True)


def _install(repo: Path) -> None:
    res = subprocess.run(
        ["bash", str(KIT_DIR / "install.sh")],
        cwd=repo, input="n\nn\n", text=True, capture_output=True, timeout=30
    )
    assert res.returncode == 0, res.stderr


def _run(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        cwd=repo, text=True, capture_output=True, timeout=30
    )


class TestYedekTemizle:
    def test_script_var_ve_calisabilir(self):
        assert SCRIPT.exists(), f"Script eksik: {SCRIPT}"
        assert SCRIPT.stat().st_mode & 0o111, "Script executable degil"

    def test_help_flag(self, tmp_path):
        repo = tmp_path / "repo"
        repo.mkdir()
        _init_repo(repo)
        _install(repo)
        result = _run(repo, "--help")
        assert result.returncode == 0
        assert "Yedek temizleme" in result.stdout or "yardim" in result.stdout.lower()

    def test_sahte_yedek_silinir(self, tmp_path):
        """Kit ile ayni icerige sahip yedek 'sahte' say + --apply ile silinir."""
        repo = tmp_path / "repo"
        repo.mkdir()
        _init_repo(repo)
        _install(repo)

        # Mevcut kit dosyasini al, ayni icerikle bir 'yedek' olustur
        target = repo / ".claude/agents/ragip-aga.md"
        sahte_yedek = target.parent / f"{target.name}.kullanici-yedek-20260101"
        sahte_yedek.write_bytes(target.read_bytes())  # Ayni icerik
        assert sahte_yedek.exists()

        # Dry-run — silmemeli
        dry = _run(repo)
        assert dry.returncode == 0
        assert "SAHTE" in dry.stdout
        assert sahte_yedek.exists(), "Dry-run yedegi silmemeli"

        # Apply — silmeli
        applied = _run(repo, "--apply")
        assert applied.returncode == 0
        assert not sahte_yedek.exists(), "--apply sahte yedegi silmeli"

    def test_gercek_yedek_korunur(self, tmp_path):
        """Kit ile FARKLI icerige sahip yedek 'gercek ozellestirme' say + silinmez."""
        repo = tmp_path / "repo"
        repo.mkdir()
        _init_repo(repo)
        _install(repo)

        target = repo / ".claude/agents/ragip-aga.md"
        gercek_yedek = target.parent / f"{target.name}.kullanici-yedek-20260101"
        # Farkli icerik — gercek kullanici ozellestirmesi
        gercek_yedek.write_text(target.read_text() + "\n# Kullanici notu\n")
        assert gercek_yedek.exists()

        # --apply ile bile silmemeli
        result = _run(repo, "--apply")
        assert result.returncode == 0
        assert "KORU" in result.stdout or "KORUNACAK" in result.stdout
        assert gercek_yedek.exists(), "Gercek ozellestirme yedegi silinmemeli"

    def test_bos_repo_temiz_rapor(self, tmp_path):
        """Yedek yoksa temiz rapor — sifir aksiyon."""
        repo = tmp_path / "repo"
        repo.mkdir()
        _init_repo(repo)
        _install(repo)
        result = _run(repo)
        assert result.returncode == 0
        assert "bulunamadi" in result.stdout.lower() or "temiz" in result.stdout.lower()

    def test_manifest_yoksa_hata(self, tmp_path):
        """Ragip Aga kurulu olmayan repoda calismamali."""
        repo = tmp_path / "repo"
        repo.mkdir()
        _init_repo(repo)
        # install YAPMA
        result = _run(repo)
        assert result.returncode != 0
        assert "Manifest" in result.stdout or "Manifest" in result.stderr
