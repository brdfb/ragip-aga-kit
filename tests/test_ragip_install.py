"""
Install/Update otomatik testleri.
Geçici git repoları oluşturarak install.sh ve update.sh'yi test eder.
"""
import json
import hashlib
import subprocess
from pathlib import Path

import pytest

KIT_DIR = Path(__file__).parent.parent


@pytest.fixture
def temp_repo(tmp_path):
    """Geçici git repo oluştur + fresh install yap."""
    repo = tmp_path / "test-repo"
    repo.mkdir()
    subprocess.run(
        ["git", "init"], cwd=repo, capture_output=True, check=True
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=repo, capture_output=True, check=True
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=repo, capture_output=True, check=True
    )
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "init"],
        cwd=repo, capture_output=True, check=True
    )
    result = subprocess.run(
        ["bash", str(KIT_DIR / "install.sh")],
        cwd=repo, input="n\nn\n", text=True, capture_output=True,
        timeout=30
    )
    assert result.returncode == 0, f"Install failed: {result.stderr}"
    return repo


class TestInstall:
    def test_fresh_install_creates_files(self, temp_repo):
        """Install sonrası core dosyalar mevcut olmalı"""
        assert (temp_repo / ".claude" / "agents" / "ragip-aga.md").exists()
        assert (temp_repo / ".claude" / "skills" / "ragip-firma" / "SKILL.md").exists()
        assert (temp_repo / "scripts" / "ragip_aga.py").exists()
        assert (temp_repo / "scripts" / "ragip_rates.py").exists()
        assert (temp_repo / "scripts" / "ragip_get_rates.sh").exists()
        assert (temp_repo / "scripts" / "ragip_crud.py").exists()
        assert (temp_repo / "config" / "ragip_aga.yaml").exists()
        assert (temp_repo / "config" / ".ragip_manifest.json").exists()

    def test_manifest_has_correct_structure(self, temp_repo):
        """Manifest JSON yapısı doğru olmalı"""
        manifest = json.loads(
            (temp_repo / "config" / ".ragip_manifest.json").read_text()
        )
        assert "kit_version" in manifest
        assert "installed_at" in manifest
        assert "kit_source" in manifest
        assert "files" in manifest
        assert isinstance(manifest["files"], dict)

    def test_manifest_file_count(self, temp_repo):
        """Manifest'te 20 core dosya olmalı (4 agent + 11 skill + 4 script + 1 config)"""
        manifest = json.loads(
            (temp_repo / "config" / ".ragip_manifest.json").read_text()
        )
        count = len(manifest["files"])
        assert count == 20, f"Beklenen 20 dosya, bulunan {count}: {sorted(manifest['files'].keys())}"

    def test_manifest_checksums_valid(self, temp_repo):
        """Her checksum sha256: prefix ile başlamalı ve 64 hex karakter olmalı"""
        manifest = json.loads(
            (temp_repo / "config" / ".ragip_manifest.json").read_text()
        )
        import re
        for path, checksum in manifest["files"].items():
            assert checksum.startswith("sha256:"), f"{path}: prefix yanlış"
            hex_part = checksum[len("sha256:"):]
            assert re.match(r"^[0-9a-f]{64}$", hex_part), (
                f"{path}: geçersiz checksum: {hex_part}"
            )

    def test_installed_files_match_manifest(self, temp_repo):
        """Her manifest dosyasının SHA-256'sı manifest'teki ile eşleşmeli"""
        manifest = json.loads(
            (temp_repo / "config" / ".ragip_manifest.json").read_text()
        )
        for rel_path, expected in manifest["files"].items():
            full_path = temp_repo / rel_path
            assert full_path.exists(), f"Dosya yok: {rel_path}"
            actual = "sha256:" + hashlib.sha256(full_path.read_bytes()).hexdigest()
            assert actual == expected, (
                f"{rel_path}: checksum uyumsuz (manifest: {expected}, disk: {actual})"
            )

    def test_gitignore_rules_added(self, temp_repo):
        """gitignore'da RAGIP_AGA ve ragip_cache satırları olmalı"""
        gitignore = (temp_repo / ".gitignore").read_text()
        assert "data/RAGIP_AGA/" in gitignore
        assert "scripts/.ragip_cache/" in gitignore

    def test_get_rates_sh_executable(self, temp_repo):
        """ragip_get_rates.sh çalıştırılabilir olmalı"""
        import os
        sh = temp_repo / "scripts" / "ragip_get_rates.sh"
        assert sh.exists()
        assert os.access(sh, os.X_OK), "ragip_get_rates.sh çalıştırılabilir değil"


