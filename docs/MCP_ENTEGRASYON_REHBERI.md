# MCP Adaptor Entegrasyon Rehberi

Ragip Aga Kit'e yeni bir ERP/CRM veri kaynagi baglamak icin MCP adaptor yazma rehberi.

**Referans:** ADR-0004 (Kit vs MCP Ayrimi), ADR-0007 (Standart Fatura Semasi)

---

## Temel Ilke

Kit sabit, MCP hedef repoya ozgu. Her repo farkli ERP kullanabilir:

```
Repo A (tekstil)   → Parasut MCP
Repo B (ihracatci)  → D365 + Logo MCP
Repo C (eczane)     → Netsis MCP
Repo D (startup)    → MCP yok, manuel import
```

Kit hesaplama motorlari yalnizca `faturalar.jsonl` semasini okur. ERP'yi bilmez.
MCP adaptoru ERP'den veriyi ceker, normalize eder, bu semaya yazar.

---

## Mimari

```
[ERP/CRM API] → MCP Server (auth + query + retry)
                      ↓
               DTO (ERP-specific normalizasyon)
                      ↓
               Semantic Tool (normalize cikti)
                      ↓
               faturalar.jsonl (ADR-0007)
                      ↓
               validate_fatura() → FinansalHesap → Rapor
```

---

## Adim 1: MCP Server

FastMCP veya baska bir MCP framework ile ERP API'sine baglan.

```python
# Ornek: ragip_{erp}_mcp.py
from fastmcp import FastMCP

mcp = FastMCP("ragip-{erp}")

@mcp.tool()
def fatura_listele(firma_id: int | None = None, durum: str = "acik") -> list[dict]:
    """ERP'den fatura listesi ceker."""
    ham_veri = erp_api.get_invoices(firma_id=firma_id, status=durum)
    return [dto_to_fatura(item) for item in ham_veri]
```

**Gerekli tool'lar:**
- `fatura_listele` — Fatura sorgulama (firma_id, durum, tarih araligi filtresi)
- `firma_listele` — Firma/musteri sorgulama
- `firma_raporu` — Tek firma icin semantik ozet (**ZORUNLU** — asagidaki "Semantic Tool" bolumune bak)

**Opsiyonel tool'lar:**
- `fatura_senkron` — faturalar.jsonl'e toplu yazma (import alternatifi)
- `odeme_kaydet` — Odeme bilgisi guncelleme

### Retry ve Pagination

Her ERP API'si rate limit uygular. MCP server'da retry + pagination destegi olmali:

```python
import time

MAX_RETRIES = 3
RETRY_BACKOFF = 2  # saniye

def request_with_retry(method, url, **kwargs):
    """429 throttle icin retry + exponential backoff."""
    for attempt in range(MAX_RETRIES):
        response = method(url, **kwargs)
        if response.status_code == 429:
            wait = int(response.headers.get("Retry-After", RETRY_BACKOFF * (attempt + 1)))
            time.sleep(wait)
            continue
        response.raise_for_status()
        return response
    raise Exception(f"API {MAX_RETRIES} denemede basarisiz: {url}")

def get_paged(url, max_pages=4, **kwargs):
    """Sayfalanmis API sonuclarini birlestir."""
    results = []
    for _ in range(max_pages):
        resp = request_with_retry(httpx.get, url, **kwargs)
        data = resp.json()
        results.extend(data.get("value", []))
        url = data.get("@odata.nextLink") or data.get("next")
        if not url:
            break
    return results
```

**Neden onemli:** Pagination olmadan buyuk dataset'ler eksik gelir. Retry olmadan gecici API hatalari kalici hata gibi gorulur.

---

## Adim 2: DTO Normalizasyonu

DTO katmani ERP-specific kurallari icerir. Her ERP icin ayri yazilir.

### Zorunlu donusumler

| Kural | Aciklama |
|-------|----------|
| **yon mapping** | ERP'deki fatura tipi → `alacak` \| `borc` |
| **durum mapping** | ERP'deki durum kodu → `acik` \| `odendi` \| `kismi` \| `iptal` |
| **tarih formati** | ERP formati → ISO 8601 (YYYY-MM-DD) |
| **tutar/toplam** | Net (KDV haric) ve brut (KDV dahil) dogru alanlara |

