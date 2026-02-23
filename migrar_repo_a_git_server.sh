#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "Uso: $0 <repo_origen_url> <repo_destino_url> [ruta_temporal]" >&2
  echo "Ejemplo: $0 https://github.com/acarmona-debug/CursorCompras.git git@gitserver:equipo/CursorCompras.git" >&2
  exit 1
fi

REPO_ORIGEN="$1"
REPO_DESTINO="$2"
TMP_DIR="${3:-$(mktemp -d)}"
CLEANUP=0

if [[ $# -lt 3 ]]; then
  CLEANUP=1
fi

cleanup() {
  if [[ "$CLEANUP" -eq 1 && -d "$TMP_DIR" ]]; then
    rm -rf "$TMP_DIR"
  fi
}
trap cleanup EXIT

if [[ -d "$TMP_DIR/.git" || -n "$(find "$TMP_DIR" -mindepth 1 -maxdepth 1 2>/dev/null || true)" ]]; then
  echo "Error: la carpeta temporal debe estar vacía: $TMP_DIR" >&2
  exit 1
fi

echo "[1/3] Clonando en modo mirror desde: $REPO_ORIGEN"
git clone --mirror "$REPO_ORIGEN" "$TMP_DIR/repo.mirror"

cd "$TMP_DIR/repo.mirror"

echo "[2/3] Configurando remoto destino: $REPO_DESTINO"
git remote set-url --push origin "$REPO_DESTINO"

echo "[3/3] Enviando TODAS las ramas, tags y refs al git server"
git push --mirror

echo "✅ Migración terminada correctamente"
