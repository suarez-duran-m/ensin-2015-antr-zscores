# ENSIN 2015 — ANTR Z-score extraction

Code-only companion to the **ENSIN 2015** (Encuesta Nacional de la Situación
Nutricional en Colombia 2015) public data repository. This repo contains a
single script that extracts anthropometric Z-scores and related fields from
the `ANTR` (ANTROPOMETRIA) table, plus the project's `CLAUDE.md` reference
notes on the dataset.

**No survey data is included here.** The `.dta`/`.TXT`/`.bak` files this
script reads must be obtained separately from the ENSIN 2015 public data
release and are not committed to this repo (see `.gitignore`).

## What it does

`scripts/extract_antr_u5_zscores.py` reads `Formato_Stata/ANTROPOMETRIA.DTA`
and produces a clean table with, per child:

| Column | Source | Notes |
|---|---|---|
| `LLAVE_PERSONA` | `LLAVE_PERSONA` | Individual identifier |
| `sex` | `ANTSEXO` | `male` / `female` |
| `age_years`, `age_months` | `AN_EDAD`, `AN_EDADM` | |
| `weight_kg`, `height_cm` | `AN_7`, `AN_8` | |
| `WHZ`, `WAZ`, `HAZ` | `WHZ`, `WAZ`, `HAZ` | WHO Anthro Z-scores (weight/height/age), ages 0–5 |
| `bmi` | `AN_IMC` | |
| `flagAnthro`, `n_flags` | `flagAnthro` | Which Z-score(s) were suppressed as implausible/missing, and how many |
| `region`, `subregion` | `Region`, `Subregion` | Subregion names are cleaned — the source `.dta` stores most of them unaccented and one ("Nariño") with a corrupted byte |
| `departamento`, `departamento_nombre` | `departamento` | Numeric code mapped to its department name (see script for the code table and how it was derived) |
| `area`, `zona` | `area`, `cabecera` | Urban/rural classification |
| `cuartil_riqueza` | `cuartil_riqueza2015` | National wealth quartile (1=poorest–4=richest) |
| `fecha_medicion` | `AN_13` | Date of anthropometric measurement |

Z-scores flagged as biologically implausible or missing raw measurements are
left as `NaN` in `WHZ`/`WAZ`/`HAZ` (that's how the source data already
represents them) — `flagAnthro`/`n_flags` let you audit which ones were
excluded instead of silently dropping rows.

## Requirements

```bash
pip install pandas
```

## Usage

Place `ANTROPOMETRIA.DTA` under `Formato_Stata/` relative to this repo (or
pass `--dta` with a different path), then:

```bash
# Children under 5 (default), print a summary
python3 scripts/extract_antr_u5_zscores.py

# Save to CSV
python3 scripts/extract_antr_u5_zscores.py --out antr_u5.csv

# Change the age cutoff (e.g. all minors, under 18)
python3 scripts/extract_antr_u5_zscores.py --max-age-years 18 --out antr_u18.csv

# Point at a different file location
python3 scripts/extract_antr_u5_zscores.py --dta /path/to/ANTROPOMETRIA.DTA
```

## Project reference

See [`CLAUDE.md`](CLAUDE.md) for notes on the full ENSIN 2015 database
structure, key tables, and common fields.
