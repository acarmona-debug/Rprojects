# Plan: automatización de compras con **un solo script** (sin macros)

## Respuesta corta
Sí: **se puede hacer casi todo en un solo script**.

La parte humana mínima sería:
1. Cargar archivos (requisa, explosión, comparativa base, PDFs de proveedores).
2. Revisar/ajustar datos detectados de proveedor.
3. Marcar checkboxes `P1/P2/P3` por partida.
4. Confirmar y generar salidas.

Con eso, el script puede hacer automáticamente:
- Llenado de comparativa.
- Totales por proveedor según checkboxes.
- Cálculo de ahorro vs presupuesto.
- Generación de 1 orden de compra por proveedor elegido.
- Actualización de estatus de requisa.

---

## Objetivo de simplicidad
Evitar macros y mantener una experiencia intuitiva.

### Propuesta de UX
- **App local de 1 clic** (doble clic / comando único).
- Pantalla única con 4 bloques:
  1) Carga de archivos.
  2) Vista de partidas y precios (auto extraídos).
  3) Selección de proveedor por fila con `P1/P2/P3`.
  4) Botón `Generar documentos`.

---

## Arquitectura mínima recomendada

### Opción A (más simple para usuario final)
- Script Python + interfaz web local (Streamlit).
- No requiere Excel con macros.
- Resultado: archivos `.xlsx` listos para usar.

### Opción B (aún más ligera visualmente)
- Script Python por consola con menús básicos.
- Menos intuitivo para operación diaria.

**Recomendación:** Opción A.

---

## Flujo funcional en un solo script
1. Leer plantilla `FORMATO DE COMPARATIVA.xlsx`.
2. Leer requisa y explosión de insumos para catálogo base de partidas.
3. Intentar extraer cotizaciones de PDFs (OCR/parser).
4. Cargar tabla unificada en comparativa.
5. Agregar columnas de selección `P1`, `P2`, `P3`.
6. Calcular totales por proveedor según selección.
7. Al confirmar, generar:
   - `OC_proveedor_A.xlsx`
   - `OC_proveedor_B.xlsx`
   - `OC_proveedor_C.xlsx`
   (solo para proveedores con partidas seleccionadas)
8. Actualizar `FORMATO ESTATUS DE REQUISA.xlsx` con datos de OC + requisa.

---

## Regla clave de negocio (checkboxes)
- Por cada partida, se marca un proveedor (`P1` o `P2` o `P3`).
- Validación sugerida: solo 1 checkbox por partida.
- Si no hay selección, la partida queda como pendiente y no se manda a OC.

---

## Qué sí requiere intervención humana (mínima)
- Validar datos que el PDF no entregue limpio.
- Elegir proveedor por partida (checkbox).

Todo lo demás puede automatizarse.

---

## Entregables esperados del script
- `Comparativa_Completada.xlsx`
- `OC_<Proveedor>.xlsx` (N archivos)
- `Estatus_Requisa_Actualizado.xlsx`
- Log de validaciones/errores para auditoría.

---

## Siguiente paso recomendado
Construir un **MVP** con tus archivos actuales para probar en caso real:
1. Carga de archivos.
2. Tabla con checkboxes `P1/P2/P3`.
3. Generación automática de OCs y estatus.

Si el MVP funciona, después se mejora la interfaz visual.
