"""Ragip Aga yapilandirilmis hata siniflandirmasi.

Kit genelinde hatalari 3 kategoriye ayirir:
- GECICI: Ag, timeout, disk I/O — retry mantikli
- KALICI: Parametre/veri hatasi — retry anlamsiz, girdiyi duzelt
- POLITIKA: Schema ihlali (ADR-0007) — veriyi duzelt

Kullanim:
    from ragip_errors import RagipHata, HataTuru, siniflandir, tekrar_denenebilir

    try:
        save_jsonl(...)
    except Exception as e:
        if tekrar_denenebilir(e):
            # retry
        else:
            raise RagipHata("Kayit yazilamadi", tur=siniflandir(e), kaynak="crud", orijinal=e)
"""
import enum


class HataTuru(enum.Enum):
    """Hata kategorisi."""
    GECICI = "gecici"       # ConnectionError, TimeoutError, URLError — retry mantikli
    KALICI = "kalici"       # ValueError, KeyError, TypeError — veri/parametre hatasi
    POLITIKA = "politika"   # Schema validation, ADR-0007 ihlali — veriyi duzelt


class RagipHata(Exception):
    """Kit genelinde yapilandirilmis hata.

    Attributes:
        tur: HataTuru — GECICI, KALICI veya POLITIKA
        kaynak: str — hatanin kaynagi ('rates', 'crud', 'output', 'pii')
        orijinal: Exception | None — sarmalanan orijinal exception
    """
    def __init__(self, mesaj, tur=HataTuru.KALICI, kaynak=None, orijinal=None):
        super().__init__(mesaj)
        self.tur = tur
        self.kaynak = kaynak
        self.orijinal = orijinal


def siniflandir(exc):
    """Exception'i HataTuru'ne siniflandirir.

    Args:
        exc: Exception instance

    Returns:
        HataTuru
    """
    if isinstance(exc, RagipHata):
        return exc.tur
    if isinstance(exc, (ConnectionError, TimeoutError, OSError)):
        return HataTuru.GECICI
    if isinstance(exc, (ValueError, KeyError, TypeError)):
        return HataTuru.KALICI
    # urllib.error.URLError — ag hatasi, gecici
    try:
        import urllib.error
        if isinstance(exc, urllib.error.URLError):
            return HataTuru.GECICI
    except ImportError:
        pass
    return HataTuru.KALICI  # Varsayilan: kalici


def tekrar_denenebilir(exc):
    """Exception retry'a uygun mu?

    Args:
        exc: Exception instance

    Returns:
        bool: True ise retry mantikli
    """
    return siniflandir(exc) == HataTuru.GECICI
