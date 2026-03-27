"""Ragip Aga CRUD skill'leri için paylaşımlı yardımcı fonksiyonlar."""
import json
import subprocess
import os
from pathlib import Path
from datetime import date


def get_root():
    """Git repo kökünü döndürür."""
    return subprocess.check_output(
        ['git', 'rev-parse', '--show-toplevel'],
        text=True, stderr=subprocess.DEVNULL
    ).strip()


def data_path(filename):
    """data/RAGIP_AGA/ altında dosya yolu döndürür, dizini oluşturur."""
    p = Path(get_root()) / 'data' / 'RAGIP_AGA' / filename
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def load_jsonl(path):
    """JSONL dosyasını oku → list[dict]. Dosya yoksa boş liste."""
    p = Path(path)
    if not p.exists():
        return []
    content = p.read_text('utf-8').strip()
    if not content:
        return []
    return [json.loads(line) for line in content.split('\n') if line.strip()]


def save_jsonl(path, records):
    """Atomic JSONL yazma (tmp → rename)."""
    p = Path(path)
    tmp = p.with_suffix('.tmp')
    tmp.write_text(
        '\n'.join(json.dumps(r, ensure_ascii=False) for r in records) + '\n',
        'utf-8'
    )
    tmp.rename(p)


def load_json(path):
    """Tekil JSON oku → dict. Dosya yoksa None."""
    p = Path(path)
    if not p.exists():
        return None
    return json.loads(p.read_text('utf-8'))


def save_json(path, data):
    """Atomic JSON yazma."""
    p = Path(path)
    tmp = p.with_suffix('.tmp')
    tmp.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + '\n',
        'utf-8'
    )
    tmp.rename(p)


def parse_kv(args_str):
    """'key1=val1 key2=val2' → {'key1': 'val1', 'key2': 'val2'}"""
    result = {}
    for kv in args_str.split():
        if '=' in kv:
            k, v = kv.split('=', 1)
            result[k.strip()] = v.strip()
    return result


def next_id(records):
    """Sonraki integer ID."""
    return max((int(r.get('id', 0)) for r in records), default=0) + 1


def today():
    """Bugünün tarihini string olarak döndürür."""
    return str(date.today())


# --- Fatura Validasyonu (ADR-0007 sema uyumu) ---

_FATURA_ZORUNLU = ('id', 'fatura_no', 'firma_id', 'yon', 'tutar', 'toplam',
                   'fatura_tarihi', 'vade_tarihi', 'durum')
_YON_DEGERLERI = ('alacak', 'borc')
_DURUM_DEGERLERI = ('acik', 'odendi', 'kismi', 'iptal')
_ISO_DATE_RE = None  # lazy compile


def _iso_date_pattern():
    """ISO 8601 tarih regex'i (YYYY-MM-DD). Lazy compile."""
    global _ISO_DATE_RE
    if _ISO_DATE_RE is None:
        import re
        _ISO_DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    return _ISO_DATE_RE


