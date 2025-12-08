from __future__ import annotations
import argparse
from pathlib import Path
from typing import Iterable

# Note: Requires Tesseract installed on Windows and pytesseract+Pillow in Python.
# If tesseract is not found, this script will skip files gracefully.

SUPPORTED_EXTS = {".pdf"}


def iter_files(roots: Iterable[Path]) -> Iterable[Path]:
    for root in roots:
        for p in root.rglob("*.pdf"):
            if p.is_file():
                yield p


def ocr_pdf_to_text(pdf_path: Path) -> str:
    try:
        import pytesseract
        from pdf2image import convert_from_path
        from PIL import Image
    except Exception:
        return ""

    try:
        images = convert_from_path(str(pdf_path))
        parts = []
        for img in images:
            txt = pytesseract.image_to_string(img) or ""
            parts.append(txt.strip())
        return "\n\n".join(filter(None, parts))
    except Exception:
        return ""


def main() -> int:
    ap = argparse.ArgumentParser(description="OCR fallback for scanned PDFs")
    project_root = Path(__file__).parent.parent
    ap.add_argument("--roots", nargs="*", default=[
        str(project_root / "1"),
        str(project_root / "2"),
    ])
    ap.add_argument("--out", default=str(project_root / "outputs" / "ocr"))
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    roots = [Path(p) for p in args.roots]
    out_root = Path(args.out)

    processed = 0
    for src in iter_files(roots):
        rel = None
        for r in roots:
            try:
                rel = src.relative_to(r)
                folder_tag = r.name
                break
            except Exception:
                continue
        if rel is None:
            folder_tag = "unknown"
            rel = src.name

        dest_dir = out_root / folder_tag / (rel.parent if hasattr(rel, 'parent') else Path("."))
        out_txt = dest_dir / f"{src.stem}.txt"
        if out_txt.exists() and not args.overwrite:
            continue

        text = ocr_pdf_to_text(src)
        if not text:
            continue
        out_txt.parent.mkdir(parents=True, exist_ok=True)
        out_txt.write_text(text, encoding="utf-8")
        processed += 1
        print(f"OCR ✔ {src} -> {out_txt}")

    print(f"Done OCR. Files processed: {processed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
