# Gibibyte Dijital Mimari

> Son guncelleme: 2026-04-02
> Durum: Lead Engine v1 CANLI, nurture activation bekliyor

## Buyuk Resim

```
                    ZIYARETCI
                       |
            +----------+----------+
            |          |          |
         Website    WhatsApp    Telefon
         (Vercel)  (Business)  (Sabit hat)
            |          |          |
            v          v          v
    +-------+----------+----------+--------+
    |          gibibyte.com.tr               |
    |  React SPA + Vercel Serverless        |
    |                                        |
    |  14 blog + pillar page + landing page  |
    |  4 lead capture form + iletisim form  |
    |  WhatsApp context-aware (10 sayfa)    |
    +------------------+--------------------+
                       |
                       | POST /api/lead-capture
                       v
    +------------------+--------------------+
    |          VERCEL API GATEWAY            |
    |                                        |
    |  1. Disposable email check (client)   |
    |  2. Honeypot bot korumasi             |
    |  3. Hidden fields (UTM, referrer)     |
    +----+----------+----------+------------+
         |          |          |
         v          v          v
    +----+---+ +----+---+ +---+------------+
    | HUNTER | | BREVO  | | POWER AUTOMATE |
    +----+---+ +----+---+ +---+------------+
         |          |          |
         v          v          v
    +----+---+ +----+---+ +---+------------+
    | Domain | | DOI    | | D365 SALES     |
    | Skor   | | Email  | | Lead + Campaign|
    | P-Model| | Nurture| | Pipeline       |
    +--------+ +--------+ +----------------+
```

## Detayli Akis Diagrami

### Lead Capture Pipeline

```
ZIYARETCI → gibibyte.com.tr/nce-est (veya diger form sayfasi)
    |
    | [Form dolduruyor: ad, email, sirket, telefon]
    |
    v
REACT FORM (client-side)
    |
    +-- Disposable email check (npm: disposable-email-domains)
    |   X tempmail.com, guerrillamail.com vs → REJECT
    |
    +-- Honeypot check (gizli "website" alani)
    |   X Bot doldurursa → sessiz 200, hicbir sey yapma
    |
    +-- Hidden fields topla:
    |   - UTM params (url'den)
    |   - Landing page path
    |   - Referrer
    |   - Visit count (localStorage)
    |
    | POST /api/lead-capture
    v
VERCEL SERVERLESS FUNCTION
    |
    +-- Corporate email mi? (gmail/yahoo/hotmail degilse)
    |   |
    |   +-- EVET → Hunter API cagir
    |   |         POST hunter.gibibyte.com.tr/api/v1/ingest/webhook
    |   |         Header: X-API-Key
    |   |         Body: {domain, company_name, contact_emails}
    |   |         Response: {score, segment, provider, scanned}
    |   |
    |   +-- HAYIR → score=0, segment=unknown (Hunter atla)
    |
    +-- Brevo API cagir
    |   POST api.brevo.com/v3/contacts
    |   Body: {email, attributes (10 field), listIds: [4]}
    |   → DOI Bekleyenler listesine (ID: 4) ekle
    |
    +-- Hot lead mi? (hunter_score >= 70 || formType == "demo")
    |   |
    |   +-- EVET → Power Automate webhook
    |   |         → D365 Lead olustur (12 field)
    |   |
    |   +-- HAYIR → sadece Brevo'da kalir
    |
    v
RESPONSE → {success, isCorpEmail, hunterScore, hunterSegment}
```

### Double Opt-in Akisi

```
Brevo Liste 4 (DOI Bekleyenler) → kisi eklendi
    |
    v
BREVO AUTOMATION #1 (DOI)
    |
    +-- Send email: "Email Adresimi Onayliyorum"
    |   (Outlook-safe VML button, {{ double_optin }} link)
    |
    +-- Kisi tikladi mi? (1 gun bekle)
        |
        +-- EVET → Liste 3'e tasi (NCE-EST Kampanya)
        |         Liste 4'ten kaldir
        |
        +-- HAYIR → Liste 4'te kalir (temizlenir)
```

