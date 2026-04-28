import streamlit as st
import joblib
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="HELOC - Prédiction", layout="wide")

# ---------------------------
# Interface utilisateur (inchangée, mais vérifiez que les 23 champs sont tous présents)
# ---------------------------
st.title("🏦 Prédiction de défaut de paiement – HELOC")
st.markdown("**Modèle XGBoost optimisé** – Semaine 3/10 Machine Learning")
st.write("Remplissez les informations du client dans la barre latérale, puis cliquez sur **Prédire**.")

# Chargement
@st.cache_resource
def load_models():
    model = joblib.load('xgb_heloc_optimized.pkl')
    imputer = joblib.load('imputer.pkl')
    feature_cols = joblib.load('feature_columns.pkl')  # noms des 23 colonnes brutes
    return model, imputer, feature_cols

model, imputer, feature_cols = load_models()

# Interface
st.title("🏦 Prédiction HELOC")
st.sidebar.header("Saisie des caractéristiques")

# Dictionnaire pour stocker les valeurs brutes saisies
input_vals = {}

with st.sidebar.expander("🔹 Scores et ancienneté"):
    input_vals['ExternalRiskEstimate'] = st.number_input("Estimation du risque externe", 0, 100, 70)
    input_vals['MSinceOldestTradeOpen'] = st.number_input("Mois depuis le plus ancien compte ouvert", 0, 1000, 100)
    input_vals['MSinceMostRecentTradeOpen'] = st.number_input("Mois depuis le compte ouvert le plus récent", 0, 400, 20)
    input_vals['AverageMInFile'] = st.number_input("Moyenne des mois dans le fichier", 0, 800, 60)

with st.sidebar.expander("🔹 Comportement"):
    input_vals['NumSatisfactoryTrades'] = st.number_input("Nombre de comptes satisfaisants", 0, 200, 10)
    input_vals['NumTrades60Ever2DerogPubRec'] = st.number_input("Nombre de comptes avec 60+ jours de retard ou défaut public", 0, 50, 0)
    input_vals['NumTrades90Ever2DerogPubRec'] = st.number_input("Nombre de comptes avec 90+ jours de retard ou défaut public", 0, 50, 0)
    input_vals['PercentTradesNeverDelq'] = st.number_input("Pourcentage de comptes jamais en retard", 0, 100, 80)
    input_vals['MSinceMostRecentDelq'] = st.number_input("Mois depuis le dernier retard", 0, 400, 50)
    input_vals['MaxDelq2PublicRecLast12M'] = st.number_input("Retard max ou dossier public sur 12 mois", 0, 10, 0)
    input_vals['MaxDelqEver'] = st.number_input("Retard maximal jamais enregistré", 0, 10, 1)

with st.sidebar.expander("🔹 Comptes"):
    input_vals['NumTotalTrades'] = st.number_input("Nombre total de comptes", 0, 200, 20)
    input_vals['NumTradesOpeninLast12M'] = st.number_input("Nombre de comptes ouverts dans les 12 derniers mois", 0, 50, 5)
    input_vals['PercentInstallTrades'] = st.number_input("Pourcentage de comptes à tempérament", 0, 100, 40)
    input_vals['NumRevolvingTradesWBalance'] = st.number_input("Nombre de comptes revolving avec solde", 0, 50, 5)
    input_vals['NumInstallTradesWBalance'] = st.number_input("Nombre de comptes à tempérament avec solde", 0, 50, 3)

with st.sidebar.expander("🔹 Demandes et utilisation"):
    input_vals['MSinceMostRecentInqexcl7days'] = st.number_input("Mois depuis la dernière demande (hors 7 jours)", 0, 200, 10)
    input_vals['NumInqLast6M'] = st.number_input("Nombre de demandes dans les 6 derniers mois", 0, 50, 2)
    input_vals['NumInqLast6Mexcl7days'] = st.number_input("Nombre de demandes dans les 6 mois (hors 7 jours)", 0, 50, 2)
    input_vals['NetFractionRevolvingBurden'] = st.number_input("Fraction nette de l'endettement revolving", 0, 100, 30)
    input_vals['NetFractionInstallBurden'] = st.number_input("Fraction nette de l'endettement à tempérament", 0, 100, 25)
    input_vals['NumBank2NatlTradesWHighUtilization'] = st.number_input("Nombre de comptes bancaires/nationaux à forte utilisation", 0, 20, 1)
    input_vals['PercentTradesWBalance'] = st.number_input("Pourcentage de comptes avec solde", 0, 100, 60)

    
# Bouton de prédiction
if st.sidebar.button("🚀 Prédire"):
    # 1. Construire un DataFrame avec les 23 valeurs brutes (dans l'ordre des feature_cols)
    df_raw = pd.DataFrame([input_vals])[feature_cols]  # garantit l'ordre
    
    # 2. Imputation (sur les valeurs brutes)
    df_imputed = pd.DataFrame(imputer.transform(df_raw), columns=feature_cols)
    
    # 3. Appliquer log1p (comme lors de l'entraînement)
    df_log = np.log1p(df_imputed)
    
    # 4. Prédiction
    proba = model.predict_proba(df_log)[0]  # [prob_Bad, prob_Good]
    proba_good = proba[1]
    pred_class = model.predict(df_log)[0]   # 0 = Bad, 1 = Good (si encodage initial)
    
   
    # Graphique
    prob_df = pd.DataFrame({
        'Catégorie': ['Good', 'Bad'],
        'Probabilité': [proba_good*100, (1-proba_good)*100]
    })
    fig = px.bar(prob_df, x='Catégorie', y='Probabilité', text='Probabilité',
                 color='Catégorie', color_discrete_sequence=['green','red'])
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(yaxis_range=[0,100])
    st.plotly_chart(fig)


     # 5. Résultats (avec encodage : 0 -> Bad, 1 -> Good)
    is_good = (pred_class == 1)
    
    st.subheader("Résultat")
    col1, col2 = st.columns(2)
    col1.success("✅ Client GOOD" if is_good else "❌ Client BAD")
    col2.metric("Probabilité GOOD", f"{proba_good*100:.1f}%")
    