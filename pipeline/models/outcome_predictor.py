from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List

# Lightweight baseline predictor with a pluggable interface.
# Later you can replace internals with real ML (e.g., sklearn/torch).


@dataclass
class Outcome:
    weight_delta_kg: float
    energy: float
    bloating: float
    acne_oiliness: float
    digestion_comfort: float
    mood: float


class OutcomePredictor:
    """
    A simple EMA-based predictor that updates per user from feedback.
    Features considered (for baseline):
    - category (e.g., high_protein, low_gi/high_fiber, gut_soothing, detox, weight_gain)
    - phenotype axes: sex, region, diet_type, activity, weight_class

    The baseline keeps running averages per (category) and per (category, phenotype hash)
    and blends them for a prediction. Replace with ML later.
    """

    def __init__(self, alpha: float = 0.4):
        self.alpha = alpha
        self.global_by_cat: Dict[str, Dict[str, float]] = {}
        self.by_cat_and_key: Dict[str, Dict[str, Dict[str, float]]] = {}
        self.metrics = [
            "weight_delta_kg",
            "energy",
            "bloating",
            "acne_oiliness",
            "digestion_comfort",
            "mood",
        ]

    def _key(self, profile: Dict[str, Any]) -> str:
        axes = [
            profile.get("sex"),
            profile.get("region"),
            profile.get("diet_type"),
            profile.get("activity"),
            profile.get("weight_class"),
        ]
        return "|".join(str(a or "?") for a in axes)

    def predict(self, category: str, profile: Dict[str, Any]) -> Outcome:
        key = self._key(profile)
        g = self.global_by_cat.get(category, {})
        l = self.by_cat_and_key.get(category, {}).get(key, {})
        # Defaults represent neutral outcome expectations
        base = {
            "weight_delta_kg": 0.0,
            "energy": 5.0,
            "bloating": 5.0,
            "acne_oiliness": 5.0,
            "digestion_comfort": 5.0,
            "mood": 5.0,
        }
        # Blend local (if any) with global, then with base
        blended = {}
        for m in self.metrics:
            v = 0.5 * g.get(m, base[m]) + 0.5 * l.get(m, g.get(m, base[m]))
            blended[m] = v
        return Outcome(**blended)

    def update(self, category: str, profile: Dict[str, Any], feedback: Dict[str, float]) -> None:
        key = self._key(profile)
        g = self.global_by_cat.setdefault(category, {})
        lk = self.by_cat_and_key.setdefault(category, {}).setdefault(key, {})
        for m in self.metrics:
            if m not in feedback:
                continue
            val = float(feedback[m])
            g[m] = self._ema(g.get(m), val)
            lk[m] = self._ema(lk.get(m), val)

    def _ema(self, prev: float | None, new: float) -> float:
        if prev is None:
            return new
        return self.alpha * new + (1 - self.alpha) * prev
