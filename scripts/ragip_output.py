"""Ragip Aga cikti yonetimi — firma bazli klasor, manifest, meta block.

Tum agent'lar cikti kaydetmek icin bu modulu kullanir.
Standart isimlendirme, YAML frontmatter ve manifest zorlanir.

Kullanim (agent bash block'larinda):
    python3 -c "
    import sys; sys.path.insert(0, '$ROOT/scripts')
    from ragip_output import kaydet
    kaydet('arastirma', 'dis-veri', 'geneks_kimya', icerik)
    "
"""
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path


def get_root():
    """Git repo kokunu dondurur."""
    return subprocess.check_output(
        ['git', 'rev-parse', '--show-toplevel'],
        text=True, stderr=subprocess.DEVNULL
    ).strip()


def _slug(text):
    """Firma adini dosya sistemi uyumlu slug'a cevirir.

    'GÜVEN PRES DÖKÜM SAN. VE TİC. A.Ş' → 'guven_pres_dokum'
    'Geneks Kimya' → 'geneks_kimya'
    """
    # Turkce karakter donusumu
    tr_map = str.maketrans('çğıöşüÇĞİÖŞÜâîûêôÂÎÛÊÔ', 'cgiosuCGIOSUaiueoAIUEO')
    s = text.translate(tr_map).lower()
    # Sadece harf, rakam, bosluk
    s = re.sub(r'[^a-z0-9\s]', '', s)
    # Bosluklar → underscore, ardisik underscore temizle
    s = re.sub(r'\s+', '_', s.strip())
    s = re.sub(r'_+', '_', s)
    # SAN VE TIC gibi gereksiz son ekleri kes (3+ kelimeden sonra)
    parcalar = s.split('_')
    if len(parcalar) > 3:
        # 'san', 've', 'tic', 'as', 'ltd', 'sti' gibi ekleri kes
        ekler = {'san', 've', 'tic', 'as', 'ltd', 'sti', 'dis', 'ic', 'a', 'sanayi',
                 'ticaret', 'anonim', 'sirketi', 'limited', 'nakliyat'}
        while len(parcalar) > 2 and parcalar[-1] in ekler:
            parcalar.pop()
    return '_'.join(parcalar)


def _ay_dizini():
    """Ay bazli alt dizin: '2026-03'."""
    return datetime.now().strftime('%Y-%m')


def _timestamp():
    """Dosya adi icin timestamp: '20260321_143022'."""
    return datetime.now().strftime('%Y%m%d_%H%M%S')


def _manifest_path():
    """Manifest dosya yolu."""
    return Path(get_root()) / 'data' / 'RAGIP_AGA' / '.ciktilar_manifest.jsonl'


def _frontmatter(agent, skill, firma, firma_id=None, ekstra=None):
    """YAML frontmatter olusturur."""
    meta = {
        'agent': agent,
        'skill': skill,
        'firma': firma,
        'tarih': datetime.now().strftime('%Y-%m-%d %H:%M'),
    }
    if firma_id:
        meta['firma_id'] = firma_id
    if ekstra and isinstance(ekstra, dict):
        meta.update(ekstra)

    lines = ['---']
    for k, v in meta.items():
        lines.append(f'{k}: {v}')
    lines.append('---')
    lines.append('')
    return '\n'.join(lines)


def kaydet(agent, skill, firma, icerik, firma_id=None, ekstra_meta=None):
    """Cikti dosyasini standart formatta kaydeder.

    Args:
        agent: 'hesap', 'arastirma', 'hukuk', 'veri', 'aga'
        skill: 'rapor', 'dis-veri', 'degerlendirme', 'strateji', 'vade-farki' vs.
        firma: Firma adi (slug'a cevirilir)
        icerik: Markdown icerik (frontmatter otomatik eklenir)
        firma_id: Opsiyonel firma GUID/ID
        ekstra_meta: Opsiyonel ekstra frontmatter alanlari (dict)

    Returns:
        str: Kaydedilen dosyanin yolu (repo-relative)
    """
    root = Path(get_root())
    firma_slug = _slug(firma)
    ay = _ay_dizini()
    ts = _timestamp()

    # Dizin olustur: ciktilar/{firma_slug}/{ay}/
    dizin = root / 'data' / 'RAGIP_AGA' / 'ciktilar' / firma_slug / ay
    dizin.mkdir(parents=True, exist_ok=True)

    # Dosya adi
    dosya_adi = f'{ts}-{agent}-{skill}-{firma_slug}.md'
    dosya_yolu = dizin / dosya_adi

    # Frontmatter + icerik
    fm = _frontmatter(agent, skill, firma, firma_id, ekstra_meta)
    tam_icerik = fm + icerik

    # Atomic write
    tmp = dosya_yolu.with_suffix('.tmp')
    tmp.write_text(tam_icerik, encoding='utf-8')
    tmp.rename(dosya_yolu)

    # Manifest guncelle
    manifest_entry = {
        'firma': firma,
        'firma_slug': firma_slug,
        'firma_id': firma_id or '',
        'agent': agent,
        'skill': skill,
        'dosya': str(dosya_yolu.relative_to(root)),
        'tarih': datetime.now().isoformat(),
        'boyut': len(tam_icerik),
    }
    manifest = _manifest_path()
    manifest.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest, 'a', encoding='utf-8') as f:
        f.write(json.dumps(manifest_entry, ensure_ascii=False) + '\n')

    # Repo-relative yol dondur
    return str(dosya_yolu.relative_to(root))


