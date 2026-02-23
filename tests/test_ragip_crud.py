"""
ragip_crud.py — Paylaşımlı CRUD yardımcı fonksiyonları unit testleri.
"""
import json
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from ragip_crud import parse_kv, load_jsonl, save_jsonl, load_json, save_json, next_id, today


class TestParseKv:
    def test_basic(self):
        assert parse_kv("a=1 b=2") == {"a": "1", "b": "2"}

    def test_empty(self):
        assert parse_kv("") == {}

    def test_equals_in_value(self):
        result = parse_kv("url=http://a=b")
        assert result == {"url": "http://a=b"}

    def test_no_equals(self):
        """Eşittir işareti olmayan parçalar atlanır."""
        assert parse_kv("hello world") == {}

    def test_mixed(self):
        result = parse_kv("firma ABC oran=3.5 vade=60")
        assert result == {"oran": "3.5", "vade": "60"}


class TestJsonl:
    def test_load_save_roundtrip(self, tmp_path):
        dosya = tmp_path / "test.jsonl"
        records = [
            {"id": "1", "ad": "ABC"},
            {"id": "2", "ad": "DEF"},
            {"id": "3", "ad": "GHI"},
        ]
        save_jsonl(dosya, records)
        loaded = load_jsonl(dosya)
        assert loaded == records

    def test_save_atomic(self, tmp_path):
        """Yazma sırasında .tmp dosya kullanılır, sonuçta kalmaz."""
        dosya = tmp_path / "test.jsonl"
        save_jsonl(dosya, [{"id": "1"}])
        tmp_file = dosya.with_suffix(".tmp")
        assert not tmp_file.exists(), ".tmp dosya kalmamalı"
        assert dosya.exists()

    def test_load_missing_file(self, tmp_path):
        dosya = tmp_path / "nonexistent.jsonl"
        assert load_jsonl(dosya) == []

    def test_load_empty_file(self, tmp_path):
        dosya = tmp_path / "empty.jsonl"
        dosya.write_text("", "utf-8")
        assert load_jsonl(dosya) == []

    def test_turkish_chars(self, tmp_path):
        dosya = tmp_path / "turkish.jsonl"
        records = [{"ad": "Öğüş Dağıtım", "not": "çok güzel"}]
        save_jsonl(dosya, records)
        loaded = load_jsonl(dosya)
        assert loaded[0]["ad"] == "Öğüş Dağıtım"


class TestJson:
    def test_load_save_roundtrip(self, tmp_path):
        dosya = tmp_path / "test.json"
        data = {"firma_adi": "Test A.Ş.", "sektor": "teknoloji"}
        save_json(dosya, data)
        loaded = load_json(dosya)
        assert loaded == data

    def test_load_missing(self, tmp_path):
        dosya = tmp_path / "nonexistent.json"
        assert load_json(dosya) is None

    def test_save_atomic(self, tmp_path):
        dosya = tmp_path / "test.json"
        save_json(dosya, {"a": 1})
        tmp_file = dosya.with_suffix(".tmp")
        assert not tmp_file.exists()
        assert dosya.exists()


class TestNextId:
    def test_basic(self):
        records = [{"id": "1"}, {"id": "3"}]
        assert next_id(records) == 4

    def test_empty(self):
        assert next_id([]) == 1

    def test_string_ids(self):
        records = [{"id": "5"}, {"id": "2"}, {"id": "10"}]
        assert next_id(records) == 11


class TestToday:
    def test_format(self):
        result = today()
        # YYYY-MM-DD format
        assert len(result) == 10
        assert result[4] == "-"
        assert result[7] == "-"
