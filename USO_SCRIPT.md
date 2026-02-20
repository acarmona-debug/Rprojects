# Cómo ejecutarlo en tu laptop (SIN Git)

## 0) Qué vas a hacer
Solo 3 cosas:
1. Descargar un ZIP
2. Abrir una carpeta
3. Dar doble clic a un archivo

---

## 1) Descarga los archivos (sin usar Git)
1. Entra a tu repo en GitHub.
2. Clic en botón verde **Code**.
3. Clic en **Download ZIP**.
4. Descomprime el ZIP en tu laptop (por ejemplo en `Escritorio\Rprojects`).

---

## 2) Requisitos mínimos
- Tener Python instalado.
- En Windows, abre `cmd` y ejecuta:

```bat
python --version
```

Si sale versión (ej. `Python 3.11.x`), ya estás listo.

---

## 3) Ejecución fácil (1 archivo)
Dentro de la carpeta descomprimida:

### Windows
- Doble clic en: **`EJECUTAR_TODO.cmd`**

Este archivo:
1. corre `prepare`,
2. te pausa para que edites Excel,
3. corre `generate`.

### Linux/macOS
```bash
./EJECUTAR_TODO.sh
```

---

## 4) Paso humano (obligatorio)
Cuando el script te lo pida:
1. abre `salidas/seleccion_proveedores.csv` en Excel,
2. llena `precio_p1`, `precio_p2`, `precio_p3`,
3. marca `p1` o `p2` o `p3` con `x` por cada fila,
4. guarda el archivo.

Luego regresas al script para continuar.

---

## 5) Resultado final
Se genera en:
- `salidas/generado/OC_P1.csv`
- `salidas/generado/OC_P2.csv`
- `salidas/generado/OC_P3.csv`
- `salidas/generado/Estatus_Requisa_Actualizado.csv`

---

## Si algo falla
- Si dice que no encuentra requisa/explosión, verifica que en la misma carpeta existan:
  - `FORMATO DE REQUISA.xlsx`
  - `EXP INSUMOS (EJEMPLO).xlsx`
- Si no abre con doble clic, abre `cmd` en esa carpeta y ejecuta:

```bat
EJECUTAR_TODO.cmd
```
