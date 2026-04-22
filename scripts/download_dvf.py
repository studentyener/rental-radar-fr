"""
download_dvf.py
---------------
Télécharge les fichiers DVF géolocalisés depuis data.gouv.fr.

Usage:
    python scripts/download_dvf.py --year 2024 --year 2025
    python scripts/download_dvf.py --all
"""

from __future__ import annotations
import argparse
import sys
from pathlib import Path
from urllib.request import urlretrieve

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
BASE_URL = "https://files.data.gouv.fr/geo-dvf/latest/csv"
AVAILABLE_YEARS = list(range(2019, 2026))


def build_url(year: int) -> str:
    return f"{BASE_URL}/{year}/full.csv.gz"


def download_year(year: int, force: bool = False) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    target = DATA_DIR / f"dvf_{year}.csv.gz"

    if target.exists() and not force:
        size_mb = target.stat().st_size / (1024 * 1024)
        print(f"[skip] {target.name} déjà présent ({size_mb:.1f} Mo). --force pour réécraser.")
        return target

    url = build_url(year)
    print(f"[get ] {url}")

    def progress(blocks, block_size, total_size):
        downloaded = blocks * block_size
        if total_size > 0:
            pct = min(downloaded * 100 / total_size, 100)
            sys.stdout.write(f"\r       {pct:5.1f}% ({downloaded // (1024*1024)} Mo)")
            sys.stdout.flush()

    urlretrieve(url, target, reporthook=progress)
    print(f"\n[ok  ] {target.name}")
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Télécharge les fichiers DVF géolocalisés.")
    parser.add_argument("--year", action="append", type=int, choices=AVAILABLE_YEARS)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.all:
        years = AVAILABLE_YEARS
    elif args.year:
        years = sorted(set(args.year))
    else:
        years = AVAILABLE_YEARS[-2:]
        print(f"[info] Aucune année spécifiée, je prends les 2 plus récentes : {years}")

    for year in years:
        try:
            download_year(year, force=args.force)
        except Exception as exc:
            print(f"[err ] échec pour {year} : {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
