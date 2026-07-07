#!/usr/bin/env python3
"""Ragip Aga Kit LLM-judge — Tier 3/4 Spirit (anlamsal kalite) olcumu.

Tier 5 (`ragip_format_dogrula.py`) yapisal HARF'i olcer (regex pattern eslesme).
Bu script anlamsal RUH'u olcer — TESPIT cumlesi gercek insight mi, GEREKCE
mevzuat referansi gercek mi, anapara etiketleri tutarli mi.

ADR-0020: Spirit Olcumu — LLM-judge.

6 dimension (Boolean + reasoning per dim, JSON output):
    T3-1 TESPIT_quality       : Insight cumlesi mi (durum + madde + tutar)?
    T3-2 ETKI_quality         : Tutar/yon/horizon mantikli mi?
    T3-3 POZISYON_quality     : Aksiyon spesifik mi, sahip net mi?
    T3-4 GEREKCE_quality      : Mevzuat/karar gercek mi, generic degil mi?
    T3-5 ETIKET_consistency   : Anapara/tutar etiketleri celiskisiz mi?
    T4   TUTARLILIK_genuine   : Denetim notu gercek mi, rubber-stamp mi?

Cikti: structured JSON. Overall: pass/fail/partial. Spirit_score: 0-6.

Kullanim:
    python3 scripts/ragip_judge.py <cikti.md>
    python3 scripts/ragip_judge.py --json <cikti.md>
    python3 scripts/ragip_judge.py --max-budget-usd 1.0 <cikti.md>
    cat cikti.md | python3 scripts/ragip_judge.py -

Cost guard:
    --max-budget-usd N      : Bu cagri icin max harcama (default 0.50)
    --max-cumulative-usd N  : Toplam haftalik harcama (default 5.0)
    State file: data/.judge_usage.json (kit reposunda, gitignored)

Exit:
    0 = judge pass (spirit_score >= 5 ve overall != fail)
    2 = judge fail (spirit_score < 5 veya overall=fail)
    1 = hata (cost limit asildi, API key yok, parse hatasi, vb.)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

KIT_ROOT = Path(__file__).resolve().parents[1]

# Sonnet 4.5 fiyat (16 Mayis 2026 itibariyle, anthropic.com/pricing)
SONNET_INPUT_USD_PER_MTOK = 3.0   # $/1M input tokens
SONNET_OUTPUT_USD_PER_MTOK = 15.0  # $/1M output tokens
# Cache hit (Anthropic prompt caching): %90 indirim
SONNET_CACHE_HIT_USD_PER_MTOK = 0.30

DEFAULT_MODEL = "anthropic/claude-sonnet-5"
DEFAULT_MAX_BUDGET_USD = 0.50      # Tek cagri max
DEFAULT_MAX_CUMULATIVE_USD = 5.0   # Haftalik max
USAGE_FILE = KIT_ROOT / "data" / ".judge_usage.json"

# 6 dimension key listesi (parse + dogrulama icin)
RUBRIC_DIMS = [
    "T3_1_TESPIT_quality",
    "T3_2_ETKI_quality",
    "T3_3_POZISYON_quality",
    "T3_4_GEREKCE_quality",
    "T3_5_ETIKET_consistency",
    "T4_TUTARLILIK_genuine",
]

JUDGE_SYSTEM_PROMPT = """Sen Ragip Aga Kit'in kalite musavirisin. Gorev: LLM ciktilarinda Tier 3/4 disiplinin **anlamsal kalitesini** (Spirit) olcersin. Yapisal grep (Tier 5 format_dogrula.py) zaten yapildi — sen "ruh"u olcersin.

6 dimension, her birinde Boolean (pass/fail) + reasoning yazarsin. Strict JSON dondurursun, baska bir sey yazmazsin.

Degerlendirme kurallarin:

1. **TESPIT_quality (T3-1):** Cumle gercek "insight" mi?
   - PASS: durum + madde + tarih/tutar + etiket dahil yorum cumlesi
   - FAIL: sadece sayi tekrari ("Anapara 142K USD") veya generic gozlem

2. **ETKI_quality (T3-2):** Etki: satiri mantikli mi?
   - PASS: tutar + yuzde + yon (artan/azalan/sabit) + horizon (30/60/90 gun veya kalici)
   - FAIL: tutarsiz birim, mantikli olmayan yuzde, horizon eksik

3. **POZISYON_quality (T3-3):** Aksiyon spesifik mi?
   - PASS: spesifik fiil + somut Sahip (Hukuk/Muhasebe/avukat) + net Zaman (tarih veya kac gun) + olculebilir Beklenen
   - FAIL: vague aksiyon ("dikkat et"), generic sahip ("biri"), belirsiz zaman

