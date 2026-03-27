"""Ragip Aga PII temizleyici — manifest ve log ciktilarinda kisisel veri korumasi.

Uc katman:
  Yuksek risk (maskele): email, telefon, TCKN → '***EMAIL***' vb.
  Orta risk (hash'le): firma, musteri, yetkili → 'h:a1b2c3d4'
  Dusuk risk (gecir): tutar, tarih, agent, skill vb.

Geri donusturulabilir maskeleme (sozlesme analizi icin):
  maskele_geri_donusturulabilir(metin) → (maskelenmis, mapping)
  geri_cevir(metin, mapping) → orijinal degerlerle metin

Kullanim:
    from ragip_pii import metin_temizle, kayit_temizle

    temiz = metin_temizle("Ahmet Bey ahmet@firma.com 05321234567")
    # → "Ahmet Bey ***EMAIL*** ***TEL***"

    kayit = kayit_temizle({"firma": "Geneks Kimya", "tutar": 1000})
    # → {"firma": "h:3a7f2b1c", "tutar": 1000}

    # Geri donusturulabilir (sozlesme analizi):
    from ragip_pii import maskele_geri_donusturulabilir, geri_cevir

    masked, mapping = maskele_geri_donusturulabilir(
        "Gibibyte ile ABC Holding arasinda 500.000 TL tutarinda sozlesme",
        firma_adlari=["Gibibyte", "ABC Holding"]
    )
    # masked: "[FIRMA_1] ile [FIRMA_2] arasinda [TUTAR_1] tutarinda sozlesme"
    # mapping: {"FIRMA_1": "Gibibyte", "FIRMA_2": "ABC Holding", "TUTAR_1": "500.000 TL"}

    orijinal = geri_cevir("[FIRMA_1] yukumlulugu", mapping)
    # → "Gibibyte yukumlulugu"
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


# ── Geri donusturulabilir maskeleme (sozlesme analizi) ────────────────────

# Tutar desenleri: 500.000 TL, 1.250.000,50 TRY, 10.000 USD, $5,000 vb.
_TUTAR_DESENI = re.compile(
    r'(?:[\$€£])\s?[\d.,]+|'                        # $5,000 veya €1.000
    r'[\d]{1,3}(?:[.,]\d{3})*(?:[.,]\d{1,2})?\s*'    # 500.000 veya 1,250.50
    r'(?:TL|TRY|USD|EUR|GBP|₺|\$|€|£)'               # para birimi
)

# Tarih desenleri: 27.03.2026, 27/03/2026, 2026-03-27
_TARIH_DESENI = re.compile(
    r'\b\d{1,2}[./]\d{1,2}[./]\d{4}\b|'   # 27.03.2026 veya 27/03/2026
    r'\b\d{4}-\d{2}-\d{2}\b'               # 2026-03-27
)

# Adres ipuclari: "... Mah. ... Sok. No: ... / ..." seklinde
_ADRES_DESENI = re.compile(
    r'(?:(?:Mah|Sok|Cad|Bul|Apt|Sit|Blok|Kat|No|Daire)[.:]?\s*[\w\d/,\s]{3,60})',
    re.IGNORECASE
)


def maskele_geri_donusturulabilir(metin, firma_adlari=None, kisi_adlari=None):
    """Metni geri donusturulabilir sekilde maskeler.

    Sozlesme analizi icin: orijinal PII yerine placeholder koyar,
    mapping dict'i ile geri cevrilebilir.

    Args:
        metin: Maskelenecek metin
        firma_adlari: Bilinen firma adlari listesi (opsiyonel)
        kisi_adlari: Bilinen kisi adlari listesi (opsiyonel)

    Returns:
        tuple: (maskelenmis_metin, mapping_dict)
    """
    if not isinstance(metin, str) or not metin:
        return metin, {}

    mapping = {}
    maskelenmis = metin
    sayac = {'FIRMA': 0, 'KISI': 0, 'EMAIL': 0, 'TEL': 0,
             'TCKN': 0, 'IBAN': 0, 'TUTAR': 0, 'TARIH': 0, 'ADRES': 0}

    def _yeni_placeholder(tip, deger):
        sayac[tip] += 1
        ph = f"[{tip}_{sayac[tip]}]"
        mapping[ph] = deger
        return ph

    # 1. Bilinen firma adlarini maskele (en uzundan en kisaya — greedy match)
    if firma_adlari:
        for firma in sorted(firma_adlari, key=len, reverse=True):
            if firma and firma in maskelenmis:
                ph = _yeni_placeholder('FIRMA', firma)
                maskelenmis = maskelenmis.replace(firma, ph)

    # 2. Bilinen kisi adlarini maskele
    if kisi_adlari:
        for kisi in sorted(kisi_adlari, key=len, reverse=True):
            if kisi and kisi in maskelenmis:
                ph = _yeni_placeholder('KISI', kisi)
                maskelenmis = maskelenmis.replace(kisi, ph)

    # 3. Yuksek risk regex desenleri
    for desen, tip in [(_YUKSEK_DESENLER[0][0], 'EMAIL'),
                       (_YUKSEK_DESENLER[1][0], 'TEL'),
                       (_YUKSEK_DESENLER[2][0], 'TCKN'),
                       (_YUKSEK_DESENLER[3][0], 'IBAN')]:
        for match in desen.finditer(maskelenmis):
            orijinal = match.group()
            if orijinal.startswith('['):  # zaten maskelenmis
                continue
            ph = _yeni_placeholder(tip, orijinal)
            maskelenmis = maskelenmis.replace(orijinal, ph, 1)

    # 4. Tutarlar
    for match in _TUTAR_DESENI.finditer(maskelenmis):
        orijinal = match.group()
        if orijinal.startswith('['):
            continue
        ph = _yeni_placeholder('TUTAR', orijinal)
        maskelenmis = maskelenmis.replace(orijinal, ph, 1)

    # 5. Tarihler
    for match in _TARIH_DESENI.finditer(maskelenmis):
        orijinal = match.group()
        if orijinal.startswith('['):
            continue
        ph = _yeni_placeholder('TARIH', orijinal)
        maskelenmis = maskelenmis.replace(orijinal, ph, 1)

    # 6. Adresler
    for match in _ADRES_DESENI.finditer(maskelenmis):
        orijinal = match.group()
        if orijinal.startswith('['):
            continue
        ph = _yeni_placeholder('ADRES', orijinal)
        maskelenmis = maskelenmis.replace(orijinal, ph, 1)

    return maskelenmis, mapping


def geri_cevir(metin, mapping):
    """Maskelenmis metindeki placeholder'lari orijinal degerlerle degistirir.

    Args:
        metin: Placeholder iceren maskelenmis metin
        mapping: {placeholder: orijinal_deger} dict

    Returns:
        str: Orijinal degerlerle metin
    """
    if not isinstance(metin, str) or not metin or not mapping:
        return metin
    sonuc = metin
    # En uzun placeholder'dan baslayarak degistir (ic ice gecme onlemi)
    for ph in sorted(mapping.keys(), key=len, reverse=True):
        sonuc = sonuc.replace(ph, mapping[ph])
    return sonuc


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
