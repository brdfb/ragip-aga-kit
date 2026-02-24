# Guncelleme Mekanizmasi

Manifest: config/.ragip_manifest.json — core dosyalarin SHA-256 checksum'lari.

Uclu checksum karsilastirma:
- manifest_hash (kit hash) vs installed_hash (diskteki) vs new_hash (yeni kit)
- installed == manifest && new != manifest -> KIT GUNCELLENDI -> dosyayi guncelle
- installed != manifest && new == manifest -> KULLANICI DEGISTIRMIS -> koru
- installed != manifest && new != manifest -> CAKISMA -> yedekle + guncelle
- installed == manifest && new == manifest -> DEGISMEDI -> atla

Kritik kural: Manifest her zaman KIT hash'i saklar, installed hash degil.
Boylece kullanici ozellestirmeleri tum ardisik update'lerde korunur. (ADR: docs/adr/0003-manifest-kit-hash.md)

Pre-commit hook (.git/hooks/pre-commit): Commit oncesi pytest otomatik calisir.
