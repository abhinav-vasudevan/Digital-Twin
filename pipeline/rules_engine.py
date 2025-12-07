from __future__ import annotations
from typing import Dict, Any, List

# Minimal rules engine scaffold for safety and filtering.

CONSTRAINTS = {
    "limit_high_gi_carbs": lambda meal: not _has_terms(meal, ["white rice", "sugar", "sweets"]),
    "ensure_fiber_min": lambda meal: True,  # placeholder
    "distribute_carbs_evenly": lambda day_items: True,  # placeholder
    "pair_carbs_with_protein": lambda meal: True,  # placeholder
    "limit_high_fodmap": lambda meal: not _has_terms(meal, ["onion", "garlic", "rajma", "chana"]),
    "limit_processed_sugar": lambda meal: not _has_terms(meal, ["soda", "cola", "dessert", "candy"]),
    "limit_saturated_fat": lambda meal: not _has_terms(meal, ["fried", "butter-heavy", "cream-laden"]),
}

CATEGORY_CONSTRAINTS = {
    "pcos": ["limit_high_gi_carbs", "ensure_fiber_min"],
    "type_1_diabetes": ["distribute_carbs_evenly", "pair_carbs_with_protein"],
    "gut": ["limit_high_fodmap"],
    "detox": ["limit_processed_sugar", "limit_saturated_fat"],
}


def _has_terms(meal: Dict[str, Any], terms: List[str]) -> bool:
    text = " ".join([meal.get("name", ""), meal.get("notes", ""), meal.get("quantity", "")]).lower()
    return any(t in text for t in terms)


def allowed_categories(profile: Dict[str, Any], desired: List[str]) -> List[str]:
    # In future: use profile conditions/allergies to exclude categories.
    return desired


def validate_plan(category: str, plan_items: List[Dict[str, Any]]) -> bool:
    constraint_ids = CATEGORY_CONSTRAINTS.get(category, [])
    if not constraint_ids:
        return True
    for item in plan_items:
        for it in item.get("items", []):
            for cid in constraint_ids:
                fn = CONSTRAINTS.get(cid)
                if fn and not fn({"name": it.get("name", ""), "quantity": it.get("quantity", ""), "notes": it.get("notes", "") } ):
                    return False
    return True
