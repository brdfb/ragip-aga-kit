# Gibibyte Urun Yol Haritasi

> Son guncelleme: 2026-04-02
> Planlama donemi: Q2-Q4 2026

## Urun / Hizmet Portfoyu

```
                    GIBIBYTE PORTFOY
                         |
         +---------------+---------------+
         |               |               |
     HIZMETLER        URUNLER        DANISMANLIK
         |               |               |
    +----+----+     +----+----+     +----+----+
    |    |    |     |         |     |         |
   M365  D365 Gvnlk Tenra   RAG   AI Gov  NCE/EST
```

### Hizmetler (Satiliyor)

| Hizmet | Olgunluk | Gelir Modeli | Hedef | Repo |
|--------|----------|-------------|-------|------|
| Microsoft 365 Yonetim | Olgun | Aylik retainer + CSP lisans | KOBi 10-250 kullanici | — |
| Dynamics 365 Sales | Buyuyen | Proje + aylik destek | KOBi 20-100 kullanici | PRST |
| Siber Guvenlik (Zero Trust) | Olgun | Proje + aylik izleme | KOBi/Orta | — |
| Azure Altyapi | Olgun | Proje + tuketim | KOBi/Orta | — |
| CSP Lisanslama | Olgun | Lisans marji | Tum segmentler | — |

### Urunler (Gelistiriliyor)

| Urun | Olgunluk | Durum | Hedef | Repo |
|------|----------|-------|-------|------|
| Tenra (Tenant Tarama) | MVP | 178 test, demo ortami var(?) | MSP'ler + IT yoneticileri | mara |
| RAG Agent (Bilgi Tabani) | Beta | 20 skill, 65 dokuman | Dahili kullanim | gibibyte-agent + knowledge-source |
| Hunter (Lead Intelligence) | Production | Canli, website entegre | Dahili satis | dyn365hunterv3 |
| Ragip Aga (KOBi Finans) | v2.11 | 533 test, kit dagitimi | KOBi finans danismani | ragip-aga-kit |

### Danismanlik (Satiliyor)

| Hizmet | Olgunluk | Durum | Farklilastirici |
|--------|----------|-------|-----------------|
| AI Governance / Copilot | Yeni | Website'de tanitim var, ilk musteri bekleniyor | Turkiye'de tek MSP |
| NCE/EST Gecis | Aktif | Landing page + kampanya canli | 4 Mayis 2026 deadline |
| KVKK Uyum | Planlama | Sayfa var ama icerik zayif | Yerel bilgi avantaji |

## Olgunluk Seviyeleri

```
OLGUN ████████████ Satiliyor, musterisi var, surec oturmus
BUYUYEN ████████░░░░ Satiliyor ama surec/otomasyon gelisiyor
YENI ████░░░░░░░░ Tanitiliyor, ilk musteri bekleniyor
MVP ███░░░░░░░░░ Urun hazir, pazar testi baslamadi
BETA ██░░░░░░░░░░ Gelistirme devam ediyor, dahili kullanim
PLANLAMA █░░░░░░░░░░░ Fikir/arastirma asamasinda
```

## Q2 2026 Hedefleri (Nisan - Haziran)

### Nisan 2026

| # | Hedef | Bagimlitik | Oncelik |
|---|-------|-----------|---------|
| 1 | NCE/EST kampanya sonuclari olc | Lead Engine canli, nurture aktif | YUKSEK |
| 2 | IYS kaydi tamamla | Sirket bilgileri | YUKSEK |
| 3 | Nurture automation aktif et | IYS + liste karari | YUKSEK |
| 4 | Ilk gercek musteri testi (Ragip Aga) | Musteri adayi (Vega Gida?) | ORTA |
| 5 | UptimeRobot kur (website + Hunter) | 5 dk, ucretsiz | DUSUK |

### Mayis 2026

| # | Hedef | Bagimlitik | Oncelik |
|---|-------|-----------|---------|
| 1 | NCE/EST deadline (4 Mayis) — son push | Kampanya aktif | KRITIK |
| 2 | E7 Frontier Suite landing page | E7 1 Mayis lansami | YUKSEK |
| 3 | Tenra demo sureci netlesir | MARA durumu | ORTA |
| 4 | Google Ads pilot ($3,500/ay) baslat? | Butce karari | DEGERLENDIR |

### Haziran 2026

| # | Hedef | Bagimlitik | Oncelik |
|---|-------|-----------|---------|
| 1 | Temmuz fiyat artisi kampanyasi hazirla | Landing page + email | YUKSEK |
| 2 | Lead Engine v2 (composite scoring) | Lead hacmi > 50 | DEGERLENDIR |
| 3 | Ilk AI Governance musterisi | Pazar hazir mi? | ORTA |
| 4 | D365 satis pipeline otomasyonu | Pipeline tanimli mi? | ORTA |

## Q3-Q4 2026 Gorunum (Temmuz - Aralik)

| Ceyrek | Odak | Beklenen Sonuc |
|--------|------|---------------|
| Q3 | Temmuz fiyat artisi kampanyasi + AI Gov ilk musteri + Tenra pilot | 3-5 yeni musteri |
| Q4 | Content cluster genisletme + paid ads optimizasyon + Tenra SaaS? | Aylik lead akisi otomasyonu |

## Urun Bagimlitik Haritasi

```
WEBSITE (continuity-hub)
  ├── Lead Engine → Hunter (skor) → Brevo (nurture) → D365 (CRM)
  │                                                       |
  │                                    D365 Sales Pipeline |
  │                                    (lead → opp → quote)|
  │                                                       |
  │                               PRST ←──── Parasut (ERP)
  │                               (fatura sync)
  │
  ├── /tenra sayfasi → MARA (Tenra platformu)
  │                    Demo talep → D365 Lead (formType=demo)
  │
  ├── Blog icerigi ←── gibibyte-knowledge-source (RAG)
  │                     gibibyte-agent (icerik uretim?)
  │
  └── Ragip Aga (ayri concern — KOBi finans)
      ragip-aga-kit → ragip-workspace → D365 MCP
```

## Kritik Kararlar (Bekleniyor)

| # | Karar | Kim | Ne zaman | Etkisi |
|---|-------|-----|---------|--------|
| 1 | Google Ads baslatilacak mi? | Kullanici | Nisan 2026 | $3,500+/ay maliyet, lead hacmi artisi |
| 2 | Tenra SaaS mi yoksa hizmet araci mi? | Kullanici | Q2 2026 | Urun stratejisi, fiyatlandirma |
| 3 | RAG agent website'e entegre olacak mi? | Kullanici | Q2 2026 | Chatbot/self-service |
| 4 | D365 satis pipeline nasil yapilandirilacak? | Kullanici | Nisan 2026 | Lead → musteri gecisi |
| 5 | Ilk Ragip Aga musterisi kim? | Kullanici | Nisan 2026 | ROI olcumu, referans |
