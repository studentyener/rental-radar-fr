# Méthodologie

## Filtrage des transactions DVF

| Filtre | Justification |
|--------|---------------|
| `nature_mutation == "Vente"` | Exclut échanges, expropriations |
| `type_local in ["Maison", "Appartement"]` | Exclut locaux commerciaux |
| `valeur_fonciere >= 10 000` | Exclut donations déguisées |
| `valeur_fonciere <= 5 000 000` | Exclut hôtels particuliers |
| `9 <= surface <= 500` | Surface minimum loi décence |
| `200 <= prix_m2 <= 25 000` | Garde-fou outliers |

## Choix de la médiane
J'utilise systématiquement la médiane et pas la moyenne. Sur DVF, la moyenne est biaisée par les ventes de luxe. Sur Paris 8e par exemple, la moyenne sort à 14 200 €/m² alors que la médiane est à 11 500 €/m².

## Estimation des loyers
Proxy : fourchettes de loyers indicatifs par zone Pinel (Abis, A, B1, B2, C). Calibrées sur les observatoires officiels des loyers 2025 pour les principales agglomérations. Écart moyen constaté : 8 %.

## Rendement brut
```
Rendement brut = (Loyer mensuel × 12) / Prix d'achat
```

## Limites
- DVF n'inclut pas l'Alsace, la Moselle ni Mayotte
- Données avec 6 mois de retard (publication semestrielle)
- Loyers estimés, pas mesurés
- Pas de prédiction : outil descriptif uniquement
