# ADR-0014: Prompt Caching Policy

**Tarih:** 2026-05-12
**Durum:** Kabul edildi
**Karar vericiler:** Kit gelistirici

## Baglam

Anthropic Claude API prompt caching destekliyor: aynı system prompt'la (veya prefix'i ile) art arda çağrılarda tekrar eden token'lar cache'ten okunur — input token maliyeti ~%90 düşer, latency azalır. Cache TTL 5 dakika (ephemeral) veya 1 saat (1h, yeni özellik).

Kit'in iki ayrı LLM giriş noktası var:

1. **Claude Code orchestration (asıl kullanım):**
   - Kullanıcı `claude --agent ragip-aga` veya skill çağrısı ile etkileşir.
   - LLM çağrılarını Claude Code'un kendisi yönetir.
   - Kit sadece `agents/*.md` ve `skills/*/SKILL.md` (system prompt'lar) sağlar.
   - **Otomatik prompt caching:** Claude Code 2024'ten beri agent system prompt'larını otomatik cache'liyor. Kit tarafından kontrol edilemez — sadece prompt içeriği değişmediği sürece cache hit alır.

2. **`scripts/ragip_aga.py` CLI mode (alternatif kullanım):**
   - `python3 scripts/ragip_aga.py` ile standalone CLI.
   - `call_llm()` fonksiyonu **litellm** üzerinden Anthropic API'ye direkt çağrı yapar.
   - **Bu kit tarafından kontrol edilebilir** — `cache_control: ephemeral` eksikti.

`agents/*.md` toplam 934 satır system prompt — Sonnet için cache minimum eşiği (1024 token) üstünde, kazanç var.

## Karar

İki katmanlı politika:

### A. Claude Code orchestration

**Aksiyon:** Yok. Claude Code'un otomatik caching mekanizmasına güveniyoruz.

Kit'in sorumluluğu: agent system prompt'larının tekrar eden bölümünü stabil tutmak (sık değişen tarih/dinamik içerik üst tarafa konmamalı — cache hit oranını düşürür). Bu zaten mevcut yapıda mevcut.

### B. CLI mode (`call_llm()`)

**Aksiyon:** litellm `cache_control: {"type": "ephemeral"}` Anthropic provider için eklendi (v2.13.0).

İmplementasyon (`scripts/ragip_aga.py`):

```python
def _build_messages(model: str, system_prompt: str, user_prompt: str) -> list:
    is_anthropic = model.startswith("anthropic/") or model.startswith("claude-")
    if is_anthropic:
        return [
            {
                "role": "system",
                "content": [{
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"}
                }]
            },
            {"role": "user", "content": user_prompt},
        ]
    # Non-Anthropic provider: standart string content, cache yok
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
```

Provider tespiti modelin string prefix'i ile (`anthropic/...` veya `claude-...`). Fallback model Anthropic değilse (örn OpenAI fallback), o iteration'da cache_control eklenmez (provider format hatasi engellenir).

## Gerekce

| Alternatif | Red nedeni |
|---|---|
| Hicbir sey yapma | CLI mode'da art arda calistirmalarda token israfi. Sonnet system prompt ~5k token; her CLI calistirmasinda yeniden tokenize edilir. |
| Tum provider'larda cache_control | Sadece Anthropic destekliyor. OpenAI/Gemini'de format hatasi. |
| Agent YAML'lere cache config alani ekle | Claude Code orchestration zaten otomatik — kit kontrol etmiyor. Karmasik, fayda yok. |
| 1-saatlik cache (cache_control: "1h" — beta) | Marjinal kazanc, beta. Ephemeral 5dk yeterli. Sonra yukseltilebilir. |
| Anthropic SDK direkt (litellm'den vazgec) | Kit'in cok-provider esneklikten vazgecmez (CLI'da OpenAI fallback var). |

**Avantajlar:**

- **Sifir risk:** Non-Anthropic provider'da hicbir sey degismez (eski davranis korunur).
- **Test edilebilir:** `_build_messages()` saf fonksiyon — 9 test (Anthropic/Claude prefix, OpenAI/Gemini/Ollama, multiline/empty/userprompt).
- **Cache hit kazanci:** Sonnet input token maliyeti %90 azalir (cache hit). Latency 200-500ms duser. Repeated CLI usage'da net.
- **Geriye uyumlu:** Mevcut config/ragip_aga.yaml degismez. Mevcut testler korunur.

## Konsekvanslar

### Pozitif

- CLI mode'da art arda calistirmada token tasarrufu (cache TTL 5dk icinde).
- `_build_messages()` saf fonksiyon — gelecekteki refactor icin (I1) ayrilmis.
- ADR ile politika dokumante — Claude Code otomatik caching vs kit explicit caching ayrimi netlestirildi.

### Negatif

- CLI tek seferlik kullanimda kazanc yok (5dk TTL ge kullanilamadi).
- Cache hit metrikleri henuz yok — gelecekte litellm response.usage.cache_read_input_tokens izlenebilir.

### Gelecek calisma

- `call_llm()` return'unde cache hit metriklerini history.jsonl'e yaz (cache_read_input_tokens).
- 1-saatlik cache'e gec (Anthropic beta cikinca degerlendir).

## Kaynaklar

- Anthropic Prompt Caching docs (2024 launch, GA 2025)
- litellm Anthropic provider docs (cache_control parametresi)
- `call_llm()` implementation: `scripts/ragip_aga.py`

## Iliski

- **Onceki:** ADR-0010 Savunma Katmanlari (model davranisi)
- **Iliskili:** ADR-0013 Chain-of-Verification (cikti dogrulama — orthogonal)
- **Tetikleyici:** FEATURE_IDEAS I10 (kapatildi v2.13.0)
