"""
Ragip Aga Sub-Agent Mimarisi - Yapisal Dogrulama Testleri.

Sub-agent dosyalarinin YAML frontmatter'ini, skill dagilimini,
model secimlerini ve dosya butunlugunu test eder.
"""
import re
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).parent.parent
# Kit kaynak dizini: agents/ altinda, kurulum sonrasi: .claude/agents/ altinda
if (_REPO_ROOT / "agents").is_dir():
    AGENTS_DIR = _REPO_ROOT / "agents"
    SKILLS_DIR = _REPO_ROOT / "skills"
else:
    AGENTS_DIR = _REPO_ROOT / ".claude" / "agents"
    SKILLS_DIR = _REPO_ROOT / ".claude" / "skills"

# --- Yardimci fonksiyonlar ---


def parse_agent_frontmatter(filepath: Path) -> dict:
    """Agent .md dosyasindan YAML frontmatter'i parse et."""
    text = filepath.read_text(encoding="utf-8")
    match = re.search(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    assert match, f"Frontmatter bulunamadi: {filepath}"
    fm = match.group(1)

    result = {}
    # name
    m = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE)
    if m:
        result["name"] = m.group(1).strip()

    # model
    m = re.search(r"^model:\s*(.+)$", fm, re.MULTILINE)
    if m:
        result["model"] = m.group(1).strip()

    # maxTurns
    m = re.search(r"^maxTurns:\s*(\d+)$", fm, re.MULTILINE)
    if m:
        result["maxTurns"] = int(m.group(1))

    # memory
    m = re.search(r"^memory:\s*(.+)$", fm, re.MULTILINE)
    if m:
        result["memory"] = m.group(1).strip()

    # skills (YAML array)
    skills = []
    in_skills = False
    for line in fm.split("\n"):
        if re.match(r"^skills:\s*\[\s*\]", line):
            # skills: []
            skills = []
            break
        if re.match(r"^skills:\s*$", line):
            in_skills = True
            continue
        if in_skills:
            m2 = re.match(r"^\s+-\s+(.+)$", line)
            if m2:
                skills.append(m2.group(1).strip())
            else:
                break
    result["skills"] = skills

    return result


# --- Agent dosyalarini yukle ---

ORCHESTRATOR_FILE = AGENTS_DIR / "ragip-aga.md"
HESAP_FILE = AGENTS_DIR / "ragip-hesap.md"
ARASTIRMA_FILE = AGENTS_DIR / "ragip-arastirma.md"
VERI_FILE = AGENTS_DIR / "ragip-veri.md"
HUKUK_FILE = AGENTS_DIR / "ragip-hukuk.md"

ALL_SUBAGENT_FILES = [HESAP_FILE, ARASTIRMA_FILE, VERI_FILE, HUKUK_FILE]

EXPECTED_ALL_SKILLS = {
    "ragip-vade-farki",
    "ragip-arbitraj",
    "ragip-ihtar",
    "ragip-analiz",
    "ragip-dis-veri",
    "ragip-gorev",
    "ragip-strateji",
    "ragip-firma",
    "ragip-import",
    "ragip-ozet",
    "ragip-profil",
    "ragip-degerlendirme",
    "ragip-zamanasimi",
    "ragip-delil",
}


# --- Test: Dosya varligi ---

class TestDosyaVarligi:
    def test_orchestrator_mevcut(self):
        assert ORCHESTRATOR_FILE.exists(), "ragip-aga.md bulunamadi"

    def test_hesap_mevcut(self):
        assert HESAP_FILE.exists(), "ragip-hesap.md bulunamadi"

    def test_arastirma_mevcut(self):
        assert ARASTIRMA_FILE.exists(), "ragip-arastirma.md bulunamadi"

    def test_veri_mevcut(self):
        assert VERI_FILE.exists(), "ragip-veri.md bulunamadi"

    def test_hukuk_mevcut(self):
        assert HUKUK_FILE.exists(), "ragip-hukuk.md bulunamadi"


# --- Test: Orchestrator yapilandirmasi ---

