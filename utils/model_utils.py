import joblib
import pandas as pd

def load_ml_model():
# Loads the trained model from disk.
    model = joblib.load('models/baseline_alpha01.pkl')
    return model

def preprocess_input(input_data):
    """
    Converts raw user inputs from the UI into the format your model expects.
    """
    # 🎨 Exclude display-only fields; wrap in list so scalar values form a single-row DataFrame
    row = {k: v for k, v in input_data.items() if k != "company_name"}
    return pd.DataFrame([row])

def make_prediction(model, input_data):
    """
    Runs the model on the preprocessed data and returns the result.
    """
    prediction = model.predict(input_data)
    return prediction[0]