def son_cikti(firma=None, agent=None, skill=None, limit=5):
    """Manifest'ten son ciktilari sorgular.

    Args:
        firma: Firma adi veya slug ile filtrele
        agent: Agent adi ile filtrele
        skill: Skill adi ile filtrele
        limit: Max sonuc sayisi

    Returns:
        list[dict]: Manifest kayitlari (yeniden eskiye)
    """
    manifest = _manifest_path()
    if not manifest.exists():
        return []

    kayitlar = []
    for line in manifest.read_text('utf-8').strip().split('\n'):
        if not line.strip():
            continue
        try:
            kayitlar.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    # Filtrele
    if firma:
        firma_lower = firma.lower()
        kayitlar = [k for k in kayitlar
                    if firma_lower in k.get('firma', '').lower()
                    or firma_lower in k.get('firma_slug', '').lower()]
    if agent:
        kayitlar = [k for k in kayitlar if k.get('agent') == agent]
    if skill:
        kayitlar = [k for k in kayitlar if k.get('skill') == skill]

    # Yeniden eskiye sirala
    kayitlar.sort(key=lambda k: k.get('tarih', ''), reverse=True)

    return kayitlar[:limit]


# ── Veri Tazeligi (t-factor) ──────────────────────────────────────────────────

# Veri tipi bazli yaslanma esikleri (gun)
_TAZELIK_ESIKLERI = {
    'hesap':     {'taze': 7, 'orta': 30, 'bayat': 90},    # Finansal veri hizli degisir
    'arastirma': {'taze': 14, 'orta': 60, 'bayat': 180},  # Dis kaynak orta hizda
    'hukuk':     {'taze': 30, 'orta': 90, 'bayat': 365},   # Mevzuat yavas degisir
    'veri':      {'taze': 7, 'orta': 30, 'bayat': 90},    # CRUD verisi hizli
    'aga':       {'taze': 7, 'orta': 30, 'bayat': 90},    # Sentez raporu
}

_TAZELIK_DEFAULT = {'taze': 14, 'orta': 60, 'bayat': 180}


def veri_tazeligi(firma=None, agent=None):
    """Firma/agent icin mevcut ciktilarin tazelik durumunu kontrol eder.

    Args:
        firma: Firma adi veya slug
        agent: Agent adi (hesap, arastirma, hukuk vs.)

    Returns:
        list[dict]: Her cikti icin tazelik bilgisi
            - dosya, agent, gun_once, durum (taze/orta/bayat), uyari
    """
    kayitlar = son_cikti(firma=firma, agent=agent, limit=50)
    if not kayitlar:
        return []

    bugun = datetime.now()
    sonuclar = []

    for k in kayitlar:
        tarih_str = k.get('tarih', '')
        if not tarih_str:
            continue
        try:
            tarih = datetime.fromisoformat(tarih_str)
        except ValueError:
            continue

        gun_once = (bugun - tarih).days
        ajan = k.get('agent', 'aga')
        esikler = _TAZELIK_ESIKLERI.get(ajan, _TAZELIK_DEFAULT)

        if gun_once <= esikler['taze']:
            durum = 'taze'
            uyari = None
        elif gun_once <= esikler['orta']:
            durum = 'orta'
            uyari = f"Bu veri {gun_once} gun once uretildi — guncelleme onerilir."
        else:
            durum = 'bayat'
            uyari = f"DIKKAT: Bu veri {gun_once} gun once uretildi — guncelligini yitirmis olabilir. Yeniden analiz onerilir."

        sonuclar.append({
            'dosya': k.get('dosya', ''),
            'agent': ajan,
            'skill': k.get('skill', ''),
            'firma': k.get('firma', ''),
            'gun_once': gun_once,
            'durum': durum,
            'uyari': uyari,
        })

    return sonuclar


def tazelik_ozeti(firma=None):
    """Firma icin tazelik ozet raporu (terminal ciktisi).

    Returns:
        str: Formatli tazelik raporu
    """
    sonuclar = veri_tazeligi(firma=firma)
    if not sonuclar:
        return "Bu firma icin onceki cikti bulunamadi — ilk analiz yapilmali."

    lines = [f"  Veri Tazeligi ({len(sonuclar)} cikti):"]
    for s in sonuclar:
        ikon = {'taze': 'OK', 'orta': '(!)', 'bayat': '!!'}[s['durum']]
        lines.append(f"    [{ikon}] {s['agent']}/{s['skill']} — {s['gun_once']} gun once")
        if s['uyari']:
            lines.append(f"         {s['uyari']}")
    return '\n'.join(lines)


def cikti_listele(firma=None):
    """Firma bazli cikti listesi (terminal ciktisi icin).

    Returns:
        str: Formatli cikti listesi
    """
    kayitlar = son_cikti(firma=firma, limit=20)
    if not kayitlar:
        return "Cikti bulunamadi."

    lines = []
    for k in kayitlar:
        tarih = k.get('tarih', '')[:16].replace('T', ' ')
        lines.append(f"  {tarih}  {k.get('agent','?')}/{k.get('skill','?')}  {k.get('firma','?')}")
        lines.append(f"    → {k.get('dosya','?')}")
    return '\n'.join(lines)
