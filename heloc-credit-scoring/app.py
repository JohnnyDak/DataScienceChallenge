import streamlit as st
import joblib
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="HELOC - Prédiction", layout="wide")

# ---------------------------
# Chargement des artefacts
# ---------------------------
@st.cache_resource
def load_models():
    model = joblib.load('xgb_heloc_optimized.pkl')
    imputer = joblib.load('imputer.pkl')
    feature_cols = joblib.load('feature_columns.pkl')  # noms des 23 colonnes brutes
    return model, imputer, feature_cols

model, imputer, feature_cols = load_models()

# ---------------------------
# Interface principale
# ---------------------------
st.title("🏦 Prédiction de défaut de paiement – HELOC")
st.markdown("**Modèle XGBoost optimisé** – Semaine 3/10 Machine Learning")
st.write("Deux options : saisie manuelle (barre latérale) ou prédiction par lot (fichier CSV).")

# ============================================
# OPTION 1 : SAISIE MANUELLE
# ============================================
st.sidebar.header("📋 Saisie manuelle des caractéristiques")

input_vals = {}

with st.sidebar.expander("🔹 Scores et ancienneté"):
    input_vals['ExternalRiskEstimate'] = st.number_input("Estimation du risque externe", 0, 100, 70)
    input_vals['MSinceOldestTradeOpen'] = st.number_input("Mois depuis le plus ancien compte ouvert", 0, 1000, 100)
    input_vals['MSinceMostRecentTradeOpen'] = st.number_input("Mois depuis le compte ouvert le plus récent", 0, 400, 20)
    input_vals['AverageMInFile'] = st.number_input("Moyenne des mois dans le fichier", 0, 800, 60)

with st.sidebar.expander("🔹 Comportement"):
    input_vals['NumSatisfactoryTrades'] = st.number_input("Nombre de comptes satisfaisants", 0, 200, 10)
    input_vals['NumTrades60Ever2DerogPubRec'] = st.number_input("Nb comptes avec 60+ jours de retard", 0, 50, 0)
    input_vals['NumTrades90Ever2DerogPubRec'] = st.number_input("Nb comptes avec 90+ jours de retard", 0, 50, 0)
    input_vals['PercentTradesNeverDelq'] = st.number_input("Pourcentage de comptes jamais en retard", 0, 100, 80)
    input_vals['MSinceMostRecentDelq'] = st.number_input("Mois depuis le dernier retard", 0, 400, 50)
    input_vals['MaxDelq2PublicRecLast12M'] = st.number_input("Retard max / dossier public (12 mois)", 0, 10, 0)
    input_vals['MaxDelqEver'] = st.number_input("Retard maximal jamais enregistré", 0, 10, 1)

with st.sidebar.expander("🔹 Comptes"):
    input_vals['NumTotalTrades'] = st.number_input("Nombre total de comptes", 0, 200, 20)
    input_vals['NumTradesOpeninLast12M'] = st.number_input("Comptes ouverts dans les 12 derniers mois", 0, 50, 5)
    input_vals['PercentInstallTrades'] = st.number_input("Pourcentage de comptes à tempérament", 0, 100, 40)
    input_vals['NumRevolvingTradesWBalance'] = st.number_input("Nb comptes revolving avec solde", 0, 50, 5)
    input_vals['NumInstallTradesWBalance'] = st.number_input("Nb comptes à tempérament avec solde", 0, 50, 3)

with st.sidebar.expander("🔹 Demandes et utilisation"):
    input_vals['MSinceMostRecentInqexcl7days'] = st.number_input("Mois depuis dernière demande (hors 7j)", 0, 200, 10)
    input_vals['NumInqLast6M'] = st.number_input("Nombre de demandes dans les 6 mois", 0, 50, 2)
    input_vals['NumInqLast6Mexcl7days'] = st.number_input("Demandes dans 6 mois (hors 7j)", 0, 50, 2)
    input_vals['NetFractionRevolvingBurden'] = st.number_input("Fraction nette endettement revolving", 0, 100, 30)
    input_vals['NetFractionInstallBurden'] = st.number_input("Fraction nette endettement à tempérament", 0, 100, 25)
    input_vals['NumBank2NatlTradesWHighUtilization'] = st.number_input("Comptes bancaires/nationaux forte util.", 0, 20, 1)
    input_vals['PercentTradesWBalance'] = st.number_input("Pourcentage de comptes avec solde", 0, 100, 60)

