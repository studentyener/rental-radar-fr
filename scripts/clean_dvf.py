"""
clean_dvf.py
------------
Lit les CSV bruts DVF, filtre, normalise, et écrit un parquet propre.
"""

from __future__ import annotations
import gzip
from pathlib import Path
import pandas as pd

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"

COLUMNS_TO_KEEP = [
    "id_mutation", "date_mutation", "valeur_fonciere",
    "code_postal", "code_commune", "nom_commune", "code_departement",
    "type_local", "surface_reelle_bati", "nombre_pieces_principales",
    "longitude", "latitude", "nature_mutation",
]

VALID_TYPES = {"Maison", "Appartement"}
VALID_NATURES = {"Vente"}


def load_year(path: Path) -> pd.DataFrame:
    print(f"[read] {path.name}")
    with gzip.open(path, "rt", encoding="utf-8") as f:
        df = pd.read_csv(
            f, usecols=COLUMNS_TO_KEEP,
            dtype={"code_postal": "string", "code_commune": "string", "code_departement": "string"},
            parse_dates=["date_mutation"], low_memory=False,
        )
    print(f"       {len(df):,} lignes brutes")
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    n0 = len(df)
    df = df[df["nature_mutation"].isin(VALID_NATURES)]
    df = df[df["type_local"].isin(VALID_TYPES)]
    df = df.dropna(subset=["valeur_fonciere", "surface_reelle_bati", "code_commune"])
    df = df[df["valeur_fonciere"].between(10_000, 5_000_000)]
    df = df[df["surface_reelle_bati"].between(9, 500)]
    df = (df.sort_values("surface_reelle_bati", ascending=False)
            .drop_duplicates(subset=["id_mutation"], keep="first"))
    df["prix_m2"] = (df["valeur_fonciere"] / df["surface_reelle_bati"]).round(0)
    df = df[df["prix_m2"].between(200, 25_000)]
    print(f"       {len(df):,} lignes après nettoyage ({(1 - len(df) / n0) * 100:.1f}% écartées)")
    return df


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(RAW_DIR.glob("dvf_*.csv.gz"))
    if not files:
        print("Aucun fichier DVF trouvé dans data/raw/. Lance d'abord download_dvf.py.")
        return

    all_years = []
    for path in files:
        df = load_year(path)
        df = clean(df)
        out = PROCESSED_DIR / f"{path.stem.replace('.csv', '')}.parquet"
        df.to_parquet(out, index=False, compression="snappy")
        print(f"[ok  ] {out.name} ({out.stat().st_size // 1024} Ko)")
        all_years.append(df)

    full = pd.concat(all_years, ignore_index=True)
    full_out = PROCESSED_DIR / "dvf_all.parquet"
    full.to_parquet(full_out, index=False, compression="snappy")
    print(f"[ok  ] {full_out.name} - {len(full):,} mutations au total")


if __name__ == "__main__":
    main()
