import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import pandas as pd
import re

# Setup paths
import joblib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = str(ROOT / "src")
MODEL_PATH = ROOT / "models" / "latest.joblib"
model = None

def get_model():
    global model
    if model is None:
        model = joblib.load(MODEL_PATH)
    return model

from .schemas import ProjectInput
from ..prediction.predictor import predict_success_probability
from ..prediction.goal_optimizer import optimize_goal
from ..analytics.analytics_engine import build_analytics_features
from ..analytics.similarity import calculate_similarity_metrics

logger = logging.getLogger(__name__)

from typing import Dict, Any

# Global cache to map raw text to numerical historical features
_CACHE: Dict[str, Any] = {
    'cat_success': {},
    'subcat_success': {},
    'global_goal_median': 5000.0,
}

STATIC_CATEGORIES = {
    "Technology": ["Hardware", "Web", "Software", "Apps", "Gadgets", "Robots", "DIY Electronics"],
    "Games": ["Tabletop Games", "Video Games", "Playing Cards", "Puzzles", "Mobile Games", "Live Games"],
    "Art": ["Painting", "Digital Art", "Illustration", "Public Art", "Sculpture", "Mixed Media", "Conceptual Art", "Ceramics", "Textiles", "Installations", "Video Art"],
    "Design": ["Product Design", "Graphic Design", "Architecture", "Interactive Design", "Typography", "Civic Design"],
    "Film & Video": ["Documentary", "Shorts", "Animation", "Webseries", "Narrative Film", "Music Videos", "Action", "Comedy", "Drama", "Family", "Fantasy", "Horror", "Romance", "Science Fiction", "Thrillers"],
    "Publishing": ["Fiction", "Nonfiction", "Art Books", "Children's Books", "Periodical", "Poetry", "Radio & Podcasts", "Zines", "Academic", "Anthologies", "Calendars", "Comedy", "Letterpress", "Literary Journals", "Translations", "Young Adult"],
    "Music": ["Indie Rock", "Pop", "Rock", "Jazz", "Electronic", "Classical Music", "Hip-Hop", "Punk", "Country & Folk", "World Music", "Metal", "R&B", "Blues", "Chiptune", "Faith", "Kids", "Latin"],
    "Food": ["Restaurants", "Food Trucks", "Drinks", "Small Batch", "Farms", "Vegan", "Events", "Community Gardens", "Spaces", "Bacon", "Cookbooks", "Farmer's Markets"],
    "Fashion": ["Apparel", "Accessories", "Footwear", "Jewelry", "Ready-to-wear", "Childrenswear", "Couture", "Pet Fashion"],
    "Comics": ["Comic Books", "Graphic Novels", "Webcomics", "Anthologies", "Events"],
    "Photography": ["Photobooks", "Fine Art", "People", "Places", "Nature", "Animals"],
    "Theater": ["Plays", "Musicals", "Festivals", "Experimental", "Immersive", "Spaces", "Comedy"],
    "Dance": ["Performances", "Workshops", "Residencies", "Spaces"],
    "Crafts": ["Woodworking", "DIY", "Crafts", "Candles", "Crochet", "Embroidery", "Glass", "Knitting", "Macrame", "Pottery", "Printing", "Quilts", "Stationery", "Taxidermy", "Weaving"]
}

historical_df = None

def load_dataset():
    ROOT = Path(__file__).resolve().parents[2]
    
    csv = ROOT / "data" / "processed" / "full_dataset.csv"
    gz  = ROOT / "data" / "processed" / "full_dataset.csv.gz"

    if csv.exists():
        print("Loading dataset CSV:", csv)
        return pd.read_csv(csv)

    if gz.exists():
        print("Loading dataset GZIP:", gz)
        return pd.read_csv(gz, compression="gzip")

    print("No dataset found")
    return None

