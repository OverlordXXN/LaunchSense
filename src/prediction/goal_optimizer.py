import os
import sys
import logging
import copy
import numpy as np

# Setup paths
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(SRC_DIR)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

from prediction.predictor import predict_success_probability

def generate_goal_candidates(base_goal: float) -> list[float]:
    """
    Generates approx 20 evenly spaced candidate funding goals 
    around the provided base goal configuration (from 30% to 200%).
    """
    min_goal = base_goal * 0.3
    max_goal = base_goal * 2.0
    
    # Generate 20 evenly spaced candidates
    candidates = np.linspace(min_goal, max_goal, num=20)
    
    # Round to the nearest 100 for cleaner numbers
    clean_candidates = [round(c, -2) for c in candidates]
    
    return sorted(list(set(clean_candidates)))

def optimize_goal(project_inputs: dict) -> dict:
    """
    Evaluates multiple candidate goals and returns the goal configuration 
    that maximizes the chance of funding success.
    """
    try:
        base_goal = float(project_inputs['goal'])
    except KeyError:
        raise ValueError("Missing 'goal' in project_inputs")
    except ValueError:
        raise ValueError("The 'goal' must be a numeric value")

    candidates = generate_goal_candidates(base_goal)
    
    analysis_results = []
    optimal_goal = base_goal
    optimal_prob = -1.0
    
    logger.info(f"Evaluating {len(candidates)} goal optimization candidates...")
    
    for candidate in candidates:
        temp_inputs = copy.deepcopy(project_inputs)
        temp_inputs['goal'] = candidate
        
        # Predict success using the ML Engine
        prediction_result = predict_success_probability(temp_inputs)
        prob = prediction_result['success_probability']
        
        analysis_results.append({
            "goal": candidate,
            "probability": prob
        })
        
        if prob > optimal_prob:
            optimal_prob = prob
            optimal_goal = candidate

    return {
        "optimal_goal": optimal_goal,
        "optimal_probability": optimal_prob,
        "goal_analysis": analysis_results
    }

if __name__ == '__main__':
    logger.info("Executing Goal Optimization Module CLI Test")
    
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
    
    print("\n--- Current Baseline ---")
    current_prediction = predict_success_probability(test_inputs)
    print(f"Goal: {test_inputs['goal']}")
    print(f"Probability: {current_prediction['success_probability'] * 100:.2f}%")
    
    print("\n--- Running Optimization ---")
    opt_result = optimize_goal(test_inputs)
    
    print("\n--- Optimization Complete ---")
    print(f"Suggested Optimal Goal: {opt_result['optimal_goal']}")
    print(f"Maximized Probability:  {opt_result['optimal_probability'] * 100:.2f}%")
