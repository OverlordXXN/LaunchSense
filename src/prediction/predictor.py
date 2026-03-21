import os
import sys
import logging
import joblib
import pandas as pd
import numpy as np

# Setup paths
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(SRC_DIR)
sys.path.append(SRC_DIR)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Expected feature order exactly as trained
EXPECTED_FEATURES = [
    'goal',
    'goal_realism_score',
    'category_success_rate',
    'subcategory_success_rate',
    'competition_density',
    'launch_month',
    'launch_day_of_week',
    'campaign_duration'
]

# Global model cache
_MODEL = None

def _load_model():
    """Lazily loads the pre-launch XGBoost model if not already in memory."""
    global _MODEL
    if _MODEL is None:
        model_path = os.path.join(ROOT_DIR, 'models', 'latest.joblib')
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")
        logger.info(f"Loading prediction model from {model_path}...")
        _MODEL = joblib.load(model_path)
    return _MODEL

def build_feature_vector(project_inputs: dict) -> np.ndarray:
    """
    Validates the input dictionary and extracts features in the correct order.
    Returns a 2D numpy array shaped for model inference.
    """
    # 1. Validate inputs
    missing_features = [f for f in EXPECTED_FEATURES if f not in project_inputs]
    if missing_features:
        raise ValueError(f"Missing required features: {missing_features}")
        
    # 2. Extract in expected order
    feature_list = []
    for f in EXPECTED_FEATURES:
        try:
            val = float(project_inputs[f])
            feature_list.append(val)
        except (ValueError, TypeError):
            raise ValueError(f"Feature '{f}' must be a numeric value, got '{project_inputs[f]}'")
            
    # Return as 2D array: (n_samples, n_features)
    return np.array([feature_list])

def predict_success_probability(project_inputs: dict, include_contributions: bool = False) -> dict:
    """
    Evaluates realistic pre-launch project metrics using the trained XGBoost model.
    Returns success probability and predicted class designation.
    Optionally includes SHAP feature contributions.
    """
    logger.info("Predicting success probability using drift-optimized model trained on >= 2020 data.")
    model = _load_model()
    
    # Map raw inputs to model space
    feature_vector = build_feature_vector(project_inputs)
    
    # Run predict_proba for class 1 (success)
    probabilities = model.predict_proba(feature_vector)[0]
    success_probability = float(probabilities[1])
    
    # Predict absolute class
    predicted_class_idx = model.predict(feature_vector)[0]
    predicted_class_str = "Successful" if predicted_class_idx == 1 else "Failed"
    
    # Evaluate Validation & Trust constraints (Phase 14)
    confidence_level = "High" if success_probability > 0.7 else "Medium" if success_probability >= 0.5 else "Low"
    warning_flags = []
    
    goal_val = project_inputs.get('goal', 0)
    duration_val = project_inputs.get('campaign_duration', 30)
    
    if goal_val > 100000:
        warning_flags.append("Warning: Exceptionally high funding goal requested. Models are inherently less confident estimating magnitudes outside normal user limits (>100k).")
    if duration_val > 60:
        warning_flags.append("Warning: Unusually long campaign duration. Campaigns exceeding optimal timelines suffer from diminished pledge curves.")
        
    output = {
        "success_probability": round(success_probability, 4),
        "predicted_class": predicted_class_str,
        "confidence_level": confidence_level,
        "warning_flags": warning_flags
    }
    
    if include_contributions:
        from prediction.explainer import explain_prediction
        explanation = explain_prediction(project_inputs)
        output["feature_contributions"] = explanation["feature_contributions"]
        
    return output

if __name__ == '__main__':
    logger.info("Executing prediction module test interface...")
    
    # Example test data triggering Phase 14 warnings
    test_inputs = {
        'goal': 150000,
        'goal_realism_score': 0.15,
        'category_success_rate': 0.41,
        'subcategory_success_rate': 0.47,
        'competition_density': 0.12,
        'launch_month': 5,
        'launch_day_of_week': 2,
        'campaign_duration': 90
    }
    
    logger.info(f"Test Inputs:\n{pd.Series(test_inputs)}")
    
    try:
        result = predict_success_probability(test_inputs)
        print("\n--- Model Prediction ---")
        print(f"Predicted Class:       {result['predicted_class']}")
        print(f"Success Probability:   {result['success_probability'] * 100:.2f}%")
        print(f"Confidence Level:      {result.get('confidence_level')}")
        if result.get("warning_flags"):
            print("\nWarnings:")
            for w in result['warning_flags']:
                print(f" - {w}")
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
