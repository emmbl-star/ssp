import joblib
import pandas as pd

def load_ml_model():
# Loads the trained model from disk.
    model = joblib.load('models/baseline_alpha01.pkl')
    return model

def preprocess_input(funding_total_usd, funding_rounds, founded_year,first_funding_year,last_funding_year,category_list,country_code,state_code):
    """
    Converts raw user inputs from the UI into the format your model expects.
    """
    # Create a DataFrame or a list in the shape your model was trained on
    input_data = pd.DataFrame({
        'funding_total_usd': [funding_total_usd],
        'funding_rounds': [funding_rounds],
        'founded_year': [founded_year],
        'first_funding_year': [first_funding_year],
        'last_funding_year': [last_funding_year],
        'category_list': [category_list],
        'country_code': [country_code],
        'state_code': [state_code],
    })
    return input_data

def make_prediction(model, input_data):
    """
    Runs the model on the preprocessed data and returns the result.
    """
    prediction = model.predict(input_data)
    return prediction[0]
