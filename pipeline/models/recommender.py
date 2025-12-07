from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List

from .outcome_predictor import OutcomePredictor, Outcome
from .policy import EpsilonGreedyPolicy, ScoredOption

# Categories to consider — later map from real simulation templates
DEFAULT_CATEGORIES = [
    "high_protein",
    "high_protein_high_fiber",
    "weight_loss",
    "weight_gain",
    "gut",
    "detox",
    "pcos",
    "type_1_diabetes",
    "skin",
    "liver_detox",
    "anti_inflammatory",
]


@dataclass
class Recommendation:
    category: str
    expected: Outcome
    rationale: str


class Recommender:
    """
    Orchestrates: candidate selection → outcome prediction → bandit policy → final pick.
    The actual plan construction (14-day items) is handled by the plan generator (later).
    """

    def __init__(self, predictor: OutcomePredictor | None = None, policy: EpsilonGreedyPolicy | None = None):
        self.predictor = predictor or OutcomePredictor()
        self.policy = policy or EpsilonGreedyPolicy()

    def candidates_for(self, profile: Dict[str, Any]) -> List[str]:
        # Later: use rules engine to filter unsafe categories based on conditions.
        conds = set((profile.get("conditions") or []))
        # If the user has specific conditions, prioritize those candidates
        prioritized = []
        if "pcos" in conds:
            prioritized.append("pcos")
        if "type_1_diabetes" in conds:
            prioritized.append("type_1_diabetes")
        if any(c in conds for c in ["acne", "skin", "oily_skin"]):
            prioritized.append("skin")
        if any(c in conds for c in ["gut", "bloating", "digestive"]):
            prioritized.append("gut")
        # always include general patterns
        tail = [c for c in DEFAULT_CATEGORIES if c not in prioritized]
        return prioritized + tail

    def recommend(self, profile: Dict[str, Any]) -> Recommendation:
        cats = self.candidates_for(profile)
        choice: ScoredOption = self.policy.pick(cats, self.predictor, profile)
        rationale = (
            f"Picked category '{choice.category}' via epsilon-greedy; "
            f"expected energy={choice.outcome.energy:.1f}, digestion={choice.outcome.digestion_comfort:.1f}, "
            f"bloating={choice.outcome.bloating:.1f}, acne={choice.outcome.acne_oiliness:.1f}"
        )
        return Recommendation(category=choice.category, expected=choice.outcome, rationale=rationale)

    def incorporate_feedback(self, profile: Dict[str, Any], used_category: str, feedback: Dict[str, float]) -> None:
        self.predictor.update(used_category, profile, feedback)