### Durumsal donusumler

| Kural | Ne zaman |
|-------|----------|
| **Doviz cevrimi** | ERP USD/EUR fatura sakliyorsa → TRY'ye cevir veya `para_birimi` alanini doldur |
| **Kismi odeme** | ERP'de kismi odeme varsa → `odeme_tutari` + `durum=kismi` |
| **Brut/net duzeltme** | Bazi ERP'ler brut saklar → KDV cikar, net hesapla |

### Ornek DTO

```python
def dto_to_fatura(erp_kayit: dict) -> dict:
    """ERP kaydini ADR-0007 semasina donusturur."""
    return {
        "id": erp_kayit["internal_id"],
        "fatura_no": erp_kayit["invoice_number"],
        "firma_id": erp_kayit["customer_id"],
        "yon": "alacak" if erp_kayit["type"] == "sales" else "borc",
        "tutar": erp_kayit["net_amount"],
        "toplam": erp_kayit["gross_amount"],
        "fatura_tarihi": erp_kayit["date"][:10],  # ISO 8601
        "vade_tarihi": erp_kayit["due_date"][:10],
        "durum": _map_durum(erp_kayit["status"]),
        "kaynak": "erp_adi",
    }
```

---

## Adim 3: Semantic Tool (ZORUNLU)

Agent'lar ham MCP tool'larina (query_records, fatura_listele) dogrudan erismemeli. Bunun yerine **semantic tool** yazilmali.

### Neden zorunlu?

Ham tool'larda agent normalize edilmemis veriyi yorumlar ve yanlis sonuc uretir. Gercek ornekte:
- Ham tool: 24 acik fatura, $124K alacak raporladi
- Semantic tool: 2 acik fatura, $20K alacak (gercek)

Fark: Ham veri odenmis faturalari da "acik" gosteriyor, doviz cevrimi yapilmamis, brut/net karismis.

### Pattern

```python
@mcp.tool()
def firma_raporu(firma_adi: str, top: int = 100) -> dict:
    """Tek firma icin normalize edilmis finansal ozet.

    Bu tool ham veriyi DTO ile normalize eder ve
    ADR-0007 semasina uygun cikti uretir.
    Agent'lar bu tool'u kullanmali, ham query tool'larini degil.
    """
    # 1. Ham veriyi cek
    firma = _get_firma(firma_adi)
    faturalar = _get_paged(f"invoices?$filter=customer eq '{firma['id']}'&$top={top}")

    # 2. DTO ile normalize et
    dto_faturalar = [dto_to_fatura(f) for f in faturalar]

    # 3. Veri kalite kontrolu
    uyarilar = _tespit_veri_uyarilari(dto_faturalar)

    # 4. ADR-0007 semasina donustur
    return {
        "firma": firma,
        "faturalar": dto_faturalar,
        "veri_uyarilari": uyarilar,
    }
```

### Veri Kalite Uyarilari

Semantic tool normalize ederken tespit ettigi sorunlari raporlamali:

```python
def _tespit_veri_uyarilari(faturalar: list[dict]) -> list[str]:
    """Normalize edilmis verideki kalite sorunlarini tespit eder."""
    uyarilar = []
    for f in faturalar:
        if f.get("durum") is None:
            uyarilar.append(f"Fatura {f['fatura_no']}: durum alani bos")
        if f.get("vade_tarihi") == f.get("fatura_tarihi"):
            uyarilar.append(f"Fatura {f['fatura_no']}: vade=fatura tarihi (gecikme hesabi guvenilmez)")
        if f.get("para_birimi", "TRY") != "TRY" and f.get("tutar") and not f.get("fatura_kuru"):
            uyarilar.append(f"Fatura {f['fatura_no']}: doviz fatura, kur bilgisi yok")
    return uyarilar
```

---

## Adim 4: Validasyon

Kit `validate_fatura()` fonksiyonu ile MCP'den gelen verinin ADR-0007'ye uygunlugunu dogrular.

