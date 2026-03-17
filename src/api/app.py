import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import numpy as np

# Setup paths
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(SRC_DIR)

from api.schemas import ProjectInput
from prediction.predictor import predict_success_probability
from prediction.goal_optimizer import optimize_goal
from analytics.analytics_engine import build_analytics_features
from analytics.similarity import calculate_similarity_metrics

logger = logging.getLogger(__name__)

# Global cache to map raw text to numerical historical features
_CACHE = {
    'cat_success': {},
    'subcat_success': {},
    'global_goal_median': 5000.0,
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load and cache category success rates from the database on API startup
    logger.info("Initializing API and caching historical analytics mapping...")
    try:
        df = build_analytics_features()
        if not df.empty:
            _CACHE['cat_success'] = df.groupby('category')['category_success_rate'].first().to_dict()
            _CACHE['subcat_success'] = df.groupby('subcategory')['subcategory_success_rate'].first().to_dict()
            _CACHE['global_goal_median'] = df['goal'].median()
            
            # Phase 8: Extract category to subcategory mapping for frontend UI dependency
            cat_to_subcat = df.groupby('category')['subcategory'].unique().apply(list).to_dict()
            _CACHE['categories_map'] = cat_to_subcat
            
            # Phase 8: Cache lightweight historical slice for similarity queries
            _CACHE['projects_df'] = df[['category', 'subcategory', 'goal', 'campaign_duration', 'is_successful']].copy()
            
            logger.info("Historical cache mapped successfully from dataset.")
    except Exception as e:
        logger.error(f"Failed to build analytics cache: {e}")
    yield
    _CACHE.clear()

app = FastAPI(title="Kickstarter Pre-Launch Predictor API", version="1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/categories")
def get_categories_endpoint():
    """
    Returns the mapped dictionary of all historical Categories and their 
    associated Subcategories to dynamically populate the UI dropdowns.
    """
    mapping = _CACHE.get('categories_map', {})
    if not mapping:
        logger.warning("Category cache was empty during /categories request.")
        # Minimal fallback in case DB is offline but API receives request
        return {"Technology": ["Web", "Hardware", "Gadgets"]}
    return mapping

@app.post("/similar-projects")
def similar_projects_endpoint(payload: ProjectInput):
    """
    Filters the in-memory cached historical dataset against the requested inputs
    to calculate empirical outcomes of 'similar' projects.
    """
    try:
        historical_df = _CACHE.get('projects_df')
        if historical_df is None or historical_df.empty:
            raise ValueError("Historical database is not loaded in cache.")
            
        metrics = calculate_similarity_metrics(payload.model_dump(), historical_df)
        return metrics
    except Exception as e:
        logger.error(f"API Error processing /similar-projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _map_to_model_features(input_data: ProjectInput) -> dict:
    """
    Simulates the analytics pipeline to map raw user inputs to ML model features.
    """
    goal = input_data.goal
    cat = input_data.category
    subcat = input_data.subcategory
    
    # 1. Map Categorical Historical Rates
    # Fallback to 0.35 (roughly average project success rate) if brand new category
    cat_success = _CACHE['cat_success'].get(cat, 0.35)
    subcat_success = _CACHE['subcat_success'].get(subcat, cat_success)
    
    # 2. Approximate Goal Realism Score (percentile mapping mockup since we don't have active rank)
    median = _CACHE['global_goal_median']
    # A rough realistic inversion: goals near median are highly realistic
    realism = float(min(max(0.01, median / (goal + 1)), 0.99))
    
    # 3. Approximate Competition Density
    density = 10 # Baseline fallback
    
    return {
        'goal': goal,
        'goal_realism_score': realism,
        'category_success_rate': cat_success,
        'subcategory_success_rate': subcat_success,
        'competition_density': density,
        'launch_month': input_data.launch_month,
        'launch_day_of_week': input_data.launch_day_of_week,
        'campaign_duration': input_data.campaign_duration
    }

@app.post("/predict")
def predict_endpoint(payload: ProjectInput, include_contributions: bool = True):
    """
    Receives raw project parameters, maps them to the XGBoost feature space, 
    and returns probability, class, goal optimizations, and SHAP explainability.
    """
    try:
        # Pre-process raw inputs
        model_inputs = _map_to_model_features(payload)
        
        # 1. Central inference request
        pred_result = predict_success_probability(model_inputs, include_contributions=include_contributions)
        
        # 2. Goal optimization request
        opt_result = optimize_goal(model_inputs)
        
        # Return merged JSON structure
        return {
            "success_probability": pred_result["success_probability"],
            "predicted_class": pred_result["predicted_class"],
            "optimal_goal": opt_result["optimal_goal"],
            "feature_contributions": pred_result.get("feature_contributions", {})
        }
    except Exception as e:
        logger.error(f"API Error processing /predict: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/optimize")
def optimize_endpoint(payload: ProjectInput):
    """
    Computes and returns the optimal Kickstarter funding goal recommendation 
    for the given project parameters.
    """
    try:
        # Pre-process raw inputs
        model_inputs = _map_to_model_features(payload)
        
        # 1. Get baseline prediction
        baseline_result = predict_success_probability(model_inputs, include_contributions=False)
        original_prob = baseline_result["success_probability"]
        
        # 2. Get optimization
        opt_result = optimize_goal(model_inputs)
        optimal_goal = opt_result["optimal_goal"]
        optimal_prob = opt_result["optimal_probability"]
        
        return {
            "original_goal": payload.goal,
            "recommended_goal": optimal_goal,
            "expected_success_probability": round(optimal_prob, 4),
            "improvement_over_original": round(optimal_prob - original_prob, 4),
            "goal_analysis": opt_result.get("goal_analysis", [])
        }
    except Exception as e:
        logger.error(f"API Error processing /optimize: {e}")
        raise HTTPException(status_code=500, detail=str(e))

