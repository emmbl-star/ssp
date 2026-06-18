# Runs the ML model on a payload and returns the predicted outcome, confidence, and feature importances.
# Called on form submit; results are displayed in the Results section below the form.
import streamlit as st
from utils.model_utils import preprocess_input

CLASS_LABELS = {0: "Acquired", 1: "Closed", 2: "IPO", 3: "Operating"}


def get_prediction(payload: dict, model) -> dict:
    try:
        input_data = preprocess_input(payload)

        proba = model.predict_proba(input_data)[0]
        predicted_idx = int(model.predict(input_data)[0])
        predicted_class = CLASS_LABELS[predicted_idx]
        confidence = float(proba[predicted_idx])

        estimator = model[-1] if hasattr(model, "__getitem__") else model
        feature_names = list(input_data.columns)
        if hasattr(estimator, "feature_importances_"):
            raw_imp = estimator.feature_importances_
        elif hasattr(estimator, "coef_"):
            raw_imp = abs(estimator.coef_[0])
        else:
            raw_imp = [1.0 / len(feature_names)] * len(feature_names)

        top_features = dict(zip(feature_names, [float(v) for v in raw_imp]))

        return {
            "predicted_class": predicted_class,
            "confidence":      confidence,
            "top_features":    top_features,
        }
    except Exception as e:
        st.warning(f"⚠️ Model error - using defaults. ({e})")
        return {"predicted_class": "Unknown", "confidence": 0.0, "top_features": {}}