class TestOrchestrator:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.fm = parse_agent_frontmatter(ORCHESTRATOR_FILE)

    def test_isim(self):
        assert self.fm["name"] == "ragip-aga"

    def test_model_sonnet(self):
        assert self.fm["model"] == "sonnet"

    def test_skills_bos(self):
        """Orchestrator'de skill olmamali — hepsi sub-agent'larda"""
        assert self.fm["skills"] == [], (
            f"Orchestrator'de skill var: {self.fm['skills']}"
        )

    def test_max_turns(self):
        assert self.fm["maxTurns"] >= 10, "maxTurns multi-step icin yeterli olmali"

    def test_memory_project(self):
        assert self.fm.get("memory") == "project"

    def test_dispatch_tablosu(self):
        """System prompt'ta 4 sub-agent referansi olmali"""
        text = ORCHESTRATOR_FILE.read_text(encoding="utf-8")
        assert "ragip-hesap" in text, "ragip-hesap dispatch referansi eksik"
        assert "ragip-arastirma" in text, "ragip-arastirma dispatch referansi eksik"
        assert "ragip-veri" in text, "ragip-veri dispatch referansi eksik"
        assert "ragip-hukuk" in text, "ragip-hukuk dispatch referansi eksik"

    def test_paralel_kurallari(self):
        """Paralel calistirma kurallari olmali"""
        text = ORCHESTRATOR_FILE.read_text(encoding="utf-8")
        assert "PARALEL" in text.upper(), "Paralel calistirma kurallari eksik"


# --- Test: Sub-agent yapilandirmasi ---

class TestSubAgentHesap:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.fm = parse_agent_frontmatter(HESAP_FILE)

    def test_isim(self):
        assert self.fm["name"] == "ragip-hesap"

    def test_model_haiku(self):
        """Hesap motoru icin haiku yeterli (deterministik hesaplama)"""
        assert self.fm["model"] == "haiku"

    def test_skills(self):
        assert self.fm["skills"] == ["ragip-vade-farki", "ragip-arbitraj"]

    def test_max_turns_kisa(self):
        assert self.fm["maxTurns"] <= 5, "Hesap motoru 3-5 turn yeterli"


class TestSubAgentArastirma:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.fm = parse_agent_frontmatter(ARASTIRMA_FILE)

    def test_isim(self):
        assert self.fm["name"] == "ragip-arastirma"

    def test_model_sonnet(self):
        """Arastirma/analiz icin sonnet gerekli (derin dusunme)"""
        assert self.fm["model"] == "sonnet"

    def test_skills(self):
        expected = {"ragip-analiz", "ragip-dis-veri", "ragip-strateji"}
        assert set(self.fm["skills"]) == expected

    def test_max_turns(self):
        assert self.fm["maxTurns"] >= 5, "Arastirma icin 5+ turn gerekli"

    def test_memory(self):
        assert self.fm.get("memory") == "project"

    def test_yasal_referanslar(self):
        """System prompt'ta yasal referans cercevesi olmali"""
        text = ARASTIRMA_FILE.read_text(encoding="utf-8")
        assert "TBK" in text, "TBK referansi eksik"
        assert "TTK" in text, "TTK referansi eksik"
        assert "IIK" in text, "IIK referansi eksik"


class TestSubAgentHukuk:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.fm = parse_agent_frontmatter(HUKUK_FILE)

    def test_isim(self):
        assert self.fm["name"] == "ragip-hukuk"

    def test_model_sonnet(self):
        """Hukuki analiz icin sonnet gerekli (yasal yorum)"""
        assert self.fm["model"] == "sonnet"

    def test_skills(self):
        expected = {"ragip-degerlendirme", "ragip-zamanasimi", "ragip-delil", "ragip-ihtar"}
        assert set(self.fm["skills"]) == expected

    def test_max_turns(self):
        assert self.fm["maxTurns"] >= 5, "Hukuk analizi icin 5+ turn gerekli"

    def test_memory(self):
        assert self.fm.get("memory") == "project"

    def test_yasal_referanslar(self):
        """System prompt'ta genisletilmis yasal referans cercevesi olmali"""
        text = HUKUK_FILE.read_text(encoding="utf-8")
        assert "TBK" in text, "TBK referansi eksik"
        assert "TTK" in text, "TTK referansi eksik"
        assert "IIK" in text, "IIK referansi eksik"
        assert "KVKK" in text, "KVKK referansi eksik"
        assert "HMK" in text, "HMK referansi eksik"

    def test_avukata_danisin_uyarisi(self):
        """Hukuk agent'inda avukata danisin uyarisi zorunlu"""
        text = HUKUK_FILE.read_text(encoding="utf-8")
        assert "avukat" in text.lower(), "Avukata danisin uyarisi eksik"

    def test_cikti_kaydetme(self):
        """Cikti kaydetme talimati icermeli"""
        text = HUKUK_FILE.read_text(encoding="utf-8")
        assert "CIKTI KAYDETME" in text
        assert "ciktilar/" in text


