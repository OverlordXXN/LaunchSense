import os
import sys
import logging
import joblib
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

from .predictor import build_feature_vector, EXPECTED_FEATURES, _load_model
import shap

# Cache explainer
_EXPLAINER = None

def _get_explainer(model):
    global _EXPLAINER
    if _EXPLAINER is None:
        logger.info("Initializing SHAP TreeExplainer...")
        _EXPLAINER = shap.TreeExplainer(model)
    return _EXPLAINER

def explain_prediction(project_inputs: dict) -> dict:
    """
    Evaluates the project and returns the ML success probability alongside
    a SHAP value breakdown of which features contributed positively or negatively.
    """
    model = _load_model()
    explainer = _get_explainer(model)
    
    # Map raw inputs to ordered 2D numpy array
    feature_vector = build_feature_vector(project_inputs)
    
    # 1. Get raw Probability
    probabilities = model.predict_proba(feature_vector)[0]
    success_probability = float(probabilities[1])
    
    # 2. Get SHAP values
    # For XGBoost binary classification, shap_values has shape (n_samples, n_features)
    # Output represents log-odds contribution.
    shap_vals = explainer.shap_values(feature_vector)[0]
    
    contributions = {}
    for i, feature_name in enumerate(EXPECTED_FEATURES):
        contributions[feature_name] = float(shap_vals[i])
        
    try:
        if isinstance(explainer.expected_value, (np.ndarray, list)):
            br = float(explainer.expected_value[0])
        else:
            br = float(explainer.expected_value)
    except Exception:
        br = 0.0
        
    return {
        "success_probability": round(success_probability, 4),
        "base_rate": br,
        "feature_contributions": contributions
    }

if __name__ == '__main__':
    logger.info("Executing Explainability Module CLI Test")
    
    test_inputs = {
        'goal': 15000,
        'goal_realism_score': 0.55,
        'category_success_rate': 0.41,
        'subcategory_success_rate': 0.47,
        'competition_density': 0.12,
        'launch_month': 5,
        'launch_day_of_week': 2,
        'campaign_duration': 30
    }
    
    print("\n--- Project Inputs ---")
    for k, v in test_inputs.items():
        print(f"{k}: {v}")
        
    try:
        explanation = explain_prediction(test_inputs)
        
        print("\n--- Prediction ---")
        print(f"Success Probability: {explanation['success_probability'] * 100:.2f}%")
        
        # Sort contributions by absolute impact
        contribs = explanation['feature_contributions']
        sorted_contribs = sorted(contribs.items(), key=lambda x: abs(x[1]), reverse=True)
        
        print("\n--- Top Expected Positive Impacts ---")
        for k, v in sorted_contribs:
            if v > 0:
                print(f"+ {k}: {v:.4f}")
                
        print("\n--- Top Expected Negative Impacts ---")
        for k, v in sorted_contribs:
            if v < 0:
                print(f"- {k}: {v:.4f}")
                
    except Exception as e:
        logger.error(f"Explanation failed: {e}")
