#!/usr/bin/env python3
"""Ragip Aga Tier 3/4 format validation — LLM ciktilarinda blok format eksigi tespiti.

Tier 5 savunma katmani (ADR-0019). Prompt-engineering ile saglanamayan Tier 3
zenginlestirilmis blok formati (TESPIT/Etki/POZISYON/GEREKCE) ve Tier 4
tutarlilik denetimi notu eksigini deterministik regex ile tespit eder.

Sinyaller:
    [T3-1] TESPIT: <insight> bullet
    [T3-2] Etki: <X TL/USD> (%Y) <yon> <horizon> satiri
    [T3-3] POZISYON: <fiil> · Sahip: <kim> · Zaman: <ne zaman> · Beklenen: <X>
    [T3-4] anapara/Anapara (nominal) veya (kalan) etiket (anapara gectiyse zorunlu)
    [T4]   Tutarlilik denetimi: <temiz / X celiski bulundu> kapanis notu

Kullanim:
    python3 scripts/ragip_format_dogrula.py <cikti.md>
    python3 scripts/ragip_format_dogrula.py --json <cikti.md>
    cat cikti.md | python3 scripts/ragip_format_dogrula.py -

Exit:
    0 = format temiz (tum zorunlu sinyaller mevcut)
    2 = format eksik (en az 1 zorunlu sinyal yok)
    1 = hata (dosya yok vs.)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

KIT_ROOT = Path(__file__).resolve().parents[1]

# Regex desenleri — case-sensitive (TESPIT vs tespit fark eder, format disipline tabi).
RE_TESPIT = re.compile(r"^TESPIT:\s*\S+", re.MULTILINE)
RE_ETKI = re.compile(r"^\s+Etki:\s*\S+", re.MULTILINE)
RE_POZISYON = re.compile(r"^POZISYON:\s*\S+", re.MULTILINE)
# POZISYON 5-bilesen (fiil + Sahip + Zaman + Beklenen). GEREKCE opsiyonel.
# Multi-line destegi (v2.19.1): LLM POZISYON: + Sahip/Zaman/Beklenen'i 2 ayri satira
# yazabilir (16 Mayis 2026 5. davranissal kosum gozlemi). POZISYON: ile sonraki
# 1-3 satir araliginda Sahip/Zaman/Beklenen ara. [\s\S]{1,300}? newline-iceren
# non-greedy, max ~300 char (yaklasik 3-4 satir).
RE_POZ_5BIL = re.compile(
    r"^POZISYON:[\s\S]{1,300}?Sahip:[\s\S]{1,100}?Zaman:[\s\S]{1,100}?Beklenen:",
    re.MULTILINE,
)
# Anapara etiketi — anapara/Anapara kelimesi gectikten sonra (nominal) veya (kalan)
RE_ANAPARA_GECTI = re.compile(r"[Aa]napara", re.UNICODE)
RE_ANAPARA_ETIKET = re.compile(
    r"[Aa]napara\s*\((nominal|kalan)\)",
    re.UNICODE,
)
# Tier 4 kapanis notu — "Tutarlilik denetimi:" satiri (rapor sonunda)
RE_TUTARLILIK = re.compile(
    r"^[*_>\s]*Tutarlilik denetimi:\s*(temiz|.*celiski)",
    re.MULTILINE | re.IGNORECASE,
)


def dogrula_metin(metin: str) -> dict:
    """Metni Tier 3/4 sinyalleri icin tara. Donus: sayim + eksik liste."""
    tespit_count = len(RE_TESPIT.findall(metin))
    etki_count = len(RE_ETKI.findall(metin))
    poz_count = len(RE_POZISYON.findall(metin))
    poz_5bil_count = len(RE_POZ_5BIL.findall(metin))
    anapara_gecti = bool(RE_ANAPARA_GECTI.search(metin))
    anapara_etiket_count = len(RE_ANAPARA_ETIKET.findall(metin))
    tutarlilik_count = len(RE_TUTARLILIK.findall(metin))

    eksikler: list[str] = []

    # Zorunlu sinyaller — her biri en az 1 olmali
    if tespit_count == 0:
        eksikler.append("[T3-1] TESPIT: bullet yok (SONUC VE ONERILER bolumunde Tier 3 blok bekleniyor)")
    if etki_count == 0:
        eksikler.append("[T3-2] Etki: satiri yok (TESPIT altinda $ tutar / % / yon / horizon)")
    if poz_count == 0:
        eksikler.append("[T3-3] POZISYON: bullet yok")
    elif poz_5bil_count < poz_count:
        eksikler.append(
            f"[T3-3] POZISYON 5-bilesen eksik: {poz_count} POZISYON bullet, "
            f"{poz_5bil_count} Sahip/Zaman/Beklenen ile dolu (fark: {poz_count - poz_5bil_count})"
        )

    # Anapara etiketi — sadece anapara kelimesi geciyorsa zorunlu
    if anapara_gecti and anapara_etiket_count == 0:
        eksikler.append(
            "[T3-4] Anapara etiketi yok (anapara/Anapara gecti ama (nominal) veya (kalan) etiket yok)"
        )

    # Tier 4 kapanis notu — tam 1 adet bekleniyor
    if tutarlilik_count == 0:
        eksikler.append("[T4] Tutarlilik denetimi notu yok (rapor sonunda 'Tutarlilik denetimi: temiz.' veya 'X celiski bulundu' bekleniyor)")

    # TESPIT vs POZISYON denge kontrolu (ucsut esit olmali — ideal)
    denge_uyari: str | None = None
    if tespit_count > 0 and poz_count > 0 and tespit_count != poz_count:
        denge_uyari = (
            f"TESPIT count ({tespit_count}) ile POZISYON count ({poz_count}) eslemiyor — "
            "her TESPIT icin 1 POZISYON bekleniyor"
        )

    return {
        "tespit_count": tespit_count,
        "etki_count": etki_count,
        "pozisyon_count": poz_count,
        "pozisyon_5bilesen_count": poz_5bil_count,
        "anapara_gecti": anapara_gecti,
        "anapara_etiket_count": anapara_etiket_count,
        "tutarlilik_denetimi_count": tutarlilik_count,
        "eksikler": eksikler,
        "denge_uyari": denge_uyari,
        "temiz": len(eksikler) == 0,
    }


def _ozet_yazdir(sonuc: dict) -> None:
    print("=" * 60)
    print("Ragip Aga — Tier 3/4 Format Dogrulama")
    print("=" * 60)
    print(f"TESPIT bullet      : {sonuc['tespit_count']}")
    print(f"Etki satiri        : {sonuc['etki_count']}")
    print(f"POZISYON bullet    : {sonuc['pozisyon_count']} (5-bilesen dolu: {sonuc['pozisyon_5bilesen_count']})")
    print(f"Anapara etiket     : {sonuc['anapara_etiket_count']} (anapara gecti: {sonuc['anapara_gecti']})")
    print(f"Tutarlilik denetimi: {sonuc['tutarlilik_denetimi_count']}")
    print()

    if sonuc["denge_uyari"]:
        print(f"UYARI: {sonuc['denge_uyari']}")
        print()

    if sonuc["eksikler"]:
        print(f"EKSIK SINYAL ({len(sonuc['eksikler'])} adet):")
        for e in sonuc["eksikler"]:
            print(f"  - {e}")
        print()
        print("Cozum: ragip-degerlendirme / ragip-analiz / ragip-strateji skill'ini")
        print("tekrar cagir veya eksik bloklari el ile ekle. Detay: ADR-0019.")
    else:
        print("Tum Tier 3/4 sinyalleri mevcut. [TEMIZ]")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="LLM ciktisinda Tier 3/4 blok format ve tutarlilik denetimi notu dogrula.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Exit: 0=temiz, 2=eksik sinyal, 1=hata",
    )
    parser.add_argument("dosya", help="Dogrulanacak dosya yolu, veya '-' stdin icin")
    parser.add_argument("--json", action="store_true", help="JSON formatinda sonuc bas")
    args = parser.parse_args()

    try:
        if args.dosya == "-":
            metin = sys.stdin.read()
        else:
            metin = Path(args.dosya).read_text(encoding="utf-8")
    except (FileNotFoundError, PermissionError) as e:
        print(f"HATA: {e}", file=sys.stderr)
        return 1

    sonuc = dogrula_metin(metin)

    if args.json:
        print(json.dumps(sonuc, ensure_ascii=False, indent=2))
    else:
        _ozet_yazdir(sonuc)

    return 0 if sonuc["temiz"] else 2


if __name__ == "__main__":
    sys.exit(main())
