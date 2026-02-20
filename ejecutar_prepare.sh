#!/usr/bin/env bash
set -euo pipefail

python3 compras_mvp.py prepare \
  --base-dir . \
  --requisa "FORMATO DE REQUISA.xlsx" \
  --explosion "EXP INSUMOS (EJEMPLO).xlsx" \
  --output-dir salidas

echo "Listo: revisa salidas/seleccion_proveedores.csv"