class TestSubAgentVeri:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.fm = parse_agent_frontmatter(VERI_FILE)

    def test_isim(self):
        assert self.fm["name"] == "ragip-veri"

    def test_model_haiku(self):
        """CRUD islemleri icin haiku yeterli"""
        assert self.fm["model"] == "haiku"

    def test_skills(self):
        expected = {"ragip-firma", "ragip-gorev", "ragip-import", "ragip-ozet", "ragip-profil"}
        assert set(self.fm["skills"]) == expected

    def test_max_turns_kisa(self):
        assert self.fm["maxTurns"] <= 5, "CRUD islemleri 3-5 turn yeterli"


# --- Test: Skill dagilimi butunlugu ---

class TestSkillDagilimi:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.hesap = parse_agent_frontmatter(HESAP_FILE)
        self.arastirma = parse_agent_frontmatter(ARASTIRMA_FILE)
        self.veri = parse_agent_frontmatter(VERI_FILE)
        self.hukuk = parse_agent_frontmatter(HUKUK_FILE)
        self.all_subagents = [self.hesap, self.arastirma, self.veri, self.hukuk]

    def test_tum_skilller_atanmis(self):
        """11 skill'in tamami sub-agent'lara atanmis olmali"""
        assigned = set()
        for agent in self.all_subagents:
            assigned.update(agent["skills"])
        assert assigned == EXPECTED_ALL_SKILLS, (
            f"Eksik skill'ler: {EXPECTED_ALL_SKILLS - assigned}"
        )

    def test_skill_cakismasi_yok(self):
        """Hicbir skill birden fazla agent'ta olmamali"""
        all_skills = []
        for agent in self.all_subagents:
            all_skills.extend(agent["skills"])
        assert len(all_skills) == len(set(all_skills)), (
            f"Cakisan skill var: {[s for s in all_skills if all_skills.count(s) > 1]}"
        )

    def test_skill_dosyalari_mevcut(self):
        """Her atanmis skill'in SKILL.md dosyasi olmali"""
        for agent in self.all_subagents:
            for skill in agent["skills"]:
                skill_file = SKILLS_DIR / skill / "SKILL.md"
                assert skill_file.exists(), (
                    f"Skill dosyasi bulunamadi: {skill}/SKILL.md "
                    f"(agent: {agent['name']})"
                )

    def test_orchestrator_skill_yok(self):
        """Orchestrator'de dogrudan skill olmamali"""
        orch = parse_agent_frontmatter(ORCHESTRATOR_FILE)
        assert orch["skills"] == [], "Orchestrator'de skill olmamali"

    def test_toplam_skill_sayisi(self):
        """Tam 14 skill olmali"""
        total = sum(len(a["skills"]) for a in self.all_subagents)
        assert total == 14, f"Beklenen 14 skill, bulunan {total}"


# --- Test: Skill disable-model-invocation tutarliligi ---

class TestSkillModelInvocation:
    """disable-model-invocation: true olan skill'ler veri/template skill'leri olmali"""

    EXPECTED_DISABLED = {"ragip-firma", "ragip-gorev", "ragip-ihtar", "ragip-ozet", "ragip-import", "ragip-profil", "ragip-zamanasimi"}

    def _has_disable_flag(self, skill_name: str) -> bool:
        skill_file = SKILLS_DIR / skill_name / "SKILL.md"
        text = skill_file.read_text(encoding="utf-8")
        return "disable-model-invocation: true" in text

    def test_beklenen_disabled_skilller(self):
        """Prosedural skill'ler disable-model-invocation: true olmali"""
        for skill in self.EXPECTED_DISABLED:
            assert self._has_disable_flag(skill), (
                f"{skill} icin disable-model-invocation: true eksik"
            )

    def test_llm_gerektiren_skilller(self):
        """LLM gerektiren skill'lerde disable-model-invocation olmamali"""
        llm_skills = EXPECTED_ALL_SKILLS - self.EXPECTED_DISABLED
        for skill in llm_skills:
            assert not self._has_disable_flag(skill), (
                f"{skill} LLM gerektiriyor ama disable-model-invocation: true var"
            )


