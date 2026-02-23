---
name: ragip-firma
description: Firma karti veritabani. Distributor, tedarikci ve musteri bilgilerini kaydet, ara, guncelle. Vade, oran, risk notu ve iletisim bilgilerini takip et.
argument-hint: "[listele | ekle <firma_adi> | guncelle <id> <alan=deger> | sil <id> | ara <terim>]"
allowed-tools: Read, Write, Bash
disable-model-invocation: true
---

Sen Ragip Aga'sin. Firma karti veritabani olarak calis. Tum firmalar `data/RAGIP_AGA/firmalar.jsonl` dosyasinda tutulur (repo koku altinda).

## Komut
$ARGUMENTS

Komut verilmemisse: `listele` yap.

## Firma Dosyasi
```
data/RAGIP_AGA/firmalar.jsonl   (repo koku altinda)
```

Her satir bir firma kaydi:
```json
{"id": "1", "ad": "ABC Dagitim A.S.", "vergi_no": "1234567890", "iletisim": {"tel": "0212...", "email": "info@abc.com"}, "vade_gun": 60, "vade_farki_oran": 3.0, "risk_notu": "orta", "notlar": "Genelde zamaninda oder", "son_islem": "2026-02-18", "olusturma": "2026-02-18"}
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

dosya = data_path('firmalar.jsonl')
firmalar = load_jsonl(dosya)
if not firmalar:
    print('Henuz firma karti yok. Eklemek icin: /ragip-firma ekle <firma_adi>')
    exit()

risk_icon = {'yuksek': '!', 'orta': '~', 'dusuk': '+'}

print(f'=== FIRMA KARTLARI ({len(firmalar)}) ===')
print()
for f in sorted(firmalar, key=lambda x: x.get('ad', '')):
    icon = risk_icon.get(f.get('risk_notu', 'orta'), '?')
    print(f\"{icon} [{f['id']}] {f['ad']}\")
    if f.get('vergi_no'):
        print(f\"    VKN: {f['vergi_no']}\")
    print(f\"    Vade: {f.get('vade_gun', '-')} gun | Oran: %{f.get('vade_farki_oran', '-')}/ay | Risk: {f.get('risk_notu', '-')}\")
    if f.get('notlar'):
        print(f\"    Not: {f['notlar']}\")
    print()
"
```

### `ekle <firma_adi> [alan=deger ...]`
Yeni firma karti olustur. Argumanlardaki `alan=deger` ciftlerini parse et:
```bash
ROOT=$(git rev-parse --show-toplevel)
python3 -c "
import sys, os
sys.path.insert(0, os.path.join('$ROOT', 'scripts'))
from ragip_crud import data_path, load_jsonl, save_jsonl, parse_kv, next_id, today

dosya = data_path('firmalar.jsonl')
firmalar = load_jsonl(dosya)

yeni_id = str(next_id(firmalar))

# Argumanlari parse et - ilk arguman firma adi, geri kalani alan=deger
args = 'ARGUMANLAR_BURAYA'
parcalar = args.split()

ad_parcalari = []
diger = []
for p in parcalar:
    if '=' in p:
        diger.append(p)
    else:
        ad_parcalari.append(p)

firma_adi = ' '.join(ad_parcalari) if ad_parcalari else 'Isimsiz Firma'

yeni = {
    'id': yeni_id,
    'ad': firma_adi,
    'vergi_no': '',
    'iletisim': {'tel': '', 'email': ''},
    'vade_gun': 30,
    'vade_farki_oran': 0.0,
    'risk_notu': 'orta',
    'notlar': '',
    'son_islem': today(),
    'olusturma': today(),
}

kvs = parse_kv(' '.join(diger))
for k, v in kvs.items():
    if k == 'tel':
        yeni['iletisim']['tel'] = v
    elif k == 'email':
        yeni['iletisim']['email'] = v
    elif k in ('vade_gun', 'vade'):
        yeni['vade_gun'] = int(v)
    elif k in ('oran', 'vade_farki_oran'):
        yeni['vade_farki_oran'] = float(v)
    elif k in ('risk', 'risk_notu'):
        yeni['risk_notu'] = v
    elif k in ('not', 'notlar'):
        yeni['notlar'] = v
    elif k == 'vergi_no':
        yeni['vergi_no'] = v
    else:
        yeni[k] = v

# Duplicate kontrolu (vergi_no)
if yeni['vergi_no']:
    for f in firmalar:
        if f.get('vergi_no') == yeni['vergi_no']:
            print(f\"! Bu vergi numarasi zaten kayitli: [{f['id']}] {f['ad']}\")
            print(f'Guncellemek icin: /ragip-firma guncelle {f[\"id\"]} alan=deger')
            exit()

firmalar.append(yeni)
save_jsonl(dosya, firmalar)
print(f'+ Firma eklendi: [{yeni_id}] {yeni[\"ad\"]}')
if yeni['vergi_no']:
    print(f'   VKN: {yeni[\"vergi_no\"]}')
print(f'   Vade: {yeni[\"vade_gun\"]} gun | Oran: %{yeni[\"vade_farki_oran\"]}/ay')
"
```

