# ADR-0018: Tier 4 — Dokuman Tutarlilik Kontrolu

**Tarih:** 2026-05-14
**Durum:** Kabul edildi
**Karar vericiler:** Kit gelistirici
**Iliski:** ADR-0010 (Savunma katmanlari), ADR-0013 (Tier 1/2A/2B), ADR-0015 (Tier 2C), ADR-0016 (Tier 3)

## Baglam

Kit'in mevcut savunma katmanlari:

- **Tier 1 Barnum** — generic-bulgu yasagi (firma adi degistirebilir mi testi)
- **Tier 1 ek (v2.17.0)** — Kesinlik kalibi (Do not fabricate certainty)
- **Tier 2A `madde_dogrula`** — deterministik kanun maddesi referansi
- **Tier 2B CoVe** — yapisal verification akisi
- **Tier 2C** — Citation source whitelist
- **Tier 3** — Cikti disiplini (3-satir blok + VARSAYIM)

Bu katmanlar **bulgu-seviyesinde** kontrol yapar. **Eksik olan**: cikti **butun** olarak bakildiginda **ic-celiski** yakalanmaz.

### Gozlemlenmis problem (14 Mayis 2026 Guven Pres testi)

ragip-degerlendirme ciktisi:
- Anapara: 142.593 USD (bolum 1)
- Talep ozeti: 142.593 + 78.039 faiz + 560 EUR (bolum 3)
- "Mart 2026 analizinde 4.368 USD gosterilmisti" (bolum 4 — discrepancy flag, iyi)

Burada cikti **kendi icinde tutarli**, ama 142.593 rakaminin **`toplam`** mi yoksa **`kalan`** mi oldugu acik degil. Kullanici "anapara 142.593 USD" goruyor — fakturalar.jsonl uzerinde dogrulamak isteyince fark cikiyor (toplam=161.555 USD, kalan=142.593 USD). Iki rakam da "anapara" diye etiketlenebilir; baglam karistiriyor.

Bunu yakalayacak otomatik kontrol yok. Modelin elinde sayisal **veri tabani** (faturalar.jsonl) ve sayisal **iddialar** (cikti) ayni baglamda, ama post-generation **cross-check** disiplini yok.

### Cherry-pick kaynagi

**Kaynak:** gibibyte-cfo-agent v0.2 (cherry-pick tarihi: 2026-04-28)
**Lokasyon:** O tarihte `C:\Users\bered\Documents\gecici\cfo` (lokal). Kit-tarafinda cherry-pick edildikten sonra **kaynak repo'nun yeri kararsiz** — `gibibyte-cfo-kit` yeni repo'ya tasinma karari beklenmektedir. Bu nedenle bu ADR sabit URL/yol referansi vermez; cherry-pick **disiplin pattern'i** seviyesinde alindi, kod dosyasi degil. Kaynak yeri degiserse ADR icerigi etkilenmez.

**K3 — Dokuman tutarlilik kontrolu** (cherry-pick edilen kural):

> Plan/tablo uretiminin son adimi: ayni dokumanda celisen mantik var mi tara. Celiski varsa duzelt sonra teslim et.

CFO agent bu disiplinde 3 farkli kontrol yapiyor:
1. **Sayisal tutarlilik** — bolum 1'deki rakam bolum 3'deki rakamla uyumlu mu
2. **Mantik tutarlilik** — onerilen aksiyon, daha onceki tespitle celisiyor mu
3. **Etiket tutarlilik** — ayni rakam farkli etiketle anılıyor mu (anapara vs kalan vs nominal)

## Karar

**Tier 4 — Dokuman tutarlilik kontrolu**, ragip-analiz / ragip-strateji / ragip-degerlendirme'de cikti sentez fazinin son adimi olarak prompt-level zorunluluk.

### Kontrol kapsami

Cikti yazimini tamamlandiktan sonra, ama "teslim" etmeden once, modelin **kendi ciktisini** tarayarak:

1. **Sayisal tutarlilik:** Ayni metrik (anapara, faiz, vade) cikti icinde birden cok yerde geciyor mu? Geciyorsa rakamlar uyumlu mu?
2. **Etiket netligi:** Sayisal iddianin **tanimi** acik mi? ("anapara" → toplam mi kalan mi? "borc" → vadesi gecmis mi tum mu?)
3. **Mantik tutarlilik:** Tavsiye ile gerekce celisiyor mu? ("ihtar at" + "konkordato → icra durdu" ayni dokumanda → ihtar yine atilir mi netlestir)
4. **Senaryo tutarlilik:** 3-senaryo analizi varsa (strateji), her senaryonun maliyet/yarar rakamlari tutarli aralikta mi?

### Davranis kurali

Cikti son draft'i hazirlandıktan sonra, modelden beklenen son adim:

```
**Tutarlilik denetimi (Tier 4):**

Bu raporu teslim etmeden once kontrol et:
- [SAYI] Aynı rakam birden cok yerde gecti mi? Eslesiyor mu?
- [ETIKET] Her sayisal iddianin tanimi acik mi (toplam vs kalan vs nominal)?
- [MANTIK] Tavsiye ile gerekce ic-celiskili mi?
- [SENARYO] Senaryolar arasi rakamlar tutarli aralikta mi?

Bulunan celiski → cikti'da duzelt ve "Tutarlilik denetimi: X celiski bulundu, duzeltildi: ..." notu dus.
Bulunmadi → "Tutarlilik denetimi: temiz." notu dus.
```

