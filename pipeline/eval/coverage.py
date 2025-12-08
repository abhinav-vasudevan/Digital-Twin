from __future__ import annotations
import json
from pathlib import Path
from collections import defaultdict

# Compute phenotype and category coverage from inspector inventory and structured outputs

project_root = Path(__file__).parent.parent.parent
INV = project_root / "data-inspector" / "report" / "inventory.json"
OUT = project_root / "outputs" / "structured"
REPORT = project_root / "data-inspector" / "report" / "coverage.md"


def load_inventory():
    if not INV.exists():
        return None
    return json.loads(INV.read_text(encoding="utf-8"))


def main() -> int:
    inv = load_inventory()
    lines = ["# Coverage Report", ""]

    if inv:
        agg = inv.get("aggregations", {})
        lines += [
            "## Inventory-based Coverage",
            "### Categories",
            *[f"- {k}: {v}" for k, v in sorted(agg.get("category", {}).items(), key=lambda x: (-x[1], x[0]))],
            "",
            "### Sex",
            *[f"- {k}: {v}" for k, v in sorted(agg.get("sex", {}).items(), key=lambda x: (-x[1], x[0]))],
            "",
        ]

    # Structured files count
    counts = defaultdict(int)
    for p in OUT.rglob("*.jsonl"):
        parts = p.parts
        try:
            folder = parts[parts.index("structured") + 1]
        except Exception:
            folder = "?"
        counts[folder] += 1

    lines += [
        "## Structured Outputs",
        *[f"- {k}: {v} files" for k, v in sorted(counts.items(), key=lambda x: x[0])],
    ]

    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
