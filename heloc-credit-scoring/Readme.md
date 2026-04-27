# Prédiction du risque crédit HELOC

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![XGBoost](https://img.shields.io/badge/XGBoost-optimisé-orange)](https://xgboost.readthedocs.io/)
[![Streamlit](https://img.shields.io/badge/Streamlit-application-red)](https://streamlit.io/)

## 📌 Présentation du projet

Ce projet vise à prédire si un client sera en **défaut de paiement** sur une ligne de crédit hypothécaire (HELOC) à partir de 23 caractéristiques financières et comportementales.  
Le jeu de données provient du [FICO HELOC Challenge](https://community.fico.com/s/explainable-machine-learning-challenge).  
Nous avons construit un modèle **XGBoost** robuste (AUC = 0,8135) et l’avons déployé dans une application interactive **Streamlit**.

## 🗂️ Jeu de données

- **Source** : FICO (Home Equity Line of Credit)
- **Échantillon** : environ 10 000 clients
- **Cible** : `RiskPerformance` – `"Good"` (pas de défaut) vs `"Bad"` (défaut)
- **Variables** : 23 variables numériques (scores de crédit, ancienneté des comptes, historique de retard, interrogations, ratios d’utilisation, etc.)

**Codes spéciaux** : `-7`, `-8`, `-9` indiquent des valeurs manquantes ou inconnues (par exemple, pas de compte, pas de transaction, inconnu).

## 🔧 Pipeline de prétraitement

1. **Remplacement des codes spéciaux** par `NaN`.
2. **Transformation logarithmique** (`log1p`) sur toutes les variables numériques pour réduire l’asymétrie et compresser les valeurs extrêmes.
3. **Imputation** des `NaN` restants par la **médiane** (par colonne).
4. **Aucune suppression des outliers** – la transformation + la robustesse du modèle les gère.

> ⚠️ L’ordre **Log puis Imputation** est critique et a été appliqué de manière cohérente pendant l’entraînement et l’inférence.

## 🤖 Modélisation et optimisation

Nous avons comparé trois modèles de gradient boosting :
- **XGBoost**
- **LightGBM**
- **Random Forest**

Les trois ont atteint des performances similaires (AUC ~ 0,80). Nous avons sélectionné **XGBoost** et effectué une recherche d’hyperparamètres par **GridSearchCV** (validation croisée stratifiée 5 plis, métrique ROC‑AUC).

### Meilleurs hyperparamètres trouvés
```python
{
    'colsample_bytree': 0.8,
    'learning_rate': 0.05,
    'max_depth': 4,
    'n_estimators': 100,
    'subsample': 0.8
}



Performance
AUC moyenne (validation croisée) : 0,8017

AUC sur le test : 0,8135 (gain de +1,3 % par rapport au modèle par défaut)



