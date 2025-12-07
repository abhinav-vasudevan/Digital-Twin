from __future__ import annotations
import json
from pathlib import Path

FOODS = [
    {
        "id": "rice",
        "name": "Rice",
        "aliases": ["white rice", "steamed rice", "chawal"],
        "nutrients": {"calories": 130, "carbs_g": 28, "protein_g": 2.7, "fat_g": 0.3, "fiber_g": 0.4, "gi": 73},
    },
    {
        "id": "roti",
        "name": "Roti (Wheat Chapati)",
        "aliases": ["chapati", "phulka", "roti"],
        "nutrients": {"calories": 120, "carbs_g": 19, "protein_g": 3.6, "fat_g": 3.2, "fiber_g": 2.0},
    },
    {
        "id": "dahi",
        "name": "Curd (Yogurt)",
        "aliases": ["dahi", "curd", "yogurt"],
        "nutrients": {"calories": 61, "carbs_g": 4.7, "protein_g": 3.5, "fat_g": 3.3, "fiber_g": 0.0},
    },
    {
        "id": "dal",
        "name": "Dal (Lentils cooked)",
        "aliases": ["dal", "lentil curry", "dal tadka"],
        "nutrients": {"calories": 116, "carbs_g": 20, "protein_g": 9, "fat_g": 0.4, "fiber_g": 8},
    },
    {
        "id": "egg",
        "name": "Egg",
        "aliases": ["boiled egg", "omelet", "andaa"],
        "nutrients": {"calories": 78, "carbs_g": 0.6, "protein_g": 6.3, "fat_g": 5.3},
    },
    {
        "id": "paneer",
        "name": "Paneer",
        "aliases": ["cottage cheese", "paneer"],
        "nutrients": {"calories": 265, "carbs_g": 6.1, "protein_g": 18.3, "fat_g": 20.8},
    }
]

RULES = [
    {
        "id": "pcos_low_gi",
        "condition": "pcos",
        "description": "Emphasize low-GI carbs and fiber; avoid refined sugar",
        "constraints": ["limit_high_gi_carbs", "ensure_fiber_min"],
    },
    {
        "id": "t1d_carb_windows",
        "condition": "type_1_diabetes",
        "description": "Distribute carbs evenly; pair carbs with protein/fat",
        "constraints": ["distribute_carbs_evenly", "pair_carbs_with_protein"],
    },
    {
        "id": "gut_low_fodmap_phase",
        "condition": "gut",
        "description": "Reduce high FODMAP foods during flare-up phase",
        "constraints": ["limit_high_fodmap"],
    },
    {
        "id": "detox_limits",
        "condition": "detox",
        "description": "Reduce processed sugar and saturated fat",
        "constraints": ["limit_processed_sugar", "limit_saturated_fat"],
    }
]


def main() -> int:
    out_dir = Path(r"D:\\Documents\\Diet plan\\kg")
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "foods.json").write_text(json.dumps({"foods": FOODS}, indent=2), encoding="utf-8")
    (out_dir / "rules.json").write_text(json.dumps({"rules": RULES}, indent=2), encoding="utf-8")
    print(f"Wrote KG files to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
