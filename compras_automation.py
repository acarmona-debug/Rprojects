#!/usr/bin/env python3
"""Automatiza el flujo base de compras sin macros ni dependencias externas.

Flujo sugerido:
1) prepare  -> genera archivos CSV de trabajo desde formatos Excel/PDF.
2) el usuario captura precios y marca P1/P2/P3 en seleccion_proveedores.csv.
3) generate -> produce OCs por proveedor y estatus de requisa.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
REL_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"


@dataclass
class Partida:
    clave: str
    descripcion: str
    unidad: str
    cantidad: float
    precio_insumos: float
    total_insumos: float


def safe_float(value: str) -> float:
    if value is None:
        return 0.0
    txt = str(value).strip().replace(",", "")
    if not txt:
        return 0.0
    try:
        return float(txt)
    except ValueError:
        return 0.0


def load_xlsx_sheet_rows(xlsx_path: Path, sheet_name: Optional[str] = None) -> List[Dict[int, str]]:
    """Lee un .xlsx con stdlib y devuelve filas como {col_idx: valor} para la hoja elegida."""
    with zipfile.ZipFile(xlsx_path) as zf:
        wb = ET.fromstring(zf.read("xl/workbook.xml"))
        rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
        rel_map = {r.attrib["Id"]: r.attrib["Target"] for r in rels}

        sheets = []
        for s in wb.find(f"{NS}sheets"):
            name = s.attrib.get("name", "")
            rid = s.attrib.get(REL_NS)
            target = rel_map.get(rid, "")
            sheets.append((name, target))

        if not sheets:
            return []

        chosen = None
        if sheet_name:
            for n, t in sheets:
                if n.strip().lower() == sheet_name.strip().lower():
                    chosen = (n, t)
                    break
        if not chosen:
            chosen = sheets[0]

        shared_strings: List[str] = []
        if "xl/sharedStrings.xml" in zf.namelist():
            ss = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            for si in ss.findall(f"{NS}si"):
                text = "".join(t.text or "" for t in si.iter(f"{NS}t"))
                shared_strings.append(text)

        target = chosen[1].replace("\\", "/")
        sheet_xml = target if target.startswith("xl/") else f"xl/{target}"
        root = ET.fromstring(zf.read(sheet_xml))

        rows: List[Dict[int, str]] = []
        for row in root.findall(f".//{NS}sheetData/{NS}row"):
            out: Dict[int, str] = {}
            for c in row.findall(f"{NS}c"):
                ref = c.attrib.get("r", "")
                m = re.match(r"([A-Z]+)", ref)
                if not m:
                    continue
                col = 0
                for ch in m.group(1):
                    col = col * 26 + (ord(ch) - 64)
                t = c.attrib.get("t")
                v = c.find(f"{NS}v")
                if v is None or v.text is None:
                    continue
                value = v.text
                if t == "s" and value.isdigit():
                    idx = int(value)
                    value = shared_strings[idx] if idx < len(shared_strings) else value
                out[col] = value.strip()
            rows.append(out)
        return rows


def detect_requisa_meta(requisa_xlsx: Path) -> Dict[str, str]:
    rows = load_xlsx_sheet_rows(requisa_xlsx)
    meta = {
        "obra": "",
        "numero_requisa": "",
        "fecha_solicitud": "",
        "solicita": "",
        "especialidad": "",
        "descripcion_trabajo": "",
    }
    for row in rows:
        joined = " | ".join(row.values()).upper()
        if "OBRA:" in joined and not meta["obra"]:
            meta["obra"] = row.get(3, "") or row.get(2, "")
        if "NUMERO REQUISICION" in joined and not meta["numero_requisa"]:
            meta["numero_requisa"] = row.get(6, "") or row.get(5, "")
        if "FECHA SOLICITUD" in joined and not meta["fecha_solicitud"]:
            meta["fecha_solicitud"] = row.get(6, "") or row.get(5, "")
        if "SOLICITA:" in joined and not meta["solicita"]:
            meta["solicita"] = row.get(3, "") or row.get(2, "")
        if "ESPECIALIDAD" in joined and not meta["especialidad"]:
            meta["especialidad"] = row.get(7, "") or row.get(6, "")
        if "DESCRIPCION DEL TRABAJO" in joined and not meta["descripcion_trabajo"]:
            meta["descripcion_trabajo"] = row.get(3, "") or row.get(2, "")
    return meta


def extract_partidas(explosion_xlsx: Path) -> List[Partida]:
    rows = load_xlsx_sheet_rows(explosion_xlsx)
    partidas: List[Partida] = []
    for row in rows:
        clave = row.get(1, "")
        descripcion = row.get(2, "")
        unidad = row.get(3, "")
        cantidad = safe_float(row.get(4, "0"))
        precio = safe_float(row.get(5, "0"))
        total = safe_float(row.get(6, "0"))
        if clave.upper() == "CLAVE" or not clave or not descripcion:
            continue
        partidas.append(
            Partida(
                clave=clave,
                descripcion=descripcion,
                unidad=unidad,
                cantidad=cantidad,
                precio_insumos=precio,
                total_insumos=total,
            )
        )
    return partidas


def discover_supplier_pdfs(base_dir: Path) -> List[Tuple[str, str]]:
    out = []
    for pdf in sorted(base_dir.glob("*.pdf")):
        stem = pdf.stem
        proveedor = stem
        up = stem.upper()
        if "DELFIN" in up:
            proveedor = "FERRETERIAS EL DELFIN"
        elif "EMMSA" in up:
            proveedor = "EMMSA"
        elif "INCO" in up:
            proveedor = "INCO"
        out.append((pdf.name, proveedor))
    return out


def write_csv(path: Path, headers: List[str], rows: Iterable[Iterable[object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        wr = csv.writer(f)
        wr.writerow(headers)
        for r in rows:
            wr.writerow(r)


def cmd_prepare(args: argparse.Namespace) -> int:
    base = Path(args.base_dir)
    out = Path(args.output_dir)

    req = Path(args.requisa)
    exp = Path(args.explosion)

    if not req.exists():
        print(f"ERROR: no existe el archivo de requisa: {req}")
        return 2
    if not exp.exists():
        print(f"ERROR: no existe el archivo de explosión: {exp}")
        return 2

    meta = detect_requisa_meta(req)
    partidas = extract_partidas(exp)
    proveedores = discover_supplier_pdfs(base)

    write_csv(
        out / "meta_requisa.csv",
        ["campo", "valor"],
        [[k, v] for k, v in meta.items()],
    )

    write_csv(
        out / "proveedores_detectados.csv",
        ["archivo_pdf", "proveedor_detectado"],
        proveedores,
    )

    rows = []
    for p in partidas:
        rows.append(
            [
                p.clave,
                p.descripcion,
                p.unidad,
                p.cantidad,
                p.precio_insumos,
                p.total_insumos,
                "",  # precio_p1
                "",  # precio_p2
                "",  # precio_p3
                "",  # p1
                "",  # p2
                "",  # p3
                "",  # proveedor_elegido
                "",  # total_compra
            ]
        )

    write_csv(
        out / "seleccion_proveedores.csv",
        [
            "clave",
            "descripcion",
            "unidad",
            "cantidad",
            "precio_insumos",
            "total_insumos",
            "precio_p1",
            "precio_p2",
            "precio_p3",
            "p1",
            "p2",
            "p3",
            "proveedor_elegido",
            "total_compra",
        ],
        rows,
    )

    print(f"OK: archivos de preparación generados en {out}")
    return 0


def pick_supplier(row: Dict[str, str]) -> str:
    for idx, key in enumerate(("p1", "p2", "p3"), start=1):
        val = (row.get(key) or "").strip().lower()
        if val in {"1", "x", "si", "sí", "true", "ok"}:
            return f"P{idx}"
    chosen = (row.get("proveedor_elegido") or "").strip().upper()
    return chosen


def cmd_generate(args: argparse.Namespace) -> int:
    inp = Path(args.selection_csv)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    if not inp.exists():
        print(f"ERROR: no existe el archivo de selección: {inp}")
        return 2

    with inp.open("r", encoding="utf-8-sig", newline="") as f:
        data = list(csv.DictReader(f))

    grouped: Dict[str, List[Dict[str, str]]] = {"P1": [], "P2": [], "P3": []}
    total_presupuesto = 0.0
    total_compra_global = 0.0

    for row in data:
        total_presupuesto += safe_float(row.get("total_insumos", "0"))
        selected = pick_supplier(row)
        if selected not in grouped:
            continue
        price_key = f"precio_{selected.lower()}"
        precio = safe_float(row.get(price_key, "0"))
        cantidad = safe_float(row.get("cantidad", "0"))
        total_compra = round(precio * cantidad, 2)
        row["total_compra"] = f"{total_compra:.2f}"
        grouped[selected].append(row)
        total_compra_global += total_compra

    # salida de OCs por proveedor
    fecha = dt.date.today().isoformat()
    for supplier, rows in grouped.items():
        if not rows:
            continue
        oc_path = out / f"OC_{supplier}.csv"
        write_csv(
            oc_path,
            [
                "fecha",
                "proveedor",
                "clave",
                "descripcion",
                "unidad",
                "cantidad",
                "precio_unitario",
                "total",
            ],
            [
                [
                    fecha,
                    supplier,
                    r.get("clave", ""),
                    r.get("descripcion", ""),
                    r.get("unidad", ""),
                    r.get("cantidad", ""),
                    r.get(f"precio_{supplier.lower()}", ""),
                    r.get("total_compra", ""),
                ]
                for r in rows
            ],
        )

    # estatus
    ahorro = round(total_presupuesto - total_compra_global, 2)
    estatus_path = out / "Estatus_Requisa_Actualizado.csv"
    write_csv(
        estatus_path,
        ["fecha", "total_explosion", "total_compra", "ahorro", "partidas_con_proveedor"],
        [[fecha, f"{total_presupuesto:.2f}", f"{total_compra_global:.2f}", f"{ahorro:.2f}", sum(len(v) for v in grouped.values())]],
    )

    # resumen
    print(f"OK: generado en {out}")
    print(f"Total explosión: {total_presupuesto:.2f}")
    print(f"Total compra:    {total_compra_global:.2f}")
    print(f"Ahorro:          {ahorro:.2f}")
    for k, v in grouped.items():
        print(f"  {k}: {len(v)} partidas")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Automatización de compras sin macros (MVP).")
    sub = p.add_subparsers(dest="cmd", required=True)

    pprep = sub.add_parser("prepare", help="Prepara CSVs de trabajo desde requisa y explosión.")
    pprep.add_argument("--base-dir", default=".", help="Directorio con PDFs de proveedores.")
    pprep.add_argument("--requisa", default="REQUISA # 328 INST. MECANICAS C-40 (1).xlsx")
    pprep.add_argument("--explosion", default="EXPLOSION DE INSUMOS VELMARI CONTRATO $52M.xlsx")
    pprep.add_argument("--output-dir", default="salidas")
    pprep.set_defaults(func=cmd_prepare)

    pgen = sub.add_parser("generate", help="Genera OCs y estatus a partir de seleccion_proveedores.csv.")
    pgen.add_argument("--selection-csv", default="salidas/seleccion_proveedores.csv")
    pgen.add_argument("--output-dir", default="salidas/generado")
    pgen.set_defaults(func=cmd_generate)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