### Nurture Email Dizisi (IYS sonrasi aktif olacak)

```
Brevo Liste 3 (NCE-EST Kampanya) → kisi eklendi
    |
    v
BREVO AUTOMATION #2 (NURTURE) [HAZIR, AKTIF DEGIL]
    |
    +-- Gun 0:  "NCE Grace Period bitiyor" → blog linki
    +-- Gun 3:  "Lisanslariniz nasil etkilenecek?" → fiyat karsilastirma
    +-- Gun 6:  "Bir musterimiz %23 tasarruf etti" → case study
    +-- Gun 9:  "Ucretsiz lisans degerlendirmesi" → iletisim formu
    +-- Gun 12: "Son hatirlatma — 4 Mayis'a az kaldi" → WhatsApp + gorusme
```

## Sistem Envanteri

### Platformlar

| Platform | URL / Erisim | Rol | Durum |
|----------|-------------|-----|-------|
| gibibyte.com.tr | Vercel (auto-deploy main) | Website + API | CANLI |
| hunter.gibibyte.com.tr | Azure VM (Docker) | Lead intelligence | CANLI |
| Brevo | app.brevo.com | Email marketing | CANLI |
| D365 Sales | org.crm4.dynamics.com | CRM | CANLI |
| Power Automate | flow.microsoft.com | Otomasyon | CANLI |
| GA4 | G-Z9EYLHL1WP | Analytics | CANLI |
| GTM | GTM-PML8LBG2 | Tag manager | CANLI |
| Clarity | w1i6s9jd7 | Heatmap | CANLI |
| WhatsApp Business | 905522898311 | Hizli temas | CANLI |
| Formspree | xeerpkyy | Iletisim formu | CANLI |

### Vercel Environment Variables

| Key | Icin | Sensitive |
|-----|------|-----------|
| BREVO_API_KEY | Brevo REST API | Evet |
| HUNTER_API_KEY | Hunter webhook auth | Evet |
| HUNTER_API_URL | https://hunter.gibibyte.com.tr | Hayir |
| POWER_AUTOMATE_WEBHOOK_URL | D365 Lead olusturma | Evet |

### Brevo Listeleri

| ID | Ad | Amac |
|----|---|------|
| 3 | NCE-EST Kampanya | Onaylanmis kisiler, nurture hedef |
| 4 | DOI Bekleyenler | Onay bekleyen kisiler |

### Brevo Contact Attributes

| Attribute | Type | Kaynak |
|-----------|------|--------|
| FIRSTNAME | Text | Form |
| LASTNAME | Text | Form |
| COMPANY | Text | Form |
| PHONE | Text | Form |
| LEAD_SCORE | Number | Hunter P-Model |
| LEAD_SEGMENT | Text | Hunter (Existing/Hot/Warm/Skip) |
| UTM_SOURCE | Text | URL param |
| UTM_CAMPAIGN | Text | URL param |
| UTM_MEDIUM | Text | URL param |
| LANDING_PAGE | Text | window.location.pathname |
| FORM_TYPE | Text | Form tipi (nce-est/pdf-download/demo/assessment) |
| VISIT_COUNT | Number | localStorage sayaci |

### D365 Entiteler

| Entity | Kullanim | Durum |
|--------|---------|-------|
| Lead | Website lead'leri | Aktif, PA webhook ile |
| Campaign | NCE-EST kampanyasi | 1 tane olusturuldu |
| hnt_* fields | Hunter custom alanlari | 29 field mevcut |

### Website Sayfalari + Lead Capture