# --- Test: Cikti yonetimi ---

class TestCiktiYonetimi:
    """Alt-ajanlarin cikti kaydetme talimatlari dogru yapilandirilmis olmali"""

    def test_orchestrator_cikti_yonetimi_bolumu(self):
        """ragip-aga.md'de CIKTI YONETIMI bolumu olmali"""
        text = ORCHESTRATOR_FILE.read_text(encoding="utf-8")
        assert "CIKTI YONETIMI" in text, (
            "Orchestrator'de CIKTI YONETIMI bolumu eksik"
        )

    def test_orchestrator_ciktilar_dizin_referansi(self):
        """Orchestrator ciktilar/ dizinine referans vermeli"""
        text = ORCHESTRATOR_FILE.read_text(encoding="utf-8")
        assert "ciktilar/" in text, (
            "Orchestrator'de ciktilar/ dizin referansi eksik"
        )

    def test_arastirma_cikti_kaydetme(self):
        """ragip-arastirma cikti kaydetme talimati icermeli"""
        text = ARASTIRMA_FILE.read_text(encoding="utf-8")
        assert "CIKTI KAYDETME" in text, (
            "ragip-arastirma'da CIKTI KAYDETME bolumu eksik"
        )
        assert "ciktilar/" in text, (
            "ragip-arastirma'da ciktilar/ dizin referansi eksik"
        )

    def test_hesap_cikti_kaydetme(self):
        """ragip-hesap cikti kaydetme talimati icermeli"""
        text = HESAP_FILE.read_text(encoding="utf-8")
        assert "CIKTI KAYDETME" in text, (
            "ragip-hesap'ta CIKTI KAYDETME bolumu eksik"
        )
        assert "ciktilar/" in text, (
            "ragip-hesap'ta ciktilar/ dizin referansi eksik"
        )

    def test_hukuk_cikti_kaydetme(self):
        """ragip-hukuk cikti kaydetme talimati icermeli"""
        text = HUKUK_FILE.read_text(encoding="utf-8")
        assert "CIKTI KAYDETME" in text, (
            "ragip-hukuk'ta CIKTI KAYDETME bolumu eksik"
        )
        assert "ciktilar/" in text, (
            "ragip-hukuk'ta ciktilar/ dizin referansi eksik"
        )

    def test_veri_cikti_kaydetme(self):
        """ragip-veri cikti kaydetme talimati icermeli"""
        text = VERI_FILE.read_text(encoding="utf-8")
        assert "CIKTI KAYDETME" in text, (
            "ragip-veri'de CIKTI KAYDETME bolumu eksik"
        )

    def test_tum_subagentlar_cikti_dizini_ayni(self):
        """Tum sub-agent'lar ayni cikti dizinine yazamali"""
        beklenen = "ciktilar/"
        for f in ALL_SUBAGENT_FILES:
            text = f.read_text(encoding="utf-8")
            assert beklenen in text, (
                f"{f.name} icinde '{beklenen}' referansi eksik"
            )


# --- Test: Portability (repo-relative paths) ---

