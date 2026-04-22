"""
enrich_with_insee.py
--------------------
Enrichit les données communales et prépare les fichiers pour Power BI.
"""

from __future__ import annotations
from pathlib import Path
import pandas as pd

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
EXTERNAL_DIR = Path(__file__).resolve().parent.parent / "data" / "external"

LOYERS_PAR_ZONE = {
    "Abis": {"min": 18.0, "median": 22.0, "max": 28.0},
    "A":    {"min": 14.0, "median": 17.0, "max": 22.0},
    "B1":   {"min": 11.0, "median": 13.5, "max": 16.5},
    "B2":   {"min": 8.5,  "median": 10.5, "max": 13.0},
    "C":    {"min": 7.0,  "median": 9.0,  "max": 11.5},
}


def load_dvf_aggregated() -> pd.DataFrame:
    df = pd.read_parquet(PROCESSED_DIR / "dvf_all.parquet")
    agg = (
        df.groupby(["code_commune", "nom_commune", "code_departement", "type_local"])
        .agg(
            nb_ventes=("id_mutation", "count"),
            prix_m2_median=("prix_m2", "median"),
            prix_m2_q1=("prix_m2", lambda s: s.quantile(0.25)),
            prix_m2_q3=("prix_m2", lambda s: s.quantile(0.75)),
            surface_mediane=("surface_reelle_bati", "median"),
        )
        .round(0)
        .reset_index()
    )
    return agg


def attach_pinel_zone(df_communes: pd.DataFrame) -> pd.DataFrame:
    pinel_path = EXTERNAL_DIR / "zonage_pinel.csv"
    if not pinel_path.exists():
        print(f"[warn] {pinel_path} introuvable. Zone Pinel ignorée.")
        df_communes["zone_pinel"] = pd.NA
        return df_communes
    pinel = pd.read_csv(pinel_path, dtype={"code_commune": "string"})
    return df_communes.merge(pinel, on="code_commune", how="left")


def estimate_loyer(df: pd.DataFrame) -> pd.DataFrame:
    df["loyer_m2_min"] = df["zone_pinel"].map(lambda z: LOYERS_PAR_ZONE.get(z, {}).get("min"))
    df["loyer_m2_median"] = df["zone_pinel"].map(lambda z: LOYERS_PAR_ZONE.get(z, {}).get("median"))
    df["loyer_m2_max"] = df["zone_pinel"].map(lambda z: LOYERS_PAR_ZONE.get(z, {}).get("max"))
    return df


def compute_rendement_brut(df: pd.DataFrame) -> pd.DataFrame:
    df["loyer_mensuel_estime"] = (
        pd.to_numeric(df["loyer_m2_median"], errors="coerce") *
        pd.to_numeric(df["surface_mediane"], errors="coerce")
    ).round(0)
    df["prix_achat_estime"] = (df["prix_m2_median"] * df["surface_mediane"]).round(0)
    df["rendement_brut"] = (
        (df["loyer_mensuel_estime"] * 12) / df["prix_achat_estime"] * 100
    ).round(2)
    return df


def make_communes_dim(df: pd.DataFrame) -> pd.DataFrame:
    """Crée une table avec une seule ligne par commune pour Power BI."""
    df_unique = df.groupby("code_commune").agg({
        "nom_commune": "first",
        "code_departement": "first",
        "prix_m2_median": "mean",
        "nb_ventes": "sum",
        "surface_mediane": "mean",
        "prix_achat_estime": "mean",
        "rendement_brut": "mean"
    }).reset_index()
    for col in df_unique.select_dtypes(include=["object"]).columns:
        df_unique[col] = df_unique[col].astype(str)
    return df_unique


def main() -> None:
    EXTERNAL_DIR.mkdir(parents=True, exist_ok=True)

    print("[1/5] Agrégation DVF par commune...")
    communes = load_dvf_aggregated()

    print("[2/5] Rattachement zonage Pinel...")
    communes = attach_pinel_zone(communes)

    print("[3/5] Estimation des loyers...")
    communes = estimate_loyer(communes)

    print("[4/5] Calcul du rendement brut...")
    communes = compute_rendement_brut(communes)

    out = PROCESSED_DIR / "communes_enrichies.parquet"
    communes.to_parquet(out, index=False, compression="snappy")
    print(f"\n[ok  ] {out.name} - {len(communes):,} lignes (commune × type_local)")

    print("[5/5] Création table dimension communes (1 ligne par commune)...")
    communes_dim = make_communes_dim(communes)
    out_dim = PROCESSED_DIR / "communes_dim.parquet"
    communes_dim.to_parquet(out_dim, index=False, compression="snappy")
    print(f"[ok  ] {out_dim.name} - {len(communes_dim):,} communes uniques")

    print("\nTop 10 communes par nb de ventes :")
    top = communes_dim.nlargest(10, "nb_ventes")[["nom_commune", "code_departement", "prix_m2_median", "nb_ventes"]]
    print(top.to_string(index=False))


if __name__ == "__main__":
    main()
