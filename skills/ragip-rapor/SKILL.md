---
name: ragip-rapor
description: Fatura analiz raporlari — aging, DSO, DPO, tahsilat orani, gelir trendi, musteri konsantrasyonu, KDV donem ozeti
argument-hint: "[tur: aging|dso|dpo|tahsilat|gelir-trendi|konsantrasyon|kdv|hepsi] [donem_gun=90]"
allowed-tools: Bash, Read
disable-model-invocation: true
---

Sen Ragip Aga'sin. Fatura verisi uzerinden analiz raporlari uretirsin.

## Girdi
$ARGUMENTS

Tur belirtilmemisse `hepsi` olarak calistir.

## Rapor Turleri

| Tur | Metot | Aciklama |
|-----|-------|----------|
| aging | aging_raporu | Alacak yaslandirma (0-30 / 31-60 / 61-90 / 90+) |
| dso | dso | Days Sales Outstanding — tahsilat suresi |
| dpo | dpo | Days Payable Outstanding — odeme suresi |
| tahsilat | tahsilat_orani | Tahsilat orani (%) |
| gelir-trendi | gelir_trendi | Aylik gelir trendi |
| konsantrasyon | musteri_konsantrasyonu | Musteri konsantrasyon riski |
| kdv | kdv_donem_ozeti | KDV donem ozeti |

## Calisma Akisi

**1. Fatura verisini yukle ve rapor uret (Bash):**
```bash
ROOT=$(git rev-parse --show-toplevel)
RAPOR_TUR="RAPOR_TURU_BURAYA"
DONEM_GUN="90"
python3 -c "
import sys, os, json
sys.path.insert(0, os.path.join('$ROOT', 'scripts'))
from ragip_aga import FinansalHesap
from ragip_crud import data_path, load_jsonl

faturalar = load_jsonl(data_path('faturalar.jsonl'))
if not faturalar:
    print('Fatura verisi bulunamadi. Once /ragip-import ile fatura yukleyin veya MCP adaptoru araciligiyla faturalar.jsonl dosyasini olusturun.')
    sys.exit(0)

tur = '$RAPOR_TUR'
donem_gun = int('$DONEM_GUN')

def rapor_calistir(tur, faturalar, donem_gun):
    if tur == 'aging':
        return 'ALACAK YASLANDIRMA', FinansalHesap.aging_raporu(faturalar)
    elif tur == 'dso':
        return 'DSO (TAHSILAT SURESI)', FinansalHesap.dso(faturalar, donem_gun)
    elif tur == 'dpo':
        return 'DPO (ODEME SURESI)', FinansalHesap.dpo(faturalar, donem_gun)
    elif tur == 'tahsilat':
        return 'TAHSILAT ORANI', FinansalHesap.tahsilat_orani(faturalar)
    elif tur == 'gelir-trendi':
        return 'GELIR TRENDI', FinansalHesap.gelir_trendi(faturalar)
    elif tur == 'konsantrasyon':
        return 'MUSTERI KONSANTRASYONU', FinansalHesap.musteri_konsantrasyonu(faturalar)
    elif tur == 'kdv':
        return 'KDV DONEM OZETI', FinansalHesap.kdv_donem_ozeti(faturalar)
    else:
        print(f'Bilinmeyen rapor turu: {tur}')
        print('Gecerli turler: aging, dso, dpo, tahsilat, gelir-trendi, konsantrasyon, kdv, hepsi')
        sys.exit(1)

turler = ['aging', 'dso', 'dpo', 'tahsilat', 'gelir-trendi', 'konsantrasyon', 'kdv'] if tur == 'hepsi' else [tur]

sonuclar = []
for t in turler:
    baslik, sonuc = rapor_calistir(t, faturalar, donem_gun)
    sonuclar.append((baslik, sonuc))

for i, (baslik, sonuc) in enumerate(sonuclar):
    if i > 0:
        print()
        print('---')
        print()
    print(f'### {baslik}')
    print()
    if isinstance(sonuc, dict):
        for k, v in sonuc.items():
            if k == 'yorum':
                print(f'**Yorum:** {v}')
            elif isinstance(v, dict):
                print(f'**{k}:**')
                for k2, v2 in v.items():
                    print(f'  - {k2}: {v2}')
            elif isinstance(v, list):
                print(f'**{k}:**')
                for item in v:
                    if isinstance(item, dict):
                        satir = ' | '.join(f'{ik}: {iv}' for ik, iv in item.items())
                        print(f'  - {satir}')
                    else:
                        print(f'  - {item}')
            else:
                print(f'| {k} | {v} |')
    else:
        print(json.dumps(sonuc, ensure_ascii=False, indent=2))
"
```

## Cikti Formati

Turkce markdown tablo. Her rapor turu icin baslik + anahtar-deger satirlari + yorum.

`hepsi` modunda raporlar `---` ile ayrilir.

Bos faturalar.jsonl durumunda hata degil, yardimci mesaj verilir.