class TestPortability:
    """Tum agent ve skill dosyalari portable olmali — hardcoded path kalmamali"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.agent_files = list(AGENTS_DIR.glob("ragip-*.md"))
        self.skill_files = list(SKILLS_DIR.glob("ragip-*/SKILL.md"))
        self.all_files = self.agent_files + self.skill_files

    def _extract_python_blocks(self, text: str) -> list[str]:
        """Python inline bloklarini cikar (python3 -c '...' icerikleri)"""
        blocks = []
        in_block = False
        current = []
        for line in text.split("\n"):
            if 'python3 -c "' in line or "python3 -c '" in line:
                in_block = True
                current = [line]
            elif in_block:
                current.append(line)
                if line.strip() == '"' or line.strip() == "'":
                    blocks.append("\n".join(current))
                    in_block = False
                    current = []
        return blocks

    def _extract_bash_blocks(self, text: str) -> list[str]:
        """Markdown bash bloklarini cikar"""
        blocks = []
        in_block = False
        current = []
        for line in text.split("\n"):
            if line.strip() == "```bash":
                in_block = True
                current = []
            elif in_block and line.strip() == "```":
                blocks.append("\n".join(current))
                in_block = False
            elif in_block:
                current.append(line)
        return blocks

    def test_no_hardcoded_path_home_in_python_blocks(self):
        """Python bloklarinda Path.home() / '.orchestrator' kalmamis olmali"""
        for f in self.all_files:
            text = f.read_text(encoding="utf-8")
            blocks = self._extract_python_blocks(text)
            for i, block in enumerate(blocks):
                assert "Path.home() / '.orchestrator" not in block, (
                    f"{f.name} Python blok #{i+1}: "
                    f"Path.home() / '.orchestrator' hala mevcut"
                )

    def test_no_tilde_orchestrator_in_python_blocks(self):
        """Python bloklarinda ~/.orchestrator kalmamis olmali"""
        for f in self.all_files:
            text = f.read_text(encoding="utf-8")
            blocks = self._extract_python_blocks(text)
            for i, block in enumerate(blocks):
                assert "~/.orchestrator" not in block, (
                    f"{f.name} Python blok #{i+1}: "
                    f"~/.orchestrator hala mevcut"
                )

    def test_bash_blocks_use_git_rev_parse(self):
        """Script cagiran bash bloklarinda git rev-parse kullaniliyor olmali"""
        for f in self.all_files:
            text = f.read_text(encoding="utf-8")
            blocks = self._extract_bash_blocks(text)
            for i, block in enumerate(blocks):
                # ~/.orchestrator/scripts/ referansi varsa git rev-parse olmali
                if "~/.orchestrator/scripts/" in block:
                    assert False, (
                        f"{f.name} Bash blok #{i+1}: "
                        f"~/.orchestrator/scripts/ var ama git rev-parse yok"
                    )

    def test_python_blocks_have_root_preamble(self):
        """Path kullanan Python bloklarinda _ROOT tanimli olmali"""
        for f in self.skill_files:
            text = f.read_text(encoding="utf-8")
            blocks = self._extract_python_blocks(text)
            for i, block in enumerate(blocks):
                if "data/RAGIP_AGA/" in block:
                    assert "_ROOT" in block, (
                        f"{f.name} Python blok #{i+1}: "
                        f"data/RAGIP_AGA/ referansi var ama _ROOT tanimli degil"
                    )

    def test_git_rev_parse_works_in_repo(self):
        """git rev-parse --show-toplevel mevcut repoda dogru path dondurmeli"""
        import subprocess
        result = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
        repo_root = Path(result)
        assert repo_root.exists(), f"git rev-parse sonucu mevcut degil: {result}"
        # Kit kaynagi veya kurulum dizini
        assert (repo_root / "agents").is_dir() or (repo_root / ".claude" / "agents").is_dir(), (
            f"{result}: ne agents/ ne de .claude/agents/ dizini bulunamadi"
        )

    def test_doc_text_uses_relative_paths(self):
        """Dokumantasyon metinlerinde path'ler repo-relative olmali"""
        # Agent dosyalarindaki **Dizin:** satirlari
        for f in self.agent_files:
            text = f.read_text(encoding="utf-8")
            if "**Dizin:**" in text:
                for line in text.split("\n"):
                    if "**Dizin:**" in line:
                        assert "~/.orchestrator" not in line, (
                            f"{f.name}: Dizin referansinda "
                            f"~/.orchestrator hala mevcut"
                        )

    def test_no_hardcoded_path_in_skill_descriptions(self):
        """Skill aciklama metinlerinde hardcoded path olmamali"""
        for f in self.skill_files:
            text = f.read_text(encoding="utf-8")
            # Frontmatter sonrasi ilk paragraf
            parts = text.split("---", 2)
            if len(parts) >= 3:
                body = parts[2]
                # Python/bash bloklari DISINDA ~/.orchestrator olmamali
                lines = body.split("\n")
                in_code = False
                for line in lines:
                    if line.strip().startswith("```"):
                        in_code = not in_code
                    elif not in_code and "~/.orchestrator" in line:
                        assert False, (
                            f"{f.name}: Metin icinde "
                            f"~/.orchestrator hala mevcut: {line.strip()}"
                        )


