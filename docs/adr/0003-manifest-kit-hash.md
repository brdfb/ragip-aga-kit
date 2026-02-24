# ADR-0003: Manifest Kit Hash Saklama
Tarih: 2025-02-20
Durum: Kabul edildi

## Baglam
v2.5.0'da manifest'e installed hash (diskteki dosyanin hash'i) yaziliyordu. Bu, kullanici dosyayi ozellestirdiginde manifest hash'inin degismesine yol aciyordu. Ikinci update'de sistem "manifest == installed" goruyordu (cunku ikisi de kullanici hash'i) ve dosyayi sessizce kit versiyonuyla ustune yaziyordu.

Bug akisi:
1. install: manifest = kit_hash, disk = kit_hash (OK)
2. Kullanici duzenler: manifest = kit_hash, disk = user_hash (OK, korunur)
3. update v1: manifest'e user_hash yazilir, disk = kit_hash (BUG: ozellestirme kayboldu)
4. update v2: manifest = kit_hash == disk, "degismedi" der, kullanici degisikligi geri gelmez

## Karar
Manifest her zaman **kit hash'i** saklar, installed hash degil. Update sirasinda manifest yazma dongusu kit_files[rel_path]["new_hash"] kullanir.

3 ayri manifest yazma dongusu tek donguye indirildi.

## Sonuc
- Kullanici ozellestirmeleri tum ardisik update'lerde korunur
- Testler: test_update_preserves_customization_on_consecutive_updates, test_manifest_stores_kit_hash, test_conflict_backup_content
- Trade-off: Manifest hash ile diskteki hash farkli olabilir (beklenen durum)
