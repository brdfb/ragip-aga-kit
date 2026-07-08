# Kullanim Sartlari ve Sinirlar

Ragip Aga Kit **egitim ve karar destek** aracidir. Bu belge kit'in yasal ve pratik sinirlarini tanimlar.

## 1. Hukuki sinirlar

**Bu kit hukuki gorus vermez.**
- Kit ticari mevzuat (TBK, TTK, IIK, HMK, KVKK) referanslariyla degerlendirme uretir.
- Uretilen **her hukuki cikti** (degerlendirme, ihtar taslagi, delil stratejisi, zamanasimi hesabi) bir avukat kontrolunden **gecmelidir**.
- Kit ciktilari kesin islem (ihtar gonderme, dava acma, icra baslatma) oncesi **tek basina yeterli degildir**.

**Sorumluluk sinirlari:**
- Kit'i olusturan ve dagitan taraf (Gibibyte) kit'in gercek dunyada uretecegi kararlarin sonuclarindan **sorumlu tutulamaz**.
- Kullanici, kit'in urettigi bir taslak veya tavsiye ile hareket etmeden once bagimsiz uzman (avukat, mali musavir, muhasebeci) gorusu almalidir.
- Kit'in Tier 5 (regex format kontrolu) ve Tier 6 (LLM-judge) katmanlari **yardimci** olcumlerdir — insan denetiminin yerini almazlar.

## 2. Yatirim/finansman sinirlari

**Bu kit yatirim tavsiyesi vermez.**
- Vade farki, arbitraj, forward kur, carry trade hesaplamalari **egitim** ve **karar destek** amaclidir.
- Piyasa risklerini icermez; gercek islem oncesi bir finansal danisman ile gorusun.
- TCMB canli oran erisimi API key gerektirir; yoksa **fallback** oranlarla calisir. Fallback tarihini kullanici gormeli (`bash scripts/ragip_get_rates.sh` ciktisinda uyari donuluyor).

## 3. Veri isleme ve KVKK

**Veri sorumlusu:** Kit'i **kuran ve kullanan** (yani kendi repo'sunda calistiran) taraf, isledigi kisisel verinin (musteri adi, TCKN, iletisim) sorumlusudur. Kit sadece bir yazilim aracidir.

**PII maskeleme:**
- Sozlesme analizinde `ragip_pii.py` maskeleme uygulanir (isim, TCKN, IBAN, telefon, email).
- Maskelenmis metin analize sokulur; orijinal sadece kullanicinin diskindedir.
- Analiz bitiminde placeholder'lar geri cevrilir; mapping dosyasi lokal repoda saklanir.

**Yasal talep hakki:**
- Silme talebi geldiginde: `data/RAGIP_AGA/sozlesmeler/<FIRMA_SLUG>/` dizini ile birlikte `firmalar.jsonl` ilgili kaydi manuel silinmelidir.
- Silme sonrasi manifest yeniden hesaplanmali (`bash update.sh`).

**Aydinlatma yukumlulugu:** Kit'i musterilere yonelik urun/hizmet olarak sunan taraf, KVKK m.10 kapsaminda **aydinlatma metni** hazirlamalidir. Kit bu metni saglamaz.

## 4. Cikti kullanimi

**Ciktilar bilgi tasir, taahhut icermez:**
- Kit'in urettigi ihtar taslagi, degerlendirme raporu, strateji plani — **imzasiz** ve **gonderilmemis** taslaklardir.
- Kullanici bunlari incelemeden, imzalamadan ve avukat kontrolunden gecirmeden **hicbir tarafa gonderemez**.

**Gonderim oncesi kullanici sorumlulugu:**
- Karsi tarafin tebligat adresini dogrula (ticaret sicil oncelikli).
- Gonderim yontemi (noter/KEP/iadeli taahhutlu) sec.
- Sozlesmedeki ihtar sekil sartini kontrol et.
- Fatura itirazinda TTK m.21/2 sinirli 8 gunluk sureyi kontrol et.

## 5. Prompt injection ve adversarial giris

**Karsi taraftan gelen dosyalar guvenli sayilmaz:**
- Sozlesme, fatura, e-posta gibi dosyalarin icine kotu niyetle model yonlendirme talimatlari gizlenmis olabilir.
- `ragip-analiz` skill'i **Adim 1a** ile bu tur sinyalleri tarar ve kullaniciya bildirir.
- Sinyal bulunursa, kullanici onayi olmadan analiz ilerlemez.

**Kullanici sorumlulugu:** Kaynagi belirsiz dosyalari kit'e sokmadan once temel bir goz gezdirme yapmali (metin icinde "talimat", "yok say", "override" gibi kaba sinyaller varsa dikkat).

## 6. Model ve maliyet

**Model:** Kit varsayilan olarak `anthropic/claude-sonnet-5` alias'ini kullanir (ADR-0022). Alias tarihsizdir; Claude Code framework guncel modele resolv eder.

**Maliyet:**
- Tier 6 LLM-judge cost guard'i uygular: `--max-budget-usd 0.50` (tek cagri), `--max-cumulative-usd 5.0` (haftalik).
- Fiyat sabitleri Sonnet 5 standard pricing (post-introductory) tarafina yakin — Agustos 2026 sonuna kadar gercek fiyat %33-50 dusuk (introductory).
- Sonnet 5 yeni tokenizer ~%30 daha fazla token uretir; kit'in tahmini token sayisi gercege yakin olmayabilir.
- Ana orchestrator + sub-agent kullanimindaki maliyet kit tarafindan olculmez; kullanici Anthropic Console'dan takip etmelidir.

## 7. Guncelleme ve surdurulebilirlik

- Kit `install.sh` ile kurulur, `update.sh` ile guncellenir.
- Kullanici ozellestirmeleri uclu checksum ile korunur (ADR-0003).
- Kit destegi ve versiyonlama **Gibibyte** tarafindan yurutulur; SLA/garanti taahhutu **yoktur**.
- Sorun bildirimi: `https://github.com/brdfb/ragip-aga-kit/issues`

## 8. Feragat

**Ragip Aga persona'sina dair:** "Ragip Aga" 40 yillik piyasa tecrubeli bir danisman **karakteridir**. Bu karakterin uslubu, tavsiyeleri ve degerlendirmeleri bir yapay zeka modelinin uretimidir — gercek bir insani danismanin gorusu **degildir**.

**"Evladim" tonu:** Persona rahat ve dogrudan konusur. Bu bir samimiyet gostergesidir; ancak arka planda calisan sistem her zaman bir yapay zeka'dir.

---

**Bu belgeyi kabul ederek kit'i kullanmaya devam edersiniz.** Sorular icin: https://github.com/brdfb/ragip-aga-kit/issues