Cikti basina veya sonuna **kisa bir denetim notu** zorunlu — model bu adimi atladıysa testle yakalaniyor.

### Kapsam

| Skill | Tier 4 uygulanir mi | Sebep |
|-------|---------------------|-------|
| ragip-analiz | **Evet** | Sayisal + etiket + mantik tutarlilik kritik (sozlesme + 3-senaryo) |
| ragip-strateji | **Evet** | Senaryo tutarlilik kritik (rakam aralik) |
| ragip-degerlendirme | **Evet** | Sayisal tutarlilik kritik (alacak/faiz/dava bilgisi) |
| ragip-vade-farki, ragip-arbitraj | Hayir | Tek-cikti deterministik hesap |
| ragip-zamanasimi, ragip-delil | Hayir | Tek-fact deterministik |
| ragip-firma, ragip-gorev, ragip-import, ragip-ozet, ragip-profil | Hayir | CRUD veri operasyonu |
| ragip-ihtar | Hayir (su an) | Sablon-bazli — gelecek surumde degerlendirilebilir |

## Gerekce

| Alternatif | Red nedeni |
|---|---|
| Sadece programmatik sayisal check | Etiket/mantik tutarlilik LLM cikti dilini cozumlemeyi gerektirir, regex/parser zayif |
| Cikti sonrasi ikinci LLM call (judge) | Maliyet 2x, latency 2x — prompt-level self-check yeterli baslangic |
| Sub-agent ile separate verification | Mevcut Senaryo A/B mimarisini bozar, sub-agent dispatch latency |
| Skill-disi hook (post-generation) | Yapisal degisiklik, mevcut prompt-level pattern'i bozar |
| Hicbir sey (mevcut) | Cherry-pick kaynagi K3 calistigi gozlemleniyor (gibibyte-cfo-agent), bos birakmak kayip |

**Secilen yaklasimin avantajlari:**

- **Defense-in-depth tamamlama:** Tier 1 (bulgu) + Tier 2 (citation) + Tier 3 (format) + **Tier 4 (cross-document)** = full coverage.
- **Prompt-level:** Geri alinabilir, dependency yok.
- **Test edilebilir:** Tutarlilik denetimi kelimesi cikti zorunlulugu olarak prompt'ta, regex/grep ile dogrulanir.
- **Cherry-pick uyumlu:** CFO agent K3 ile birebir uyumlu — cross-project disiplin tutarli.

**Sinirlamalari:**

- Prompt-level enforcement → model atlayabilir. Test sadece prompt'ta kuralin oldugunu dogrular.
- Self-check "model ayni model" sinirlamasi taşır — modelin yapamadigi celisikleri yine yakalayamaz.
- "Tutarlilik denetimi: temiz." notu model her seferinde yazabilir (otomatik onaylama riski) — Tier 4 yapay olarak "yapildi" mesaji uretebilir. Davranissal test bu sinirin disinda.
- Kismi cozum — sec-but-aldatma vs sec-ama-yardim arasi karar verir.

## Konsekvanslar

### Pozitif

- Cikti **butun** olarak guvenilir hale gelir, parca-parca kontrol degil.
- Patch #4 (anapara=toplam vs kalan netligi) gibi etiket-tutarlilik problemleri yapisal yakalanir.
- gibibyte-cfo-agent ile cross-project disiplin tutarliligi (Tier 1-4 hepsi K1-K5 turetimi).

### Negatif

- Cikti uzunlugu artar (1-2 satir denetim notu).
- Self-check zayif olabilir (model atlar veya "temiz" yazar).
- Davranissal test yok — prompt-level kabuk.

### Gelecek calisma

- **LLM-as-judge:** Tier 4'u baska modelle bagimsiz dogrulamak (Haiku gibi ucuz model ile cross-check).
- **Programmatik sayisal check:** Cikti'da gecen sayisal iddialari extract et, faturalar.jsonl ile karsilastir (deterministik). Su an manuel — `scripts/ragip_tutarlilik.py` adayı.
- **Tier 4 metrics:** Test ortaminda her sentez ciktisinda Tier 4 denetim notu var mi take/dump.

## Iliski

- **Onceki:** ADR-0010 (savunma katmanlari), ADR-0013 (Tier 1/2A/2B), ADR-0015 (Tier 2C), ADR-0016 (Tier 3).
- **Cherry-pick:** gibibyte-cfo-agent v0.2 K3 — Dokuman tutarlilik kontrolu.
- **Sonraki:** Tier 4 enforcement guclendirme (LLM-judge ya da programmatik), Patch #4 cikti formati gozeten degisiklik.

## Kaynaklar

- gibibyte-cfo-agent v0.2 (Nisan 2026) — K3 disiplin pattern'i
- 14 Mayis 2026 Guven Pres test bulgusu — anapara etiket belirsizligi
- ADR-0016 — Tier 3 cikti disiplini (TESPIT/POZISYON/GEREKCE format) — Tier 4'un format kompleminderi
