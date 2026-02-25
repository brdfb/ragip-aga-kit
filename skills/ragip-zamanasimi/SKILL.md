---
name: ragip-zamanasimi
description: Zamanasimi ve hukuki sure hesapla. Fatura itirazi (TTK m.21/2), sozlesme zamanasimi (TBK m.146-147), arabuluculuk suresi, icra takip suresi, KVKK basvuru suresi gibi yasal sureler icin kalan gun sayisini hesapla ve uyar.
argument-hint: "[tur: fatura-itirazi|sozlesme-genel|sozlesme-kisa|vade-farki|icra-takip|arabuluculuk|kvkk-basvuru|kvkk-sikayet] [baslangic_tarihi=YYYY-MM-DD]"
allowed-tools: Bash
disable-model-invocation: true
---

Sen Ragip Aga'nin hukuk kolusun. Yasal sure ve zamanasimi hesaplama araci olarak calis.

## Girdi
$ARGUMENTS

Tur verilmemisse tum turleri listele. Baslangic tarihi verilmemisse sor.

## Yapilacaklar

**1. Sure turunu ve baslangic tarihini al**

Gecerli turler ve yasal dayanagi:

| Tur | Sure | Kanun | Aciklama |
|-----|------|-------|----------|
| fatura-itirazi | 8 is gunu | TTK m.21/2 | Faturaya itiraz suresi |
| sozlesme-genel | 10 yil | TBK m.146 | Genel zamanasimi |
| sozlesme-kisa | 5 yil | TBK m.147 | Kisa zamanasimi (kira, hizmet, eser, vekalet) |
| vade-farki | 5 yil | TBK m.147/5 | Vade farki (faiz) zamanasimi |
| icra-takip | 1 yil | IIK m.58 | Icra takip zamanasimi |
| arabuluculuk | 6 hafta | 6325 s.K. m.18/A | Ticari arabuluculuk suresi (uzatma ile 8 hafta) |
| kvkk-basvuru | 30 gun | KVKK m.13 | Veri sorumlusuna basvuru suresi |
| kvkk-sikayet | 30 gun | KVKK m.14 | Kurula sikayet suresi (basvurudan sonra) |

**2. Hesaplama (Bash)**

