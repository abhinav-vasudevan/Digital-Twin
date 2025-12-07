from __future__ import annotations
import argparse
import sys
from pathlib import Path
from typing import List


def extract_text_from_pdf(pdf_path: Path, max_pages: int | None = None) -> str:
    import pdfplumber

    text_parts: List[str] = []
    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            num_pages = len(pdf.pages)
            page_limit = min(num_pages, max_pages) if max_pages is not None else num_pages
            for i in range(page_limit):
                page = pdf.pages[i]
                # Tweak tolerances a bit for better layout
                page_text = page.extract_text(x_tolerance=1.5, y_tolerance=1.5) or ""
                text_parts.append(page_text.strip())
    except Exception as e:
        raise RuntimeError(f"Failed to read '{pdf_path.name}': {e}")

    return "\n\n".join(filter(None, text_parts))


def extract_tables_from_pdf(pdf_path: Path, max_pages: int | None = None) -> List[List[List[str]]]:
    """Return a list of tables, where each table is a list of rows, and each row is a list of cell strings."""
    import pdfplumber

    tables: List[List[List[str]]] = []
    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            num_pages = len(pdf.pages)
            page_limit = min(num_pages, max_pages) if max_pages is not None else num_pages
            for i in range(page_limit):
                page = pdf.pages[i]
                page_tables = page.extract_tables() or []
                for tbl in page_tables:
                    # Normalize cells to strings
                    normalized = [[(cell if cell is not None else "").strip() for cell in row] for row in tbl]
                    # Skip empty tables
                    if any(any(cell for cell in row) for row in normalized):
                        tables.append(normalized)
    except Exception as e:
        raise RuntimeError(f"Failed to extract tables from '{pdf_path.name}': {e}")

    return tables


def write_text(out_path: Path, content: str, overwrite: bool) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists() and not overwrite:
        return
    out_path.write_text(content, encoding="utf-8")


def write_tables_to_excel(out_path: Path, tables: List[List[List[str]]], overwrite: bool) -> None:
    if not tables:
        return
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists() and not overwrite:
        return

    import pandas as pd

    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        for idx, tbl in enumerate(tables, start=1):
            # Find the longest row to normalize column counts
            max_cols = max((len(r) for r in tbl), default=0)
            norm_rows = [r + [""] * (max_cols - len(r)) for r in tbl]
            df = pd.DataFrame(norm_rows)
            sheet_name = f"table_{idx}"
            # Excel sheet names limited to 31 chars
            if len(sheet_name) > 31:
                sheet_name = sheet_name[:31]
            df.to_excel(writer, index=False, header=False, sheet_name=sheet_name)


def process_pdf(
    pdf_path: Path,
    root: Path,
    out_dir: Path | None,
    extract_tables: bool,
    max_pages: int | None,
    overwrite: bool,
) -> dict:
    rel = pdf_path.relative_to(root)
    base_name = pdf_path.stem

    if out_dir:
        text_out = out_dir / rel.parent / f"{base_name}.txt"
        excel_out = out_dir / rel.parent / f"{base_name}_tables.xlsx"
    else:
        text_out = pdf_path.with_suffix(".txt")
        excel_out = pdf_path.with_name(f"{base_name}_tables.xlsx")

    result = {"pdf": str(pdf_path), "text_out": str(text_out), "excel_out": str(excel_out), "tables": 0}

    text = extract_text_from_pdf(pdf_path, max_pages=max_pages)
    write_text(text_out, text, overwrite=overwrite)

    if extract_tables:
        tables = extract_tables_from_pdf(pdf_path, max_pages=max_pages)
        write_tables_to_excel(excel_out, tables, overwrite=overwrite)
        result["tables"] = len(tables)

    return result


def main(argv: List[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Extract text (and tables) from PDFs in bulk.")
    p.add_argument("--root", type=Path, default=Path("."), help="Root directory to search (default: current directory)")
    p.add_argument("--pattern", default="**/*.pdf", help="Glob pattern relative to root (default: **/*.pdf)")
    p.add_argument("--out-dir", type=Path, default=None, help="Optional directory to write outputs into (preserves structure)")
    p.add_argument("--tables", action="store_true", help="Also extract tables into an Excel file per PDF")
    p.add_argument("--max-pages", type=int, default=None, help="Limit pages processed per PDF (useful for testing)")
    p.add_argument("--overwrite", action="store_true", help="Overwrite existing outputs if present")

    args = p.parse_args(argv)

    root = args.root.resolve()
    if not root.exists() or not root.is_dir():
        print(f"Root directory not found: {root}", file=sys.stderr)
        return 2

    pdfs = sorted(root.glob(args.pattern))
    if not pdfs:
        print("No PDFs matched the given root/pattern.")
        return 0

    processed = 0
    errors = 0

    for pdf_path in pdfs:
        try:
            res = process_pdf(
                pdf_path=pdf_path,
                root=root,
                out_dir=(args.out_dir.resolve() if args.out_dir else None),
                extract_tables=args.tables,
                max_pages=args.max_pages,
                overwrite=args.overwrite,
            )
            processed += 1
            tables_note = f", tables: {res['tables']}" if args.tables else ""
            print(f"✔ {pdf_path} -> {res['text_out']}{tables_note}")
        except Exception as e:
            errors += 1
            print(f"✘ {pdf_path}: {e}", file=sys.stderr)

    print(f"Done. Processed: {processed}, Errors: {errors}")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
