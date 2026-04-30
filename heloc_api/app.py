import joblib
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import xgboost as xgb

app = FastAPI(title="HELOC Credit Scoring API")

# ------------------- CHARGEMENT -------------------
model = joblib.load("xgb_heloc_optimized.pkl")
booster = model.get_booster() if hasattr(model, 'get_booster') else model

feature_columns = joblib.load("feature_columns.pkl")   # 23 noms (bruts, ordre)
imputer = joblib.load("imputer.pkl")                   # fit sur les brutes

print(f"✅ Modèle chargé, {len(feature_columns)} features, imputer chargé")

# ------------------- SCHEMA D'ENTRÉE -------------------
class HELOCInput(BaseModel):
    values: List[float]  # 23 valeurs brutes, dans l'ordre de feature_columns

    class Config:
        json_schema_extra = {
            "example": {
                "values": [55.0, 144.0, 4.0, 84.0, 20.0, 3.0, 0.0, 83.0, 2.0, 3.0, 5.0,
                           23.0, 1.0, 43.0, 0.0, 0.0, 0.0, 33.0, 0.0, 8.0, 1.0, 1.0, 69.0]
            }
        }

# ------------------- PRÉTRAITEMENT -------------------
def preprocess(raw_values: List[float]) -> pd.DataFrame:
    if len(raw_values) != len(feature_columns):
        raise ValueError(f"Attendu {len(feature_columns)} valeurs, reçu {len(raw_values)}")
    
    df_raw = pd.DataFrame([raw_values], columns=feature_columns)
    # Imputation sur les brutes
    df_imputed = pd.DataFrame(imputer.transform(df_raw), columns=feature_columns)
    # Transformation log1p (comme dans l'entraînement)
    df_log = np.log1p(df_imputed)
    return df_log

# ------------------- ENDPOINT -------------------
@app.post("/predict")
async def predict(input_data: HELOCInput):
    try:
        df_processed = preprocess(input_data.values)
        dmatrix = xgb.DMatrix(df_processed)
        # Le booster retourne la probabilité de la classe 1 (Good)
        prob_good = booster.predict(dmatrix)[0]
        prob_bad = 1 - prob_good
        prediction = 1 if prob_good > 0.5 else 0   # 1 = Good, 0 = Bad
        return {
            "prediction": prediction,
            "status": "Good" if prediction == 1 else "Bad",
            "probability_bad": round(float(prob_bad), 4),
            "probability_good": round(float(prob_good), 4)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
def root():
    return {"message": "HELOC Credit Scoring - Envoyez 23 valeurs brutes"}

@app.get("/features")
def get_features():
    return {"n_features": len(feature_columns), "feature_names": feature_columns}