4. **GEREKCE_quality (T3-4):** Mevzuat referansi gercek mi?
   - PASS: spesifik kanun maddesi (TBK m.117, TTK m.1530, IIK m.297 vb.) ve neden uygulandigi
   - FAIL: generic ("yasal sebepler"), uydurma madde, alakasiz referans

5. **ETIKET_consistency (T3-5):** Anapara/tutar etiketleri tutarli mi?
   - PASS: ayni tutar her yerde ayni etiket ("anapara (kalan): 142K") veya tutarli ayrim ("nominal: 161K vs kalan: 142K")
   - FAIL: ayni tutar farkli etiketle (bir yerde "anapara 142K", baska yerde "borc 142K"), birden cok rakam ayni etiketle

6. **TUTARLILIK_genuine (T4):** Tutarlilik denetimi notu gercek mi?
   - PASS: gercek tutarsizlik tespit edilmis ve duzeltilmis, veya "temiz" notu gercek bir gozden gecirme sonucu (cross-doc karsilastirma, etiket kontrolu izi var)
   - FAIL: rubber-stamp ("Tutarlilik denetimi: temiz" diye yazilmis ama metinde acik celiski var), denetim izi yok

**ZORUNLU CIKTI FORMATI** (strict JSON, baska aciklama veya markdown YAZMA):

```json
{
  "T3_1_TESPIT_quality": {"pass": true|false, "reasoning": "kisa aciklama, 1-2 cumle"},
  "T3_2_ETKI_quality": {"pass": true|false, "reasoning": "..."},
  "T3_3_POZISYON_quality": {"pass": true|false, "reasoning": "..."},
  "T3_4_GEREKCE_quality": {"pass": true|false, "reasoning": "..."},
  "T3_5_ETIKET_consistency": {"pass": true|false, "reasoning": "..."},
  "T4_TUTARLILIK_genuine": {"pass": true|false, "reasoning": "..."},
  "overall": "pass" | "fail" | "partial",
  "spirit_score": 0-6,
  "notes": "ozet (opsiyonel, max 2 cumle)"
}
```

**overall** karari:
- pass: spirit_score >= 5
- partial: 3 <= spirit_score < 5
- fail: spirit_score < 3

JSON disinda HICBIR sey yazma (markdown code fence dahil)."""


def _estimate_input_cost(input_text: str, system_prompt_len: int) -> float:
    """Tahmini input maliyeti (USD). 1 token ~= 4 karakter (kaba tahmin)."""
    total_chars = len(input_text) + system_prompt_len
    estimated_tokens = total_chars / 4
    return (estimated_tokens / 1_000_000) * SONNET_INPUT_USD_PER_MTOK


def _calculate_actual_cost(input_tokens: int, output_tokens: int,
                            cache_read_tokens: int = 0) -> float:
    """Gercek maliyet (USD). litellm response.usage'dan."""
    # Cache hit indirimi (cache_read_tokens varsa)
    non_cache_input = max(0, input_tokens - cache_read_tokens)
    cost_input = (non_cache_input / 1_000_000) * SONNET_INPUT_USD_PER_MTOK
    cost_cache = (cache_read_tokens / 1_000_000) * SONNET_CACHE_HIT_USD_PER_MTOK
    cost_output = (output_tokens / 1_000_000) * SONNET_OUTPUT_USD_PER_MTOK
    return cost_input + cost_cache + cost_output


def _load_usage() -> dict:
    """Haftalik kümülatif harcama state'i yükle."""
    if not USAGE_FILE.exists():
        return {"week_start": datetime.now(timezone.utc).isoformat(), "cumulative_usd": 0.0, "call_count": 0}
    try:
        return json.loads(USAGE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"week_start": datetime.now(timezone.utc).isoformat(), "cumulative_usd": 0.0, "call_count": 0}


def _save_usage(usage: dict) -> None:
    """Kümülatif harcama state'i yaz."""
    USAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    USAGE_FILE.write_text(json.dumps(usage, indent=2), encoding="utf-8")