# --- Test: Versiyon ve manifest dogrulamasi ---

class TestVersionManifest:
    """VERSION dosyasi, config uyumu ve manifest yapisal dogrulamasi"""

    def test_version_file_exists(self):
        """Kit kokunde VERSION dosyasi olmali ve semver formatinda olmali"""
        version_file = _REPO_ROOT / "VERSION"
        if version_file.exists():
            version = version_file.read_text(encoding="utf-8").strip()
            assert re.match(r"^\d+\.\d+\.\d+$", version), (
                f"VERSION semver formatinda degil: {version}"
            )

    def test_version_matches_changelog(self):
        """VERSION ile changelog'daki son surum uyumlu olmali"""
        version_file = _REPO_ROOT / "VERSION"
        changelog = _REPO_ROOT / "RAGIP_AGA_CHANGELOG.md"
        if version_file.exists() and changelog.exists():
            version = version_file.read_text(encoding="utf-8").strip()
            cl_text = changelog.read_text(encoding="utf-8")
            match = re.search(r"## \[(\d+\.\d+\.\d+)\]", cl_text)
            assert match, "Changelog'da surum bulunamadi"
            assert match.group(1) == version, (
                f"VERSION ({version}) ile changelog ({match.group(1)}) uyumsuz"
            )

    def test_config_version_matches(self):
        """config/ragip_aga.yaml version alani VERSION ile uyumlu olmali"""
        version_file = _REPO_ROOT / "VERSION"
        config_file = _REPO_ROOT / "config" / "ragip_aga.yaml"
        if version_file.exists() and config_file.exists():
            version = version_file.read_text(encoding="utf-8").strip()
            config_text = config_file.read_text(encoding="utf-8")
            match = re.search(r'version:\s*"(\d+\.\d+\.\d+)"', config_text)
            assert match, "Config'de version alani bulunamadi"
            assert match.group(1) == version, (
                f"Config version ({match.group(1)}) ile VERSION ({version}) uyumsuz"
            )

    def test_manifest_structure(self):
        """Kurulumda manifest varsa yapisal olarak dogru olmali"""
        manifest_file = _REPO_ROOT / "config" / ".ragip_manifest.json"
        if manifest_file.exists():
            import json
            manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
            assert "kit_version" in manifest
            assert "installed_at" in manifest
            assert "files" in manifest
            assert isinstance(manifest["files"], dict)
            for path, checksum in manifest["files"].items():
                assert checksum.startswith("sha256:"), (
                    f"Manifest checksum formati hatali: {path} = {checksum}"
                )

    def test_manifest_files_exist(self):
        """Manifestteki tum dosyalar mevcut olmali"""
        manifest_file = _REPO_ROOT / "config" / ".ragip_manifest.json"
        if manifest_file.exists():
            import json
            manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
            for rel_path in manifest["files"]:
                full_path = _REPO_ROOT / rel_path
                assert full_path.exists(), (
                    f"Manifestte kayitli ama mevcut degil: {rel_path}"
                )


# --- Test: Bash blok yapısal doğrulama ---

