# MCP Adaptor Entegrasyon Rehberi

Ragip Aga Kit'e yeni bir ERP/CRM veri kaynagi baglamak icin MCP adaptor yazma rehberi.

**Referans:** ADR-0004 (Kit vs MCP Ayrimi), ADR-0007 (Standart Fatura Semasi)

---

## Mimari

```
[ERP/CRM API] → MCP Server (auth + query) → DTO (normalizasyon) → faturalar.jsonl (ADR-0007) → Kit
```

Kit hesaplama motorlari yalnizca `faturalar.jsonl` semasini okur. ERP'yi bilmez.
MCP adaptoru ERP'den veriyi ceker, normalize eder, bu semaya yazar.

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
    # ERP API cagrisi
    ham_veri = erp_api.get_invoices(firma_id=firma_id, status=durum)
    # DTO ile normalize et
    return [dto_to_fatura(item) for item in ham_veri]
```

**Gerekli tool'lar:**
- `fatura_listele` — Fatura sorgulama (firma_id, durum, tarih araligi filtresi)
- `firma_listele` — Firma/musteri sorgulama
- `fatura_senkron` — faturalar.jsonl'e toplu yazma (opsiyonel, import alternatifi)

**Opsiyonel tool'lar:**
- `firma_raporu` — Tek firma icin semantik ozet (aging + odeme davranisi + risk)
- `odeme_kaydet` — Odeme bilgisi guncelleme

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

## Adim 3: Validasyon

Kit `validate_fatura()` fonksiyonu ile MCP'den gelen verinin ADR-0007'ye uygunlugunu dogrular.

```python
from ragip_crud import validate_faturalar, load_jsonl, data_path

# MCP'den gelen veriyi yukle
faturalar = load_jsonl(data_path('faturalar.jsonl'))

# Dogrula
gecerli, hatali = validate_faturalar(faturalar)
if hatali:
    print(f"{len(hatali)} hatali kayit atlanıyor")
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

## Adim 4: Hedef Repo Yapilandirmasi

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

### ragip-aga.md ozellestirmesi

MCP tool'larini disallowedTools'a ekle (orchestrator dogrudan MCP cagirmasin):

```yaml
disallowedTools:
  - WebSearch
  - WebFetch
  - mcp__ragip-{erp}__fatura_listele
  - mcp__ragip-{erp}__firma_listele
```

---

## Checklist

- [ ] MCP server: ERP API baglantisi + auth
- [ ] DTO: ERP → ADR-0007 normalizasyonu
- [ ] faturalar.jsonl'e yazma mekanizmasi (MCP tool veya import)
- [ ] validate_fatura() ile sema dogrulamasi
- [ ] .mcp.json yapilandirmasi
- [ ] disallowedTools guncelleme (ragip-aga.md)
- [ ] Entegrasyon testi: gercek fatura → rapor akisi

---

## Referans Uygulama

D365 Sales MCP (gb_ragipaga repo):
- `scripts/ragip_dataverse_mcp.py` — FastMCP + MSAL auth
- `scripts/ragip_dataverse_dto.py` — InvoiceDTO, dto_to_faturalar bridge
- 7 MCP tool (query_records, firma_raporu, vb.)

Bu uygulama referans olarak kullanilabilir. Her ERP'nin DTO katmani farkli olacaktir.
