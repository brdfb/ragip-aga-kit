# Kurulum Rehberi

Ragip Aga Kit'i sifirdan calisir hale getirmek — KOBI sahibi, muhasebeci veya danisman icin adim adim. Teknik detay minimum.

**Tahmini sure:** 20-30 dakika (API key kayitlari dahil).

---

## Once ne almak gerekiyor?

Kit iki disaridaki servisle konusuyor. Ikisinden de bir "API key" (giris anahtari) gerekli:

| Servis | Ne icin | Zorunlu mu? |
|---|---|---|
| **Anthropic Claude** | Ragip Aga'nin **beynini** calistirir (sozlesme analizi, degerlendirme, strateji) | **EVET** — bu olmadan model cagrilari calismaz |
| **TCMB EVDS3** | Canli **faiz ve kur** verisi (politika faizi, dolar, euro) | Cok onerilir — yoksa kit eski fallback verilerle calisir, yanlis vade farki hesaplayabilir |

Iki key de **ucretsiz aliniyor** (Anthropic'te sadece kullanim kadar odenir; TCMB tamamen ucretsiz).

---

## Adim 1 — Anthropic API key al (15 dk)

**Neden:** Kit sozlesme analizi, ihtar taslagi, hukuki degerlendirme yaparken Claude Sonnet 5 modeline cagri yapar. Bu cagrilar senin Anthropic hesabina yazilir; sen ne kadar kullaninsan o kadar odersin.

**Nasil alinir:**

1. https://console.anthropic.com adresine git.
2. Hesabin yoksa **Sign up** — e-posta + kredi kart bilgisi (kayit ucretsiz, sadece kullaninca odenir).
3. Girince sol menuden **Settings → Billing** — kart ekle. Onerilen ilk yukleme: **$20** (test amacli).
4. Sol menuden **Settings → Workspaces** — sag ustten **Create Workspace** → ad: "Ragip Aga" (ya da is/musteri adin).
5. **Budget limit koy (COK ONEMLI):** Workspace ayarlarinda **Spend Limits → Monthly**  $10 gir. Bu bir "sigorta" — bir hata olsa bile faturan patlamaz.
6. Sol menuden **Settings → API Keys** → **Create Key** → workspace: az once acdigin — anahtar `sk-ant-api03-...` ile baslayan uzun bir string.
7. **BU KEY'I HEMEN KOPYALA** — bir daha gostermeyecek. Bir yere kaydet (yalniz sen erisebilecegin bir yere).

**Sat perspektifi:** Bu key SENIN. Musteriye kit'i satsan, o kendi Anthropic hesabini acar, kendi key'ini alir. Bu **karisamaz** — kimin key'i kimin hesabina yazilir, izole.

---

## Adim 2 — TCMB EVDS3 kayit (5 dk)

**Neden:** Kit vade farki, arbitraj, temerrud faizi hesaplarken guncel **politika faizi** ve **dolar/euro kuru** gerekiyor. TCMB (Merkez Bankasi) bu veriyi ucretsiz veriyor ama kayit istiyor.

**Nasil alinir:**

1. https://evds3.tcmb.gov.tr adresine git.
2. Sag ustten **Uye Girisi → Uyelik**.
3. Sirket adin veya kendi adinla kayit. TCKN + e-posta + telefon.
4. Kayit sonrasi giris yap → **Profil → API Anahtari → Uret**.
5. Anahtari kopyala (32 karakter civari).

**Uyari:** TCMB API key **degil** de sirket adin ile alinabilirdi ama gerekmez — kisi kaydi da yeterli. Tek key TCMB'ye erisim veriyor, sirket-kisi ayrimi yok.

**Alma zorluysa ne olur?** Kit fallback verilerle calisir — su an "137 gun once manuel girilmis" degerler. Vade farki hesabi bu durumda yanlis olabilir. Musteriye demo yapmadan once mutlaka al.

---

## Adim 3 — Kit'i indir + kur (5 dk)

Bu tamamen bilgisayarinda yapilir; hicbir servise baglanmaz.

```bash
# 1. Kit'i indir (bir defa)
git clone https://github.com/brdfb/ragip-aga-kit.git /tmp/ragip-aga-kit

# 2. Kit'i kurmak istedigin hedef repoya git
#    (bu senin is repo'n olabilir — musteri kayitlarini burada tutacaksin)
cd /path/to/senin-is-repo

# 3. Kur
bash /tmp/ragip-aga-kit/install.sh

# 4. Test — hepsi gecmeli
python -m pytest tests/test_ragip_subagents.py -v
```

**Onemli:** `hedef repo` bir git deposu olmali. Yoksa `git init` ile bir tane yap once.

---

## Adim 4 — `.env` dosyasini olustur ve doldur (2 dk)

Kit kurulumun sonunda sana "SIRADAKI ADIM: .env" diye bir uyari verecek. Uyariyi takip et:

```bash
# 1. Ornek dosyayi kopyala
cp /tmp/ragip-aga-kit/.env.example .env

# 2. .env dosyasini ac (nano, vim, VSCode — istedigin editor)
nano .env
```

Dosyada su iki satiri bul ve iki nokta ustusten (`=`) sonra key'lerini yaz:

```
ANTHROPIC_API_KEY=sk-ant-api03-BURAYA_ADIM1_KEY_YAPISTIR
TCMB_API_KEY=BURAYA_ADIM2_KEY_YAPISTIR
```

Kaydet, kapat.

**Guvenlik notu:** `.env` **git'e commit edilmez** (kit `.gitignore` ile korumus). Yalniz senin bilgisayarinda kalir. Yine de yedegini bir sifre yoneticisinde (Bitwarden, 1Password vb.) tut.

---

## Adim 5 — Ilk kullanim (5 dk)

Claude Code'u ac. Su komutlari sirayla dene:

```
/ragip-profil kaydet
```

Ragip Aga sana bazi sorular soracak: firmanin sektoru, is tipi (ithalat/uretim/dagitim/hizmet), doviz riski var mi vb. Bu profil tum analizlerde arka planda kullanilir.

```
/ragip-firma ekle ABC Dagitim tip=musteri vade=45 oran=3
```

Bir musteri firma kayitli ekle.

```
/ragip-vade-farki 250000 3 45
```

250.000 TL, aylik %3, 45 gun icin vade farki hesabi. Ciktida canli TCMB politika faizi ile karsilastirma gorursun.

Bunlarin hepsi calisiyorsa **kit yasyor**. Simdi gercek is:

```
/ragip-analiz musterinin_sozlesmesi.pdf
```

Bir sozlesme PDF'ini analiz ettir. PII maskeleme, madde tespit, risk skoru, oneri listesi — 3-5 dakikada bir rapor uretir.

---

## Adim 6 — (Opsiyonel) Zamanlanmis gorevler

Kit her hafta ici sabahi TCMB oranlarini otomatik yenileyebilir, her pazar cikti dosyalarini temizler:

```bash
bash /tmp/ragip-aga-kit/scripts/ragip_cron.sh --setup
```

Kontrol icin:

```bash
bash /tmp/ragip-aga-kit/scripts/ragip_cron.sh --status
```

Iptal:

```bash
bash /tmp/ragip-aga-kit/scripts/ragip_cron.sh --remove
```

---

## Sorun giderme

### "Model cagrisi hata verdi" mesaji
- `.env` dosyasi hedef repoda mi? `ls -la .env` ile kontrol et.
- `ANTHROPIC_API_KEY` satirinda bosluk yok mu, `=` isaretinden sonra dogru mu yapistirdim?
- Anthropic Console'da workspace budget limit'ini asmis olabilirsin — Settings → Billing → Usage'a bak.

### "TCMB fallback kullaniliyor" uyarisi
- `.env` icinde `TCMB_API_KEY` bos veya yanlis. EVDS3 profil sayfasindan tekrar uret.
- Yakinlarda bir API degisikligi olabilir. `python3 scripts/ragip_rates.py --pretty` ile manuel test et.

### "PYTHONPATH" veya "ImportError" hatasi
- `pip install -r /tmp/ragip-aga-kit/requirements.txt` calistir.
- Python 3.12 veya ustu kullaniyor musun? `python3 --version`.

### Cikti dosyalari nereye gidiyor?
- `data/RAGIP_AGA/ciktilar/YYYYMMDD_HHMMSS-<agent>-<skill>-<konu>.md` seklinde hedef repoda.
- Ay klasoru ve firma klasoru otomatik olusur.

### Bir musteri kit'i satin aldi, nasil kuracak?
- Ayni bu rehberi takip eder — sadece **kendi** Anthropic + TCMB key'lerini alir.
- **Musterinin key'i sana gitmez, seninki musteriye gitmez.** Kit self-hosted.

---

## Yardim

- Sorun: https://github.com/brdfb/ragip-aga-kit/issues
- Yasal sinirlar: [KULLANIM_SARTLARI.md](KULLANIM_SARTLARI.md)
- Teknik referans: [README.md](README.md)