# Prédiction manuelle
if st.sidebar.button("🚀 Prédire (saisie manuelle)"):
    # 1. DataFrame avec les 23 colonnes brutes dans l'ordre
    df_raw = pd.DataFrame([input_vals])[feature_cols]
    
    # 2. Imputation (sur valeurs brutes)
    df_imputed = pd.DataFrame(imputer.transform(df_raw), columns=feature_cols)
    
    # 3. Transformation log1p
    df_log = np.log1p(df_imputed)
    
    # 4. Prédiction
    proba = model.predict_proba(df_log)[0]  # [prob_Bad, prob_Good]
    proba_good = proba[1]
    pred_class = model.predict(df_log)[0]   # 0 = Bad, 1 = Good
    
    # Affichage
    st.subheader("📊 Résultat de la prédiction manuelle")
    col1, col2 = st.columns(2)
    col1.success("✅ Client GOOD" if pred_class == 1 else "❌ Client BAD")
    col2.metric("Probabilité GOOD", f"{proba_good*100:.1f}%")
    
    prob_df = pd.DataFrame({
        'Catégorie': ['Good', 'Bad'],
        'Probabilité (%)': [proba_good*100, (1-proba_good)*100]
    })
    fig = px.bar(prob_df, x='Catégorie', y='Probabilité (%)', text='Probabilité (%)',
                 color='Catégorie', color_discrete_sequence=['green','red'])
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(yaxis_range=[0,100])
    st.plotly_chart(fig)

# ============================================
# OPTION 2 : PRÉDICTION PAR LOT (CSV)
# ============================================
st.markdown("---")
st.header("📁 Prédiction par lot (fichier CSV)")
st.write("Le fichier CSV doit contenir **exactement les 23 colonnes** suivantes (dans n’importe quel ordre) :")
st.write(", ".join(feature_cols))

uploaded_file = st.file_uploader("Choisir un fichier CSV", type="csv")

if uploaded_file is not None:
    df_batch = pd.read_csv(uploaded_file)
    
    # Vérifier que toutes les colonnes sont présentes
    missing_cols = set(feature_cols) - set(df_batch.columns)
    if missing_cols:
        st.error(f"Colonnes manquantes dans le CSV : {missing_cols}")
    else:
        # Réordonner les colonnes comme attendu
        df_batch = df_batch[feature_cols]
        
        # Prétraitement batch (identique à la saisie manuelle)
        with st.spinner("Prétraitement et prédiction en cours..."):
            X_imputed = pd.DataFrame(imputer.transform(df_batch), columns=feature_cols)
            X_log = np.log1p(X_imputed)
            probas = model.predict_proba(X_log)[:, 1]   # probabilité Good
            preds = model.predict(X_log)               # 0 ou 1
        
        # Ajout des résultats
        df_batch['Probabilité_Good'] = probas
        df_batch['Prédiction'] = preds
        df_batch['Classe'] = df_batch['Prédiction'].map({0: 'Bad', 1: 'Good'})
        
        st.subheader("Aperçu des résultats")
        st.dataframe(df_batch.head(10))
        
        # Statistiques rapides
        good_pct = (preds == 1).mean() * 100
        st.metric("Proportion de clients GOOD dans le lot", f"{good_pct:.1f}%")
        
        # Téléchargement
        csv_result = df_batch.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Télécharger les prédictions (CSV)", csv_result, "predictions_batch.csv", "text/csv")
        
        # Optionnel : histogramme des probabilités
        fig_hist = px.histogram(df_batch, x='Probabilité_Good', nbins=20,
                                title="Distribution des probabilités GOOD",
                                labels={'Probabilité_Good': 'Probabilité d\'être GOOD'})
        st.plotly_chart(fig_hist)