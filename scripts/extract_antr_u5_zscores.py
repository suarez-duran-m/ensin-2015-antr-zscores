"""
Extract sex, age, weight, height, WHZ, WAZ, HAZ and BMI for children under 5
from the ANTR (ANTROPOMETRIA) table, keeping the flagAnthro/flagPlus columns
so flagged (implausible/missing) Z-scores can be audited rather than silently
dropped.

Requires: pandas (pip install pandas)
"""

import argparse
from pathlib import Path

import pandas as pd

DTA_PATH = Path(__file__).resolve().parent.parent / "Formato_Stata" / "ANTROPOMETRIA.DTA"

SEX_LABELS = {1: "male", 2: "female"}

# ANTR.departamento stores the 1-based position in the dictionary's DANE-code-ordered
# domain list (1 -> DANE 05, 2 -> DANE 08, ...), not the DANE code itself and not the
# same order as PTS.departa. Verified by cross-tabulating against the Region field.
DEPARTAMENTO_NAMES = {
    1: "Antioquia",
    2: "Atlántico",
    3: "Bogotá D.C.",
    4: "Bolívar",
    5: "Boyacá",
    6: "Caldas",
    7: "Caquetá",
    8: "Cauca",
    9: "Cesar",
    10: "Córdoba",
    11: "Cundinamarca",
    12: "Chocó",
    13: "Huila",
    14: "La Guajira",
    15: "Magdalena",
    16: "Meta",
    17: "Nariño",
    18: "Norte de Santander",
    19: "Quindío",
    20: "Risaralda",
    21: "Santander",
    22: "Sucre",
    23: "Tolima",
    24: "Valle del Cauca",
    25: "Arauca",
    26: "Casanare",
    27: "Putumayo",
    28: "San Andrés y Providencia",
    29: "Amazonas",
    30: "Guainía",
    31: "Guaviare",
    32: "Vaupés",
    33: "Vichada",
}

# pandas/Stata decode Subregion with a latin-1 fallback (see UnicodeWarning on load),
# but one source value ("Nariño") has a corrupted byte upstream in the .dta itself that
# no encoding fixes cleanly. The other 15 values decode fine but were stored unaccented
# by the survey team (e.g. "Bogota", "Medellin"). This maps every raw value to a clean,
# correctly accented display name so both problems disappear.
SUBREGION_NAMES = {
    "Antioquia sin Medellin": "Antioquia sin Medellín",
    "Atlantico, San Andres, Bolivar Norte": "Atlántico, San Andrés, Bolívar Norte",
    "Barranquilla A. M.": "Barranquilla A.M.",
    "Bogota": "Bogotá",
    "Bolivar Sur, Sucre, Cordoba": "Bolívar Sur, Sucre, Córdoba",
    "Boyaca, Cmarca, Meta": "Boyacá, Cundinamarca, Meta",
    "Caldas, Risaralda, Quindio": "Caldas, Risaralda, Quindío",
    "Cali A.M.": "Cali A.M.",
    "Cauca y Nari+\xa6o sin Litoral": "Cauca y Nariño sin Litoral",
    "Guajira, Cesar, Magdalena": "La Guajira, Cesar, Magdalena",
    "Litoral Pacifico": "Litoral Pacífico",
    "Medellin A.M.": "Medellín A.M.",
    "Orinoquia y Amazonia": "Orinoquía y Amazonía",
    "Santanderes": "Santanderes",
    "Tolima, Huila, Caqueta": "Tolima, Huila, Caquetá",
    "Valle sin Cali ni Litoral": "Valle sin Cali ni Litoral",
}


def clean_subregion(series: pd.Series) -> pd.Series:
    stripped = series.astype(str).str.strip()
    mapped = stripped.map(SUBREGION_NAMES)
    return mapped.fillna(stripped)


COLUMNS = [
    "LLAVE_PERSONA",
    "ANTSEXO",
    "AN_EDAD",
    "AN_EDADM",
    "AN_7",
    "AN_8",
    "WHZ",
    "WAZ",
    "HAZ",
    "AN_IMC",
    "BAZ",
    "flagAnthro",
    "flagPlus",
    "Region",
    "Subregion",
    "departamento",
    "area",
    "cabecera",
    "cuartil_riqueza2015",
    "AN_13",
]

RENAME = {
    "ANTSEXO": "sex",
    "AN_EDAD": "age_years",
    "AN_EDADM": "age_months",
    "AN_7": "weight_kg",
    "AN_8": "height_cm",
    "AN_IMC": "bmi",
    "Region": "region",
    "Subregion": "subregion",
    "departamento": "departamento",
    "area": "area",
    "cabecera": "zona",
    "cuartil_riqueza2015": "cuartil_riqueza",
    "AN_13": "fecha_medicion",
}


def extract(dta_path: Path = DTA_PATH, max_age_years: int = 5) -> pd.DataFrame:
    df = pd.read_stata(dta_path, columns=COLUMNS, convert_categoricals=False)

    df["flagAnthro"] = df["flagAnthro"].str.strip()
    df["flagPlus"] = df["flagPlus"].str.strip()

    under5 = df[df["AN_EDAD"] < max_age_years].copy()
    under5 = under5.rename(columns=RENAME)
    under5["sex"] = under5["sex"].map(SEX_LABELS)
    under5["departamento_nombre"] = under5["departamento"].map(DEPARTAMENTO_NAMES)
    under5["subregion"] = clean_subregion(under5["subregion"])

    flag_cols = ["WHZ", "WAZ", "HAZ"]
    under5["n_flags"] = under5["flagAnthro"].apply(
        lambda f: 0 if f == "" else len([x for x in f.replace(".", ",").split(",") if x.strip()])
    )

    return under5[
        [
            "LLAVE_PERSONA",
            "sex",
            "age_years",
            "age_months",
            "weight_kg",
            "height_cm",
            "WHZ",
            "WAZ",
            "HAZ",
            "bmi",
            "flagAnthro",
            "n_flags",
            "region",
            "subregion",
            "departamento",
            "departamento_nombre",
            "area",
            "zona",
            "cuartil_riqueza",
            "fecha_medicion",
        ]
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dta", type=Path, default=DTA_PATH, help="Path to ANTROPOMETRIA.DTA")
    parser.add_argument("--out", type=Path, default=None, help="Output CSV path (default: print summary only)")
    parser.add_argument("--max-age-years", type=int, default=5, help="Exclusive upper age bound in years")
    args = parser.parse_args()

    table = extract(args.dta, args.max_age_years)

    print(f"Extracted {len(table)} children under {args.max_age_years} years")
    print(f"  clean (no flags):    {(table['n_flags'] == 0).sum()}")
    print(f"  with >=1 flag:       {(table['n_flags'] > 0).sum()}")
    print()
    print(table.head(10).to_string(index=False))

    if args.out:
        table.to_csv(args.out, index=False)
        print(f"\nSaved to {args.out}")


if __name__ == "__main__":
    main()
