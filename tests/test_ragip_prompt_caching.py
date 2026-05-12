"""ragip_aga.call_llm() prompt caching testleri — Anthropic cache_control yapisi."""
from __future__ import annotations

import sys
from pathlib import Path

KIT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT_ROOT / "scripts"))

from ragip_aga import _build_messages  # noqa: E402


class TestBuildMessagesAnthropic:
    def test_anthropic_provider_prefix(self):
        m = _build_messages("anthropic/claude-sonnet-4-5-20250929", "SYS", "USR")
        assert len(m) == 2
        assert m[0]["role"] == "system"
        assert isinstance(m[0]["content"], list)
        assert m[0]["content"][0]["cache_control"] == {"type": "ephemeral"}
        assert m[0]["content"][0]["text"] == "SYS"
        assert m[1] == {"role": "user", "content": "USR"}

    def test_claude_direct_prefix(self):
        m = _build_messages("claude-haiku-4-5-20251001", "SYS", "USR")
        assert isinstance(m[0]["content"], list)
        assert m[0]["content"][0]["cache_control"] == {"type": "ephemeral"}

    def test_claude_sonnet_no_provider_prefix(self):
        m = _build_messages("claude-sonnet-4-5", "Long sys prompt", "Short user")
        assert m[0]["content"][0]["text"] == "Long sys prompt"
        assert m[0]["content"][0]["cache_control"]["type"] == "ephemeral"


class TestBuildMessagesNonAnthropic:
    def test_openai_provider(self):
        m = _build_messages("openai/gpt-4o", "SYS", "USR")
        assert m[0]["content"] == "SYS"
        assert isinstance(m[0]["content"], str)
        assert "cache_control" not in str(m[0])

    def test_unknown_provider_no_cache(self):
        m = _build_messages("ollama/llama3", "SYS", "USR")
        assert m[0]["content"] == "SYS"

    def test_gemini_no_cache(self):
        m = _build_messages("gemini/gemini-pro", "SYS", "USR")
        assert m[0]["content"] == "SYS"
        assert m[1]["content"] == "USR"


class TestBuildMessagesContent:
    def test_user_prompt_unchanged(self):
        m = _build_messages("anthropic/claude-sonnet-4-5", "SYS", "User question here")
        assert m[1]["content"] == "User question here"
        assert m[1]["role"] == "user"

    def test_multiline_system_prompt(self):
        sys_prompt = "Line 1\nLine 2\nLine 3"
        m = _build_messages("anthropic/claude-sonnet-4-5", sys_prompt, "U")
        assert m[0]["content"][0]["text"] == sys_prompt

    def test_empty_system_prompt(self):
        m = _build_messages("anthropic/claude-sonnet-4-5", "", "USR")
        # Bos system prompt'ta da cache_control eklenir — Anthropic cache min token siniri var,
        # ama format dogru olmali. Format hosting; min token Anthropic tarafinda kontrol edilir.
        assert m[0]["content"][0]["text"] == ""
        assert m[0]["content"][0]["cache_control"]["type"] == "ephemeral"
