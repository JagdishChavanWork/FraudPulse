# FinIntel Publication Readiness Checklist

## Current Position

FinIntel is **not yet submission-ready**, but it is now organized well enough to be upgraded into a publishable applied ML manuscript.

## Already Completed

- Integrated project architecture exists for:
  - credit approval prediction
  - credit amount estimation
  - fraud detection
  - dashboards
  - authentication
  - prediction logging
- Real saved metrics are available for deployed models
- Project report has been corrected to match actual code and artifact values
- Analysis notebooks now exist for:
  - `notebooks/credit_risk/02_ml_model_building.ipynb`
  - `notebooks/fraud/01_fraud_detection.ipynb`
- A publication-style manuscript draft now exists:
  - `docs/reports/FinIntel_Publication_Draft.md`

## Still Required Before Submission

### 1. Execute the new notebooks

Required because the paper still needs baseline comparison tables and exported charts from actual notebook runs.

Deliverables:
- compact credit model comparison table
- enhanced credit model comparison table
- fraud model comparison table
- confusion matrices
- feature-importance plots
- final saved chart files for the manuscript

### 2. Strengthen the experimental section

Add:
- explicit train-test split description
- fixed random seed statement
- hyperparameter justification
- threshold tuning explanation for fraud
- baseline-to-final model comparison narrative

### 3. Add robustness checks

Recommended:
- repeated holdout experiments or cross-validation
- leakage audit for fraud features
- class-wise stability analysis for credit approval
- sensitivity analysis for fraud threshold selection

### 4. Clean the references

The current academic report still has repeated entries from iterative drafting.

Required:
- deduplicate the bibliography
- reduce repeated citations
- keep only the strongest and most relevant references
- align citations with paper sections rather than project-report sections

### 5. Reframe the writing style

The final submission should sound like a research manuscript, not a semester report.

Required improvements:
- tighter novelty statement
- stronger related-work positioning
- separate limitations / threats-to-validity section
- reproducibility statement
- less descriptive implementation narration
- more experiment-driven explanation

## Recommended Submission Positioning

Best positioning for publication:

1. **Integrated banking risk intelligence platform**
2. **Comparative study of ML models for credit and fraud workflows**
3. **Applied decision-support system with analyst-facing deployment**

Avoid positioning it as:

- a novel deep-learning architecture
- a state-of-the-art theoretical ML contribution
- a purely algorithmic paper

## Suggested Next Working Sequence

1. Run both notebooks fully
2. Export final tables and figures
3. Deduplicate references
4. Convert the markdown publication draft into submission format
5. Prepare a conference-style paper version

## Reviewer View

If submitted today, the work would likely be seen as:

- a strong academic project
- a promising applied system paper
- not fully publication-ready due to incomplete experimental framing and reference cleanup

If the remaining steps are completed, it can become a credible submission for an **applied AI / financial analytics / decision-support** venue.
