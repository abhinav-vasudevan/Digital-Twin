from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

SECTION_HEADERS = [
    "breakfast",
    "mid morning",
    "mid-morning",
    "lunch",
    "evening",
    "evening snack",
    "snack",
    "snacks",
    "dinner",
]

HEADER_RE = re.compile(r"^(?:day\s*\d+\s*[-:])?\s*(.+)$", re.IGNORECASE)
SECTION_RE = re.compile(r"^\s*(" + "|".join([re.escape(h) for h in SECTION_HEADERS]) + r")\b", re.IGNORECASE)
DAY_RE = re.compile(r"^\s*day\s*(\d+)\b", re.IGNORECASE)

UNIT_MAP = {
    "katori": "bowl",
    "cup": "cup",
    "cups": "cup",
    "tbsp": "tbsp",
    "tsp": "tsp",
    "g": "g",
    "gram": "g",
    "grams": "g",
    "ml": "ml",
}


def normalize_unit(text: str) -> str:
    t = text.strip()
    for k, v in UNIT_MAP.items():
        t = re.sub(rf"\b{k}\b", v, t, flags=re.IGNORECASE)
    return t


def parse_file(txt_path: Path) -> List[Dict]:
    text = txt_path.read_text(encoding="utf-8", errors="ignore")
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    day = 1
    current_section = None
    items: List[Dict] = []

    for line in lines:
        # Detect day
        mday = DAY_RE.match(line)
        if mday:
            try:
                day = int(mday.group(1))
            except Exception:
                day = day
            continue

        # Detect sections
        if SECTION_RE.match(line):
            # extract normalized header
            header = SECTION_RE.match(line).group(1).lower()
            header = header.replace(" ", "_").replace("-", "_")
            # map synonyms
            if header in {"mid_morning", "mid-morning"}:
                header = "mid_morning"
            if header in {"snack", "snacks", "evening_snack"}:
                header = "snack"
            current_section = header
            continue

        if current_section:
            # best-effort split: "name — quantity" or "name - qty"
            parts = re.split(r"\s+[-–—:]\s+", line, maxsplit=1)
            name = parts[0].strip()
            qty = normalize_unit(parts[1]) if len(parts) > 1 else ""
            items.append({
                "day": day,
                "meal": current_section,
                "time": "",
                "items": [{"name": name, "quantity": qty, "notes": ""}],
            })

    return items


def main() -> int:
    ap = argparse.ArgumentParser(description="Parse structured meal items from extracted text")
    ap.add_argument("--in", dest="in_dir", default=r"D:\\Documents\\Diet plan\\outputs\\raw")
    ap.add_argument("--out", dest="out_dir", default=r"D:\\Documents\\Diet plan\\outputs\\structured")
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    in_root = Path(args.in_dir)
    out_root = Path(args.out_dir)

    processed = 0
    for txt in in_root.rglob("*.txt"):
        rel = txt.relative_to(in_root)
        out_path = out_root / rel.with_suffix(".jsonl")
        if out_path.exists() and not args.overwrite:
            continue
        items = parse_file(txt)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as f:
            for it in items:
                f.write(json.dumps(it, ensure_ascii=False) + "\n")
        processed += 1
        print(f"Parsed ✔ {txt} -> {out_path} ({len(items)} items)")

    print(f"Done parsing. Files processed: {processed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
