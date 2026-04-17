
/*

PROJET : DataScienceChallenge – Semaine 2 : SQL Avancé & Base de Données
AUTEUR : DAKOU Koudjo
BASE   : Brazilian Ecommerce (SQL Server Management Studio)

OBJECTIF DU SCRIPT :
- Créer et interroger une base de données relationnelle à partir du jeu de données
  Brazilian Ecommerce.
- Mettre en œuvre des requêtes SQL avancées : jointures, agrégations, sous-requêtes,
  fonctions de fenêtrage, CTE, vues et index (les index sont à exécuter séparément).
- Répondre à des questions métier : fidélité clients, performance vendeurs,
  logistique, produits premium, tendances temporelles.

STRUCTURE :
1. Analyses générales (statuts commandes, clients fidèles)
2. Détail commande et segmentation clients
3. Produits premium et vendeurs performants
4. Classements (catégories, commandes mensuelles)
5. Tendances temporelles et avis produits
6. Requêtes complémentaires (top produits, écarts de prix)

*/



/* 
   1. ANALYSES GÉNÉRALES
      ------------------  */

-- 1.1 Compter le nombre total de commandes par statut
-- Objectif : Comprendre la répartition des commandes (livrées, annulées, en attente…)
-- Usage : Dashboard opérationnel, suivi des livraisons.
SELECT order_status, COUNT(*) AS Nb_commande
FROM olist_orders_dataset
GROUP BY order_status
ORDER BY Nb_commande DESC;


-- 1.2 Lister les clients qui ont passé plus de 2 commandes
-- Objectif : Identifier les clients fidèles (répétitifs) pour des actions de fidélisation.
-- Seuil > 2 (ajustable). Utilise HAVING pour filtrer après agrégation.
SELECT customer_id, COUNT(order_id) AS nb_commandes
FROM olist_orders_dataset
GROUP BY customer_id
HAVING COUNT(order_id) > 2
ORDER BY nb_commandes DESC;


/* 
   2. DÉTAIL D'UNE COMMANDE ET SEGMENTATION CLIENTS
      ---------------------------------------------  */

-- 2.1 Détail d’une commande spécifique : produits, vendeurs, prix
-- Objectif : Analyser le contenu d’une commande et la performance des vendeurs.
-- Jointure de 4 tables pour obtenir une vue complète.
-- La commande exemple est identifiée par son order_id.
SELECT o.order_id, p.product_category_name, i.price, i.freight_value, s.seller_city
FROM olist_orders_dataset o
JOIN olist_order_items_dataset i ON o.order_id = i.order_id
JOIN olist_products_dataset p ON i.product_id = p.product_id
JOIN olist_sellers_dataset s ON i.seller_id = s.seller_id
WHERE o.order_id = 'a4591c265e18cb1dcee52889e2d8acc3';


-- 2.2 Montant total dépensé par client (seuil > 5000 R$)
-- Objectif : Segmenter les clients par valeur (RFM simplifié).
-- Utilisé pour : cibler les clients VIP (campagne marketing).
-- La colonne payment_value a été convertie en FLOAT au préalable (voir script préparatoire).
SELECT c.customer_unique_id, SUM(p.payment_value) AS total_depense
FROM olist_customers_dataset c
JOIN olist_orders_dataset o ON c.customer_id = o.customer_id
JOIN olist_order_payments_dataset p ON o.order_id = p.order_id
GROUP BY c.customer_unique_id
HAVING SUM(p.payment_value) > 5000
ORDER BY total_depense DESC;


/* 
   3. PRODUITS PREMIUM ET VENDEURS PERFORMANTS
      ---------------------------------------- */

