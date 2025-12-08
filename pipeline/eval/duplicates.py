from __future__ import annotations
from pathlib import Path
import math

project_root = Path(__file__).parent.parent.parent
RAW = project_root / "outputs" / "raw"
REPORT = project_root / "data-inspector" / "report" / "duplicates.md"


def text_of(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / max(1, len(a | b))


def shingles(text: str, k: int = 5) -> set[str]:
    toks = [t for t in text.lower().split() if t.isalpha() or t.isalnum()]
    return {" ".join(toks[i:i+k]) for i in range(0, max(0, len(toks)-k+1))}


def main() -> int:
    files = list(RAW.rglob("*.txt"))
    pairs = []
    # Simple O(n^2) — OK for ~460 files
    sigs = [(p, shingles(text_of(p))) for p in files]
    for i in range(len(sigs)):
        for j in range(i+1, len(sigs)):
            si = sigs[i][1]
            sj = sigs[j][1]
            sim = jaccard(si, sj)
            if sim >= 0.9:
                pairs.append((files[i], files[j], sim))

    lines = ["# Potential Duplicates (Jaccard shingles k=5, threshold=0.9)", ""]
    for a, b, s in pairs:
        lines.append(f"- {a}  ~=  {b}  (sim={s:.2f})")

    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {REPORT} with {len(pairs)} pairs above threshold")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
