# Runs the ML model on a payload and returns success probability, risk score, and feature importances.
# Called on form submit; results are displayed in the Results section below the form.
import streamlit as st
from utils.model_utils import preprocess_input, make_prediction


def get_prediction(payload: dict, model) -> dict:
    try:
        input_data = preprocess_input(payload)

        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(input_data)[0]
            success_probability = float(proba[1]) if len(proba) > 1 else float(proba[0])
        else:
            success_probability = float(make_prediction(model, input_data))

        risk_score = 1.0 - success_probability

        feature_names = list(input_data.columns)
        estimator = model[-1] if hasattr(model, "__getitem__") else model
        if hasattr(estimator, "feature_importances_"):
            raw_imp = estimator.feature_importances_
        elif hasattr(estimator, "coef_"):
            raw_imp = abs(estimator.coef_[0])
        else:
            raw_imp = [1.0 / len(feature_names)] * len(feature_names)

        top_features = dict(zip(feature_names, [float(v) for v in raw_imp]))

        return {
            "success_probability": success_probability,
            "risk_score": risk_score,
            "top_features": top_features,
        }
    except Exception as e:
        st.warning(f"⚠️ Model error - using defaults. ({e})")
        return {"success_probability": 0.0, "risk_score": 1.0, "top_features": {}}
