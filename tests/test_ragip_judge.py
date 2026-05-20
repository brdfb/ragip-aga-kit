"""ragip_judge.py testleri — Tier 3/4 Spirit (anlamsal) olcumu (ADR-0020).

Mock-only: gercek Anthropic API cagrisi yapilmaz. litellm.completion monkeypatch
ile sahte response dondurulur. Integration test ayri (manuel script).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

KIT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT_ROOT / "scripts"))

from ragip_judge import (  # noqa: E402
    DEFAULT_MAX_BUDGET_USD,
    DEFAULT_MAX_CUMULATIVE_USD,
    DEFAULT_MODEL,
    JUDGE_SYSTEM_PROMPT,
    RUBRIC_DIMS,
    _calculate_actual_cost,
    _check_cost_guards,
    _estimate_input_cost,
    _parse_judge_response,
    judge_cikti,
)


# Sahte temiz judge cevabi (6/6 pass)
MOCK_TEMIZ_JSON = json.dumps({
    "T3_1_TESPIT_quality": {"pass": True, "reasoning": "Insight cumlesi mevcut, madde + tutar dahil."},
    "T3_2_ETKI_quality": {"pass": True, "reasoning": "Tutar/yuzde/yon/horizon hepsi var."},
    "T3_3_POZISYON_quality": {"pass": True, "reasoning": "Sahip Hukuk, Zaman 5 gun, Beklenen olculebilir."},
    "T3_4_GEREKCE_quality": {"pass": True, "reasoning": "TTK m.21/2 spesifik referans."},
    "T3_5_ETIKET_consistency": {"pass": True, "reasoning": "anapara (kalan) tutarli."},
    "T4_TUTARLILIK_genuine": {"pass": True, "reasoning": "Cross-doc karsilastirma yapilmis."},
    "overall": "pass",
    "spirit_score": 6,
    "notes": "Tum disiplinler uygulandi.",
})

# Sahte fail judge cevabi (1/6 pass)
MOCK_FAIL_JSON = json.dumps({
    "T3_1_TESPIT_quality": {"pass": False, "reasoning": "Sadece sayi tekrari, insight yok."},
    "T3_2_ETKI_quality": {"pass": False, "reasoning": "Horizon eksik."},
    "T3_3_POZISYON_quality": {"pass": False, "reasoning": "Sahip belirsiz."},
    "T3_4_GEREKCE_quality": {"pass": True, "reasoning": "Mevzuat ref var."},
    "T3_5_ETIKET_consistency": {"pass": False, "reasoning": "Iki farkli rakam ayni etiketle."},
    "T4_TUTARLILIK_genuine": {"pass": False, "reasoning": "Rubber-stamp 'temiz' notu, denetim izi yok."},
    "overall": "fail",
    "spirit_score": 1,
    "notes": "Disiplin yarim uygulanmis.",
})

# Markdown code fence ile sarilmis (modeller bazen yine ekliyor)
MOCK_TEMIZ_FENCED = f"```json\n{MOCK_TEMIZ_JSON}\n```"


def _mock_llm_response(content: str, prompt_tokens: int = 3000,
                       completion_tokens: int = 500,
                       cache_read_tokens: int = 0) -> MagicMock:
    """Sahte litellm.completion() response."""
    mock = MagicMock()
    mock.choices = [MagicMock()]
    mock.choices[0].message.content = content
    mock.usage.prompt_tokens = prompt_tokens
    mock.usage.completion_tokens = completion_tokens
    mock.usage.cache_read_input_tokens = cache_read_tokens
    return mock


# ─── _parse_judge_response ──────────────────────────────────────────────


class TestParseJudgeResponse:
    def test_temiz_json(self):
        s = _parse_judge_response(MOCK_TEMIZ_JSON)
        assert s["overall"] == "pass"
        assert s["spirit_score"] == 6
        for dim in RUBRIC_DIMS:
            assert s[dim]["pass"] is True

    def test_fail_json(self):
        s = _parse_judge_response(MOCK_FAIL_JSON)
        assert s["overall"] == "fail"
        assert s["spirit_score"] == 1
        # Sadece T3-4 pass
        passes = sum(1 for d in RUBRIC_DIMS if s[d]["pass"])
        assert passes == 1

    def test_markdown_fence_stripp(self):
        """Modeller bazen ```json ... ``` ile sarip donduruyor — parse etmeli."""
        s = _parse_judge_response(MOCK_TEMIZ_FENCED)
        assert s["overall"] == "pass"

    def test_invalid_json_raises(self):
        with pytest.raises(ValueError, match="JSON parse"):
            _parse_judge_response("not a json")

    def test_eksik_dimension_raises(self):
        bozuk = json.dumps({
            "T3_1_TESPIT_quality": {"pass": True, "reasoning": "ok"},
            # T3_2-T4 yok
            "overall": "pass",
            "spirit_score": 1,
        })
        with pytest.raises(ValueError, match="Eksik dimension"):
            _parse_judge_response(bozuk)

    def test_overall_gecersiz_raises(self):
        d = json.loads(MOCK_TEMIZ_JSON)
        d["overall"] = "unknown"
        with pytest.raises(ValueError, match="overall"):
            _parse_judge_response(json.dumps(d))

    def test_spirit_score_gecersiz_raises(self):
        d = json.loads(MOCK_TEMIZ_JSON)
        d["spirit_score"] = 7
        with pytest.raises(ValueError, match="spirit_score"):
            _parse_judge_response(json.dumps(d))

    def test_consistency_warning(self):
        """spirit_score ile gercek pass sayisi eslesmiyorsa warning dus."""
        d = json.loads(MOCK_TEMIZ_JSON)
        d["spirit_score"] = 3  # gercek 6, sahte 3
        s = _parse_judge_response(json.dumps(d))
        assert "_consistency_warning" in s

    def test_pass_field_bool_zorunlu(self):
        d = json.loads(MOCK_TEMIZ_JSON)
        d["T3_1_TESPIT_quality"]["pass"] = "true"  # string, bool degil
        with pytest.raises(ValueError, match="Boolean"):
            _parse_judge_response(json.dumps(d))


# ─── Cost hesabi ────────────────────────────────────────────────────────


class TestCostHesabi:
    def test_estimate_input_cost_kucuk_metin(self):
        # 4000 char / 4 char-per-token = 1000 token. Maliyet = 1000/1M × $3 = $0.003
        c = _estimate_input_cost("x" * 4000, 0)
        assert 0.002 <= c <= 0.004

    def test_estimate_input_cost_system_prompt_dahil(self):
        # 0 char input + 4000 char sys = 1000 token total
        c = _estimate_input_cost("", 4000)
        assert 0.002 <= c <= 0.004

    def test_actual_cost_cache_yok(self):
        # 3000 in / 500 out
        # input: 3000/1M × $3 = $0.009
        # output: 500/1M × $15 = $0.0075
        # toplam: $0.0165
        c = _calculate_actual_cost(3000, 500, 0)
        assert abs(c - 0.0165) < 0.0001

    def test_actual_cost_full_cache(self):
        # 3000 in (hepsi cache) + 500 out
        # cache: 3000/1M × $0.30 = $0.0009
        # output: 500/1M × $15 = $0.0075
        # toplam: $0.0084
        c = _calculate_actual_cost(3000, 500, 3000)
        assert abs(c - 0.0084) < 0.0001

    def test_actual_cost_kismi_cache(self):
        # 3000 in (2000 cache, 1000 normal) + 500 out
        # normal in: 1000/1M × $3 = $0.003
        # cache: 2000/1M × $0.30 = $0.0006
        # output: 500/1M × $15 = $0.0075
        # toplam: $0.0111
        c = _calculate_actual_cost(3000, 500, 2000)
        assert abs(c - 0.0111) < 0.0001


# ─── Cost guards ────────────────────────────────────────────────────────


class TestCostGuards:
    def test_normal_cikti_gecer(self, monkeypatch, tmp_path):
        # Usage file'i temp'e yonlendir
        from ragip_judge import USAGE_FILE
        monkeypatch.setattr("ragip_judge.USAGE_FILE", tmp_path / "judge_usage.json")
        ok, hata = _check_cost_guards("normal cikti " * 500, 0.50, 5.0)
        assert ok is True
        assert hata == ""

    def test_buyuk_cikti_tek_call_limiti_asar(self, monkeypatch, tmp_path):
        monkeypatch.setattr("ragip_judge.USAGE_FILE", tmp_path / "judge_usage.json")
        # 1M karakter input — yaklasik 250K token, $0.75 — $0.50 limitini asar
        ok, hata = _check_cost_guards("x" * 1_000_000, 0.50, 5.0)
        assert ok is False
        assert "tek-cagri limiti" in hata.lower() or "asar" in hata.lower()

    def test_cumulative_limit_asar(self, monkeypatch, tmp_path):
        usage_file = tmp_path / "judge_usage.json"
        usage_file.write_text(json.dumps({
            "week_start": "2026-05-16T00:00:00+00:00",
            "cumulative_usd": 4.99,
            "call_count": 100,
        }))
        monkeypatch.setattr("ragip_judge.USAGE_FILE", usage_file)
        # Cumulative ~5.0, yeni cagri $0.01+ → toplamn 5.0 limitini asar
        ok, hata = _check_cost_guards("normal" * 1000, 0.50, 5.0)
        assert ok is False
        assert "haftalik" in hata.lower() or "cumulative" in hata.lower() or "toplam" in hata.lower()


# ─── judge_cikti (mock) ─────────────────────────────────────────────────


class TestJudgeCikti:
    def test_temiz_cikti_pass(self, monkeypatch, tmp_path):
        # Usage file'i temp'e
        monkeypatch.setattr("ragip_judge.USAGE_FILE", tmp_path / "judge_usage.json")
        # API key set et (cagri yapilmadigi icin gercek lazim degil, ama check'e takilmasin)
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-dummy")
        # litellm.completion mock
        # litellm sistemde kurulu olmayabilir — sys.modules'a mock inject
        mock_litellm = MagicMock()
        mock_litellm.completion = lambda **kwargs: _mock_llm_response(MOCK_TEMIZ_JSON)
        monkeypatch.setitem(sys.modules, "litellm", mock_litellm)
        sonuc = judge_cikti("ornek cikti")
        assert sonuc["overall"] == "pass"
        assert sonuc["spirit_score"] == 6
        assert sonuc["_meta"]["cost_usd"] > 0
        assert sonuc["_meta"]["input_tokens"] == 3000
        # Usage state guncellendi mi
        usage = json.loads((tmp_path / "judge_usage.json").read_text())
        assert usage["call_count"] == 1
        assert usage["cumulative_usd"] > 0

    def test_fail_cikti(self, monkeypatch, tmp_path):
        monkeypatch.setattr("ragip_judge.USAGE_FILE", tmp_path / "judge_usage.json")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-dummy")
        mock_litellm = MagicMock()
        mock_litellm.completion = lambda **kwargs: _mock_llm_response(MOCK_FAIL_JSON)
        monkeypatch.setitem(sys.modules, "litellm", mock_litellm)
        sonuc = judge_cikti("kotu cikti")
        assert sonuc["overall"] == "fail"
        assert sonuc["spirit_score"] == 1

    def test_api_key_yoksa_hata(self, monkeypatch, tmp_path):
        monkeypatch.setattr("ragip_judge.USAGE_FILE", tmp_path / "judge_usage.json")
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
            judge_cikti("ornek")

    def test_skip_cost_guard(self, monkeypatch, tmp_path):
        """--skip-cost-guard ile guard atlatma cagri ulasir."""
        usage_file = tmp_path / "judge_usage.json"
        usage_file.write_text(json.dumps({
            "week_start": "2026-05-16T00:00:00+00:00",
            "cumulative_usd": 100.0,  # limit cok asilmis
            "call_count": 1000,
        }))
        monkeypatch.setattr("ragip_judge.USAGE_FILE", usage_file)
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-dummy")
        # litellm sistemde kurulu olmayabilir — sys.modules'a mock inject
        mock_litellm = MagicMock()
        mock_litellm.completion = lambda **kwargs: _mock_llm_response(MOCK_TEMIZ_JSON)
        monkeypatch.setitem(sys.modules, "litellm", mock_litellm)
        # skip_cost_guard=True ile cagri yapilir
        sonuc = judge_cikti("ornek", skip_cost_guard=True)
        assert sonuc["overall"] == "pass"


# ─── Sabitlar ───────────────────────────────────────────────────────────


class TestSabitler:
    def test_default_model_anthropic(self):
        assert DEFAULT_MODEL.startswith("anthropic/")

    def test_rubric_6_dim(self):
        assert len(RUBRIC_DIMS) == 6

    def test_rubric_dim_naming(self):
        # T3-1, T3-2, T3-3, T3-4, T3-5, T4 sirasi
        assert RUBRIC_DIMS[0].startswith("T3_1")
        assert RUBRIC_DIMS[5].startswith("T4")

    def test_default_budget_makul(self):
        # Tek cagri max $0.50, haftalik $5
        assert 0.10 <= DEFAULT_MAX_BUDGET_USD <= 1.0
        assert 1.0 <= DEFAULT_MAX_CUMULATIVE_USD <= 20.0

    def test_system_prompt_rubric_isimleri_dahil(self):
        for dim in RUBRIC_DIMS:
            assert dim in JUDGE_SYSTEM_PROMPT, f"{dim} system prompt'ta yok"

    def test_system_prompt_format_uyarisi(self):
        # JSON disinda sey YAZMA uyarisi
        assert "JSON" in JUDGE_SYSTEM_PROMPT
        assert "HICBIR" in JUDGE_SYSTEM_PROMPT or "baska" in JUDGE_SYSTEM_PROMPT.lower()
