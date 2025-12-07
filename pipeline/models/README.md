# ML Components (Scaffold)

This folder contains a minimal, swappable foundation for learning user patterns and recommending diet categories.

- `outcome_predictor.py`: Baseline EMA predictor that learns from weekly feedback per user phenotype and category. Replace internals with ML when ready (sklearn/torch).
- `policy.py`: Epsilon-greedy bandit over categories with a simple utility function combining predicted outcomes.
- `recommender.py`: Orchestrates candidate selection → prediction → policy → final category, with feedback incorporation.

## Expected Data Flow
1. Parse and structure documents into `outputs/structured/` (plan items by day/meal).
2. When user requests a plan: build profile JSON and call `Recommender.recommend(profile)` to select a category.
3. Generate a 14-day concrete plan using templates/rules for that category (separate component).
4. After a week, collect `feedback.json` and call `Recommender.incorporate_feedback(profile, category, feedback)`.

## Upgrading to Real ML
- Replace `OutcomePredictor` with a learned model trained on historical `(profile, category) → outcomes` pairs.
- Support time-series inputs (LSTM/1D-CNN) if meal logs are available; otherwise use tabular features.
- Swap `EpsilonGreedyPolicy` with Thompson Sampling or UCB for better exploration.