def find_similar_projects(payload: ProjectInput, df: pd.DataFrame, top_n=5) -> list:
    if df is None or df.empty:
        return []
        
    mask = (df["category"].str.lower() == payload.category.lower())
    if not mask.any():
        return []
        
    calc_df = df[mask].copy()
    
    # Calculate simple distance normalized to 0-1
    # distance = abs(log(project_goal) - log(target_goal))
    calc_df["goal_diff"] = np.abs(np.log1p(calc_df["goal"].fillna(0)) - np.log1p(payload.goal))
    
    # If duration exists
    if "campaign_duration" in calc_df.columns:
        calc_df["dur_diff"] = np.abs(calc_df["campaign_duration"] - payload.campaign_duration) / payload.campaign_duration
    else:
        calc_df["dur_diff"] = 0
        
    calc_df["distance"] = calc_df["goal_diff"] + calc_df["dur_diff"]
    calc_df["similarity"] = 1 / (1 + calc_df["distance"])
    
    top = calc_df.sort_values("similarity", ascending=False).head(top_n)
    
    results = []
    for _, row in top.iterrows():
        results.append({
            "title": str(row.get("title", "Unknown Project")),
            "category": str(row.get("category", payload.category)),
            "goal": float(row.get("goal", 0)),
            "pledged": float(row.get("pledged", 0)),
            "success": bool(row.get("success", False)),
            "similarity": float(row["similarity"])
        })
    return results

def clean_label(text: str) -> str:
    """Normalize string casing fixing apostrophes and acronyms overriding .title() anomalies."""
    if pd.isna(text) or not str(text).strip():
        return ""
    
    text = str(text).strip().title()
    
    # 1. Fix apostrophe casing (e.g., "Farmer'S" -> "Farmer's")
    text = re.sub(r"'S\b", "'s", text)
    
    # 2. Fix known acronyms implicitly bypassing title()
    acronyms = {
        r"\bDiy\b": "DIY",
        r"\bR&B\b": "R&B",
        r"\bSci-Fi\b": "Sci-Fi",
        r"\b3D\b": "3D"
    }
    
    for pattern, replacement in acronyms.items():
        text = re.sub(pattern, replacement, text)
        
    return text

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load and cache category success rates from the database on API startup
    logger.info("Initializing API and caching historical analytics mapping...")
    try:
        import time
        t0 = time.time()
        
        try:
            df = build_analytics_features()
        except Exception as feature_err:
            logger.warning(f"Dataset unavailable for feature building: {feature_err}")
            df = pd.DataFrame()
            
        if not df.empty:
            _CACHE['cat_success'] = df.groupby('category')['category_success_rate'].first().to_dict()
            _CACHE['subcat_success'] = df.groupby('subcategory')['subcategory_success_rate'].first().to_dict()
            _CACHE['global_goal_median'] = df['goal'].median()
            
            # Phase 8: Extract category to subcategory mapping for frontend UI dependency (Deferred)
            
            # Phase 8: Cache lightweight historical slice for similarity queries
            _CACHE['projects_df'] = df[['category', 'subcategory', 'goal', 'campaign_duration', 'is_successful']].copy()
            
            logger.info("Historical cache mapped successfully from dataset.")
            
        global historical_df
        historical_df = load_dataset()
        historical_available = historical_df is not None
        
        if historical_available:
            print("Dataset rows:", len(historical_df))
            
            # Normalize dataset globally for historical similarity
            col_map = {c: c.lower().replace("-", "_").replace(" ", "_") for c in historical_df.columns}
            historical_df = historical_df.rename(columns=col_map)
            
            if "name" in historical_df.columns and "title" not in historical_df.columns:
                historical_df["title"] = historical_df["name"]
            if "usd_pledged" in historical_df.columns and "pledged" not in historical_df.columns:
                historical_df["pledged"] = historical_df["usd_pledged"]
            if "is_successful" in historical_df.columns and "success" not in historical_df.columns:
                historical_df["success"] = historical_df["is_successful"]
            elif "state" in historical_df.columns and "success" not in historical_df.columns:
                historical_df["success"] = (historical_df["state"].astype(str).str.lower() == "successful")
                
            # Now build categories mapping
            cols = historical_df.columns
            actual_cat_col = next((c for c in cols if c in ['category', 'main_category']), None)
            actual_subcat_col = next((c for c in cols if c in ['subcategory', 'sub_category']), None)
            
            if actual_cat_col and actual_subcat_col:
                cat_df = historical_df[[actual_cat_col, actual_subcat_col]].dropna().copy()
                cat_df[actual_cat_col] = cat_df[actual_cat_col].apply(clean_label)
                cat_df[actual_subcat_col] = cat_df[actual_subcat_col].apply(clean_label)
                cat_df = cat_df[(cat_df[actual_cat_col] != "") & (cat_df[actual_subcat_col] != "")]
                
                logger.info(f"Loaded normalized dataset for categories. Shape: {cat_df.shape}")
                
                raw_mapping = cat_df.groupby(actual_cat_col)[actual_subcat_col].unique()
                mapping = {}
                for cat, subcats in raw_mapping.items():
                    clean_subcats = {str(item) for item in subcats if str(item) and str(item) != cat}
                    mapping[cat] = sorted(list(clean_subcats))
                    
                _CACHE['categories_map'] = mapping
                logger.info(f"Successfully processed {len(mapping)} clean categories in {time.time() - t0:.2f}s.")
            else:
                logger.warning("Category columns missing. Using fallback.")
                _CACHE['categories_map'] = {}
        else:
            logger.warning("No dataset found for categories.")
            _CACHE['categories_map'] = {}

    except Exception as e:
        logger.error(f"Failed to build analytics cache: {e}")
        _CACHE['categories_map'] = {}
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
    try:
        mapping = _CACHE.get('categories_map', {})
        if mapping:
            return {
                "source": "dataset",
                "mapping": mapping
            }
        else:
            return {
                "source": "fallback",
                "mapping": STATIC_CATEGORIES
            }
    except Exception as e:
        logger.error(f"API Error processing /categories: {e}")
        return {
            "source": "fallback",
            "mapping": STATIC_CATEGORIES
        }