def _check_cost_guards(input_text: str, max_budget_usd: float,
                       max_cumulative_usd: float) -> tuple[bool, str]:
    """Pre-check cost guards. Donus: (ok, hata_mesaji)."""
    # Pre-check: tahmini input maliyeti tek cagri limitini asar mi
    estimated = _estimate_input_cost(input_text, len(JUDGE_SYSTEM_PROMPT))
    # Output tahmini ~500 token = $0.0075
    estimated_total = estimated + (500 / 1_000_000) * SONNET_OUTPUT_USD_PER_MTOK

    if estimated_total > max_budget_usd:
        return False, (
            f"Tahmini cagri maliyeti (${estimated_total:.4f}) tek-cagri limitini "
            f"(${max_budget_usd:.2f}) asar. --max-budget-usd ile yukseltebilirsin."
        )

    # Cumulative: bu haftaki toplam
    usage = _load_usage()
    cumulative = usage.get("cumulative_usd", 0.0)
    if cumulative + estimated_total > max_cumulative_usd:
        return False, (
            f"Toplam haftalik harcama (${cumulative:.4f} + ${estimated_total:.4f} tahmini = "
            f"${cumulative + estimated_total:.4f}) limit (${max_cumulative_usd:.2f}) asar. "
            f"--max-cumulative-usd ile yukseltebilirsin veya hafta degisene kadar bekle."
        )

    return True, ""


def _parse_judge_response(response_text: str) -> dict:
    """LLM JSON cevabini parse + validate. Hata varsa exception."""
    # Markdown code fence stripp (modeller bazen yine eklemis olabiliyor)
    text = response_text.strip()
    if text.startswith("```"):
        # Ilk ve son satiri at
        lines = text.split("\n")
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1])
    text = text.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON parse hatasi: {e}. Yanit:\n{response_text[:300]}")

    # 6 dimension dogrula
    for dim in RUBRIC_DIMS:
        if dim not in data:
            raise ValueError(f"Eksik dimension: {dim}")
        dim_data = data[dim]
        if not isinstance(dim_data, dict):
            raise ValueError(f"{dim} dict olmali, gelen: {type(dim_data).__name__}")
        if "pass" not in dim_data or not isinstance(dim_data["pass"], bool):
            raise ValueError(f"{dim}.pass Boolean olmali")
        if "reasoning" not in dim_data or not isinstance(dim_data["reasoning"], str):
            raise ValueError(f"{dim}.reasoning string olmali")

    # Overall + spirit_score dogrula
    if data.get("overall") not in ("pass", "fail", "partial"):
        raise ValueError(f"overall pass/fail/partial olmali, gelen: {data.get('overall')!r}")
    score = data.get("spirit_score")
    if not isinstance(score, int) or score < 0 or score > 6:
        raise ValueError(f"spirit_score 0-6 int olmali, gelen: {score!r}")

    # Spirit_score ve overall tutarlilik (warning, exception degil)
    actual_passes = sum(1 for d in RUBRIC_DIMS if data[d]["pass"])
    if actual_passes != score:
        data["_consistency_warning"] = (
            f"spirit_score ({score}) ile gercek pass sayisi ({actual_passes}) eslemiyor"
        )

    return data


def _call_llm_judge(cikti_metni: str, model: str = DEFAULT_MODEL) -> tuple[str, dict]:
    """litellm ile judge cagrisi yap. Donus: (response_text, usage_dict)."""
    # Once API key check (mock testler icin onemli — litellm sistemde olmayabilir)
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError(
            "ANTHROPIC_API_KEY env'de bulunamadi. .env'de tanimli mi? "
            "Workspace tarafinda calistirir misin?"
        )

    try:
        import litellm
    except ImportError:
        raise RuntimeError("litellm kurulu degil. pip install litellm")

    user_prompt = (
        "Asagidaki ciktiyi Tier 3/4 disiplinine anlamsal olarak degerlendir. "
        "Strict JSON dondur.\n\n"
        f"CIKTI METNI:\n---\n{cikti_metni}\n---"
    )

    # Anthropic provider icin prompt caching (kit pattern ile uyumlu)
    messages = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": JUDGE_SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
        },
        {"role": "user", "content": user_prompt},
    ]

    response = litellm.completion(
        model=model,
        messages=messages,
        temperature=0.2,  # Dusuk varyans — degerlendirme tutarli olsun
        max_tokens=2000,
    )

    response_text = response.choices[0].message.content
    usage = {
        "input_tokens": getattr(response.usage, "prompt_tokens", 0),
        "output_tokens": getattr(response.usage, "completion_tokens", 0),
        "cache_read_tokens": getattr(response.usage, "cache_read_input_tokens", 0) or 0,
    }
    return response_text, usage