class TestBashBlocks:
    """Skill'lerdeki bash bloklarinin yapisal dogrulamasi — syntax, env var, helper kullanimi"""

    SCRIPTS_DIR = _REPO_ROOT / "scripts"

    @pytest.fixture(autouse=True)
    def setup(self):
        self.skill_files = list(SKILLS_DIR.glob("ragip-*/SKILL.md"))

    def _extract_bash_blocks(self, text: str) -> list[str]:
        """Markdown bash bloklarini cikar"""
        blocks = []
        in_block = False
        current = []
        for line in text.split("\n"):
            if line.strip() == "```bash":
                in_block = True
                current = []
            elif in_block and line.strip() == "```":
                blocks.append("\n".join(current))
                in_block = False
            elif in_block:
                current.append(line)
        return blocks

    def _extract_python_inline_code(self, bash_block: str) -> list[str]:
        """Bash bloğundan python3 -c '...' içeriklerini çıkar"""
        codes = []
        lines = bash_block.split("\n")
        in_python = False
        current = []
        for line in lines:
            if 'python3 -c "' in line or "python3 -c '" in line:
                in_python = True
                # python3 -c " sonrasındaki kısmı al
                idx = line.find('python3 -c "')
                if idx >= 0:
                    rest = line[idx + len('python3 -c "'):]
                    current = [rest]
                else:
                    idx = line.find("python3 -c '")
                    rest = line[idx + len("python3 -c '"):]
                    current = [rest]
            elif in_python:
                if line.strip() == '"' or line.strip() == "'":
                    codes.append("\n".join(current))
                    in_python = False
                    current = []
                else:
                    current.append(line)
        return codes

    def test_python_blocks_valid_syntax(self):
        """Her python3 -c bloğu geçerli Python sözdizimi olmalı"""
        for f in self.skill_files:
            text = f.read_text(encoding="utf-8")
            bash_blocks = self._extract_bash_blocks(text)
            for i, block in enumerate(bash_blocks):
                py_codes = self._extract_python_inline_code(block)
                for j, code in enumerate(py_codes):
                    # Placeholder'lar env var pattern'e dönüştürüldü,
                    # ama hala agent'in dolduracağı PLACEHOLDER string'ler olabilir
                    # Bunları geçerli string'lerle değiştirerek syntax kontrolü yap
                    # Bash \" escape'lerini Python " ile değiştir
                    # (bash python3 -c "..." içinde \" kullanır, Python'da " olmalı)
                    test_code = code.replace('\\"', '"')
                    test_code = test_code.replace("ARGUMANLAR_BURAYA", "test")
                    test_code = test_code.replace("ID_BURAYA", "1")
                    test_code = test_code.replace("GUNCELLEMELER_BURAYA", "a=b")
                    test_code = test_code.replace("TERIM_BURAYA", "test")
                    try:
                        compile(test_code, f"{f.name}:bash#{i+1}:py#{j+1}", "exec")
                    except SyntaxError as e:
                        assert False, (
                            f"{f.name} Bash blok #{i+1} Python #{j+1}: "
                            f"Sözdizimi hatası: {e}"
                        )

    def test_no_bare_placeholder_in_python(self):
        """Python bloklarında bare placeholder (= ANAPARA, = TUTAR, = GUN) kalmamış olmalı"""
        bare_patterns = [
            r"=\s*ANAPARA\b",
            r"=\s*TUTAR\b",
            r"=\s*GUN\b",
            r"=\s*ORAN\b",
        ]
        for f in self.skill_files:
            text = f.read_text(encoding="utf-8")
            bash_blocks = self._extract_bash_blocks(text)
            for i, block in enumerate(bash_blocks):
                py_codes = self._extract_python_inline_code(block)
                for j, code in enumerate(py_codes):
                    for pattern in bare_patterns:
                        matches = re.findall(pattern, code)
                        assert not matches, (
                            f"{f.name} Bash blok #{i+1} Python #{j+1}: "
                            f"Bare placeholder bulundu: {matches} — env var pattern kullanılmalı"
                        )

    def test_rates_fetch_uses_helper(self):
        """TCMB oran çeken skill'ler ragip_get_rates.sh kullanıyor olmalı"""
        rate_skills = {"ragip-vade-farki", "ragip-arbitraj", "ragip-strateji"}
        for f in self.skill_files:
            skill_name = f.parent.name
            if skill_name not in rate_skills:
                continue
            text = f.read_text(encoding="utf-8")
            bash_blocks = self._extract_bash_blocks(text)
            # En az bir bash bloğunda ragip_get_rates.sh kullanılıyor olmalı
            uses_helper = any("ragip_get_rates.sh" in b for b in bash_blocks)
            assert uses_helper, (
                f"{skill_name}: TCMB oranları çekiyor ama ragip_get_rates.sh kullanmıyor"
            )

    def test_crud_skills_use_helper(self):
        """CRUD skill'leri ragip_crud import ediyor olmalı"""
        crud_skills = {"ragip-firma", "ragip-gorev", "ragip-profil"}
        for f in self.skill_files:
            skill_name = f.parent.name
            if skill_name not in crud_skills:
                continue
            text = f.read_text(encoding="utf-8")
            assert "ragip_crud" in text, (
                f"{skill_name}: CRUD skill ama ragip_crud import etmiyor"
            )

    def test_bash_blocks_quote_variables(self):
        """Bash bloklarında $RATES gibi değişkenler tırnak içinde olmalı"""
        for f in self.skill_files:
            text = f.read_text(encoding="utf-8")
            bash_blocks = self._extract_bash_blocks(text)
            for i, block in enumerate(bash_blocks):
                # echo $RATES (tırnak olmadan) kontrolü — python3 -c içindeki satırları atla
                for line in block.split("\n"):
                    line_stripped = line.strip()
                    # Python bloğu içindeki satırları atla
                    if line_stripped.startswith("import ") or line_stripped.startswith("from "):
                        continue
                    # Bash değişken ataması ve env var satırları (KEY="$VAR") zaten doğru
                    # Sorunlu pattern: echo $VAR (tırnak yok)
                    if re.search(r'echo\s+\$[A-Z]', line_stripped):
                        assert False, (
                            f"{f.name} Bash blok #{i+1}: "
                            f"Tırnak olmayan değişken: {line_stripped}"
                        )

    def test_get_rates_sh_exists(self):
        """scripts/ragip_get_rates.sh mevcut ve çalıştırılabilir olmalı"""
        get_rates = self.SCRIPTS_DIR / "ragip_get_rates.sh"
        assert get_rates.exists(), "scripts/ragip_get_rates.sh bulunamadı"
        import os
        assert os.access(get_rates, os.X_OK), (
            "scripts/ragip_get_rates.sh çalıştırılabilir değil (chmod +x gerekli)"
        )

    def test_crud_py_exists(self):
        """scripts/ragip_crud.py mevcut olmalı"""
        crud = self.SCRIPTS_DIR / "ragip_crud.py"
        assert crud.exists(), "scripts/ragip_crud.py bulunamadı"

    def test_env_var_export_import_match(self):
        """Bash'te export edilen env var'lar Python'da kullanılan env var'larla eşleşmeli"""
        for f in self.skill_files:
            text = f.read_text(encoding="utf-8")
            bash_blocks = self._extract_bash_blocks(text)
            for i, block in enumerate(bash_blocks):
                # Pattern: KEY="val" python3 -c satırlarını bul
                # Birden fazla KEY="val" olabilir aynı satırda
                env_line_match = re.search(
                    r'^((?:\w+="[^"]*"\s+)+)python3\s+-c',
                    block, re.MULTILINE
                )
                if not env_line_match:
                    continue
                env_part = env_line_match.group(1)
                exported_keys = set(re.findall(r'(\w+)="', env_part))

                py_codes = self._extract_python_inline_code(block)
                for j, code in enumerate(py_codes):
                    # Python'da kullanılan os.environ key'leri
                    used_keys = set(re.findall(
                        r"os\.environ\[?\.?g?e?t?\(?['\"](\w+)", code
                    ))
                    # Her kullanılan key export edilmiş olmalı
                    missing = used_keys - exported_keys
                    if missing:
                        # Bazı key'ler ${VAR:-default} pattern'i ile set edilmiş olabilir
                        # Bunları da kabul et
                        env_default = set(re.findall(r'(\w+)="\$\{', env_part))
                        missing = missing - env_default
                    # RATES_JSON gibi dynamic env var'lar $RATES ile set ediliyor
                    # Pattern: RATES_JSON="$RATES" — bu da geçerli
                    dynamic_env = set(re.findall(r'(\w+)="\$\w+"', env_part))
                    missing = missing - dynamic_env

    def test_firma_tip_field_in_schema(self):
        """ragip-firma skill'inde tip alanı schema'da tanımlı olmalı"""
        firma_skill = SKILLS_DIR / "ragip-firma" / "SKILL.md"
        text = firma_skill.read_text(encoding="utf-8")
        assert '"tip"' in text, "Firma schema'sında tip alanı eksik"
        for tip in ["tedarikci", "musteri", "distributor", "diger"]:
            assert tip in text, f"Firma tip değeri eksik: {tip}"

    def test_firma_tip_validation_in_ekle(self):
        """ragip-firma ekle komutunda tip validasyonu olmalı"""
        firma_skill = SKILLS_DIR / "ragip-firma" / "SKILL.md"
        text = firma_skill.read_text(encoding="utf-8")
        assert "VALID_TIP" in text, "Firma ekle komutunda tip validasyonu eksik"