| Sayfa | URL | Lead Capture | Form Tipi |
|-------|-----|-------------|-----------|
| Ana Sayfa | / | AIReadinessChecker + LeadMagnet | assessment + pdf-download |
| Hizmetler | /hizmetler | LicenseCalculator | pdf-download |
| AI Governance | /ai-governance | LicenseCalculator (AI) | pdf-download |
| NCE/EST | /nce-est | NCE form (4 alan + countdown) | nce-est |
| Tenra | /tenra | Demo talep | demo |
| Iletisim | /iletisim | Formspree (ayri kanal) | contact |
| Blog | /blog/* | Yok (inline CTA'lar) | — |
| Pillar | /microsoft-365-rehber | Yok (blog linkleri) | — |

### WhatsApp Context Mesajlari

| Sayfa | Pre-filled Mesaj |
|-------|-----------------|
| / | Gibibyte hizmetleri hakkinda bilgi almak istiyorum |
| /hizmetler | Microsoft 365 hizmetleriniz hakkinda |
| /ai-governance | AI Governance hizmeti hakkinda |
| /tenra | Tenra demo talebi hakkinda |
| /nce-est | NCE lisans gecisi hakkinda |
| /iletisim | Bir sorum var |
| /blog/* | Blog yazinizi okudum, bir sorum var |

## SEO Altyapisi

| Bilesen | Durum | Detay |
|---------|-------|-------|
| Sitemap | 19 URL | public/sitemap.xml |
| robots.txt | Tum bot'lara acik | GPTBot, ClaudeBot, PerplexityBot dahil |
| llms.txt | 58 satir | Hizmetler, fiyat modeli, blog listesi, farklilastiricilar |
| JSON-LD Organization | Tamam | index.html |
| JSON-LD ProfessionalService | Tamam | geo, hours, priceRange |
| JSON-LD OfferCatalog | 6 kategori, 11 hizmet | index.html |
| JSON-LD BlogPosting | Tamam | Dinamik, her blog sayfasinda |
| PageMeta | Tum sayfalarda | Title + description + OG tags |

## Icerik Envanteri

### Blog Yazilari (14)

| # | Slug | Kategori | Kelime | Tarih |
|---|------|----------|--------|-------|
| 1 | microsoft-365-e3-yeni-ozellikler-temmuz-2026 | Lisanslama | ~1150 | 2026-03-28 |
| 2 | microsoft-nce-lisanslama-rehberi | Lisanslama | ~1090 | 2026-03-28 |
| 3 | microsoft-365-e7-frontier-suite | Lisanslama | ~976 | 2026-03-28 |
| 4 | microsoft-365-fiyat-artisi-temmuz-2026 | Lisanslama | ~794 | 2026-03-28 |
| 5 | microsoft-nce-est-mayis-2026 | Lisanslama | ~756 | 2026-03-28 |
| 6 | microsoft-365-business-basic-vs-premium | Lisanslama | ~657 | 2026-03-28 |
| 7 | copilot-governance-rehberi | AI Governance | ~697 | 2026-03-29 |
| 8 | shadow-ai-nedir-nasil-tespit-edilir | AI Governance | ~1155 | 2026-03-29 |
| 9 | microsoft-copilot-verimlilik-rehberi | AI Governance | ~796 | 2026-03-29 |
| 10 | mfa-neden-kritik-copilot-baglantisi | Guvenlik | ~717 | 2026-03-29 |
| 11 | microsoft-365-secure-score-rehberi | Guvenlik | ~787 | 2026-04-06 |
| 12 | zero-trust-kobi-uygulama | Guvenlik | ~871 | 2026-04-13 |
| 13 | intune-cihaz-yonetimi-rehberi | Guvenlik | ~756 | 2026-04-20 |
| 14 | dynamics-365-sales-dijitallestirme | CRM | ~770 | 2026-04-27 |

### Dagitim: Lisanslama 6 (%43) | Guvenlik 4 (%28) | AI Gov 3 (%22) | CRM 1 (%7)

## Koruma Katmanlari

```
KATMAN 1 — CLIENT (React)
  +-- Disposable email domain listesi (3400+ domain)
  +-- Honeypot gizli input alani
  +-- HTML5 form validation

KATMAN 2 — SERVER (Vercel API)
  +-- Honeypot server-side kontrol
  +-- Hunter email dogrulama (MX + SMTP)
  +-- Corporate vs webmail ayirimi

KATMAN 3 — EMAIL (Brevo)
  +-- Double opt-in (onay emaili)
  +-- Liste ayirimi (DOI bekleyenler vs onaylanmis)

KATMAN 4 — CRM (D365)
  +-- Hunter P-Model skoru threshold (>= 70)
  +-- Lead Rating (Hot/Warm/Cold)
  +-- Campaign attribution
```

## Metrikler (Hedef)

```
1,000 ziyaretci/ay
  → 30 lead (%3 donusum)
    → 21 DOI onay (%70 onay orani)
      → 6 MQL (%30 kalifikasyon — Hunter score >= 60)
        → 2 SQL (%33 — demo/gorusme talep etti)
          → 1 musteri / 2 ayda (%50 close)
            → 2,000 TL/ay kontrat = 72,000 TL LTV (3 yil)
```

## Maliyet Tablosu

| Platform | Plan | Aylik Maliyet | Limit | Upgrade Tetikleyici |
|----------|------|--------------|-------|---------------------|
| Vercel | Hobby (free) | $0 | 100GB bant, 12 serverless fn | Trafik > 100GB/ay |
| Brevo | Free | $0 | 300 email/gun, 100K kisi, 2K automation | > 300 email/gun |
| Hunter | Self-hosted | $0 (Azure VM maliyeti haric) | Rate limit: 60/dk | — |
| D365 Sales | E5 dahil | $0 (E5 lisansinda) | — | — |
| Power Automate | E5 dahil | $0 (E5 lisansinda) | 6K calistirma/ay | — |
| GA4 + GTM | Free | $0 | — | — |
| Clarity | Free | $0 | — | — |
| Formspree | Free | $0 | 50 submit/ay | > 50 submit/ay → $10/ay |
| WhatsApp Business | App (free) | $0 | — | API gerekirse ~$50/ay |
| **TOPLAM** | | **$0/ay** | | |

Ilk ucretli upgrade: Brevo Starter ($25/ay) — email hacmi artinca.

## Deploy Workflow

```
KURAL: Dogrudan main'e push YASAK (acil hotfix harici)

1. Degisiklik → dev branch'te yap
2. bun run build → basarili mi?
3. git push origin dev → Vercel preview deploy
4. Preview URL'de kontrol et
5. Onay → git checkout main && git merge dev && git push origin main
6. Vercel production auto-deploy
7. Canli sitede son kontrol
```

### Commit Kontrol Listesi
- Build gecti mi
- Blog: sitemap guncel, slug dogru
- Form/CTA: analytics event eklendi
- console.log temizlendi
- Commit mesaji: imperative, Ingilizce

## Claude Code Altyapisi (Continuity Hub)

### Skills (4)
| Skill | Tetikleyici | Ne yapar |
|-------|------------|----------|
| `/blog-yaz [konu]` | "blog yaz", "makale olustur" | Arastirma → BlogPost → sitemap → build dogrula |
| `/seo-kontrol` | "SEO durumu", "sitemap guncel mi" | 7 adim SEO denetimi, KRITIK/UYARI/OK rapor |
| `/deploy-kontrol` | "deploy oncesi kontrol" | Build + lint + icerik tutarliligi + redirect |
| `/design-review` | "tasarim kontrol", "tutarlilik" | 8 kontrol: H1, label, badge, CTA, glass-card |

### Agents (2)
| Agent | Model | Rol | Skill'ler |
|-------|-------|-----|-----------|
| content-writer | Sonnet | Blog/FAQ/sayfa icerigi | blog-yaz, react-best-practices |
| qa-reviewer | Haiku | Build/lint/SEO/deploy kontrol | seo-kontrol, deploy-kontrol |

### MCP Server'lar (3)
| Server | Tip | Ne yapar |
|--------|-----|----------|
| shadcn/ui | HTTP | Component registry erisimi |
| Playwright | stdio | Browser otomasyon ve test |
| Lighthouse | stdio | Performance, SEO, a11y audit |

### Hooks (2)
| Hook | Tetik | Ne yapar |
|------|-------|----------|
| PostToolUse (Edit/Write) | Dosya degisikligi | Prettier auto-format |
| SessionStart (compact) | Context kaybi | Kritik kurallari yeniden enjekte |

## Sorumluluk Matrisi

### Roller

```
UST AKIL (ragip-aga-kit Claude Code)
  → Strateji, arastirma, plan, prompt yazma
  → Cross-repo koordinasyon
  → Kalite kontrol, "bu dogru mu?" sorusu
  → Memory ve dokumantasyon

WEB DEV (continuity-hub Claude Code)
  → React component gelistirme
  → Vercel API endpoint'leri
  → Blog icerigi (content-writer agent)
  → SEO/QA (qa-reviewer agent)
  → Build + deploy

HUNTER DEV (dyn365hunterv3 Claude Code)
  → Hunter API endpoint'leri
  → Nginx config, guvenlik
  → D365 push entegrasyonu
  → Scorer/P-Model degisiklikleri
```

### Karar Matrisi

| Karar | Kim karar verir | Kim uygular |
|-------|----------------|-------------|
| Yeni ozellik eklensin mi | Kullanici + Ust Akil | Web Dev / Hunter Dev |
| Hangi blog yazilsin | Kullanici + Ust Akil | Web Dev (content-writer) |
| API endpoint tasarimi | Ust Akil | Web Dev / Hunter Dev |
| D365 field mapping | Hunter Dev | Hunter Dev |
| Brevo automation | Ust Akil | Kullanici (dashboard) |
| Power Automate flow | Ust Akil | Kullanici (dashboard) |
| Deploy onay | Kullanici | Web Dev |
| Mimari karar (ADR) | Ust Akil + Kullanici | Ilgili Dev |

## Hata Durumlari ve Fail-Safe

### Temel Kural: Hic bir dis servis hatasi lead kaybettirmez

```
HUNTER COKERSE:
  → lead-capture.ts try/catch ile yakalar
  → score=0, segment=unknown olarak devam eder
  → Brevo'ya kisi yine eklenir
  → D365'e gitmez (score < 70)
  → SONUC: Lead kaybolmaz, sadece skorlanmaz

BREVO COKERSE:
  → lead-capture.ts try/catch ile yakalar
  → 500 hatasi → kullaniciya "Tekrar deneyin" mesaji
  → SONUC: Lead kaybolur (yeniden form doldurmalari lazim)
  → ONLEM: Brevo status page izle

POWER AUTOMATE COKERSE:
  → lead-capture.ts try/catch ile yakalar
  → Brevo'ya kisi yine eklenir
  → D365'e gitmez
  → SONUC: Hot lead D365'te gorulmez, Brevo'da var
  → ONLEM: Brevo'dan manuel D365 aktarimi yapilabilir

VERCEL COKERSE:
  → Tum site erisim disi
  → SONUC: Hicbir sey calismaz
  → ONLEM: Vercel status page, uptime monitoring

D365 COKERSE:
  → Power Automate retry (3 deneme)
  → SONUC: Lead gecikmeli olusur veya kaybolur
  → ONLEM: Power Automate hata emaili gonderir
```

### Rate Limit'ler

| Servis | Limit | Risk |
|--------|-------|------|
| Hunter API | 60 istek/dk | Dusuk (gunde 5-20 lead) |
| Brevo API | 300 email/gun | Dusuk (DOI + nurture) |
| Brevo automation | 2,000 kisi | Orta (buyuyunce upgrade) |
| Power Automate | 6,000 calistirma/ay | Dusuk |
| Vercel serverless | 100GB bant/ay | Dusuk |
| Formspree | 50 submit/ay | Orta (iletisim yogunlugu) |

## Erisim ve Hesap Sahiplikleri

| Platform | Hesap Sahibi | Erisim Yontemi | Notlar |
|----------|-------------|---------------|--------|
| Vercel | brdfbai (GitHub org) | GitHub OAuth | Hobby plan |
| Brevo | subs@gibibyte.com.tr | Email login | Free plan |
| D365 Sales | Gibibyte M365 tenant | Azure AD | E5 lisans |
| Power Automate | Gibibyte M365 tenant | Azure AD | E5 dahil |
| Hunter (VM) | Azure subscription | SSH | Docker compose |
| GA4 | Gmail hesabi | Google login | Property: G-Z9EYLHL1WP |
| GTM | Gmail hesabi | Google login | Container: GTM-PML8LBG2 |
| Clarity | Microsoft hesabi | MS login | Project: w1i6s9jd7 |
| GitHub (brdfb) | Kisisel | SSH key | ragip-aga-kit, hunter |
| GitHub (brdfbai) | Organizasyon | SSH key | continuity-hub, PRST, gibibyte-* |
| Formspree | — | API | Form ID: xeerpkyy |
| WhatsApp Business | 905522898311 | Telefon app | Business profil ayarli |
| Cloudflare | — | Dashboard | DNS: gibibyte.com.tr |

## Acik Sorular ve Riskler

### 1. Lead → Musteri → Fatura gecisi dokumante degil

Hunter lead olusturuyor (satis oncesi), PRST fatura sync yapiyor (satis sonrasi).
Ortadaki satis sureci tamamen manuel:

```
Hunter Lead → ??? → D365 Opportunity → ??? → D365 Order → PRST Fatura Sync
```

Sorular:
- Lead'den opportunity'ye kim/nasil geciriyor?
- Teklif sureci D365'te mi, Excel'de mi?
- Quote/Order entity'leri kullaniliyor mu?
- PRST ne zaman devreye giriyor?

### 2. MARA/Tenra — demo hazirlik durumu belirsiz

`/tenra` sayfasi "Demo Talep Edin" diyor. Birisi demo isterse:
- Demo ortami canli mi?
- Demo sureci nasil isliyor?
- Tenra'nin production durumu ne?
- Form submit → D365 Lead (formType=demo) → sonra ne oluyor?

### 3. RAG sistemi (agent + knowledge-source) pasif

gibibyte-agent (20 skill, Qdrant) ve gibibyte-knowledge-source (65 dokuman) mevcut
ama continuity-hub'la entegrasyonu yok. Su an:
- Kim kullaniyor?
- Hangi is akisinda devreye giriyor?
- Website'den erisim var mi yoksa sadece dahili mi?
- Aktif gelistirme var mi yoksa bekleme modunda mi?

### 4. D365 satis pipeline belirsiz

Lead entity kullaniliyor (Lead Engine'den). Ama:
- Opportunity entity kullaniliyor mu?
- Pipeline asamalari tanimli mi?
- Win/loss takibi var mi?
- Forecast/raporlama var mi?

### 5. Monitoring sifir

Hicbir sistemde uptime/health monitoring yok:

| Sistem | Cokerse | Fark eden |
|--------|---------|-----------|
| gibibyte.com.tr (Vercel) | Site erisim disi | Kimse (Vercel statuspage var ama alert yok) |
| hunter.gibibyte.com.tr | Lead skorlama durur | Kimse |
| Brevo | Email gitmez | Kimse |
| Power Automate | D365 lead olusturmaz | Kimse |
| D365 | CRM erisim disi | Muhtemelen kullanici fark eder |

Oneri: UptimeRobot (ucretsiz, 5 dk aralik) ile en az website ve Hunter izlenmeli.

### 6. Uncommitted degisiklikler (2 Nisan 2026 snapshot)

| Repo | Degisiklik | Durum |
|------|-----------|-------|
| dyn365hunterv3 | 4 dosya | Aktif gelistirme mi, unutulmus mu? |
| gb_ragipaga | 2 dosya | Emekli repo'da neden degisiklik var? |
| gibibyte-continuity-hub | 1 dosya | Dev branch'te calisan is? |
| ragip-workspace | 1 dosya | Senaryo testi bekleyen degisiklik? |

## Bekleyen Isler

### Yakin Vadeli
| # | Is | Bagimlitik | Kim |
|---|---|-----------|-----|
| 1 | Nurture automation activate | Liste karari (toplu data import) | Kullanici |
| 2 | IYS kaydi (iys.org.tr) | Sirket bilgileri | Kullanici |
| 3 | DOI 404 redirect duzelt | Brevo ayari | Kullanici |

### v2 (Lead hacmi artinca)
| # | Is | Neden bekliyor |
|---|---|---------------|
| 1 | D365 composite scoring | Power Automate flow, lead hacmi < 50 |
| 2 | Brevo ↔ D365 engagement sync | Karmasiklik/fayda orani |
| 3 | GA4 web_intent_score | Custom infrastructure lazim |
| 4 | Hunter scan callback | Poll yeterli su an |
| 5 | WhatsApp component refactor | Context-aware linkler calisiyor |
| 6 | Padding/badge standardizasyonu | Gorsel etki dusuk |

## Repo Baglantilari

```
gibibyte-continuity-hub (website)
    |
    +-- API call → dyn365hunterv3 (Hunter — lead intelligence)
    |                  |
    |                  +-- API call → D365 Sales (CRM)
    |
    +-- API call → Brevo (email marketing)
    |
    +-- Webhook → Power Automate → D365 Sales
    |
    +-- Formspree (sadece iletisim formu)
    |
    +-- GA4 + GTM + Clarity (analytics)

ragip-aga-kit (bu repo)
    +-- Dokumantasyon hub'i
    +-- Claude Code ust akil
    +-- Agent sistemi (KOBi finans — ayri concern)

PRST (Parasut → D365 sync)
    +-- Fatura/odeme senkronizasyonu
    +-- D365 prst_* alanlari
    +-- Lead Engine "satis sonrasi" ayagi

mara (Tenra platformu)
    +-- Tenant yonetim + tarama
    +-- 178 test, 7 adapter, 28 route
    +-- /tenra sayfasinin arkasindaki urun

gibibyte-agent (sidecar RAG agent)
    +-- 20 skill, Qdrant vektör DB
    +-- FastMCP, v0.9.0
    +-- Continuity Hub ile entegrasyonu YOK (bagimsiz)

gibibyte-knowledge-source (RAG bilgi tabani)
    +-- 65 dokuman, v0.7.0
    +-- Teklif sablonu, NCE kurallar, brand guide
    +-- gibibyte-agent tarafindan kullanilir
```

### Tum Repolar Durum Tablosu

| # | Repo | Durum | Son Aktivite | Not |
|---|------|-------|-------------|-----|
| 1 | ragip-aga-kit | Aktif | 2 Nisan 2026 | Ust akil, dokumantasyon |
| 2 | ragip-workspace | Aktif | 28 Mart 2026 | Kit kurulumu + D365 MCP |
| 3 | dyn365hunterv3 | Aktif | 1 Nisan 2026 | Lead intelligence, canli |
| 4 | gibibyte-continuity-hub | Aktif | 2 Nisan 2026 | Website, Lead Engine |
| 5 | PRST | Aktif | 2 Nisan 2026 | Parasut→D365 sync |
| 6 | mara | Aktif | 2 Nisan 2026 | Tenra platformu |
| 7 | gibibyte-agent | Aktif | 24 Mart 2026 | RAG agent |
| 8 | gibibyte-knowledge-source | Aktif | 19 Mart 2026 | RAG bilgi tabani |
| 9 | gb_ragipaga | Emekli | 19 Mart 2026 | Referans, kit'e tasindi |
| 10 | gb_ragip_new | Emekli? | 23 Subat 2026 | Temizlik adayi |
| 11 | gb_ragip | Olu | — | Git yok, temizlik adayi |
