# ADR-0002: Version-Manifest-Update Sistemi
Tarih: 2025-02-01
Durum: Kabul edildi

## Baglam
Kit baska repo'lara kuruldugundan, kullanicinin hangi versiyonu kurulmus oldugunu ve dosyalarda ne degistirdigini bilmek gerekiyor. Update isleminde kullanici ozelestirmelerini korumak kritik.

## Karar
Uc katmanli sistem:
1. **VERSION dosyasi**: Tek kaynak versiyon (semver, tek satir). config/ragip_aga.yaml ve changelog ile uyum testi var.
2. **JSON manifest** (config/.ragip_manifest.json): Core dosyalarin SHA-256 checksum'lari. install.sh olusturur.
3. **Uclu checksum karsilastirma**: update.sh manifest_hash vs installed_hash vs new_hash karsilastirir.

Sonuclar:
- Kit guncellendi -> dosya guncellenir
- Kullanici degistirmis -> korunur
- Cakisma -> yedek olusturulur (.kullanici-yedek-YYYYMMDD)
- Degismedi -> atlanir

## Sonuc
- Kullanici ozellestirmeleri guvenle korunur
- Hangi dosyalarin degistigi acikca gorunur (--dry-run)
- Manifest-tabanli: update.sh sadece manifestteki dosyalara dokunur
- Trade-off: Her yeni core dosya manifeste eklenmeli (unutulursa update kapsamina girmez)
