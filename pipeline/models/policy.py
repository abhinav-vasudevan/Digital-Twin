from __future__ import annotations
import math
import random
from dataclasses import dataclass
from typing import Dict, Any, List

from .outcome_predictor import OutcomePredictor, Outcome


@dataclass
class ScoredOption:
    category: str
    score: float
    outcome: Outcome


class EpsilonGreedyPolicy:
    """
    Simple bandit policy over categories. Score is a weighted utility of predicted outcomes.
    Epsilon controls exploration.
    """

    def __init__(self, epsilon: float = 0.15):
        self.epsilon = epsilon

    def score_outcome(self, outcome: Outcome) -> float:
        # Utility: higher energy/digestion/mood is good; lower bloating/acne; weight delta target ~ context-specific.
        return (
            0.25 * outcome.energy
            + 0.25 * outcome.digestion_comfort
            + 0.20 * outcome.mood
            - 0.15 * outcome.bloating
            - 0.15 * outcome.acne_oiliness
        )

    def pick(self, categories: List[str], predictor: OutcomePredictor, profile: Dict[str, Any]) -> ScoredOption:
        # Exploration
        if random.random() < self.epsilon:
            cat = random.choice(categories)
            oc = predictor.predict(cat, profile)
            return ScoredOption(cat, self.score_outcome(oc), oc)
        # Exploitation
        best = None
        for c in categories:
            oc = predictor.predict(c, profile)
            sc = self.score_outcome(oc)
            if best is None or sc > best.score:
                best = ScoredOption(c, sc, oc)
        return best  # type: ignore
