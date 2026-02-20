@echo off
setlocal

REM Ejecuta todo el flujo con mensajes simples para usuario final.

if not exist "compras_mvp.py" (
  echo ERROR: no encuentro compras_mvp.py en esta carpeta.
  echo Asegurate de descomprimir todo el ZIP del proyecto y abrir esta misma carpeta.
  pause
  exit /b 2
)

echo.
echo [1/3] Preparando archivos...
python compras_mvp.py prepare --base-dir . --requisa "FORMATO DE REQUISA.xlsx" --explosion "EXP INSUMOS (EJEMPLO).xlsx" --output-dir salidas
if errorlevel 1 (
  echo.
  echo ERROR en prepare. Revisa que existan:
  echo - FORMATO DE REQUISA.xlsx
  echo - EXP INSUMOS (EJEMPLO).xlsx
  pause
  exit /b 2
)

echo.
echo [2/3] Ya se creo: salidas\seleccion_proveedores.csv
echo Abre ese archivo en Excel, llena precios y marca p1/p2/p3 con x.
echo Guarda el archivo y REGRESA aqui.
pause

echo.
echo [3/3] Generando ordenes y estatus...
python compras_mvp.py generate --selection-csv "salidas/seleccion_proveedores.csv" --output-dir "salidas/generado"
if errorlevel 1 (
  echo ERROR en generate.
  pause
  exit /b 2
)

echo.
echo LISTO. Archivos finales en: salidas\generado\
pause
