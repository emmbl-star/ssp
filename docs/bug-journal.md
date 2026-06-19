# Bug Journal

Chronological log of bugs encountered, their root cause, and how they were resolved.

---

## Template

```
### [DATE] — Short description
**Status:** Open | Fixed | Workaround
**File(s):** path/to/file.py
**Symptom:** What the user sees or what breaks.
**Root cause:** Why it happens.
**Fix:** What was changed.
**Notes:** Any edge cases or follow-up risk.
```

---

## Log

---

### 2026-06-19 — `render_page_navbar()` unexpected keyword argument `full_width`

**Status:** Fixed
**File(s):** `src/components/navigation.py`, `pages/4_compare.py`
**Symptom:** `TypeError: render_page_navbar() got an unexpected keyword argument 'full_width'` on app load.
**Root cause:** Python imported a stale `.pyc` bytecode cache from `src/components/__pycache__/` that predated the addition of the `full_width` parameter to the function signature. The source file was correct; the cache was not.
**Fix:** Deleted all `.pyc` files under `src/components/__pycache__/` and restarted the Streamlit server.
**Notes:** Will recur if the server is not restarted after edits to `navigation.py`. Streamlit's hot-reload does not always invalidate `__pycache__` on first run.

---

### [DATE] — Pickle model load failure after multiclass migration

**Status:** Fixed
**File(s):** `utils/model_utils.py`, `models/ssp_multiclass_xgb_smote.pkl`
**Symptom:** App crashed on startup with a pickle/joblib deserialization error.
**Root cause:** Model file was rebuilt for multiclass XGBoost with SMOTE; the old binary was still on disk and referenced by joblib.
**Fix:** Replaced the `.pkl` file with the newly trained multiclass pipeline (`cf2b785`).
**Notes:** `scikit-learn` version is pinned to `1.6.1` in `requirements.txt` to avoid future deserialization mismatches between training and inference environments.

---

### [DATE] — Voice input fields not persisting to form overview

**Status:** Fixed
**File(s):** `pages/2_fill_form.py`, `src/components/voice_input.py`
**Symptom:** After speaking, the form on `3_form_overview.py` showed empty fields.
**Root cause:** `extracted_fields` was being written to `st.session_state` inside the voice component but the session key was initialised to `{}` at the top of `2_fill_form.py` on every rerun, overwriting the populated value.
**Fix:** Moved the `if "extracted_fields" not in st.session_state` guard to only initialise when the key is absent (`d9_userflow` branch, `ae34190`).
**Notes:** Same pattern used in `3_form_overview.py` — guard-only init, never unconditional reset.

---

### [DATE] — Orange button color inconsistency across pages

**Status:** Fixed
**File(s):** `pages/4_compare.py`, `src/components/navigation.py`
**Symptom:** The "Compare startups" button on the Portfolio Builder page rendered a slightly different shade of orange (`#FF841F`) compared to all other orange CTAs in the app (`#F87F19`).
**Root cause:** The compare page hardcoded its own hex value rather than referencing a shared token.
**Fix:** Added `ACCENT_ORANGE = "#F87F19"` to `navigation.py` and updated `4_compare.py` to use `#F87F19`. (`demoday10`)

---

### [DATE] — Compare page layout broken by global card CSS

**Status:** Fixed
**File(s):** `pages/4_compare.py`, `src/components/navigation.py`
**Symptom:** The Portfolio Builder page appeared inside a narrow white card instead of using its intended full-width transparent layout.
**Root cause:** `render_page_navbar` injected a white card `.block-container` style as default; the compare page's local override came after but was fragile and duplicated layout logic.
**Fix:** Added `full_width: bool = False` parameter to `render_page_navbar`. When `True`, it injects the full-width transparent override after the card CSS. The compare page now calls `render_page_navbar(..., full_width=True)`. (`demoday10`)

---

### [DATE] — Breadcrumb row z-index conflict with Streamlit toolbar

**Status:** Fixed
**File(s):** `src/components/navigation.py`
**Symptom:** The breadcrumb links were partially hidden behind Streamlit's default toolbar.
**Root cause:** `[data-testid="stHeader"]` and `[data-testid="stToolbar"]` were not hidden.
**Fix:** Added `display: none !important` for both elements in the navbar CSS block in `render_page_navbar`.

---

### [DATE] — Action buttons on Startup Profile page too wide / overflow on small viewports

**Status:** Fixed
**File(s):** `pages/3_form_overview.py`
**Symptom:** The 3 action buttons ("Speak to edit", "Compare startups", "Predict success") overflowed their columns on narrower screens.
**Root cause:** Default Streamlit button sizing does not constrain width or font-size responsively.
**Fix:** Added `font-size: clamp(0.5rem, 1.1vw, 0.875rem)` and responsive padding via `clamp()` to the shared column button selector in `3_form_overview.py`. Added `white-space: nowrap` and `text-overflow: ellipsis` to prevent wrapping. (`demoday10`)
