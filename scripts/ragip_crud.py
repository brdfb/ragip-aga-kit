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
