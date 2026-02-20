@echo off
python compras_mvp.py generate --selection-csv "salidas/seleccion_proveedores.csv" --output-dir "salidas/generado"
if errorlevel 1 exit /b %errorlevel%
echo Listo: revisa salidas\generado\