class TestUpdate:
    def _install_fresh(self, repo_path):
        """Helper: fresh install yap."""
        result = subprocess.run(
            ["bash", str(KIT_DIR / "install.sh")],
            cwd=repo_path, input="n\nn\n", text=True, capture_output=True,
            timeout=30
        )
        assert result.returncode == 0, f"Install failed: {result.stderr}"

    def _run_update(self, repo_path, *args):
        """Helper: update çalıştır."""
        cmd = ["bash", str(KIT_DIR / "update.sh")] + list(args)
        return subprocess.run(
            cmd, cwd=repo_path, text=True, capture_output=True, timeout=30
        )

    def _create_repo(self, tmp_path, name="test-repo"):
        """Helper: git repo oluştur."""
        repo = tmp_path / name
        repo.mkdir()
        subprocess.run(["git", "init"], cwd=repo, capture_output=True, check=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=repo, capture_output=True, check=True
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=repo, capture_output=True, check=True
        )
        subprocess.run(
            ["git", "commit", "--allow-empty", "-m", "init"],
            cwd=repo, capture_output=True, check=True
        )
        return repo

    def test_same_version_rejected(self, tmp_path):
        """Aynı versiyonda update → 'zaten güncel' mesajı"""
        repo = self._create_repo(tmp_path)
        self._install_fresh(repo)
        result = self._run_update(repo)
        assert result.returncode == 0
        assert "zaten" in result.stdout.lower() or "surumunde" in result.stdout.lower()

    def test_force_same_version(self, tmp_path):
        """--force ile aynı versiyon → güncelleme yapılır"""
        repo = self._create_repo(tmp_path)
        self._install_fresh(repo)
        result = self._run_update(repo, "--force")
        assert result.returncode == 0
        # "degismedi" veya "Guncellenecek" çıktısı beklenir
        assert "GUNCELLEME" in result.stdout or "degismedi" in result.stdout.lower() or "Degismedi" in result.stdout

    def test_user_change_preserved(self, tmp_path):
        """Hedefte değiştirilen core dosya korunmalı"""
        repo = self._create_repo(tmp_path)
        self._install_fresh(repo)
        # Bir core dosyayı değiştir
        agent_file = repo / ".claude" / "agents" / "ragip-aga.md"
        original = agent_file.read_text()
        agent_file.write_text(original + "\n# Kullanıcı notu\n")
        user_hash = hashlib.sha256(agent_file.read_bytes()).hexdigest()
        # Force update yap
        result = self._run_update(repo, "--force")
        assert result.returncode == 0
        # Dosya korunmuş olmalı (kullanıcı değişikliği) veya yedeklenmiş olmalı
        current_hash = hashlib.sha256(agent_file.read_bytes()).hexdigest()
        # Ya korunmuş (aynı hash) ya da yedeklenmiş (farklı hash + .kullanici-yedek dosyası)
        if current_hash != user_hash:
            # Yedek dosya olmalı
            backups = list(agent_file.parent.glob("*.kullanici-yedek*"))
            assert len(backups) > 0, (
                "Kullanıcı değişikliği ne korundu ne de yedeklendi"
            )

    def test_deleted_file_reinstalled(self, tmp_path):
        """Hedefte silinen core dosya yeniden kurulmalı"""
        repo = self._create_repo(tmp_path)
        self._install_fresh(repo)
        # Bir core dosyayı sil
        target = repo / "scripts" / "ragip_aga.py"
        assert target.exists()
        target.unlink()
        assert not target.exists()
        # Force update yap
        result = self._run_update(repo, "--force")
        assert result.returncode == 0
        # Dosya geri yüklenmeli
        assert target.exists(), "Silinen dosya yeniden kurulmalıydı"

    def test_dry_run_no_changes(self, tmp_path):
        """--dry-run → hiçbir dosya değişmez"""
        repo = self._create_repo(tmp_path)
        self._install_fresh(repo)
        # Bir dosyayı sil (güncelleme yapılabilecek durum oluştur)
        target = repo / "scripts" / "ragip_aga.py"
        target.unlink()
        # Manifest hash'lerini kaydet
        manifest_before = (repo / "config" / ".ragip_manifest.json").read_text()
        # --dry-run --force ile çalıştır
        result = self._run_update(repo, "--force", "--dry-run")
        assert result.returncode == 0
        assert "dry-run" in result.stdout.lower() or "dry_run" in result.stdout.lower()
        # Dosya hala silinmiş olmalı (değişiklik yapılmadı)
        assert not target.exists(), "dry-run modunda dosya geri yüklenmemeli"
        # Manifest değişmemiş olmalı
        manifest_after = (repo / "config" / ".ragip_manifest.json").read_text()
        assert manifest_before == manifest_after, "dry-run modunda manifest değişmemeli"
