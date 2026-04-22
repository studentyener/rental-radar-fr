# Mesures DAX — Rental Radar FR

Toutes les mesures utilisées dans le dashboard, organisées par dossier.

---

## Dossier : Base

```dax
NbVentes = COUNTROWS ( dvf_all )
```

```dax
PrixMedian = MEDIAN ( dvf_all[valeur_fonciere] )
```

```dax
PrixM2Median = MEDIAN ( dvf_all[prix_m2] )
```

```dax
SurfaceMediane = MEDIAN ( dvf_all[surface_reelle_bati] )
```

---

## Dossier : Évolution

```dax
EvolutionPrixYoY =
DIVIDE (
    [PrixM2Median] - CALCULATE ( [PrixM2Median], SAMEPERIODLASTYEAR ( DateCalendrier[Date] ) ),
    CALCULATE ( [PrixM2Median], SAMEPERIODLASTYEAR ( DateCalendrier[Date] ) )
)
```

---

## Dossier : Rentabilité

```dax
RendementBrut = DIVIDE ( [PrixM2Median] * 12, [PrixMedian] )
```

```dax
ScoreAttractivite = DIVIDE ( [RendementBrut] * 100, 1 )
```

---

## Table Date (à créer via Modélisation → Nouvelle table)

```dax
DateCalendrier =
ADDCOLUMNS (
    CALENDAR ( DATE ( 2014, 1, 1 ), DATE ( 2026, 12, 31 ) ),
    "Année",       YEAR ( [Date] ),
    "Mois",        MONTH ( [Date] ),
    "Mois nom",    FORMAT ( [Date], "MMMM" ),
    "Trimestre",   "T" & FORMAT ( [Date], "Q" ),
    "AnnéeMois",   FORMAT ( [Date], "YYYY-MM" )
)
```

Après création → clic droit → **"Marquer comme table de dates"** → colonne `Date`.
