import joblib
import numpy as np
import pandas as pd

# Median funding from training data — used to replicate the high_funding flag
_HIGH_FUNDING_THRESHOLD = 5_000_000

def load_ml_model():
    model = joblib.load('models/ssp_multiclass_xgb_smote.pkl')
    return model

def preprocess_input(input_data: dict) -> pd.DataFrame:
    funding = input_data["funding_total_usd"]
    rounds  = input_data["funding_rounds"]
    founded = input_data["founded_year"]
    first   = input_data["first_funding_year"]
    last    = input_data["last_funding_year"]

    row = {
        "category_list":          input_data["category_list"],
        "funding_total_usd":      funding,
        "country_code":           input_data["country_code"],
        "state_code":             input_data["state_code"],
        "funding_rounds":         rounds,
        "founded_year":           founded,
        "first_funding_year":     first,
        "last_funding_year":      last,
        "years_to_first_funding": first - founded,
        "funding_duration":       last - first,
        "log_funding_total_usd":  np.log1p(funding),
        "funding_per_round":      funding / rounds if rounds > 0 else 0.0,
        "multiple_rounds":        int(rounds > 1),
        "early_funding":          int((first - founded) <= 2),
        "high_funding":           int(funding > _HIGH_FUNDING_THRESHOLD),
    }
    return pd.DataFrame([row])

def make_prediction(model, input_data):
    prediction = model.predict(input_data)
    return prediction[0]
