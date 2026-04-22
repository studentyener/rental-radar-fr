# Modèle de données

## Schéma

```
DateCalendrier
     │ (1)
     │
dvf_all (*) ──── (1) communes_dim
```

## Relations à créer

| De | Vers | Colonne | Cardinalité |
|----|------|---------|-------------|
| dvf_all | DateCalendrier | date_mutation → Date | Plusieurs à un |
| dvf_all | communes_dim | code_commune → code_commune | Plusieurs à un |

## Tables

### dvf_all (table de faits)
Source : `data/processed/dvf_all.parquet`
~1,6 millions de lignes sur 2024-2025.

### communes_dim (dimension)
Source : `data/processed/communes_dim.parquet`
~35 000 communes, 1 ligne par commune.

### DateCalendrier (dimension)
Créée en DAX. Voir `dax_measures.md`.

## Fichiers Power BI
Le fichier `.pbix` n'est pas versionné (trop lourd).
Reconstruire en suivant `dax_measures.md` et `visuals.md`.
