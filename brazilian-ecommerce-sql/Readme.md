# Analyse de données – Brazilian Ecommerce (SQL Avancé)

## 📌 Description du projet

Ce projet a été réalisé dans le cadre du **DataScienceChallenge – Semaine 2 : SQL Avancé & Base de Données**.  
L’objectif est de créer une base de données relationnelle à partir du jeu de données **Brazilian Ecommerce** (disponible sur Kaggle) et d’écrire une série de requêtes SQL avancées pour répondre à des questions métier :

- Répartition des commandes
- Fidélisation clients
- Performance des vendeurs
- Produits « premium » par catégorie
- Analyse logistique (délais de livraison)
- Tendances temporelles et satisfaction client

Toutes les requêtes sont exécutables sur **SQL Server Management Studio (SSMS)**.

---

## 📁 Contenu du dépôt

- `DSC_SQL_Scripts.sql` – Fichier principal contenant l’ensemble des requêtes SQL (agrégations, jointures, sous‑requêtes, CTE, fonctions de fenêtrage)
- `README.md` – Ce fichier.

---

## 🗃️ Base de données utilisée

**Source** : [Brazilian Ecommerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)  

**Tables principales** :
- `olist_orders_dataset` – commandes
- `olist_order_items_dataset` – articles commandés
- `olist_products_dataset` – produits
- `olist_sellers_dataset` – vendeurs
- `olist_customers_dataset` – clients
- `olist_order_payments_dataset` – paiements
- `olist_order_reviews_dataset` – avis clients

> **Note** : Le script suppose que ces tables ont été importées dans une base SQL Server

---

## 🚀 Installation et exécution

### 1. Prérequis
- SQL Server (2016 ou supérieur recommandé)
- SQL Server Management Studio (SSMS) ou tout autre client SQL compatible.
- Les données doivent être importées dans une base nommée `Brazilian_DB` (ou adaptez le nom dans les requêtes).

### 2. Importation des données
Téléchargez les fichiers CSV depuis Kaggle, puis utilisez l’**Assistant Importation et Exportation** de SQL Server (`Tasks` → `Import Data`) pour créer les tables et y insérer les données.

### 3. Exécution des requêtes
- Ouvrez le fichier `DSC_SQL_Scripts.sql` dans SSMS.
- Vérifiez que le nom de la base de données correspond (en haut à gauche, sélectionnez la bonne base).
- Exécutez les requêtes une par une (ou sélectionnez des blocs spécifiques).

> **Remarque** : Les index suggérés sont facultatifs mais fortement recommandés pour améliorer les performances sur de gros volumes de données et doivent être exécutés un à un juste après l'importation des fichiers.

---

## 📊 Aperçu des requêtes

| Catégorie | Exemple de requête |
|-----------|--------------------|
| Analyses générales | Nombre de commandes par statut, clients fidèles (>2 commandes) |
| Segmentation clients | Montant total dépensé par client (seuil > 5000 R$) |
| Produits premium | Produits dont le prix > moyenne de leur catégorie |
| Vendeurs performants | Vendeurs avec CA > moyenne des vendeurs |
| Classements | Catégories les plus vendues (RANK), grosses commandes par mois |
| Logistique | Délai moyen de livraison par état du vendeur et par catégorie de produit |
| Tendances | Évolution mensuelle des ventes, notes moyennes par catégorie |
| Window functions | Différence de prix entre produits d’une même commande (LAG) |

---

## 🔧 Optimisation (index)

Les index suivants sont proposés pour accélérer les jointures fréquentes :

```sql
CREATE INDEX idx_orders_customer ON olist_orders_dataset(customer_id);
CREATE INDEX idx_items_order ON olist_order_items_dataset(order_id);
CREATE INDEX idx_items_product ON olist_order_items_dataset(product_id);
CREATE INDEX idx_payments_order ON olist_order_payments_dataset(order_id);
CREATE INDEX idx_reviews_order ON olist_order_reviews_dataset(order_id);
