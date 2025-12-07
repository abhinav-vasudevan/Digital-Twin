from __future__ import annotations
import re
from pathlib import Path
from typing import Dict, Optional

# Precompile regex patterns for common attributes found in filenames
SEX_RE = re.compile(r"\b(male|female)\b", re.IGNORECASE)
REGION_RE = re.compile(r"\b(north\s*indian|south\s*indian)\b", re.IGNORECASE)
VEGTYPE_RE = re.compile(r"\b(veg|vegetarian|vegeterian|eggetarian|eggeterian|non\s*veg|non-veg)\b", re.IGNORECASE)
ACTIVITY_RE = re.compile(r"\b(sedentary|light\s*(worker|active)?|moderate\s*(worker|active)?|heavy\s*(worker|active)?)\b", re.IGNORECASE)
WEIGHTCLASS_RE = re.compile(r"\b(underweight|normal|overweight|obese)\b", re.IGNORECASE)

# Condition/diet categories inferred from folder names or file basenames
CATEGORY_HINTS = [
    (re.compile(r"\bpcos\b", re.IGNORECASE), "pcos"),
    (re.compile(r"type\s*1\s*diabetes|t1d", re.IGNORECASE), "type_1_diabetes"),
    (re.compile(r"\bskin\s*(detox|health|acne|oily)\b", re.IGNORECASE), "skin"),
    (re.compile(r"\bgut\b|bloating|digestive", re.IGNORECASE), "gut"),
    (re.compile(r"\bliver\s*detox\b", re.IGNORECASE), "liver_detox"),
    (re.compile(r"\bprobiotic\b", re.IGNORECASE), "probiotic"),
    (re.compile(r"\b(weight\s*loss)\b", re.IGNORECASE), "weight_loss"),
    (re.compile(r"\bweight\s*gain|underweight\s*n\s*malnutrition\b", re.IGNORECASE), "weight_gain"),
    (re.compile(r"anti[-\s]*inflamm?atory", re.IGNORECASE), "anti_inflammatory"),
    (re.compile(r"anti[-\s]*aging|sun\s*damage|fine\s*lines", re.IGNORECASE), "anti_aging_skin"),
    (re.compile(r"high\s*protein\s*high\s*fiber", re.IGNORECASE), "high_protein_high_fiber"),
    (re.compile(r"high\s*protein\b", re.IGNORECASE), "high_protein"),
    (re.compile(r"\bdetox\b", re.IGNORECASE), "detox"),
]


def parse_from_path(path: Path) -> Dict[str, Optional[str]]:
    """Parse attributes from a file path (name + parent folders)."""
    text = " ".join(p.name for p in [*path.parents][:4][::-1] + [path])

    sex = _first_match(SEX_RE, text)
    region = _first_match(REGION_RE, text)
    vegtype = _normalize_veg(_first_match(VEGTYPE_RE, text))
    activity = _normalize_activity(_first_match(ACTIVITY_RE, text))
    weight_class = _first_match(WEIGHTCLASS_RE, text)

    category = None
    for regex, label in CATEGORY_HINTS:
        if regex.search(text):
            category = label
            break

    return {
        "sex": _lower_or_none(sex),
        "region": _normalize_region(region),
        "diet_type": vegtype,
        "activity": activity,
        "weight_class": _lower_or_none(weight_class),
        "category": category,
    }


def _first_match(regex: re.Pattern, text: str) -> Optional[str]:
    m = regex.search(text)
    return m.group(1) if m else None


def _lower_or_none(s: Optional[str]) -> Optional[str]:
    return s.lower() if isinstance(s, str) else None


def _normalize_veg(s: Optional[str]) -> Optional[str]:
    if not s:
        return None
    t = s.lower().replace("-", " ").strip()
    if t.startswith("non"):
        return "non_veg"
    if t.startswith("egg"):
        return "eggetarian"
    if t in {"veg", "vegetarian", "vegeterian"}:
        return "veg"
    return t.replace(" ", "_")


def _normalize_activity(s: Optional[str]) -> Optional[str]:
    if not s:
        return None
    t = s.lower().replace("worker", "").replace("active", "").strip()
    for key in ["sedentary", "light", "moderate", "heavy"]:
        if key in t:
            return key
    return t


def _normalize_region(s: Optional[str]) -> Optional[str]:
    if not s:
        return None
    t = s.lower().replace(" ", "_")
    if t in {"north_indian", "south_indian"}:
        return t
    return s.lower()
