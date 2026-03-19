# Commit ve Release Kurallari

## Commit Kontrol Listesi (ZORUNLU)

Kod veya prompt degisikligi yapan HER commit'te asagidaki kontrolleri yap:

1. VERSION bump gerekiyor mu? (fix/prompt → patch, feat → minor)
2. config/ragip_aga.yaml version eslesme
3. RAGIP_AGA_CHANGELOG.md yeni giris
4. README.md: test sayisi, tablo sayilari guncel mi
5. CLAUDE.md: test dosya listesi guncel mi
6. install.sh: agent/skill sayilari guncel mi
7. docs/FEATURE_IDEAS.md: eski sayilar var mi

Bu kontrolleri AYRI commit olarak DEGIL, ayni commit icinde yap.
Sadece docs-only degisikliklerde (ADR, FEATURE_IDEAS) versiyon bump gerekmez.

## Release Checklist

- Yukaridaki commit kontrolleri tamam mi
- Testleri calistir
- Tag olustur, push, `gh release create`
