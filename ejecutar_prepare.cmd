@echo off
python compras_mvp.py prepare --base-dir . --requisa "FORMATO DE REQUISA.xlsx" --explosion "EXP INSUMOS (EJEMPLO).xlsx" --output-dir salidas
if errorlevel 1 exit /b %errorlevel%
echo Listo: revisa salidas\seleccion_proveedores.csv