def judge_cikti(
    cikti_metni: str,
    model: str = DEFAULT_MODEL,
    max_budget_usd: float = DEFAULT_MAX_BUDGET_USD,
    max_cumulative_usd: float = DEFAULT_MAX_CUMULATIVE_USD,
    skip_cost_guard: bool = False,
) -> dict:
    """Ana judge fonksiyonu. Cost guard + LLM call + parse.

    Donus dict: rubric + overall + spirit_score + cost (USD) + meta.
    """
    if not skip_cost_guard:
        ok, hata = _check_cost_guards(cikti_metni, max_budget_usd, max_cumulative_usd)
        if not ok:
            raise RuntimeError(hata)

    response_text, usage = _call_llm_judge(cikti_metni, model)
    sonuc = _parse_judge_response(response_text)

    # Gercek maliyet ekle
    cost = _calculate_actual_cost(
        usage["input_tokens"],
        usage["output_tokens"],
        usage["cache_read_tokens"],
    )
    sonuc["_meta"] = {
        "model": model,
        "input_tokens": usage["input_tokens"],
        "output_tokens": usage["output_tokens"],
        "cache_read_tokens": usage["cache_read_tokens"],
        "cost_usd": round(cost, 6),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Cumulative state guncelle
    if not skip_cost_guard:
        u = _load_usage()
        u["cumulative_usd"] = u.get("cumulative_usd", 0.0) + cost
        u["call_count"] = u.get("call_count", 0) + 1
        _save_usage(u)

    return sonuc


def _ozet_yazdir(sonuc: dict) -> None:
    """Insan-okur cikti."""
    print("=" * 60)
    print("Ragip Aga — LLM-Judge Spirit Olcumu (Tier 3/4)")
    print("=" * 60)
    print()
    for dim in RUBRIC_DIMS:
        d = sonuc[dim]
        marker = "[PASS]" if d["pass"] else "[FAIL]"
        print(f"{marker} {dim}")
        print(f"       {d['reasoning']}")
        print()

    print(f"OVERALL         : {sonuc['overall'].upper()}")
    print(f"Spirit Score    : {sonuc['spirit_score']}/6")
    if sonuc.get("notes"):
        print(f"Notes           : {sonuc['notes']}")
    if sonuc.get("_consistency_warning"):
        print(f"WARNING         : {sonuc['_consistency_warning']}")
    print()
    meta = sonuc.get("_meta", {})
    print(f"Model           : {meta.get('model', '?')}")
    print(f"Tokens (in/out) : {meta.get('input_tokens', 0)}/{meta.get('output_tokens', 0)}")
    if meta.get("cache_read_tokens", 0) > 0:
        print(f"Cache hit       : {meta['cache_read_tokens']} tokens")
    print(f"Cost            : ${meta.get('cost_usd', 0):.6f}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="LLM-judge: Tier 3/4 disiplin Spirit (anlamsal) olcumu",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Exit: 0=pass, 2=fail/partial, 1=hata (cost limit, API key, parse)",
    )
    parser.add_argument("dosya", help="Dogrulanacak cikti dosyasi yolu, veya '-' stdin icin")
    parser.add_argument("--json", action="store_true", help="JSON formatinda sonuc bas")
    parser.add_argument(
        "--model", default=DEFAULT_MODEL,
        help=f"Judge model (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--max-budget-usd", type=float, default=DEFAULT_MAX_BUDGET_USD,
        help=f"Tek cagri max maliyet USD (default: {DEFAULT_MAX_BUDGET_USD})",
    )
    parser.add_argument(
        "--max-cumulative-usd", type=float, default=DEFAULT_MAX_CUMULATIVE_USD,
        help=f"Haftalik toplam max maliyet USD (default: {DEFAULT_MAX_CUMULATIVE_USD})",
    )
    parser.add_argument(
        "--skip-cost-guard", action="store_true",
        help="Cost guard'i devre disi birak (TEHLIKELI — test/debug icin)",
    )
    args = parser.parse_args()

    try:
        if args.dosya == "-":
            metin = sys.stdin.read()
        else:
            metin = Path(args.dosya).read_text(encoding="utf-8")
    except (FileNotFoundError, PermissionError) as e:
        print(f"HATA: {e}", file=sys.stderr)
        return 1

    try:
        sonuc = judge_cikti(
            metin,
            model=args.model,
            max_budget_usd=args.max_budget_usd,
            max_cumulative_usd=args.max_cumulative_usd,
            skip_cost_guard=args.skip_cost_guard,
        )
    except (RuntimeError, ValueError) as e:
        print(f"HATA: {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(sonuc, ensure_ascii=False, indent=2))
    else:
        _ozet_yazdir(sonuc)

    # Exit: pass=0, fail/partial=2
    return 0 if sonuc["overall"] == "pass" else 2


if __name__ == "__main__":
    sys.exit(main())