### `guncelle <id> <alan=deger ...>`
Mevcut firma kartini guncelle:
```bash
ROOT=$(git rev-parse --show-toplevel)
python3 -c "
import sys, os
sys.path.insert(0, os.path.join('$ROOT', 'scripts'))
from ragip_crud import data_path, load_jsonl, save_jsonl, parse_kv, today

dosya = data_path('firmalar.jsonl')
firmalar = load_jsonl(dosya)
if not firmalar:
    print('Henuz firma karti yok.')
    exit()

firma_id = 'ID_BURAYA'
guncellemeler = 'GUNCELLEMELER_BURAYA'

bulundu = False
for f in firmalar:
    if f['id'] == firma_id:
        bulundu = True
        kvs = parse_kv(guncellemeler)
        for k, v in kvs.items():
            if k == 'tel':
                f.setdefault('iletisim', {})['tel'] = v
            elif k == 'email':
                f.setdefault('iletisim', {})['email'] = v
            elif k in ('vade_gun', 'vade'):
                f['vade_gun'] = int(v)
            elif k in ('oran', 'vade_farki_oran'):
                f['vade_farki_oran'] = float(v)
            elif k in ('risk', 'risk_notu'):
                f['risk_notu'] = v
            elif k in ('not', 'notlar'):
                f['notlar'] = v
            else:
                f[k] = v
        f['son_islem'] = today()
        print(f'+ Guncellendi: [{f[\"id\"]}] {f[\"ad\"]}')
        break

if not bulundu:
    print(f'X Firma bulunamadi: ID {firma_id}')
    exit()

save_jsonl(dosya, firmalar)
"
```

### `sil <id>`
Firma kartini sil:
```bash
ROOT=$(git rev-parse --show-toplevel)
python3 -c "
import sys, os
sys.path.insert(0, os.path.join('$ROOT', 'scripts'))
from ragip_crud import data_path, load_jsonl, save_jsonl

dosya = data_path('firmalar.jsonl')
firmalar = load_jsonl(dosya)
if not firmalar:
    print('Henuz firma karti yok.')
    exit()

firma_id = 'ID_BURAYA'
yeni = [f for f in firmalar if f['id'] != firma_id]

if len(yeni) == len(firmalar):
    print(f'X Firma bulunamadi: ID {firma_id}')
    exit()

silinen = [f for f in firmalar if f['id'] == firma_id][0]
save_jsonl(dosya, yeni)
print(f'Silindi: [{silinen[\"id\"]}] {silinen[\"ad\"]}')
"
```

### `ara <terim>`
Firma adi, vergi no veya notlarda ara:
```bash
ROOT=$(git rev-parse --show-toplevel)
python3 -c "
import sys, os
sys.path.insert(0, os.path.join('$ROOT', 'scripts'))
from ragip_crud import data_path, load_jsonl

dosya = data_path('firmalar.jsonl')
firmalar = load_jsonl(dosya)
if not firmalar:
    print('Henuz firma karti yok.')
    exit()

terim = 'TERIM_BURAYA'.lower()

sonuclar = []
for f in firmalar:
    aranacak = f'{f.get(\"ad\",\"\")} {f.get(\"vergi_no\",\"\")} {f.get(\"notlar\",\"\")}'.lower()
    if terim in aranacak:
        sonuclar.append(f)

if not sonuclar:
    print(f'Sonuc bulunamadi: \"{terim}\"')
    exit()

risk_icon = {'yuksek': '!', 'orta': '~', 'dusuk': '+'}
print(f'=== ARAMA SONUCLARI: \"{terim}\" ({len(sonuclar)} firma) ===')
print()
for f in sonuclar:
    icon = risk_icon.get(f.get('risk_notu', 'orta'), '?')
    print(f\"{icon} [{f['id']}] {f['ad']}\")
    if f.get('vergi_no'):
        print(f\"    VKN: {f['vergi_no']}\")
    print(f\"    Vade: {f.get('vade_gun', '-')} gun | Oran: %{f.get('vade_farki_oran', '-')}/ay | Risk: {f.get('risk_notu', '-')}\")
    if f.get('notlar'):
        print(f\"    Not: {f['notlar']}\")
    print()
"
```

## Not
Firma kartlari `/ragip-analiz`, `/ragip-strateji` ve `/ragip-dis-veri` ile birlikte kullanilabilir. Analiz sonrasi firma bilgilerini guncellemek icin `guncelle` komutunu kullan.
