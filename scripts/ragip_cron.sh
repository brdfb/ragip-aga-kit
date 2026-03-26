#!/usr/bin/env bash
# ragip_cron.sh — zamanlanmis gorev yonetimi
#
# Kullanim:
#   bash scripts/ragip_cron.sh run <gorev>     Gorevi calistir (rates, temizle)
#   bash scripts/ragip_cron.sh --setup         Crontab'a ekle
#   bash scripts/ragip_cron.sh --status        Mevcut durumu goster
#   bash scripts/ragip_cron.sh --remove        Crontab'dan kaldir
#   bash scripts/ragip_cron.sh --list          Kayitli gorevleri listele
#
# Cron ortami icin tasarlandi: PATH/venv/env izolasyonu saglar.
# Loglama: data/RAGIP_AGA/logs/cron_YYYYMMDD.log

set -euo pipefail

CRON_TAG="# Ragip Aga cron"

# --- Root tespit ---
resolve_root() {
  if [[ -n "${RAGIP_ROOT:-}" ]]; then
    echo "$RAGIP_ROOT"
  elif command -v git &>/dev/null; then
    git rev-parse --show-toplevel 2>/dev/null || echo "."
  else
    echo "."
  fi
}

ROOT=$(resolve_root)

# --- Python tespit ---
resolve_python() {
  local venv_py="$ROOT/.ragip-venv/bin/python3"
  if [[ -x "$venv_py" ]]; then
    echo "$venv_py"
  else
    echo "python3"
  fi
}

PYTHON=$(resolve_python)

# --- Log altyapisi ---
LOG_DIR="$ROOT/data/RAGIP_AGA/logs"

log_msg() {
  local msg="$1"
  mkdir -p "$LOG_DIR"
  local logfile="$LOG_DIR/cron_$(date +%Y%m%d).log"
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $msg" >> "$logfile"
}

# --- .env yukleme ---
load_env() {
  local envfile="$ROOT/.env"
  if [[ -f "$envfile" ]]; then
    # Sadece KEY=VALUE satirlarini export et (yorumlar ve bos satirlar atla)
    while IFS='=' read -r key value; do
      # Bos satir, yorum, veya key'siz satir atla
      [[ -z "$key" || "$key" =~ ^[[:space:]]*# ]] && continue
      # Bosluk temizle
      key=$(echo "$key" | tr -d '[:space:]')
      # Degeri tirnaklardan temizle
      value="${value%\"}"
      value="${value#\"}"
      value="${value%\'}"
      value="${value#\'}"
      export "$key=$value" 2>/dev/null || true
    done < "$envfile"
  fi
}

# --- Gorev tanimi ---
declare -A GOREVLER=(
  [rates]="TCMB oranlarini yenile"
  [temizle]="Ciktilar dizinini temizle"
)

run_task() {
  local task="$1"
  local exit_code=0
  local start_ts
  start_ts=$(date +%s)

  log_msg "BASLADI: $task"

  case "$task" in
    rates)
      "$PYTHON" "$ROOT/scripts/ragip_rates.py" --refresh 2>&1 || exit_code=$?
      ;;
    temizle)
      bash "$ROOT/scripts/ragip_temizle.sh" 2>&1 || exit_code=$?
      ;;
    *)
      echo "HATA: Bilinmeyen gorev: $task" >&2
      echo "Gecerli gorevler: ${!GOREVLER[*]}" >&2
      log_msg "HATA: Bilinmeyen gorev: $task"
      return 1
      ;;
  esac

  local end_ts
  end_ts=$(date +%s)
  local sure=$((end_ts - start_ts))

  if [[ $exit_code -eq 0 ]]; then
    log_msg "TAMAMLANDI: $task (${sure}s)"
  else
    log_msg "BASARISIZ: $task (exit=$exit_code, ${sure}s)"
  fi

  return $exit_code
}

# --- Crontab yonetimi ---
generate_cron_lines() {
  local root="$1"
  cat <<EOF
$CRON_TAG — v$(cat "$root/VERSION" 2>/dev/null || echo "?")
RAGIP_ROOT=$root
0 8 * * 1-5  bash \$RAGIP_ROOT/scripts/ragip_cron.sh run rates $CRON_TAG
0 3 * * 0    bash \$RAGIP_ROOT/scripts/ragip_cron.sh run temizle $CRON_TAG
EOF
}

