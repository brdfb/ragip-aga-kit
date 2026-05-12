#!/usr/bin/env python3
"""Ragip Aga citation validation — LLM ciktilarinda yasal madde halusinasyonu tespiti.

Tier 2 savunma (Tier 1 prompt-based Barnum filtresinin ustune): deterministik,
LLM dahil edilmez, ragip_get_rates.sh ve ragip_madde_dogrula tarz yardimcilar
gibi standalone calisir.

Akis:
    1. Cikti metnindeki kanun madde referanslarini regex ile cikar
       (TBK m.117, TTK m.21/2, IIK m.58, m.117-120 ranges)
    2. config/kanun_maddeleri.json'daki bilinen maddelerle karsilastir
    3. Bilinmeyen madde varsa "uydurma sanigi" olarak isaretle, exit 2

Kullanim:
    python3 scripts/ragip_madde_dogrula.py <cikti.md>
    python3 scripts/ragip_madde_dogrula.py --json <cikti.md>
    cat cikti.md | python3 scripts/ragip_madde_dogrula.py -
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

KIT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_KANUN_JSON = KIT_ROOT / "config" / "kanun_maddeleri.json"

# Generic kanun kodu pattern: 2-6 buyuk harf (Turkce dahil), m.X formati.
# Bilinen kanunlar JSON'dan gelir. Bilinmeyen kod "bilinmeyen_kanun" olarak isaretlenir
# (TCK m.207 gibi scope disi referanslar veya uydurma kanun adlari yakalanir).
KOD_PATTERN = r"([A-ZİĞÜŞÖÇ]{2,6})"
MADDE_TEK_RE = re.compile(
    rf"\b{KOD_PATTERN}\s*m(?:adde)?\.?\s*(\d+)(?:/(\d+))?(?:[-]([a-zA-ZçğıöşüİĞÜŞÖÇ]))?",
    re.UNICODE,
)
MADDE_RANGE_RE = re.compile(
    rf"\b{KOD_PATTERN}\s*m(?:adde)?\.?\s*(\d+)\s*[-–]\s*(\d+)\b",
    re.UNICODE,
)


def _normalize_kanun_kod(raw: str) -> str:
    """Turkce karakter normalize: 'İİK' -> 'IIK'."""
    return raw.replace("İ", "I").upper()


def _kanunlari_yukle(json_yolu: Path) -> dict:
    """kanun_maddeleri.json'u oku, kanunlar dict'i dondur."""
    if not json_yolu.exists():
        raise FileNotFoundError(f"Kanun maddeleri JSON bulunamadi: {json_yolu}")
    with open(json_yolu, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("kanunlar", {})


def madde_var_mi(kanun_kod: str, madde_no: str, kanunlar: dict) -> bool:
    """Belirli kanun + madde numarasi bilinen veri tabaninda var mi?

    Match fikra/bent detayina degil, base madde numarasina yapilir
    (m.21/2 var mi sorusu: TTK'da m.21 var mi ile cevaplanir).
    """
    kanun_kod = _normalize_kanun_kod(kanun_kod)
    if kanun_kod not in kanunlar:
        return False
    return madde_no in kanunlar[kanun_kod].get("maddeler", {})


def referanslari_cikar(metin: str) -> list[dict]:
    """Metinden tum madde referanslarini cikar.

    Donus: [{'kanun': 'TBK', 'madde': '117', 'fikra': '2', 'bent': 'c', 'ham': 'TBK m.117/2-c', 'range': False}]
    Range 'TBK m.117-120' -> 4 ayri referans (range=True).
    """
    bulunanlar: list[dict] = []
    gorulen_konum: set[tuple[int, int]] = set()

    # Once range'leri yakala (overlap'i engellemek icin)
    for m in MADDE_RANGE_RE.finditer(metin):
        kanun = _normalize_kanun_kod(m.group(1))
        baslangic = int(m.group(2))
        bitis = int(m.group(3))
        if bitis < baslangic or bitis - baslangic > 50:
            # Bariz bozuk range — tek madde olarak kaydet
            bulunanlar.append({
                "kanun": kanun,
                "madde": str(baslangic),
                "fikra": None,
                "bent": None,
                "ham": m.group(0),
                "range": False,
            })
        else:
            for n in range(baslangic, bitis + 1):
                bulunanlar.append({
                    "kanun": kanun,
                    "madde": str(n),
                    "fikra": None,
                    "bent": None,
                    "ham": m.group(0),
                    "range": True,
                })
        gorulen_konum.add((m.start(), m.end()))

    # Sonra tek/fikra/bent eslesmeleri (range icindekiler atlanir)
    for m in MADDE_TEK_RE.finditer(metin):
        if any(m.start() >= s and m.end() <= e for s, e in gorulen_konum):
            continue
        bulunanlar.append({
            "kanun": _normalize_kanun_kod(m.group(1)),
            "madde": m.group(2),
            "fikra": m.group(3),
            "bent": m.group(4),
            "ham": m.group(0),
            "range": False,
        })

    return bulunanlar


def dogrula_metin(metin: str, json_yolu: Path = DEFAULT_KANUN_JSON) -> dict:
    """Metni dogrula. Donus: bulunan/dogrulananlar/uydurma_sanigi listeleri + ozet."""
    kanunlar = _kanunlari_yukle(json_yolu)
    referanslar = referanslari_cikar(metin)

    dogrulananlar: list[dict] = []
    uydurma_sanigi: list[dict] = []
    bilinmeyen_kanun: list[dict] = []

    for ref in referanslar:
        if ref["kanun"] not in kanunlar:
            bilinmeyen_kanun.append(ref)
            continue
        if madde_var_mi(ref["kanun"], ref["madde"], kanunlar):
            dogrulananlar.append(ref)
        else:
            uydurma_sanigi.append(ref)

    return {
        "toplam_referans": len(referanslar),
        "dogrulanan": len(dogrulananlar),
        "uydurma_sanigi": len(uydurma_sanigi),
        "bilinmeyen_kanun": len(bilinmeyen_kanun),
        "referanslar": referanslar,
        "dogrulananlar": dogrulananlar,
        "uydurma_sanigi_detay": uydurma_sanigi,
        "bilinmeyen_kanun_detay": bilinmeyen_kanun,
    }


def _ozet_yazdir(sonuc: dict) -> None:
    print("=" * 60)
    print("Ragip Aga — Yasal Madde Dogrulama")
    print("=" * 60)
    print(f"Toplam referans:    {sonuc['toplam_referans']}")
    print(f"Dogrulanan:         {sonuc['dogrulanan']}")
    print(f"Uydurma sanigi:     {sonuc['uydurma_sanigi']}")
    print(f"Bilinmeyen kanun:   {sonuc['bilinmeyen_kanun']}")
    print()

    if sonuc["uydurma_sanigi"] > 0:
        print("UYDURMA SANIGI MADDELER (kanun_maddeleri.json'da yok):")
        for r in sonuc["uydurma_sanigi_detay"]:
            print(f"  - {r['ham']}  (kanun={r['kanun']}, madde={r['madde']})")
        print()

    if sonuc["bilinmeyen_kanun"] > 0:
        print("BILINMEYEN KANUN KODU:")
        for r in sonuc["bilinmeyen_kanun_detay"]:
            print(f"  - {r['ham']}  (kanun={r['kanun']})")
        print()

    if sonuc["dogrulanan"] > 0 and sonuc["uydurma_sanigi"] == 0:
        print("Tum referanslar dogrulandi. ✓")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="LLM ciktisindaki yasal madde referanslarini dogrula.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Exit: 0=temiz, 2=uydurma sanigi var, 1=hata",
    )
    parser.add_argument("dosya", help="Dogrulanacak dosya yolu, veya '-' stdin icin")
    parser.add_argument("--json", action="store_true", help="JSON formatinda sonuc bas")
    parser.add_argument(
        "--kanunlar",
        default=str(DEFAULT_KANUN_JSON),
        help=f"Kanun maddeleri JSON yolu (varsayilan: {DEFAULT_KANUN_JSON})",
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

    sonuc = dogrula_metin(metin, Path(args.kanunlar))

    if args.json:
        print(json.dumps(sonuc, ensure_ascii=False, indent=2))
    else:
        _ozet_yazdir(sonuc)

    return 2 if sonuc["uydurma_sanigi"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
