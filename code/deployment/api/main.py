import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Wine Quality API")
model = joblib.load("models/model.pkl")

class WineFeatures(BaseModel):
    fixed_acidity: float
    volatile_acidity: float
    citric_acid: float
    residual_sugar: float
    chlorides: float
    free_sulfur_dioxide: float
    total_sulfur_dioxide: float
    density: float
    pH: float
    sulphates: float
    alcohol: float

@app.post("/predict")
def predict(features: WineFeatures):
    data_dict = {k.replace("_", " "): [v] for k, v in features.model_dump().items()}
    df = pd.DataFrame(data_dict)
    
    pred = int(model.predict(df)[0])
    prob = float(model.predict_proba(df)[0][1])
    
    return {
        "prediction": pred,
        "label": "High Quality (>= 6)" if pred == 1 else "Low/Medium Quality (< 6)",
        "probability_high_quality": round(prob, 4)
    }

@app.get("/health")
def health():
    return {"status": "healthy"}