setup_cron() {
  # Oncelikle mevcut Ragip girisleri temizle
  remove_cron 2>/dev/null || true

  local new_lines
  new_lines=$(generate_cron_lines "$ROOT")

  # Mevcut crontab + yeni satirlar
  (crontab -l 2>/dev/null || true; echo "$new_lines") | crontab -

  echo "Crontab guncellendi."
  echo ""
  echo "Eklenen gorevler:"
  echo "  rates   — Hafta ici 08:00 (TCMB oranlarini yenile)"
  echo "  temizle — Pazar 03:00 (ciktilar temizleme)"
  echo ""

  # WSL2 cron servisi kontrolu
  if ! pgrep -x cron &>/dev/null && ! pgrep -x crond &>/dev/null; then
    echo "UYARI: cron servisi calismiyir!"
    echo "  Baslatmak icin:  sudo service cron start"
    echo ""
    echo "  Kalici hale getirmek icin /etc/wsl.conf'a ekleyin:"
    echo "  [boot]"
    echo "  command = service cron start"
  fi
}

remove_cron() {
  local current
  current=$(crontab -l 2>/dev/null || true)

  if [[ -z "$current" ]]; then
    echo "Crontab bos — silinecek bir sey yok."
    return 0
  fi

  local filtered
  filtered=$(echo "$current" | grep -v "$CRON_TAG" | grep -v "^RAGIP_ROOT=" || true)

  # Bos satirlari temizle
  filtered=$(echo "$filtered" | sed '/^$/d' || true)

  if [[ -z "$filtered" ]]; then
    crontab -r 2>/dev/null || true
  else
    echo "$filtered" | crontab -
  fi

  echo "Ragip Aga cron girisleri kaldirildi."
}

show_status() {
  echo "=== Ragip Aga Cron Durumu ==="
  echo ""

  # Crontab girisleri
  local entries
  entries=$(crontab -l 2>/dev/null | grep "$CRON_TAG" 2>/dev/null || true)
  if [[ -n "$entries" ]]; then
    echo "Crontab girisleri:"
    echo "$entries" | while IFS= read -r line; do
      echo "  $line"
    done
  else
    echo "Crontab girisleri: YOK"
  fi
  echo ""

  # Cron servisi
  if pgrep -x cron &>/dev/null || pgrep -x crond &>/dev/null; then
    echo "Cron servisi: CALISIYOR"
  else
    echo "Cron servisi: DURMUS"
  fi
  echo ""

  # Son loglar
  if [[ -d "$LOG_DIR" ]]; then
    local latest_log
    latest_log=$(ls -t "$LOG_DIR"/cron_*.log 2>/dev/null | head -1 || true)
    if [[ -n "$latest_log" ]]; then
      echo "Son log ($latest_log):"
      tail -5 "$latest_log" | while IFS= read -r line; do
        echo "  $line"
      done
    else
      echo "Log dosyasi: YOK (henuz calistirilmamis)"
    fi
  else
    echo "Log dizini: YOK (henuz calistirilmamis)"
  fi
}

list_tasks() {
  echo "Kayitli gorevler:"
  for task in "${!GOREVLER[@]}"; do
    echo "  $task — ${GOREVLER[$task]}"
  done
}

# --- Ortam yukleme (run komutu icin) ---
prepare_env() {
  load_env
  # PATH'e standart dizinleri ekle (cron ortaminda eksik olabilir)
  export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"
}

# --- Ana giris ---
main() {
  if [[ $# -eq 0 ]]; then
    echo "Kullanim: ragip_cron.sh <komut>"
    echo ""
    echo "Komutlar:"
    echo "  run <gorev>  Gorevi calistir (rates, temizle)"
    echo "  --setup      Crontab'a ekle"
    echo "  --status     Durumu goster"
    echo "  --remove     Crontab'dan kaldir"
    echo "  --list       Gorevleri listele"
    return 1
  fi

  case "$1" in
    run)
      if [[ $# -lt 2 ]]; then
        echo "HATA: Gorev adi belirtilmedi." >&2
        echo "Kullanim: ragip_cron.sh run <gorev>" >&2
        list_tasks >&2
        return 1
      fi
      prepare_env
      run_task "$2"
      ;;
    --setup)
      setup_cron
      ;;
    --status)
      show_status
      ;;
    --remove)
      remove_cron
      ;;
    --list)
      list_tasks
      ;;
    *)
      echo "HATA: Bilinmeyen komut: $1" >&2
      main
      ;;
  esac
}

main "$@"
