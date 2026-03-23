"""Ragip Aga PII temizleyici — manifest ve log ciktilarinda kisisel veri korumasi.

Uc katman:
  Yuksek risk (maskele): email, telefon, TCKN → '***EMAIL***' vb.
  Orta risk (hash'le): firma, musteri, yetkili → 'h:a1b2c3d4'
  Dusuk risk (gecir): tutar, tarih, agent, skill vb.

Kullanim:
    from ragip_pii import metin_temizle, kayit_temizle

    temiz = metin_temizle("Ahmet Bey ahmet@firma.com 05321234567")
    # → "Ahmet Bey ***EMAIL*** ***TEL***"

    kayit = kayit_temizle({"firma": "Geneks Kimya", "tutar": 1000})
    # → {"firma": "h:3a7f2b1c", "tutar": 1000}
"""
import hashlib
import re

# ── Yuksek risk: regex ile maskele ──────────────────────────────────────────

_YUKSEK_DESENLER = [
    # Email
    (re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'), '***EMAIL***'),
    # Turk telefon: +90 veya 0 ile baslayan 10 haneli
    (re.compile(r'(?:\+90|0)\s?[\s\-]?\(?\d{3}\)?\s?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}'), '***TEL***'),
    # TCKN: tam 11 haneli sayi (kelime sinirinda)
    (re.compile(r'\b\d{11}\b'), '***TCKN***'),
    # IBAN: TR ile baslayan 26 karakter
    (re.compile(r'\bTR\d{2}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{2}\b'), '***IBAN***'),
]

# ── Orta risk: alan adina gore hash'le ──────────────────────────────────────

_ORTA_ALANLAR = {'firma', 'firma_slug', 'musteri', 'yetkili', 'sorumlu',
                 'firma_adi', 'musteri_adi', 'ilgili_kisi'}


def _hash_deger(deger):
    """Degeri SHA-256 hash'inin ilk 8 karakterine donusturur.

    Deterministik: ayni girdi her zaman ayni hash uretir.
    Geri donusturulemez: orijinal deger hash'ten cikarilmaz.
    """
    return "h:" + hashlib.sha256(str(deger).encode('utf-8')).hexdigest()[:8]


def metin_temizle(metin):
    """Metindeki yuksek riskli PII desenlerini maskeler.

    Args:
        metin: Temizlenecek metin

    Returns:
        str: Maskelenmis metin
    """
    if not isinstance(metin, str) or not metin:
        return metin
    for desen, maske in _YUKSEK_DESENLER:
        metin = desen.sub(maske, metin)
    return metin


def kayit_temizle(kayit, orta_alanlar=None):
    """Dict kaydindaki PII alanlarini temizler.

    Orta risk alanlari (firma, musteri vb.) hash'lenir.
    Tum string degerlerde yuksek risk desenleri (email, tel) maskelenir.
    Orijinal dict degismez — yeni kopya dondurulur.

    Args:
        kayit: dict — manifest veya log kaydi
        orta_alanlar: set — hash'lenecek alan adlari (varsayilan: _ORTA_ALANLAR)

    Returns:
        dict: Temizlenmis kopya
    """
    if not isinstance(kayit, dict):
        return kayit
    if orta_alanlar is None:
        orta_alanlar = _ORTA_ALANLAR
    temiz = {}
    for k, v in kayit.items():
        if k in orta_alanlar and isinstance(v, str) and v:
            temiz[k] = _hash_deger(v)
        elif isinstance(v, str):
            temiz[k] = metin_temizle(v)
        else:
            temiz[k] = v
    return temiz
