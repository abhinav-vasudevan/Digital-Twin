# Long TODO — End-to-End Pipeline Build

## Phase 0 — Data Understanding & Curation
- Inventory folders `1/` and `2/` (done: scaffolding; pending: run `discover.py`).
- Normalize filename conventions (map typos: vegeterian→vegetarian, eggeterian→eggetarian, non veg→non_veg, worker→activity).
- Build phenotype taxonomy: sex, region, diet_type, activity, weight_class.
- Map categories: pcos, type_1_diabetes, skin, gut, liver_detox, probiotic, weight_loss, weight_gain, anti_inflammatory, anti_aging_skin, high_protein, high_protein_high_fiber, detox.
- Add OCR pipeline for scanned PDFs (tesseract + pytesseract), configurable per batch.
- De-duplicate near-identical plans (cosine sim on TF-IDF / MinHash / SimHash), keep canonical.
- Coverage matrix: for each category, compute slice availability across phenotype axes; export heatmaps.

## Phase 1 — Content Extraction
- PDF text extraction (pdfplumber) with layout hints; fall back to OCR when no selectable text.
- DOCX text extraction (python-docx); preserve basic structure (headings, tables).
- Table extraction from PDFs (pdfplumber) into structured CSV/Excel (meals, times, quantities).
- Section splitter: detect standardized sections (e.g., breakfast/lunch/dinner/snacks; do/don’t; notes; substitutions).
- Unit normalization: map `cup`, `katori`, `tbsp`, `tsp`, `g`, `ml` to canonical units; handle Indian measures.

## Phase 2 — Knowledge Graph & Canonicalization
- Food entity resolver: map text mentions to canonical foods (e.g., `dahi`→`curd`→`yogurt`).
- Nutrient mapping: per food item, fetch macro/micro (calories, protein, carbs, fats, fiber, GI/GL where available).
- Contraindication rules: e.g., PCOS→low-GI emphasis; T1D→carb distribution; gut issues→FODMAP-aware; liver detox→saturated fat/processed sugar limits.
- Substitution rules (regional and dietary preference variants).
- Store graph in simple JSON/CSV first; later upgrade to a graph DB.

## Phase 3 — Digital Twin & Simulation
- User profile schema: age, sex, BMI, region, diet type, activity, medical conditions, preferences.
- Baseline estimator: resting energy, TDEE, insulin sensitivity proxy, gut reactivity proxy.
- Simulation candidates: map categories to intervention templates (high_protein, low_GI/high_fiber, gut_soothing, detox, weight_gain).
- Outcome predictors (initial heuristic → ML later): expected Δweight, energy, bloating, acne/oiliness, digestion comfort, mood.
- Safety guardrails from rules engine; filter unsafe suggestions.

## Phase 4 — Feedback & Learning
- Weekly feedback schema: sliders for outcomes; adherence/meal logging (optional for v1).
- Update rules: Bayesian/EMA updates to twin parameters from feedback.
- Recommendation policy: rank next 2-week plan with exploration vs exploitation.

## Phase 5 — APIs & UI
- Minimal API (FastAPI): endpoints for profile, recommend, feedback, plan retrieval.
- Simple UI (Streamlit) to demo flows; later native/mobile/web.

## Phase 6 — Validation & Ops
- Offline evaluation: backtest using historical outcomes (if available) or heuristic plausibility checks.
- Content QA: lint plans for completeness (meals covered, macros within range, constraints respected).
- Versioning: track plan versions and provenance.

## Tasks to Start Implementing Now
- [ ] Run `data-inspector/discover.py` and commit `inventory.json` + `understanding.md`.
- [ ] Add OCR support to inspector for scanned PDFs.
- [ ] Implement section splitter and table normalizer for extracted text.
- [ ] Draft user/profile and feedback JSON schemas.
- [ ] Define intervention templates mapped from categories.
- [ ] Create a small FastAPI service skeleton.