-- 3.1 Produits dont le prix est supérieur à la moyenne de leur catégorie
-- Objectif : Identifier les produits « premium » au sein de chaque catégorie.
-- Sous-requête corrélée : calcule la moyenne par catégorie et compare.
-- Attention : les catégories sans aucun produit dans order_items ne remontent pas.
SELECT product_category_name, price
FROM olist_order_items_dataset i
JOIN olist_products_dataset p ON i.product_id = p.product_id
WHERE price > (
    SELECT AVG(price)
    FROM olist_order_items_dataset i2
    JOIN olist_products_dataset p2 ON i2.product_id = p2.product_id
    WHERE p2.product_category_name = p.product_category_name
);


-- 3.2 Vendeurs ayant réalisé un chiffre d'affaires supérieur à la moyenne des vendeurs
-- Objectif : Repérer les vendeurs les plus performants (pour partenariats ou récompenses).
-- Utilisation d'une sous-requête dans le HAVING qui calcule la moyenne des CA par vendeur.
-- Note : l'alias ca_ventes représente le chiffre d'affaires total par vendeur.
SELECT seller_id, SUM(price) AS ca_ventes
FROM olist_order_items_dataset
GROUP BY seller_id
HAVING SUM(price) > (
    SELECT AVG(ca_ventes)
    FROM (SELECT seller_id, SUM(price) AS ca_ventes
          FROM olist_order_items_dataset
          GROUP BY seller_id) AS sub
);


/* 
   4. CLASSEMENTS ET FENÊTRAGE
   ---------------------------- */

-- 4.1 Classement des catégories de produits par nombre de ventes (CTE + RANK)
-- Objectif : Connaître les catégories les plus populaires.
-- La CTE ventes_categorie agrège d'abord les ventes par catégorie.
-- RANK() attribue un rang (ex æquo possible).
WITH ventes_categorie AS (
    SELECT p.product_category_name, COUNT(i.order_id) AS nb_ventes
    FROM olist_order_items_dataset i
    JOIN olist_products_dataset p ON i.product_id = p.product_id
    GROUP BY p.product_category_name
)
SELECT product_category_name, nb_ventes,
       RANK() OVER (ORDER BY nb_ventes DESC) AS classement
FROM ventes_categorie;


-- 4.2 Délai moyen de livraison par état du vendeur (CTE)
-- Objectif : Évaluer la performance logistique par région.
-- La CTE delivery_time calcule le délai en jours pour chaque ligne de commande.
-- AVG et GROUP BY par état. Seules les commandes livrées sont prises en compte.
WITH delivery_time AS (
    SELECT s.seller_state,
           DATEDIFF(DAY, o.order_purchase_timestamp, o.order_delivered_customer_date) AS delai_jours
    FROM olist_orders_dataset o
    JOIN olist_order_items_dataset i ON o.order_id = i.order_id
    JOIN olist_sellers_dataset s ON i.seller_id = s.seller_id
    WHERE o.order_delivered_customer_date IS NOT NULL
)
SELECT seller_state, AVG(delai_jours) AS delai_moyen
FROM delivery_time
GROUP BY seller_state
ORDER BY delai_moyen;


-- 4.3 Classement des commandes par montant total, par mois (fenêtrage)
-- Objectif : Identifier les « grosses commandes » de chaque mois.
-- DATEFROMPARTS construit le premier jour du mois pour partitionner.
-- RANK() classe les commandes au sein de chaque mois par montant décroissant.
SELECT 
    DATEFROMPARTS(YEAR(o.order_purchase_timestamp), MONTH(o.order_purchase_timestamp), 1) AS mois,
    o.order_id,
    SUM(p.payment_value) AS montant,
    RANK() OVER (PARTITION BY DATEFROMPARTS(YEAR(o.order_purchase_timestamp), MONTH(o.order_purchase_timestamp), 1) 
                 ORDER BY SUM(p.payment_value) DESC) AS rang_mois
FROM olist_orders_dataset o
JOIN olist_order_payments_dataset p ON o.order_id = p.order_id
GROUP BY DATEFROMPARTS(YEAR(o.order_purchase_timestamp), MONTH(o.order_purchase_timestamp), 1), o.order_id;


