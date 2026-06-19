# Project Information

## Overview

**Startup Success Predictor (SSP)** is a Streamlit web application that predicts the likely outcome of a startup based on its funding profile and industry data. Users enter a company's details (manually, by text autofill from Wikipedia, or by voice), then receive an ML-generated prediction and a comparative analysis against other startups.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit (multi-page app, `st.navigation`) |
| ML model | XGBoost multiclass classifier, trained with SMOTE oversampling |
| Model serialization | `joblib` |
| AI field extraction | Anthropic Claude (`claude-haiku-4-5-20251001`) |
| Voice transcription | Whisper (via `src/services/transcriptor.py`) |
| Company data lookup | Wikipedia / Wikidata scraping (`utils/autofill_system.py`) |
| Charts | Plotly |
| API layer | FastAPI (`project/api/fast.py`) |
| Environment | Python 3.10, `python-dotenv` |

---

## ML Model

**File:** `models/ssp_multiclass_xgb_smote.pkl`

**Task:** Multiclass classification — predict one of 4 startup outcomes:

| Label | Index |
|---|---|
| Acquired | 0 |
| Closed | 1 |
| IPO | 2 |
| Operating | 3 |

**Input features (after preprocessing in `utils/model_utils.preprocess_input`):**

| Feature | Description |
|---|---|
| `category_list` | Industry category |
| `funding_total_usd` | Raw total funding in USD |
| `country_code` | ISO 3-letter country code |
| `state_code` | US state abbreviation (or equivalent) |
| `funding_rounds` | Number of rounds |
| `founded_year` | Year founded |
| `first_funding_year` | Year of first funding |
| `last_funding_year` | Year of last funding |
| `years_to_first_funding` | `first_funding_year - founded_year` |
| `funding_duration` | `last_funding_year - first_funding_year` |
| `log_funding_total_usd` | `log1p(funding_total_usd)` |
| `funding_per_round` | `funding_total_usd / funding_rounds` |
| `multiple_rounds` | Binary: `funding_rounds > 1` |
| `early_funding` | Binary: `years_to_first_funding <= 2` |
| `high_funding` | Binary: `funding_total_usd > $5M` (training median) |

---

## Pages

| URL | File | Navigation label | Step |
|---|---|---|---|
| `/intro` | `pages/0_intro.py` | Home | — |
| `/fill_form` | `pages/2_fill_form.py` | Startup Picker | 2 / 4 |
| `/form_overview` | `pages/3_form_overview.py` | Startup Profile | 3 / 4 |
| `/results` | `pages/5_results.py` | Decision Center | 4 / 4 |
| `/compare` | `pages/4_compare.py` | Portfolio Builder | 4 / 4 |

Navigation order is defined in `FLOW` in `src/components/navigation.py`.

---

## Key Features

### Text Autofill
User types a company name → `utils/autofill_system.py` scrapes Wikipedia/Wikidata → raw text is passed to Claude (`src/services/field_extractor.py`) → returns structured JSON → form pre-fills.

### Voice Input
User records audio → `src/services/transcriptor.py` transcribes with Whisper → transcript passed to Claude (`field_extractor.py`) → structured fields returned → form pre-fills.

### Prediction
`src/services/predictor.get_prediction()` preprocesses the payload, runs `model.predict_proba()`, and returns:
- `predicted_class` — most likely outcome
- `confidence` — probability of predicted class
- `all_probabilities` — dict of all 4 class probabilities
- `top_features` — feature importances from the estimator

### Portfolio Builder (Compare)
Up to 10 startups entered manually or via CSV upload. Each is run through the model independently. Results are ranked by `Operating Prob (%)` and displayed as a sortable table.

---

## Environment Variables

Defined in `.env`, loaded via `python-dotenv` in `app.py`.

| Variable | Used by |
|---|---|
| `ANTHROPIC_API_KEY` | `src/config.py` → `field_extractor.py` |

---

## Running the App

```bash
streamlit run app.py
```

---

## Branch Convention

Main branch: `master`
Active development branch pattern: `demoday<N>` (e.g. `demoday10`)
