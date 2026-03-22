import os
import sys
import logging
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report

# Setup paths to ensure absolute imports work
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(SRC_DIR)
sys.path.append(SRC_DIR)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

from analytics.analytics_engine import build_analytics_features

def main():
    logger.info("Starting Pre-Launch Predictor model training pipeline...")
    
    # 1. Build the training dataset
    logger.info("Generating analytics features...")
    df = build_analytics_features()
    
    if df.empty:
        logger.error("Error: DataFrame is empty. Cannot train model.")
        sys.exit(1)
        
    logger.info(f"Dataset generated. Shape: {df.shape}")
    
    # Phase 13 Drift Optimization: isolate modern data
    logger.info("Filtering dataset to modern Kickstarters (launch_year >= 2020)...")
    if 'launch_year' in df.columns:
        df = df[df['launch_year'] >= 2020]
        
    logger.info(f"Filtered modern dataset. New shape: {df.shape}")
    
    # 2. Select ONLY pre-launch numeric ML features and target variable
    # average_pledge_per_backer is explicitly excluded to prevent data leakage
    features = [
        'goal',
        'goal_realism_score',
        'category_success_rate',
        'subcategory_success_rate',
        'competition_density',
        'launch_month',
        'launch_day_of_week',
        'campaign_duration'
    ]
    target = 'is_successful'
    
    logger.info(f"Selecting features: {features}")
    X = df[features]
    y = df[target]
    
    # Fill any remaining NaNs to prevent model training errors
    X = X.fillna(0)
    
    # 3. Train/Test split
    logger.info("Splitting dataset into train and test sets (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    logger.info(f"Train split size: {X_train.shape[0]} samples")
    logger.info(f"Test split size: {X_test.shape[0]} samples")
    
    # 4. Train XGBoost model
    logger.info('Initializing XGBoost Classifier (eval_metric="logloss")...')
    model = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss",
        random_state=42,
        n_jobs=-1
    )
    
    logger.info("Training model...")
    model.fit(X_train, y_train)
    
    # 5. Evaluate the model
    logger.info("Evaluating model on test set...")
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    accuracy = accuracy_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_prob)
    
    print("\n--- Model Evaluation Metrics ---")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"ROC AUC Score: {roc_auc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # 5.b Calibration Check (Phase 14)
    from sklearn.calibration import calibration_curve
    prob_true, prob_pred = calibration_curve(y_test, y_prob, n_bins=5)
    print("\n--- Calibration Check ---")
    for pt, pp in zip(prob_true, prob_pred):
        print(f"Predicted Probability Bin ~{pp:.2f} -> Actual Success Rate: {pt:.2f}")

    # 6. Feature importance
    print("\n--- Feature Importances ---")
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    for i in range(len(features)):
        print(f"{i+1}. {features[indices[i]]}: {importances[indices[i]]:.4f}")
    
    # 7. Save the trained model
    models_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(models_dir, 'kickstarter_launch_predictor.pkl')
    
    logger.info(f"Saving trained model to {model_path}...")
    joblib.dump(model, model_path)
    
    print(f"\nModel successfully saved to: models/kickstarter_launch_predictor.pkl")

if __name__ == '__main__':
    main()
