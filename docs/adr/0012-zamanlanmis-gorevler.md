# ADR-0012: Zamanlanmis Gorevler (Cron)

**Tarih:** 2026-03-27
**Durum:** Kabul edildi
**Karar vericiler:** Kit gelistirici

## Baglam

Kit'in iki gorevinin periyodik calistirilmasi gerekiyor:
- TCMB oran guncelleme (`ragip_rates.py --refresh`) — cache yenilemesi
- Ciktilar temizleme (`ragip_temizle.sh`) — disk alani yonetimi

Claude Code uc zamanlanmis gorev secenegi sunuyor:
1. **`/loop`** — session bazli, max 3 gun, session kapaninca biter
2. **Desktop Tasks** — native Desktop app gerekli, WSL2'de calismaz
3. **`/schedule` (Cloud)** — 7/24 ama lokal dosya/MCP erisimi yok

## Karar

**WSL2 sistem crontab** ile zamanlanmis gorevler yonetilecek.

Tek entry point: `scripts/ragip_cron.sh` — cron ortaminda PATH, venv, .env izolasyonu saglar.

## Gerekce

| Secenek | Red nedeni |
|---------|-----------|
| Desktop Tasks | WSL2 ortaminda native Desktop app yok, VS Code extension kullnilyor |
| Cloud /schedule | Lokal FastMCP sunucularina (D365, RAG) erisamez, fresh git clone yapar |
| /loop | Gecici (max 3 gun), session kapaninca biter, kalici degil |
| systemd timers | Crontab daha basit, WSL2/Linux arasi tasinabilir |

Crontab avantajlari:
- WSL2'de calisiyor (cron servisi aktif edilmeli)
- Dakika bazinda esneklik (Cloud min 1 saat)
- Lokal dosya + .env + venv erisimi
- 50 yillik kanitlanmis teknoloji

## Tasarim

```
ragip_cron.sh run <gorev>     # Gorevi calistir
ragip_cron.sh --setup         # Crontab'a ekle (idempotent)
ragip_cron.sh --status        # Durumu goster
ragip_cron.sh --remove        # Crontab'dan kaldir
ragip_cron.sh --list          # Kayitli gorevleri listele
```

### Ortam izolasyonu
- `RAGIP_ROOT` env var (crontab'a baked-in) — git'e bagimsiz
- `.ragip-venv/bin/python3` tespit (varsa venv, yoksa sistem python3)
- `.env` dosyasi parse (TCMB_API_KEY, COLLECTAPI_KEY icin)
- PATH genisletme (cron minimal PATH ile calisir)

### Loglama
- `data/RAGIP_AGA/logs/cron_YYYYMMDD.log` — gunluk rotasyon
- Her calisma: timestamp, gorev adi, sure, exit code

### Crontab yapisi
```
# Ragip Aga cron — vX.Y.Z
RAGIP_ROOT=/path/to/workspace
0 8 * * 1-5  bash $RAGIP_ROOT/scripts/ragip_cron.sh run rates    # Hafta ici 08:00
0 3 * * 0    bash $RAGIP_ROOT/scripts/ragip_cron.sh run temizle  # Pazar 03:00
```

## WSL2 cron servisi

WSL2'de cron servisi varsayilan olarak kapali. Aktif etmek icin:

```bash
sudo service cron start

# Kalici hale getirmek icin /etc/wsl.conf:
[boot]
command = service cron start
```

`ragip_cron.sh --setup` bu durumu tespit eder ve uyari verir.

## Sonuclar

- Yeni dosya: `scripts/ragip_cron.sh`
- Yeni test: `tests/test_ragip_cron.py` (34 test)
- `install.sh` guncellendi (kopyalama + manifest)
- Claude Code `/loop` session ici gecici isler icin ayrica kullanilabilir
- Cloud `/schedule` git repo bazli isler icin (dependency audit vb.) ayrica kullanilabilir