def validate_fatura(record):
    """Tek fatura kaydını ADR-0007 şemasına göre doğrular.

    Args:
        record: dict — fatura kaydı

    Returns:
        list[str] — hata mesajları listesi (boş = geçerli)
    """
    errors = []

    # Zorunlu alan kontrolü
    for alan in _FATURA_ZORUNLU:
        if alan not in record:
            errors.append(f"zorunlu alan eksik: {alan}")

    # Erken dönüş — zorunlu alanlar yoksa tip kontrolleri anlamsız
    if errors:
        return errors

    # yon enum kontrolü
    if record['yon'] not in _YON_DEGERLERI:
        errors.append(f"gecersiz yon: '{record['yon']}' (beklenen: alacak|borc)")

    # durum enum kontrolü
    if record['durum'] not in _DURUM_DEGERLERI:
        errors.append(f"gecersiz durum: '{record['durum']}' (beklenen: acik|odendi|kismi|iptal)")

    # firma_id tip kontrolü (int veya str kabul, diger tipler hata)
    fid = record['firma_id']
    if not isinstance(fid, (int, str)):
        errors.append(f"firma_id int veya str olmali: {type(fid).__name__}")

    # Sayısal alan tip kontrolü
    for alan in ('tutar', 'toplam'):
        val = record[alan]
        if not isinstance(val, (int, float)):
            errors.append(f"{alan} sayisal olmali: {type(val).__name__}")

    # Tarih format kontrolü (ISO 8601)
    pat = _iso_date_pattern()
    for alan in ('fatura_tarihi', 'vade_tarihi'):
        val = record[alan]
        if not isinstance(val, str) or not pat.match(val):
            errors.append(f"{alan} ISO 8601 formatta olmali (YYYY-MM-DD): '{val}'")

    # Opsiyonel alan tip kontrolleri
    if 'odeme_tutari' in record and record['odeme_tutari'] is not None:
        if not isinstance(record['odeme_tutari'], (int, float)):
            errors.append(f"odeme_tutari sayisal olmali: {type(record['odeme_tutari']).__name__}")

    if 'odeme_tarihi' in record and record['odeme_tarihi'] is not None:
        val = record['odeme_tarihi']
        if not isinstance(val, str) or not pat.match(val):
            errors.append(f"odeme_tarihi ISO 8601 formatta olmali: '{val}'")

    if 'para_birimi' in record:
        pb = record['para_birimi']
        if not isinstance(pb, str) or len(pb) != 3:
            errors.append(f"para_birimi ISO 4217 (3 harf) olmali: '{pb}'")

    # Doviz kuru kontrolleri (fatura_kuru, odeme_kuru)
    for kur_alan in ('fatura_kuru', 'odeme_kuru'):
        if kur_alan in record and record[kur_alan] is not None:
            val = record[kur_alan]
            if not isinstance(val, (int, float)):
                errors.append(f"{kur_alan} sayisal olmali: {type(val).__name__}")
            elif val <= 0:
                errors.append(f"{kur_alan} pozitif olmali: {val}")

    # Kısmi ödeme tutarlılığı
    if record['durum'] == 'kismi':
        ot = record.get('odeme_tutari')
        if ot is None:
            errors.append("durum=kismi ama odeme_tutari yok")
        elif isinstance(ot, (int, float)) and isinstance(record['toplam'], (int, float)):
            if ot >= record['toplam']:
                errors.append(f"durum=kismi ama odeme_tutari({ot}) >= toplam({record['toplam']})")

    return errors


_SOZLESME_TURLERI = {'gizlilik', 'hizmet', 'tedarik', 'distributorluk', 'diger'}
_SOZLESME_DURUMLARI = {'taslak', 'inceleme', 'imzali', 'aktif', 'suresi_doldu', 'iptal'}
_SOZLESME_ZORUNLU = ('id', 'firma', 'tur', 'durum', 'tarih')


def validate_sozlesme(record):
    """Sozlesme kaydini dogrular (sozlesmeler.jsonl semasi).

    Zorunlu: id, firma, tur, durum, tarih
    Opsiyonel: firma_id, dosya, masked_dosya, bitis_tarihi, taraflar,
               kaynak, aciklama, mapping

    Returns:
        list[str]: Hata mesajlari (bos = gecerli)
    """
    errors = []

    for alan in _SOZLESME_ZORUNLU:
        if alan not in record or record[alan] is None:
            errors.append(f"Zorunlu alan eksik: {alan}")

    if errors:
        return errors

    # tur kontrolu
    if record['tur'] not in _SOZLESME_TURLERI:
        errors.append(f"tur gecersiz: '{record['tur']}'. Gecerli: {sorted(_SOZLESME_TURLERI)}")

    # durum kontrolu
    if record['durum'] not in _SOZLESME_DURUMLARI:
        errors.append(f"durum gecersiz: '{record['durum']}'. Gecerli: {sorted(_SOZLESME_DURUMLARI)}")

    # tarih format
    pat = _iso_date_pattern()
    val = record['tarih']
    if not isinstance(val, str) or not pat.match(val):
        errors.append(f"tarih ISO 8601 formatta olmali (YYYY-MM-DD): '{val}'")

    if 'bitis_tarihi' in record and record['bitis_tarihi'] is not None:
        val = record['bitis_tarihi']
        if not isinstance(val, str) or not pat.match(val):
            errors.append(f"bitis_tarihi ISO 8601 formatta olmali: '{val}'")

    # taraflar list kontrolu
    if 'taraflar' in record and record['taraflar'] is not None:
        if not isinstance(record['taraflar'], list):
            errors.append("taraflar liste olmali")

    return errors


def validate_faturalar(records):
    """Birden fazla fatura kaydını doğrular.

    Args:
        records: list[dict] — fatura kayıtları

    Returns:
        tuple(list[dict], list[dict]) — (gecerli_kayitlar, hatali_kayitlar)
        Hatalı kayıtlara '_hatalar' anahtarı eklenir.
    """
    gecerli = []
    hatali = []
    for r in records:
        hatalar = validate_fatura(r)
        if hatalar:
            r_copy = dict(r)
            r_copy['_hatalar'] = hatalar
            hatali.append(r_copy)
        else:
            gecerli.append(r)
    return gecerli, hatali
