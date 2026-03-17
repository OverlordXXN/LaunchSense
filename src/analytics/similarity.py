"""
Functions for calculating metrics on historically similar projects.
"""

import pandas as pd
import numpy as np

def calculate_similarity_metrics(input_project: dict, df: pd.DataFrame) -> dict:
    """
    Computes performance metrics of historical projects that resemble the input.
    """
    target_category = input_project.get("category")
    target_subcategory = input_project.get("subcategory")
    target_goal = float(input_project.get("goal", 0))
    target_duration = int(input_project.get("campaign_duration", 30))
    
    # Base filter: Same exact subcategory ensures maximum relevance
    mask = (df['category'] == target_category) & (df['subcategory'] == target_subcategory)
    base_comps = df[mask]
    
    # If we have a healthy baseline, try to narrow down financially and chronologically
    refined_mask = mask & \
                   (df['goal'] >= target_goal * 0.5) & \
                   (df['goal'] <= target_goal * 1.5) & \
                   (df['campaign_duration'] >= target_duration - 7) & \
                   (df['campaign_duration'] <= target_duration + 7)
                   
    refined_comps = df[refined_mask]
    
    # Fallback to broader category if the refined version is too sparse
    if len(refined_comps) >= 20:
        comps = refined_comps
        tier = "High"
    elif len(base_comps) >= 20:
        comps = base_comps
        tier = "Moderate"
    else:
        # Extreme fallback
        comps = df[df['category'] == target_category]
        tier = "Low"
        
    if comps.empty:
        return {
            "similar_projects_found": 0,
            "historical_success_rate": 0.0,
            "average_goal": 0.0,
            "average_duration": 0.0,
            "confidence": "None"
        }
        
    return {
        "similar_projects_found": len(comps),
        "historical_success_rate": comps['is_successful'].mean(),
        "average_goal": comps['goal'].mean(),
        "average_duration": comps['campaign_duration'].mean(),
        "confidence": tier
    }