@app.post("/similar-projects")
def similar_projects_endpoint(payload: ProjectInput):
    """
    Filters the in-memory cached historical dataset against the requested inputs
    to calculate empirical outcomes of 'similar' projects.
    """
    try:
        historical_df = _CACHE.get('projects_df')
        if historical_df is None or historical_df.empty:
            return {"status": "unavailable"}
            
        metrics = calculate_similarity_metrics(payload.model_dump(), historical_df)
        return metrics
    except Exception as e:
        logger.error(f"API Error processing /similar-projects: {e}")
        return {"status": "unavailable"}

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
        
        # Ensure model is strictly loaded in memory via lazy evaluation (TASK-138)
        _ = get_model()
        
        # 1. Central inference request
        pred_result = predict_success_probability(model_inputs, include_contributions=include_contributions)
        
        # 2. Goal optimization request
        opt_result = optimize_goal(model_inputs)
        
        # 3. Similar Projects request
        historical_df = globals().get('historical_df')
        if historical_df is not None and not historical_df.empty:
            historical_available = True
            sim_projs = find_similar_projects(payload, historical_df, top_n=5)
            
            # Additional aggregate metrics
            historical_proj_df = _CACHE.get('projects_df')
            if historical_proj_df is not None and not historical_proj_df.empty:
                sim_result = calculate_similarity_metrics(payload.model_dump(), historical_proj_df)
            else:
                sim_result = {}
        else:
            historical_available = False
            sim_projs = []
            sim_result = {}
        
        # Return merged JSON structure securely dictating new taxonomy matching UI streams
        contribs = pred_result.get("feature_contributions", {})
        br = pred_result.get("base_rate", 0.0)
        
        return {
            "probability": pred_result["success_probability"],
            "outcome": pred_result["predicted_class"],
            "confidence": pred_result.get("confidence_level", "Unknown"),
            "shap_values": list(contribs.values()),
            "feature_names": list(contribs.keys()),
            "base_rate": br,
            "optimization": {
                "recommended_goal": opt_result.get("optimal_goal", payload.goal),
                "expected_probability": opt_result.get("optimal_probability", pred_result["success_probability"]),
                "improvement": opt_result.get("optimal_probability", pred_result["success_probability"]) - pred_result["success_probability"]
            },
            "historical_available": historical_available,
            "similar_projects": sim_projs,
            "historical": {
                "win_rate": sim_result.get("historical_success_rate", 0) if historical_available else 0,
                "avg_goal": sim_result.get("average_goal", 0) if historical_available else 0,
                "avg_duration": sim_result.get("average_duration", 0) if historical_available else 0,
                "sample_size": sim_result.get("similar_projects_found", 0) if historical_available else 0
            }
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

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("src.api.app:app", host="0.0.0.0", port=port)

