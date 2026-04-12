# Projet 1/10 : Analyse Exploratoire du Titanic (EDA)

## Objectif
Ce projet est le premier d’un défi personnel de 10 semaines en data science. L’objectif est de maîtriser les bases de l’analyse exploratoire de données (EDA) : nettoyage, visualisation, interprétation.

## Jeu de données
Le dataset Titanic (Kaggle) contient des informations sur 891 passagers : âge, sexe, classe, tarif, nombre de proches à bord, port d’embarquement, et la variable cible `Survived`.

## Étapes réalisées
1. **Chargement et inspection** des données (`df.info()`, `df.describe()`)
2. **Nettoyage** :
   - Valeurs manquantes d’âge : remplacées par la médiane
   - Cabine (Cabin) : remplacée par `"Unknown"`
   - Port d’embarquement (Embarked) : suppression des 2 lignes manquantes
3. **Traitement des outliers** : conservation des valeurs extrêmes (âges élevés, tarifs très chers) car réelles et plausibles
4. **Analyse exploratoire** :
   - Statistiques descriptives
   - Visualisations avec `matplotlib` et `seaborn`
   - Matrice de corrélation après encodage des variables catégorielles
5. **Tableaux récapitulatifs** : effectifs et pourcentages par variable

## Principales conclusions
- **Sexe** : 75 % des femmes ont survécu, contre 20 % des hommes
- **Classe** : 63 % de survie en 1ʳᵉ classe, 24 % en 3ᵉ classe
- **Âge** : les enfants (0‑10 ans) ont survécu à 75 %, les personnes âgées (+60 ans) à moins de 20 %
- **Tarif** : corrélation positive avec la survie (0,26)
- **Taille de la famille** : les passagers seuls ou avec peu de proches ont mieux survécu

## Graphiques produits
- `countplot` avec pourcentages pour les variables catégorielles
- Boxplot et histogramme pour `Age` et `Fare`
- Heatmap des corrélations

## Technologies utilisées
- Python 3
- pandas, numpy, matplotlib, seaborn
