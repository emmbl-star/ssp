# Style Guide

## Color Tokens

| Token | Hex | Usage |
|---|---|---|
| `ACCENT` | `#1C95FF` | Primary CTA buttons, active breadcrumb, progress bar, focus rings |
| `ACCENT_HOVER` | `#0B80E8` | Primary button hover state |
| `ACCENT_ORANGE` | `#F87F19` | Secondary CTA buttons (e.g. "Compare startups"), form submit accent |
| `#111827` | — | Body text, headings, labels |
| `#6B7280` | — | Subtitles, helper text |
| `#9CA3AF` | — | Placeholders, inactive breadcrumb links |
| `#374151` | — | Back button text, mid-weight labels |
| `#E5E7EB` | — | Borders, dividers, inactive progress track |
| `#F9FAFB` | — | App background on full-width pages |
| `#ffffff` | — | Card backgrounds, navbar background |

All tokens are defined in `src/components/navigation.py`.

---

## Typography

| Class | Size | Weight | Use |
|---|---|---|---|
| `.page-title` | `1.375rem` | 700 | Standard page heading |
| `.page-title-xl` | `2.5rem` | 800 | Full-width page heading (compare page) |
| `.page-subtitle` | `0.875rem` | 400 | Subheading below page title |
| `.page-lead` | `1.14rem` | 600 | Lead paragraph |
| `.cmp-card-title` | `18px` | 700 | Card title inside startup comparison cards |
| `.cmp-section-header` | `14px` | 700 | Section label inside a card column |
| `.cmp-stepper-label` | `18px` | 700 | Label above the stepper input |

All classes are injected via `GLOBAL_CSS` in `navigation.py`, available on every page that calls `render_page_navbar`.

---

## Buttons

### Primary (blue)
- Targets: `button[kind="primary"]`
- Background: `#1C95FF`, hover `#0B80E8`
- Border radius: `16px`
- Padding: `0.9rem 2rem`
- Shadow: `0 4px 14px rgba(43,133,228,0.35)`
- Use for: main forward-flow CTAs ("Get your score →", "Predict success")

### Secondary form submit (orange)
- Targets: `button[kind="secondaryFormSubmit"]`
- Background: `#F87F19`, hover `#E07010`
- Same radius/padding as primary
- Use for: "Compare startups" form actions

### Compare page buttons (orange, flat)
- All `stButton` on the compare page are overridden to `#F87F19`
- `border-radius: 8px`, `padding: 10px 20px` — compact style
- Download / upload / expander buttons use white + `#E5E7EB` border

### Form overview action row (3-button bar)
- Uses column-position `:nth-child` CSS in `3_form_overview.py`
- col 1 → white/outline (voice)
- col 2 → orange `#F87F19` (compare)
- col 3 → blue `#1C95FF` (predict)
- All buttons in this row are locked to `border-radius: 8px` via the shared selector

> Do not change the column order of the 3-button row — the CSS targeting is position-dependent.

---

## Layout

### Card layout (default)
Applied by `render_page_navbar` to all pages unless `full_width=True`.

```
max-width: calc(100% - 160px)
margin: 115px auto 2rem
padding: 2rem 2.5rem
background: #ffffff
border-radius: 16px
border: 1px solid #E5E7EB
box-shadow: 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -1px rgba(0,0,0,0.04)
```

Pages using it: Home, Startup Picker, Startup Profile, Decision Center

### Narrow card override (Startup Picker)
`2_fill_form.py` overrides `max-width: 760px` with a slightly different shadow.

### Full-width layout
Activated with `render_page_navbar(..., full_width=True)`.

```
.stApp background: #F9FAFB
max-width: 100%
margin: 72px 0 0
padding: 64px
background: transparent
border: none / box-shadow: none
```

Pages using it: Portfolio Builder (`4_compare.py`)

---

## Navbar

- Fixed top bar, `height: 56px`, `z-index: 9999`
- Logo left-aligned (`28px` tall SVG)
- Breadcrumb floated to center via CSS `:has([data-testid="stPageLink"])`
- Optional back button right-aligned (`.ssp-back-btn`)
- Progress strip: 3px bar rendered via `::after` pseudo-element below the navbar
- Rendered by `render_page_navbar()` in `navigation.py`

---

## Form Inputs

All inputs get a clean white box style via `GLOBAL_CSS`:
- Background: `#ffffff`, border: `1px solid #E5E7EB`, radius: `8px`
- Focus: border `#1C95FF`, box-shadow `0 0 0 3px rgba(28,149,255,0.12)`
- Text: `#111827`, placeholder: `#9CA3AF`, font-size: `0.9rem`
- Applies to: `stTextInput`, `stNumberInput`, `stSelectbox`

---

## Mode Cards (Startup Picker)

- Icon wrap: `56×56px`, background `#DBEAFE`, `border-radius: 12px`
- Title: `15px / 700`
- Description: `13px / #6B7280`
- Hover state: background `#EFF6FF`, border `#93C5FD`, text `#1C95FF`
