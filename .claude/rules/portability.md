# Tasinabilirlik

- Tum path'ler `git rev-parse --show-toplevel` ile cozumlenir
- Hardcoded path YASAK (test: TestPortability)
- ragip_rates.py standalone calisabilir (stdlib only, sifir bagimlilik)
- ragip_crud.py import path'i: sys.path.insert(0, os.path.join('$ROOT', 'scripts'))
- Runtime veri (data/RAGIP_AGA/, scripts/.ragip_cache/) otomatik olusturulur, gitignore'da
