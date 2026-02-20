#!/usr/bin/env bash
set -euo pipefail

python3 compras_mvp.py generate \
  --selection-csv "salidas/seleccion_proveedores.csv" \
  --output-dir "salidas/generado"

echo "Listo: revisa salidas/generado/"
