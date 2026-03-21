import os
import sys
import logging
import pandas as pd
import numpy as np
import shap
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report

# Setup paths
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(SRC_DIR)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

from analytics.analytics_engine import build_analytics_features

def evaluate_model(name, model, X_test, y_test):
    logger.info(f"Evaluating {name}...")
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)
    
    print(f"\n--- {name} Results ---")
    print(f"Accuracy: {acc:.4f}")
    print(f"ROC AUC: {auc:.4f}")
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    
    return acc, auc

def main():
    print("=== PHASE 12: TEMPORAL DRIFT EXPERIMENT ===")
    logger.info("Generating features...")
    df = build_analytics_features()
    
    if df.empty:
        logger.error("Dataset empty.")
        sys.exit(1)
        
    print("\n--- Temporal Analysis (Success Rate by Launch Year) ---")
    # Group by launch year
    temporal_stats = df.groupby('launch_year').agg(
        total_projects=('is_successful', 'count'),
        success_rate=('is_successful', 'mean')
    ).reset_index()
    print(temporal_stats.to_string(index=False))
    
    # Base configuration
    base_features = [
        'goal',
        'goal_realism_score',
        'category_success_rate',
        'subcategory_success_rate',
        'competition_density',
        'average_pledge_per_backer'
    ]
    enhanced_features = base_features + ['launch_year']
    target = 'is_successful'
    
    # A) Baseline Model Training
    X_base = df[base_features].fillna(0)
    y = df[target]
    
    X_train_b, X_test_b, y_train_b, y_test_b = train_test_split(X_base, y, test_size=0.2, random_state=42, stratify=y)
    
    logger.info("Training Baseline Model (current features)...")
    baseline_model = XGBClassifier(n_estimators=300, max_depth=6, learning_rate=0.05, random_state=42, n_jobs=-1)
    baseline_model.fit(X_train_b, y_train_b)
    evaluate_model("Baseline Model", baseline_model, X_test_b, y_test_b)
    
    # B) Enhanced Model Training
    X_enh = df[enhanced_features].fillna(0)
    X_train_e, X_test_e, y_train_e, y_test_e = train_test_split(X_enh, y, test_size=0.2, random_state=42, stratify=y)
    
    logger.info("Training Enhanced Model (with launch_year)...")
    enhanced_model = XGBClassifier(n_estimators=300, max_depth=6, learning_rate=0.05, random_state=42, n_jobs=-1)
    enhanced_model.fit(X_train_e, y_train_e)
    evaluate_model("Enhanced Model (Drift-Aware)", enhanced_model, X_test_e, y_test_e)
    
    # Feature Importances & SHAP
    print("\n--- Enhanced Model Feature Importances ---")
    importances = enhanced_model.feature_importances_
    indices = np.argsort(importances)[::-1]
    for i in range(len(enhanced_features)):
        print(f"{i+1}. {enhanced_features[indices[i]]}: {importances[indices[i]]:.4f}")
        
    logger.info("Calculating SHAP values for Enhanced Model (sample size to save time)...")
    # Sample to avoid massive computation time
    X_sample = X_test_e.sample(n=min(5000, len(X_test_e)), random_state=42)
    explainer = shap.TreeExplainer(enhanced_model)
    shap_values = explainer.shap_values(X_sample)
    
    # Mean absolute SHAP value per feature
    mean_shap = np.abs(shap_values).mean(axis=0)
    shap_impact = pd.DataFrame({
        'Feature': enhanced_features,
        'Mean |SHAP|': mean_shap
    }).sort_values('Mean |SHAP|', ascending=False)
    
    print("\n--- SHAP Impact (Mean Absolute Value) ---")
    print(shap_impact.to_string(index=False))
    
    # Optional Experiment: Modern Data Only
    print("\n=== OPTIONAL EXPERIMENT: RECENT DATA ONLY (>= 2020) ===")
    df_recent = df[df['launch_year'] >= 2020]
    if len(df_recent) > 1000:
        logger.info(f"Filtering recent data... Found {len(df_recent)} rows.")
        X_rec = df_recent[enhanced_features].fillna(0)
        y_rec = df_recent[target]
        
        X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(X_rec, y_rec, test_size=0.2, random_state=42, stratify=y_rec)
        recent_model = XGBClassifier(n_estimators=300, max_depth=6, learning_rate=0.05, random_state=42, n_jobs=-1)
        recent_model.fit(X_train_r, y_train_r)
        
        evaluate_model("Recent-Only Enhanced Model", recent_model, X_test_r, y_test_r)
    else:
        logger.warning(f"Not enough recent data (only {len(df_recent)} rows) for robust training.")
        
    print("\n=== EXPERIMENT COMPLETE ===")

if __name__ == "__main__":
    main()