```bash
python3 -c "
from datetime import datetime, timedelta
import sys

TUR = 'TUR_BURAYA'
BASLANGIC = 'TARIH_BURAYA'

SURELER = {
    'fatura-itirazi': {'gun': 8, 'is_gunu': True, 'kanun': 'TTK m.21/2', 'aciklama': 'Faturaya itiraz suresi'},
    'sozlesme-genel': {'yil': 10, 'is_gunu': False, 'kanun': 'TBK m.146', 'aciklama': 'Genel zamanasimi'},
    'sozlesme-kisa': {'yil': 5, 'is_gunu': False, 'kanun': 'TBK m.147', 'aciklama': 'Kisa zamanasimi (kira, hizmet, eser)'},
    'vade-farki': {'yil': 5, 'is_gunu': False, 'kanun': 'TBK m.147/5', 'aciklama': 'Vade farki (faiz) zamanasimi'},
    'icra-takip': {'yil': 1, 'is_gunu': False, 'kanun': 'IIK m.58', 'aciklama': 'Icra takip zamanasimi'},
    'arabuluculuk': {'hafta': 6, 'is_gunu': False, 'kanun': '6325 s.K. m.18/A', 'aciklama': 'Ticari arabuluculuk suresi'},
    'kvkk-basvuru': {'gun': 30, 'is_gunu': False, 'kanun': 'KVKK m.13', 'aciklama': 'Veri sorumlusuna basvuru suresi'},
    'kvkk-sikayet': {'gun': 30, 'is_gunu': False, 'kanun': 'KVKK m.14', 'aciklama': 'Kurula sikayet suresi'},
}

if TUR not in SURELER:
    print(f'! Gecersiz tur: {TUR}')
    print(f'Gecerli turler: {\", \".join(SURELER.keys())}')
    sys.exit(1)

try:
    baslangic = datetime.strptime(BASLANGIC, '%Y-%m-%d')
except ValueError:
    print(f'! Gecersiz tarih: {BASLANGIC} (format: YYYY-MM-DD)')
    sys.exit(1)

sure = SURELER[TUR]
bugun = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

# Son gun hesapla
if 'yil' in sure:
    bitis = baslangic.replace(year=baslangic.year + sure['yil'])
elif 'hafta' in sure:
    bitis = baslangic + timedelta(weeks=sure['hafta'])
elif sure.get('is_gunu'):
    # Is gunu hesabi (cumartesi/pazar haric)
    gun_sayaci = 0
    tarih = baslangic
    while gun_sayaci < sure['gun']:
        tarih += timedelta(days=1)
        if tarih.weekday() < 5:  # Pazartesi-Cuma
            gun_sayaci += 1
    bitis = tarih
else:
    bitis = baslangic + timedelta(days=sure['gun'])

kalan = (bitis - bugun).days

print(f'=== ZAMANASIMI / SURE HESABI ===')
print(f'Tur          : {TUR}')
print(f'Kanun        : {sure[\"kanun\"]}')
print(f'Aciklama     : {sure[\"aciklama\"]}')
print(f'Baslangic    : {baslangic.strftime(\"%Y-%m-%d\")}')
print(f'Son gun      : {bitis.strftime(\"%Y-%m-%d\")}')
print(f'Kalan gun    : {kalan}')
print()

if kalan < 0:
    print(f'!! SURESI DOLMUS ({abs(kalan)} gun once)')
    print(f'   Hukuki hak kaybi riski var. Derhal avukata danisin.')
elif kalan <= 7:
    print(f'!! KRITIK — {kalan} gun kaldi!')
    print(f'   Acil islem gerekli. Avukata danisin.')
elif kalan <= 30:
    print(f'! UYARI — {kalan} gun kaldi.')
    print(f'  Hazirliklara baslayin.')
else:
    print(f'+ Yeterli sure var ({kalan} gun).')

print()
print(f'NOT: Resmi tatiller hesaba dahil degildir. Is gunu hesabinda sadece hafta sonu cikarildi.')
print(f'UYARI: Bu hesaplama hukuki gorus degildir. Kesin islem oncesi bir avukata danisin.')
"
```

**3. Tum sureleri listele (tur belirtilmemisse)**

```bash
python3 -c "
SURELER = {
    'fatura-itirazi': ('8 is gunu', 'TTK m.21/2', 'Faturaya itiraz suresi'),
    'sozlesme-genel': ('10 yil', 'TBK m.146', 'Genel zamanasimi'),
    'sozlesme-kisa': ('5 yil', 'TBK m.147', 'Kisa zamanasimi (kira, hizmet, eser)'),
    'vade-farki': ('5 yil', 'TBK m.147/5', 'Vade farki (faiz) zamanasimi'),
    'icra-takip': ('1 yil', 'IIK m.58', 'Icra takip zamanasimi'),
    'arabuluculuk': ('6 hafta', '6325 s.K. m.18/A', 'Ticari arabuluculuk suresi'),
    'kvkk-basvuru': ('30 gun', 'KVKK m.13', 'Veri sorumlusuna basvuru suresi'),
    'kvkk-sikayet': ('30 gun', 'KVKK m.14', 'Kurula sikayet suresi'),
}
print('=== YASAL SURELER TABLOSU ===')
print()
for tur, (sure, kanun, aciklama) in SURELER.items():
    print(f'  {tur:<20} {sure:<12} {kanun:<20} {aciklama}')
print()
print('Kullanim: /ragip-zamanasimi [tur] baslangic_tarihi=YYYY-MM-DD')
print('Ornek:    /ragip-zamanasimi fatura-itirazi baslangic_tarihi=2026-02-15')
"
```
