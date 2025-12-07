from __future__ import annotations
import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any

from filename_parser import parse_from_path

SUPPORTED_EXTS = {".pdf", ".docx"}


@dataclass
class FileMeta:
    path: str
    folder: str
    ext: str
    size_bytes: int
    has_text: bool | None
    sample_text: str | None
    attrs: Dict[str, Any]


def sample_pdf_text(path: Path, max_chars: int = 600) -> tuple[bool, str]:
    import pdfplumber
    try:
        with pdfplumber.open(str(path)) as pdf:
            if not pdf.pages:
                return False, ""
            text = pdf.pages[0].extract_text(x_tolerance=1.5, y_tolerance=1.5) or ""
            text = text.strip()
            return (len(text) > 0), text[:max_chars]
    except Exception:
        return False, ""


def sample_docx_text(path: Path, max_chars: int = 600) -> tuple[bool, str]:
    try:
        from docx import Document
    except Exception:
        # python-docx not installed
        return None, ""
    try:
        doc = Document(str(path))
        text = "\n".join(p.text for p in doc.paragraphs if p.text).strip()
        return (len(text) > 0), text[:max_chars]
    except Exception:
        return False, ""


def discover(root_dirs: List[Path]) -> Dict[str, Any]:
    files: List[FileMeta] = []
    totals: Dict[str, int] = {"files": 0, "pdf": 0, "docx": 0}

    for root in root_dirs:
        for p in root.rglob("*"):
            if p.is_dir():
                continue
            ext = p.suffix.lower()
            if ext not in SUPPORTED_EXTS:
                continue

            has_text = None
            sample = ""
            if ext == ".pdf":
                has_text, sample = sample_pdf_text(p)
                totals["pdf"] += 1
            elif ext == ".docx":
                has_text, sample = sample_docx_text(p)
                totals["docx"] += 1

            attrs = parse_from_path(p)
            meta = FileMeta(
                path=str(p),
                folder=str(root),
                ext=ext,
                size_bytes=p.stat().st_size,
                has_text=has_text,
                sample_text=sample,
                attrs=attrs,
            )
            files.append(meta)
            totals["files"] += 1

    # Aggregations
    agg: Dict[str, Dict[str, int]] = {
        "category": {},
        "sex": {},
        "region": {},
        "diet_type": {},
        "activity": {},
        "weight_class": {},
    }

    for f in files:
        for key in agg.keys():
            val = (f.attrs.get(key) or "unknown").lower()
            agg[key][val] = agg[key].get(val, 0) + 1

    # Textability
    textability = {
        "has_text": sum(1 for f in files if f.has_text is True),
        "no_text": sum(1 for f in files if f.has_text is False),
        "unknown": sum(1 for f in files if f.has_text is None),
    }

    return {
        "totals": totals,
        "aggregations": agg,
        "textability": textability,
        "files": [asdict(f) for f in files],
    }


def write_reports(data: Dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    # JSON inventory
    (out_dir / "inventory.json").write_text(json.dumps(data, indent=2), encoding="utf-8")

    # Markdown understanding
    md = _to_markdown(data)
    (out_dir / "understanding.md").write_text(md, encoding="utf-8")


def _kvlist(d: Dict[str, int]) -> str:
    items = sorted(d.items(), key=lambda x: (-x[1], x[0]))
    return "\n".join(f"- {k}: {v}" for k, v in items)


def _to_markdown(data: Dict[str, Any]) -> str:
    t = data["totals"]
    agg = data["aggregations"]
    textability = data["textability"]

    parts = [
        "# Data Understanding Report",
        "",
        "## Overview",
        f"- Total files: {t['files']}",
        f"- PDFs: {t['pdf']}",
        f"- DOCX: {t['docx']}",
        "",
        "## Text Extractability",
        f"- Has selectable text: {textability['has_text']}",
        f"- No selectable text (likely scanned): {textability['no_text']}",
        f"- Unknown (dependency missing/errors): {textability['unknown']}",
        "",
        "## Categories (conditions/diets)",
        _kvlist(agg.get("category", {})) or "- (none)",
        "",
        "## Demographics & Phenotypes",
        "### Sex",
        _kvlist(agg.get("sex", {})) or "- (none)",
        "",
        "### Region",
        _kvlist(agg.get("region", {})) or "- (none)",
        "",
        "### Diet Type",
        _kvlist(agg.get("diet_type", {})) or "- (none)",
        "",
        "### Activity",
        _kvlist(agg.get("activity", {})) or "- (none)",
        "",
        "### Weight Class",
        _kvlist(agg.get("weight_class", {})) or "- (none)",
        "",
        "## Notes",
        "- Attributes are inferred from filenames and folders; verify edge cases.",
        "- Scanned PDFs may require OCR for reliable text extraction.",
    ]
    return "\n".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(description="Discover and summarize data in folders 1 and 2")
    ap.add_argument("--folders", nargs="*", default=[
        r"D:\\Documents\\Diet plan\\1",
        r"D:\\Documents\\Diet plan\\2",
    ], help="Folders to scan")
    ap.add_argument("--out", default=r"D:\\Documents\\Diet plan\\data-inspector\\report", help="Output directory for reports")
    args = ap.parse_args()

    roots = [Path(p) for p in args.folders]
    data = discover(roots)
    write_reports(data, Path(args.out))
    print(f"Wrote reports to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
