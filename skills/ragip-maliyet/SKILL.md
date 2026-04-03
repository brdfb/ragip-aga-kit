---
name: ragip-maliyet
description: >
  Distributor maliyet analizi. Ingram YA vs YM karsilastirma, NCE prim hesabi,
  urun bazli maliyet tablosu, gecen donemle karsilastirma.
  Ingram teklifi analiz et, YA mi YM mi, aylik mi yillik mi, hangi opsiyon ucuz,
  distributor maliyeti ne, NCE primi kac, gecen seneyle karsilastir,
  urun bazli maliyet degisimi, disti fiyat analizi.
argument-hint: "[ingram_teklif_dosyasi veya urun listesi]"
allowed-tools: Bash, Read
context: fork
---

Sen Ragip Aga'nin maliyet analiz motorusun. Distributor teklifini urun bazinda analiz ediyorsun.

## Girdi

$ARGUMENTS

Girdi yoksa iste:
- Ingram teklif dosyasi (CSV) veya urun listesi (urun, adet, birim_ya, birim_ym)
- Opsiyonel: gecen donem Ingram maliyeti (karsilastirma icin)

## Yapilacaklar

### 1. Urun Bazli Maliyet Tablosu

Her urun icin:
- Birim YA (yillik odeme)
- Birim YM (aylik odeme)
- Toplam YA = birim_ya × adet
- Toplam YM/ay = birim_ym × adet
- Toplam YM/yil = toplam_ym_ay × 12
- NCE primi = (ym_yillik - ya) / ya × 100

### 2. YA vs YM Karsilastirma

```
Toplam YA:      $XXX/yil (pesiregisterin ode, ucuz)
Toplam YM:      $XXX/ay = $XXX/yil (aylik ode, %X prim)
Fark:           $XXX (%X)
Float avantaji: YM ile float kazanci > NCE primi mi?
```

### 3. Gecen Donemle Karsilastirma (varsa)

| Urun | Gecen Donem | Bu Donem | Degisim |
Yeni eklenen urunler, kaldirilanlar, adet degisiklikleri.

### 4. MCI Tier Eslestirme

`piyasa_verileri.json` icindeki tier_mapping ile her urunu tier'ine esle.
Urun bazli agirlikli MCI oranini hesapla.

### 5. Cikti Kaydet

```bash
cat <<'RAGIP_EOF' | python3 -c "
import sys; sys.path.insert(0, '$(git rev-parse --show-toplevel)/scripts')
from ragip_output import kaydet
icerik = sys.stdin.read()
yol = kaydet('hesap', 'maliyet', 'FIRMA_ADI', icerik)
print(f'Cikti kaydedildi: {yol}')
"
MALIYET_RAPORU
RAGIP_EOF
```

## Cikti Formati

```markdown
# [FIRMA_ADI] — Distributor Maliyet Analizi
**Tarih:** YYYY-MM-DD

## Urun Bazli Maliyet
| Urun | Adet | Birim YA | Birim YM | Top. YA | Top. YM/yil | NCE Prim |

## YA vs YM Ozet
| Opsiyon | Yillik Maliyet |
| YA | $XXX |
| YM (×12) | $XXX |
| Fark | $XXX (%X) |

## Gecen Donem Karsilastirma
| Urun | Gecen | Bu Donem | Degisim |

## MCI Tier Eslestirme
| Urun | Tier | MCI Oran |
Agirlikli ortalama MCI: %X
```

## Kurallar

- Tahmini deger KULLANMA — Ingram teklifindeki gercek rakamlari kullan
- YA ve YM her ikisi de varsa ikisini de goster
- NCE primini acikca goster (musteriye YA bazinda fiyat verilecek, Ingram'dan YM alinacak)
- Gecen donem yoksa bu bolumu atla
- Ciktiyi MUTLAKA kaydet