```python
from ragip_crud import validate_faturalar, load_jsonl, data_path

# MCP'den gelen veriyi yukle
faturalar = load_jsonl(data_path('faturalar.jsonl'))

# Dogrula
gecerli, hatali = validate_faturalar(faturalar)
if hatali:
    print(f"{len(hatali)} hatali kayit atlaniyor")
    for h in hatali:
        print(f"  id={h.get('id')}: {h['_hatalar']}")
```

**Validasyon kontrolleri:**
- Zorunlu alan varligi (id, fatura_no, firma_id, yon, tutar, toplam, fatura_tarihi, vade_tarihi, durum)
- yon enum: `alacak` | `borc`
- durum enum: `acik` | `odendi` | `kismi` | `iptal`
- Sayisal tip: tutar, toplam (int veya float)
- Tarih formati: ISO 8601 (YYYY-MM-DD)
- Kismi odeme tutarliligi: durum=kismi → odeme_tutari < toplam
- Para birimi: ISO 4217 (3 karakter)

---

## Adim 5: Hedef Repo Yapilandirmasi

### .mcp.json

```json
{
  "mcpServers": {
    "ragip-{erp}": {
      "command": "python3",
      "args": ["scripts/ragip_{erp}_mcp.py"],
      "env": {
        "ERP_API_URL": "https://...",
        "ERP_API_KEY": "..."
      }
    }
  }
}
```

### disallowedTools — TUM agent'larda

Ham MCP tool'larini **tum** agent'larda bloke et. Yalnizca semantic tool (firma_raporu) acik kalmali.

```yaml
# ragip-aga.md, ragip-hesap.md, ragip-arastirma.md, ragip-veri.md, ragip-hukuk.md
disallowedTools:
  - WebSearch
  - WebFetch
  - mcp__ragip-{erp}__fatura_listele
  - mcp__ragip-{erp}__firma_listele
  - mcp__ragip-{erp}__fatura_senkron
  # firma_raporu ACIK — semantic tool
```

**Neden tum agent'larda?** Agent MCP tool gorunde system prompt talimatini atlayip dogrudan ham tool'u cagirabilir. disallowedTools frontmatter ile runtime'da engellenir, prompt'a guvenilmez.

### CLI Dogrulama Araci

MCP server'inizi agent'siz test etmek icin DTO modulune CLI modu ekleyin:

```python
# ragip_{erp}_dto.py sonuna:
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--firma", required=True)
    parser.add_argument("--top", type=int, default=100)
    args = parser.parse_args()

    rapor = firma_raporu(args.firma, args.top)
    print(json.dumps(rapor, indent=2, ensure_ascii=False))
```

Kullanim: `python3 scripts/ragip_{erp}_dto.py --firma "ABC Dagitim"`

Bu, MCP ciktisini agent olmadan terminal'de dogrulamanizi saglar. Fatura sayisi, tutar toplamlari, durum dagilimi hizlica kontrol edilir.

---

## Checklist

### MCP Server
- [ ] ERP API baglantisi + auth
- [ ] Retry mekanizmasi (429 throttle + backoff)
- [ ] Pagination destegi (buyuk dataset'ler icin)

### DTO
- [ ] ERP → ADR-0007 normalizasyonu (yon, durum, tarih, tutar)
- [ ] Veri kalite uyarilari (_tespit_veri_uyarilari)

### Semantic Tool
- [ ] `firma_raporu` (veya benzeri) semantic tool — normalize cikti
- [ ] Ham tool'lar TUM agent'larda disallowedTools ile bloke

### Entegrasyon
- [ ] faturalar.jsonl'e yazma mekanizmasi (MCP tool veya import)
- [ ] validate_fatura() ile sema dogrulamasi
- [ ] .mcp.json yapilandirmasi
- [ ] CLI dogrulama araci (agent'siz test)
- [ ] Entegrasyon testi: gercek fatura → rapor akisi

---

## Referans Uygulama

D365 Sales MCP (gb_ragipaga repo):
- `scripts/ragip_dataverse_mcp.py` — FastMCP + MSAL auth, 7 tool
- `scripts/ragip_dataverse_dto.py` — InvoiceDTO, dto_to_faturalar bridge, 8 analiz senaryosu
- `docs/adr/007-mcp-normalization-layer.md` — Semantic tool zorunlulugu karari

Bu uygulama referans olarak kullanilabilir. Her ERP'nin DTO katmani farkli olacaktir.
