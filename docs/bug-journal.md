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

### 2026-06-19 — Company Profile form blank when returning from Results page

**Status:** Fixed
**File(s):** `src/components/input_form.py`
**Symptom:** Navigating from Decision Center (results) back to Startup Profile (form overview) showed a completely empty/default form, even though the data had been filled in.
**Root cause:** Streamlit clears session state entries that are owned by widgets (`frm_*` keys) when the script execution leaves the page that renders those widgets. On return, `_init_form_state` ran the hash check — the hash still matched (`extracted_fields` was unchanged) — and returned early *without reinitialising*. Because `frm_*` keys no longer existed, all widgets rendered with their default values.
**Fix:** Added `_save_form_backup()`, which copies all `frm_*` values into a plain (non-widget) dict at `st.session_state["_form_backup"]` at the end of every `render_input_form` call. Non-widget keys are never cleared by Streamlit on navigation. In `_init_form_state`, when the hash check passes but `frm_company_name` is absent (keys were cleared), the backup is restored before returning.
**Notes:** The backup reflects the state at the END of each render (i.e. the user's latest inputs). It is overwritten on every form render, so it always tracks the most recent values. A new autofill or voice submission takes the normal reinitialisation path and immediately overwrites the backup.

---

### 2026-06-19 — Company Profile form reset to defaults when navigating between pages

**Status:** Fixed
**File(s):** `src/components/input_form.py`, `src/components/voice_input.py`
**Symptom:** Navigating away from the Company Profile page and returning sometimes showed a blank/default form instead of the user's previously entered data.
**Root cause:** Two paths could reset `extracted_fields` to `{}` while `frm_ef_hash` was set to a real hash, causing `_init_form_state` to see a hash mismatch and reinitialize all `frm_*` keys to defaults:
  1. `voice_input.py` "Clear transcript" explicitly set `extracted_fields = {}`.
  2. `_init_form_state` had no guard against reinitializing from an empty `ef` when `frm_*` keys were already populated.
**Fix:**
  - Added `if not ef and "frm_ef_hash" in st.session_state: return` as an early-exit in `_init_form_state`. An empty `extracted_fields` arriving after the form has been initialized must never wipe existing data.
  - Replaced `st.session_state.extracted_fields = {}` in "Clear transcript" with clearing only voice-specific state (`transcript`, `last_audio_hash`, `pending_voice_update`). Also added `last_audio_hash = None` so re-recording the same clip retriggers transcription.
**Notes:** `frm_*` widget keys persist in session state across all page navigations. The only legitimate reason to reinitialize them is a genuinely new `extracted_fields` payload (new autofill lookup or new voice submission). Any other path — empty ef, transcript reset, page hop — must leave them untouched.

---

### 2026-06-19 — Backward navigation to Startup Picker skips mode selector

**Status:** Fixed
**File(s):** `pages/2_fill_form.py`
**Symptom:** Clicking "Startup Picker" in the navbar breadcrumb from Startup Profile, Decision Center, or Portfolio Builder opened the text-fill (or voice) panel directly instead of the mode selector cards.
**Root cause:** Same as the intro CTA bug: `fill_mode` is guard-initialised (`if not in ss`) so it kept its previous value when the page reloaded. The navbar breadcrumb uses `st.page_link` (a plain anchor tag), so no Python code runs on click — the reset cannot be placed on the origin page.
**Fix:** In `2_fill_form.py`, before `render_page_navbar` modifies `nav_stack`, check whether the last entry is a later step (`Startup Profile`, `Decision Center`, or `Portfolio Builder`). If so, set `fill_mode = None` unconditionally. `render_page_navbar` then trims the stack, so on every subsequent rerun within fill_form the condition is False and the user's chosen mode is preserved.
**Notes:** The intro CTA fix (`0_intro.py`) still handles the intro → fill_form path. This fix covers all backward navigations via the navbar.

---

### 2026-06-19 — CTA from intro lands on text-fill module instead of mode selector

**Status:** Fixed
**File(s):** `pages/0_intro.py`
**Symptom:** Clicking "Get your score →" on the intro page sometimes opened the text-input (or voice) panel on `2_fill_form.py` directly, skipping the mode selector cards.
**Root cause:** `fill_mode` is guarded with `if "fill_mode" not in st.session_state`, so it keeps whatever value was set on a previous visit. If the user had previously selected text mode, `fill_mode` was already `"text"` when the page re-loaded, causing it to branch past the selector.
**Fix:** Added `st.session_state.fill_mode = None` before `st.switch_page` in `0_intro.py`. Coming from the intro always means a fresh start, so the mode selector should always be shown.
**Notes:** Navigating to `2_fill_form.py` from the breadcrumb (returning to change startup) intentionally preserves `fill_mode` — only the intro CTA resets it.

---

### 2026-06-19 — Voice "Review form →" button never appeared after recording

**Status:** Fixed
**File(s):** `pages/2_fill_form.py`
**Symptom:** After recording voice on `2_fill_form.py`, the "Review form →" button never appeared, leaving voice users stuck on the page with no way to proceed.
**Root cause:** The display condition checked `st.session_state.get("extracted_fields")`, but `voice_input.py` stores extracted data in `pending_voice_update` — not in `extracted_fields`. `extracted_fields` stays `{}` (falsy) throughout the voice flow, so the condition is never True.
**Fix:** Changed the condition to `st.session_state.get("pending_voice_update")`. On click, `extracted_fields` is synced from `pending_voice_update` before switching page so `_init_form_state` in `render_input_form` has a consistent source of truth.
**Notes:** `pending_voice_update` is the sparse-update channel used by voice on the form overview page too — do not replace it with `extracted_fields` inside `voice_input.py`, as that would break partial voice corrections.

---

### 2026-06-19 — Stale voice data overwrote autofill results intermittently

**Status:** Fixed
**File(s):** `src/components/autofill.py`
**Symptom:** After trying voice mode and then switching to autofill (text mode), the form on `3_form_overview.py` showed the voice-extracted values instead of the autofill values — intermittent because it only occurred when the user had previously attempted voice on the same session.
**Root cause:** `render_input_form` pops and applies `pending_voice_update` after `_init_form_state`. If the user tried voice (setting `pending_voice_update`) and then did an autofill lookup without clearing it, the stale voice data overwrote the freshly initialised autofill fields.
**Fix:** Added `st.session_state.pop("pending_voice_update", None)` immediately after `extracted_fields` is set in `render_autofill`. Autofill is a full replacement, so any pending voice state is irrelevant.
**Notes:** The reverse (voice after autofill) is handled correctly — recording new audio overwrites `pending_voice_update`, and clicking "Review form →" re-syncs `extracted_fields`.

---

### [DATE] — Action buttons on Startup Profile page too wide / overflow on small viewports

**Status:** Fixed
**File(s):** `pages/3_form_overview.py`
**Symptom:** The 3 action buttons ("Speak to edit", "Compare startups", "Predict success") overflowed their columns on narrower screens.
**Root cause:** Default Streamlit button sizing does not constrain width or font-size responsively.
**Fix:** Added `font-size: clamp(0.5rem, 1.1vw, 0.875rem)` and responsive padding via `clamp()` to the shared column button selector in `3_form_overview.py`. Added `white-space: nowrap` and `text-overflow: ellipsis` to prevent wrapping. (`demoday10`)
