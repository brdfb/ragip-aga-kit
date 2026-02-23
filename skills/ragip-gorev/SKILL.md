---
name: ragip-gorev
description: Ragip Aga'nin urettigi aksiyon maddelerini listele, tamamla veya yeni ekle. Her analizin ardindan "bu hafta yapilacaklar"i takip et.
argument-hint: "[listele | tamamla <id> | ekle <aciklama> [konu=X oncelik=yuksek|orta|dusuk son_tarih=YYYY-MM-DD] | temizle]"
allowed-tools: Read, Write, Bash
disable-model-invocation: true
---

Sen Ragip Aga'sin. Gorev takip sistemi olarak calis. Tum gorevler `data/RAGIP_AGA/gorevler.jsonl` dosyasinda tutulur (repo koku altinda).

## Komut
$ARGUMENTS

Komut verilmemisse: `listele` yap.

## Gorev Dosyasi
```
data/RAGIP_AGA/gorevler.jsonl   (repo koku altinda)
```

Her satir bir gorev:
```json
{"id": "1", "tarih": "2026-02-18", "konu": "ABC Dagitim - vade farki", "gorev": "Sozlesmeyi avukata gonder", "oncelik": "yuksek", "durum": "bekliyor", "son_tarih": "2026-02-25"}
```

## Komutlara Gore Davran

### `listele`
Bash ile dosyayi oku ve tablo goster:
```bash
ROOT=$(git rev-parse --show-toplevel)
python3 -c "
import sys, os
sys.path.insert(0, os.path.join('$ROOT', 'scripts'))
from ragip_crud import data_path, load_jsonl

dosya = data_path('gorevler.jsonl')
gorevler = load_jsonl(dosya)
if not gorevler:
    print('Henuz gorev yok. Eklemek icin: /ragip-gorev ekle <aciklama>')
    exit()

bekleyenler = [g for g in gorevler if g.get('durum') != 'tamamlandi']
tamamlananlar = [g for g in gorevler if g.get('durum') == 'tamamlandi']

oncelik_icon = {'yuksek': '!', 'orta': '~', 'dusuk': '+'}

print(f'=== AKTIF GOREVLER ({len(bekleyenler)}) ===')
for g in sorted(bekleyenler, key=lambda x: x.get('son_tarih','')):
    icon = oncelik_icon.get(g.get('oncelik','orta'), '?')
    print(f\"{icon} [{g['id']}] {g.get('konu', '-')}\")
    print(f\"    -> {g['gorev']}\")
    if g.get('son_tarih'):
        print(f\"    Son tarih: {g['son_tarih']}\")
    print()

if tamamlananlar:
    print(f'=== TAMAMLANAN ({len(tamamlananlar)}) ===')
    for g in tamamlananlar[-3:]:
        print(f\"  [{g['id']}] {g['gorev']}\")
"
```

### `tamamla <id>`
Bash ile durumu guncelle:
```bash
ROOT=$(git rev-parse --show-toplevel)
python3 -c "
import sys, os
sys.path.insert(0, os.path.join('$ROOT', 'scripts'))
from ragip_crud import data_path, load_jsonl, save_jsonl, today

dosya = data_path('gorevler.jsonl')
gorevler = load_jsonl(dosya)
if not gorevler:
    print('Henuz gorev yok.')
    exit()

gorev_id = 'ID_BURAYA'
bulundu = False
for g in gorevler:
    if g['id'] == gorev_id:
        g['durum'] = 'tamamlandi'
        g['tamamlanma_tarihi'] = today()
        print(f'Tamamlandi: {g[\"gorev\"]}')
        bulundu = True

if not bulundu:
    print(f'Gorev bulunamadi: ID {gorev_id}')
    exit()

save_jsonl(dosya, gorevler)
"
```

### `ekle <aciklama> [konu=X oncelik=yuksek|orta|dusuk son_tarih=YYYY-MM-DD]`
Yeni gorev ekle. Opsiyonel alanlar `alan=deger` formatiyla verilebilir:
```bash
ROOT=$(git rev-parse --show-toplevel)
python3 -c "
import sys, os
sys.path.insert(0, os.path.join('$ROOT', 'scripts'))
from ragip_crud import data_path, load_jsonl, save_jsonl, parse_kv, next_id, today
from datetime import timedelta, date

dosya = data_path('gorevler.jsonl')
gorevler = load_jsonl(dosya)

yeni_id = str(next_id(gorevler))

# Argumanlari parse et
args = 'ARGUMANLAR_BURAYA'
parcalar = args.split()

aciklama_parcalari = []
opsiyonlar = {}
for p in parcalar:
    if '=' in p:
        k, v = p.split('=', 1)
        opsiyonlar[k.strip()] = v.strip()
    else:
        aciklama_parcalari.append(p)

aciklama = ' '.join(aciklama_parcalari) if aciklama_parcalari else 'Tanimsiz gorev'

yeni = {
    'id': yeni_id,
    'tarih': today(),
    'konu': opsiyonlar.get('konu', 'Genel'),
    'gorev': aciklama,
    'oncelik': opsiyonlar.get('oncelik', 'orta'),
    'durum': 'bekliyor',
    'son_tarih': opsiyonlar.get('son_tarih', str(date.today() + timedelta(days=7)))
}

# Oncelik validasyonu
if yeni['oncelik'] not in ('yuksek', 'orta', 'dusuk'):
    print(f'UYARI: Gecersiz oncelik \"{yeni[\"oncelik\"]}\", \"orta\" olarak ayarlandi.')
    yeni['oncelik'] = 'orta'

gorevler.append(yeni)
save_jsonl(dosya, gorevler)
print(f'Gorev eklendi: [{yeni_id}] {yeni[\"gorev\"]}')
print(f'  Konu: {yeni[\"konu\"]} | Oncelik: {yeni[\"oncelik\"]} | Son tarih: {yeni[\"son_tarih\"]}')
"
```

### `temizle`
Tamamlananlari arsivle:
```bash
ROOT=$(git rev-parse --show-toplevel)
python3 -c "
import sys, os
sys.path.insert(0, os.path.join('$ROOT', 'scripts'))
from ragip_crud import data_path, load_jsonl, save_jsonl
from datetime import datetime
from pathlib import Path

dosya = data_path('gorevler.jsonl')
gorevler = load_jsonl(dosya)
if not gorevler:
    print('Henuz gorev yok.')
    exit()

# Arsiv dosyasi timestamp ile
ts = datetime.now().strftime('%Y%m%d_%H%M%S')
arsiv = data_path(f'gorevler_arsiv_{ts}.jsonl')

aktif = [g for g in gorevler if g.get('durum') != 'tamamlandi']
tamamlanan = [g for g in gorevler if g.get('durum') == 'tamamlandi']

if not tamamlanan:
    print('Tamamlanan gorev yok, temizlenecek bir sey bulunamadi.')
    exit()

# Aktif gorevleri yaz
save_jsonl(dosya, aktif) if aktif else dosya.write_text('', 'utf-8')

# Arsiv dosyasina yaz
save_jsonl(arsiv, tamamlanan)

print(f'{len(tamamlanan)} gorev arsivlendi -> {arsiv.name}')
print(f'{len(aktif)} aktif gorev kaldi.')
"
```

## Not
Her Ragip Aga analizinin sonunda otomatik gorev uretilmez — kullanici `ekle` komutuyla veya `/ragip-gorev ekle [aciklama]` ile manuel ekler.