-- 4.4 Différence de prix entre un produit et le précédent (par prix) dans la même commande
-- Objectif : Détecter les écarts de prix entre produits d’une même commande.
-- LAG(price) récupère le prix du produit juste avant dans l'ordre croissant des prix.
-- L'écart est calculé entre le produit courant et le moins cher suivant.
-- Autre variante possible : ORDER BY order_item_id pour l'ordre réel d'achat.
SELECT order_id, product_id, price,
       LAG(price) OVER (PARTITION BY order_id ORDER BY price) AS prix_precedent,
       price - LAG(price) OVER (PARTITION BY order_id ORDER BY price) AS ecart
FROM olist_order_items_dataset;


/* 
   5. TENDANCES TEMPORELLES ET AVIS PRODUITS
      -------------------------------------- */

-- 5.1 Tendance mensuelle des ventes (chiffre d’affaires, nombre de commandes)
-- Objectif : Visualiser l'évolution de l'activité dans le temps.
-- Agrégation par année et mois. COUNT(DISTINCT) évite de compter plusieurs fois une commande.
SELECT 
    YEAR(order_purchase_timestamp) AS annee,
    MONTH(order_purchase_timestamp) AS mois,
    COUNT(DISTINCT o.order_id) AS nb_commandes,
    SUM(p.payment_value) AS ca_total
FROM olist_orders_dataset o
JOIN olist_order_payments_dataset p ON o.order_id = p.order_id
GROUP BY YEAR(order_purchase_timestamp), MONTH(order_purchase_timestamp)
ORDER BY annee, mois;


-- 5.2 Évaluation moyenne des produits par catégorie (à partir de la table order_reviews)
-- Objectif : Associer la satisfaction client (note) aux catégories de produits.
-- Nécessite la table olist_order_reviews_dataset. Jointure sur order_id.
-- Moyenne des review_score par catégorie.
SELECT p.product_category_name, AVG(r.review_score) AS note_moyenne
FROM olist_order_items_dataset i
JOIN olist_products_dataset p ON i.product_id = p.product_id
JOIN olist_order_reviews_dataset r ON i.order_id = r.order_id
GROUP BY p.product_category_name
ORDER BY note_moyenne DESC;


/* 
   6. REQUÊTES COMPLÉMENTAIRES (TOP PRODUITS, ANALYSE LOGISTIQUE PAR CATÉGORIE)
      ------------------------------------------------------------------------- */

-- 6.1 Top 5 des produits les plus vendus (par nombre de commandes)
-- Objectif : Identifier les best-sellers.
-- Compte le nombre de lignes dans order_items pour chaque produit (une ligne = un article).
-- Limité aux 5 premiers.
SELECT TOP 5 p.product_id, p.product_category_name, COUNT(*) AS nb_ventes
FROM olist_order_items_dataset i
JOIN olist_products_dataset p ON i.product_id = p.product_id
GROUP BY p.product_id, p.product_category_name
ORDER BY nb_ventes DESC;


-- 6.2 Délai moyen de livraison par catégorie de produit
-- Objectif : Identifier les catégories pour lesquelles la livraison est plus lente.
-- CTE delivery_by_cat calcule le délai en jours pour chaque ligne de commande.
-- Jointure avec la table produits pour obtenir la catégorie.
-- Moyenne par catégorie.
WITH delivery_by_cat AS (
    SELECT p.product_category_name,
           DATEDIFF(DAY, o.order_purchase_timestamp, o.order_delivered_customer_date) AS delai
    FROM olist_orders_dataset o
    JOIN olist_order_items_dataset i ON o.order_id = i.order_id
    JOIN olist_products_dataset p ON i.product_id = p.product_id
    WHERE o.order_delivered_customer_date IS NOT NULL
)
SELECT product_category_name, AVG(delai) AS delai_moyen
FROM delivery_by_cat
GROUP BY product_category_name
ORDER BY delai_moyen;



