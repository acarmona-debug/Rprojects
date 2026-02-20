#!/usr/bin/env bash
set -euo pipefail

echo "[1/3] Preparando archivos..."
python3 compras_mvp.py prepare \
  --base-dir . \
  --requisa "FORMATO DE REQUISA.xlsx" \
  --explosion "EXP INSUMOS (EJEMPLO).xlsx" \
  --output-dir salidas

echo
echo "[2/3] Abre salidas/seleccion_proveedores.csv en Excel"
echo "Llena precios y marca p1/p2/p3 con x, guarda y vuelve aqui."
read -r -p "Presiona ENTER para continuar cuando hayas guardado... " _

echo "[3/3] Generando ordenes y estatus..."
python3 compras_mvp.py generate \
  --selection-csv salidas/seleccion_proveedores.csv \
  --output-dir salidas/generado

echo "Listo. Resultado en salidas/generado/"
